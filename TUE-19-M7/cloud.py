import os
import tempfile
import discord
from discord.ext import commands
from ollama import Client
from model import get_class
import base64

# নিরাপ secure your token
# py -m pip install ollama
DISCORD_TOKEN = "YOUR_DISCORD_BOT_TOKEN_HERE"
OLLAMA_API_KEY = "YOUR_OLLAMA_API_KEY_HERE"

intents = discord.Intents.default()
intents = discord.Intents.all()
intents.message_content = True
intents.messages = True # Allowing the bot to process messages
intents.guilds = True   # Allowing the bot to work with servers (guilds)

bot = commands.Bot(command_prefix="$", intents=intents)

# Ollama client
client = Client(
    host="http://localhost:11434",
    headers={'Authorization': f'Bearer {OLLAMA_API_KEY}'}
)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

@bot.command()
async def ask(ctx, *, question: str):
    """Ask the AI something"""

    messages = [
        {"role": "user", "content": question}
    ]

    # send initial message
    msg = await ctx.send("⏳ Thinking...")

    full_response = ""
    temp_path = None

    try:
        for part in client.chat("gemma4:31b-cloud", messages=messages, stream=True):
            chunk = part['message']['content']
            full_response += chunk

            # Keep the user notified while waiting
            if len(full_response) > 1900:
                await msg.edit(content="⏳ Still receiving response...")

        if not full_response:
            await msg.edit(content="⚠️ No response received from Ollama.")
            return

        if len(full_response) <= 1900:
            await msg.edit(content=full_response)
            return

        with tempfile.NamedTemporaryFile(delete=False, suffix=".txt", mode="w", encoding="utf-8") as tmp:
            tmp.write(full_response)
            temp_path = tmp.name

        await ctx.send(file=discord.File(temp_path))
        await msg.edit(content="✅ Response was too long for Discord and has been sent as a .txt file.")

    except Exception as e:
        await msg.edit(content=f"❌ Error: {e}")
    finally:
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)

@bot.command()
async def detect(ctx):
    """Detect objects in an attached image using Ollama."""
    if not ctx.message.attachments:
        return await ctx.send("Please attach an image to detect objects.")

    attachment = ctx.message.attachments[0]
    if not attachment.content_type or not attachment.content_type.startswith("image"):
        return await ctx.send("The first attachment is not an image.")

    temp_path = None
    msg = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=attachment.filename[attachment.filename.rfind("."):], mode="wb") as tmp:
            await attachment.save(tmp.name)
            temp_path = tmp.name
        
        msg = await ctx.send("⏳ Detecting objects in the image...")
        
        # Read image and encode to base64 for Ollama
        with open(temp_path, "rb") as image_file:
            image_data = base64.b64encode(image_file.read()).decode("utf-8")
        
        messages = [
            {
                "role": "user",
                "content": "Analyze this image and list all objects visible in it.",
                "images": [image_data]
            }
        ]

        full_response = ""
        for part in client.chat("gemma4:31b-cloud", messages=messages, stream=True):
            chunk = part["message"]["content"]
            full_response += chunk
        
        response_text = full_response if full_response else "No objects detected."
        await msg.edit(content=response_text[:2000])
        
    except Exception as e:
        if msg:
            await msg.edit(content=f"❌ Error: {e}")
        else:
            await ctx.send(f"❌ Error: {e}")
    finally:
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)


#Computer Vision Classification Pipit/Merpati
@bot.command()
async def klasifikasi(ctx):
    if ctx.message.attachments:
        for attachment in ctx.message.attachments:
            file_name = attachment.filename
            #file_url = attachment.url IF URL
            await attachment.save(f"./CV/{file_name}")
            await ctx.send(get_class(model_path="keras_model.h5", labels_path="labels.txt", image_path=f"./CV/{file_name}"))
    else:
        await ctx.send("Anda lupa mengunggah gambar :(")

bot.run(DISCORD_TOKEN)
