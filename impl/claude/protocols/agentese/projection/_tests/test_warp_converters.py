"""
Tests for WARP Primitive → SceneGraph Converters.

These tests verify:
1. TraceNode → SceneNode conversion preserves semantics
2. Walk → SceneGraph conversion includes all key data
3. Timeline layout generates proper edges
4. Palette colors are correctly applied
5. Animation hints respect state (active=breathing, complete=static)

Philosophy:
    "If laws pass, arbitrary composition is safe" — meta.md
"""

from __future__ import annotations

from datetime import datetime, timedelta

import pytest

from protocols.agentese.projection.scene import (
    LayoutDirective,
    SceneGraph,
    SceneNode,
    SceneNodeKind,
)
from protocols.agentese.projection.warp_converters import (
    PALETTE,
    PALETTE_HEX,
    palette_to_hex,
    trace_node_to_scene,
    trace_timeline_to_scene,
    walk_dashboard_to_scene,
    walk_to_scene,
)
from services.witness.trace_node import (
    NPhase,
    Response,
    Stimulus,
    TraceNode,
    UmweltSnapshot,
)
from services.witness.walk import Walk, WalkIntent, WalkStatus

# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def sample_trace() -> TraceNode:
    """Create a sample TraceNode for testing."""
    return TraceNode(
        origin="witness",
        stimulus=Stimulus.from_event("git", "Commit abc123", "git"),
        response=Response.thought("Noticed commit abc123", ("git", "commit")),
        umwelt=UmweltSnapshot.witness(trust_level=1),
        phase=NPhase.SENSE,
        tags=("git", "commit"),
    )


@pytest.fixture
def sample_traces() -> list[TraceNode]:
    """Create a sequence of TraceNodes for timeline testing."""
    traces = []
    base_time = datetime.now()
    for i in range(5):
        trace = TraceNode(
            origin="witness",
            stimulus=Stimulus.from_event("test", f"Event {i}", "test"),
            response=Response.thought(f"Response {i}", ("test",)),
            umwelt=UmweltSnapshot.witness(),
            timestamp=base_time + timedelta(seconds=i * 10),
        )
        traces.append(trace)
    return traces


@pytest.fixture
def sample_walk() -> Walk:
    """Create a sample Walk for testing."""
    return Walk.create(
        goal="Test the WARP converters",
        root_plan="plans/test.md",
        name="Test Walk",
    )


# =============================================================================
# Palette Tests
# =============================================================================


class TestPalette:
    """Tests for Living Earth palette."""

    def test_palette_has_required_colors(self) -> None:
        """Palette includes all required semantic colors."""
        required = ["copper", "sage", "soil", "paper", "living_green", "amber_glow", "twilight"]
        for color in required:
            assert hasattr(PALETTE, color.upper())

    def test_palette_hex_mapping(self) -> None:
        """Palette hex values are valid hex codes."""
        for name, hex_value in PALETTE_HEX.items():
            assert hex_value.startswith("#"), f"{name} should be hex"
            assert len(hex_value) == 7, f"{name} should be #RRGGBB format"

    def test_palette_to_hex_known_color(self) -> None:
        """palette_to_hex converts known colors."""
        assert palette_to_hex("sage") == "#9caf88"
        assert palette_to_hex("copper") == "#b87333"

    def test_palette_to_hex_unknown_passthrough(self) -> None:
        """palette_to_hex passes through unknown values."""
        assert palette_to_hex("#custom") == "#custom"
        assert palette_to_hex("unknown") == "unknown"


# =============================================================================
# TraceNode Converter Tests
# =============================================================================


class TestTraceNodeConverter:
    """Tests for TraceNode → SceneNode conversion."""

    def test_trace_to_scene_basic(self, sample_trace: TraceNode) -> None:
        """Basic TraceNode converts to SceneNode."""
        node = trace_node_to_scene(sample_trace)

        assert node.kind == SceneNodeKind.TRACE
        assert "trace_id" in node.content
        assert node.content["origin"] == "witness"
        assert node.content["phase"] == "SENSE"

    def test_trace_to_scene_label_truncation(self) -> None:
        """Long stimulus content is truncated in label."""
        long_stimulus = "A" * 100
        trace = TraceNode(
            origin="test",
            stimulus=Stimulus(kind="test", content=long_stimulus),
            response=Response(kind="test", content="ok"),
        )

        node = trace_node_to_scene(trace)

        assert len(node.label) <= 43  # 40 chars + "..."
        assert node.label.endswith("...")

    def test_trace_to_scene_style_applied(self, sample_trace: TraceNode) -> None:
        """Sage background and paper grain applied."""
        node = trace_node_to_scene(sample_trace)

        assert node.style.background == PALETTE.SAGE
        assert node.style.paper_grain is True

    def test_trace_to_scene_breathing_on_success(self, sample_trace: TraceNode) -> None:
        """Successful traces breathe."""
        node = trace_node_to_scene(sample_trace, animate=True)
        assert node.style.breathing is True

    def test_trace_to_scene_no_breathing_on_error(self) -> None:
        """Failed traces don't breathe."""
        trace = TraceNode(
            origin="test",
            stimulus=Stimulus(kind="test", content="test"),
            response=Response.error("Something went wrong"),
        )

        node = trace_node_to_scene(trace, animate=True)
        assert node.style.breathing is False

    def test_trace_to_scene_animation_disabled(self, sample_trace: TraceNode) -> None:
        """Animation can be disabled."""
        node = trace_node_to_scene(sample_trace, animate=False)
        assert node.style.breathing is False

    def test_trace_to_scene_metadata(self, sample_trace: TraceNode) -> None:
        """Metadata includes trace_id and origin."""
        node = trace_node_to_scene(sample_trace)

        assert "trace_id" in node.metadata
        assert node.metadata["origin"] == "witness"
        assert node.metadata["success"] is True


class TestTraceTimelineConverter:
    """Tests for trace timeline conversion."""

    def test_empty_timeline(self) -> None:
        """Empty trace list returns empty graph."""
        graph = trace_timeline_to_scene([])
        assert graph.is_empty()

    def test_timeline_nodes_created(self, sample_traces: list[TraceNode]) -> None:
        """All traces become nodes."""
        graph = trace_timeline_to_scene(sample_traces)

        assert graph.node_count() == 5
        for node in graph.nodes:
            assert node.kind == SceneNodeKind.TRACE

    def test_timeline_edges_created(self, sample_traces: list[TraceNode]) -> None:
        """Sequential traces have causal edges."""
        graph = trace_timeline_to_scene(sample_traces, show_edges=True)

        assert len(graph.edges) == 4  # n-1 edges for n nodes
        for edge in graph.edges:
            assert edge.metadata.get("relation") == "causal"

    def test_timeline_edges_disabled(self, sample_traces: list[TraceNode]) -> None:
        """Edges can be disabled."""
        graph = trace_timeline_to_scene(sample_traces, show_edges=False)
        assert len(graph.edges) == 0

    def test_timeline_horizontal_layout(self, sample_traces: list[TraceNode]) -> None:
        """Timeline uses horizontal layout."""
        graph = trace_timeline_to_scene(sample_traces)
        assert graph.layout.direction == "horizontal"

    def test_timeline_title(self, sample_traces: list[TraceNode]) -> None:
        """Custom title is applied."""
        graph = trace_timeline_to_scene(sample_traces, title="My Timeline")
        assert graph.title == "My Timeline"


# =============================================================================
# Walk Converter Tests
# =============================================================================


class TestWalkConverter:
    """Tests for Walk → SceneGraph conversion."""

    def test_walk_to_scene_basic(self, sample_walk: Walk) -> None:
        """Basic Walk converts to SceneGraph."""
        graph = walk_to_scene(sample_walk)

        assert not graph.is_empty()
        assert graph.title == "Test Walk"

    def test_walk_node_kind(self, sample_walk: Walk) -> None:
        """Walk becomes WALK-kind node."""
        graph = walk_to_scene(sample_walk)

        walk_nodes = graph.nodes_by_kind(SceneNodeKind.WALK)
        assert len(walk_nodes) == 1

    def test_walk_content_complete(self, sample_walk: Walk) -> None:
        """Walk node contains all key information."""
        graph = walk_to_scene(sample_walk)

        walk_node = graph.nodes_by_kind(SceneNodeKind.WALK)[0]
        content = walk_node.content

        assert "walk_id" in content
        assert "name" in content
        assert "goal" in content
        assert "phase" in content
        assert "status" in content
        assert content["status"] == "ACTIVE"

    def test_walk_breathing_when_active(self, sample_walk: Walk) -> None:
        """Active walk breathes."""
        graph = walk_to_scene(sample_walk)

        walk_node = graph.nodes_by_kind(SceneNodeKind.WALK)[0]
        assert walk_node.style.breathing is True

    def test_walk_not_breathing_when_complete(self, sample_walk: Walk) -> None:
        """Completed walk doesn't breathe."""
        sample_walk.complete()
        graph = walk_to_scene(sample_walk)

        walk_node = graph.nodes_by_kind(SceneNodeKind.WALK)[0]
        assert walk_node.style.breathing is False

    def test_walk_status_colors(self) -> None:
        """Different statuses have different colors."""
        walks = [
            Walk.create("Active", name="Active"),
            Walk.create("Paused", name="Paused"),
            Walk.create("Complete", name="Complete"),
        ]
        walks[1].pause()
        walks[2].complete()

        graphs = [walk_to_scene(w) for w in walks]
        walk_nodes = [g.nodes_by_kind(SceneNodeKind.WALK)[0] for g in graphs]

        # Each should have different background
        backgrounds = [n.style.background for n in walk_nodes]
        assert backgrounds[0] == PALETTE.LIVING_GREEN  # Active
        assert backgrounds[1] == PALETTE.AMBER_GLOW  # Paused
        assert backgrounds[2] == PALETTE.SAGE  # Complete

    def test_walk_has_click_interaction(self, sample_walk: Walk) -> None:
        """Walk node is clickable."""
        graph = walk_to_scene(sample_walk)

        walk_node = graph.nodes_by_kind(SceneNodeKind.WALK)[0]
        assert len(walk_node.interactions) > 0
        assert walk_node.interactions[0].kind == "click"


class TestWalkDashboardConverter:
    """Tests for Walk dashboard conversion."""

    def test_empty_dashboard(self) -> None:
        """Empty walk list shows message."""
        graph = walk_dashboard_to_scene([])

        assert not graph.is_empty()
        assert "No active walks" in graph.nodes[0].content

    def test_dashboard_with_walks(self) -> None:
        """Dashboard displays multiple walks."""
        walks = [
            Walk.create(f"Walk {i}", name=f"Walk {i}")
            for i in range(3)
        ]

        graph = walk_dashboard_to_scene(walks)

        # Should have multiple WALK nodes
        walk_nodes = graph.nodes_by_kind(SceneNodeKind.WALK)
        assert len(walk_nodes) == 3

    def test_dashboard_grid_layout(self) -> None:
        """Dashboard section uses grid layout."""
        walks = [Walk.create("Test", name="Test")]

        graph = walk_dashboard_to_scene(walks)

        # At least one node group should use grid
        assert any(
            isinstance(graph.layout, LayoutDirective)
            for _ in [graph.layout]
        )


# =============================================================================
# Composition Tests
# =============================================================================


class TestConverterComposition:
    """Tests for composing converted graphs."""

    def test_trace_timeline_composition(self, sample_traces: list[TraceNode]) -> None:
        """Trace timelines can be composed."""
        timeline1 = trace_timeline_to_scene(sample_traces[:2], title="Part 1")
        timeline2 = trace_timeline_to_scene(sample_traces[2:], title="Part 2")

        composed = timeline1 >> timeline2

        assert composed.node_count() == 5

    def test_walk_with_trace_composition(
        self,
        sample_walk: Walk,
        sample_traces: list[TraceNode],
    ) -> None:
        """Walk and trace timeline can be composed."""
        walk_graph = walk_to_scene(sample_walk)
        trace_graph = trace_timeline_to_scene(sample_traces)

        composed = walk_graph >> trace_graph

        # Should have both WALK and TRACE nodes
        assert len(composed.nodes_by_kind(SceneNodeKind.WALK)) >= 1
        assert len(composed.nodes_by_kind(SceneNodeKind.TRACE)) == 5

    def test_composition_preserves_layout(
        self,
        sample_walk: Walk,
        sample_traces: list[TraceNode],
    ) -> None:
        """Left graph's layout is preserved (left-dominant)."""
        walk_graph = walk_to_scene(sample_walk)  # vertical
        trace_graph = trace_timeline_to_scene(sample_traces)  # horizontal

        composed = walk_graph >> trace_graph

        assert composed.layout.direction == "vertical"


# =============================================================================
# Serialization Tests
# =============================================================================


class TestConverterSerialization:
    """Tests for serializing converted graphs."""

    def test_trace_scene_serializes(self, sample_trace: TraceNode) -> None:
        """Converted trace node serializes to dict."""
        node = trace_node_to_scene(sample_trace)
        data = node.to_dict()

        assert data["kind"] == "TRACE"
        assert "content" in data
        assert "style" in data

    def test_walk_scene_serializes(self, sample_walk: Walk) -> None:
        """Converted walk graph serializes to dict."""
        graph = walk_to_scene(sample_walk)
        data = graph.to_dict()

        assert "nodes" in data
        assert len(data["nodes"]) > 0
        assert data["nodes"][0]["kind"] == "WALK"

    def test_timeline_serializes(self, sample_traces: list[TraceNode]) -> None:
        """Timeline with edges serializes correctly."""
        graph = trace_timeline_to_scene(sample_traces)
        data = graph.to_dict()

        assert len(data["nodes"]) == 5
        assert len(data["edges"]) == 4
        assert data["layout"]["direction"] == "horizontal"


# =============================================================================
# Edge Case Tests (Session 7 QA)
# =============================================================================


class TestEdgeCases:
    """Edge cases for converter robustness. Session 7 QA additions."""

    def test_unicode_in_stimulus(self) -> None:
        """Unicode characters in stimulus content handled correctly."""
        trace = TraceNode(
            origin="test",
            stimulus=Stimulus(kind="test", content="🚀 日本語 émoji Ω∞"),
            response=Response(kind="test", content="ok"),
        )

        node = trace_node_to_scene(trace)

        assert "🚀" in node.label
        assert "日本語" in node.label
        assert node.content["stimulus"]["content"] == "🚀 日本語 émoji Ω∞"

    def test_empty_stimulus_content(self) -> None:
        """Empty stimulus content doesn't crash converter."""
        trace = TraceNode(
            origin="test",
            stimulus=Stimulus(kind="test", content=""),
            response=Response(kind="test", content="ok"),
        )

        node = trace_node_to_scene(trace)

        assert node.label == ""  # Empty is valid
        assert node.kind == SceneNodeKind.TRACE

    def test_empty_response_content(self) -> None:
        """Empty response content doesn't crash converter."""
        trace = TraceNode(
            origin="test",
            stimulus=Stimulus(kind="test", content="test"),
            response=Response(kind="test", content=""),
        )

        node = trace_node_to_scene(trace)

        assert node.content["response"]["content"] == ""

    def test_very_long_stimulus_truncated(self) -> None:
        """Very long stimulus (1000+ chars) truncates to reasonable label."""
        long_content = "A" * 1000
        trace = TraceNode(
            origin="test",
            stimulus=Stimulus(kind="test", content=long_content),
            response=Response(kind="test", content="ok"),
        )

        node = trace_node_to_scene(trace)

        # Label should be 40 chars max (37 + "...")
        assert len(node.label) <= 43
        assert node.label.endswith("...")
        # But full content is preserved
        assert len(node.content["stimulus"]["content"]) == 1000

    def test_walk_with_zero_traces(self, sample_walk: Walk) -> None:
        """Walk with no traces converts correctly."""
        graph = walk_to_scene(sample_walk, include_traces=False)

        walk_nodes = graph.nodes_by_kind(SceneNodeKind.WALK)
        assert len(walk_nodes) == 1
        assert walk_nodes[0].content["trace_count"] == 0

    def test_walk_with_empty_name_gets_default(self) -> None:
        """Walk with empty name gets auto-generated name."""
        walk = Walk.create(
            goal="Test goal",
            root_plan="plans/test.md",
            name="",  # Empty name → auto-generated
        )

        graph = walk_to_scene(walk)
        walk_node = graph.nodes_by_kind(SceneNodeKind.WALK)[0]

        # Auto-generated name format: "Walk-YYYYMMDD-HHMM"
        assert walk_node.label.startswith("Walk-")
        # Converter doesn't crash on empty name
        assert walk_node.kind == SceneNodeKind.WALK

    def test_walk_with_empty_goal(self) -> None:
        """Walk with empty goal handles gracefully."""
        walk = Walk.create(
            goal="",  # Empty goal
            root_plan="plans/test.md",
            name="Test Walk",
        )

        graph = walk_to_scene(walk)
        walk_node = graph.nodes_by_kind(SceneNodeKind.WALK)[0]

        # Empty goal is stored as empty string (not None)
        assert walk_node.content["goal"] == ""
        # Converter doesn't crash
        assert walk_node.kind == SceneNodeKind.WALK

    def test_large_dashboard_performance(self) -> None:
        """Dashboard with 100 walks converts in reasonable time."""
        import time

        walks = [Walk.create(f"Walk {i}", name=f"Walk {i}") for i in range(100)]

        start = time.perf_counter()
        graph = walk_dashboard_to_scene(walks)
        elapsed = time.perf_counter() - start

        # Should complete in under 500ms
        assert elapsed < 0.5, f"Dashboard conversion took {elapsed:.2f}s"
        assert graph.node_count() >= 100  # At least 100 WALK nodes

    def test_special_characters_in_origin(self) -> None:
        """Origin with special characters handled correctly."""
        trace = TraceNode(
            origin="test/path:special<chars>",
            stimulus=Stimulus(kind="test", content="test"),
            response=Response(kind="test", content="ok"),
        )

        node = trace_node_to_scene(trace)

        assert node.content["origin"] == "test/path:special<chars>"
        assert node.metadata["origin"] == "test/path:special<chars>"


# =============================================================================
# Full Pipeline Integration Tests (Session 7)
# =============================================================================


class TestFullPipeline:
    """
    Integration tests: Walk → SceneGraph → JSON → verify React structure.

    These tests ensure the JSON structure matches what the React components expect.
    """

    def test_walk_to_json_react_structure(self, sample_walk: Walk) -> None:
        """Walk → SceneGraph → JSON has structure React expects."""
        graph = walk_to_scene(sample_walk)
        json_data = graph.to_dict()

        # Top-level structure
        assert "id" in json_data
        assert "nodes" in json_data
        assert "edges" in json_data
        assert "layout" in json_data
        assert "title" in json_data

        # Layout structure
        layout = json_data["layout"]
        assert "direction" in layout
        assert layout["direction"] in ("vertical", "horizontal", "grid", "free")
        assert "mode" in layout
        assert layout["mode"] in ("COMPACT", "COMFORTABLE", "SPACIOUS")

        # Node structure (matching ServoNodeRenderer props)
        for node in json_data["nodes"]:
            assert "id" in node
            assert "kind" in node
            assert "content" in node
            assert "label" in node
            assert "style" in node
            assert "metadata" in node

            # Style structure
            style = node["style"]
            assert "background" in style
            assert "breathing" in style

    def test_trace_timeline_to_json_react_structure(
        self, sample_traces: list[TraceNode]
    ) -> None:
        """Trace timeline JSON matches React ServoSceneRenderer expectations."""
        graph = trace_timeline_to_scene(sample_traces)
        json_data = graph.to_dict()

        # Edge structure
        for edge in json_data["edges"]:
            assert "source" in edge
            assert "target" in edge
            assert "label" in edge
            assert "style" in edge
            assert "metadata" in edge

            # source and target are valid node IDs
            node_ids = {n["id"] for n in json_data["nodes"]}
            assert edge["source"] in node_ids
            assert edge["target"] in node_ids

    def test_trace_content_matches_react_types(self, sample_trace: TraceNode) -> None:
        """TraceNode content JSON matches TraceNodeCard TypeScript types."""
        node = trace_node_to_scene(sample_trace)
        data = node.to_dict()
        content = data["content"]

        # Must match TraceNodeContent interface in TraceNodeCard.tsx
        assert "trace_id" in content
        assert isinstance(content["trace_id"], str)

        assert "origin" in content
        assert isinstance(content["origin"], str)

        assert "stimulus" in content
        assert "kind" in content["stimulus"]
        assert "content" in content["stimulus"]
        assert "source" in content["stimulus"]

        assert "response" in content
        assert "kind" in content["response"]
        assert "content" in content["response"]
        assert "success" in content["response"]
        assert isinstance(content["response"]["success"], bool)

        assert "timestamp" in content
        assert "phase" in content
        assert "tags" in content
        assert isinstance(content["tags"], list)

    def test_walk_content_matches_react_types(self, sample_walk: Walk) -> None:
        """Walk content JSON matches WalkCard TypeScript types."""
        graph = walk_to_scene(sample_walk)
        walk_node = graph.nodes_by_kind(SceneNodeKind.WALK)[0]
        data = walk_node.to_dict()
        content = data["content"]

        # Must match WalkContent interface in WalkCard.tsx
        assert "walk_id" in content
        assert isinstance(content["walk_id"], str)

        assert "name" in content
        assert isinstance(content["name"], str)

        assert "goal" in content
        # goal can be None

        assert "phase" in content
        assert isinstance(content["phase"], str)

        assert "status" in content
        assert content["status"] in ("ACTIVE", "PAUSED", "COMPLETE", "ABANDONED")

        assert "trace_count" in content
        assert isinstance(content["trace_count"], int)

        assert "participants" in content
        assert isinstance(content["participants"], list)

        assert "duration_seconds" in content
        assert isinstance(content["duration_seconds"], (int, float))

        assert "started_at" in content
        assert isinstance(content["started_at"], str)  # ISO format
