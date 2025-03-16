"""
User-related schemas.
"""

from .user import (
    UserBase,
    UserCreate,
    UserUpdate,
    UserResponse,
    UserBaseSimple,
    UserCreateSimple,
    UserResponseSimple
)

from .auth import (
    Token,
    TokenData,
    UserLogin,
    UserRegister,
    PasswordResetRequest,
    PasswordResetConfirm
)

# Re-export UserResponse as User to match the expected import
User = UserResponse

__all__ = [
    # Base user schemas
    'User',  # Alias for UserResponse
    'UserBase',
    'UserCreate',
    'UserUpdate',
    'UserResponse',
    'UserBaseSimple',
    'UserCreateSimple',
    'UserResponseSimple',
    
    # Auth schemas
    'Token',
    'TokenData',
    'UserLogin',
    'UserRegister',
    'PasswordResetRequest',
    'PasswordResetConfirm'
]
