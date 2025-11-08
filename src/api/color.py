"""
Color analysis API endpoints.
"""
from fastapi import APIRouter, UploadFile, File, Query, HTTPException
from PIL import Image
from io import BytesIO
from typing import Literal
import time
from src.services import (
    get_your_color_season,
    get_your_color_season_ensemble_parallel,
    get_your_color_season_ensemble_hybrid,
)
from src.models import AnalyzeColorSeasonRequest
from src.utils.logger import get_logger
from src.utils.image_validator import (
    validate_image_from_bytes,
    validate_image_from_base64,
    ImageValidationError
)

logger = get_logger("api.color")
router = APIRouter(prefix="/api", tags=["color-analysis"])


@router.post("/test/analyze/color")
async def test_upload_image(file: UploadFile = File(...)):
    """
    Test endpoint: Analyze color season from uploaded image file.
    
    Use this for testing directly in FastAPI docs with file upload.
    """
    start_time = time.time()
    logger.info("Test color analysis request received (file upload)")
    
    try:
        contents = await file.read()
        
        # Validate image
        try:
            image, validation_result = validate_image_from_bytes(
                contents,
                require_face=True,  # Color analysis requires face
                max_dimension=4096,
                min_dimension=100
            )
            logger.debug(f"Image validated: {validation_result}")
        except ImageValidationError as e:
            logger.warning(f"Image validation failed: {str(e)}")
            raise HTTPException(status_code=400, detail=str(e))
        
        result = get_your_color_season(image)
        process_time = time.time() - start_time
        logger.info(
            f"Test color analysis completed: season={result.personal_color_type}, "
            f"confidence={result.confidence:.2f}, time={process_time:.2f}s"
        )
        return result.model_dump()
    except HTTPException:
        raise
    except Exception as e:
        process_time = time.time() - start_time
        logger.error(
            f"Test color analysis failed: {str(e)}, time={process_time:.2f}s",
            exc_info=True
        )
        return {"error": str(e)}


@router.post("/analyze/color")
def get_color_season(request: AnalyzeColorSeasonRequest):
    """
    Analyze color season from a base64-encoded image (single model - Gemini).
    
    Request body should contain:
    {
        "image": "data:image/png;base64,iVBORw0KGgo..." or just "iVBORw0KGgo..."
    }
    
    Returns:
        Personal color analysis results including season, undertone, confidence, etc.
    """
    start_time = time.time()
    logger.info("Color analysis request received (single model - Gemini)")
    
    try:
        # Validate image
        try:
            image, validation_result = validate_image_from_base64(
                request.image,
                require_face=True,  # Color analysis requires face
                max_dimension=4096,
                min_dimension=100
            )
            logger.debug(f"Image validated: {validation_result}")
        except ImageValidationError as e:
            logger.warning(f"Image validation failed: {str(e)}")
            raise HTTPException(status_code=400, detail=str(e))
        
        result = get_your_color_season(image)
        process_time = time.time() - start_time
        logger.info(
            f"Color analysis completed: season={result.personal_color_type}, "
            f"confidence={result.confidence:.2f}, time={process_time:.2f}s"
        )
        return result.model_dump()
    except HTTPException:
        raise
    except Exception as e:
        process_time = time.time() - start_time
        logger.error(
            f"Color analysis failed: {str(e)}, time={process_time:.2f}s",
            exc_info=True
        )
        return {"error": str(e)}


@router.post("/analyze/color/ensemble/parallel")
async def get_color_season_ensemble_parallel(
    request: AnalyzeColorSeasonRequest,
    aggregation_method: Literal["voting", "weighted_average", "consensus"] = Query(
        default="weighted_average",
        description="Method to aggregate results from multiple models"
    )
):
    """
    Analyze color season using ensemble of 3 models (Gemini, OpenAI, Claude) in parallel.
    
    All models analyze simultaneously, then results are aggregated.
    This is the fastest ensemble approach and provides diverse perspectives.
    
    Request body should contain:
    {
        "image": "data:image/png;base64,iVBORw0KGgo..." or just "iVBORw0KGgo..."
    }
    
    Query parameters:
    - aggregation_method: "voting" (majority vote), "weighted_average" (weight by confidence), 
      or "consensus" (require ≥67% agreement)
    
    Returns:
        Aggregated personal color analysis results from all models.
    """
    start_time = time.time()
    logger.info(f"Ensemble parallel color analysis request received (method={aggregation_method})")
    
    try:
        # Validate image
        try:
            image, validation_result = validate_image_from_base64(
                request.image,
                require_face=True,  # Color analysis requires face
                max_dimension=4096,
                min_dimension=100
            )
            logger.debug(f"Image validated: {validation_result}")
        except ImageValidationError as e:
            logger.warning(f"Image validation failed: {str(e)}")
            raise HTTPException(status_code=400, detail=str(e))
        
        result = await get_your_color_season_ensemble_parallel(
            image,
            aggregation_method=aggregation_method
        )
        process_time = time.time() - start_time
        logger.info(
            f"Ensemble parallel analysis completed: season={result.personal_color_type}, "
            f"confidence={result.confidence:.2f}, method={aggregation_method}, time={process_time:.2f}s"
        )
        return result.model_dump()
    except HTTPException:
        raise
    except Exception as e:
        process_time = time.time() - start_time
        logger.error(
            f"Ensemble parallel analysis failed: {str(e)}, method={aggregation_method}, time={process_time:.2f}s",
            exc_info=True
        )
        return {"error": str(e)}


@router.post("/analyze/color/ensemble/hybrid")
async def get_color_season_ensemble_hybrid(
    request: AnalyzeColorSeasonRequest,
    judge_model: Literal["gemini", "openai", "claude"] = Query(
        default="gemini",
        description="Which model acts as judge/evaluator"
    )
):
    """
    Analyze color season using hybrid ensemble approach.
    
    Two models (the remaining ones) analyze in parallel, third model acts as judge/evaluator.
    This provides deeper analysis and validation with expert judgment.
    
    Request body should contain:
    {
        "image": "data:image/png;base64,iVBORw0KGgo..." or just "iVBORw0KGgo..."
    }
    
    Query parameters:
    - judge_model: "gemini", "openai", or "claude" - which model evaluates the results
    
    Returns:
        Judged personal color analysis results with expert evaluation.
    """
    start_time = time.time()
    logger.info(f"Ensemble hybrid color analysis request received (judge_model={judge_model})")
    
    try:
        # Validate image
        try:
            image, validation_result = validate_image_from_base64(
                request.image,
                require_face=True,  # Color analysis requires face
                max_dimension=4096,
                min_dimension=100
            )
            logger.debug(f"Image validated: {validation_result}")
        except ImageValidationError as e:
            logger.warning(f"Image validation failed: {str(e)}")
            raise HTTPException(status_code=400, detail=str(e))
        
        result = await get_your_color_season_ensemble_hybrid(
            image,
            judge_model=judge_model
        )
        process_time = time.time() - start_time
        logger.info(
            f"Ensemble hybrid analysis completed: season={result.personal_color_type}, "
            f"confidence={result.confidence:.2f}, judge_model={judge_model}, time={process_time:.2f}s"
        )
        return result.model_dump()
    except HTTPException:
        raise
    except Exception as e:
        process_time = time.time() - start_time
        logger.error(
            f"Ensemble hybrid analysis failed: {str(e)}, judge_model={judge_model}, time={process_time:.2f}s",
            exc_info=True
        )
        return {"error": str(e)}


@router.post("/test/analyze/color/ensemble/parallel")
async def test_upload_image_ensemble_parallel(
    file: UploadFile = File(...),
    aggregation_method: Literal["voting", "weighted_average", "consensus"] = Query(
        default="weighted_average",
        description="Method to aggregate results from multiple models"
    )
):
    """
    Test endpoint: Analyze color season from uploaded image file using ensemble of 3 models in parallel.
    
    Use this for testing directly in FastAPI docs with file upload.
    """
    start_time = time.time()
    logger.info(f"Test ensemble parallel color analysis request received (file upload, method={aggregation_method})")
    
    try:
        contents = await file.read()
        
        # Validate image
        try:
            image, validation_result = validate_image_from_bytes(
                contents,
                require_face=True,  # Color analysis requires face
                max_dimension=4096,
                min_dimension=100
            )
            logger.debug(f"Image validated: {validation_result}")
        except ImageValidationError as e:
            logger.warning(f"Image validation failed: {str(e)}")
            raise HTTPException(status_code=400, detail=str(e))
        
        result = await get_your_color_season_ensemble_parallel(
            image,
            aggregation_method=aggregation_method
        )
        process_time = time.time() - start_time
        logger.info(
            f"Test ensemble parallel analysis completed: season={result.personal_color_type}, "
            f"confidence={result.confidence:.2f}, method={aggregation_method}, time={process_time:.2f}s"
        )
        return result.model_dump()
    except HTTPException:
        raise
    except Exception as e:
        process_time = time.time() - start_time
        logger.error(
            f"Test ensemble parallel analysis failed: {str(e)}, method={aggregation_method}, time={process_time:.2f}s",
            exc_info=True
        )
        return {"error": str(e)}

@router.post("/test/analyze/color/ensemble/hybrid")
async def test_upload_image_ensemble_hybrid(
    file: UploadFile = File(...),
    judge_model: Literal["gemini", "openai", "claude"] = Query(
        default="gemini",
        description="Which model acts as judge/evaluator"
    )
):
    """
    Test endpoint: Analyze color season from uploaded image file using ensemble of 3 models in hybrid.
    
    Use this for testing directly in FastAPI docs with file upload.
    """
    start_time = time.time()
    logger.info(f"Test ensemble hybrid color analysis request received (file upload, judge_model={judge_model})")
    
    try:
        contents = await file.read()
        
        # Validate image
        try:
            image, validation_result = validate_image_from_bytes(
                contents,
                require_face=True,  # Color analysis requires face
                max_dimension=4096,
                min_dimension=100
            )
            logger.debug(f"Image validated: {validation_result}")
        except ImageValidationError as e:
            logger.warning(f"Image validation failed: {str(e)}")
            raise HTTPException(status_code=400, detail=str(e))
        
        result = await get_your_color_season_ensemble_hybrid(
            image,
            judge_model=judge_model
        )
        process_time = time.time() - start_time
        logger.info(
            f"Test ensemble hybrid analysis completed: season={result.personal_color_type}, "
            f"confidence={result.confidence:.2f}, judge_model={judge_model}, time={process_time:.2f}s"
        )
        return result.model_dump()
    except HTTPException:
        raise
    except Exception as e:
        process_time = time.time() - start_time
        logger.error(
            f"Test ensemble hybrid analysis failed: {str(e)}, judge_model={judge_model}, time={process_time:.2f}s",
            exc_info=True
        )
        return {"error": str(e)}


# Color palette data for each season
COLOR_PALETTES = {
    # Spring palettes
    "Warm Spring": {
        "primary": ["#FFB347", "#FF6B6B", "#FFD93D", "#6BCB77", "#FFE5B4"],
        "secondary": ["#FF8C42", "#FFA07A", "#FFD700", "#98D8C8", "#F7DC6F"],
        "accent": ["#FF6347", "#FFA500", "#FFD700", "#90EE90", "#FFE4B5"]
    },
    "Bright Spring": {
        "primary": ["#FF6B6B", "#00CED1", "#FFD700", "#32CD32", "#FF1493"],
        "secondary": ["#FF4500", "#00BFFF", "#FFFF00", "#00FF7F", "#FF69B4"],
        "accent": ["#FF0000", "#00FFFF", "#FFD700", "#00FF00", "#FF1493"]
    },
    "Light Spring": {
        "primary": ["#FFB6C1", "#FFE4E1", "#FFFACD", "#B0E0E6", "#F0E68C"],
        "secondary": ["#FFC0CB", "#FFEFD5", "#FFFFE0", "#AFEEEE", "#FAFAD2"],
        "accent": ["#FF69B4", "#FFDAB9", "#FFFF99", "#87CEEB", "#EEE8AA"]
    },
    # Summer palettes
    "Light Summer": {
        "primary": ["#B0C4DE", "#FFB6C1", "#98FB98", "#F0F8FF", "#E0E0E0"],
        "secondary": ["#87CEEB", "#FFC0CB", "#90EE90", "#E6E6FA", "#D3D3D3"],
        "accent": ["#6495ED", "#FF69B4", "#7CFC00", "#B0E0E6", "#C0C0C0"]
    },
    "True Summer": {
        "primary": ["#708090", "#000080", "#9370DB", "#DA70D6", "#FFB6C1"],
        "secondary": ["#778899", "#191970", "#BA55D3", "#EE82EE", "#FFC0CB"],
        "accent": ["#2F4F4F", "#0000CD", "#8A2BE2", "#FF1493", "#FF69B4"]
    },
    "Soft Summer": {
        "primary": ["#778899", "#DDA0DD", "#98D8C8", "#B0C4DE", "#C0C0C0"],
        "secondary": ["#696969", "#DA70D6", "#AFEEEE", "#87CEEB", "#A9A9A9"],
        "accent": ["#2F4F4F", "#BA55D3", "#48D1CC", "#6495ED", "#808080"]
    },
    # Autumn palettes
    "Warm Autumn": {
        "primary": ["#CD853F", "#8B4513", "#FFD700", "#228B22", "#A0522D"],
        "secondary": ["#D2691E", "#A0522D", "#FFA500", "#32CD32", "#8B7355"],
        "accent": ["#FF6347", "#654321", "#FFD700", "#00FF00", "#6B4423"]
    },
    "Deep Autumn": {
        "primary": ["#008B8B", "#800020", "#8B4513", "#FF4500", "#2F4F4F"],
        "secondary": ["#48D1CC", "#8B0000", "#A0522D", "#FF6347", "#556B2F"],
        "accent": ["#00CED1", "#DC143C", "#CD853F", "#FF8C00", "#708090"]
    },
    "Soft Autumn": {
        "primary": ["#FFDAB9", "#D2B48C", "#BC8F8F", "#DEB887", "#F4A460"],
        "secondary": ["#FFE4B5", "#CD853F", "#CD5C5C", "#D2B48C", "#DAA520"],
        "accent": ["#FFC0CB", "#A0522D", "#A0522D", "#BC8F8F", "#CD853F"]
    },
    # Winter palettes
    "Cool Winter": {
        "primary": ["#0000FF", "#008000", "#FF00FF", "#00FFFF", "#F0F8FF"],
        "secondary": ["#0000CD", "#228B22", "#BA55D3", "#00CED1", "#E6E6FA"],
        "accent": ["#000080", "#32CD32", "#8A2BE2", "#48D1CC", "#B0C4DE"]
    },
    "Bright Winter": {
        "primary": ["#FF0000", "#0000FF", "#00FF00", "#FF00FF", "#FFFF00"],
        "secondary": ["#DC143C", "#0000CD", "#32CD32", "#BA55D3", "#FFD700"],
        "accent": ["#8B0000", "#000080", "#228B22", "#8A2BE2", "#FFA500"]
    },
    "Deep Winter": {
        "primary": ["#000080", "#800080", "#008000", "#000000", "#FFFFFF"],
        "secondary": ["#191970", "#4B0082", "#006400", "#2F2F2F", "#F5F5F5"],
        "accent": ["#0000CD", "#8A2BE2", "#32CD32", "#696969", "#D3D3D3"]
    }
}


@router.get("/color/palette/{season}")
def get_color_palette(season: str):
    """
    Get color palette (HEX colors) for a specific personal color season.
    
    Args:
        season: Personal color type (e.g., "Deep Autumn", "Light Spring", "Cool Winter")
    
    Returns:
        Dictionary containing primary, secondary, and accent color arrays in HEX format
    """
    logger.info(f"Get color palette request: season={season}")
    
    # Normalize season name (handle variations)
    season_normalized = season.strip()
    
    # Try exact match first
    if season_normalized in COLOR_PALETTES:
        palette = COLOR_PALETTES[season_normalized]
        logger.info(f"Found palette for season={season}")
        return {
            "season": season_normalized,
            "palette": palette
        }
    
    # Try case-insensitive match
    season_lower = season_normalized.lower()
    for key, value in COLOR_PALETTES.items():
        if key.lower() == season_lower:
            logger.info(f"Found palette for season={season} (case-insensitive match: {key})")
            return {
                "season": key,
                "palette": value
            }
    
    # Try partial match (e.g., "Autumn" matches "Deep Autumn", "Warm Autumn", etc.)
    matching_seasons = [k for k in COLOR_PALETTES.keys() if season_lower in k.lower() or k.lower() in season_lower]
    if matching_seasons:
        # Return the first match, or prefer exact subtype match
        best_match = matching_seasons[0]
        logger.info(f"Found palette for season={season} (partial match: {best_match})")
        return {
            "season": best_match,
            "palette": COLOR_PALETTES[best_match],
            "note": f"Matched '{season}' to '{best_match}'. Available seasons: {list(COLOR_PALETTES.keys())}"
        }
    
    # No match found
    logger.warning(f"Color palette not found for season={season}")
    raise HTTPException(
        status_code=404,
        detail=f"Color palette not found for season '{season}'. Available seasons: {list(COLOR_PALETTES.keys())}"
    )