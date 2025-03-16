"""
Comprehensive testing of the admin dashboard functionality.

This test suite validates the admin dashboard components, including customer management,
quote review, discount approval, reporting, and rate card management.
"""

import unittest
import logging
import asyncio
from datetime import datetime, timedelta
from decimal import Decimal
from unittest.mock import MagicMock, patch
import pytest
from fastapi.testclient import TestClient

from warehouse_quote_app.app.main import app
from warehouse_quote_app.app.core.auth import create_access_token
from warehouse_quote_app.app.models.user import User
from warehouse_quote_app.app.models.customer import Customer
from warehouse_quote_app.app.models.quote import Quote
from warehouse_quote_app.app.models.rate import Rate
from warehouse_quote_app.app.services.reporting_service import ReportingService
from warehouse_quote_app.app.database import get_db

# Set up logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TestAdminDashboard(unittest.TestCase):
    """Test the admin dashboard functionality."""
    
    def setUp(self):
        """Set up test environment."""
        self.client = TestClient(app)
        
        # Create admin token
        self.admin_token = create_access_token({"sub": "admin@example.com", "is_admin": True})
        
        # Mock services
        self.mock_reporting_service = MagicMock(spec=ReportingService)
        
        logger.info("=== Starting admin dashboard test case ===")

    @patch("warehouse_quote_app.app.database.get_db")
    def test_admin_dashboard_access(self, mock_get_db):
        """Test admin dashboard access and components."""
        logger.info("Testing admin dashboard access")
        
        # Mock database session
        mock_db = MagicMock()
        mock_get_db.return_value = mock_db
        
        # Set up mock data
        mock_customers = [
            Customer(
                id=1,
                company_name="Test Company 1",
                contact_email="contact1@example.com",
                phone="1234567890",
                address="123 Test St",
                industry="Manufacturing",
                total_quotes=10,
                accepted_quotes=8,
                total_spend=Decimal("10000.00"),
                created_at=datetime.now() - timedelta(days=365),
                updated_at=datetime.now()
            ),
            Customer(
                id=2,
                company_name="Test Company 2",
                contact_email="contact2@example.com",
                phone="0987654321",
                address="456 Test Ave",
                industry="Retail",
                total_quotes=5,
                accepted_quotes=3,
                total_spend=Decimal("5000.00"),
                created_at=datetime.now() - timedelta(days=180),
                updated_at=datetime.now()
            )
        ]
        
        mock_quotes = [
            Quote(
                id=1,
                user_id=1,
                customer_id=1,
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
                user_id=2,
                customer_id=2,
                total_amount=Decimal("2400.00"),
                status="pending_approval",
                service_type="storage",
                storage_type="business",
                duration_weeks=24,
                quantity="large",
                discount_percentage=10,
                discount_status="pending_approval",
                created_at=datetime.now() - timedelta(days=7),
                updated_at=datetime.now() - timedelta(days=7)
            )
        ]
        
        # Configure mocks
        mock_db.query.side_effect = lambda model: MagicMock(
            all=lambda: mock_customers if model == Customer else mock_quotes,
            filter=lambda *args, **kwargs: MagicMock(
                all=lambda: [q for q in mock_quotes if q.status == "pending_approval"] if "status" in str(args) else mock_quotes
            )
        )
        
        # Access admin dashboard
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
        
        # Verify customer data
        self.assertEqual(len(dashboard_data["customers"]), 2)
        self.assertEqual(dashboard_data["customers"][0]["company_name"], "Test Company 1")
        
        # Verify quote data
        self.assertEqual(len(dashboard_data["quotes"]), 2)
        
        # Verify pending approvals
        self.assertEqual(len(dashboard_data["pending_approvals"]), 1)
        self.assertEqual(dashboard_data["pending_approvals"][0]["id"], 2)

    @patch("warehouse_quote_app.app.database.get_db")
    def test_customer_management(self, mock_get_db):
        """Test customer management functionality."""
        logger.info("Testing customer management")
        
        # Mock database session
        mock_db = MagicMock()
        mock_get_db.return_value = mock_db
        
        # Set up mock data
        mock_customer = Customer(
            id=1,
            company_name="Test Company",
            contact_email="contact@example.com",
            phone="1234567890",
            address="123 Test St",
            industry="Manufacturing",
            total_quotes=10,
            accepted_quotes=8,
            total_spend=Decimal("10000.00"),
            created_at=datetime.now() - timedelta(days=365),
            updated_at=datetime.now()
        )
        
        # Configure mocks
        mock_db.query.return_value.filter.return_value.first.return_value = mock_customer
        mock_db.add.return_value = None
        mock_db.commit.return_value = None
        mock_db.refresh.return_value = None
        
        # View customer details
        details_response = self.client.get(
            "/api/v1/admin/customers/1",
            headers={"Authorization": f"Bearer {self.admin_token}"}
        )
        
        # Verify customer details
        self.assertEqual(details_response.status_code, 200)
        self.assertEqual(details_response.json()["company_name"], "Test Company")
        
        # Update customer
        update_data = {
            "company_name": "Updated Company",
            "contact_email": "updated@example.com",
            "phone": "9876543210"
        }
        
        update_response = self.client.put(
            "/api/v1/admin/customers/1",
            json=update_data,
            headers={"Authorization": f"Bearer {self.admin_token}"}
        )
        
        # Verify update
        self.assertEqual(update_response.status_code, 200)
        
        # Create new customer
        new_customer_data = {
            "company_name": "New Company",
            "contact_email": "new@example.com",
            "phone": "5555555555",
            "address": "555 New St",
            "industry": "Technology"
        }
        
        # Mock the add method to set the id
        def mock_add(customer):
            customer.id = 2
            return None
            
        mock_db.add.side_effect = mock_add
        
        create_response = self.client.post(
            "/api/v1/admin/customers",
            json=new_customer_data,
            headers={"Authorization": f"Bearer {self.admin_token}"}
        )
        
        # Verify creation
        self.assertEqual(create_response.status_code, 201)
        self.assertEqual(create_response.json()["id"], 2)
        self.assertEqual(create_response.json()["company_name"], "New Company")

    @patch("warehouse_quote_app.app.database.get_db")
    def test_quote_approval(self, mock_get_db):
        """Test quote approval functionality."""
        logger.info("Testing quote approval")
        
        # Mock database session
        mock_db = MagicMock()
        mock_get_db.return_value = mock_db
        
        # Set up mock data
        mock_quote = Quote(
            id=1,
            user_id=1,
            customer_id=1,
            total_amount=Decimal("1200.00"),
            original_amount=Decimal("1200.00"),
            status="draft",
            service_type="storage",
            storage_type="business",
            duration_weeks=24,
            quantity="large",
            discount_percentage=10,
            discount_status="pending_approval",
            created_at=datetime.now() - timedelta(days=7),
            updated_at=datetime.now() - timedelta(days=7)
        )
        
        # Configure mocks
        mock_db.query.return_value.filter.return_value.first.return_value = mock_quote
        mock_db.commit.return_value = None
        
        # Approve quote discount
        approval_data = {
            "approved_discount": 10,
            "notes": "Approved for valued customer"
        }
        
        approve_response = self.client.post(
            "/api/v1/admin/quotes/1/approve",
            json=approval_data,
            headers={"Authorization": f"Bearer {self.admin_token}"}
        )
        
        # Verify approval
        self.assertEqual(approve_response.status_code, 200)
        self.assertEqual(approve_response.json()["status"], "approved")
        
        # Verify quote was updated
        self.assertEqual(mock_quote.discount_status, "approved")
        self.assertEqual(mock_quote.total_amount, Decimal("1080.00"))  # 10% discount applied

    @patch("warehouse_quote_app.app.database.get_db")
    @patch("warehouse_quote_app.app.services.reporting_service.ReportingService.generate_quote_status_report")
    def test_reporting(self, mock_generate_status_report, mock_get_db):
        """Test reporting functionality."""
        logger.info("Testing reporting functionality")
        
        # Mock database session
        mock_db = MagicMock()
        mock_get_db.return_value = mock_db
        
        # Set up mock report data
        mock_status_report = {
            "pending": 5,
            "accepted": 10,
            "rejected": 2,
            "completed": 8,
            "total": 25
        }
        
        mock_generate_status_report.return_value = mock_status_report
        
        # Get quote status report
        report_response = self.client.get(
            "/api/v1/admin/reports/quotes/status",
            headers={"Authorization": f"Bearer {self.admin_token}"}
        )
        
        # Verify report
        self.assertEqual(report_response.status_code, 200)
        self.assertEqual(report_response.json()["pending"], 5)
        self.assertEqual(report_response.json()["accepted"], 10)
        self.assertEqual(report_response.json()["total"], 25)
        
        # Set up mock revenue report
        mock_revenue_report = {
            "total": Decimal("50000.00"),
            "breakdown": {
                "storage": Decimal("30000.00"),
                "transport": Decimal("15000.00"),
                "packaging": Decimal("5000.00")
            }
        }
        
        # Mock the revenue report method
        with patch("warehouse_quote_app.app.services.reporting_service.ReportingService.generate_revenue_report") as mock_generate_revenue:
            mock_generate_revenue.return_value = mock_revenue_report
            
            # Get revenue report
            revenue_response = self.client.get(
                "/api/v1/admin/reports/revenue",
                params={"period": "month"},
                headers={"Authorization": f"Bearer {self.admin_token}"}
            )
            
            # Verify report
            self.assertEqual(revenue_response.status_code, 200)
            self.assertEqual(revenue_response.json()["total"], "50000.00")
            self.assertEqual(revenue_response.json()["breakdown"]["storage"], "30000.00")

    @patch("warehouse_quote_app.app.database.get_db")
    def test_rate_management(self, mock_get_db):
        """Test rate management functionality."""
        logger.info("Testing rate management")
        
        # Mock database session
        mock_db = MagicMock()
        mock_get_db.return_value = mock_db
        
        # Set up mock data
        mock_rates = [
            Rate(
                id=1,
                service_type="storage",
                storage_type="household",
                quantity="medium",
                rate_amount=Decimal("100.00"),
                unit="week",
                effective_date=datetime.now() - timedelta(days=30),
                expiration_date=datetime.now() + timedelta(days=30)
            ),
            Rate(
                id=2,
                service_type="storage",
                storage_type="business",
                quantity="large",
                rate_amount=Decimal("200.00"),
                unit="week",
                effective_date=datetime.now() - timedelta(days=30),
                expiration_date=datetime.now() + timedelta(days=30)
            )
        ]
        
        # Configure mocks
        mock_db.query.return_value.all.return_value = mock_rates
        mock_db.query.return_value.filter.return_value.first.return_value = mock_rates[0]
        mock_db.add.return_value = None
        mock_db.commit.return_value = None
        
        # Get all rates
        rates_response = self.client.get(
            "/api/v1/admin/rates",
            headers={"Authorization": f"Bearer {self.admin_token}"}
        )
        
        # Verify rates
        self.assertEqual(rates_response.status_code, 200)
        self.assertEqual(len(rates_response.json()), 2)
        self.assertEqual(rates_response.json()[0]["rate_amount"], "100.00")
        
        # Update a rate
        update_data = {
            "rate_amount": 110.00,
            "effective_date": (datetime.now() + timedelta(days=1)).isoformat()
        }
        
        update_response = self.client.put(
            "/api/v1/admin/rates/1",
            json=update_data,
            headers={"Authorization": f"Bearer {self.admin_token}"}
        )
        
        # Verify update
        self.assertEqual(update_response.status_code, 200)
        
        # Create a new rate
        new_rate_data = {
            "service_type": "packaging",
            "quantity": "small",
            "rate_amount": 50.00,
            "unit": "item",
            "effective_date": datetime.now().isoformat()
        }
        
        # Mock the add method to set the id
        def mock_add(rate):
            rate.id = 3
            return None
            
        mock_db.add.side_effect = mock_add
        
        create_response = self.client.post(
            "/api/v1/admin/rates",
            json=new_rate_data,
            headers={"Authorization": f"Bearer {self.admin_token}"}
        )
        
        # Verify creation
        self.assertEqual(create_response.status_code, 201)
        self.assertEqual(create_response.json()["id"], 3)
        self.assertEqual(create_response.json()["service_type"], "packaging")


if __name__ == '__main__':
    unittest.main(verbosity=2)
