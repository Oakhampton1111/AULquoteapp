"""
API v1 router initialization.
"""

from fastapi import APIRouter

from .endpoints.admin import router as admin_router
from .endpoints.auth import router as auth_router
from .endpoints.client import router as client_router
from .endpoints.customer import router as customer_router
from .endpoints.quotes import router as quotes_router
from .endpoints.rate_cards import router as rate_cards_router
from .ws import router as ws_router

# Create main v1 router
router = APIRouter()

# Include all routers
router.include_router(auth_router)
router.include_router(admin_router)
router.include_router(client_router)
router.include_router(customer_router)
router.include_router(quotes_router)
router.include_router(rate_cards_router)
router.include_router(ws_router)
