"""
Storage: The Left Hemisphere substrate.

From the critique:
    "Left Hemisphere (Instance DB): Structured, ACID, Relational, Exact. (The Bookkeeper)"

This module provides the storage substrate that D-gents build upon.
It is Infrastructure—bytes and rows—not semantics.

The Four Stores:
1. Relational: SQL operations (instances, shapes, dreams)
2. Vector: Embedding storage (semantic similarity)
3. Blob: Large binary storage (state dumps, artifacts)
4. Telemetry: Event logging (O-gent integration)

All stores implement Protocol interfaces for pluggable backends.
D-gent adapters provide the semantic layer on top.
"""

from __future__ import annotations

from abc import abstractmethod
from dataclasses import dataclass
from typing import Any, Protocol, runtime_checkable

from .ground import (
    Ground,
    InfrastructureConfig,
    XDGPaths,
)

# =============================================================================
# Protocol Interfaces (Infrastructure Layer)
# =============================================================================


@runtime_checkable
class IRelationalStore(Protocol):
    """
    Protocol for relational (SQL) storage.

    The Bookkeeper: exact, ACID, deterministic.
    """

    @abstractmethod
    async def execute(self, query: str, params: dict[str, Any] | None = None) -> int:
        """Execute query, return rows affected."""
        ...

    @abstractmethod
    async def fetch_one(
        self, query: str, params: dict[str, Any] | None = None
    ) -> dict[str, Any] | None:
        """Fetch single row as dict."""
        ...

    @abstractmethod
    async def fetch_all(
        self, query: str, params: dict[str, Any] | None = None
    ) -> list[dict[str, Any]]:
        """Fetch all rows as list of dicts."""
        ...

    @abstractmethod
    async def executemany(self, query: str, params_list: list[dict[str, Any]]) -> int:
        """Execute query for multiple parameter sets."""
        ...

    @abstractmethod
    async def close(self) -> None:
        """Close connection."""
        ...


@runtime_checkable
class IVectorStore(Protocol):
    """
    Protocol for vector storage.

    The Poet's substrate: approximate, probabilistic.
    D-gent VectorAgent provides the semantic layer.
    """

    @abstractmethod
    async def upsert(
        self,
        id: str,
        vector: list[float],
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Insert or update a vector."""
        ...

    @abstractmethod
    async def search(
        self,
        query_vector: list[float],
        limit: int = 10,
        filter: dict[str, Any] | None = None,
    ) -> list["VectorSearchResult"]:
        """Search for similar vectors."""
        ...

    @abstractmethod
    async def delete(self, id: str) -> bool:
        """Delete a vector by ID."""
        ...

    @abstractmethod
    async def count(self) -> int:
        """Return total vector count."""
        ...

    @abstractmethod
    async def close(self) -> None:
        """Close connection."""
        ...


@runtime_checkable
class IBlobStore(Protocol):
    """
    Protocol for blob storage.

    Large binary objects: state dumps, artifacts, exports.
    """

    @abstractmethod
    async def put(self, key: str, data: bytes) -> None:
        """Store blob data."""
        ...

    @abstractmethod
    async def get(self, key: str) -> bytes | None:
        """Retrieve blob data."""
        ...

    @abstractmethod
    async def delete(self, key: str) -> bool:
        """Delete blob by key."""
        ...

    @abstractmethod
    async def list(self, prefix: str = "") -> list[str]:
        """List blob keys with optional prefix."""
        ...

    @abstractmethod
    async def exists(self, key: str) -> bool:
        """Check if blob exists."""
        ...

    @abstractmethod
    async def close(self) -> None:
        """Close connection."""
        ...


@runtime_checkable
class ITelemetryStore(Protocol):
    """
    Protocol for telemetry/event storage.

    Event logs for O-gent observability.
    Append-only, time-series optimized.
    """

    @abstractmethod
    async def append(self, events: list["TelemetryEvent"]) -> int:
        """Append events, return count appended."""
        ...

    @abstractmethod
    async def query(
        self,
        event_type: str | None = None,
        since: str | None = None,
        until: str | None = None,
        instance_id: str | None = None,
        limit: int = 100,
    ) -> list["TelemetryEvent"]:
        """Query events with filters."""
        ...

    @abstractmethod
    async def prune(self, older_than_days: int) -> int:
        """Prune old events, return count deleted."""
        ...

    @abstractmethod
    async def count(self, event_type: str | None = None) -> int:
        """Count events with optional type filter."""
        ...

    @abstractmethod
    async def close(self) -> None:
        """Close connection."""
        ...


# =============================================================================
# Data Classes
# =============================================================================


@dataclass(frozen=True)
class VectorSearchResult:
    """Result from vector similarity search."""

    id: str
    distance: float
    metadata: dict[str, Any]

    def __hash__(self) -> int:
        return hash((self.id, self.distance))


@dataclass(frozen=True)
class TelemetryEvent:
    """A telemetry event for logging."""

    event_type: str
    timestamp: str
    instance_id: str | None
    project_hash: str | None
    data: dict[str, Any]


# =============================================================================
# Storage Provider (The Unified Substrate)
# =============================================================================


@dataclass
class StorageProvider:
    """
    Unified access to all storage backends.

    This is the Left Hemisphere—the Bookkeeper's domain.
    D-gent adapters provide semantic meaning on top.

    From the architecture:
        StorageProvider: IRelationalStore + IVectorStore + IBlobStore + ITelemetryStore
    """

    relational: IRelationalStore
    vector: IVectorStore
    blob: IBlobStore
    telemetry: ITelemetryStore
    config: InfrastructureConfig
    paths: XDGPaths

    async def close(self) -> None:
        """Close all providers."""
        await self.relational.close()
        await self.vector.close()
        await self.blob.close()
        await self.telemetry.close()

    async def run_migrations(self) -> None:
        """
        Run database migrations for all relational stores.

        Creates core tables for infrastructure:
        - instances: CLI instance tracking
        - shapes: Observed patterns
        - dreams: Consolidated insights
        - embedding_metadata: Model versioning
        - schema_version: Migration tracking
        """
        # Core membrane schema (Left Hemisphere structure)
        membrane_schema = """
        -- Instances table: tracks active kgent instances
        CREATE TABLE IF NOT EXISTS instances (
            id TEXT PRIMARY KEY,
            hostname TEXT NOT NULL,
            pid INTEGER NOT NULL,
            project_path TEXT,
            project_hash TEXT,
            started_at TEXT NOT NULL,
            last_heartbeat TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'active'
        );

        CREATE INDEX IF NOT EXISTS idx_instances_status ON instances(status);
        CREATE INDEX IF NOT EXISTS idx_instances_project ON instances(project_hash);

        -- Shapes table: observed patterns
        CREATE TABLE IF NOT EXISTS shapes (
            id TEXT PRIMARY KEY,
            shape_type TEXT NOT NULL,
            intensity REAL NOT NULL DEFAULT 1.0,
            persistence REAL NOT NULL DEFAULT 1.0,
            interpretation TEXT,
            project_hash TEXT,
            instance_id TEXT,
            observed_at TEXT NOT NULL,
            embedding_status TEXT DEFAULT 'none'
        );

        CREATE INDEX IF NOT EXISTS idx_shapes_type ON shapes(shape_type);
        CREATE INDEX IF NOT EXISTS idx_shapes_project ON shapes(project_hash);
        CREATE INDEX IF NOT EXISTS idx_shapes_observed ON shapes(observed_at DESC);

        -- Dreams table: consolidated insights
        CREATE TABLE IF NOT EXISTS dreams (
            id TEXT PRIMARY KEY,
            content TEXT NOT NULL,
            source_shapes TEXT NOT NULL,
            confidence REAL NOT NULL DEFAULT 1.0,
            dreamed_at TEXT NOT NULL
        );

        CREATE INDEX IF NOT EXISTS idx_dreams_dreamed ON dreams(dreamed_at DESC);

        -- Embedding metadata: tracks model versions
        CREATE TABLE IF NOT EXISTS embedding_metadata (
            source_id TEXT PRIMARY KEY,
            model_name TEXT NOT NULL,
            dimensions INTEGER NOT NULL,
            created_at TEXT NOT NULL,
            needs_reembed INTEGER DEFAULT 0,
            content TEXT
        );

        CREATE INDEX IF NOT EXISTS idx_embedding_reembed ON embedding_metadata(needs_reembed);

        -- Schema version
        CREATE TABLE IF NOT EXISTS schema_version (
            version INTEGER PRIMARY KEY,
            applied_at TEXT NOT NULL
        );

        INSERT OR IGNORE INTO schema_version (version, applied_at)
        VALUES (1, datetime('now'));
        """

        await self.relational.execute(membrane_schema)

    @classmethod
    async def from_ground(cls, ground: Ground) -> StorageProvider:
        """
        Create StorageProvider from Ground.

        This is the infrastructure bootstrap path:
        Ground → Config → Providers → StorageProvider
        """
        from .providers import create_providers

        # Ensure directories exist
        ground.paths.ensure_dirs()

        # Create providers from config
        relational, vector, blob, telemetry = await create_providers(
            ground.config, ground.paths
        )

        return cls(
            relational=relational,
            vector=vector,
            blob=blob,
            telemetry=telemetry,
            config=ground.config,
            paths=ground.paths,
        )

    def __repr__(self) -> str:
        return (
            f"StorageProvider("
            f"relational={type(self.relational).__name__}, "
            f"vector={type(self.vector).__name__}, "
            f"blob={type(self.blob).__name__}, "
            f"telemetry={type(self.telemetry).__name__})"
        )
