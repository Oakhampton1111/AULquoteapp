"""
Authentication schemas for the Warehouse Quote System.

This module defines Pydantic models for:
1. Authentication tokens
2. User data
3. User creation and updates
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field

from .user import (
    UserBase,
    UserCreate,
    UserUpdate,
    UserResponse,
    UserBaseSimple,
    UserCreateSimple,
    UserResponseSimple
)

class Token(BaseModel):
    """JWT token schema."""
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    """JWT token payload data."""
    email: Optional[str] = None
    user_id: Optional[int] = None
    is_admin: bool = False
    exp: Optional[datetime] = None

class PasswordResetRequest(BaseModel):
    """Password reset request schema."""
    email: EmailStr

class PasswordResetConfirm(BaseModel):
    """Password reset confirmation schema."""
    token: str
    new_password: str = Field(..., min_length=8)

class UserLogin(BaseModel):
    """Schema for user login credentials."""
    email: EmailStr
    password: str = Field(..., min_length=8, description="User password, minimum 8 characters")

class UserRegister(UserCreate):
    """Schema for user registration."""
    password_confirm: str = Field(..., min_length=8)

    def validate_passwords_match(self) -> None:
        """Validate that passwords match."""
        if self.password != self.password_confirm:
            raise ValueError("Passwords do not match")

__all__ = [
    'Token',
    'TokenData',
    'PasswordResetRequest',
    'PasswordResetConfirm',
    'UserLogin',
    'UserRegister',
    'UserBase',
    'UserCreate',
    'UserUpdate',
    'UserResponse',
    'UserBaseSimple',
    'UserCreateSimple',
    'UserResponseSimple'
]
