"""Rate model."""

from datetime import datetime
from decimal import Decimal
from typing import Optional, Dict, Any, List
from sqlalchemy import Column, Integer, String, Numeric, JSON, ForeignKey, DateTime
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.ext.asyncio import AsyncAttrs

from warehouse_quote_app.app.models.base import BaseModel
from warehouse_quote_app.app.models.mixins import ValidityMixin, OptimizationMixin

class Rate(AsyncAttrs, ValidityMixin, OptimizationMixin, BaseModel):
    """Rate model."""

    # Basic rate information
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(String(500), nullable=False)
    base_rate: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    service_type: Mapped[str] = mapped_column(String(50), nullable=False)
    category: Mapped[str] = mapped_column(String(50), nullable=False)
    
    # Additional specifications
    conditions: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    discounts: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    surcharges: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    
    # Versioning
    parent_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("rate.id"), nullable=True)
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    
    # User tracking
    created_by: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)
    deactivated_by: Mapped[Optional[int]] = mapped_column(ForeignKey("user.id"), nullable=True)
    deactivated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Relationships
    creator: Mapped["User"] = relationship(foreign_keys=[created_by], back_populates="created_rates")
    deactivator: Mapped[Optional["User"]] = relationship(foreign_keys=[deactivated_by], back_populates="deactivated_rates")
    parent: Mapped[Optional["Rate"]] = relationship("Rate", remote_side=[id], back_populates="versions")
    versions: Mapped[list["Rate"]] = relationship("Rate", back_populates="parent", remote_side=[parent_id])
    
    async def deactivate(self, deactivated_by: int) -> None:
        """Deactivate the rate."""
        self.is_active = False
        self.deactivated_at = datetime.utcnow()
        self.deactivated_by = deactivated_by

    async def create_new_version(self, updates: Dict[str, Any], created_by: int) -> "Rate":
        """Create a new version of this rate."""
        new_version = Rate(
            parent_id=self.id,
            version=self.version + 1,
            created_by=created_by,
            name=updates.get("name", self.name),
            description=updates.get("description", self.description),
            base_rate=updates.get("base_rate", self.base_rate),
            service_type=updates.get("service_type", self.service_type),
            category=updates.get("category", self.category),
            valid_from=updates.get("valid_from", self.valid_from),
            valid_until=updates.get("valid_until", self.valid_until),
            conditions=updates.get("conditions", self.conditions),
            discounts=updates.get("discounts", self.discounts),
            surcharges=updates.get("surcharges", self.surcharges)
        )
        return new_version

    async def update_conditions(self, conditions: Dict[str, Any]) -> None:
        """Update rate conditions."""
        self.conditions = conditions

    async def update_discounts(self, discounts: Dict[str, Any]) -> None:
        """Update rate discounts."""
        self.discounts = discounts

    async def update_surcharges(self, surcharges: Dict[str, Any]) -> None:
        """Update rate surcharges."""
        self.surcharges = surcharges

    async def add_optimization_history(self, optimization_data: Dict[str, Any]) -> None:
        """Add a new optimization record to history."""
        if not self.optimization_history:
            self.optimization_history = []
        self.optimization_history.append({
            **optimization_data,
            "timestamp": datetime.utcnow().isoformat()
        })
        self.last_optimized_at = datetime.utcnow()

    async def update_market_analysis(self, analysis_data: Dict[str, Any]) -> None:
        """Update market analysis data."""
        self.market_analysis = {
            **analysis_data,
            "updated_at": datetime.utcnow().isoformat()
        }

    async def add_validation_rule(self, rule: Dict[str, Any]) -> None:
        """Add a new validation rule."""
        if not self.validation_rules:
            self.validation_rules = []
        self.validation_rules.append({
            **rule,
            "created_at": datetime.utcnow().isoformat()
        })

    async def get_active_validation_rules(self) -> List[Dict[str, Any]]:
        """Get all active validation rules."""
        if not self.validation_rules:
            return []
        return [rule for rule in self.validation_rules if rule.get("is_active", True)]

    async def get_latest_optimization(self) -> Optional[Dict[str, Any]]:
        """Get the most recent optimization record."""
        if not self.optimization_history:
            return None
        return self.optimization_history[-1]
