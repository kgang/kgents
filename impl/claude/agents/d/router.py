"""
DgentRouter: Backend selection with graceful degradation.

Routes data operations to the best available backend in the projection lattice.

This is the NEW simplified D-gent architecture (data-architecture-rewrite).
"""

from __future__ import annotations

import asyncio
import os
from dataclasses import dataclass, field
from enum import Enum, auto
from pathlib import Path
from typing import Final, List

from .backends.jsonl import JSONLBackend
from .backends.memory import MemoryBackend
from .backends.sqlite import SQLiteBackend
from .datum import Datum
from .protocol import BaseDgent, DgentProtocol

# Environment variable for backend override
ENV_BACKEND: Final[str] = "KGENTS_DGENT_BACKEND"
ENV_POSTGRES_URL: Final[str] = "KGENTS_POSTGRES_URL"


class Backend(Enum):
    """Available backends in the projection lattice."""

    MEMORY = auto()  # Tier 0: Ephemeral
    JSONL = auto()  # Tier 1: Simple file
    SQLITE = auto()  # Tier 2: Local database
    POSTGRES = auto()  # Tier 3-4: Production database


@dataclass
class BackendStatus:
    """Status of a backend."""

    backend: Backend
    available: bool
    reason: str = ""
    latency_ms: float | None = None


@dataclass
class DgentRouter(BaseDgent):
    """
    Routes data operations to the best available backend.

    Selection order:
    1. Explicit override (if provided via constructor)
    2. Environment detection (KGENTS_DGENT_BACKEND)
    3. Availability probe (try preferred, fallback on failure)

    The router implements DgentProtocol itself, delegating to the selected backend.

    Usage:
        router = DgentRouter()  # Auto-select best available
        router = DgentRouter(preferred=Backend.SQLITE)  # Prefer SQLite
        router = DgentRouter(preferred=Backend.POSTGRES)  # Prefer Postgres

        await router.put(datum)  # Automatically routes to best backend
    """

    namespace: str = "default"
    preferred: Backend | None = None
    fallback_chain: list[Backend] = field(
        default_factory=lambda: [Backend.SQLITE, Backend.JSONL, Backend.MEMORY]
    )
    data_dir: Path | None = None

    _backend: DgentProtocol | None = field(default=None, repr=False)
    _selected: Backend | None = field(default=None, repr=False)
    _lock: asyncio.Lock = field(default_factory=asyncio.Lock, repr=False)

    async def _check_available(self, backend: Backend) -> BackendStatus:
        """Check if a backend is available."""
        try:
            if backend == Backend.MEMORY:
                return BackendStatus(backend, True)

            elif backend == Backend.JSONL:
                # JSONL is always available (can create file)
                return BackendStatus(backend, True)

            elif backend == Backend.SQLITE:
                # SQLite requires we can write to data dir
                data_dir = self.data_dir or Path.home() / ".kgents" / "data"
                try:
                    data_dir.mkdir(parents=True, exist_ok=True)
                    test_file = data_dir / ".write_test"
                    test_file.touch()
                    test_file.unlink()
                    return BackendStatus(backend, True)
                except OSError as e:
                    return BackendStatus(backend, False, str(e))

            elif backend == Backend.POSTGRES:
                # Postgres requires URL and asyncpg
                url = os.environ.get(ENV_POSTGRES_URL)
                if not url:
                    return BackendStatus(backend, False, "KGENTS_POSTGRES_URL not set")

                try:
                    import asyncpg  # noqa: F401

                    # TODO: Actually test connection
                    return BackendStatus(backend, True)
                except ImportError:
                    return BackendStatus(backend, False, "asyncpg not installed")

            return BackendStatus(backend, False, "Unknown backend")

        except Exception as e:
            return BackendStatus(backend, False, str(e))

    def _create_backend(self, backend: Backend) -> DgentProtocol:
        """Create a backend instance."""
        if backend == Backend.MEMORY:
            return MemoryBackend()

        elif backend == Backend.JSONL:
            return JSONLBackend(
                namespace=self.namespace,
                data_dir=self.data_dir,
            )

        elif backend == Backend.SQLITE:
            return SQLiteBackend(
                namespace=self.namespace,
                data_dir=self.data_dir,
            )

        elif backend == Backend.POSTGRES:
            # Import and create Postgres backend
            from .backends.postgres import PostgresBackend

            url = os.environ.get(ENV_POSTGRES_URL, "")
            return PostgresBackend(url, namespace=self.namespace)

        raise ValueError(f"Unknown backend: {backend}")

    async def _select_backend(self) -> tuple[Backend, DgentProtocol]:
        """Select the best available backend."""
        # 1. Check environment override
        env_backend = os.environ.get(ENV_BACKEND)
        if env_backend:
            try:
                backend = Backend[env_backend.upper()]
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
        return Backend.MEMORY, MemoryBackend()

    async def _get_backend(self) -> DgentProtocol:
        """Get or create the selected backend."""
        async with self._lock:
            if self._backend is None:
                self._selected, self._backend = await self._select_backend()
            return self._backend

    # --- DgentProtocol Implementation ---

    async def put(self, datum: Datum) -> str:
        """Store datum via selected backend."""
        backend = await self._get_backend()
        return await backend.put(datum)

    async def get(self, id: str) -> Datum | None:
        """Retrieve datum via selected backend."""
        backend = await self._get_backend()
        return await backend.get(id)

    async def delete(self, id: str) -> bool:
        """Delete datum via selected backend."""
        backend = await self._get_backend()
        return await backend.delete(id)

    async def list(
        self,
        prefix: str | None = None,
        after: float | None = None,
        limit: int = 100,
    ) -> List[Datum]:
        """List data via selected backend."""
        backend = await self._get_backend()
        return await backend.list(prefix=prefix, after=after, limit=limit)

    async def causal_chain(self, id: str) -> List[Datum]:
        """Get causal chain via selected backend."""
        backend = await self._get_backend()
        return await backend.causal_chain(id)

    async def exists(self, id: str) -> bool:
        """Check existence via selected backend."""
        backend = await self._get_backend()
        return await backend.exists(id)

    async def count(self) -> int:
        """Count data via selected backend."""
        backend = await self._get_backend()
        return await backend.count()

    # --- Router-specific Methods ---

    @property
    def selected_backend(self) -> Backend | None:
        """Get the currently selected backend (None if not yet selected)."""
        return self._selected

    async def status(self) -> List[BackendStatus]:
        """Get availability status of all backends."""
        statuses = []
        for backend in Backend:
            status = await self._check_available(backend)
            statuses.append(status)
        return statuses

    async def force_backend(self, backend: Backend) -> None:
        """Force use of a specific backend (raises if unavailable)."""
        async with self._lock:
            status = await self._check_available(backend)
            if not status.available:
                raise RuntimeError(f"Backend {backend.name} not available: {status.reason}")
            self._selected = backend
            self._backend = self._create_backend(backend)

    def reset(self) -> None:
        """Reset the router (clears selected backend)."""
        self._backend = None
        self._selected = None


# Convenience factory
def create_dgent(
    namespace: str = "default",
    preferred: Backend | None = None,
    data_dir: Path | None = None,
) -> DgentRouter:
    """
    Create a D-gent router with the given configuration.

    Args:
        namespace: Name for this data store
        preferred: Preferred backend (auto-selects if None)
        data_dir: Directory for data files

    Returns:
        Configured DgentRouter
    """
    return DgentRouter(
        namespace=namespace,
        preferred=preferred,
        data_dir=data_dir,
    )
