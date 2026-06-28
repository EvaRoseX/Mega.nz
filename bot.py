# --- PYTHON 3.11/3.13/3.14+ ALL-IN-ONE ERROR FIX (PATCH) ---
import asyncio
import sys

if not hasattr(asyncio, "coroutine"):
    asyncio.coroutine = lambda f: f

try:
    asyncio.get_event_loop()
except RuntimeError:
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
# ------------------------------------------------------------

import os
import random
from threading import Thread
from flask import Flask
from pyrogram import Client, filters
from mega import Mega

flask_app = Flask(__name__)

@flask_app.route('/')
def home():
    return "Bot is Running 24/7 on Koyeb!"

def run_flask():
    # Koyeb default port 8000 use karta hai
    port = int(os.environ.get("PORT", 8000))
    flask_app.run(host='0.0.0.0', port=port)

# --- TELEGRAM BOT CREDENTIALS (UPDATED) ---
API_ID = 33361737
API_HASH = "7cd3bda26b08957a7205bbe8a51e6e90"
BOT_TOKEN = "8861881763:AAHCVZ1V7pIYOJe4yRt3rwGU5qtt3BUBt0Q"

app = Client("mega_downloader_koyeb", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

@app.on_message(filters.command("start"))
async def start_command(client, message):
    await message.reply_text("👋 Koyeb Server se Hello! Main naye token ke sath active hoon. Mujhe Mega link bhejiye.")

@app.on_message(filters.regex(r"https://mega\.nz/(file|folder)/"))
async def handle_mega_link(client, message):
    url = message.text
    status_message = await message.reply_text("🔄 Mega link mil gaya! Server par check chal raha hai...")

    try:
        download_dir = "./downloads"
        if not os.path.exists(download_dir):
            os.makedirs(download_dir)

        await status_message.edit_text("📥 Koyeb server se video download ho rahi hai...")
        
        mega = Mega()
        m = mega.login() 
        
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = asyncio.get_event_loop()
            
        file_path = await loop.run_in_executor(None, lambda: m.download_url(url, dest_path=download_dir))
        
        if isinstance(file_path, list):
            file_path = file_path[0]

        await status_message.edit_text("📤 Download complete! Ab Telegram par video upload ho rahi hai...")
        await client.send_video(chat_id=message.chat.id, video=file_path, reply_to_message_id=message.id)
        await status_message.delete()
        
        if os.path.exists(file_path):
            os.remove(file_path)

    except Exception as e:
        await status_message.edit_text(f"❌ Error: {str(e)}")
        if 'file_path' in locals() and os.path.exists(file_path):
            os.remove(file_path)

if __name__ == "__main__":
    t = Thread(target=run_flask)
    t.daemon = True
    t.start()
    
    print("🚀 Starting Bot on Koyeb with new token...")
    app.run()
