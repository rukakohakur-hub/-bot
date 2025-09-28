import discord
from discord.ext import commands
import sqlite3
import random  # ランダム選択用

TOKEN = "YOUR_BOT_TOKEN"  # ←自分のBotトークンに置き換えてね
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

# ===== Embed作成関数（ページごと） =====
def get_page_embed(page: int, per_page: int = 5):
    c.execute("SELECT * FROM biomes")
    rows = c.fetchall()
    total_pages = max(1, (len(rows) + per_page - 1) // per_page)

    start = (page - 1) * per_page
    end = start + per_page
    current = rows[start:end]

    embed = discord.Embed(
        title=f"バイオーム座標一覧 (ページ {page}/{total_pages})",
        color=discord.Color.green()
    )

    if not current:
        embed.description = "まだ登録はありません。"
    else:
        for row in current:
            embed.add_field(
                name=f"📍 ID: {row[0]} | {row[1]}",
                value=f"座標: X:{row[2]} Y:{row[3]} Z:{row[4]}\n登録者: {row[5]}",
                inline=False
            )
    return embed, total_pages

# ===== ページ操作View =====
class PageView(discord.ui.View):
    def __init__(self, page: int, total_pages: int):
        super().__init__(timeout=None)
        self.page = page
        self.total_pages = total_pages

    @discord.ui.button(label="◀️", style=discord.ButtonStyle.secondary)
    async def previous(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.page > 1:
            self.page -= 1
            embed, total = get_page_embed(self.page)
            self.total_pages = total
            await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="▶️", style=discord.ButtonStyle.secondary)
    async def next(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.page < self.total_pages:
            self.page += 1
            embed, total = get_page_embed(self.page)
            self.total_pages = total
            await interaction.response.edit_message(embed=embed, view=self)

# ===== 一覧更新 =====
async def update_list():
    channel = bot.get_channel(LIST_CHANNEL_ID)
    if channel is None:
        return

    embed, total_pages = get_page_embed(1)
    view = PageView(1, total_pages)

    messages = [msg async for msg in channel.history(limit=1)]
    if messages:
        await messages[0].edit(embed=embed, view=view)
    else:
        await channel.send(embed=embed, view=view)

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

@bot.command()
async def search(ctx, biome: str):
    c.execute("SELECT * FROM biomes WHERE biome LIKE ?", (f"%{biome}%",))
    rows = c.fetchall()

    if not rows:
        await ctx.send(f"🔍 {biome} は見つかりませんでした。")
        return

    embed = discord.Embed(
        title=f"検索結果: {biome}",
        color=discord.Color.blue()
    )
    for row in rows:
        embed.add_field(
            name=f"📍 ID: {row[0]} | {row[1]}",
            value=f"座標: X:{row[2]} Y:{row[3]} Z:{row[4]}\n登録者: {row[5]}",
            inline=False
        )
    await ctx.send(embed=embed)

@bot.command()
async def random_biome(ctx):
    c.execute("SELECT * FROM biomes")
    rows = c.fetchall()

    if not rows:
        await ctx.send("📭 登録されているバイオームはまだありません。")
        return

    row = random.choice(rows)
    embed = discord.Embed(
        title="🎲 ランダムに選ばれたバイオーム",
        color=discord.Color.purple()
    )
    embed.add_field(
        name=f"📍 ID: {row[0]} | {row[1]}",
        value=f"座標: X:{row[2]} Y:{row[3]} Z:{row[4]}\n登録者: {row[5]}",
        inline=False
    )
    await ctx.send(embed=embed)

# ===== 起動 =====
@bot.event
async def on_ready():
    print(f"ログインしました: {bot.user}")
    await update_list()

import os

TOKEN = os.getenv("DISCORD_TOKEN")

if not TOKEN:
    print("⚠️ TOKENが読み込めていません")
else:
    print("✅ TOKENが読み込めました")

bot.run(TOKEN)
