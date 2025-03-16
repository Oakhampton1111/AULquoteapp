"""
Rate schema exports.
"""

from typing import List, Optional
from pydantic import BaseModel, Field

from .rate import (
    RateBase,
    RateCreate,
    RateUpdate,
    RateResponse
)

from .rate_card import (
    Rate,
    RateCardBase,
    RateCardCreate,
    RateCardUpdate,
    RateCardResponse,
    RateCardSettingsBase,
    RateCardSettingsCreate,
    RateCardSettingsUpdate,
    RateCardSettingsResponse,
    CustomerRateCardBase,
    CustomerRateCardCreate,
    CustomerRateCardUpdate,
    CustomerRateCardResponse
)

from .rate_optimization import (
    OptimizationRequest,
    OptimizationResponse,
    ValidationRuleBase,
    ValidationRuleCreate,
    ValidationRule,
    OptimizationMetrics
)

# Define missing RateFilter class
class RateFilter(BaseModel):
    """Filter criteria for rates."""
    name: Optional[str] = None
    category: Optional[str] = None
    is_active: Optional[bool] = None
    service_types: Optional[List[str]] = Field(default=None)
    min_rate: Optional[float] = None
    max_rate: Optional[float] = None

# Import enums from the correct location
try:
    from app.models.types import RateCategory, RateType
except ImportError:
    # Define fallback enums if the types module doesn't exist
    from enum import Enum, auto
    
    class RateCategory(str, Enum):
        STANDARD = "standard"
        PREMIUM = "premium"
        DISCOUNT = "discount"
        SPECIAL = "special"
    
    class RateType(str, Enum):
        STORAGE = "storage"
        HANDLING = "handling"
        CONTAINER = "container"
        TRANSPORT = "transport"
        EXPORT = "export"
        ALL = "all"

__all__ = [
    'Rate',
    'RateBase',
    'RateCreate',
    'RateUpdate',
    'RateResponse',
    'RateCategory',
    'RateType',
    'RateFilter',
    'RateCardBase',
    'RateCardCreate',
    'RateCardUpdate',
    'RateCardResponse',
    'RateCardSettingsBase',
    'RateCardSettingsCreate',
    'RateCardSettingsUpdate',
    'RateCardSettingsResponse',
    'CustomerRateCardBase',
    'CustomerRateCardCreate',
    'CustomerRateCardUpdate',
    'CustomerRateCardResponse',
    'OptimizationRequest',
    'OptimizationResponse',
    'ValidationRuleBase',
    'ValidationRuleCreate',
    'ValidationRule',
    'OptimizationMetrics'
]
