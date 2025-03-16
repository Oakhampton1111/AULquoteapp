"""Client endpoints."""
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, Path, HTTPException, status

from warehouse_quote_app.app.core.auth import get_current_client_user
from warehouse_quote_app.app.models.user import User
from warehouse_quote_app.app.models.quote import QuoteStatus
from warehouse_quote_app.app.schemas.client import (
    ClientProfile,
    ClientQuoteResponse,
    ClientServiceResponse,
    SupportTicketCreate,
    SupportTicketResponse
)
from warehouse_quote_app.app.services.client import get_client_service, ClientService
from warehouse_quote_app.app.core.logging import get_logger

router = APIRouter()
logger = get_logger("client")

@router.get(
    "/client/me",
    response_model=ClientProfile,
    dependencies=[Depends(get_current_client_user)]
)
async def get_profile(
    client_service: ClientService = Depends(get_client_service)
):
    """Get current client profile."""
    return await client_service.get_profile()

@router.get(
    "/client/quotes",
    response_model=List[ClientQuoteResponse],
    dependencies=[Depends(get_current_client_user)]
)
async def list_quotes(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    status: Optional[QuoteStatus] = Query(None),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    client_service: ClientService = Depends(get_client_service)
):
    """List client quotes with optional filters."""
    return await client_service.list_quotes(
        skip=skip,
        limit=limit,
        status=status,
        start_date=start_date,
        end_date=end_date
    )

@router.get(
    "/client/quotes/{quote_id}",
    response_model=ClientQuoteResponse,
    dependencies=[Depends(get_current_client_user)]
)
async def get_quote(
    quote_id: int,
    client_service: ClientService = Depends(get_client_service)
):
    """Get specific quote details."""
    return await client_service.get_quote(quote_id)

@router.get(
    "/client/services/active",
    response_model=List[ClientServiceResponse],
    dependencies=[Depends(get_current_client_user)]
)
async def list_active_services(
    client_service: ClientService = Depends(get_client_service)
):
    """List active services for the client."""
    return await client_service.list_active_services()

@router.get(
    "/client/services/{service_id}",
    response_model=ClientServiceResponse,
    dependencies=[Depends(get_current_client_user)]
)
async def get_service(
    service_id: int,
    client_service: ClientService = Depends(get_client_service)
):
    """Get specific service details."""
    return await client_service.get_service(service_id)

@router.post(
    "/client/support/tickets",
    response_model=SupportTicketResponse,
    dependencies=[Depends(get_current_client_user)]
)
async def create_support_ticket(
    ticket: SupportTicketCreate,
    client_service: ClientService = Depends(get_client_service)
):
    """Create a new support ticket."""
    return await client_service.create_support_ticket(ticket)

@router.get(
    "/client/support/tickets",
    response_model=List[SupportTicketResponse],
    dependencies=[Depends(get_current_client_user)]
)
async def list_support_tickets(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    status: Optional[str] = Query(None),
    client_service: ClientService = Depends(get_client_service)
):
    """List support tickets."""
    return await client_service.list_support_tickets(
        skip=skip,
        limit=limit,
        status=status
    )
