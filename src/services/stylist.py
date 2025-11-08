"""
Stylist service - color analysis and outfit try-on business logic.
"""
import json
from PIL import Image
from google.genai import types

from src.config import config
from src.models import AnalyzeColorSeasonResponseModel
from src.utils.image_utils import base64_to_image
from src.services.ensemble import ensemble_analyzer

client = config.get_client()

def get_your_face_shape(image_input: str | Image.Image) -> str:
    """
    Analyze face shape from an image.
    """
    if isinstance(image_input, str):
        image = base64_to_image(image_input)
    else:
        image = image_input

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        config=types.GenerateContentConfig(
            system_instruction="You are a helpful assistant that analyzes the face shape of a person in an image. You will return the face shape of the person in the image.",
            response_mime_type="text/plain",
        ),
        contents=[image],
    )

    return response.text.strip()

def get_your_body_shape(image_input: str | Image.Image) -> str:
    """
    Analyze body shape from an image.
    """
    if isinstance(image_input, str):
        image = base64_to_image(image_input)
    else:
        image = image_input

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        config=types.GenerateContentConfig(
            system_instruction="You are a helpful assistant that analyzes the body shape of a person in an image. You will return the body shape of the person in the image.",
            response_mime_type="text/plain",
        ),
        contents=[image],
    )

    return response.text.strip()

def get_your_color_season(
    image_input: str | Image.Image,
) -> AnalyzeColorSeasonResponseModel:
    """
    Analyze color season from an image (single model - Gemini only).
    This is the original implementation for backward compatibility.

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
        
        # Provide defaults for missing fields
        defaults = {
            "undertone": "unknown",
            "season": "unknown",
            "subtype": "unknown",
            "reasoning": ""
        }
        for key, default_value in defaults.items():
            if key not in data or data[key] is None:
                data[key] = default_value
        
        model = AnalyzeColorSeasonResponseModel.model_validate(data)
        return model

    except json.JSONDecodeError as e:
        raise ValueError(f"JSON decode error: {e}. Response text: {response_text[:200]}")
    except Exception as e:
        # Log the actual data received for debugging
        try:
            data_str = json.dumps(data, indent=2) if 'data' in locals() else "No data parsed"
        except:
            data_str = "Could not serialize data"
        raise ValueError(
            f"Validation error: {e}\n"
            f"Received data: {data_str}\n"
            f"Response text (first 500 chars): {response_text[:500]}"
        )


async def get_your_color_season_ensemble_parallel(
    image_input: str | Image.Image,
    aggregation_method: str = "weighted_average"
) -> AnalyzeColorSeasonResponseModel:
    """
    Analyze color season using ensemble of 3 models (Gemini, OpenAI, Claude) in parallel.
    
    All models analyze simultaneously, then results are aggregated.
    This is the fastest ensemble approach.
    
    Args:
        image_input: Either a base64 string/data URL or a PIL Image object
        aggregation_method: "voting", "weighted_average", or "consensus"
    
    Returns:
        AnalyzeColorSeasonResponseModel object with aggregated results
    """
    return await ensemble_analyzer.analyze_parallel(
        image_input, 
        aggregation_method=aggregation_method
    )


async def get_your_color_season_ensemble_hybrid(
    image_input: str | Image.Image,
    judge_model: str = "gemini"
) -> AnalyzeColorSeasonResponseModel:
    """
    Analyze color season using hybrid ensemble approach.
    
    Two models analyze in parallel, third model acts as judge/evaluator.
    This provides deeper analysis and validation.
    
    Args:
        image_input: Either a base64 string/data URL or a PIL Image object
        judge_model: "gemini", "openai", or "claude" - which model judges the results
    
    Returns:
        AnalyzeColorSeasonResponseModel object with judged results
    """
    return await ensemble_analyzer.analyze_hybrid(
        image_input,
        judge_model=judge_model
    )


def get_outfit_on(
    user_image_input: str | Image.Image, product_image_input: str | Image.Image
) -> Image.Image:
    """
    Generate outfit try-on image.

    Args:
        user_image_input: Either a base64 string/data URL or a PIL Image object
        product_image_input: Either a base64 string/data URL or a PIL Image object
    
    Returns:
        PIL Image object with the try-on result
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
            from io import BytesIO
            image = Image.open(BytesIO(part.inline_data.data))
            return image

