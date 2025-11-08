"""
Image utility functions.
"""
import base64
from io import BytesIO
from PIL import Image


def base64_to_image(base64_string_or_data_url: str) -> Image.Image:
    """
    Convert a base64 string or data URL to a PIL Image object.

    Args:
        base64_string_or_data_url: Base64 string (with or without data URL prefix)

    Returns:
        PIL Image object
    """
    # Remove data URL prefix if present (e.g., "data:image/png;base64,")
    if base64_string_or_data_url.startswith("data:"):
        # Extract base64 part after the comma
        base64_string_or_data_url = base64_string_or_data_url.split(",", 1)[1]

    # Decode base64 string to bytes
    image_data = base64.b64decode(base64_string_or_data_url)

    # Create PIL Image from bytes
    image = Image.open(BytesIO(image_data))

    return image

