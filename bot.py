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
import re
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

# 🔴 YAHAN APNI TELEGRAM ID DAALEIN (Bina quotes ke, sirf number)
# Is ID par bot restart hone ka message jayega
ADMIN_ID = 8391386178  

app = Client("mega_downloader_koyeb", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

@app.on_message(filters.command("start"))
async def start_command(client, message):
    await message.reply_text("👋 Bot ready hai! Mujhe Mega file/folder ka link bhejiye, main saari videos bhej dunga.")

@app.on_message(filters.regex(r"https://mega\.nz/(file|folder|#F!|#)!?[\w\-_]+"))
async def handle_mega_link(client, message):
    match = re.search(r"(https://mega\.nz/[^\s]+)", message.text)
    if not match:
        await message.reply_text("❌ Sahi Mega link nahi mila!")
        return
        
    url = match.group(1)
    status_message = await message.reply_text("🔄 Mega link mil gaya! Link aur Key check ho rahi hai...")

    try:
        user_download_dir = f"./downloads_{message.id}"
        if not os.path.exists(user_download_dir):
            os.makedirs(user_download_dir)

        await status_message.edit_text("📥 Mega se downloading shuru ho gayi hai... (Thoda wait karein)")
        
        mega = Mega()
        m = mega.login() 
        
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = asyncio.get_event_loop()
            
        downloaded_paths = await loop.run_in_executor(None, lambda: m.download_url(url, dest_path=user_download_dir))
        
        if not downloaded_paths:
            raise Exception("Mega ne koi file download nahi ki. Link check karein.")

        if not isinstance(downloaded_paths, list):
            downloaded_paths = [downloaded_paths]

        await status_message.edit_text(f"📤 Download complete! Total {len(downloaded_paths)} files mili hain. Uploading...")

        file_count = 1
        for file_path in downloaded_paths:
            if os.path.isfile(file_path):
                file_name = os.path.basename(file_path)
                await status_message.edit_text(f"📤 Uploading file {file_count}/{len(downloaded_paths)}:\n`{file_name}`")
                
                await client.send_document(
                    chat_id=message.chat.id, 
                    document=file_path,
                    caption=f"✅ Part {file_count}: {file_name}"
                )
                file_count += 1
                os.remove(file_path)

        await status_message.delete()
        
        if os.path.exists(user_download_dir):
            shutil.rmtree(user_download_dir)

    except Exception as e:
        error_msg = str(e)
        if "Url key missing" in error_msg:
            await status_message.edit_text("❌ **Error: Url key missing**\n\nPura link copy karke bhejiye.")
        else:
            await status_message.edit_text(f"❌ Error: {error_msg}")
            
        if 'user_download_dir' in locals() and os.path.exists(user_download_dir):
            shutil.rmtree(user_download_dir)

# --- BOT RESTART ALERT FUNCTION ---
async def start_bot():
    # Flask web server ko background me chalu karein
    t = Thread(target=run_flask)
    t.daemon = True
    t.start()
    
    print("🚀 Starting Bot on Koyeb...")
    await app.start()
    
    # Bot start hote hi Admin ko message bhejega
    try:
        await app.send_message(chat_id=ADMIN_ID, text="🔄 **Bot successfully restart ho gaya hai!**")
        print("✅ Restart alert sent to Admin.")
    except Exception as e:
        print(f"⚠️ Could not send restart alert: {str(e)}")
        
    await asyncio.Event().wait()

if __name__ == "__main__":
    # Pyrogram ko custom start function ke sath run karne ke liye
    app.run(start_bot())
