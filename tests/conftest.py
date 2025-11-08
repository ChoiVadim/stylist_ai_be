"""
Pytest configuration and fixtures.
"""
import pytest
from PIL import Image
from io import BytesIO


@pytest.fixture
def sample_image():
    """Create a sample PIL Image for testing."""
    return Image.new('RGB', (800, 600), color='red')


@pytest.fixture
def sample_image_bytes(sample_image):
    """Create sample image as bytes."""
    buffer = BytesIO()
    sample_image.save(buffer, format='PNG')
    return buffer.getvalue()


@pytest.fixture
def sample_image_base64(sample_image_bytes):
    """Create sample image as base64 string."""
    import base64
    return base64.b64encode(sample_image_bytes).decode('utf-8')


@pytest.fixture
def small_image():
    """Create a small image for testing size validation."""
    return Image.new('RGB', (50, 50), color='blue')


@pytest.fixture
def large_image():
    """Create a large image for testing size validation."""
    return Image.new('RGB', (5000, 5000), color='green')

