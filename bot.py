import discord
from discord.ext import commands, tasks
from discord.ui import Button, View
import sqlite3
import os

TOKEN = os.getenv("DISCORD_TOKEN")

# チャンネルID
INPUT_CHANNEL_ID = 1421839788272648223  # 入力用
LOG_CHANNEL_ID = 1421840287000563724    # ログ用

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# ===== データベース =====
conn = sqlite3.connect("biomes.db")
c = conn.cursor()
c.execute("""CREATE TABLE IF NOT EXISTS biomes (
    name TEXT,
    x INTEGER,
    y INTEGER,
    z INTEGER,
    user TEXT
)""")
conn.commit()

# ===== ボタンビュー =====
class BiomeView(View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="バイオーム登録", style=discord.ButtonStyle.primary, custom_id="add_biome_button")
    async def add_biome_button(self, interaction: discord.Interaction, button: Button):
        modal = BiomeModal()
        await interaction.response.send_modal(modal)

# ===== モーダル入力 =====
class BiomeModal(discord.ui.Modal, title="バイオーム登録"):
    name = discord.ui.TextInput(label="バイオーム名", placeholder="例: 森")
    x = discord.ui.TextInput(label="X座標", placeholder="例: 100")
    y = discord.ui.TextInput(label="Y座標", placeholder="例: 64")
    z = discord.ui.TextInput(label="Z座標", placeholder="例: -200")

    async def on_submit(self, interaction: discord.Interaction):
        name = self.name.value
        try:
            x, y, z = int(self.x.value), int(self.y.value), int(self.z.value)
        except ValueError:
            await interaction.response.send_message("❌ 座標は数値で入力してください。", ephemeral=True)
            return

        # DB保存
        c.execute("INSERT INTO biomes (name, x, y, z, user) VALUES (?, ?, ?, ?, ?)",
                  (name, x, y, z, str(interaction.user)))
        conn.commit()

        # 入力チャンネルに表示（30秒後に削除）
        await interaction.response.send_message(
            f"✅ バイオーム **{name}** を登録しました！（座標: {x}, {y}, {z}）",
            ephemeral=False,
            delete_after=30
        )

        # ログチャンネルに送信（残す）
        log_channel = bot.get_channel(LOG_CHANNEL_ID)
        if log_channel:
            embed = discord.Embed(title="📝 新しいバイオームが登録されました！", color=0x95a5a6)
            embed.add_field(name="バイオーム", value=name, inline=False)
            embed.add_field(name="座標", value=f"({x}, {y}, {z})", inline=False)
            embed.add_field(name="登録者", value=str(interaction.user), inline=False)
            await log_channel.send(embed=embed)

# ===== 定期的にボタンを更新 =====
last_message = None

@tasks.loop(minutes=1)
async def update_button():
    global last_message
    channel = bot.get_channel(INPUT_CHANNEL_ID)
    if channel:
        # 前のボタンを消す
        if last_message:
            try:
                await last_message.delete()
            except:
                pass
        # 新しいボタンを投稿
        view = BiomeView()
        last_message = await channel.send("⬇️ バイオームを登録するには下のボタンを押してください！", view=view)

@bot.event
async def on_ready():
    print(f"✅ ログイン完了: {bot.user}")

    # タスクが止まってたら再スタート
    if not update_button.is_running():
        update_button.start()

bot.run(TOKEN)
