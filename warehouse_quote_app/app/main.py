"""
AU Logistics Warehouse Quote System - Main Application

This is the main entry point for the FastAPI application that handles warehouse quotes.
The system provides functionality for both administrators and customers to manage
warehouse quotes, rate cards, and customer information.

Key Components:
- Authentication & Authorization
- Admin Dashboard
- Customer Portal
- Quote Management
- Rate Card System
- Real-time Features:
  - WebSocket Communication
  - Live Updates
  - Chat System
- AI-Powered Features:
  - FLAN-T5 Language Model
  - RAG (Retrieval Augmented Generation)
  - Intelligent Rate Calculation
  - Customer Service Assistance
"""

import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from warehouse_quote_app.app.core.config import settings
from warehouse_quote_app.app.api.v1.api import api_router
from warehouse_quote_app.app.services.communication.realtime import RealtimeService
from warehouse_quote_app.app.database.db import init_db, close_db

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan."""
    try:
        # Initialize monitoring
        from warehouse_quote_app.app.core.monitoring import setup_monitoring
        setup_monitoring(app)
        
        # Initialize database
        await init_db()  
        logger.info("Database initialized successfully")
        
        # Initialize real-time service
        app.state.realtime_service = RealtimeService()
        logger.info("Real-time service initialized")
        
        yield
    finally:
        # Cleanup
        await close_db()  
        logger.info("Database connections closed")

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    description=__doc__,
    version=settings.APP_VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan
)

# Set up CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add custom middleware
from warehouse_quote_app.app.middleware import (
    RequestLoggingMiddleware,
    ErrorHandlingMiddleware,
    AuthenticationMiddleware
)

app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(ErrorHandlingMiddleware)
app.add_middleware(AuthenticationMiddleware)

# API routes
app.include_router(api_router, prefix=settings.API_V1_STR)

# Serve static files for React app
frontend_path = Path(__file__).parent.parent / "frontend" / "dist"
if frontend_path.exists():
    app.mount("/assets", StaticFiles(directory=str(frontend_path / "assets")), name="static")

    @app.get("/{full_path:path}")
    async def serve_react_app(full_path: str):
        """Serve React app for any non-API route."""
        if full_path.startswith("api/"):
            return {"detail": "Not Found"}
        return FileResponse(str(frontend_path / "index.html"))

# WebSocket connection handler
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """Handle WebSocket connections."""
    await app.state.realtime_service.handle_connection(websocket)
