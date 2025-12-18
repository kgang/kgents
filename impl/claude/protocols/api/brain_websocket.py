"""
WebSocket endpoint for Brain real-time communication.

Provides server-to-client streaming for:
- Crystal formed events (new captures)
- Memory surfaced events (ghost activations)
- Vault imported events (bulk imports)

Subscribes to synergy bus CRYSTAL_FORMED events and broadcasts to connected clients.

Phase 1 of Crown Jewels completion: Brain WebSocket + Synergy integration.
"""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from fastapi import APIRouter

logger = logging.getLogger(__name__)

# Graceful FastAPI/WebSocket import
try:
    from fastapi import APIRouter, WebSocket, WebSocketDisconnect
    from starlette.websockets import WebSocketState

    HAS_WEBSOCKET = True
except ImportError:
    HAS_WEBSOCKET = False
    APIRouter = None  # type: ignore
    WebSocket = None  # type: ignore
    WebSocketDisconnect = Exception  # type: ignore
    WebSocketState = None  # type: ignore


# =============================================================================
# Message Types
# =============================================================================


class BrainServerMessageType(str, Enum):
    """Message types sent from server to client."""

    CRYSTAL_FORMED = "crystal_formed"  # New crystal captured
    MEMORY_SURFACED = "memory_surfaced"  # Ghost activation
    VAULT_IMPORTED = "vault_imported"  # Bulk import complete
    STATUS = "status"  # Status update
    ERROR = "error"  # Error message
    CONNECTED = "connected"  # Connection established
    PONG = "pong"  # Keepalive response


class BrainClientMessageType(str, Enum):
    """Message types sent from client to server."""

    PING = "ping"  # Keepalive
    SUBSCRIBE = "subscribe"  # Subscribe to event types
    UNSUBSCRIBE = "unsubscribe"  # Unsubscribe from event types


# =============================================================================
# Brain WebSocket Session
# =============================================================================


@dataclass
class BrainWebSocketSession:
    """
    Manages a WebSocket connection for Brain updates.

    Handles:
    - Event streaming from synergy bus
    - Subscription filtering
    - Keepalive
    """

    session_id: str
    websocket: Any  # WebSocket
    subscribed_events: set[str] = field(
        default_factory=lambda: {"crystal_formed", "memory_surfaced", "vault_imported"}
    )
    _stop_event: asyncio.Event = field(default_factory=asyncio.Event)

    async def send_message(self, msg_type: str, data: dict[str, Any]) -> None:
        """Send a message to the client."""
        message = {
            "type": msg_type,
            "data": data,
            "timestamp": datetime.now().isoformat(),
        }
        try:
            if self.websocket.client_state == WebSocketState.CONNECTED:
                await self.websocket.send_json(message)
        except Exception as e:
            logger.warning(f"Failed to send Brain WebSocket message: {e}")

    async def handle_command(self, message: dict[str, Any]) -> None:
        """Process a command from the client."""
        cmd_type = message.get("type", "").lower()

        if cmd_type == "ping":
            await self.send_message(
                BrainServerMessageType.PONG.value,
                {"timestamp": datetime.now().isoformat()},
            )

        elif cmd_type == "subscribe":
            events = message.get("events", [])
            self.subscribed_events.update(events)
            await self.send_message(
                BrainServerMessageType.STATUS.value,
                {"subscribed": list(self.subscribed_events)},
            )

        elif cmd_type == "unsubscribe":
            events = message.get("events", [])
            self.subscribed_events.difference_update(events)
            await self.send_message(
                BrainServerMessageType.STATUS.value,
                {"subscribed": list(self.subscribed_events)},
            )

        else:
            await self.send_message(
                BrainServerMessageType.ERROR.value,
                {"error": f"Unknown command: {cmd_type}"},
            )

    def should_receive(self, event_type: str) -> bool:
        """Check if session should receive this event type."""
        return event_type in self.subscribed_events

    def stop(self) -> None:
        """Signal the session to stop."""
        self._stop_event.set()

    @property
    def stopped(self) -> bool:
        """Check if session is stopped."""
        return self._stop_event.is_set()


# =============================================================================
# Active Sessions Registry
# =============================================================================


# Global registry of active Brain WebSocket sessions
_active_sessions: list[BrainWebSocketSession] = []
_sessions_lock = asyncio.Lock()


async def register_session(session: BrainWebSocketSession) -> None:
    """Register a WebSocket session."""
    async with _sessions_lock:
        _active_sessions.append(session)
    logger.debug(f"Brain WebSocket session registered: {session.session_id}")


async def unregister_session(session: BrainWebSocketSession) -> None:
    """Unregister a WebSocket session."""
    async with _sessions_lock:
        if session in _active_sessions:
            _active_sessions.remove(session)
    logger.debug(f"Brain WebSocket session unregistered: {session.session_id}")


async def broadcast_brain_event(event_type: str, data: dict[str, Any]) -> int:
    """
    Broadcast a Brain event to all subscribed sessions.

    Returns number of sessions messaged.
    """
    async with _sessions_lock:
        sessions = list(_active_sessions)

    count = 0
    for session in sessions:
        if session.should_receive(event_type):
            try:
                await session.send_message(event_type, data)
                count += 1
            except Exception:
                pass
    return count


# =============================================================================
# Synergy Bus Integration
# =============================================================================


_synergy_unsubscribe: Any = None


def _setup_synergy_subscription() -> None:
    """Subscribe to synergy bus events for broadcasting."""
    global _synergy_unsubscribe

    try:
        from protocols.synergy.bus import get_synergy_bus
        from protocols.synergy.events import (
            SynergyEvent,
            SynergyEventType,
            SynergyResult,
        )

        bus = get_synergy_bus()

        def on_synergy_result(event: SynergyEvent, result: SynergyResult) -> None:
            """Handle synergy event for broadcasting."""
            # Map synergy events to Brain WebSocket messages
            event_mapping = {
                SynergyEventType.CRYSTAL_FORMED: BrainServerMessageType.CRYSTAL_FORMED,
                SynergyEventType.MEMORY_SURFACED: BrainServerMessageType.MEMORY_SURFACED,
                SynergyEventType.VAULT_IMPORTED: BrainServerMessageType.VAULT_IMPORTED,
            }

            msg_type = event_mapping.get(event.event_type)
            if msg_type:
                # Schedule broadcast (non-blocking)
                try:
                    loop = asyncio.get_event_loop()
                    loop.create_task(
                        broadcast_brain_event(
                            msg_type.value,
                            {
                                "source_id": event.source_id,
                                "payload": event.payload,
                                "correlation_id": event.correlation_id,
                            },
                        )
                    )
                except RuntimeError:
                    # No event loop - skip broadcast
                    pass

        _synergy_unsubscribe = bus.subscribe_results(on_synergy_result)
        logger.info("Brain WebSocket subscribed to synergy bus")

    except ImportError:
        logger.warning("Synergy bus not available for Brain WebSocket")


# =============================================================================
# Router Factory
# =============================================================================


def create_brain_websocket_router() -> "APIRouter | None":
    """
    Create WebSocket router for Brain.

    Returns None if FastAPI/WebSocket not available.
    """
    if not HAS_WEBSOCKET:
        logger.warning("FastAPI WebSocket not available for Brain")
        return None

    # Setup synergy subscription on router creation
    _setup_synergy_subscription()

    router = APIRouter(tags=["brain-websocket"])

    @router.websocket("/ws/brain")
    async def brain_websocket_endpoint(websocket: WebSocket) -> None:
        """
        WebSocket endpoint for real-time Brain updates.

        Server sends: crystal_formed, memory_surfaced, vault_imported, status, error
        Client sends: ping, subscribe, unsubscribe
        """
        import uuid

        await websocket.accept()

        # Create session
        session = BrainWebSocketSession(
            session_id=str(uuid.uuid4()),
            websocket=websocket,
        )
        await register_session(session)

        # Send connected message
        await session.send_message(
            BrainServerMessageType.CONNECTED.value,
            {
                "session_id": session.session_id,
                "subscribed": list(session.subscribed_events),
            },
        )

        try:
            # Process incoming messages
            while not session.stopped:
                try:
                    # Wait for message with timeout
                    data = await asyncio.wait_for(
                        websocket.receive_json(),
                        timeout=30.0,  # 30 second timeout
                    )
                    await session.handle_command(data)
                except asyncio.TimeoutError:
                    # Send keepalive
                    await session.send_message(
                        BrainServerMessageType.STATUS.value,
                        {"keepalive": True},
                    )
                except WebSocketDisconnect:
                    break

        except Exception as e:
            logger.error(f"Brain WebSocket error: {e}")
            await session.send_message(
                BrainServerMessageType.ERROR.value,
                {"error": str(e)},
            )

        finally:
            session.stop()
            await unregister_session(session)
            try:
                await websocket.close()
            except Exception:
                pass

    return router


# =============================================================================
# Exports
# =============================================================================


__all__ = [
    "BrainClientMessageType",
    "BrainServerMessageType",
    "BrainWebSocketSession",
    "broadcast_brain_event",
    "create_brain_websocket_router",
    "register_session",
    "unregister_session",
]
