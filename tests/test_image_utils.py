"""
Unit tests for image utility functions.
"""
import pytest
import base64
from PIL import Image
from io import BytesIO

from src.utils.image_utils import base64_to_image


class TestBase64ToImage:
    """Tests for base64_to_image function."""
    
    def test_base64_to_image_simple(self):
        """Test converting simple base64 string to image."""
        # Create a test image
        image = Image.new('RGB', (100, 100), color='red')
        buffer = BytesIO()
        image.save(buffer, format='PNG')
        image_bytes = buffer.getvalue()
        base64_string = base64.b64encode(image_bytes).decode('utf-8')
        
        # Convert back to image
        result_image = base64_to_image(base64_string)
        
        assert isinstance(result_image, Image.Image)
        assert result_image.size == (100, 100)
    
    def test_base64_to_image_with_data_url(self):
        """Test converting base64 data URL to image."""
        # Create a test image
        image = Image.new('RGB', (100, 100), color='blue')
        buffer = BytesIO()
        image.save(buffer, format='PNG')
        image_bytes = buffer.getvalue()
        base64_string = base64.b64encode(image_bytes).decode('utf-8')
        data_url = f"data:image/png;base64,{base64_string}"
        
        # Convert back to image
        result_image = base64_to_image(data_url)
        
        assert isinstance(result_image, Image.Image)
        assert result_image.size == (100, 100)
    
    def test_base64_to_image_invalid(self):
        """Test that invalid base64 raises error."""
        with pytest.raises(Exception):  # Should raise some error
            base64_to_image("invalid_base64_string!!!")

