"""
Base schema configuration.

This module provides:
1. Base Pydantic models for request/response schemas
2. Common schema utilities and mixins
3. Type-safe base configurations
"""

from datetime import datetime
from typing import TypeVar, Generic, Optional, Dict, Any, Literal, Union, List, cast, Type
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator, ValidationInfo
from pydantic.generics import GenericModel

ModelType = TypeVar("ModelType")
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)

class BaseSchema(BaseModel):
    """Base class for all Pydantic schemas."""
    
    model_config = ConfigDict(
        from_attributes=True,  # Allow ORM model -> Pydantic conversion
        populate_by_name=True,  # Allow both alias and original names
        strict=True,  # Enforce strict type checking
        validate_assignment=True  # Validate on attribute assignment
    )

class BaseResponseSchema(BaseSchema):
    """Base class for all response schemas."""
    id: int = Field(..., gt=0)
    created_at: datetime
    updated_at: Optional[datetime] = None

    @field_validator('updated_at')
    def validate_updated_at(cls, v: Optional[datetime], info: ValidationInfo) -> Optional[datetime]:
        """Validate that updated_at is after created_at if present."""
        if v is not None:
            created_at = info.data.get('created_at')
            if created_at and v <= created_at:
                raise ValueError("updated_at must be after created_at")
        return v

class BaseCreateSchema(BaseSchema, Generic[ModelType]):
    """Base class for all create request schemas."""
    
    @model_validator(mode='after')
    def validate_create_data(self) -> 'BaseCreateSchema[ModelType]':
        """Custom validation for create schemas."""
        return self

class BaseUpdateSchema(BaseSchema, Generic[ModelType]):
    """Base class for all update request schemas."""
    
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        strict=True,
        validate_assignment=True,
        extra='forbid'  # Forbid extra fields in updates
    )
    
    @model_validator(mode='after')
    def validate_update_data(self) -> 'BaseUpdateSchema[ModelType]':
        """Custom validation for update schemas."""
        return self

class BaseFilterSchema(BaseSchema):
    """Base class for all filter schemas."""
    skip: int = Field(default=0, ge=0)
    limit: int = Field(default=100, ge=1, le=1000)
    order_by: Optional[str] = None
    order_direction: Optional[Literal["asc", "desc"]] = Field(
        default="asc",
        description="Sort direction"
    )

# Generic types for pagination
T = TypeVar("T", bound=BaseModel)

class PageMetadata(BaseSchema):
    """Pagination metadata."""
    total: int = Field(..., ge=0)
    skip: int = Field(..., ge=0)
    limit: int = Field(..., ge=1)
    has_more: bool

class Page(GenericModel, Generic[T]):
    """Generic pagination model."""
    items: List[T]
    metadata: PageMetadata
    
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        strict=True,
        validate_assignment=True
    )
    
    @field_validator('metadata')
    def validate_metadata(cls, v: PageMetadata, info: ValidationInfo) -> PageMetadata:
        """Validate metadata against items."""
        items = info.data.get('items', [])
        if len(items) > v.limit:
            raise ValueError("Number of items exceeds limit")
        if v.skip < 0:
            raise ValueError("Skip must be non-negative")
        if v.limit < 1:
            raise ValueError("Limit must be positive")
        return v

class ErrorDetail(BaseSchema):
    """Detailed error information."""
    code: str = Field(..., min_length=1)
    message: str = Field(..., min_length=1)
    field: Optional[str] = None
    info: Optional[Dict[str, Any]] = None

class ErrorResponse(BaseSchema):
    """Standard error response model."""
    detail: Union[str, List[ErrorDetail]] = Field(
        ...,
        description="Error details. Can be a simple string or list of detailed errors"
    )
    
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "detail": "Error message details"
                },
                {
                    "detail": [
                        {
                            "code": "VALIDATION_ERROR",
                            "message": "Invalid input",
                            "field": "email",
                            "info": {"pattern": "^[^@]+@[^@]+\\.[^@]+$"}
                        }
                    ]
                }
            ]
        }
    )

class SuccessResponse(BaseSchema):
    """Standard success response model."""
    message: str = Field(..., min_length=1)
    data: Optional[Dict[str, Any]] = None
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "message": "Operation completed successfully",
                "data": {"id": 123}
            }
        }
    )

class WebSocketMessage(BaseSchema):
    """WebSocket message schema."""
    channel: str = Field(..., description="Message channel/topic")
    event: str = Field(..., description="Event type")
    data: Dict[str, Any] = Field(default_factory=dict, description="Message payload")
    sender_id: Optional[int] = Field(None, description="ID of the message sender")
    timestamp: datetime = Field(default_factory=datetime.now, description="Message timestamp")
