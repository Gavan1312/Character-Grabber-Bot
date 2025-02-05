'''import random
import io
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton as IKB, InlineKeyboardMarkup as IKM
from Grabber.modules.block import block_cbq
from Grabber.modules.Utility.image_utils import generate_random_math_image

from Grabber import user_collection, collection
from Grabber.modules import add, deduct, show, abank, dbank, sbank, sudb, capsify, app, sudo_filter, group_user_totals_collection
from Grabber.modules.watchers import delta_watcher
from Grabber.utils.sudo import *

@app.on_message(filters.command("stime") & sudo_filter)
async def set_message_limit(client, message):
    # sudo_user_ids = await get_sudo_user_ids()
    # user_id = message.from_user.id
    # if user_id not in sudo_user_ids:
    #     await message.reply_text(capsify("Only sudo users can set the message limit!"))
    #     return
    try:
        limit = int(message.command[1])
        if limit <= 0:
            await message.reply_text(capsify("Message limit must be a positive integer!"))
            return

        group_message_counts[message.chat.id] = {'count': 0, 'limit': limit}
        await message.reply_text(capsify(f"Message limit set to {limit}. Now spawning math equations every {limit} messages!"))
    except (IndexError, ValueError):
        await message.reply_text(capsify("Please provide a valid message limit (integer)."))


async def set_message_limit(client: Client, message):
    # sudo_user_ids = await get_sudo_user_ids()
    # user_id = message.from_user.id
    # if user_id not in sudo_user_ids:
    #     await message.reply("Only sudo users can set the message limit!")
    #     return
    try:
        limit = int(message.command[1])
        if limit <= 0:
            await message.reply("Message limit must be a positive integer!")
            return

        group_message_counts[message.chat.id] = {'count': 0, 'limit': limit}
        await message.reply(f"Message limit set to {limit}. Now spawning images every {limit} messages!")
    except (IndexError, ValueError):
        await message.reply("Please provide a valid message limit (integer).")


@app.on_message(filters.command("wtime") & sudo_filter)
async def on_wtime(client: Client, message):
    await set_message_limit(client, message)
'''