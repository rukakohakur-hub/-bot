import discord
from discord.ext import commands
import random
import os

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

omikuji_results = [
    "🎉 大吉！今日は最高の一日になりそうです！",
    "😊 中吉。いいことが起こる予感です。",
    "😌 小吉。ちょっとした幸せが訪れるかも。",
    "🤔 吉。悪くはない一日になりそうです。",
    "😅 凶…今日は注意して過ごしましょう。",
    "😱 大凶！？でも逆にレア運かも！？"
]

@bot.event
async def on_ready():
    print(f"ログインしました: {bot.user}")

@bot.command()
async def omikuji(ctx):
    result = random.choice(omikuji_results)
    await ctx.send(result)

if __name__ == "__main__":
    TOKEN = os.environ.get("DISCORD_TOKEN")
    if TOKEN is None:
        print("環境変数 DISCORD_TOKEN が設定されていません")
    else:
        bot.run(TOKEN)
