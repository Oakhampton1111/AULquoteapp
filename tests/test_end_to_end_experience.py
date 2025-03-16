"""
End-to-end testing of customer and admin experiences.

This test suite validates the complete user journey for both customers and administrators,
including authentication, quote generation, negotiation, and workflow management.
"""

import unittest
import logging
import asyncio
from datetime import datetime, timedelta
from decimal import Decimal
from unittest.mock import MagicMock, patch
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from warehouse_quote_app.app.main import app
from warehouse_quote_app.app.core.auth import create_access_token
from warehouse_quote_app.app.models.user import User
from warehouse_quote_app.app.models.customer import Customer
from warehouse_quote_app.app.models.quote import Quote
from warehouse_quote_app.app.schemas.quote import QuoteRequest, QuoteResponse
from warehouse_quote_app.app.schemas.user import UserCreate, UserLogin
from warehouse_quote_app.app.services.conversation.conversation_state import ConversationState
from warehouse_quote_app.app.services.communication.email import EmailService
from warehouse_quote_app.app.database import get_db

# Set up logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TestCustomerExperience(unittest.TestCase):
    """Test the complete customer experience from login to quote management."""
    
    def setUp(self):
        """Set up test environment."""
        self.client = TestClient(app)
        
        # Mock database session
        self.mock_db = MagicMock(spec=AsyncSession)
        
        # Mock services
        self.mock_email_service = MagicMock(spec=EmailService)
        
        # Test user data
        self.test_user_data = {
            "email": "testcustomer@example.com",
            "username": "testcustomer",
            "password": "securepassword123",
            "first_name": "Test",
            "last_name": "Customer"
        }
        
        # Test customer data
        self.test_customer_data = {
            "company_name": "Test Company Ltd",
            "contact_email": "contact@testcompany.com",
            "phone": "1234567890",
            "address": "123 Test Street, Test City",
            "industry": "Manufacturing"
        }
        
        # Test quote data
        self.test_quote_data = {
            "services": ["storage"],
            "storage_type": "household",
            "duration_weeks": 12,
            "quantity": "medium",
            "special_instructions": "Need climate control"
        }
        
        logger.info("=== Starting customer experience test case ===")

    @patch("warehouse_quote_app.app.database.get_db")
    @patch("warehouse_quote_app.app.services.communication.email.EmailService.send_email")
    def test_customer_registration_login(self, mock_send_email, mock_get_db):
        """Test customer registration and login process."""
        mock_get_db.return_value = self.mock_db
        
        # Step 1: Register a new customer
        logger.info("Testing customer registration")
        register_response = self.client.post(
            "/api/v1/auth/register",
            json=self.test_user_data
        )
        
        # Verify registration was successful
        self.assertEqual(register_response.status_code, 201)
        self.assertIn("id", register_response.json())
        self.assertIn("email", register_response.json())
        
        # Verify welcome email was sent
        mock_send_email.assert_called_once()
        
        # Step 2: Login with the new customer
        logger.info("Testing customer login")
        login_response = self.client.post(
            "/api/v1/auth/login",
            data={"username": self.test_user_data["email"], "password": self.test_user_data["password"]}
        )
        
        # Verify login was successful
        self.assertEqual(login_response.status_code, 200)
        self.assertIn("access_token", login_response.json())
        self.assertIn("token_type", login_response.json())
        
        # Store token for subsequent requests
        self.access_token = login_response.json()["access_token"]
        
        # Step 3: Access the customer dashboard
        logger.info("Testing customer dashboard access")
        dashboard_response = self.client.get(
            "/api/v1/dashboard",
            headers={"Authorization": f"Bearer {self.access_token}"}
        )
        
        # Verify dashboard access
        self.assertEqual(dashboard_response.status_code, 200)
        dashboard_data = dashboard_response.json()
        
        # Verify dashboard contains required components
        self.assertIn("user_info", dashboard_data)
        self.assertIn("recent_quotes", dashboard_data)
        self.assertIn("terms_and_conditions_url", dashboard_data)
        self.assertIn("rate_card_url", dashboard_data)

    @patch("warehouse_quote_app.app.database.get_db")
    @patch("warehouse_quote_app.app.services.conversation.conversation_state.ConversationState")
    def test_nlp_quote_generation(self, mock_conversation_state, mock_get_db):
        """Test generating a quote through the NLP interface."""
        mock_get_db.return_value = self.mock_db
        
        # Mock conversation state
        mock_conversation = MagicMock()
        mock_conversation_state.return_value.new_conversation.return_value = mock_conversation
        
        # Create a token for authentication
        token = create_access_token({"sub": "testcustomer@example.com"})
        
        # Step 1: Start a conversation
        logger.info("Testing conversation initiation")
        start_response = self.client.post(
            "/api/v1/chat/start",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        # Verify conversation started
        self.assertEqual(start_response.status_code, 200)
        self.assertIn("conversation_id", start_response.json())
        conversation_id = start_response.json()["conversation_id"]
        
        # Step 2: Send initial query
        logger.info("Testing initial query")
        query_response = self.client.post(
            "/api/v1/chat/message",
            json={"conversation_id": conversation_id, "message": "I need storage for household items for 3 months"},
            headers={"Authorization": f"Bearer {token}"}
        )
        
        # Verify query response
        self.assertEqual(query_response.status_code, 200)
        self.assertIn("messages", query_response.json())
        self.assertIn("questions", query_response.json())
        
        # Step 3: Respond to quantity question
        logger.info("Testing quantity response")
        quantity_response = self.client.post(
            "/api/v1/chat/message",
            json={"conversation_id": conversation_id, "message": "medium size"},
            headers={"Authorization": f"Bearer {token}"}
        )
        
        # Verify quantity response
        self.assertEqual(quantity_response.status_code, 200)
        
        # Step 4: Get generated quote
        logger.info("Testing quote generation")
        quote_response = self.client.get(
            f"/api/v1/quotes/{conversation_id}/result",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        # Verify quote was generated
        self.assertEqual(quote_response.status_code, 200)
        self.assertIn("quote_id", quote_response.json())
        self.assertIn("total_amount", quote_response.json())
        self.assertIn("service_type", quote_response.json())
        
        # Store quote ID for subsequent tests
        self.quote_id = quote_response.json()["quote_id"]

    @patch("warehouse_quote_app.app.database.get_db")
    @patch("warehouse_quote_app.app.services.communication.email.EmailService.send_email")
    def test_quote_negotiation_acceptance(self, mock_send_email, mock_get_db):
        """Test quote negotiation and acceptance process."""
        mock_get_db.return_value = self.mock_db
        
        # Create a token for authentication
        token = create_access_token({"sub": "testcustomer@example.com"})
        
        # Create a mock quote ID if not already set
        if not hasattr(self, 'quote_id'):
            self.quote_id = "mock-quote-id-12345"
        
        # Step 1: Request a discount
        logger.info("Testing discount request")
        discount_response = self.client.post(
            f"/api/v1/quotes/{self.quote_id}/negotiate",
            json={"discount_percentage": 10, "reason": "Long-term customer"},
            headers={"Authorization": f"Bearer {token}"}
        )
        
        # Verify discount request
        self.assertEqual(discount_response.status_code, 200)
        self.assertIn("status", discount_response.json())
        
        # Check if discount was auto-approved or needs admin review
        if discount_response.json()["status"] == "pending_approval":
            # Step 2a: Admin approves discount (simulated)
            logger.info("Testing admin approval of discount")
            
            # Create admin token
            admin_token = create_access_token({"sub": "admin@example.com", "is_admin": True})
            
            approve_response = self.client.post(
                f"/api/v1/admin/quotes/{self.quote_id}/approve",
                json={"approved_discount": 10, "notes": "Approved for valued customer"},
                headers={"Authorization": f"Bearer {admin_token}"}
            )
            
            # Verify admin approval
            self.assertEqual(approve_response.status_code, 200)
            
            # Verify notification email was sent
            mock_send_email.assert_called_with(
                recipient="testcustomer@example.com",
                subject="Quote Discount Approved",
                template="quote_discount_approved",
                template_data={"quote_id": self.quote_id}
            )
        
        # Step 3: Accept the quote
        logger.info("Testing quote acceptance")
        accept_response = self.client.post(
            f"/api/v1/quotes/{self.quote_id}/accept",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        # Verify quote acceptance
        self.assertEqual(accept_response.status_code, 200)
        self.assertIn("status", accept_response.json())
        self.assertEqual(accept_response.json()["status"], "accepted")
        
        # Verify notification email was sent
        mock_send_email.assert_called()

    @patch("warehouse_quote_app.app.database.get_db")
    def test_view_past_quotes(self, mock_get_db):
        """Test viewing and filtering past quotes."""
        mock_get_db.return_value = self.mock_db
        
        # Create a token for authentication
        token = create_access_token({"sub": "testcustomer@example.com"})
        
        # Step 1: View all quotes
        logger.info("Testing view all quotes")
        all_quotes_response = self.client.get(
            "/api/v1/quotes/my",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        # Verify quotes retrieval
        self.assertEqual(all_quotes_response.status_code, 200)
        self.assertIsInstance(all_quotes_response.json(), list)
        
        # Step 2: Filter quotes by status
        logger.info("Testing quote filtering by status")
        filtered_quotes_response = self.client.get(
            "/api/v1/quotes/my?status=accepted",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        # Verify filtered quotes
        self.assertEqual(filtered_quotes_response.status_code, 200)
        self.assertIsInstance(filtered_quotes_response.json(), list)
        
        # Ensure all returned quotes have the correct status
        for quote in filtered_quotes_response.json():
            self.assertEqual(quote["status"], "accepted")


class TestAdminExperience(unittest.TestCase):
    """Test the complete admin experience."""
    
    def setUp(self):
        """Set up test environment."""
        self.client = TestClient(app)
        
        # Mock database session
        self.mock_db = MagicMock(spec=AsyncSession)
        
        # Test admin data
        self.test_admin_data = {
            "email": "admin@example.com",
            "username": "admin",
            "password": "adminpassword123",
            "is_admin": True
        }
        
        # Create admin token
        self.admin_token = create_access_token({"sub": "admin@example.com", "is_admin": True})
        
        logger.info("=== Starting admin experience test case ===")

    @patch("warehouse_quote_app.app.database.get_db")
    def test_admin_dashboard_access(self, mock_get_db):
        """Test admin dashboard access and components."""
        mock_get_db.return_value = self.mock_db
        
        # Step 1: Access admin dashboard
        logger.info("Testing admin dashboard access")
        dashboard_response = self.client.get(
            "/api/v1/admin/dashboard",
            headers={"Authorization": f"Bearer {self.admin_token}"}
        )
        
        # Verify dashboard access
        self.assertEqual(dashboard_response.status_code, 200)
        dashboard_data = dashboard_response.json()
        
        # Verify dashboard contains required components
        self.assertIn("customers", dashboard_data)
        self.assertIn("quotes", dashboard_data)
        self.assertIn("pending_approvals", dashboard_data)
        self.assertIn("reports", dashboard_data)

    @patch("warehouse_quote_app.app.database.get_db")
    def test_admin_customer_management(self, mock_get_db):
        """Test admin customer management functionality."""
        mock_get_db.return_value = self.mock_db
        
        # Step 1: List all customers
        logger.info("Testing customer listing")
        customers_response = self.client.get(
            "/api/v1/admin/customers",
            headers={"Authorization": f"Bearer {self.admin_token}"}
        )
        
        # Verify customers list
        self.assertEqual(customers_response.status_code, 200)
        self.assertIsInstance(customers_response.json(), list)
        
        # Step 2: Create a new customer
        logger.info("Testing customer creation")
        new_customer_data = {
            "company_name": "New Test Company",
            "contact_email": "contact@newtestcompany.com",
            "phone": "9876543210",
            "address": "456 New Street, New City",
            "industry": "Retail"
        }
        
        create_response = self.client.post(
            "/api/v1/admin/customers",
            json=new_customer_data,
            headers={"Authorization": f"Bearer {self.admin_token}"}
        )
        
        # Verify customer creation
        self.assertEqual(create_response.status_code, 201)
        self.assertIn("id", create_response.json())
        
        # Store customer ID for subsequent tests
        customer_id = create_response.json()["id"]
        
        # Step 3: View customer details
        logger.info("Testing customer details view")
        details_response = self.client.get(
            f"/api/v1/admin/customers/{customer_id}",
            headers={"Authorization": f"Bearer {self.admin_token}"}
        )
        
        # Verify customer details
        self.assertEqual(details_response.status_code, 200)
        self.assertEqual(details_response.json()["company_name"], new_customer_data["company_name"])

    @patch("warehouse_quote_app.app.database.get_db")
    @patch("warehouse_quote_app.app.services.communication.email.EmailService.send_email")
    def test_admin_quote_management(self, mock_send_email, mock_get_db):
        """Test admin quote management functionality."""
        mock_get_db.return_value = self.mock_db
        
        # Step 1: List quotes pending approval
        logger.info("Testing pending quotes listing")
        pending_response = self.client.get(
            "/api/v1/admin/quotes/pending",
            headers={"Authorization": f"Bearer {self.admin_token}"}
        )
        
        # Verify pending quotes list
        self.assertEqual(pending_response.status_code, 200)
        self.assertIsInstance(pending_response.json(), list)
        
        # If there are pending quotes, approve one
        if pending_response.json():
            quote_id = pending_response.json()[0]["id"]
            
            # Step 2: Approve a quote with discount
            logger.info("Testing quote approval")
            approve_response = self.client.post(
                f"/api/v1/admin/quotes/{quote_id}/approve",
                json={"approved_discount": 10, "notes": "Approved for valued customer"},
                headers={"Authorization": f"Bearer {self.admin_token}"}
            )
            
            # Verify quote approval
            self.assertEqual(approve_response.status_code, 200)
            self.assertEqual(approve_response.json()["status"], "approved")
            
            # Verify notification email was sent
            mock_send_email.assert_called()
        
        # Step 3: Create a quote for a customer
        logger.info("Testing quote creation for customer")
        
        # First get a customer ID
        customers_response = self.client.get(
            "/api/v1/admin/customers",
            headers={"Authorization": f"Bearer {self.admin_token}"}
        )
        
        if customers_response.json():
            customer_id = customers_response.json()[0]["id"]
            
            # Create quote
            new_quote_data = {
                "customer_id": customer_id,
                "services": ["storage"],
                "storage_type": "business",
                "duration_weeks": 24,
                "quantity": "large",
                "special_instructions": "High security required"
            }
            
            create_quote_response = self.client.post(
                "/api/v1/admin/quotes",
                json=new_quote_data,
                headers={"Authorization": f"Bearer {self.admin_token}"}
            )
            
            # Verify quote creation
            self.assertEqual(create_quote_response.status_code, 201)
            self.assertIn("id", create_quote_response.json())
            
            # Verify notification email was sent
            mock_send_email.assert_called()

    @patch("warehouse_quote_app.app.database.get_db")
    def test_admin_rate_management(self, mock_get_db):
        """Test admin rate management functionality."""
        mock_get_db.return_value = self.mock_db
        
        # Step 1: View current rates
        logger.info("Testing rate card view")
        rates_response = self.client.get(
            "/api/v1/admin/rates",
            headers={"Authorization": f"Bearer {self.admin_token}"}
        )
        
        # Verify rates retrieval
        self.assertEqual(rates_response.status_code, 200)
        self.assertIsInstance(rates_response.json(), list)
        
        # Step 2: Update a rate
        logger.info("Testing rate update")
        
        # If there are rates, update one
        if rates_response.json():
            rate_id = rates_response.json()[0]["id"]
            current_rate = rates_response.json()[0]["rate_amount"]
            
            update_rate_data = {
                "rate_amount": float(current_rate) * 1.05,  # 5% increase
                "effective_date": (datetime.now() + timedelta(days=30)).isoformat()
            }
            
            update_response = self.client.put(
                f"/api/v1/admin/rates/{rate_id}",
                json=update_rate_data,
                headers={"Authorization": f"Bearer {self.admin_token}"}
            )
            
            # Verify rate update
            self.assertEqual(update_response.status_code, 200)
            self.assertNotEqual(update_response.json()["rate_amount"], current_rate)

    @patch("warehouse_quote_app.app.database.get_db")
    def test_admin_reporting(self, mock_get_db):
        """Test admin reporting functionality."""
        mock_get_db.return_value = self.mock_db
        
        # Step 1: View quote status report
        logger.info("Testing quote status report")
        status_report_response = self.client.get(
            "/api/v1/admin/reports/quotes/status",
            headers={"Authorization": f"Bearer {self.admin_token}"}
        )
        
        # Verify report retrieval
        self.assertEqual(status_report_response.status_code, 200)
        self.assertIn("pending", status_report_response.json())
        self.assertIn("accepted", status_report_response.json())
        self.assertIn("rejected", status_report_response.json())
        
        # Step 2: View revenue report
        logger.info("Testing revenue report")
        revenue_report_response = self.client.get(
            "/api/v1/admin/reports/revenue",
            params={"period": "month"},
            headers={"Authorization": f"Bearer {self.admin_token}"}
        )
        
        # Verify report retrieval
        self.assertEqual(revenue_report_response.status_code, 200)
        self.assertIn("total", revenue_report_response.json())
        self.assertIn("breakdown", revenue_report_response.json())


if __name__ == '__main__':
    unittest.main(verbosity=2)
