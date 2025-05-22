"""
Admin service for managing administrative operations.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from decimal import Decimal
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from warehouse_quote_app.app.database.db import get_db
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
from warehouse_quote_app.app.repositories.customer import CustomerRepository
from warehouse_quote_app.app.repositories.quote import QuoteRepository


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
        """Return simple metrics."""
        total_customers = self.customers.count()
        total_quotes = self.quotes.count()
        pending_quotes = self.quotes.count(filters={"status": QuoteStatus.SUBMITTED})
        return AdminMetricsResponse(
            total_customers=total_customers,
            active_customers=total_customers,
            new_customers_30d=0,
            total_quotes=total_quotes,
            pending_quotes=pending_quotes,
            completed_quotes=0,
            total_revenue=0.0,
            revenue_30d=0.0,
        )
    
    async def get_dashboard(self) -> Dict[str, Any]:
        """Return basic dashboard information."""
        metrics = await self.get_metrics()
        return {
            "customers": [],
            "quotes": [],
            "pending_approvals": [],
            "reports": {},
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
