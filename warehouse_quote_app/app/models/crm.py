"""CRM-specific models and mixins."""
from datetime import datetime
from typing import Optional, List, Dict, Any
from sqlalchemy import Column, String, DateTime, Integer, ForeignKey, JSON, Float, Enum as SQLEnum
from sqlalchemy.orm import relationship, Mapped, mapped_column, declared_attr
from sqlalchemy.ext.mutable import MutableDict
import enum

from warehouse_quote_app.app.models.base import BaseModel
from warehouse_quote_app.app.models.mixins import (
    TimestampMixin,
    StatusTrackingMixin,
    SerializationMixin
)

class InteractionType(str, enum.Enum):
    """Types of customer interactions."""
    CALL = "CALL"
    EMAIL = "EMAIL"
    MEETING = "MEETING"
    NOTE = "NOTE"

class DealStage(str, enum.Enum):
    """Stages in the deal pipeline."""
    LEAD = "LEAD"
    CONTACT = "CONTACT"
    QUOTE_REQUESTED = "QUOTE_REQUESTED"
    QUOTE_SENT = "QUOTE_SENT"
    NEGOTIATION = "NEGOTIATION"
    CLOSED_WON = "CLOSED_WON"
    CLOSED_LOST = "CLOSED_LOST"

class CustomerInteraction(BaseModel, TimestampMixin, SerializationMixin):
    """Model for tracking customer interactions."""

    customer_id: Mapped[int] = mapped_column(ForeignKey("customer.id"), nullable=False)
    type: Mapped[InteractionType] = mapped_column(SQLEnum(InteractionType), nullable=False)
    description: Mapped[str] = mapped_column(String(500), nullable=False)
    agent_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)
    interaction_data: Mapped[Dict] = mapped_column(MutableDict.as_mutable(JSON), nullable=True)

    # Relationships
    customer = relationship("Customer", back_populates="interactions")
    agent = relationship("User")

class Deal(BaseModel, TimestampMixin, StatusTrackingMixin, SerializationMixin):
    """Model for tracking deals in the pipeline."""

    customer_id: Mapped[int] = mapped_column(ForeignKey("customer.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    stage: Mapped[DealStage] = mapped_column(SQLEnum(DealStage), nullable=False, default=DealStage.LEAD)
    value: Mapped[float] = mapped_column(Float, nullable=True)
    probability: Mapped[int] = mapped_column(Integer, nullable=True)
    expected_close_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    actual_close_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    deal_data: Mapped[Dict] = mapped_column(MutableDict.as_mutable(JSON), nullable=True)

    # Relationships
    customer = relationship("Customer", back_populates="deals")
    quotes = relationship("Quote", back_populates="deal")

class CRMMixin:
    """Mixin for CRM functionality."""
    lifecycle_stage: Mapped[str] = mapped_column(String(50), nullable=True)
    lead_source: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    last_contact_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    next_follow_up: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Relationships
    @declared_attr
    def interactions(cls):
        return relationship(
            "CustomerInteraction",
            back_populates="customer",
            lazy="selectin",
            cascade="all, delete-orphan"
        )
        
    @declared_attr
    def deals(cls):
        return relationship(
            "Deal",
            back_populates="customer",
            lazy="selectin",
            cascade="all, delete-orphan"
        )
    
    async def add_interaction(
        self,
        type: InteractionType,
        description: str,
        agent_id: int,
        interaction_data: Optional[Dict] = None
    ):
        """Add a new interaction for this customer."""
        interaction = CustomerInteraction(
            customer_id=self.id,
            type=type,
            description=description,
            agent_id=agent_id,
            interaction_data=interaction_data or {}
        )
        self.interactions.append(interaction)
        self.last_contact_date = datetime.utcnow()
        return interaction
    
    async def create_deal(
        self,
        title: str,
        description: Optional[str] = None,
        value: Optional[float] = None,
        probability: Optional[int] = None,
        expected_close_date: Optional[datetime] = None,
        metadata: Optional[Dict] = None
    ):
        """Create a new deal for this customer."""
        deal = Deal(
            customer_id=self.id,
            title=title,
            description=description,
            value=value,
            probability=probability,
            expected_close_date=expected_close_date,
            deal_data=metadata or {}
        )
        self.deals.append(deal)
        return deal
    
    def get_active_deals(self):
        """Get all active deals for this customer."""
        return [
            deal for deal in self.deals
            if deal.stage not in [DealStage.CLOSED_WON, DealStage.CLOSED_LOST]
        ]
    
    def get_won_deals(self):
        """Get all won deals for this customer."""
        return [
            deal for deal in self.deals
            if deal.stage == DealStage.CLOSED_WON
        ]
    
    def calculate_success_rate(self) -> float:
        """Calculate the deal success rate for this customer."""
        closed_deals = [
            deal for deal in self.deals
            if deal.stage in [DealStage.CLOSED_WON, DealStage.CLOSED_LOST]
        ]
        
        if not closed_deals:
            return 0.0
            
        won_deals = [deal for deal in closed_deals if deal.stage == DealStage.CLOSED_WON]
        return len(won_deals) / len(closed_deals) * 100.0
