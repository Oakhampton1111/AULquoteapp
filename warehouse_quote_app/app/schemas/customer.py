"""
Customer-specific schemas for the Warehouse Quote System.

This module defines Pydantic models for customer operations including:
1. Customer profile
2. Customer dashboard
3. Customer preferences
4. Customer CRUD operations
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, EmailStr, ConfigDict

from warehouse_quote_app.app.schemas.user.user import UserBase

class CustomerBase(UserBase):
    """Base customer schema."""
    company_name: Optional[str] = None
    address: Optional[str] = None
    industry: Optional[str] = None
    
class CustomerCreate(CustomerBase):
    """Customer creation schema."""
    password: str = Field(..., min_length=8)

class CustomerUpdate(BaseModel):
    """Customer update schema."""
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    company_name: Optional[str] = None
    address: Optional[str] = None
    industry: Optional[str] = None
    
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True
    )

class CustomerResponse(CustomerBase):
    """Customer response schema."""
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True
    )

class CustomerListResponse(BaseModel):
    """Customer list response schema."""
    items: List[CustomerResponse]
    total: int
    page: int
    size: int
    pages: int
    
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True
    )

class CustomerProfileResponse(CustomerResponse):
    """Customer profile response schema."""
    total_quotes: int = 0
    active_quotes: int = 0
    completed_quotes: int = 0
    total_spent: float = 0.0
    
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True
    )

class CustomerPreferenceUpdate(BaseModel):
    """Customer preference update schema."""
    notification_preferences: Optional[Dict[str, bool]] = None
    preferred_contact_method: Optional[str] = None
    special_requirements: Optional[str] = None
    
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True
    )

class CustomerDashboardResponse(BaseModel):
    """Customer dashboard response schema."""
    profile: CustomerProfileResponse
    recent_quotes: List[Dict[str, Any]] = []
    active_services: List[Dict[str, Any]] = []
    notifications: List[Dict[str, Any]] = []
    
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True
    )

__all__ = [
    'CustomerBase',
    'CustomerCreate',
    'CustomerUpdate',
    'CustomerResponse',
    'CustomerListResponse',
    'CustomerProfileResponse',
    'CustomerPreferenceUpdate',
    'CustomerDashboardResponse'
]
