"""
Tests for Brain Differance Integration (Phase 6B).

Verifies that Brain operations record traces correctly:
- capture() → trace with alternatives
- surface() → trace with alternatives
- delete() → trace with alternatives
- search/get/list → NO traces (read-only)

See: plans/differance-crown-jewel-wiring.md (Phase 6B)
"""

from __future__ import annotations

import pytest

from agents.d import MemoryBackend, TableAdapter
from agents.differance.integration import (
    clear_trace_buffer,
    create_isolated_buffer,
    get_trace_buffer,
    reset_isolated_buffer,
)
from services.brain.persistence import BrainPersistence


# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture(autouse=True)
def differance_buffer():
    """Create an isolated trace buffer for each test."""
    buffer = create_isolated_buffer()
    yield buffer
    reset_isolated_buffer()


@pytest.fixture
def memory_backend():
    """Create a fresh D-gent memory backend."""
    return MemoryBackend()


@pytest.fixture
def mock_table_adapter(mocker):
    """Create a mock TableAdapter for testing."""
    # Create a minimal mock that supports async context manager
    mock_adapter = mocker.MagicMock()

    # Mock session factory to return an async context manager
    mock_session = mocker.AsyncMock()
    mock_session.add = mocker.MagicMock()
    mock_session.commit = mocker.AsyncMock()
    mock_session.delete = mocker.AsyncMock()
    mock_session.get = mocker.AsyncMock(return_value=None)
    mock_session.execute = mocker.AsyncMock()

    # Make session factory an async context manager
    async def async_session_factory():
        return mock_session

    mock_adapter.session_factory = mocker.MagicMock()
    mock_adapter.session_factory.return_value.__aenter__ = mocker.AsyncMock(
        return_value=mock_session
    )
    mock_adapter.session_factory.return_value.__aexit__ = mocker.AsyncMock(
        return_value=None
    )

    return mock_adapter, mock_session


# =============================================================================
# Brain Capture Tests
# =============================================================================


class TestBrainCaptureTraces:
    """Tests for capture() trace recording."""

    @pytest.mark.asyncio
    async def test_capture_records_trace(self, memory_backend, mock_table_adapter, differance_buffer):
        """capture() records a trace with alternatives."""
        mock_adapter, mock_session = mock_table_adapter

        persistence = BrainPersistence(
            table_adapter=mock_adapter,
            dgent=memory_backend,
        )

        # Perform capture
        result = await persistence.capture(
            content="Python is great for data science",
            tags=["programming", "data"],
            source_type="capture",
        )

        # Allow async trace recording to complete
        import asyncio
        await asyncio.sleep(0.01)

        # Verify trace was recorded
        buffer = get_trace_buffer()
        assert len(buffer) >= 1, "Expected at least one trace in buffer"

        # Find the capture trace
        capture_traces = [t for t in buffer if t.operation == "capture"]
        assert len(capture_traces) == 1, f"Expected 1 capture trace, got {len(capture_traces)}"

        trace = capture_traces[0]
        assert trace.output == result.crystal_id
        assert "brain" in trace.context.lower()
        assert len(trace.alternatives) >= 1, "Expected alternatives for capture"

    @pytest.mark.asyncio
    async def test_capture_trace_has_correct_alternatives(
        self, memory_backend, mock_table_adapter, differance_buffer
    ):
        """capture() trace includes auto_tag and defer_embedding alternatives."""
        mock_adapter, mock_session = mock_table_adapter

        persistence = BrainPersistence(
            table_adapter=mock_adapter,
            dgent=memory_backend,
        )

        await persistence.capture(content="Test content")

        import asyncio
        await asyncio.sleep(0.01)

        buffer = get_trace_buffer()
        capture_traces = [t for t in buffer if t.operation == "capture"]
        assert len(capture_traces) == 1

        trace = capture_traces[0]
        alt_ops = [alt.operation for alt in trace.alternatives]
        assert "auto_tag" in alt_ops, "Expected auto_tag alternative"
        assert "defer_embedding" in alt_ops, "Expected defer_embedding alternative"

    @pytest.mark.asyncio
    async def test_capture_truncates_content_in_trace(
        self, memory_backend, mock_table_adapter, differance_buffer
    ):
        """capture() truncates content to 100 chars in trace inputs."""
        mock_adapter, mock_session = mock_table_adapter

        persistence = BrainPersistence(
            table_adapter=mock_adapter,
            dgent=memory_backend,
        )

        long_content = "x" * 500
        await persistence.capture(content=long_content)

        import asyncio
        await asyncio.sleep(0.01)

        buffer = get_trace_buffer()
        capture_traces = [t for t in buffer if t.operation == "capture"]
        assert len(capture_traces) == 1

        trace = capture_traces[0]
        # Inputs should be truncated to 100 chars
        assert len(trace.inputs[0]) == 100


# =============================================================================
# Brain Delete Tests
# =============================================================================


class TestBrainDeleteTraces:
    """Tests for delete() trace recording."""

    @pytest.mark.asyncio
    async def test_delete_records_trace(self, memory_backend, mock_table_adapter, differance_buffer):
        """delete() records a trace with alternatives."""
        mock_adapter, mock_session = mock_table_adapter

        # Mock crystal exists for deletion
        mock_crystal = type("Crystal", (), {
            "id": "crystal-test123",
            "summary": "Test crystal content",
            "datum_id": None,
        })()
        mock_session.get = mock_session.get.return_value = mock_crystal

        persistence = BrainPersistence(
            table_adapter=mock_adapter,
            dgent=memory_backend,
        )

        # Perform delete
        result = await persistence.delete("crystal-test123")

        import asyncio
        await asyncio.sleep(0.01)

        # Verify trace was recorded
        buffer = get_trace_buffer()
        delete_traces = [t for t in buffer if t.operation == "delete"]
        assert len(delete_traces) == 1, f"Expected 1 delete trace, got {len(delete_traces)}"

        trace = delete_traces[0]
        assert "crystal-test123" in trace.inputs[0]
        assert len(trace.alternatives) >= 1, "Expected alternatives for delete"


# =============================================================================
# Read Operations Should NOT Trace
# =============================================================================


class TestBrainReadOperationsNoTrace:
    """Tests that read operations don't create traces."""

    @pytest.mark.asyncio
    async def test_search_does_not_record_trace(
        self, memory_backend, mock_table_adapter, differance_buffer
    ):
        """search() should NOT record a trace (read-only, high frequency)."""
        mock_adapter, mock_session = mock_table_adapter

        # Mock empty result
        mock_result = type("Result", (), {"scalars": lambda: type("S", (), {"all": lambda: []})()})()
        mock_session.execute.return_value = mock_result

        persistence = BrainPersistence(
            table_adapter=mock_adapter,
            dgent=memory_backend,
        )

        await persistence.search("test query", limit=5)

        import asyncio
        await asyncio.sleep(0.01)

        buffer = get_trace_buffer()
        search_traces = [t for t in buffer if t.operation == "search"]
        assert len(search_traces) == 0, "search() should not create traces"

    @pytest.mark.asyncio
    async def test_get_by_id_does_not_record_trace(
        self, memory_backend, mock_table_adapter, differance_buffer
    ):
        """get_by_id() should NOT record a trace (read-only)."""
        mock_adapter, mock_session = mock_table_adapter
        mock_session.get.return_value = None

        persistence = BrainPersistence(
            table_adapter=mock_adapter,
            dgent=memory_backend,
        )

        await persistence.get_by_id("nonexistent")

        import asyncio
        await asyncio.sleep(0.01)

        buffer = get_trace_buffer()
        get_traces = [t for t in buffer if t.operation == "get_by_id"]
        assert len(get_traces) == 0, "get_by_id() should not create traces"


# =============================================================================
# Buffer Isolation Tests
# =============================================================================


class TestBufferIsolation:
    """Tests that buffer isolation works correctly."""

    @pytest.mark.asyncio
    async def test_isolated_buffer_is_empty_at_start(self, differance_buffer):
        """Each test starts with an empty isolated buffer."""
        assert len(differance_buffer) == 0

    @pytest.mark.asyncio
    async def test_clear_buffer_works(self, differance_buffer):
        """clear_trace_buffer() returns and clears contents."""
        from agents.differance.integration import record_trace_sync

        record_trace_sync(
            operation="test",
            inputs=("a",),
            output="b",
            context="test",
        )

        assert len(differance_buffer) == 1

        cleared = clear_trace_buffer()
        assert len(cleared) == 1
        assert len(differance_buffer) == 0
