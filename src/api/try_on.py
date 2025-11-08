"""
Try-on image generation API endpoints.
"""
from fastapi import APIRouter, UploadFile, File
from fastapi.responses import StreamingResponse
from PIL import Image
from io import BytesIO
import base64
from src.services import get_outfit_on as service_get_outfit_on, get_outfit_on_full_outfit as service_get_outfit_on_full_outfit
from src.services import get_outfit_on_full_outfit_on_sequential as service_get_outfit_on_sequential
from src.models import GenerateOutfitOnRequest, GenerateOutfitOnFullOutfitRequest

router = APIRouter(prefix="/api", tags=["try-on"])


@router.post(
    "/test/try-on/generate",
    responses={
        200: {
            "content": {
                "image/png": {
                    "schema": {"type": "string", "format": "binary"}
                }
            },
            "description": "Returns the generated try-on PNG image as downloadable file",
        }
    },
)
async def download_try_on_image(
    user_image: UploadFile = File(...), 
    product_image: UploadFile = File(...)
):
    """
    Test endpoint: Generate try-on image from uploaded files.
    
    Returns a downloadable PNG file. Use this in FastAPI docs to test with file uploads.
    """
    contents = await user_image.read()
    user_image_pil = Image.open(BytesIO(contents))
    contents = await product_image.read()
    product_image_pil = Image.open(BytesIO(contents))
    
    result = service_get_outfit_on(user_image_pil, product_image_pil)

    buffer = BytesIO()
    result.save(buffer, format="PNG")
    buffer.seek(0)
    headers = {"Content-Disposition": 'attachment; filename="try_on.png"'}
    return StreamingResponse(buffer, media_type="image/png", headers=headers)

@router.post("/test/try-on/full_outfit")
async def download_try_on_full_outfit(
    user_image: UploadFile = File(...), 
    upper_image: UploadFile = File(...),
    lower_image: UploadFile = File(...),
    shoes_image: UploadFile = File(...),
):

    contents = await user_image.read()
    user_image_pil = Image.open(BytesIO(contents))
    contents = await upper_image.read()
    upper_image_pil = Image.open(BytesIO(contents))
    contents = await lower_image.read()
    lower_image_pil = Image.open(BytesIO(contents))
    contents = await shoes_image.read()
    shoes_image_pil = Image.open(BytesIO(contents))

    result = service_get_outfit_on_full_outfit(user_image_pil, upper_image_pil, lower_image_pil, shoes_image_pil)

    buffer = BytesIO()
    result.save(buffer, format="PNG")   
    buffer.seek(0)
    headers = {"Content-Disposition": 'attachment; filename="full_outfit_try_on.png"'}
    return StreamingResponse(buffer, media_type="image/png", headers=headers)

@router.post("/try-on/generate-full-outfit")
async def get_outfit_on_full_outfit(
    request: GenerateOutfitOnFullOutfitRequest,
):
    """
    Generate full outfit try-on image from base64-encoded images.
    
    Request body should contain:
    {
        "user_image": "data:image/png;base64,iVBORw0KGgo...",
        "upper_image": "data:image/png;base64,iVBORw0KGgo...",
        "lower_image": "data:image/png;base64,iVBORw0KGgo...",
        "shoes_image": "data:image/png;base64,iVBORw0KGgo..."
    }
    """
    result = service_get_outfit_on_full_outfit(request.user_image, request.upper_image, request.lower_image, request.shoes_image)
    buffer = BytesIO()
    result.save(buffer, format="PNG")
    image_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")
    return {
        "try_on_full_outfit_image": f"data:image/png;base64,{image_base64}",
        "status": "success",
        "message": "Outfit try-on image generated successfully",
    }

@router.post("/try-on/generate")
def get_outfit_on(request: GenerateOutfitOnRequest):
    """
    Generate outfit try-on image from base64-encoded images.
    
    Request body should contain:
    {
        "user_image": "data:image/png;base64,iVBORw0KGgo...",
        "product_image": "data:image/png;base64,iVBORw0KGgo..."
    }
    
    Returns:
        JSON response with base64-encoded try-on image
    """
    result_image = service_get_outfit_on(request.user_image, request.product_image)

    buffer = BytesIO()
    result_image.save(buffer, format="PNG")
    image_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")

    return {
        "try_on_image": f"data:image/png;base64,{image_base64}",
        "status": "success",
        "message": "Outfit try-on image generated successfully",
    }

@router.post("/try-on/generate-full-outfit/on-sequential")
async def get_outfit_on_full_outfit_on_sequential(
    request: GenerateOutfitOnFullOutfitRequest,
):
    """
    Generate full outfit try-on image from base64-encoded images.
    """
    result = service_get_outfit_on_sequential(request.user_image, request.upper_image, request.lower_image, request.shoes_image)
    buffer = BytesIO()
    result.save(buffer, format="PNG")
    image_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")
    return {
        "try_on_full_outfit_on_sequential_image": f"data:image/png;base64,{image_base64}",
        "status": "success",
        "message": "Outfit try-on on sequential image generated successfully",
    }

@router.post("/test/try-on/generate-full-outfit/on-sequential")
async def get_outfit_on_full_outfit_on_sequential_test(
    user_image: UploadFile = File(...),
    upper_image: UploadFile = File(...),
    lower_image: UploadFile = File(...),
    shoes_image: UploadFile = File(...),
):
    """
    Test endpoint: Generate full outfit try-on image from uploaded files sequentially.
    """
    # Convert UploadFile objects to PIL Images
    contents = await user_image.read()
    user_image_pil = Image.open(BytesIO(contents))
    contents = await upper_image.read()
    upper_image_pil = Image.open(BytesIO(contents))
    contents = await lower_image.read()
    lower_image_pil = Image.open(BytesIO(contents))
    contents = await shoes_image.read()
    shoes_image_pil = Image.open(BytesIO(contents))
    
    result = service_get_outfit_on_sequential(user_image_pil, upper_image_pil, lower_image_pil, shoes_image_pil)
    buffer = BytesIO()
    result.save(buffer, format="PNG")   
    buffer.seek(0)
    headers = {"Content-Disposition": 'attachment; filename="full_outfit_try_on_sequential.png"'}
    return StreamingResponse(buffer, media_type="image/png", headers=headers)