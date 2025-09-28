import threading
from flask import Flask
import discord
from discord.ext import commands
import sqlite3
import os

# ===== Flask（だまし用Webサーバー） =====
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running!"

def run_web():
    # Renderが確認できるようにポート10000で起動
    app.run(host="0.0.0.0", port=10000)

# ===== Discord Bot 設定 =====
TOKEN = os.getenv("DISCORD_TOKEN")
bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())

# ログ用チャンネルID
LOG_CHANNEL_ID = 1421840287000563724

# ===== データベース初期化 =====
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

# ===== 起動確認 =====
@bot.event
async def on_ready():
    print(f"✅ ログイン完了: {bot.user}")
    await bot.change_presence(activity=discord.Game(name="Minecraft Biome Logger"))

# ===== バイオーム登録 =====
@bot.command()
async def add_biome(ctx, name: str, x: int, y: int, z: int):
    c.execute("INSERT INTO biomes (name, x, y, z, user) VALUES (?, ?, ?, ?, ?)",
              (name, x, y, z, str(ctx.author)))
    conn.commit()
    await ctx.send(f"✅ バイオーム **{name}** を登録しました！（座標: {x}, {y}, {z}）")

        # ログチャンネルに送信
    log_channel = bot.get_channel(LOG_CHANNEL_ID)
    if log_channel:
        embed = discord.Embed(
            title="📝 新しいバイオームが登録されました！",
            description=f"{ctx.author.mention} さんが新しいバイオームを追加しました！",
            color=0x95a5a6
        )
        embed.add_field(name="🌍 バイオーム", value=str(name), inline=False)
        embed.add_field(name="📍 座標", value=f"({x}, {y}, {z})", inline=False)
        embed.add_field(name="👤 登録者", value=str(ctx.author), inline=False)
        await log_channel.send(embed=embed)

# ===== バイオーム一覧（最新5件） =====
@bot.command()
async def list_biomes(ctx):
    c.execute("SELECT name, x, y, z, user FROM biomes ORDER BY id DESC LIMIT 5")
    rows = c.fetchall()

    if not rows:
        await ctx.send("📭 登録されているバイオームはまだありません。")
        return

    embed = discord.Embed(title="📜 バイオーム一覧（最新5件）", color=0x2ecc71)
    for i, row in enumerate(rows, 1):
        name, x, y, z, user = row
        embed.add_field(
            name=f"{i}. {name}",
            value=f"座標: ({x}, {y}, {z})\n登録者: {user}",
            inline=False
        )
    await ctx.send(embed=embed)

# ===== バイオーム削除 =====
@bot.command()
async def del_biome(ctx, biome_id: int):
    c.execute("DELETE FROM biomes WHERE id = ?", (biome_id,))
    conn.commit()
    await ctx.send(f"🗑️ バイオームID {biome_id} を削除しました。")

# ===== 全部リスト =====
@bot.command()
async def all_biomes(ctx):
    c.execute("SELECT id, name, x, y, z, user FROM biomes ORDER BY id DESC")
    rows = c.fetchall()

    if not rows:
        await ctx.send("📭 登録されているバイオームはまだありません。")
        return

    embed = discord.Embed(title="🌍 全バイオーム一覧", color=0x3498db)
    for row in rows:
        biome_id, name, x, y, z, user = row
        embed.add_field(
            name=f"ID {biome_id}: {name}",
            value=f"座標: ({x}, {y}, {z})\n登録者: {user}",
            inline=False
        )
    await ctx.send(embed=embed)

# ===== Bot起動 =====
if __name__ == "__main__":
    # Flaskを別スレッドで起動
    threading.Thread(target=run_web).start()
    bot.run(TOKEN)
for command in bot.commands:
    print(f"📌 読み込まれたコマンド: {command}")
