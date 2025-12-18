"""
Town Bus Wiring: Connect Town services to the three-bus architecture.

Event Flow:
1. TownPersistence emits to DataBus on every write
2. DataBus → SynergyBus bridge for cross-jewel events
3. SynergyBus → EventBus fan-out for UI subscribers

Wire Diagram:
    TownPersistence ──emit──▶ DataBus
                                 │
                                 │ wire_data_to_synergy()
                                 ▼
                             SynergyBus ──▶ K-gent (gossip → narrative)
                                 │         ──▶ Atelier (coalition → prompt)
                                 │         ──▶ M-gent (relationship → stigmergy)
                                 │
                                 │ wire_synergy_to_event()
                                 ▼
                              EventBus ──▶ SSE stream
                                       ──▶ WebSocket
                                       ──▶ CLI logging

See: plans/town-rebuild.md Part II (Event Architecture)
"""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass, field
from typing import Any, Awaitable, Callable

from agents.d.bus import DataBus, DataEvent, DataEventType

from .events import (
    CitizenCreated,
    CitizenUpdated,
    CoalitionDissolved,
    CoalitionFormed,
    ConversationEnded,
    ConversationStarted,
    ConversationTurn,
    ForceApplied,
    GossipSpread,
    InhabitEnded,
    InhabitStarted,
    RegionActivity,
    RelationshipChanged,
    RelationshipCreated,
    SimulationStep,
    TownEvent,
    TownTopics,
)

logger = logging.getLogger(__name__)


# =============================================================================
# Type Definitions
# =============================================================================

# Handler types
TownEventHandler = Callable[[TownEvent], Awaitable[None]]
SynergyHandler = Callable[[str, TownEvent], Awaitable[None]]
UnsubscribeFunc = Callable[[], None]


# =============================================================================
# SynergyBus (Simplified for Town)
# =============================================================================


@dataclass
class TownSynergyBus:
    """
    Simplified SynergyBus for cross-jewel town events.

    Patterns subscribed by topic wildcard (e.g., "town.social.*").
    Handlers receive (topic, event) pairs.
    """

    _handlers: dict[str, list[SynergyHandler]] = field(default_factory=dict)
    _wildcard_handlers: list[tuple[str, SynergyHandler]] = field(default_factory=list)
    _emit_count: int = 0
    _error_count: int = 0

    async def publish(self, topic: str, event: TownEvent) -> None:
        """
        Publish an event to a topic.

        Notifies:
        1. Exact topic subscribers
        2. Wildcard subscribers (e.g., "town.*" matches "town.citizen.created")
        """
        self._emit_count += 1

        # Exact match handlers
        handlers = list(self._handlers.get(topic, []))

        # Wildcard handlers
        for pattern, handler in self._wildcard_handlers:
            if self._matches_wildcard(pattern, topic):
                handlers.append(handler)

        # Notify all (non-blocking, isolated)
        for handler in handlers:
            asyncio.create_task(self._safe_notify(handler, topic, event))

    def subscribe(self, topic: str, handler: SynergyHandler) -> UnsubscribeFunc:
        """
        Subscribe to a topic.

        Supports wildcards:
        - "town.*" matches all town events
        - "town.citizen.*" matches all citizen events
        """
        if "*" in topic:
            self._wildcard_handlers.append((topic, handler))

            def unsubscribe() -> None:
                try:
                    self._wildcard_handlers.remove((topic, handler))
                except ValueError:
                    pass

        else:
            self._handlers.setdefault(topic, []).append(handler)

            def unsubscribe() -> None:
                try:
                    self._handlers[topic].remove(handler)
                except (KeyError, ValueError):
                    pass

        return unsubscribe

    def _matches_wildcard(self, pattern: str, topic: str) -> bool:
        """Check if topic matches wildcard pattern."""
        if not pattern.endswith("*"):
            return pattern == topic

        prefix = pattern[:-1]  # Remove *
        return topic.startswith(prefix)

    async def _safe_notify(self, handler: SynergyHandler, topic: str, event: TownEvent) -> None:
        """Safely notify a handler, catching exceptions."""
        try:
            await handler(topic, event)
        except Exception as e:
            self._error_count += 1
            logger.error(f"SynergyBus handler error on {topic}: {e}")

    @property
    def stats(self) -> dict[str, int]:
        """Get bus statistics."""
        return {
            "total_emitted": self._emit_count,
            "total_errors": self._error_count,
            "topic_count": len(self._handlers),
            "wildcard_count": len(self._wildcard_handlers),
        }

    def clear(self) -> None:
        """Clear all handlers (for testing)."""
        self._handlers.clear()
        self._wildcard_handlers.clear()
        self._emit_count = 0
        self._error_count = 0


# =============================================================================
# EventBus (Fan-out to UI)
# =============================================================================


@dataclass
class TownEventBus:
    """
    EventBus for UI fan-out.

    Subscribers receive all events matching their filter.
    Used for SSE streams, WebSocket connections, CLI logging.
    """

    _subscribers: list[TownEventHandler] = field(default_factory=list)
    _emit_count: int = 0
    _dropped_count: int = 0
    _max_queue_size: int = 100

    async def publish(self, event: TownEvent) -> None:
        """Publish event to all subscribers."""
        self._emit_count += 1

        for subscriber in list(self._subscribers):
            asyncio.create_task(self._safe_notify(subscriber, event))

    def subscribe(self, handler: TownEventHandler) -> UnsubscribeFunc:
        """Subscribe to all events."""
        self._subscribers.append(handler)

        def unsubscribe() -> None:
            try:
                self._subscribers.remove(handler)
            except ValueError:
                pass

        return unsubscribe

    async def _safe_notify(self, handler: TownEventHandler, event: TownEvent) -> None:
        """Safely notify a handler."""
        try:
            await handler(event)
        except Exception as e:
            logger.error(f"EventBus handler error: {e}")

    @property
    def stats(self) -> dict[str, int]:
        """Get bus statistics."""
        return {
            "total_emitted": self._emit_count,
            "subscriber_count": len(self._subscribers),
            "dropped_count": self._dropped_count,
        }

    def clear(self) -> None:
        """Clear all subscribers (for testing)."""
        self._subscribers.clear()
        self._emit_count = 0
        self._dropped_count = 0


# =============================================================================
# TownDataBus (Extends DataBus for Town events)
# =============================================================================


class TownDataBus:
    """
    Town-specific DataBus that emits TownEvent types.

    Wraps the base DataBus with town-specific event handling.
    """

    def __init__(self, base_bus: DataBus | None = None) -> None:
        """Initialize with optional base DataBus."""
        self._base_bus = base_bus or DataBus()
        self._town_handlers: dict[type, list[TownEventHandler]] = {}
        self._all_handlers: list[TownEventHandler] = []
        self._emit_count = 0

    async def emit(self, event: TownEvent) -> None:
        """Emit a town event."""
        self._emit_count += 1

        # Type-specific handlers
        handlers = list(self._town_handlers.get(type(event), []))

        # All-event handlers
        handlers.extend(self._all_handlers)

        # Notify all
        for handler in handlers:
            asyncio.create_task(self._safe_notify(handler, event))

    def subscribe(self, event_type: type[TownEvent], handler: TownEventHandler) -> UnsubscribeFunc:
        """Subscribe to a specific event type."""
        self._town_handlers.setdefault(event_type, []).append(handler)

        def unsubscribe() -> None:
            try:
                self._town_handlers[event_type].remove(handler)
            except (KeyError, ValueError):
                pass

        return unsubscribe

    def subscribe_all(self, handler: TownEventHandler) -> UnsubscribeFunc:
        """Subscribe to all event types."""
        self._all_handlers.append(handler)

        def unsubscribe() -> None:
            try:
                self._all_handlers.remove(handler)
            except ValueError:
                pass

        return unsubscribe

    async def _safe_notify(self, handler: TownEventHandler, event: TownEvent) -> None:
        """Safely notify a handler."""
        try:
            await handler(event)
        except Exception as e:
            logger.error(f"TownDataBus handler error: {e}")

    @property
    def stats(self) -> dict[str, int]:
        """Get bus statistics."""
        return {
            "total_emitted": self._emit_count,
            "type_count": len(self._town_handlers),
            "all_handler_count": len(self._all_handlers),
        }

    def clear(self) -> None:
        """Clear all handlers (for testing)."""
        self._town_handlers.clear()
        self._all_handlers.clear()
        self._emit_count = 0


# =============================================================================
# Bus Wiring Functions
# =============================================================================


def wire_data_to_synergy(
    data_bus: TownDataBus,
    synergy_bus: TownSynergyBus,
) -> list[UnsubscribeFunc]:
    """
    Wire DataBus events to SynergyBus topics.

    This is the bridge between persistence and cross-jewel communication.

    Returns:
        List of unsubscribe functions (call to disconnect)
    """
    unsubscribes: list[UnsubscribeFunc] = []

    # Map event types to topics
    event_topic_map: dict[type, str] = {
        CitizenCreated: TownTopics.CITIZEN_CREATED,
        CitizenUpdated: TownTopics.CITIZEN_UPDATED,
        ConversationStarted: TownTopics.CONVERSATION_STARTED,
        ConversationTurn: TownTopics.CONVERSATION_TURN,
        ConversationEnded: TownTopics.CONVERSATION_ENDED,
        RelationshipCreated: TownTopics.RELATIONSHIP_CREATED,
        RelationshipChanged: TownTopics.RELATIONSHIP_CHANGED,
        GossipSpread: TownTopics.GOSSIP_SPREAD,
        CoalitionFormed: TownTopics.COALITION_FORMED,
        CoalitionDissolved: TownTopics.COALITION_DISSOLVED,
        InhabitStarted: TownTopics.INHABIT_STARTED,
        InhabitEnded: TownTopics.INHABIT_ENDED,
        ForceApplied: TownTopics.FORCE_APPLIED,
        SimulationStep: TownTopics.SIMULATION_STEP,
        RegionActivity: TownTopics.REGION_ACTIVITY,
    }

    for event_type, topic in event_topic_map.items():
        # Create closure properly with default parameter capture
        async def handler(event: TownEvent, _topic: str = topic) -> None:
            await synergy_bus.publish(_topic, event)

        unsub = data_bus.subscribe(event_type, handler)
        unsubscribes.append(unsub)

    return unsubscribes


def wire_synergy_to_event(
    synergy_bus: TownSynergyBus,
    event_bus: TownEventBus,
    topics: list[str] | None = None,
) -> list[UnsubscribeFunc]:
    """
    Wire SynergyBus topics to EventBus fan-out.

    This enables UI subscribers to receive town events.

    Args:
        synergy_bus: Source synergy bus
        event_bus: Target event bus
        topics: Topics to wire (default: all town topics)

    Returns:
        List of unsubscribe functions
    """
    unsubscribes: list[UnsubscribeFunc] = []

    if topics is None:
        topics = [TownTopics.ALL]

    for topic in topics:

        async def handler(t: str, event: TownEvent) -> None:
            await event_bus.publish(event)

        unsub = synergy_bus.subscribe(topic, handler)
        unsubscribes.append(unsub)

    return unsubscribes


# =============================================================================
# Cross-Jewel Handlers (Examples)
# =============================================================================


async def kgent_narrative_handler(topic: str, event: TownEvent) -> None:
    """
    K-gent handler: Generate narrative from gossip events.

    This would connect to the K-gent soul for narrative generation.
    """
    if isinstance(event, GossipSpread):
        logger.info(
            f"K-gent: Generating narrative for gossip from "
            f"{event.source_citizen} to {event.target_citizen}"
        )
        # In production: await kgent.generate_narrative(event)


async def atelier_prompt_handler(topic: str, event: TownEvent) -> None:
    """
    Atelier handler: Generate creative prompt from coalition events.

    This would connect to the Atelier crown jewel.
    """
    if isinstance(event, CoalitionFormed):
        logger.info(
            f"Atelier: Generating creative prompt for coalition "
            f"{event.coalition_id} with {len(event.members)} members"
        )
        # In production: await atelier.generate_prompt(event)


async def mgent_stigmergy_handler(topic: str, event: TownEvent) -> None:
    """
    M-gent handler: Update stigmergy from relationship events.

    This would connect to the M-gent memory system.
    """
    if isinstance(event, RelationshipChanged):
        logger.info(
            f"M-gent: Updating stigmergy for relationship {event.citizen_a} <-> {event.citizen_b}"
        )
        # In production: await mgent.update_stigmergy(event)


# =============================================================================
# TownBusManager (Orchestrator)
# =============================================================================


@dataclass
class TownBusManager:
    """
    Manages the three-bus architecture for Town.

    Provides lifecycle management and wiring coordination.
    """

    data_bus: TownDataBus = field(default_factory=TownDataBus)
    synergy_bus: TownSynergyBus = field(default_factory=TownSynergyBus)
    event_bus: TownEventBus = field(default_factory=TownEventBus)
    _wiring_unsubs: list[UnsubscribeFunc] = field(default_factory=list)
    _cross_jewel_unsubs: list[UnsubscribeFunc] = field(default_factory=list)
    _is_wired: bool = False

    def wire_all(self) -> None:
        """Wire all buses together."""
        if self._is_wired:
            return

        # DataBus → SynergyBus
        self._wiring_unsubs.extend(wire_data_to_synergy(self.data_bus, self.synergy_bus))

        # SynergyBus → EventBus
        self._wiring_unsubs.extend(wire_synergy_to_event(self.synergy_bus, self.event_bus))

        self._is_wired = True

    def wire_cross_jewel_handlers(self) -> None:
        """Wire cross-jewel event handlers."""
        # K-gent: gossip → narrative
        self._cross_jewel_unsubs.append(
            self.synergy_bus.subscribe(TownTopics.GOSSIP_SPREAD, kgent_narrative_handler)
        )

        # Atelier: coalition → prompt
        self._cross_jewel_unsubs.append(
            self.synergy_bus.subscribe(TownTopics.COALITION_FORMED, atelier_prompt_handler)
        )

        # M-gent: relationship → stigmergy
        self._cross_jewel_unsubs.append(
            self.synergy_bus.subscribe(TownTopics.RELATIONSHIP_CHANGED, mgent_stigmergy_handler)
        )

    def unwire_all(self) -> None:
        """Disconnect all wiring."""
        for unsub in self._wiring_unsubs:
            unsub()
        self._wiring_unsubs.clear()

        for unsub in self._cross_jewel_unsubs:
            unsub()
        self._cross_jewel_unsubs.clear()

        self._is_wired = False

    def clear(self) -> None:
        """Clear all buses and wiring (for testing)."""
        self.unwire_all()
        self.data_bus.clear()
        self.synergy_bus.clear()
        self.event_bus.clear()

    @property
    def stats(self) -> dict[str, dict[str, int]]:
        """Get combined statistics."""
        return {
            "data_bus": self.data_bus.stats,
            "synergy_bus": self.synergy_bus.stats,
            "event_bus": self.event_bus.stats,
        }


# =============================================================================
# Global Instance
# =============================================================================

_town_bus_manager: TownBusManager | None = None


def get_town_bus_manager() -> TownBusManager:
    """Get the global TownBusManager instance."""
    global _town_bus_manager
    if _town_bus_manager is None:
        _town_bus_manager = TownBusManager()
    return _town_bus_manager


def reset_town_bus_manager() -> None:
    """Reset the global TownBusManager (for testing)."""
    global _town_bus_manager
    if _town_bus_manager is not None:
        _town_bus_manager.clear()
    _town_bus_manager = None


# =============================================================================
# Exports
# =============================================================================


__all__ = [
    # Buses
    "TownDataBus",
    "TownSynergyBus",
    "TownEventBus",
    # Wiring
    "wire_data_to_synergy",
    "wire_synergy_to_event",
    # Manager
    "TownBusManager",
    "get_town_bus_manager",
    "reset_town_bus_manager",
    # Handlers
    "kgent_narrative_handler",
    "atelier_prompt_handler",
    "mgent_stigmergy_handler",
    # Types
    "TownEventHandler",
    "SynergyHandler",
    "UnsubscribeFunc",
]
