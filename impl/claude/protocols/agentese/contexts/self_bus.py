"""
AGENTESE Self Bus Context

Data Bus nodes for self.bus.* paths:
- BusNode: The agent's reactive data bus (DataBus)

Part of the Data Architecture Rewrite (plans/data-architecture-rewrite.md).
Provides AGENTESE access to the reactive event bus for data changes.

Operations: subscribe, replay, latest, stats, emit (internal)
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from ..node import (
    BaseLogosNode,
    BasicRendering,
    Renderable,
)

if TYPE_CHECKING:
    from bootstrap.umwelt import Umwelt


# === Bus Affordances ===

BUS_AFFORDANCES: tuple[str, ...] = (
    # Subscription
    "subscribe",  # Subscribe to event types
    "unsubscribe",  # Unsubscribe from events
    # Replay
    "replay",  # Replay buffered events
    # Inspection
    "latest",  # Get most recent event
    "stats",  # Get bus statistics
    "history",  # Get recent event history
)


# === Bus Node ===


@dataclass
class BusNode(BaseLogosNode):
    """
    self.bus - The agent's reactive data bus.

    Provides access to DataBus operations via AGENTESE:
    - subscribe: Subscribe to data events (PUT, DELETE, UPGRADE, DEGRADE)
    - replay: Replay buffered events for late subscribers
    - latest: Get most recent event
    - stats: Bus statistics

    AGENTESE: self.bus.*

    Event Types:
        PUT     - New datum stored
        DELETE  - Datum removed
        UPGRADE - Datum promoted to higher tier
        DEGRADE - Datum demoted (graceful degradation)

    Guarantees:
        - At-least-once delivery
        - Causal ordering (if A caused B, A delivered before B)
        - Non-blocking emission
        - Bounded buffer (old events dropped when full)
    """

    _handle: str = "self.bus"

    # DataBus (injected via create_bus_resolver)
    _bus: Any = None

    # Active subscriptions (handler_id -> unsubscribe_fn)
    _subscriptions: dict[str, Any] = None  # type: ignore[assignment]

    def __post_init__(self) -> None:
        """Initialize subscriptions dict."""
        if self._subscriptions is None:
            self._subscriptions = {}

    @property
    def handle(self) -> str:
        return self._handle

    def _get_affordances_for_archetype(self, archetype: str) -> tuple[str, ...]:
        """Bus affordances available to all archetypes."""
        return BUS_AFFORDANCES

    async def manifest(self, observer: "Umwelt[Any, Any]", **kwargs: Any) -> Renderable:
        """View current bus state."""
        if self._bus is None:
            return BasicRendering(
                summary="Data Bus (Not Configured)",
                content="DataBus not configured. Wire via create_bus_resolver().",
                metadata={"configured": False},
            )

        stats = self._bus.stats
        latest = self._bus.latest

        latest_info = "None"
        if latest:
            latest_info = f"{latest.event_type.name} on {latest.datum_id}"

        return BasicRendering(
            summary="Data Bus State",
            content=f"Buffer: {stats['buffer_size']} events\n"
            f"Total emitted: {stats['total_emitted']}\n"
            f"Subscribers: {stats['subscriber_count']}\n"
            f"Latest: {latest_info}",
            metadata={
                "configured": True,
                **stats,
                "latest_event": latest.event_id if latest else None,
            },
        )

    async def _invoke_aspect(
        self,
        aspect: str,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> Any:
        """Handle bus-specific aspects."""
        match aspect:
            case "subscribe":
                return await self._subscribe(observer, **kwargs)
            case "unsubscribe":
                return await self._unsubscribe(observer, **kwargs)
            case "replay":
                return await self._replay(observer, **kwargs)
            case "latest":
                return await self._latest(observer, **kwargs)
            case "stats":
                return await self._stats(observer, **kwargs)
            case "history":
                return await self._history(observer, **kwargs)
            case _:
                return {"aspect": aspect, "status": "not implemented"}

    # === Subscription Operations ===

    async def _subscribe(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Subscribe to data events.

        AGENTESE: self.bus.subscribe[event_type="PUT", handler_id="my_handler"]

        Note: In AGENTESE context, subscriptions are registered but handlers
        are managed externally. Use handler_id to track subscriptions.

        Args:
            event_type: Event type to subscribe to ("PUT", "DELETE", "UPGRADE", "DEGRADE", "ALL")
            handler_id: Identifier for this subscription (for later unsubscribe)

        Returns:
            Dict with subscription confirmation
        """
        if self._bus is None:
            return {"error": "DataBus not configured"}

        from agents.d.bus import DataEventType

        event_type_str = kwargs.get("event_type", "ALL")
        handler_id = kwargs.get("handler_id")

        if not handler_id:
            import uuid

            handler_id = f"sub_{uuid.uuid4().hex[:8]}"

        # Create a simple collecting handler
        collected_events: list[dict[str, Any]] = []

        async def handler(event: Any) -> None:
            collected_events.append(
                {
                    "event_id": event.event_id,
                    "event_type": event.event_type.name,
                    "datum_id": event.datum_id,
                    "timestamp": event.timestamp,
                }
            )

        # Subscribe based on event type
        if event_type_str == "ALL":
            unsubscribe = self._bus.subscribe_all(handler)
        else:
            try:
                event_type = DataEventType[event_type_str]
                unsubscribe = self._bus.subscribe(event_type, handler)
            except KeyError:
                return {
                    "error": f"Unknown event type: {event_type_str}",
                    "valid_types": ["PUT", "DELETE", "UPGRADE", "DEGRADE", "ALL"],
                }

        # Store subscription for later unsubscribe
        self._subscriptions[handler_id] = {
            "unsubscribe": unsubscribe,
            "events": collected_events,
            "event_type": event_type_str,
        }

        return {
            "status": "subscribed",
            "handler_id": handler_id,
            "event_type": event_type_str,
        }

    async def _unsubscribe(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Unsubscribe from data events.

        AGENTESE: self.bus.unsubscribe[handler_id="my_handler"]

        Args:
            handler_id: The subscription to remove

        Returns:
            Dict with unsubscription confirmation
        """
        handler_id = kwargs.get("handler_id")
        if not handler_id:
            return {
                "error": "handler_id is required",
                "active_subscriptions": list(self._subscriptions.keys()),
            }

        if handler_id not in self._subscriptions:
            return {
                "error": f"Unknown handler_id: {handler_id}",
                "active_subscriptions": list(self._subscriptions.keys()),
            }

        sub = self._subscriptions.pop(handler_id)
        sub["unsubscribe"]()

        return {
            "status": "unsubscribed",
            "handler_id": handler_id,
            "events_received": len(sub["events"]),
        }

    # === Replay Operations ===

    async def _replay(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Replay buffered events.

        AGENTESE: self.bus.replay
                  self.bus.replay[since=1702756800, event_type="PUT"]

        Useful for late subscribers to catch up on missed events.

        Args:
            since: Only replay events after this Unix timestamp
            event_type: Only replay events of this type

        Returns:
            Dict with replayed events
        """
        if self._bus is None:
            return {"error": "DataBus not configured"}

        from agents.d.bus import DataEventType

        since = kwargs.get("since")
        event_type_str = kwargs.get("event_type")

        event_type = None
        if event_type_str:
            try:
                event_type = DataEventType[event_type_str]
            except KeyError:
                return {
                    "error": f"Unknown event type: {event_type_str}",
                    "valid_types": ["PUT", "DELETE", "UPGRADE", "DEGRADE"],
                }

        # Collect events via replay
        collected: list[dict[str, Any]] = []

        async def collector(event: Any) -> None:
            collected.append(
                {
                    "event_id": event.event_id,
                    "event_type": event.event_type.name,
                    "datum_id": event.datum_id,
                    "timestamp": event.timestamp,
                    "source": event.source,
                }
            )

        count = await self._bus.replay(
            handler=collector,
            since=since,
            event_type=event_type,
        )

        return {
            "status": "replayed",
            "count": count,
            "events": collected,
            "filters": {
                "since": since,
                "event_type": event_type_str,
            },
        }

    # === Inspection Operations ===

    async def _latest(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Get most recent event.

        AGENTESE: self.bus.latest

        Returns:
            Dict with latest event details or None
        """
        if self._bus is None:
            return {"error": "DataBus not configured"}

        latest = self._bus.latest

        if latest is None:
            return {"status": "no_events", "latest": None}

        return {
            "status": "ok",
            "latest": {
                "event_id": latest.event_id,
                "event_type": latest.event_type.name,
                "datum_id": latest.datum_id,
                "timestamp": latest.timestamp,
                "source": latest.source,
                "causal_parent": latest.causal_parent,
                "metadata": latest.metadata,
            },
        }

    async def _stats(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Get bus statistics.

        AGENTESE: self.bus.stats

        Returns:
            Dict with bus statistics
        """
        if self._bus is None:
            return {"error": "DataBus not configured"}

        stats = self._bus.stats

        return {
            "status": "ok",
            "buffer_size": stats["buffer_size"],
            "total_emitted": stats["total_emitted"],
            "total_errors": stats["total_errors"],
            "subscriber_count": stats["subscriber_count"],
            "local_subscriptions": len(self._subscriptions),
        }

    async def _history(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Get recent event history from buffer.

        AGENTESE: self.bus.history
                  self.bus.history[limit=10]

        Args:
            limit: Maximum events to return (default 20)

        Returns:
            Dict with recent events
        """
        if self._bus is None:
            return {"error": "DataBus not configured"}

        limit = kwargs.get("limit", 20)

        # Access buffer directly (it's a deque)
        buffer = list(self._bus._buffer)
        recent = buffer[-limit:] if len(buffer) > limit else buffer

        return {
            "status": "ok",
            "count": len(recent),
            "total_buffered": len(buffer),
            "events": [
                {
                    "event_id": e.event_id,
                    "event_type": e.event_type.name,
                    "datum_id": e.datum_id,
                    "timestamp": e.timestamp,
                    "source": e.source,
                }
                for e in recent
            ],
        }


# === Factory Function ===


def create_bus_resolver(bus: Any = None) -> BusNode:
    """
    Create a BusNode with optional DataBus.

    Args:
        bus: DataBus instance. If None, creates unconfigured node.
             Use get_data_bus() for the global singleton.

    Returns:
        Configured BusNode

    Example:
        from agents.d.bus import get_data_bus
        bus = get_data_bus()
        bus_node = create_bus_resolver(bus)
    """
    node = BusNode()
    node._bus = bus
    node._subscriptions = {}
    return node


# =============================================================================
# DataBus → Synergy Bus Bridge
# =============================================================================


_bridge_active = False


def wire_data_to_synergy(
    data_bus: Any = None,
    synergy_bus: Any = None,
    backend_tier: str = "MEMORY",
) -> None:
    """
    Wire DataBus events to the Synergy Bus.

    This bridge forwards D-gent data events to the cross-jewel
    synergy bus, making data operations visible in the UI.

    Args:
        data_bus: DataBus instance (default: global singleton)
        synergy_bus: SynergyEventBus instance (default: global singleton)
        backend_tier: Current backend tier name for events

    Example:
        from agents.d.bus import get_data_bus
        from protocols.synergy import get_synergy_bus

        wire_data_to_synergy(get_data_bus(), get_synergy_bus())
    """
    global _bridge_active

    if _bridge_active:
        return  # Already wired

    from agents.d.bus import DataEventType, get_data_bus
    from protocols.synergy.bus import get_synergy_bus
    from protocols.synergy.events import (
        create_data_degraded_event,
        create_data_deleted_event,
        create_data_stored_event,
        create_data_upgraded_event,
    )

    data_bus = data_bus or get_data_bus()
    synergy_bus = synergy_bus or get_synergy_bus()

    async def forward_event(event: Any) -> None:
        """Forward DataEvent to SynergyBus."""
        import asyncio

        synergy_event = None

        if event.event_type == DataEventType.PUT:
            synergy_event = create_data_stored_event(
                datum_id=event.datum_id,
                content_preview=str(event.metadata) if event.metadata else "",
                content_size=0,  # Size not available in event
                backend_tier=backend_tier,
                has_parent=event.causal_parent is not None,
                metadata=event.metadata,
            )
        elif event.event_type == DataEventType.DELETE:
            synergy_event = create_data_deleted_event(
                datum_id=event.datum_id,
                backend_tier=backend_tier,
            )
        elif event.event_type == DataEventType.UPGRADE:
            synergy_event = create_data_upgraded_event(
                datum_id=event.datum_id,
                old_tier=event.metadata.get("old_tier", backend_tier),
                new_tier=event.metadata.get("new_tier", backend_tier),
                reason=event.metadata.get("reason", "access_pattern"),
            )
        elif event.event_type == DataEventType.DEGRADE:
            synergy_event = create_data_degraded_event(
                datum_id=event.datum_id,
                old_tier=event.metadata.get("old_tier", backend_tier),
                new_tier=event.metadata.get("new_tier", backend_tier),
                reason=event.metadata.get("reason", "graceful_degradation"),
            )

        if synergy_event:
            await synergy_bus.emit(synergy_event)

    # Subscribe to all data events
    data_bus.subscribe_all(forward_event)
    _bridge_active = True


def reset_data_synergy_bridge() -> None:
    """Reset the bridge state (for testing)."""
    global _bridge_active
    _bridge_active = False
