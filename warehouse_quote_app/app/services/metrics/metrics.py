"""
Service for collecting and managing application metrics.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func
from prometheus_client import Counter, Histogram, Gauge

from warehouse_quote_app.app.models.quote import Quote
from warehouse_quote_app.app.models.rate import Rate
from warehouse_quote_app.app.models.user import User
from warehouse_quote_app.app.core.monitoring import log_event

class MetricsService:
    """Service for collecting and managing application metrics."""

    def __init__(self):
        """Initialize metrics collectors."""
        # Prometheus metrics
        self.quote_counter = Counter(
            'quotes_total',
            'Total number of quotes generated',
            ['status']
        )
        self.quote_amount = Histogram(
            'quote_amount_dollars',
            'Distribution of quote amounts',
            buckets=[100, 500, 1000, 5000, 10000, 50000]
        )
        self.active_users = Gauge(
            'active_users',
            'Number of active users'
        )

    async def collect_quote_metrics(
        self,
        db: Session,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Collect quote-related metrics."""
        if not start_date:
            start_date = datetime.utcnow() - timedelta(days=30)
        if not end_date:
            end_date = datetime.utcnow()

        # Query metrics
        total_quotes = db.query(func.count(Quote.id)).scalar()
        avg_quote_amount = db.query(func.avg(Quote.total_amount)).scalar()
        quotes_by_status = (
            db.query(Quote.status, func.count(Quote.id))
            .group_by(Quote.status)
            .all()
        )
        
        # Update Prometheus metrics
        for status, count in quotes_by_status:
            self.quote_counter.labels(status=status).inc(count)
        
        metrics = {
            "total_quotes": total_quotes,
            "average_quote_amount": float(avg_quote_amount) if avg_quote_amount else 0,
            "quotes_by_status": dict(quotes_by_status),
            "period": {
                "start": start_date,
                "end": end_date
            }
        }
        
        log_event(
            db=db,
            event_type="metrics_collected",
            user_id=None,
            resource_type="metrics",
            resource_id="quotes",
            details=metrics
        )
        
        return metrics

    async def collect_rate_metrics(
        self,
        db: Session
    ) -> Dict[str, Any]:
        """Collect rate-related metrics."""
        total_rates = db.query(func.count(Rate.id)).scalar()
        active_rates = (
            db.query(func.count(Rate.id))
            .filter(Rate.is_active == True)
            .scalar()
        )
        rates_by_category = (
            db.query(Rate.category, func.count(Rate.id))
            .group_by(Rate.category)
            .all()
        )
        
        metrics = {
            "total_rates": total_rates,
            "active_rates": active_rates,
            "rates_by_category": dict(rates_by_category)
        }
        
        log_event(
            db=db,
            event_type="metrics_collected",
            user_id=None,
            resource_type="metrics",
            resource_id="rates",
            details=metrics
        )
        
        return metrics

    async def collect_user_metrics(
        self,
        db: Session,
        days: int = 30
    ) -> Dict[str, Any]:
        """Collect user-related metrics."""
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        total_users = db.query(func.count(User.id)).scalar()
        active_users = (
            db.query(func.count(User.id))
            .filter(User.last_login >= cutoff_date)
            .scalar()
        )
        users_by_role = (
            db.query(User.role, func.count(User.id))
            .group_by(User.role)
            .all()
        )
        
        # Update Prometheus metrics
        self.active_users.set(active_users)
        
        metrics = {
            "total_users": total_users,
            "active_users": active_users,
            "users_by_role": dict(users_by_role),
            "period_days": days
        }
        
        log_event(
            db=db,
            event_type="metrics_collected",
            user_id=None,
            resource_type="metrics",
            resource_id="users",
            details=metrics
        )
        
        return metrics

    async def get_system_health(
        self,
        db: Session
    ) -> Dict[str, Any]:
        """Get overall system health metrics."""
        # Collect all metrics
        quote_metrics = await self.collect_quote_metrics(db)
        rate_metrics = await self.collect_rate_metrics(db)
        user_metrics = await self.collect_user_metrics(db)
        
        return {
            "quotes": quote_metrics,
            "rates": rate_metrics,
            "users": user_metrics,
            "timestamp": datetime.utcnow()
        }

    async def get_quote_metrics(
        self,
        db: Session,
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Any]:
        """Get quote-related metrics for a date range."""
        return {
            "average_quote_value": await self.calculate_average_quote_value(db),
            "total_handling_fees": await self.calculate_total_handling_fees(db),
            "quote_acceptance_rate": await self.calculate_quote_acceptance_rate(db),
            "total_quotes": await self.get_number_of_quotes_created(db),
            "accepted_quotes": await self.get_number_of_quotes_accepted(db),
            "total_revenue": await self.get_total_revenue(db)
        }

    async def calculate_average_quote_value(self, db: Session) -> float:
        """Calculates the average quote value."""
        total_revenue = await self.get_total_revenue(db)
        number_of_quotes_accepted = await self.get_number_of_quotes_accepted(db)
        if number_of_quotes_accepted == 0:
            return 0
        return total_revenue / number_of_quotes_accepted

    async def calculate_total_handling_fees(self, db: Session) -> float:
        """Calculates the total handling fees from accepted quotes."""
        return await self.get_total_handling_fees(db)

    async def calculate_quote_acceptance_rate(self, db: Session) -> float:
        """Calculates the quote acceptance rate."""
        number_of_quotes_accepted = await self.get_number_of_quotes_accepted(db)
        number_of_quotes_created = await self.get_number_of_quotes_created(db)
        if number_of_quotes_created == 0:
            return 0
        return number_of_quotes_accepted / number_of_quotes_created

    async def get_total_revenue(self, db: Session) -> float:
        """Get total revenue from accepted quotes."""
        return await self._get_total_revenue(db)

    async def get_number_of_quotes_accepted(self, db: Session) -> int:
        """Get number of accepted quotes."""
        return await self._get_number_of_quotes_accepted(db)

    async def get_number_of_quotes_created(self, db: Session) -> int:
        """Get total number of quotes created."""
        return await self._get_number_of_quotes_created(db)

    async def _get_total_revenue(self, db: Session) -> float:
        """Get total revenue from accepted quotes."""
        return db.query(func.sum(Quote.total_amount)).filter(Quote.status == "accepted").scalar()

    async def _get_total_handling_fees(self, db: Session) -> float:
        """Get total handling fees from accepted quotes."""
        return db.query(func.sum(Quote.handling_fee)).filter(Quote.status == "accepted").scalar()

    async def _get_number_of_quotes_accepted(self, db: Session) -> int:
        """Get number of accepted quotes."""
        return db.query(func.count(Quote.id)).filter(Quote.status == "accepted").scalar()

    async def _get_number_of_quotes_created(self, db: Session) -> int:
        """Get total number of quotes created."""
        return db.query(func.count(Quote.id)).scalar()

    async def log_metrics(
        self,
        db: Session,
        metrics: Dict[str, Any],
        user_id: int
    ) -> None:
        """Log metrics collection event."""
        log_event(
            db=db,
            event_type="metrics_collected",
            user_id=user_id,
            resource_type="metrics",
            resource_id="quote_metrics",
            details=metrics
        )
