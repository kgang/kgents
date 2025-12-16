"""
Tests for DgentRouter (backend selection with graceful degradation).

Tests verify:
1. Backend selection logic
2. Graceful degradation fallback
3. Environment variable override
4. Router-specific methods
"""

from __future__ import annotations

import os
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from ..datum import Datum
from ..router import Backend, BackendStatus, DgentRouter, create_dgent


@pytest.fixture
def temp_dir() -> Path:
    """Temporary directory for file-based backends."""
    with tempfile.TemporaryDirectory() as td:
        yield Path(td)


@pytest.fixture
def router(temp_dir: Path) -> DgentRouter:
    """Fresh router for each test."""
    return DgentRouter(namespace="test", data_dir=temp_dir)


class TestBackendSelection:
    """Tests for backend selection logic."""

    @pytest.mark.asyncio
    async def test_selects_from_fallback_chain(self, temp_dir: Path) -> None:
        """Router selects available backend from fallback chain."""
        router = DgentRouter(
            namespace="test",
            data_dir=temp_dir,
            fallback_chain=[Backend.SQLITE, Backend.JSONL, Backend.MEMORY],
        )

        # Trigger selection by using the router
        await router.put(Datum.create(b"test"))

        # Should have selected SQLite (first in chain, available)
        assert router.selected_backend == Backend.SQLITE

    @pytest.mark.asyncio
    async def test_uses_preferred_if_available(self, temp_dir: Path) -> None:
        """Router uses preferred backend if available."""
        router = DgentRouter(
            namespace="test",
            data_dir=temp_dir,
            preferred=Backend.JSONL,
        )

        await router.put(Datum.create(b"test"))

        assert router.selected_backend == Backend.JSONL

    @pytest.mark.asyncio
    async def test_falls_back_to_memory(self) -> None:
        """Router falls back to memory as last resort."""
        # Use a non-existent directory that can't be created
        router = DgentRouter(
            namespace="test",
            data_dir=Path("/nonexistent/path/that/cannot/be/created"),
            fallback_chain=[Backend.MEMORY],
        )

        await router.put(Datum.create(b"test"))

        assert router.selected_backend == Backend.MEMORY


class TestEnvironmentOverride:
    """Tests for environment variable override."""

    @pytest.mark.asyncio
    async def test_env_override_selects_backend(self, temp_dir: Path) -> None:
        """KGENTS_DGENT_BACKEND environment variable overrides selection."""
        router = DgentRouter(
            namespace="test",
            data_dir=temp_dir,
            preferred=Backend.SQLITE,  # Would normally select SQLite
        )

        with patch.dict(os.environ, {"KGENTS_DGENT_BACKEND": "MEMORY"}):
            # Reset to force re-selection
            router.reset()
            await router.put(Datum.create(b"test"))

            assert router.selected_backend == Backend.MEMORY

    @pytest.mark.asyncio
    async def test_invalid_env_ignored(self, temp_dir: Path) -> None:
        """Invalid environment variable value is ignored."""
        router = DgentRouter(
            namespace="test",
            data_dir=temp_dir,
        )

        with patch.dict(os.environ, {"KGENTS_DGENT_BACKEND": "INVALID"}):
            router.reset()
            await router.put(Datum.create(b"test"))

            # Should fall through to normal selection
            assert router.selected_backend in [
                Backend.SQLITE,
                Backend.JSONL,
                Backend.MEMORY,
            ]


class TestRouterProtocol:
    """Tests that router correctly delegates to selected backend."""

    @pytest.mark.asyncio
    async def test_put_get_roundtrip(self, router: DgentRouter) -> None:
        """put() and get() work through router."""
        d = Datum.create(b"test content")

        await router.put(d)
        result = await router.get(d.id)

        assert result is not None
        assert result.content == b"test content"

    @pytest.mark.asyncio
    async def test_delete_through_router(self, router: DgentRouter) -> None:
        """delete() works through router."""
        d = Datum.create(b"test")
        await router.put(d)

        assert await router.delete(d.id) is True
        assert await router.get(d.id) is None

    @pytest.mark.asyncio
    async def test_list_through_router(self, router: DgentRouter) -> None:
        """list() works through router."""
        for i in range(5):
            await router.put(Datum.create(f"item-{i}".encode()))

        result = await router.list()
        assert len(result) == 5

    @pytest.mark.asyncio
    async def test_causal_chain_through_router(self, router: DgentRouter) -> None:
        """causal_chain() works through router."""
        a = Datum.create(b"a")
        b = a.derive(b"b")

        await router.put(a)
        await router.put(b)

        chain = await router.causal_chain(b.id)
        assert len(chain) == 2

    @pytest.mark.asyncio
    async def test_exists_through_router(self, router: DgentRouter) -> None:
        """exists() works through router."""
        d = Datum.create(b"test")
        await router.put(d)

        assert await router.exists(d.id) is True
        assert await router.exists("nonexistent") is False

    @pytest.mark.asyncio
    async def test_count_through_router(self, router: DgentRouter) -> None:
        """count() works through router."""
        for i in range(3):
            await router.put(Datum.create(f"item-{i}".encode()))

        assert await router.count() == 3


class TestRouterMethods:
    """Tests for router-specific methods."""

    @pytest.mark.asyncio
    async def test_status_returns_all_backends(self, router: DgentRouter) -> None:
        """status() returns status for all backends."""
        statuses = await router.status()

        # Should have status for all backends
        backend_names = {s.backend for s in statuses}
        assert Backend.MEMORY in backend_names
        assert Backend.JSONL in backend_names
        assert Backend.SQLITE in backend_names

    @pytest.mark.asyncio
    async def test_force_backend(self, router: DgentRouter) -> None:
        """force_backend() switches to specified backend."""
        await router.force_backend(Backend.MEMORY)

        assert router.selected_backend == Backend.MEMORY

    @pytest.mark.asyncio
    async def test_force_unavailable_backend_raises(
        self, temp_dir: Path
    ) -> None:
        """force_backend() raises for unavailable backend."""
        router = DgentRouter(namespace="test", data_dir=temp_dir)

        # Postgres is not available (no URL configured)
        with pytest.raises(RuntimeError, match="not available"):
            await router.force_backend(Backend.POSTGRES)

    @pytest.mark.asyncio
    async def test_reset_clears_selection(self, router: DgentRouter) -> None:
        """reset() clears backend selection."""
        await router.put(Datum.create(b"test"))
        assert router.selected_backend is not None

        router.reset()

        assert router.selected_backend is None


class TestCreateDgentFactory:
    """Tests for create_dgent() factory function."""

    @pytest.mark.asyncio
    async def test_create_dgent_default(self, temp_dir: Path) -> None:
        """create_dgent() creates router with defaults."""
        dgent = create_dgent(namespace="test", data_dir=temp_dir)

        assert isinstance(dgent, DgentRouter)
        assert dgent.namespace == "test"

    @pytest.mark.asyncio
    async def test_create_dgent_with_preferred(self, temp_dir: Path) -> None:
        """create_dgent() accepts preferred backend."""
        dgent = create_dgent(
            namespace="test",
            preferred=Backend.MEMORY,
            data_dir=temp_dir,
        )

        await dgent.put(Datum.create(b"test"))

        assert dgent.selected_backend == Backend.MEMORY
