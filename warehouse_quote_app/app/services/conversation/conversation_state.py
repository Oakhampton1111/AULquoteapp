from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any, Union
from uuid import uuid4
from pydantic import BaseModel

from sqlalchemy.orm import Session

from warehouse_quote_app.app.services.business.quotes import QuoteService
from warehouse_quote_app.app.services.business.storage import StorageService
from warehouse_quote_app.app.schemas.quote import StorageRequirements, QuoteRequest, QuoteResponse, ServiceRequest

class ConversationResponse:
    """Represents a response in the conversation flow."""
    def __init__(
        self,
        messages: List[str],
        questions: List[str],
        quote: Optional[QuoteResponse] = None
    ):
        self.messages = messages
        self.questions = questions
        self.quote = quote

class ConversationContext:
    """Manages the context and state of a single conversation."""
    
    def __init__(self, db: Session, quote_service=None, storage_service=None):
        self.conversation_id = str(uuid4())
        self.start_time = datetime.now()
        self.state = 'initial'
        self.gathered_info = {}
        self.db = db
        self.quote_service = quote_service
        self.storage_service = storage_service
        
    def handle_input(self, user_input: str) -> ConversationResponse:
        """Process user input based on current state and return appropriate response."""
        # Very basic state machine for conversation
        if self.state == 'initial':
            return self._handle_initial_input(user_input)
        elif self.state == 'storage_type':
            return self._handle_storage_type_input(user_input)
        elif self.state == 'quantity':
            return self._handle_quantity_input(user_input)
        elif self.state == 'duration':
            return self._handle_duration_input(user_input)
        else:
            return ConversationResponse(
                messages=["I'm not sure how to proceed. Let's start over."],
                suggested_responses=["Start over"]
            )
    
    def _handle_initial_input(self, user_input: str) -> ConversationResponse:
        """Handle initial user request."""
        self.state = 'storage_type'
        return ConversationResponse(
            messages=['Let me help you with a storage quote.'],
            questions=[
                'What type of storage do you need?',
                '- Household items',
                '- Business inventory',
                '- Equipment/machinery'
            ]
        )
    
    def _handle_storage_type_input(self, user_input: str) -> ConversationResponse:
        """Handle storage type input."""
        if 'house' in user_input or 'furniture' in user_input:
            self.gathered_info['storage_type'] = 'household'
            self.gathered_info['has_dangerous_goods'] = False
        elif 'business' in user_input or 'inventory' in user_input:
            self.gathered_info['storage_type'] = 'business'
            self.gathered_info['has_dangerous_goods'] = False
        elif 'equipment' in user_input or 'machine' in user_input:
            self.gathered_info['storage_type'] = 'equipment'
            self.gathered_info['has_dangerous_goods'] = True
        
        self.state = 'quantity'
        return ConversationResponse(
            messages=['Got it. Now let\'s determine how much you need to store.'],
            questions=[
                'How much do you need to store?',
                '- Small (fits in a garage)',
                '- Medium (fits 2-3 garages)',
                '- Large (warehouse space)'
            ]
        )
    
    def _handle_quantity_input(self, user_input: str) -> ConversationResponse:
        """Handle quantity input."""
        size_mapping = {
            'small': 20,
            'medium': 40,
            'large': 100
        }
        
        for size, space in size_mapping.items():
            if size in user_input:
                self.gathered_info['floor_area'] = float(space)
                self.state = 'duration'
                return ConversationResponse(
                    messages=[f'Got it - approximately {space}m² of space.'],
                    questions=[
                        'How long do you need storage for?',
                        '- Short term (1-3 months)',
                        '- Medium term (3-6 months)',
                        '- Long term (6+ months)'
                    ]
                )
        
        return ConversationResponse(
            messages=['I didn\'t understand that quantity.'],
            questions=[
                'Please choose: small, medium, or large'
            ]
        )
    
    def _handle_duration_input(self, user_input: str) -> ConversationResponse:
        """Handle duration input and generate quote."""
        # Map duration input to weeks
        if 'short' in user_input or '1-3' in user_input:
            self.gathered_info['duration_weeks'] = 2
        elif 'medium' in user_input or '1-6' in user_input:
            self.gathered_info['duration_weeks'] = 6
        elif 'long' in user_input or '6+' in user_input:
            self.gathered_info['duration_weeks'] = 12
        else:
            # Default duration
            self.gathered_info['duration_weeks'] = 4
            
        # Prepare storage requirements
        storage_req = StorageRequirements(
            storage_type=self.gathered_info.get('storage_type', 'standard'),
            quantity=self.gathered_info.get('quantity', 1),
            duration_weeks=self.gathered_info.get('duration_weeks', 4),
            floor_area=self.gathered_info.get('floor_area'),
            is_dangerous_goods=self.gathered_info.get('has_dangerous_goods', False)
        )
        
        # Create quote request
        request = QuoteRequest(
            services=['storage'],
            storage_requirements=storage_req,
            duration_weeks=self.gathered_info.get('duration_weeks', 4),
            has_dangerous_goods=self.gathered_info.get('has_dangerous_goods', False)
        )
        
        # Calculate quote using QuoteService
        quote_response = self.quote_service.calculate_quote(request, self.db)
        
        return ConversationResponse(
            messages=[
                'I\'ve prepared your quote based on the information provided.',
                'The first 2 weeks of storage are complimentary!'
            ],
            questions=[
                'Would you like to see a detailed breakdown of the costs?',
                'Do you need any additional services like packing or transport?'
            ],
            quote=quote_response
        )
    
    def _create_error_response(self) -> ConversationResponse:
        """Create a response for error conditions."""
        return ConversationResponse(
            messages=['I\'m having trouble understanding. Let\'s start over.'],
            questions=[
                'What type of storage do you need?',
                '- Household items',
                '- Business inventory',
                '- Equipment/machinery'
            ]
        )

class ConversationState:
    """Manages multiple conversations and their states."""
    
    def __init__(self):
        self.conversations = {}
        
    def new_conversation(self, user_id: int, db, initial_context=None):
        """Create and return a new conversation context."""
        conversation_id = str(uuid4())
        created_at = datetime.now()
        
        conversation = {
            "id": conversation_id,
            "user_id": user_id,
            "created_at": created_at,
            "updated_at": created_at,
            "messages": [],
            "context": initial_context or {}
        }
        
        self.conversations[conversation_id] = conversation
        return conversation
        
    def get_conversation(self, conversation_id: str, user_id: int):
        """Get conversation by ID if it exists."""
        conversation = self.conversations.get(conversation_id)
        if not conversation:
            raise ValueError(f"Conversation {conversation_id} not found")
        
        if conversation["user_id"] != user_id:
            raise ValueError("Unauthorized access to conversation")
            
        return conversation
        
    def process_message(self, conversation_id: str, user_id: int, message: str, db):
        """Process a message in a conversation."""
        conversation = self.get_conversation(conversation_id, user_id)
        
        # Add user message to history
        message_id = str(uuid4())
        timestamp = datetime.now()
        
        user_message = {
            "message_id": str(uuid4()),
            "sender": "user",
            "content": message,
            "timestamp": timestamp
        }
        
        conversation["messages"].append(user_message)
        conversation["updated_at"] = timestamp
        
        # Generate response
        response_content = "Thank you for your message. I'm processing your request."
        
        # Add system response to history
        system_message = {
            "message_id": message_id,
            "sender": "system",
            "content": response_content,
            "timestamp": timestamp
        }
        
        conversation["messages"].append(system_message)
        
        # Return response object
        return type('MessageResponse', (), {
            'message_id': message_id,
            'content': response_content,
            'timestamp': timestamp,
            'quote_data': None
        })
        
    def get_conversation_history(self, conversation_id: str, user_id: int, db):
        """Get the history of a conversation."""
        conversation = self.get_conversation(conversation_id, user_id)
        
        return type('ConversationHistory', (), {
            'messages': conversation["messages"],
            'created_at': conversation["created_at"],
            'updated_at': conversation["updated_at"]
        })
        
    def end_conversation(self, conversation_id: str, user_id: int):
        """End and cleanup a conversation by ID."""
        self.get_conversation(conversation_id, user_id)
        if conversation_id in self.conversations:
            del self.conversations[conversation_id]
