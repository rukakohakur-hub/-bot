import discord
from discord.ext import commands, tasks
import sqlite3
import os

TOKEN = os.getenv("DISCORD_TOKEN")
bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())

# ===== チャンネル設定 =====
INPUT_CHANNEL_ID = 1421839788272648223
LOG_CHANNEL_ID = 1421840287000563724

# ===== DB初期化 =====
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

# ===== フォーム =====
class BiomeModal(discord.ui.Modal, title="バイオーム登録"):
    biome_name = discord.ui.TextInput(label="バイオーム名", placeholder="例: Jungle", required=True)
    x = discord.ui.TextInput(label="X座標", placeholder="例: 120", required=True)
    y = discord.ui.TextInput(label="Y座標", placeholder="例: 64", required=True)
    z = discord.ui.TextInput(label="Z座標", placeholder="例: -320", required=True)

    async def on_submit(self, interaction: discord.Interaction):
        # DBに保存
        c.execute(
            "INSERT INTO biomes (name, x, y, z, user) VALUES (?, ?, ?, ?, ?)",
            (self.biome_name.value, int(self.x.value), int(self.y.value), int(self.z.value), str(interaction.user))
        )
        conn.commit()

        # ユーザーに返信
        await interaction.response.send_message(
            f"✅ バイオーム **{self.biome_name.value}** を登録しました！", ephemeral=True
        )

        # ログチャンネルに送信
        log_channel = bot.get_channel(LOG_CHANNEL_ID)
        if log_channel:
            embed = discord.Embed(title="📝 新しいバイオームが登録されました！", color=0x95a5a6)
            embed.add_field(name="バイオーム", value=self.biome_name.value, inline=False)
            embed.add_field(name="座標", value=f"({self.x.value}, {self.y.value}, {self.z.value})", inline=False)
            embed.add_field(name="登録者", value=str(interaction.user), inline=False)
            await log_channel.send(embed=embed)

# ===== ボタン =====
class BiomeButton(discord.ui.View):
    @discord.ui.button(label="バイオームを登録する", style=discord.ButtonStyle.primary)
    async def register(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(BiomeModal())

# ===== 定期更新 =====
latest_message = None

@tasks.loop(minutes=1)
async def refresh_button():
    global latest_message
    channel = bot.get_channel(INPUT_CHANNEL_ID)

    # 古いメッセージを削除
    if latest_message:
        try:
            await latest_message.delete()
        except:
            pass

    # 新しいボタンを送信
    view = BiomeButton()
    latest_message = await channel.send("⬇️ 新しい登録ボタン ⬇️", view=view)

# ===== 起動時 =====
@bot.event
async def on_ready():
    print(f"✅ ログイン完了: {bot.user}")
    refresh_button.start()

# ===== Bot起動 =====
if __name__ == "__main__":
    bot.run(TOKEN)
