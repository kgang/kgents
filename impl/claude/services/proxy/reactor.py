"""
Proxy Reactor: Reactive invalidation for proxy handles.

AD-015: Proxy Handles & Transparent Batch Processes

The radical insight: Proxy handles should REACT to source changes.
When a Witness event indicates source data changed, the proxy auto-invalidates.
This enables **reactive staleness** — not just TTL-based expiration.

Event Flow:
    WitnessSynergyBus ──publish──▶ ProxyReactor._on_source_changed()
                                          │
                                          │ await store.invalidate()
                                          ▼
                                   ProxyHandleStore
                                          │
                                          │ emit event
                                          ▼
                                   WitnessSynergyBus ──▶ (cycle continues)

Source-to-Topic Mapping:
    SourceType.SPEC_CORPUS → [SPEC_DEPRECATED, SPEC_EVIDENCE_ADDED, GIT_COMMIT]
    SourceType.WITNESS_GRAPH → [THOUGHT_CAPTURED, GIT_COMMIT]
    SourceType.CODEBASE_GRAPH → [GIT_COMMIT]
    SourceType.TOWN_SNAPSHOT → [town.citizen.*]

This is the bidirectional half of Phase 2:
- Events flow OUT from store (already implemented)
- Events flow IN to invalidate (this module)

AGENTESE: services.proxy.reactor
"""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Callable

from .types import SourceType

if TYPE_CHECKING:
    from .store import ProxyHandleStore

logger = logging.getLogger(__name__)

# Type alias for unsubscribe functions
UnsubscribeFunc = Callable[[], None]


# =============================================================================
# Source-to-Topic Mapping
# =============================================================================


@dataclass(frozen=True)
class InvalidationTrigger:
    """
    Maps a WitnessSynergyBus topic to a SourceType for invalidation.

    The insight: Not all events trigger invalidation. Only source-relevant
    events should invalidate. This mapping makes that relationship explicit.
    """

    topic: str
    source_types: tuple[SourceType, ...]
    filter_fn: Callable[[dict[str, Any]], bool] | None = None  # Optional filter

    def matches_event(self, event: dict[str, Any]) -> bool:
        """Check if event should trigger invalidation."""
        if self.filter_fn is None:
            return True
        try:
            return self.filter_fn(event)
        except Exception:
            return False


# Default invalidation triggers
DEFAULT_TRIGGERS: tuple[InvalidationTrigger, ...] = (
    # Spec corpus invalidation
    InvalidationTrigger(
        topic="witness.spec.deprecated",
        source_types=(SourceType.SPEC_CORPUS,),
    ),
    InvalidationTrigger(
        topic="witness.spec.evidence_added",
        source_types=(SourceType.SPEC_CORPUS,),
    ),
    InvalidationTrigger(
        topic="witness.spec.orphan",
        source_types=(SourceType.SPEC_CORPUS,),
    ),
    # Sovereign ingest invalidation
    # When a new document is ingested, spec corpus must refresh
    InvalidationTrigger(
        topic="witness.sovereign.ingested",
        source_types=(SourceType.SPEC_CORPUS,),
    ),
    # Git commit invalidation (filtered by path)
    InvalidationTrigger(
        topic="witness.git.commit",
        source_types=(SourceType.SPEC_CORPUS, SourceType.CODEBASE_GRAPH),
        filter_fn=lambda e: any(
            f.startswith("spec/") or f.startswith("impl/")
            for f in e.get("files", e.get("files_changed", []))
            if isinstance(f, str)
        ),
    ),
    # Witness graph invalidation
    InvalidationTrigger(
        topic="witness.thought.captured",
        source_types=(SourceType.WITNESS_GRAPH,),
    ),
    # Memory crystals invalidation
    InvalidationTrigger(
        topic="witness.kblock.saved",
        source_types=(SourceType.MEMORY_CRYSTALS,),
    ),
)


# =============================================================================
# Proxy Reactor
# =============================================================================


@dataclass
class ProxyReactor:
    """
    Reactive invalidation for proxy handles.

    Subscribes to WitnessSynergyBus topics and invalidates handles
    when source data changes. This enables event-driven staleness
    detection, complementing TTL-based expiration.

    Example:
        store = get_proxy_handle_store()
        reactor = ProxyReactor(store)
        reactor.wire()  # Start listening

        # Later: Spec file changes trigger invalidation
        # → reactor detects SPEC_DEPRECATED event
        # → reactor.invalidate(SourceType.SPEC_CORPUS)
        # → handle is now STALE
        # → next access sees staleness, agent decides to refresh

    The insight: Reactive > Polling. Instead of checking "is source stale?"
    on every access, we listen for "source changed" events and pre-emptively
    invalidate. This inverts the staleness check from pull to push.
    """

    store: ProxyHandleStore
    triggers: tuple[InvalidationTrigger, ...] = field(default_factory=lambda: DEFAULT_TRIGGERS)

    # Internal state
    _unsubscribes: list[UnsubscribeFunc] = field(default_factory=list, repr=False)
    _is_wired: bool = field(default=False, repr=False)
    _invalidation_count: int = field(default=0, repr=False)
    _event_count: int = field(default=0, repr=False)

    def wire(self) -> None:
        """
        Wire reactor to WitnessSynergyBus.

        Idempotent: Multiple calls are safe.
        """
        if self._is_wired:
            logger.debug("ProxyReactor already wired, skipping")
            return

        try:
            from services.witness.bus import get_synergy_bus
        except ImportError:
            logger.warning("WitnessSynergyBus not available, ProxyReactor disabled")
            return

        bus = get_synergy_bus()
        if bus is None:
            logger.warning("WitnessSynergyBus is None, ProxyReactor disabled")
            return

        # Subscribe to each unique topic
        subscribed_topics: set[str] = set()
        for trigger in self.triggers:
            if trigger.topic in subscribed_topics:
                continue

            # Create handler bound to this trigger's source types
            async def make_handler(
                t: InvalidationTrigger,
            ) -> Callable[[str, Any], Any]:
                async def handler(topic: str, event: Any) -> None:
                    await self._on_event(topic, event, t)

                return handler

            # Subscribe
            handler = asyncio.get_event_loop().run_until_complete(make_handler(trigger))
            unsub = bus.subscribe(trigger.topic, handler)
            self._unsubscribes.append(unsub)
            subscribed_topics.add(trigger.topic)

        self._is_wired = True
        logger.info(f"ProxyReactor wired to {len(subscribed_topics)} topics")

    def wire_async(self) -> None:
        """
        Wire reactor to WitnessSynergyBus (async-safe version).

        Use this when already in an async context.
        """
        if self._is_wired:
            return

        try:
            from services.witness.bus import get_synergy_bus
        except ImportError:
            logger.warning("WitnessSynergyBus not available")
            return

        bus = get_synergy_bus()
        if bus is None:
            return

        subscribed_topics: set[str] = set()
        for trigger in self.triggers:
            if trigger.topic in subscribed_topics:
                continue

            # Subscribe with a closure that captures the trigger
            def make_handler(t: InvalidationTrigger) -> Callable[[str, Any], Any]:
                async def handler(topic: str, event: Any) -> None:
                    await self._on_event(topic, event, t)

                return handler

            unsub = bus.subscribe(trigger.topic, make_handler(trigger))
            self._unsubscribes.append(unsub)
            subscribed_topics.add(trigger.topic)

        self._is_wired = True
        logger.info(f"ProxyReactor wired (async) to {len(subscribed_topics)} topics")

    async def _on_event(
        self,
        topic: str,
        event: Any,
        trigger: InvalidationTrigger,
    ) -> None:
        """
        Handle an incoming event and potentially invalidate handles.

        Non-blocking: Errors don't crash the reactor.
        """
        self._event_count += 1

        # Ensure event is dict-like
        event_dict: dict[str, Any] = {}
        if isinstance(event, dict):
            event_dict = event
        elif hasattr(event, "to_dict"):
            event_dict = event.to_dict()

        # Check filter
        if not trigger.matches_event(event_dict):
            logger.debug(f"Event filtered out: {topic}")
            return

        # Invalidate all source types for this trigger
        for source_type in trigger.source_types:
            try:
                invalidated = await self.store.invalidate(source_type)
                if invalidated:
                    self._invalidation_count += 1
                    logger.info(f"ReactiveInvalidation: {source_type.value} due to {topic}")
            except Exception as e:
                # Never let invalidation errors crash the reactor
                logger.warning(f"Invalidation failed for {source_type.value}: {e}")

    def unwire(self) -> None:
        """
        Stop all event subscriptions.

        Safe to call multiple times.
        """
        for unsub in self._unsubscribes:
            try:
                unsub()
            except Exception as e:
                logger.warning(f"Unsubscribe failed: {e}")

        self._unsubscribes.clear()
        self._is_wired = False
        logger.info("ProxyReactor unwired")

    @property
    def stats(self) -> dict[str, Any]:
        """Get reactor statistics."""
        return {
            "is_wired": self._is_wired,
            "trigger_count": len(self.triggers),
            "subscription_count": len(self._unsubscribes),
            "event_count": self._event_count,
            "invalidation_count": self._invalidation_count,
        }

    def add_trigger(self, trigger: InvalidationTrigger) -> None:
        """
        Add a custom invalidation trigger.

        Must be called before wire().
        """
        if self._is_wired:
            raise RuntimeError("Cannot add triggers after wiring. Call unwire() first.")

        self.triggers = (*self.triggers, trigger)


# =============================================================================
# Global Reactor Instance
# =============================================================================

_reactor: ProxyReactor | None = None


def get_proxy_reactor() -> ProxyReactor:
    """
    Get the global ProxyReactor instance.

    Creates and wires the reactor if not already done.
    Uses the singleton ProxyHandleStore.
    """
    global _reactor
    if _reactor is None:
        from .store import get_proxy_handle_store

        store = get_proxy_handle_store()
        _reactor = ProxyReactor(store=store)
        _reactor.wire_async()

    return _reactor


def reset_proxy_reactor() -> None:
    """Reset the global reactor (for testing)."""
    global _reactor
    if _reactor is not None:
        _reactor.unwire()
    _reactor = None


# =============================================================================
# Module Exports
# =============================================================================

__all__ = [
    # Core class
    "ProxyReactor",
    # Trigger configuration
    "InvalidationTrigger",
    "DEFAULT_TRIGGERS",
    # Factory
    "get_proxy_reactor",
    "reset_proxy_reactor",
]
