"""
Quote-related background tasks.
"""

from datetime import datetime, timedelta
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from warehouse_quote_app.app.core.tasks.celery import celery_app
from warehouse_quote_app.app.models.quote import Quote
from warehouse_quote_app.app.core.db import get_db

@celery_app.task
def cleanup_expired_quotes() -> int:
    """Clean up expired quotes from the database.
    
    Returns:
        int: Number of quotes deleted
    """
    session = next(get_db())
    
    # Get quotes that expired more than 30 days ago
    expiry_date = datetime.utcnow() - timedelta(days=30)
    
    # Delete expired quotes
    result = session.execute(
        delete(Quote).where(Quote.expiry_date < expiry_date)
    )
    session.commit()
    
    return result.rowcount

__all__ = ['cleanup_expired_quotes']
