"""Authentication middleware."""

import logging
from typing import Callable, Optional
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from warehouse_quote_app.app.core.auth.jwt import decode_access_token
from warehouse_quote_app.app.core.exceptions import AuthenticationError

logger = logging.getLogger(__name__)

class AuthenticationMiddleware(BaseHTTPMiddleware):
    """Middleware for handling authentication."""
    
    EXEMPT_PATHS = {
        "/api/v1/auth/login",
        "/api/v1/auth/register",
        "/api/v1/docs",
        "/api/v1/openapi.json",
        "/ws"
    }
    
    def is_path_exempt(self, path: str) -> bool:
        """Check if path is exempt from authentication."""
        if path.startswith("/assets/"):
            return True
        return path in self.EXEMPT_PATHS
    
    async def get_token_from_request(self, request: Request) -> Optional[str]:
        """Extract token from request headers."""
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return None
        return auth_header.split(" ")[1]
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process the request and handle authentication."""
        # Skip authentication for exempt paths
        if self.is_path_exempt(request.url.path):
            return await call_next(request)
        
        # Get token
        token = await self.get_token_from_request(request)
        if not token:
            logger.warning("No authentication token provided")
            raise AuthenticationError("No authentication token provided")
        
        try:
            # Validate token
            payload = decode_access_token(token)
            
            # Add user info to request state
            request.state.user = payload
            
            return await call_next(request)
            
        except Exception as e:
            logger.warning(f"Authentication failed: {str(e)}")
            raise AuthenticationError("Invalid authentication token")
