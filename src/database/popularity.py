"""
Popularity tracking for outfit items.
Stores like counts in the database.
"""
from sqlalchemy.orm import Session
from src.database.user_db import SessionLocal, Popularity
from typing import Dict
from src.utils.logger import get_logger

logger = get_logger("database.popularity")


def _get_db_session() -> Session:
    """Get a database session."""
    return SessionLocal()


def like_item(item_id: str) -> int:
    """
    Increment like count for an item.
    
    Args:
        item_id: The ID of the item to like
    
    Returns:
        New like count for the item
    """
    db = _get_db_session()
    try:
        # Try to get existing popularity record
        popularity = db.query(Popularity).filter(Popularity.item_id == item_id).first()
        
        if popularity:
            # Increment existing count
            popularity.like_count += 1
            db.commit()
            return popularity.like_count
        else:
            # Create new record
            popularity = Popularity(item_id=item_id, like_count=1)
            db.add(popularity)
            db.commit()
            db.refresh(popularity)
            return popularity.like_count
    except Exception as e:
        db.rollback()
        logger.error(f"Error liking item {item_id}: {str(e)}", exc_info=True)
        raise
    finally:
        db.close()


def get_item_popularity(item_id: str) -> int:
    """
    Get current popularity (like count) for an item.
    
    Args:
        item_id: The ID of the item
    
    Returns:
        Like count (0 if item has no likes)
    """
    db = _get_db_session()
    try:
        popularity = db.query(Popularity).filter(Popularity.item_id == item_id).first()
        return popularity.like_count if popularity else 0
    finally:
        db.close()


def get_all_popularity() -> Dict[str, int]:
    """
    Get all popularity data.
    
    Returns:
        Dictionary mapping item_id to like count
    """
    db = _get_db_session()
    try:
        popularities = db.query(Popularity).all()
        return {str(pop.item_id): pop.like_count for pop in popularities}
    finally:
        db.close()


def add_popularity_to_items(items: list[dict]) -> list[dict]:
    """
    Add popularity scores to a list of items and sort by popularity (descending).
    
    Args:
        items: List of item dictionaries
    
    Returns:
        List of items with 'popularity' field added, sorted by popularity (highest first)
    """
    popularity = get_all_popularity()
    
    # Add popularity to each item
    for item in items:
        item_id = str(item.get("ID", ""))
        item["popularity"] = popularity.get(item_id, 0)
    
    # Sort by popularity (descending), then by ID for consistency
    sorted_items = sorted(
        items,
        key=lambda x: (x.get("popularity", 0), x.get("ID", 0)),
        reverse=True
    )
    
    return sorted_items

