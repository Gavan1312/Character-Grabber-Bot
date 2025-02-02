import requests
from pyrogram import Client, filters
from pyrogram.types import Message
from pymongo import ReturnDocument, UpdateOne
from Grabber.modules import uploader_filter, app, user_collection
from Grabber import collection, db, CHARA_CHANNEL_ID, OWNER_ID
from Grabber.modules.UploaderPanel.upload_catbox import upload_to_catbox

@app.on_message(filters.command('update_image') & uploader_filter)
async def update_image(client: Client, message: Message):
    if not message.reply_to_message or not message.reply_to_message.photo:
        await message.reply_text("Please reply to an image with the caption in the format: '\nId - Id number Here'")
        return

    caption = message.reply_to_message.caption.strip().split("\n")
    if len(caption) != 1:
        await message.reply_text("Incorrect format. Please use the format: '\nId - Id number Here'")
        return

    try:
        character_id_number = caption[0].split(" - ")[1].strip().title()
    except (KeyError, ValueError, IndexError):
        await message.reply_text("Invalid format. Please use the format: '\nId - Id number Here")
        return

    try:
        photo = await client.download_media(message.reply_to_message.photo)
        new_img_url = upload_to_catbox(photo)        
        character = await collection.find_one({'id': character_id_number})
        if not character:
            await message.reply_text('Character not found.')
            return
        
        await collection.update_one({'id': character_id_number}, {'$set': {'img_url': new_img_url}})
        
        bulk_operations = []
        async for user in user_collection.find():
            if 'characters' in user:
                for char in user['characters']:
                    if char['id'] == character_id_number:
                        char['img_url'] = new_img_url
                bulk_operations.append(
                    UpdateOne({'_id': user['_id']}, {'$set': {'characters': user['characters']}})
                )

        if bulk_operations:
            await user_collection.bulk_write(bulk_operations)
        
    except Exception as e:
        await message.reply_text(f"An error occurred: {str(e)}")
        return
    
    await message.reply_text('Update done in Database and all user collections.')