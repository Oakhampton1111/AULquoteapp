"""
End-to-end testing of customer and admin experiences with async support.

This test suite validates the complete user journey for both customers and administrators,
including authentication, quote generation, negotiation, and workflow management.
It properly handles async database operations.
"""

import pytest
import logging
from datetime import datetime, timedelta
from decimal import Decimal
from unittest.mock import MagicMock, patch, AsyncMock
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from warehouse_quote_app.app.main import app
from warehouse_quote_app.app.core.auth import create_access_token
from warehouse_quote_app.app.models.user import User
from warehouse_quote_app.app.models.customer import Customer
from warehouse_quote_app.app.models.quote import Quote, QuoteStatus
from warehouse_quote_app.app.models.negotiation import QuoteNegotiation
from warehouse_quote_app.app.schemas.quote import QuoteRequest, QuoteResponse
from warehouse_quote_app.app.schemas.user import UserCreate, UserLogin
from warehouse_quote_app.app.services.conversation.conversation_state import ConversationState
from warehouse_quote_app.app.services.communication.email import EmailService
# Import directly from the module to avoid circular imports
from warehouse_quote_app.app.database.db import get_db
from tests.utils import async_return, configure_mock_db_for_test, mock_repository_methods

# Set up logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


@pytest.fixture
def test_client():
    """Create a test client for the FastAPI app."""
    return TestClient(app)


@pytest.fixture
def test_user_data():
    """Return test user data."""
    return {
        "email": "testcustomer@example.com",
        "username": "testcustomer",
        "password": "securepassword123",
        "first_name": "Test",
        "last_name": "Customer"
    }


@pytest.fixture
def test_customer_data():
    """Return test customer data."""
    return {
        "company_name": "Test Company Ltd",
        "contact_email": "contact@testcompany.com",
        "phone": "1234567890",
        "address": "123 Test Street, Test City",
        "industry": "Manufacturing"
    }


@pytest.fixture
def test_quote_data():
    """Return test quote data."""
    return {
        "services": ["storage"],
        "storage_type": "household",
        "duration_weeks": 12,
        "quantity": "medium",
        "special_instructions": "Need climate control"
    }


@pytest.fixture
def test_negotiation_data():
    """Return test negotiation data."""
    return {
        "proposed_price": Decimal("850.00"),
        "reason": "Budget constraints",
        "counter_offer": True
    }


@pytest.fixture
def mock_email_service():
    """Create a mock email service."""
    mock = MagicMock(spec=EmailService)
    mock.send_email = AsyncMock()
    return mock


@pytest.fixture
def mock_user():
    """Create a mock user."""
    user = MagicMock(spec=User)
    user.id = 1
    user.email = "testcustomer@example.com"
    user.username = "testcustomer"
    user.is_active = True
    user.is_admin = False
    return user


@pytest.fixture
def mock_admin_user():
    """Create a mock admin user."""
    user = MagicMock(spec=User)
    user.id = 2
    user.email = "admin@example.com"
    user.username = "admin"
    user.is_active = True
    user.is_admin = True
    return user


@pytest.fixture
def mock_quote():
    """Create a mock quote."""
    quote = MagicMock(spec=Quote)
    quote.id = 1
    quote.user_id = 1
    quote.status = QuoteStatus.DRAFT
    quote.total_price = Decimal("1000.00")
    quote.created_at = datetime.now()
    quote.updated_at = datetime.now()
    return quote


@pytest.mark.asyncio
async def test_customer_registration_login(
    test_client, 
    test_user_data, 
    mock_async_db, 
    mock_email_service,
    override_get_db
):
    """Test customer registration and login process."""
    # Configure mock DB to return a user after registration
    mock_user = MagicMock(spec=User)
    mock_user.id = 1
    mock_user.email = test_user_data["email"]
    mock_user.username = test_user_data["username"]
    mock_user.is_active = True
    mock_user.is_admin = False
    
    # Configure the mock database
    test_data = {
        "User": [mock_user]
    }
    configure_mock_db_for_test(mock_async_db, test_data)
    
    # Step 1: Register a new customer
    logger.info("Testing customer registration")
    register_response = test_client.post(
        "/api/v1/auth/register",
        json=test_user_data
    )
    
    # Verify registration was successful
    assert register_response.status_code == 201
    assert "id" in register_response.json()
    assert "email" in register_response.json()
    
    # Step 2: Login with the new customer
    logger.info("Testing customer login")
    login_response = test_client.post(
        "/api/v1/auth/login",
        data={"username": test_user_data["email"], "password": test_user_data["password"]}
    )
    
    # Verify login was successful
    assert login_response.status_code == 200
    assert "access_token" in login_response.json()
    assert "token_type" in login_response.json()
    
    # Store token for subsequent requests
    access_token = login_response.json()["access_token"]
    
    # Step 3: Access the customer dashboard
    logger.info("Testing customer dashboard access")
    dashboard_response = test_client.get(
        "/api/v1/dashboard",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    
    # Verify dashboard access
    assert dashboard_response.status_code == 200
    dashboard_data = dashboard_response.json()
    
    # Verify dashboard contains required components
    assert "user_info" in dashboard_data
    assert "recent_quotes" in dashboard_data