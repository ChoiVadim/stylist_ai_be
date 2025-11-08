"""
Color analysis API endpoints.
"""
from fastapi import APIRouter, UploadFile, File
from PIL import Image
from io import BytesIO
from src.services import get_your_color_season
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
    Analyze color season from a base64-encoded image.
    
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

