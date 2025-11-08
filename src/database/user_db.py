"""
User database models and session management.
"""
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey, Float, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from pathlib import Path
from src.utils.logger import get_logger

logger = get_logger("database")

# Database file path
DB_PATH = Path("data/users.db")
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

# SQLite database URL
DATABASE_URL = f"sqlite:///{DB_PATH}"

# Create engine
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()


class User(Base):
    """User model for authentication."""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    liked_outfits = relationship("UserLikedOutfit", back_populates="user", cascade="all, delete-orphan")
    color_results = relationship("UserColorResult", back_populates="user", cascade="all, delete-orphan")
    profile = relationship("UserProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")


class UserLikedOutfit(Base):
    """User's liked outfits - many-to-many relationship."""
    __tablename__ = "user_liked_outfits"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    item_id = Column(String, nullable=False, index=True)  # Item ID from products table (external_id)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship
    user = relationship("User", back_populates="liked_outfits")


class UserColorResult(Base):
    """User's personal color analysis results."""
    __tablename__ = "user_color_results"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    personal_color_type = Column(String, nullable=False)
    confidence = Column(Float, nullable=False)
    undertone = Column(String)
    season = Column(String)
    subtype = Column(String)
    reasoning = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationship
    user = relationship("User", back_populates="color_results")


class UserProfile(Base):
    """User profile information for clothing recommendations."""
    __tablename__ = "user_profiles"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True, index=True)
    
    # Body measurements (optional)
    height = Column(Float, nullable=True)  # in cm
    weight = Column(Float, nullable=True)  # in kg
    chest_size = Column(Float, nullable=True)  # in cm
    waist_size = Column(Float, nullable=True)  # in cm
    hip_size = Column(Float, nullable=True)  # in cm
    shoe_size = Column(Float, nullable=True)  # EU size
    clothing_size = Column(String, nullable=True)  # S, M, L, XL, etc.
    
    # Personal information (optional)
    age = Column(Integer, nullable=True)
    gender = Column(String, nullable=True)  # male, female, other
    preferred_style = Column(String, nullable=True)  # casual, formal, sporty, etc.
    
    # Images (optional) - stored as base64 encoded strings
    body_image = Column(Text, nullable=True)  # Full body photo as base64 string
    face_image = Column(Text, nullable=True)  # Face photo as base64 string
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship
    user = relationship("User", back_populates="profile")


class Product(Base):
    """Product/outfit item model for storing clothing items."""
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True, index=True)
    # Store the original ID from JSON as external_id to maintain compatibility
    external_id = Column(Integer, unique=True, index=True, nullable=False)
    
    # Product information
    description = Column(Text, nullable=True)
    price = Column(String, nullable=True)
    image_url = Column(Text, nullable=True)
    color_hex = Column(String, nullable=True)
    product_url = Column(Text, nullable=True)
    color_name = Column(String, nullable=True)
    detail_description = Column(Text, nullable=True)
    type = Column(String, nullable=True, index=True)  # Category: t-shirts, trousers, etc.
    personal_color_type = Column(String, nullable=True, index=True)  # Deep Autumn, etc.
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Popularity(Base):
    """Popularity tracking for outfit items - stores like counts."""
    __tablename__ = "popularity"
    
    id = Column(Integer, primary_key=True, index=True)
    item_id = Column(String, unique=True, index=True, nullable=False)  # Item ID (external_id from products)
    like_count = Column(Integer, default=0, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


def init_db():
    """Initialize database - create all tables."""
    try:
        logger.info(f"Initializing database at {DB_PATH}")
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {str(e)}", exc_info=True)
        raise


def get_db():
    """Dependency for getting database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

