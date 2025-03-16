"""
User repository for database operations.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import select, func

from warehouse_quote_app.app.models.user import User
from warehouse_quote_app.app.schemas.user import UserCreate, UserUpdate
from warehouse_quote_app.app.repositories.base import BaseRepository

class UserRepository(BaseRepository[User, UserCreate, UserUpdate]):
    """Repository for user-related database operations."""

    def get_by_email(
        self,
        db: Session,
        email: str
    ) -> Optional[User]:
        """Get a user by email."""
        return db.query(self.model).filter(self.model.email == email).first()

    def get_by_username(
        self,
        db: Session,
        username: str
    ) -> Optional[User]:
        """Get a user by username."""
        return db.query(self.model).filter(self.model.username == username).first()

    def get_active_users(
        self,
        db: Session,
        skip: int = 0,
        limit: int = 100
    ) -> List[User]:
        """Get active users."""
        return (
            db.query(self.model)
            .filter(self.model.is_active == True)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_admin_users(
        self,
        db: Session
    ) -> List[User]:
        """Get admin users."""
        return db.query(self.model).filter(self.model.is_admin == True).all()

    def authenticate(
        self,
        db: Session,
        *,
        email: str,
        password: str
    ) -> Optional[User]:
        """Authenticate a user by email and password."""
        user = self.get_by_email(db, email=email)
        if not user:
            return None
        if not user.verify_password(password):
            return None
        return user

    def create(
        self,
        db: Session,
        *,
        obj_in: UserCreate
    ) -> User:
        """Create a new user with password hashing."""
        db_obj = User(
            email=obj_in.email,
            username=obj_in.username if obj_in.username else obj_in.email,
            first_name=obj_in.first_name,
            last_name=obj_in.last_name,
            is_active=obj_in.is_active,
            is_admin=obj_in.is_admin,
            company_name=obj_in.company_name,
            phone=obj_in.phone
        )
        db_obj.set_password(obj_in.password)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update_password(
        self,
        db: Session,
        *,
        user_id: int,
        new_password: str
    ) -> Optional[User]:
        """Update a user's password."""
        user = self.get(db, id=user_id)
        if not user:
            return None
        user.set_password(new_password)
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
