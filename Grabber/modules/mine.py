from pyrogram import filters, Client
from pyrogram.types import InlineKeyboardButton as IKB, InlineKeyboardMarkup as IKM, CallbackQuery, Message
from Grabber import app, user_collection
import random
from . import aruby, druby, sruby, capsify, nopvt, limit, dev_filter
import time
import asyncio
from .block import block_dec, temp_block, block_cbq
from Grabber.config_settings import * 
from Grabber.config import OWNER_ID

MINING_COOLDOWN_PERIOD = 300
FULL_BOARD_SIZE = 9
SINGLE_LINE_SIZE = 3

def generate_minefield(size, bombs):
    minefield = ['☄️'] * size
    bomb_positions = random.sample(range(size), bombs)
    for pos in bomb_positions:
        minefield[pos] = '☢'
    return minefield

@app.on_message(filters.command("crystalize"))
@block_dec
async def mines(client, message):
    user_id = message.from_user.id
    if temp_block(user_id):
        return
    user_data = await user_collection.find_one({"id": user_id})
    last_game_time = user_data.get("last_game_time", 0) if user_data else 0

    if time.time() - last_game_time < MINING_COOLDOWN_PERIOD:
        remaining_time = int(MINING_COOLDOWN_PERIOD - (time.time() - last_game_time))
        await message.reply_text(capsify(f"Please wait {remaining_time} seconds before starting a new game."))
        return

    try:
        amount = int(message.command[1])
        bombs = int(message.command[2])
        if amount < 1 or bombs < 1:
            raise ValueError("Invalid bet amount or Blasters count.")
    except (IndexError, ValueError):
        await message.reply_text(capsify("Use /crystalize [amount] [Blasters]"))
        return

    user_balance = await sruby(user_id)
    max_bet = int(user_balance * 0.5)
    if amount > max_bet:
        await message.reply_text(capsify(f"Your bet amount cannot exceed 50% of your total {currency_names_plural['rubies']}. The maximum bet is {max_bet} {currency_names_plural['rubies']}."))
        return

    if user_balance < amount:
        await message.reply_text(capsify(f"Insufficient {currency_names_plural['rubies']} to make the bet."))
        return

    size = FULL_BOARD_SIZE
    minefield = generate_minefield(size, bombs)
    # base_multiplier = bombs / 10
    base_multiplier = 0

    game_data = {
        "amount": amount,
        "minefield": minefield,
        "revealed": [False] * size,
        "bombs": bombs,
        "game_active": True,
        "multiplier": 0 + base_multiplier
    }

    await user_collection.update_one({"id": user_id}, {"$set": {"game_data": game_data}}, upsert=True)

    keyboard = [
        [IKB(" ", callback_data=f"{user_id}_{i}") for i in range(j, j + SINGLE_LINE_SIZE)]
        for j in range(0, size, SINGLE_LINE_SIZE)
    ]
    reply_markup = IKM(keyboard)
    await message.reply_text(
        capsify(f"Choose a tile:\n\n**Current Multiplier:** {game_data['multiplier']:.2f}x\n**Bet Amount:** {amount} {currency_names_plural['rubies']}"),
        reply_markup=reply_markup
    )

@app.on_callback_query(filters.regex(r"^\d+_\d+$"))
@block_cbq
async def mines_button(client, query: CallbackQuery):
    user_id, index = map(int, query.data.split('_'))
    if user_id != query.from_user.id:
        await query.answer(capsify("This is not your game."), show_alert=True)
        return

    user_data = await user_collection.find_one({"id": user_id})
    game_data = user_data.get("game_data") if user_data else None

    if not game_data or not game_data["game_active"]:
        await query.answer(capsify("Game has already ended."), show_alert=True)
        return

    index = int(index)
    minefield = game_data["minefield"]
    revealed = game_data["revealed"]
    amount = game_data["amount"]
    multiplier = game_data["multiplier"]

    if revealed[index]:
        await query.answer(capsify("This tile is already revealed."), show_alert=True)
        return

    if time.time() - user_data.get("last_click_time", 0) < 5:
        remaining_time = 5 - (time.time() - user_data.get("last_click_time", 0))
        await query.answer(capsify(f"Please maintain a 5-second gap between clicks. Wait for {int(remaining_time)} seconds."), show_alert=True)
        return

    revealed[index] = True
    await user_collection.update_one(
        {"id": user_id},
        {"$set": {"game_data.revealed": revealed, "last_click_time": time.time()}}
    )

    await asyncio.sleep(5)

    if minefield[index] == '☢':
        await druby(user_id, amount)
        await query.message.edit_text(
            capsify(f"☢ You hit the Blasters! Game over! You lost {amount} {currency_names_plural['rubies']}."),
            reply_markup=None
        )
        await user_collection.update_one({"id": user_id}, {"$set": {"last_game_time": time.time(), "game_data": None}})
        return

    multiplier += game_data["bombs"] / 10
    game_data["multiplier"] = multiplier

    if all(revealed[i] or minefield[i] == '☢' for i in range(len(minefield))):
        winnings = int(amount * multiplier)
        await aruby(user_id, winnings)
        await query.message.edit_text(
            capsify(f"🎉 You revealed all the safe tiles! You win {winnings} {currency_names_plural['rubies']}!"),
            reply_markup=None
        )
        await user_collection.update_one({"id": user_id}, {"$set": {"last_game_time": time.time(), "game_data": None}})
        return

    await user_collection.update_one({"id": user_id}, {"$set": {"game_data": game_data}})

    keyboard = [
        [IKB(minefield[i] if revealed[i] else " ", callback_data=f"{user_id}_{i}")
         for i in range(j, j + SINGLE_LINE_SIZE)]
        for j in range(0, len(minefield), SINGLE_LINE_SIZE)
    ]
    keyboard.append([IKB(f"Cash Out ({int(amount * multiplier)} {currency_names_plural['rubies']})", callback_data=f"{user_id}_cash_out")])
    reply_markup = IKM(keyboard)

    await query.message.edit_text(
        capsify(f"Choose a tile:\n\n**Current Multiplier:** {multiplier:.2f}x"),
        reply_markup=reply_markup
    )

@app.on_callback_query(filters.regex(r"^\d+_cash_out$"))
async def cash_out(client, query: CallbackQuery):
    user_id = int(query.data.split('_')[0])
    if user_id != query.from_user.id:
        await query.answer(capsify("This is not your game."), show_alert=True)
        return

    user_data = await user_collection.find_one({"id": user_id})
    game_data = user_data.get("game_data") if user_data else None

    if not game_data or not game_data["game_active"]:
        await query.answer(capsify("Game has already ended."), show_alert=True)
        return

    amount = game_data["amount"]
    # winnings = int(amount * game_data["multiplier"]) - amount
    winnings = int(amount * game_data["multiplier"])
    winnings = max(winnings, 0)

    await aruby(user_id, winnings)
    await query.message.edit_text(
        capsify(f"💰 You cashed out! You won {winnings} {currency_names_plural['rubies']}."),
        reply_markup=None
    )
    await user_collection.update_one({"id": user_id}, {"$set": {"last_game_time": time.time(), "game_data": None}})
    
    
@app.on_message(filters.command("changehscooldownperiod") & (dev_filter | filters.user(OWNER_ID)))
async def change_hs_cooldown_period(client, message: Message):
    # Split message text into parts
    args = message.text.split()

    # Ensure argument is provided
    if len(args) < 2:
        return await message.reply("⚠️ Please provide a cooldown period. Usage: /changehscooldownperiod <seconds>")

    try:
        # Convert argument to an integer
        cooldown_period = int(args[1])

        # Update global variable (if necessary)
        global MINING_COOLDOWN_PERIOD
        MINING_COOLDOWN_PERIOD = cooldown_period

        await message.reply(f"✅ Mining cooldown period set to {MINING_COOLDOWN_PERIOD} seconds.")
    
    except ValueError:
        await message.reply("⚠️ Invalid input! Please enter a valid number for the cooldown period.")