import os
import discord
from discord.ext import commands

TOKEN = os.getenv("DISCORD_TOKEN")  # Renderの環境変数から読み込む

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"ログインしました: {bot.user}")

@bot.command()
async def ping(ctx):
    await ctx.send("Pong!")

bot.run(TOKEN)
