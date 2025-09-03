import os
import asyncio
from fastapi import FastAPI, Request
from pyrogram import Client, types
from dotenv import load_dotenv
import logging
from .music_player import play_music, stop_music

# Configure logging
logging.basicConfig(level=logging.INFO)

# Load environment variables
load_dotenv()
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")

app = FastAPI()
pyrogram_client = Client("my_music_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

@app.post(f"/webhook/{BOT_TOKEN}")
async def process_webhook(request: Request):
    update_data = await request.json()
    asyncio.create_task(handle_update(update_data))
    return {"status": "ok"}

async def handle_update(update_data: dict):
    # Pyrogram can handle raw updates.
    # Deserialize the update into a Pyrogram Update object
    update = types.Update.parse(update_data)
    
    if update.message:
        message = update.message
        if message.text and message.text.startswith('/play'):
            query = message.text.split(' ', 1)
            if len(query) > 1:
                await play_music(pyrogram_client, message, query[1])
            else:
                await pyrogram_client.send_message(message.chat.id, "Please provide a song to play.")
        elif message.text == '/stop':
            await stop_music(pyrogram_client, message)
    
@app.on_event("startup")
async def startup_event():
    await pyrogram_client.start()
    logging.info("Pyrogram client started.")
