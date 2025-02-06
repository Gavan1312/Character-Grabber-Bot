from datetime import datetime
from Grabber import user_collection
from . import capsify, app
from .block import block_dec, temp_block, block_cbq
from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup as IKM, InlineKeyboardButton as IKB

@app.on_message(filters.command("gift"))
@block_dec
async def gift(client, message):
    sender_id = message.from_user.id
    user_id = message.from_user.id
    if temp_block(user_id):
        return

    if not message.reply_to_message:
        await message.reply(capsify("You need to reply to a user's message to gift a character!"))
        return

    receiver_id = message.reply_to_message.from_user.id
    receiver_first_name = message.reply_to_message.from_user.first_name

    if sender_id == receiver_id:
        await message.reply(capsify("You can't gift a character to yourself!"))
        return
    if temp_block(sender_id):
        return

    if len(message.command) != 2:
        await message.reply(capsify("You need to provide a character ID!"))
        return

    character_id = message.command[1]
    sender = await user_collection.find_one({'id': sender_id})

    if not sender:
        sender = {
            'id': sender_id,
            'characters': [],
            # 'daily_gift_count': 0,
            # 'last_reset': None,
        }
        await user_collection.insert_one(sender)

    # last_reset = sender.get('last_reset')
    # daily_gift_count = sender.get('daily_gift_count', 0)

    # if not last_reset or datetime.fromisoformat(last_reset).date() < datetime.utcnow().date():
    #     daily_gift_count = 0
    #     await user_collection.update_one(
    #         {'id': sender_id}, 
    #         {'$set': {'daily_gift_count': 0, 'last_reset': datetime.utcnow().isoformat()}}
    #     )

    # if daily_gift_count >= 10:
    #     await message.reply(capsify("You have reached your daily gift limit. Try again tomorrow!"))
    #     return

    character = next((character for character in sender.get('characters', []) if character.get('id') == character_id), None)

    if not character:
        await message.reply(capsify(f"You do not have a character with ID {character_id}!"))
        return

    # gifts_left = 10 - daily_gift_count
    success_message = (
        f"{capsify('🎁 CONFIRM GIFTING')}\n\n"
        f"{capsify('♦️ NAME:')} {capsify(character['name'])} \n"
        f"{capsify('🧧 ANIME:')} {capsify(character['anime'])}\n"
        f"{capsify('🆔:')} {int(character['id']):03}\n"
        f"{capsify('🌟:')} {character.get('rarity', '🔮 LIMITED')}\n\n"
        # f"{capsify('GIFTS LEFT:')} {gifts_left}"
    )
    keyboard = IKM([
        # [IKB(capsify("INLINE"), switch_inline_query_current_chat=f"{character_id}")],
        [
            IKB(capsify("CONFIRM"), callback_data=f"con_gift:{sender_id}:{character_id}:{receiver_id}"),
            IKB(capsify("CANCEL"), callback_data=f"can_gift:{sender_id}")
        ]
    ])
    await message.reply(success_message, reply_markup=keyboard)


@app.on_callback_query(filters.regex(r"^(con_gift|can_gift):"))
@block_cbq
async def gift_callback(client, callback_query):
    action, sender_id, *data = callback_query.data.split(":")
    sender_id = int(sender_id)  # Convert to integer

    print(f"[DEBUG] Callback triggered - action: {action}, sender_id: {sender_id}, data: {data}")
    print(f"[DEBUG] Callback triggered by user_id: {callback_query.from_user.id}")

    if callback_query.from_user.id != sender_id:
        print(f"[ERROR] Unauthorized user! Expected: {sender_id}, Got: {callback_query.from_user.id}")
        await callback_query.answer("This is not for you baka ❗", show_alert=True)
        return

    if action == "can_gift":
        print(f"[INFO] Gift cancelation requested by user: {sender_id}")
        await callback_query.message.edit(capsify("🎁 GIFT CANCELED SUCCESSFULLY!"))
        return

    if action == "con_gift":
        if len(data) < 2:
            print(f"[ERROR] Invalid callback data format: {data}")
            await callback_query.message.edit(capsify("ERROR: Invalid callback data!"))
            return

        character_id, receiver_id = data
        character_id = int(character_id)  # Convert to integer
        receiver_id = int(receiver_id)

        print(f"[INFO] Processing gift transfer - Sender: {sender_id}, Receiver: {receiver_id}, Character ID: {character_id}")

        sender = await user_collection.find_one({'id': sender_id})
        if not sender:
            print(f"[ERROR] Sender data not found in database for ID: {sender_id}")
            await callback_query.message.edit(capsify("SENDER DATA NOT FOUND!"))
            return

        print(f"[DEBUG] Sender data found: {sender}")

        character = next((char for char in sender.get('characters', []) if char.get('id') == character_id), None)
        if not character:
            print(f"[ERROR] Character ID {character_id} not found in sender's inventory!")
            await callback_query.message.edit(capsify("CHARACTER NOT FOUND IN YOUR INVENTORY!"))
            return

        print(f"[INFO] Character found: {character}")

        # Remove character from sender's inventory
        sender_characters = [char for char in sender['characters'] if char['id'] != character_id]
        await user_collection.update_one({'id': sender_id}, {'$set': {'characters': sender_characters}})
        print(f"[INFO] Character {character_id} removed from sender {sender_id}")

        # Add character to receiver
        receiver = await user_collection.find_one({'id': receiver_id})
        if receiver:
            print(f"[INFO] Receiver {receiver_id} found, updating character list")
            await user_collection.update_one({'id': receiver_id}, {'$push': {'characters': character}})
        else:
            print(f"[INFO] Receiver {receiver_id} not found, creating new entry")
            await user_collection.insert_one({'id': receiver_id, 'characters': [character]})

        print(f"[SUCCESS] Character {character_id} transferred from {sender_id} to {receiver_id}")

        updated_message = (
            f"{capsify('🎁 GIFT SENT SUCCESSFULLY!')}\n\n"
            f"{capsify('♦️ NAME:')} {capsify(character['name'])} \n"
            f"{capsify('🧧 ANIME:')} {capsify(character['anime'])}\n"
            f"{capsify('🆔:')} {character['id']:03}\n"
            f"{capsify('🌟:')} {character.get('rarity', '')}\n"
        )
        await callback_query.message.edit(updated_message)
      