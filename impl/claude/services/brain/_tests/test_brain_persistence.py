"""
Tests for BrainPersistence behavior.

These tests verify the gotchas documented in persistence.py:
1. test_heal_ghosts - Dual-track storage healing
2. test_capture_performance - Fire-and-forget trace recording
3. test_access_tracking - search() updates access_count via touch()

Teaching (Test Patterns):
    TIMING TESTS use `preferred_backend="memory"` to avoid Postgres index
    creation lock contention (15-17s) under parallel xdist execution.
    We're testing capture() latency, not Postgres performance.

    See: docs/skills/test-patterns.md (Pattern 1: Memory Backend)

See: services/brain/persistence.py (Teaching section)
"""

from __future__ import annotations

import time
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from agents.d import Datum
from agents.d.universe import Universe

# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def mock_table_adapter():
    """Create a mock TableAdapter with async session factory."""
    adapter = MagicMock()

    # Mock session factory as an async context manager
    mock_session = MagicMock()
    mock_session.add = MagicMock()
    mock_session.commit = AsyncMock()
    mock_session.execute = AsyncMock()
    mock_session.get = AsyncMock(return_value=None)
    mock_session.delete = AsyncMock()

    # Create async context manager
    class AsyncSessionContextManager:
        async def __aenter__(self):
            return mock_session

        async def __aexit__(self, *args):
            pass

    adapter.session_factory = MagicMock(return_value=AsyncSessionContextManager())
    adapter._session = mock_session  # For test access
    return adapter


@pytest.fixture
def brain_persistence(mock_table_adapter):
    """Create a BrainPersistence instance with mocks.

    Uses memory backend to avoid Postgres lock contention in parallel CI.
    """
    from services.brain.persistence import BrainPersistence

    universe = Universe(namespace="test", preferred_backend="memory")
    return BrainPersistence(
        universe=universe,
        table_adapter=mock_table_adapter,
        embedder=None,
    )


# =============================================================================
# Test: heal_ghosts - Dual-track storage healing
# =============================================================================


class TestHealGhosts:
    """
    Tests for heal_ghosts() behavior.

    Note: With Universe, ghosts shouldn't exist - all crystals are stored
    as complete datum+schema pairs. heal_ghosts() exists for backward
    compatibility but always returns 0.
    """

    @pytest.mark.asyncio
    async def test_heal_ghosts_always_returns_zero_with_universe(self, mock_table_adapter):
        """heal_ghosts() returns 0 with Universe (no ghosts possible)."""
        from services.brain.persistence import BrainPersistence

        universe = Universe(namespace="test")
        persistence = BrainPersistence(
            universe=universe,
            table_adapter=mock_table_adapter,
            embedder=None,
        )

        # With Universe, heal_ghosts always returns 0
        healed_count = await persistence.heal_ghosts()

        assert healed_count == 0


# =============================================================================
# Test: capture_performance - Fire-and-forget trace recording
# =============================================================================


class TestCapturePerformance:
    """
    Tests for capture() performance behavior.

    Gotcha: capture() returns immediately but trace recording is fire-and-forget.
            Never await the trace task or you'll block the hot path.
    """

    @pytest.mark.asyncio
    async def test_capture_returns_without_waiting_for_trace(self, mock_table_adapter):
        """capture() returns quickly without blocking on trace recording.

        Note: Uses in-memory backend to avoid Postgres index creation lock
        contention during parallel CI execution. We're testing capture()
        behavior (fire-and-forget trace), not Postgres performance.
        """
        from services.brain.persistence import BrainPersistence

        # Use memory backend to avoid Postgres lock contention in parallel CI
        universe = Universe(namespace="test", preferred_backend="memory")
        persistence = BrainPersistence(
            universe=universe,
            table_adapter=mock_table_adapter,
            embedder=None,
        )

        # Capture should be fast (trace is fire-and-forget)
        start = time.perf_counter()
        result = await persistence.capture(content="Test content")
        elapsed = time.perf_counter() - start

        # capture() should complete quickly (< 1 second)
        # The trace recording runs in background, doesn't block
        assert elapsed < 1.0, f"capture() took {elapsed:.2f}s, should be < 1s"
        assert result.crystal_id is not None

    @pytest.mark.asyncio
    async def test_capture_succeeds_even_if_trace_would_fail(self, mock_table_adapter):
        """capture() succeeds even if trace recording is unavailable."""
        from services.brain.persistence import BrainPersistence

        # Use memory backend to avoid Postgres lock contention in parallel CI
        universe = Universe(namespace="test", preferred_backend="memory")
        persistence = BrainPersistence(
            universe=universe,
            table_adapter=mock_table_adapter,
            embedder=None,
        )

        # Patch DifferanceIntegration.record to raise an exception
        # This simulates trace recording failure
        with patch.object(
            persistence._differance, "record", side_effect=RuntimeError("Trace failed")
        ):
            # capture() should still succeed (trace is fire-and-forget)
            result = await persistence.capture(content="Test content")

            assert result.crystal_id is not None
            assert result.content == "Test content"


# =============================================================================
# Test: access_tracking - search() updates access_count via touch()
# =============================================================================


class TestSearch:
    """
    Tests for search() behavior.

    Note: search() now uses Universe for querying, not SQLAlchemy table_adapter.
    Access tracking is deferred (TODO: implement via Universe updates).
    """

    @pytest.mark.asyncio
    async def test_search_returns_matching_crystals(self, mock_table_adapter):
        """search() returns crystals matching the query via Universe."""
        from services.brain.persistence import BrainPersistence

        universe = Universe(namespace="test")
        persistence = BrainPersistence(
            universe=universe,
            table_adapter=mock_table_adapter,
            embedder=None,
        )

        # Capture some content first
        await persistence.capture(content="Python programming is great for data science")
        await persistence.capture(content="JavaScript is used for web development")

        # Search for python-related content
        results = await persistence.search(query="python", limit=10)

        # Should find the Python crystal
        assert len(results) >= 1
        assert any("python" in r.content.lower() for r in results)

    @pytest.mark.asyncio
    async def test_search_returns_empty_for_no_matches(self, mock_table_adapter):
        """search() returns empty list when no crystals match."""
        from services.brain.persistence import BrainPersistence

        universe = Universe(namespace="test")
        persistence = BrainPersistence(
            universe=universe,
            table_adapter=mock_table_adapter,
            embedder=None,
        )

        # Capture content that won't match
        await persistence.capture(content="JavaScript is used for web development")

        # Search for something not in the content
        results = await persistence.search(query="quantum", limit=10)

        # Should return empty
        assert len(results) == 0


__all__ = ["TestHealGhosts", "TestCapturePerformance", "TestSearch"]
