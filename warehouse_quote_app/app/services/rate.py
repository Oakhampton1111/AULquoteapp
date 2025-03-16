"""Rate service for managing rate operations with AI optimization."""

from datetime import datetime
from decimal import Decimal
from typing import List, Optional, Dict, Any, Tuple, cast
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from warehouse_quote_app.app.models.rate import Rate
from warehouse_quote_app.app.repositories.rate import RateRepository
from warehouse_quote_app.app.services.validation.validation import ValidationService, ValidationResult
from warehouse_quote_app.app.services.ai.llm import LLMService
from warehouse_quote_app.app.services.ai.rag import RAGService
from warehouse_quote_app.app.schemas.rate.rate import (
    RateCreate,
    RateUpdate,
    RateResponse,
    RateOptimizationResult,
    RateValidationResponse,
    RateListResponse
)
from warehouse_quote_app.app.core.monitoring import log_event
from warehouse_quote_app.app.core.config import Settings

class RateService:
    """Service for managing rate operations with AI optimization."""

    def __init__(
        self,
        db: AsyncSession,
        llm: Optional[LLMService] = None,
        rag: Optional[RAGService] = None,
        settings: Optional[Settings] = None
    ) -> None:
        """Initialize rate service with AI capabilities.
        
        Args:
            db: Database session
            llm: Language model service for rate optimization
            rag: Retrieval-augmented generation service
            settings: Application settings
            
        Note:
            LLM and RAG services will be initialized with defaults if not provided
        """
        self.db = db
        self.repository = RateRepository(db)
        self.validator = ValidationService()
        self.llm = llm or LLMService()
        self.rag = rag or RAGService()
        self.settings = settings or Settings()

    async def create_rate(
        self,
        rate_data: RateCreate,
        user_id: int
    ) -> RateResponse:
        """Create a new rate with validation and optimization.
        
        Args:
            rate_data: Rate creation data
            user_id: ID of the user creating the rate
            
        Returns:
            RateResponse: Created rate data
            
        Raises:
            ValueError: If rate data is invalid
            HTTPException: If rate creation fails
        """
        # Validate rate data
        validation_result = await self.validator.validate_rate(rate_data)
        if not validation_result.is_valid:
            raise ValueError(f"Invalid rate data: {validation_result.errors}")

        # Create rate
        rate = await self.repository.create(rate_data)
        
        # Log event
        await log_event(
            "rate_created",
            {"rate_id": rate.id, "user_id": user_id}
        )
        
        return RateResponse.from_orm(rate)

    async def update_rate(
        self,
        rate_id: int,
        rate_data: RateUpdate,
        user_id: int
    ) -> Optional[RateResponse]:
        """Update an existing rate.
        
        Args:
            rate_id: ID of the rate to update
            rate_data: Rate update data
            user_id: ID of the user making the update
            
        Returns:
            Optional[RateResponse]: Updated rate data or None if not found
            
        Raises:
            ValueError: If rate data is invalid
            HTTPException: If update fails
        """
        # Validate update data
        validation_result = await self.validator.validate_rate_update(rate_data)
        if not validation_result.is_valid:
            raise ValueError(f"Invalid rate data: {validation_result.errors}")

        # Update rate
        rate = await self.repository.update(rate_id, rate_data)
        if not rate:
            return None

        # Log event
        await log_event(
            "rate_updated",
            {"rate_id": rate_id, "user_id": user_id}
        )

        return RateResponse.from_orm(rate)

    async def get_rate(
        self,
        rate_id: int
    ) -> Optional[RateResponse]:
        """Get rate by ID.
        
        Args:
            rate_id: ID of the rate to retrieve
            
        Returns:
            Optional[RateResponse]: Rate data or None if not found
        """
        rate = await self.repository.get(rate_id)
        if not rate:
            return None
        return RateResponse.from_orm(rate)

    async def list_rates(
        self,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None
    ) -> Tuple[List[RateListResponse], int]:
        """List rates with pagination and filtering.
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            filters: Optional filtering criteria
            
        Returns:
            Tuple[List[RateListResponse], int]: List of rates and total count
        """
        rates, total = await self.repository.get_multi(
            skip=skip,
            limit=limit,
            filters=filters or {}
        )
        return [RateListResponse.from_orm(r) for r in rates], total

    async def optimize_rate(
        self,
        rate_id: int,
        context: Dict[str, Any]
    ) -> RateOptimizationResult:
        """Optimize rate using AI models.
        
        Args:
            rate_id: ID of the rate to optimize
            context: Contextual data for optimization
            
        Returns:
            RateOptimizationResult: Optimization suggestions and confidence scores
            
        Raises:
            HTTPException: If rate not found or optimization fails
        """
        rate = await self.repository.get(rate_id)
        if not rate:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Rate not found"
            )

        # Get historical context
        historical_data = await self.rag.get_rate_context(rate_id)
        
        # Run optimization
        optimization_result = await self.llm.optimize_rate(
            rate=rate,
            context=context,
            historical_data=historical_data
        )
        
        # Log optimization attempt
        await log_event(
            "rate_optimization",
            {
                "rate_id": rate_id,
                "confidence": optimization_result.confidence_score,
                "suggested_changes": len(optimization_result.suggestions)
            }
        )
        
        return optimization_result

    async def validate_rate_rules(
        self,
        rate_id: int
    ) -> RateValidationResponse:
        """Validate rate against business rules.
        
        Args:
            rate_id: ID of the rate to validate
            
        Returns:
            RateValidationResponse: Validation results and suggestions
            
        Raises:
            HTTPException: If rate not found
        """
        rate = await self.repository.get(rate_id)
        if not rate:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Rate not found"
            )

        # Run validation
        validation_result = await self.validator.validate_rate_rules(rate)
        
        # Log validation
        await log_event(
            "rate_validation",
            {
                "rate_id": rate_id,
                "is_valid": validation_result.is_valid,
                "error_count": len(validation_result.errors)
            }
        )
        
        return RateValidationResponse(
            is_valid=validation_result.is_valid,
            errors=validation_result.errors,
            warnings=validation_result.warnings,
            suggestions=validation_result.suggestions
        )
