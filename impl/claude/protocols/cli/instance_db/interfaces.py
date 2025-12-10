"""
Repository Interfaces for Instance DB.

These interfaces abstract the storage backend, enabling:
- Local-first SQLite (default)
- PostgreSQL (team/cloud)
- Qdrant (vectors at scale)
- S3/GCS (blob storage)
- ClickHouse (telemetry at scale)

Design: Repository Pattern with async support.
"""

from contextlib import asynccontextmanager
from dataclasses import dataclass
from typing import Any, AsyncIterator, Protocol, runtime_checkable


@runtime_checkable
class IRelationalStore(Protocol):
    """
    Abstracts SQLite, PostgreSQL, MySQL, or any SQL database.

    All agent state, shapes, and dreams go through this interface.
    Uses parameterized queries with :name syntax for portability.

    Example:
        await store.execute(
            "INSERT INTO shapes (id, type) VALUES (:id, :type)",
            {"id": "SHAPE-001", "type": "insight"}
        )
    """

    async def execute(self, query: str, params: dict[str, Any] | None = None) -> int:
        """
        Execute query, return rows affected.

        Args:
            query: SQL with :name placeholders
            params: Parameter dict

        Returns:
            Number of rows affected
        """
        ...

    async def fetch_one(
        self, query: str, params: dict[str, Any] | None = None
    ) -> dict | None:
        """
        Fetch single row as dict.

        Args:
            query: SQL with :name placeholders
            params: Parameter dict

        Returns:
            Row as dict, or None if not found
        """
        ...

    async def fetch_all(
        self, query: str, params: dict[str, Any] | None = None
    ) -> list[dict]:
        """
        Fetch all rows as list of dicts.

        Args:
            query: SQL with :name placeholders
            params: Parameter dict

        Returns:
            List of rows as dicts
        """
        ...

    async def executemany(self, query: str, params_list: list[dict[str, Any]]) -> int:
        """
        Execute query for each param set (batch insert/update).

        Args:
            query: SQL with :name placeholders
            params_list: List of parameter dicts

        Returns:
            Total rows affected
        """
        ...

    @asynccontextmanager
    async def transaction(self) -> AsyncIterator["IRelationalStore"]:
        """
        Begin transaction, auto-commit on success, rollback on exception.

        Usage:
            async with store.transaction() as tx:
                await tx.execute(...)
                await tx.execute(...)
            # Auto-committed here

        Yields:
            Transaction-scoped store instance
        """
        ...

    async def close(self) -> None:
        """Close the connection."""
        ...


@dataclass
class VectorSearchResult:
    """Result from vector similarity search."""

    id: str
    distance: float
    metadata: dict[str, Any]


@runtime_checkable
class IVectorStore(Protocol):
    """
    Abstracts sqlite-vec, pgvector, Qdrant, Pinecone, or numpy fallback.

    Semantic embeddings for shapes, memories, and intents.
    Supports metadata filtering and dynamic dimensions.
    """

    @property
    def dimensions(self) -> int:
        """Current embedding dimensions (from model registry)."""
        ...

    async def upsert(
        self,
        id: str,
        vector: list[float],
        metadata: dict[str, Any],
    ) -> None:
        """
        Insert or update vector with metadata.

        Args:
            id: Unique identifier (usually shape ID)
            vector: Embedding vector
            metadata: Filterable metadata (shape_type, project_hash, etc.)
        """
        ...

    async def search(
        self,
        query_vector: list[float],
        limit: int = 10,
        filter: dict[str, Any] | None = None,
    ) -> list[VectorSearchResult]:
        """
        Search for similar vectors.

        Args:
            query_vector: Query embedding
            limit: Max results
            filter: Metadata filter (e.g., {"shape_type": "insight"})

        Returns:
            List of results with distance and metadata
        """
        ...

    async def delete(self, id: str) -> bool:
        """
        Delete vector by ID.

        Returns:
            True if deleted, False if not found
        """
        ...

    async def count(self) -> int:
        """Return total vector count."""
        ...

    async def close(self) -> None:
        """Close the store."""
        ...


@runtime_checkable
class IBlobStore(Protocol):
    """
    Abstracts filesystem, S3, GCS, MinIO, or Obsidian.

    Large state dumps, backup archives, exported artifacts.
    Uses key-value semantics with optional content types.
    """

    async def put(
        self,
        key: str,
        data: bytes,
        content_type: str | None = None,
    ) -> str:
        """
        Store blob, return URL/path.

        Args:
            key: Unique key (e.g., "backups/2025-12-10.bak")
            data: Raw bytes
            content_type: MIME type (optional)

        Returns:
            Full path or URL to stored blob
        """
        ...

    async def get(self, key: str) -> bytes | None:
        """
        Retrieve blob by key.

        Returns:
            Raw bytes, or None if not found
        """
        ...

    async def delete(self, key: str) -> bool:
        """
        Delete blob.

        Returns:
            True if deleted, False if not found
        """
        ...

    async def list(self, prefix: str = "") -> list[str]:
        """
        List keys with prefix.

        Args:
            prefix: Key prefix filter

        Returns:
            List of matching keys
        """
        ...

    async def exists(self, key: str) -> bool:
        """Check if key exists."""
        ...

    async def close(self) -> None:
        """Close the store."""
        ...


@dataclass
class TelemetryEvent:
    """A telemetry event."""

    event_type: str
    timestamp: str
    data: dict[str, Any]
    instance_id: str | None = None
    project_hash: str | None = None


@runtime_checkable
class ITelemetryStore(Protocol):
    """
    Abstracts SQLite, ClickHouse, or time-series databases.

    High-velocity event logs (separate from state for independent rotation).
    Designed for append-heavy workloads with time-based queries.
    """

    async def append(self, events: list[TelemetryEvent]) -> int:
        """
        Batch append events.

        Args:
            events: List of telemetry events

        Returns:
            Number of events appended
        """
        ...

    async def query(
        self,
        event_type: str | None = None,
        since: str | None = None,
        until: str | None = None,
        instance_id: str | None = None,
        limit: int = 1000,
    ) -> list[TelemetryEvent]:
        """
        Query events with filters.

        Args:
            event_type: Filter by event type
            since: ISO timestamp lower bound
            until: ISO timestamp upper bound
            instance_id: Filter by instance
            limit: Max results

        Returns:
            List of matching events (newest first)
        """
        ...

    async def prune(self, older_than_days: int) -> int:
        """
        Delete old events.

        Args:
            older_than_days: Delete events older than this

        Returns:
            Number of events deleted
        """
        ...

    async def count(self, event_type: str | None = None) -> int:
        """Count events, optionally by type."""
        ...

    async def close(self) -> None:
        """Close the store."""
        ...


# Type aliases for convenience
RelationalStore = IRelationalStore
VectorStore = IVectorStore
BlobStore = IBlobStore
TelemetryStore = ITelemetryStore
