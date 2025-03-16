"""User schemas."""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, ConfigDict

class UserBase(BaseModel):
    """Base user schema."""
    email: EmailStr
    first_name: str = Field(..., min_length=1)
    last_name: str = Field(..., min_length=1)
    is_active: bool = True
    is_admin: bool = False
    company_name: Optional[str] = None
    phone: Optional[str] = None

class UserCreate(UserBase):
    """User creation schema."""
    password: str = Field(..., min_length=8)
    username: Optional[str] = None

class UserUpdate(BaseModel):
    """Schema for updating an existing user."""
    email: Optional[EmailStr] = None
    first_name: Optional[str] = Field(None, min_length=1)
    last_name: Optional[str] = Field(None, min_length=1)
    password: Optional[str] = Field(None, min_length=8)
    is_active: Optional[bool] = None
    is_admin: Optional[bool] = None
    company_name: Optional[str] = None
    phone: Optional[str] = None

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True
    )

class UserResponse(UserBase):
    """User response schema."""
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True
    )

class UserBaseSimple(BaseModel):
    """Simple base user schema."""
    email: EmailStr
    is_active: bool = True
    is_admin: bool = False

class UserCreateSimple(UserBaseSimple):
    """Simple user creation schema."""
    password: str = Field(..., min_length=8)

class UserResponseSimple(UserBaseSimple):
    """Simple user response schema."""
    id: int

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True
    )

__all__ = [
    'UserBase',
    'UserCreate',
    'UserUpdate',
    'UserResponse',
    'UserBaseSimple',
    'UserCreateSimple',
    'UserResponseSimple'
]
