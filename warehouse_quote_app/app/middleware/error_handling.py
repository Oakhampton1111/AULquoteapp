"""Error handling middleware."""

import logging
from typing import Callable
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from sqlalchemy.exc import SQLAlchemyError
from jwt.exceptions import PyJWTError

from app.core.exceptions import (
    AppError,
    AuthenticationError,
    AuthorizationError,
    ValidationError,
    NotFoundError
)

logger = logging.getLogger(__name__)

class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    """Middleware for handling application errors."""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process the request and handle any errors."""
        try:
            return await call_next(request)
            
        except AuthenticationError as e:
            logger.warning(f"Authentication error: {str(e)}")
            return JSONResponse(
                status_code=401,
                content={"detail": str(e)}
            )
            
        except AuthorizationError as e:
            logger.warning(f"Authorization error: {str(e)}")
            return JSONResponse(
                status_code=403,
                content={"detail": str(e)}
            )
            
        except ValidationError as e:
            logger.warning(f"Validation error: {str(e)}")
            return JSONResponse(
                status_code=422,
                content={"detail": str(e)}
            )
            
        except NotFoundError as e:
            logger.warning(f"Not found error: {str(e)}")
            return JSONResponse(
                status_code=404,
                content={"detail": str(e)}
            )
            
        except SQLAlchemyError as e:
            logger.error(f"Database error: {str(e)}")
            return JSONResponse(
                status_code=500,
                content={"detail": "Internal database error"}
            )
            
        except PyJWTError as e:
            logger.warning(f"JWT error: {str(e)}")
            return JSONResponse(
                status_code=401,
                content={"detail": "Invalid authentication token"}
            )
            
        except AppError as e:
            logger.error(f"Application error: {str(e)}")
            return JSONResponse(
                status_code=e.status_code,
                content={"detail": str(e)}
            )
            
        except Exception as e:
            logger.exception("Unexpected error")
            return JSONResponse(
                status_code=500,
                content={"detail": "Internal server error"}
            )
