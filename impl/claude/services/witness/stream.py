"""
Crystal Streaming: Real-Time Crystal Updates via SSE.

Provides Server-Sent Events (SSE) streaming for crystal updates,
enabling real-time UI subscriptions and agent notifications.

Architecture:
    CrystalStore.append() ──▶ WitnessSynergyBus ──▶ crystal_stream()
                                     │
                                     ├──▶ SSE endpoint
                                     └──▶ WebSocket (future)

The stream emits:
- "crystal.created" — New crystal appended to store
- "crystal.batch" — Multiple crystals (e.g., after bulk crystallization)
- "heartbeat" — Keep-alive every 30 seconds

Philosophy:
    "Crystallization is observable. Compression is public."

    Unlike marks (which are often private actions), crystals are
    designed to be shared. Streaming makes this sharing real-time.

See: spec/protocols/witness-crystallization.md
See: docs/skills/data-bus-integration.md
"""

from __future__ import annotations

import asyncio
import json
import logging
import time
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any, AsyncIterator, Callable

from .bus import WitnessEventBus, WitnessSynergyBus, WitnessTopics, get_witness_bus_manager
from .crystal import Crystal, CrystalId, CrystalLevel
from .crystal_store import get_crystal_store

logger = logging.getLogger("kgents.witness.stream")


# =============================================================================
# Crystal Event Types
# =============================================================================


class CrystalEventType:
    """Event types for crystal streaming."""

    CREATED = "crystal.created"
    BATCH = "crystal.batch"
    HEARTBEAT = "heartbeat"
    ERROR = "error"


@dataclass
class CrystalEvent:
    """
    A crystal streaming event.

    Wraps crystal data with metadata for SSE transmission.
    """

    event_type: str
    data: dict[str, Any]
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))

    def to_sse(self) -> str:
        """Format as SSE string."""
        payload = {
            "type": self.event_type,
            "timestamp": self.timestamp.isoformat(),
            "data": self.data,
        }
        return f"event: {self.event_type}\ndata: {json.dumps(payload)}\n\n"

    @classmethod
    def created(cls, crystal: Crystal) -> CrystalEvent:
        """Create a crystal.created event."""
        return cls(
            event_type=CrystalEventType.CREATED,
            data={
                "id": str(crystal.id),
                "level": crystal.level.name,
                "insight": crystal.insight,
                "significance": crystal.significance,
                "principles": list(crystal.principles),
                "topics": list(crystal.topics),
                "source_count": crystal.source_count,
                "confidence": crystal.confidence,
                "crystallized_at": crystal.crystallized_at.isoformat(),
            },
        )

    @classmethod
    def batch(cls, crystals: list[Crystal]) -> CrystalEvent:
        """Create a crystal.batch event."""
        return cls(
            event_type=CrystalEventType.BATCH,
            data={
                "count": len(crystals),
                "crystals": [
                    {
                        "id": str(c.id),
                        "level": c.level.name,
                        "insight": c.insight[:100],
                    }
                    for c in crystals
                ],
            },
        )

    @classmethod
    def heartbeat(cls) -> CrystalEvent:
        """Create a heartbeat event."""
        return cls(
            event_type=CrystalEventType.HEARTBEAT,
            data={
                "message": "keep-alive",
                "server_time": datetime.now(UTC).isoformat(),
            },
        )

    @classmethod
    def error(cls, message: str, code: str = "unknown") -> CrystalEvent:
        """Create an error event."""
        return cls(
            event_type=CrystalEventType.ERROR,
            data={
                "code": code,
                "message": message,
            },
        )


# =============================================================================
# Crystal Stream Generator
# =============================================================================


async def crystal_stream(
    level_filter: CrystalLevel | None = None,
    heartbeat_interval: float = 30.0,
    include_initial: bool = False,
    initial_limit: int = 10,
) -> AsyncIterator[str]:
    """
    Async generator yielding SSE-formatted crystal events.

    Subscribes to the WitnessSynergyBus and emits crystal events.

    Args:
        level_filter: Only emit crystals at this level (None = all levels)
        heartbeat_interval: Seconds between heartbeat events
        include_initial: Whether to emit recent crystals on connect
        initial_limit: Number of initial crystals to emit

    Yields:
        SSE-formatted strings (event: type\\ndata: json\\n\\n)

    Example:
        async for event in crystal_stream(level_filter=CrystalLevel.SESSION):
            print(event)
    """
    # Get the event bus for fan-out
    manager = get_witness_bus_manager()
    event_bus = manager.event_bus
    synergy_bus = manager.synergy_bus

    # Queue for receiving events
    event_queue: asyncio.Queue[CrystalEvent] = asyncio.Queue()
    last_heartbeat = time.time()

    # Subscribe to crystal events on synergy bus
    async def on_crystal_created(topic: str, event: Any) -> None:
        """Handle crystal creation from synergy bus."""
        if not isinstance(event, dict):
            return

        # Check level filter
        if level_filter is not None:
            event_level = event.get("level")
            if event_level != level_filter.name:
                return

        # Convert to CrystalEvent
        crystal_event = CrystalEvent(
            event_type=CrystalEventType.CREATED,
            data=event,
        )
        await event_queue.put(crystal_event)

    # Register topic for crystal creation (we'll add this topic)
    CRYSTAL_CREATED_TOPIC = "witness.crystal.created"
    unsub = synergy_bus.subscribe(CRYSTAL_CREATED_TOPIC, on_crystal_created)

    try:
        # Emit initial crystals if requested
        if include_initial:
            store = get_crystal_store()
            initial_crystals = store.recent(limit=initial_limit, level=level_filter)
            if initial_crystals:
                yield CrystalEvent.batch(initial_crystals).to_sse()

        # Main event loop
        while True:
            try:
                # Wait for event with heartbeat timeout
                event = await asyncio.wait_for(
                    event_queue.get(),
                    timeout=heartbeat_interval,
                )
                yield event.to_sse()

            except asyncio.TimeoutError:
                # No event received, emit heartbeat
                now = time.time()
                if now - last_heartbeat >= heartbeat_interval:
                    yield CrystalEvent.heartbeat().to_sse()
                    last_heartbeat = now

    except asyncio.CancelledError:
        logger.debug("Crystal stream cancelled")
    finally:
        unsub()


# =============================================================================
# Crystal Event Publishing
# =============================================================================


async def publish_crystal_created(crystal: Crystal) -> None:
    """
    Publish a crystal creation event to the synergy bus.

    Call this after appending a crystal to the store.

    Args:
        crystal: The newly created crystal
    """
    manager = get_witness_bus_manager()
    synergy_bus = manager.synergy_bus

    CRYSTAL_CREATED_TOPIC = "witness.crystal.created"

    event_data = {
        "id": str(crystal.id),
        "level": crystal.level.name,
        "insight": crystal.insight,
        "significance": crystal.significance,
        "principles": list(crystal.principles),
        "topics": list(crystal.topics),
        "source_count": crystal.source_count,
        "confidence": crystal.confidence,
        "crystallized_at": crystal.crystallized_at.isoformat(),
    }

    await synergy_bus.publish(CRYSTAL_CREATED_TOPIC, event_data)
    logger.debug(f"Published crystal.created for {crystal.id}")


# =============================================================================
# CLI Stream Command
# =============================================================================


async def stream_crystals_cli(
    level: int | None = None,
    include_initial: bool = True,
) -> AsyncIterator[str]:
    """
    CLI-friendly crystal stream.

    Formats events for terminal display.

    Args:
        level: Filter by level (0-3) or None for all
        include_initial: Show recent crystals on start

    Yields:
        Formatted strings for terminal display
    """
    level_filter = CrystalLevel(level) if level is not None else None

    async for event_str in crystal_stream(
        level_filter=level_filter,
        include_initial=include_initial,
    ):
        # Parse event
        try:
            lines = event_str.strip().split("\n")
            event_type = lines[0].replace("event: ", "")
            data_json = lines[1].replace("data: ", "")
            payload = json.loads(data_json)

            if event_type == CrystalEventType.HEARTBEAT:
                yield "[heartbeat]"
            elif event_type == CrystalEventType.CREATED:
                data = payload.get("data", {})
                level_name = data.get("level", "?")
                insight = data.get("insight", "")[:60]
                yield f"[{level_name}] {insight}..."
            elif event_type == CrystalEventType.BATCH:
                data = payload.get("data", {})
                count = data.get("count", 0)
                yield f"[batch] {count} crystals"
            else:
                yield f"[{event_type}] {payload}"
        except (json.JSONDecodeError, IndexError):
            yield event_str


# =============================================================================
# SSE Endpoint Helper
# =============================================================================


def create_crystal_sse_response(
    level_filter: CrystalLevel | None = None,
    include_initial: bool = True,
) -> AsyncIterator[str]:
    """
    Create an SSE response generator for FastAPI/Starlette.

    Example with FastAPI:
        @app.get("/witness/crystals/stream")
        async def crystal_stream_endpoint(level: int | None = None):
            from starlette.responses import StreamingResponse
            level_filter = CrystalLevel(level) if level else None
            return StreamingResponse(
                create_crystal_sse_response(level_filter),
                media_type="text/event-stream",
            )
    """
    return crystal_stream(
        level_filter=level_filter,
        include_initial=include_initial,
    )


# =============================================================================
# Module Exports
# =============================================================================

__all__ = [
    # Event types
    "CrystalEventType",
    "CrystalEvent",
    # Streaming
    "crystal_stream",
    "publish_crystal_created",
    "stream_crystals_cli",
    "create_crystal_sse_response",
]
