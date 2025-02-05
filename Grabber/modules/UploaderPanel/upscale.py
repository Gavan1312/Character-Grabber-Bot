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

async def upscale_image(client, message, keep_id=False):
    reply = message.reply_to_message
    if not reply or not reply.photo:
        return await message.reply("Reply to an image to upscale it.")
    
    progress = await message.reply("Upscaling your image, please wait...")
    image = await client.download_media(reply.photo.file_id)
    
    with open(image, "rb") as f:
        encoded = base64.b64encode(f.read()).decode("utf-8")
    
    async with aiohttp.ClientSession() as s:
        async with s.post("https://lexica.qewertyy.dev/upscale", data={"image_data": encoded}) as r:
            output_path = "upscaled_image.png"
            with open(output_path, "wb") as out:
                out.write(await r.read())
    
    await progress.delete()
    caption = ""
    
    if keep_id:
        image_id = get_caption_with_id(reply)
        if image_id:
            caption = f"id - {image_id}"
    else:
        caption = f"**Upscaled by @{client.me.username}**"
    
    await message.reply_photo(output_path, caption=caption if caption else None)
    os.remove(output_path)  # Clean up the file

@app.on_message(filters.command("upscale") & uploader_filter)
async def upscale_command(client, message):
    await upscale_image(client, message, keep_id=False)

@app.on_message(filters.command("upscalewithid") & uploader_filter)
async def upscale_with_id_command(client, message):
    await upscale_image(client, message, keep_id=True)