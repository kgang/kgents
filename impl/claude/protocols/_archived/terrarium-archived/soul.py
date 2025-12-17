"""
SoulBridge: Bridge between Terrarium WebSocket and KgentFlux.

K-gent Phase 2: Terrarium Integration.

SoulBridge connects K-gent to the external world via WebSocket:

    Browser → WebSocket → SoulBridge → KgentFlux → KgentSoul
                                   ↓
                            HolographicBuffer → WebSocket → Browser

The bridge handles:
1. WebSocket message → SoulEvent conversion
2. SoulEvent → WebSocket broadcast
3. Connection lifecycle management
4. Error handling and recovery

Protocol:
    - Client sends: {"type": "dialogue", "message": "...", "mode": "reflect"}
    - Server responds: {"type": "dialogue_turn", "payload": {...}, ...}
    - Server emits: {"type": "pulse", ...} (periodic vitality)

This enables K-gent to be an ambient presence in web applications,
responding to user dialogue while maintaining personality and state.
"""

from __future__ import annotations

import asyncio
import json
import logging
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import TYPE_CHECKING, Any, AsyncIterator, Optional

if TYPE_CHECKING:
    from agents.k.flux import KgentFlux

from agents.k.events import (
    SoulEvent,
    SoulEventType,
    dialogue_turn_event,
    error_event,
    intercept_request_event,
    mode_change_event,
    ping_event,
)

from .gateway import Terrarium
from .mirror import HolographicBuffer

logger = logging.getLogger(__name__)


class MessageType(str, Enum):
    """Types of messages from WebSocket clients."""

    # Dialogue
    DIALOGUE = "dialogue"
    DIALOGUE_START = "dialogue_start"
    DIALOGUE_END = "dialogue_end"

    # Mode
    MODE_CHANGE = "mode_change"

    # Semaphore
    INTERCEPT = "intercept"

    # System
    PING = "ping"
    SNAPSHOT = "snapshot"


@dataclass
class SoulBridgeConfig:
    """Configuration for SoulBridge."""

    # Agent registration
    agent_id: str = "kgent"

    # Message handling
    max_message_length: int = 10000
    default_mode: str = "reflect"

    # Timeouts
    processing_timeout: float = 60.0

    # Enable broadcasting
    enable_broadcast: bool = True


@dataclass
class SoulBridge:
    """
    Bridge between Terrarium WebSocket and KgentFlux.

    Receives WebSocket messages, converts them to SoulEvents,
    injects them into KgentFlux, and broadcasts responses.

    Usage:
        # Create bridge
        bridge = SoulBridge(flux=kgent_flux, gateway=terrarium)

        # Start streaming (call this after flux.start())
        asyncio.create_task(bridge.stream_to_websocket())

        # Handle incoming WebSocket messages
        await bridge.handle_websocket_message({"type": "dialogue", "message": "..."})
    """

    flux: "KgentFlux"
    gateway: Terrarium
    config: SoulBridgeConfig = field(default_factory=SoulBridgeConfig)

    # Runtime state
    _mirror: Optional[HolographicBuffer] = field(default=None, init=False)
    _is_streaming: bool = field(default=False, init=False)
    _stream_task: Optional[asyncio.Task[None]] = field(default=None, init=False)

    def __post_init__(self) -> None:
        """Initialize and register with gateway."""
        # Register with gateway to get mirror
        self._mirror = self.gateway.register_agent(
            agent_id=self.config.agent_id,
            agent=self.flux,  # type: ignore[arg-type]  # duck typing
            metadata={
                "type": "kgent",
                "description": "K-gent Soul Bridge",
            },
        )

        # Attach mirror to flux for direct emission
        self.flux.attach_mirror(self._mirror)

    @property
    def is_streaming(self) -> bool:
        """Check if bridge is actively streaming."""
        return self._is_streaming

    @property
    def mirror(self) -> Optional[HolographicBuffer]:
        """Get the holographic buffer."""
        return self._mirror

    # ─────────────────────────────────────────────────────────────
    # WebSocket → SoulEvent
    # ─────────────────────────────────────────────────────────────

    async def handle_websocket_message(self, message: dict[str, Any]) -> None:
        """
        Convert WebSocket message to SoulEvent and inject into flux.

        Args:
            message: Parsed JSON message from WebSocket client

        Raises:
            ValueError: If message is malformed
        """
        event = self._message_to_event(message)
        if event is None:
            # Invalid message, send error
            if self._mirror is not None:
                err = error_event(
                    error="Invalid message type",
                    error_type="ValidationError",
                )
                await self._mirror.reflect(err.to_dict())
            return

        # Inject as perturbation (high priority)
        try:
            result = await asyncio.wait_for(
                self.flux.invoke(event),
                timeout=self.config.processing_timeout,
            )

            # Broadcast result
            if self._mirror is not None and self.config.enable_broadcast:
                await self._mirror.reflect(result.to_dict())

        except asyncio.TimeoutError:
            if self._mirror is not None:
                err = error_event(
                    error="Processing timeout",
                    error_type="TimeoutError",
                    correlation_id=event.correlation_id,
                )
                await self._mirror.reflect(err.to_dict())

        except Exception as e:
            logger.exception(f"Error processing message: {e}")
            if self._mirror is not None:
                err = error_event(
                    error=str(e),
                    error_type=type(e).__name__,
                    correlation_id=event.correlation_id,
                )
                await self._mirror.reflect(err.to_dict())

    def _message_to_event(self, message: dict[str, Any]) -> Optional[SoulEvent]:
        """Convert a WebSocket message to a SoulEvent."""
        msg_type = message.get("type", "")
        correlation_id = message.get("correlation_id") or f"ws-{uuid.uuid4().hex[:8]}"

        try:
            match msg_type:
                case "dialogue" | "dialogue_turn":
                    return self._parse_dialogue_message(message, correlation_id)

                case "mode_change":
                    return self._parse_mode_change_message(message, correlation_id)

                case "intercept":
                    return self._parse_intercept_message(message, correlation_id)

                case "ping":
                    return ping_event()

                case "snapshot":
                    return SoulEvent(
                        event_type=SoulEventType.STATE_SNAPSHOT,
                        timestamp=datetime.now(timezone.utc),
                        payload={},
                        correlation_id=correlation_id,
                    )

                case _:
                    logger.warning(f"Unknown message type: {msg_type}")
                    return None

        except Exception as e:
            logger.exception(f"Error parsing message: {e}")
            return None

    def _parse_dialogue_message(
        self,
        message: dict[str, Any],
        correlation_id: str,
    ) -> SoulEvent:
        """Parse a dialogue message."""
        msg = message.get("message", "")

        # Truncate if too long
        if len(msg) > self.config.max_message_length:
            msg = msg[: self.config.max_message_length]

        mode = message.get("mode", self.config.default_mode)

        return dialogue_turn_event(
            message=msg,
            mode=mode,
            is_request=True,
            correlation_id=correlation_id,
        )

    def _parse_mode_change_message(
        self,
        message: dict[str, Any],
        correlation_id: str,
    ) -> SoulEvent:
        """Parse a mode change message."""
        from_mode = message.get("from_mode", self.config.default_mode)
        to_mode = message.get("to_mode", message.get("mode", self.config.default_mode))

        return mode_change_event(
            from_mode=from_mode,
            to_mode=to_mode,
            correlation_id=correlation_id,
        )

    def _parse_intercept_message(
        self,
        message: dict[str, Any],
        correlation_id: str,
    ) -> SoulEvent:
        """Parse an intercept message."""
        token_id = message.get("token_id", f"token-{uuid.uuid4().hex[:8]}")
        prompt = message.get("prompt", "")
        severity = message.get("severity", "info")
        options = message.get("options", [])

        return intercept_request_event(
            token_id=token_id,
            prompt=prompt,
            severity=severity,
            options=options,
            correlation_id=correlation_id,
        )

    # ─────────────────────────────────────────────────────────────
    # SoulEvent → WebSocket
    # ─────────────────────────────────────────────────────────────

    async def stream_to_websocket(self) -> None:
        """
        Stream SoulEvents from KgentFlux to WebSocket clients.

        This should be called after flux.start() to begin streaming.
        Events flow through the HolographicBuffer to all observers.
        """
        if self._is_streaming:
            return

        self._is_streaming = True

        try:
            # The mirror handles actual broadcasting
            # We just need to ensure events are being emitted
            # This is a monitoring loop
            while self._is_streaming and self.flux.is_running:
                await asyncio.sleep(1.0)

        finally:
            self._is_streaming = False

    def start_streaming(self) -> asyncio.Task[None]:
        """Start streaming in background."""
        if self._stream_task is not None:
            return self._stream_task

        self._stream_task = asyncio.create_task(
            self.stream_to_websocket(),
            name=f"soul-bridge-stream-{self.config.agent_id}",
        )
        return self._stream_task

    async def stop_streaming(self) -> None:
        """Stop streaming."""
        self._is_streaming = False

        if self._stream_task is not None:
            self._stream_task.cancel()
            try:
                await self._stream_task
            except asyncio.CancelledError:
                pass
            self._stream_task = None

    # ─────────────────────────────────────────────────────────────
    # Lifecycle
    # ─────────────────────────────────────────────────────────────

    async def start(self, source: AsyncIterator[SoulEvent]) -> None:
        """
        Start the bridge with a source stream.

        This is a convenience method that:
        1. Starts the KgentFlux with the source
        2. Starts streaming to WebSocket

        Args:
            source: Input stream of SoulEvents
        """
        # Start flux processing
        self._stream_task = asyncio.create_task(
            self._run_flux(source),
            name=f"soul-bridge-flux-{self.config.agent_id}",
        )

        self._is_streaming = True

    async def _run_flux(self, source: AsyncIterator[SoulEvent]) -> None:
        """Run the flux and handle events."""
        async for event in self.flux.start(source):
            # Events are automatically broadcast via mirror
            # Just ensure we're tracking them
            pass

    async def stop(self) -> None:
        """Stop the bridge and cleanup."""
        await self.stop_streaming()
        await self.flux.stop()

        # Unregister from gateway
        self.gateway.unregister_agent(self.config.agent_id)

    # ─────────────────────────────────────────────────────────────
    # Direct Dialogue (Convenience)
    # ─────────────────────────────────────────────────────────────

    async def dialogue(
        self,
        message: str,
        mode: Optional[str] = None,
    ) -> dict[str, Any]:
        """
        Send a dialogue message and get response.

        This is a convenience method for direct dialogue without
        going through WebSocket. Useful for testing and CLI.

        Args:
            message: The user's message
            mode: Optional dialogue mode

        Returns:
            Response as dict
        """
        event = dialogue_turn_event(
            message=message,
            mode=mode or self.config.default_mode,
            is_request=True,
            correlation_id=f"direct-{uuid.uuid4().hex[:8]}",
        )

        result = await self.flux.invoke(event)
        return result.to_dict()


# =============================================================================
# Factory Functions
# =============================================================================


def create_soul_bridge(
    flux: Optional["KgentFlux"] = None,
    gateway: Optional[Terrarium] = None,
    agent_id: str = "kgent",
) -> SoulBridge:
    """
    Create a SoulBridge instance.

    Args:
        flux: Optional KgentFlux (creates new if None)
        gateway: Optional Terrarium gateway (creates new if None)
        agent_id: Agent ID for registration

    Returns:
        Configured SoulBridge
    """
    from agents.k.flux import KgentFlux

    if flux is None:
        flux = KgentFlux()

    if gateway is None:
        gateway = Terrarium()

    return SoulBridge(
        flux=flux,
        gateway=gateway,
        config=SoulBridgeConfig(agent_id=agent_id),
    )


async def ambient_source() -> AsyncIterator[SoulEvent]:
    """
    Ambient event source that yields nothing.

    Use this when you want KgentFlux to run in ambient mode,
    only responding to perturbations (injected events).

    This async generator waits indefinitely, never yielding events.
    Events are injected via perturbation instead.
    """
    # Make this a proper async generator by having a yield statement
    # that is syntactically present but never executed
    if False:
        yield ping_event()  # Never executed, but makes this an async generator

    # Wait forever
    while True:
        await asyncio.sleep(3600)  # 1 hour


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    "SoulBridge",
    "SoulBridgeConfig",
    "MessageType",
    "create_soul_bridge",
    "ambient_source",
]
