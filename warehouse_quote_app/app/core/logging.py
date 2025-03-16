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
    logger.error(
        f"Error: {str(error)}",
        extra={
            "error_type": type(error).__name__,
            "error_details": str(error),
            "context": context
        }
    )

__all__ = ['get_logger', 'log_error']
