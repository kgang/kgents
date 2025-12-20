"""
Tests for SceneGraph: Target-Agnostic Visual Abstraction Layer.

These tests verify:
1. Category laws (identity, associativity)
2. SceneNode immutability and semantics
3. SceneGraph composition
4. Serialization round-trips
5. Layout directives

Philosophy:
    "If laws pass, arbitrary nesting is safe" — meta.md
"""

from __future__ import annotations

from datetime import datetime

import pytest

from protocols.agentese.projection.scene import (
    Interaction,
    LayoutDirective,
    LayoutMode,
    NodeStyle,
    SceneEdge,
    SceneGraph,
    SceneNode,
    SceneNodeKind,
    compose_scenes,
    generate_graph_id,
    generate_node_id,
)

# =============================================================================
# ID Generation Tests
# =============================================================================


class TestIdGeneration:
    """Tests for unique ID generation."""

    def test_node_id_format(self) -> None:
        """Node IDs have correct format."""
        node_id = generate_node_id()
        assert node_id.startswith("sn-")
        assert len(node_id) == 15  # "sn-" + 12 hex chars

    def test_graph_id_format(self) -> None:
        """Graph IDs have correct format."""
        graph_id = generate_graph_id()
        assert graph_id.startswith("sg-")
        assert len(graph_id) == 15

    def test_ids_are_unique(self) -> None:
        """Generated IDs are unique."""
        node_ids = {generate_node_id() for _ in range(100)}
        assert len(node_ids) == 100

        graph_ids = {generate_graph_id() for _ in range(100)}
        assert len(graph_ids) == 100


# =============================================================================
# SceneNode Tests
# =============================================================================


class TestSceneNode:
    """Tests for SceneNode atomic visual element."""

    def test_create_text_node(self) -> None:
        """Can create text node."""
        node = SceneNode.text("Hello, kgents!")
        assert node.kind == SceneNodeKind.TEXT
        assert node.content == "Hello, kgents!"
        assert node.id.startswith("sn-")

    def test_create_panel_node(self) -> None:
        """Can create panel node."""
        node = SceneNode.panel("Dashboard")
        assert node.kind == SceneNodeKind.PANEL
        assert node.label == "Dashboard"

    def test_create_node_with_style(self) -> None:
        """Can create node with custom style."""
        style = NodeStyle(background="sage", breathing=True)
        node = SceneNode(
            kind=SceneNodeKind.TRACE,
            label="Trace #1",
            style=style,
        )
        assert node.style.background == "sage"
        assert node.style.breathing is True

    def test_node_is_frozen(self) -> None:
        """SceneNode is immutable (Law 3)."""
        node = SceneNode.text("Test")
        with pytest.raises(Exception):  # FrozenInstanceError
            node.content = "Modified"  # type: ignore

    def test_with_interaction_immutable(self) -> None:
        """with_interaction returns new node."""
        original = SceneNode.panel("Test")
        interaction = Interaction(kind="click", action="self.test.invoke")

        modified = original.with_interaction(interaction)

        assert len(original.interactions) == 0
        assert len(modified.interactions) == 1
        assert modified.interactions[0].action == "self.test.invoke"

    def test_node_serialization(self) -> None:
        """Node can be serialized and has correct structure."""
        node = SceneNode(
            kind=SceneNodeKind.INTENT,
            content={"goal": "Test something"},
            label="Test Intent",
            flex=2.0,
        )

        data = node.to_dict()

        assert data["kind"] == "INTENT"
        assert data["content"] == {"goal": "Test something"}
        assert data["label"] == "Test Intent"
        assert data["flex"] == 2.0

    def test_all_node_kinds_exist(self) -> None:
        """All expected node kinds are defined."""
        expected_kinds = {
            "PANEL",
            "TRACE",
            "INTENT",
            "OFFERING",
            "COVENANT",
            "WALK",
            "RITUAL",
            "TEXT",
            "GROUP",
        }
        actual_kinds = {k.name for k in SceneNodeKind}
        assert expected_kinds == actual_kinds


# =============================================================================
# NodeStyle Tests
# =============================================================================


class TestNodeStyle:
    """Tests for NodeStyle visual styling."""

    def test_default_style(self) -> None:
        """Default style has expected values."""
        style = NodeStyle.default()
        assert style.background is None
        assert style.breathing is False
        assert style.opacity == 1.0

    def test_breathing_panel_style(self) -> None:
        """Breathing panel style has animation enabled."""
        style = NodeStyle.breathing_panel()
        assert style.breathing is True

    def test_trace_item_style(self) -> None:
        """Trace item style has expected values."""
        style = NodeStyle.trace_item()
        assert style.background == "sage"
        assert style.paper_grain is True

    def test_style_serialization(self) -> None:
        """Style can be serialized."""
        style = NodeStyle(
            background="soil",
            foreground="living_green",
            breathing=True,
            opacity=0.9,
        )

        data = style.to_dict()

        assert data["background"] == "soil"
        assert data["foreground"] == "living_green"
        assert data["breathing"] is True
        assert data["opacity"] == 0.9


# =============================================================================
# LayoutDirective Tests
# =============================================================================


class TestLayoutDirective:
    """Tests for LayoutDirective declarative layouts."""

    def test_vertical_layout(self) -> None:
        """Vertical layout has correct properties."""
        layout = LayoutDirective.vertical(gap=2.0)
        assert layout.direction == "vertical"
        assert layout.gap == 2.0
        assert layout.mode == LayoutMode.COMFORTABLE

    def test_horizontal_layout(self) -> None:
        """Horizontal layout has correct properties."""
        layout = LayoutDirective.horizontal(wrap=True)
        assert layout.direction == "horizontal"
        assert layout.wrap is True

    def test_grid_layout(self) -> None:
        """Grid layout has correct properties."""
        layout = LayoutDirective.grid(gap=1.5)
        assert layout.direction == "grid"
        assert layout.gap == 1.5

    def test_free_layout(self) -> None:
        """Free layout has correct properties."""
        layout = LayoutDirective.free()
        assert layout.direction == "free"

    def test_layout_modes(self) -> None:
        """All layout modes exist."""
        assert LayoutMode.COMPACT is not None
        assert LayoutMode.COMFORTABLE is not None
        assert LayoutMode.SPACIOUS is not None

    def test_layout_serialization_roundtrip(self) -> None:
        """Layout can be serialized and deserialized."""
        original = LayoutDirective(
            direction="grid",
            mode=LayoutMode.SPACIOUS,
            gap=2.0,
            padding=1.5,
            align="center",
        )

        data = original.to_dict()
        restored = LayoutDirective.from_dict(data)

        assert restored.direction == "grid"
        assert restored.mode == LayoutMode.SPACIOUS
        assert restored.gap == 2.0
        assert restored.align == "center"


# =============================================================================
# SceneGraph Tests
# =============================================================================


class TestSceneGraph:
    """Tests for SceneGraph composable scene structure."""

    def test_create_empty_graph(self) -> None:
        """Can create empty graph."""
        graph = SceneGraph.empty()
        assert graph.is_empty()
        assert graph.node_count() == 0

    def test_create_from_nodes(self) -> None:
        """Can create graph from list of nodes."""
        nodes = [SceneNode.text("A"), SceneNode.text("B")]
        graph = SceneGraph.from_nodes(nodes)

        assert graph.node_count() == 2
        assert not graph.is_empty()

    def test_create_panel_graph(self) -> None:
        """Can create panel graph with children."""
        child1 = SceneNode.text("Child 1")
        child2 = SceneNode.text("Child 2")
        graph = SceneGraph.panel("Container", child1, child2)

        assert graph.node_count() == 3  # panel + 2 children
        assert graph.title == "Container"
        assert graph.nodes[0].kind == SceneNodeKind.PANEL

    def test_graph_is_frozen(self) -> None:
        """SceneGraph is immutable."""
        graph = SceneGraph.empty()
        with pytest.raises(Exception):
            graph.nodes = (SceneNode.text("Test"),)  # type: ignore

    def test_find_node_by_id(self) -> None:
        """Can find node by ID."""
        node = SceneNode.text("Target")
        graph = SceneGraph.from_nodes([SceneNode.text("Other"), node])

        found = graph.find_node(node.id)

        assert found is not None
        assert found.content == "Target"

    def test_find_node_not_found(self) -> None:
        """find_node returns None for missing ID."""
        graph = SceneGraph.from_nodes([SceneNode.text("A")])
        found = graph.find_node(generate_node_id())
        assert found is None

    def test_nodes_by_kind(self) -> None:
        """Can filter nodes by kind."""
        graph = SceneGraph.from_nodes(
            [
                SceneNode.text("Text 1"),
                SceneNode.panel("Panel 1"),
                SceneNode.text("Text 2"),
            ]
        )

        texts = graph.nodes_by_kind(SceneNodeKind.TEXT)
        panels = graph.nodes_by_kind(SceneNodeKind.PANEL)

        assert len(texts) == 2
        assert len(panels) == 1

    def test_with_node_immutable(self) -> None:
        """with_node returns new graph."""
        original = SceneGraph.from_nodes([SceneNode.text("A")])
        modified = original.with_node(SceneNode.text("B"))

        assert original.node_count() == 1
        assert modified.node_count() == 2

    def test_with_edge_immutable(self) -> None:
        """with_edge returns new graph."""
        node1 = SceneNode.text("A")
        node2 = SceneNode.text("B")
        graph = SceneGraph.from_nodes([node1, node2])

        edge = SceneEdge(source=node1.id, target=node2.id)
        modified = graph.with_edge(edge)

        assert len(graph.edges) == 0
        assert len(modified.edges) == 1

    def test_with_layout_immutable(self) -> None:
        """with_layout returns new graph."""
        original = SceneGraph.from_nodes([SceneNode.text("A")])
        modified = original.with_layout(LayoutDirective.horizontal())

        assert original.layout.direction == "vertical"
        assert modified.layout.direction == "horizontal"

    def test_graph_serialization(self) -> None:
        """Graph can be serialized."""
        graph = SceneGraph(
            nodes=(SceneNode.text("Test"),),
            layout=LayoutDirective.grid(),
            title="Test Graph",
        )

        data = graph.to_dict()

        assert len(data["nodes"]) == 1
        assert data["layout"]["direction"] == "grid"
        assert data["title"] == "Test Graph"


# =============================================================================
# Category Law Tests (Critical!)
# =============================================================================


class TestCategoryLaws:
    """
    Tests for category laws.

    These are the most important tests. If laws pass, arbitrary
    composition is safe.
    """

    def test_identity_law_left(self) -> None:
        """
        Law 1a: empty >> G ≡ G

        The empty graph is a left identity.
        """
        empty = SceneGraph.empty()
        g = SceneGraph.from_nodes([SceneNode.text("A"), SceneNode.text("B")])

        result = empty >> g

        assert result.node_count() == g.node_count()
        # Result should be equivalent to G
        for i, node in enumerate(result.nodes):
            assert node.content == g.nodes[i].content

    def test_identity_law_right(self) -> None:
        """
        Law 1b: G >> empty ≡ G

        The empty graph is a right identity.
        """
        empty = SceneGraph.empty()
        g = SceneGraph.from_nodes([SceneNode.text("A"), SceneNode.text("B")])

        result = g >> empty

        assert result.node_count() == g.node_count()
        for i, node in enumerate(result.nodes):
            assert node.content == g.nodes[i].content

    def test_identity_law_both(self) -> None:
        """
        Law 1: empty >> G ≡ G ≡ G >> empty

        Full identity law verification.
        """
        empty = SceneGraph.empty()
        g = SceneGraph.from_nodes([SceneNode.text("Test")])

        left_identity = empty >> g
        right_identity = g >> empty

        # Both should be equivalent to G
        assert left_identity.node_count() == 1
        assert right_identity.node_count() == 1
        assert left_identity.nodes[0].content == g.nodes[0].content
        assert right_identity.nodes[0].content == g.nodes[0].content

    def test_associativity_law(self) -> None:
        """
        Law 2: (A >> B) >> C ≡ A >> (B >> C)

        Composition is associative.
        """
        a = SceneGraph.from_nodes([SceneNode.text("A")])
        b = SceneGraph.from_nodes([SceneNode.text("B")])
        c = SceneGraph.from_nodes([SceneNode.text("C")])

        left_grouped = (a >> b) >> c  # (A >> B) >> C
        right_grouped = a >> (b >> c)  # A >> (B >> C)

        # Both should have same node count
        assert left_grouped.node_count() == right_grouped.node_count() == 3

        # Nodes should be in same order: A, B, C
        assert left_grouped.nodes[0].content == "A"
        assert left_grouped.nodes[1].content == "B"
        assert left_grouped.nodes[2].content == "C"

        assert right_grouped.nodes[0].content == "A"
        assert right_grouped.nodes[1].content == "B"
        assert right_grouped.nodes[2].content == "C"

    def test_associativity_with_complex_graphs(self) -> None:
        """Associativity holds for complex graphs with edges."""
        node_a = SceneNode.text("A")
        node_b = SceneNode.text("B")
        node_c = SceneNode.text("C")

        a = SceneGraph(nodes=(node_a,), edges=())
        b = SceneGraph(
            nodes=(node_b,),
            edges=(SceneEdge(source=node_a.id, target=node_b.id),),
        )
        c = SceneGraph(nodes=(node_c,), edges=())

        left = (a >> b) >> c
        right = a >> (b >> c)

        assert left.node_count() == right.node_count()
        assert len(left.edges) == len(right.edges)

    def test_compose_scenes_utility(self) -> None:
        """compose_scenes is equivalent to >> chain."""
        a = SceneGraph.from_nodes([SceneNode.text("A")])
        b = SceneGraph.from_nodes([SceneNode.text("B")])
        c = SceneGraph.from_nodes([SceneNode.text("C")])

        composed = compose_scenes(a, b, c)
        chained = a >> b >> c

        assert composed.node_count() == chained.node_count()
        for i in range(3):
            assert composed.nodes[i].content == chained.nodes[i].content

    def test_compose_empty_sequence(self) -> None:
        """compose_scenes with no args returns empty graph."""
        result = compose_scenes()
        assert result.is_empty()

    def test_compose_single_graph(self) -> None:
        """compose_scenes with one arg returns that graph."""
        g = SceneGraph.from_nodes([SceneNode.text("Solo")])
        result = compose_scenes(g)

        assert result.node_count() == 1
        assert result.nodes[0].content == "Solo"


# =============================================================================
# SceneEdge Tests
# =============================================================================


class TestSceneEdge:
    """Tests for SceneEdge graph connections."""

    def test_create_edge(self) -> None:
        """Can create edge between nodes."""
        node1 = SceneNode.text("A")
        node2 = SceneNode.text("B")

        edge = SceneEdge(
            source=node1.id,
            target=node2.id,
            label="depends on",
        )

        assert edge.source == node1.id
        assert edge.target == node2.id
        assert edge.label == "depends on"

    def test_edge_styles(self) -> None:
        """Edge supports different styles."""
        solid = SceneEdge(source=generate_node_id(), target=generate_node_id())
        dashed = SceneEdge(
            source=generate_node_id(),
            target=generate_node_id(),
            style="dashed",
        )

        assert solid.style == "solid"
        assert dashed.style == "dashed"

    def test_edge_serialization(self) -> None:
        """Edge can be serialized."""
        edge = SceneEdge(
            source=generate_node_id(),
            target=generate_node_id(),
            label="causes",
            style="dotted",
        )

        data = edge.to_dict()

        assert "source" in data
        assert "target" in data
        assert data["label"] == "causes"
        assert data["style"] == "dotted"


# =============================================================================
# Integration Tests
# =============================================================================


class TestIntegration:
    """Integration tests for SceneGraph usage patterns."""

    def test_build_dashboard_scene(self) -> None:
        """Can build complex dashboard scene."""
        # Header
        header = SceneGraph.panel(
            "Header",
            SceneNode.text("kgents Dashboard"),
            layout=LayoutDirective.horizontal(),
        )

        # Sidebar with navigation
        sidebar = SceneGraph.panel(
            "Sidebar",
            SceneNode(kind=SceneNodeKind.INTENT, label="Garden"),
            SceneNode(kind=SceneNodeKind.INTENT, label="Witness"),
            SceneNode(kind=SceneNodeKind.INTENT, label="Brain"),
        )

        # Main content
        content = SceneGraph.panel(
            "Content",
            SceneNode(kind=SceneNodeKind.TRACE, label="Recent activity"),
            SceneNode(kind=SceneNodeKind.WALK, label="Current session"),
        )

        # Compose
        dashboard = header >> (sidebar >> content).with_layout(LayoutDirective.horizontal())

        # Verify structure
        assert dashboard.node_count() > 5
        assert len(dashboard.nodes_by_kind(SceneNodeKind.INTENT)) == 3
        assert len(dashboard.nodes_by_kind(SceneNodeKind.TRACE)) == 1

    def test_build_trace_timeline(self) -> None:
        """Can build trace timeline with edges."""
        # Create trace nodes
        traces = [
            SceneNode(kind=SceneNodeKind.TRACE, label=f"Trace {i}", content={"id": f"t{i}"})
            for i in range(5)
        ]

        # Build graph with causality edges
        graph = SceneGraph.from_nodes(traces)
        for i in range(len(traces) - 1):
            edge = SceneEdge(
                source=traces[i].id,
                target=traces[i + 1].id,
                label="causes",
            )
            graph = graph.with_edge(edge)

        assert graph.node_count() == 5
        assert len(graph.edges) == 4

    def test_scene_with_interactions(self) -> None:
        """Can build scene with interactive elements."""
        button = SceneNode.panel("Submit").with_interaction(
            Interaction(
                kind="click",
                action="self.form.submit",
                requires_trust=1,
            )
        )

        graph = SceneGraph.from_nodes([button])
        serialized = graph.to_dict()

        # Verify interaction is serialized
        assert len(serialized["nodes"][0]["interactions"]) == 1
        assert serialized["nodes"][0]["interactions"][0]["action"] == "self.form.submit"

    def test_compose_many_graphs(self) -> None:
        """Composition scales to many graphs."""
        graphs = [SceneGraph.from_nodes([SceneNode.text(f"Section {i}")]) for i in range(20)]

        composed = compose_scenes(*graphs)

        assert composed.node_count() == 20

    def test_serialization_preserves_structure(self) -> None:
        """Full serialization preserves all information."""
        original = SceneGraph(
            nodes=(
                SceneNode(
                    kind=SceneNodeKind.PANEL,
                    label="Test Panel",
                    style=NodeStyle(breathing=True, background="sage"),
                ),
            ),
            edges=(
                SceneEdge(
                    source=generate_node_id(),
                    target=generate_node_id(),
                    label="test edge",
                ),
            ),
            layout=LayoutDirective.grid(gap=2.0),
            title="Test Scene",
            metadata={"version": 1},
        )

        data = original.to_dict()

        # Verify structure
        assert data["title"] == "Test Scene"
        assert data["layout"]["direction"] == "grid"
        assert data["layout"]["gap"] == 2.0
        assert len(data["nodes"]) == 1
        assert data["nodes"][0]["style"]["breathing"] is True
        assert len(data["edges"]) == 1
        assert data["metadata"]["version"] == 1
