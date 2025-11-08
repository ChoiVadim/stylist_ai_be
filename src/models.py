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

class GenerateOutfitOnFullOutfitRequest(BaseModel):
    user_image: str = Field(description="The image of the user")
    upper_image: str = Field(description="The image of the upper body")
    lower_image: str = Field(description="The image of the lower body")
    shoes_image: str = Field(description="The image of the shoes")


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


# User profile models
class UpdateUserProfileRequest(BaseModel):
    """Request model for updating user profile - all fields are optional."""
    height: float | None = Field(None, description="Height in cm", gt=0)
    weight: float | None = Field(None, description="Weight in kg", gt=0)
    chest_size: float | None = Field(None, description="Chest/bust size in cm", gt=0)
    waist_size: float | None = Field(None, description="Waist size in cm", gt=0)
    hip_size: float | None = Field(None, description="Hip size in cm", gt=0)
    shoe_size: float | None = Field(None, description="Shoe size (EU)", gt=0)
    clothing_size: str | None = Field(None, description="Clothing size (S, M, L, XL, etc.)")
    age: int | None = Field(None, description="Age in years", gt=0, lt=150)
    gender: str | None = Field(None, description="Gender (male, female, other)")
    preferred_style: str | None = Field(None, description="Preferred clothing style")
    body_image: str | None = Field(None, description="Base64 encoded full body image")
    face_image: str | None = Field(None, description="Base64 encoded face image")


class UserProfileResponse(BaseModel):
    """Response model for user profile."""
    id: int
    user_id: int
    height: float | None = None
    weight: float | None = None
    chest_size: float | None = None
    waist_size: float | None = None
    hip_size: float | None = None
    shoe_size: float | None = None
    clothing_size: str | None = None
    age: int | None = None
    gender: str | None = None
    preferred_style: str | None = None
    body_image: str | None = None  # Base64 encoded image string
    face_image: str | None = None  # Base64 encoded image string
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Outfit compatibility models
class OutfitScoreRequest(BaseModel):
    """Request model for outfit compatibility scoring."""
    user_image: str = Field(description="Base64 encoded image of the user wearing the outfit")
    personal_color_type: str | None = Field(None, description="User's personal color type (optional, can be analyzed from image)")
    outfit_items: list[str] | None = Field(None, description="List of outfit item IDs (optional)")


class OutfitScoreResponse(BaseModel):
    """Response model for outfit compatibility score."""
    score: float = Field(description="Compatibility score from 0.0 to 1.0", ge=0.0, le=1.0)
    personal_color_type: str = Field(description="Detected or provided personal color type")
    compatibility_level: str = Field(description="Compatibility level: excellent, good, fair, poor")
    color_harmony: float = Field(description="Color harmony score (0.0-1.0)", ge=0.0, le=1.0)
    style_match: float = Field(description="Style match score (0.0-1.0)", ge=0.0, le=1.0)
    feedback: str = Field(description="Detailed feedback and recommendations")
    strengths: list[str] = Field(description="List of outfit strengths")
    improvements: list[str] = Field(description="List of suggested improvements")


# Beauty recommendation models
class MakeupRecommendationRequest(BaseModel):
    """Request model for makeup recommendations."""
    face_image: str = Field(description="Base64 encoded face image")
    personal_color_type: str | None = Field(None, description="Personal color type (optional)")


class MakeupRecommendationResponse(BaseModel):
    """Response model for makeup recommendations."""
    personal_color_type: str = Field(description="Detected or provided personal color type")
    lipstick_colors: list[str] = Field(description="Recommended lipstick colors (HEX)")
    eyeshadow_colors: list[str] = Field(description="Recommended eyeshadow colors (HEX)")
    blush_colors: list[str] = Field(description="Recommended blush colors (HEX)")
    foundation_tone: str = Field(description="Recommended foundation tone")
    recommendations: str = Field(description="Detailed makeup recommendations")


class HairRecommendationRequest(BaseModel):
    """Request model for hair recommendations."""
    face_image: str = Field(description="Base64 encoded face image")
    personal_color_type: str | None = Field(None, description="Personal color type (optional)")
    current_hair_color: str | None = Field(None, description="Current hair color (optional)")


class HairRecommendationResponse(BaseModel):
    """Response model for hair recommendations."""
    personal_color_type: str = Field(description="Detected or provided personal color type")
    recommended_colors: list[str] = Field(description="Recommended hair colors (HEX)")
    recommended_styles: list[str] = Field(description="Recommended hair styles")
    recommendations: str = Field(description="Detailed hair recommendations")
