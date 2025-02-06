import random
import io
import time
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton as IKB, InlineKeyboardMarkup as IKM
from Grabber.modules.Utility.image_utils import *
from Grabber.modules.GroupGames.wordlist import word_list_of_characters
from Grabber.modules.watchers import gend_watcher

from Grabber.modules import group_user_totals_collection,sudb,app,add, deduct, show,sudo_filter,capsify
from Grabber.config import *
from Grabber.config_settings import *
from Grabber.utils.sudo import *


alpha_dict = {}
guess_start_time = {}
group_message_counts = {}
DEFAULT_MESSAGE_LIMIT = 25


@app.on_message(filters.command("wtime") & sudo_filter)
async def set_word_message_limit(client, message):
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
        await message.reply_text(capsify(f"Message limit set to {limit}. Now spawning word every {limit} messages!"))
    except (IndexError, ValueError):
        await message.reply_text(capsify("Please provide a valid message limit (integer)."))


def shuffle_characters(word):
    """Shuffle characters of the word randomly"""
    word_list = list(word)
    random.shuffle(word_list)
    return ''.join(word_list)

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

        random_word = random.choice(word_list_of_characters)
        processed_word = shuffle_characters(random_word)
        alpha_dict[chat_id] = random_word
        guess_start_time[chat_id] = time.time()

        # image_bytes = generate_random_word_image(random_word)
        # keyboard = [[IKB("Support", url=f"https://t.me/{SUPPORT_CHAT}"), IKB("Play", url=f"https://t.me/{PLAY_CHAT}")]]
        # reply_markup = IKM(keyboard)

        # await client.send_photo(chat_id, photo=image_bytes, caption="Guess the word!", reply_markup=reply_markup)
        # await client.send_message(chat_id, text=f"Guess the word: {shifted_word}", reply_markup=reply_markup)
        await client.send_message(chat_id, text=f"Say the character's name right,\nTrue fans know the difference! 😉\n**{processed_word}**\nReply with the correct answer to Win LP and increase your Love Stash !🎊\n")

@app.on_message(filters.group)
async def handle_guess(client, message):
    chat_id = message.chat.id
    user_guess = message.text.strip().lower()

    if chat_id in alpha_dict:
        correct_answer = alpha_dict[chat_id].lower()
        if user_guess == correct_answer:
            reward = random.randint(20000, 40000)
            await add(message.from_user.id, reward)

            await message.reply(
                f"✨Correct!✨ You earned {reward:,.0f} {currency_names_plural['balance']}! 💖"
            )

            # Remove the guessed word to prevent duplicate guesses
            del alpha_dict[chat_id]
            del guess_start_time[chat_id]