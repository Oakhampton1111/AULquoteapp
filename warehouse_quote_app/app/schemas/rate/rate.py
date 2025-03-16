from pydantic import BaseModel, field_validator, ConfigDict
from typing import Optional, List, Dict, Any
from decimal import Decimal
from enum import Enum

class RateCategory(str, Enum):
    """Categories of warehouse rates."""
    STORAGE = "storage"
    HANDLING = "handling"
    ADDITIONAL = "additional"
    CONTAINER = "container"
    TRANSPORT = "transport"
    EXPORT = "export"

class RateUnit(str, Enum):
    """Units for warehouse rates."""
    ITEM = "item"
    PALLET = "pallet"
    BOX = "box"
    CONTAINER = "container"
    KG = "kg"
    HOUR = "hour"
    DAY = "day"
    FLAT = "flat"

class RateBase(BaseModel):
    name: str
    description: Optional[str] = None
    category: RateCategory
    rate: float
    unit: RateUnit
    is_active: bool = True

class RateCreate(RateBase):
    @field_validator('rate')
    def validate_rate(cls, v):
        if v < 0:
            raise ValueError('Rate cannot be negative')
        return float(v)

class RateUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    category: Optional[RateCategory] = None
    rate: Optional[float] = None
    unit: Optional[RateUnit] = None
    is_active: Optional[bool] = None
    
    @field_validator('rate')
    def validate_rate(cls, v):
        if v is not None and v < 0:
            raise ValueError('Rate cannot be negative')
        return v

class RateResponse(RateBase):
    id: int
    
    model_config = ConfigDict(orm_mode=True)

class RateListResponse(BaseModel):
    rates: List[RateResponse]
    count: int

class RateOptimizationResult(BaseModel):
    """Result of rate optimization with AI."""
    original_rate: RateResponse
    optimized_rate: RateResponse
    confidence_score: float
    reasoning: str
    market_analysis: Optional[Dict[str, Any]] = None

class RateValidationResponse(BaseModel):
    """Response from rate validation."""
    is_valid: bool
    errors: List[str] = []
    warnings: List[str] = []
    suggestions: List[str] = []
