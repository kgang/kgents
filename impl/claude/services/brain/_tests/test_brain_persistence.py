"""
Tests for BrainPersistence behavior.

These tests verify the gotchas documented in persistence.py:
1. test_heal_ghosts - Dual-track storage healing
2. test_capture_performance - Fire-and-forget trace recording
3. test_access_tracking - search() updates access_count via touch()

See: services/brain/persistence.py (Teaching section)
"""

from __future__ import annotations

import time
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from agents.d import Datum

# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def mock_dgent():
    """Create a mock D-gent protocol."""
    dgent = MagicMock()
    dgent.put = AsyncMock(return_value="datum-123")
    dgent.get = AsyncMock(return_value=None)  # Default: datum not found
    dgent.delete = AsyncMock(return_value=True)
    return dgent


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
def brain_persistence(mock_table_adapter, mock_dgent):
    """Create a BrainPersistence instance with mocks."""
    from services.brain.persistence import BrainPersistence

    return BrainPersistence(
        table_adapter=mock_table_adapter,
        dgent=mock_dgent,
        embedder=None,
    )


# =============================================================================
# Test: heal_ghosts - Dual-track storage healing
# =============================================================================


class TestHealGhosts:
    """
    Tests for heal_ghosts() behavior.

    Gotcha: Dual-track storage means Crystal table AND D-gent must both succeed.
            If one fails after the other succeeds, you get "ghost" memories.
            heal_ghosts() finds these and recreates the missing D-gent datums.
    """

    @pytest.mark.asyncio
    async def test_heal_ghosts_recreates_missing_datum(self, mock_table_adapter, mock_dgent):
        """heal_ghosts() recreates D-gent datums for crystals with missing datums."""
        from services.brain.persistence import BrainPersistence

        # Create a mock crystal with a datum_id that points to missing datum
        mock_crystal = MagicMock()
        mock_crystal.datum_id = "datum-orphan-123"
        mock_crystal.summary = "This crystal lost its datum"

        # Configure session to return the orphan crystal
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [mock_crystal]
        mock_table_adapter._session.execute = AsyncMock(return_value=mock_result)

        # D-gent returns None for the orphan datum (it's missing)
        mock_dgent.get = AsyncMock(return_value=None)

        persistence = BrainPersistence(
            table_adapter=mock_table_adapter,
            dgent=mock_dgent,
            embedder=None,
        )

        # Call heal_ghosts
        healed_count = await persistence.heal_ghosts()

        # Verify: D-gent.put was called to recreate the datum
        assert healed_count == 1
        mock_dgent.put.assert_called_once()

        # Verify: The recreated datum has correct structure
        recreated_datum = mock_dgent.put.call_args[0][0]
        assert recreated_datum.id == "datum-orphan-123"
        assert b"This crystal lost its datum" in recreated_datum.content
        assert recreated_datum.metadata.get("healed") == "true"

    @pytest.mark.asyncio
    async def test_heal_ghosts_skips_healthy_crystals(self, mock_table_adapter, mock_dgent):
        """heal_ghosts() does not touch crystals with valid D-gent datums."""
        from services.brain.persistence import BrainPersistence

        # Create a healthy crystal with existing datum
        mock_crystal = MagicMock()
        mock_crystal.datum_id = "datum-healthy-456"
        mock_crystal.summary = "Healthy crystal"

        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [mock_crystal]
        mock_table_adapter._session.execute = AsyncMock(return_value=mock_result)

        # D-gent returns a valid datum (not missing)
        mock_dgent.get = AsyncMock(
            return_value=Datum(
                id="datum-healthy-456",
                content=b"Healthy content",
                created_at=time.time(),
                causal_parent=None,
                metadata={},
            )
        )

        persistence = BrainPersistence(
            table_adapter=mock_table_adapter,
            dgent=mock_dgent,
            embedder=None,
        )

        healed_count = await persistence.heal_ghosts()

        # No healing needed
        assert healed_count == 0
        mock_dgent.put.assert_not_called()


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
    async def test_capture_returns_without_waiting_for_trace(self, mock_table_adapter, mock_dgent):
        """capture() returns quickly without blocking on trace recording."""
        from services.brain.persistence import BrainPersistence

        # Track timing
        mock_dgent.put = AsyncMock(return_value="datum-123")

        persistence = BrainPersistence(
            table_adapter=mock_table_adapter,
            dgent=mock_dgent,
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
    async def test_capture_succeeds_even_if_trace_would_fail(self, mock_table_adapter, mock_dgent):
        """capture() succeeds even if trace recording is unavailable."""
        from services.brain.persistence import BrainPersistence

        persistence = BrainPersistence(
            table_adapter=mock_table_adapter,
            dgent=mock_dgent,
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


class TestAccessTracking:
    """
    Tests for access tracking behavior.

    Gotcha: search() updates access_count via touch(). High-frequency searches
            will cause write amplification. Consider batching access updates.
    """

    @pytest.mark.asyncio
    async def test_search_calls_touch_on_matched_crystals(self, mock_table_adapter, mock_dgent):
        """search() calls crystal.touch() for each matched crystal."""
        from services.brain.persistence import BrainPersistence

        # Create mock crystals
        mock_crystal1 = MagicMock()
        mock_crystal1.id = "crystal-1"
        mock_crystal1.summary = "python programming"
        mock_crystal1.datum_id = None
        mock_crystal1.created_at = None
        mock_crystal1.touch = MagicMock()

        mock_crystal2 = MagicMock()
        mock_crystal2.id = "crystal-2"
        mock_crystal2.summary = "python data science"
        mock_crystal2.datum_id = None
        mock_crystal2.created_at = None
        mock_crystal2.touch = MagicMock()

        # Configure session to return crystals
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [mock_crystal1, mock_crystal2]
        mock_table_adapter._session.execute = AsyncMock(return_value=mock_result)

        persistence = BrainPersistence(
            table_adapter=mock_table_adapter,
            dgent=mock_dgent,
            embedder=None,
        )

        # Search for python-related content
        results = await persistence.search(query="python", limit=10)

        # Both crystals match "python" - both should have touch() called
        assert len(results) == 2
        mock_crystal1.touch.assert_called_once()
        mock_crystal2.touch.assert_called_once()

    @pytest.mark.asyncio
    async def test_search_commits_after_touching(self, mock_table_adapter, mock_dgent):
        """search() commits the session after touch() calls to persist access updates."""
        from services.brain.persistence import BrainPersistence

        mock_crystal = MagicMock()
        mock_crystal.id = "crystal-1"
        mock_crystal.summary = "test content"
        mock_crystal.datum_id = None
        mock_crystal.created_at = None
        mock_crystal.touch = MagicMock()

        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [mock_crystal]
        mock_table_adapter._session.execute = AsyncMock(return_value=mock_result)

        persistence = BrainPersistence(
            table_adapter=mock_table_adapter,
            dgent=mock_dgent,
            embedder=None,
        )

        await persistence.search(query="test", limit=10)

        # Session should be committed to persist the access_count update
        mock_table_adapter._session.commit.assert_called()


__all__ = ["TestHealGhosts", "TestCapturePerformance", "TestAccessTracking"]
