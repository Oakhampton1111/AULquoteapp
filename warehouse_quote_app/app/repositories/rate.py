"""
Rate repository for database operations.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import select, func

from warehouse_quote_app.app.models.rate import Rate
from warehouse_quote_app.app.schemas.rate import RateCreate, RateUpdate
from warehouse_quote_app.app.repositories.base import BaseRepository

class RateRepository(BaseRepository[Rate, RateCreate, RateUpdate]):
    """Repository for rate-related database operations."""

    def get_active_rates(
        self,
        db: Session,
        category: Optional[str] = None
    ) -> List[Rate]:
        """Get active rates, optionally filtered by category."""
        query = db.query(self.model).filter(self.model.is_active == True)
        
        if category:
            query = query.filter(self.model.category == category)
            
        return query.all()

    def get_rates_by_date_range(
        self,
        db: Session,
        start_date: datetime,
        end_date: datetime
    ) -> List[Rate]:
        """Get rates valid within a date range."""
        return (
            db.query(self.model)
            .filter(self.model.valid_from <= end_date)
            .filter(self.model.valid_until >= start_date)
            .all()
        )

    def get_rate_history(
        self,
        db: Session,
        rate_id: int
    ) -> List[Rate]:
        """Get historical versions of a rate."""
        return (
            db.query(self.model)
            .filter(self.model.parent_id == rate_id)
            .order_by(self.model.valid_from.desc())
            .all()
        )

    def get_rates_by_service(
        self,
        db: Session,
        service_type: str
    ) -> List[Rate]:
        """Get rates for a specific service type."""
        return (
            db.query(self.model)
            .filter(self.model.service_type == service_type)
            .filter(self.model.is_active == True)
            .all()
        )

    def get_rate_statistics(
        self,
        db: Session
    ) -> Dict[str, Any]:
        """Get statistics about rates."""
        total_rates = db.scalar(
            select(func.count())
            .select_from(self.model)
        )
        
        active_rates = db.scalar(
            select(func.count())
            .select_from(self.model)
            .where(self.model.is_active == True)
        )
        
        rates_by_category = (
            db.query(
                self.model.category,
                func.count(self.model.id)
            )
            .group_by(self.model.category)
            .all()
        )
        
        return {
            "total_rates": total_rates,
            "active_rates": active_rates,
            "rates_by_category": dict(rates_by_category)
        }
