"""Schemas for chat and conversation functionality."""
from datetime import datetime
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field

class ConversationStart(BaseModel):
    """Schema for starting a new conversation."""
    context: Optional[Dict[str, Any]] = Field(None, description="Initial context for the conversation")

class ConversationResponse(BaseModel):
    """Schema for conversation response."""
    conversation_id: str = Field(..., description="Unique identifier for the conversation")
    created_at: datetime = Field(..., description="Timestamp when the conversation was created")
    welcome_message: str = Field(..., description="Welcome message to start the conversation")

class MessageRequest(BaseModel):
    """Schema for a message request."""
    content: str = Field(..., description="Message content")
    attachments: Optional[List[Dict[str, Any]]] = Field(None, description="Optional attachments")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Optional metadata")

class MessageResponse(BaseModel):
    """Schema for a message response."""
    message_id: str = Field(..., description="Unique identifier for the message")
    content: str = Field(..., description="Message content")
    timestamp: datetime = Field(..., description="Timestamp when the message was sent")
    quote_data: Optional[Dict[str, Any]] = Field(None, description="Quote data if available")

class Message(BaseModel):
    """Schema for a message in conversation history."""
    message_id: str = Field(..., description="Unique identifier for the message")
    sender: str = Field(..., description="Sender of the message (user or system)")
    content: str = Field(..., description="Message content")
    timestamp: datetime = Field(..., description="Timestamp when the message was sent")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Optional metadata")

class ConversationHistory(BaseModel):
    """Schema for conversation history."""
    conversation_id: str = Field(..., description="Unique identifier for the conversation")
    messages: List[Message] = Field(..., description="List of messages in the conversation")
    created_at: datetime = Field(..., description="Timestamp when the conversation was created")
    updated_at: datetime = Field(..., description="Timestamp when the conversation was last updated")
