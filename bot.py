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
import shutil
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

@app.on_message(filters.command("start"))
async def start_command(client, message):
    await message.reply_text("👋 Bot ready hai! Mujhe Mega file ya folder ka link bhejiye, main saari videos bhej dunga.")

@app.on_message(filters.regex(r"https://mega\.nz/(file|folder)/"))
async def handle_mega_link(client, message):
    url = message.text
    status_message = await message.reply_text("🔄 Mega link mil gaya! Folder/File check ho rahi hai...")

    try:
        # Har request ke liye unique folder taaki files mix na hon
        user_download_dir = f"./downloads_{message.id}"
        if not os.path.exists(user_download_dir):
            os.makedirs(user_download_dir)

        await status_message.edit_text("📥 Mega se downloading shuru ho gayi hai... (Folder me thoda time lag sakta hai)")
        
        mega = Mega()
        m = mega.login() 
        
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = asyncio.get_event_loop()
            
        # Download folder or file
        downloaded_paths = await loop.run_in_executor(None, lambda: m.download_url(url, dest_path=user_download_dir))
        
        # Agar single file hai toh use bhi list me convert kar dete hain loop chalane ke liye
        if not isinstance(downloaded_paths, list):
            downloaded_paths = [downloaded_paths]

        await status_message.edit_text(f"📤 Download complete! Total {len(downloaded_paths)} files mili hain. Uploading shuru...")

        # Loop chalakar ek-ek karke saari files upload karenge
        file_count = 1
        for file_path in downloaded_paths:
            # Agar folder ke andar subfolder ho toh file_path ko check karna zaroori hai
            if os.path.isfile(file_path):
                file_name = os.path.basename(file_path)
                await status_message.edit_text(f"📤 Uploading file {file_count}/{len(downloaded_paths)}:\n`{file_name}`")
                
                await client.send_document(
                    chat_id=message.chat.id, 
                    document=file_path,
                    caption=f"✅ Part {file_count}: {file_name}"
                )
                file_count += 1
                
                # Upload hote hi file delete karein taaki server space full na ho
                os.remove(file_path)

        await status_message.delete()
        
        # Poora temporary folder delete karein
        if os.path.exists(user_download_dir):
            shutil.rmtree(user_download_dir)

    except Exception as e:
        await status_message.edit_text(f"❌ Error: {str(e)}")
        if 'user_download_dir' in locals() and os.path.exists(user_download_dir):
            shutil.rmtree(user_download_dir)

if __name__ == "__main__":
    t = Thread(target=run_flask)
    t.daemon = True
    t.start()
    
    print("🚀 Starting Folder Supported Bot on Koyeb...")
    app.run()
