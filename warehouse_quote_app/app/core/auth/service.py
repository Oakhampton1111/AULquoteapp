"""
Authentication service for handling user authentication and authorization.
"""

from datetime import datetime, timedelta
from typing import Optional
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from jose import JWTError
import hashlib
import redis.asyncio as redis
from fastapi.concurrency import run_in_threadpool

REVOCATION_PREFIX = "revoked_token:"

from app.core.config import settings
from app.core.database import get_db
from app.models.user import User
from app.schemas.user.auth import Token, TokenData
from .jwt import create_access_token, decode_access_token
from .dependencies import get_password_hash, verify_password

class AuthService:
    """Service for handling authentication and authorization."""

    def __init__(self, db: Session = Depends(get_db)):
        self.db = db
        self.redis = redis.from_url(settings.redis_url)

    async def _run(self, func, *args, **kwargs):
        """Run blocking database operations in a thread pool."""
        return await run_in_threadpool(func, *args, **kwargs)

    async def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """Authenticate a user by username and password."""
        user = await self._run(
            lambda: self.db.query(User).filter(User.username == username).first()
        )
        if not user or not verify_password(password, user.hashed_password):
            return None
        return user

    async def create_user(self, username: str, email: str, password: str, is_admin: bool = False) -> User:
        """Create a new user."""
        hashed_password = get_password_hash(password)
        user = User(
            username=username,
            email=email,
            hashed_password=hashed_password,
            is_admin=is_admin
        )
        await self._run(self.db.add, user)
        await self._run(self.db.commit)
        await self._run(self.db.refresh, user)
        return user

    async def get_login_token(self, username: str, password: str) -> Token:
        """Get login token for user."""
        user = await self.authenticate_user(username, password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.username, "is_admin": user.is_admin},
            expires_delta=access_token_expires
        )
        return Token(access_token=access_token, token_type="bearer")

    async def change_password(self, user: User, current_password: str, new_password: str) -> bool:
        """Change user password."""
        if not verify_password(current_password, user.hashed_password):
            return False

        user.hashed_password = get_password_hash(new_password)
        await self._run(self.db.commit)
        return True

    async def request_password_reset(self, email: str) -> Optional[str]:
        """Request password reset for user."""
        user = await self._run(
            lambda: self.db.query(User).filter(User.email == email).first()
        )
        if not user:
            return None
        
        # Generate reset token valid for 1 hour
        reset_token = create_access_token(
            data={"sub": user.username, "type": "reset"},
            expires_delta=timedelta(hours=1)
        )
        return reset_token

    async def reset_password(self, token: str, new_password: str) -> bool:
        """Reset user password using reset token."""
        try:
            payload = decode_access_token(token)
            if payload.get("type") != "reset":
                return False

            username = payload.get("sub")
            if not username:
                return False

            user = await self._run(
                lambda: self.db.query(User).filter(User.username == username).first()
            )
            if not user:
                return False

            user.hashed_password = get_password_hash(new_password)
            await self._run(self.db.commit)
            return True
            
        except JWTError:
            return False

    async def revoke_token(self, token: str) -> bool:
        """Revoke an access token."""
        try:
            payload = decode_access_token(token)
        except JWTError:
            return False

        exp = payload.get("exp")
        if not exp:
            return False

        ttl = exp - int(datetime.utcnow().timestamp())
        if ttl <= 0:
            return False

        token_hash = hashlib.sha256(token.encode()).hexdigest()
        await self.redis.setex(f"{REVOCATION_PREFIX}{token_hash}", ttl, "1")
        return True

    async def verify_token(self, token: str) -> Optional[TokenData]:
        """Verify an access token."""
        try:
            try:
                token_hash = hashlib.sha256(token.encode()).hexdigest()
                # Check if the token is in the Redis blacklist
                if await self.redis.get(f"{REVOCATION_PREFIX}{token_hash}"):
                    return None # Token is revoked
            except redis.RedisError as e:
                # logger.error(f"Redis error during token verification for {token_hash}: {e}") # Consider logging
                # Fail-closed: If Redis is inaccessible, we cannot confirm the token is NOT revoked.
                return None 


            payload = decode_access_token(token)
            username = payload.get("sub")
            if not username:
                return None
            return TokenData(username=username, is_admin=payload.get("is_admin", False))
        except JWTError:
            return None
