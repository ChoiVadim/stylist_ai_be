import fastapi
import uvicorn

import src.stylist as Stylist
from src.models import AnalyzeColorSeasonRequest, GenerateOutfitOnRequest
from fastapi import UploadFile, File
from fastapi.responses import StreamingResponse

from PIL import Image
from io import BytesIO

app = fastapi.FastAPI()


@app.get("/")
def read_root():
    return {"message": "Lets win Hack Seoul! I need more money, please im broke!"}

@app.post("/api/test/analyze/color")
async def test_upload_image(file: UploadFile = File(...)):
    contents = await file.read()
    image = Image.open(BytesIO(contents))
    return Stylist.get_your_color_season(image).model_dump()

@app.post(
    "/api/test/try-on/generate",
    responses={
        200: {
            "content": {
                "image/png": {
                    "schema": {"type": "string", "format": "binary"}
                }
            },
            "description": "Returns the generated try-on PNG image",
        }
    },
)
async def download_try_on_image(user_image: UploadFile = File(...), product_image: UploadFile = File(...)):
    contents = await user_image.read()
    user_image = Image.open(BytesIO(contents))
    contents = await product_image.read()
    product_image = Image.open(BytesIO(contents))
    result = Stylist.get_outfit_on(user_image, product_image)

    buffer = BytesIO()
    result.save(buffer, format="PNG")
    buffer.seek(0)
    headers = {"Content-Disposition": 'attachment; filename="try_on.png"'}
    return StreamingResponse(buffer, media_type="image/png", headers=headers)


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
