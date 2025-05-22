"""Admin endpoints."""
from datetime import datetime
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, Query, Path, HTTPException, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session

from warehouse_quote_app.app.core.auth import get_current_admin_user
from warehouse_quote_app.app.database import get_db
from warehouse_quote_app.app.models.user import User
from warehouse_quote_app.app.schemas.quote import QuoteStatus
from warehouse_quote_app.app.schemas.admin import (
    AdminDashboard,
    SystemStatus,
    UserManagement,
    AuditLog,
    AdminMetricsResponse,
    CustomerResponse,
    RateCardResponse,
    RateCardCreate,
    RateCardUpdate,
    QuoteResponse,
    QuoteGenerateRequest
)
from warehouse_quote_app.app.schemas.rate.rate import RateCreate, RateUpdate
from warehouse_quote_app.app.schemas.reports.quote_report import QuoteReport
from warehouse_quote_app.app.schemas.reports.service_report import ServiceReport
from warehouse_quote_app.app.schemas.reports.customer_report import CustomerReport
from warehouse_quote_app.app.services.admin import get_admin_service, AdminService
from warehouse_quote_app.app.services.rate_admin import get_rate_admin_service, RateAdminService
from warehouse_quote_app.app.services.quote_generator import get_quote_generator, QuoteGenerator
from warehouse_quote_app.app.services.audit_logger import get_audit_logger, AuditLogger
from warehouse_quote_app.app.services.reporting_service import get_reporting_service, ReportingService
from warehouse_quote_app.app.core.logging import get_logger
from warehouse_quote_app.app.api.v1.mixins import PaginationMixin, QuoteFilterMixin, CRUDMixin, ReportingMixin

router = APIRouter()
logger = get_logger("admin")

# Set up CRUD routes for rate cards
rate_card_crud = CRUDMixin[RateCardCreate, RateAdminService](
    router=router,
    path="rate-cards",
    response_model=RateCardResponse,
    service_dependency=get_rate_admin_service,
    admin_only=True
)

@router.get("/admin/rates")
async def list_rates(
    pagination: dict = Depends(PaginationMixin.paginate),
    service: RateAdminService = Depends(get_rate_admin_service),
    current_user: User = Depends(get_current_admin_user)
) -> Any:
    return await service.list(skip=pagination["skip"], limit=pagination["limit"])

@router.get("/admin/rates/{rate_id}")
async def get_rate(
    rate_id: int,
    service: RateAdminService = Depends(get_rate_admin_service),
    current_user: User = Depends(get_current_admin_user)
) -> Any:
    rate = await service.get(rate_id)
    if not rate:
        raise HTTPException(status_code=404, detail="Rate not found")
    return rate

@router.post("/admin/rates", status_code=201)
async def create_rate(
    rate: Dict[str, Any],
    service: RateAdminService = Depends(get_rate_admin_service),
    current_user: User = Depends(get_current_admin_user)
) -> Any:
    return await service.create(RateCreate(**rate))

@router.put("/admin/rates/{rate_id}")
async def update_rate(
    rate_id: int,
    rate: Dict[str, Any],
    service: RateAdminService = Depends(get_rate_admin_service),
    current_user: User = Depends(get_current_admin_user)
) -> Any:
    return await service.update(rate_id, RateUpdate(**rate))

class LoginCredentials(BaseModel):
    email: str
    password: str

@router.post("/admin/login")
async def admin_login(
    credentials: LoginCredentials,
    admin_service: AdminService = Depends(get_admin_service)
) -> Dict[str, str]:
    """Login as admin user."""
    token = await admin_service.login(credentials.email, credentials.password)
    return {"access_token": token, "token_type": "bearer"}

@router.get("/admin/metrics", response_model=AdminMetricsResponse)
async def get_metrics(
    admin_service: AdminService = Depends(get_admin_service)
) -> AdminMetricsResponse:
    """Get admin dashboard metrics."""
    return await admin_service.get_metrics()

@router.get("/admin/dashboard")
async def admin_dashboard(
    admin_service: AdminService = Depends(get_admin_service),
    current_user: User = Depends(get_current_admin_user)
) -> Dict[str, Any]:
    """Return admin dashboard data."""
    return await admin_service.get_dashboard()

@router.get("/admin/customers", response_model=List[CustomerResponse])
async def list_customers(
    pagination: dict = Depends(PaginationMixin.paginate),
    search: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None),
    admin_service: AdminService = Depends(get_admin_service)
) -> List[CustomerResponse]:
    """List customers with optional filters."""
    return await admin_service.list_customers(
        skip=pagination["skip"],
        limit=pagination["limit"],
        search=search,
        is_active=is_active
    )

@router.get("/admin/customers/{customer_id}", response_model=CustomerResponse)
async def get_customer(
    customer_id: int = Path(..., gt=0),
    admin_service: AdminService = Depends(get_admin_service),
    current_user: User = Depends(get_current_admin_user),
) -> Any:
    customer = await admin_service.get_customer(customer_id)
    if not customer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found")
    return customer

@router.post("/admin/customers", response_model=CustomerResponse, status_code=201)
async def create_customer(
    customer: Dict[str, Any],
    admin_service: AdminService = Depends(get_admin_service),
    current_user: User = Depends(get_current_admin_user),
) -> Any:
    return await admin_service.create_customer(customer)

@router.put("/admin/customers/{customer_id}", response_model=CustomerResponse)
async def update_customer(
    customer_id: int = Path(..., gt=0),
    customer: Dict[str, Any] = None,
    admin_service: AdminService = Depends(get_admin_service),
    current_user: User = Depends(get_current_admin_user),
) -> Any:
    updated = await admin_service.update_customer(customer_id, customer)
    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found")
    return updated

@router.get("/admin/quotes", response_model=List[QuoteResponse])
async def list_quotes(
    pagination: dict = Depends(PaginationMixin.paginate),
    filters: dict = Depends(QuoteFilterMixin.filter_quotes),
    admin_service: AdminService = Depends(get_admin_service)
) -> List[QuoteResponse]:
    """List all quotes with optional filters."""
    return await admin_service.list_quotes(pagination["skip"], pagination["limit"], filters)


@router.post("/admin/quotes", status_code=201)
async def create_quote(
    quote: Dict[str, Any],
    admin_service: AdminService = Depends(get_admin_service),
    current_user: User = Depends(get_current_admin_user)
) -> Any:
    return await admin_service.create_quote(quote, current_user.id)

@router.post("/admin/quotes/generate")
async def generate_quote(
    quote_request: QuoteGenerateRequest,
    admin_user: User = Depends(get_current_admin_user),
    quote_generator: QuoteGenerator = Depends(get_quote_generator),
    audit_logger: AuditLogger = Depends(get_audit_logger)
) -> Dict[str, Any]:
    """Generate a quote using LLM and notify customer."""
    try:
        quote = await quote_generator.generate_quote(quote_request)
        
        # Log the action
        await audit_logger.log_action(
            user_id=admin_user.id,
            action="generate_quote",
            details={
                "customer_id": quote_request.customer_id,
                "service_type": quote_request.service_type,
                "quote_id": quote.id
            }
        )
        
        return {
            "status": "success",
            "quote_id": quote.id,
            "message": "Quote generated successfully"
        }
        
    except Exception as e:
        logger.error(f"Error generating quote: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate quote"
        )

@router.get("/admin/reports/quotes", response_model=QuoteReport)
async def get_quote_report(
    date_range: dict = Depends(ReportingMixin.get_date_range),
    filters: dict = Depends(ReportingMixin.get_report_filters),
    format: str = Depends(ReportingMixin.get_report_format),
    admin_service: AdminService = Depends(get_admin_service)
) -> QuoteReport:
    """Generate quote activity report."""
    return await admin_service.generate_quote_report(date_range, filters, format)

@router.get("/admin/reports/service-usage", response_model=ServiceReport)
async def get_service_usage(
    date_range: dict = Depends(ReportingMixin.get_date_range),
    format: str = Depends(ReportingMixin.get_report_format),
    admin_service: AdminService = Depends(get_admin_service)
) -> ServiceReport:
    """Generate service usage report."""
    return await admin_service.generate_service_usage_report(date_range, format)

@router.get("/admin/reports/customer-activity/{customer_id}", response_model=CustomerReport)
async def get_customer_activity(
    customer_id: int = Path(..., gt=0),
    date_range: dict = Depends(ReportingMixin.get_date_range),
    format: str = Depends(ReportingMixin.get_report_format),
    admin_service: AdminService = Depends(get_admin_service)
) -> CustomerReport:
    """Generate customer activity report."""
    return await admin_service.generate_customer_activity_report(
        customer_id,
        date_range,
        format
    )

@router.get("/admin/reports/quotes/status")
async def get_quote_status_report(
    reporting: ReportingService = Depends(get_reporting_service),
    current_user: User = Depends(get_current_admin_user)
) -> Any:
    return await reporting.generate_quote_status_report()

@router.get("/admin/reports/revenue")
async def get_revenue_report(
    period: str = Query("month"),
    reporting: ReportingService = Depends(get_reporting_service),
    current_user: User = Depends(get_current_admin_user)
) -> Any:
    return await reporting.generate_revenue_report(period)

@router.get("/admin/quotes/pending", response_model=List[QuoteResponse])
async def list_pending_quotes(
    admin_service: AdminService = Depends(get_admin_service),
    current_user: User = Depends(get_current_admin_user)
) -> List[QuoteResponse]:
    return await admin_service.list_pending_quotes()

@router.post("/admin/quotes/{quote_id}/approve")
async def approve_quote(
    quote_id: int = Path(..., gt=0),
    approval: Dict[str, Any] = None,
    admin_service: AdminService = Depends(get_admin_service),
    current_user: User = Depends(get_current_admin_user)
) -> Any:
    discount = approval.get("approved_discount", 0) if approval else 0
    return await admin_service.approve_quote(quote_id, discount, approval.get("notes") if approval else None)
