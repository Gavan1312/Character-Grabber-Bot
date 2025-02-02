import requests
from pyrogram import Client, filters
from pyrogram.types import Message
from pymongo import ReturnDocument
import random
from . import uploader_filter, app, user_collection
from Grabber import collection, db, CHARA_CHANNEL_ID, OWNER_ID

@app.on_message(filters.command('rename_celestial_icon') & filters.user(OWNER_ID))
async def rename_celestial_icon(client: Client, message: Message):
    try:
        # Perform asynchronous updates
        result = await collection.update_many(
            {"rarity": "🎐 Celestial"},  # Filter
            {"$set": {"rarity": "🎐 Celestial"}}  # Update operation
        )

        result1 = await user_collection.update_many(
            {"characters.rarity": "🎐 Celestial"},  # Filter documents with matching rarity in characters array
            {"$set": {"characters.$[elem].rarity": "🎐 Celestial"}},  # Update operation
            array_filters=[{"elem.rarity": "🎐 Celestial"}]  # Array filter
        )

        # Send success message to the bot user
        await message.reply_text(
            f"Update completed successfully!\n\n"
            f"Characters Table:\n"
            f"- Matched Documents: {result.matched_count}\n"
            f"- Modified Documents: {result.modified_count}\n\n"
            f"User Collection:\n"
            f"- Matched Documents: {result1.matched_count}\n"
            f"- Modified Documents: {result1.modified_count}"
        )

    except Exception as e:
        # Send error message to the bot user
        await message.reply_text(f"An error occurred: {e}")

        
@app.on_message(filters.command('rename_rarity_icon') & filters.user(OWNER_ID))
async def rename_rarity_icon(client: Client, message: Message):
    try:
        # Extract old and new text from the message
        import re
        match = re.search(r"\((.*?)\)\s+\((.*?)\)", message.text)

        if not match:
            await message.reply_text("Please provide the old and new text for replacement in the format: /rename_celestial_icon (old text) (new text)")
            return

        old_text = match.group(1)
        new_text = match.group(2)

        # Perform asynchronous updates
        result = await collection.update_many(
            {"rarity": old_text},  # Filter
            {"$set": {"rarity": new_text}}  # Update operation
        )

        result1 = await user_collection.update_many(
            {"characters.rarity": old_text},  # Filter documents with matching rarity in characters array
            {"$set": {"characters.$[elem].rarity": new_text}},  # Update operation
            array_filters=[{"elem.rarity": old_text}]  # Array filter
        )

        # Send success message to the bot user
        await message.reply_text(
            f"Update completed successfully!\n\n"
            f"Characters Table:\n"
            f"- Matched Documents: {result.matched_count}\n"
            f"- Modified Documents: {result.modified_count}\n\n"
            f"User Collection:\n"
            f"- Matched Documents: {result1.matched_count}\n"
            f"- Modified Documents: {result1.modified_count}"
        )

    except Exception as e:
        # Send error message to the bot user
        await message.reply_text(f"An error occurred: {e}")
