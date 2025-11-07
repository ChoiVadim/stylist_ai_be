from PIL import Image
from io import BytesIO
from google.genai import types
from src.config import config

client = config.get_client()

def get_your_color_season(image_url: str) -> str:
    image = Image.open(image_url)

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        config=types.GenerateContentConfig(
            system_instruction=config.SYSTEM_PROMPT),
        contents=[image, "Analyze the person's color season."]
    )

    return response.text

def get_outfit_on(user_image_url: str, product_image_url: str) -> str:
    prompt = (config.NANO_BANANA_PROMPT)

    user_image = Image.open(user_image_url)
    product_image = Image.open(product_image_url)
    contents = [prompt, user_image, product_image]

    response = client.models.generate_content(
        model="gemini-2.0-flash-preview-image-generation",
        contents=contents,
        config=types.GenerateContentConfig(
            image_config=types.ImageConfig(
                aspect_ratio="16:9",
            )
        )
    )


    for part in response.candidates[0].content.parts:
        if part.text is not None:
            print(part.text)
        elif part.inline_data is not None:
            image = Image.open(BytesIO(part.inline_data.data))
            image.save("generated_image.png")


if __name__ == "__main__":
    # get_your_color_season("data/image_test.JPG")
    get_outfit_on("data/image_test.JPG", "data/product_test.png")