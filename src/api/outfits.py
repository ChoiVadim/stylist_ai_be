"""
Outfit-related API endpoints.
"""
from fastapi import APIRouter
from src.database.db import (
    get_outfit_by_season as db_get_outfit_by_season,
    get_outfit_by_category as db_get_outfit_by_category,
    get_outfit_by_season_and_category as db_get_outfit_by_season_and_category,
)

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
    Get outfits filtered by both season and category.
    
    Args:
        season: Personal color type
        category: Product category
    
    Returns:
        List of outfit items matching both filters
    """
    return db_get_outfit_by_season_and_category(season, category)

