import requests
from pyrogram import Client, filters
from pyrogram.types import Message
from pymongo import ReturnDocument
import random
from . import uploader_filter, app, user_collection
from Grabber import collection, db, CHARA_CHANNEL_ID, OWNER_ID
from Grabber.modules.UploaderPanel.upload_catbox import upload_to_catbox

async def get_next_sequence_number(sequence_name):
    sequence_collection = db.sequences
    sequence_document = await sequence_collection.find_one_and_update(
        {'_id': sequence_name},
        {'$inc': {'sequence_value': 1}},
        return_document=ReturnDocument.AFTER
    )
    if not sequence_document:
        await sequence_collection.insert_one({'_id': sequence_name, 'sequence_value': 0})
        return 0
    return sequence_document['sequence_value']


rarity_map = {
    1: "🟢 Common",
    2: "🔵 Medium",
    3: "🟠 Rare",
    4: "🟡 Legendary",
    5: "🎐 Celestial",
    6: "🥵 Divine",
    7: "🥴 Special",
    8: "💮 Exclusive",
    9: "🔮 Limited",
    10: "🍭 Cosplay",
    11: "💋 Aura",
    12: "❄️ Winter",
    13: "⚡ Drip",
    14: "🍥 Retro"
}


@app.on_message(filters.command('upload') & uploader_filter)
async def upload(client: Client, message: Message):
    if not message.reply_to_message or not message.reply_to_message.photo:
        await message.reply_text("Please reply to an image with the caption in the format: 'Name - Name Here\nAnime - Anime Here\nRarity - Number'")
        return

    caption = message.reply_to_message.caption.strip().split("\n")
    if len(caption) != 3:
        await message.reply_text("Incorrect format. Please use the format: 'Name - Name Here\nAnime - Anime Here\nRarity - Number'")
        return

    try:
        character_name = caption[0].split(" - ")[1].strip().title()
        anime = caption[1].split(" - ")[1].strip().title()
        rarity_str = caption[2].split(" - ")[1].strip()
        rarity = rarity_map[int(rarity_str)]
    except (KeyError, ValueError, IndexError):
        await message.reply_text("Invalid format or rarity. Please use the format: 'Name - Name Here\nAnime - Anime Here\nRarity - Number' and ensure rarity is a number between 1 and 10.")
        return

    try:
        photo = await client.download_media(message.reply_to_message.photo)

        img_url = upload_to_catbox(photo)

        id = str(await get_next_sequence_number('character_id')).zfill(2)
        price = random.randint(60000, 80000)

        sent_message = await client.send_photo(
            chat_id=CHARA_CHANNEL_ID,
            photo=img_url,
            caption=(
                f'Waifu Name: {character_name}\n'
                f'Anime Name: {anime}\n'
                f'Quality: {rarity}\n'
                f'Price: {price}\n'
                f'ID: {id}\n'
                f'Added by {message.from_user.first_name}'
            )
        )

        character = {
            'img_url': img_url,
            'name': character_name,
            'anime': anime,
            'rarity': rarity,
            'price': price,
            'id': id,
            'message_id': sent_message.id
        }

        await collection.insert_one(character)
        await message.reply_text('WAIFU ADDED....')

    except Exception as e:
        await message.reply_text(f"An error occurred: {str(e)}")
  
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
