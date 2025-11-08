"""
Color analysis API endpoints.
"""
from fastapi import APIRouter, UploadFile, File, Query
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
        image = Image.open(BytesIO(contents))
        logger.debug(f"Image loaded: size={image.size}, format={image.format}")
        
        result = get_your_color_season(image)
        process_time = time.time() - start_time
        logger.info(
            f"Test color analysis completed: season={result.personal_color_type}, "
            f"confidence={result.confidence:.2f}, time={process_time:.2f}s"
        )
        return result.model_dump()
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
        result = get_your_color_season(request.image)
        process_time = time.time() - start_time
        logger.info(
            f"Color analysis completed: season={result.personal_color_type}, "
            f"confidence={result.confidence:.2f}, time={process_time:.2f}s"
        )
        return result.model_dump()
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
        result = await get_your_color_season_ensemble_parallel(
            request.image,
            aggregation_method=aggregation_method
        )
        process_time = time.time() - start_time
        logger.info(
            f"Ensemble parallel analysis completed: season={result.personal_color_type}, "
            f"confidence={result.confidence:.2f}, method={aggregation_method}, time={process_time:.2f}s"
        )
        return result.model_dump()
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
        result = await get_your_color_season_ensemble_hybrid(
            request.image,
            judge_model=judge_model
        )
        process_time = time.time() - start_time
        logger.info(
            f"Ensemble hybrid analysis completed: season={result.personal_color_type}, "
            f"confidence={result.confidence:.2f}, judge_model={judge_model}, time={process_time:.2f}s"
        )
        return result.model_dump()
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
        image = Image.open(BytesIO(contents))
        logger.debug(f"Image loaded: size={image.size}, format={image.format}")
        
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
        image = Image.open(BytesIO(contents))
        logger.debug(f"Image loaded: size={image.size}, format={image.format}")
        
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
    except Exception as e:
        process_time = time.time() - start_time
        logger.error(
            f"Test ensemble hybrid analysis failed: {str(e)}, judge_model={judge_model}, time={process_time:.2f}s",
            exc_info=True
        )
        return {"error": str(e)}