from pyrogram import filters, types as t
import time
import asyncio
from pyrogram import Client
from Grabber import application, user_collection
from Grabber.modules import add, deduct, show, app
from Grabber.modules.block import block_dec
from Grabber.modules.xp import add_xp, deduct_xp
from Grabber.config_settings import *

cooldown_duration_dice = 60
last_usage_time_dice = {}

@app.on_message(filters.command(["roll","dice","dicey"]))
@block_dec
async def roll_dice(client: Client, message: t.Message):
    user_id = message.from_user.id
    current_time = time.time()

    if not await user_collection.find_one({'id': user_id}):
        await message.reply("You need to grab some characters first.")
        return

    if user_id in last_usage_time_dice:
        time_elapsed = current_time - last_usage_time_dice[user_id]
        remaining_time = max(0, cooldown_duration_dice - time_elapsed)
        if remaining_time > 0:
            return await message.reply_text(f"You're on cooldown. Please wait {int(remaining_time)} seconds.")

    command_parts = message.text.split()
    if len(command_parts) != 3 or command_parts[2].lower() not in ["even", "odd", "e", "o"]:
        return await message.reply_text("Invalid command.\nUsage: /roll or /dice 100 even or /roll or /dice 100 odd")

    try:
        bet_amount = int(command_parts[1].replace(',', ''))
    except ValueError:
        return await message.reply_text("Invalid amount.")

    bet_choice = command_parts[2].lower()
    
    bal = await show(user_id)
    if bal is None:
        return await message.reply_text(f"You don't have enough {currency_names_plural['balance']} to roll the dice.")

    if bet_amount > bal:
        return await message.reply_text(f"Insufficient {currency_names_plural['balance']} to roll the dice.")

    min_bet_amount = int(bal * 0.05)
    if bet_amount < min_bet_amount:
        return await message.reply_text(f"Please bet at least 5% of your {currency_names_plural['balance']}, which is {currency_symbols['balance']}`{min_bet_amount}`.")

    value = await client.send_dice(chat_id=message.chat.id, emoji="🎲")
    await asyncio.sleep(6)
    
    dice_result = value.dice.value
    result_type = "even" if dice_result % 2 == 0 else "odd"

    if (bet_choice in ["even", "e"] and result_type == "even") or (bet_choice in ["odd", "o"] and result_type == "odd"):
        await add(user_id, bet_amount)
        await message.reply_text(f"[🎲] Congratulations! You rolled a {dice_result} ({result_type}) and won {currency_symbols['balance']}`{bet_amount}`")
        await add_xp(user_id, 2)
    else:
        await deduct(user_id, bet_amount)
        await message.reply_text(f"[💀] Oops! You rolled a {dice_result} ({result_type}) and lost {currency_symbols['balance']}`{bet_amount}`")
        # await deduct_xp(user_id, 2)

    last_usage_time_dice[user_id] = current_time
