"""
VgentRouter: Backend selection with graceful degradation for vector operations.

Routes vector operations to the best available backend in the projection lattice.

The projection lattice for vectors:
    Qdrant (10M+ vectors, distributed)
       ↑
    pgvector (100K-1M, SQL filtering)
       ↑
    D-gent (10K-100K, local persistence)
       ↑
    Memory (< 10K, ephemeral)

Graceful degradation: if preferred backend unavailable, descend the lattice.
"""

from __future__ import annotations

import asyncio
import os
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import TYPE_CHECKING, Final

from .backends.memory import MemoryVectorBackend
from .protocol import BaseVgent, VgentProtocol
from .types import DistanceMetric, Embedding, SearchResult, VectorEntry

if TYPE_CHECKING:
    from agents.d import DgentProtocol


# Environment variables for backend configuration
ENV_BACKEND: Final[str] = "KGENTS_VGENT_BACKEND"
ENV_QDRANT_URL: Final[str] = "KGENTS_QDRANT_URL"
ENV_POSTGRES_URL: Final[str] = "KGENTS_POSTGRES_URL"


class VectorBackend(Enum):
    """Available vector backends in the projection lattice."""

    MEMORY = auto()  # Tier 0: Ephemeral (< 10K vectors)
    DGENT = auto()  # Tier 1: D-gent persisted (10K-100K)
    POSTGRES = auto()  # Tier 2: pgvector (100K-1M)
    QDRANT = auto()  # Tier 3: Dedicated vector DB (10M+)


@dataclass
class BackendStatus:
    """Status of a vector backend."""

    backend: VectorBackend
    available: bool
    reason: str = ""
    latency_ms: float | None = None


@dataclass
class VgentRouter(BaseVgent):
    """
    Routes vector operations to the best available backend.

    Selection order:
    1. Explicit override (if provided via constructor)
    2. Environment detection (KGENTS_VGENT_BACKEND)
    3. Availability probe (try preferred, fallback on failure)

    The router implements VgentProtocol itself, delegating to the selected backend.

    Usage:
        router = VgentRouter(dimension=768)  # Auto-select best available
        router = VgentRouter(dimension=768, preferred=VectorBackend.DGENT)
        router = VgentRouter(dimension=768, preferred=VectorBackend.QDRANT)

        await router.add("doc1", embedding)  # Automatically routes to best backend
        results = await router.search(query)

    Architecture:
        - VgentRouter is a facade that delegates to a concrete backend
        - Backend selection is lazy (happens on first operation)
        - Selection is locked to prevent concurrent backend switching
        - For D-gent backend, a DgentRouter is created if not provided
    """

    dimension_: int
    metric_: DistanceMetric = DistanceMetric.COSINE
    namespace: str = "vectors"
    preferred: VectorBackend | None = None
    fallback_chain: list[VectorBackend] = field(
        default_factory=lambda: [VectorBackend.DGENT, VectorBackend.MEMORY]
    )
    dgent: DgentProtocol | None = None  # Optional injected D-gent

    _backend: VgentProtocol | None = field(default=None, repr=False)
    _selected: VectorBackend | None = field(default=None, repr=False)
    _lock: asyncio.Lock = field(default_factory=asyncio.Lock, repr=False)
    _index_loaded: bool = field(default=False, repr=False)

    @property
    def dimension(self) -> int:
        """Dimension of vectors in this router."""
        return self.dimension_

    @property
    def metric(self) -> DistanceMetric:
        """Distance metric used for comparison."""
        return self.metric_

    # =========================================================================
    # Backend Selection
    # =========================================================================

    async def _check_available(self, backend: VectorBackend) -> BackendStatus:
        """Check if a backend is available."""
        try:
            if backend == VectorBackend.MEMORY:
                # Memory is always available
                return BackendStatus(backend, True)

            elif backend == VectorBackend.DGENT:
                # D-gent is always available (uses its own projection lattice)
                return BackendStatus(backend, True)

            elif backend == VectorBackend.POSTGRES:
                # Postgres requires URL and asyncpg with pgvector
                url = os.environ.get(ENV_POSTGRES_URL)
                if not url:
                    return BackendStatus(backend, False, "KGENTS_POSTGRES_URL not set")
                try:
                    import asyncpg  # noqa: F401

                    # TODO: Actually test pgvector extension
                    return BackendStatus(backend, True)
                except ImportError:
                    return BackendStatus(backend, False, "asyncpg not installed")

            elif backend == VectorBackend.QDRANT:
                # Qdrant requires URL and qdrant-client
                url = os.environ.get(ENV_QDRANT_URL)
                if not url:
                    return BackendStatus(backend, False, "KGENTS_QDRANT_URL not set")
                try:
                    import qdrant_client  # noqa: F401

                    return BackendStatus(backend, True)
                except ImportError:
                    return BackendStatus(backend, False, "qdrant-client not installed")

            return BackendStatus(backend, False, "Unknown backend")

        except Exception as e:
            return BackendStatus(backend, False, str(e))

    def _create_backend(self, backend: VectorBackend) -> VgentProtocol:
        """Create a backend instance."""
        if backend == VectorBackend.MEMORY:
            return MemoryVectorBackend(
                dimension=self.dimension_,
                metric=self.metric_,
            )

        elif backend == VectorBackend.DGENT:
            from .backends.dgent import DgentVectorBackend

            # Use injected D-gent or create a new router
            if self.dgent is not None:
                dgent = self.dgent
            else:
                from agents.d import DgentRouter

                dgent = DgentRouter(namespace=f"vgent_{self.namespace}")

            return DgentVectorBackend(
                dgent=dgent,
                dimension=self.dimension_,
                metric=self.metric_,
                namespace=self.namespace,
            )

        elif backend == VectorBackend.POSTGRES:
            # Postgres backend (Phase 6 - not yet implemented)
            raise NotImplementedError("PostgresVectorBackend not yet implemented")

        elif backend == VectorBackend.QDRANT:
            # Qdrant backend (Phase 6 - not yet implemented)
            raise NotImplementedError("QdrantBackend not yet implemented")

        raise ValueError(f"Unknown backend: {backend}")

    async def _select_backend(self) -> tuple[VectorBackend, VgentProtocol]:
        """Select the best available backend."""
        # 1. Check environment override
        env_backend = os.environ.get(ENV_BACKEND)
        if env_backend:
            try:
                backend = VectorBackend[env_backend.upper()]
                status = await self._check_available(backend)
                if status.available:
                    return backend, self._create_backend(backend)
            except KeyError:
                pass  # Invalid env value, continue with fallback

        # 2. Try preferred backend
        if self.preferred:
            status = await self._check_available(self.preferred)
            if status.available:
                return self.preferred, self._create_backend(self.preferred)

        # 3. Try fallback chain
        for backend in self.fallback_chain:
            status = await self._check_available(backend)
            if status.available:
                return backend, self._create_backend(backend)

        # 4. Last resort: memory (always available)
        return VectorBackend.MEMORY, MemoryVectorBackend(
            dimension=self.dimension_,
            metric=self.metric_,
        )

    async def _get_backend(self) -> VgentProtocol:
        """Get or create the selected backend."""
        async with self._lock:
            if self._backend is None:
                self._selected, self._backend = await self._select_backend()

                # Load index for D-gent backend
                if self._selected == VectorBackend.DGENT and not self._index_loaded:
                    from .backends.dgent import DgentVectorBackend

                    if isinstance(self._backend, DgentVectorBackend):
                        await self._backend.load_index()
                        self._index_loaded = True

            return self._backend

    # =========================================================================
    # VgentProtocol Implementation (delegation)
    # =========================================================================

    async def add(
        self,
        id: str,
        embedding: Embedding | list[float],
        metadata: dict[str, str] | None = None,
    ) -> str:
        """Add a vector via selected backend."""
        backend = await self._get_backend()
        return await backend.add(id, embedding, metadata)

    async def add_batch(
        self,
        entries: list[tuple[str, Embedding | list[float], dict[str, str] | None]],
    ) -> list[str]:
        """Add multiple vectors via selected backend."""
        backend = await self._get_backend()
        return await backend.add_batch(entries)

    async def remove(self, id: str) -> bool:
        """Remove a vector via selected backend."""
        backend = await self._get_backend()
        return await backend.remove(id)

    async def clear(self) -> int:
        """Clear all vectors via selected backend."""
        backend = await self._get_backend()
        return await backend.clear()

    async def get(self, id: str) -> VectorEntry | None:
        """Retrieve a vector via selected backend."""
        backend = await self._get_backend()
        return await backend.get(id)

    async def search(
        self,
        query: Embedding | list[float],
        limit: int = 10,
        filters: dict[str, str] | None = None,
        threshold: float | None = None,
    ) -> list[SearchResult]:
        """Search for similar vectors via selected backend."""
        backend = await self._get_backend()
        return await backend.search(query, limit, filters, threshold)

    async def count(self) -> int:
        """Count vectors via selected backend."""
        backend = await self._get_backend()
        return await backend.count()

    async def exists(self, id: str) -> bool:
        """Check if vector exists via selected backend."""
        backend = await self._get_backend()
        return await backend.exists(id)

    # =========================================================================
    # Router-specific Methods
    # =========================================================================

    @property
    def selected_backend(self) -> VectorBackend | None:
        """Get the currently selected backend (None if not yet selected)."""
        return self._selected

    async def status(self) -> list[BackendStatus]:
        """Get availability status of all backends."""
        statuses = []
        for backend in VectorBackend:
            status = await self._check_available(backend)
            statuses.append(status)
        return statuses

    async def force_backend(self, backend: VectorBackend) -> None:
        """
        Force use of a specific backend.

        Args:
            backend: The backend to use

        Raises:
            RuntimeError: If backend is not available
        """
        async with self._lock:
            status = await self._check_available(backend)
            if not status.available:
                raise RuntimeError(
                    f"Backend {backend.name} not available: {status.reason}"
                )
            self._selected = backend
            self._backend = self._create_backend(backend)
            self._index_loaded = False

            # Load index for D-gent backend
            if backend == VectorBackend.DGENT:
                from .backends.dgent import DgentVectorBackend

                if isinstance(self._backend, DgentVectorBackend):
                    await self._backend.load_index()
                    self._index_loaded = True

    def reset(self) -> None:
        """Reset the router (clears selected backend)."""
        self._backend = None
        self._selected = None
        self._index_loaded = False

    def __repr__(self) -> str:
        backend_str = self._selected.name if self._selected else "not_selected"
        return (
            f"VgentRouter("
            f"dimension={self.dimension_}, "
            f"metric={self.metric_.value}, "
            f"namespace={self.namespace!r}, "
            f"backend={backend_str})"
        )


# Convenience factory
def create_vgent(
    dimension: int,
    metric: DistanceMetric = DistanceMetric.COSINE,
    namespace: str = "vectors",
    preferred: VectorBackend | None = None,
    dgent: DgentProtocol | None = None,
) -> VgentRouter:
    """
    Create a V-gent router with the given configuration.

    Args:
        dimension: Dimension of vectors (must match embeddings)
        metric: Distance metric for similarity (default: cosine)
        namespace: Name for this vector store (default: "vectors")
        preferred: Preferred backend (auto-selects if None)
        dgent: Optional D-gent instance for D-gent backend

    Returns:
        Configured VgentRouter

    Example:
        vgent = create_vgent(dimension=768)
        await vgent.add("doc1", embedding)
        results = await vgent.search(query)
    """
    return VgentRouter(
        dimension_=dimension,
        metric_=metric,
        namespace=namespace,
        preferred=preferred,
        dgent=dgent,
    )
