from pyrogram import filters, types as t
import random
import time
import asyncio
from pyrogram import Client
from Grabber import user_collection
from . import add, deduct, show, app
from .block import block_dec, temp_block
from .xp import add_xp
from Grabber.config_settings import * 

cooldown_duration_roll = 180
last_usage_time_roll = {}

@app.on_message(filters.command(["lever"]))
@block_dec
async def roll_dart(client: Client, message: t.Message):
    user_id = message.from_user.id
    if temp_block(user_id):
        return

    current_time = time.time()

    if not await user_collection.find_one({'id': user_id}):
        await message.reply("You need to grab some characters first.")
        return

    command_parts = message.text.split()
    if len(command_parts) != 2:
        return await message.reply_text("Invalid command.\nUsage: /lever 99999")

    try:
        slot_amount = int(command_parts[1].replace(',', ''))
    except ValueError:
        return await message.reply_text("Invalid amount.")

    bal = await show(user_id)
    if bal is None or slot_amount > bal:
        return await message.reply_text(f"Insufficient {currency_names_plural['balance']} to place a slot game.")

    min_bet_amount = int(bal * 0.05)
    if slot_amount < min_bet_amount:
        return await message.reply_text(
            f"Please bet at least 5% of your {currency_names_plural['balance']}, which is {currency_symbols['balance']}{min_bet_amount}."
        )

    max_bet_amount = int(bal * 0.4)
    if slot_amount > max_bet_amount:
        return await message.reply_text(
            f"Can't bet more than 40% of your {currency_names_plural['balance']}, which is {currency_symbols['balance']}{max_bet_amount}."
        )

    if user_id in last_usage_time_roll:
        time_elapsed = current_time - last_usage_time_roll[user_id]
        remaining_time = max(0, cooldown_duration_roll - time_elapsed)
        if remaining_time > 0:
            return await message.reply_text(f"You're on cooldown. Please wait {int(remaining_time)} seconds.")

    last_usage_time_roll[user_id] = current_time

    # Send slot machine dice 🎰
    value = await client.send_dice(chat_id=message.chat.id, emoji="🎰")
    await asyncio.sleep(random.uniform(1, 5))
    slot_value = value.dice.value  # 1-64 range

    # Custom win conditions (based on dice value ranges)
    if slot_value in [1, 22, 43]:  # Triple match (Jackpot)
        reward = slot_amount * 3
        await add(user_id, reward)
        await message.reply_text(f"[🎰] **JACKPOT!** 🎉\nYou won {currency_symbols['balance']}{reward}!")
        await add_xp(user_id, 10)

    elif slot_value in [2, 23, 44, 12, 33, 54]:  # Two-matching
        reward = slot_amount * 2
        await add(user_id, reward)
        await message.reply_text(f"[🎰] **Nice!** Two symbols matched!\nYou won {currency_symbols['balance']}{reward}!")
        await add_xp(user_id, 5)

    elif slot_value in [3, 24, 45, 13, 34, 55]:  # Near-Miss (Close)
        reward = int(slot_amount * 1.5)
        await add(user_id, reward)
        await message.reply_text(f"[🎰] **So close!** You got a near-match.\nYou won {currency_symbols['balance']}{reward}!")
        await add_xp(user_id, 3)

    else:  # Loss
        await deduct(user_id, slot_amount)
        await message.reply_text(f"[🍷] **Oof!** No match this time.\nYou lost {currency_symbols['balance']}{slot_amount}.")
