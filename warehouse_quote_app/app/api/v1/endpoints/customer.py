"""Customer endpoints."""
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, Path

from warehouse_quote_app.app.core.auth import get_current_user
from warehouse_quote_app.app.models.user import User
from warehouse_quote_app.app.models.quote import QuoteStatus
from warehouse_quote_app.app.schemas.customer import (
    CustomerDashboardResponse,
    CustomerProfileResponse,
    CustomerPreferenceUpdate,
    CustomerCreate,
    CustomerUpdate,
    CustomerResponse,
    CustomerListResponse
)
from warehouse_quote_app.app.schemas.quote import QuoteDetailResponse
from warehouse_quote_app.app.services.customer import CustomerService
from warehouse_quote_app.app.core.logging import get_logger
from warehouse_quote_app.app.api.v1.mixins import PaginationMixin, QuoteFilterMixin
from warehouse_quote_app.app.database import get_db
from warehouse_quote_app.app.repositories.customer import CustomerRepository
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()
logger = get_logger("customer")

# Define customer routes directly instead of using CRUDMixin
@router.get("/customer/profile/{customer_id}")
async def get_customer(
    customer_id: int = Path(..., gt=0),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get a customer by ID."""
    repository = CustomerRepository(db)
    service = CustomerService(db=db, repository=repository)
    return await service.get(customer_id)

@router.get("/customer/profile")
async def list_customers(
    pagination: dict = Depends(PaginationMixin.paginate),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List all customers with pagination."""
    repository = CustomerRepository(db)
    service = CustomerService(db=db, repository=repository)
    return await service.list(**pagination)

@router.post("/customer/profile")
async def create_customer(
    customer: CustomerCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new customer."""
    repository = CustomerRepository(db)
    service = CustomerService(db=db, repository=repository)
    return await service.create(customer_in=customer)

@router.put("/customer/profile/{customer_id}")
async def update_customer(
    customer_id: int,
    customer: CustomerUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update an existing customer."""
    repository = CustomerRepository(db)
    service = CustomerService(db=db, repository=repository)
    return await service.update(customer_id=customer_id, customer_in=customer)

@router.delete("/customer/profile/{customer_id}")
async def delete_customer(
    customer_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete a customer."""
    repository = CustomerRepository(db)
    service = CustomerService(db=db, repository=repository)
    return await service.delete(customer_id=customer_id)

@router.get("/customer/dashboard")
async def get_dashboard(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get customer dashboard."""
    repository = CustomerRepository(db)
    service = CustomerService(db=db, repository=repository)
    return await service.get_dashboard(current_user)

@router.put("/customer/preferences")
async def update_preferences(
    preferences: CustomerPreferenceUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update customer preferences."""
    repository = CustomerRepository(db)
    service = CustomerService(db=db, repository=repository)
    return await service.update_preferences(current_user.id, preferences)

@router.get("/customer/quotes")
async def list_quotes(
    pagination: dict = Depends(PaginationMixin.paginate),
    filters: dict = Depends(QuoteFilterMixin.filter_quotes),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List customer quotes."""
    repository = CustomerRepository(db)
    service = CustomerService(db=db, repository=repository)
    return await service.list_quotes(current_user.id, **pagination, **filters)

@router.get("/customer/quotes/{quote_id}")
async def get_quote(
    quote_id: int = Path(..., gt=0),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get specific quote."""
    repository = CustomerRepository(db)
    service = CustomerService(db=db, repository=repository)
    return await service.get_quote(current_user.id, quote_id)
