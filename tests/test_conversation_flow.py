"""
Comprehensive testing of the conversation flow for quote generation.

This test suite focuses on validating the conversation state machine,
transitions between states, and the extraction of quote parameters from
natural language inputs.
"""

import unittest
import logging
import asyncio
from unittest.mock import MagicMock, patch
import pytest

from warehouse_quote_app.app.services.conversation.conversation_state import ConversationState
from warehouse_quote_app.app.services.conversation.state_machine import StateMachine, State
from warehouse_quote_app.app.services.conversation.intent_recognizer import IntentRecognizer
from warehouse_quote_app.app.services.quote_service import QuoteService
from warehouse_quote_app.app.schemas.quote import QuoteRequest
from warehouse_quote_app.app.database import get_db

# Set up logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TestConversationFlow(unittest.TestCase):
    """Test the conversation flow for quote generation."""
    
    def setUp(self):
        """Set up test environment."""
        # Mock services
        self.mock_quote_service = MagicMock(spec=QuoteService)
        self.mock_intent_recognizer = MagicMock(spec=IntentRecognizer)
        
        # Create conversation state with mocked dependencies
        self.conversation_state = ConversationState(
            quote_service=self.mock_quote_service,
            intent_recognizer=self.mock_intent_recognizer
        )
        
        # Test user data
        self.user_id = "test-user-123"
        
        logger.info("=== Starting conversation flow test case ===")

    def test_conversation_initialization(self):
        """Test conversation initialization."""
        logger.info("Testing conversation initialization")
        
        # Initialize a new conversation
        conversation = self.conversation_state.new_conversation(self.user_id)
        
        # Verify conversation is initialized correctly
        self.assertIsNotNone(conversation)
        self.assertEqual(conversation.user_id, self.user_id)
        self.assertEqual(conversation.current_state, "initial")
        self.assertEqual(len(conversation.messages), 0)

    @patch("warehouse_quote_app.app.services.conversation.intent_recognizer.IntentRecognizer.recognize_intent")
    def test_initial_greeting_transition(self, mock_recognize_intent):
        """Test transition from initial state to gathering requirements."""
        logger.info("Testing initial greeting transition")
        
        # Set up mock intent recognizer
        mock_recognize_intent.return_value = {
            "intent": "storage_inquiry",
            "confidence": 0.95,
            "entities": []
        }
        
        # Initialize a new conversation
        conversation = self.conversation_state.new_conversation(self.user_id)
        
        # Process initial greeting
        response = conversation.process_message("I need storage for my furniture")
        
        # Verify state transition
        self.assertEqual(conversation.current_state, "gathering_requirements")
        self.assertIn("What type of storage", response["message"])
        
        # Verify message was added to history
        self.assertEqual(len(conversation.messages), 2)  # User message + system response

    @patch("warehouse_quote_app.app.services.conversation.intent_recognizer.IntentRecognizer.recognize_intent")
    @patch("warehouse_quote_app.app.services.conversation.intent_recognizer.IntentRecognizer.extract_entities")
    def test_gathering_storage_type(self, mock_extract_entities, mock_recognize_intent):
        """Test gathering storage type requirements."""
        logger.info("Testing gathering storage type")
        
        # Set up mocks
        mock_recognize_intent.return_value = {
            "intent": "provide_storage_type",
            "confidence": 0.95,
            "entities": []
        }
        
        mock_extract_entities.return_value = {
            "storage_type": "household"
        }
        
        # Initialize conversation and set state
        conversation = self.conversation_state.new_conversation(self.user_id)
        conversation.current_state = "gathering_requirements"
        conversation.quote_params = {}
        
        # Process storage type response
        response = conversation.process_message("I need household storage")
        
        # Verify parameter extraction
        self.assertEqual(conversation.quote_params.get("storage_type"), "household")
        
        # Verify next question is asked
        self.assertIn("how long", response["message"].lower())

    @patch("warehouse_quote_app.app.services.conversation.intent_recognizer.IntentRecognizer.recognize_intent")
    @patch("warehouse_quote_app.app.services.conversation.intent_recognizer.IntentRecognizer.extract_entities")
    def test_gathering_duration(self, mock_extract_entities, mock_recognize_intent):
        """Test gathering duration requirements."""
        logger.info("Testing gathering duration")
        
        # Set up mocks
        mock_recognize_intent.return_value = {
            "intent": "provide_duration",
            "confidence": 0.95,
            "entities": []
        }
        
        mock_extract_entities.return_value = {
            "duration_weeks": 12
        }
        
        # Initialize conversation and set state
        conversation = self.conversation_state.new_conversation(self.user_id)
        conversation.current_state = "gathering_requirements"
        conversation.quote_params = {"storage_type": "household"}
        
        # Process duration response
        response = conversation.process_message("I need it for 3 months")
        
        # Verify parameter extraction
        self.assertEqual(conversation.quote_params.get("duration_weeks"), 12)
        
        # Verify next question is asked
        self.assertIn("quantity", response["message"].lower())

    @patch("warehouse_quote_app.app.services.conversation.intent_recognizer.IntentRecognizer.recognize_intent")
    @patch("warehouse_quote_app.app.services.conversation.intent_recognizer.IntentRecognizer.extract_entities")
    def test_gathering_quantity(self, mock_extract_entities, mock_recognize_intent):
        """Test gathering quantity requirements."""
        logger.info("Testing gathering quantity")
        
        # Set up mocks
        mock_recognize_intent.return_value = {
            "intent": "provide_quantity",
            "confidence": 0.95,
            "entities": []
        }
        
        mock_extract_entities.return_value = {
            "quantity": "medium"
        }
        
        # Initialize conversation and set state
        conversation = self.conversation_state.new_conversation(self.user_id)
        conversation.current_state = "gathering_requirements"
        conversation.quote_params = {
            "storage_type": "household",
            "duration_weeks": 12
        }
        
        # Process quantity response
        response = conversation.process_message("Medium size, about a one-bedroom apartment worth")
        
        # Verify parameter extraction
        self.assertEqual(conversation.quote_params.get("quantity"), "medium")
        
        # Verify next question is asked
        self.assertIn("special instructions", response["message"].lower())

    @patch("warehouse_quote_app.app.services.conversation.intent_recognizer.IntentRecognizer.recognize_intent")
    @patch("warehouse_quote_app.app.services.conversation.intent_recognizer.IntentRecognizer.extract_entities")
    def test_gathering_special_instructions(self, mock_extract_entities, mock_recognize_intent):
        """Test gathering special instructions."""
        logger.info("Testing gathering special instructions")
        
        # Set up mocks
        mock_recognize_intent.return_value = {
            "intent": "provide_special_instructions",
            "confidence": 0.95,
            "entities": []
        }
        
        mock_extract_entities.return_value = {
            "special_instructions": "Need climate control for antiques"
        }
        
        # Initialize conversation and set state
        conversation = self.conversation_state.new_conversation(self.user_id)
        conversation.current_state = "gathering_requirements"
        conversation.quote_params = {
            "storage_type": "household",
            "duration_weeks": 12,
            "quantity": "medium"
        }
        
        # Process special instructions response
        response = conversation.process_message("I need climate control for my antiques")
        
        # Verify parameter extraction
        self.assertEqual(conversation.quote_params.get("special_instructions"), 
                         "Need climate control for antiques")
        
        # Verify transition to quote generation
        self.assertEqual(conversation.current_state, "generating_quote")

    @patch("warehouse_quote_app.app.services.quote_service.QuoteService.generate_quote")
    def test_quote_generation(self, mock_generate_quote):
        """Test quote generation from gathered parameters."""
        logger.info("Testing quote generation")
        
        # Set up mock quote service
        mock_quote = {
            "quote_id": "test-quote-123",
            "total_amount": 1250.00,
            "service_type": "storage",
            "duration_weeks": 12,
            "storage_type": "household",
            "quantity": "medium",
            "special_instructions": "Need climate control for antiques"
        }
        mock_generate_quote.return_value = mock_quote
        
        # Initialize conversation and set state for quote generation
        conversation = self.conversation_state.new_conversation(self.user_id)
        conversation.current_state = "generating_quote"
        conversation.quote_params = {
            "storage_type": "household",
            "duration_weeks": 12,
            "quantity": "medium",
            "special_instructions": "Need climate control for antiques"
        }
        
        # Generate quote
        response = conversation.generate_quote()
        
        # Verify quote generation
        self.assertEqual(conversation.current_state, "quote_generated")
        self.assertEqual(conversation.quote_id, "test-quote-123")
        
        # Verify quote service was called with correct parameters
        mock_generate_quote.assert_called_once()
        call_args = mock_generate_quote.call_args[0][0]
        self.assertEqual(call_args.storage_type, "household")
        self.assertEqual(call_args.duration_weeks, 12)
        self.assertEqual(call_args.quantity, "medium")
        
        # Verify response contains quote details
        self.assertIn("total_amount", response)
        self.assertEqual(response["total_amount"], 1250.00)

    @patch("warehouse_quote_app.app.services.conversation.intent_recognizer.IntentRecognizer.recognize_intent")
    def test_quote_negotiation(self, mock_recognize_intent):
        """Test quote negotiation flow."""
        logger.info("Testing quote negotiation")
        
        # Set up mock intent recognizer
        mock_recognize_intent.return_value = {
            "intent": "request_discount",
            "confidence": 0.95,
            "entities": [
                {"entity": "discount_percentage", "value": 10}
            ]
        }
        
        # Initialize conversation and set state for quote negotiation
        conversation = self.conversation_state.new_conversation(self.user_id)
        conversation.current_state = "quote_generated"
        conversation.quote_id = "test-quote-123"
        conversation.quote_params = {
            "storage_type": "household",
            "duration_weeks": 12,
            "quantity": "medium",
            "special_instructions": "Need climate control for antiques"
        }
        conversation.quote_result = {
            "quote_id": "test-quote-123",
            "total_amount": 1250.00,
            "service_type": "storage"
        }
        
        # Process discount request
        response = conversation.process_message("Can I get a 10% discount?")
        
        # Verify state transition
        self.assertEqual(conversation.current_state, "negotiating")
        
        # Verify response contains negotiation information
        self.assertIn("discount", response["message"].lower())

    @patch("warehouse_quote_app.app.services.quote_service.QuoteService.apply_discount")
    @patch("warehouse_quote_app.app.services.quote_service.QuoteService.check_discount_eligibility")
    def test_discount_approval_flow(self, mock_check_eligibility, mock_apply_discount):
        """Test discount approval flow."""
        logger.info("Testing discount approval flow")
        
        # Set up mocks
        mock_check_eligibility.return_value = {
            "eligible": True,
            "max_discount": 15,
            "auto_approve": True
        }
        
        mock_apply_discount.return_value = {
            "quote_id": "test-quote-123",
            "original_amount": 1250.00,
            "discounted_amount": 1125.00,
            "discount_percentage": 10,
            "status": "approved"
        }
        
        # Initialize conversation and set state for negotiation
        conversation = self.conversation_state.new_conversation(self.user_id)
        conversation.current_state = "negotiating"
        conversation.quote_id = "test-quote-123"
        conversation.quote_result = {
            "quote_id": "test-quote-123",
            "total_amount": 1250.00,
            "service_type": "storage"
        }
        
        # Request discount
        discount_result = conversation.request_discount(10, "I'm a returning customer")
        
        # Verify discount was applied
        self.assertEqual(discount_result["status"], "approved")
        self.assertEqual(discount_result["discounted_amount"], 1125.00)
        
        # Verify state transition
        self.assertEqual(conversation.current_state, "quote_updated")

    def test_quote_acceptance(self):
        """Test quote acceptance flow."""
        logger.info("Testing quote acceptance flow")
        
        # Mock quote service accept method
        self.mock_quote_service.accept_quote.return_value = {
            "quote_id": "test-quote-123",
            "status": "accepted",
            "acceptance_date": "2023-07-15T14:30:00Z"
        }
        
        # Initialize conversation and set state for acceptance
        conversation = self.conversation_state.new_conversation(self.user_id)
        conversation.current_state = "quote_generated"
        conversation.quote_id = "test-quote-123"
        
        # Process acceptance message
        response = conversation.process_message("I accept the quote")
        
        # Verify quote was accepted
        self.assertEqual(conversation.current_state, "completed")
        self.assertIn("accepted", response["message"].lower())
        
        # Verify quote service was called
        self.mock_quote_service.accept_quote.assert_called_once_with("test-quote-123")

    def test_quote_rejection(self):
        """Test quote rejection flow."""
        logger.info("Testing quote rejection flow")
        
        # Mock quote service reject method
        self.mock_quote_service.reject_quote.return_value = {
            "quote_id": "test-quote-123",
            "status": "rejected",
            "rejection_date": "2023-07-15T14:30:00Z"
        }
        
        # Initialize conversation and set state for rejection
        conversation = self.conversation_state.new_conversation(self.user_id)
        conversation.current_state = "quote_generated"
        conversation.quote_id = "test-quote-123"
        
        # Process rejection message
        response = conversation.process_message("I reject the quote, it's too expensive")
        
        # Verify quote was rejected
        self.assertEqual(conversation.current_state, "completed")
        self.assertIn("rejected", response["message"].lower())
        
        # Verify quote service was called
        self.mock_quote_service.reject_quote.assert_called_once_with(
            "test-quote-123", 
            "too expensive"
        )

    def test_conversation_restart(self):
        """Test conversation restart functionality."""
        logger.info("Testing conversation restart")
        
        # Initialize conversation
        conversation = self.conversation_state.new_conversation(self.user_id)
        
        # Add some state
        conversation.current_state = "quote_generated"
        conversation.quote_params = {
            "storage_type": "household",
            "duration_weeks": 12
        }
        conversation.quote_id = "test-quote-123"
        
        # Restart conversation
        conversation.restart()
        
        # Verify conversation was reset
        self.assertEqual(conversation.current_state, "initial")
        self.assertEqual(conversation.quote_params, {})
        self.assertIsNone(conversation.quote_id)
        self.assertEqual(len(conversation.messages), 0)


if __name__ == '__main__':
    unittest.main(verbosity=2)
