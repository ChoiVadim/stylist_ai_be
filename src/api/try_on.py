"""
Try-on image generation API endpoints.
"""
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import StreamingResponse
from PIL import Image
from io import BytesIO
import base64
from src.services import get_outfit_on as service_get_outfit_on, get_outfit_on_full_outfit as service_get_outfit_on_full_outfit
from src.services import get_outfit_on_full_outfit_on_sequential as service_get_outfit_on_sequential
from src.models import GenerateOutfitOnRequest, GenerateOutfitOnFullOutfitRequest
from src.utils.logger import get_logger
from src.utils.image_validator import (
    validate_image_from_bytes,
    validate_image_from_base64,
    ImageValidationError
)
import time

logger = get_logger("api.try_on")
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
    start_time = time.time()
    logger.info("Test try-on generation request received (file upload)")
    
    try:
        user_contents = await user_image.read()
        # Validate user image (requires face for try-on)
        try:
            user_image_pil, user_validation = validate_image_from_bytes(
                user_contents,
                require_face=True,
                max_dimension=4096,
                min_dimension=100
            )
            logger.debug(f"User image validated: {user_validation}")
        except ImageValidationError as e:
            logger.warning(f"User image validation failed: {str(e)}")
            raise HTTPException(status_code=400, detail=f"User image validation failed: {str(e)}")
        
        product_contents = await product_image.read()
        # Validate product image (no face required)
        try:
            product_image_pil, product_validation = validate_image_from_bytes(
                product_contents,
                require_face=False,
                max_dimension=4096,
                min_dimension=100
            )
            logger.debug(f"Product image validated: {product_validation}")
        except ImageValidationError as e:
            logger.warning(f"Product image validation failed: {str(e)}")
            raise HTTPException(status_code=400, detail=f"Product image validation failed: {str(e)}")
        
        result = service_get_outfit_on(user_image_pil, product_image_pil)
        process_time = time.time() - start_time
        logger.info(f"Try-on image generated successfully, time={process_time:.2f}s")

        buffer = BytesIO()
        result.save(buffer, format="PNG")
        buffer.seek(0)
        headers = {"Content-Disposition": 'attachment; filename="try_on.png"'}
        return StreamingResponse(buffer, media_type="image/png", headers=headers)
    except Exception as e:
        process_time = time.time() - start_time
        logger.error(f"Error generating try-on image: {str(e)}, time={process_time:.2f}s", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error generating try-on image: {str(e)}")

@router.post("/test/try-on/full_outfit")
async def download_try_on_full_outfit(
    user_image: UploadFile = File(...), 
    upper_image: UploadFile = File(...),
    lower_image: UploadFile = File(...),
    shoes_image: UploadFile = File(...),
):
    start_time = time.time()
    logger.info("Test full outfit try-on generation request received (file upload)")
    
    try:
        # Validate all images
        user_contents = await user_image.read()
        try:
            user_image_pil, _ = validate_image_from_bytes(
                user_contents,
                require_face=True,
                max_dimension=4096,
                min_dimension=100
            )
        except ImageValidationError as e:
            raise HTTPException(status_code=400, detail=f"User image validation failed: {str(e)}")
        
        upper_contents = await upper_image.read()
        try:
            upper_image_pil, _ = validate_image_from_bytes(
                upper_contents,
                require_face=False,
                max_dimension=4096,
                min_dimension=100
            )
        except ImageValidationError as e:
            raise HTTPException(status_code=400, detail=f"Upper image validation failed: {str(e)}")
        
        lower_contents = await lower_image.read()
        try:
            lower_image_pil, _ = validate_image_from_bytes(
                lower_contents,
                require_face=False,
                max_dimension=4096,
                min_dimension=100
            )
        except ImageValidationError as e:
            raise HTTPException(status_code=400, detail=f"Lower image validation failed: {str(e)}")
        
        shoes_contents = await shoes_image.read()
        try:
            shoes_image_pil, _ = validate_image_from_bytes(
                shoes_contents,
                require_face=False,
                max_dimension=4096,
                min_dimension=100
            )
        except ImageValidationError as e:
            raise HTTPException(status_code=400, detail=f"Shoes image validation failed: {str(e)}")
        
        logger.debug("All outfit images validated successfully")

        result = service_get_outfit_on_full_outfit(user_image_pil, upper_image_pil, lower_image_pil, shoes_image_pil)
        process_time = time.time() - start_time
        logger.info(f"Full outfit try-on image generated successfully, time={process_time:.2f}s")

        buffer = BytesIO()
        result.save(buffer, format="PNG")   
        buffer.seek(0)
        headers = {"Content-Disposition": 'attachment; filename="full_outfit_try_on.png"'}
        return StreamingResponse(buffer, media_type="image/png", headers=headers)
    except Exception as e:
        process_time = time.time() - start_time
        logger.error(f"Error generating full outfit try-on image: {str(e)}, time={process_time:.2f}s", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error generating full outfit try-on image: {str(e)}")

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
    start_time = time.time()
    logger.info("Full outfit try-on generation request received (base64)")
    
    try:
        # Validate all images
        try:
            user_img, _ = validate_image_from_base64(
                request.user_image,
                require_face=True,
                max_dimension=4096,
                min_dimension=100
            )
            upper_img, _ = validate_image_from_base64(
                request.upper_image,
                require_face=False,
                max_dimension=4096,
                min_dimension=100
            )
            lower_img, _ = validate_image_from_base64(
                request.lower_image,
                require_face=False,
                max_dimension=4096,
                min_dimension=100
            )
            shoes_img, _ = validate_image_from_base64(
                request.shoes_image,
                require_face=False,
                max_dimension=4096,
                min_dimension=100
            )
        except ImageValidationError as e:
            logger.warning(f"Image validation failed: {str(e)}")
            raise HTTPException(status_code=400, detail=str(e))
        
        result = service_get_outfit_on_full_outfit(user_img, upper_img, lower_img, shoes_img)
        process_time = time.time() - start_time
        logger.info(f"Full outfit try-on image generated successfully, time={process_time:.2f}s")
        
        buffer = BytesIO()
        result.save(buffer, format="PNG")
        image_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")
        return {
            "try_on_full_outfit_image": f"data:image/png;base64,{image_base64}",
            "status": "success",
            "message": "Outfit try-on image generated successfully",
        }
    except Exception as e:
        process_time = time.time() - start_time
        logger.error(f"Error generating full outfit try-on image: {str(e)}, time={process_time:.2f}s", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error generating full outfit try-on image: {str(e)}")

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
    start_time = time.time()
    logger.info("Try-on generation request received (base64)")
    
    try:
        # Validate images
        try:
            user_img, _ = validate_image_from_base64(
                request.user_image,
                require_face=True,
                max_dimension=4096,
                min_dimension=100
            )
            product_img, _ = validate_image_from_base64(
                request.product_image,
                require_face=False,
                max_dimension=4096,
                min_dimension=100
            )
        except ImageValidationError as e:
            logger.warning(f"Image validation failed: {str(e)}")
            raise HTTPException(status_code=400, detail=str(e))
        
        result_image = service_get_outfit_on(user_img, product_img)
        process_time = time.time() - start_time
        logger.info(f"Try-on image generated successfully, time={process_time:.2f}s")

        buffer = BytesIO()
        result_image.save(buffer, format="PNG")
        image_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")

        return {
            "try_on_image": f"data:image/png;base64,{image_base64}",
            "status": "success",
            "message": "Outfit try-on image generated successfully",
        }
    except Exception as e:
        process_time = time.time() - start_time
        logger.error(f"Error generating try-on image: {str(e)}, time={process_time:.2f}s", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error generating try-on image: {str(e)}")

@router.post("/try-on/generate-full-outfit/on-sequential")
async def get_outfit_on_full_outfit_on_sequential(
    request: GenerateOutfitOnFullOutfitRequest,
):
    """
    Generate full outfit try-on image from base64-encoded images.
    """
    start_time = time.time()
    logger.info("Sequential full outfit try-on generation request received (base64)")
    
    try:
        result = service_get_outfit_on_sequential(request.user_image, request.upper_image, request.lower_image, request.shoes_image)
        process_time = time.time() - start_time
        logger.info(f"Sequential full outfit try-on image generated successfully, time={process_time:.2f}s")
        
        buffer = BytesIO()
        result.save(buffer, format="PNG")
        image_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")
        return {
            "try_on_full_outfit_on_sequential_image": f"data:image/png;base64,{image_base64}",
            "status": "success",
            "message": "Outfit try-on on sequential image generated successfully",
        }
    except Exception as e:
        process_time = time.time() - start_time
        logger.error(f"Error generating sequential full outfit try-on image: {str(e)}, time={process_time:.2f}s", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error generating sequential full outfit try-on image: {str(e)}")

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
    start_time = time.time()
    logger.info("Test sequential full outfit try-on generation request received (file upload)")
    
    try:
        # Convert UploadFile objects to PIL Images
        contents = await user_image.read()
        user_image_pil = Image.open(BytesIO(contents))
        contents = await upper_image.read()
        upper_image_pil = Image.open(BytesIO(contents))
        contents = await lower_image.read()
        lower_image_pil = Image.open(BytesIO(contents))
        contents = await shoes_image.read()
        shoes_image_pil = Image.open(BytesIO(contents))
        logger.debug("All outfit images loaded successfully for sequential processing")
        
        result = service_get_outfit_on_sequential(user_image_pil, upper_image_pil, lower_image_pil, shoes_image_pil)
        process_time = time.time() - start_time
        logger.info(f"Sequential full outfit try-on image generated successfully, time={process_time:.2f}s")
        
        buffer = BytesIO()
        result.save(buffer, format="PNG")   
        buffer.seek(0)
        headers = {"Content-Disposition": 'attachment; filename="full_outfit_try_on_sequential.png"'}
        return StreamingResponse(buffer, media_type="image/png", headers=headers)
    except Exception as e:
        process_time = time.time() - start_time
        logger.error(f"Error generating sequential full outfit try-on image: {str(e)}, time={process_time:.2f}s", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error generating sequential full outfit try-on image: {str(e)}")