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
from warehouse_quote_app.app.services.communication.email import EmailService
from sqlalchemy import func
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
        self.quotes = QuoteRepository(Quote)

    async def login(self, email: str, password: str) -> str:
        """Very basic login implementation returning a dummy token."""
        user = self.db.query(User).filter(User.email == email, User.is_admin == True).first()
        if not user or not user.verify_password(password):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
        return "dummy-token"

    async def get_metrics(self) -> AdminMetricsResponse:
        """Gather dashboard metrics from the database."""
        total_customers = self.customers.count()
        active_customers = self.db.query(Customer).filter(Customer.is_active == True).count()
        new_customers_30d = (
            self.db.query(Customer)
            .filter(Customer.created_at >= datetime.utcnow() - timedelta(days=30))
            .count()
        )

        total_quotes = self.quotes.count(self.db)
        pending_quotes = self.db.query(Quote).filter(Quote.status == "pending_approval").count()
        completed_quotes = self.db.query(Quote).filter(Quote.status == "completed").count()

        total_revenue = float(self.db.query(func.sum(Quote.total_amount)).scalar() or 0)
        revenue_30d = float(
            self.db.query(func.sum(Quote.total_amount))
            .filter(Quote.created_at >= datetime.utcnow() - timedelta(days=30))
            .scalar()
            or 0
        )

        return AdminMetricsResponse(
            total_customers=total_customers,
            active_customers=active_customers,
            new_customers_30d=new_customers_30d,
            total_quotes=total_quotes,
            pending_quotes=pending_quotes,
            completed_quotes=completed_quotes,
            total_revenue=total_revenue,
            revenue_30d=revenue_30d,
        )
    
    async def get_dashboard(self) -> Dict[str, Any]:
        """Return dashboard information including customers and quotes."""
        metrics = await self.get_metrics()
        customers = self.customers.list()
        quotes = self.quotes.get_multi(self.db, limit=100)
        pending = self.quotes.get_multi(self.db, filters={"status": "pending_approval"})

        return {
            "customers": [c.__dict__ for c in customers],
            "quotes": [q.__dict__ for q in quotes],
            "pending_approvals": [p.__dict__ for p in pending],
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
        customers = self.customers.list(skip=skip, limit=limit)
        if is_active is not None:
            customers = [c for c in customers if getattr(c, "is_active", True) == is_active]
        if search:
            customers = [c for c in customers if search.lower() in getattr(c, "company_name", "").lower()]
        return customers

    async def get_customer(self, customer_id: int) -> Optional[Customer]:
        return self.customers.get(self.db, customer_id)

    async def create_customer(self, data: Dict[str, Any]) -> Customer:
        return self.customers.create(self.db, obj_in=data)

    async def update_customer(self, customer_id: int, data: Dict[str, Any]) -> Optional[Customer]:
        db_obj = self.customers.get(self.db, customer_id)
        if not db_obj:
            return None
        return self.customers.update(self.db, db_obj=db_obj, obj_in=data)

    async def create_quote(self, data: Dict[str, Any], user_id: int) -> Quote:
        """Create a new quote for a customer."""
        quote = Quote(
            customer_id=data.get("customer_id"),
            total_amount=Decimal(str(data.get("total_amount", 0))),
            service_type=data.get("service_type", (data.get("services") or ["storage"])[0]),
            created_by=user_id,
            storage_requirements=data.get("storage_requirements"),
            transport_services=data.get("transport_services"),
            special_requirements=data.get("special_instructions"),
        )
        self.db.add(quote)
        self.db.commit()
        self.db.refresh(quote)

        email_service = EmailService()
        await email_service.send_email(
            email_to=[data.get("contact_email", "customer@example.com")],
            subject="New Quote Created",
            template_name="quote.html",
            template_data={"quote_id": quote.id},
        )

        return quote
    
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
