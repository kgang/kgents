"""
Tests for Portal Marks: Witness integration for portal expansion events.

Tests verify:
- Depth filtering (depth 1 = no mark, depth 2+ = mark)
- Evidence edge type always marks
- Fire-and-forget behavior (errors don't propagate)
- Trail save marks

Teaching:
    gotcha: These tests use the mock bus pattern. The actual bus
            is not tested here - see test_bus.py for bus tests.
            We only verify that portal_marks emits to the bus correctly.
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from services.witness.portal_marks import (
    mark_portal_collapse,
    mark_portal_expansion,
    mark_trail_save,
)

# =============================================================================
# Test Fixtures
# =============================================================================


@pytest.fixture
def mock_bus():
    """Mock the witness synergy bus."""
    bus = AsyncMock()
    bus.publish = AsyncMock()
    return bus


@pytest.fixture
def mock_trail():
    """Create a mock Trail for testing."""
    trail = MagicMock()
    trail.id = "trail-test-123"
    trail.name = "Test Trail"
    trail.steps = [MagicMock(), MagicMock(), MagicMock()]  # 3 steps
    trail.annotations = []

    # Mock step attributes
    for i, step in enumerate(trail.steps):
        step.node_path = f"path_{i}"
        step.edge_type = "expand" if i > 0 else None
        step.annotations = []

    trail.as_outline = MagicMock(return_value="Trail outline")
    return trail


# =============================================================================
# Portal Expansion Tests
# =============================================================================


class TestMarkPortalExpansion:
    """Tests for mark_portal_expansion()."""

    @pytest.mark.asyncio
    async def test_depth_1_not_marked(self, mock_bus):
        """Depth 1 expansions should not emit marks (exploratory)."""
        with patch("services.witness.portal_marks.get_synergy_bus", return_value=mock_bus):
            result = await mark_portal_expansion(
                file_path="test.py",
                edge_type="imports",
                portal_path=["imports"],  # depth 1
                depth=1,
                observer_archetype="developer",
            )

        assert result is None
        mock_bus.publish.assert_not_called()

    @pytest.mark.asyncio
    async def test_depth_2_emits_mark(self, mock_bus):
        """Depth 2+ expansions SHOULD emit marks."""
        with patch("services.witness.portal_marks.get_synergy_bus", return_value=mock_bus):
            result = await mark_portal_expansion(
                file_path="test.py",
                edge_type="imports",
                portal_path=["imports", "pathlib"],  # depth 2
                depth=2,
                observer_archetype="developer",
            )

        assert result is not None
        assert result.startswith("mark-")
        mock_bus.publish.assert_called_once()

    @pytest.mark.asyncio
    async def test_depth_3_emits_mark(self, mock_bus):
        """Depth 3 expansions emit marks with moderate evidence strength."""
        with patch("services.witness.portal_marks.get_synergy_bus", return_value=mock_bus):
            result = await mark_portal_expansion(
                file_path="test.py",
                edge_type="calls",
                portal_path=["imports", "pathlib", "Path"],  # depth 3
                depth=3,
                observer_archetype="developer",
            )

        assert result is not None
        mock_bus.publish.assert_called_once()

        # Check the published event has correct structure
        call_args = mock_bus.publish.call_args
        topic = call_args[0][0]
        event = call_args[0][1]

        assert topic == "witness.trail.captured"
        assert event["action"] == "exploration.portal.expand"
        assert event["depth"] == 3
        assert event["edge_type"] == "calls"

    @pytest.mark.asyncio
    async def test_evidence_edge_always_marks(self, mock_bus):
        """Evidence edge type always marks, even at depth 1."""
        with patch("services.witness.portal_marks.get_synergy_bus", return_value=mock_bus):
            result = await mark_portal_expansion(
                file_path="test.py",
                edge_type="evidence",
                portal_path=["evidence"],  # depth 1 but evidence edge
                depth=1,
                observer_archetype="developer",
            )

        assert result is not None
        mock_bus.publish.assert_called_once()

    @pytest.mark.asyncio
    async def test_errors_dont_propagate(self, mock_bus):
        """Errors should be logged, not raised (fire-and-forget)."""
        mock_bus.publish.side_effect = Exception("Bus error!")

        with patch("services.witness.portal_marks.get_synergy_bus", return_value=mock_bus):
            # Should not raise
            result = await mark_portal_expansion(
                file_path="test.py",
                edge_type="imports",
                portal_path=["imports", "pathlib"],
                depth=2,
                observer_archetype="developer",
            )

        # Should return None on error
        assert result is None

    @pytest.mark.asyncio
    async def test_mark_id_format(self, mock_bus):
        """Mark IDs should follow the mark-{uuid} format."""
        with patch("services.witness.portal_marks.get_synergy_bus", return_value=mock_bus):
            result = await mark_portal_expansion(
                file_path="test.py",
                edge_type="imports",
                portal_path=["imports", "pathlib"],
                depth=2,
                observer_archetype="developer",
            )

        assert result is not None
        assert result.startswith("mark-")
        assert len(result) == 17  # "mark-" + 12 hex chars


# =============================================================================
# Portal Collapse Tests
# =============================================================================


class TestMarkPortalCollapse:
    """Tests for mark_portal_collapse()."""

    @pytest.mark.asyncio
    async def test_depth_2_not_marked(self, mock_bus):
        """Depth 2 collapses should not emit marks (less signal)."""
        with patch("services.witness.portal_marks.get_synergy_bus", return_value=mock_bus):
            result = await mark_portal_collapse(
                file_path="test.py",
                portal_path=["imports", "pathlib"],
                depth=2,
                observer_archetype="developer",
            )

        assert result is None
        mock_bus.publish.assert_not_called()

    @pytest.mark.asyncio
    async def test_depth_3_emits_mark(self, mock_bus):
        """Depth 3+ collapses emit marks."""
        with patch("services.witness.portal_marks.get_synergy_bus", return_value=mock_bus):
            result = await mark_portal_collapse(
                file_path="test.py",
                portal_path=["imports", "pathlib", "Path"],
                depth=3,
                observer_archetype="developer",
            )

        assert result is not None
        mock_bus.publish.assert_called_once()


# =============================================================================
# Trail Save Tests
# =============================================================================


class TestMarkTrailSave:
    """Tests for mark_trail_save()."""

    @pytest.mark.asyncio
    async def test_trail_save_emits_mark(self, mock_trail):
        """Trail save should emit mark via trail_bridge."""
        # Patch at the source module, not the import point
        with patch("services.witness.trail_bridge.emit_trail_as_mark") as mock_emit:
            mock_mark = MagicMock()
            mock_mark.id = "mark-trail-123"
            mock_emit.return_value = mock_mark

            result = await mark_trail_save(mock_trail)

        assert result == "mark-trail-123"
        mock_emit.assert_called_once_with(mock_trail)

    @pytest.mark.asyncio
    async def test_trail_save_errors_dont_propagate(self, mock_trail):
        """Trail save errors should not propagate."""
        with patch("services.witness.trail_bridge.emit_trail_as_mark") as mock_emit:
            mock_emit.side_effect = Exception("Trail bridge error!")

            # Should not raise
            result = await mark_trail_save(mock_trail)

        assert result is None


# =============================================================================
# Integration Pattern Tests
# =============================================================================


class TestPortalMarksPatterns:
    """Tests for portal marks usage patterns."""

    @pytest.mark.asyncio
    async def test_expansion_sequence_marks_correctly(self, mock_bus):
        """Simulates a typical expansion sequence."""
        with patch("services.witness.portal_marks.get_synergy_bus", return_value=mock_bus):
            # First expansion (depth 1) - no mark
            r1 = await mark_portal_expansion(
                file_path="core.py",
                edge_type="imports",
                portal_path=["imports"],
                depth=1,
                observer_archetype="developer",
            )
            assert r1 is None

            # Second expansion (depth 2) - mark!
            r2 = await mark_portal_expansion(
                file_path="core.py",
                edge_type="imports",
                portal_path=["imports", "pathlib"],
                depth=2,
                observer_archetype="developer",
            )
            assert r2 is not None

            # Third expansion (depth 3) - mark!
            r3 = await mark_portal_expansion(
                file_path="core.py",
                edge_type="calls",
                portal_path=["imports", "pathlib", "Path"],
                depth=3,
                observer_archetype="developer",
            )
            assert r3 is not None

        # Only 2 marks emitted (depth 2 and 3)
        assert mock_bus.publish.call_count == 2

    @pytest.mark.asyncio
    async def test_different_edge_types_captured(self, mock_bus):
        """Different edge types should be captured in mark metadata."""
        with patch("services.witness.portal_marks.get_synergy_bus", return_value=mock_bus):
            edge_types = ["imports", "tests", "calls", "implements"]

            for edge_type in edge_types:
                await mark_portal_expansion(
                    file_path="core.py",
                    edge_type=edge_type,
                    portal_path=["a", "b"],  # depth 2
                    depth=2,
                    observer_archetype="developer",
                )

        assert mock_bus.publish.call_count == 4

        # Check each call captured the edge type
        for i, call in enumerate(mock_bus.publish.call_args_list):
            event = call[0][1]
            assert event["edge_type"] == edge_types[i]
