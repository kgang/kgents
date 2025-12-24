"""
Backend Protocol for Unified Data Crystal Architecture.

This is the NEW abstraction layer that sits above the existing D-gent backends.
It provides a unified interface for storage operations with:
- Declarative queries (not just prefix/after filtering)
- Backend priority/fallback system
- Health checking and statistics

Key differences from DgentProtocol:
- Query object instead of prefix/after params
- is_available() for backend selection
- stats() for monitoring
- priority field for fallback ordering

See: spec/protocols/unified-data-crystal.md
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol

from ..datum import Datum


@dataclass(frozen=True)
class Query:
    """
    Declarative query specification for backend-agnostic data retrieval.

    This is a NoSQL-like query interface that works across all backends.
    Backends translate this to their native query language (SQL, dict filters, etc.).

    Attributes:
        tags: Filter to data with ALL of these tags (AND operation)
        author: Filter by author field in metadata
        source: Filter by source field in metadata
        after: Filter to data created after this Unix timestamp
        before: Filter to data created before this Unix timestamp
        prefix: Filter to IDs starting with this prefix
        limit: Maximum number of results (default 100)
        offset: Skip this many results (for pagination)
        where: Flexible key-value filters on metadata (AND operation)

    Examples:
        # Get recent marks
        Query(tags={"eureka"}, after=time.time() - 86400, limit=50)

        # Get data by author with metadata filter
        Query(author="kent", where={"status": "active"})

        # Pagination
        Query(limit=100, offset=100)  # Second page
    """

    tags: frozenset[str] = frozenset()
    author: str | None = None
    source: str | None = None
    after: float | None = None
    before: float | None = None
    prefix: str | None = None
    limit: int = 100
    offset: int = 0
    where: dict[str, str] | None = None  # metadata key-value filters


@dataclass(frozen=True)
class BackendStats:
    """
    Statistics about a backend's current state.

    Used for monitoring, debugging, and backend selection decisions.

    Attributes:
        name: Backend identifier (e.g., "postgres", "sqlite", "memory")
        total_datums: Number of data currently stored
        size_bytes: Total storage size in bytes (0 for memory backends)
        is_persistent: Whether data survives process restart
        is_available: Whether backend is currently accessible
        error: Error message if backend is unavailable (None if available)
    """

    name: str
    total_datums: int
    size_bytes: int
    is_persistent: bool
    is_available: bool = True
    error: str | None = None


class Backend(Protocol):
    """
    Storage backend interface for Unified Data Crystal Architecture.

    All backends (Memory, SQLite, Postgres) implement this protocol.
    The Universe class uses priority to select the best available backend.

    Attributes:
        name: Unique backend identifier (e.g., "postgres", "sqlite", "memory")
        priority: Lower = preferred (postgres=10, sqlite=50, memory=100)

    Methods:
        store: Persist a datum (idempotent - overwrites if exists)
        get: Retrieve datum by ID (None if not found)
        query: Find data matching query specification
        delete: Remove datum by ID (True if deleted, False if not found)
        is_available: Check if backend is accessible
        stats: Get current backend statistics

    Backend Selection:
        Universe iterates backends by priority (lowest first).
        First available backend is used for operations.
        If preferred backend unavailable, falls back to next.

    Example Priority Chain:
        1. PostgresBackend (priority=10) - Production, distributed
        2. SQLiteBackend (priority=50) - Local, persistent
        3. MemoryBackend (priority=100) - Ephemeral, always available
    """

    name: str
    priority: int

    async def store(self, datum: Datum) -> None:
        """
        Store a datum in the backend.

        This operation is idempotent. If a datum with the same ID already exists,
        it will be overwritten. This supports graceful degradation and updates.

        Args:
            datum: The datum to store

        Raises:
            BackendError: If storage operation fails
        """
        ...

    async def get(self, id: str) -> Datum | None:
        """
        Retrieve a datum by ID.

        Args:
            id: The datum ID to retrieve

        Returns:
            The datum if found, None otherwise

        Raises:
            BackendError: If retrieval operation fails
        """
        ...

    async def query(self, q: Query) -> list[Datum]:
        """
        Find data matching query specification.

        Backends should implement efficient queries using their native
        query language (SQL WHERE clauses, dict filtering, etc.).

        Results are always sorted by created_at descending (newest first).

        Args:
            q: Query specification with filters and limits

        Returns:
            List of matching data (may be empty)

        Raises:
            BackendError: If query operation fails

        Implementation Notes:
            - Multiple filters are combined with AND logic
            - Empty/None filters are ignored
            - Limit/offset used for pagination
            - Results sorted by created_at DESC
        """
        ...

    async def delete(self, id: str) -> bool:
        """
        Delete a datum by ID.

        Args:
            id: The datum ID to delete

        Returns:
            True if datum existed and was deleted
            False if datum was not found

        Raises:
            BackendError: If delete operation fails
        """
        ...

    async def is_available(self) -> bool:
        """
        Check if this backend is currently accessible.

        Used by Universe for backend selection. Should be fast (<100ms).

        Returns:
            True if backend can be used for operations
            False if backend is unavailable (connection failed, file missing, etc.)

        Implementation Notes:
            - Memory backend: always returns True
            - SQLite backend: checks if data directory is writable
            - Postgres backend: attempts connection with timeout
            - Should NOT raise exceptions - return False instead
        """
        ...

    async def stats(self) -> BackendStats:
        """
        Get current backend statistics.

        Used for monitoring, debugging, and health checks.

        Returns:
            BackendStats with current state

        Raises:
            BackendError: If stats collection fails
        """
        ...
