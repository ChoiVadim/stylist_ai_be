"""
Popularity tracking for outfit items.
Stores like counts in a JSON file for simplicity (can be migrated to database later).
"""
import json
import os
from pathlib import Path
from typing import Dict

POPULARITY_FILE = Path("data/popularity.json")


def _load_popularity() -> Dict[str, int]:
    """Load popularity data from file."""
    if not POPULARITY_FILE.exists():
        return {}
    
    try:
        with open(POPULARITY_FILE, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return {}


def _save_popularity(data: Dict[str, int]):
    """Save popularity data to file."""
    # Ensure data directory exists
    POPULARITY_FILE.parent.mkdir(parents=True, exist_ok=True)
    
    with open(POPULARITY_FILE, "w") as f:
        json.dump(data, f, indent=2)


def like_item(item_id: str) -> int:
    """
    Increment like count for an item.
    
    Args:
        item_id: The ID of the item to like
    
    Returns:
        New like count for the item
    """
    popularity = _load_popularity()
    current_count = popularity.get(item_id, 0)
    popularity[item_id] = current_count + 1
    _save_popularity(popularity)
    return popularity[item_id]


def get_item_popularity(item_id: str) -> int:
    """
    Get current popularity (like count) for an item.
    
    Args:
        item_id: The ID of the item
    
    Returns:
        Like count (0 if item has no likes)
    """
    popularity = _load_popularity()
    return popularity.get(item_id, 0)


def get_all_popularity() -> Dict[str, int]:
    """
    Get all popularity data.
    
    Returns:
        Dictionary mapping item_id to like count
    """
    return _load_popularity()


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

