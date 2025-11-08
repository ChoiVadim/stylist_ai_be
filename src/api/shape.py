from fastapi import APIRouter
from src.services.stylist import get_your_face_shape, get_your_body_shape
from fastapi import UploadFile, File
from PIL import Image
from io import BytesIO

router = APIRouter(prefix="/api/shape", tags=["shape"])

@router.post("/face")
def get_face_shape(image: str):
    try:
        result = get_your_face_shape(image)
        return result.model_dump()
    except Exception as e:
        return {"error": str(e)}

@router.post("/test/analyze/face")
async def test_upload_face_image(file: UploadFile = File(...)):
    """
    Test endpoint: Analyze face shape from uploaded image file.
    
    Use this for testing directly in FastAPI docs with file upload.
    """
    contents = await file.read()
    image = Image.open(BytesIO(contents))
    return {"face_shape": get_your_face_shape(image)}

@router.post("/body")
def get_body_shape(image: str):
    try:
        result = get_your_body_shape(image)
        return result.model_dump()
    except Exception as e:
        return {"error": str(e)}

@router.post("/test/analyze/body")
async def test_upload_body_image(file: UploadFile = File(...)):
    """
    Test endpoint: Analyze body shape from uploaded image file.
    
    Use this for testing directly in FastAPI docs with file upload.
    """
    contents = await file.read()
    image = Image.open(BytesIO(contents))
    return {"body_shape": get_your_body_shape(image)}