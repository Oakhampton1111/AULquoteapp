"""Customer schemas."""
from typing import Optional, List, TYPE_CHECKING
from datetime import datetime
from pydantic import EmailStr, Field

if TYPE_CHECKING:
    from .quote import QuoteDetailResponse

from .base import BaseSchema, BaseResponseSchema, BaseCreateSchema, BaseUpdateSchema

class CustomerBase(BaseSchema):
    """Base schema for customer data."""
    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    phone: str = Field(..., min_length=8, max_length=20)
    address: str = Field(..., min_length=5, max_length=200)
    company_name: Optional[str] = Field(None, max_length=100)
    notes: Optional[str] = None

class CustomerCreate(BaseCreateSchema[CustomerBase], CustomerBase):
    """Schema for creating a new customer."""
    pass

class CustomerUpdate(BaseUpdateSchema[CustomerBase], CustomerBase):
    """Schema for updating an existing customer."""
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, min_length=8, max_length=20)
    address: Optional[str] = Field(None, min_length=5, max_length=200)

class CustomerResponse(BaseResponseSchema, CustomerBase):
    """Schema for customer response."""
    quotes: Optional[List['QuoteDetailResponse']] = []
    accepted_quotes: int = Field(ge=0, description="Number of accepted quotes")
    rejected_quotes: int = Field(ge=0, description="Number of rejected quotes")
    total_spent: float = Field(ge=0, description="Total amount spent")
    recent_quotes: List['QuoteDetailResponse'] = Field(
        default_factory=list,
        description="List of recent quotes"
    )

    class Config:
        """Pydantic config."""
        from_attributes = True
