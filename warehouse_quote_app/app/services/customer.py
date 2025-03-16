"""Customer service module for handling customer-related business logic."""

from typing import Optional, List, Dict, Any
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from warehouse_quote_app.app.database import get_db
from warehouse_quote_app.app.models.customer import Customer
from warehouse_quote_app.app.repositories.customer import CustomerRepository
from warehouse_quote_app.app.schemas.customer import (
    CustomerCreate,
    CustomerUpdate,
    CustomerPreferenceUpdate,
    CustomerResponse,
    CustomerDashboardResponse,
    CustomerListResponse
)

class CustomerService:
    """Service for managing customer operations and business logic."""

    def __init__(
        self,
        db: AsyncSession = Depends(get_db),
        repository: CustomerRepository = Depends()
    ) -> None:
        """Initialize the customer service.
        
        Args:
            db: Async database session
            repository: Customer repository for data access
        """
        self.db = db
        self.repository = repository

    async def create(
        self,
        *,
        customer_in: CustomerCreate
    ) -> CustomerResponse:
        """Create a new customer.
        
        Args:
            customer_in: Customer creation data
            
        Returns:
            CustomerResponse: Created customer data
            
        Raises:
            ValueError: If required fields are missing
        """
        customer = await self.repository.create(self.db, obj_in=customer_in)
        return CustomerResponse.from_orm(customer)

    async def update(
        self,
        *,
        customer_id: int,
        customer_in: CustomerUpdate
    ) -> Optional[CustomerResponse]:
        """Update customer details.
        
        Args:
            customer_id: ID of the customer to update
            customer_in: Customer update data
            
        Returns:
            Optional[CustomerResponse]: Updated customer data or None if not found
        """
        customer = await self.repository.get(self.db, id=customer_id)
        if not customer:
            return None
        updated = await self.repository.update(self.db, db_obj=customer, obj_in=customer_in)
        return CustomerResponse.from_orm(updated)

    async def get(
        self,
        customer_id: int
    ) -> Optional[CustomerResponse]:
        """Get customer by ID.
        
        Args:
            customer_id: ID of the customer to retrieve
            
        Returns:
            Optional[CustomerResponse]: Customer data or None if not found
        """
        customer = await self.repository.get(self.db, id=customer_id)
        if not customer:
            return None
        return CustomerResponse.from_orm(customer)

    async def get_by_email(
        self,
        email: str
    ) -> Optional[Customer]:
        """Get customer by email."""
        return await self.repository.get_by_email(self.db, email)

    async def get_dashboard(
        self,
        customer_id: int
    ) -> Optional[CustomerDashboardResponse]:
        """Get customer dashboard data.
        
        Args:
            customer_id: ID of the customer
            
        Returns:
            Optional[CustomerDashboardResponse]: Dashboard data or None if not found
            
        Note:
            Dashboard includes aggregated metrics and recent activity
        """
        customer = await self.repository.get_with_quotes(self.db, customer_id)
        if not customer:
            return None
        
        # Get dashboard metrics
        metrics = await self.repository.get_customer_metrics(self.db, customer_id)
        return CustomerDashboardResponse(
            id=customer.id,
            total_quotes=metrics.get("total_quotes", 0),
            accepted_quotes=metrics.get("accepted_quotes", 0),
            rejected_quotes=metrics.get("rejected_quotes", 0),
            total_spent=metrics.get("total_spent", 0.0),
            last_quote_date=metrics.get("last_quote_date"),
            recent_quotes=customer.recent_quotes[:5]  # Last 5 quotes
        )

    async def update_preferences(
        self,
        *,
        customer_id: int,
        preferences: CustomerPreferenceUpdate
    ) -> Optional[Customer]:
        """Update customer preferences."""
        customer = await self.repository.get(self.db, id=customer_id)
        if not customer:
            return None
        
        await customer.update_preferences(
            contact_method=preferences.preferred_contact_method,
            notifications=preferences.notification_preferences,
            requirements=preferences.special_requirements
        )
        
        self.db.add(customer)
        await self.db.commit()
        await self.db.refresh(customer)
        return customer

    async def list_active(
        self,
        *,
        skip: int = 0,
        limit: int = 100
    ) -> List[Customer]:
        """List active customers."""
        return await self.repository.list_active(self.db, skip=skip, limit=limit)

async def get_customer_service(
    db: AsyncSession = Depends(get_db),
    repository: Optional[CustomerRepository] = None
) -> CustomerService:
    """Dependency injection for customer service.
    
    Args:
        db: Async database session
        repository: Customer repository instance
        
    Returns:
        CustomerService: Configured customer service instance
    """
    if repository is None:
        repository = CustomerRepository(db)
    return CustomerService(db=db, repository=repository)
