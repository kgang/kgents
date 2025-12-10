"""
Infrastructure Backends: D-gent adapters for Instance DB stores.

This module bridges agents/d (D-gents) with protocols/cli/instance_db (Cortex).

Provides:
- InstanceDBVectorBackend: Wraps IVectorStore as D-gent VectorAgent backend
- InstanceDBRelationalBackend: Wraps IRelationalStore as D-gent data store
- CortexAdapter: Unified interface for Bicameral Memory operations

Design rationale:
- D-gents are the user-facing API (semantic, temporal, relational operations)
- Instance DB is the infrastructure layer (SQLite, numpy, filesystem)
- This module provides the glue layer

From the implementation plan:
> "Left Hemisphere (SQL) and Right Hemisphere (Vector) can diverge."
> "Solution: Coherency Protocol - Cross-hemisphere validation preventing Ghost Memories"
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Generic, Protocol, TypeVar, runtime_checkable

# Import from instance_db (protocols layer)
try:
    from protocols.cli.instance_db.interfaces import (
        IRelationalStore,
        IVectorStore,
        VectorSearchResult,
    )
    from protocols.cli.instance_db.nervous import Signal

    _INSTANCE_DB_AVAILABLE = True
except ImportError:
    _INSTANCE_DB_AVAILABLE = False
    IRelationalStore = None  # type: ignore
    IVectorStore = None  # type: ignore
    VectorSearchResult = None  # type: ignore
    Signal = None  # type: ignore

from .errors import NoosphereError, StateNotFoundError, StorageError
from .protocol import DataAgent

S = TypeVar("S")


class InfraBackendError(NoosphereError):
    """Infrastructure backend operation failed."""


class GhostMemoryError(InfraBackendError):
    """Vector entry points to non-existent relational row (Ghost Memory)."""


class StaleEmbeddingError(InfraBackendError):
    """Embedding is stale - content has changed since embedding."""


@dataclass
class ContentHash:
    """Content hash for staleness detection."""

    algorithm: str = "sha256"
    hash_value: str = ""
    computed_at: str = field(default_factory=lambda: datetime.now().isoformat())

    @classmethod
    def compute(cls, data: Any) -> "ContentHash":
        """Compute content hash for any data."""
        serialized = json.dumps(data, sort_keys=True, default=str)
        hash_value = hashlib.sha256(serialized.encode()).hexdigest()[:16]
        return cls(algorithm="sha256", hash_value=hash_value)


@dataclass
class VectorMetadata:
    """Metadata stored alongside vector embeddings."""

    relational_id: str  # ID in relational store (source of truth)
    content_hash: str  # For staleness detection
    created_at: str
    updated_at: str
    table: str  # Which relational table this came from
    extra: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dict for storage."""
        return {
            "relational_id": self.relational_id,
            "content_hash": self.content_hash,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "table": self.table,
            **self.extra,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "VectorMetadata":
        """Create from stored dict."""
        extra = {
            k: v
            for k, v in data.items()
            if k
            not in (
                "relational_id",
                "content_hash",
                "created_at",
                "updated_at",
                "table",
            )
        }
        return cls(
            relational_id=data.get("relational_id", ""),
            content_hash=data.get("content_hash", ""),
            created_at=data.get("created_at", ""),
            updated_at=data.get("updated_at", ""),
            table=data.get("table", ""),
            extra=extra,
        )


@dataclass
class RecallResult:
    """Result from cross-hemisphere recall."""

    id: str
    data: dict[str, Any]
    distance: float  # From vector search
    is_stale: bool = False  # True if content_hash mismatch
    was_ghost: bool = False  # True if healed ghost


@runtime_checkable
class IEmbeddingProvider(Protocol):
    """Protocol for generating embeddings."""

    def embed(self, text: str) -> list[float]:
        """Generate embedding for text."""
        ...

    @property
    def dimensions(self) -> int:
        """Embedding dimensions."""
        ...


class NullEmbeddingProvider:
    """Null embedding provider (zeros) for testing."""

    def __init__(self, dimensions: int = 384):
        self._dimensions = dimensions

    def embed(self, text: str) -> list[float]:
        """Return zero vector."""
        return [0.0] * self._dimensions

    @property
    def dimensions(self) -> int:
        return self._dimensions


@dataclass
class InstanceDBVectorBackendConfig:
    """Configuration for InstanceDBVectorBackend."""

    # Which relational table to track
    table: str = "shapes"
    id_column: str = "id"
    content_column: str = "content"

    # Ghost healing
    auto_heal_ghosts: bool = True

    # Staleness
    flag_stale_on_recall: bool = True


class InstanceDBVectorBackend:
    """
    Wraps IVectorStore for use with D-gent semantic operations.

    This adapter:
    - Stores vectors with relational metadata for coherency
    - Supports ghost detection and self-healing
    - Tracks content hashes for staleness detection

    Usage:
        backend = InstanceDBVectorBackend(vector_store, relational_store)
        await backend.upsert(
            id="shape-001",
            vector=embeddings,
            content={"type": "insight", "text": "..."}
        )
        results = await backend.search(query_vector, limit=10)
    """

    def __init__(
        self,
        vector_store: IVectorStore,
        relational_store: IRelationalStore | None = None,
        config: InstanceDBVectorBackendConfig | None = None,
    ):
        """
        Initialize the vector backend.

        Args:
            vector_store: IVectorStore for vector operations
            relational_store: IRelationalStore for coherency validation
            config: Backend configuration
        """
        if not _INSTANCE_DB_AVAILABLE:
            raise ImportError(
                "Instance DB not available. Ensure protocols/cli/instance_db is accessible."
            )

        self._vector_store = vector_store
        self._relational_store = relational_store
        self._config = config or InstanceDBVectorBackendConfig()

        # Healing statistics
        self._ghosts_healed = 0
        self._stale_flagged = 0

    @property
    def dimensions(self) -> int:
        """Get vector dimensions."""
        return self._vector_store.dimensions

    async def upsert(
        self,
        id: str,
        vector: list[float],
        content: dict[str, Any],
        table: str | None = None,
    ) -> VectorMetadata:
        """
        Insert or update vector with relational metadata.

        Args:
            id: Unique identifier
            vector: Embedding vector
            content: Content for hash computation
            table: Override relational table name

        Returns:
            VectorMetadata including content_hash
        """
        now = datetime.now().isoformat()
        content_hash = ContentHash.compute(content)

        metadata = VectorMetadata(
            relational_id=id,
            content_hash=content_hash.hash_value,
            created_at=now,
            updated_at=now,
            table=table or self._config.table,
        )

        await self._vector_store.upsert(
            id=id,
            vector=vector,
            metadata=metadata.to_dict(),
        )

        return metadata

    async def search(
        self,
        query_vector: list[float],
        limit: int = 10,
        filter: dict[str, Any] | None = None,
        validate_coherency: bool = True,
    ) -> list[RecallResult]:
        """
        Search for similar vectors with optional coherency validation.

        Args:
            query_vector: Query embedding
            limit: Max results
            filter: Metadata filter
            validate_coherency: If True, validate against relational store

        Returns:
            List of RecallResult with coherency info
        """
        # Get vector results
        vector_results = await self._vector_store.search(
            query_vector=query_vector,
            limit=limit * 2
            if validate_coherency
            else limit,  # Over-fetch for filtering
            filter=filter,
        )

        if not validate_coherency or not self._relational_store:
            # No coherency check - return raw results
            return [
                RecallResult(
                    id=r.id,
                    data=r.metadata,
                    distance=r.distance,
                )
                for r in vector_results[:limit]
            ]

        # Validate against relational store
        return await self._validate_results(vector_results, limit)

    async def _validate_results(
        self,
        vector_results: list[VectorSearchResult],
        limit: int,
    ) -> list[RecallResult]:
        """
        Validate vector results against relational store.

        This implements the Coherency Protocol:
        1. Fetch relational rows for all vector result IDs
        2. Detect ghosts (vector exists, row doesn't)
        3. Detect staleness (content_hash mismatch)
        4. Self-heal ghosts if configured
        """
        if not self._relational_store:
            return [
                RecallResult(id=r.id, data=r.metadata, distance=r.distance)
                for r in vector_results[:limit]
            ]

        # Batch fetch relational rows
        ids = [r.id for r in vector_results]
        id_list = ",".join(f"'{id}'" for id in ids)
        query = f"""
            SELECT * FROM {self._config.table}
            WHERE {self._config.id_column} IN ({id_list})
        """

        rows = await self._relational_store.fetch_all(query)
        row_map = {row[self._config.id_column]: row for row in rows}

        results = []
        for vec_result in vector_results:
            metadata = VectorMetadata.from_dict(vec_result.metadata)
            row = row_map.get(vec_result.id)

            if row is None:
                # Ghost Memory: Vector exists, row doesn't
                if self._config.auto_heal_ghosts:
                    await self._heal_ghost(vec_result.id)
                    self._ghosts_healed += 1
                continue  # Skip ghost

            # Check staleness
            is_stale = False
            if self._config.flag_stale_on_recall:
                current_hash = ContentHash.compute(row).hash_value
                if current_hash != metadata.content_hash:
                    is_stale = True
                    self._stale_flagged += 1

            results.append(
                RecallResult(
                    id=vec_result.id,
                    data=row,
                    distance=vec_result.distance,
                    is_stale=is_stale,
                )
            )

            if len(results) >= limit:
                break

        return results

    async def _heal_ghost(self, ghost_id: str) -> bool:
        """
        Remove orphaned vector entry (self-healing).

        Called when vector entry points to non-existent relational row.

        Args:
            ghost_id: ID of the ghost vector

        Returns:
            True if healed, False if failed
        """
        return await self._vector_store.delete(ghost_id)

    async def delete(self, id: str) -> bool:
        """Delete vector by ID."""
        return await self._vector_store.delete(id)

    async def count(self) -> int:
        """Return total vector count."""
        return await self._vector_store.count()

    def stats(self) -> dict[str, Any]:
        """Get backend statistics."""
        return {
            "ghosts_healed": self._ghosts_healed,
            "stale_flagged": self._stale_flagged,
            "config": {
                "table": self._config.table,
                "auto_heal_ghosts": self._config.auto_heal_ghosts,
                "flag_stale_on_recall": self._config.flag_stale_on_recall,
            },
        }


@dataclass
class InstanceDBRelationalBackendConfig:
    """Configuration for InstanceDBRelationalBackend."""

    # Default table for state storage
    default_table: str = "d_gent_state"

    # State key column
    key_column: str = "key"

    # State data column (JSON)
    state_column: str = "state"

    # Version tracking
    enable_versioning: bool = True
    version_column: str = "version"

    # History
    max_history: int = 100


class InstanceDBRelationalBackend(Generic[S], DataAgent[S]):
    """
    Wraps IRelationalStore as a D-gent DataAgent.

    This adapter provides:
    - DataAgent[S] interface over IRelationalStore
    - Versioned state storage
    - History tracking
    - JSON serialization for state

    Usage:
        backend = InstanceDBRelationalBackend(relational_store, "my-agent", dict)
        await backend.save({"count": 1})
        state = await backend.load()
    """

    def __init__(
        self,
        store: IRelationalStore,
        key: str,
        schema: type[S] | None = None,
        config: InstanceDBRelationalBackendConfig | None = None,
    ):
        """
        Initialize the relational backend.

        Args:
            store: IRelationalStore instance
            key: Unique key for this agent's state
            schema: Type hint for state (for documentation)
            config: Backend configuration
        """
        if not _INSTANCE_DB_AVAILABLE:
            raise ImportError(
                "Instance DB not available. Ensure protocols/cli/instance_db is accessible."
            )

        self._store = store
        self._key = key
        self._schema = schema
        self._config = config or InstanceDBRelationalBackendConfig()
        self._initialized = False

    async def _ensure_table(self) -> None:
        """Create table if it doesn't exist."""
        if self._initialized:
            return

        query = f"""
            CREATE TABLE IF NOT EXISTS {self._config.default_table} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                {self._config.key_column} TEXT NOT NULL,
                {self._config.state_column} TEXT NOT NULL,
                {self._config.version_column} INTEGER NOT NULL DEFAULT 1,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """
        await self._store.execute(query)

        # Create index for fast lookups
        index_query = f"""
            CREATE INDEX IF NOT EXISTS idx_{self._config.default_table}_key
            ON {self._config.default_table} ({self._config.key_column}, {self._config.version_column} DESC)
        """
        await self._store.execute(index_query)
        self._initialized = True

    async def load(self) -> S:
        """
        Load latest state from database.

        Returns:
            Deserialized state

        Raises:
            StateNotFoundError: If no state exists for this key
        """
        await self._ensure_table()

        query = f"""
            SELECT {self._config.state_column}
            FROM {self._config.default_table}
            WHERE {self._config.key_column} = :key
            ORDER BY {self._config.version_column} DESC
            LIMIT 1
        """
        row = await self._store.fetch_one(query, {"key": self._key})

        if not row:
            raise StateNotFoundError(f"No state for key '{self._key}'")

        try:
            return json.loads(row[self._config.state_column])
        except json.JSONDecodeError as e:
            raise StorageError(f"Invalid JSON in database: {e}")

    async def save(self, state: S) -> None:
        """
        Save state to database with versioning.

        Args:
            state: State to persist
        """
        await self._ensure_table()

        now = datetime.now().isoformat()

        # Get next version
        version_query = f"""
            SELECT COALESCE(MAX({self._config.version_column}), 0) + 1 as next_version
            FROM {self._config.default_table}
            WHERE {self._config.key_column} = :key
        """
        version_row = await self._store.fetch_one(version_query, {"key": self._key})
        next_version = version_row["next_version"] if version_row else 1

        # Insert new version
        insert_query = f"""
            INSERT INTO {self._config.default_table}
            ({self._config.key_column}, {self._config.state_column}, {self._config.version_column}, created_at, updated_at)
            VALUES (:key, :state, :version, :created_at, :updated_at)
        """
        await self._store.execute(
            insert_query,
            {
                "key": self._key,
                "state": json.dumps(state, default=str),
                "version": next_version,
                "created_at": now,
                "updated_at": now,
            },
        )

        # Prune old versions
        if self._config.enable_versioning:
            await self._prune_history()

    async def history(self, limit: int | None = None) -> list[S]:
        """
        Load historical states.

        Args:
            limit: Max entries to return (newest first, excludes current)

        Returns:
            List of historical states
        """
        await self._ensure_table()

        effective_limit = (limit or self._config.max_history) + 1
        query = f"""
            SELECT {self._config.state_column}
            FROM {self._config.default_table}
            WHERE {self._config.key_column} = :key
            ORDER BY {self._config.version_column} DESC
            LIMIT :limit
        """
        rows = await self._store.fetch_all(
            query, {"key": self._key, "limit": effective_limit}
        )

        if not rows:
            return []

        # Skip first (current), return rest
        states = []
        for row in rows[1:]:
            try:
                states.append(json.loads(row[self._config.state_column]))
            except json.JSONDecodeError:
                continue

        return states[: limit if limit else self._config.max_history]

    async def _prune_history(self) -> None:
        """Remove old versions exceeding max_history."""
        # Find version threshold
        threshold_query = f"""
            SELECT {self._config.version_column}
            FROM {self._config.default_table}
            WHERE {self._config.key_column} = :key
            ORDER BY {self._config.version_column} DESC
            LIMIT 1 OFFSET :offset
        """
        row = await self._store.fetch_one(
            threshold_query,
            {"key": self._key, "offset": self._config.max_history},
        )

        if row:
            delete_query = f"""
                DELETE FROM {self._config.default_table}
                WHERE {self._config.key_column} = :key
                AND {self._config.version_column} <= :threshold
            """
            await self._store.execute(
                delete_query,
                {"key": self._key, "threshold": row[self._config.version_column]},
            )

    async def exists(self) -> bool:
        """Check if state exists."""
        await self._ensure_table()

        query = f"""
            SELECT 1
            FROM {self._config.default_table}
            WHERE {self._config.key_column} = :key
            LIMIT 1
        """
        row = await self._store.fetch_one(query, {"key": self._key})
        return row is not None

    async def delete(self) -> bool:
        """Delete all state for this key."""
        await self._ensure_table()

        query = f"""
            DELETE FROM {self._config.default_table}
            WHERE {self._config.key_column} = :key
        """
        affected = await self._store.execute(query, {"key": self._key})
        return affected > 0


@dataclass
class CortexAdapterConfig:
    """Configuration for CortexAdapter."""

    # Vector backend config
    vector_config: InstanceDBVectorBackendConfig | None = None

    # Relational backend config
    relational_config: InstanceDBRelationalBackendConfig | None = None

    # Embedding provider
    embedding_provider: IEmbeddingProvider | None = None


class CortexAdapter:
    """
    Unified adapter for Bicameral Memory operations.

    Provides a single interface that coordinates:
    - Left Hemisphere (Relational): Source of truth
    - Right Hemisphere (Vector): Semantic search
    - Coherency Protocol: Cross-hemisphere validation

    This is the integration point for D-gents to use Instance DB.

    Usage:
        adapter = CortexAdapter(
            relational_store=sqlite_store,
            vector_store=numpy_store,
        )

        # Store with embedding
        await adapter.store("shape-001", {"type": "insight", "text": "..."})

        # Semantic recall with coherency
        results = await adapter.recall("similar to insight about X")
    """

    def __init__(
        self,
        relational_store: IRelationalStore,
        vector_store: IVectorStore | None = None,
        config: CortexAdapterConfig | None = None,
    ):
        """
        Initialize the Cortex adapter.

        Args:
            relational_store: Required relational store (Left Hemisphere)
            vector_store: Optional vector store (Right Hemisphere)
            config: Adapter configuration
        """
        if not _INSTANCE_DB_AVAILABLE:
            raise ImportError(
                "Instance DB not available. Ensure protocols/cli/instance_db is accessible."
            )

        self._config = config or CortexAdapterConfig()
        self._relational_store = relational_store

        # Initialize vector backend if available
        self._vector_backend: InstanceDBVectorBackend | None = None
        if vector_store:
            self._vector_backend = InstanceDBVectorBackend(
                vector_store=vector_store,
                relational_store=relational_store,
                config=self._config.vector_config,
            )

        # Embedding provider
        self._embedder = self._config.embedding_provider or NullEmbeddingProvider()

    @property
    def has_semantic(self) -> bool:
        """Check if semantic (vector) operations are available."""
        return self._vector_backend is not None

    def create_agent(
        self,
        key: str,
        schema: type[S] | None = None,
    ) -> InstanceDBRelationalBackend[S]:
        """
        Create a D-gent backed by this cortex.

        Args:
            key: Unique key for the agent's state
            schema: Type hint for state

        Returns:
            InstanceDBRelationalBackend instance
        """
        return InstanceDBRelationalBackend(
            store=self._relational_store,
            key=key,
            schema=schema,
            config=self._config.relational_config,
        )

    async def store(
        self,
        id: str,
        data: dict[str, Any],
        table: str | None = None,
        embed_field: str | None = None,
    ) -> str:
        """
        Store data in both hemispheres.

        Args:
            id: Unique identifier
            data: Data to store
            table: Override table name
            embed_field: Field to use for embedding (default: entire data)

        Returns:
            Stored ID
        """
        table_name = table or (
            self._config.relational_config.default_table
            if self._config.relational_config
            else "shapes"
        )

        # Store in relational (Left Hemisphere)
        now = datetime.now().isoformat()
        query = f"""
            INSERT INTO {table_name} (id, data, created_at, updated_at)
            VALUES (:id, :data, :created_at, :updated_at)
            ON CONFLICT(id) DO UPDATE SET
                data = :data,
                updated_at = :updated_at
        """
        await self._relational_store.execute(
            query,
            {
                "id": id,
                "data": json.dumps(data, default=str),
                "created_at": now,
                "updated_at": now,
            },
        )

        # Store in vector (Right Hemisphere) if available
        if self._vector_backend:
            embed_content = data.get(embed_field) if embed_field else json.dumps(data)
            vector = self._embedder.embed(str(embed_content))
            await self._vector_backend.upsert(
                id=id,
                vector=vector,
                content=data,
                table=table_name,
            )

        return id

    async def recall(
        self,
        query: str,
        limit: int = 10,
        filter: dict[str, Any] | None = None,
    ) -> list[RecallResult]:
        """
        Semantic recall with coherency validation.

        Args:
            query: Text query for semantic search
            limit: Max results
            filter: Metadata filter

        Returns:
            List of RecallResult with coherency info
        """
        if not self._vector_backend:
            raise InfraBackendError("Vector store not configured")

        query_vector = self._embedder.embed(query)
        return await self._vector_backend.search(
            query_vector=query_vector,
            limit=limit,
            filter=filter,
            validate_coherency=True,
        )

    async def fetch(self, id: str, table: str | None = None) -> dict[str, Any] | None:
        """
        Fetch data by ID from relational store.

        Args:
            id: Data ID
            table: Override table name

        Returns:
            Data dict or None if not found
        """
        table_name = table or (
            self._config.relational_config.default_table
            if self._config.relational_config
            else "shapes"
        )

        query = f"SELECT * FROM {table_name} WHERE id = :id"
        row = await self._relational_store.fetch_one(query, {"id": id})

        if not row:
            return None

        # Parse JSON data field if present
        if "data" in row and isinstance(row["data"], str):
            try:
                row["data"] = json.loads(row["data"])
            except json.JSONDecodeError:
                pass

        return row

    async def delete(self, id: str, table: str | None = None) -> bool:
        """
        Delete data from both hemispheres.

        Args:
            id: Data ID
            table: Override table name

        Returns:
            True if deleted
        """
        table_name = table or (
            self._config.relational_config.default_table
            if self._config.relational_config
            else "shapes"
        )

        # Delete from relational
        query = f"DELETE FROM {table_name} WHERE id = :id"
        affected = await self._relational_store.execute(query, {"id": id})

        # Delete from vector if available
        if self._vector_backend:
            await self._vector_backend.delete(id)

        return affected > 0

    def stats(self) -> dict[str, Any]:
        """Get adapter statistics."""
        return {
            "has_semantic": self.has_semantic,
            "vector_stats": self._vector_backend.stats()
            if self._vector_backend
            else None,
        }


# Factory functions


def create_vector_backend(
    vector_store: IVectorStore,
    relational_store: IRelationalStore | None = None,
    **config_kwargs,
) -> InstanceDBVectorBackend:
    """
    Create an InstanceDBVectorBackend.

    Args:
        vector_store: IVectorStore instance
        relational_store: Optional IRelationalStore for coherency
        **config_kwargs: InstanceDBVectorBackendConfig parameters

    Returns:
        Configured InstanceDBVectorBackend
    """
    config = InstanceDBVectorBackendConfig(**config_kwargs)
    return InstanceDBVectorBackend(
        vector_store=vector_store,
        relational_store=relational_store,
        config=config,
    )


def create_relational_backend(
    store: IRelationalStore,
    key: str,
    schema: type[S] | None = None,
    **config_kwargs,
) -> InstanceDBRelationalBackend[S]:
    """
    Create an InstanceDBRelationalBackend.

    Args:
        store: IRelationalStore instance
        key: Unique key for state
        schema: Type hint for state
        **config_kwargs: InstanceDBRelationalBackendConfig parameters

    Returns:
        Configured InstanceDBRelationalBackend
    """
    config = InstanceDBRelationalBackendConfig(**config_kwargs)
    return InstanceDBRelationalBackend(
        store=store,
        key=key,
        schema=schema,
        config=config,
    )


def create_cortex_adapter(
    relational_store: IRelationalStore,
    vector_store: IVectorStore | None = None,
    embedding_provider: IEmbeddingProvider | None = None,
) -> CortexAdapter:
    """
    Create a CortexAdapter for Bicameral Memory operations.

    Args:
        relational_store: Required relational store
        vector_store: Optional vector store
        embedding_provider: Optional embedding provider

    Returns:
        Configured CortexAdapter
    """
    config = CortexAdapterConfig(embedding_provider=embedding_provider)
    return CortexAdapter(
        relational_store=relational_store,
        vector_store=vector_store,
        config=config,
    )
