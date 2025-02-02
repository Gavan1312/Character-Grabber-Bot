import random
import io
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton as IKB, InlineKeyboardMarkup as IKM
from Grabber import add, capsify, app, sudo_filter, group_user_totals_collection
from modules.block import block_cbq
from Utility.image_utils import generate_random_math_image

math_questions = {}
group_message_counts = {}

DEFAULT_MESSAGE_LIMIT = 45

@app.on_message(filters.command("stime") & sudo_filter)
async def set_message_limit(client, message):
    user_id = message.from_user.id
    if user_id not in await get_sudo_user_ids():
        await message.reply_text(capsify("Only sudo users can set the message limit!"))
        return

    try:
        limit = int(message.command[1])
        if limit <= 0:
            await message.reply_text(capsify("Message limit must be a positive integer!"))
            return

        group_message_counts[message.chat.id] = {'count': 0, 'limit': limit}
        await message.reply_text(capsify(f"Message limit set to {limit}. Now spawning math equations every {limit} messages!"))
    except (IndexError, ValueError):
        await message.reply_text(capsify("Please provide a valid message limit (integer)."))

@app.on_message(filters.group, group=delta_watcher)
async def delta(client, message):
    chat_id = message.chat.id
    group_message_counts.setdefault(chat_id, {'count': 0, 'limit': DEFAULT_MESSAGE_LIMIT})
    group_message_counts[chat_id]['count'] += 1

    if group_message_counts[chat_id]['count'] >= group_message_counts[chat_id]['limit']:
        group_message_counts[chat_id]['count'] = 0

        chat_modes = await group_user_totals_collection.find_one({"chat_id": chat_id}) or DEFAULT_MODE_SETTINGS
        if not chat_modes.get('maths', True):
            return

        image_bytes, answer = generate_random_math_image()
        math_questions[chat_id] = answer

        keyboard = [
            [IKB(str(answer), callback_data='correct')],
            [IKB(str(random.randint(100, 999)), callback_data='incorrect1')],
            [IKB(str(random.randint(100, 999)), callback_data='incorrect2')],
            [IKB(str(random.randint(100, 999)), callback_data='incorrect3')]
        ]
        random.shuffle(keyboard)
        reply_markup = IKM([[keyboard[0][0], keyboard[1][0]], [keyboard[2][0], keyboard[3][0]]])

        await client.send_photo(
            chat_id=chat_id,
            photo=io.BytesIO(image_bytes),
            caption=capsify("Solve the math equation!"),
            reply_markup=reply_markup
        )

@app.on_callback_query(filters.regex('correct|incorrect'))
@block_cbq
async def sumu(client, callback_query):
    chat_id = callback_query.message.chat.id
    if chat_id not in math_questions:
        return

    if callback_query.data == 'correct':
        reward = random.randint(20000, 40000)
        await callback_query.answer(capsify(f"Correct! You earned {reward} 🔖"), show_alert=True)
        await add(callback_query.from_user.id, reward)
    else:
        await callback_query.answer(capsify("Incorrect! Try again later."), show_alert=True)

    del math_questions[chat_id]
    await callback_query.message.edit_caption(caption=capsify("Math equation solved!"), reply_markup=None)
