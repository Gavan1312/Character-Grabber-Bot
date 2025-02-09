import time
import random
import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message
from Grabber.modules import add, deduct, show, app

rob_cooldown = 1800  # 1 hour cooldown
last_robbery_time = {}

# @app.on_message(filters.command(["lprob","roblp","lpsteal","steallp"]) & filters.reply)
async def rob_love_points(client: Client, message: Message):
    user_id = message.from_user.id

    if not message.reply_to_message or not message.reply_to_message.from_user:
        return await message.reply_text("Reply to someone's message to rob them!")

    target_id = message.reply_to_message.from_user.id

    if user_id == target_id:
        return await message.reply_text("You can't rob yourself!")

    current_time = time.time()
    if user_id in last_robbery_time:
        elapsed_time = current_time - last_robbery_time[user_id]
        remaining_time = max(0, rob_cooldown - elapsed_time)
        if remaining_time > 0:
            return await message.reply_text(f"You're on cooldown. Try again in {int(remaining_time // 30)} minutes.")

    user_balance = await show(user_id)
    target_balance = await show(target_id)

    if user_balance is None or target_balance is None:
        return await message.reply_text("Either you or the target has no love points to steal!")

    if target_balance < 10:
        return await message.reply_text("The target has too few love points to rob.")

    success_chance = 50  # 50% chance to succeed
    if random.randint(1, 100) <= success_chance:
        stolen_amount = int(target_balance * (random.uniform(0, 0.3)))  # Steal 0-30%
        await add(user_id, stolen_amount)
        await deduct(target_id, stolen_amount)
        await message.reply_text(f"💰 Success! You robbed {stolen_amount} love points from {message.reply_to_message.from_user.mention}!")
    else:
        penalty = int(user_balance * 0.1)  # Lose 10% of own love points
        await deduct(user_id, penalty)
        await message.reply_text(f"🚔 You got caught! Lost {penalty} love points as a penalty.")

    last_robbery_time[user_id] = current_time
