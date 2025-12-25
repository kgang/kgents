"""
MemoryBackend: In-memory storage for D-gent.

Tier 0 in the projection lattice. Fast but ephemeral.
Data is lost when the process exits.

This is the NEW simplified D-gent architecture (data-architecture-rewrite).
"""

from __future__ import annotations

from typing import List

from ..datum import Datum
from ..protocol import BaseDgent


class MemoryBackend(BaseDgent):
    """
    In-memory storage backend.

    - Fast: O(1) put/get/delete, O(n) list
    - Ephemeral: Data lost on process exit
    - No external dependencies
    - Always available (tier 0 fallback)

    Thread-safety: Not thread-safe. Use with asyncio only.
    """

    def __init__(self) -> None:
        self._store: dict[str, Datum] = {}

    async def put(self, datum: Datum) -> str:
        """Store datum in memory."""
        self._store[datum.id] = datum
        return datum.id

    async def get(self, id: str) -> Datum | None:
        """Retrieve datum from memory."""
        return self._store.get(id)

    async def delete(self, id: str) -> bool:
        """Remove datum from memory."""
        if id in self._store:
            del self._store[id]
            return True
        return False

    async def list(
        self,
        prefix: str | None = None,
        after: float | None = None,
        limit: int = 100,
        schema: str | None = None,
    ) -> List[Datum]:
        """List data with filters, sorted by created_at descending.

        Args:
            prefix: Filter by ID prefix
            after: Filter by created_at timestamp
            limit: Maximum results
            schema: Filter by schema in metadata
        """
        results: List[Datum] = []

        for datum in self._store.values():
            # Apply prefix filter
            if prefix is not None and not datum.id.startswith(prefix):
                continue

            # Apply timestamp filter
            if after is not None and datum.created_at <= after:
                continue

            # Apply schema filter
            if schema is not None and datum.metadata.get("schema") != schema:
                continue

            results.append(datum)

        # Sort by created_at descending (newest first)
        results.sort(key=lambda d: d.created_at, reverse=True)

        # Apply limit
        return results[:limit]

    async def causal_chain(self, id: str) -> List[Datum]:
        """
        Get causal ancestors of a datum.

        Follows causal_parent links back to the root.
        Returns [oldest_ancestor, ..., datum] or [] if not found.
        """
        datum = self._store.get(id)
        if datum is None:
            return []

        chain: list[Datum] = [datum]

        # Walk back through parents
        current = datum
        while current.causal_parent is not None:
            parent = self._store.get(current.causal_parent)
            if parent is None:
                # Parent not found (orphaned datum)
                break
            chain.append(parent)
            current = parent

        # Reverse to get oldest first
        chain.reverse()
        return chain

    async def exists(self, id: str) -> bool:
        """Check existence directly (faster than get)."""
        return id in self._store

    async def count(self) -> int:
        """Count data directly (faster than list)."""
        return len(self._store)

    def clear(self) -> None:
        """Clear all data (for testing)."""
        self._store.clear()

    def __repr__(self) -> str:
        return f"MemoryBackend(count={len(self._store)})"
