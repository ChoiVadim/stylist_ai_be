"""
User liked outfits API endpoints.
"""
from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from typing import List
from src.database.user_db import get_db, User, UserLikedOutfit
from src.utils.auth import get_current_user
from src.database.db import get_outfits_by_ids
from src.models import (
    LikeOutfitRequest,
    LikedOutfitResponse,
    LikedOutfitWithDetailsResponse
)
from src.utils.logger import get_logger

logger = get_logger("api.user_outfits")
router = APIRouter(prefix="/api/user/outfits", tags=["user-outfits"])


@router.post("/like", response_model=LikedOutfitResponse, status_code=status.HTTP_201_CREATED)
def like_outfit(
    request: LikeOutfitRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Like an outfit item (add to user's liked outfits).
    
    Args:
        request: Contains item_id of the outfit to like
        current_user: Current authenticated user
        db: Database session
    
    Returns:
        Liked outfit information
    """
    logger.info(f"Like outfit request: user_id={current_user.id}, item_id={request.item_id}")
    
    try:
        # Check if already liked
        existing_like = db.query(UserLikedOutfit).filter(
            UserLikedOutfit.user_id == current_user.id,
            UserLikedOutfit.item_id == request.item_id
        ).first()
        
        if existing_like:
            logger.warning(f"Outfit already liked: user_id={current_user.id}, item_id={request.item_id}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Outfit already liked"
            )
        
        # Create new like
        new_like = UserLikedOutfit(
            user_id=current_user.id,
            item_id=request.item_id
        )
        
        db.add(new_like)
        db.commit()
        db.refresh(new_like)
        
        logger.info(f"Outfit liked successfully: user_id={current_user.id}, item_id={request.item_id}, like_id={new_like.id}")
        
        return LikedOutfitResponse(
            id=new_like.id,
            item_id=new_like.item_id,
            created_at=new_like.created_at
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error liking outfit for user_id={current_user.id}, item_id={request.item_id}: {str(e)}", exc_info=True)
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to like outfit"
        )


@router.delete("/like/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def unlike_outfit(
    item_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Unlike an outfit item (remove from user's liked outfits).
    
    Args:
        item_id: ID of the outfit item to unlike
        current_user: Current authenticated user
        db: Database session
    """
    logger.info(f"Unlike outfit request: user_id={current_user.id}, item_id={item_id}")
    
    try:
        liked_outfit = db.query(UserLikedOutfit).filter(
            UserLikedOutfit.user_id == current_user.id,
            UserLikedOutfit.item_id == item_id
        ).first()
        
        if not liked_outfit:
            logger.warning(f"Outfit not found in liked items: user_id={current_user.id}, item_id={item_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Outfit not found in liked items"
            )
        
        db.delete(liked_outfit)
        db.commit()
        
        logger.info(f"Outfit unliked successfully: user_id={current_user.id}, item_id={item_id}")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error unliking outfit for user_id={current_user.id}, item_id={item_id}: {str(e)}", exc_info=True)
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to unlike outfit"
        )


@router.get("/liked", response_model=List[LikedOutfitWithDetailsResponse])
def get_liked_outfits(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all liked outfits for the current user with full item details.
    
    Args:
        current_user: Current authenticated user
        db: Database session
    
    Returns:
        List of liked outfits with full item details
    """
    logger.info(f"Get liked outfits request for user_id={current_user.id}")
    
    try:
        liked_outfits = db.query(UserLikedOutfit).filter(
            UserLikedOutfit.user_id == current_user.id
        ).order_by(UserLikedOutfit.created_at.desc()).all()
        
        logger.debug(f"Found {len(liked_outfits)} liked outfits for user_id={current_user.id}")
        
        # Get all item IDs
        item_ids = [outfit.item_id for outfit in liked_outfits]
        
        # Fetch full item details for all items at once
        items_data = get_outfits_by_ids(item_ids)
        
        # Combine liked outfit info with full item details
        result = []
        for outfit in liked_outfits:
            item_data = items_data.get(outfit.item_id, {})
            
            result.append(
                LikedOutfitWithDetailsResponse(
                    id=outfit.id,
                    item_id=outfit.item_id,
                    created_at=outfit.created_at,
                    # Add full item details if found (using database column names)
                    description=item_data.get('Description'),
                    price=item_data.get('Price'),
                    imageUrl=item_data.get('ImageURL'),
                    colorHex=item_data.get('ColorHEX'),
                    productUrl=item_data.get('ProductURL'),
                    colorName=item_data.get('ColorName'),
                    detailDescription=item_data.get('DetailDescription'),
                    type=item_data.get('Type'),
                    personalColorType=item_data.get('PersonalColorType')
                )
            )
        
        logger.info(f"Returning {len(result)} liked outfits with details for user_id={current_user.id}")
        return result
    except Exception as e:
        logger.error(f"Error getting liked outfits for user_id={current_user.id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve liked outfits"
        )


@router.get("/liked/{item_id}")
def check_if_liked(
    item_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Check if a specific outfit is liked by the current user.
    
    Args:
        item_id: ID of the outfit item to check
        current_user: Current authenticated user
        db: Database session
    
    Returns:
        Boolean indicating if the outfit is liked
    """
    logger.debug(f"Check if liked: user_id={current_user.id}, item_id={item_id}")
    
    try:
        liked_outfit = db.query(UserLikedOutfit).filter(
            UserLikedOutfit.user_id == current_user.id,
            UserLikedOutfit.item_id == item_id
        ).first()
        
        is_liked = liked_outfit is not None
        logger.debug(f"Outfit like status: user_id={current_user.id}, item_id={item_id}, is_liked={is_liked}")
        
        return {"is_liked": is_liked}
    except Exception as e:
        logger.error(f"Error checking if outfit is liked: user_id={current_user.id}, item_id={item_id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to check outfit like status"
        )

