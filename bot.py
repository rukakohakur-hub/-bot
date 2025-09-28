import discord
from discord.ext import commands
import random
import os

TOKEN = os.getenv("DISCORD_TOKEN")

bot = commands.Bot(command_prefix="!")

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

@bot.command()
async def omikuji(ctx):
    fortunes = [
        "大吉 🎉",
        "中吉 😊",
        "小吉 🍀",
        "吉 ✨",
        "末吉 🤔",
        "凶 💦"
    ]
    
    messages = [
        "今日のゲーム、レアドロップが期待できるかも",
        "スマホの充電は早めにしておくと安心",
        "新しいアプリを探すと掘り出し物が見つかる予感",
        "ソシャゲのログインボーナス、忘れないでね",
        "画面の見すぎ注意。休憩で運気アップ",
        "音楽を聴くと気分が切り替わりそう",
        "チャットで誰かに声をかけると面白いことが起きるかも",
        "スクショしておくと後で役立つ可能性大"
    ]

    lucky_items = [
        "イヤホン 🎧",
        "スマホスタンド 📱",
        "お気に入りのゲームソフト 🎮",
        "キーボード ⌨️",
        "お菓子 🍫",
        "冷たい飲み物 🥤",
        "ブランケット 🛋️",
        "充電ケーブル 🔌"
    ]
    
    result = random.choice(fortunes)
    msg = random.choice(messages)
    item = random.choice(lucky_items)
    
    await ctx.send(f"🔮 {result}\n💬 {msg}\n🎁 今日のラッキーアイテム: {item}")

bot.run(TOKEN)
