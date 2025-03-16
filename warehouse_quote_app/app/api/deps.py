"""Dependencies for API endpoints."""
from typing import Generator
from sqlalchemy.orm import Session
from warehouse_quote_app.app.database import get_db

# Re-export get_db for backward compatibility
__all__ = ["get_db"]
