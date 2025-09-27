import discord
from openai import OpenAI
client = OpenAI()
import os

# トークンとキーを環境変数から読み込む
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

openai.api_key = OPENAI_API_KEY

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'ログインしました: {client.user}')

@client.event
async def on_message(message):
    if message.author.bot:
        return

    # ユーザーのメッセージを取得
    user_message = message.content

    # ChatGPTに投げる
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "あなたは『Re:ゼロから始める異世界生活』のレムとして会話してください。"},
            {"role": "user", "content": user_message}
        ]
    )

    reply = response['choices'][0]['message']['content']
    await message.channel.send(reply)

client.run(DISCORD_TOKEN)
