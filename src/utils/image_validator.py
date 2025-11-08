"""
Image validation utilities.
Validates image size, format, and face detection.
"""
from PIL import Image
from io import BytesIO
from typing import Tuple, Optional
from fastapi import HTTPException
import numpy as np

try:
    import cv2
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False

from src.utils.logger import get_logger

logger = get_logger("utils.image_validator")


class ImageValidationError(Exception):
    """Custom exception for image validation errors."""
    pass


# Default validation constraints
DEFAULT_MAX_SIZE_MB = 10  # Maximum file size in MB
DEFAULT_MAX_DIMENSION = 4096  # Maximum width or height in pixels
DEFAULT_MIN_DIMENSION = 100  # Minimum width or height in pixels
ALLOWED_FORMATS = {"JPEG", "PNG", "JPG", "WEBP"}


def validate_image_size(image: Image.Image, max_dimension: int = DEFAULT_MAX_DIMENSION, 
                        min_dimension: int = DEFAULT_MIN_DIMENSION) -> Tuple[int, int]:
    """
    Validate image dimensions.
    
    Args:
        image: PIL Image object
        max_dimension: Maximum allowed width or height
        min_dimension: Minimum allowed width or height
    
    Returns:
        Tuple of (width, height)
    
    Raises:
        ImageValidationError: If dimensions are invalid
    """
    width, height = image.size
    
    if width < min_dimension or height < min_dimension:
        raise ImageValidationError(
            f"Image too small: {width}x{height}. Minimum dimension: {min_dimension}px"
        )
    
    if width > max_dimension or height > max_dimension:
        raise ImageValidationError(
            f"Image too large: {width}x{height}. Maximum dimension: {max_dimension}px"
        )
    
    return width, height


def validate_image_format(image: Image.Image, allowed_formats: set = ALLOWED_FORMATS) -> str:
    """
    Validate image format.
    
    Args:
        image: PIL Image object
        allowed_formats: Set of allowed format names
    
    Returns:
        Format name
    
    Raises:
        ImageValidationError: If format is not allowed
    """
    format_name = image.format
    if format_name is None:
        raise ImageValidationError("Unable to determine image format")
    
    if format_name.upper() not in allowed_formats:
        raise ImageValidationError(
            f"Unsupported image format: {format_name}. Allowed formats: {', '.join(allowed_formats)}"
        )
    
    return format_name


def validate_file_size(file_size_bytes: int, max_size_mb: int = DEFAULT_MAX_SIZE_MB) -> None:
    """
    Validate file size.
    
    Args:
        file_size_bytes: File size in bytes
        max_size_mb: Maximum file size in MB
    
    Raises:
        ImageValidationError: If file is too large
    """
    max_size_bytes = max_size_mb * 1024 * 1024
    if file_size_bytes > max_size_bytes:
        raise ImageValidationError(
            f"File too large: {file_size_bytes / (1024 * 1024):.2f}MB. Maximum: {max_size_mb}MB"
        )


def detect_face_opencv(image: Image.Image) -> bool:
    """
    Detect if a face is present in the image using OpenCV.
    
    Args:
        image: PIL Image object
    
    Returns:
        True if face is detected, False otherwise
    """
    if not CV2_AVAILABLE:
        logger.warning("OpenCV not available, skipping face detection")
        return True  # Skip validation if OpenCV is not available
    
    try:
        # Convert PIL Image to OpenCV format
        img_array = np.array(image)
        
        # Convert RGB to BGR if needed
        if image.mode == 'RGB':
            img_array = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
        elif image.mode == 'RGBA':
            img_array = cv2.cvtColor(img_array, cv2.COLOR_RGBA2BGR)
        elif image.mode == 'L':
            # Grayscale image
            img_array = cv2.cvtColor(img_array, cv2.COLOR_GRAY2BGR)
        
        # Convert to grayscale for face detection
        gray = cv2.cvtColor(img_array, cv2.COLOR_BGR2GRAY)
        
        # Load the face cascade classifier
        # Try to use the built-in cascade file
        cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        face_cascade = cv2.CascadeClassifier(cascade_path)
        
        if face_cascade.empty():
            logger.warning("Could not load face cascade, skipping face detection")
            return True  # Skip validation if cascade cannot be loaded
        
        # Detect faces
        faces = face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(30, 30)
        )
        
        return len(faces) > 0
    
    except Exception as e:
        logger.warning(f"Error during face detection: {str(e)}, skipping face validation")
        return True  # Skip validation on error to avoid blocking valid requests


def validate_image(
    image: Image.Image,
    require_face: bool = False,
    max_dimension: int = DEFAULT_MAX_DIMENSION,
    min_dimension: int = DEFAULT_MIN_DIMENSION,
    allowed_formats: set = ALLOWED_FORMATS,
    file_size_bytes: Optional[int] = None,
    max_size_mb: int = DEFAULT_MAX_SIZE_MB
) -> dict:
    """
    Comprehensive image validation.
    
    Args:
        image: PIL Image object
        require_face: Whether to require face detection
        max_dimension: Maximum allowed width or height
        min_dimension: Minimum allowed width or height
        allowed_formats: Set of allowed format names
        file_size_bytes: Optional file size in bytes for validation
        max_size_mb: Maximum file size in MB
    
    Returns:
        Dictionary with validation results:
        {
            "valid": bool,
            "width": int,
            "height": int,
            "format": str,
            "face_detected": bool (if require_face=True)
        }
    
    Raises:
        ImageValidationError: If validation fails
    """
    # Validate format
    format_name = validate_image_format(image, allowed_formats)
    
    # Validate size
    width, height = validate_image_size(image, max_dimension, min_dimension)
    
    # Validate file size if provided
    if file_size_bytes is not None:
        validate_file_size(file_size_bytes, max_size_mb)
    
    # Face detection if required
    face_detected = None
    if require_face:
        face_detected = detect_face_opencv(image)
        if not face_detected:
            raise ImageValidationError(
                "No face detected in the image. Please upload an image with a visible face."
            )
    
    result = {
        "valid": True,
        "width": width,
        "height": height,
        "format": format_name,
    }
    
    if require_face:
        result["face_detected"] = face_detected
    
    return result


def validate_image_from_bytes(
    image_bytes: bytes,
    require_face: bool = False,
    max_dimension: int = DEFAULT_MAX_DIMENSION,
    min_dimension: int = DEFAULT_MIN_DIMENSION,
    allowed_formats: set = ALLOWED_FORMATS,
    max_size_mb: int = DEFAULT_MAX_SIZE_MB
) -> Tuple[Image.Image, dict]:
    """
    Validate image from bytes and return PIL Image and validation results.
    
    Args:
        image_bytes: Image data as bytes
        require_face: Whether to require face detection
        max_dimension: Maximum allowed width or height
        min_dimension: Minimum allowed width or height
        allowed_formats: Set of allowed format names
        max_size_mb: Maximum file size in MB
    
    Returns:
        Tuple of (PIL Image, validation results dict)
    
    Raises:
        ImageValidationError: If validation fails
    """
    # Validate file size
    validate_file_size(len(image_bytes), max_size_mb)
    
    # Load image
    try:
        image = Image.open(BytesIO(image_bytes))
        # Verify it's actually an image by loading it
        image.verify()
        # Reopen because verify() closes the image
        image = Image.open(BytesIO(image_bytes))
    except Exception as e:
        raise ImageValidationError(f"Invalid image file: {str(e)}")
    
    # Validate image
    validation_result = validate_image(
        image=image,
        require_face=require_face,
        max_dimension=max_dimension,
        min_dimension=min_dimension,
        allowed_formats=allowed_formats,
        file_size_bytes=len(image_bytes),
        max_size_mb=max_size_mb
    )
    
    return image, validation_result


def validate_image_from_base64(
    base64_string: str,
    require_face: bool = False,
    max_dimension: int = DEFAULT_MAX_DIMENSION,
    min_dimension: int = DEFAULT_MIN_DIMENSION,
    allowed_formats: set = ALLOWED_FORMATS,
    max_size_mb: int = DEFAULT_MAX_SIZE_MB
) -> Tuple[Image.Image, dict]:
    """
    Validate image from base64 string and return PIL Image and validation results.
    
    Args:
        base64_string: Base64 encoded image string (with or without data URL prefix)
        require_face: Whether to require face detection
        max_dimension: Maximum allowed width or height
        min_dimension: Minimum allowed width or height
        allowed_formats: Set of allowed format names
        max_size_mb: Maximum file size in MB
    
    Returns:
        Tuple of (PIL Image, validation results dict)
    
    Raises:
        ImageValidationError: If validation fails
    """
    import base64 as b64
    
    # Remove data URL prefix if present
    if base64_string.startswith("data:"):
        base64_string = base64_string.split(",", 1)[1]
    
    try:
        image_bytes = b64.b64decode(base64_string)
    except Exception as e:
        raise ImageValidationError(f"Invalid base64 encoding: {str(e)}")
    
    return validate_image_from_bytes(
        image_bytes=image_bytes,
        require_face=require_face,
        max_dimension=max_dimension,
        min_dimension=min_dimension,
        allowed_formats=allowed_formats,
        max_size_mb=max_size_mb
    )

