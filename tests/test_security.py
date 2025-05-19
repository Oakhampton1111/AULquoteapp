import unittest

from warehouse_quote_app.app.core.security.security import validate_api_key
from warehouse_quote_app.app.core.config import settings


class TestValidateApiKey(unittest.TestCase):
    def test_validate_api_key(self):
        original_keys = settings.API_KEYS
        settings.API_KEYS = ["test-key", "another-key"]
        try:
            self.assertTrue(validate_api_key("test-key"))
            self.assertFalse(validate_api_key("invalid"))
        finally:
            settings.API_KEYS = original_keys


if __name__ == "__main__":
    unittest.main()
