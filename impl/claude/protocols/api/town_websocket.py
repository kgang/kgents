"""
WebSocket endpoint for Agent Town real-time communication.

Provides bidirectional streaming:
- Server → Client: Events, dialogue chunks, status updates
- Client → Server: Commands (play, pause, step, speed, perturb)

See: plans/velvety-mapping-puddle.md Phase 3
"""

from __future__ import annotations

import asyncio
import json
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
    APIRouter = None  # type: ignore[assignment, misc]
    WebSocket = None  # type: ignore[assignment, misc]
    WebSocketDisconnect = Exception  # type: ignore[assignment, misc]


# =============================================================================
# Message Types
# =============================================================================


class ServerMessageType(str, Enum):
    """Message types sent from server to client."""

    EVENT = "event"  # TownEvent
    DIALOGUE_CHUNK = "dialogue_chunk"  # Partial LLM output
    DIALOGUE_DONE = "dialogue_done"  # Complete dialogue
    STATUS = "status"  # Status update
    PHASE = "phase"  # Phase transition
    ERROR = "error"  # Error message
    CONNECTED = "connected"  # Connection established
    COMMAND_ACK = "command_ack"  # Command acknowledged


class ClientMessageType(str, Enum):
    """Message types sent from client to server."""

    PLAY = "play"
    PAUSE = "pause"
    STEP = "step"
    SPEED = "speed"  # {"type": "speed", "value": 2.0}
    PERTURB = "perturb"  # {"type": "perturb", "operation": "trade", "participants": [...]}
    PING = "ping"


# =============================================================================
# Town WebSocket Session
# =============================================================================


@dataclass
class TownWebSocketSession:
    """
    Manages a WebSocket connection to a town simulation.

    Handles:
    - Event streaming from TownFlux
    - Command processing from client
    - Playback state management
    """

    town_id: str
    websocket: Any  # WebSocket
    is_playing: bool = False
    playback_speed: float = 1.0
    current_tick: int = 0
    _event_queue: asyncio.Queue[dict[str, Any]] = field(
        default_factory=lambda: asyncio.Queue(maxsize=100)
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
            await self.websocket.send_json(message)
        except Exception as e:
            logger.warning(f"Failed to send WebSocket message: {e}")

    async def handle_command(self, message: dict[str, Any]) -> None:
        """Process a command from the client."""
        cmd_type = message.get("type", "").lower()

        if cmd_type == "play":
            self.is_playing = True
            await self.send_message(
                ServerMessageType.COMMAND_ACK.value,
                {"command": "play", "status": "playing"},
            )

        elif cmd_type == "pause":
            self.is_playing = False
            await self.send_message(
                ServerMessageType.COMMAND_ACK.value,
                {"command": "pause", "status": "paused"},
            )

        elif cmd_type == "step":
            # Queue a single step event
            await self._event_queue.put({"action": "step"})
            await self.send_message(
                ServerMessageType.COMMAND_ACK.value,
                {"command": "step", "status": "stepping"},
            )

        elif cmd_type == "speed":
            speed = message.get("value", 1.0)
            self.playback_speed = max(0.25, min(4.0, float(speed)))
            await self.send_message(
                ServerMessageType.COMMAND_ACK.value,
                {"command": "speed", "value": self.playback_speed},
            )

        elif cmd_type == "perturb":
            operation = message.get("operation", "greet")
            participants = message.get("participants")
            await self._event_queue.put(
                {
                    "action": "perturb",
                    "operation": operation,
                    "participants": participants,
                }
            )
            await self.send_message(
                ServerMessageType.COMMAND_ACK.value,
                {"command": "perturb", "operation": operation},
            )

        elif cmd_type == "ping":
            await self.send_message(
                ServerMessageType.COMMAND_ACK.value,
                {"command": "pong", "tick": self.current_tick},
            )

        else:
            await self.send_message(
                ServerMessageType.ERROR.value,
                {"error": f"Unknown command: {cmd_type}"},
            )

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


# Global registry of active WebSocket sessions
_active_sessions: dict[str, list[TownWebSocketSession]] = {}


def register_session(town_id: str, session: TownWebSocketSession) -> None:
    """Register a WebSocket session for a town."""
    if town_id not in _active_sessions:
        _active_sessions[town_id] = []
    _active_sessions[town_id].append(session)


def unregister_session(town_id: str, session: TownWebSocketSession) -> None:
    """Unregister a WebSocket session."""
    if town_id in _active_sessions:
        _active_sessions[town_id] = [s for s in _active_sessions[town_id] if s != session]
        if not _active_sessions[town_id]:
            del _active_sessions[town_id]


async def broadcast_to_town(town_id: str, msg_type: str, data: dict[str, Any]) -> int:
    """
    Broadcast a message to all sessions for a town.

    Returns number of sessions messaged.
    """
    sessions = _active_sessions.get(town_id, [])
    count = 0
    for session in sessions:
        try:
            await session.send_message(msg_type, data)
            count += 1
        except Exception:
            pass
    return count


# =============================================================================
# Router Factory
# =============================================================================


def create_town_websocket_router() -> "APIRouter | None":
    """
    Create WebSocket router for Agent Town.

    Returns None if FastAPI/WebSocket not available.
    """
    if not HAS_WEBSOCKET:
        logger.warning("FastAPI WebSocket not available")
        return None

    router = APIRouter(tags=["town-websocket"])

    @router.websocket("/ws/town/{town_id}")
    async def town_websocket_endpoint(websocket: WebSocket, town_id: str) -> None:
        """
        WebSocket endpoint for real-time town communication.

        Bidirectional protocol:
        - Server sends: event, dialogue_chunk, status, phase, error
        - Client sends: play, pause, step, speed, perturb, ping
        """
        await websocket.accept()

        # Create session
        session = TownWebSocketSession(town_id=town_id, websocket=websocket)
        register_session(town_id, session)

        # Send connected message
        await session.send_message(
            ServerMessageType.CONNECTED.value,
            {"town_id": town_id, "status": "connected"},
        )

        try:
            # Start simulation runner task (fire and forget, cleaned up on disconnect)
            asyncio.create_task(_run_simulation(session))

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
                    # Send ping to keep connection alive
                    await session.send_message(
                        ServerMessageType.STATUS.value,
                        {"tick": session.current_tick, "playing": session.is_playing},
                    )
                except WebSocketDisconnect:
                    break

        except Exception as e:
            logger.error(f"WebSocket error for town {town_id}: {e}")
            await session.send_message(
                ServerMessageType.ERROR.value,
                {"error": str(e)},
            )

        finally:
            session.stop()
            unregister_session(town_id, session)
            try:
                await websocket.close()
            except Exception:
                pass

    return router


# =============================================================================
# Simulation Runner
# =============================================================================


async def _run_simulation(session: TownWebSocketSession) -> None:
    """
    Run the town simulation and stream events to WebSocket.

    Respects play/pause state and processes queued commands.
    """
    from agents.town.event_bus import EventBus
    from agents.town.flux import TownFlux
    from agents.town.phase_governor import PhaseGovernor, PhaseTimingConfig

    # Try to get existing flux from AUP router
    try:
        from . import aup

        # Access the module-level dict (created inside create_aup_router)
        flux_registry = getattr(aup, "_town_fluxes", None)
        if flux_registry is None:
            # Try to get from the router closure (it's created inside the function)
            # Fall back to creating a new flux
            from agents.town.environment import create_mpp_environment
            from agents.town.flux import TownFlux

            env = create_mpp_environment()
            flux = TownFlux(env, seed=42)
        else:
            flux = flux_registry.get(session.town_id)
            if not flux:
                await session.send_message(
                    ServerMessageType.ERROR.value,
                    {
                        "error": f"Town '{session.town_id}' not initialized",
                        "suggestion": "Call POST /api/v1/town/{town_id}/init first",
                    },
                )
                return
    except ImportError as e:
        await session.send_message(
            ServerMessageType.ERROR.value,
            {"error": f"Town flux module not available: {e}"},
        )
        return

    # Create governor for controlled playback
    event_bus: EventBus[Any] = EventBus()
    config = PhaseTimingConfig(
        phase_duration_ms=5000,
        events_per_phase=5,
        playback_speed=session.playback_speed,
        min_event_delay_ms=200,
        max_event_delay_ms=2000,
    )
    governor = PhaseGovernor(flux=flux, config=config, event_bus=event_bus)

    current_phase = None

    try:
        while not session.stopped:
            # Check for queued commands
            try:
                cmd = session._event_queue.get_nowait()
                if cmd.get("action") == "step":
                    # Execute single step
                    async for event in flux.step():
                        await _send_event(session, event, session.current_tick)
                        session.current_tick += 1
                elif cmd.get("action") == "perturb":
                    # Execute perturbation
                    perturb_event = await flux.perturb_async(
                        cmd.get("operation", "greet"),
                        cmd.get("participants"),
                    )
                    if perturb_event:
                        await _send_event(session, perturb_event, session.current_tick)
                        session.current_tick += 1
            except asyncio.QueueEmpty:
                pass

            # If playing, run simulation
            if session.is_playing:
                # Update governor speed
                governor.config.playback_speed = session.playback_speed

                # Run one event
                try:
                    async for event in governor.run(num_phases=1):
                        session.current_tick += 1

                        # Send phase transition if changed
                        if event.phase.name != current_phase:
                            current_phase = event.phase.name
                            await session.send_message(
                                ServerMessageType.PHASE.value,
                                {"tick": session.current_tick, "phase": current_phase},
                            )

                        # Send event
                        await _send_event(session, event, session.current_tick)
                except Exception as e:
                    logger.warning(f"Simulation error: {e}")
                    await session.send_message(
                        ServerMessageType.ERROR.value,
                        {"error": str(e)},
                    )

            # Brief pause to prevent busy loop
            await asyncio.sleep(0.1)

    finally:
        event_bus.close()


async def _send_event(session: TownWebSocketSession, event: Any, tick: int) -> None:
    """Send a TownEvent to the WebSocket client."""
    event_data: dict[str, Any] = {
        "tick": tick,
        "phase": event.phase.name,
        "operation": event.operation,
        "participants": event.participants,
        "success": event.success,
        "message": event.message,
        "tokens_used": event.tokens_used,
        "timestamp": event.timestamp.isoformat(),
    }

    # Include dialogue if present
    if event.dialogue:
        event_data["dialogue"] = {
            "text": event.dialogue,
            "tokens": event.dialogue_tokens,
            "model": event.dialogue_model,
            "was_template": event.dialogue_was_template,
            "grounded_memories": event.dialogue_grounded,
        }

    await session.send_message(ServerMessageType.EVENT.value, event_data)


# =============================================================================
# Exports
# =============================================================================


__all__ = [
    "ClientMessageType",
    "ServerMessageType",
    "TownWebSocketSession",
    "broadcast_to_town",
    "create_town_websocket_router",
    "register_session",
    "unregister_session",
]
