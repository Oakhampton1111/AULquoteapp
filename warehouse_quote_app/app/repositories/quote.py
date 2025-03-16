"""
Quote repository for database operations.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import select, func

from warehouse_quote_app.app.models.quote import Quote
from warehouse_quote_app.app.schemas.quote import QuoteCreate, QuoteUpdate
from warehouse_quote_app.app.repositories.base import BaseRepository
from warehouse_quote_app.app.repositories.mixins import FilterMixin, AggregationMixin, PaginationMixin

class QuoteRepository(
    BaseRepository[Quote, QuoteCreate, QuoteUpdate],
    FilterMixin[Quote],
    AggregationMixin[Quote],
    PaginationMixin[Quote]
):
    """Repository for quote-related database operations."""

    def get_quotes_by_customer(
        self,
        db: Session,
        customer_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[Quote]:
        """Get quotes for a specific customer."""
        return self.get_by_field(db, "customer_id", customer_id, skip, limit)

    def get_quotes_by_status(
        self,
        db: Session,
        status: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[Quote]:
        """Get quotes by status."""
        return self.get_by_field(db, "status", status, skip, limit)

    def get_quotes_by_date_range(
        self,
        db: Session,
        start_date: datetime,
        end_date: datetime,
        skip: int = 0,
        limit: int = 100
    ) -> List[Quote]:
        """Get quotes within a date range."""
        return self.get_by_date_range(db, "created_at", start_date, end_date, skip, limit)

    def get_total_quote_value(
        self,
        db: Session,
        customer_id: Optional[int] = None
    ) -> float:
        """Get total value of all quotes, optionally filtered by customer."""
        query = select(func.sum(self.model.total_amount))
        
        if customer_id:
            query = query.where(self.model.customer_id == customer_id)
            
        return db.scalar(query) or 0.0

    def get_quote_count_by_status(
        self,
        db: Session
    ) -> Dict[str, int]:
        """Get count of quotes grouped by status."""
        result = (
            db.query(
                self.model.status,
                func.count(self.model.id)
            )
            .group_by(self.model.status)
            .all()
        )
        
        return {status: count for status, count in result}

    def get_quote_stats_by_customer(
        self,
        db: Session,
        customer_id: int
    ) -> dict:
        """Get quote statistics for a customer."""
        return {
            "total_quotes": self.count_by_field(db, "customer_id", customer_id),
            "total_amount_stats": self.get_field_stats(db, "total_amount")
        }
