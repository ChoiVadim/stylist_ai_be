"""
Beauty-related API endpoints (makeup and hair recommendations).
"""
from fastapi import APIRouter, HTTPException
import time
import json
from PIL import Image
from google.genai import types

from src.config import config
from src.models import (
    MakeupRecommendationRequest,
    MakeupRecommendationResponse,
    HairRecommendationRequest,
    HairRecommendationResponse
)
from src.services.stylist import get_your_color_season
from src.utils.logger import get_logger
from src.utils.image_validator import (
    validate_image_from_base64,
    ImageValidationError
)
from src.utils.image_utils import base64_to_image

logger = get_logger("api.beauty")
router = APIRouter(prefix="/api/beauty", tags=["beauty"])

client = config.get_client()


def get_makeup_recommendations(
    face_image_input: str | Image.Image,
    personal_color_type: str | None = None
) -> dict:
    """
    Get makeup recommendations based on face image and personal color type.
    
    Args:
        face_image_input: Either a base64 string/data URL or a PIL Image object
        personal_color_type: Optional personal color type (if not provided, will be analyzed)
    
    Returns:
        Dictionary with makeup recommendations
    """
    if isinstance(face_image_input, str):
        image = base64_to_image(face_image_input)
    else:
        image = face_image_input
    
    # Analyze personal color if not provided
    if not personal_color_type:
        color_result = get_your_color_season(image)
        personal_color_type = color_result.personal_color_type
    else:
        color_result = None
    
    # Create prompt for makeup recommendations
    makeup_prompt = f"""Analyze this face image and provide makeup recommendations based on the person's personal color type: {personal_color_type}.

Consider:
1. Lipstick colors that complement the personal color type (provide HEX codes)
2. Eyeshadow colors that enhance the natural eye color and skin tone (provide HEX codes)
3. Blush colors that create a natural, harmonious look (provide HEX codes)
4. Foundation tone recommendations

Return ONLY a valid JSON object with this exact structure:
{{
    "lipstick_colors": ["#HEX1", "#HEX2", "#HEX3"],
    "eyeshadow_colors": ["#HEX1", "#HEX2", "#HEX3"],
    "blush_colors": ["#HEX1", "#HEX2"],
    "foundation_tone": "description of recommended foundation tone",
    "recommendations": "detailed makeup recommendations and tips"
}}"""
    
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
        ),
        contents=[image, makeup_prompt],
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
        
        result = {
            "personal_color_type": personal_color_type,
            "lipstick_colors": data.get("lipstick_colors", []),
            "eyeshadow_colors": data.get("eyeshadow_colors", []),
            "blush_colors": data.get("blush_colors", []),
            "foundation_tone": data.get("foundation_tone", "Natural"),
            "recommendations": data.get("recommendations", "No recommendations provided")
        }
        
        return result
    except json.JSONDecodeError as e:
        raise ValueError(f"JSON decode error: {e}. Response text: {response_text[:200]}")
    except Exception as e:
        raise ValueError(f"Error parsing makeup recommendations: {e}")


def get_hair_recommendations(
    face_image_input: str | Image.Image,
    personal_color_type: str | None = None,
    current_hair_color: str | None = None
) -> dict:
    """
    Get hair recommendations based on face image and personal color type.
    
    Args:
        face_image_input: Either a base64 string/data URL or a PIL Image object
        personal_color_type: Optional personal color type (if not provided, will be analyzed)
        current_hair_color: Optional current hair color description
    
    Returns:
        Dictionary with hair recommendations
    """
    if isinstance(face_image_input, str):
        image = base64_to_image(face_image_input)
    else:
        image = face_image_input
    
    # Analyze personal color if not provided
    if not personal_color_type:
        color_result = get_your_color_season(image)
        personal_color_type = color_result.personal_color_type
    else:
        color_result = None
    
    # Create prompt for hair recommendations
    hair_info = f"Current hair color: {current_hair_color}" if current_hair_color else "Current hair color: not specified"
    
    hair_prompt = f"""Analyze this face image and provide hair color and style recommendations based on the person's personal color type: {personal_color_type}. {hair_info}

Consider:
1. Hair colors that complement the personal color type (provide HEX codes for recommended colors)
2. Hair styles that suit the face shape and personal color type
3. Overall recommendations for hair care and styling

Return ONLY a valid JSON object with this exact structure:
{{
    "recommended_colors": ["#HEX1", "#HEX2", "#HEX3"],
    "recommended_styles": ["style1", "style2", "style3"],
    "recommendations": "detailed hair recommendations and tips"
}}"""
    
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
        ),
        contents=[image, hair_prompt],
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
        
        result = {
            "personal_color_type": personal_color_type,
            "recommended_colors": data.get("recommended_colors", []),
            "recommended_styles": data.get("recommended_styles", []),
            "recommendations": data.get("recommendations", "No recommendations provided")
        }
        
        return result
    except json.JSONDecodeError as e:
        raise ValueError(f"JSON decode error: {e}. Response text: {response_text[:200]}")
    except Exception as e:
        raise ValueError(f"Error parsing hair recommendations: {e}")


@router.post("/makeup", response_model=MakeupRecommendationResponse)
def get_makeup_recommendations_endpoint(request: MakeupRecommendationRequest):
    """
    Get makeup recommendations based on face image and personal color type.
    
    Provides personalized makeup color recommendations including lipstick, eyeshadow,
    blush colors in HEX format, and foundation tone suggestions.
    
    Args:
        request: Contains face_image (base64) and optional personal_color_type
    
    Returns:
        MakeupRecommendationResponse with color recommendations and tips
    """
    start_time = time.time()
    logger.info("Makeup recommendation request received")
    
    try:
        # Validate image
        try:
            image, validation_result = validate_image_from_base64(
                request.face_image,
                require_face=True,  # Makeup recommendations require face
                max_dimension=4096,
                min_dimension=100
            )
            logger.debug(f"Image validated: {validation_result}")
        except ImageValidationError as e:
            logger.warning(f"Image validation failed: {str(e)}")
            raise HTTPException(status_code=400, detail=str(e))
        
        # Get makeup recommendations
        result = get_makeup_recommendations(
            image,
            personal_color_type=request.personal_color_type
        )
        
        process_time = time.time() - start_time
        logger.info(
            f"Makeup recommendations completed: personal_color_type={result['personal_color_type']}, "
            f"time={process_time:.2f}s"
        )
        
        return MakeupRecommendationResponse(**result)
    except HTTPException:
        raise
    except Exception as e:
        process_time = time.time() - start_time
        logger.error(
            f"Makeup recommendations failed: {str(e)}, time={process_time:.2f}s",
            exc_info=True
        )
        raise HTTPException(status_code=500, detail=f"Error getting makeup recommendations: {str(e)}")


@router.post("/hair", response_model=HairRecommendationResponse)
def get_hair_recommendations_endpoint(request: HairRecommendationRequest):
    """
    Get hair color and style recommendations based on face image and personal color type.
    
    Provides personalized hair color recommendations in HEX format and style suggestions
    that complement the user's personal color type and face shape.
    
    Args:
        request: Contains face_image (base64), optional personal_color_type, and optional current_hair_color
    
    Returns:
        HairRecommendationResponse with color and style recommendations
    """
    start_time = time.time()
    logger.info("Hair recommendation request received")
    
    try:
        # Validate image
        try:
            image, validation_result = validate_image_from_base64(
                request.face_image,
                require_face=True,  # Hair recommendations require face
                max_dimension=4096,
                min_dimension=100
            )
            logger.debug(f"Image validated: {validation_result}")
        except ImageValidationError as e:
            logger.warning(f"Image validation failed: {str(e)}")
            raise HTTPException(status_code=400, detail=str(e))
        
        # Get hair recommendations
        result = get_hair_recommendations(
            image,
            personal_color_type=request.personal_color_type,
            current_hair_color=request.current_hair_color
        )
        
        process_time = time.time() - start_time
        logger.info(
            f"Hair recommendations completed: personal_color_type={result['personal_color_type']}, "
            f"time={process_time:.2f}s"
        )
        
        return HairRecommendationResponse(**result)
    except HTTPException:
        raise
    except Exception as e:
        process_time = time.time() - start_time
        logger.error(
            f"Hair recommendations failed: {str(e)}, time={process_time:.2f}s",
            exc_info=True
        )
        raise HTTPException(status_code=500, detail=f"Error getting hair recommendations: {str(e)}")

