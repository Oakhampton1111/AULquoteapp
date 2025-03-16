"""
Test configuration and fixtures.

This module provides pytest fixtures for testing the warehouse quote application.
"""

import asyncio
from typing import AsyncGenerator, Generator
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from sqlalchemy.ext.asyncio import AsyncSession

# Import directly from the module to avoid circular imports
from warehouse_quote_app.app.database.db import get_db


@pytest.fixture
def event_loop():
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def mock_async_db() -> AsyncGenerator[AsyncMock, None]:
    """
    Create a mock async database session.
    
    This fixture creates an AsyncMock that can be used to mock the database
    session in tests. It properly handles async context manager behavior.
    """
    mock_session = AsyncMock(spec=AsyncSession)
    
    # Add common mock methods that tests might use
    mock_session.commit = AsyncMock()
    mock_session.rollback = AsyncMock()
    mock_session.close = AsyncMock()
    mock_session.execute = AsyncMock()
    mock_session.refresh = AsyncMock()
    
    # Make query results return empty lists by default
    mock_session.execute.return_value.scalars().all.return_value = []
    mock_session.execute.return_value.first.return_value = None
    
    yield mock_session


@pytest.fixture
async def override_get_db(mock_async_db: AsyncMock) -> AsyncGenerator[AsyncSession, None]:
    """
    Override the get_db dependency with our mock database session.
    
    This fixture can be used to patch the get_db dependency in tests.
    """
    # Create a new async generator function that yields our mock
    async def _override_get_db():
        yield mock_async_db
    
    # Use patch to replace the dependency
    with patch('warehouse_quote_app.app.database.db.get_db', _override_get_db):
        yield mock_async_db