"""Quote lifecycle management service."""

from typing import List, Optional, Dict, Any, Union
from datetime import datetime, timedelta
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update, delete

from warehouse_quote_app.app.models.quote import Quote
from warehouse_quote_app.app.models.customer import Customer
from warehouse_quote_app.app.schemas.quote import (
    QuoteCreate,
    QuoteResponse,
    QuoteStatusUpdate,
    QuoteListResponse,
    QuoteFilter,
    QuoteNegotiationRequest,
    QuoteNegotiationResponse,
)
from warehouse_quote_app.app.core.logging import get_logger
from warehouse_quote_app.app.repositories.quote import QuoteRepository
from warehouse_quote_app.app.repositories.customer import CustomerRepository
from warehouse_quote_app.app.repositories.negotiation import NegotiationRepository
from warehouse_quote_app.app.services.crm import CRMService
from warehouse_quote_app.app.schemas.crm import DealCreate, InteractionCreate
from warehouse_quote_app.app.models.crm import DealStage, InteractionType

logger = get_logger("quote_lifecycle")


class QuoteLifecycleService:
    """Service for managing the quote lifecycle from creation to acceptance/rejection."""

    def __init__(self, db: AsyncSession, repository: Optional[QuoteRepository] = None):
        """Initialize the service with database session and optional repository."""
        self.db = db
        self.repository = repository or QuoteRepository(db)
        self.customer_repository = CustomerRepository(db)
        self.negotiation_repository = NegotiationRepository(db)

    async def create_quote(self, quote_data: QuoteCreate, created_by_id: int) -> QuoteResponse:
        """Create a new quote."""
        logger.info(f"Creating new quote for customer {quote_data.customer_id}")

        # Verify customer exists
        customer = await self.customer_repository.get(quote_data.customer_id)
        if not customer:
            logger.error(f"Customer {quote_data.customer_id} not found")
            raise ValueError(f"Customer with ID {quote_data.customer_id} not found")

        # Create quote
        quote = await self.repository.create_quote(
            customer_id=quote_data.customer_id,
            created_by_id=created_by_id,
            quote_request=quote_data.quote_request,
        )

        # Create a CRM deal and interaction for the new quote
        crm_service = CRMService(self.db)
        deal = await crm_service.create_deal(
            customer_id=quote_data.customer_id,
            deal=DealCreate(
                title=f"Quote {quote.id} request",
                description=f"Deal for quote {quote.id}",
                value=float(quote.total_amount),
            ),
            agent_id=created_by_id,
        )
        # Persist the deal ID on the quote so later status updates can
        # modify the correct CRM record
        await self.db.execute(
            update(Quote).where(Quote.id == quote.id).values(deal_id=deal.id)
        )
        await self.db.commit()
        await self.db.refresh(quote)
        await crm_service.update_deal_stage(
            deal_id=deal.id, stage=DealStage.QUOTE_REQUESTED, agent_id=created_by_id
        )
        await crm_service.create_interaction(
            customer_id=quote_data.customer_id,
            interaction=InteractionCreate(
                type=InteractionType.NOTE, description=f"Quote {quote.id} requested"
            ),
            agent_id=created_by_id,
        )

        return await self.get_quote_response(quote.id)

    async def get_quote(self, quote_id: int) -> QuoteResponse:
        """Get a quote by ID."""
        logger.info(f"Retrieving quote {quote_id}")
        return await self.get_quote_response(quote_id)

    async def list_quotes(
        self, skip: int = 0, limit: int = 100, filter_params: Optional[QuoteFilter] = None
    ) -> QuoteListResponse:
        """List quotes with pagination and filtering."""
        logger.info(f"Listing quotes with skip={skip}, limit={limit}")

        quotes, total = await self.repository.list_quotes(
            skip=skip, limit=limit, filter_params=filter_params
        )

        # Convert to response models
        quote_responses = []
        for quote in quotes:
            quote_response = await self.repository.to_response_model(quote)
            quote_responses.append(quote_response)

        # Calculate pagination
        page = skip // limit + 1 if limit > 0 else 1
        pages = (total + limit - 1) // limit if limit > 0 else 1

        return QuoteListResponse(
            items=quote_responses, total=total, page=page, page_size=limit, pages=pages
        )

    async def update_quote_status(
        self, quote_id: int, status_update: QuoteStatusUpdate
    ) -> QuoteResponse:
        """Update a quote's status."""
        logger.info(f"Updating quote {quote_id} status to {status_update.status}")

        # Get the quote
        quote = await self.repository.get(quote_id)
        if not quote:
            logger.error(f"Quote {quote_id} not found")
            raise ValueError(f"Quote with ID {quote_id} not found")

        # Update status
        updated_quote = await self.repository.update_status(
            quote_id=quote_id,
            status=status_update.status,
            rejection_reason=status_update.rejection_reason,
        )

        # Update CRM deal stage based on the new quote status
        crm_service = CRMService(self.db)
        deal_id = updated_quote.deal_id or quote.deal_id
        if deal_id:
            if status_update.status == "accepted":  # Consider using QuoteStatus.ACCEPTED.value
                await crm_service.update_deal_stage(
                    deal_id=deal_id,
                    stage=DealStage.CLOSED_WON,
                    agent_id=quote.created_by,
                )
            elif status_update.status == "rejected":  # Consider using QuoteStatus.REJECTED.value
                await crm_service.update_deal_stage(
                    deal_id=deal_id,
                    stage=DealStage.CLOSED_LOST,
                    agent_id=quote.created_by,
                )

        return await self.get_quote_response(quote_id)

    async def delete_quote(self, quote_id: int) -> bool:
        """Delete a quote."""
        logger.info(f"Deleting quote {quote_id}")

        # Get the quote
        quote = await self.repository.get(quote_id)
        if not quote:
            logger.error(f"Quote {quote_id} not found")
            raise ValueError(f"Quote with ID {quote_id} not found")

        # Delete the quote
        return await self.repository.delete(quote_id)

    async def get_quote_response(self, quote_id: int) -> QuoteResponse:
        """Get a quote response model by ID."""
        quote = await self.repository.get(quote_id)
        if not quote:
            logger.error(f"Quote {quote_id} not found")
            raise ValueError(f"Quote with ID {quote_id} not found")

        return await self.repository.to_response_model(quote)

    async def negotiate_quote(
        self, quote_id: int, user_id: int, negotiation_request: QuoteNegotiationRequest
    ) -> QuoteNegotiationResponse:
        """Submit a negotiation request for a quote."""
        logger.info(f"Processing negotiation request for quote {quote_id}")

        # Get the quote
        quote = await self.repository.get(quote_id)
        if not quote:
            logger.error(f"Quote {quote_id} not found")
            raise ValueError(f"Quote with ID {quote_id} not found")

        # Verify the quote is in a negotiable state
        if quote.status not in ["pending", "quoted"]:
            logger.error(f"Quote {quote_id} is not in a negotiable state")
            raise ValueError(f"Quote with ID {quote_id} is not in a negotiable state")

        # Create negotiation record
        negotiation = await self.negotiation_repository.create_negotiation(
            quote_id=quote_id,
            user_id=user_id,
            original_amount=quote.total_amount,
            negotiation_request=negotiation_request,
        )

        # Update quote status to reflect negotiation
        await self.repository.update_status(
            quote_id=quote_id,
            status="negotiating",
            notes=f"Negotiation requested: {negotiation_request.reason}",
        )

        # Return response
        return await self.negotiation_repository.to_response_model(negotiation)


def get_quote_lifecycle_service(db: AsyncSession) -> QuoteLifecycleService:
    """Dependency for getting the quote lifecycle service."""
    return QuoteLifecycleService(db)
