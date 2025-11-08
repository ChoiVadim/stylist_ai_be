"""
Outfit-related API endpoints.
"""
from fastapi import APIRouter, HTTPException
from src.database.db import (
    get_outfit_by_season as db_get_outfit_by_season,
    get_outfit_by_category as db_get_outfit_by_category,
    get_outfit_by_season_and_category as db_get_outfit_by_season_and_category,
)
from src.database.popularity import like_item, get_item_popularity
from src.models import LikeItemRequest

router = APIRouter(prefix="/api/outfit", tags=["outfits"])


@router.get("/season/{season}")
def get_outfit_by_season(season: str):
    """
    Get outfits filtered by personal color season/type.
    
    Args:
        season: Personal color type (e.g., "Deep Autumn", "Spring Warm")
    
    Returns:
        List of outfit items matching the season
    """
    return db_get_outfit_by_season(season)


@router.get("/category/{category}")
def get_outfit_by_category(category: str):
    """
    Get outfits filtered by category.
    
    Args:
        category: Product category (e.g., "t-shirts", "trousers")
    
    Returns:
        List of outfit items matching the category
    """
    return db_get_outfit_by_category(category)


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
    return db_get_outfit_by_season_and_category(season, category, sort_by_popularity=True)


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
    try:
        new_count = like_item(request.item_id)
        return {
            "success": True,
            "message": f"Item {request.item_id} liked successfully",
            "item_id": request.item_id,
            "popularity": new_count
        }
    except Exception as e:
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
    popularity = get_item_popularity(item_id)
    return {
        "item_id": item_id,
        "popularity": popularity
    }

