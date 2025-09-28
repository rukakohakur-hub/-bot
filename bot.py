import discord
from discord.ext import commands
import sqlite3

# ===== Bot設定 =====
TOKEN = "YOUR_BOT_TOKEN"  # ←自分のBotトークンに置き換えてね
GUILD_ID = 123456789012345678  # ←サーバーID
LIST_CHANNEL_ID = 123456789012345678  # ←#バイオーム一覧 のチャンネルID
PREFIX = "!"
bot = commands.Bot(command_prefix=PREFIX, intents=discord.Intents.all())

# ===== データベース =====
conn = sqlite3.connect("biomes.db")
c = conn.cursor()
c.execute("""
CREATE TABLE IF NOT EXISTS biomes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    biome TEXT,
    x INTEGER,
    y INTEGER,
    z INTEGER,
    user TEXT
)
""")
conn.commit()

# ===== 一覧更新 =====
async def update_list():
    channel = bot.get_channel(LIST_CHANNEL_ID)
    if channel is None:
        return

    # データを取得
    c.execute("SELECT * FROM biomes")
    rows = c.fetchall()

    if not rows:
        content = "== バイオーム座標一覧 ==\nまだ登録はありません。"
    else:
        content = "== バイオーム座標一覧 ==\n"
        for row in rows:
            content += f"ID: {row[0]} | {row[1]} | X:{row[2]} Y:{row[3]} Z:{row[4]} | 登録者: {row[5]}\n"

    # チャンネルの最新メッセージを取得
    messages = [msg async for msg in channel.history(limit=1)]
    if messages:
        await messages[0].edit(content=content)
    else:
        await channel.send(content)

# ===== コマンド =====
@bot.command()
async def add(ctx, biome: str, x: int, y: int, z: int):
    c.execute("INSERT INTO biomes (biome, x, y, z, user) VALUES (?, ?, ?, ?, ?)",
              (biome, x, y, z, str(ctx.author)))
    conn.commit()
    await update_list()
    await ctx.send(f"✅ {biome} を登録しました！")

@bot.command()
async def remove(ctx, id: int):
    c.execute("DELETE FROM biomes WHERE id=?", (id,))
    conn.commit()
    await update_list()
    await ctx.send(f"🗑️ ID {id} を削除しました。")

@bot.command()
async def edit(ctx, id: int, biome: str, x: int, y: int, z: int):
    c.execute("UPDATE biomes SET biome=?, x=?, y=?, z=?, user=? WHERE id=?",
              (biome, x, y, z, str(ctx.author), id))
    conn.commit()
    await update_list()
    await ctx.send(f"✏️ ID {id} を更新しました！")

# ===== 起動 =====
@bot.event
async def on_ready():
    print(f"ログインしました: {bot.user}")
    await update_list()

bot.run(TOKEN)
