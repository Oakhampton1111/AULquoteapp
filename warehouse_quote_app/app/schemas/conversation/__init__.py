"""
Pydantic models for chat conversations.
"""

from datetime import datetime
from typing import Dict, Any, List, Optional
from decimal import Decimal # Keep Decimal for offered_discounts
from pydantic import BaseModel, Field
# Import Message from chat.py, assuming it's the standard
from ..chat import Message as ChatMessage # Use an alias to avoid name clash if any

class MessageCreate(BaseModel):
    """Schema for creating a new message."""
    session_id: str
    content: str

# This MessageResponse seems specific to an endpoint, not directly used by ChatService internally.
# ChatService's process_message returns a Dict[str, Any]
# class MessageResponse(BaseModel):
#     """Schema for message response."""
#     content: str
#     quote_details: Optional[Dict[str, Any]] = None
#     suggestions: List[str] = Field(default_factory=list)

class CurrentQuoteInfo(BaseModel):
    """Structure to store current quote details in session context."""
    line_items: List[Dict[str, Any]]
    total_amount: str # Store as string to ensure JSON serializability from Decimal
    messages: List[str] = Field(default_factory=list)
    follow_up_questions: List[str] = Field(default_factory=list)


class QuoteContext(BaseModel):
    """Context for quote generation."""
    # system_prompt: str # Removed as per plan
    current_quote: Optional[CurrentQuoteInfo] = None # Use the new structure
    collected_info: Dict[str, Any] = Field(default_factory=dict) # For QuoteRequest compatible data
    offered_discounts: Dict[str, Decimal] = Field(default_factory=dict)

class ChatSession(BaseModel):
    """Chat session with memory management."""
    id: str
    user_id: int
    messages: List[ChatMessage] = Field(default_factory=list) # Use ChatMessage from chat.py
    context: QuoteContext
    created_at: datetime

class QuoteUpdate(BaseModel):
    """Schema for updating a quote."""
    session_id: str
    updates: Dict[str, Dict[str, Any]]
