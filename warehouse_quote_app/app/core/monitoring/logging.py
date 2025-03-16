"""
Logging configuration and utilities.
"""

import logging
import sys
from typing import Dict, Any
from pathlib import Path

from warehouse_quote_app.app.core.config import settings

# Configure logging format
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format=settings.LOG_FORMAT,
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("app.log")
    ]
)

def get_logger(name: str) -> logging.Logger:
    """Get a logger instance."""
    return logging.getLogger(name)

def log_error(
    logger: logging.Logger,
    error: Exception,
    context: Dict[str, Any]
) -> None:
    """Log an error with context."""
    error_type = type(error).__name__
    error_message = str(error)
    
    logger.error(
        f"Error: {error_type} - {error_message}",
        extra={
            "error_type": error_type,
            "error_message": error_message,
            **context
        }
    )

__all__ = ['get_logger', 'log_error']
