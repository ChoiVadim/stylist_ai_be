import fastapi
import uvicorn

import src.stylist as Stylist
from src.models import AnalyzeColorSeasonRequest, GenerateOutfitOnRequest
from fastapi import UploadFile, File

app = fastapi.FastAPI()


@app.get("/")
def read_root():
    return {"message": "Hello, World!"}

@app.post("/api/test/upload")
async def test_upload_image(file: UploadFile = File(...)):
    """
    Test endpoint to upload an image file.
    You can test this directly in FastAPI docs!
    """
    # Read the uploaded file
    contents = await file.read()
    
    # You can process it with PIL if needed
    from PIL import Image
    from io import BytesIO
    
    image = Image.open(BytesIO(contents))
    
    return Stylist.get_your_color_season(image).model_dump()

@app.post("/api/analyze/color")
def get_color_season(request: AnalyzeColorSeasonRequest):
    """
    Analyze color season from an image.

    Request body should contain:
    {
        "image": "data:image/png;base64,iVBORw0KGgo..." or just "iVBORw0KGgo..."
    }
    """
    try:
        result = Stylist.get_your_color_season(request.image)
        return result.model_dump()
    except Exception as e:
        return {"error": str(e)}


@app.post("/api/try-on/generate")
def get_outfit_on(request: GenerateOutfitOnRequest):
    """
    Generate outfit try-on image.

    Request body should contain:
    {
        "user_image": "data:image/png;base64,iVBORw0KGgo...",
        "product_image": "data:image/png;base64,iVBORw0KGgo..."
    }
    """
    result_image = Stylist.get_outfit_on(request.user_image, request.product_image)

    # Convert PIL Image to base64 for response
    from io import BytesIO
    import base64

    buffer = BytesIO()
    result_image.save(buffer, format="PNG")
    image_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")

    return {
        "try_on_image": f"data:image/png;base64,{image_base64}",
        "status": "success",
        "message": "Outfit try-on image generated successfully",
    }


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
