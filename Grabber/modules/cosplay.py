import requests
from pyrogram import filters
from pyrogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram.enums import ChatAction
from . import app
from .block import *
from Grabber.config import * 

@app.on_message(filters.command("cosplay"))
@block_dec 
async def cosplay(_, msg):
    user_id = msg.from_user.id
    if temp_block(user_id):
        return
    bot_info = await app.get_me()
    bot_username = bot_info.username

    DRAGONS = [
        [
            InlineKeyboardButton(text="ᴀᴅᴅ ᴍᴇ ʙᴀʙʏ!", url=f"https://t.me/{bot_username}?startgroup=true"),
            InlineKeyboardButton(text="ᴊᴏɪɴ ɢʀᴏᴜᴘ", url=f"https://t.me/{SUPPORT_CHAT}"),
        ],
    ]

    img = requests.get("https://waifu-api.vercel.app").json()
    await msg.reply_photo(img, caption=f"❅ ᴄᴏsᴘʟᴀʏ ʙʏ ➠ ๛𝓛𝓪𝓾𝓰𝓱𝓽𝓪𝓵𝓮 𝓜𝓮𝓶𝓫𝓮𝓻𝓼 ༗", reply_markup=InlineKeyboardMarkup(DRAGONS))

