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
from warehouse_quote_app.app.schemas.reports.quote_report import QuoteReport
from warehouse_quote_app.app.schemas.reports.service_report import ServiceReport
from warehouse_quote_app.app.schemas.reports.customer_report import CustomerReport
from warehouse_quote_app.app.services.admin import get_admin_service, AdminService
from warehouse_quote_app.app.services.rate_admin import get_rate_admin_service, RateAdminService
from warehouse_quote_app.app.services.quote_generator import get_quote_generator, QuoteGenerator
from warehouse_quote_app.app.services.audit_logger import get_audit_logger, AuditLogger
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

@router.get("/admin/quotes", response_model=List[QuoteResponse])
async def list_quotes(
    pagination: dict = Depends(PaginationMixin.paginate),
    filters: dict = Depends(QuoteFilterMixin.filter_quotes),
    admin_service: AdminService = Depends(get_admin_service)
) -> List[QuoteResponse]:
    """List all quotes with optional filters."""
    return await admin_service.list_quotes(pagination["skip"], pagination["limit"], filters)

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
