"""
Database queries for outfit data from Google Sheets.
"""
import gspread
import pandas as pd
from src.database.popularity import add_popularity_to_items
from functools import lru_cache
from time import time

auth_file = "auth.json"
sheet_url = "https://docs.google.com/spreadsheets/d/10NkfXVm8WYel4GTTTIaFyPxmVy52ODjda0WNpl70dF8/edit?gid=0#gid=0"

# Lazy initialization - only connect when needed
_gc = None
_sheet_file = None
_sheet = None

# Cache configuration: 5 minutes TTL
CACHE_TTL = 300  # seconds


def _get_sheet():
    """
    Lazy initialization of Google Sheets connection.
    Only connects when first accessed.
    """
    global _gc, _sheet_file, _sheet
    
    if _sheet is None:
        _gc = gspread.service_account(filename=auth_file)
        _sheet_file = _gc.open_by_url(sheet_url)
        _sheet = _sheet_file.worksheet("Main")
    
    return _sheet


@lru_cache(maxsize=1)
def __get_all_items_cached(cache_time: int):
    """
    Internal function to fetch all items from the sheet with time-based cache.
    
    Args:
        cache_time: Current cache period (used to invalidate cache after TTL)
    
    Returns:
        DataFrame with all items from Google Sheets
    """
    sheet = _get_sheet()
    data = sheet.get_all_records()
    df = pd.DataFrame(data)
    return df


def __get_all_items():
    """
    Get all items with automatic time-based cache invalidation.
    Cache refreshes every CACHE_TTL seconds.
    """
    cache_time = int(time() // CACHE_TTL)
    return __get_all_items_cached(cache_time)


def get_outfit_by_season(season: str) -> list[dict]:
    """
    Get outfits filtered by personal color season/type.
    
    Args:
        season: Personal color type (e.g., "Deep Autumn", "Spring Warm")
    
    Returns:
        List of outfit items matching the season
    """
    df = __get_all_items()
    df = df.loc[df['PersonalColorType'] == season]
    return df.to_dict(orient='records')


def get_outfit_by_category(category: str) -> list[dict]:
    """
    Get outfits filtered by category.
    
    Args:
        category: Product category (e.g., "t-shirts", "trousers")
    
    Returns:
        List of outfit items matching the category
    """
    df = __get_all_items()
    df = df.loc[df['Type'] == category]
    return df.to_dict(orient='records')


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
    df = __get_all_items()
    if season is not None:
        df = df.loc[df['PersonalColorType'] == season]
    if category is not None:
        df = df.loc[df['Type'] == category]
    if season is not None and category is not None:
        df = df.loc[(df['PersonalColorType'] == season) & (df['Type'] == category)]
        items = df.to_dict(orient='records')
        
        # Sort by popularity if requested
        if sort_by_popularity:
            items = add_popularity_to_items(items)
        
        return items
    return []


def get_outfit_by_id(item_id: str) -> dict | None:
    """
    Get a specific outfit item by its ID.
    
    Args:
        item_id: The ID of the item to retrieve
    
    Returns:
        Dictionary containing the item data, or None if not found
    """
    df = __get_all_items()
    # Convert item_id to int for comparison
    try:
        item_id_int = int(item_id)
        item = df.loc[df['ID'] == item_id_int]
        if not item.empty:
            return item.to_dict(orient='records')[0]
    except (ValueError, IndexError):
        pass
    return None


def get_outfits_by_ids(item_ids: list[str]) -> dict[str, dict]:
    """
    Get multiple outfit items by their IDs.
    
    Args:
        item_ids: List of item IDs to retrieve
    
    Returns:
        Dictionary mapping item_id to item data
    """
    df = __get_all_items()
    result = {}
    
    for item_id in item_ids:
        try:
            item_id_int = int(item_id)
            item = df.loc[df['ID'] == item_id_int]
            if not item.empty:
                result[item_id] = item.to_dict(orient='records')[0]
        except (ValueError, IndexError):
            continue
    
    return result


if __name__ == "__main__":
    print(get_outfit_by_season_and_category("Deep Autumn", "t-shirts"))

