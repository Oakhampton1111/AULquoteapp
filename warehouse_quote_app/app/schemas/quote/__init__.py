"""Quote schemas for the Warehouse Quote System."""
from datetime import datetime, timedelta
from decimal import Decimal
from enum import Enum
from typing import (
    List, Optional, Dict, Any, Union, Literal, TypeVar,
    cast, Type, TypedDict, Annotated
)
from typing_extensions import TypeAlias
from pydantic import (
    BaseModel, ConfigDict, Field, field_validator,
    model_validator, ValidationInfo, GetCoreSchemaHandler,
    GetJsonSchemaHandler
)

from warehouse_quote_app.app.schemas.base import BaseSchema, BaseResponseSchema, BaseCreateSchema, BaseUpdateSchema
from warehouse_quote_app.app.schemas.user.customer import CustomerResponse

T = TypeVar('T', bound=BaseModel)

class ServiceType(str, Enum):
    """Service type enum."""
    PALLET_STORAGE = "Pallet Storage - Internal Racked"
    OVERSIZE_STORAGE = "Oversize Cargo - Internal Storage"
    CONTAINER_HANDLING = "Container Handling"
    CONTAINER_TRANSPORT = "Container Transport"
    CARTAGE = "Cartage"

class ContainerType(str, Enum):
    """Container type enum."""
    STANDARD = "standard"
    HIGH_CUBE = "high_cube"
    REFRIGERATED = "refrigerated"
    OPEN_TOP = "open_top"
    FLAT_RACK = "flat_rack"

class HandlingService(str, Enum):
    """Handling service enum."""
    LOADING = "loading"
    UNLOADING = "unloading"
    PACKING = "packing"
    UNPACKING = "unpacking"
    SORTING = "sorting"
    LABELING = "labeling"

class TransportMode(str, Enum):
    """Transport mode enum."""
    ROAD = "road"
    RAIL = "rail"
    SEA = "sea"
    AIR = "air"
    MULTIMODAL = "multimodal"

class QuoteStatus(str, Enum):
    """Quote status enum."""
    DRAFT = "draft"
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    EXPIRED = "expired"
    CANCELLED = "cancelled"

class ContainerSize(str, Enum):
    """Container size enum."""
    TWENTY_FOOT = "20ft"
    FORTY_FOOT = "40ft"
    FORTY_FOOT_HC = "40ft_hc"

class StorageType(str, Enum):
    """Storage type enum."""
    STANDARD = "standard"
    CLIMATE_CONTROLLED = "climate_controlled"
    HIGH_SECURITY = "high_security"
    OUTDOOR = "outdoor"
    HAZARDOUS = "hazardous"

class HandlingRequirement(str, Enum):
    """Handling requirement enum."""
    NONE = "none"
    FORKLIFT = "forklift"
    CRANE = "crane"
    MANUAL = "manual"
    SPECIAL = "special"

class StorageRequirements(BaseSchema):
    """Storage requirements model."""
    model_config = ConfigDict(
        extra='forbid',
        strict=True,
        validate_assignment=True
    )
    
    # Dimensions
    length: Optional[float] = Field(None, description="Length in meters", gt=0)
    width: Optional[float] = Field(None, description="Width in meters", gt=0)
    height: Optional[float] = Field(None, description="Height in meters", gt=0)
    volume: Optional[float] = Field(None, description="Volume in cubic meters", gt=0)
    floor_area: Optional[float] = Field(None, description="Floor area in square meters", gt=0)
    
    # Storage type
    storage_type: StorageType = Field(
        default=StorageType.STANDARD,
        description="Type of storage required"
    )
    is_palletized: bool = Field(False, description="Whether items are on pallets")
    num_pallets: Optional[int] = Field(None, description="Number of pallets if palletized", gt=0)
    pallet_type: Optional[str] = Field(None, description="Type of pallets used")
    num_bulky_items: Optional[int] = Field(None, description="Number of bulky items", ge=0)
    is_exceptionally_tall: bool = Field(False, description="Whether items exceed standard racking height")
    requires_climate_control: bool = Field(False, description="Whether items need temperature control")
    
    # Special handling
    handling_requirements: List[HandlingRequirement] = Field(
        default_factory=lambda: [HandlingRequirement.NONE],
        description="Required handling methods"
    )
    needs_handling: bool = Field(False, description="Whether items need handling services")
    is_fragile: bool = Field(False, description="Whether items require special handling")
    is_hazardous: bool = Field(False, description="Whether items contain hazardous materials")
    requires_special_equipment: bool = Field(False, description="Whether special equipment is needed")
    
    @field_validator('volume', mode='after')
    def calculate_volume(cls, v: Optional[float], info: ValidationInfo) -> Optional[float]:
        """Calculate volume if dimensions are provided."""
        if v is not None:
            return v
        data = info.data
        if all(dim is not None for dim in [data.get('length'), data.get('width'), data.get('height')]):
            return data['length'] * data['width'] * data['height']  # type: ignore
        return None

    @field_validator('floor_area', mode='after')
    def calculate_floor_area(cls, v: Optional[float], info: ValidationInfo) -> Optional[float]:
        """Calculate floor area if dimensions are provided."""
        if v is not None:
            return v
        data = info.data
        if all(dim is not None for dim in [data.get('length'), data.get('width')]):
            return data['length'] * data['width']  # type: ignore
        return None
    
    @model_validator(mode='after')
    def validate_storage_requirements(self) -> 'StorageRequirements':
        """Validate storage requirements consistency."""
        if self.is_palletized and self.num_pallets is None:
            raise ValueError("num_pallets is required when is_palletized is True")
            
        if self.requires_climate_control:
            if self.storage_type != StorageType.CLIMATE_CONTROLLED:
                raise ValueError(
                    "storage_type must be CLIMATE_CONTROLLED when requires_climate_control is True"
                )
                
        if self.is_hazardous and self.storage_type != StorageType.HAZARDOUS:
            raise ValueError("storage_type must be HAZARDOUS when is_hazardous is True")
            
        if HandlingRequirement.NONE in self.handling_requirements:
            if len(self.handling_requirements) > 1:
                raise ValueError("Cannot combine NONE with other handling requirements")
                
        return self

class Item(BaseModel):
    type: str
    quantity: int
    volume: Optional[float] = None
    weight: Optional[float] = None
    dangerous_goods_class: Optional[str] = None

    @field_validator('quantity')
    def validate_quantity(cls, v):
        if v < 1:
            raise ValueError('Quantity must be positive')
        return v

class AdditionalService(BaseModel):
    type: str
    quantity: Optional[int] = None

class ServiceDates(BaseModel):
    start_date: datetime
    end_date: datetime

    @field_validator('end_date')
    def validate_dates(cls, v, info: ValidationInfo):
        if 'start_date' in info.data and v < info.data['start_date']:
            raise ValueError('End date must be after start date')
        return v

class ServiceRequest(BaseModel):
    service_type: str
    items: List[Item]
    additional_services: Optional[List[AdditionalService]] = None
    dates: Optional[ServiceDates] = None

    @field_validator('service_type')
    def validate_service_type(cls, v):
        valid_types = ['export', 'storage', 'transport']
        if v not in valid_types:
            raise ValueError(f'Service type must be one of: {", ".join(valid_types)}')
        return v

class MultiServiceQuoteRequest(BaseModel):
    requests: List[ServiceRequest]

    @field_validator('requests')
    def validate_requests(cls, v):
        if not v:
            raise ValueError('At least one service request is required')
        return v

class ServiceBreakdown(BaseModel):
    handling: Decimal = Decimal('0')
    storage: Decimal = Decimal('0')
    additional_services: Decimal = Decimal('0')
    m041_forms: Optional[Decimal] = Decimal('0')
    transport: Optional[Decimal] = Decimal('0')
    total_cost: Decimal

class QuoteItemBase(BaseSchema):
    """Base quote item model."""
    description: str = Field(..., min_length=1, description="Item description")
    quantity: int = Field(gt=0, description="Quantity of items")
    unit_price: Decimal = Field(gt=0, max_digits=10, decimal_places=2, description="Price per unit")
    item_type: str = Field(..., min_length=1, description="Type of item for rate calculation")
    weight: Optional[float] = Field(None, gt=0, description="Weight in kilograms")
    notes: Optional[str] = Field(None, min_length=1)
    
    @field_validator('unit_price')
    def validate_unit_price(cls, v: Decimal) -> Decimal:
        """Validate unit price format."""
        if v.as_tuple().exponent < -2:  # type: ignore
            raise ValueError("unit_price cannot have more than 2 decimal places")
        return v

class QuoteItem(QuoteItemBase):
    """Quote item model with additional fields."""
    model_config = ConfigDict(from_attributes=True)
    
    id: int = Field(..., gt=0)
    quote_id: int = Field(..., gt=0)
    subtotal: Decimal = Field(gt=0, max_digits=10, decimal_places=2, description="Item subtotal before discounts")
    discount_amount: Optional[Decimal] = Field(None, ge=0, max_digits=10, decimal_places=2, description="Discount amount if any")
    final_price: Decimal = Field(gt=0, max_digits=10, decimal_places=2, description="Final price after discounts")
    
    @model_validator(mode='after')
    def validate_amounts(self) -> 'QuoteItem':
        """Validate price calculations."""
        calculated_subtotal = self.quantity * self.unit_price
        if self.subtotal != calculated_subtotal:
            raise ValueError("subtotal must equal quantity * unit_price")
            
        if self.discount_amount is not None:
            if self.discount_amount > self.subtotal:
                raise ValueError("discount_amount cannot be greater than subtotal")
            calculated_final = self.subtotal - self.discount_amount
            if self.final_price != calculated_final:
                raise ValueError("final_price must equal subtotal - discount_amount")
        elif self.final_price != self.subtotal:
            raise ValueError("final_price must equal subtotal when no discount is applied")
            
        return self

class QuoteBase(BaseSchema):
    """Base quote model."""
    model_config = ConfigDict(from_attributes=True)
    
    items: List[QuoteItemBase] = Field(..., min_items=1)
    delivery_date: datetime
    delivery_address: str = Field(..., min_length=1)
    special_instructions: Optional[str] = Field(None, min_length=1)
    storage_requirements: StorageRequirements
    service_requests: List[ServiceRequest]
    
    @field_validator('delivery_date')
    def validate_delivery_date(cls, v: datetime) -> datetime:
        """Validate delivery date is in the future."""
        if v <= datetime.utcnow():
            raise ValueError("delivery_date must be in the future")
        return v

class QuoteRequest(BaseSchema):
    """Quote request model."""
    model_config = ConfigDict(extra='forbid')
    
    storage_requirements: StorageRequirements
    delivery_postcode: str = Field(
        ...,
        min_length=4,
        max_length=10,
        description="Delivery location postcode"
    )
    requires_timed_delivery: bool = Field(
        False,
        description="Whether delivery needs to be at specific time"
    )
    requires_container_transport: bool = Field(
        False,
        description="Whether container transport is needed"
    )
    container_size: Optional[ContainerSize] = Field(
        None,
        description="Container size if container transport is required"
    )
    service_requests: List[ServiceRequest]
    
    @model_validator(mode='after')
    def validate_container_transport(self) -> 'QuoteRequest':
        """Validate container transport requirements."""
        if self.requires_container_transport and not self.container_size:
            raise ValueError("container_size is required when requires_container_transport is True")
        return self

Quote: TypeAlias = 'QuoteResponse'

class QuoteCreate(BaseCreateSchema[Quote]):
    """Quote creation model."""
    customer_id: int = Field(..., gt=0)
    quote_request: QuoteRequest

class QuoteUpdate(BaseUpdateSchema[Quote]):
    """Quote update model."""
    model_config = ConfigDict(extra='forbid')
    
    items: Optional[List[QuoteItemBase]] = Field(None, min_items=1)
    delivery_date: Optional[datetime] = None
    delivery_address: Optional[str] = Field(None, min_length=1)
    special_instructions: Optional[str] = Field(None, min_length=1)
    storage_requirements: Optional[StorageRequirements] = None
    service_requests: Optional[List[ServiceRequest]] = None
    
    @field_validator('delivery_date')
    def validate_delivery_date(cls, v: Optional[datetime]) -> Optional[datetime]:
        """Validate delivery date if provided."""
        if v is not None and v <= datetime.utcnow():
            raise ValueError("delivery_date must be in the future")
        return v

class QuoteStatusUpdate(BaseSchema):
    """Quote status update model."""
    model_config = ConfigDict(extra='forbid')
    
    status: QuoteStatus
    rejection_reason: Optional[str] = Field(None, min_length=1)
    
    @model_validator(mode='after')
    def validate_status_update(self) -> 'QuoteStatusUpdate':
        """Validate status update consistency."""
        if self.status == QuoteStatus.REJECTED and not self.rejection_reason:
            raise ValueError("rejection_reason is required when status is REJECTED")
        if self.status != QuoteStatus.REJECTED and self.rejection_reason:
            raise ValueError("rejection_reason should only be provided when status is REJECTED")
        return self

class CustomerInfo(BaseSchema):
    """Customer info model."""
    model_config = ConfigDict(from_attributes=True)
    
    id: int = Field(..., gt=0)
    name: str = Field(..., min_length=1)
    email: str = Field(..., min_length=5)
    phone: str = Field(..., min_length=8)

class QuoteResponse(BaseResponseSchema):
    """Quote response model."""
    model_config = ConfigDict(from_attributes=True)
    
    created_by_id: int = Field(..., gt=0)
    customer: CustomerResponse
    status: QuoteStatus
    total_price: Decimal = Field(gt=0, max_digits=10, decimal_places=2, description="Total price")
    items: List[QuoteItem]
    storage_requirements: StorageRequirements
    service_breakdown: Dict[str, ServiceBreakdown]
    accepted_at: Optional[datetime] = None
    rejected_at: Optional[datetime] = None
    rejection_reason: Optional[str] = None
    
    @model_validator(mode='after')
    def validate_response(self) -> 'QuoteResponse':
        """Validate response consistency."""
        if self.status == QuoteStatus.ACCEPTED and not self.accepted_at:
            raise ValueError("accepted_at is required when status is ACCEPTED")
        if self.status == QuoteStatus.REJECTED:
            if not self.rejected_at:
                raise ValueError("rejected_at is required when status is REJECTED")
            if not self.rejection_reason:
                raise ValueError("rejection_reason is required when status is REJECTED")
        return self

class QuoteDetailResponse(QuoteResponse):
    """Detailed quote response model with additional information for customer views."""
    items: List[QuoteItem]
    delivery_date: datetime
    delivery_address: str
    special_instructions: Optional[str] = None
    valid_until: datetime
    subtotal: Decimal = Field(gt=0, max_digits=10, decimal_places=2, description="Subtotal before tax and fees")
    tax_amount: Decimal = Field(ge=0, max_digits=10, decimal_places=2, description="Tax amount")
    handling_fees: Decimal = Field(ge=0, max_digits=10, decimal_places=2, description="Handling fees")
    discounts: Decimal = Field(ge=0, max_digits=10, decimal_places=2, description="Total discounts applied")
    payment_terms: Optional[str] = None
    notes: Optional[str] = None
    
    @field_validator('valid_until')
    def validate_valid_until(cls, v: datetime, info: ValidationInfo) -> datetime:
        """Ensure valid_until is after created_at."""
        data = info.data
        created_at = data.get('created_at')
        if created_at and v <= created_at:
            raise ValueError("valid_until must be after created_at")
        return v
    
    @model_validator(mode='after')
    def validate_amounts(self) -> 'QuoteDetailResponse':
        """Validate price calculations."""
        calculated_total = self.subtotal + self.tax_amount + self.handling_fees - self.discounts
        if self.total_price != calculated_total:
            raise ValueError(
                "total_price must equal subtotal + tax_amount + handling_fees - discounts"
            )
        return self

class RateCardBase(BaseSchema):
    """Rate card base model."""
    model_config = ConfigDict(
        extra='forbid',
        arbitrary_types_allowed=True
    )
    
    storage_type: StorageType
    rate_per_unit: Decimal
    minimum_fee: Decimal
    rate_limit_per_minute: Optional[int] = Field(None, gt=0)  # Add if valid

class QuoteMetrics(BaseSchema):
    """Quote metrics model."""
    model_config = ConfigDict(extra='forbid')
    
    total_quotes: int = Field(ge=0, default=0)
    accepted_quotes: int = Field(ge=0, default=0)
    rejected_quotes: int = Field(ge=0, default=0)
    pending_quotes: int = Field(ge=0, default=0)
    expired_quotes: int = Field(ge=0, default=0)
    total_value: Decimal = Field(ge=0, max_digits=12, decimal_places=2, description="Total value of all quotes")
    average_value: Decimal = Field(ge=0, max_digits=10, decimal_places=2, description="Average quote value")
    
    @field_validator('average_value', mode='after')
    def calculate_average(cls, v: Decimal, info: ValidationInfo) -> Decimal:
        """Calculate average value if not provided."""
        data = info.data
        if v == 0 and data.get('total_quotes', 0) > 0:
            total_value = data.get('total_value', Decimal('0'))
            total_quotes = data.get('total_quotes', 0)
            if total_quotes > 0:
                return total_value / Decimal(str(total_quotes))
        return v
    
    @model_validator(mode='after')
    def validate_metrics(self) -> 'QuoteMetrics':
        """Validate metrics consistency."""
        total = (
            self.accepted_quotes +
            self.rejected_quotes +
            self.pending_quotes +
            self.expired_quotes
        )
        if total != self.total_quotes:
            raise ValueError(
                "Sum of quote statuses must equal total_quotes"
            )
        return self

class QuoteReport(BaseSchema):
    """Quote report model."""
    model_config = ConfigDict(extra='forbid')
    
    metrics: QuoteMetrics
    quotes: List[QuoteResponse] = Field(default_factory=list)
    period_start: datetime
    period_end: datetime
    
    @field_validator('period_end')
    def validate_period(cls, v: datetime, info: ValidationInfo) -> datetime:
        """Validate report period."""
        data = info.data
        period_start = data.get('period_start')
        if period_start and v <= period_start:
            raise ValueError("period_end must be after period_start")
        return v

class QuoteErrorResponse(BaseSchema):
    """Standard error response model for quote routes."""
    model_config = ConfigDict(extra='forbid')
    
    detail: str = Field(..., min_length=1, description="Error message")
    code: str = Field(..., min_length=1, description="Error code for client handling")
    field: Optional[str] = None

class ServiceSelection(BaseSchema):
    """Schema for selecting service options. Placeholder implementation."""
    pass


class ThreePLServices(BaseSchema):
    """Schema for third-party logistics services. Placeholder implementation."""
    pass


class TransportServices(BaseSchema):
    """Schema for transport services. Placeholder implementation."""
    pass

class QuoteFilter(BaseModel):
    """Quote filter schema."""
    
    status: Optional[str] = Field(None, description="Filter by quote status")
    start_date: Optional[datetime] = Field(None, description="Filter by start date")
    end_date: Optional[datetime] = Field(None, description="Filter by end date")
    
    @field_validator('end_date')
    def validate_date_range(cls, v, values):
        """Validate that end_date is after start_date if both are provided."""
        if v and values.get('start_date') and v < values['start_date']:
            raise ValueError("end_date must be after start_date")
        return v
    
    @field_validator('status')
    def validate_status(cls, v):
        """Validate status value."""
        if v and v not in QuoteStatus.__members__:
            raise ValueError(f"Invalid status. Must be one of: {', '.join(QuoteStatus.__members__)}")
        return v

class BulkQuoteItem(BaseModel):
    quote_id: str
    customer_id: str
    requests: List[ServiceRequest]

    @field_validator('quote_id')
    def validate_quote_id(cls, v):
        if not v:
            raise ValueError('Quote ID is required')
        return v

    @field_validator('customer_id')
    def validate_customer_id(cls, v):
        if not v:
            raise ValueError('Customer ID is required')
        return v

class BulkQuoteRequest(BaseModel):
    quotes: List[BulkQuoteItem]

    @field_validator('quotes')
    def validate_quotes(cls, v):
        if not v:
            raise ValueError('At least one quote is required')
        
        # Check for duplicate quote IDs
        quote_ids = [q.quote_id for q in v]
        if len(quote_ids) != len(set(quote_ids)):
            raise ValueError('Duplicate quote IDs are not allowed')
        
        return v

class BulkQuoteResult(BaseModel):
    quote_id: str
    customer_id: str
    result: QuoteResponse

class BulkQuoteError(BaseModel):
    quote_id: str
    customer_id: str
    error: str

class BulkQuoteResponse(BaseModel):
    results: List[BulkQuoteResult]
    errors: List[BulkQuoteError]
    total_quotes: int
    successful_quotes: int
    failed_quotes: int

    @field_validator('successful_quotes')
    def validate_successful_quotes(cls, v, values):
        if 'total_quotes' in values and v > values['total_quotes']:
            raise ValueError('Successful quotes cannot exceed total quotes')
        return v

    @field_validator('failed_quotes')
    def validate_failed_quotes(cls, v, values):
        if 'total_quotes' in values and v > values['total_quotes']:
            raise ValueError('Failed quotes cannot exceed total quotes')
        return v

class ServiceComparison(BaseModel):
    original_quote: QuoteResponse
    variations: List[QuoteResponse]
    savings_potential: Decimal
    recommended_option: QuoteResponse
    comparison_factors: Dict[str, str]

    @field_validator('savings_potential')
    def validate_savings(cls, v):
        if v < 0:
            raise ValueError('Savings potential cannot be negative')
        return v

    @field_validator('recommended_option')
    def validate_recommendation(cls, v, info: ValidationInfo):
        if 'original_quote' in info.data and v.total_cost > info.data['original_quote'].total_cost:
            raise ValueError('Recommended option should not cost more than original quote')
        return v

class QuoteListResponse(BaseModel):
    """Schema for returning a list of quotes with pagination metadata."""
    model_config = ConfigDict(from_attributes=True)
    
    items: List[QuoteResponse] = Field(..., description="List of quotes")
    total: int = Field(..., description="Total number of quotes matching the filter criteria")
    page: int = Field(1, ge=1, description="Current page number")
    page_size: int = Field(..., gt=0, description="Number of items per page")
    pages: int = Field(..., ge=1, description="Total number of pages")
    
    @model_validator(mode='after')
    def validate_pagination(self) -> 'QuoteListResponse':
        """Validate pagination consistency."""
        if self.page > self.pages and self.total > 0:
            raise ValueError(f"Page number {self.page} exceeds total pages {self.pages}")
        
        if self.page_size * self.pages < self.total and self.pages > 1:
            raise ValueError(f"Pagination inconsistency: {self.page_size} * {self.pages} < {self.total}")
            
        return self
