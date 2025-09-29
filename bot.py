import discord
from discord.ext import commands, tasks
import sqlite3
import os

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# ===== データベース初期化 =====
conn = sqlite3.connect("biomes.db")
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS biomes
             (id INTEGER PRIMARY KEY AUTOINCREMENT,
              name TEXT, x INTEGER, y INTEGER, z INTEGER, author TEXT)''')
conn.commit()

# ===== 定数 =====
INPUT_CHANNEL_ID = 123456789012345678  # ←バイオーム入力用チャンネルIDを入れてね
ANNOUNCE_CHANNEL_ID = 123456789012345678  # ←アナウンス用チャンネルIDを入れてね

last_message = None  # 前のボタンメッセージを保持


# ===== ビュー（ボタンUI） =====
class BiomeModal(discord.ui.Modal, title="バイオーム登録"):
    biome_name = discord.ui.TextInput(label="バイオーム名", placeholder="例: 砂漠")
    x = discord.ui.TextInput(label="X座標", placeholder="例: 100")
    y = discord.ui.TextInput(label="Y座標", placeholder="例: 64")
    z = discord.ui.TextInput(label="Z座標", placeholder="例: 200")

    async def on_submit(self, interaction: discord.Interaction):
        # DBに保存
        c.execute("INSERT INTO biomes (name, x, y, z, author) VALUES (?, ?, ?, ?, ?)",
                  (self.biome_name.value,
                   int(self.x.value), int(self.y.value), int(self.z.value),
                   str(interaction.user)))
        conn.commit()

        # 成功メッセージ（ephemeralじゃないので全員に見える）
        await interaction.response.send_message(
            f"✅ バイオーム {self.biome_name.value} を登録しました！"
            f"（座標: {self.x.value}, {self.y.value}, {self.z.value}）",
            ephemeral=False
        )

        # アナウンスチャンネルに通知
        channel = bot.get_channel(ANNOUNCE_CHANNEL_ID)
        if channel:
            embed = discord.Embed(
                title="📝 新しいバイオームが登録されました！",
                description=f"**バイオーム**\n{self.biome_name.value}\n\n"
                            f"**座標**\n({self.x.value}, {self.y.value}, {self.z.value})\n\n"
                            f"**登録者**\n{interaction.user}",
                color=discord.Color.green()
            )
            await channel.send(embed=embed)


class BiomeView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="バイオーム登録", style=discord.ButtonStyle.blurple)
    async def button_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(BiomeModal())


# ===== 定期的にボタンを維持するタスク =====
@tasks.loop(minutes=1)
async def update_button():
    global last_message
    channel = bot.get_channel(INPUT_CHANNEL_ID)
    if channel:
        # 古いボタンメッセージを削除
        if last_message:
            try:
                await last_message.delete()
            except:
                pass

        # 新しいボタンメッセージを送信（silent=True → 通知を飛ばさない！）
        view = BiomeView()
        last_message = await channel.send(
            "⬇️ バイオームを登録するには下のボタンを押してください！",
            view=view,
            silent=True
        )


# ===== 起動イベント =====
@bot.event
async def on_ready():
    print(f"ログイン完了: {bot.user}")
    update_button.start()


# ===== 実行 =====
bot.run(os.getenv("DISCORD_TOKEN"))
