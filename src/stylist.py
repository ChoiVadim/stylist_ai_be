import json
import base64
from io import BytesIO
from PIL import Image
from google.genai import types

from src.config import config
from src.models import AnalyzeColorSeasonResponseModel

client = config.get_client()


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


def get_your_color_season(
    image_input: str | Image.Image,
) -> AnalyzeColorSeasonResponseModel:
    """
    Analyze color season from an image.

    Args:
        image_input: Either a base64 string/data URL or a PIL Image object

    Returns:
        AnalyzeColorSeasonResponseModel object
    """
    if isinstance(image_input, str):
        image = base64_to_image(image_input)
    else:
        image = image_input

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        config=types.GenerateContentConfig(
            system_instruction=config.SYSTEM_PROMPT,
            response_mime_type="application/json",
        ),
        contents=[image, config.JSON_PROMPT],
    )

    try:
        response_text = response.text.strip()
        if response_text.startswith("```json"):
            response_text = response_text[7:]
        if response_text.startswith("```"):
            response_text = response_text[3:]
        if response_text.endswith("```"):
            response_text = response_text[:-3]
        response_text = response_text.strip()

        data = json.loads(response_text)
        model = AnalyzeColorSeasonResponseModel.model_validate(data)
        return model

    except json.JSONDecodeError as e:
        raise ValueError(f"JSON decode error: {e}")
    except Exception as e:
        raise ValueError(f"Unexpected error: {e}")


def get_outfit_on(
    user_image_input: str | Image.Image, product_image_input: str | Image.Image
) -> Image.Image:
    """
    Generate outfit try-on image.

    Args:
        user_image_input: Either a base64 string/data URL or a PIL Image object
        product_image_input: Either a base64 string/data URL or a PIL Image object
    """
    prompt = config.NANO_BANANA_PROMPT

    # Convert to PIL Images if they're strings
    if isinstance(user_image_input, str):
        user_image = base64_to_image(user_image_input)
    else:
        user_image = user_image_input

    if isinstance(product_image_input, str):
        product_image = base64_to_image(product_image_input)
    else:
        product_image = product_image_input

    contents = [prompt, user_image, product_image]

    response = client.models.generate_content(
        model="gemini-2.5-flash-image",
        contents=contents,
        config=types.GenerateContentConfig(
            image_config=types.ImageConfig(
                aspect_ratio="9:16",
            )
        ),
    )

    for part in response.candidates[0].content.parts:
        if part.text is not None:
            print(part.text)
        elif part.inline_data is not None:
            image = Image.open(BytesIO(part.inline_data.data))
            # image.save("images/generated_image.png")
            return image
