import os
import discord
from discord.ext import tasks
from discord.ui import View, Button
from keep_alive import keep_alive

TOKEN = os.environ.get("DISCORD_BOT_TOKEN")
CHANNEL_ID = int(os.environ.get("DISCORD_CHANNEL_ID"))

intents = discord.Intents.default()
client = discord.Client(intents=intents)

# ボタンを作るクラス
class BiomeButton(Button):
    def __init__(self):
        super().__init__(label="登録する", style=discord.ButtonStyle.primary)

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_message(
            "バイオームを登録しました！", ephemeral=True
        )

class BiomeView(View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(BiomeButton())

# 編集対象のメッセージを保持
last_message = None

@client.event
async def on_ready():
    print(f"ログイン成功: {client.user}")
    update_button.start()

@tasks.loop(minutes=1)
async def update_button():
    global last_message
    channel = client.get_channel(CHANNEL_ID)
    if channel is None:
        print("チャンネルが見つかりません。")
        return

    view = BiomeView()

    # 初回は送信して保持、それ以降は編集
    if last_message is None:
        last_message = await channel.send(
            "⬇️ バイオームを登録するには下のボタンを押してください！",
            view=view
        )
    else:
        try:
            await last_message.edit(
                content="⬇️ バイオームを登録するには下のボタンを押してください！",
                view=view
            )
        except discord.NotFound:
            # メッセージが消されたら再送
            last_message = await channel.send(
                "⬇️ バイオームを登録するには下のボタンを押してください！",
                view=view
            )

keep_alive()
client.run(TOKEN)
