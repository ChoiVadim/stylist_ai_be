"""
Unit tests for image validation utilities.
"""
import pytest
from PIL import Image
from io import BytesIO
import base64

from src.utils.image_validator import (
    validate_image_size,
    validate_image_format,
    validate_file_size,
    validate_image,
    validate_image_from_bytes,
    validate_image_from_base64,
    ImageValidationError,
    DEFAULT_MAX_DIMENSION,
    DEFAULT_MIN_DIMENSION,
    ALLOWED_FORMATS
)


class TestImageSizeValidation:
    """Tests for image size validation."""
    
    def test_valid_size(self):
        """Test validation of valid image size."""
        image = Image.new('RGB', (800, 600))
        width, height = validate_image_size(image)
        assert width == 800
        assert height == 600
    
    def test_too_small_image(self):
        """Test validation fails for too small image."""
        image = Image.new('RGB', (50, 50))
        with pytest.raises(ImageValidationError) as exc_info:
            validate_image_size(image, min_dimension=100)
        assert "too small" in str(exc_info.value).lower()
    
    def test_too_large_image(self):
        """Test validation fails for too large image."""
        image = Image.new('RGB', (5000, 5000))
        with pytest.raises(ImageValidationError) as exc_info:
            validate_image_size(image, max_dimension=4096)
        assert "too large" in str(exc_info.value).lower()
    
    def test_custom_dimensions(self):
        """Test validation with custom dimension limits."""
        image = Image.new('RGB', (200, 200))
        # Should pass with custom limits
        validate_image_size(image, max_dimension=500, min_dimension=100)
        
        # Should fail with stricter limits
        with pytest.raises(ImageValidationError):
            validate_image_size(image, max_dimension=150, min_dimension=100)


class TestImageFormatValidation:
    """Tests for image format validation."""
    
    def test_valid_jpeg(self):
        """Test validation of JPEG format."""
        image = Image.new('RGB', (100, 100))
        # Save as JPEG to set format
        buffer = BytesIO()
        image.save(buffer, format='JPEG')
        buffer.seek(0)
        image_with_format = Image.open(buffer)
        
        format_name = validate_image_format(image_with_format)
        assert format_name == "JPEG"
    
    def test_valid_png(self):
        """Test validation of PNG format."""
        image = Image.new('RGB', (100, 100))
        buffer = BytesIO()
        image.save(buffer, format='PNG')
        buffer.seek(0)
        image_with_format = Image.open(buffer)
        
        format_name = validate_image_format(image_with_format)
        assert format_name == "PNG"
    
    def test_invalid_format(self):
        """Test validation fails for unsupported format."""
        image = Image.new('RGB', (100, 100))
        # Try to set an invalid format (this is tricky, so we'll test with custom allowed formats)
        with pytest.raises(ImageValidationError):
            validate_image_format(image, allowed_formats={"PNG"})


class TestFileSizeValidation:
    """Tests for file size validation."""
    
    def test_valid_file_size(self):
        """Test validation of valid file size."""
        size_bytes = 5 * 1024 * 1024  # 5 MB
        validate_file_size(size_bytes, max_size_mb=10)
    
    def test_too_large_file(self):
        """Test validation fails for too large file."""
        size_bytes = 15 * 1024 * 1024  # 15 MB
        with pytest.raises(ImageValidationError) as exc_info:
            validate_file_size(size_bytes, max_size_mb=10)
        assert "too large" in str(exc_info.value).lower()


class TestComprehensiveValidation:
    """Tests for comprehensive image validation."""
    
    def test_validate_valid_image(self):
        """Test comprehensive validation of valid image."""
        image = Image.new('RGB', (800, 600))
        buffer = BytesIO()
        image.save(buffer, format='PNG')
        buffer.seek(0)
        image_with_format = Image.open(buffer)
        
        result = validate_image(
            image_with_format,
            require_face=False,
            max_dimension=4096,
            min_dimension=100
        )
        
        assert result["valid"] is True
        assert result["width"] == 800
        assert result["height"] == 600
        assert result["format"] == "PNG"
    
    def test_validate_image_from_bytes(self):
        """Test validation from bytes."""
        image = Image.new('RGB', (800, 600))
        buffer = BytesIO()
        image.save(buffer, format='PNG')
        image_bytes = buffer.getvalue()
        
        pil_image, result = validate_image_from_bytes(
            image_bytes,
            require_face=False,
            max_dimension=4096,
            min_dimension=100
        )
        
        assert isinstance(pil_image, Image.Image)
        assert result["valid"] is True
        assert result["width"] == 800
        assert result["height"] == 600
    
    def test_validate_image_from_base64(self):
        """Test validation from base64 string."""
        image = Image.new('RGB', (800, 600))
        buffer = BytesIO()
        image.save(buffer, format='PNG')
        image_bytes = buffer.getvalue()
        base64_string = base64.b64encode(image_bytes).decode('utf-8')
        
        pil_image, result = validate_image_from_base64(
            base64_string,
            require_face=False,
            max_dimension=4096,
            min_dimension=100
        )
        
        assert isinstance(pil_image, Image.Image)
        assert result["valid"] is True
    
    def test_validate_image_from_base64_with_data_url(self):
        """Test validation from base64 data URL."""
        image = Image.new('RGB', (800, 600))
        buffer = BytesIO()
        image.save(buffer, format='PNG')
        image_bytes = buffer.getvalue()
        base64_string = base64.b64encode(image_bytes).decode('utf-8')
        data_url = f"data:image/png;base64,{base64_string}"
        
        pil_image, result = validate_image_from_base64(
            data_url,
            require_face=False,
            max_dimension=4096,
            min_dimension=100
        )
        
        assert isinstance(pil_image, Image.Image)
        assert result["valid"] is True
    
    def test_invalid_base64(self):
        """Test validation fails for invalid base64."""
        with pytest.raises(ImageValidationError):
            validate_image_from_base64("invalid_base64_string")
    
    def test_file_size_validation_in_bytes(self):
        """Test file size validation when validating from bytes."""
        # Create a large image
        image = Image.new('RGB', (800, 600))
        buffer = BytesIO()
        image.save(buffer, format='PNG')
        image_bytes = buffer.getvalue()
        
        # Should pass with default limits
        validate_image_from_bytes(image_bytes, max_size_mb=10)
        
        # Should fail with strict limit
        with pytest.raises(ImageValidationError):
            # Create artificially large data
            large_bytes = image_bytes * 1000  # Make it large
            validate_image_from_bytes(large_bytes, max_size_mb=1)

