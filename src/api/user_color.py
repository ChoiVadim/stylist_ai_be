"""
User personal color results API endpoints.
"""
from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from typing import List, Optional
from src.database.user_db import get_db, User, UserColorResult
from src.utils.auth import get_current_user
from src.models import (
    SaveColorResultRequest,
    ColorResultResponse
)

router = APIRouter(prefix="/api/user/color", tags=["user-color"])


@router.post("/save", response_model=ColorResultResponse, status_code=status.HTTP_201_CREATED)
def save_color_result(
    request: SaveColorResultRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Save a personal color analysis result for the current user.
    
    Args:
        request: Color analysis result data
        current_user: Current authenticated user
        db: Database session
    
    Returns:
        Saved color result information
    """
    color_result = UserColorResult(
        user_id=current_user.id,
        personal_color_type=request.personal_color_type,
        confidence=request.confidence,
        undertone=request.undertone,
        season=request.season,
        subtype=request.subtype,
        reasoning=request.reasoning
    )
    
    db.add(color_result)
    db.commit()
    db.refresh(color_result)
    
    return ColorResultResponse(
        id=color_result.id,
        personal_color_type=color_result.personal_color_type,
        confidence=color_result.confidence,
        undertone=color_result.undertone,
        season=color_result.season,
        subtype=color_result.subtype,
        reasoning=color_result.reasoning,
        created_at=color_result.created_at
    )


@router.get("/results", response_model=List[ColorResultResponse])
def get_color_results(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    limit: Optional[int] = None
):
    """
    Get all personal color analysis results for the current user.
    
    Args:
        current_user: Current authenticated user
        db: Database session
        limit: Optional limit on number of results to return (most recent first)
    
    Returns:
        List of color analysis results
    """
    query = db.query(UserColorResult).filter(
        UserColorResult.user_id == current_user.id
    ).order_by(UserColorResult.created_at.desc())
    
    if limit:
        query = query.limit(limit)
    
    results = query.all()
    
    return [
        ColorResultResponse(
            id=result.id,
            personal_color_type=result.personal_color_type,
            confidence=result.confidence,
            undertone=result.undertone,
            season=result.season,
            subtype=result.subtype,
            reasoning=result.reasoning,
            created_at=result.created_at
        )
        for result in results
    ]


@router.get("/latest", response_model=ColorResultResponse)
def get_latest_color_result(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get the most recent personal color analysis result for the current user.
    
    Args:
        current_user: Current authenticated user
        db: Database session
    
    Returns:
        Most recent color analysis result
    """
    result = db.query(UserColorResult).filter(
        UserColorResult.user_id == current_user.id
    ).order_by(UserColorResult.created_at.desc()).first()
    
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No color analysis results found"
        )
    
    return ColorResultResponse(
        id=result.id,
        personal_color_type=result.personal_color_type,
        confidence=result.confidence,
        undertone=result.undertone,
        season=result.season,
        subtype=result.subtype,
        reasoning=result.reasoning,
        created_at=result.created_at
    )


@router.delete("/results/{result_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_color_result(
    result_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete a specific color analysis result.
    
    Args:
        result_id: ID of the color result to delete
        current_user: Current authenticated user
        db: Database session
    """
    result = db.query(UserColorResult).filter(
        UserColorResult.id == result_id,
        UserColorResult.user_id == current_user.id
    ).first()
    
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Color result not found"
        )
    
    db.delete(result)
    db.commit()

