"""
Logging configuration for the application.
"""
import os
import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler
from datetime import datetime

# Create logs directory if it doesn't exist
LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

# Log file path
LOG_FILE = LOG_DIR / f"app_{datetime.now().strftime('%Y%m%d')}.log"

# Log format
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# Detailed format for file logging
DETAILED_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(funcName)s() - %(message)s"


def setup_logger(name: str = "hackseoul", level: str = "INFO") -> logging.Logger:
    """
    Set up a logger with both console and file handlers.
    
    Args:
        name: Logger name
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    
    # Don't add handlers if they already exist
    if logger.handlers:
        return logger
    
    # Set log level
    log_level = getattr(logging, level.upper(), logging.INFO)
    logger.setLevel(log_level)
    
    # Console handler (stdout)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_formatter = logging.Formatter(LOG_FORMAT, DATE_FORMAT)
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    # File handler with rotation
    file_handler = RotatingFileHandler(
        LOG_FILE,
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5,
        encoding="utf-8"
    )
    file_handler.setLevel(log_level)
    file_formatter = logging.Formatter(DETAILED_FORMAT, DATE_FORMAT)
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)
    
    # Prevent propagation to root logger
    logger.propagate = False
    
    return logger


def get_logger(name: str = None) -> logging.Logger:
    """
    Get a logger instance. If name is provided, returns a child logger.
    
    Args:
        name: Optional logger name (e.g., 'api.auth', 'database', etc.)
    
    Returns:
        Logger instance
    """
    if name:
        return logging.getLogger(f"hackseoul.{name}")
    return logging.getLogger("hackseoul")


# Initialize root logger
root_logger = setup_logger("hackseoul", os.getenv("LOG_LEVEL", "INFO"))

