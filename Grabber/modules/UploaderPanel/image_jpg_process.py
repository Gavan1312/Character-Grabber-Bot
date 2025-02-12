from PIL import Image
import os

def process_image_to_jpg(image_path):
    """Converts a local image to JPG if necessary and returns the file path."""
    quality=95
    
    if not os.path.exists(image_path):
        raise Exception(f"File not found: {image_path}")
    
    # Open image
    image = Image.open(image_path)
    format = image.format.lower()

    # If already JPG, return original path
    if format in ["jpeg", "jpg"]:
        return image_path  # ✅ Return file path

    # Convert to JPG
    new_path = image_path.rsplit(".", 1)[0] + ".jpg"  # Change extension to .jpg
    image = image.convert("RGB")
    image.save(new_path, "JPEG", quality=quality, optimize=True)

    return new_path  # ✅ Return new file path
