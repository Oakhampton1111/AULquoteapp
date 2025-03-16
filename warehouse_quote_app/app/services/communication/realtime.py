"""
Realtime service for WebSocket communication.
"""

from typing import Dict, Any, List, Optional
from fastapi import WebSocket
import json

from warehouse_quote_app.app.core.monitoring import log_event
from warehouse_quote_app.app.schemas.base import WebSocketMessage

class RealtimeService:
    """Service for managing realtime WebSocket connections."""

    def __init__(self):
        """Initialize realtime service."""
        self.active_connections: Dict[int, List[WebSocket]] = {}
        self.user_channels: Dict[int, List[str]] = {}

    async def connect(
        self,
        websocket: WebSocket,
        user_id: int,
        channels: Optional[List[str]] = None
    ) -> None:
        """Connect a user to WebSocket."""
        await websocket.accept()
        
        if user_id not in self.active_connections:
            self.active_connections[user_id] = []
        self.active_connections[user_id].append(websocket)
        
        if channels:
            self.user_channels[user_id] = channels
        
        log_event(
            event_type="websocket_connected",
            user_id=user_id,
            resource_type="websocket",
            resource_id=None,
            details={"channels": channels}
        )

    async def disconnect(
        self,
        websocket: WebSocket,
        user_id: int
    ) -> None:
        """Disconnect a user from WebSocket."""
        if user_id in self.active_connections:
            self.active_connections[user_id].remove(websocket)
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]
                if user_id in self.user_channels:
                    del self.user_channels[user_id]
        
        log_event(
            event_type="websocket_disconnected",
            user_id=user_id,
            resource_type="websocket",
            resource_id=None,
            details={}
        )

    async def broadcast_to_users(
        self,
        users: List[int],
        message: WebSocketMessage
    ) -> None:
        """Broadcast message to specific users."""
        for user_id in users:
            if user_id in self.active_connections:
                for connection in self.active_connections[user_id]:
                    try:
                        await connection.send_text(message.model_dump_json())
                    except Exception as e:
                        await self.handle_connection_error(connection, user_id, e)

    async def broadcast_to_channel(
        self,
        channel: str,
        message: WebSocketMessage
    ) -> None:
        """Broadcast message to all users in a channel."""
        for user_id, channels in self.user_channels.items():
            if channel in channels:
                await self.broadcast_to_users([user_id], message)

    async def handle_connection_error(
        self,
        websocket: WebSocket,
        user_id: int,
        error: Exception
    ) -> None:
        """Handle WebSocket connection errors."""
        log_event(
            event_type="websocket_error",
            user_id=user_id,
            resource_type="websocket",
            resource_id=None,
            details={"error": str(error)}
        )
        await self.disconnect(websocket, user_id)

    async def handle_connection(self, websocket: WebSocket) -> None:
        """Handle incoming WebSocket connection without authentication.
        
        This is used for anonymous connections or connections that will
        authenticate after the initial connection is established.
        """
        await websocket.accept()
        
        try:
            while True:
                # Wait for messages from the client
                data = await websocket.receive_text()
                message_data = json.loads(data)
                
                # Check if this is an authentication message
                if message_data.get("type") == "auth":
                    # Authentication logic would go here
                    user_id = message_data.get("user_id")
                    if user_id:
                        # Register the connection with a user ID
                        if isinstance(user_id, str):
                            user_id = int(user_id)
                        await self.connect(websocket, user_id)
                        await websocket.send_text(json.dumps({"type": "auth_success"}))
                    else:
                        await websocket.send_text(json.dumps({"type": "auth_error", "message": "Invalid authentication"}))
                else:
                    # Echo back for now
                    await websocket.send_text(json.dumps({"type": "echo", "data": message_data}))
        except Exception as e:
            # For anonymous connections, just log the error
            log_event(
                event_type="websocket_error",
                user_id=None,
                resource_type="websocket",
                resource_id=None,
                details={"error": str(e)}
            )
            # Close the connection
            if not websocket.client_state.DISCONNECTED:
                await websocket.close(code=1011)  # Internal Error
