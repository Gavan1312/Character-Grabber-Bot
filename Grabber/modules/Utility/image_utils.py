import random
import io
from PIL import Image, ImageDraw, ImageFont

BG_IMAGE_PATH = "Images/blue.jpg"  # Background image path
FONT_PATH = "Fonts/font.ttf"  # Font path

def create_text_image(text: str, font_size: int = 60) -> io.BytesIO:
    """Generates an image with the given text centered on it."""
    img = Image.open(BG_IMAGE_PATH)
    d = ImageDraw.Draw(img)
    fnt = ImageFont.truetype(FONT_PATH, font_size)

    # Get text size (newer Pillow version)
    bbox = d.textbbox((0, 0), text, font=fnt)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    # Center text
    text_x = (img.width - text_width) / 2
    text_y = (img.height - text_height) / 2

    # Draw text on image
    d.text((text_x, text_y), text, font=fnt, fill=(0, 0, 0))

    # Convert image to bytes
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='PNG')
    img_byte_arr.seek(0)

    return img_byte_arr

def generate_math_equation() -> tuple[str, int]:
    """Generates a random math equation and its answer."""
    num1 = random.randint(100, 999)
    num2 = random.randint(100, 999)
    operation = random.choice(['+', '-', '*'])

    if operation == '+':
        answer = num1 + num2
    elif operation == '-':
        answer = num1 - num2
    else:
        answer = num1 * num2

    equation = f"{num1} {operation} {num2} = ?"
    return equation, answer

def generate_random_math_image() -> tuple[bytes, int]:
    """Generates an image containing a random math equation and returns the answer."""
    equation, answer = generate_math_equation()
    img_bytes = create_text_image(equation, font_size=60)
    return img_bytes.getvalue(), answer

def generate_random_word_image(word: str) -> bytes:
    """Generates an image with a given word."""
    return create_text_image(word, font_size=76)
