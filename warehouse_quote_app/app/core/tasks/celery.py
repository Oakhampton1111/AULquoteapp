"""
Celery configuration and task queue setup.
"""

from celery import Celery
from celery.schedules import crontab
from pathlib import Path
import os
from typing import Any, Dict

from warehouse_quote_app.app.core.config import settings

# Create Celery app
celery_app = Celery(
    'warehouse_quote_app',
    broker='redis://localhost:6379/0',
    backend='redis://localhost:6379/0',
    include=[
        'app.services.business.tasks.rates',  # Rate-related tasks
        'app.core.tasks.cleanup',            # General cleanup tasks
        'app.core.tasks.monitoring',          # Monitoring tasks
        'warehouse_quote_app.app.core.tasks.quotes',  # Quote-related tasks
        'warehouse_quote_app.app.core.tasks.rates',  # Rate-related tasks
        'warehouse_quote_app.app.core.tasks.admin',  # Admin tasks
    ]
)

# Configure Celery
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)

# Configure periodic tasks
celery_app.conf.beat_schedule = {
    "cleanup-expired-quotes": {
        "task": "warehouse_quote_app.app.core.tasks.quotes.cleanup_expired_quotes",
        "schedule": crontab(hour=0, minute=0),  # Run daily at midnight
    },
    "update-rate-cards": {
        "task": "warehouse_quote_app.app.core.tasks.rates.update_rate_cards",
        "schedule": crontab(hour="*/6"),  # Run every 6 hours
    },
    "backup-database": {
        "task": "warehouse_quote_app.app.core.tasks.admin.backup_database",
        "schedule": crontab(hour=3, minute=0),  # Run daily at 3 AM
    },
}

def init_celery(app=None) -> None:
    """Initialize Celery with FastAPI app context."""
    if app:
        class ContextTask(celery_app.Task):
            def __call__(self, *args: Any, **kwargs: Dict[str, Any]) -> Any:
                with app.app_context():
                    return self.run(*args, **kwargs)

        celery_app.Task = ContextTask

__all__ = ['celery_app', 'init_celery']
