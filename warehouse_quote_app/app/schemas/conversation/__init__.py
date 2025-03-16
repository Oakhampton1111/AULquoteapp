"""
Pydantic models for chat conversations.
"""

from datetime import datetime
from typing import Dict, Any, List, Optional
from decimal import Decimal
from pydantic import BaseModel, Field

class MessageCreate(BaseModel):
    """Schema for creating a new message."""
    session_id: str
    content: str

class MessageResponse(BaseModel):
    """Schema for message response."""
    content: str
    quote_details: Optional[Dict[str, Any]] = None
    suggestions: List[str] = Field(default_factory=list)

class QuoteContext(BaseModel):
    """Context for quote generation."""
    system_prompt: str
    current_quote: Optional[Dict[str, Any]] = None
    collected_info: Dict[str, Any] = Field(default_factory=dict)
    offered_discounts: Dict[str, Decimal] = Field(default_factory=dict)

class ChatSession(BaseModel):
    """Chat session with memory management."""
    id: str
    user_id: int
    messages: List[Dict[str, Any]] = Field(default_factory=list)
    context: QuoteContext
    created_at: datetime

class QuoteUpdate(BaseModel):
    """Schema for updating a quote."""
    session_id: str
    updates: Dict[str, Dict[str, Any]]
