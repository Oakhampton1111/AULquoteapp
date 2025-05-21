"""
User repository for database operations.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession # Changed import
from sqlalchemy.future import select # Ensure this is used for new style queries
from sqlalchemy import func # Keep for things like count

from warehouse_quote_app.app.models.user import User
from warehouse_quote_app.app.schemas.user import UserCreate, UserUpdate
from warehouse_quote_app.app.repositories.base import BaseRepository

class UserRepository(BaseRepository[User, UserCreate, UserUpdate]):
    """Repository for user-related database operations."""

    async def get_by_email( # Changed to async
        self,
        db: AsyncSession, # Changed to AsyncSession
        email: str
    ) -> Optional[User]:
        """Get a user by email."""
        result = await db.execute(select(self.model).filter(self.model.email == email))
        return result.scalars().first()

    async def get_by_username( # Changed to async
        self,
        db: AsyncSession, # Changed to AsyncSession
        username: str
    ) -> Optional[User]:
        """Get a user by username."""
        result = await db.execute(select(self.model).filter(self.model.username == username))
        return result.scalars().first()

    async def get_active_users( # Changed to async
        self,
        db: AsyncSession, # Changed to AsyncSession
        skip: int = 0,
        limit: int = 100
    ) -> List[User]:
        """Get active users."""
        result = await db.execute(
            select(self.model)
            .filter(self.model.is_active == True)
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def get_admin_users( # Changed to async
        self,
        db: AsyncSession # Changed to AsyncSession
    ) -> List[User]:
        """Get admin users."""
        result = await db.execute(select(self.model).filter(self.model.is_admin == True))
        return result.scalars().all()

    async def authenticate( # Changed to async
        self,
        db: AsyncSession, # Changed to AsyncSession
        *,
        email: str,
        password: str
    ) -> Optional[User]:
        """Authenticate a user by email and password."""
        user = await self.get_by_email(db, email=email) # Await the call
        if not user:
            return None
        # verify_password is CPU bound, no await needed unless it becomes async itself (unlikely)
        if not user.verify_password(password): 
            return None
        return user

    async def create( # Changed to async
        self,
        db: AsyncSession, # Changed to AsyncSession
        *,
        obj_in: UserCreate
    ) -> User:
        """Create a new user with password hashing."""
        db_obj = User(
            email=obj_in.email,
            username=obj_in.username if obj_in.username else obj_in.email,
            first_name=obj_in.first_name,
            last_name=obj_in.last_name,
            is_active=obj_in.is_active, # Default to True from UserCreate schema if not provided
            is_admin=obj_in.is_admin,
            company_name=obj_in.company_name,
            phone=obj_in.phone
        )
        # set_password is CPU bound, no await needed
        db_obj.set_password(obj_in.password) 
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def update_password( # Changed to async
        self,
        db: AsyncSession, # Changed to AsyncSession
        *,
        user_id: int,
        new_password: str
    ) -> Optional[User]:
        """Update a user's password."""
        # Assuming self.get is also async now or needs to be called from an async context
        user = await self.get(db, id=user_id) # If self.get is from BaseRepository, it also needs to be async
        if not user:
            return None
        user.set_password(new_password) # CPU bound
        db.add(user) # Not async
        await db.commit()
        await db.refresh(user)
        return user

    # BaseRepository.get and other methods (like update, remove) would also need to be async.
    # For this task, focusing on methods directly used or easily inferred.
    # Example for BaseRepository.get:
    async def get(self, db: AsyncSession, id: Any) -> Optional[User]:
        result = await db.execute(select(self.model).filter(self.model.id == id))
        return result.scalars().first()
