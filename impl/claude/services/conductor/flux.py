"""
ConductorFlux: Reactive event integration for CLI v7 Phase 7 (Live Flux).

This module provides reactive event handling across all CLI v7 phases:
- Phase 1: File I/O events
- Phase 2: Conversation events
- Phase 3: Presence events
- Phase 6: Swarm/A2A events

The ConductorFlux subscribes to SynergyBus events and coordinates
cross-phase reactions, enabling real-time updates across CLI/TUI/Web/Canvas.

Architecture:
    SynergyBus events ──> ConductorFlux ──> Cross-phase coordination
           │                    │
           │                    ├──> Presence updates (file changes → cursors)
           │                    ├──> Canvas updates (swarm → nodes)
           │                    └──> UI fan-out (all events → EventBus)
           │
           └──> EventBus[ConductorEvent] ──> CLI/TUI/Web/Canvas
"""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable

from protocols.synergy import (
    SynergyEvent,
    SynergyEventBus,
    SynergyEventType,
    SynergyResult,
    get_synergy_bus,
)
from protocols.synergy.handlers import BaseSynergyHandler

logger = logging.getLogger("kgents.conductor.flux")


class ConductorEventType(Enum):
    """Event types for conductor-level fan-out."""

    # File events
    FILE_CHANGED = "conductor.file.changed"

    # Conversation events
    TURN_ADDED = "conductor.turn.added"

    # Presence events
    CURSOR_MOVED = "conductor.cursor.moved"
    AGENT_JOINED = "conductor.agent.joined"
    AGENT_LEFT = "conductor.agent.left"

    # Swarm events
    SWARM_ACTIVITY = "conductor.swarm.activity"
    A2A_MESSAGE = "conductor.a2a.message"

    # Meta events
    PHASE_SYNC = "conductor.phase.sync"


@dataclass
class ConductorEvent:
    """Unified event type for conductor fan-out."""

    event_type: ConductorEventType
    source_event: SynergyEvent
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Serialize for WebSocket/SSE."""
        return {
            "type": self.event_type.value,
            "source": self.source_event.to_dict(),
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata,
        }


# Type for event subscribers
ConductorEventSubscriber = Callable[[ConductorEvent], None]


class ConductorFlux:
    """
    Reactive agent for CLI v7 event integration.

    Subscribes to cross-phase SynergyBus events and coordinates:
    - FILE_EDITED → notify presence cursors
    - CONVERSATION_TURN → update canvas context
    - SWARM_* → coordinate swarm activity
    - CURSOR_* → sync across surfaces

    This is the nerve center that makes all surfaces feel alive.
    """

    def __init__(
        self,
        bus: SynergyEventBus | None = None,
    ) -> None:
        self._bus = bus or get_synergy_bus()
        self._subscribers: list[ConductorEventSubscriber] = []
        self._unsubscribe_handles: list[Callable[[], None]] = []
        self._running = False

    @property
    def running(self) -> bool:
        """Check if flux is currently running."""
        return self._running

    def subscribe(self, subscriber: ConductorEventSubscriber) -> Callable[[], None]:
        """
        Subscribe to ConductorEvents.

        Returns unsubscribe function.
        """
        self._subscribers.append(subscriber)

        def unsubscribe() -> None:
            if subscriber in self._subscribers:
                self._subscribers.remove(subscriber)

        return unsubscribe

    def start(self) -> None:
        """
        Start the ConductorFlux.

        Registers handlers for all cross-phase events.
        """
        if self._running:
            logger.debug("ConductorFlux already running")
            return

        # Register handlers for each event type we care about
        event_types = [
            # Phase 1: File events
            SynergyEventType.FILE_READ,
            SynergyEventType.FILE_EDITED,
            SynergyEventType.FILE_CREATED,
            # Phase 2: Conversation events
            SynergyEventType.CONVERSATION_TURN,
            # Phase 3: Presence events
            SynergyEventType.CURSOR_UPDATED,
            SynergyEventType.CURSOR_JOINED,
            SynergyEventType.CURSOR_LEFT,
            # Phase 6: Swarm events
            SynergyEventType.SWARM_SPAWNED,
            SynergyEventType.SWARM_DESPAWNED,
            SynergyEventType.SWARM_A2A_MESSAGE,
            SynergyEventType.SWARM_HANDOFF,
        ]

        for event_type in event_types:
            handler = _ConductorEventHandler(
                event_type=event_type,
                flux=self,
            )
            unsubscribe = self._bus.register(event_type, handler)
            self._unsubscribe_handles.append(unsubscribe)

        self._running = True
        logger.info(f"ConductorFlux started, listening to {len(event_types)} event types")

    def stop(self) -> None:
        """Stop the ConductorFlux."""
        for unsubscribe in self._unsubscribe_handles:
            unsubscribe()
        self._unsubscribe_handles.clear()
        self._running = False
        logger.info("ConductorFlux stopped")

    def _notify_subscribers(self, event: ConductorEvent) -> None:
        """Notify all subscribers of an event."""
        for subscriber in self._subscribers:
            try:
                subscriber(event)
            except Exception as e:
                logger.warning(f"Subscriber error: {e}")

    def _handle_file_event(self, event: SynergyEvent) -> ConductorEvent:
        """Handle file-related events."""
        return ConductorEvent(
            event_type=ConductorEventType.FILE_CHANGED,
            source_event=event,
            metadata={
                "path": event.payload.get("path"),
                "agent_id": event.payload.get("agent_id"),
            },
        )

    def _handle_conversation_event(self, event: SynergyEvent) -> ConductorEvent:
        """Handle conversation events."""
        return ConductorEvent(
            event_type=ConductorEventType.TURN_ADDED,
            source_event=event,
            metadata={
                "session_id": event.payload.get("session_id"),
                "turn_number": event.payload.get("turn_number"),
                "role": event.payload.get("role"),
            },
        )

    def _handle_presence_event(self, event: SynergyEvent) -> ConductorEvent:
        """Handle presence/cursor events."""
        event_map = {
            SynergyEventType.CURSOR_UPDATED: ConductorEventType.CURSOR_MOVED,
            SynergyEventType.CURSOR_JOINED: ConductorEventType.AGENT_JOINED,
            SynergyEventType.CURSOR_LEFT: ConductorEventType.AGENT_LEFT,
        }
        conductor_type = event_map.get(
            event.event_type,
            ConductorEventType.CURSOR_MOVED,
        )
        return ConductorEvent(
            event_type=conductor_type,
            source_event=event,
            metadata={
                "agent_id": event.payload.get("agent_id"),
                "display_name": event.payload.get("display_name"),
            },
        )

    def _handle_swarm_event(self, event: SynergyEvent) -> ConductorEvent:
        """Handle swarm/A2A events."""
        if event.event_type == SynergyEventType.SWARM_A2A_MESSAGE:
            return ConductorEvent(
                event_type=ConductorEventType.A2A_MESSAGE,
                source_event=event,
                metadata={
                    "from_agent": event.payload.get("from_agent"),
                    "to_agent": event.payload.get("to_agent"),
                },
            )
        return ConductorEvent(
            event_type=ConductorEventType.SWARM_ACTIVITY,
            source_event=event,
            metadata={
                "agent_id": event.payload.get("agent_id") or event.source_id,
            },
        )


class _ConductorEventHandler(BaseSynergyHandler):
    """Internal handler that routes SynergyEvents to ConductorFlux."""

    def __init__(
        self,
        event_type: SynergyEventType,
        flux: ConductorFlux,
    ) -> None:
        self._event_type = event_type
        self._flux = flux

    @property
    def name(self) -> str:
        return f"ConductorFlux[{self._event_type.value}]"

    async def handle(self, event: SynergyEvent) -> SynergyResult:
        """Route event to ConductorFlux."""
        try:
            # Determine handler based on event type
            if event.event_type in (
                SynergyEventType.FILE_READ,
                SynergyEventType.FILE_EDITED,
                SynergyEventType.FILE_CREATED,
            ):
                conductor_event = self._flux._handle_file_event(event)
            elif event.event_type == SynergyEventType.CONVERSATION_TURN:
                conductor_event = self._flux._handle_conversation_event(event)
            elif event.event_type in (
                SynergyEventType.CURSOR_UPDATED,
                SynergyEventType.CURSOR_JOINED,
                SynergyEventType.CURSOR_LEFT,
            ):
                conductor_event = self._flux._handle_presence_event(event)
            else:
                # Swarm events
                conductor_event = self._flux._handle_swarm_event(event)

            # Notify subscribers
            self._flux._notify_subscribers(conductor_event)

            return SynergyResult(
                success=True,
                handler_name=self.name,
                message=f"Routed {event.event_type.value} to conductor",
            )

        except Exception as e:
            logger.warning(f"Handler error: {e}")
            return SynergyResult(
                success=False,
                handler_name=self.name,
                message=f"Error: {e}",
            )


# =============================================================================
# Singleton Instance
# =============================================================================

_flux: ConductorFlux | None = None


def get_conductor_flux() -> ConductorFlux:
    """Get the global ConductorFlux instance."""
    global _flux
    if _flux is None:
        _flux = ConductorFlux()
    return _flux


def reset_conductor_flux() -> None:
    """Reset the global flux (for testing)."""
    global _flux
    if _flux is not None:
        _flux.stop()
    _flux = None


def start_conductor_flux() -> ConductorFlux:
    """Start the global ConductorFlux."""
    flux = get_conductor_flux()
    flux.start()
    return flux


__all__ = [
    "ConductorFlux",
    "ConductorEvent",
    "ConductorEventType",
    "ConductorEventSubscriber",
    "get_conductor_flux",
    "reset_conductor_flux",
    "start_conductor_flux",
]
