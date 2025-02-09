from datetime import datetime
from Grabber import user_collection, application
from . import capsify, app
from .block import block_dec, temp_block, block_cbq
from telegram import InlineKeyboardMarkup, InlineKeyboardButton, Update
from telegram.ext import CallbackContext, CommandHandler, CallbackQueryHandler

async def gift_new(update: Update, context: CallbackContext):
    message = update.message
    sender_id = message.from_user.id
    user_id = message.from_user.id
    if temp_block(user_id):
        return

    if not message.reply_to_message:
        await message.reply_text(capsify("You need to reply to a user's message to gift a character!"))
        return

    receiver_id = message.reply_to_message.from_user.id
    receiver_first_name = message.reply_to_message.from_user.first_name

    if sender_id == receiver_id:
        await message.reply_text(capsify("You can't gift a character to yourself!"))
        return
    if temp_block(sender_id):
        return

    if len(context.args) != 1:
        await message.reply_text(capsify("You need to provide a character ID!"))
        return

    character_id = context.args[0]
    sender = await user_collection.find_one({'id': sender_id})

    if not sender:
        sender = {
            'id': sender_id,
            'characters': [],
        }
        await user_collection.insert_one(sender)

    character = next((character for character in sender.get('characters', []) if character.get('id') == character_id), None)

    if not character:
        await message.reply_text(capsify(f"You do not have a character with ID {character_id}!"))
        return

    success_message = (
        f"{capsify('🎁 CONFIRM GIFTING')}\n\n"
        f"{capsify('♦️ NAME:')} {capsify(character['name'])} \n"
        f"{capsify('🧧 ANIME:')} {capsify(character['anime'])}\n"
        f"{capsify('🆔:')} {int(character['id']):03}\n"
        f"{capsify('🌟:')} {character.get('rarity', '🔮 LIMITED')}\n\n"
    )
    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton(capsify("CONFIRM"), callback_data=f"con_gift_new:{sender_id}:{character_id}:{receiver_id}"),
            InlineKeyboardButton(capsify("CANCEL"), callback_data=f"can_gift_new:{sender_id}")
        ]
    ])
    await message.reply_text(success_message, reply_markup=keyboard)

async def gift_callback_new(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    action, sender_id, *data = query.data.split(":")
    sender_id = int(sender_id)

    if query.from_user.id != sender_id:
        await query.answer("This is not for you baka ❗", show_alert=True)
        return

    if action == "can_gift_new":
        await query.edit_message_text(capsify("🎁 GIFT CANCELED SUCCESSFULLY!"))
        return

    if action == "con_gift_new":
        if len(data) < 2:
            await query.edit_message_text(capsify("ERROR: Invalid callback data!"))
            return

        character_id, receiver_id = map(int, data)
        sender = await user_collection.find_one({'id': sender_id})
        if not sender:
            await query.edit_message_text(capsify("SENDER DATA NOT FOUND!"))
            return

        character = next((char for char in sender.get('characters', []) if char.get('id') == character_id), None)
        if not character:
            await query.edit_message_text(capsify("CHARACTER NOT FOUND IN YOUR INVENTORY!"))
            return

        sender_characters = [char for char in sender['characters'] if char['id'] != character_id]
        await user_collection.update_one({'id': sender_id}, {'$set': {'characters': sender_characters}})

        receiver = await user_collection.find_one({'id': receiver_id})
        if receiver:
            await user_collection.update_one({'id': receiver_id}, {'$push': {'characters': character}})
        else:
            await user_collection.insert_one({'id': receiver_id, 'characters': [character]})

        updated_message = (
            f"{capsify('🎁 GIFT SENT SUCCESSFULLY!')}\n\n"
            f"{capsify('♦️ NAME:')} {capsify(character['name'])} \n"
            f"{capsify('🧧 ANIME:')} {capsify(character['anime'])}\n"
            f"{capsify('🆔:')} {character['id']:03}\n"
            f"{capsify('🌟:')} {character.get('rarity', '')}\n"
        )
        await query.edit_message_text(updated_message)

application.add_handler(CommandHandler("giftnew", gift_new))
application.add_handler(CallbackQueryHandler(gift_callback_new, pattern=r"^(con_gift_new|can_gift_new):"))