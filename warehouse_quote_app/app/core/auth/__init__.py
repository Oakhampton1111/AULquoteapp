"""
Authentication and authorization utilities.

This module provides:
1. Token creation and validation
2. Password hashing and verification
3. User authentication functions
"""

from datetime import datetime, timedelta, timezone
from typing import Optional, Union, Dict, Any, Annotated, TYPE_CHECKING, ForwardRef

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt as jose_jwt
from jose import JWTError
from passlib.context import CryptContext
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from warehouse_quote_app.app.core.config import settings
from warehouse_quote_app.app.core.dependencies import get_db_dependency
from warehouse_quote_app.app.schemas.user.auth import UserResponse

# Use forward references for User to break circular dependency
# We don't actually import the User class at module level
if TYPE_CHECKING:
    from warehouse_quote_app.app.models.user import User

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 scheme for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

class TokenData(BaseModel):
    email: Optional[str] = None

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Hash a password."""
    return pwd_context.hash(password)

def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jose_jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

async def get_current_user(
    db: AsyncSession = Depends(get_db_dependency),
    token: str = Depends(oauth2_scheme)
) -> UserResponse:
    """Get the current authenticated user."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jose_jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = TokenData(email=email)
    except JWTError:
        raise credentials_exception
    
    # Import User only when needed to avoid circular import
    from warehouse_quote_app.app.models.user import User
    user = db.query(User).filter(User.email == token_data.email).first()
    if user is None:
        raise credentials_exception
    return UserResponse.from_orm(user)

async def get_current_active_user(
    current_user: UserResponse = Depends(get_current_user)
) -> UserResponse:
    """Get the current active user."""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

async def get_current_admin_user(
    current_user: UserResponse = Depends(get_current_active_user)
) -> UserResponse:
    """Get the current admin user."""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user

async def get_current_client_user(
    db: AsyncSession = Depends(get_db_dependency),
    token: str = Depends(oauth2_scheme)
) -> UserResponse:
    """Get the current client user."""
    # TO DO: implement logic to get current client user
    pass

# Custom types for dependencies
TokenDep = Annotated[str, Depends(oauth2_scheme)]
# Use strings for the type annotations to avoid importing User directly
UserDep = Annotated[UserResponse, Depends(get_current_user)]
ActiveUserDep = Annotated[UserResponse, Depends(get_current_active_user)]
AdminUserDep = Annotated[UserResponse, Depends(get_current_admin_user)]

__all__ = [
    'verify_password',
    'get_password_hash',
    'create_access_token',
    'get_current_user',
    'get_current_active_user',
    'get_current_admin_user',
    'get_current_client_user',
    'TokenDep',
    'UserDep',
    'ActiveUserDep',
    'AdminUserDep'
]
