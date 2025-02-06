import random
import html

from pyrogram import Client, filters
from Grabber import app, group_user_totals_collection
from Grabber.utils.bal import add
from Grabber.modules.block import block_cbq
from Grabber.modules.Utility.image_utils import generate_random_math_image

from Grabber import user_collection, collection
from Grabber.modules import add, deduct, show, abank, dbank, sbank, sudb, capsify, app, sudo_filter, group_user_totals_collection, capsify
from Grabber.modules.watchers import delta_watcher
from Grabber.utils.sudo import *
from Grabber.config_settings import *

math_questions = {}
group_message_counts = {}

DEFAULT_MESSAGE_LIMIT = 30

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

async def generate_random_math_equation():
    # Define possible operators
    operators = ['+', '-', '*']

    # Randomly select two numbers and an operator
    num1 = random.randint(1, 20)
    num2 = random.randint(1, 20)
    operator = random.choice(operators)

    # Ensure no division by zero
    if operator == '/':
        num2 = random.randint(1, 20)  # Ensure non-zero divisor

    # Generate the equation and calculate the answer
    equation = f"{num1} {operator} {num2}"

    # Perform the calculation based on the operator
    if operator == '+':
        answer = num1 + num2
    elif operator == '-':
        answer = num1 - num2
    elif operator == '*':
        answer = num1 * num2
    elif operator == '/':
        # Ensure the answer is an integer
        answer = num1 // num2  # Use floor division for integer result

    return equation, answer

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

        question, answer = await generate_random_math_equation()  # This function can return a text question now.
        math_questions[chat_id] = answer

        # Ensure that the text is safe for HTML parsing
        question = html.escape(question)  # This will escape any HTML special characters

        # Send the math equation as text
        await client.send_message(
            chat_id, 
            text=f"Time to test your brainpower! 🧠\nSolve this math equation and prove it! 🤓\n\n**{question}**\n\nReply with the correct answer to Win LP and increase your Love Stash !🎊\n"
        )

@app.on_message(filters.group & filters.reply)
async def check_reply(client, message):
    chat_id = message.chat.id

    if chat_id not in math_questions:
        return

    if message.text == str(math_questions[chat_id]):
        reward = random.randint(20000, 40000)
        
        await message.reply(
            f"✨Correct!✨ You earned {reward:,.0f} {currency_names_plural['balance']}! 💖"
        )
        
        await add(message.from_user.id, reward)
    else:
        await message.reply_text(capsify("Incorrect! Try again later."))

    # Remove the current question from the math_questions dictionary
    del math_questions[chat_id]
