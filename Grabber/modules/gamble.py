import random
from pyrogram import Client, filters
from Grabber import user_collection
from . import add, deduct, show, abank, dbank, sbank, app, capsify
from .block import block_dec, temp_block
from Grabber.config_settings import *

@app.on_message(filters.command("gamble"))
@block_dec
async def gamble(client, message):
    user_id = message.from_user.id
    if temp_block(user_id):
        return
    user = await user_collection.find_one({'id': user_id})
    balance = int(user.get('balance', 0))

    args = message.text.split()[1:]
    if len(args) != 2:
        await message.reply_text(capsify("Usage: /gamble <amount> <l/r>"))
        return

    try:
        amount = int(args[0].replace(',', ''))
        choice = args[1].lower()
    except ValueError:
        await message.reply_text(capsify("Invalid amount."))
        return

    if choice not in ['l', 'r']:
        await message.reply_text(capsify("Invalid choice. Please use /gamble l/r."))
        return

    min_bet = int(balance * 0.05)
    if amount < min_bet:
        await message.reply_text(capsify(f"Please gamble at least 5% of your {currency_names_plural['balance']}, which is {currency_symbols['balance']}{min_bet}."))
        return

    if amount > balance:
        await message.reply_text(capsify(f"You do not have enough {currency_names_plural['balance']} to gamble {currency_symbols['balance']}{amount:,.0f}. Your current {currency_names_plural['balance']} are {currency_symbols['balance']}{balance}."))
        return

    # Winning chance is now 40 out of 100
    if random.randint(1, 100) <= 40:  # 40% chance to win
        coin_side = choice
        new_balance = amount  # Amount to add
        message_text = capsify(f"You chose {choice} and won {currency_symbols['balance']}{amount:,.0f}. 🤩\nCoin was in {coin_side} hand.")
    else:
        coin_side = 'l' if choice == 'r' else 'r'
        new_balance = -amount  # Amount to deduct
        message_text = capsify(f"You chose {choice} and lost {currency_symbols['balance']}{amount:,.0f}. 🥲\nCoin was in {coin_side} hand.")

    await add(user_id, new_balance)

    # photo_url = "https://telegra.ph/file/889fb66c41a9ead354c59.jpg" if coin_side == choice else "https://telegra.ph/file/99a98f60b22759857056a.jpg"
    # await message.reply_photo(photo=photo_url, caption=message_text)
    await message.reply_text(message_text)
    

@app.on_message(filters.command(["betlove", "betlp","lpbet"]))
@block_dec
async def gamble(client, message):
    user_id = message.from_user.id
    if temp_block(user_id):
        return
    user = await user_collection.find_one({'id': user_id})
    balance = int(user.get('balance', 0))

    args = message.text.split()[1:]
    if len(args) != 2:
        await message.reply_text(capsify("Usage: /betlove <amount> <h/t>"))
        return

    try:
        amount = int(args[0].replace(',', ''))
        choice = args[1].lower()
    except ValueError:
        await message.reply_text(capsify("Invalid amount."))
        return

    if choice not in ['h', 't']:
        await message.reply_text(capsify("Invalid choice. Please use /betlove h/t."))
        return

    min_bet = int(balance * 0.05)
    if amount < min_bet:
        await message.reply_text(capsify(f"Please bet at least 5% of your {currency_names_plural['balance']}, which is {currency_symbols['balance']}`{min_bet}`."))
        return

    if amount > balance:
        await message.reply_text(capsify(f"You do not have enough {currency_names_plural['balance']} to bet `{amount:,.0f}`. Your current {currency_names_plural['balance']} are {currency_symbols['balance']}`{balance}`."))
        return

    # Winning chance is now 40 out of 100
    if random.randint(1, 100) <= 50:  # 40% chance to win
        coin_side = choice
        new_balance = amount  # Amount to add
        message_text = capsify(f"The Coin landed on {coin_side} 🤩\nYou won {currency_symbols['balance']}`{amount:,.0f}`.")
    else:
        coin_side = 'h' if choice == 't' else 't'
        new_balance = -amount  # Amount to deduct
        message_text = capsify(f"The Coin landed on {coin_side} 🥲\nYou lost {currency_symbols['balance']}`{amount:,.0f}`.")

    await add(user_id, new_balance)

    # photo_url = "https://telegra.ph/file/889fb66c41a9ead354c59.jpg" if coin_side == choice else "https://telegra.ph/file/99a98f60b22759857056a.jpg"
    # await message.reply_photo(photo=photo_url, caption=message_text)
    await message.reply_text(message_text)