import random
import io
import time
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton as IKB, InlineKeyboardMarkup as IKM
from Grabber import app, group_user_totals_collection
from Grabber.utils.bal import add
from Grabber.modules.Utility.image_utils import generate_random_math_image
from words import words
from Grabber.modules.watchers import gend_watcher

from Grabber.utils.bal  import add, deduct, show
from Grabber.modules import group_user_totals_collection,sudb
from words import words
from Grabber.config import *
from Grabber.config_settings import *


alpha_dict = {}
guess_start_time = {}
group_message_counts = {}
DEFAULT_MESSAGE_LIMIT = 30

@app.on_message(filters.text, group=gend_watcher)
async def on_message(client, message):
    chat_id = message.chat.id
    group_message_counts.setdefault(chat_id, {'count': 0, 'limit': DEFAULT_MESSAGE_LIMIT})
    group_message_counts[chat_id]['count'] += 1

    if group_message_counts[chat_id]['count'] >= group_message_counts[chat_id]['limit']:
        group_message_counts[chat_id]['count'] = 0

        random_word = random.choice(words)
        alpha_dict[chat_id] = random_word
        guess_start_time[chat_id] = time.time()

        image_bytes = generate_random_word_image(random_word)
        keyboard = [[IKB("Support", url="https://t.me/support"), IKB("Play", url="https://t.me/play")]]
        reply_markup = IKM(keyboard)

        await client.send_photo(chat_id, photo=image_bytes, caption="Guess the word!", reply_markup=reply_markup)

@app.on_message(filters.text)
async def handle_guess(client, message):
    chat_id = message.chat.id
    if chat_id in alpha_dict and message.text.strip().lower() == alpha_dict[chat_id]:
        reward = random.randint(20000, 40000)
        await add(message.from_user.id, reward)
        await message.reply(f"Correct! You earned {reward} 🔖")
