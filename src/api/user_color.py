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
from src.utils.logger import get_logger

logger = get_logger("api.user_color")
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
    logger.info(f"Save color result request for user_id={current_user.id}, color_type={request.personal_color_type}")
    
    try:
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
        
        logger.info(f"Color result saved successfully: id={color_result.id}, user_id={current_user.id}, color_type={color_result.personal_color_type}, confidence={color_result.confidence:.2f}")
        
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
    except Exception as e:
        logger.error(f"Error saving color result for user_id={current_user.id}: {str(e)}", exc_info=True)
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to save color result"
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
    logger.info(f"Get color results request for user_id={current_user.id}, limit={limit}")
    
    try:
        query = db.query(UserColorResult).filter(
            UserColorResult.user_id == current_user.id
        ).order_by(UserColorResult.created_at.desc())
        
        if limit:
            query = query.limit(limit)
        
        results = query.all()
        logger.info(f"Found {len(results)} color results for user_id={current_user.id}")
        
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
    except Exception as e:
        logger.error(f"Error getting color results for user_id={current_user.id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve color results"
        )


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
    logger.info(f"Get latest color result request for user_id={current_user.id}")
    
    try:
        result = db.query(UserColorResult).filter(
            UserColorResult.user_id == current_user.id
        ).order_by(UserColorResult.created_at.desc()).first()
        
        if not result:
            logger.warning(f"No color results found for user_id={current_user.id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No color analysis results found"
            )
        
        logger.info(f"Latest color result retrieved: id={result.id}, color_type={result.personal_color_type}, user_id={current_user.id}")
        
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
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting latest color result for user_id={current_user.id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve latest color result"
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
    logger.info(f"Delete color result request: result_id={result_id}, user_id={current_user.id}")
    
    try:
        result = db.query(UserColorResult).filter(
            UserColorResult.id == result_id,
            UserColorResult.user_id == current_user.id
        ).first()
        
        if not result:
            logger.warning(f"Color result not found: result_id={result_id}, user_id={current_user.id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Color result not found"
            )
        
        db.delete(result)
        db.commit()
        
        logger.info(f"Color result deleted successfully: result_id={result_id}, user_id={current_user.id}")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting color result {result_id} for user_id={current_user.id}: {str(e)}", exc_info=True)
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete color result"
        )

