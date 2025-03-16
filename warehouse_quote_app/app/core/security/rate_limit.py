"""
Rate limiting functionality.
"""

from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
import time
from typing import Dict, Tuple, Optional
from collections import defaultdict

from warehouse_quote_app.app.core.config import settings

# Store for rate limiting data
# key: IP address, value: (request_count, window_start)
rate_limit_store: Dict[str, Tuple[int, float]] = defaultdict(lambda: (0, time.time()))

def get_client_ip(request: Request) -> str:
    """Get client IP address from request."""
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0]
    return request.client.host if request.client else "unknown"  # type: ignore

async def rate_limit(
    request: Request,
    requests: Optional[int] = None,
    period: Optional[int] = None
) -> None:
    """Rate limit middleware."""
    if not settings.RATE_LIMIT_ENABLED:
        return

    ip = get_client_ip(request)
    now = time.time()
    
    # Get rate limit settings
    max_requests = requests or settings.RATE_LIMIT_REQUESTS
    window_size = period or settings.RATE_LIMIT_PERIOD
    
    # Get current state
    count, window_start = rate_limit_store[ip]
    
    # Reset if window has expired
    if now - window_start >= window_size:
        count = 0
        window_start = now
    
    # Check limit
    if count >= max_requests:
        reset_time = window_start + window_size - now
        raise HTTPException(
            status_code=429,
            detail={
                "error": "Too many requests",
                "reset_in_seconds": int(reset_time)
            }
        )
    
    # Update store
    rate_limit_store[ip] = (count + 1, window_start)

__all__ = ['rate_limit', 'get_client_ip']
