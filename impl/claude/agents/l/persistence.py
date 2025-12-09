"""
L-gent Persistence Layer - D-gent Integration

Provides durable storage for L-gent catalogs using D-gent primitives.

The integration follows the spec:
  "L-gent uses D-gents for persistence:
   - PersistentAgent: Store the catalog itself"

Key Features:
- PersistentRegistry: Wraps Registry with file-backed storage
- Auto-save on modifications (configurable)
- History tracking for catalog evolution
- Crash recovery via atomic writes
- Symbiont-style composition (logic + memory separation)

Usage:
    >>> from agents.l import PersistentRegistry
    >>> from pathlib import Path
    >>>
    >>> # Create persistent registry
    >>> registry = await PersistentRegistry.create(
    ...     path=Path("catalog.json"),
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

from dataclasses import dataclass
from enum import Enum
from pathlib import Path

from .registry import Registry
from .types import (
    Catalog,
    CatalogEntry,
    EntityType,
    SearchResult,
    Status,
)

# Import D-gent primitives
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from agents.d import PersistentAgent, StateNotFoundError


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

    Wraps the in-memory Registry with PersistentAgent[Catalog] for durable storage.
    All Registry methods are available, with automatic or manual persistence.

    The architecture follows the Symbiont pattern:
    - Logic: Registry (in-memory operations)
    - Memory: PersistentAgent[Catalog] (file-backed state)

    This separation allows:
    - Testing logic without disk I/O
    - Swapping storage backends (file → database → cloud)
    - Composing with other D-gents (caching, entropy limits)

    Example:
        >>> registry = await PersistentRegistry.create(
        ...     path=Path("./data/catalog.json"),
        ...     config=PersistenceConfig(save_strategy=SaveStrategy.ON_WRITE),
        ... )
        >>>
        >>> # All Registry methods work identically
        >>> await registry.register(entry)  # Auto-saves if ON_WRITE
        >>> results = await registry.find(query="calendar")
        >>>
        >>> # Explicit persistence control
        >>> await registry.save()  # Force save
        >>> await registry.reload()  # Reload from disk
        >>> history = await registry.catalog_history(limit=5)  # View past states
    """

    def __init__(
        self,
        registry: Registry,
        storage: PersistentAgent,
        config: PersistenceConfig,
        path: Path,
    ):
        """
        Initialize persistent registry.

        Note: Use PersistentRegistry.create() factory method instead.
        """
        self._registry = registry
        self._storage = storage
        self._config = config
        self._path = path
        self._dirty = False  # Track unsaved changes

    @classmethod
    async def create(
        cls,
        path: Path | str,
        config: PersistenceConfig | None = None,
    ) -> "PersistentRegistry":
        """
        Factory method to create a persistent registry.

        Loads existing catalog from disk, or creates new one if missing.

        Args:
            path: Path to catalog JSON file
            config: Persistence configuration (defaults to ON_WRITE auto-save)

        Returns:
            Initialized PersistentRegistry

        Example:
            >>> registry = await PersistentRegistry.create(
            ...     path=Path("catalog.json"),
            ... )
        """
        config = config or PersistenceConfig()
        path = Path(path)

        # Create D-gent storage (using Catalog as schema)
        storage = PersistentAgent(
            path=path,
            schema=dict,  # We serialize Catalog to dict
            max_history=config.max_history,
        )

        # Try to load existing catalog
        try:
            data = await storage.load()
            catalog = Catalog.from_dict(data)
            registry = Registry(catalog=catalog)
        except StateNotFoundError:
            if config.create_if_missing:
                # Create fresh registry
                registry = Registry()
            else:
                raise FileNotFoundError(f"Catalog not found at {path}")

        return cls(
            registry=registry,
            storage=storage,
            config=config,
            path=path,
        )

    # ========== Persistence Operations ==========

    async def save(self) -> None:
        """
        Persist current catalog state to disk.

        Uses atomic writes (temp file + rename) for crash safety.
        Appends to history for evolution tracking.
        """
        data = self._registry.catalog.to_dict()
        await self._storage.save(data)
        self._dirty = False

    async def reload(self) -> None:
        """
        Reload catalog from disk, discarding in-memory changes.

        Useful after external catalog modifications or to reset state.
        """
        data = await self._storage.load()
        catalog = Catalog.from_dict(data)
        self._registry = Registry(catalog=catalog)
        self._dirty = False

    async def catalog_history(self, limit: int | None = None) -> list[Catalog]:
        """
        Retrieve historical catalog states.

        D-gent's PersistentAgent maintains JSONL history of all saves.

        Args:
            limit: Maximum number of historical states to return

        Returns:
            List of Catalog snapshots, newest first
        """
        history_data = await self._storage.history(limit=limit)
        return [Catalog.from_dict(data) for data in history_data]

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
    ) -> list[CatalogEntry]:
        """List entries with optional filters. See Registry.list()."""
        return await self._registry.list(
            entity_type=entity_type,
            status=status,
            author=author,
            limit=limit,
        )

    async def find(
        self,
        query: str | None = None,
        entity_type: EntityType | None = None,
        keywords: list[str] | None = None,
        limit: int = 10,
    ) -> list[SearchResult]:
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
        result = await self._registry.add_relationship(
            source_id, target_id, relationship_type
        )
        if result:
            await self._maybe_save()
        return result

    async def find_related(
        self,
        id: str,
        relationship_type: str,
    ) -> list[CatalogEntry]:
        """Find entries related to a given entry. See Registry.find_related()."""
        return await self._registry.find_related(id, relationship_type)

    # ========== Properties ==========

    @property
    def catalog(self) -> Catalog:
        """Access the underlying catalog (read-only view)."""
        return self._registry.catalog

    @property
    def path(self) -> Path:
        """Path to the catalog file."""
        return self._path

    @property
    def is_dirty(self) -> bool:
        """Whether there are unsaved changes."""
        return self._dirty

    @property
    def config(self) -> PersistenceConfig:
        """Current persistence configuration."""
        return self._config

    def to_dict(self) -> dict:
        """Export catalog as dictionary."""
        return self._registry.to_dict()


# ========== Convenience Functions ==========


async def create_persistent_registry(
    path: Path | str,
    auto_save: bool = True,
    max_history: int = 50,
) -> PersistentRegistry:
    """
    Create a persistent registry with sensible defaults.

    Convenience wrapper around PersistentRegistry.create().

    Args:
        path: Path to catalog JSON file
        auto_save: If True, save after each modification (default)
        max_history: Number of historical catalog states to keep

    Returns:
        Initialized PersistentRegistry

    Example:
        >>> registry = await create_persistent_registry("catalog.json")
        >>> await registry.register(entry)  # Auto-saved
    """
    config = PersistenceConfig(
        save_strategy=SaveStrategy.ON_WRITE if auto_save else SaveStrategy.MANUAL,
        max_history=max_history,
    )
    return await PersistentRegistry.create(path=path, config=config)


async def load_or_create_registry(
    path: Path | str,
    auto_save: bool = True,
) -> PersistentRegistry:
    """
    Load existing registry or create new one.

    This is the recommended way to initialize a persistent registry
    in most applications.

    Args:
        path: Path to catalog JSON file
        auto_save: If True, save after each modification

    Returns:
        PersistentRegistry (existing or newly created)
    """
    return await create_persistent_registry(path=path, auto_save=auto_save)
