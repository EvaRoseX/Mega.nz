# --- PYTHON 3.11+ ASYNCIO PATCH ---
import asyncio
if not hasattr(asyncio, "coroutine"):
    asyncio.coroutine = lambda f: f
# ----------------------------------

import os
from threading import Thread
from flask import Flask
from pyrogram import Client, filters
from mega import Mega

# --- 1. RENDER TIMEOUT SE BACHNE KE LIYE WEB SERVER ---
flask_app = Flask(__name__)

@flask_app.route('/')
def home():
    return "Bot is Running 24/7!"

def run_flask():
    # Render automatically $PORT environment variable deta hai
    port = int(os.environ.get("PORT", 8080))
    flask_app.run(host='0.0.0.0', port=port)

# --- 2. TELEGRAM BOT CODE ---
API_ID = 33361737
API_HASH = "7cd3bda26b08957a7205bbe8a51e6e90"
BOT_TOKEN = "8845441338:AAH_8gomla1JqmxCX4qaUeb1iT37udhwayU"

app = Client("mega_downloader_render", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
mega = Mega()

@app.on_message(filters.command("start"))
async def start_command(client, message):
    await message.reply_text("👋 Render Server se Hello! Main active hoon, mujhe Mega link bhejiye.")

@app.on_message(filters.regex(r"https://mega\.nz/(file|folder)/"))
async def handle_mega_link(client, message):
    url = message.text
    status_message = await message.reply_text("🔄 Mega link mil gaya! Processing shuru...")

    try:
        download_dir = "./downloads"
        if not os.path.exists(download_dir):
            os.makedirs(download_dir)

        await status_message.edit_text("📥 Mega se download ho raha hai...")
        m = mega.login()
        loop = asyncio.get_event_loop()
        file_path = await loop.run_in_executor(None, lambda: m.download_url(url, dest_path=download_dir))
        
        if isinstance(file_path, list):
            file_path = file_path[0]

        await status_message.edit_text("📤 Telegram par upload ho raha hai...")
        await client.send_video(chat_id=message.chat.id, video=file_path, reply_to_message_id=message.id)
        await status_message.delete()
        
        if os.path.exists(file_path):
            os.remove(file_path)

    except Exception as e:
        await status_message.edit_text(f"❌ Error: {str(e)}")
        if 'file_path' in locals() and os.path.exists(file_path):
            os.remove(file_path)

# --- 3. BOT AUR WEB SERVER KO SATH ME CHALANA ---
if __name__ == "__main__":
    # Flask ko alag thread me chalayenge taaki bot block na ho
    t = Thread(target=run_flask)
    t.daemon = True
    t.start()
    
    print("🚀 Starting Telegram Bot on Render...")
    app.run()
