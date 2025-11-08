"""
Authentication utilities for password hashing and JWT tokens.
"""
import os
import bcrypt
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from src.database.user_db import get_db, User
from src.utils.logger import get_logger

logger = get_logger("utils.auth")

# HTTP Bearer scheme for token extraction (simpler for JWT tokens)
security = HTTPBearer()

# JWT settings
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30 * 24 * 60  # 30 days

if not SECRET_KEY:
    logger.warning("SECRET_KEY not set in environment variables! Using default (not secure for production)")
    SECRET_KEY = "your-secret-key-change-in-production"
else:
    logger.info("SECRET_KEY loaded from environment")


def get_password_hash(password: str) -> str:
    """
    Hash a password using bcrypt.
    Handles the 72-byte limit by encoding to bytes and truncating if necessary.
    """
    password_bytes = password.encode('utf-8')
    # Bcrypt has a 72-byte limit, truncate if necessary
    if len(password_bytes) > 72:
        password_bytes = password_bytes[:72]
    # Generate salt and hash password
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    password_bytes = plain_password.encode('utf-8')
    # Bcrypt has a 72-byte limit, truncate if necessary
    if len(password_bytes) > 72:
        password_bytes = password_bytes[:72]
    hashed_bytes = hashed_password.encode('utf-8')
    return bcrypt.checkpw(password_bytes, hashed_bytes)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token."""
    try:
        to_encode = data.copy()
        # Ensure user_id is converted to string for JWT
        if "sub" in to_encode:
            to_encode["sub"] = str(to_encode["sub"])
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        logger.debug(f"Access token created for user_id={to_encode.get('sub')}")
        return encoded_jwt
    except Exception as e:
        logger.error(f"Failed to create access token: {str(e)}", exc_info=True)
        raise


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """Get the current authenticated user from JWT token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    token = credentials.credentials
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id_str = payload.get("sub")
        if user_id_str is None:
            logger.warning("JWT token missing 'sub' claim")
            raise credentials_exception
        user_id = int(user_id_str)
    except JWTError as e:
        logger.warning(f"JWT decode error: {str(e)}")
        raise credentials_exception
    except (ValueError, TypeError) as e:
        logger.warning(f"Invalid user_id in token: {str(e)}")
        raise credentials_exception
    
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        logger.warning(f"User not found for user_id={user_id}")
        raise credentials_exception
    
    logger.debug(f"User authenticated: user_id={user_id}, email={user.email}")
    return user


def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
    """Authenticate a user by email and password."""
    try:
        user = db.query(User).filter(User.email == email).first()
        if not user:
            logger.debug(f"Authentication failed: User not found - {email}")
            return None
        if not verify_password(password, user.password_hash):
            logger.debug(f"Authentication failed: Invalid password - {email}")
            return None
        logger.debug(f"Authentication successful: {email}")
        return user
    except Exception as e:
        logger.error(f"Authentication error for {email}: {str(e)}", exc_info=True)
        return None

