"""
User profile management endpoints.
Allows users to store and retrieve their personal information for clothing recommendations.
"""
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.database.user_db import get_db, User, UserProfile
from src.models import UpdateUserProfileRequest, UserProfileResponse
from src.utils.auth import get_current_user
from src.utils.logger import get_logger

logger = get_logger("api.user_info")
router = APIRouter(prefix="/api/user", tags=["user-profile"])


def normalize_base64_image(base64_image: str) -> str:
    """
    Normalize base64 encoded image string.
    Removes data:image/xxx;base64, prefix if present and validates the format.
    
    Args:
        base64_image: Base64 encoded image string
    
    Returns:
        Normalized base64 string (with prefix)
    """
    # If it already has the prefix, return as is
    if base64_image.startswith("data:image/"):
        return base64_image
    
    # If no prefix, add a default one
    return f"data:image/jpeg;base64,{base64_image}"


@router.get("/profile", response_model=UserProfileResponse)
async def get_user_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get current user's profile information.
    Returns 404 if profile doesn't exist yet.
    """
    logger.info(f"Get profile request for user_id={current_user.id}")
    
    try:
        profile = db.query(UserProfile).filter(UserProfile.user_id == current_user.id).first()
        
        if not profile:
            logger.warning(f"Profile not found for user_id={current_user.id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User profile not found. Please create a profile first."
            )
        
        logger.info(f"Profile retrieved successfully for user_id={current_user.id}")
        return profile
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving profile for user_id={current_user.id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve user profile"
        )


@router.post("/profile", response_model=UserProfileResponse, status_code=status.HTTP_201_CREATED)
async def create_or_update_user_profile(
    profile_data: UpdateUserProfileRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create or update user profile information.
    All fields are optional - user can provide as much or as little information as they want.
    Images are stored as base64 encoded strings in the request and saved to disk.
    """
    logger.info(f"Create/update profile request for user_id={current_user.id}")
    
    try:
        # Check if profile already exists
        profile = db.query(UserProfile).filter(UserProfile.user_id == current_user.id).first()
        
        # Prepare data dictionary
        profile_dict = profile_data.model_dump(exclude_none=True)
        fields_provided = list(profile_dict.keys())
        logger.debug(f"Profile update fields provided: {fields_provided} for user_id={current_user.id}")
        
        # Normalize image strings if provided
        if profile_dict.get("body_image"):
            profile_dict["body_image"] = normalize_base64_image(profile_dict["body_image"])
            logger.debug(f"Body image normalized for user_id={current_user.id}")
        
        if profile_dict.get("face_image"):
            profile_dict["face_image"] = normalize_base64_image(profile_dict["face_image"])
            logger.debug(f"Face image normalized for user_id={current_user.id}")
        
        if profile:
            # Update existing profile
            logger.info(f"Updating existing profile for user_id={current_user.id}")
            for key, value in profile_dict.items():
                setattr(profile, key, value)
            profile.updated_at = datetime.utcnow()
        else:
            # Create new profile
            logger.info(f"Creating new profile for user_id={current_user.id}")
            profile = UserProfile(user_id=current_user.id, **profile_dict)
            db.add(profile)
        
        db.commit()
        db.refresh(profile)
        
        logger.info(f"Profile {'updated' if profile.updated_at else 'created'} successfully for user_id={current_user.id}")
        return profile
    except Exception as e:
        logger.error(f"Error creating/updating profile for user_id={current_user.id}: {str(e)}", exc_info=True)
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create or update user profile"
        )


@router.put("/profile", response_model=UserProfileResponse)
async def update_user_profile(
    profile_data: UpdateUserProfileRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update existing user profile information.
    This is an alias for POST /profile for convenience.
    """
    return await create_or_update_user_profile(profile_data, current_user, db)


@router.delete("/profile", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete user profile information.
    """
    logger.info(f"Delete profile request for user_id={current_user.id}")
    
    try:
        profile = db.query(UserProfile).filter(UserProfile.user_id == current_user.id).first()
        
        if not profile:
            logger.warning(f"Profile not found for deletion, user_id={current_user.id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User profile not found"
            )
        
        db.delete(profile)
        db.commit()
        
        logger.info(f"Profile deleted successfully for user_id={current_user.id}")
        return None
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting profile for user_id={current_user.id}: {str(e)}", exc_info=True)
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete user profile"
        )


@router.get("/profile/completeness")
async def get_profile_completeness(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get profile completeness percentage.
    Useful for showing progress in onboarding UI.
    """
    logger.info(f"Get profile completeness request for user_id={current_user.id}")
    
    try:
        profile = db.query(UserProfile).filter(UserProfile.user_id == current_user.id).first()
        
        if not profile:
            logger.debug(f"No profile found, returning 0% completeness for user_id={current_user.id}")
            return {
                "completeness": 0,
                "total_fields": 12,
                "filled_fields": 0,
                "missing_fields": [
                    "height", "weight", "chest_size", "waist_size", "hip_size",
                    "shoe_size", "clothing_size", "age", "gender", "preferred_style",
                    "body_image", "face_image"
                ]
            }
        
        # Define all profile fields
        fields = [
            "height", "weight", "chest_size", "waist_size", "hip_size",
            "shoe_size", "clothing_size", "age", "gender", "preferred_style",
            "body_image", "face_image"
        ]
        
        # Count filled fields
        filled_fields = sum(1 for field in fields if getattr(profile, field) is not None)
        total_fields = len(fields)
        completeness = round((filled_fields / total_fields) * 100, 2)
        
        # Get missing fields
        missing_fields = [field for field in fields if getattr(profile, field) is None]
        
        logger.info(f"Profile completeness: {completeness}% ({filled_fields}/{total_fields} fields) for user_id={current_user.id}")
        
        return {
            "completeness": completeness,
            "total_fields": total_fields,
            "filled_fields": filled_fields,
            "missing_fields": missing_fields
        }
    except Exception as e:
        logger.error(f"Error getting profile completeness for user_id={current_user.id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get profile completeness"
        )

