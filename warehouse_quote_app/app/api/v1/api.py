"""API router configuration."""
from fastapi import APIRouter
from warehouse_quote_app.app.api.v1.endpoints import (
    admin,
    auth,
    chat,
    client,
    crm,
    customer,
    dashboard,
    documents,
    quotes,
    rate_cards
)
from warehouse_quote_app.app.api.v1 import ws

# Create main API router
api_router = APIRouter()

# Authentication and user management
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])
api_router.include_router(customer.router, prefix="/customer", tags=["customer"])

# Business operations
api_router.include_router(client.router, prefix="/client", tags=["client"])
api_router.include_router(quotes.router, prefix="/quotes", tags=["quotes"])
api_router.include_router(rate_cards.router, prefix="/rate-cards", tags=["rate-cards"])
api_router.include_router(crm.router, prefix="/crm", tags=["crm"])

# Dashboard
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])

# Documents
api_router.include_router(documents.router, prefix="/documents", tags=["documents"])

# Chat endpoints
api_router.include_router(chat.router, prefix="/chat", tags=["chat"])

# WebSocket endpoints
api_router.include_router(ws.router, prefix="/ws", tags=["websocket"])
