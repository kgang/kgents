"""
HolographicBuffer: The Mirror Protocol implementation.

The Mirror Protocol separates observation from interaction:
- Agent emits events ONCE to the buffer
- Buffer broadcasts to N clients
- Slow clients don't slow the agent

This is the key to respecting AGENTESE: "To Observe is to Disturb."
50 browsers observing should NOT cost the agent 50x entropy.

The Mechanism:
1. Agent calls reflect(event) - fire and forget
2. Buffer stores in history (for late joiners)
3. Buffer broadcasts to all active mirrors (non-blocking)
4. Disconnected mirrors are cleaned up automatically
"""

from __future__ import annotations

import asyncio
import json
import logging
from collections import deque
from dataclasses import dataclass, field
from typing import Any, Protocol, TypeVar

logger = logging.getLogger(__name__)

T = TypeVar("T")


class WebSocketLike(Protocol):
    """Protocol for WebSocket-like objects."""

    async def send_text(self, data: str) -> None:
        """Send text data."""
        ...

    async def accept(self) -> None:
        """Accept the connection."""
        ...


@dataclass
class HolographicBuffer:
    """
    The Mirror.

    Decouples the Agent's metabolism from the Observer's curiosity.

    The agent emits events ONCE to the buffer.
    The buffer broadcasts to N clients.
    Slow clients don't slow the agent.

    Design Principles:
    - reflect() is fire-and-forget (agent never waits for observers)
    - Broadcast failures don't propagate
    - Late joiners receive history (The Ghost)
    - Disconnected observers are automatically cleaned

    Usage:
        buffer = HolographicBuffer()

        # Agent side (in FluxAgent)
        await buffer.reflect({"type": "result", "data": "..."})

        # Observer side (WebSocket endpoint)
        await buffer.attach_mirror(websocket)
        # ... websocket stays connected, receives broadcasts
        buffer.detach_mirror(websocket)
    """

    max_history: int = 100
    broadcast_timeout: float = 0.1
    drain_timeout: float = 5.0  # Max time to wait for pending broadcasts on shutdown

    # Internal state
    _active_mirrors: list[WebSocketLike] = field(default_factory=list, init=False)
    _history: deque[dict[str, Any]] = field(init=False)
    _event_count: int = field(default=0, init=False)
    _broadcast_lock: asyncio.Lock = field(default_factory=asyncio.Lock, init=False)
    _pending_broadcasts: set[asyncio.Task[None]] = field(
        default_factory=set, init=False
    )
    _shutting_down: bool = field(default=False, init=False)

    def __post_init__(self) -> None:
        """Initialize the history deque."""
        self._history = deque(maxlen=self.max_history)

    @property
    def observer_count(self) -> int:
        """Number of active observers (mirrors)."""
        return len(self._active_mirrors)

    @property
    def history_length(self) -> int:
        """Current history length."""
        return len(self._history)

    @property
    def events_reflected(self) -> int:
        """Total events reflected through this buffer."""
        return self._event_count

    @property
    def pending_broadcast_count(self) -> int:
        """Number of broadcasts still in flight."""
        return len(self._pending_broadcasts)

    @property
    def is_shutting_down(self) -> bool:
        """True if the buffer is draining for shutdown."""
        return self._shutting_down

    async def reflect(self, event: dict[str, Any]) -> None:
        """
        Emit an event through the mirror.

        Called by FluxAgent. Does NOT await client acknowledgments.
        Fire and forget—don't let slow clients slow the agent.

        The agent's metabolism is sacred. Observers pay the cost of observation,
        not the agent.

        Args:
            event: The event to broadcast (must be JSON-serializable)
        """
        # During shutdown, skip new broadcasts but still record to history
        if self._shutting_down:
            logger.debug("Skipping broadcast during shutdown")
            self._history.append(event)
            self._event_count += 1
            return

        self._history.append(event)
        self._event_count += 1

        # Fire and forget: don't await the broadcast
        # Use create_task to avoid blocking the agent
        # Track tasks for graceful shutdown
        if self._active_mirrors:
            task = asyncio.create_task(self._broadcast(event))
            self._pending_broadcasts.add(task)
            task.add_done_callback(self._pending_broadcasts.discard)

    async def _broadcast(self, event: dict[str, Any]) -> None:
        """
        Broadcast to all mirrors, ignoring failures.

        Slow or disconnected observers are cleaned up automatically.
        The agent never sees or cares about broadcast failures.
        """
        if not self._active_mirrors:
            return

        async with self._broadcast_lock:
            try:
                payload = json.dumps(event)
            except (TypeError, ValueError) as e:
                logger.warning(f"Failed to serialize event: {e}")
                return

            # Broadcast to all, collect results
            send_tasks = [
                asyncio.wait_for(
                    ws.send_text(payload),
                    timeout=self.broadcast_timeout,
                )
                for ws in self._active_mirrors
            ]

            results = await asyncio.gather(*send_tasks, return_exceptions=True)

            # Remove disconnected mirrors
            new_mirrors = []
            for ws, result in zip(self._active_mirrors, results):
                if isinstance(result, Exception):
                    logger.debug(f"Mirror disconnected: {type(result).__name__}")
                else:
                    new_mirrors.append(ws)

            self._active_mirrors = new_mirrors

    async def attach_mirror(self, websocket: WebSocketLike) -> None:
        """
        Connect a read-only observer (The Reflection).

        New observers receive:
        1. The Ghost: Full history since buffer creation (up to max_history)
        2. Live events: All future events as they are reflected

        Args:
            websocket: WebSocket connection to attach
        """
        await websocket.accept()
        self._active_mirrors.append(websocket)

        # Send initial snapshot (The Ghost)
        for event in self._history:
            try:
                payload = json.dumps(event)
                await asyncio.wait_for(
                    websocket.send_text(payload),
                    timeout=self.broadcast_timeout,
                )
            except Exception as e:
                logger.debug(f"Failed to send history event: {e}")
                # Don't abort, try to send remaining history

    def detach_mirror(self, websocket: WebSocketLike) -> bool:
        """
        Remove an observer.

        Called when observer disconnects or is removed.

        Args:
            websocket: WebSocket to detach

        Returns:
            True if websocket was found and removed, False otherwise
        """
        if websocket in self._active_mirrors:
            self._active_mirrors.remove(websocket)
            return True
        return False

    def clear_history(self) -> None:
        """Clear the history buffer."""
        self._history.clear()

    def get_snapshot(self) -> list[dict[str, Any]]:
        """
        Get current history snapshot.

        Useful for REST endpoints that want current state without WebSocket.

        Returns:
            Copy of the current history
        """
        return list(self._history)

    async def drain(self, timeout: float | None = None) -> int:
        """
        Gracefully drain pending broadcasts before shutdown.

        Waits for all pending broadcast tasks to complete, up to timeout.
        After calling drain, new reflect() calls will skip broadcasting.

        Args:
            timeout: Maximum seconds to wait. Defaults to self.drain_timeout.

        Returns:
            Number of broadcasts that completed during drain.
        """
        if timeout is None:
            timeout = self.drain_timeout

        self._shutting_down = True

        if not self._pending_broadcasts:
            logger.info("No pending broadcasts to drain")
            return 0

        pending_count = len(self._pending_broadcasts)
        logger.info(f"Draining {pending_count} pending broadcasts (timeout={timeout}s)")

        try:
            # Wait for all pending broadcasts with timeout
            done, pending = await asyncio.wait(
                self._pending_broadcasts,
                timeout=timeout,
                return_when=asyncio.ALL_COMPLETED,
            )

            completed = len(done)
            cancelled = len(pending)

            if cancelled > 0:
                logger.warning(f"Cancelled {cancelled} broadcasts during drain")
                for task in pending:
                    task.cancel()

            logger.info(f"Drain complete: {completed} broadcasts delivered")
            return completed

        except Exception as e:
            logger.error(f"Error during drain: {e}")
            # Cancel remaining tasks
            for task in self._pending_broadcasts:
                task.cancel()
            return 0

    async def shutdown(self) -> None:
        """
        Full graceful shutdown: drain broadcasts and disconnect mirrors.

        Call this from server shutdown handlers (e.g., FastAPI lifespan).
        """
        # 1. Drain pending broadcasts
        await self.drain()

        # 2. Disconnect all mirrors
        mirror_count = len(self._active_mirrors)
        self._active_mirrors.clear()
        logger.info(f"Disconnected {mirror_count} mirrors during shutdown")
