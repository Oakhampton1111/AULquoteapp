"""Quote model."""

from datetime import datetime
from decimal import Decimal
from typing import Optional, Dict, Any, List
from sqlalchemy import Column, Integer, String, Numeric, ForeignKey, JSON, DateTime
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.ext.asyncio import AsyncAttrs
from enum import Enum, auto

from warehouse_quote_app.app.models.base import BaseModel
from warehouse_quote_app.app.models.mixins import StatusTrackingMixin

class QuoteStatus(str, Enum):
    """Quote status enum."""
    DRAFT = "draft"
    SUBMITTED = "submitted"
    UNDER_REVIEW = "under_review"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    EXPIRED = "expired"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    NEGOTIATING = "negotiating"

class Quote(AsyncAttrs, StatusTrackingMixin, BaseModel):
    """Quote model."""

    # Basic quote information
    customer_id: Mapped[int] = mapped_column(ForeignKey("customer.id"), nullable=False)
    total_amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    service_type: Mapped[str] = mapped_column(String(50), nullable=False)
    
    # Requirements and specifications
    storage_requirements: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    transport_services: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    special_requirements: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    
    # Timestamps and tracking
    submitted_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    accepted_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    rejected_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # User tracking
    created_by: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)
    accepted_by: Mapped[Optional[int]] = mapped_column(ForeignKey("user.id"), nullable=True)
    rejected_by: Mapped[Optional[int]] = mapped_column(ForeignKey("user.id"), nullable=True)
    completed_by: Mapped[Optional[int]] = mapped_column(ForeignKey("user.id"), nullable=True)
    
    # Relationships
    customer: Mapped["Customer"] = relationship(back_populates="quotes")
    creator: Mapped["User"] = relationship(foreign_keys=[created_by], back_populates="created_quotes")
    acceptor: Mapped[Optional["User"]] = relationship(foreign_keys=[accepted_by], back_populates="accepted_quotes")
    rejector: Mapped[Optional["User"]] = relationship(foreign_keys=[rejected_by], back_populates="rejected_quotes")
    completer: Mapped[Optional["User"]] = relationship(foreign_keys=[completed_by], back_populates="completed_quotes")
    items: Mapped[List["QuoteItem"]] = relationship(back_populates="quote", cascade="all, delete-orphan")
    negotiations: Mapped[List["QuoteNegotiation"]] = relationship(back_populates="quote", cascade="all, delete-orphan")
    
    async def submit(self, submitted_by: int) -> None:
        """Submit the quote."""
        self.status = "submitted"
        self.submitted_at = datetime.utcnow()
        self.created_by = submitted_by

    async def accept(self, accepted_by: int) -> None:
        """Accept the quote."""
        self.status = "accepted"
        self.accepted_at = datetime.utcnow()
        self.accepted_by = accepted_by

    async def reject(self, rejected_by: int, reason: Optional[str] = None) -> None:
        """Reject the quote."""
        self.status = "rejected"
        self.rejected_at = datetime.utcnow()
        self.rejected_by = rejected_by
        if reason:
            self.special_requirements = self.special_requirements or {}
            self.special_requirements["rejection_reason"] = reason

    async def complete(self, completed_by: int) -> None:
        """Complete the quote."""
        self.status = "completed"
        self.completed_at = datetime.utcnow()
        self.completed_by = completed_by

    async def update_storage_requirements(self, requirements: Dict[str, Any]) -> None:
        """Update storage requirements."""
        self.storage_requirements = requirements

    async def update_transport_services(self, services: Dict[str, Any]) -> None:
        """Update transport services."""
        self.transport_services = services

    async def update_special_requirements(self, requirements: Dict[str, Any]) -> None:
        """Update special requirements."""
        self.special_requirements = requirements


class QuoteItem(AsyncAttrs, BaseModel):
    """Quote item model representing individual line items in a quote."""
    
    # Foreign key to the parent quote
    quote_id: Mapped[int] = mapped_column(ForeignKey("quote.id"), nullable=False)
    
    # Item details
    service_name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    unit_price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    total_price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    
    # Additional specifications
    specifications: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    
    # Relationships
    quote: Mapped["Quote"] = relationship(back_populates="items")
    
    def __repr__(self) -> str:
        """String representation of the quote item."""
        return f"<QuoteItem(id={self.id}, service={self.service_name}, quantity={self.quantity})>"
