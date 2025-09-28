import discord
from discord.ext import commands
import sqlite3
import os

TOKEN = os.getenv("DISCORD_TOKEN")
bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())

# チャンネルID
INPUT_CHANNEL_ID = 1421839788272648223
LOG_CHANNEL_ID = 1421840287000563724

# データベース準備
conn = sqlite3.connect("biomes.db")
c = conn.cursor()
c.execute("""CREATE TABLE IF NOT EXISTS biomes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    x INTEGER,
    y INTEGER,
    z INTEGER,
    user TEXT
)""")
conn.commit()

# ==== ボタンビュー ====
class BiomeView(discord.ui.View):
    @discord.ui.button(label="➕ バイオーム登録", style=discord.ButtonStyle.green)
    async def add_biome_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = BiomeModal()
        await interaction.response.send_modal(modal)


# ==== モーダル ====
class BiomeModal(discord.ui.Modal, title="🌱 バイオーム登録"):
    biome_name = discord.ui.TextInput(label="バイオーム名", placeholder="例: Jungle")
    x_coord = discord.ui.TextInput(label="X座標", placeholder="整数を入力してください")
    y_coord = discord.ui.TextInput(label="Y座標", placeholder="整数を入力してください")
    z_coord = discord.ui.TextInput(label="Z座標", placeholder="整数を入力してください")

    async def on_submit(self, interaction: discord.Interaction):
        name = str(self.biome_name)
        try:
            x = int(self.x_coord.value)
            y = int(self.y_coord.value)
            z = int(self.z_coord.value)
        except ValueError:
            await interaction.response.send_message("❌ 座標は整数で入力してください。", ephemeral=True)
            return

        # DBに保存
        c.execute("INSERT INTO biomes (name, x, y, z, user) VALUES (?, ?, ?, ?, ?)",
                  (name, x, y, z, str(interaction.user)))
        conn.commit()

        # ログチャンネルに送信
        log_channel = bot.get_channel(LOG_CHANNEL_ID)
        if log_channel:
            embed = discord.Embed(title="📝 新しいバイオームが登録されました！", color=0x2ecc71)
            embed.add_field(name="バイオーム", value=name, inline=False)
            embed.add_field(name="座標", value=f"({x}, {y}, {z})", inline=False)
            embed.add_field(name="登録者", value=str(interaction.user), inline=False)
            await log_channel.send(embed=embed)

        await interaction.response.send_message(f"✅ バイオーム **{name}** を登録しました！", ephemeral=True)


# ==== 起動処理 ====
@bot.event
async def on_ready():
    print(f"✅ ログイン完了: {bot.user}")
    await bot.change_presence(activity=discord.Game(name="Biome Logger"))

    # 入力用チャンネルにボタン設置
    input_channel = bot.get_channel(INPUT_CHANNEL_ID)
    if input_channel:
        view = BiomeView()
        await input_channel.send("ここからバイオームを登録できます！", view=view)


# Bot起動
if __name__ == "__main__":
    bot.run(TOKEN)
