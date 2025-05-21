"""
Authentication service for handling user authentication and authorization.
"""

from datetime import datetime, timedelta
from typing import Optional, Union # Added Union
from fastapi import Depends, HTTPException, status # Depends might be removed from __init__
from sqlalchemy.ext.asyncio import AsyncSession # Changed import
from sqlalchemy.future import select # For async queries
from jose import JWTError
import hashlib
import redis.asyncio as redis
# from fastapi.concurrency import run_in_threadpool # For sync CPU-bound tasks if needed

# Assuming these imports are relative to the app's root or adjusted for new structure
from warehouse_quote_app.app.core.config import settings
# from warehouse_quote_app.app.core.database import get_async_db # Example if using it for default injection
from warehouse_quote_app.app.models.user import User
from warehouse_quote_app.app.schemas.user.auth import Token, TokenData # Make sure Token has all needed fields
from warehouse_quote_app.app.schemas.user import UserCreate # For create_user_account
from .jwt import create_access_token, decode_access_token # These are likely sync
# get_password_hash and verify_password are CPU-bound, so they remain sync
from warehouse_quote_app.app.core.security.security import get_password_hash, verify_password 
# Import user_crud correctly, assuming it's now async
from warehouse_quote_app.app.crud import user as user_crud # user_crud is now an instance of async UserRepository


REVOCATION_PREFIX = "revoked_token:"

class AuthService:
    """Service for handling authentication and authorization with async operations."""

    # db: AsyncSession removed from __init__ as it's better to pass session per method
    # or ensure the instance of AuthService is request-scoped if db is stored.
    # For simplicity, methods will accept `db: AsyncSession`.
    def __init__(self): 
        # Consider how redis client is managed. If it's per-request, it should be passed too.
        # If it's a shared client, this is okay.
        self.redis_client = redis.from_url(settings.redis_url)

    async def authenticate_user(self, db: AsyncSession, email: str, password: str) -> Optional[User]:
        """Authenticate a user by email and password using async user_crud."""
        # user_crud.authenticate is now async
        user = await user_crud.authenticate(db, email=email, password=password)
        if not user:
            return None
        # verify_password is sync and CPU-bound, okay to call directly
        # if not verify_password(password, user.hashed_password): # This check is done in user_crud.authenticate
        #     return None
        return user

    async def create_user_account(self, db: AsyncSession, user_in: UserCreate) -> User:
        """Create a new user account. Used by SSO and potentially registration."""
        # user_crud.create is now async
        # Note: user_crud.create already handles password hashing.
        # If UserCreate for SSO has a dummy password, that's fine.
        existing_user = await user_crud.get_by_email(db, email=user_in.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="The user with this email already exists in the system.",
            )
        
        user = await user_crud.create(db, obj_in=user_in)
        return user

    async def get_login_token(self, db: AsyncSession, *, user_id: int, email: str, is_admin: bool) -> Token:
        """
        Get login token for a user.
        Accepts user_id, email, is_admin directly, useful after SSO or direct user fetching.
        """
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        token_payload = {"sub": str(user_id), "email": email, "is_admin": is_admin} # Use user_id as sub
        
        access_token_str = create_access_token( 
            data=token_payload,
            expires_delta=access_token_expires
        )
        # Assuming create_access_token returns a dict with 'access_token' and 'expires_at'
        # or just the token string. Let's assume it returns the string for now.
        
        # The Token schema needs to be compatible.
        # If create_access_token returns a dict like {"access_token": "...", "expires_at": ...}
        # then Token(**token_dict_from_create_access_token, token_type="bearer", user_id=user_id, is_admin=is_admin)
        # For now, assuming Token takes access_token string and generates others.
        
        # The schemas.Token expects access_token, token_type, user_id, is_admin, expires_at
        # create_access_token from .jwt likely just returns the string.
        # We need to construct the Token response model appropriately.
        # Let's assume create_access_token returns the token string and we calculate expiry.
        
        expires_at_dt = datetime.utcnow() + access_token_expires
        
        return Token(
            access_token=access_token_str, 
            token_type="bearer",
            user_id=user_id, # Added user_id
            is_admin=is_admin, # Added is_admin
            expires_at=expires_at_dt # Added expires_at
        )

    async def get_login_token_for_credentials(self, db: AsyncSession, email: str, password: str) -> Token:
        """Get login token for user using email and password."""
        user = await self.authenticate_user(db, email=email, password=password) # Changed from username to email
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password", # Changed from username
                headers={"WWW-Authenticate": "Bearer"},
            )
        return await self.get_login_token(db, user_id=user.id, email=user.email, is_admin=user.is_admin)


    async def change_password(self, db: AsyncSession, user: User, current_password: str, new_password: str) -> bool:
        """Change user password."""
        if not verify_password(current_password, user.hashed_password): # Sync, CPU-bound
            return False
        
        # Assuming user model has set_password or we use user_crud.update_password
        # user.hashed_password = get_password_hash(new_password) # Sync, CPU-bound
        # await db.commit() # This assumes user is already part of the session and modified.
        # More robust: use user_crud.update_password
        updated_user = await user_crud.update_password(db, user_id=user.id, new_password=new_password)
        return updated_user is not None


    async def request_password_reset(self, db: AsyncSession, email: str) -> Optional[str]:
        """Request password reset for user."""
        user = await user_crud.get_by_email(db, email=email) # Use async user_crud
        if not user:
            return None
        
        reset_token_expires = timedelta(hours=settings.PASSWORD_RESET_TOKEN_EXPIRE_HOURS) # Assume this setting exists
        reset_token = create_access_token( # Sync
            data={"sub": str(user.id), "type": "reset"}, # Use user.id as sub
            expires_delta=reset_token_expires
        )
        return reset_token

    async def reset_password(self, db: AsyncSession, token: str, new_password: str) -> bool:
        """Reset user password using reset token."""
        try:
            payload = decode_access_token(token) # Sync
            if payload.get("type") != "reset":
                return False
            
            user_id_str = payload.get("sub")
            if not user_id_str:
                return False
            
            user = await user_crud.get(db, id=int(user_id_str)) # Use async user_crud.get
            if not user:
                return False
            
            # user.hashed_password = get_password_hash(new_password) # Sync
            # await db.commit() # Use user_crud.update_password instead
            updated_user = await user_crud.update_password(db, user_id=user.id, new_password=new_password)
            return updated_user is not None
            
        except JWTError:
            return False

    async def revoke_token(self, token: str) -> bool:
        """Revoke an access token."""
        try:
            # decode_access_token is sync. If it were significantly CPU bound & called often,
            # one might use run_in_threadpool, but usually JWT decoding is fast.
            payload = decode_access_token(token) 
        except JWTError:
            return False # Token is invalid or expired, effectively revoked or unusable

        exp = payload.get("exp")
        if not exp: # Should not happen for valid access tokens
            return False

        # Calculate remaining TTL for Redis
        # Ensure exp is treated as UTC if it's a POSIX timestamp
        # datetime.fromtimestamp(exp, tz=timezone.utc) vs datetime.utcfromtimestamp(exp)
        # Assuming exp is a UNIX timestamp (seconds since epoch)
        ttl_seconds = int(exp - datetime.utcnow().timestamp()) 
        
        if ttl_seconds <= 0:
            return True # Already expired

        token_hash = hashlib.sha256(token.encode()).hexdigest()
        await self.redis_client.setex(f"{REVOCATION_PREFIX}{token_hash}", ttl_seconds, "1")
        return True

    async def is_token_revoked(self, token: str) -> bool:
        """Check if a token has been revoked."""
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        return await self.redis_client.exists(f"{REVOCATION_PREFIX}{token_hash}") > 0


    async def verify_token(self, db: AsyncSession, token: str) -> Optional[User]: # Changed to return User model
        """Verify an access token and return the user if valid and not revoked."""
        try:
            if await self.is_token_revoked(token):
                return None

            payload = decode_access_token(token) # Sync
            user_id_str = payload.get("sub")
            if not user_id_str:
                return None
            
            user = await user_crud.get(db, id=int(user_id_str)) # Fetch user
            if user and user.is_active:
                return user
            return None
        except JWTError:
            return None
