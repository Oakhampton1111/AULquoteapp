"""
Quote generation and management API routes.
"""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from decimal import Decimal

from warehouse_quote_app.app.core.database import get_db
from warehouse_quote_app.app.services.quote_service import QuoteService
from warehouse_quote_app.app.schemas.quote import (
    MultiServiceQuoteRequest,
    ServiceRequest,
    QuoteResponse,
    ServiceBreakdown,
    BulkQuoteRequest,
    BulkQuoteResponse
)

router = APIRouter(prefix="/quotes", tags=["quotes"])

@router.post("/calculate", response_model=QuoteResponse)
async def calculate_multiple_services_quote(
    request: MultiServiceQuoteRequest,
    quote_service: QuoteService = Depends(),
    db: Session = Depends(get_db)
):
    """Calculate quote for multiple services."""
    return await quote_service.calculate_quote(request)

@router.post("/bulk", response_model=BulkQuoteResponse)
async def calculate_bulk_quotes(
    request: BulkQuoteRequest,
    quote_service: QuoteService = Depends(),
    db: Session = Depends(get_db)
):
    """Calculate multiple quotes in bulk."""
    return await quote_service.calculate_bulk_quotes(request)

@router.post("/compare", response_model=List[QuoteResponse])
async def compare_service_combinations(
    request: MultiServiceQuoteRequest,
    quote_service: QuoteService = Depends(),
    db: Session = Depends(get_db)
):
    """Compare different combinations of services."""
    return await quote_service.compare_service_combinations(request)

@router.post("/chat")
async def process_chat_message(
    message: Dict[str, Any],
    quote_service: QuoteService = Depends(),
    db: Session = Depends(get_db)
):
    """Process chat messages for quote generation."""
    return await quote_service.process_chat_message(message)

@router.put("/modify")
async def modify_existing_quote(
    request: Dict[str, Any],
    quote_service: QuoteService = Depends(),
    db: Session = Depends(get_db)
):
    """Modify an existing quote based on chat input."""
    return await quote_service.modify_quote(request)
