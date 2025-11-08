import base64
from src.services import get_your_color_season, get_outfit_on

if __name__ == "__main__":
    # CORRECT: Read file as bytes, then encode to base64
    with open("images/image_test.JPG", "rb") as f:
        image_bytes = f.read()
        base64_image = base64.b64encode(image_bytes).decode("utf-8")
    
    # Or create a data URL format
    base64_image = f"data:image/jpeg;base64,{base64_image}"
    
    result = get_your_color_season(base64_image)
    print(result.model_dump())

    # Same for product image
    with open("images/product_test.png", "rb") as f:
        product_bytes = f.read()
        base64_product_image = base64.b64encode(product_bytes).decode("utf-8")
    
    base64_product_image = f"data:image/png;base64,{base64_product_image}"
    
    result = get_outfit_on(base64_image, base64_product_image)
    result.save("images/generated_image.png")