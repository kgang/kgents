"""
Universe: D-gent's unified data management domain.

Philosophy:
    "Agents don't think about storage. They think about data.
     The Universe handles the rest."

The Universe is a higher-level abstraction over DgentProtocol that provides:
- Automatic backend selection (Postgres > SQLite > Memory)
- Schema registry for typed data (Crystal, Mark, etc.)
- Graceful degradation when backends unavailable
- Unified interface for both Datum (schema-free) and typed objects

Design:
    Universe wraps DgentRouter and extends it with schema awareness.
    It knows how to serialize/deserialize typed objects (Crystal, etc.)
    but still stores everything as Datum underneath.

    Schema-free Datum → store_datum() → DgentRouter
    Typed objects → store() → serialize → Datum → DgentRouter

Teaching:
    gotcha: Universe is NOT a replacement for DgentRouter
            It's a convenience layer for services that work with typed data.
            Low-level code should still use DgentRouter directly.

    gotcha: Schemas are serialization helpers, not enforcement
            D-gent remains schema-free at the Datum level.
            Schemas only matter at the Universe boundary.

    gotcha: Backend selection happens at Universe init, not per-operation
            Once initialized, the backend is fixed for that Universe instance.
            Create a new Universe if you need a different backend.

See: spec/agents/d-gent.md
See: docs/skills/unified-storage.md
"""

from __future__ import annotations

import asyncio
import json
import logging
from dataclasses import dataclass
from typing import Any, Callable, Generic, Protocol, TypeVar, cast

from ..backends import MemoryBackend, SQLiteBackend
from ..datum import Datum
from ..protocol import DgentProtocol

# PostgresBackend is optional - use new wrapper with URL normalization
try:
    from .backends.postgres import PostgresBackend
except ImportError:
    PostgresBackend = None  # type: ignore

logger = logging.getLogger(__name__)

# =============================================================================
# Type Variables
# =============================================================================

T = TypeVar("T")  # Generic type for typed objects

# =============================================================================
# Schema Protocol
# =============================================================================


class Schema(Protocol[T]):
    """
    Schema defines serialization/deserialization for typed objects.

    A Schema is just a pair of functions:
    - serialize: T → dict[str, Any]
    - deserialize: dict[str, Any] → T

    This allows Universe to store typed objects as Datum.
    """

    name: str  # Schema name for registry lookup

    def serialize(self, obj: T) -> dict[str, Any]:
        """Convert typed object to JSON-serializable dict."""
        ...

    def deserialize(self, data: dict[str, Any]) -> T:
        """Convert dict back to typed object."""
        ...


@dataclass
class DataclassSchema(Generic[T]):
    """
    Schema implementation for dataclasses with to_dict/from_dict methods.

    Works with types like Crystal, Mark, etc. that follow this pattern.
    """

    name: str
    type_cls: type[T]

    def serialize(self, obj: T) -> dict[str, Any]:
        """Use to_dict() if available, else __dict__."""
        if hasattr(obj, "to_dict"):
            return obj.to_dict()  # type: ignore
        elif hasattr(obj, "__dict__"):
            return obj.__dict__
        else:
            raise TypeError(f"Cannot serialize {type(obj).__name__}")

    def deserialize(self, data: dict[str, Any]) -> T:
        """Use from_dict() if available, else direct construction."""
        if hasattr(self.type_cls, "from_dict"):
            return self.type_cls.from_dict(data)  # type: ignore
        else:
            return self.type_cls(**data)


# =============================================================================
# Query Protocol
# =============================================================================


@dataclass
class Query:
    """
    Query for filtering stored data.

    Maps to DgentProtocol.list() parameters:
    - prefix: Filter by ID prefix
    - after: Filter by timestamp
    - limit: Maximum results
    - schema: Filter by schema type (via metadata tag)
    """

    prefix: str | None = None
    after: float | None = None
    limit: int = 100
    schema: str | None = None  # Filter by schema metadata tag


# =============================================================================
# Backend Enum
# =============================================================================


class Backend:
    """Backend tier enumeration for Universe selection."""

    MEMORY = "memory"
    SQLITE = "sqlite"
    POSTGRES = "postgres"
    AUTO = "auto"  # Auto-select best available


# =============================================================================
# Universe Stats
# =============================================================================


@dataclass
class UniverseStats:
    """Statistics about Universe state."""

    backend: str  # Which backend is active
    total_data: int  # Total datum count
    schemas_registered: int  # Number of schemas
    namespace: str  # Current namespace


# =============================================================================
# Universe: The Unified Data Manager
# =============================================================================


class Universe:
    """
    D-gent's domain. Manages all data across all backends.

    Agents don't think about storage. They think about data.
    The Universe handles the rest.

    Architecture:
        Universe wraps DgentRouter and adds schema awareness.
        Everything is still stored as Datum underneath.

    Usage:
        >>> universe = await init_universe()
        >>> crystal = Crystal(...)
        >>> crystal_id = await universe.store(crystal)
        >>> retrieved = await universe.get(crystal_id)  # Returns Crystal
    """

    def __init__(
        self,
        namespace: str = "default",
        preferred_backend: str = Backend.AUTO,
    ):
        """
        Create Universe instance.

        Args:
            namespace: Namespace for data isolation
            preferred_backend: Preferred backend tier (auto-selects if unavailable)
        """
        self._namespace = namespace
        self._preferred = preferred_backend
        self._active_backend: DgentProtocol | None = None
        self._schemas: dict[str, Schema[Any]] = {}
        self._type_to_schema: dict[type, str] = {}
        self._initialized = False

    async def _ensure_initialized(self) -> None:
        """Lazy initialization of backend."""
        if self._initialized:
            return

        # Select and initialize backend directly
        self._active_backend = await self._select_backend()
        self._initialized = True

        logger.info(
            f"Universe initialized: backend={self._backend_name()}, namespace={self._namespace}"
        )

    async def _select_backend(self) -> DgentProtocol:
        """
        Auto-select best available backend.

        Tier preference: Postgres > SQLite > Memory
        Graceful fallback if preferred unavailable.
        """
        backend: DgentProtocol

        # If explicitly requesting memory, use it directly
        if self._preferred == Backend.MEMORY:
            logger.info("Using Memory backend (explicit)")
            return MemoryBackend()

        if self._preferred == Backend.POSTGRES or self._preferred == Backend.AUTO:
            try:
                if PostgresBackend is not None:
                    # Try to connect to Postgres
                    import os

                    url = os.getenv("KGENTS_DATABASE_URL")
                    if url and "postgresql" in url:
                        backend = PostgresBackend(url)
                        # Test connection
                        await backend.count()
                        logger.info("Selected Postgres backend")
                        return backend
            except Exception as e:
                logger.warning(f"Postgres unavailable: {e}")

        if self._preferred == Backend.SQLITE or self._preferred == Backend.AUTO:
            try:
                from pathlib import Path

                # XDG-compliant path
                data_home = Path.home() / ".local" / "share" / "kgents"
                data_home.mkdir(parents=True, exist_ok=True)
                db_path = data_home / f"{self._namespace}.db"

                backend = SQLiteBackend(str(db_path))
                await backend.count()  # Test initialization
                logger.info(f"Selected SQLite backend: {db_path}")
                return backend
            except Exception as e:
                logger.warning(f"SQLite unavailable: {e}")

        # Fallback to memory
        logger.info("Falling back to Memory backend")
        return MemoryBackend()

    def _backend_name(self) -> str:
        """Get current backend name."""
        if self._active_backend is None:
            return "uninitialized"
        backend_type = type(self._active_backend).__name__
        return backend_type.replace("Backend", "").lower()

    # -------------------------------------------------------------------------
    # Schema Registry
    # -------------------------------------------------------------------------

    def register_schema(self, schema: Schema[T]) -> None:
        """
        Register a schema for typed objects.

        Args:
            schema: Schema defining serialization for type T
        """
        self._schemas[schema.name] = schema
        logger.debug(f"Registered schema: {schema.name}")

    def register_type(self, name: str, type_cls: type[T]) -> None:
        """
        Convenience method to register dataclass type.

        Args:
            name: Schema name
            type_cls: Type with to_dict/from_dict methods
        """
        schema = DataclassSchema(name=name, type_cls=type_cls)
        self.register_schema(schema)
        self._type_to_schema[type_cls] = name

    def schema_for(self, name: str) -> Schema[Any] | None:
        """Get schema by name."""
        return self._schemas.get(name)

    def schema_for_type(self, cls: type) -> Schema[Any] | None:
        """Get schema for a type."""
        schema_name = self._type_to_schema.get(cls)
        if schema_name:
            return self._schemas.get(schema_name)
        return None

    # -------------------------------------------------------------------------
    # Core Operations
    # -------------------------------------------------------------------------

    async def store(self, obj: T, schema_name: str | None = None) -> str:
        """
        Store a typed object.

        Args:
            obj: The object to store (Crystal, Mark, etc.)
            schema_name: Optional schema name (auto-detected if registered)

        Returns:
            The datum ID
        """
        await self._ensure_initialized()

        # Find schema
        if schema_name is None:
            schema = self.schema_for_type(type(obj))
            if schema is None:
                raise ValueError(f"No schema registered for {type(obj).__name__}")
        else:
            schema = self.schema_for(schema_name)
            if schema is None:
                raise ValueError(f"Schema not found: {schema_name}")

        # Serialize to dict
        data = schema.serialize(obj)

        # Add schema metadata
        datum = Datum.create(
            content=json.dumps(data).encode("utf-8"),
            metadata={"schema": schema.name},
        )

        # Store via backend
        assert self._active_backend is not None
        return await self._active_backend.put(datum)

    async def store_datum(self, datum: Datum) -> str:
        """
        Store a raw Datum (schema-free path).

        Args:
            datum: The datum to store

        Returns:
            The datum ID
        """
        await self._ensure_initialized()
        assert self._active_backend is not None
        return await self._active_backend.put(datum)

    async def get(self, id: str) -> Any | None:
        """
        Retrieve data by ID.

        Returns Crystal/Mark/etc. if schema known, Datum if unknown.

        Args:
            id: The datum ID

        Returns:
            Typed object if schema known, Datum if unknown, None if not found
        """
        await self._ensure_initialized()
        assert self._active_backend is not None

        datum = await self._active_backend.get(id)
        if datum is None:
            return None

        # Check for schema metadata
        schema_name = datum.metadata.get("schema")
        if schema_name:
            schema = self.schema_for(schema_name)
            if schema:
                # Deserialize to typed object
                data = json.loads(datum.content.decode("utf-8"))
                # Inject datum metadata into context for Crystal lookup
                if "context" in data or hasattr(schema, "contract"):
                    context = data.get("context", {})
                    if isinstance(context, dict):
                        context = {
                            **context,
                            "id": datum.id,
                            "created_at": datum.created_at,
                        }
                        data["context"] = context
                return schema.deserialize(data)

        # Return raw datum if no schema
        return datum

    async def query(self, q: Query) -> list[Any]:
        """
        Query for data matching filters.

        Args:
            q: Query filters

        Returns:
            List of matching objects (typed or Datum)
        """
        await self._ensure_initialized()
        assert self._active_backend is not None

        # Map Query to list() parameters
        data = await self._active_backend.list(
            prefix=q.prefix,
            after=q.after,
            limit=q.limit,
        )

        # Filter by schema if specified
        if q.schema:
            data = [d for d in data if d.metadata.get("schema") == q.schema]

        # Deserialize each datum
        results = []
        for datum in data:
            schema_name = datum.metadata.get("schema")
            if schema_name:
                schema = self.schema_for(schema_name)
                if schema:
                    obj_data = json.loads(datum.content.decode("utf-8"))
                    # Inject datum metadata into context for Crystal lookup
                    # This preserves id and created_at for adapters to use
                    if "context" in obj_data or hasattr(schema, "contract"):
                        context = obj_data.get("context", {})
                        if isinstance(context, dict):
                            context = {
                                **context,
                                "id": datum.id,
                                "created_at": datum.created_at,
                            }
                            obj_data["context"] = context
                    results.append(schema.deserialize(obj_data))
                    continue
            # Fallback to raw datum
            results.append(datum)

        return results

    async def delete(self, id: str) -> bool:
        """
        Delete data by ID.

        Args:
            id: The datum ID

        Returns:
            True if deleted, False if not found
        """
        await self._ensure_initialized()
        assert self._active_backend is not None
        return await self._active_backend.delete(id)

    # -------------------------------------------------------------------------
    # Convenience Methods
    # -------------------------------------------------------------------------

    async def remember(self, value: T, schema_name: str | None = None, **meta: str) -> T:
        """
        Store and return the object (fluent API).

        Args:
            value: Object to store
            schema_name: Optional schema name
            **meta: Additional metadata tags

        Returns:
            The same object (for chaining)
        """
        await self.store(value, schema_name)
        return value

    async def recall(self, schema: str, **filters: Any) -> list[Any]:
        """
        Recall objects by schema and filters.

        Args:
            schema: Schema name to filter
            **filters: Additional filter kwargs (mapped to Query)

        Returns:
            List of matching objects
        """
        q = Query(
            schema=schema,
            limit=filters.get("limit", 100),
            prefix=filters.get("prefix"),
            after=filters.get("after"),
        )
        return await self.query(q)

    # -------------------------------------------------------------------------
    # Stats
    # -------------------------------------------------------------------------

    async def stats(self) -> UniverseStats:
        """Get Universe statistics."""
        await self._ensure_initialized()
        assert self._active_backend is not None

        total = await self._active_backend.count()

        return UniverseStats(
            backend=self._backend_name(),
            total_data=total,
            schemas_registered=len(self._schemas),
            namespace=self._namespace,
        )


# =============================================================================
# Singleton Access
# =============================================================================

_universe: Universe | None = None
_lock = asyncio.Lock()


def get_universe() -> Universe:
    """
    Get the singleton Universe instance.

    Note: This returns an uninitialized Universe. You must await operations
    which will trigger lazy initialization.

    Usage:
        >>> universe = get_universe()
        >>> await universe.store(crystal)  # Triggers init on first operation
    """
    global _universe
    if _universe is None:
        _universe = Universe()
    return _universe


async def init_universe(
    backend: str = Backend.AUTO,
    namespace: str = "default",
) -> Universe:
    """
    Initialize Universe with explicit backend selection.

    Args:
        backend: Backend tier (auto, postgres, sqlite, memory)
        namespace: Namespace for data isolation

    Returns:
        Initialized Universe instance

    Usage:
        >>> universe = await init_universe(backend="postgres")
        >>> await universe.store(crystal)
    """
    global _universe
    async with _lock:
        if _universe is None:
            _universe = Universe(namespace=namespace, preferred_backend=backend)
        await _universe._ensure_initialized()
        return _universe


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    "Universe",
    "Schema",
    "DataclassSchema",
    "Query",
    "Backend",
    "UniverseStats",
    "get_universe",
    "init_universe",
]
