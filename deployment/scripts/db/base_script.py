"""Base script for database operations."""
import sys
from pathlib import Path
from typing import List, Type, Optional
from sqlalchemy.orm import Session

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

from warehouse_quote_app.database import SessionLocal, engine
from warehouse_quote_app.models.base import BaseModel

class DatabaseScript:
    """Base class for database scripts."""

    def __init__(self, models: Optional[List[Type[BaseModel]]] = None):
        """Initialize script with models to create."""
        self.models = models or []
        self.db: Optional[Session] = None

    def __enter__(self) -> Session:
        """Create tables and return session."""
        # Create tables for specified models
        for model in self.models:
            model.metadata.create_all(bind=engine)
        
        # Create and return session
        self.db = SessionLocal()
        return self.db

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Close session."""
        if self.db:
            if exc_type:
                self.db.rollback()
            else:
                self.db.commit()
            self.db.close()

    @staticmethod
    def add_and_flush(db: Session, *objects: BaseModel) -> None:
        """Add objects to session and flush."""
        for obj in objects:
            db.add(obj)
        db.flush()

    @staticmethod
    def bulk_save(db: Session, objects: List[BaseModel]) -> None:
        """Bulk save objects to database."""
        db.bulk_save_objects(objects)
        db.flush()
