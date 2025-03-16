"""
CRUD operations module.

This module provides CRUD (Create, Read, Update, Delete) operations for various entities
in the application. It serves as a compatibility layer for code that was previously
using the 'crud' module directly.
"""

from warehouse_quote_app.app.repositories.user import UserRepository
from warehouse_quote_app.app.repositories.quote import QuoteRepository
from warehouse_quote_app.app.repositories.rate import RateRepository
from warehouse_quote_app.app.models.user import User
from warehouse_quote_app.app.models.quote import Quote
from warehouse_quote_app.app.models.rate import Rate

# Create repository instances with their respective models
user = UserRepository(User)
quote = QuoteRepository(Quote)
rate = RateRepository(Rate)

__all__ = [
    "user",
    "quote",
    "rate"
]
