"""
General security utilities.
"""

import secrets
from typing import Optional
from fastapi import Request, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from passlib.context import CryptContext

from warehouse_quote_app.app.core.config import settings

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Hash a password."""
    return pwd_context.hash(password)

def generate_secure_token(length: int = 32) -> str:
    """Generate a secure random token."""
    return secrets.token_urlsafe(length)

def validate_api_key(api_key: str) -> bool:
    """Validate an API key."""
    # TODO: Implement proper API key validation
    return api_key == settings.SECRET_KEY

class CustomHTTPBearer(HTTPBearer):
    """Custom HTTP Bearer authentication."""
    
    def __call__(
        self,
        request: Request
    ) -> Optional[HTTPAuthorizationCredentials]:
        """Validate bearer token."""
        credentials = super().__call__(request)
        
        if not credentials:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid authorization credentials"
            )
        
        if not validate_api_key(credentials.credentials):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid API key"
            )
        
        return credentials

__all__ = [
    'verify_password',
    'get_password_hash',
    'generate_secure_token',
    'validate_api_key',
    'CustomHTTPBearer'
]
