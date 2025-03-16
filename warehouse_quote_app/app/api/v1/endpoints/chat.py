"""Chat endpoints for conversation-based quote generation."""
from typing import Dict, Any, Optional, List
from fastapi import APIRouter, Depends, HTTPException, status, Body

from warehouse_quote_app.app.core.auth import get_current_user
from warehouse_quote_app.app.models.user import User
from warehouse_quote_app.app.schemas.chat import (
    ConversationStart,
    ConversationResponse,
    MessageRequest,
    MessageResponse,
    ConversationHistory
)
from warehouse_quote_app.app.services.conversation.conversation_state import ConversationState
from warehouse_quote_app.app.database import get_db
from sqlalchemy.orm import Session
from warehouse_quote_app.app.core.logging import get_logger

router = APIRouter()
logger = get_logger("chat")

@router.post(
    "/start",
    response_model=ConversationResponse,
    status_code=status.HTTP_200_OK
)
def start_conversation(
    conversation_data: Optional[ConversationStart] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Start a new conversation for quote generation.
    
    This endpoint initializes a new conversation context and returns
    a conversation ID that can be used for subsequent messages.
    """
    logger.info(f"Starting new conversation for user {current_user.id}")
    
    # Initialize conversation state
    conversation = ConversationState.create_new(
        user_id=current_user.id,
        initial_data=conversation_data.dict() if conversation_data else {}
    )
    
    return {
        "conversation_id": conversation.id,
        "welcome_message": conversation.get_welcome_message(),
        "created_at": conversation.created_at
    }


@router.post(
    "/message",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK
)
def send_message(
    message: MessageRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Send a message in an existing conversation.
    
    This endpoint processes a user message within an existing conversation
    and returns the system's response.
    """
    logger.info(f"Message received in conversation {message.conversation_id}")
    
    # Retrieve conversation state
    conversation = ConversationState.load(message.conversation_id)
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    
    # Verify user owns this conversation
    if conversation.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this conversation"
        )
    
    # Process message and get response
    response = conversation.process_message(message.content)
    
    # Save updated conversation state
    conversation.save()
    
    return {
        "conversation_id": conversation.id,
        "response": response,
        "timestamp": conversation.last_updated
    }


@router.get(
    "/history/{conversation_id}",
    response_model=ConversationHistory,
    status_code=status.HTTP_200_OK
)
def get_conversation_history(
    conversation_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get the history of a conversation.
    
    This endpoint retrieves the message history for a specific conversation.
    """
    logger.info(f"Retrieving history for conversation {conversation_id}")
    
    # Retrieve conversation state
    conversation = ConversationState.load(conversation_id)
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    
    # Verify user owns this conversation
    if conversation.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this conversation"
        )
    
    return {
        "conversation_id": conversation.id,
        "messages": conversation.get_message_history(),
        "created_at": conversation.created_at,
        "last_updated": conversation.last_updated
    }
