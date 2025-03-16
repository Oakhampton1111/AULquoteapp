"""Customer model."""
from datetime import datetime
from typing import Optional, List
from sqlalchemy.orm import relationship, declared_attr
from sqlalchemy.ext.asyncio import AsyncAttrs

from warehouse_quote_app.app.models.base import BaseModel
from warehouse_quote_app.app.models.mixins import (
    TrackingMixin,
    PreferencesMixin,
    ContactInfoMixin,
    MetricsMixin
)
from warehouse_quote_app.app.models.crm import CRMMixin

# Test change for file watcher - 2025-02-25
# Test change for file watcher - 2025-02-25 18:06
# Test change for file watcher - 2025-02-25 18:08
# Test change for file watcher - 2025-02-25 18:09
# Test change for file watcher - 2025-02-25 18:23
class Customer(AsyncAttrs, BaseModel, ContactInfoMixin, PreferencesMixin, TrackingMixin, MetricsMixin, CRMMixin):
    """Customer model with comprehensive tracking of quotes, preferences, and CRM data."""

    # Relationships from base Customer
    @declared_attr
    def quotes(cls):
        return relationship("Quote", back_populates="customer", lazy="selectin")
        
    @declared_attr
    def recent_quotes(cls):
        return relationship(
            "Quote",
            back_populates="customer",
            lazy="selectin",
            order_by="desc(Quote.created_at)",
            primaryjoin="and_(Customer.id==Quote.customer_id, Quote.created_at>=func.now()-interval('30 days'))"
        )

    async def update_metrics(self) -> None:
        """Update customer metrics based on quotes and deals."""
        # Update quote metrics
        await super().update_metrics(self.quotes)
        
        # Update CRM metrics
        if self.deals:
            self.total_deal_value = sum(deal.value or 0 for deal in self.deals)
            self.active_deals = len(self.get_active_deals())
            self.success_rate = self.calculate_success_rate()

    async def deactivate(self) -> None:
        """Deactivate the customer."""
        self.is_active = False
        # Cancel any active deals
        for deal in self.get_active_deals():
            deal.stage = "CLOSED_LOST"
            deal.actual_close_date = datetime.utcnow()

    async def activate(self) -> None:
        """Activate the customer."""
        self.is_active = True

    async def update_preferences(
        self,
        *,
        contact_method: Optional[str] = None,
        notifications: Optional[str] = None,
        requirements: Optional[str] = None
    ) -> None:
        """Update customer preferences."""
        if contact_method is not None:
            self.preferred_contact_method = contact_method
        if notifications is not None:
            self.notification_preferences = notifications
        if requirements is not None:
            self.special_requirements = requirements
