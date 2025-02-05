import requests
from pyrogram import Client, filters
from pyrogram.types import Message
from pymongo import ReturnDocument
import random
from . import uploader_filter, app, user_collection
from Grabber import collection, db, CHARA_CHANNEL_ID, OWNER_ID
from Grabber.modules.UploaderPanel.upload_catbox import upload_to_catbox
from Grabber.modules.Settings.rarityMap import *
from Grabber.modules.UploaderPanel.upscale import process_upscale

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

rarity_map = RARITY_TO_USE_NUMBER_MAPPING

def parse_caption(caption_text):
    caption = caption_text.strip().split("\n")
    if len(caption) != 3:
        return None, None, None
    
    try:
        character_name = caption[0].split(" - ")[1].strip().title()
        anime = caption[1].split(" - ")[1].strip().title()
        rarity_str = caption[2].split(" - ")[1].strip()
        rarity = rarity_map[int(rarity_str)]
        return character_name, anime, rarity
    except (KeyError, ValueError, IndexError):
        return None, None, None

async def upload_character(client, message, img_url, character_name, anime, rarity):
    id = str(await get_next_sequence_number('character_id')).zfill(2)
    # price = random.randint(60000, 80000)
    user_link = f'[{message.from_user.first_name}](tg://user?id={message.from_user.id})'
    
    sent_message = await client.send_photo(
        chat_id=CHARA_CHANNEL_ID,
        photo=img_url,
        caption=(
            f'**Waifu Name:** {character_name}\n'
            f'**Anime Name:** {anime}\n'
            f'**Quality:** {rarity}\n'
            # f'**Price: {price}\n'
            f'**ID:** {id}\n'
            f'**Added by:** {user_link}'
        )
    )

    character = {
        'img_url': img_url,
        'name': character_name,
        'anime': anime,
        'rarity': rarity,
        # 'price': price,
        'id': id,
        'message_id': sent_message.id
    }

    await collection.insert_one(character)
    await message.reply_text('WAIFU ADDED....')

@app.on_message(filters.command('upload') & uploader_filter)
async def upload(client: Client, message: Message):
    if not message.reply_to_message or not message.reply_to_message.photo:
        await message.reply_text("Please reply to an image with the caption in the format: 'Name - Name Here\nAnime - Anime Here\nRarity - Number'")
        return

    character_name, anime, rarity = parse_caption(message.reply_to_message.caption)
    if not character_name:
        await message.reply_text("Incorrect format or invalid rarity. Please use the format: 'Name - Name Here\nAnime - Anime Here\nRarity - Number'")
        return

    try:
        photo = await client.download_media(message.reply_to_message.photo)
        img_url = upload_to_catbox(photo)
        await upload_character(client, message, img_url, character_name, anime, rarity)
    except Exception as e:
        await message.reply_text(f"An error occurred: {str(e)}")

@app.on_message(filters.command(['upload_with_upscale','upload_with_quality']) & uploader_filter)
async def upload_with_upscale(client: Client, message: Message):
    if not message.reply_to_message or not message.reply_to_message.photo:
        await message.reply_text("Please reply to an image with the caption in the format: 'Name - Name Here\nAnime - Anime Here\nRarity - Number'")
        return

    character_name, anime, rarity = parse_caption(message.reply_to_message.caption)
    if not character_name:
        await message.reply_text("Incorrect format or invalid rarity. Please use the format: 'Name - Name Here\nAnime - Anime Here\nRarity - Number'")
        return

    try:
        photo = await client.download_media(message.reply_to_message.photo)
        upscaled_photo = await process_upscale(photo)
        img_url = upload_to_catbox(upscaled_photo)
        await upload_character(client, message, img_url, character_name, anime, rarity)
    except Exception as e:
        await message.reply_text(f"An error occurred: {str(e)}")
        
        
@app.on_message(filters.command('character_list_stats') & uploader_filter)
async def character_list_stats(client: Client, message: Message):
    pipeline = [
        {
            "$group": {
                "_id": "$rarity",  # Group by rarity
                "count": {"$sum": 1}  # Count the number of occurrences of each rarity
            }
        }
    ]
    rarity_counts = list(collection.aggregate(pipeline))

    # Format the message text
    stats_message = "**Character Rarity Stats:**\n"
    for rarity in rarity_counts:
        stats_message += f"**{rarity['_id']}**: {rarity['count']} characters\n"

    # Send the message
    await message.reply_text(stats_message)
