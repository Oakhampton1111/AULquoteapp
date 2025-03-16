"""
Client authentication utilities.
"""

from typing import Optional
from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from warehouse_quote_app.app.core.auth.jwt import get_token_payload
from warehouse_quote_app.app.database import get_db
from warehouse_quote_app.app.models.user import User
from warehouse_quote_app.app.repositories.user import UserRepository
from warehouse_quote_app.app.core.auth import oauth2_scheme

async def get_current_client_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> User:
    """
    Get the current authenticated client user.
    
    Args:
        token: JWT token from authorization header
        db: Database session
        
    Returns:
        User: The authenticated client user
        
    Raises:
        HTTPException: If authentication fails or user is not a client
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    # Decode the token
    payload = get_token_payload(token)
    if payload is None:
        raise credentials_exception
    
    # Extract user ID from token
    user_id: Optional[int] = payload.get("user_id")
    if user_id is None:
        raise credentials_exception
    
    # Get user from database
    user_repo = UserRepository(db)
    user = await user_repo.get(user_id)
    if user is None:
        raise credentials_exception
    
    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )
    
    # Check if user is a client (not an admin)
    if user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin users cannot access client endpoints"
        )
    
    return user

__all__ = [
    'get_current_client_user'
]
