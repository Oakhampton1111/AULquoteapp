"""
Authentication dependencies for FastAPI.
"""

from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession # Changed import
# from passlib.context import CryptContext # pwd_context is defined in security.security

# Assuming get_async_db is now in deps
from warehouse_quote_app.app.api.deps import get_async_db 
from warehouse_quote_app.app.models.user import User
# from .jwt import decode_access_token # decode_access_token is used by AuthService
# AuthService will handle token verification and user fetching
from warehouse_quote_app.app.core.auth.service import AuthService 


# Password hashing utilities are in core.security.security
# pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto") # Moved or use from security.security

# The tokenUrl should point to your actual token endpoint, e.g., /api/v1/auth/login
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login") 

# get_password_hash and verify_password are in core.security.security and are synchronous.
# No need to redefine them here if they are not directly used or can be imported.

# Dependency to get AuthService instance
# This could be simplified if AuthService doesn't have dependencies itself,
# or if a more robust DI system is in place.
async def get_auth_service_dependency() -> AuthService:
    # This is a simplified way. In a real app, if AuthService has its own dependencies (like Redis client),
    # they would need to be managed here or AuthService becomes a singleton managed elsewhere.
    return AuthService()


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_async_db), # Use async session
    auth_service: AuthService = Depends(get_auth_service_dependency) # Inject AuthService
) -> User:
    """
    Get current user from token using AuthService.
    AuthService.verify_token will handle decoding, revocation check, and fetching user.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    user = await auth_service.verify_token(db=db, token=token) # verify_token is now async
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user( # No change in signature, but depends on async get_current_user
    current_user: User = Depends(get_current_user)
) -> User:
    """Get current active user."""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user

async def get_current_admin_user(
    current_user: User = Depends(get_current_active_user)
) -> User:
    """Get current admin user."""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user
