"""
Negotiation repository for database operations.
"""

from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, update
from sqlalchemy.future import select

from warehouse_quote_app.app.models.negotiation import QuoteNegotiation, NegotiationStatus
from warehouse_quote_app.app.schemas.quote import QuoteNegotiationRequest, QuoteNegotiationResponse
from warehouse_quote_app.app.repositories.base import BaseRepository
from warehouse_quote_app.app.repositories.mixins import FilterMixin, AggregationMixin, PaginationMixin
from warehouse_quote_app.app.core.logging import get_logger

logger = get_logger("negotiation_repository")

class NegotiationRepository(
    BaseRepository,
    FilterMixin,
    AggregationMixin,
    PaginationMixin
):
    """Repository for negotiation-related database operations."""
    
    def __init__(self, db: AsyncSession = None):
        """Initialize with optional database session."""
        self.db = db
        self.model = QuoteNegotiation
    
    async def create_negotiation(
        self,
        quote_id: int,
        user_id: int,
        original_amount: float,
        negotiation_request: QuoteNegotiationRequest
    ) -> QuoteNegotiation:
        """Create a new negotiation record."""
        logger.info(f"Creating negotiation for quote {quote_id} by user {user_id}")
        
        negotiation = QuoteNegotiation(
            quote_id=quote_id,
            user_id=user_id,
            original_amount=original_amount,
            proposed_amount=negotiation_request.proposed_amount,
            reason=negotiation_request.reason,
            additional_notes=negotiation_request.additional_notes,
            status=NegotiationStatus.PENDING
        )
        
        self.db.add(negotiation)
        await self.db.commit()
        await self.db.refresh(negotiation)
        
        return negotiation
    
    async def get_by_quote_id(self, quote_id: int) -> List[QuoteNegotiation]:
        """Get all negotiations for a quote."""
        logger.info(f"Getting negotiations for quote {quote_id}")
        
        result = await self.db.execute(
            select(QuoteNegotiation)
            .where(QuoteNegotiation.quote_id == quote_id)
            .order_by(QuoteNegotiation.created_at.desc())
        )
        
        return result.scalars().all()
    
    async def update_status(
        self,
        negotiation_id: int,
        status: str,
        admin_response: Optional[str] = None
    ) -> QuoteNegotiation:
        """Update negotiation status."""
        logger.info(f"Updating negotiation {negotiation_id} status to {status}")
        
        stmt = (
            update(QuoteNegotiation)
            .where(QuoteNegotiation.id == negotiation_id)
            .values(
                status=status,
                admin_response=admin_response,
                updated_at=datetime.utcnow()
            )
            .returning(QuoteNegotiation)
        )
        
        result = await self.db.execute(stmt)
        await self.db.commit()
        
        return result.scalar_one()
    
    async def to_response_model(self, negotiation: QuoteNegotiation) -> QuoteNegotiationResponse:
        """Convert database model to response schema."""
        return QuoteNegotiationResponse(
            quote_id=negotiation.quote_id,
            original_amount=negotiation.original_amount,
            proposed_amount=negotiation.proposed_amount,
            status=negotiation.status,
            admin_response=negotiation.admin_response,
            created_at=negotiation.created_at
        )
