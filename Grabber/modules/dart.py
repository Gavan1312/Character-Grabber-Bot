from pyrogram import filters, types as t
import random
import time
import asyncio
from pyrogram import Client
from Grabber import user_collection
from . import add, deduct, show, app
from .block import block_dec, temp_block
from .xp import add_xp, deduct_xp

cooldown_duration_roll = 30
last_usage_time_roll = {}

@app.on_message(filters.command(["dart"]))
@block_dec
async def roll_dart(client: Client, message: t.Message):
    user_id = message.from_user.id
    if temp_block(user_id):
        return
    current_time = time.time()

    if not await user_collection.find_one({'id': user_id}):
        await message.reply("You need to grab some Characters first.")
        return

    if user_id in last_usage_time_roll:
        time_elapsed = current_time - last_usage_time_roll[user_id]
        remaining_time = max(0, cooldown_duration_roll - time_elapsed)
        if remaining_time > 0:
            return await message.reply_text(f"You're on cooldown. Please wait {int(remaining_time)} seconds.")

    command_parts = message.text.split()
    if len(command_parts) != 2:
        return await message.reply_text("Invalid command.\nUsage: /dart 10000")

    try:
        dart_amount = int(command_parts[1].replace(',', ''))
    except ValueError:
        return await message.reply_text("Invalid amount.")

    bal = await show(user_id)
    if bal is None:
        return await message.reply_text("You don't have enough cash to place this bet.")

    if dart_amount > bal:
        return await message.reply_text("Insufficient Love Points to place this bet.")

    min_bet_amount = int(bal * 0.05)
    if dart_amount < min_bet_amount:
        return await message.reply_text(f"Please bet at least 5% of your Love Points, which is ₩{min_bet_amount}.")

    value = await client.send_dice(chat_id=message.chat.id, emoji="🎯")
    await asyncio.sleep(2)

    if value.dice.value == 6:
        reward_amount = dart_amount * 3
        await add(user_id, reward_amount)
        await message.reply_text(f"[🎯] You're lucky!\nYou won ₩{reward_amount}")
        await add_xp(user_id, 4)
    else:
        await deduct(user_id, dart_amount)
        await message.reply_text(f"[🎯] Better luck next time!\nYou lost ₩{dart_amount}")
        # await deduct_xp(user_id, 2)

    last_usage_time_roll[user_id] = current_time
