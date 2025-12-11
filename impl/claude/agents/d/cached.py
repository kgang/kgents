"""
CachedAgent: Layered persistence with fast cache + durable backend.

Implements a two-tier D-gent:
- VolatileAgent (cache): Fast in-memory reads
- PersistentAgent (backend): Durable writes

This demonstrates D-gent composition: combining two D-gents to create
a new D-gent with different performance characteristics.
"""

from typing import TYPE_CHECKING, Generic, List, TypeVar

from .protocol import DataAgent

if TYPE_CHECKING:
    from .lens import Lens
    from .lens_agent import LensAgent

S = TypeVar("S")
A = TypeVar("A")


class CachedAgent(Generic[S]):
    """
    Two-tier D-gent with volatile cache + persistent backend.

    Read Strategy:
    - Always reads from cache (fast, in-memory)
    - Cache is populated from backend on initialization

    Write Strategy (Write-Through):
    - Updates both cache AND backend
    - Ensures cache and backend stay synchronized
    - If backend write fails, cache is NOT updated

    History Strategy:
    - Delegates to backend (source of truth)
    - Cache history is not exposed (implementation detail)

    Example:
        >>> from dataclasses import dataclass
        >>> from pathlib import Path
        >>> from agents.d import VolatileAgent, PersistentAgent
        >>>
        >>> @dataclass
        ... class Config:
        ...     setting: str
        ...
        >>> # Create cache + backend
        >>> cache = VolatileAgent(_state=Config(setting="default"))
        >>> backend = PersistentAgent(
        ...     path=Path("config.json"),
        ...     schema=Config
        ... )
        >>>
        >>> # Compose into cached agent
        >>> cached = CachedAgent(cache=cache, backend=backend)
        >>>
        >>> # Reads from cache (fast)
        >>> config = await cached.load()
        >>>
        >>> # Writes to both (synchronized)
        >>> await cached.save(Config(setting="production"))
        >>>
        >>> # History from backend (durable)
        >>> history = await cached.history()
    """

    def __init__(
        self,
        cache: DataAgent[S],
        backend: DataAgent[S],
    ):
        """
        Initialize cached D-gent.

        Args:
            cache: Fast in-memory D-gent (typically VolatileAgent)
            backend: Durable persistent D-gent (typically PersistentAgent)
        """
        self.cache = cache
        self.backend = backend

    async def load(self) -> S:
        """
        Load state from cache.

        Returns:
            Current state from fast cache

        Note:
            Always reads from cache, not backend.
            Assumes cache is synchronized via write-through.
        """
        return await self.cache.load()

    async def save(self, state: S) -> None:
        """
        Write-through: Update both cache and backend.

        Strategy:
        1. Write to backend first (source of truth)
        2. If successful, update cache
        3. If backend fails, cache is NOT updated

        This ensures cache never has data that isn't persisted.

        Args:
            state: New state to persist

        Raises:
            StateSerializationError: If backend can't serialize state
            StorageError: If backend write fails
        """
        # Write to backend FIRST (source of truth)
        await self.backend.save(state)

        # Only update cache if backend write succeeded
        await self.cache.save(state)

    async def history(self, limit: int | None = None) -> List[S]:
        """
        Query historical states from backend.

        Args:
            limit: Max entries to return (newest first)

        Returns:
            Historical states from durable backend

        Note:
            Delegates to backend, not cache.
            Backend is the authoritative source for history.
        """
        return await self.backend.history(limit=limit)

    async def warm_cache(self) -> None:
        """
        Populate cache from backend (cache miss recovery).

        Use this to:
        - Initialize cache on first load
        - Recover from cache invalidation
        - Synchronize after backend was updated externally

        Example:
            >>> # Create cached agent with empty cache
            >>> cached = CachedAgent(
            ...     cache=VolatileAgent(_state=None),
            ...     backend=PersistentAgent(...)
            ... )
            >>>
            >>> # Populate cache from backend
            >>> await cached.warm_cache()
            >>>
            >>> # Now reads are fast (from cache)
            >>> state = await cached.load()
        """
        backend_state = await self.backend.load()
        await self.cache.save(backend_state)

    async def invalidate_cache(self) -> None:
        """
        Invalidate cache and reload from backend.

        Use this when:
        - Backend was updated externally (outside this agent)
        - You want to ensure fresh data from backend
        - Testing cache miss scenarios

        Note:
            This method both invalidates AND repopulates the cache atomically.
            The cache is refreshed with current backend state.

        Example:
            >>> # External process updated backend
            >>> await cached.invalidate_cache()
            >>> # Cache now has fresh data from backend
        """
        # Reload cache from backend (invalidate + warm in one operation)
        await self.warm_cache()

    def __rshift__(self, other: "Lens[S, A]") -> "LensAgent[S, A]":
        """
        Compose with a lens to create focused view: cached_dgent >> lens.

        Creates a LensAgent that provides scoped access to sub-state,
        while maintaining the cache layer for performance.

        Type: CachedAgent[S] >> Lens[S, A] → LensAgent[S, A]

        Example:
            >>> from agents.d.lens import key_lens
            >>> from pathlib import Path
            >>>
            >>> # Cached state with fast reads
            >>> cached = CachedAgent(
            ...     cache=VolatileAgent(_state={"users": {}, "config": {}}),
            ...     backend=PersistentAgent(path=Path("state.json"), schema=dict)
            ... )
            >>>
            >>> # Focus on users via composition
            >>> user_dgent = cached >> key_lens("users")
            >>>
            >>> # Focused agent has cache performance
            >>> await user_dgent.save({"alice": {"age": 30}})
            >>> await user_dgent.load()  # Fast read from cache
            {'alice': {'age': 30}}
        """
        from .lens_agent import LensAgent

        return LensAgent(parent=self, lens=other)
