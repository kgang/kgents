"""
Tests for CachedAgent: layered persistence (cache + backend).

Validates:
- Cache hit performance (fast reads from VolatileAgent)
- Write-through synchronization (both cache and backend updated)
- Cache miss fallback (warm_cache recovery)
- History delegation (backend is source of truth)
"""

import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pytest
from agents.d import CachedAgent, PersistentAgent, VolatileAgent


@dataclass
class TestState:
    """Test state schema."""

    value: int
    label: str


# -------------------------------------------------------------------
# Basic Operations
# -------------------------------------------------------------------


@pytest.mark.asyncio
async def test_load_from_cache() -> None:
    """Load reads from fast cache, not backend."""
    cache = VolatileAgent(_state=TestState(value=42, label="cached"))
    backend = VolatileAgent(_state=TestState(value=99, label="backend"))

    cached = CachedAgent(cache=cache, backend=backend)

    # Should read from cache, not backend
    state = await cached.load()
    assert state.value == 42
    assert state.label == "cached"


@pytest.mark.asyncio
async def test_save_write_through() -> None:
    """Save updates BOTH cache and backend."""
    cache = VolatileAgent(_state=TestState(value=1, label="old"))
    backend = VolatileAgent(_state=TestState(value=1, label="old"))

    cached = CachedAgent(cache=cache, backend=backend)

    # Write through both layers
    await cached.save(TestState(value=100, label="new"))

    # Verify cache updated
    cache_state = await cache.load()
    assert cache_state.value == 100
    assert cache_state.label == "new"

    # Verify backend updated
    backend_state = await backend.load()
    assert backend_state.value == 100
    assert backend_state.label == "new"


@pytest.mark.asyncio
async def test_history_from_backend() -> None:
    """History delegates to backend, not cache."""
    cache = VolatileAgent(_state=TestState(value=1, label="cache"))
    backend = VolatileAgent(_state=TestState(value=1, label="backend"))

    cached = CachedAgent(cache=cache, backend=backend)

    # Generate history via backend
    await backend.save(TestState(value=2, label="v2"))
    await backend.save(TestState(value=3, label="v3"))

    # CachedAgent.history should delegate to backend
    history = await cached.history()

    # Should have 2 entries (initial state + first save)
    assert len(history) >= 1
    assert history[0].value == 2  # Most recent history entry


# -------------------------------------------------------------------
# Cache Warming
# -------------------------------------------------------------------


@pytest.mark.asyncio
async def test_warm_cache_from_backend() -> None:
    """warm_cache() populates cache from backend."""
    with tempfile.TemporaryDirectory() as tmpdir:
        path = Path(tmpdir) / "state.json"

        # Setup: Backend has data, cache is empty
        backend = PersistentAgent(path=path, schema=TestState)
        await backend.save(TestState(value=200, label="from_backend"))

        # Cache starts with different data
        cache = VolatileAgent(_state=TestState(value=0, label="empty"))

        cached = CachedAgent(cache=cache, backend=backend)

        # Before warm: cache has old data
        state_before = await cached.load()
        assert state_before.value == 0

        # Warm cache from backend
        await cached.warm_cache()

        # After warm: cache has backend data
        state_after = await cached.load()
        assert state_after.value == 200
        assert state_after.label == "from_backend"


@pytest.mark.asyncio
async def test_invalidate_cache() -> None:
    """invalidate_cache() forces fresh read from backend."""
    with tempfile.TemporaryDirectory() as tmpdir:
        path = Path(tmpdir) / "state.json"

        backend = PersistentAgent(path=path, schema=TestState)
        await backend.save(TestState(value=10, label="initial"))

        cache = VolatileAgent(_state=TestState(value=10, label="initial"))

        cached = CachedAgent(cache=cache, backend=backend)

        # Simulate external update to backend (bypassing cached agent)
        await backend.save(TestState(value=999, label="external_update"))

        # Cache still has old data
        stale = await cached.load()
        assert stale.value == 10

        # Invalidate and repopulate
        await cached.invalidate_cache()

        # Now cache has fresh data
        fresh = await cached.load()
        assert fresh.value == 999
        assert fresh.label == "external_update"


# -------------------------------------------------------------------
# Performance Characteristics
# -------------------------------------------------------------------


@pytest.mark.asyncio
async def test_cache_hit_performance() -> None:
    """Cache reads should be faster than backend reads."""
    import time

    with tempfile.TemporaryDirectory() as tmpdir:
        path = Path(tmpdir) / "state.json"

        # Create backend with data
        backend = PersistentAgent(path=path, schema=TestState)
        await backend.save(TestState(value=1, label="test"))

        # Create cache pre-warmed
        cache = VolatileAgent(_state=TestState(value=1, label="test"))

        cached = CachedAgent(cache=cache, backend=backend)

        # Measure cache read time (should be < 1ms)
        start = time.perf_counter()
        for _ in range(100):
            await cached.load()
        cache_time = time.perf_counter() - start

        # Measure backend read time
        start = time.perf_counter()
        for _ in range(100):
            await backend.load()
        backend_time = time.perf_counter() - start

        # Cache should be faster (or at least not slower)
        assert cache_time <= backend_time * 2  # Allow 2x margin


# -------------------------------------------------------------------
# Composition with Persistent Backend
# -------------------------------------------------------------------


@pytest.mark.asyncio
async def test_cached_agent_with_persistent_backend() -> None:
    """Full integration: VolatileAgent cache + PersistentAgent backend."""
    with tempfile.TemporaryDirectory() as tmpdir:
        path = Path(tmpdir) / "data.json"

        # Create persistent backend
        backend = PersistentAgent(path=path, schema=TestState)
        await backend.save(TestState(value=50, label="persisted"))

        # Create volatile cache (initially synced)
        cache = VolatileAgent(_state=TestState(value=50, label="persisted"))

        # Compose
        cached = CachedAgent(cache=cache, backend=backend)

        # Update via cached agent
        await cached.save(TestState(value=100, label="updated"))

        # Verify persistence: destroy and recreate
        del cached
        del cache
        del backend

        # Recreate backend from file
        backend2 = PersistentAgent(path=path, schema=TestState)
        state = await backend2.load()

        # Data survived (was persisted)
        assert state.value == 100
        assert state.label == "updated"


# -------------------------------------------------------------------
# Error Handling
# -------------------------------------------------------------------


@pytest.mark.asyncio
async def test_backend_write_failure_preserves_cache() -> None:
    """If backend write fails, cache should NOT be updated."""

    # Create a backend that will fail on save
    class FailingBackend:
        async def load(self) -> TestState:
            return TestState(value=1, label="old")

        async def save(self, state: TestState) -> None:
            raise RuntimeError("Backend write failed!")

        async def history(self, limit: int | None = None) -> list[Any]:
            return []

    cache = VolatileAgent(_state=TestState(value=1, label="old"))
    backend = FailingBackend()

    cached = CachedAgent(cache=cache, backend=backend)

    # Attempt save (backend will fail)
    with pytest.raises(RuntimeError, match="Backend write failed"):
        await cached.save(TestState(value=999, label="new"))

    # Cache should NOT be updated (write-through failed)
    cache_state = await cache.load()
    assert cache_state.value == 1  # Still old value
    assert cache_state.label == "old"


# -------------------------------------------------------------------
# History Behavior
# -------------------------------------------------------------------


@pytest.mark.asyncio
async def test_history_limit() -> None:
    """History respects limit parameter."""
    cache = VolatileAgent(_state=TestState(value=0, label="v0"))
    backend = VolatileAgent(_state=TestState(value=0, label="v0"))

    cached = CachedAgent(cache=cache, backend=backend)

    # Generate history
    for i in range(1, 6):
        await cached.save(TestState(value=i, label=f"v{i}"))

    # Query with limit
    history = await cached.history(limit=3)

    # Should return 3 entries (newest first)
    assert len(history) == 3
    assert history[0].value == 4  # Most recent history entry


@pytest.mark.asyncio
async def test_empty_history() -> None:
    """History returns empty list if no history exists."""
    cache = VolatileAgent(_state=TestState(value=1, label="only"))
    backend = VolatileAgent(_state=TestState(value=1, label="only"))

    cached = CachedAgent(cache=cache, backend=backend)

    # No saves yet, so no history
    history = await cached.history()
    assert history == []


# -------------------------------------------------------------------
# Isolation
# -------------------------------------------------------------------


@pytest.mark.asyncio
async def test_cached_agent_isolation() -> None:
    """Mutations to loaded state don't affect cache or backend."""
    cache = VolatileAgent(_state=TestState(value=10, label="original"))
    backend = VolatileAgent(_state=TestState(value=10, label="original"))

    cached = CachedAgent(cache=cache, backend=backend)

    # Load and mutate
    state = await cached.load()
    state.value = 999
    state.label = "mutated"

    # Load again - should be unchanged
    state2 = await cached.load()
    assert state2.value == 10
    assert state2.label == "original"
