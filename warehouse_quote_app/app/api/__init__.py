"""
API router initialization.
"""

from fastapi import APIRouter

from .v1 import router as v1_router

# Create main API router
router = APIRouter()

# Include v1 router with prefix
router.include_router(v1_router, prefix="/v1")
