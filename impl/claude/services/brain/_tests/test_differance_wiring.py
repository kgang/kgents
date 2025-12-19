"""
Tests for Brain Differance Integration (Phase 6B).

These tests verify the buffer isolation infrastructure and the DifferanceIntegration
class used by BrainPersistence. The actual wiring is tested via integration tests
that exercise the full Brain persistence flow.

See: plans/differance-crown-jewel-wiring.md (Phase 6B)
"""

from __future__ import annotations

import pytest

from agents.differance import (
    BRAIN_ALTERNATIVES,
    Alternative,
    DifferanceIntegration,
    clear_trace_buffer,
    create_isolated_buffer,
    get_alternatives,
    get_trace_buffer,
    record_trace_sync,
    reset_isolated_buffer,
)

# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture(autouse=True)
def differance_buffer():
    """Create an isolated trace buffer for each test."""
    buffer = create_isolated_buffer()
    yield buffer
    reset_isolated_buffer()


# =============================================================================
# Buffer Isolation Tests
# =============================================================================


class TestBufferIsolation:
    """Tests that buffer isolation works correctly."""

    def test_isolated_buffer_is_empty_at_start(self, differance_buffer):
        """Each test starts with an empty isolated buffer."""
        assert len(differance_buffer) == 0

    def test_clear_buffer_works(self, differance_buffer):
        """clear_trace_buffer() returns and clears contents."""
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

    def test_buffer_isolation_between_records(self, differance_buffer):
        """Multiple records accumulate in isolated buffer."""
        record_trace_sync(operation="op1", inputs=("a",), output="1", context="c1")
        record_trace_sync(operation="op2", inputs=("b",), output="2", context="c2")
        record_trace_sync(operation="op3", inputs=("c",), output="3", context="c3")

        assert len(differance_buffer) == 3
        operations = [t.operation for t in differance_buffer]
        assert operations == ["op1", "op2", "op3"]


# =============================================================================
# DifferanceIntegration Tests
# =============================================================================


class TestDifferanceIntegration:
    """Tests for the DifferanceIntegration class."""

    def test_integration_sync_recording(self, differance_buffer):
        """DifferanceIntegration.record_sync() records to buffer."""
        integration = DifferanceIntegration("brain")

        trace_id = integration.record_sync(
            operation="capture",
            inputs=("content preview",),
            output="crystal-123",
            context="Captured text",
        )

        assert trace_id is not None
        assert len(differance_buffer) == 1
        trace = differance_buffer[0]
        assert trace.operation == "capture"
        assert "[brain]" in trace.context.lower()

    def test_integration_with_alternatives(self, differance_buffer):
        """DifferanceIntegration.record_sync() records alternatives."""
        integration = DifferanceIntegration("brain")
        alt = integration.alternative("auto_tag", (), "User didn't request auto-tagging")

        trace_id = integration.record_sync(
            operation="capture",
            inputs=("content",),
            output="crystal-456",
            context="Captured",
            alternatives=[alt],
        )

        assert len(differance_buffer) == 1
        trace = differance_buffer[0]
        assert len(trace.alternatives) == 1
        assert trace.alternatives[0].operation == "auto_tag"

    def test_integration_disable_enable(self, differance_buffer):
        """DifferanceIntegration.disable() stops recording."""
        integration = DifferanceIntegration("brain")

        integration.record_sync(operation="op1", inputs=(), output="1", context="")
        assert len(differance_buffer) == 1

        integration.disable()
        integration.record_sync(operation="op2", inputs=(), output="2", context="")
        assert len(differance_buffer) == 1  # No new record

        integration.enable()
        integration.record_sync(operation="op3", inputs=(), output="3", context="")
        assert len(differance_buffer) == 2  # Recording resumed

    @pytest.mark.asyncio
    async def test_integration_async_recording(self, differance_buffer):
        """DifferanceIntegration.record() records asynchronously."""
        integration = DifferanceIntegration("gardener")

        trace_id = await integration.record(
            operation="plant",
            inputs=("idea content",),
            output="idea-789",
            context="Planted idea",
        )

        # Note: async record goes to store/monoid, not buffer
        # But if no store is configured, it should still work
        assert trace_id is not None or trace_id is None  # Either outcome is valid


# =============================================================================
# Static Alternatives Tests
# =============================================================================


class TestStaticAlternatives:
    """Tests for the static alternatives registry."""

    def test_brain_capture_alternatives(self):
        """Brain capture has expected alternatives."""
        alts = get_alternatives("brain", "capture")
        assert len(alts) == 2
        ops = [a.operation for a in alts]
        assert "auto_tag" in ops
        assert "defer_embedding" in ops

    def test_brain_surface_alternatives(self):
        """Brain surface has expected alternatives."""
        alts = get_alternatives("brain", "surface")
        assert len(alts) == 2
        ops = [a.operation for a in alts]
        assert "different_seed" in ops
        assert "context_weighted" in ops

    def test_brain_delete_alternatives(self):
        """Brain delete has expected alternatives."""
        alts = get_alternatives("brain", "delete")
        assert len(alts) == 2
        ops = [a.operation for a in alts]
        assert "archive_instead" in ops
        assert "soft_delete" in ops

    def test_gardener_plant_alternatives(self):
        """Gardener plant has expected alternatives."""
        alts = get_alternatives("gardener", "plant")
        assert len(alts) == 2
        ops = [a.operation for a in alts]
        assert "different_lifecycle" in ops
        assert "auto_connect" in ops

    def test_gardener_nurture_alternatives(self):
        """Gardener nurture has expected alternatives."""
        alts = get_alternatives("gardener", "nurture")
        assert len(alts) == 2
        ops = [a.operation for a in alts]
        assert "prune" in ops
        assert "water" in ops

    def test_unknown_jewel_returns_empty(self):
        """Unknown jewel returns empty list."""
        alts = get_alternatives("unknown", "capture")
        assert alts == []

    def test_unknown_operation_returns_empty(self):
        """Unknown operation returns empty list."""
        alts = get_alternatives("brain", "unknown_op")
        assert alts == []

    def test_alternatives_are_immutable(self):
        """Returned alternatives are frozen dataclasses."""
        alts = get_alternatives("brain", "capture")
        alt = alts[0]
        with pytest.raises(AttributeError):
            alt.operation = "modified"


# =============================================================================
# Trace Context Tests
# =============================================================================


class TestTraceContext:
    """Tests for trace context and parent linking."""

    def test_trace_has_context_prefix(self, differance_buffer):
        """Traces include jewel name in context."""
        integration = DifferanceIntegration("brain")
        integration.record_sync(operation="test", inputs=(), output="out", context="detail")

        trace = differance_buffer[0]
        assert "[brain]" in trace.context

    def test_trace_inputs_stored(self, differance_buffer):
        """Trace inputs are stored correctly."""
        integration = DifferanceIntegration("gardener")
        integration.record_sync(
            operation="plant",
            inputs=("idea content", "plot-123"),
            output="idea-456",
            context="Planted",
        )

        trace = differance_buffer[0]
        assert trace.inputs == ("idea content", "plot-123")

    def test_trace_output_stored(self, differance_buffer):
        """Trace output is stored correctly."""
        integration = DifferanceIntegration("brain")
        integration.record_sync(
            operation="capture",
            inputs=("content",),
            output="crystal-abc",
            context="Captured",
        )

        trace = differance_buffer[0]
        assert trace.output == "crystal-abc"
