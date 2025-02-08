import os
import pytz
from PIL import Image, ImageDraw, ImageFont
import requests
from io import BytesIO
from pyrogram import Client, filters
from . import user_collection, collection, app, capsify
from .block import block_dec, temp_block
from Grabber.config_settings import *

# --- Helper function to generate the bounty poster image ---
def generate_bounty_poster(profile_image_path: str) -> str:
    """
    Generates a bounty poster using the user's profile image.
    The poster includes "WANTED" at the top, the profile image centered,
    and "REWARD" below the image. Returns the temporary poster file path.
    """
    # Poster dimensions and background color (parchment-like)
    poster_width, poster_height = 600, 800
    background_color = (230, 200, 160)  # light brown parchment color
    poster = Image.new("RGB", (poster_width, poster_height), background_color)
    draw = ImageDraw.Draw(poster)

    # --- Load Fonts ---
    try:
        # Change these paths if needed; ensure western.ttf exists
        title_font = ImageFont.truetype("western.ttf", 80)
        text_font = ImageFont.truetype("arial.ttf", 40)
    except Exception as e:
        print(f"Font load error: {e}. Using default fonts.")
        title_font = ImageFont.load_default()
        text_font = ImageFont.load_default()

    # --- Add "WANTED" at the top ---
    wanted_text = "WANTED"
    text_width, text_height = draw.textsize(wanted_text, font=title_font)
    draw.text(
        ((poster_width - text_width) / 2, 30),
        wanted_text,
        font=title_font,
        fill="black"
    )

    # --- Process the profile image ---
    try:
        profile_img = Image.open(profile_image_path).convert("RGB")
    except Exception as e:
        print(f"Error opening profile image: {e}")
        # If for some reason we can't open the image, return the poster as-is
        profile_img = Image.new("RGB", (300, 300), (255, 255, 255))

    # Ensure the profile image is square.
    # Option 1: Resize it directly to 300x300 (might distort if not square)
    profile_img = profile_img.resize((300, 300))

    # Option 2: Crop to square (uncomment if you prefer cropping)
    # width, height = profile_img.size
    # min_dim = min(width, height)
    # left = (width - min_dim) // 2
    # top = (height - min_dim) // 2
    # right = left + min_dim
    # bottom = top + min_dim
    # profile_img = profile_img.crop((left, top, right, bottom)).resize((300,300))

    # --- Paste the profile image in the center of the poster ---
    image_x = (poster_width - 300) // 2
    image_y = (poster_height - 300) // 2
    poster.paste(profile_img, (image_x, image_y))

    # --- Add "REWARD" text below the profile image ---
    reward_text = "REWARD"
    reward_width, reward_height = draw.textsize(reward_text, font=title_font)
    reward_y = image_y + 300 + 20  # 20 pixels below the image
    draw.text(
        ((poster_width - reward_width) / 2, reward_y),
        reward_text,
        font=title_font,
        fill="black"
    )

    # Optionally, add additional decoration or reward amount text here

    # Save the generated poster to a temporary file
    poster_path = "temp_poster.jpg"
    poster.save(poster_path)
    return poster_path


# --- Your xprofile command handler ---
@app.on_message(filters.command('xprofilen'))
@block_dec
async def xprofile(client, message):
    user_id = message.from_user.id
    if temp_block(user_id):
        return

    try:
        user_data = await user_collection.find_one(
            {'id': user_id},
            projection={'balance': 1, 'saved_amount': 1, 'characters': 1, 'gender': 1, 'profile_media': 1, 'created_at': 1}
        )

        if user_data:
            balance_amount = int(user_data.get('balance', 0))
            bank_balance = int(user_data.get('saved_amount', 0))
            characters = user_data.get('characters', [])
            gender = user_data.get('gender')
            profile_media = user_data.get('profile_media')

            total_characters = len(characters)
            all_characters = await collection.find({}).to_list(length=None)
            total_database_characters = len(all_characters)

            gender_icon = '👦🏻' if gender == 'male' else '👧🏻' if gender == 'female' else '👶🏻'

            balance_message = capsify(
                f"PROFILE\n\n"
                f"Name: {message.from_user.first_name or ''} {message.from_user.last_name or ''} [{gender_icon}]\n"
                f"ID: `{user_id}`\n\n"
                f"Coins: {currency_symbols['balance']}`{balance_amount:,.0f}`\n"
                f"Bank: {currency_symbols['balance']}`{(bank_balance)}`\n"
                f"Characters: `{total_characters}/{total_database_characters}`\n"
                # f"Days Old: `{days_old}`\n"
            )

            if profile_media:
                # Download the user's profile image to a temporary file
                temp_profile_path = "temp_profile_image.jpg"
                await download_image(profile_media, temp_profile_path)

                # Generate the bounty poster using the downloaded profile image
                poster_path = generate_bounty_poster(temp_profile_path)

                # Send the poster as a photo with the remaining profile details as caption
                await message.reply_photo(
                    photo=poster_path,
                    caption=balance_message
                )

                # Clean up temporary files
                if os.path.exists(temp_profile_path):
                    os.remove(temp_profile_path)
                if os.path.exists(poster_path):
                    os.remove(poster_path)
            else:
                await message.reply_text(balance_message)

        else:
            await message.reply_text(capsify("Claim bonus first using /xbonus"))

    except Exception as e:
        await message.reply_text(capsify(f"An error occurred: {e}"))
