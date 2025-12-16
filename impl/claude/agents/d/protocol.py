"""
DgentProtocol: The minimal interface for data persistence.

Five methods. That's it.

This is the NEW simplified D-gent architecture (data-architecture-rewrite).

Backward Compatibility:
    DataAgent is the OLD protocol (load/save/history). It's kept for backward
    compatibility with existing code but new code should use DgentProtocol.
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
    DEPRECATED: The old protocol for state management.

    New code should use DgentProtocol instead.

    This is kept for backward compatibility with:
    - CachedAgent
    - PersistentAgent
    - VolatileAgent
    - etc.
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
    ) -> list[Datum]:
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

    async def causal_chain(self, id: str) -> list[Datum]:
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
    ) -> list[Datum]:
        """List data with optional filters."""
        raise NotImplementedError

    async def causal_chain(self, id: str) -> list[Datum]:
        """Get causal ancestors of a datum."""
        raise NotImplementedError
