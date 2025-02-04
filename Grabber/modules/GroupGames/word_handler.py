import random
import io
import time
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton as IKB, InlineKeyboardMarkup as IKM
from Grabber import app, group_user_totals_collection
from Grabber.utils.bal import add
from Grabber.modules.Utility.image_utils import *
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

def shift_characters(word):
    """Shift characters of the word by a random amount"""
    shifted_word = []
    shift_amount = random.randint(1, 3)  # Shift by 1 to 3 positions for variety
    for char in word:
        if char.isalpha():  # Only shift alphabetic characters
            shifted_word.append(chr(((ord(char.lower()) - ord('a') + shift_amount) % 26) + ord('a')))
        else:
            shifted_word.append(char)  # Keep non-alphabetic characters unchanged
    return ''.join(shifted_word)

@app.on_message(filters.text, group=gend_watcher)
async def on_message(client, message):
    chat_id = message.chat.id
    group_message_counts.setdefault(chat_id, {'count': 0, 'limit': DEFAULT_MESSAGE_LIMIT})
    group_message_counts[chat_id]['count'] += 1

    if group_message_counts[chat_id]['count'] >= group_message_counts[chat_id]['limit']:
        group_message_counts[chat_id]['count'] = 0

        random_word = random.choice(words)
        shifted_word = shift_characters(random_word)
        alpha_dict[chat_id] = random_word
        guess_start_time[chat_id] = time.time()

        # image_bytes = generate_random_word_image(random_word)
        # keyboard = [[IKB("Support", url=f"https://t.me/{SUPPORT_CHAT}"), IKB("Play", url=f"https://t.me/{PLAY_CHAT}")]]
        # reply_markup = IKM(keyboard)

        # await client.send_photo(chat_id, photo=image_bytes, caption="Guess the word!", reply_markup=reply_markup)
        # await client.send_message(chat_id, text=f"Guess the word: {shifted_word}", reply_markup=reply_markup)
        await client.send_message(chat_id, text=f"Guess the word: {shifted_word}")

@app.on_message(filters.text)
async def handle_guess(client, message):
    chat_id = message.chat.id
    if chat_id in alpha_dict and message.text.strip().lower() == alpha_dict[chat_id]:
        reward = random.randint(20000, 40000)
        await add(message.from_user.id, reward)
        await message.reply(f"Correct! You earned {reward} {currency_names_plural['balance']}")
