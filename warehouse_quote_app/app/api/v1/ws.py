"""
WebSocket routes for real-time communication.
"""

from fastapi import APIRouter, WebSocket, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from warehouse_quote_app.app.database import get_db
from warehouse_quote_app.app.core.auth import get_current_user
from warehouse_quote_app.app.models.user import User
from warehouse_quote_app.app.services.communication.realtime import RealtimeService

router = APIRouter(prefix="/ws", tags=["websocket"])

@router.websocket("/")
async def websocket_endpoint(
    websocket: WebSocket,
    token: str,
    db: AsyncSession = Depends(get_db)
):
    """WebSocket endpoint for real-time communication."""
    try:
        # Get user from token
        user = await get_current_user(token, db)
        
        # Initialize real-time service
        realtime_service = RealtimeService()
        
        # Connect the user
        await realtime_service.connect(websocket, user.id)
        
        try:
            while True:
                # Wait for messages from the client
                data = await websocket.receive_text()
                # Process the message (implement as needed)
                # For now, just echo back
                await websocket.send_text(f"Message received: {data}")
        except Exception as e:
            await realtime_service.handle_connection_error(websocket, user.id, e)
        
    except HTTPException:
        await websocket.close(code=1008)  # Policy Violation
    except Exception:
        await websocket.close(code=1011)  # Internal Error
