"""Database session access function."""

from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession

# Global variable to hold the sessionmanager
# This will be initialized in session.py
_sessionmanager = None

def initialize_sessionmanager(manager):
    """Initialize the sessionmanager reference."""
    global _sessionmanager
    _sessionmanager = manager

async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    """Get async database session."""
    if _sessionmanager is None:
        raise RuntimeError("SessionManager not initialized. Call initialize_sessionmanager first.")
    
    async with _sessionmanager.session() as session:
        yield session
