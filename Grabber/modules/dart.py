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
        return await message.reply_text(f"You don't have enough {currency_names_plural['balance']} to throw a dart.")

    if dart_amount > bal:
        return await message.reply_text(f"Insufficient {currency_names_plural['balance']} to throw a dart.")

    min_bet_amount = int(bal * 0.05)
    if dart_amount < min_bet_amount:
        return await message.reply_text(f"Please bet at least 5% of your {currency_names_plural['balance']}, which is {currency_symbols['balance']}{min_bet_amount}.")

    value = await client.send_dice(chat_id=message.chat.id, emoji="🎯")
    await asyncio.sleep(2)

    dice_result = value.dice.value  # Telegram returns a number between 1-6

    if dice_result == 6:  # Perfect shot!
        reward_amount = dart_amount * 3
        await add(user_id, reward_amount)
        await message.reply_text(f"[🎯] **Bullseye!** 🎯\nYou won {currency_symbols['balance']}{reward_amount}!")
        await add_xp(user_id, 5)
    elif dice_result in [4, 5]:  # Good shot!
        reward_amount = int(dart_amount * 1.5)
        await add(user_id, reward_amount)
        await message.reply_text(f"[🎯] **Great shot!** ✨\nYou won {currency_symbols['balance']}{reward_amount}!")
        await add_xp(user_id, 3)
    else:  # 1, 2, 3 = Miss
        await deduct(user_id, dart_amount)
        await message.reply_text(f"[🎯] **Missed the target!** 😢\nYou lost {currency_symbols['balance']}{dart_amount}.")
        # await deduct_xp(user_id, 2)  # Optional XP loss

    last_usage_time_roll[user_id] = current_time
