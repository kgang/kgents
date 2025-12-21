"""
D-gent Protocols: Dual interface for data persistence.

Two complementary protocols:

1. DgentProtocol (5 methods):
   - put/get/delete/list/causal_chain
   - Schema-free Datum persistence
   - Use for: raw data storage, causal lineage, schema-at-read

2. DataAgent[S] (3 methods):
   - load/save/history
   - Typed state management
   - Use for: Symbiont state threading, typed agents, state machines

These serve different purposes and both are actively used.

Teaching:
    gotcha: put() overwrites existing datum with same ID
            This is intentional for graceful degradation updates, not a bug.
            Use content-addressed IDs (SHA-256) if you need immutability.
            (Evidence: test_backends.py::TestPut::test_put_overwrites_existing)

    gotcha: causal_chain() returns empty list for missing parent, not error
            If a datum has causal_parent pointing to a deleted datum, you get
            just the child in the chain. Handle orphaned data gracefully.
            (Evidence: test_backends.py::TestCausalChain::test_causal_chain_orphaned_datum)

    gotcha: list() returns newest first (sorted by created_at descending)
            This affects pagination. Use `after` param for time-based filtering.
            (Evidence: test_backends.py::TestList::test_list_sorted_by_created_at_desc)

    gotcha: DgentRouter silently falls back to memory backend
            If preferred backend unavailable (e.g., Postgres URL missing),
            it uses MEMORY without error. Check selected_backend after put().
            (Evidence: test_router.py::TestBackendSelection::test_falls_back_to_memory)

    gotcha: DataBus subscriber errors don't block other subscribers
            A failing handler is logged but doesn't prevent event delivery.
            Check bus.stats["total_errors"] for silent failures.
            (Evidence: test_bus.py::TestErrorHandling::test_subscriber_error_does_not_block)

    gotcha: get() and list() are silent reads - no DataBus events emitted
            Only put() and delete() emit events. If you need read tracking,
            instrument at a higher layer (e.g., M-gent reinforcement).
            (Evidence: test_bus.py::TestBusEnabledDgent::test_get_does_not_emit)
"""

from __future__ import annotations

from abc import abstractmethod
from typing import List, Protocol, TypeVar, runtime_checkable

from .datum import Datum

# =============================================================================
# OLD PROTOCOL (Backward Compatibility)
# =============================================================================

S = TypeVar("S")  # State type


class DataAgent(Protocol[S]):
    """
    Typed state management protocol for Symbiont pattern.

    Use DataAgent[S] when you need:
    - State threading with Symbiont
    - Typed state (not schema-free bytes)
    - State history queries

    Implementations: VolatileAgent, PersistentAgent, LensAgent, etc.

    For schema-free Datum persistence, use DgentProtocol instead.
    """

    @abstractmethod
    async def load(self) -> S:
        """Retrieve current state."""
        ...

    @abstractmethod
    async def save(self, state: S) -> None:
        """Persist new state."""
        ...

    @abstractmethod
    async def history(self, limit: int | None = None) -> List[S]:
        """Query state evolution over time."""
        ...


# =============================================================================
# NEW PROTOCOL
# =============================================================================


@runtime_checkable
class DgentProtocol(Protocol):
    """
    The minimal interface every D-gent backend implements.

    Five methods for projection-agnostic data persistence:
    - put: Store datum, return ID
    - get: Retrieve datum by ID
    - delete: Remove datum, return success
    - list: List data with optional filters
    - causal_chain: Get causal ancestors

    All backends (Memory, JSONL, SQLite, Postgres) implement this.
    The DgentRouter selects which backend to use based on availability.
    """

    async def put(self, datum: Datum) -> str:
        """
        Store datum, return ID.

        Args:
            datum: The datum to store

        Returns:
            The datum's ID (same as datum.id)

        Note:
            If a datum with the same ID already exists, it is overwritten.
            This is intentional for supporting graceful degradation updates.
        """
        ...

    async def get(self, id: str) -> Datum | None:
        """
        Retrieve datum by ID.

        Args:
            id: The datum ID to retrieve

        Returns:
            The datum if found, None otherwise
        """
        ...

    async def delete(self, id: str) -> bool:
        """
        Remove datum, return success.

        Args:
            id: The datum ID to delete

        Returns:
            True if datum existed and was deleted, False if not found
        """
        ...

    async def list(
        self,
        prefix: str | None = None,
        after: float | None = None,
        limit: int = 100,
    ) -> List[Datum]:
        """
        List data with optional filters.

        Args:
            prefix: Filter to IDs starting with this prefix (optional)
            after: Filter to data created after this Unix timestamp (optional)
            limit: Maximum number of results to return (default 100)

        Returns:
            List of matching data, sorted by created_at descending (newest first)
        """
        ...

    async def causal_chain(self, id: str) -> List[Datum]:
        """
        Get causal ancestors of a datum.

        Follows the causal_parent links to build the full lineage.

        Args:
            id: The datum ID to trace ancestry for

        Returns:
            List of data from oldest ancestor to the given datum.
            Empty list if datum not found or has no parents.

        Example:
            If A → B → C (A is parent of B, B is parent of C):
            causal_chain("C") returns [A, B, C]
        """
        ...

    async def exists(self, id: str) -> bool:
        """
        Check if a datum exists.

        Default implementation uses get(), but backends may override
        for efficiency.

        Args:
            id: The datum ID to check

        Returns:
            True if datum exists, False otherwise
        """
        ...

    async def count(self) -> int:
        """
        Count total number of data stored.

        Default implementation may be slow for large datasets.
        Backends may override for efficiency.

        Returns:
            Total count of data
        """
        ...


class BaseDgent:
    """
    Base class providing default implementations for optional methods.

    Backends should inherit from this and implement the 5 core methods:
    put, get, delete, list, causal_chain
    """

    async def exists(self, id: str) -> bool:
        """Default: check via get()."""
        return await self.get(id) is not None

    async def count(self) -> int:
        """Default: count via list() - may be slow."""
        all_data = await self.list(limit=1_000_000)
        return len(all_data)

    async def put(self, datum: Datum) -> str:
        """Store datum, return ID."""
        raise NotImplementedError

    async def get(self, id: str) -> Datum | None:
        """Retrieve datum by ID."""
        raise NotImplementedError

    async def delete(self, id: str) -> bool:
        """Remove datum, return success."""
        raise NotImplementedError

    async def list(
        self,
        prefix: str | None = None,
        after: float | None = None,
        limit: int = 100,
    ) -> List[Datum]:
        """List data with optional filters."""
        raise NotImplementedError

    async def causal_chain(self, id: str) -> List[Datum]:
        """Get causal ancestors of a datum."""
        raise NotImplementedError
