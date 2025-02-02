import requests
from pyrogram import filters
from . import app
from Grabber.modules.UploaderPanel.upload_catbox import upload_to_catbox

@app.on_message(filters.command("tgm"))
def ul(_, message):
    reply = message.reply_to_message
    if not reply or not reply.media:
        return message.reply("Please reply to an image or media to upload.")

    i = message.reply("**Downloading...**")
    path = reply.download()

    if not path:
        return i.edit("Failed to download the file.")

    try:
        file_url = upload_to_catbox(path)
        i.edit(f'Your Catbox [link]({file_url})', disable_web_page_preview=True)
    except Exception as e:
        i.edit(f"An error occurred: {str(e)}")