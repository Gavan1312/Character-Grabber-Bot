from pyrogram import Client, filters
import base64
import aiohttp
import os
from Grabber.modules import app, uploader_filter

def get_caption_with_id(message):
    """Extracts the ID from the caption if present."""
    if message.caption and "id - " in message.caption.lower():
        return message.caption.split("id - ")[-1].strip()
    return None

def get_caption_with_details(message):
    """Extracts name, anime, and rarity details from the caption."""
    if message.caption:
        return message.caption.strip()
    return None

async def process_upscale(image_path):
    """Handles the actual image upscaling."""
    with open(image_path, "rb") as f:
        encoded = base64.b64encode(f.read()).decode("utf-8")
    
    async with aiohttp.ClientSession() as s:
        async with s.post("https://lexica.qewertyy.dev/upscale", data={"image_data": encoded}) as r:
            output_path = "upscaled_image.png"
            with open(output_path, "wb") as out:
                out.write(await r.read())
    return output_path

async def upscale_image(client, message, caption_type=None):
    reply = message.reply_to_message
    if not reply or not reply.photo:
        return await message.reply("Reply to an image to upscale it.")
    
    progress = await message.reply("Upscaling your image, please wait...")
    image = await client.download_media(reply.photo.file_id)
    output_path = await process_upscale(image)
    
    await progress.delete()
    caption = ""
    
    if caption_type == "id":
        image_id = get_caption_with_id(reply)
        if image_id:
            caption = f"ID - {image_id}"
    elif caption_type == "details":
        details = get_caption_with_details(reply)
        if details:
            caption = details
    else:
        caption = f"**Upscaled by @{client.me.username}**"
    
    await message.reply_photo(output_path, caption=caption if caption else None)
    os.remove(output_path)  # Clean up the file

@app.on_message(filters.command("upscale") & uploader_filter)
async def upscale_command(client, message):
    await upscale_image(client, message)

@app.on_message(filters.command("upscalewithid") & uploader_filter)
async def upscale_with_id_command(client, message):
    await upscale_image(client, message, caption_type="id")

@app.on_message(filters.command("upscale_with_details") & uploader_filter)
async def upscale_with_details_command(client, message):
    await upscale_image(client, message, caption_type="details")
