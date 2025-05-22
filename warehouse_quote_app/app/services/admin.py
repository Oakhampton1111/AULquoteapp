"""
Admin service for managing administrative operations.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from decimal import Decimal
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from warehouse_quote_app.app.core.config import settings
from warehouse_quote_app.app.database import get_db
from warehouse_quote_app.app.models.user import User
from warehouse_quote_app.app.models.customer import Customer
from warehouse_quote_app.app.models.quote import Quote, QuoteStatus
from warehouse_quote_app.app.schemas.admin import (
    AdminMetricsResponse,
    CustomerResponse,
    QuoteResponse,
    AdminDashboard,
    SystemStatus,
)
from warehouse_quote_app.app.schemas.reports.quote_report import QuoteReport
from warehouse_quote_app.app.schemas.reports.service_report import ServiceReport
from warehouse_quote_app.app.schemas.reports.customer_report import CustomerReport
from warehouse_quote_app.app.core.auth import get_current_admin_user
from warehouse_quote_app.app.repositories.user import UserRepository
from warehouse_quote_app.app.repositories.customer import CustomerRepository
from warehouse_quote_app.app.repositories.quote import QuoteRepository
from warehouse_quote_app.app.services.reporting_service import ReportingService
from warehouse_quote_app.app.services.crm import CRMService


class AdminService:
    """Service for admin operations."""

    def __init__(self, db: Session):
        self.db = db
        self.customers = CustomerRepository(db)
        self.quotes = QuoteRepository(db)

    async def login(self, email: str, password: str) -> str:
        """Very basic login implementation returning a dummy token."""
        user = self.db.query(User).filter(User.email == email, User.is_admin == True).first()
        if not user or not user.verify_password(password):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
        return "dummy-token"

    async def get_metrics(self) -> AdminMetricsResponse:
        """Calculate key business metrics for the admin dashboard."""

        now = datetime.utcnow()
        last_30_days = now - timedelta(days=30)

        # Customer metrics
        total_customers = self.customers.count()
        active_customers = (
            self.db.query(func.count(Customer.id))
            .filter(Customer.is_active == True)
            .scalar()
        ) or 0
        new_customers_30d = (
            self.db.query(func.count(Customer.id))
            .filter(Customer.created_at >= last_30_days)
            .scalar()
        ) or 0

        # Quote metrics
        total_quotes = self.quotes.count()
        status_counts = self.quotes.get_quote_count_by_status(self.db)
        pending_quotes = status_counts.get("submitted", 0) + status_counts.get("pending_approval", 0)
        completed_quotes = status_counts.get("completed", 0)

        # Revenue metrics
        total_revenue = (
            self.db.query(func.sum(Quote.total_amount))
            .filter(Quote.status == QuoteStatus.COMPLETED)
            .scalar()
        ) or 0.0
        revenue_30d = (
            self.db.query(func.sum(Quote.total_amount))
            .filter(Quote.status == QuoteStatus.COMPLETED, Quote.created_at >= last_30_days)
            .scalar()
        ) or 0.0

        return AdminMetricsResponse(
            total_customers=total_customers,
            active_customers=int(active_customers),
            new_customers_30d=int(new_customers_30d),
            total_quotes=total_quotes,
            pending_quotes=int(pending_quotes),
            completed_quotes=int(completed_quotes),
            total_revenue=float(total_revenue),
            revenue_30d=float(revenue_30d),
        )
    
    async def get_dashboard(self) -> Dict[str, Any]:
        """Return aggregated dashboard information for the admin UI."""

        metrics = await self.get_metrics()

        recent_customers = (
            self.db.query(Customer)
            .order_by(Customer.created_at.desc())
            .limit(5)
            .all()
        )

        recent_quotes = (
            self.db.query(Quote)
            .order_by(Quote.created_at.desc())
            .limit(5)
            .all()
        )

        pending_approvals = self.quotes.get_multi(
            self.db, filters={"status": "pending_approval"}
        )

        reporting = ReportingService(self.db)
        crm = CRMService(self.db)

        reports = {
            "quote_status": await reporting.generate_quote_status_report(),
            "revenue": await reporting.generate_revenue_report("month"),
            "pipeline": (await crm.get_pipeline_stats()).model_dump(),
        }

        return {
            "customers": recent_customers,
            "quotes": recent_quotes,
            "pending_approvals": pending_approvals,
            "reports": reports,
            "metrics": metrics.model_dump(),
        }
    
    async def list_customers(
        self,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
        is_active: Optional[bool] = None,
    ) -> List[Customer]:
        filters = {}
        if is_active is not None:
            filters["is_active"] = is_active
        return self.customers.get_multi(self.db, skip=skip, limit=limit, filters=filters)

    async def get_customer(self, customer_id: int) -> Optional[Customer]:
        return self.customers.get(self.db, customer_id)

    async def create_customer(self, data: Dict[str, Any]) -> Customer:
        return self.customers.create(self.db, obj_in=data)

    async def update_customer(self, customer_id: int, data: Dict[str, Any]) -> Optional[Customer]:
        db_obj = self.customers.get(self.db, customer_id)
        if not db_obj:
            return None
        return self.customers.update(self.db, db_obj=db_obj, obj_in=data)
    
    async def list_quotes(self, skip: int = 0, limit: int = 100, filters: Dict[str, Any] | None = None) -> List[Quote]:
        return self.quotes.get_multi(self.db, skip=skip, limit=limit, filters=filters)

    async def list_pending_quotes(self) -> List[Quote]:
        return self.quotes.get_multi(self.db, filters={"status": "pending_approval"})

    async def approve_quote(self, quote_id: int, approved_discount: float, notes: Optional[str] = None) -> Dict[str, Any]:
        quote = self.quotes.get(self.db, quote_id)
        if not quote:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Quote not found")
        if approved_discount:
            if hasattr(quote, "total_amount"):
                quote.total_amount = Decimal(str(quote.total_amount)) * (Decimal("100") - Decimal(str(approved_discount))) / Decimal("100")
        setattr(quote, "discount_status", "approved")
        self.db.add(quote)
        self.db.commit()
        return {"status": "approved"}
    
    async def generate_quote_report(self, date_range: Dict[str, datetime], filters: Dict[str, Any], fmt: str) -> QuoteReport:
        return QuoteReport(
            total_quotes=0,
            accepted_quotes=0,
            conversion_rate=0.0,
            status_counts={"PENDING": 0, "ACCEPTED": 0, "REJECTED": 0},
            start_date=date_range.get("start_date"),
            end_date=date_range.get("end_date"),
        )
    
    async def generate_service_usage_report(self, date_range: Dict[str, datetime], fmt: str) -> ServiceReport:
        return ServiceReport(
            service_usage={},
            total_quotes=0,
            start_date=date_range.get("start_date"),
            end_date=date_range.get("end_date"),
        )
    
    async def generate_customer_activity_report(self, customer_id: int, date_range: Dict[str, datetime], fmt: str) -> CustomerReport:
        return CustomerReport(
            customer_id=customer_id,
            customer_name="",
            total_quotes=0,
            total_value=0.0,
            quote_status={},
            start_date=date_range.get("start_date"),
            end_date=date_range.get("end_date"),
        )


def get_admin_service(db: Session = Depends(get_db)) -> AdminService:
    """Dependency for getting the admin service."""
    return AdminService(db)
