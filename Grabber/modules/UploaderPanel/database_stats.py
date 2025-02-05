import requests
from pyrogram import Client, filters
from pyrogram.types import Message
from Grabber.modules import uploader_filter, app, user_collection
from Grabber import collection, db, CHARA_CHANNEL_ID, OWNER_ID

@app.on_message(filters.command('character_list_stats') & uploader_filter)
async def character_list_stats(client: Client, message: Message):
    pipeline = [
        {
            "$match": {
                "rarity": {"$exists": True, "$ne": None}  # Only include documents with a non-null rarity
            }
        },
        {
            "$group": {
                "_id": "$rarity",  # Group by rarity text
                "count": {"$sum": 1}  # Count occurrences of each rarity
            }
        }
    ]

    cursor = collection.aggregate(pipeline)  # Async cursor
    rarity_counts = await cursor.to_list(None)  # Convert cursor to list

    if not rarity_counts:
        await message.reply_text("No character rarity stats available.")
        return

    # Format the message text
    stats_message = "**Character Rarity Stats:**\n\n"
    for rarity in rarity_counts:
        stats_message += f"**{rarity['_id']}**: {rarity['count']} characters\n"

    # Send the message
    await message.reply_text(stats_message)