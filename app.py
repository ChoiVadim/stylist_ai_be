import fastapi
import uvicorn

import src.stylist as Stylist
from src.models import AnalyzeColorSeasonRequest, GenerateOutfitOnRequest

app = fastapi.FastAPI()


@app.get("/")
def read_root():
    return {"message": "Hello, World!"}


@app.post("/api/analyze/color")
def get_color_season(request: AnalyzeColorSeasonRequest):
    """
    Analyze color season from an image.

    Request body should contain:
    {
        "image": "data:image/png;base64,iVBORw0KGgo..." or just "iVBORw0KGgo..."
    }
    """
    result = Stylist.get_your_color_season(request.image)
    return result.model_dump()


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
