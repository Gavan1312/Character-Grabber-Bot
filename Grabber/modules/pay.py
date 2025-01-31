import math
from pyrogram import Client, filters
from Grabber import application, user_collection
from pyrogram.types import Message, InlineKeyboardMarkup as IKM, InlineKeyboardButton as IKB, CallbackQuery
from datetime import datetime, timedelta
import asyncio
from . import add, deduct, show, app, capsify
from .block import block_dec, temp_block
from Grabber.config_settings import *

last_payment_times = {}

def format_timedelta(td: timedelta) -> str:
    seconds = td.total_seconds()
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return "{:02}h {:02}m {:02}s".format(int(hours), int(minutes), int(seconds))

@app.on_message(filters.command('pay'))
@block_dec
async def mpay(client, message):
    sender_id = message.from_user.id
    if temp_block(sender_id):
        return

    if not message.reply_to_message:
        await message.reply_text(capsify("Please reply to a user to /pay."))
        return

    recipient_id = message.reply_to_message.from_user.id

    if sender_id == recipient_id:
        await message.reply_text(capsify("You can't pay yourself."))
        return

    try:
        amount = int(message.text.split()[1].replace(',', ''))
        if amount <= 0:
            raise ValueError("Amount must be greater than zero.")
    except (IndexError, ValueError):
        await message.reply_text(capsify("Invalid amount. Please provide a valid positive amount."))
        return

    sender_balance = await show(sender_id)
    if not sender_balance or sender_balance < amount:
        await message.reply_text(capsify("Insufficient Love Points to make the payment."))
        return

    last_payment_time = last_payment_times.get(sender_id)
    if last_payment_time:
        time_since_last_payment = datetime.now() - last_payment_time
        if time_since_last_payment < timedelta(minutes=10):
            cooldown_time = timedelta(minutes=10) - time_since_last_payment
            formatted_cooldown = format_timedelta(cooldown_time)
            await message.reply_text(capsify(f"Cooldown! You can pay again in {formatted_cooldown}."))
            return

    recipient_name = message.reply_to_message.from_user.first_name  # Get the recipient's name

    # Send confirmation message with buttons
    keyboard = IKM([
        [
            IKB(capsify("✅ Confirm"), callback_data=f'pay_confirm_{sender_id}_{recipient_id}_{amount}'),
            IKB(capsify("❌ Cancel"), callback_data=f'pay_cancel_{sender_id}')
        ]
    ])
    
    await message.reply_text(
        capsify(f"Are you sure you want to pay {currency_symbols['balance']}{amount} Love Points to {recipient_name}?"),
        reply_markup=keyboard
    )

@app.on_callback_query(filters.regex(r'^pay_(confirm|cancel)_(\d+)_?(\d+)?_?(\d+)?'))
async def pay_callback(client: Client, callback_query: CallbackQuery):
    data_parts = callback_query.data.split('_')
    action = data_parts[1]
    sender_id = int(data_parts[2])

    if callback_query.from_user.id != sender_id:
        await callback_query.answer("This is not for you!", show_alert=True)
        return

    # Delete the confirmation message
    await callback_query.message.delete()

    if action == "cancel":
        await app.send_message(callback_query.message.chat.id, capsify("Payment canceled."))
        return

    recipient_id = int(data_parts[3])
    amount = int(data_parts[4])

    sender_balance = await show(sender_id)
    if not sender_balance or sender_balance < amount:
        await app.send_message(callback_query.message.chat.id, capsify("Insufficient Love Points to make the payment."))
        return

    await deduct(sender_id, amount)
    await add(recipient_id, amount)
    last_payment_times[sender_id] = datetime.now()

    recipient_name = (await app.get_users(recipient_id)).first_name

    await app.send_message(
        callback_query.message.chat.id,
        capsify(f"Payment Successful! You Paid {currency_symbols['balance']}{amount} Love Points to {recipient_name}.")
    )