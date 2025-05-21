"""Chat endpoints for conversation-based quote generation."""
from typing import Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.ext.asyncio import AsyncSession # Use AsyncSession

from warehouse_quote_app.app.api import deps # For get_async_db and get_current_active_user
# from warehouse_quote_app.app.core.auth import get_current_user # Old sync version
from warehouse_quote_app.app.models.user import User as UserModel # Renamed to avoid clash with User schema if any
from warehouse_quote_app.app.schemas.chat import ( # Keep existing schemas for now, might need adjustment
    ConversationStart, # This might not be used if ChatService handles context differently
    ConversationResponse as ChatConversationResponseSchema, # Renamed to avoid clash
    MessageRequest as ChatMessageRequestSchema, # Renamed
    MessageResponse as ChatMessageResponseSchema, # Renamed
    ConversationHistory as ChatConversationHistorySchema # Renamed
)
# Import ChatService and its dependencies
from warehouse_quote_app.app.services.llm.chat_service import ChatService
from warehouse_quote_app.app.services.crm.base import BaseCRMService
# from warehouse_quote_app.app.database import get_async_db # Already in deps
from warehouse_quote_app.app.core.logging import get_logger

router = APIRouter()
logger = get_logger("chat_api") # Changed logger name for clarity

# Dependency injector for ChatService
# This should ideally be in deps.py but placing here for brevity during refactor
async def get_chat_service(
    crm_service: BaseCRMService = Depends(deps.get_crm_service),
    # db: AsyncSession = Depends(deps.get_async_db) # ChatService constructor doesn't take db now
) -> ChatService:
    # ChatService constructor now takes crm_service. db was made optional and not used.
    return ChatService(crm_service=crm_service)


@router.post(
    "/start",
    response_model=ChatConversationResponseSchema, # Use existing schema for now
    status_code=status.HTTP_200_OK
)
async def start_conversation( # Changed to async
    # conversation_data: Optional[ConversationStart] = None, # ChatService.create_session doesn't use this
    current_user: UserModel = Depends(deps.get_current_active_user), # Use async active user
    # db: AsyncSession = Depends(deps.get_async_db), # Not directly used by endpoint, ChatService manages its needs
    chat_service: ChatService = Depends(get_chat_service) # Inject ChatService
):
    """
    Start a new conversation for quote generation using ChatService.
    """
    logger.info(f"Starting new conversation for user {current_user.id}")
    
    session_id = await chat_service.create_session(user_id=current_user.id)
    session = await chat_service.get_session(session_id) # Fetch session to get initial message
    
    if not session or not session.messages:
        logger.error(f"Failed to create session or initial message for user {current_user.id}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Could not start conversation.")

    # Adapt to ConversationResponse schema
    return ChatConversationResponseSchema(
        conversation_id=session_id,
        welcome_message=session.messages[0].content, # First message is the welcome message
        created_at=session.created_at
    )


@router.post(
    "/{session_id}/message", # Changed path to include session_id as path parameter
    response_model=Dict[str, Any], # ChatService.process_message returns a Dict
    status_code=status.HTTP_200_OK
)
async def send_message( # Changed to async
    session_id: str, # Added session_id from path
    message_request: ChatMessageRequestSchema, # Use existing schema for request body
    current_user: UserModel = Depends(deps.get_current_active_user), # Use async active user
    # db: AsyncSession = Depends(deps.get_async_db), # Not directly used by endpoint
    chat_service: ChatService = Depends(get_chat_service) # Inject ChatService
):
    """
    Send a message in an existing conversation using ChatService.
    """
    logger.info(f"Message received in session {session_id} by user {current_user.id}")
    
    session = await chat_service.get_session(session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    if session.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this session"
        )
    
    # Pass current_user to process_message for CRM integration
    response_data = await chat_service.process_message(
        session_id=session_id, 
        user_content=message_request.content,
        current_user=current_user 
    )
    
    if "error" in response_data:
        # Handle errors from ChatService if any (e.g., session not found again)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=response_data["error"])

    # The response_data from ChatService.process_message is a Dict.
    # It needs to be mapped to ChatMessageResponseSchema or the endpoint response_model changed.
    # Current ChatService returns: {"session_id", "response", "quote", "collected_info", "missing_information", "service_type_provided"}
    # ChatMessageResponseSchema expects: {"message_id", "content", "timestamp", "quote_data"}
    # For now, returning the dict directly and changing response_model of endpoint.
    return response_data


@router.get(
    "/{session_id}/history", # Changed path
    response_model=ChatConversationHistorySchema, # Use existing schema for now
    status_code=status.HTTP_200_OK
)
async def get_conversation_history( # Changed to async
    session_id: str, # Added session_id from path
    current_user: UserModel = Depends(deps.get_current_active_user), # Use async active user
    # db: AsyncSession = Depends(deps.get_async_db), # Not directly used
    chat_service: ChatService = Depends(get_chat_service) # Inject ChatService
):
    """
    Get the history of a conversation using ChatService.
    """
    logger.info(f"Retrieving history for session {session_id} by user {current_user.id}")
    
    session = await chat_service.get_session(session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    if session.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this session"
        )
    
    # Adapt ChatSession.messages (List[schemas.chat.Message]) to ConversationHistory.messages
    # schemas.chat.Message has: message_id, sender, content, timestamp, metadata
    # This should be compatible if ConversationHistory expects a list of such objects.
    return ChatConversationHistorySchema(
        conversation_id=session.id, # ChatSession.id is session_id
        messages=[msg.model_dump() for msg in session.messages], # Convert Pydantic models to dicts if necessary
        created_at=session.created_at,
        updated_at=session.messages[-1].timestamp if session.messages else session.created_at # Example for updated_at
    )
