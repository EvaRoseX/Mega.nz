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
import time
from threading import Thread
from flask import Flask
from pyrogram import Client, filters
from mega import Mega

flask_app = Flask(__name__)

@flask_app.route('/')
def home():
    return "Bot is Running 24/7 on Render!"

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    flask_app.run(host='0.0.0.0', port=port)

# --- TELEGRAM BOT CREDENTIALS ---
API_ID = 33361737
API_HASH = "7cd3bda26b08957a7205bbe8a51e6e90"
BOT_TOKEN = "8845441338:AAH_8gomla1JqmxCX4qaUeb1iT37udhwayU"

app = Client("mega_downloader_render", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# Is baar hum mega instance function ke andar banayenge har naye link ke liye

@app.on_message(filters.command("start"))
async def start_command(client, message):
    await message.reply_text("👋 Render se Hello! Mujhe Mega link bhejiye. (IP Block Bypass Activated)")

@app.on_message(filters.regex(r"https://mega\.nz/(file|folder)/"))
async def handle_mega_link(client, message):
    url = message.text
    status_message = await message.reply_text("🔄 Mega link mil gaya! Server session create ho raha hai...")

    try:
        download_dir = "./downloads"
        if not os.path.exists(download_dir):
            os.makedirs(download_dir)

        # Mega Block Bypass: Har request se pehle random delay taaki Render ka IP target na bane
        await asyncio.sleep(random.randint(3, 7))
        await status_message.edit_text("📥 Mega se download ho raha hai... (Render IP Bypass On)")
        
        # New Instance for every request to avoid concurrency detection
        mega = Mega()
        m = mega.login() 
        
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
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
        error_str = str(e)
        if "ETOOMANY" in error_str:
            await status_message.edit_text(
                "❌ **Mega IP Block Error (Render Limitation)**\n\n"
                "Render ke is Server IP ko Mega ne temporarily limit kar diya hai kyuki bohot log ise use kar rahe hain.\n\n"
                "💡 **Solution:** Kuch der baad doosra link try karein, ya fir is bot ko Koyeb.com ya Pydroid me VPN ke sath chalayein jahan IP fresh milta hai."
            )
        else:
            await status_message.edit_text(f"❌ Error: {error_str}")
            
        if 'file_path' in locals() and os.path.exists(file_path):
            os.remove(file_path)

if __name__ == "__main__":
    t = Thread(target=run_flask)
    t.daemon = True
    t.start()
    
    print("🚀 Starting Bot...")
    app.run()
