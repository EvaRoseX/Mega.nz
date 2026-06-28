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
import re
from threading import Thread
from flask import Flask
from pyrogram import Client, filters
from mega import Mega

# Hachoir parser tool video metadata extract karne ke liye
from hachoir.metadata import extractMetadata
from hachoir.parser import createParser

flask_app = Flask(__name__)

@flask_app.route('/')
def home():
    return "Bot is Running 24/7 on Koyeb!"

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    flask_app.run(host='0.0.0.0', port=port)

# --- TELEGRAM BOT CREDENTIALS ---
API_ID = int(os.environ.get("API_ID", 33361737))
API_HASH = os.environ.get("API_HASH", "7cd3bda26b08957a7205bbe8a51e6e90")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "8861881763:AAHCVZ1V7pIYOJe4yRt3rwGU5qtt3BUBt0Q")

app = Client("mega_downloader_koyeb", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# --- MEGA LINK CONVERTER ---
def convert_mega_url(url):
    if "mega.nz/file/" in url:
        match = re.search(r"mega\.nz/file/([^#]+)#(.+)", url)
        if match:
            return f"https://mega.nz/#!{match.group(1)}!{match.group(2)}"
    return url

# --- LIVE PROGRESS BAR FUNCTION ---
async def progress_bar(current, total, status_message, start_time):
    now = time.time()
    if not hasattr(progress_bar, "last_update"):
        progress_bar.last_update = 0
        
    if now - progress_bar.last_update < 4 and current != total:
        return

    progress_bar.last_update = now
    percentage = (current / total) * 100
    completed_blocks = int(percentage // 10)
    remaining_blocks = 10 - completed_blocks
    bar = "█" * completed_blocks + "░" * remaining_blocks
    
    elapsed_time = now - start_time
    speed = current / elapsed_time / (1024 * 1024) if elapsed_time > 0 else 0
    current_mb = current / (1024 * 1024)
    total_mb = total / (1024 * 1024)

    status_text = (
        f"📤 **Uploading Your Media...**\n\n"
        f"🌀 **Progress:** `[{bar}] {percentage:.1f}%`\n"
        f"📦 **Size:** `{current_mb:.2f} MB` / `{total_mb:.2f} MB`\n"
        f"⚡ **Speed:** `{speed:.2f} MB/s` (⚡ TgCrypto Active)"
    )
    
    try:
        await status_message.edit_text(status_text)
    except Exception:
        pass

@app.on_message(filters.command("start"))
async def start_command(client, message):
    await message.reply_text("👋 Bot ready hai! Mujhe Mega link bhejiye, main fast speed (Tgcrypto) aur metadata ke sath upload karunga.")

@app.on_message(filters.regex(r"https://mega\.nz/"))
async def handle_mega_link(client, message):
    url = message.text.strip()
    status_message = await message.reply_text("🔄 Mega link mil gaya! Link check ho raha hai...")

    final_url = convert_mega_url(url)
    download_dir = "./downloads"
    file_path = None
    thumb_path = None

    try:
        if not os.path.exists(download_dir):
            os.makedirs(download_dir)

        await status_message.edit_text("📥 Koyeb server me Mega se file download ho rahi hai...")
        
        mega = Mega()
        m = mega.login() 
        
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = asyncio.get_event_loop()
            
        # 1. Download Thumbnail
        try:
            thumb_path = await loop.run_in_executor(None, lambda: m.download_thumbnail(final_url, dest_path=download_dir))
            if isinstance(thumb_path, list) and len(thumb_path) > 0:
                thumb_path = thumb_path[0]
        except Exception:
            thumb_path = None

        # 2. Download File
        file_path = await loop.run_in_executor(None, lambda: m.download_url(final_url, dest_path=download_dir))
        if isinstance(file_path, list):
            file_path = file_path[0] if len(file_path) > 0 else None

        if not file_path or not os.path.exists(str(file_path)):
            await status_message.edit_text("❌ Error: File download nahi ho saki.")
            return

        file_size = os.path.getsize(str(file_path)) / (1024 * 1024)
        start_time = time.time()
        file_name = str(file_path).lower()
        
        # 3. HACHOIR METADATA EXTRACTION FOR VIDEO
        duration = 0
        width = 320
        height = 180
        
        if file_name.endswith(('.mp4', '.mkv', '.webm', '.avi')):
            try:
                metadata = extractMetadata(createParser(str(file_path)))
                if metadata:
                    if metadata.has("duration"):
                        duration = metadata.get('duration').seconds
                    if metadata.has("width"):
                        width = metadata.get('width')
                    if metadata.has("height"):
                        height = metadata.get('height')
            except Exception:
                pass # metadata na mile to default zero rahega, bot crash nahi hoga
            
            await status_message.edit_text(f"📤 Video upload ho rahi hai... Size: {file_size:.2f} MB")
            
            video_thumb = str(thumb_path) if thumb_path and os.path.exists(str(thumb_path)) else None
            
            await client.send_video(
                chat_id=message.chat.id, 
                video=str(file_path),
                duration=duration,     # Hachoir metadata injection
                width=width,           # Hachoir metadata injection
                height=height,         # Hachoir metadata injection
                thumb=video_thumb,     
                caption=f"✅ **Aapki Video Taiyar Hai!**\n📦 **Size:** {file_size:.2f} MB",
                supports_streaming=True,
                progress=progress_bar,
                progress_args=(status_message, start_time)
            )
        elif file_name.endswith(('.jpg', '.jpeg', '.png', '.webp')):
            await status_message.edit_text(f"📤 Photo upload ho rahi hai...")
            await client.send_photo(chat_id=message.chat.id, photo=str(file_path), caption="✅ **Photo Uploaded!**")
        else:
            await status_message.edit_text(f"📤 Document file upload ho rahi hai...")
            await client.send_document(
                chat_id=message.chat.id, 
                document=str(file_path), 
                caption=f"✅ **File Uploaded!**\n📦 **Size:** {file_size:.2f} MB",
                progress=progress_bar,
                progress_args=(status_message, start_time)
            )
        
        await status_message.delete()

    except Exception as e:
        await status_message.edit_text(f"❌ Error: {str(e)}")
    
    finally:
        # Cleanup code for Koyeb disk management
        if file_path and os.path.exists(str(file_path)):
            try: os.remove(str(file_path))
            except Exception: pass
        if thumb_path and os.path.exists(str(thumb_path)):
            try: os.remove(str(thumb_path))
            except Exception: pass

if __name__ == "__main__":
    t = Thread(target=run_flask)
    t.daemon = True
    t.start()
    
    print("🚀 Starting Bot on Koyeb...")
    app.run()
