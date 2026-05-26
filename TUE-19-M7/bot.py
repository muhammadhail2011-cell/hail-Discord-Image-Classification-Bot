import discord
from discord.ext import commands
import os
import uuid

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='$', intents=intents)

@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')

@bot.command()
async def hello(ctx):
    await ctx.send(f'Hi! I am a bot {bot.user}!')

@bot.command()
async def heh(ctx, count_heh=5):
    await ctx.send("he" * count_heh)

# Command upload gambar
@bot.command()
async def detect(ctx):
    if len(ctx.message.attachments) > 0:
        if not os.path.exists("images"):
            os.makedirs("images")
        attachment = ctx.message.attachments[0]
        unique_name = f"{uuid.uuid4()}_{attachment.filename}"
        file_path = f"images/{unique_name}"
        await attachment.save(file_path)
        await ctx.send(f"Gambar berhasil disimpan di: {file_path}")
    else:
        await ctx.send("Kamu belum mengupload gambar!")

bot.run("YOUR_BOT_TOKEN_HERE")