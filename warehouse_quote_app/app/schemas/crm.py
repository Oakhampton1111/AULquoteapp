"""CRM schemas."""
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict

from warehouse_quote_app.app.models.crm import InteractionType, DealStage

class InteractionBase(BaseModel):
    """Base schema for customer interactions."""
    type: InteractionType
    description: str
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)

class InteractionCreate(InteractionBase):
    """Schema for creating a customer interaction."""
    pass

class InteractionUpdate(InteractionBase):
    """Schema for updating a customer interaction."""
    type: Optional[InteractionType] = None
    description: Optional[str] = None

class InteractionRead(InteractionBase):
    """Schema for reading a customer interaction."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    customer_id: int
    agent_id: int
    created_at: datetime
    updated_at: datetime

class DealBase(BaseModel):
    """Base schema for deals."""
    title: str
    description: Optional[str] = None
    value: Optional[float] = None
    probability: Optional[int] = Field(None, ge=0, le=100)
    expected_close_date: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)

class DealCreate(DealBase):
    """Schema for creating a deal."""
    pass

class DealUpdate(DealBase):
    """Schema for updating a deal."""
    title: Optional[str] = None
    stage: Optional[DealStage] = None

class DealRead(DealBase):
    """Schema for reading a deal."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    customer_id: int
    stage: DealStage
    created_by: int
    created_at: datetime
    updated_at: datetime
    actual_close_date: Optional[datetime] = None
    completed_by: Optional[int] = None
    rejected_by: Optional[int] = None

class PipelineStageStats(BaseModel):
    """Statistics for a pipeline stage."""
    stage: DealStage
    count: int
    value: float

class PipelineStats(BaseModel):
    """Overall pipeline statistics."""
    stages: List[PipelineStageStats]
    total_deals: int
    total_value: float
    win_rate: float

class CustomerCRMStats(BaseModel):
    """CRM statistics for a customer."""
    total_interactions: int
    last_interaction: Optional[datetime]
    active_deals: int
    total_deal_value: float
    active_deal_value: float
    won_deal_value: float
    success_rate: float

class CustomerWithCRMStats(BaseModel):
    """Schema for customer data with CRM statistics"""
    id: int
    name: str
    company: str
    email: str
    phone: str
    total_deal_value: float
    won_deal_value: float
    active_deals: int
    success_rate: float
    last_interaction: Optional[datetime]

    class Config:
        from_attributes = True
