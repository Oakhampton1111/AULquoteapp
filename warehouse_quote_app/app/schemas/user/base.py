from datetime import datetime
from typing import Optional, Generic, TypeVar
from pydantic import BaseModel, Field, ConfigDict

T = TypeVar('T')

class BaseSchema(BaseModel):
    """Base schema class with common configuration"""
    id: int = Field(..., description="Unique identifier")
    created_at: datetime = Field(default_factory=datetime.now, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.now, description="Last update timestamp")
    model_config = ConfigDict(from_attributes=True)

class BaseResponseSchema(BaseSchema):
    """Base schema for all response models."""
    pass

class BaseCreateSchema(BaseSchema, Generic[T]):
    """Base schema for all creation models."""
    pass

class BaseUpdateSchema(BaseSchema, Generic[T]):
    """Base schema for all update models."""
    updated_at: datetime = Field(default_factory=datetime.now, description="Update timestamp")

    class Config:
        from_attributes = True
