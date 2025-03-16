"""
Client service module for the Warehouse Quote System.

This module provides the ClientService class that handles client-specific operations.
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from warehouse_quote_app.app.database import get_db
from warehouse_quote_app.app.models.user import User
from warehouse_quote_app.app.models.quote import Quote, QuoteStatus
from warehouse_quote_app.app.repositories.user import UserRepository
from warehouse_quote_app.app.repositories.quote import QuoteRepository
from warehouse_quote_app.app.schemas.client import (
    ClientProfile,
    ClientQuoteResponse,
    ClientServiceResponse,
    SupportTicketCreate,
    SupportTicketResponse
)
from warehouse_quote_app.app.core.auth import get_current_client_user
from warehouse_quote_app.app.core.logging import get_logger

logger = get_logger("client_service")

class ClientService:
    """Client service class."""
    
    def __init__(
        self,
        db: AsyncSession,
        current_user: User
    ):
        """Initialize the client service."""
        self.db = db
        self.current_user = current_user
        self.user_repo = UserRepository(db)
        self.quote_repo = QuoteRepository(db)
    
    async def get_profile(self) -> ClientProfile:
        """Get client profile."""
        return ClientProfile.model_validate(self.current_user)
    
    async def list_quotes(
        self,
        skip: int = 0,
        limit: int = 100,
        status: Optional[QuoteStatus] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[ClientQuoteResponse]:
        """List client quotes with optional filters."""
        quotes = await self.quote_repo.get_by_customer_id(
            customer_id=self.current_user.id,
            skip=skip,
            limit=limit,
            status=status,
            start_date=start_date,
            end_date=end_date
        )
        return [ClientQuoteResponse.model_validate(quote) for quote in quotes]
    
    async def get_quote(self, quote_id: int) -> ClientQuoteResponse:
        """Get specific quote details."""
        quote = await self.quote_repo.get(quote_id)
        if not quote or quote.customer_id != self.current_user.id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Quote not found"
            )
        return ClientQuoteResponse.model_validate(quote)
    
    async def list_active_services(self) -> List[ClientServiceResponse]:
        """List active services for the client."""
        # This is a placeholder - in a real implementation, you would fetch from a service repository
        return []
    
    async def get_service(self, service_id: int) -> ClientServiceResponse:
        """Get specific service details."""
        # This is a placeholder - in a real implementation, you would fetch from a service repository
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service not found"
        )
    
    async def create_support_ticket(
        self,
        ticket: SupportTicketCreate
    ) -> SupportTicketResponse:
        """Create a new support ticket."""
        # This is a placeholder - in a real implementation, you would save to a ticket repository
        return SupportTicketResponse(
            id=1,
            subject=ticket.subject,
            description=ticket.description,
            priority=ticket.priority,
            category=ticket.category,
            status="open",
            created_at=datetime.utcnow()
        )
    
    async def list_support_tickets(
        self,
        skip: int = 0,
        limit: int = 100,
        status: Optional[str] = None
    ) -> List[SupportTicketResponse]:
        """List support tickets."""
        # This is a placeholder - in a real implementation, you would fetch from a ticket repository
        return []

async def get_client_service(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_client_user)
) -> ClientService:
    """Get client service dependency."""
    return ClientService(db, current_user)

__all__ = [
    'ClientService',
    'get_client_service'
]
