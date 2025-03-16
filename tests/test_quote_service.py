"""
Comprehensive testing of the quote service functionality.

This test suite validates the quote generation, calculation, negotiation,
and management functionality of the quote service.
"""

import unittest
import logging
import asyncio
from datetime import datetime, timedelta
from decimal import Decimal
from unittest.mock import MagicMock, patch
import pytest

from warehouse_quote_app.app.services.quote_service import QuoteService
from warehouse_quote_app.app.schemas.quote import QuoteRequest, QuoteResponse
from warehouse_quote_app.app.models.quote import Quote
from warehouse_quote_app.app.models.rate import Rate
from warehouse_quote_app.app.models.user import User
from warehouse_quote_app.app.models.customer import Customer
from warehouse_quote_app.app.database import get_db

# Set up logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TestQuoteService(unittest.TestCase):
    """Test the quote service functionality."""
    
    def setUp(self):
        """Set up test environment."""
        # Mock database session
        self.mock_db = MagicMock()
        
        # Create quote service with mocked dependencies
        self.quote_service = QuoteService(db=self.mock_db)
        
        # Test user data
        self.user_id = 1
        self.customer_id = 1
        
        # Test quote request data
        self.quote_request = QuoteRequest(
            services=["storage"],
            storage_type="household",
            duration_weeks=12,
            quantity="medium",
            special_instructions="Need climate control"
        )
        
        logger.info("=== Starting quote service test case ===")

    @patch("warehouse_quote_app.app.services.quote_service.QuoteService._get_rate")
    def test_quote_calculation(self, mock_get_rate):
        """Test quote calculation logic."""
        logger.info("Testing quote calculation")
        
        # Set up mock rate
        mock_get_rate.return_value = Rate(
            id=1,
            service_type="storage",
            storage_type="household",
            quantity="medium",
            rate_amount=Decimal("100.00"),
            unit="week",
            effective_date=datetime.now() - timedelta(days=30),
            expiration_date=datetime.now() + timedelta(days=30)
        )
        
        # Calculate quote
        quote_amount = self.quote_service._calculate_quote_amount(self.quote_request)
        
        # Verify calculation
        # Expected: 100.00 * 12 weeks = 1200.00
        self.assertEqual(quote_amount, Decimal("1200.00"))

    @patch("warehouse_quote_app.app.services.quote_service.QuoteService._get_rate")
    @patch("warehouse_quote_app.app.services.quote_service.QuoteService._create_quote")
    def test_generate_quote(self, mock_create_quote, mock_get_rate):
        """Test quote generation."""
        logger.info("Testing quote generation")
        
        # Set up mocks
        mock_get_rate.return_value = Rate(
            id=1,
            service_type="storage",
            storage_type="household",
            quantity="medium",
            rate_amount=Decimal("100.00"),
            unit="week",
            effective_date=datetime.now() - timedelta(days=30),
            expiration_date=datetime.now() + timedelta(days=30)
        )
        
        mock_create_quote.return_value = Quote(
            id=1,
            user_id=self.user_id,
            customer_id=self.customer_id,
            total_amount=Decimal("1200.00"),
            status="draft",
            service_type="storage",
            storage_type="household",
            duration_weeks=12,
            quantity="medium",
            special_instructions="Need climate control",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        # Generate quote
        quote = self.quote_service.generate_quote(
            self.quote_request, 
            user_id=self.user_id,
            customer_id=self.customer_id
        )
        
        # Verify quote generation
        self.assertEqual(quote.id, 1)
        self.assertEqual(quote.total_amount, Decimal("1200.00"))
        self.assertEqual(quote.status, "draft")
        self.assertEqual(quote.service_type, "storage")
        self.assertEqual(quote.storage_type, "household")
        self.assertEqual(quote.duration_weeks, 12)
        
        # Verify create quote was called with correct parameters
        mock_create_quote.assert_called_once()
        call_args = mock_create_quote.call_args[0]
        self.assertEqual(call_args[0], self.user_id)
        self.assertEqual(call_args[1], self.customer_id)
        self.assertEqual(call_args[2], Decimal("1200.00"))
        self.assertEqual(call_args[3].services, ["storage"])
        self.assertEqual(call_args[3].storage_type, "household")

    @patch("warehouse_quote_app.app.services.quote_service.QuoteService._get_quote")
    def test_check_discount_eligibility(self, mock_get_quote):
        """Test discount eligibility checking."""
        logger.info("Testing discount eligibility")
        
        # Set up mock quote
        mock_quote = Quote(
            id=1,
            user_id=self.user_id,
            customer_id=self.customer_id,
            total_amount=Decimal("1200.00"),
            status="draft",
            service_type="storage",
            storage_type="household",
            duration_weeks=12,
            quantity="medium",
            special_instructions="Need climate control",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        mock_get_quote.return_value = mock_quote
        
        # Set up mock customer with good history
        mock_customer = Customer(
            id=self.customer_id,
            company_name="Test Company",
            contact_email="test@example.com",
            phone="1234567890",
            address="123 Test St",
            industry="Manufacturing",
            total_quotes=10,
            accepted_quotes=8,
            total_spend=Decimal("10000.00"),
            created_at=datetime.now() - timedelta(days=365),
            updated_at=datetime.now()
        )
        
        # Mock the customer retrieval
        self.mock_db.query.return_value.filter.return_value.first.return_value = mock_customer
        
        # Check eligibility
        eligibility = self.quote_service.check_discount_eligibility("quote-1", 10)
        
        # Verify eligibility
        self.assertTrue(eligibility["eligible"])
        self.assertGreaterEqual(eligibility["max_discount"], 10)
        
        # Test with a new customer (should be less eligible)
        mock_customer.total_quotes = 1
        mock_customer.accepted_quotes = 0
        mock_customer.total_spend = Decimal("0.00")
        mock_customer.created_at = datetime.now() - timedelta(days=10)
        
        # Check eligibility again
        eligibility = self.quote_service.check_discount_eligibility("quote-1", 10)
        
        # Verify eligibility is limited
        self.assertTrue(eligibility["eligible"])
        self.assertLess(eligibility["max_discount"], 10)
        self.assertFalse(eligibility["auto_approve"])

    @patch("warehouse_quote_app.app.services.quote_service.QuoteService._get_quote")
    @patch("warehouse_quote_app.app.services.quote_service.QuoteService.check_discount_eligibility")
    def test_apply_discount(self, mock_check_eligibility, mock_get_quote):
        """Test discount application."""
        logger.info("Testing discount application")
        
        # Set up mocks
        mock_quote = Quote(
            id=1,
            user_id=self.user_id,
            customer_id=self.customer_id,
            total_amount=Decimal("1200.00"),
            status="draft",
            service_type="storage",
            storage_type="household",
            duration_weeks=12,
            quantity="medium",
            special_instructions="Need climate control",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        mock_get_quote.return_value = mock_quote
        
        mock_check_eligibility.return_value = {
            "eligible": True,
            "max_discount": 15,
            "auto_approve": True
        }
        
        # Apply discount
        discount_result = self.quote_service.apply_discount(
            "quote-1", 
            discount_percentage=10, 
            reason="Valued customer"
        )
        
        # Verify discount application
        self.assertEqual(discount_result["status"], "approved")
        self.assertEqual(discount_result["original_amount"], Decimal("1200.00"))
        self.assertEqual(discount_result["discounted_amount"], Decimal("1080.00"))
        self.assertEqual(discount_result["discount_percentage"], 10)
        
        # Verify quote was updated
        self.assertEqual(mock_quote.total_amount, Decimal("1080.00"))
        self.assertEqual(mock_quote.discount_percentage, 10)
        self.assertEqual(mock_quote.discount_reason, "Valued customer")
        
        # Test with discount requiring approval
        mock_check_eligibility.return_value = {
            "eligible": True,
            "max_discount": 10,
            "auto_approve": False
        }
        
        # Apply discount requiring approval
        discount_result = self.quote_service.apply_discount(
            "quote-1", 
            discount_percentage=10, 
            reason="Valued customer"
        )
        
        # Verify pending approval status
        self.assertEqual(discount_result["status"], "pending_approval")

    @patch("warehouse_quote_app.app.services.quote_service.QuoteService._get_quote")
    def test_approve_discount(self, mock_get_quote):
        """Test admin discount approval."""
        logger.info("Testing discount approval")
        
        # Set up mock quote with pending discount
        mock_quote = Quote(
            id=1,
            user_id=self.user_id,
            customer_id=self.customer_id,
            total_amount=Decimal("1200.00"),
            original_amount=Decimal("1200.00"),
            discount_percentage=10,
            discount_reason="Valued customer",
            discount_status="pending_approval",
            status="draft",
            service_type="storage",
            storage_type="household",
            duration_weeks=12,
            quantity="medium",
            special_instructions="Need climate control",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        mock_get_quote.return_value = mock_quote
        
        # Approve discount
        approval_result = self.quote_service.approve_discount(
            "quote-1", 
            approved_discount=10, 
            admin_id=2, 
            notes="Approved for valued customer"
        )
        
        # Verify approval
        self.assertEqual(approval_result["status"], "approved")
        self.assertEqual(approval_result["approved_discount"], 10)
        
        # Verify quote was updated
        self.assertEqual(mock_quote.total_amount, Decimal("1080.00"))
        self.assertEqual(mock_quote.discount_status, "approved")
        self.assertEqual(mock_quote.discount_approved_by, 2)
        self.assertEqual(mock_quote.discount_notes, "Approved for valued customer")

    @patch("warehouse_quote_app.app.services.quote_service.QuoteService._get_quote")
    def test_accept_quote(self, mock_get_quote):
        """Test quote acceptance."""
        logger.info("Testing quote acceptance")
        
        # Set up mock quote
        mock_quote = Quote(
            id=1,
            user_id=self.user_id,
            customer_id=self.customer_id,
            total_amount=Decimal("1200.00"),
            status="draft",
            service_type="storage",
            storage_type="household",
            duration_weeks=12,
            quantity="medium",
            special_instructions="Need climate control",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        mock_get_quote.return_value = mock_quote
        
        # Accept quote
        acceptance_result = self.quote_service.accept_quote("quote-1")
        
        # Verify acceptance
        self.assertEqual(acceptance_result["status"], "accepted")
        
        # Verify quote was updated
        self.assertEqual(mock_quote.status, "accepted")
        self.assertIsNotNone(mock_quote.accepted_at)

    @patch("warehouse_quote_app.app.services.quote_service.QuoteService._get_quote")
    def test_reject_quote(self, mock_get_quote):
        """Test quote rejection."""
        logger.info("Testing quote rejection")
        
        # Set up mock quote
        mock_quote = Quote(
            id=1,
            user_id=self.user_id,
            customer_id=self.customer_id,
            total_amount=Decimal("1200.00"),
            status="draft",
            service_type="storage",
            storage_type="household",
            duration_weeks=12,
            quantity="medium",
            special_instructions="Need climate control",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        mock_get_quote.return_value = mock_quote
        
        # Reject quote
        rejection_result = self.quote_service.reject_quote("quote-1", "Too expensive")
        
        # Verify rejection
        self.assertEqual(rejection_result["status"], "rejected")
        
        # Verify quote was updated
        self.assertEqual(mock_quote.status, "rejected")
        self.assertEqual(mock_quote.rejection_reason, "Too expensive")
        self.assertIsNotNone(mock_quote.rejected_at)

    @patch("warehouse_quote_app.app.services.quote_service.QuoteService._get_quotes_for_user")
    def test_get_user_quotes(self, mock_get_quotes_for_user):
        """Test retrieving quotes for a user."""
        logger.info("Testing user quote retrieval")
        
        # Set up mock quotes
        mock_quotes = [
            Quote(
                id=1,
                user_id=self.user_id,
                customer_id=self.customer_id,
                total_amount=Decimal("1200.00"),
                status="accepted",
                service_type="storage",
                storage_type="household",
                duration_weeks=12,
                quantity="medium",
                created_at=datetime.now() - timedelta(days=30),
                updated_at=datetime.now() - timedelta(days=30)
            ),
            Quote(
                id=2,
                user_id=self.user_id,
                customer_id=self.customer_id,
                total_amount=Decimal("2400.00"),
                status="draft",
                service_type="storage",
                storage_type="business",
                duration_weeks=24,
                quantity="large",
                created_at=datetime.now() - timedelta(days=7),
                updated_at=datetime.now() - timedelta(days=7)
            )
        ]
        mock_get_quotes_for_user.return_value = mock_quotes
        
        # Get quotes for user
        user_quotes = self.quote_service.get_quotes_for_user(self.user_id)
        
        # Verify quotes retrieval
        self.assertEqual(len(user_quotes), 2)
        self.assertEqual(user_quotes[0].id, 1)
        self.assertEqual(user_quotes[1].id, 2)
        
        # Test filtering by status
        mock_get_quotes_for_user.return_value = [mock_quotes[0]]
        
        # Get accepted quotes
        accepted_quotes = self.quote_service.get_quotes_for_user(self.user_id, status="accepted")
        
        # Verify filtered quotes
        self.assertEqual(len(accepted_quotes), 1)
        self.assertEqual(accepted_quotes[0].id, 1)
        self.assertEqual(accepted_quotes[0].status, "accepted")

    @patch("warehouse_quote_app.app.services.quote_service.QuoteService._get_quotes_for_customer")
    def test_get_customer_quotes(self, mock_get_quotes_for_customer):
        """Test retrieving quotes for a customer."""
        logger.info("Testing customer quote retrieval")
        
        # Set up mock quotes
        mock_quotes = [
            Quote(
                id=1,
                user_id=self.user_id,
                customer_id=self.customer_id,
                total_amount=Decimal("1200.00"),
                status="accepted",
                service_type="storage",
                storage_type="household",
                duration_weeks=12,
                quantity="medium",
                created_at=datetime.now() - timedelta(days=30),
                updated_at=datetime.now() - timedelta(days=30)
            ),
            Quote(
                id=2,
                user_id=self.user_id,
                customer_id=self.customer_id,
                total_amount=Decimal("2400.00"),
                status="draft",
                service_type="storage",
                storage_type="business",
                duration_weeks=24,
                quantity="large",
                created_at=datetime.now() - timedelta(days=7),
                updated_at=datetime.now() - timedelta(days=7)
            )
        ]
        mock_get_quotes_for_customer.return_value = mock_quotes
        
        # Get quotes for customer
        customer_quotes = self.quote_service.get_quotes_for_customer(self.customer_id)
        
        # Verify quotes retrieval
        self.assertEqual(len(customer_quotes), 2)
        self.assertEqual(customer_quotes[0].id, 1)
        self.assertEqual(customer_quotes[1].id, 2)


if __name__ == '__main__':
    unittest.main(verbosity=2)
