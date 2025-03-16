"""Repository mixins for common database operations."""

from typing import List, Optional, Dict, Any, TypeVar, Generic, Type
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import select, func

from warehouse_quote_app.app.models.base import Base

ModelType = TypeVar("ModelType", bound=Base)

class FilterMixin(Generic[ModelType]):
    """Mixin for common filtering operations."""

    model: Type[ModelType]

    def get_by_field(
        self,
        db: Session,
        field: str,
        value: Any,
        skip: int = 0,
        limit: int = 100
    ) -> List[ModelType]:
        """Get records by field value."""
        return (
            db.query(self.model)
            .filter(getattr(self.model, field) == value)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_date_range(
        self,
        db: Session,
        date_field: str,
        start_date: datetime,
        end_date: datetime,
        skip: int = 0,
        limit: int = 100
    ) -> List[ModelType]:
        """Get records within a date range."""
        return (
            db.query(self.model)
            .filter(
                getattr(self.model, date_field) >= start_date,
                getattr(self.model, date_field) <= end_date
            )
            .offset(skip)
            .limit(limit)
            .all()
        )


class AggregationMixin(Generic[ModelType]):
    """Mixin for common aggregation operations."""

    model: Type[ModelType]

    def count_by_field(
        self,
        db: Session,
        field: str,
        value: Any
    ) -> int:
        """Count records by field value."""
        return (
            db.query(func.count())
            .filter(getattr(self.model, field) == value)
            .scalar()
        )

    def get_field_stats(
        self,
        db: Session,
        field: str
    ) -> Dict[str, Any]:
        """Get statistics for a numeric field."""
        result = (
            db.query(
                func.avg(getattr(self.model, field)).label("avg"),
                func.min(getattr(self.model, field)).label("min"),
                func.max(getattr(self.model, field)).label("max"),
                func.count(getattr(self.model, field)).label("count")
            )
            .first()
        )
        return {
            "average": float(result.avg) if result.avg else 0,
            "minimum": float(result.min) if result.min else 0,
            "maximum": float(result.max) if result.max else 0,
            "count": result.count
        }


class PaginationMixin(Generic[ModelType]):
    """Mixin for pagination operations."""

    model: Type[ModelType]

    def get_paginated(
        self,
        db: Session,
        skip: int = 0,
        limit: int = 100,
        order_by: Optional[str] = None,
        descending: bool = False
    ) -> List[ModelType]:
        """Get paginated records."""
        query = db.query(self.model)
        
        if order_by:
            order_field = getattr(self.model, order_by)
            if descending:
                order_field = order_field.desc()
            query = query.order_by(order_field)
            
        return query.offset(skip).limit(limit).all()

    def get_total_count(self, db: Session) -> int:
        """Get total count of records."""
        return db.query(func.count(self.model.id)).scalar()
