from datetime import datetime
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


class LikeItemRequest(BaseModel):
    item_id: str = Field(description="The ID of the item to like")


# Authentication models
class UserRegisterRequest(BaseModel):
    email: str = Field(description="User email address")
    password: str = Field(description="User password", min_length=6)


class UserLoginRequest(BaseModel):
    email: str = Field(description="User email address")
    password: str = Field(description="User password")


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: int
    email: str


class UserResponse(BaseModel):
    id: int
    email: str
    created_at: datetime
    
    class Config:
        from_attributes = True


# Liked outfits models
class LikeOutfitRequest(BaseModel):
    item_id: str = Field(description="The ID of the outfit item to like")


class LikedOutfitResponse(BaseModel):
    id: int
    item_id: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class LikedOutfitWithDetailsResponse(BaseModel):
    id: int
    item_id: str
    created_at: datetime
    # Full item details
    description: str | None = None
    price: str | None = None
    imageUrl: str | None = None
    colorHex: str | None = None
    productUrl: str | None = None
    colorName: str | None = None
    detailDescription: str | None = None
    type: str | None = None
    personalColorType: str | None = None
    
    class Config:
        from_attributes = True


# Color results models
class SaveColorResultRequest(BaseModel):
    personal_color_type: str
    confidence: float
    undertone: str = "unknown"
    season: str = "unknown"
    subtype: str = "unknown"
    reasoning: str = ""


class ColorResultResponse(BaseModel):
    id: int
    personal_color_type: str
    confidence: float
    undertone: str
    season: str
    subtype: str
    reasoning: str
    created_at: datetime
    
    class Config:
        from_attributes = True
