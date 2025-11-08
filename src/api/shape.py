from fastapi import APIRouter, HTTPException
from src.services.stylist import get_your_face_shape, get_your_body_shape
from fastapi import UploadFile, File
from PIL import Image
from io import BytesIO
from src.utils.logger import get_logger
from src.utils.image_validator import (
    validate_image_from_bytes,
    validate_image_from_base64,
    ImageValidationError
)
import time

logger = get_logger("api.shape")
router = APIRouter(prefix="/api/shape", tags=["shape"])

@router.post("/face")
def get_face_shape(image: str):
    start_time = time.time()
    logger.info("Face shape analysis request received (base64)")
    
    try:
        result = get_your_face_shape(image)
        process_time = time.time() - start_time
        logger.info(f"Face shape analysis completed: shape={result.face_shape}, confidence={result.confidence:.2f}, time={process_time:.2f}s")
        return result.model_dump()
    except Exception as e:
        process_time = time.time() - start_time
        logger.error(f"Face shape analysis failed: {str(e)}, time={process_time:.2f}s", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error analyzing face shape: {str(e)}")

@router.post("/test/analyze/face")
async def test_upload_face_image(file: UploadFile = File(...)):
    """
    Test endpoint: Analyze face shape from uploaded image file.
    
    Use this for testing directly in FastAPI docs with file upload.
    """
    start_time = time.time()
    logger.info("Test face shape analysis request received (file upload)")
    
    try:
        contents = await file.read()
        
        # Validate image (face shape analysis requires face)
        try:
            image, validation_result = validate_image_from_bytes(
                contents,
                require_face=True,
                max_dimension=4096,
                min_dimension=100
            )
            logger.debug(f"Face image validated: {validation_result}")
        except ImageValidationError as e:
            logger.warning(f"Image validation failed: {str(e)}")
            raise HTTPException(status_code=400, detail=str(e))
        
        result = get_your_face_shape(image)
        process_time = time.time() - start_time
        logger.info(f"Face shape analysis completed: shape={result.face_shape}, confidence={result.confidence:.2f}, time={process_time:.2f}s")
        
        return {"face_shape": result.face_shape, "confidence": result.confidence, "reasoning": result.reasoning}
    except Exception as e:
        process_time = time.time() - start_time
        logger.error(f"Face shape analysis failed: {str(e)}, time={process_time:.2f}s", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error analyzing face shape: {str(e)}")

@router.post("/body")
def get_body_shape(image: str):
    start_time = time.time()
    logger.info("Body shape analysis request received (base64)")
    
    try:
        result = get_your_body_shape(image)
        process_time = time.time() - start_time
        logger.info(f"Body shape analysis completed: shape={result.body_shape}, confidence={result.confidence:.2f}, time={process_time:.2f}s")
        return result.model_dump()
    except Exception as e:
        process_time = time.time() - start_time
        logger.error(f"Body shape analysis failed: {str(e)}, time={process_time:.2f}s", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error analyzing body shape: {str(e)}")

@router.post("/test/analyze/body")
async def test_upload_body_image(file: UploadFile = File(...)):
    """
    Test endpoint: Analyze body shape from uploaded image file.
    
    Use this for testing directly in FastAPI docs with file upload.
    """
    start_time = time.time()
    logger.info("Test body shape analysis request received (file upload)")
    
    try:
        contents = await file.read()
        
        # Validate image (body shape analysis doesn't require face, but validates size/format)
        try:
            image, validation_result = validate_image_from_bytes(
                contents,
                require_face=False,
                max_dimension=4096,
                min_dimension=100
            )
            logger.debug(f"Body image validated: {validation_result}")
        except ImageValidationError as e:
            logger.warning(f"Image validation failed: {str(e)}")
            raise HTTPException(status_code=400, detail=str(e))
        
        result = get_your_body_shape(image)
        process_time = time.time() - start_time
        logger.info(f"Body shape analysis completed: shape={result.body_shape}, confidence={result.confidence:.2f}, time={process_time:.2f}s")
        
        return {"body_shape": result.body_shape, "confidence": result.confidence, "reasoning": result.reasoning}
    except Exception as e:
        process_time = time.time() - start_time
        logger.error(f"Body shape analysis failed: {str(e)}, time={process_time:.2f}s", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error analyzing body shape: {str(e)}")