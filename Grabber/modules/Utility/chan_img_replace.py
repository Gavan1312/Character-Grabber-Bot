from Grabber.modules import app
from Grabber.config import *
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.errors import ChatAdminRequired

channel_id = CHARA_CHANNEL_ID  # Ensure this is a valid numeric ID
CHUNK_SIZE = 4096  # Telegram's message limit
 # Replace with your channel ID
 

@app.on_message(filters.command('db_channel_bot_permission'))
async def check_bot_permissions(client, message):
    try:
        # Check if the bot is an admin in the channel
        bot_permissions = await client.get_chat_member(channel_id, client.me.id)
        if bot_permissions.status in ["administrator", "member"]:
            await message.reply("Bot has necessary permissions.")
        else:
            await message.reply("Bot is not an admin in the channel.")
    except ChatAdminRequired:
        await message.reply("Bot is not an admin in the channel.")


# Function to process messages
async def process_messages():
    # Fetch messages asynchronously
    async for msg in app.get_chat_history(chat_id=channel_id, limit=100):
        if msg.photo and msg.caption:
            caption = msg.caption
            print("\nCaption Found:", caption)

            # Extract details using basic parsing
            lines = caption.split("\n")
            details = {line.split(":")[0].strip(): line.split(":")[1].strip() for line in lines if ":" in line}

            print(details)  # Dictionary of extracted data

# Command handler to trigger message processing
@app.on_message(filters.command('db_channel_fetch_characters'))
async def fetch_characters(client, message):
    # Directly call the function within the running loop
    await process_messages()
    await message.reply("Character details have been processed.")  # Optional response

