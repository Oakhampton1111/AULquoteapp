"""
Rate service for managing rate operations with AI optimization capabilities.
"""

from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from warehouse_quote_app.app.core.monitoring import log_event
from warehouse_quote_app.app.models.rate import Rate
from warehouse_quote_app.app.schemas.rate.rate import (
    RateCreate, 
    RateUpdate,
    RateResponse,
    RateOptimizationResult,
    RateValidationResponse,
    RateListResponse
)
from warehouse_quote_app.app.repositories.rate import RateRepository
from warehouse_quote_app.app.services.validation.validation import ValidationService
from warehouse_quote_app.app.services.llm.model import WarehouseLLM
from warehouse_quote_app.app.services.llm.rag import RAGService
from warehouse_quote_app.app.core.config import Settings

class RateService:
    """Service for managing rate operations with AI optimization."""

    def __init__(
        self,
        db: AsyncSession = None,
        llm: Optional[WarehouseLLM] = None,
        rag: Optional[RAGService] = None,
        settings: Optional[Settings] = None
    ):
        """Initialize rate service with AI capabilities."""
        self.db = db
        self.repository = RateRepository(db) if db else None
        self.validator = ValidationService()
        self.llm = llm or WarehouseLLM()
        self.rag = rag or RAGService()
        self.settings = settings or Settings()

    async def create_rate(
        self,
        rate_data: RateCreate,
        user_id: int
    ) -> Rate:
        """Create a new rate with validation."""
        # Validate rate card
        validation_result = await self.validator.validate_rate_card(
            rate_data.model_dump(),
            self.db,
            user_id
        )
        
        if not validation_result["valid"]:
            raise ValueError(f"Invalid rate card: {validation_result['errors']}")

        # Create rate
        rate = await self.repository.create(obj_in=rate_data)

        # Log event
        log_event(
            db=self.db,
            event_type="rate_created",
            user_id=user_id,
            resource_type="rate",
            resource_id=str(rate.id),
            details={"category": rate.category}
        )
        
        return rate

    async def update_rate(
        self,
        rate_id: int,
        rate_data: RateUpdate,
        user_id: int
    ) -> Rate:
        """Update an existing rate."""
        # Get existing rate
        rate = await self.repository.get(rate_id)
        if not rate:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Rate not found"
            )

        # Validate update
        validation_result = await self.validator.validate_rate_card(
            rate_data.model_dump(),
            self.db,
            user_id
        )
        
        if not validation_result["valid"]:
            raise ValueError(f"Invalid rate update: {validation_result['errors']}")

        # Update rate
        rate = await self.repository.update(rate_id, obj_in=rate_data)

        # Log event
        log_event(
            db=self.db,
            event_type="rate_updated",
            user_id=user_id,
            resource_type="rate",
            resource_id=str(rate.id),
            details={"category": rate.category}
        )
        
        return rate

    async def delete_rate(
        self,
        rate_id: int,
        user_id: int
    ) -> Rate:
        """Delete a rate."""
        rate = await self.repository.get(rate_id)
        if not rate:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Rate not found"
            )

        # Delete rate
        await self.repository.delete(rate_id)

        # Log event
        log_event(
            db=self.db,
            event_type="rate_deleted",
            user_id=user_id,
            resource_type="rate",
            resource_id=str(rate_id)
        )
        
        return rate

    async def get_rate(
        self,
        rate_id: int
    ) -> Optional[Rate]:
        """Get a rate by ID."""
        return await self.repository.get(rate_id)

    async def get_rates(
        self,
        category: Optional[str] = None,
        active_only: bool = True
    ) -> List[Rate]:
        """Get all rates or filter by category."""
        filters = {"is_active": active_only} if active_only else {}
        if category:
            filters["category"] = category
        return await self.repository.get_multi(filters=filters)

    async def get_active_rates(
        self,
        category: Optional[str] = None
    ) -> List[Rate]:
        """Get active rates, optionally filtered by category."""
        return await self.repository.get_active_rates(
            self.db,
            category
        )

    async def get_rates_by_date_range(
        self,
        start_date: datetime,
        end_date: datetime
    ) -> List[Rate]:
        """Get rates valid within a date range."""
        return await self.repository.get_rates_by_date_range(
            self.db,
            start_date,
            end_date
        )

    async def get_rate_history(
        self,
        rate_id: int
    ) -> List[Rate]:
        """Get historical versions of a rate."""
        return await self.repository.get_rate_history(
            self.db,
            rate_id
        )

    async def get_rates_by_service(
        self,
        service_type: str
    ) -> List[Rate]:
        """Get rates for a specific service type."""
        return await self.repository.get_rates_by_service(
            self.db,
            service_type
        )

    async def get_rate_statistics(self) -> Dict[str, Any]:
        """Get statistics about rates."""
        return await self.repository.get_rate_statistics(self.db)

    async def optimize_rate(
        self,
        rate_id: int,
        optimization_params: Dict[str, Any]
    ) -> RateOptimizationResult:
        """Optimize a rate using LLM."""
        rate = await self.repository.get(rate_id)
        if not rate:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Rate not found"
            )

        # Generate optimization suggestions
        suggestions = await self.llm.optimize_rate(
            rate.model_dump(),
            {},  # No historical data needed
            optimization_params
        )

        return RateOptimizationResult(
            rate_id=rate_id,
            suggestions=suggestions,
            confidence_score=suggestions.get("confidence", 0.0)
        )

    async def validate_rate(
        self,
        rate_data: Dict[str, Any]
    ) -> RateValidationResponse:
        """Validate a rate using LLM and business rules."""
        # Get validation rules
        validation_rules = await self.rag.get_validation_rules(
            rate_data.get("category")
        )

        # Validate with LLM
        validation_result = await self.llm.validate_rate(
            rate_data,
            validation_rules
        )

        # Combine with business rule validation
        business_validation = await self.validator.validate_rate_card(
            rate_data,
            self.db,
            None  # No user_id needed for validation only
        )

        return RateValidationResponse(
            valid=validation_result["valid"] and business_validation["valid"],
            llm_validation=validation_result,
            business_validation=business_validation
        )
