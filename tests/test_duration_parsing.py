import unittest
from unittest.mock import MagicMock

from warehouse_quote_app.app.services.conversation.conversation_state import ConversationContext

class TestDurationParsing(unittest.TestCase):
    def test_medium_term_duration(self):
        # Setup conversation context with mocked services
        convo = ConversationContext(db=MagicMock(), quote_service=MagicMock(), storage_service=MagicMock())
        convo.state = 'duration'
        convo.gathered_info = {}

        # Mock quote service calculate_quote to avoid errors
        convo.quote_service.calculate_quote.return_value = MagicMock()

        # Provide medium term duration input
        response = convo.handle_input('I need storage for 3-6 months')

        self.assertEqual(convo.gathered_info['duration_weeks'], 6)

if __name__ == '__main__':
    unittest.main()
