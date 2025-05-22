"""
Quote-specific schemas for the Warehouse Quote System.

This module defines Pydantic models for quote operations including:
1. Quote creation
2. Quote updates
3. Quote responses
4. Quote details
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from decimal import Decimal
from pydantic import BaseModel, Field, ConfigDict

from warehouse_quote_app.app.models.quote import QuoteStatus

class QuoteBase(BaseModel):
    """Base quote schema."""
    customer_id: int
    deal_id: Optional[int] = None
    total_amount: Decimal
    service_type: str
    storage_requirements: Optional[Dict[str, Any]] = None
    transport_services: Optional[Dict[str, Any]] = None
    special_requirements: Optional[Dict[str, Any]] = None

class QuoteCreate(QuoteBase):
    """Quote creation schema."""
    pass

class QuoteUpdate(BaseModel):
    """Quote update schema."""
    total_amount: Optional[Decimal] = None
    service_type: Optional[str] = None
    status: Optional[str] = None
    deal_id: Optional[int] = None
    storage_requirements: Optional[Dict[str, Any]] = None
    transport_services: Optional[Dict[str, Any]] = None
    special_requirements: Optional[Dict[str, Any]] = None
    
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True
    )

class QuoteResponse(QuoteBase):
    """Quote response schema."""
    id: int
    status: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    submitted_at: Optional[datetime] = None
    accepted_at: Optional[datetime] = None
    rejected_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True
    )

class QuoteDetailResponse(QuoteResponse):
    """Quote detail response schema with additional information."""
    customer_name: str
    customer_email: str
    customer_phone: Optional[str] = None
    customer_company: Optional[str] = None
    admin_notes: Optional[str] = None
    history: List[Dict[str, Any]] = []
    
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True
    )

class QuoteStatusUpdate(BaseModel):
    """Quote status update schema."""
    status: str = Field(..., description="New status for the quote")
    notes: Optional[str] = None
    
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True
    )

class QuoteItemBase(BaseModel):
    """Base schema for quote items."""
    service_name: str
    description: Optional[str] = None
    quantity: int = 1
    unit_price: Decimal
    total_price: Decimal
    specifications: Optional[Dict[str, Any]] = None

class QuoteItemCreate(QuoteItemBase):
    """Schema for creating a quote item."""
    pass

class QuoteItemUpdate(BaseModel):
    """Schema for updating a quote item."""
    service_name: Optional[str] = None
    description: Optional[str] = None
    quantity: Optional[int] = None
    unit_price: Optional[Decimal] = None
    total_price: Optional[Decimal] = None
    specifications: Optional[Dict[str, Any]] = None
    
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True
    )

class QuoteItemResponse(QuoteItemBase):
    """Schema for quote item response."""
    id: int
    quote_id: int
    
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True
    )

class QuoteNegotiationRequest(BaseModel):
    """Quote negotiation request schema."""
    proposed_amount: Decimal = Field(..., description="Customer's proposed amount for the quote")
    reason: str = Field(..., description="Reason for the negotiation request")
    additional_notes: Optional[str] = None
    
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True
    )

class QuoteNegotiationResponse(BaseModel):
    """Quote negotiation response schema."""
    quote_id: int
    original_amount: Decimal
    proposed_amount: Decimal
    status: str = Field(..., description="Status of the negotiation (pending, accepted, rejected)")
    admin_response: Optional[str] = None
    created_at: datetime
    
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True
    )

__all__ = [
    'QuoteBase',
    'QuoteCreate',
    'QuoteUpdate',
    'QuoteResponse',
    'QuoteDetailResponse',
    'QuoteStatusUpdate',
    'QuoteItemBase',
    'QuoteItemCreate',
    'QuoteItemUpdate',
    'QuoteItemResponse',
    'QuoteNegotiationRequest',
    'QuoteNegotiationResponse'
]
