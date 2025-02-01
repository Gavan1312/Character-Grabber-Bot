from pyrogram import filters
from Grabber import application, user_collection
from . import app as bot, BOT_USERNAME, OWNER_ID
from pyrogram.types import Message
from html import escape
from telegram.ext import CommandHandler
from .block import block_dec
from .block import capsify
from pyrogram.types import InlineKeyboardButton as IKB, InlineKeyboardMarkup as IKM
from Grabber.utils.realuserdetails import *

XP_PER_LEVEL = 10

LEVEL_TITLES = {
    (0, 10): "💫 Novice",
    (11, 30): "✨ Dreamer",
    (31, 50): "⚡️ Spark",
    (51, 75): "🔥 Fiery",
    (76, 100): "💖 Knight",
    (101, 125): "🏆 Champion",
    (126, 150): "🛡 Guardian",
    (151, 175): "🏅 Hero",
    (176, 200): "👑 Emperor",
    (201, 2000): "🏰 Sovereign",
}

def calculate_level(xp):
    return xp // XP_PER_LEVEL

def get_user_level_title(user_level):
    for level_range, title in LEVEL_TITLES.items():
        if level_range[0] <= user_level <= level_range[1]:
            return title
    return "👤 Hacker"

@bot.on_message(filters.command(["xp"]))
@block_dec
async def check_stats(_, message: Message):
    user_id = message.from_user.id
    replied_user_id = None
    
    if message.reply_to_message:
        replied_user_id = message.reply_to_message.from_user.id
    
    if replied_user_id:
        user_id = replied_user_id
    
    user_data = await user_collection.find_one({'id': user_id})
    
    if not user_data:
        # return await message.reply_text("You need to start the bot first.")
        return await message.reply_text(
            capsify(f"🚀 {get_user_full_name(user_id)}, You haven't started your journey yet, You need to start the bot first in DM. click the button below to Set on a new journey 🎊"),
            reply_markup=IKM([
                [IKB(capsify("Start in DM"), url=f"https://t.me/{BOT_USERNAME}?start=start")]
            ])
        )
    
    user_xp_data = await user_collection.find_one({'id': user_id})
    
    if user_xp_data:
        user_xp = user_xp_data.get('xp', 0)
        user_level = user_xp // XP_PER_LEVEL
        user_level_title = get_user_level_title(user_level)
        first_name = user_data.get('first_name', 'User')

        # Calculate the XP required for the next level
        next_level_xp = (user_level + 1) * XP_PER_LEVEL
        xp_needed_for_next_level = next_level_xp - user_xp
        
        # Calculate the number of filled segments for the progress bar (10 segments total)
        progress_bar_length = 10
        unfilled_segments = ((next_level_xp - user_xp) * progress_bar_length) // XP_PER_LEVEL
        progress_bar = "■" * (progress_bar_length - unfilled_segments) + "□" * (unfilled_segments)

        # Send the formatted message
        await message.reply_text(f"{first_name} is a {user_level_title} at level {user_level} with {user_xp} XP.\n"
                                f"[{progress_bar}] ({xp_needed_for_next_level} XP needed for next level.)")

    else:
        await message.reply_text("You don't have any XP yet.")

async def xtop(update, context):
    top_users = await user_collection.find({}, projection={'id': 1, 'first_name': 1, 'last_name': 1, 'xp': 1}).sort('xp', -1).limit(10).to_list(10)
    top_users_message = "Top 10 XP Users:\n───────────────────\n"
    
    for i, user in enumerate(top_users, start=1):
        first_name = user.get('first_name', 'Unknown')
        last_name = user.get('last_name', '')
        user_id = user.get('id', 'Unknown')
        full_name = f"{first_name} {last_name}" if last_name else first_name
        user_link = f"<a href='tg://user?id={user_id}'>{escape(first_name)}</a>"
        # top_users_message += f"{i}. {user_link} - ({user.get('xp', 0):,.0f} xp)\n"
        top_users_message += f"{i}. {user_link} - (Level {user.get('xp', 0)// XP_PER_LEVEL})\n"
    
    # top_users_message += "────────────────────\nTop 10 Users via @Character_Grabber_Game_bot"
    top_users_message += "────────────────────\n💟 @Character_Grabber_Game_bot"
    # photo_path = 'https://telegra.ph/file/0dd6484b96c63f06379ef.jpg'
    # await update.message.reply_photo(photo=photo_path, caption=top_users_message, parse_mode='HTML')
    await update.message.reply_text(top_users_message, parse_mode='HTML')

async def add_xp(user_id, xp_amount):
    await user_collection.update_one({'id': user_id}, {'$inc': {'xp': xp_amount}}, upsert=True)

async def deduct_xp(user_id, xp_amount):
    await user_collection.update_one({'id': user_id}, {'$inc': {'xp': -xp_amount}}, upsert=True)


@bot.on_message(filters.command("add_xp_by_owner") & (filters.user(OWNER_ID)))
async def add_xp_by_owner(client, message: Message):
    user_id = None
    xp_amount = 0
    if message.reply_to_message:
        user_id = message.reply_to_message.from_user.id
        xp_amount = int(message.text.split()[1])
    else:
        try:
            user_id = int(message.text.split()[1])
            xp_amount = int(message.text.split()[2])
        except Exception:
            return await message.reply_text(capsify('Either reply to a user or provide an ID.'))
    try:
        await add_xp(user_id, xp_amount)
        return await message.reply_text(f"{xp_amount} XP Added Successfully.")
    except Exception:
        return await message.reply_text(capsify('Please provide xp amount.or user id'))

@bot.on_message(filters.command("deduct_xp_by_owner") & (filters.user(OWNER_ID)))
async def deduct_xp_by_owner(client, message: Message):
    user_id = None
    xp_amount = 0
    if message.reply_to_message:
        user_id = message.reply_to_message.from_user.id
        xp_amount = int(message.text.split()[1])
    else:
        try:
            user_id = int(message.text.split()[1])
            xp_amount = int(message.text.split()[2])
        except Exception:
            return await message.reply_text(capsify('Either reply to a user or provide an ID.'))
    try:
        await deduct_xp(user_id, xp_amount)
        await message.reply_text(f"{xp_amount} XP Deducted Successfully.")
    except Exception:
        return await message.reply_text(capsify('Please provide xp amount. or user id'))

from pyrogram.types import ReplyKeyboardRemove

@bot.on_message(filters.command("levels_text"))
async def send_levels(client, message: Message):
    levels_message = ""
    levels_title = "𝐿𝑒𝑣𝑒𝑙𝑠\n.........................................\n\n"
    levels_content = capsify(
        "- 💫 Novice (0, 10)\nNew to the world of love and affection.\n\n"
        "- ✨ Dreamer (11, 30)\nA heart full of potential and desires.\n\n"
        "- ⚡️ Spark (31, 50)\nElectric chemistry, igniting passions.\n\n"
        "- 🔥 Fiery (51, 75)\nBurning with determination and love.\n\n"
        "- 💖 Knight (76, 100)\nA protector of hearts, always devoted.\n\n"
        "- 🏆 Champion (101, 125)\nChampion of hearts, admired by all.\n\n"
        "- 🛡 Guardian (126, 150)\nA gentle guardian, shielding love with care.\n\n"
        "- 🏅 Hero (151, 175)\nA true hero, winning hearts with kindness.\n\n"
        "- 👑 Emperor (176, 200)\nRuler of hearts, commanding affection.\n\n"
        "- 🏰 Sovereign (201, 2000)\nThe supreme ruler of love, cherished by all."
    )
    levels_footer = capsify(
        "\n\nUse Explore, Crime, and play minigames like, basket, lever, gamble, dart to gain levels\n"
        "To see the top users by use \\xtop"
    )
    levels_message = levels_title + levels_content + levels_footer
    
    # Send message with restrictions (no forwarding, no web page preview)
    await message.reply_text(
        levels_message,
        disable_web_page_preview=True,
        reply_markup=ReplyKeyboardRemove()  # This prevents sharing the message through reply options
    )

application.add_handler(CommandHandler("xptop", xtop, block=False))