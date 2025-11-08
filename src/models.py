from pydantic import BaseModel, Field


class AnalyzeColorSeasonResponseModel(BaseModel):
    personal_color_type: str = Field(
        description="The personal color type of the person"
    )
    confidence: float = Field(description="The confidence of the personal color type")
    undertone: str = Field(
        default="unknown",
        description="The undertone of the personal color type (warm, cool, or neutral)"
    )
    season: str = Field(
        default="unknown",
        description="The season of the personal color type (spring, summer, autumn, or winter)"
    )
    subtype: str = Field(
        default="unknown",
        description="The subtype of the personal color type (e.g., deep, light, soft, bright)"
    )
    reasoning: str = Field(
        default="",
        description="The reasoning of the personal color type"
    )


class AnalyzeColorSeasonRequest(BaseModel):
    image: str = Field(description="The image to analyze")


class GenerateOutfitOnRequest(BaseModel):
    user_image: str = Field(description="The image of the user")
    product_image: str = Field(description="The image of the product")
