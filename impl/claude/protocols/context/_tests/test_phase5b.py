"""
Phase 5B Tests: Trail → Witness Integration.

Tests for:
- Auto-witness on threshold (5+ steps or 2+ annotations)
- CLI `kg context trail witness` command
- Trail appears in witness marks

"The trail IS evidence. The mark IS the witness."
"""

import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from datetime import datetime

from protocols.agentese.contexts.self_context import (
    ContextNavNode,
    ContextGraph,
    ContextNode,
    Trail,
    TrailStep,
    Observer,
    set_context_nav_node,
)


# =============================================================================
# Test Fixtures
# =============================================================================


@pytest.fixture
def observer() -> Observer:
    """Default test observer."""
    return Observer(archetype="developer", capabilities=frozenset({"debug"}))


@pytest.fixture
def nav_node() -> ContextNavNode:
    """Fresh ContextNavNode for each test."""
    node = ContextNavNode()
    set_context_nav_node(node)
    return node


@pytest.fixture
def trail_with_5_steps(observer: Observer) -> Trail:
    """Create a trail with 5 steps (threshold for auto-witness)."""
    steps = [
        TrailStep(node_path="world.auth", edge_type=None),
        TrailStep(node_path="world.auth.middleware", edge_type="contains"),
        TrailStep(node_path="world.auth.tests", edge_type="tests"),
        TrailStep(node_path="world.auth.tests.test_auth", edge_type="contains"),
        TrailStep(node_path="world.auth.tests.test_edge", edge_type="related"),
    ]
    return Trail(
        id="trail-5-steps",
        name="Auth Investigation",
        created_by=observer,
        steps=steps,
    )


@pytest.fixture
def trail_with_annotations(observer: Observer) -> Trail:
    """Create a trail with 2+ annotations (threshold for auto-witness)."""
    steps = [
        TrailStep(
            node_path="world.auth",
            edge_type=None,
            annotations="Starting investigation",
        ),
        TrailStep(
            node_path="world.auth.bug",
            edge_type="related",
            annotations="Found the bug here!",
        ),
    ]
    return Trail(
        id="trail-annotated",
        name="Bug Hunt",
        created_by=observer,
        steps=steps,
    )


@pytest.fixture
def trail_under_threshold(observer: Observer) -> Trail:
    """Create a trail under all thresholds."""
    steps = [
        TrailStep(node_path="world.start", edge_type=None),
        TrailStep(node_path="world.next", edge_type="related"),
    ]
    return Trail(
        id="trail-small",
        name="Quick Look",
        created_by=observer,
        steps=steps,
    )


# =============================================================================
# Test: _current_trail Property
# =============================================================================


class TestCurrentTrailProperty:
    """Tests for ContextNavNode._current_trail property."""

    async def test_current_trail_returns_none_without_graph(
        self, nav_node: ContextNavNode
    ):
        """Returns None when no graph is initialized."""
        assert nav_node._current_trail is None

    async def test_current_trail_returns_trail_from_graph(
        self, nav_node: ContextNavNode, observer: Observer
    ):
        """Returns Trail object from graph's trail steps."""
        # Initialize graph with some steps
        graph = nav_node._ensure_graph(observer)
        graph.trail = [
            TrailStep(node_path="world.test", edge_type=None),
        ]

        trail = nav_node._current_trail
        assert trail is not None
        assert len(trail.steps) == 1
        assert trail.steps[0].node_path == "world.test"

    async def test_current_trail_setter_updates_graph(
        self, nav_node: ContextNavNode, observer: Observer, trail_with_5_steps: Trail
    ):
        """Setting _current_trail updates the graph's trail."""
        # Initialize graph
        graph = nav_node._ensure_graph(observer)
        assert len(graph.trail) == 0

        # Set trail
        nav_node._current_trail = trail_with_5_steps

        # Verify graph updated
        assert len(graph.trail) == 5


# =============================================================================
# Test: Auto-Witness Threshold
# =============================================================================


class TestAutoWitnessThreshold:
    """Tests for auto-witness on threshold."""

    async def test_no_witness_under_threshold(
        self, nav_node: ContextNavNode, observer: Observer
    ):
        """Does not auto-witness when under threshold."""
        graph = nav_node._ensure_graph(observer)
        graph.trail = [
            TrailStep(node_path="world.a", edge_type=None),
            TrailStep(node_path="world.b", edge_type="related"),
        ]

        with patch(
            "services.witness.trail_bridge.emit_trail_as_mark"
        ) as mock_emit:
            mock_emit.return_value = AsyncMock()

            await nav_node._maybe_auto_witness(graph)

            mock_emit.assert_not_called()

    async def test_auto_witness_at_5_steps(
        self, nav_node: ContextNavNode, observer: Observer
    ):
        """Auto-witnesses when trail reaches 5 steps."""
        graph = nav_node._ensure_graph(observer)
        graph.trail = [
            TrailStep(node_path=f"world.node{i}", edge_type="related" if i > 0 else None)
            for i in range(5)
        ]

        with patch(
            "services.witness.trail_bridge.emit_trail_as_mark"
        ) as mock_emit:
            mock_emit.return_value = AsyncMock()

            await nav_node._maybe_auto_witness(graph)

            mock_emit.assert_called_once()

    async def test_auto_witness_at_2_annotations(
        self, nav_node: ContextNavNode, observer: Observer
    ):
        """Auto-witnesses when trail has 2+ annotations."""
        graph = nav_node._ensure_graph(observer)
        graph.trail = [
            TrailStep(node_path="world.a", edge_type=None, annotations="Note 1"),
            TrailStep(node_path="world.b", edge_type="related", annotations="Note 2"),
        ]

        with patch(
            "services.witness.trail_bridge.emit_trail_as_mark"
        ) as mock_emit:
            mock_emit.return_value = AsyncMock()

            await nav_node._maybe_auto_witness(graph)

            mock_emit.assert_called_once()

    async def test_auto_witness_only_once(
        self, nav_node: ContextNavNode, observer: Observer
    ):
        """Only auto-witnesses once per threshold crossing."""
        graph = nav_node._ensure_graph(observer)
        graph.trail = [
            TrailStep(node_path=f"world.node{i}", edge_type="related" if i > 0 else None)
            for i in range(5)
        ]

        with patch(
            "services.witness.trail_bridge.emit_trail_as_mark"
        ) as mock_emit:
            mock_emit.return_value = AsyncMock()

            # First call should emit
            await nav_node._maybe_auto_witness(graph)
            assert mock_emit.call_count == 1

            # Second call should not emit (already witnessed)
            await nav_node._maybe_auto_witness(graph)
            assert mock_emit.call_count == 1

    async def test_auto_witness_fails_silently(
        self, nav_node: ContextNavNode, observer: Observer
    ):
        """Auto-witness failure doesn't break navigation."""
        graph = nav_node._ensure_graph(observer)
        graph.trail = [
            TrailStep(node_path=f"world.node{i}", edge_type="related" if i > 0 else None)
            for i in range(5)
        ]

        with patch(
            "services.witness.trail_bridge.emit_trail_as_mark"
        ) as mock_emit:
            mock_emit.side_effect = Exception("Witness failed!")

            # Should not raise
            await nav_node._maybe_auto_witness(graph)


# =============================================================================
# Test: Trail Witness CLI Handler
# =============================================================================


class TestTrailWitnessCLI:
    """Tests for `kg context trail witness` CLI command."""

    def test_witness_command_exists(self):
        """The witness subcommand is recognized and routes correctly."""
        from protocols.cli.handlers.context import _handle_trail

        # Reset to fresh node
        set_context_nav_node(ContextNavNode())

        # Should route to _handle_trail_witness, which returns 1 for no trail
        result = _handle_trail(["witness"])
        assert result == 1  # No trail to witness

    def test_witness_no_trail_returns_error(self):
        """Returns error when no trail to witness."""
        from protocols.cli.handlers.context import _handle_trail_witness

        # Reset node to clear any trail
        set_context_nav_node(ContextNavNode())

        result = _handle_trail_witness([])
        assert result == 1

    def test_witness_with_claim(self):
        """Parses --claim flag correctly."""
        from protocols.cli.handlers.context import _handle_trail_witness

        # Setup a node with trail
        node = ContextNavNode()
        set_context_nav_node(node)

        # Can't easily test the full flow without mocking,
        # but we verify the function exists and handles args
        # (Will fail with "No trail to witness")
        result = _handle_trail_witness(["--claim", "Test claim"])
        assert result == 1  # No trail


# =============================================================================
# Test: Trail Evidence in Witness
# =============================================================================


class TestTrailEvidenceInWitness:
    """Tests for trail evidence appearing in witness marks."""

    def test_trail_mark_has_origin(self):
        """Trail marks have origin='context_perception'."""
        from services.witness.trail_bridge import convert_trail_to_mark

        observer = Observer(archetype="developer", capabilities=frozenset())
        trail = Trail(
            id="test-trail",
            name="Test",
            created_by=observer,
            steps=[TrailStep(node_path="world.test", edge_type=None)],
        )

        mark = convert_trail_to_mark(trail)
        assert mark.origin == "context_perception"

    def test_trail_mark_has_evidence(self):
        """Trail marks contain evidence analysis."""
        from services.witness.trail_bridge import convert_trail_to_mark

        observer = Observer(archetype="developer", capabilities=frozenset())
        trail = Trail(
            id="test-trail",
            name="Test",
            created_by=observer,
            steps=[
                TrailStep(node_path=f"world.node{i}", edge_type="tests" if i > 0 else None)
                for i in range(7)
            ],
        )

        mark = convert_trail_to_mark(trail)
        assert mark.evidence.step_count == 7
        assert mark.evidence.evidence_strength in ("moderate", "strong", "definitive")

    def test_trail_mark_serializes_for_bus(self):
        """Trail marks can be serialized for bus publishing."""
        from services.witness.trail_bridge import convert_trail_to_mark

        observer = Observer(archetype="developer", capabilities=frozenset())
        trail = Trail(
            id="test-trail",
            name="Test",
            created_by=observer,
            steps=[TrailStep(node_path="world.test", edge_type=None)],
        )

        mark = convert_trail_to_mark(trail)
        data = mark.to_dict()

        assert "id" in data
        assert "origin" in data
        assert "evidence" in data
        assert data["origin"] == "context_perception"
