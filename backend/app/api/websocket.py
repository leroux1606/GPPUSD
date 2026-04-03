"""WebSocket handler — real-time price streaming, signals, and notifications."""

from fastapi import WebSocket, WebSocketDisconnect
from typing import List
import json
import asyncio
from app.data.live_feed import stream_gbpusd_live
from app.utils.logger import logger


class ConnectionManager:
    """Manages WebSocket connections and coordinates streaming."""

    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.price_task: asyncio.Task = None

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"WS connected ({len(self.active_connections)} total)")
        if len(self.active_connections) == 1:
            self._start_price_stream()
            self._start_signal_engine()

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        logger.info(f"WS disconnected ({len(self.active_connections)} total)")
        if not self.active_connections:
            if self.price_task:
                self.price_task.cancel()
            from app.services.signal_engine import signal_engine
            if signal_engine:
                signal_engine.stop()

    async def broadcast(self, message: dict):
        """Broadcast a message to all connected clients."""
        dead = []
        for conn in self.active_connections:
            try:
                await conn.send_json(message)
            except Exception:
                dead.append(conn)
        for c in dead:
            self.disconnect(c)

    async def handle_message(self, websocket: WebSocket, raw: str):
        """Handle incoming client messages (commands)."""
        try:
            msg = json.loads(raw)
            cmd = msg.get("cmd")

            if cmd == "ping":
                await websocket.send_json({"type": "pong"})

            elif cmd == "update_account":
                from app.services.signal_engine import signal_engine
                if signal_engine:
                    signal_engine.update_account(
                        balance=msg.get("balance", 10000),
                        equity=msg.get("equity", 10000),
                        positions=msg.get("positions", []),
                    )

            elif cmd == "get_ai_commentary":
                from app.services.ai_advisor import get_market_commentary
                context = msg.get("context", {})
                commentary = await get_market_commentary(context)
                await websocket.send_json({"type": "ai_commentary", "data": {"text": commentary}})

        except json.JSONDecodeError:
            pass
        except Exception as e:
            logger.error(f"WS message handling error: {e}")

    def _start_price_stream(self):
        if self.price_task and not self.price_task.done():
            return

        async def _stream():
            try:
                async for price_data in stream_gbpusd_live():
                    if self.active_connections:
                        await self.broadcast({"type": "price_update", "data": price_data})
                    else:
                        break
            except asyncio.CancelledError:
                pass
            except Exception as e:
                logger.error(f"Price stream error: {e}")

        self.price_task = asyncio.create_task(_stream())

    def _start_signal_engine(self):
        from app.services import signal_engine as se_module
        if se_module.signal_engine is None:
            from app.services.signal_engine import SignalEngine
            se_module.signal_engine = SignalEngine(broadcast_fn=self.broadcast)
        se_module.signal_engine.start()


# Global connection manager
manager = ConnectionManager()


async def websocket_endpoint(websocket: WebSocket):
    """Main WebSocket endpoint."""
    await manager.connect(websocket)
    try:
        while True:
            raw = await websocket.receive_text()
            await manager.handle_message(websocket, raw)
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WS endpoint error: {e}")
        manager.disconnect(websocket)
