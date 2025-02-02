import asyncio
import random
import time
from pyrogram import Client, filters
from . import user_collection, collection, capsify, app, db
from .block import block_dec, temp_block
from datetime import datetime
from Grabber.config import *
from Grabber.config_settings import *

cooldown_collection = db.cooldowns
marry_cooldown = 900

if(IN_DEV_MODE):
    marry_cooldown = 1

async def get_cooldown_from_db(user_id):
    try:
        user_data = await cooldown_collection.find_one({'id': user_id})
        if user_data and 'last_roll' in user_data:
            return user_data['last_roll']
        return None
    except Exception as e:
        print(f"Error retrieving cooldown from DB: {e}")
        return None

async def update_cooldown_in_db(user_id):
    try:
        current_time = datetime.utcnow()
        await cooldown_collection.update_one(
            {'id': user_id},
            {'$set': {'last_roll': current_time}},
            upsert=True
        )
    except Exception as e:
        print(f"Error updating cooldown in DB: {e}")

async def get_unique_characters(receiver_id, target_rarities=['🟢 Common', '🔵 Medium', '🟠 Rare', '🟡 Legendary']):
    try:
        user = await user_collection.find_one({'id': receiver_id}, {'characters': 1})
        owned_ids = [char['id'] for char in user['characters']] if user and 'characters' in user else []
        pipeline = [
            {'$match': {'rarity': {'$in': target_rarities}, 'id': {'$nin': owned_ids}}},
            {'$sample': {'size': 1}}
        ]
        cursor = collection.aggregate(pipeline)
        characters = await cursor.to_list(length=None)
        if not characters:
            fallback_pipeline = [
                {'$match': {'rarity': {'$in': target_rarities}}},
                {'$sample': {'size': 1}}
            ]
            cursor = collection.aggregate(fallback_pipeline)
            characters = await cursor.to_list(length=None)
        return characters
    except Exception:
        return []

async def send_error_report(client, message, error_message):
    report_message = (
        f"{capsify('Error')}: {error_message}\n"
        f"{capsify('Please report this issue')}: @YourSupportBot"
    )
    await client.send_message(
        chat_id=message.chat.id,
        text=report_message,
        reply_to_message_id=message.id
    )

async def handle_marriage(client, message, receiver_id):
    try:
        unique_characters = await get_unique_characters(receiver_id)
        if not unique_characters:
            await send_error_report(client, message, "Failed to retrieve characters. Please try again later.")
            return

        await user_collection.update_one({'id': receiver_id}, {'$push': {'characters': {'$each': unique_characters}}})

        for character in unique_characters:
            caption = (
                f"{capsify('Congratulations')}! {message.from_user.first_name}, {capsify('You have successfully tempted a waifu! 😈')}! "
                f"{capsify('Here is your Waifu')}:\n"
                f"Name: {character['name']}\n"
                f"Rarity: {character['rarity']}\n"
                f"Anime: {character['anime']}\n"
            )
            await client.send_photo(
                chat_id=message.chat.id,
                photo=character['img_url'],
                caption=caption,
                reply_to_message_id=message.id,
                protect_content = True
            )

    except Exception as e:
        await send_error_report(client, message, str(e))

async def handle_dice(client, message, receiver_id):
    try:
        dice_message = await client.send_dice(chat_id=message.chat.id)
        value = int(dice_message.dice.value)

        if value in [1, 2, 5, 6]:
            unique_characters = await get_unique_characters(receiver_id)
            print("marry unique : ")
            print(unique_characters)
            if not unique_characters:
                await send_error_report(client, message, "Failed to retrieve characters. Please try again later.")
                return

            for character in unique_characters:
                await user_collection.update_one({'id': receiver_id}, {'$push': {'characters': character}})

            for character in unique_characters:
                married_character_name_to_display = character['name'].split()[0]
                caption = (
                    f"{capsify('Congratulations')}! {message.from_user.first_name}, {capsify(f'You have successfully tempted {married_character_name_to_display}! 🔥')}!\n"
                    f"{capsify('Here is your character')}:\n"
                    f"Name: {character['name']}\n"
                    f"Rarity: {character['rarity']}\n"
                    f"Anime: {character['anime']}\n"
                )
                await client.send_photo(
                    chat_id=message.chat.id,
                    photo=character['img_url'],
                    caption=caption,
                    reply_to_message_id=message.id,
                    protect_content = True
                )
        else:
            await client.send_message(
                chat_id=message.chat.id,
                text=f"{message.from_user.first_name}, {capsify('Your temptation has failed and she is laughing at you')}! 🤡",
                reply_to_message_id=message.id
            )

    except Exception as e:
        await send_error_report(client, message, str(e))

@app.on_message(filters.command("tempt"))
@block_dec
async def dice_command(client, message):
    user_id = message.from_user.id
    if temp_block(user_id):
        return

    last_roll_time = await get_cooldown_from_db(user_id)
    if last_roll_time:
        cooldown_time = (datetime.utcnow() - last_roll_time).total_seconds()
        if cooldown_time < marry_cooldown:
            remaining_time = marry_cooldown - cooldown_time
            hours, remainder = divmod(int(remaining_time), marry_cooldown)
            minutes, seconds = divmod(remainder, 60)
            await client.send_message(
                chat_id=message.chat.id,
                text=capsify(f"Please wait {hours} hours, {minutes} minutes, and {seconds} seconds before trying to someone tempt again."),
                reply_to_message_id=message.id
            )
            return

    await update_cooldown_in_db(user_id)

    if user_id == 7162166061:
        await client.send_message(
            chat_id=message.chat.id,
            text=capsify("You are banned from using this command."),
            reply_to_message_id=message.id
        )
        return

    receiver_id = message.from_user.id
    await handle_dice(client, message, receiver_id)

