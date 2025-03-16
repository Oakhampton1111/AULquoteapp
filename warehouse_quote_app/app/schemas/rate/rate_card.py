"""Rate card schemas."""
from pydantic import BaseModel, ConfigDict, Field, field_validator
from typing import List, Optional, Dict, Any, Union, Annotated
from datetime import datetime
from decimal import Decimal
from enum import Enum
from warehouse_quote_app.app.schemas.base import BaseSchema, BaseResponseSchema
from warehouse_quote_app.app.models.types import RateCategory, RateType

class ClientType(str, Enum):
    """Client type enumeration."""
    RETAIL = "retail"
    WHOLESALE = "wholesale"
    ENTERPRISE = "enterprise"
    GOVERNMENT = "government"

class VolumeDiscount(BaseSchema):
    """Volume discount configuration."""
    min_quantity: Annotated[int, Field(gt=0, description="Minimum quantity for discount")]
    discount_percentage: Annotated[Decimal, Field(gt=0, le=100, description="Discount percentage as decimal")]

class Rate(BaseSchema):
    """Individual rate configuration."""
    item_type: Annotated[str, Field(min_length=1, description="Type of item being rated")]
    base_rate: Annotated[Decimal, Field(gt=0, description="Base rate as decimal")]
    volume_discounts: List[VolumeDiscount] = Field(default_factory=list)

class RateCardSettingsBase(BaseSchema):
    """Base schema for rate card settings."""
    name: Annotated[str, Field(min_length=1)]
    description: Optional[str] = None
    is_active: bool = True
    minimum_charge: Annotated[Decimal, Field(default=Decimal("0.00"), ge=0, description="Minimum charge amount")]
    handling_fee_percentage: Annotated[Decimal, Field(default=Decimal("0.00"), ge=0, le=100, description="Handling fee percentage")]
    tax_rate: Annotated[Decimal, Field(default=Decimal("0.10"), ge=0, le=100, description="Tax rate percentage")]
    volume_discount_tiers: Dict[str, Dict[str, Union[int, Decimal]]] = Field(
        default_factory=lambda: {
            "tier1": {"min_amount": 1000, "discount": Decimal("0.05")},
            "tier2": {"min_amount": 5000, "discount": Decimal("0.10")},
            "tier3": {"min_amount": 10000, "discount": Decimal("0.15")}
        }
    )
    max_quote_items: Annotated[int, Field(default=100, gt=0)]
    max_quote_value: Annotated[Decimal, Field(default=Decimal("100000.00"), gt=0)]
    requires_approval_above: Annotated[Decimal, Field(default=Decimal("10000.00"), gt=0)]

class RateCardSettingsCreate(RateCardSettingsBase):
    """Schema for creating rate card settings."""
    max_quote_items: Annotated[int, Field(gt=0, description="Maximum number of items per quote")]
    max_quote_value: Annotated[Decimal, Field(gt=0, description="Maximum quote value allowed")]
    requires_approval_above: Annotated[Decimal, Field(gt=0, description="Quote value that requires approval")]

class RateCardSettingsUpdate(BaseSchema):
    """Schema for updating rate card settings."""
    name: Optional[Annotated[str, Field(min_length=1)]] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None
    minimum_charge: Optional[Annotated[Decimal, Field(ge=0)]] = None
    handling_fee_percentage: Optional[Annotated[Decimal, Field(ge=0, le=100)]] = None
    tax_rate: Optional[Annotated[Decimal, Field(ge=0, le=100)]] = None
    volume_discount_tiers: Optional[Dict[str, Dict[str, Union[int, Decimal]]]] = None
    max_quote_items: Optional[Annotated[int, Field(gt=0)]] = None
    max_quote_value: Optional[Annotated[Decimal, Field(gt=0)]] = None
    requires_approval_above: Optional[Annotated[Decimal, Field(gt=0)]] = None

class RateCardSettingsResponse(RateCardSettingsBase, BaseResponseSchema):
    """Schema for rate card settings response."""
    model_config = ConfigDict(from_attributes=True)
    id: int

class RateCardBase(BaseSchema):
    """Base schema for rate card."""
    name: Annotated[str, Field(min_length=1)]
    description: Optional[str] = None
    rate_type: RateType = Field(default=RateType.ALL)
    category: RateCategory = Field(default=RateCategory.STANDARD)
    rates: Dict[str, Decimal] = Field(default_factory=dict)
    additional_charges: Dict[str, Any] = Field(default_factory=dict)
    is_active: bool = True
    effective_from: datetime = Field(..., description="When the rate card becomes effective")
    effective_until: Optional[datetime] = None
    settings_id: Optional[int] = None

    @field_validator('rates')
    def validate_rates(cls, v: Dict[str, Decimal]) -> Dict[str, Decimal]:
        """Validate that all rates are positive."""
        for rate in v.values():
            if rate <= 0:
                raise ValueError("Rates must be positive")
        return v

class RateCardCreate(RateCardBase):
    """Schema for creating rate card."""
    rates: Dict[str, Dict[str, Dict[str, Any]]] = Field(
        default_factory=dict,
        description="Rate configuration by service type and item type"
    )

class RateCardUpdate(BaseSchema):
    """Schema for updating rate card."""
    name: Optional[Annotated[str, Field(min_length=1)]] = None
    description: Optional[str] = None
    rate_type: Optional[RateType] = None
    category: Optional[RateCategory] = None
    rates: Optional[Dict[str, Decimal]] = None
    additional_charges: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None
    effective_until: Optional[datetime] = None
    settings_id: Optional[int] = None

class RateCardResponse(RateCardBase, BaseResponseSchema):
    """Schema for rate card response."""
    model_config = ConfigDict(from_attributes=True)
    id: int
    rates: Dict[str, Dict[str, Dict[str, Any]]]
    settings: Optional[RateCardSettingsResponse] = None

class CalculationItem(BaseSchema):
    """Schema for rate calculation item."""
    item_type: Annotated[str, Field(min_length=1, description="Type of item to calculate rate for")]
    quantity: Annotated[int, Field(gt=0, description="Quantity of items")]

class CalculateQuoteRequest(BaseSchema):
    """Schema for quote calculation request."""
    items: Annotated[List[CalculationItem], Field(min_items=1)]

class PriceBreakdown(BaseSchema):
    """Schema for price breakdown."""
    item_type: str
    quantity: Annotated[int, Field(gt=0)]
    base_rate: Annotated[Decimal, Field(gt=0)]
    base_price: Annotated[Decimal, Field(gt=0)]
    discount_percentage: Annotated[Decimal, Field(ge=0, le=100)]
    discount_amount: Annotated[Decimal, Field(ge=0)]
    final_price: Annotated[Decimal, Field(gt=0)]

class QuotePriceResponse(BaseSchema):
    """Schema for quote price response."""
    total_price: Annotated[Decimal, Field(gt=0)]
    breakdown: List[PriceBreakdown]

class CustomerRateCardBase(BaseSchema):
    """Base schema for customer-specific rate card."""
    customer_id: int = Field(..., description="ID of the customer")
    rate_card_id: int = Field(..., description="Original rate card ID")
    custom_rates: Optional[Dict[str, Decimal]] = Field(default_factory=dict, description="Override rates if applicable")


class CustomerRateCardCreate(CustomerRateCardBase):
    """Schema for creating a customer-specific rate card."""
    pass


class CustomerRateCardUpdate(BaseSchema):
    """Schema for updating a customer-specific rate card."""
    customer_id: Optional[int] = Field(None, description="ID of the customer")
    rate_card_id: Optional[int] = Field(None, description="Original rate card ID")
    custom_rates: Optional[Dict[str, Decimal]] = Field(None, description="Override rates if applicable")


class CustomerRateCardResponse(CustomerRateCardBase, BaseResponseSchema):
    """Schema for customer-specific rate card response."""
    id: int
