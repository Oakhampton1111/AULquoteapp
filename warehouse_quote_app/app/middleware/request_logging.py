"""Request logging middleware."""

import logging
import time
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for logging request details."""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process the request and log details."""
        start_time = time.time()
        
        # Extract request details
        method = request.method
        url = str(request.url)
        client_host = request.client.host if request.client else "unknown"
        
        # Log request start
        logger.info(f"Request started: {method} {url} from {client_host}")
        
        try:
            # Process request
            response = await call_next(request)
            
            # Calculate duration
            duration = time.time() - start_time
            
            # Log request completion
            logger.info(
                f"Request completed: {method} {url} "
                f"- Status: {response.status_code} "
                f"- Duration: {duration:.2f}s"
            )
            
            return response
            
        except Exception as e:
            # Log error
            logger.error(
                f"Request failed: {method} {url} "
                f"- Error: {str(e)}"
            )
            raise
