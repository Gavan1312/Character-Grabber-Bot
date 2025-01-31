import asyncio
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton as IKB, InlineKeyboardMarkup as IKM, Message, CallbackQuery
from Grabber.config import GROUP_ID

from . import user_collection, app, capsify
from .block import block_dec, block_cbq, temp_block

group_id_to_use_for_log = int(GROUP_ID)

@app.on_message(filters.command("fav"))
@block_dec
async def fav(client: Client, message: Message):
    user_id = message.from_user.id
    if temp_block(user_id):
        return

    if len(message.command) < 2:
        await message.reply_text(capsify('Please provide Character ID...'))
        return

    character_id = message.command[1]
    user = await user_collection.find_one({'id': user_id})
    if not user:
        await message.reply_text(capsify('You have not got any Waifus yet...😣'))
        return

    character = next((c for c in user['characters'] if c['id'] == character_id), None)
    if not character:
        await message.reply_text(capsify('This Waifu is not in your collection🙄'))
        return

    if message.chat.id == group_id_to_use_for_log:
        await handle_confirmation(user_id, character_id, character)
    else:
        # Send the image with confirmation buttons in a single message
        await message.reply_photo(
            photo=character['img_url'],  # Use the character's image URL
            caption=capsify(f'Are you sure you want to make {character["name"]} your favorite Waifu?'),
            reply_markup=IKM(
                [
                    [
                        IKB(capsify("✅ Yes"), callback_data=f'confirm_{user_id}_{character_id}'),
                        IKB(capsify("❌ No"), callback_data=f'cancel_{user_id}_{character_id}')
                    ]
                ]
            )
        )
        # keyboard = IKM(
        #     [
        #         [IKB(capsify("INLINE"), switch_inline_query_current_chat=f"{character_id}")],
        #         [
        #             IKB(capsify("CONFIRM"), callback_data=f'confirm_{user_id}_{character_id}'),
        #             IKB(capsify("CANCEL"), callback_data=f'cancel_{user_id}_{character_id}')
        #         ]
        #     ]
        # )
        # await message.reply_text(capsify(f'Do you want to make {character["name"]} your favorite slave?'), reply_markup=keyboard)

async def handle_confirmation(user_id, character_id, character=None):
    if character:
        user = await user_collection.find_one({'id': user_id})
        if user:
            user['favorites'] = [character_id]
            await user_collection.update_one({'id': user_id}, {'$set': {'favorites': user['favorites']}})
            await app.send_message(user_id, capsify(f'Waifu {character["name"]} is your favorite now...'))
    else:
        await app.send_message(user_id, capsify('You have not got any Waifu yet...'))

@app.on_callback_query(filters.regex(r'^(confirm_|cancel_)'))
@block_cbq
async def button(client: Client, callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    data = callback_query.data
    action, cmd_user_id, character_id = data.split('_')

    if int(cmd_user_id) != user_id:
        await callback_query.answer("This is not for you baka ❗", show_alert=True)
        return

    # Delete the original message containing the image and buttons
    await callback_query.message.delete()

    if callback_query.message.chat.id == group_id_to_use_for_log:
        if action == "confirm":
            await handle_confirmation(user_id, character_id)
        else:
            await app.send_message(user_id, capsify('Operation canceled.'))
    else:
        if action == "confirm":
            user = await user_collection.find_one({'id': user_id})
            if user:
                character = next((c for c in user['characters'] if c['id'] == character_id), None)
                if character:
                    user['favorites'] = [character_id]
                    await user_collection.update_one({'id': user_id}, {'$set': {'favorites': user['favorites']}})
                    await app.send_message(user_id, capsify(f'Waifu {character["name"]} is your favorite now...'))
                else:
                    await app.send_message(user_id, capsify('This Waifu is not present in your Collection 🙄'))
            else:
                await app.send_message(user_id, capsify('You have not got any Waifus yet...😣'))
        elif action == "cancel":
            await app.send_message(user_id, capsify('Operation canceled.'))