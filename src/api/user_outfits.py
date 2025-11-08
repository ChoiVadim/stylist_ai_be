"""
User liked outfits API endpoints.
"""
from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from typing import List
from src.database.user_db import get_db, User, UserLikedOutfit
from src.utils.auth import get_current_user
from src.models import (
    LikeOutfitRequest,
    LikedOutfitResponse
)

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
    # Check if already liked
    existing_like = db.query(UserLikedOutfit).filter(
        UserLikedOutfit.user_id == current_user.id,
        UserLikedOutfit.item_id == request.item_id
    ).first()
    
    if existing_like:
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
    
    return LikedOutfitResponse(
        id=new_like.id,
        item_id=new_like.item_id,
        created_at=new_like.created_at
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
    liked_outfit = db.query(UserLikedOutfit).filter(
        UserLikedOutfit.user_id == current_user.id,
        UserLikedOutfit.item_id == item_id
    ).first()
    
    if not liked_outfit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Outfit not found in liked items"
        )
    
    db.delete(liked_outfit)
    db.commit()


@router.get("/liked", response_model=List[LikedOutfitResponse])
def get_liked_outfits(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all liked outfits for the current user.
    
    Args:
        current_user: Current authenticated user
        db: Database session
    
    Returns:
        List of liked outfits
    """
    liked_outfits = db.query(UserLikedOutfit).filter(
        UserLikedOutfit.user_id == current_user.id
    ).order_by(UserLikedOutfit.created_at.desc()).all()
    
    return [
        LikedOutfitResponse(
            id=outfit.id,
            item_id=outfit.item_id,
            created_at=outfit.created_at
        )
        for outfit in liked_outfits
    ]


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
    liked_outfit = db.query(UserLikedOutfit).filter(
        UserLikedOutfit.user_id == current_user.id,
        UserLikedOutfit.item_id == item_id
    ).first()
    
    return {"is_liked": liked_outfit is not None}

