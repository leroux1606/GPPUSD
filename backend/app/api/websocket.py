"""WebSocket handler for real-time data streaming."""

from fastapi import WebSocket, WebSocketDisconnect
from typing import List
import json
import asyncio
from app.data.live_feed import stream_gbpusd_live
from app.utils.logger import logger


class ConnectionManager:
    """Manages WebSocket connections."""
    
    def __init__(self):
        """Initialize connection manager."""
        self.active_connections: List[WebSocket] = []
        self.stream_task = None
    
    async def connect(self, websocket: WebSocket):
        """Accept WebSocket connection."""
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"WebSocket connected. Total connections: {len(self.active_connections)}")
        
        # Start streaming if first connection
        if len(self.active_connections) == 1:
            self.start_streaming()
    
    def disconnect(self, websocket: WebSocket):
        """Remove WebSocket connection."""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        logger.info(f"WebSocket disconnected. Total connections: {len(self.active_connections)}")
        
        # Stop streaming if no connections
        if len(self.active_connections) == 0 and self.stream_task:
            self.stream_task.cancel()
    
    async def send_personal_message(self, message: str, websocket: WebSocket):
        """Send message to specific connection."""
        try:
            await websocket.send_text(message)
        except Exception as e:
            logger.error(f"Error sending message: {e}")
            self.disconnect(websocket)
    
    async def broadcast(self, message: dict):
        """Broadcast message to all connections."""
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Error broadcasting: {e}")
                disconnected.append(connection)
        
        # Remove disconnected clients
        for conn in disconnected:
            self.disconnect(conn)
    
    def start_streaming(self):
        """Start price streaming."""
        if self.stream_task and not self.stream_task.done():
            return
        
        async def stream_prices():
            try:
                async for price_data in stream_gbpusd_live():
                    if len(self.active_connections) > 0:
                        await self.broadcast({
                            "type": "price_update",
                            "data": price_data
                        })
                    else:
                        break
            except asyncio.CancelledError:
                logger.info("Price streaming cancelled")
            except Exception as e:
                logger.error(f"Error in price stream: {e}")
        
        self.stream_task = asyncio.create_task(stream_prices())


# Global connection manager
manager = ConnectionManager()


async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint handler."""
    await manager.connect(websocket)
    try:
        while True:
            # Keep connection alive
            data = await websocket.receive_text()
            # Echo back or handle commands
            await websocket.send_json({"type": "pong", "data": data})
    except WebSocketDisconnect:
        manager.disconnect(websocket)

