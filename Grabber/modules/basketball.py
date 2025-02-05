from pyrogram import filters, types as t
import time
import asyncio
from pyrogram import Client
from Grabber import application, user_collection
from . import add, deduct, show, app
from .block import block_dec
from .xp import add_xp, deduct_xp
from Grabber.config_settings import * 

cooldown_duration_roll = 90
last_usage_time_roll = {}

@app.on_message(filters.command(["basket"]))
@block_dec
async def roll_dart(client: Client, message: t.Message):
    user_id = message.from_user.id
    #if temp_block(user_id):
        #return
    current_time = time.time()

    if not await user_collection.find_one({'id': user_id}):
        await message.reply("You need to grab some characters first.")
        return

    if user_id in last_usage_time_roll:
        time_elapsed = current_time - last_usage_time_roll[user_id]
        remaining_time = max(0, cooldown_duration_roll - time_elapsed)
        if remaining_time > 0:
            return await message.reply_text(f"You're on cooldown. Please wait {int(remaining_time)} seconds.")

    command_parts = message.text.split()
    if len(command_parts) != 2:
        return await message.reply_text("Invalid command.\nUsage: /basket 10000")

    try:
        basket_amount = int(command_parts[1].replace(',', ''))
    except ValueError:
        return await message.reply_text("Invalid amount.")

    bal = await show(user_id)
    if bal is None:
        return await message.reply_text(f"You don't have enough {currency_names_plural['balance']} to place a basketball.")

    if basket_amount > bal:
        return await message.reply_text(f"Insufficient {currency_names_plural['balance']} to place a basketball.")

    min_bet_amount = int(bal * 0.05)
    if basket_amount < min_bet_amount:
        return await message.reply_text(f"Please bet at least 5% of your {currency_names_plural['balance']}, which is {currency_symbols['balance']}`{min_bet_amount:,.0f}`.")

    value = await client.send_dice(chat_id=message.chat.id, emoji="🏀")

    await asyncio.sleep(6)
    
    dice_result = value.dice.value 
    
    if dice_result in [4, 5]: # Winning only if the dice rolls a 6
        await add(user_id, basket_amount)
        await message.reply_text(f"[🏀] You're lucky!\nYou won {currency_symbols['balance']}`{basket_amount:,.0f}`")
        await add_xp(user_id, 2)
    else:
        await deduct(user_id, basket_amount)
        await message.reply_text(f"[🍷] Better luck next time!\nYou lost {currency_symbols['balance']}`{basket_amount:,.0f}`")
        # await deduct_xp(user_id, 2)

    last_usage_time_roll[user_id] = current_time