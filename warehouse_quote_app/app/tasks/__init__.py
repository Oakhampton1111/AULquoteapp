"""
Task definitions and celery configuration.
"""

from warehouse_quote_app.app.core.tasks.celery import celery_app

__all__ = ['celery_app']
