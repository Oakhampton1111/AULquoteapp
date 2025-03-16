"""Base model for all database models."""

from datetime import datetime
from sqlalchemy import Column, DateTime, Integer
from sqlalchemy.ext.declarative import declared_attr

# Import Base class directly to avoid circular imports
from warehouse_quote_app.app.database.session import Base


class BaseModel(Base):
    """Base model for all database models."""

    __abstract__ = True
    __table_args__ = {'extend_existing': True}

    @declared_attr
    def __tablename__(cls):
        """Return table name based on class name."""
        return cls.__name__.lower()

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)