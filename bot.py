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
import time
from threading import Thread
from flask import Flask
from pyrogram import Client, filters
from mega import Mega

flask_app = Flask(__name__)

@flask_app.route('/')
def home():
    return "Bot is Running 24/7 on Koyeb!"

def run_flask():
    port = int(os.environ.get("PORT", 8000))
    flask_app.run(host='0.0.0.0', port=port)

# --- TELEGRAM BOT CREDENTIALS ---
API_ID = 33361737
API_HASH = "7cd3bda26b08957a7205bbe8a51e6e90"
BOT_TOKEN = "8861881763:AAHCVZ1V7pIYOJe4yRt3rwGU5qtt3BUBt0Q"

app = Client("mega_downloader_koyeb", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# --- LIVE PROGRESS BAR FUNCTION ---
async def progress_bar(current, total, status_message, start_time):
    now = time.time()
    if not hasattr(progress_bar, "last_update"):
        progress_bar.last_update = 0
        
    if now - progress_bar.last_update < 3 and current != total:
        return

    progress_bar.last_update = now
    
    percentage = (current / total) * 100
    completed_blocks = int(percentage // 10)
    remaining_blocks = 10 - completed_blocks
    
    bar = "█" * completed_blocks + "░" * remaining_blocks
    
    elapsed_time = now - start_time
    if elapsed_time > 0:
        speed = current / elapsed_time / (1024 * 1024) # MB/s
    else:
        speed = 0
        
    current_mb = current / (1024 * 1024)
    total_mb = total / (1024 * 1024)

    status_text = (
        f"📤 **Uploading Video...**\n\n"
        f"🌀 **Progress:** `[{bar}] {percentage:.1f}%`\n"
        f"📦 **Size:** `{current_mb:.2f} MB` / `{total_mb:.2f} MB`\n"
        f"⚡ **Speed:** `{speed:.2f} MB/s`"
    )
    
    try:
        await status_message.edit_text(status_text)
    except Exception:
        pass

@app.on_message(filters.command("start"))
async def start_command(client, message):
    await message.reply_text("👋 Bot ready hai! Mujhe Mega link bhejiye, main direct streaming video bhejunga.")

@app.on_message(filters.regex(r"https://mega\.nz/(file|folder)/"))
async def handle_mega_link(client, message):
    url = message.text
    status_message = await message.reply_text("🔄 Mega link mil gaya! Processing...")

    try:
        download_dir = "./downloads"
        if not os.path.exists(download_dir):
            os.makedirs(download_dir)

        await status_message.edit_text("📥 Koyeb server me Mega se video download ho rahi hai...")
        
        mega = Mega()
        m = mega.login() 
        
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = asyncio.get_event_loop()
            
        file_path = await loop.run_in_executor(None, lambda: m.download_url(url, dest_path=download_dir))
        
        if isinstance(file_path, list):
            if len(file_path) == 0:
                await status_message.edit_text("❌ Error: Mega link se koi file download nahi ho payi.")
                return
            else:
                file_path = file_path[0]

        if not file_path or not os.path.exists(str(file_path)):
            await status_message.edit_text("❌ Error: File server par nahi mili.")
            return

        start_time = time.time()
        await status_message.edit_text("📤 Uploading started... Video player generate ho raha hai...")
        
        # --- FIX: send_video use kiya hai stream support ke saath ---
        await client.send_video(
            chat_id=message.chat.id, 
            video=str(file_path),
            caption="✅ **Aapki Video Taiyar Hai!**",
            supports_streaming=True, # Isse video bina poori download huye play ho jayegi
            progress=progress_bar,
            progress_args=(status_message, start_time)
        )
        
        await status_message.delete()
        
        if os.path.exists(str(file_path)):
            os.remove(str(file_path))

    except Exception as e:
        await status_message.edit_text(f"❌ Error: {str(e)}")
        if 'file_path' in locals() and file_path and os.path.exists(str(file_path)):
            os.remove(str(file_path))

if __name__ == "__main__":
    t = Thread(target=run_flask)
    t.daemon = True
    t.start()
    
    print("🚀 Starting Bot on Koyeb...")
    app.run()
