"""User model."""

from datetime import datetime
from typing import Optional, List
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.ext.asyncio import AsyncAttrs
from passlib.context import CryptContext

from warehouse_quote_app.app.models.base import BaseModel

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class User(AsyncAttrs, BaseModel):
    """User model."""
    
    __tablename__ = 'user'
    __table_args__ = {'extend_existing': True}

    # Basic user information
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    username: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    
    # User status and permissions
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    
    # Additional user information
    first_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    last_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    phone: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    
    # Account management
    last_login: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    password_changed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Relationships - Quotes
    created_quotes = relationship("Quote", foreign_keys="Quote.created_by", back_populates="creator")
    accepted_quotes = relationship("Quote", foreign_keys="Quote.accepted_by", back_populates="acceptor")
    rejected_quotes = relationship("Quote", foreign_keys="Quote.rejected_by", back_populates="rejector")
    completed_quotes = relationship("Quote", foreign_keys="Quote.completed_by", back_populates="completer")
    
    # Relationships - Rates
    created_rates = relationship("Rate", foreign_keys="Rate.created_by", back_populates="creator")
    deactivated_rates = relationship("Rate", foreign_keys="Rate.deactivated_by", back_populates="deactivator")
    
    # Relationships - Negotiations
    negotiations: Mapped[List["QuoteNegotiation"]] = relationship(back_populates="user")
    
    def set_password(self, password: str) -> None:
        """Set user password."""
        self.hashed_password = pwd_context.hash(password)
        self.password_changed_at = datetime.utcnow()

    def verify_password(self, password: str) -> bool:
        """Verify user password."""
        return pwd_context.verify(password, self.hashed_password)

    async def update_last_login(self) -> None:
        """Update last login timestamp."""
        self.last_login = datetime.utcnow()

    async def deactivate(self) -> None:
        """Deactivate user account."""
        self.is_active = False

    async def activate(self) -> None:
        """Activate user account."""
        self.is_active = True

    async def make_admin(self) -> None:
        """Make user an admin."""
        self.is_admin = True

    async def remove_admin(self) -> None:
        """Remove admin privileges."""
        self.is_admin = False

    async def update_profile(
        self,
        *,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        phone: Optional[str] = None
    ) -> None:
        """Update user profile information."""
        if first_name is not None:
            self.first_name = first_name
        if last_name is not None:
            self.last_name = last_name
        if phone is not None:
            self.phone = phone
