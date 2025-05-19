"""API middleware and dependencies."""
from typing import Callable, Optional, Any
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from fastapi_cache import FastAPICache
from fastapi_cache.decorator import cache
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter
import redis.asyncio as redis
from warehouse_quote_app.app.core.config import settings
from warehouse_quote_app.app.core.logging import get_logger

logger = get_logger(__name__)

# Rate limiting configuration
RATE_LIMIT_STANDARD = "100/minute"  # Standard API endpoints
RATE_LIMIT_AUTH = "5/minute"        # Authentication endpoints
RATE_LIMIT_ADMIN = "200/minute"     # Admin endpoints

# Cache configuration
CACHE_EXPIRE_TIME = 60  # seconds
CACHE_KEY_PREFIX = "aulogistics_"

async def init_redis():
    """Initialize Redis for rate limiting and caching."""
    redis_instance = redis.from_url(settings.REDIS_URL)
    await FastAPILimiter.init(redis_instance)
    FastAPICache.init(
        backend=redis_instance,
        prefix=CACHE_KEY_PREFIX,
        expire=CACHE_EXPIRE_TIME
    )

def rate_limit(limit: str = RATE_LIMIT_STANDARD) -> Callable:
    """Rate limiting decorator with configurable limits."""
    return RateLimiter(times=int(limit.split('/')[0]),
                      seconds=60 if limit.split('/')[1] == 'minute' else 1)

def cache_response(expire: int = CACHE_EXPIRE_TIME,
                  key_prefix: Optional[str] = None) -> Callable:
    """Cache decorator with configurable expiration."""
    def decorator(func: Callable) -> Callable:
        prefix = key_prefix or func.__name__
        return cache(expire=expire, namespace=f"{CACHE_KEY_PREFIX}{prefix}")(func)
    return decorator

async def handle_rate_limit_exceeded(request: Request, exc: Exception) -> Response:
    """Handle rate limit exceeded exceptions."""
    logger.warning(f"Rate limit exceeded for {request.url}")
    return JSONResponse(
        status_code=429,
        content={
            "detail": "Too many requests. Please try again later.",
            "type": "rate_limit_exceeded"
        }
    )

# Export dependencies
__all__ = [
    'init_redis',
    'rate_limit',
    'cache_response',
    'handle_rate_limit_exceeded',
    'RATE_LIMIT_STANDARD',
    'RATE_LIMIT_AUTH',
    'RATE_LIMIT_ADMIN'
]
