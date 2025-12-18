"""
L-gent Persistence Layer - D-gent Integration

Provides durable storage for L-gent catalogs using the NEW D-gent architecture.

Uses:
- DgentRouter: Auto-selects best backend (SQLite by default)
- Datum: Schema-free bytes with causal linking for history
- causal_chain: Replaces old history() method

Key Features:
- PersistentRegistry: Wraps Registry with D-gent storage
- Auto-save on modifications (configurable)
- History tracking via causal chain
- Backend flexibility (Memory → JSONL → SQLite → Postgres)

Usage:
    >>> from agents.l import PersistentRegistry
    >>> from pathlib import Path
    >>>
    >>> # Create persistent registry
    >>> registry = await PersistentRegistry.create(
    ...     namespace="catalog",
    ...     auto_save=True,
    ... )
    >>>
    >>> # Use exactly like in-memory Registry
    >>> await registry.register(entry)
    >>> results = await registry.find(query="calendar")
    >>>
    >>> # Explicit save/load available
    >>> await registry.save()
    >>> await registry.reload()
"""

from __future__ import annotations

import builtins
import json
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any

# New D-gent imports
from agents.d import (
    Datum,
    DgentRouter,
    StateNotFoundError,
)
from agents.d.router import Backend

from .registry import Registry
from .types import (
    Catalog,
    CatalogEntry,
    EntityType,
    SearchResult,
    Status,
)

# Well-known ID for the catalog datum
CATALOG_DATUM_ID = "lgent_catalog_current"


class SaveStrategy(Enum):
    """When to persist catalog changes."""

    MANUAL = "manual"  # Only save when explicitly called
    ON_WRITE = "on_write"  # Save after each modification (register, delete, update)
    PERIODIC = "periodic"  # Save at intervals (requires external scheduler)
    ON_EXIT = "on_exit"  # Save when close() is called


@dataclass
class PersistenceConfig:
    """Configuration for persistent registry behavior."""

    save_strategy: SaveStrategy = SaveStrategy.ON_WRITE
    max_history: int = 50  # Max catalog snapshots in history
    create_if_missing: bool = True  # Create new catalog if file doesn't exist
    validate_on_load: bool = True  # Validate entries on load
    backup_on_save: bool = False  # Create .bak file before save


class PersistentRegistry:
    """
    L-gent Registry with D-gent persistence.

    Uses the NEW D-gent architecture:
    - DgentRouter for backend selection (SQLite by default)
    - Datum for storage (catalog serialized as JSON bytes)
    - causal_chain for history tracking

    The architecture follows the Symbiont pattern:
    - Logic: Registry (in-memory operations)
    - Memory: DgentRouter (projection-agnostic storage)

    Example:
        >>> registry = await PersistentRegistry.create(
        ...     namespace="my_catalog",
        ...     config=PersistenceConfig(save_strategy=SaveStrategy.ON_WRITE),
        ... )
        >>>
        >>> # All Registry methods work identically
        >>> await registry.register(entry)  # Auto-saves if ON_WRITE
        >>> results = await registry.find(query="calendar")
        >>>
        >>> # Explicit persistence control
        >>> await registry.save()  # Force save
        >>> await registry.reload()  # Reload from storage
        >>> history = await registry.catalog_history(limit=5)  # View past states
    """

    def __init__(
        self,
        registry: Registry,
        storage: DgentRouter,
        config: PersistenceConfig,
        namespace: str,
        current_datum_id: str | None = None,
    ) -> None:
        """
        Initialize persistent registry.

        Note: Use PersistentRegistry.create() factory method instead.
        """
        self._registry = registry
        self._storage = storage
        self._config = config
        self._namespace = namespace
        self._current_datum_id = current_datum_id
        self._dirty = False  # Track unsaved changes

    @classmethod
    async def create(
        cls,
        namespace: str = "lgent_catalog",
        config: PersistenceConfig | None = None,
        data_dir: Path | None = None,
        preferred_backend: Backend = Backend.SQLITE,
    ) -> "PersistentRegistry":
        """
        Factory method to create a persistent registry.

        Loads existing catalog from storage, or creates new one if missing.

        Args:
            namespace: Namespace for the D-gent storage
            config: Persistence configuration (defaults to ON_WRITE auto-save)
            data_dir: Directory for data files (defaults to ~/.kgents/data)
            preferred_backend: Preferred storage backend (defaults to SQLite)

        Returns:
            Initialized PersistentRegistry

        Example:
            >>> registry = await PersistentRegistry.create(
            ...     namespace="catalog",
            ... )
        """
        config = config or PersistenceConfig()

        # Create D-gent router with SQLite as preferred backend
        storage = DgentRouter(
            namespace=namespace,
            preferred=preferred_backend,
            data_dir=data_dir,
        )

        # Try to load existing catalog
        current_datum_id = None
        try:
            # Get the most recent datum
            recent = await storage.list(limit=1)
            if recent:
                current_datum_id = recent[0].id
                data = json.loads(recent[0].content.decode("utf-8"))
                catalog = Catalog.from_dict(data)
                registry = Registry(catalog=catalog)
            else:
                if config.create_if_missing:
                    registry = Registry()
                else:
                    raise StateNotFoundError(f"No catalog found in namespace {namespace}")
        except Exception as e:
            if config.create_if_missing:
                registry = Registry()
            else:
                raise StateNotFoundError(f"Failed to load catalog: {e}")

        return cls(
            registry=registry,
            storage=storage,
            config=config,
            namespace=namespace,
            current_datum_id=current_datum_id,
        )

    # ========== Persistence Operations ==========

    async def save(self) -> None:
        """
        Persist current catalog state to storage.

        Creates a new Datum with the current state, linked to the previous
        state via causal_parent for history tracking.
        """
        data = self._registry.catalog.to_dict()
        content = json.dumps(data, default=str).encode("utf-8")

        # Create datum with causal link to previous state
        datum = Datum.create(
            content=content,
            causal_parent=self._current_datum_id,
            metadata={"type": "lgent_catalog", "namespace": self._namespace},
        )

        await self._storage.put(datum)
        self._current_datum_id = datum.id
        self._dirty = False

    async def reload(self) -> None:
        """
        Reload catalog from storage, discarding in-memory changes.

        Useful after external catalog modifications or to reset state.
        """
        recent = await self._storage.list(limit=1)
        if recent:
            self._current_datum_id = recent[0].id
            data = json.loads(recent[0].content.decode("utf-8"))
            catalog = Catalog.from_dict(data)
            self._registry = Registry(catalog=catalog)
        else:
            self._registry = Registry()
            self._current_datum_id = None
        self._dirty = False

    async def catalog_history(self, limit: int | None = None) -> builtins.list[Catalog]:
        """
        Retrieve historical catalog states via causal chain.

        Uses D-gent's causal_chain to trace the evolution of the catalog.

        Args:
            limit: Maximum number of historical states to return

        Returns:
            List of Catalog snapshots, oldest to newest
        """
        if self._current_datum_id is None:
            return []

        chain = await self._storage.causal_chain(self._current_datum_id)
        catalogs = []

        for datum in chain:
            try:
                data = json.loads(datum.content.decode("utf-8"))
                catalogs.append(Catalog.from_dict(data))
            except (json.JSONDecodeError, KeyError):
                continue  # Skip malformed entries

        if limit is not None:
            catalogs = catalogs[-limit:]

        return catalogs

    async def close(self) -> None:
        """
        Close registry, saving if dirty and strategy permits.

        Call this when done with the registry to ensure data is persisted.
        """
        if self._dirty and self._config.save_strategy == SaveStrategy.ON_EXIT:
            await self.save()

    async def _maybe_save(self) -> None:
        """Auto-save if configured for ON_WRITE strategy."""
        if self._config.save_strategy == SaveStrategy.ON_WRITE:
            await self.save()
        else:
            self._dirty = True

    # ========== Delegated Registry Operations ==========
    # All methods delegate to the wrapped Registry, with auto-save for writes

    async def register(self, entry: CatalogEntry) -> str:
        """
        Add or update an artifact in the registry.

        See Registry.register() for full documentation.
        """
        result = await self._registry.register(entry)
        await self._maybe_save()
        return result

    async def get(self, id: str) -> CatalogEntry | None:
        """Retrieve entry by ID. See Registry.get()."""
        return await self._registry.get(id)

    async def exists(self, id: str) -> bool:
        """Check existence without retrieving. See Registry.exists()."""
        return await self._registry.exists(id)

    async def list(
        self,
        entity_type: EntityType | None = None,
        status: Status | None = None,
        author: str | None = None,
        limit: int | None = None,
    ) -> builtins.list[CatalogEntry]:
        """List entries with optional filters. See Registry.list_entries()."""
        return await self._registry.list_entries(
            entity_type=entity_type,
            status=status,
            author=author,
            limit=limit,
        )

    async def find(
        self,
        query: str | None = None,
        entity_type: EntityType | None = None,
        keywords: builtins.list[str] | None = None,
        limit: int = 10,
    ) -> builtins.list[SearchResult]:
        """Search for entries. See Registry.find()."""
        return await self._registry.find(
            query=query,
            entity_type=entity_type,
            keywords=keywords,
            limit=limit,
        )

    async def delete(self, id: str) -> bool:
        """Remove entry from registry. See Registry.delete()."""
        result = await self._registry.delete(id)
        if result:
            await self._maybe_save()
        return result

    async def update_usage(
        self,
        id: str,
        success: bool = True,
        error: str | None = None,
    ) -> None:
        """Update usage metrics for an entry. See Registry.update_usage()."""
        await self._registry.update_usage(id, success=success, error=error)
        await self._maybe_save()

    async def deprecate(
        self,
        id: str,
        reason: str,
        successor_id: str | None = None,
    ) -> bool:
        """Mark an entry as deprecated. See Registry.deprecate()."""
        result = await self._registry.deprecate(id, reason, successor_id)
        if result:
            await self._maybe_save()
        return result

    async def add_relationship(
        self,
        source_id: str,
        target_id: str,
        relationship_type: str,
    ) -> bool:
        """Add a relationship between entries. See Registry.add_relationship()."""
        result = await self._registry.add_relationship(source_id, target_id, relationship_type)
        if result:
            await self._maybe_save()
        return result

    async def find_related(
        self,
        id: str,
        relationship_type: str,
    ) -> builtins.list[CatalogEntry]:
        """Find entries related to a given entry. See Registry.find_related()."""
        return await self._registry.find_related(id, relationship_type)

    # ========== Properties ==========

    @property
    def catalog(self) -> Catalog:
        """Access the underlying catalog (read-only view)."""
        return self._registry.catalog

    @property
    def namespace(self) -> str:
        """Namespace for this registry's storage."""
        return self._namespace

    @property
    def is_dirty(self) -> bool:
        """Whether there are unsaved changes."""
        return self._dirty

    @property
    def config(self) -> PersistenceConfig:
        """Current persistence configuration."""
        return self._config

    @property
    def current_datum_id(self) -> str | None:
        """ID of the current catalog datum (for causal linking)."""
        return self._current_datum_id

    def to_dict(self) -> dict[str, Any]:
        """Export catalog as dictionary."""
        return self._registry.to_dict()


# ========== Convenience Functions ==========


async def create_persistent_registry(
    namespace: str = "lgent_catalog",
    auto_save: bool = True,
    max_history: int = 50,
    data_dir: Path | None = None,
) -> PersistentRegistry:
    """
    Create a persistent registry with sensible defaults.

    Convenience wrapper around PersistentRegistry.create().

    Args:
        namespace: Namespace for D-gent storage
        auto_save: If True, save after each modification (default)
        max_history: Number of historical catalog states to keep
        data_dir: Directory for data files

    Returns:
        Initialized PersistentRegistry

    Example:
        >>> registry = await create_persistent_registry("my_catalog")
        >>> await registry.register(entry)  # Auto-saved
    """
    config = PersistenceConfig(
        save_strategy=SaveStrategy.ON_WRITE if auto_save else SaveStrategy.MANUAL,
        max_history=max_history,
    )
    return await PersistentRegistry.create(
        namespace=namespace,
        config=config,
        data_dir=data_dir,
    )


async def load_or_create_registry(
    namespace: str = "lgent_catalog",
    auto_save: bool = True,
    data_dir: Path | None = None,
) -> PersistentRegistry:
    """
    Load existing registry or create new one.

    This is the recommended way to initialize a persistent registry
    in most applications.

    Args:
        namespace: Namespace for D-gent storage
        auto_save: If True, save after each modification
        data_dir: Directory for data files

    Returns:
        PersistentRegistry (existing or newly created)
    """
    return await create_persistent_registry(
        namespace=namespace,
        auto_save=auto_save,
        data_dir=data_dir,
    )
