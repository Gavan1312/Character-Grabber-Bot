from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton as IKB, InlineKeyboardMarkup as IKM
from PIL import Image, ImageDraw, ImageFont
import io
import random
import time
from . import app as bot

BG_IMAGE_PATH = "Images/blue.jpg"  # Your background image
LEVELS = [
    ("💫 Novice", "New to the world of love and affection.", (0, 10)),
    ("✨ Dreamer", "A heart full of potential and desires.", (11, 30)),
    ("⚡️ Spark", "Electric chemistry, igniting passions.", (31, 50)),
    ("🔥 Fiery", "Burning with determination and love.", (51, 75)),
    ("💖 Knight", "A protector of hearts, always devoted.", (76, 100)),
    ("🏆 Champion", "Champion of hearts, admired by all.", (101, 125)),
    ("🛡 Guardian", "A gentle guardian, shielding love with care.", (126, 150)),
    ("🏅 Hero", "A true hero, winning hearts with kindness.", (151, 175)),
    ("👑 Emperor", "Ruler of hearts, commanding affection.", (176, 200)),
    ("🏰 Sovereign", "The supreme ruler of love, cherished by all.", (201, 2000))
]
FONT_PATH = 'Fonts/font.ttf'  # Your custom font file

async def generate_levels_image() -> io.BytesIO:
    img = Image.open(BG_IMAGE_PATH)
    draw = ImageDraw.Draw(img)

    # Load the font, fall back to default if not available
    try:
        font = ImageFont.truetype(FONT_PATH, 40)
    except IOError:
        font = ImageFont.load_default()

    # Draw the level titles and descriptions
    y_position = 20  # Start drawing from the top
    for level in LEVELS:
        title, description, _range = level
        draw.text((20, y_position), f"{title} ({_range[0]} - {_range[1]})", font=font, fill=(0, 0, 0))
        y_position += 50  # Add space between each level

        # Draw description below title
        draw.text((20, y_position), description, font=font, fill=(0, 0, 0))
        y_position += 70  # Add space between description and next title

    # Save the image to a byte buffer
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='PNG')
    img_byte_arr.seek(0)

    return img_byte_arr

@bot.on_message(filters.command("levels_png"))
async def on_levels(client, message):
    # Generate the levels image
    levels_image = await generate_levels_image()

    # Send the image to the user
    await message.reply_photo(levels_image, caption="Here are the different levels!")
