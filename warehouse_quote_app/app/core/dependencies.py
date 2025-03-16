"""
Shared dependencies for FastAPI dependency injection.
This module is designed to avoid circular imports by providing a central
location for common dependencies used across the application.
"""

from typing import AsyncGenerator, Annotated
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

# This will be imported from database.session after initialization
# We set it to None initially to avoid the circular import
get_db_dependency = None

# Type annotation for database dependency injection
DbSession = None
