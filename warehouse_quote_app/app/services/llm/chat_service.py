"""
Multi-turn conversation service for quote generation with memory management.
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
import uuid
from decimal import Decimal

from warehouse_quote_app.app.core.config import settings
from warehouse_quote_app.app.services.llm.model import WarehouseLLM
from warehouse_quote_app.app.services.business.rates import RateService
from warehouse_quote_app.app.schemas.conversation import ChatSession, QuoteContext, MessageResponse
from sqlalchemy.ext.asyncio import AsyncSession

class ChatService:
    def __init__(self):
        self.llm = WarehouseLLM()
        self.sessions: Dict[str, ChatSession] = {}
        
    async def create_session(self, user_id: int, db: AsyncSession) -> str:
        """Create a new chat session."""
        session_id = str(uuid.uuid4())
        self.sessions[session_id] = ChatSession(
            id=session_id,
            user_id=user_id,
            messages=[],
            context=QuoteContext(system_prompt=""),
            created_at=datetime.now()
        )
        
        # Store session in database
        # This would typically involve saving to a database table
        # For now we'll just use the in-memory sessions dictionary
        
        return session_id

    async def get_session(self, session_id: str) -> Optional[ChatSession]:
        """Get existing chat session by ID."""
        return self.sessions.get(session_id)
    
    async def add_message(
        self,
        session_id: str,
        content: str,
        is_user: bool = True,
        db: AsyncSession = None
    ) -> Optional[Dict[str, Any]]:
        """Add a message to the chat session."""
        session = await self.get_session(session_id)
        if not session:
            return None
            
        message = {
            "content": content,
            "is_user": is_user,
            "timestamp": datetime.now().isoformat()
        }
        session.messages.append(message)
        
        return message
        
    async def process_message(
        self,
        session_id: str,
        content: str,
        db: AsyncSession
    ) -> Dict[str, Any]:
        """Process user message and generate LLM response."""
        session = await self.get_session(session_id)
        if not session:
            return {"error": "Session not found"}
            
        # Add user message to session
        user_message = await self.add_message(session_id, content, is_user=True, db=db)
        
        # Context for LLM
        context = {
            "session_id": session_id,
            "user_id": session.user_id,
            "history": [m.get("content", "") for m in session.messages[-10:] if "content" in m],
            "collected_info": session.context.collected_info
        }
        
        # Generate LLM response
        response_text = await self.llm.generate_response(
            input_text=content,
            template_key="quote_conversation",
            context=context
        )
        
        # Add LLM response to session
        assistant_message = await self.add_message(
            session_id,
            response_text,
            is_user=False,
            db=db
        )
        
        # Extract any information from the response
        # In a real system, you would parse the response for any extracted information
        extracted_info = {}  # Placeholder
        
        # Update collected info with any extracted information
        if extracted_info:
            session.context.collected_info.update(extracted_info)
        
        # Generate quote if we have sufficient information
        quote_details = None
        if session.context.collected_info:
            try:
                rate_service = RateService(db)
                quote_details = await rate_service.calculate_rates(
                    services=session.context.collected_info,
                    customer_id=session.user_id
                )
                session.context.current_quote = quote_details
            except Exception as e:
                # Log the error but continue
                print(f"Error calculating rates: {e}")
            
        return {
            "session_id": session_id,
            "response": response_text,
            "quote": session.context.current_quote,
            "collected_info": session.context.collected_info
        }
        
    async def update_session_context(
        self,
        session_id: str,
        updates: Dict[str, Any],
        db: AsyncSession
    ) -> Dict[str, Any]:
        """Update session context with new information."""
        session = await self.get_session(session_id)
        if not session:
            return {"error": "Session not found"}
            
        # Update context
        session.context.collected_info.update(updates)
        
        # Recalculate quote
        quote_details = None
        try:
            rate_service = RateService(db)
            quote_details = await rate_service.calculate_rates(
                services=session.context.collected_info,
                customer_id=session.user_id
            )
            session.context.current_quote = quote_details
        except Exception as e:
            # Log the error but continue
            print(f"Error calculating rates: {e}")
            
        return {
            "session_id": session_id,
            "quote": session.context.current_quote,
            "collected_info": session.context.collected_info
        }
