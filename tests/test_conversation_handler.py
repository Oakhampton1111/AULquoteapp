import unittest
import logging
from decimal import Decimal
from datetime import datetime
from unittest.mock import MagicMock

# Import directly from the quote module to avoid circular imports in __init__.py
from warehouse_quote_app.app.schemas.quote import (
    QuoteRequest, 
    StorageRequirements, 
    StorageType,
    ServiceRequest, 
    QuoteResponse
)

# Import service and conversation handlers
from warehouse_quote_app.app.services.business.quotes import QuoteService
from warehouse_quote_app.app.services.conversation.conversation_state import ConversationState
from warehouse_quote_app.app.services.business.storage import StorageService

# Set up logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TestConversationHandler(unittest.TestCase):
    def setUp(self):
        """Initialize test components"""
        # Create a mock database session
        self.mock_db = MagicMock()
        
        # Initialize services with mocks
        self.quote_service = MagicMock()
        self.storage_service = MagicMock()
        self.conversation_state = ConversationState(
            self.mock_db,
            quote_service=self.quote_service,
            storage_service=self.storage_service
        )
        logger.info("=== Starting conversation test case ===")

    def test_progressive_information_gathering(self):
        """Test the progressive information gathering flow"""
        logger.info("Testing progressive information gathering")
        conversation = self.conversation_state.new_conversation()
        
        # Test initial vague request
        user_input = "need storage asap how much???"
        logger.info(f"USER: {user_input}")
        response = conversation.handle_input(user_input)
        
        logger.info(f"SYSTEM STATE: {conversation.state}")
        logger.info("SYSTEM MESSAGES:")
        for msg in response.messages:
            logger.info(f"  - {msg}")
        logger.info("SYSTEM QUESTIONS:")
        for question in response.questions:
            logger.info(f"  - {question}")
        
        # Updated to check for storage_type questions instead of size
        self.assertTrue(any('type' in msg.lower() for msg in response.questions))
        self.assertTrue(len(response.questions) >= 3, "Should provide at least 3 storage type options")
        
        # Test storage type selection
        user_input = "household items"
        logger.info(f"USER: {user_input}")
        response = conversation.handle_input(user_input)
        
        logger.info(f"SYSTEM STATE: {conversation.state}")
        logger.info("SYSTEM MESSAGES:")
        for msg in response.messages:
            logger.info(f"  - {msg}")
        logger.info("SYSTEM QUESTIONS:")
        for question in response.questions:
            logger.info(f"  - {question}")
        
        # Now checks for quantity questions
        self.assertTrue(any('quantity' in msg.lower() or 'how much' in msg.lower() for msg in response.questions))
        
        # Test quantity selection
        user_input = "medium"
        logger.info(f"USER: {user_input}")
        response = conversation.handle_input(user_input)
        
        logger.info(f"SYSTEM STATE: {conversation.state}")
        logger.info("SYSTEM MESSAGES:")
        for msg in response.messages:
            logger.info(f"  - {msg}")
        logger.info("SYSTEM QUESTIONS:")
        for question in response.questions:
            logger.info(f"  - {question}")
        
        logger.info(f"GATHERED INFO: {conversation.gathered_info}")
        
        self.assertEqual(conversation.gathered_info.get('storage_type'), 'household')
        self.assertFalse(conversation.gathered_info.get('has_dangerous_goods', True))

    def test_conversation_state_management(self):
        """Test conversation state management"""
        logger.info("Testing conversation state management")
        
        # Test multiple conversations
        conv1 = self.conversation_state.new_conversation()
        conv2 = self.conversation_state.new_conversation()
        
        logger.info(f"Created two conversations with IDs: {conv1.conversation_id} and {conv2.conversation_id}")
        
        self.assertNotEqual(conv1.conversation_id, conv2.conversation_id)
        
        # Test state progression
        user_input = "need storage"
        logger.info(f"USER (conv1): {user_input}")
        conv1.handle_input(user_input)
        logger.info(f"SYSTEM STATE: {conv1.state}")
        
        user_input = "household items"
        logger.info(f"USER (conv1): {user_input}")
        conv1.handle_input(user_input)
        logger.info(f"SYSTEM STATE: {conv1.state}")
        
        self.assertEqual(conv1.state, 'quantity')
        
        # Test conversation retrieval
        retrieved_conv = self.conversation_state.get_conversation(conv1.conversation_id)
        logger.info(f"Retrieved conversation {conv1.conversation_id}, state: {retrieved_conv.state}")
        self.assertEqual(retrieved_conv.state, 'quantity')
        
        # Test conversation cleanup
        self.conversation_state.end_conversation(conv1.conversation_id)
        logger.info(f"Ended conversation {conv1.conversation_id}")
        retrieved_conv = self.conversation_state.get_conversation(conv1.conversation_id)
        logger.info(f"Attempted to retrieve ended conversation: {retrieved_conv}")
        self.assertIsNone(retrieved_conv)

    def test_error_handling(self):
        """Test conversation error handling"""
        logger.info("Testing error handling")
        
        conversation = self.conversation_state.new_conversation()
        
        # Test invalid quantity input
        user_input = "need storage"
        logger.info(f"USER: {user_input}")
        response = conversation.handle_input(user_input)
        logger.info(f"SYSTEM STATE: {conversation.state}")
        
        user_input = "household items"
        logger.info(f"USER: {user_input}")
        response = conversation.handle_input(user_input)
        logger.info(f"SYSTEM STATE: {conversation.state}")
        
        user_input = "enormous"  # Invalid quantity
        logger.info(f"USER: {user_input}")
        response = conversation.handle_input(user_input)
        
        logger.info(f"SYSTEM STATE: {conversation.state}")
        logger.info("SYSTEM MESSAGES:")
        for msg in response.messages:
            logger.info(f"  - {msg}")
        logger.info("SYSTEM QUESTIONS:")
        for question in response.questions:
            logger.info(f"  - {question}")
        
        self.assertTrue(any('didn\'t understand' in msg.lower() for msg in response.messages))
        self.assertTrue(any('small, medium, or large' in msg.lower() for msg in response.questions))
        
        # Test invalid type input
        conversation = self.conversation_state.new_conversation()
        logger.info("Starting new conversation for invalid type test")
        
        user_input = "need storage"
        logger.info(f"USER: {user_input}")
        response = conversation.handle_input(user_input)
        logger.info(f"SYSTEM STATE: {conversation.state}")
        
        user_input = "quantum particles"  # Invalid type
        logger.info(f"USER: {user_input}")
        response = conversation.handle_input(user_input)
        
        logger.info(f"SYSTEM STATE: {conversation.state}")
        logger.info("SYSTEM MESSAGES:")
        for msg in response.messages:
            logger.info(f"  - {msg}")
        logger.info("SYSTEM QUESTIONS:")
        for question in response.questions:
            logger.info(f"  - {question}")
        
        # Still should proceed to quantity, but might not recognize storage type properly
        self.assertEqual(conversation.state, 'quantity')
        
        logger.info("=== End of test run ===")

if __name__ == '__main__':
    unittest.main(verbosity=2)
