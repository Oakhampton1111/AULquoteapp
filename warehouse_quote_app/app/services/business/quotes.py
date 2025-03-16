"""
Quote generation and management service.
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from datetime import datetime
from decimal import Decimal

from warehouse_quote_app.app.core.monitoring import log_event
from warehouse_quote_app.app.models.quote import Quote
from warehouse_quote_app.app.schemas.quote import (
    QuoteCreate,
    QuoteUpdate,
    MultiServiceQuoteRequest,
    BulkQuoteRequest,
    BulkQuoteResponse
)
from warehouse_quote_app.app.repositories.quote import QuoteRepository
from warehouse_quote_app.app.services.base import BaseService
from warehouse_quote_app.app.services.llm.rate_integration import RateIntegrationService
from warehouse_quote_app.app.services.business.storage import StorageService
from warehouse_quote_app.app.services.business.three_pl import ThreePLService
from warehouse_quote_app.app.services.business.transport import TransportService

class QuoteService(BaseService[Quote, QuoteCreate, QuoteUpdate]):
    """Service for managing quotes."""

    def __init__(self, db: Session):
        """Initialize with Quote model."""
        super().__init__(Quote, db)
        self.rate_integration_service = RateIntegrationService(db=db)
        self.storage_service = StorageService()
        self.three_pl_service = ThreePLService()
        self.transport_service = TransportService()
        self.repository = QuoteRepository(Quote)

    def calculate_quote(
        self,
        request: MultiServiceQuoteRequest,
        db: Session
    ) -> Dict[str, Any]:
        """Calculate quote for multiple services."""
        # Calculate costs for each service type
        costs = {}
        total_cost = Decimal('0')

        # Storage costs
        if request.storage_requirements:
            storage_cost = self.storage_service.calculate_storage_cost(
                request.storage_requirements,
                db
            )
            costs['storage'] = storage_cost
            total_cost += storage_cost

            self.storage_service.log_storage_calculation(
                db,
                request.storage_requirements,
                storage_cost,
                request.user_id
            )

        # 3PL costs
        if request.three_pl_services:
            three_pl_cost = self.three_pl_service.calculate_3pl_cost(
                request.three_pl_services,
                db
            )
            costs['3pl'] = three_pl_cost
            total_cost += three_pl_cost

            self.three_pl_service.log_3pl_calculation(
                db,
                request.three_pl_services,
                three_pl_cost,
                request.user_id
            )

        # Transport costs
        if request.transport_services:
            transport_cost = self.transport_service.calculate_transport_cost(
                request.transport_services,
                db
            )
            costs['transport'] = transport_cost
            total_cost += transport_cost

            self.transport_service.log_transport_calculation(
                db,
                request.transport_services,
                transport_cost,
                request.user_id
            )

        # Use rate integration service to get best rates
        optimized_rates = self.rate_integration_service.optimize_rates(request)
        
        # Create quote in database
        quote = self.create_quote_from_costs(
            db=db,
            costs=costs,
            total_cost=total_cost,
            optimized_rates=optimized_rates,
            request=request
        )
        
        # Log quote creation
        log_event(
            db=db,
            event_type="quote_created",
            user_id=request.user_id,
            resource_type="quote",
            resource_id=str(quote.id),
            details={
                "services": request.services,
                "costs": {k: str(v) for k, v in costs.items()},
                "total_cost": str(total_cost)
            }
        )
        
        return quote

    def calculate_bulk_quotes(
        self,
        request: BulkQuoteRequest,
        db: Session
    ) -> BulkQuoteResponse:
        """Calculate multiple quotes in bulk."""
        quotes = []
        for quote_request in request.quotes:
            quote = self.calculate_quote(quote_request, db)
            quotes.append(quote)
        
        return BulkQuoteResponse(quotes=quotes)

    def compare_service_combinations(
        self,
        request: MultiServiceQuoteRequest,
        db: Session
    ) -> List[Dict[str, Any]]:
        """Compare different combinations of services."""
        combinations = self.rate_integration_service.generate_service_combinations(request)
        
        quotes = []
        for combo in combinations:
            modified_request = request.copy(update={"services": combo})
            quote = self.calculate_quote(modified_request, db)
            quotes.append(quote)
        
        return quotes

    def create_quote_from_costs(
        self,
        db: Session,
        costs: Dict[str, Decimal],
        total_cost: Decimal,
        optimized_rates: Dict[str, Any],
        request: MultiServiceQuoteRequest
    ) -> Quote:
        """Create a quote record from calculated costs and rates."""
        quote_data = QuoteCreate(
            user_id=request.user_id,
            customer_id=request.customer_id,
            services=request.services,
            costs=costs,
            rates=optimized_rates,
            total_amount=total_cost,
            valid_until=datetime.utcnow().date(),
            status="draft"
        )
        
        quote = self.repository.create(db, obj_in=quote_data)
        return quote

    def finalize_quote(
        self,
        db: Session,
        quote_id: int,
        user_id: int
    ) -> Quote:
        """Finalize a quote."""
        quote = self.repository.get(db, quote_id)
        if not quote:
            raise ValueError("Quote not found")
        
        quote_update = QuoteUpdate(
            status="final",
            finalized_at=datetime.utcnow(),
            finalized_by=user_id
        )
        
        updated_quote = self.repository.update(db, db_obj=quote, obj_in=quote_update)
        
        log_event(
            db=db,
            event_type="quote_finalized",
            user_id=user_id,
            resource_type="quote",
            resource_id=str(quote_id),
            details={"total_amount": updated_quote.total_amount}
        )
        
        return updated_quote
