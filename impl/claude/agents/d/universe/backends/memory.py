"""
MemoryBackend: In-memory storage adapter for Unified Data Crystal.

Wraps the existing agents.d.backends.MemoryBackend with the new Backend protocol.

Characteristics:
- Priority: 100 (lowest - fallback of last resort)
- Persistent: No (data lost on process exit)
- Always available: Yes
- Performance: O(1) get/store, O(n) query

Use cases:
- Testing
- Ephemeral data
- Fallback when other backends unavailable
"""

from __future__ import annotations

import logging

from ...backends.memory import MemoryBackend as LegacyMemoryBackend
from ...datum import Datum
from ..backend import BackendStats, Query

logger = logging.getLogger(__name__)


class MemoryBackend:
    """
    In-memory storage backend adapter.

    Wraps agents.d.backends.MemoryBackend to implement the new Backend protocol.

    Priority: 100 (lowest priority - used as fallback)
    Persistent: No
    Available: Always
    """

    name: str = "memory"
    priority: int = 100

    def __init__(self) -> None:
        """Initialize in-memory backend."""
        self._backend = LegacyMemoryBackend()
        logger.debug("MemoryBackend initialized")

    async def store(self, datum: Datum) -> None:
        """Store datum in memory."""
        await self._backend.put(datum)

    async def get(self, id: str) -> Datum | None:
        """Retrieve datum from memory."""
        return await self._backend.get(id)

    async def query(self, q: Query) -> list[Datum]:
        """
        Query data in memory with filters.

        Implementation uses the legacy list() method and adds additional filtering.
        """
        # Start with prefix and timestamp filters (supported by legacy backend)
        results = await self._backend.list(
            prefix=q.prefix,
            after=q.after,
            limit=q.limit + q.offset,  # Get extra for offset
        )

        # Apply additional filters manually
        filtered: list[Datum] = []

        for datum in results:
            # Before filter
            if q.before is not None and datum.created_at >= q.before:
                continue

            # Tags filter (must have ALL tags)
            if q.tags:
                datum_tags = (
                    set(datum.metadata.get("tags", "").split(","))
                    if datum.metadata.get("tags")
                    else set()
                )
                if not q.tags.issubset(datum_tags):
                    continue

            # Author filter
            if q.author is not None and datum.metadata.get("author") != q.author:
                continue

            # Source filter
            if q.source is not None and datum.metadata.get("source") != q.source:
                continue

            # Where filter (AND of all key-value pairs)
            if q.where:
                match = True
                for key, value in q.where.items():
                    if datum.metadata.get(key) != value:
                        match = False
                        break
                if not match:
                    continue

            filtered.append(datum)

        # Apply offset and limit
        return filtered[q.offset : q.offset + q.limit]

    async def delete(self, id: str) -> bool:
        """Delete datum from memory."""
        return await self._backend.delete(id)

    async def is_available(self) -> bool:
        """Memory backend is always available."""
        return True

    async def stats(self) -> BackendStats:
        """Get current memory backend statistics."""
        count = await self._backend.count()

        # Estimate size (rough approximation)
        # Each datum ~= 100 bytes overhead + content size
        total_size = 0
        for datum in self._backend._store.values():
            total_size += 100 + len(datum.content)

        return BackendStats(
            name=self.name,
            total_datums=count,
            size_bytes=total_size,
            is_persistent=False,
            is_available=True,
        )

    def clear(self) -> None:
        """Clear all data (for testing)."""
        self._backend.clear()

    def __repr__(self) -> str:
        return f"MemoryBackend(count={len(self._backend._store)})"
