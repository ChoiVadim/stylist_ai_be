"""
Color analysis API endpoints.
"""
from fastapi import APIRouter, UploadFile, File, Query
from PIL import Image
from io import BytesIO
from typing import Literal
from src.services import (
    get_your_color_season,
    get_your_color_season_ensemble_parallel,
    get_your_color_season_ensemble_hybrid,
)
from src.models import AnalyzeColorSeasonRequest

router = APIRouter(prefix="/api", tags=["color-analysis"])


@router.post("/test/analyze/color")
async def test_upload_image(file: UploadFile = File(...)):
    """
    Test endpoint: Analyze color season from uploaded image file.
    
    Use this for testing directly in FastAPI docs with file upload.
    """
    contents = await file.read()
    image = Image.open(BytesIO(contents))
    return get_your_color_season(image).model_dump()


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
    try:
        result = get_your_color_season(request.image)
        return result.model_dump()
    except Exception as e:
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
    try:
        result = await get_your_color_season_ensemble_parallel(
            request.image,
            aggregation_method=aggregation_method
        )
        return result.model_dump()
    except Exception as e:
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
    try:
        result = await get_your_color_season_ensemble_hybrid(
            request.image,
            judge_model=judge_model
        )
        return result.model_dump()
    except Exception as e:
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
    try:
        contents = await file.read()
        image = Image.open(BytesIO(contents))
        result = await get_your_color_season_ensemble_parallel(
            image,
            aggregation_method=aggregation_method
        )
        return result.model_dump()
    except Exception as e:
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
    try:
        contents = await file.read()
        image = Image.open(BytesIO(contents))
        result = await get_your_color_season_ensemble_hybrid(
            image,
            judge_model=judge_model
        )
        return result.model_dump()
    except Exception as e:
        return {"error": str(e)}