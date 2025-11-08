"""
Authentication API endpoints for user registration and login.
"""
from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from src.database.user_db import get_db, User
from src.utils.auth import (
    get_password_hash,
    authenticate_user,
    create_access_token,
    get_current_user
)
from src.models import (
    UserRegisterRequest,
    UserLoginRequest,
    TokenResponse,
    UserResponse
)
from src.utils.logger import get_logger

logger = get_logger("api.auth")
router = APIRouter(prefix="/api/auth", tags=["authentication"])


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def register(request: UserRegisterRequest, db: Session = Depends(get_db)):
    """
    Register a new user.
    
    Args:
        request: User registration data (email and password)
        db: Database session
    
    Returns:
        Access token and user information
    """
    logger.info(f"Registration attempt for email: {request.email}")
    
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == request.email).first()
    if existing_user:
        logger.warning(f"Registration failed: Email already registered - {request.email}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    try:
        # Create new user
        hashed_password = get_password_hash(request.password)
        new_user = User(
            email=request.email,
            password_hash=hashed_password
        )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        logger.info(f"User registered successfully: user_id={new_user.id}, email={new_user.email}")
        
        # Create access token
        access_token = create_access_token(data={"sub": new_user.id})
        
        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            user_id=new_user.id,
            email=new_user.email
        )
    except Exception as e:
        logger.error(f"Registration error for email {request.email}: {str(e)}", exc_info=True)
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to register user"
        )


@router.post("/login", response_model=TokenResponse)
def login(request: UserLoginRequest, db: Session = Depends(get_db)):
    """
    Login with email and password.
    
    Args:
        request: User login credentials
        db: Database session
    
    Returns:
        Access token and user information
    """
    logger.info(f"Login attempt for email: {request.email}")
    
    user = authenticate_user(db, request.email, request.password)
    if not user:
        logger.warning(f"Login failed: Invalid credentials for email {request.email}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token
    access_token = create_access_token(data={"sub": user.id})
    logger.info(f"Login successful: user_id={user.id}, email={user.email}")
    
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user_id=user.id,
        email=user.email
    )


@router.get("/me", response_model=UserResponse)
def get_current_user_info(current_user: User = Depends(get_current_user)):
    """
    Get current authenticated user information.
    
    Args:
        current_user: Current authenticated user (from token)
    
    Returns:
        User information
    """
    logger.info(f"Get current user info request: user_id={current_user.id}, email={current_user.email}")
    
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        created_at=current_user.created_at
    )

