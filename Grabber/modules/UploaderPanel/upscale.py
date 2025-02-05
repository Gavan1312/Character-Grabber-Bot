from pyrogram import Client, filters
import base64
import aiohttp
from Grabber.modules import app, uploader_filter

@app.on_message(filters.command("upscale") & uploader_filter)
async def upscale_image(client, message):
    #3.7 for glitch
    reply = message.reply_to_message
    if not reply or not reply.photo:
        return await message.reply("Reply to an image to upscale it.")
    
    progress = await message.reply("Upscaling your image, please wait...")
    
    image = await client.download_media(reply.photo.file_id)
    
    with open(image, "rb") as f:
        encoded = base64.b64encode(f.read()).decode("utf-8")
    
    async with aiohttp.ClientSession() as s:
        async with s.post("https://lexica.qewertyy.dev/upscale", data={"image_data": encoded}) as r:
            with open("upscaled_image.png", "wb") as out:
                out.write(await r.read())
    
    await progress.delete()
    await message.reply_photo("upscaled_image.png", caption=f"**Upscaled by @{client.me.username}**")