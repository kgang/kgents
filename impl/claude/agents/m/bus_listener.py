"""
Bus Listener: Data Bus Integration for M-gent

Connects M-gent to the D-gent Data Bus for reactive updates.

Part of the Data Architecture Rewrite (plans/data-architecture-rewrite.md).
Follows spec/m-gents/architecture.md.

When D-gent stores data, it emits events on the Data Bus.
M-gent can listen to these events to:
    - Automatically index new data as memories
    - Update embeddings when data changes
    - Remove index entries when data is deleted

Event Types:
    PUT     - New datum stored -> Index as memory (if configured)
    DELETE  - Datum removed -> Remove from memory index
    UPGRADE - Datum promoted to higher tier -> Update metadata
    DEGRADE - Datum demoted -> Trigger resolution degradation
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Callable, Awaitable

from .memory import Lifecycle, Memory, simple_embedding

if TYPE_CHECKING:
    from agents.d.bus import DataBus, DataEvent, DataEventType
    from .associative import AssociativeMemory


# === Event Handlers ===


@dataclass
class BusEventHandler:
    """
    Handler for processing Data Bus events.

    Configurable behavior for each event type.
    """

    # Auto-index new data as memories
    auto_index: bool = True

    # Auto-remove index on delete
    auto_remove: bool = True

    # Embedder for auto-indexing
    embedder: Callable[[str], Awaitable[list[float]]] | None = None

    async def handle_put(
        self,
        event: "DataEvent",
        mgent: "AssociativeMemory",
    ) -> None:
        """
        Handle PUT event - new datum stored.

        If auto_index is True, creates a Memory entry for the datum.
        """
        if not self.auto_index:
            return

        # Check if already indexed
        if await mgent.exists(event.datum_id):
            return  # Already have this memory

        # Get content from D-gent
        datum = await mgent.dgent.get(event.datum_id)
        if datum is None:
            return

        # Compute embedding
        content = datum.content if isinstance(datum.content, str) else datum.content.decode("utf-8", errors="ignore")
        if self.embedder is not None:
            embedding = await self.embedder(content)
        else:
            embedding = list(simple_embedding(content))

        # Create memory entry (don't re-store in D-gent, just index)
        memory = Memory.create(
            datum_id=event.datum_id,
            embedding=embedding,
            metadata=event.metadata or {},
        )
        mgent._memories[event.datum_id] = memory

    async def handle_delete(
        self,
        event: "DataEvent",
        mgent: "AssociativeMemory",
    ) -> None:
        """
        Handle DELETE event - datum removed.

        If auto_remove is True, removes the Memory entry.
        """
        if not self.auto_remove:
            return

        # Remove from index (if present)
        if event.datum_id in mgent._memories:
            del mgent._memories[event.datum_id]

    async def handle_upgrade(
        self,
        event: "DataEvent",
        mgent: "AssociativeMemory",
    ) -> None:
        """
        Handle UPGRADE event - datum promoted to higher tier.

        Could update metadata to reflect new storage tier.
        """
        memory = mgent._memories.get(event.datum_id)
        if memory is None:
            return

        # Update metadata to reflect upgrade
        new_metadata = {**memory.metadata, "storage_tier": event.metadata.get("tier", "unknown")}
        mgent._memories[event.datum_id] = Memory(
            datum_id=memory.datum_id,
            embedding=memory.embedding,
            resolution=memory.resolution,
            lifecycle=memory.lifecycle,
            relevance=memory.relevance,
            last_accessed=memory.last_accessed,
            access_count=memory.access_count,
            metadata=new_metadata,
        )

    async def handle_degrade(
        self,
        event: "DataEvent",
        mgent: "AssociativeMemory",
    ) -> None:
        """
        Handle DEGRADE event - datum demoted.

        Triggers resolution degradation on the memory.
        """
        memory = mgent._memories.get(event.datum_id)
        if memory is None:
            return

        # Degrade resolution (since storage tier went down)
        mgent._memories[event.datum_id] = memory.degrade(factor=0.8)


# === Bus Listener ===


@dataclass
class MgentBusListener:
    """
    Listener that connects M-gent to the Data Bus.

    Usage:
        # Create listener
        listener = MgentBusListener(mgent=my_mgent, bus=data_bus)

        # Start listening
        listener.start()

        # ... M-gent will auto-index new data ...

        # Stop listening
        listener.stop()
    """

    mgent: "AssociativeMemory"
    bus: "DataBus"
    handler: BusEventHandler = field(default_factory=BusEventHandler)

    # Unsubscribe functions
    _unsubscribe_fns: list[Callable[[], None]] = field(default_factory=list)

    # Running state
    _is_running: bool = False

    def start(self) -> None:
        """
        Start listening to Data Bus events.

        Subscribes to all event types.
        """
        if self._is_running:
            return

        from agents.d.bus import DataEventType

        # Subscribe to each event type
        async def on_put(event: "DataEvent") -> None:
            await self.handler.handle_put(event, self.mgent)

        async def on_delete(event: "DataEvent") -> None:
            await self.handler.handle_delete(event, self.mgent)

        async def on_upgrade(event: "DataEvent") -> None:
            await self.handler.handle_upgrade(event, self.mgent)

        async def on_degrade(event: "DataEvent") -> None:
            await self.handler.handle_degrade(event, self.mgent)

        self._unsubscribe_fns.append(self.bus.subscribe(DataEventType.PUT, on_put))
        self._unsubscribe_fns.append(self.bus.subscribe(DataEventType.DELETE, on_delete))
        self._unsubscribe_fns.append(self.bus.subscribe(DataEventType.UPGRADE, on_upgrade))
        self._unsubscribe_fns.append(self.bus.subscribe(DataEventType.DEGRADE, on_degrade))

        self._is_running = True

    def stop(self) -> None:
        """
        Stop listening to Data Bus events.

        Unsubscribes from all event types.
        """
        for unsubscribe in self._unsubscribe_fns:
            unsubscribe()

        self._unsubscribe_fns.clear()
        self._is_running = False

    @property
    def is_running(self) -> bool:
        """Check if listener is currently active."""
        return self._is_running

    async def replay_and_index(self, since: float | None = None) -> int:
        """
        Replay buffered events and index any missed data.

        Useful for late-starting listeners to catch up.

        Args:
            since: Only replay events after this Unix timestamp

        Returns:
            Number of events processed
        """
        from agents.d.bus import DataEventType

        count = 0

        async def process(event: "DataEvent") -> None:
            nonlocal count
            match event.event_type:
                case DataEventType.PUT:
                    await self.handler.handle_put(event, self.mgent)
                case DataEventType.DELETE:
                    await self.handler.handle_delete(event, self.mgent)
                case DataEventType.UPGRADE:
                    await self.handler.handle_upgrade(event, self.mgent)
                case DataEventType.DEGRADE:
                    await self.handler.handle_degrade(event, self.mgent)
            count += 1

        await self.bus.replay(handler=process, since=since)
        return count


# === Factory Function ===


def create_bus_listener(
    mgent: "AssociativeMemory",
    bus: "DataBus",
    auto_index: bool = True,
    auto_remove: bool = True,
    embedder: Callable[[str], Awaitable[list[float]]] | None = None,
) -> MgentBusListener:
    """
    Create a bus listener for M-gent.

    Args:
        mgent: AssociativeMemory instance
        bus: DataBus instance
        auto_index: Auto-create memories for new data (default True)
        auto_remove: Auto-remove memories when data deleted (default True)
        embedder: Embedder function for auto-indexing

    Returns:
        Configured MgentBusListener (call .start() to begin)
    """
    handler = BusEventHandler(
        auto_index=auto_index,
        auto_remove=auto_remove,
        embedder=embedder,
    )
    return MgentBusListener(mgent=mgent, bus=bus, handler=handler)
