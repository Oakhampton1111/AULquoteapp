"""
Background task and Celery worker configuration.
"""

from .celery import celery_app, init_celery

__all__ = [
    'celery_app',
    'init_celery'
]
