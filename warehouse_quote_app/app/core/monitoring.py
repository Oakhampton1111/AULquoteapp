"""
Monitoring and observability setup for the application.
"""

import logging
from fastapi import FastAPI

from warehouse_quote_app.app.core.config import settings

def setup_monitoring(app: FastAPI) -> None:
    """
    Set up monitoring and observability for the application.
    
    This includes:
    - Configuring logging
    - Setting up middleware for request/response logging
    - Initializing metrics collection
    - Setting up tracing (if enabled)
    """
    logger = logging.getLogger(__name__)
    logger.info(f"Setting up monitoring for {settings.APP_NAME}")
    
    # Add middleware for request/response logging
    @app.middleware("http")
    async def log_requests(request, call_next):
        # Skip logging for health check endpoints
        if request.url.path == "/health" or request.url.path == "/ping":
            return await call_next(request)
            
        logger.debug(f"Request: {request.method} {request.url.path}")
        response = await call_next(request)
        logger.debug(f"Response: {request.method} {request.url.path} - Status: {response.status_code}")
        return response
    
    logger.info("Monitoring setup complete")

def log_event(
    event_type: str,
    user_id: int = None,
    resource_type: str = None,
    resource_id: str = None,
    details: dict = None
) -> None:
    """
    Log an application event.
    
    Args:
        event_type: Type of event (e.g., "user_login", "quote_created")
        user_id: ID of the user who triggered the event
        resource_type: Type of resource affected (e.g., "quote", "rate_card")
        resource_id: ID of the resource affected
        details: Additional details about the event
    """
    logger = logging.getLogger("app.events")
    
    log_data = {
        "event_type": event_type,
        "user_id": user_id,
        "resource_type": resource_type,
        "resource_id": resource_id,
        "details": details or {}
    }
    
    logger.info(f"Event: {event_type}", extra=log_data)
