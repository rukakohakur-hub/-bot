import discord
from openai import OpenAI
import os

# OpenAI クライアント
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Discord トークン
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

# Discord クライアント
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
discord_client = discord.Client(intents=intents)

@discord_client.event
async def on_ready():
    print(f'ログインしました: {discord_client.user}')

@discord_client.event
async def on_message(message):
    if message.author.bot:
        return

    # ChatGPT に問い合わせ
    response = openai_client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "あなたは親切なメイド、レムです。"},
            {"role": "user", "content": message.content},
        ]
    )
    reply = response.choices[0].message.content

    # Discord に返信
    await message.channel.send(reply)

discord_client.run(DISCORD_TOKEN)
