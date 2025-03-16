"""
API routes for quote generation chat functionality.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any
from decimal import Decimal

from app.database import get_db
from app.schemas.conversation import (
    ChatSession,
    MessageCreate,
    MessageResponse,
    QuoteUpdate
)
from app.services.llm.chat_service import ChatService

router = APIRouter(prefix="/api/v1/chat", tags=["chat"])
chat_service = ChatService()

@router.post("/session")
async def create_session(
    db: Session = Depends(get_db)
) -> ChatSession:
    """Create a new chat session for quote generation."""
    try:
        session_id = await chat_service.create_session(db.user_id, db)
        return chat_service.get_session_context(session_id)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create chat session: {str(e)}"
        )

@router.post("/message")
async def send_message(
    message: MessageCreate,
    db: Session = Depends(get_db)
) -> MessageResponse:
    """Process a chat message and return AI response."""
    try:
        response = await chat_service.send_message(
            session_id=message.session_id,
            content=message.content,
            db=db
        )
        return MessageResponse(**response)
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process message: {str(e)}"
        )

@router.post("/quote/update")
async def update_quote(
    update: QuoteUpdate,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Update an existing quote based on conversation."""
    try:
        return await chat_service.update_quote(
            session_id=update.session_id,
            updates=update.updates,
            db=db
        )
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update quote: {str(e)}"
        )

@router.post("/quote/discount")
async def apply_discount(
    session_id: str,
    service_id: str,
    discount_percentage: Decimal,
    db: Session = Depends(get_db)
) -> Dict[str, bool]:
    """Apply a discount to a specific service (max 10%)."""
    try:
        success = await chat_service.apply_discount(
            session_id=session_id,
            service_id=service_id,
            discount_percentage=discount_percentage,
            db=db
        )
        return {"applied": success}
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to apply discount: {str(e)}"
        )

@router.get("/session/{session_id}")
async def get_session(
    session_id: str,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Get the current session context and memory."""
    try:
        return chat_service.get_session_context(session_id)
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get session: {str(e)}"
        )
