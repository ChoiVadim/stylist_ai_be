"""
Database queries for outfit data from database.
"""
from sqlalchemy.orm import Session
from src.database.user_db import SessionLocal, Product
from src.database.popularity import add_popularity_to_items
from src.utils.logger import get_logger
from functools import lru_cache
from time import time

logger = get_logger("database.products")

# Cache configuration: 5 minutes TTL
CACHE_TTL = 300  # seconds


def _get_db_session() -> Session:
    """Get a database session."""
    return SessionLocal()


@lru_cache(maxsize=1)
def __get_all_items_cached(cache_time: int) -> list[dict]:
    """
    Internal function to fetch all items from the database with time-based cache.
    
    Args:
        cache_time: Current cache period (used to invalidate cache after TTL)
    
    Returns:
        List of dictionaries with all items from database
    """
    db = _get_db_session()
    try:
        products = db.query(Product).all()
        return [_product_to_dict(product) for product in products]
    finally:
        db.close()


def __get_all_items() -> list[dict]:
    """
    Get all items with automatic time-based cache invalidation.
    Cache refreshes every CACHE_TTL seconds.
    """
    cache_time = int(time() // CACHE_TTL)
    return __get_all_items_cached(cache_time)


def _product_to_dict(product: Product) -> dict:
    """
    Convert Product model to dictionary format matching the original Google Sheets structure.
    
    This maintains backward compatibility with the existing API.
    """
    return {
        "ID": product.external_id,  # Use external_id to match original ID field
        "Description": product.description or "",
        "Price": product.price or "",
        "ImageURL": product.image_url or "",
        "ColorHEX": product.color_hex or "",
        "ProductURL": product.product_url or "",
        "ColorName": product.color_name or "",
        "DetailDescription": product.detail_description or "",
        "Type": product.type or "",
        "PersonalColorType": product.personal_color_type or "",
    }


def get_outfit_by_season(season: str) -> list[dict]:
    """
    Get outfits filtered by personal color season/type.
    
    Args:
        season: Personal color type (e.g., "Deep Autumn", "Spring Warm")
    
    Returns:
        List of outfit items matching the season
    """
    db = _get_db_session()
    try:
        products = db.query(Product).filter(
            Product.personal_color_type == season
        ).all()
        return [_product_to_dict(product) for product in products]
    finally:
        db.close()


def get_outfit_by_category(category: str) -> list[dict]:
    """
    Get outfits filtered by category.
    
    Args:
        category: Product category (e.g., "t-shirts", "trousers")
    
    Returns:
        List of outfit items matching the category
    """
    db = _get_db_session()
    try:
        products = db.query(Product).filter(
            Product.type == category
        ).all()
        return [_product_to_dict(product) for product in products]
    finally:
        db.close()


def get_outfit_by_season_and_category(season: str, category: str, sort_by_popularity: bool = True) -> list[dict]:
    """
    Get outfits filtered by both season and category, sorted by popularity.
    
    Args:
        season: Personal color type
        category: Product category
        sort_by_popularity: If True, sort by popularity (most popular first)
    
    Returns:
        List of outfit items matching both filters, sorted by popularity
    """
    db = _get_db_session()
    try:
        query = db.query(Product)
        
        if season is not None:
            query = query.filter(Product.personal_color_type == season)
        if category is not None:
            query = query.filter(Product.type == category)
        
        products = query.all()
        items = [_product_to_dict(product) for product in products]
        
        # Sort by popularity if requested
        if sort_by_popularity:
            items = add_popularity_to_items(items)
        
        return items
    finally:
        db.close()


def get_outfit_by_id(item_id: str) -> dict | None:
    """
    Get a specific outfit item by its ID.
    
    Args:
        item_id: The ID of the item to retrieve (external_id)
    
    Returns:
        Dictionary containing the item data, or None if not found
    """
    db = _get_db_session()
    try:
        try:
            item_id_int = int(item_id)
            product = db.query(Product).filter(Product.external_id == item_id_int).first()
            if product:
                return _product_to_dict(product)
        except ValueError:
            pass
        return None
    finally:
        db.close()


def get_outfits_by_ids(item_ids: list[str]) -> dict[str, dict]:
    """
    Get multiple outfit items by their IDs.
    
    Args:
        item_ids: List of item IDs to retrieve (external_ids)
    
    Returns:
        Dictionary mapping item_id to item data
    """
    db = _get_db_session()
    try:
        result = {}
        
        # Convert all IDs to integers, filtering out invalid ones
        valid_ids = []
        for item_id in item_ids:
            try:
                valid_ids.append(int(item_id))
            except ValueError:
                continue
        
        if not valid_ids:
            return result
        
        # Query all products with matching external_ids
        products = db.query(Product).filter(Product.external_id.in_(valid_ids)).all()
        
        # Build result dictionary
        for product in products:
            result[str(product.external_id)] = _product_to_dict(product)
        
        return result
    finally:
        db.close()


if __name__ == "__main__":
    print(get_outfit_by_season_and_category("Deep Autumn", "t-shirts"))
