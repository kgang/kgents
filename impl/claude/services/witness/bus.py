"""
Witness Bus Architecture: Event-Driven Cross-Jewel Communication.

Parallel to services/town/bus_wiring.py — follows the same three-bus pattern.

Event Flow:
    GitWatcherFlux ──yield──▶ WitnessDaemon
                                    │
                                    │ publish()
                                    ▼
                             WitnessSynergyBus ──▶ K-gent (thought → narrative)
                                    │            ──▶ Brain (thought → crystal)
                                    │            ──▶ Gardener (commit → plot)
                                    │
                                    │ wire_synergy_to_event()
                                    ▼
                              WitnessEventBus ──▶ SSE stream
                                              ──▶ WebSocket
                                              ──▶ CLI logging

Key Principle (from meta.md):
    "Timer-driven loops create zombies—use event-driven Flux"

See: docs/skills/data-bus-integration.md
"""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass, field
from typing import Any, Awaitable, Callable

logger = logging.getLogger(__name__)


# =============================================================================
# Type Definitions
# =============================================================================

WitnessEventHandler = Callable[[Any], Awaitable[None]]
SynergyHandler = Callable[[str, Any], Awaitable[None]]
UnsubscribeFunc = Callable[[], None]


# =============================================================================
# WitnessTopics (Namespace Constants)
# =============================================================================


class WitnessTopics:
    """Topic namespace for witness events."""

    # Git events
    GIT_COMMIT = "witness.git.commit"
    GIT_CHECKOUT = "witness.git.checkout"
    GIT_PUSH = "witness.git.push"
    GIT_MERGE = "witness.git.merge"

    # Thought events
    THOUGHT_CAPTURED = "witness.thought.captured"

    # Daemon lifecycle
    DAEMON_STARTED = "witness.daemon.started"
    DAEMON_STOPPED = "witness.daemon.stopped"

    # Wildcards
    ALL = "witness.*"
    GIT_ALL = "witness.git.*"
    THOUGHT_ALL = "witness.thought.*"
    DAEMON_ALL = "witness.daemon.*"


# =============================================================================
# WitnessSynergyBus (Cross-Jewel Pub/Sub)
# =============================================================================


@dataclass
class WitnessSynergyBus:
    """
    Cross-jewel pub/sub bus with wildcard support.

    Follows TownSynergyBus pattern exactly:
    - Exact topic subscriptions
    - Wildcard subscriptions (e.g., "witness.git.*")
    - Non-blocking handler notification
    - Error isolation per handler
    """

    _handlers: dict[str, list[SynergyHandler]] = field(default_factory=dict)
    _wildcard_handlers: list[tuple[str, SynergyHandler]] = field(default_factory=list)
    _emit_count: int = 0
    _error_count: int = 0

    async def publish(self, topic: str, event: Any) -> None:
        """
        Publish an event to a topic.

        Notifies:
        1. Exact topic subscribers
        2. Wildcard subscribers (e.g., "witness.*" matches "witness.git.commit")
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
        - "witness.*" matches all witness events
        - "witness.git.*" matches all git events
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

    async def _safe_notify(self, handler: SynergyHandler, topic: str, event: Any) -> None:
        """Safely notify a handler, catching exceptions."""
        try:
            await handler(topic, event)
        except Exception as e:
            self._error_count += 1
            logger.error(f"WitnessSynergyBus handler error on {topic}: {e}")

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
# WitnessEventBus (Fan-out to UI)
# =============================================================================


@dataclass
class WitnessEventBus:
    """
    EventBus for UI fan-out.

    Subscribers receive all events.
    Used for SSE streams, WebSocket connections, CLI logging.
    """

    _subscribers: list[WitnessEventHandler] = field(default_factory=list)
    _emit_count: int = 0
    _dropped_count: int = 0

    async def publish(self, event: Any) -> None:
        """Publish event to all subscribers."""
        self._emit_count += 1

        for subscriber in list(self._subscribers):
            asyncio.create_task(self._safe_notify(subscriber, event))

    def subscribe(self, handler: WitnessEventHandler) -> UnsubscribeFunc:
        """Subscribe to all events."""
        self._subscribers.append(handler)

        def unsubscribe() -> None:
            try:
                self._subscribers.remove(handler)
            except ValueError:
                pass

        return unsubscribe

    async def _safe_notify(self, handler: WitnessEventHandler, event: Any) -> None:
        """Safely notify a handler."""
        try:
            await handler(event)
        except Exception as e:
            logger.error(f"WitnessEventBus handler error: {e}")

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
# Wiring Functions
# =============================================================================


def wire_synergy_to_event(
    synergy_bus: WitnessSynergyBus,
    event_bus: WitnessEventBus,
    topics: list[str] | None = None,
) -> list[UnsubscribeFunc]:
    """
    Wire SynergyBus topics to EventBus fan-out.

    This enables UI subscribers to receive witness events.

    Args:
        synergy_bus: Source synergy bus
        event_bus: Target event bus
        topics: Topics to wire (default: all witness topics)

    Returns:
        List of unsubscribe functions
    """
    unsubscribes: list[UnsubscribeFunc] = []

    if topics is None:
        topics = [WitnessTopics.ALL]

    for topic in topics:

        async def handler(t: str, event: Any) -> None:
            await event_bus.publish(event)

        unsub = synergy_bus.subscribe(topic, handler)
        unsubscribes.append(unsub)

    return unsubscribes


# =============================================================================
# WitnessBusManager (Orchestrator)
# =============================================================================


@dataclass
class WitnessBusManager:
    """
    Manages the two-bus architecture for Witness.

    Note: Witness uses SynergyBus + EventBus (no DataBus layer).
    The daemon publishes directly to SynergyBus.

    Provides lifecycle management and wiring coordination.
    """

    synergy_bus: WitnessSynergyBus = field(default_factory=WitnessSynergyBus)
    event_bus: WitnessEventBus = field(default_factory=WitnessEventBus)
    _wiring_unsubs: list[UnsubscribeFunc] = field(default_factory=list)
    _cross_jewel_unsubs: list[UnsubscribeFunc] = field(default_factory=list)
    _is_wired: bool = False

    def wire_all(self) -> None:
        """Wire all buses together."""
        if self._is_wired:
            return

        # SynergyBus → EventBus (all witness topics)
        self._wiring_unsubs.extend(wire_synergy_to_event(self.synergy_bus, self.event_bus))

        self._is_wired = True

    def wire_cross_jewel_handlers(self) -> None:
        """
        Wire cross-jewel event handlers.

        Example handlers (to be implemented):
        - K-gent: thought → narrative generation
        - Brain: thought → crystal storage
        - Gardener: commit → plot cultivation
        """
        # Placeholder for cross-jewel handlers
        # These will be added as other jewels integrate with Witness
        pass

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
        self.synergy_bus.clear()
        self.event_bus.clear()

    @property
    def stats(self) -> dict[str, dict[str, int]]:
        """Get combined statistics."""
        return {
            "synergy_bus": self.synergy_bus.stats,
            "event_bus": self.event_bus.stats,
        }


# =============================================================================
# Global Instance
# =============================================================================

_witness_bus_manager: WitnessBusManager | None = None


def get_witness_bus_manager() -> WitnessBusManager:
    """Get the global WitnessBusManager instance."""
    global _witness_bus_manager
    if _witness_bus_manager is None:
        _witness_bus_manager = WitnessBusManager()
    return _witness_bus_manager


def reset_witness_bus_manager() -> None:
    """Reset the global WitnessBusManager (for testing)."""
    global _witness_bus_manager
    if _witness_bus_manager is not None:
        _witness_bus_manager.clear()
    _witness_bus_manager = None


# =============================================================================
# Exports
# =============================================================================


__all__ = [
    # Topics
    "WitnessTopics",
    # Buses
    "WitnessSynergyBus",
    "WitnessEventBus",
    # Wiring
    "wire_synergy_to_event",
    # Manager
    "WitnessBusManager",
    "get_witness_bus_manager",
    "reset_witness_bus_manager",
    # Types
    "WitnessEventHandler",
    "SynergyHandler",
    "UnsubscribeFunc",
]
