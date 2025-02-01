import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message
import random
from datetime import datetime, timedelta
from Grabber import collection, user_collection, user_totals_collection
from . import add as add_balance, deduct as deduct_balance, app, capsify
from .block import block_dec, temp_block
from Grabber.config import *
from Grabber.config_settings import *

rarity_map = {
    "🟢 Common": True,
    "🔵 Medium": True,
    "🟠 Rare": True,
    "🟡 Legendary": True
}

last_propose_times = {}
proposing_users = {}
propose_cooldown = 300 

if(message.from_user.id == OWNER_ID and IN_DEV_MODE):
    propose_cooldown = 1

@app.on_message(filters.command("confess"))
@block_dec
async def propose(client, message: Message):
    user_id = message.from_user.id
    if temp_block(user_id):
        return

    user_data = await user_collection.find_one({'id': user_id})

    if not user_data or int(user_data.get('balance', 0)) < 20000:
        await message.reply_text(capsify("You need at least 20000 tokens to confess your love."))
        proposing_users[user_id] = False
        return

    if proposing_users.get(user_id):
        await message.reply_text(capsify("You are already confessing your love. Please wait for the current confession to finish."))
        proposing_users[user_id] = False
        return
    else:
        proposing_users[user_id] = True

    last_propose_time = last_propose_times.get(user_id)
    if last_propose_time:
        time_since_last_propose = (datetime.now() - last_propose_time).total_seconds()
        if time_since_last_propose < propose_cooldown:
            remaining_cooldown = propose_cooldown - time_since_last_propose
            remaining_cooldown_minutes = remaining_cooldown // 60
            remaining_cooldown_seconds = remaining_cooldown % 60
            await message.reply_text(capsify(f"Cooldown! Please wait {int(remaining_cooldown_minutes)}m {int(remaining_cooldown_seconds)}s before confessing again."))
            proposing_users[user_id] = False
            return

    await deduct_balance(user_id, 10000)

    proposal_message = capsify("✨ Time to Confess ✨")
    photo_path = 'https://telegra.ph/file/68491359070e2e045c919.jpg'
    await message.reply_photo(photo=photo_path, caption=proposal_message)

    await asyncio.sleep(2)

    await message.reply_text(capsify("Confessing your love 💌"))

    await asyncio.sleep(2)

    if random.random() < 0.6:
        rejection_message = capsify("She rejected your confession and slapped you 😔🤣")
        rejection_photo_path = 'https://graph.org/file/43ac16b34453bafe480d9.jpg'
        await message.reply_photo(photo=rejection_photo_path, caption=rejection_message)
    else:
        all_characters = list(await collection.find({}).to_list(length=None))
        print(all_characters)
        valid_characters = [char for char in all_characters if char.get('rarity') in rarity_map.keys()]
        print(valid_characters)

        if not valid_characters:
            await message.reply_text(capsify("No characters available with the specified rarity."))
            return

        character = random.choice(valid_characters)
        await user_collection.update_one({'id': user_id}, {'$push': {'characters': character}})
        # await message.reply_photo(photo=character['img_url'], caption=capsify(f"{character['name']} accepted your confession of love! 💕"))
        await client.send_photo(
            chat_id=message.chat.id,
            photo=character['img_url'],
            caption=capsify(f"{character['name']} accepted your confession of love! 💕"),
            reply_to_message_id=message.id,  
            protect_content=True  
        )

    last_propose_times[user_id] = datetime.now()
    proposing_users[user_id] = False