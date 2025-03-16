"""
Client-specific schemas for the Warehouse Quote System.

This module defines Pydantic models for client operations including:
1. Client profile
2. Client quote responses
3. Client service responses
4. Support ticket creation and responses
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, EmailStr, ConfigDict

from warehouse_quote_app.app.models.quote import QuoteStatus

class ClientBase(BaseModel):
    """Base client schema."""
    email: EmailStr
    first_name: str
    last_name: str
    company_name: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None

class ClientCreate(ClientBase):
    """Client creation schema."""
    password: str = Field(..., min_length=8)
    
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True
    )

class ClientUpdate(BaseModel):
    """Client update schema."""
    email: Optional[EmailStr] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    company_name: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True
    )

class ClientResponse(ClientBase):
    """Client response schema."""
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True
    )

class ClientUser(ClientBase):
    """Client user schema."""
    id: int
    is_active: bool = True
    created_at: datetime
    
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True
    )

class ClientProfile(BaseModel):
    """Client profile schema."""
    id: int
    email: EmailStr
    first_name: str
    last_name: str
    company_name: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    created_at: datetime
    
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True
    )

class ClientQuoteResponse(BaseModel):
    """Client quote response schema."""
    id: int
    total_amount: float
    service_type: str
    status: str
    created_at: datetime
    submitted_at: Optional[datetime] = None
    accepted_at: Optional[datetime] = None
    rejected_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True
    )

class ClientServiceResponse(BaseModel):
    """Client service response schema."""
    id: int
    service_type: str
    start_date: datetime
    end_date: Optional[datetime] = None
    status: str
    cost: float
    details: Optional[Dict[str, Any]] = None
    
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True
    )

class SupportTicketCreate(BaseModel):
    """Support ticket creation schema."""
    subject: str = Field(..., min_length=3, max_length=100)
    description: str = Field(..., min_length=10, max_length=1000)
    priority: str = Field("medium", pattern="^(low|medium|high|urgent)$")
    category: str = Field(..., min_length=3, max_length=50)

class SupportTicketResponse(BaseModel):
    """Support ticket response schema."""
    id: int
    subject: str
    description: str
    priority: str
    category: str
    status: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True
    )

__all__ = [
    'ClientBase',
    'ClientCreate',
    'ClientUpdate',
    'ClientResponse',
    'ClientUser',
    'ClientProfile',
    'ClientQuoteResponse',
    'ClientServiceResponse',
    'SupportTicketCreate',
    'SupportTicketResponse'
]
