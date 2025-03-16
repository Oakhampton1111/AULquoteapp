"""Validation service for quotes and rates."""

from datetime import datetime
from typing import Dict, Any, Optional, List, Union
from pydantic import BaseModel, ValidationError, Field, field_validator
from sqlalchemy.orm import Session

from warehouse_quote_app.app.core.monitoring import get_logger
from warehouse_quote_app.app.schemas.quote import QuoteCreate, QuoteUpdate
from warehouse_quote_app.app.schemas.rate.rate import RateCreate, RateUpdate, RateValidationResponse
from warehouse_quote_app.app.models.rate import Rate
from warehouse_quote_app.app.core.exceptions import ValidationError

# Initialize logger
logger = get_logger(__name__)

class ValidationResult(BaseModel):
    """Validation result model."""
    is_valid: bool = Field(default=False, description="Whether validation passed")
    errors: List[str] = Field(default_factory=list, description="List of validation errors")
    warnings: List[str] = Field(default_factory=list, description="List of validation warnings")
    suggestions: List[str] = Field(default_factory=list, description="List of improvement suggestions")

class StorageRequirements(BaseModel):
    """Storage requirements validation model."""
    floor_area: float = Field(..., gt=0, description="Floor area in square meters")
    length: Optional[float] = Field(None, gt=0, description="Length in meters")
    width: Optional[float] = Field(None, gt=0, description="Width in meters")
    height: Optional[float] = Field(None, gt=0, description="Height in meters")

    @field_validator("floor_area")
    def validate_floor_area(cls, v: float) -> float:
        """Validate floor area is reasonable."""
        if v > 10000:  # 10,000 square meters
            raise ValueError("Floor area seems unreasonably large")
        return v

class TransportServices(BaseModel):
    """Transport services validation model."""
    destination_postcode: str = Field(..., min_length=4, max_length=10)
    num_shipments: int = Field(..., gt=0, le=1000)

    @field_validator("destination_postcode")
    def validate_postcode(cls, v: str) -> str:
        """Validate postcode format."""
        if not v.replace(" ", "").isalnum():
            raise ValueError("Postcode must contain only letters and numbers")
        return v

class ValidationService:
    """Service for validating quotes and rates."""

    async def validate_rate(
        self,
        rate_data: Union[RateCreate, RateUpdate]
    ) -> ValidationResult:
        """Validate rate data against schema and business rules.
        
        Args:
            rate_data: Rate data to validate
            
        Returns:
            ValidationResult: Validation results including errors and suggestions
            
        Raises:
            ValidationError: If validation fails with critical errors
        """
        result = ValidationResult()
        
        try:
            # Schema validation is handled by Pydantic
            if isinstance(rate_data, RateUpdate):
                # For updates, we need to check if any field is set
                if not any(
                    getattr(rate_data, field) is not None
                    for field in rate_data.model_fields
                ):
                    result.errors.append("At least one field must be provided for update")
                    return result
            
            # Business rules validation
            if hasattr(rate_data, "valid_from") and hasattr(rate_data, "valid_until"):
                if rate_data.valid_from and rate_data.valid_until:
                    if rate_data.valid_from >= rate_data.valid_until:
                        result.errors.append(
                            "Valid from date must be before valid until date"
                        )
            
            if hasattr(rate_data, "rate") and rate_data.rate is not None:
                if rate_data.rate <= 0:
                    result.errors.append("Rate must be greater than 0")
                elif rate_data.rate > 10000:
                    result.warnings.append(
                        "Rate seems unusually high, please verify"
                    )
            
            # Set validation status
            result.is_valid = len(result.errors) == 0
            
            # Add suggestions if appropriate
            if result.is_valid and len(result.warnings) > 0:
                result.suggestions.append(
                    "Consider reviewing the warnings before proceeding"
                )
            
        except ValidationError as e:
            result.errors.extend(str(err) for err in e.errors())
            logger.error(f"Rate validation error: {e}")
        
        return result

    async def validate_quote(
        self,
        quote_data: Union[QuoteCreate, QuoteUpdate]
    ) -> ValidationResult:
        """Validate quote data against schema and business rules.
        
        Args:
            quote_data: Quote data to validate
            
        Returns:
            ValidationResult: Validation results including errors and suggestions
            
        Raises:
            ValidationError: If validation fails with critical errors
        """
        result = ValidationResult()
        
        try:
            # Schema validation is handled by Pydantic
            if isinstance(quote_data, QuoteUpdate):
                if not any(
                    getattr(quote_data, field) is not None
                    for field in quote_data.model_fields
                ):
                    result.errors.append("At least one field must be provided for update")
                    return result
            
            # Business rules validation
            if hasattr(quote_data, "storage_requirements"):
                try:
                    StorageRequirements(**quote_data.storage_requirements)
                except ValidationError as e:
                    result.errors.extend(
                        f"Storage requirements: {err}" for err in e.errors()
                    )
            
            if hasattr(quote_data, "transport_services"):
                try:
                    TransportServices(**quote_data.transport_services)
                except ValidationError as e:
                    result.errors.extend(
                        f"Transport services: {err}" for err in e.errors()
                    )
            
            # Set validation status
            result.is_valid = len(result.errors) == 0
            
            # Add suggestions
            if result.is_valid:
                if hasattr(quote_data, "notes") and not quote_data.notes:
                    result.suggestions.append(
                        "Consider adding notes for better tracking"
                    )
            
        except ValidationError as e:
            result.errors.extend(str(err) for err in e.errors())
            logger.error(f"Quote validation error: {e}")
        
        return result

    async def validate_rate_rules(
        self,
        rate: Rate
    ) -> ValidationResult:
        """Validate rate against configurable business rules.
        
        Args:
            rate: Rate model to validate
            
        Returns:
            ValidationResult: Validation results including errors and suggestions
        """
        result = ValidationResult()
        
        # Get active rules for rate type
        rules = await self._get_active_rules(rate.type)
        
        for rule in rules:
            # Apply rule validation
            rule_result = await self._apply_rule(rate, rule)
            if not rule_result.is_valid:
                result.errors.extend(rule_result.errors)
                result.warnings.extend(rule_result.warnings)
        
        # Set validation status
        result.is_valid = len(result.errors) == 0
        
        return result

    async def _get_active_rules(self, rate_type: str) -> List[Dict[str, Any]]:
        """Get active validation rules for rate type.
        
        Args:
            rate_type: Type of rate to get rules for
            
        Returns:
            List[Dict[str, Any]]: List of active rules
        """
        # TODO: Implement rule retrieval from database or configuration
        return []

    async def _apply_rule(
        self,
        rate: Rate,
        rule: Dict[str, Any]
    ) -> ValidationResult:
        """Apply a single validation rule to a rate.
        
        Args:
            rate: Rate to validate
            rule: Rule to apply
            
        Returns:
            ValidationResult: Result of applying the rule
        """
        # TODO: Implement rule application logic
        return ValidationResult(is_valid=True)
