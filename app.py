import fastapi
import uvicorn

import src.stylist as Stylist

app = fastapi.FastAPI()

@app.get("/")
def read_root():
    return {"message": "Hello, World!"}

@app.get("/color-season")
def get_color_season(image_url: str):
    return Stylist.get_your_color_season(image_url)

@app.get("/outfit-on")
def get_outfit_on(user_image_url: str, product_image_url: str):
    return Stylist.get_outfit_on(user_image_url, product_image_url)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)