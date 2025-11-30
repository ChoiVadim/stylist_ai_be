"""
Outfit-related API endpoints.
"""
from fastapi import APIRouter, HTTPException
import time
import json
import os
from src.database.db import (
    get_outfit_by_season as db_get_outfit_by_season,
    get_outfit_by_category as db_get_outfit_by_category,
    get_outfit_by_season_and_category as db_get_outfit_by_season_and_category,
)
from src.database.popularity import like_item, get_item_popularity
from src.models import LikeItemRequest, OutfitScoreRequest, OutfitScoreResponse
from src.services.stylist import score_outfit_compatibility
from src.utils.logger import get_logger
from src.utils.image_validator import (
    validate_image_from_base64,
    ImageValidationError
)

logger = get_logger("api.outfits")
router = APIRouter(prefix="/api/outfit", tags=["outfits"])

@router.get("/all/{brand}")
def get_outfit_by_brand(brand: str):
    """
    Get outfits filtered by brand.
    
    Args:
        brand: Brand name (e.g., "lacoste", "zara")
    
    Returns:
        List of outfit items matching the brand
    """
    logger.info(f"Get outfits by brand request: brand={brand}")
    
    try:
        #TODO: move it to db
        # Construct absolute path to the data file
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        data_path = os.path.join(base_dir, "data", "lacoste_coupang_combined.json")
        
        with open(data_path, "r") as f:
            results = json.load(f)
        logger.info(f"Found {len(results)} outfits for brand={brand}")
        return results
    except Exception as e:
        logger.error(f"Error getting outfits by brand={brand}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error retrieving outfits: {str(e)}")

@router.get("/season/{season}")
def get_outfit_by_season(season: str):
    """
    Get outfits filtered by personal color season/type.
    
    Args:
        season: Personal color type (e.g., "Deep Autumn", "Spring Warm")
    
    Returns:
        List of outfit items matching the season
    """
    logger.info(f"Get outfits by season request: season={season}")
    
    try:
        results = db_get_outfit_by_season(season)
        logger.info(f"Found {len(results)} outfits for season={season}")
        return results
    except Exception as e:
        logger.error(f"Error getting outfits by season={season}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error retrieving outfits: {str(e)}")


@router.get("/category/{category}")
def get_outfit_by_category(category: str):
    """
    Get outfits filtered by category.
    
    Args:
        category: Product category (e.g., "t-shirts", "trousers")
    
    Returns:
        List of outfit items matching the category
    """
    logger.info(f"Get outfits by category request: category={category}")
    
    try:
        results = db_get_outfit_by_category(category)
        logger.info(f"Found {len(results)} outfits for category={category}")
        return results
    except Exception as e:
        logger.error(f"Error getting outfits by category={category}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error retrieving outfits: {str(e)}")


@router.get("/season/{season}/category/{category}")
def get_outfit_by_season_and_category(season: str, category: str):
    """
    Get outfits filtered by both season and category, sorted by popularity (most popular first).
    
    Args:
        season: Personal color type
        category: Product category
    
    Returns:
        List of outfit items matching both filters, sorted by popularity (highest first)
        Each item includes a 'popularity' field showing the number of likes.
    """
    logger.info(f"Get outfits by season and category request: season={season}, category={category}")
    
    try:
        results = db_get_outfit_by_season_and_category(season, category, sort_by_popularity=True)
        logger.info(f"Found {len(results)} outfits for season={season}, category={category}")
        return results
    except Exception as e:
        logger.error(f"Error getting outfits by season={season}, category={category}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error retrieving outfits: {str(e)}")


@router.post("/like")
def like_outfit_item(request: LikeItemRequest):
    """
    Like an outfit item to increase its popularity.
    
    When users like an item, its popularity score increases.
    Popular items will appear first in search results.
    
    Args:
        request: Contains item_id of the item to like
    
    Returns:
        Success message with new popularity count
    """
    logger.info(f"Like outfit item request: item_id={request.item_id}")
    
    try:
        new_count = like_item(request.item_id)
        logger.info(f"Item {request.item_id} liked successfully, new popularity count: {new_count}")
        return {
            "success": True,
            "message": f"Item {request.item_id} liked successfully",
            "item_id": request.item_id,
            "popularity": new_count
        }
    except Exception as e:
        logger.error(f"Error liking item {request.item_id}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error liking item: {str(e)}")


@router.get("/popularity/{item_id}")
def get_item_popularity_endpoint(item_id: str):
    """
    Get the current popularity (like count) for a specific item.
    
    Args:
        item_id: The ID of the item
    
    Returns:
        Popularity information for the item
    """
    logger.info(f"Get item popularity request: item_id={item_id}")
    
    try:
        popularity = get_item_popularity(item_id)
        logger.debug(f"Item {item_id} popularity: {popularity}")
        return {
            "item_id": item_id,
            "popularity": popularity
        }
    except Exception as e:
        logger.error(f"Error getting popularity for item {item_id}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error retrieving popularity: {str(e)}")


@router.post("/score", response_model=OutfitScoreResponse)
def score_outfit(request: OutfitScoreRequest):
    """
    Score outfit compatibility based on user image and personal color type.
    
    Analyzes how well the outfit matches the user's personal color type and provides
    detailed feedback with scores for color harmony and style match.
    
    Args:
        request: Contains user_image (base64), optional personal_color_type, and optional outfit_items
    
    Returns:
        OutfitScoreResponse with compatibility scores, feedback, strengths, and improvements
    """
    start_time = time.time()
    logger.info("Outfit score request received")
    
    try:
        # Validate image
        try:
            image, validation_result = validate_image_from_base64(
                request.user_image,
                require_face=True,  # Outfit scoring requires face for color analysis
                max_dimension=4096,
                min_dimension=100
            )
            logger.debug(f"Image validated: {validation_result}")
        except ImageValidationError as e:
            logger.warning(f"Image validation failed: {str(e)}")
            raise HTTPException(status_code=400, detail=str(e))
        
        # Score outfit compatibility
        result = score_outfit_compatibility(
            image,
            personal_color_type=request.personal_color_type
        )
        
        process_time = time.time() - start_time
        logger.info(
            f"Outfit score completed: score={result['score']:.2f}, "
            f"level={result['compatibility_level']}, time={process_time:.2f}s"
        )
        
        return OutfitScoreResponse(**result)
    except HTTPException:
        raise
    except Exception as e:
        process_time = time.time() - start_time
        logger.error(
            f"Outfit scoring failed: {str(e)}, time={process_time:.2f}s",
            exc_info=True
        )
        raise HTTPException(status_code=500, detail=f"Error scoring outfit: {str(e)}")

