"""
Tests for GraphLayout widget - 2D node-edge graph visualization.

Tests verify:
- Layout algorithms (semantic, tree, force)
- Node positioning and edge rendering
- Semantic positions for agent taxonomy
- Empty state handling
- Boundary conditions
"""

from __future__ import annotations

import pytest
from agents.i.widgets.graph_layout import (
    SEMANTIC_POSITIONS,
    GraphLayout,
    LayoutAlgorithm,
    NodePosition,
    compute_force_layout,
    compute_semantic_layout,
    compute_tree_layout,
    get_semantic_position,
    render_graph_to_lines,
)


class TestSemanticPositions:
    """Tests for semantic positioning based on agent taxonomy."""

    def test_k_gent_at_center(self) -> None:
        """K-gent should be positioned at center (0.5, 0.5)."""
        x, y = get_semantic_position("K")
        assert x == 0.5, "K-gent x should be center"
        assert y == 0.5, "K-gent y should be center"

    def test_k_gent_variations(self) -> None:
        """K-gent should be at center regardless of suffix."""
        for name in ["K", "K-gent", "Kgent", "K-test"]:
            x, y = get_semantic_position(name)
            assert x == 0.5, f"{name} x should be center"
            assert y == 0.5, f"{name} y should be center"

    def test_d_gent_right_side(self) -> None:
        """D-gent should be positioned on right side."""
        x, y = get_semantic_position("D")
        assert x > 0.5, "D-gent should be right of center"

    def test_a_gent_upper_left(self) -> None:
        """A-gent should be positioned in upper left."""
        x, y = get_semantic_position("A")
        assert x < 0.5, "A-gent should be left of center"
        assert y < 0.5, "A-gent should be above center"

    def test_unknown_type_defaults_to_center_ish(self) -> None:
        """Unknown agent types should get consistent hash-based positions."""
        x1, y1 = get_semantic_position("XYZ-agent")
        x2, y2 = get_semantic_position("XYZ-agent")
        # Same unknown type should get same position (hash-based)
        assert x1 == x2
        assert y1 == y2
        # Should be in center-ish region
        assert 0.2 < x1 < 0.8
        assert 0.2 < y1 < 0.8

    def test_empty_string_defaults_to_center(self) -> None:
        """Empty node ID should default to center."""
        x, y = get_semantic_position("")
        assert x == 0.5
        assert y == 0.5

    def test_all_defined_types_have_positions(self) -> None:
        """All predefined types should have semantic positions."""
        expected_types = ["A", "B", "C", "D", "E", "K", "L", "M", "N", "T", "U", "Y"]
        for agent_type in expected_types:
            assert agent_type in SEMANTIC_POSITIONS, (
                f"{agent_type} should have a position"
            )


class TestComputeSemanticLayout:
    """Tests for semantic layout computation."""

    def test_empty_nodes_returns_empty_dict(self) -> None:
        """Empty node list should return empty positions."""
        positions = compute_semantic_layout([], 100, 50)
        assert positions == {}

    def test_single_node_positioned(self) -> None:
        """Single node should be positioned correctly."""
        positions = compute_semantic_layout(["K"], 100, 50)
        assert "K" in positions
        pos = positions["K"]
        # K should be near center
        assert 40 < pos.x < 60
        assert 20 < pos.y < 30

    def test_multiple_nodes_unique_positions(self) -> None:
        """Multiple nodes should have distinct positions."""
        nodes = ["A", "K", "D"]
        positions = compute_semantic_layout(nodes, 100, 50)

        # All nodes should have positions
        assert len(positions) == 3

        # Positions should be distinct
        pos_tuples = [(p.x, p.y) for p in positions.values()]
        assert len(set(pos_tuples)) == 3, "All positions should be unique"


class TestComputeTreeLayout:
    """Tests for tree layout computation."""

    def test_empty_graph(self) -> None:
        """Empty graph should return empty positions."""
        positions = compute_tree_layout([], [], 100, 50)
        assert positions == {}

    def test_single_node(self) -> None:
        """Single node should be positioned."""
        positions = compute_tree_layout(["A"], [], 100, 50)
        assert "A" in positions

    def test_linear_chain(self) -> None:
        """Linear chain should have increasing y positions."""
        nodes = ["A", "B", "C"]
        edges = [("A", "B"), ("B", "C")]
        positions = compute_tree_layout(nodes, edges, 100, 50)

        # A should be above B, B above C (parent → child goes down)
        assert positions["A"].y < positions["B"].y
        assert positions["B"].y < positions["C"].y

    def test_two_children(self) -> None:
        """Parent with two children should spread children horizontally."""
        nodes = ["parent", "child1", "child2"]
        edges = [("parent", "child1"), ("parent", "child2")]
        positions = compute_tree_layout(nodes, edges, 100, 50)

        # Children should be on same level
        assert positions["child1"].y == positions["child2"].y
        # Children should be spread horizontally
        assert positions["child1"].x != positions["child2"].x

    def test_disconnected_nodes_handled(self) -> None:
        """Disconnected nodes should still get positions."""
        nodes = ["A", "B", "C"]  # No edges - all disconnected
        edges: list[tuple[str, str]] = []
        positions = compute_tree_layout(nodes, edges, 100, 50)

        # All nodes should have positions
        assert len(positions) == 3


class TestComputeForceLayout:
    """Tests for force-directed layout computation."""

    def test_empty_graph(self) -> None:
        """Empty graph should return empty positions."""
        positions = compute_force_layout([], [], 100, 50)
        assert positions == {}

    def test_single_node(self) -> None:
        """Single node should be positioned."""
        positions = compute_force_layout(["A"], [], 100, 50, iterations=10)
        assert "A" in positions

    def test_connected_nodes_closer(self) -> None:
        """Connected nodes should be pulled closer together than unconnected."""
        # Two connected nodes
        nodes = ["A", "B", "C"]
        edges = [("A", "B")]  # A-B connected, C isolated
        positions = compute_force_layout(nodes, edges, 100, 100, iterations=100)

        # Calculate distances
        def dist(p1: NodePosition, p2: NodePosition) -> float:
            return float(((p1.x - p2.x) ** 2 + (p1.y - p2.y) ** 2) ** 0.5)

        ab_dist = dist(positions["A"], positions["B"])
        ac_dist = dist(positions["A"], positions["C"])
        bc_dist = dist(positions["B"], positions["C"])

        # A-B should be closer than at least one of the unconnected pairs
        # (due to spring attraction)
        assert ab_dist < max(ac_dist, bc_dist)

    def test_positions_within_bounds(self) -> None:
        """All positions should be within the specified bounds."""
        nodes = ["A", "B", "C", "D"]
        edges = [("A", "B"), ("B", "C"), ("C", "D")]
        width, height = 100, 50
        positions = compute_force_layout(nodes, edges, width, height, iterations=50)

        for pos in positions.values():
            assert 0 <= pos.x < width, f"x={pos.x} out of bounds"
            assert 0 <= pos.y < height, f"y={pos.y} out of bounds"


class TestRenderGraphToLines:
    """Tests for rendering graph to ASCII lines."""

    def test_empty_graph(self) -> None:
        """Empty graph should render empty canvas."""
        lines = render_graph_to_lines([], [], {}, 20, 10)
        # Should have 10 lines of 20 spaces
        assert len(lines) == 10
        assert all(len(line) == 20 for line in lines)
        # All spaces
        assert all(line.strip() == "" for line in lines)

    def test_single_node_renders_box(self) -> None:
        """Single node should render as a box with label."""
        nodes = ["K"]
        positions = {"K": NodePosition(x=5, y=3, width=7, height=3)}
        lines = render_graph_to_lines(nodes, [], positions, 20, 10)

        # Should contain box characters
        content = "\n".join(lines)
        assert "K" in content, "Node label should appear"
        assert any(c in content for c in "┌─┐└┘│"), "Box characters should appear"

    def test_focused_node_highlighted(self) -> None:
        """Focused node should use bold box characters."""
        nodes = ["K"]
        positions = {"K": NodePosition(x=5, y=3, width=7, height=3)}
        lines = render_graph_to_lines(nodes, [], positions, 20, 10, focused_node="K")

        content = "\n".join(lines)
        # Bold box uses ┏┓┗┛━┃ instead of ┌┐└┘─│
        assert any(c in content for c in "┏┓┗┛━┃"), "Focused node should use bold box"

    def test_edge_renders_dots(self) -> None:
        """Edge between nodes should render as dotted line."""
        nodes = ["A", "B"]
        positions = {
            "A": NodePosition(x=2, y=2, width=5, height=3),
            "B": NodePosition(x=15, y=2, width=5, height=3),
        }
        edges = [("A", "B")]
        lines = render_graph_to_lines(nodes, edges, positions, 25, 8)

        content = "\n".join(lines)
        # Should contain edge characters
        assert "·" in content or "►" in content, "Edge should be visible"


class TestGraphLayoutWidget:
    """Tests for GraphLayout widget class."""

    def test_init_defaults(self) -> None:
        """Widget should initialize with empty defaults."""
        widget = GraphLayout()
        assert widget.nodes == []
        assert widget.edges == []
        assert widget.layout_algorithm == LayoutAlgorithm.SEMANTIC
        assert widget.focused_node is None

    def test_init_with_data(self) -> None:
        """Widget should accept nodes and edges."""
        widget = GraphLayout(
            nodes=["A", "B"],
            edges=[("A", "B")],
            layout=LayoutAlgorithm.TREE,
            focused_node="A",
        )
        assert widget.nodes == ["A", "B"]
        assert widget.edges == [("A", "B")]
        assert widget.layout_algorithm == LayoutAlgorithm.TREE
        assert widget.focused_node == "A"

    def test_string_layout_converted(self) -> None:
        """String layout should be converted to enum."""
        widget = GraphLayout(layout="tree")
        assert widget.layout_algorithm == LayoutAlgorithm.TREE

        widget2 = GraphLayout(layout="force")
        assert widget2.layout_algorithm == LayoutAlgorithm.FORCE

    def test_add_node(self) -> None:
        """add_node should add new nodes."""
        widget = GraphLayout()
        widget.add_node("A")
        widget.add_node("B")
        assert "A" in widget.nodes
        assert "B" in widget.nodes

    def test_add_node_idempotent(self) -> None:
        """Adding same node twice should not duplicate."""
        widget = GraphLayout()
        widget.add_node("A")
        widget.add_node("A")
        assert widget.nodes.count("A") == 1

    def test_remove_node(self) -> None:
        """remove_node should remove node and its edges."""
        widget = GraphLayout(
            nodes=["A", "B", "C"],
            edges=[("A", "B"), ("B", "C")],
        )
        widget.remove_node("B")

        assert "B" not in widget.nodes
        assert ("A", "B") not in widget.edges
        assert ("B", "C") not in widget.edges

    def test_add_edge(self) -> None:
        """add_edge should add edges."""
        widget = GraphLayout(nodes=["A", "B"])
        widget.add_edge("A", "B")
        assert ("A", "B") in widget.edges

    def test_add_edge_idempotent(self) -> None:
        """Adding same edge twice should not duplicate."""
        widget = GraphLayout(nodes=["A", "B"])
        widget.add_edge("A", "B")
        widget.add_edge("A", "B")
        assert widget.edges.count(("A", "B")) == 1

    def test_remove_edge(self) -> None:
        """remove_edge should remove specific edge."""
        widget = GraphLayout(
            nodes=["A", "B", "C"],
            edges=[("A", "B"), ("B", "C")],
        )
        widget.remove_edge("A", "B")

        assert ("A", "B") not in widget.edges
        assert ("B", "C") in widget.edges  # Other edge preserved

    def test_set_focus(self) -> None:
        """set_focus should update focused_node."""
        widget = GraphLayout(nodes=["A", "B"])
        widget.set_focus("A")
        assert widget.focused_node == "A"

        widget.set_focus(None)
        assert widget.focused_node is None

    def test_cycle_layout(self) -> None:
        """cycle_layout should cycle through all algorithms."""
        widget = GraphLayout()
        assert widget.layout_algorithm == LayoutAlgorithm.SEMANTIC

        widget.cycle_layout()
        # mypy doesn't track reactive value changes
        assert widget.layout_algorithm == LayoutAlgorithm.TREE  # type: ignore[comparison-overlap]

        widget.cycle_layout()
        assert widget.layout_algorithm == LayoutAlgorithm.FORCE  # type: ignore[comparison-overlap]

        widget.cycle_layout()
        assert widget.layout_algorithm == LayoutAlgorithm.SEMANTIC  # Back to start


class TestGraphLayoutRender:
    """Tests for GraphLayout rendering."""

    def test_render_empty_shows_message(self) -> None:
        """Empty graph should show 'No nodes' message."""
        widget = GraphLayout()
        # Set size for rendering
        widget._size = (40, 15)  # type: ignore
        result = widget.render()
        assert "No nodes" in str(result)

    def test_render_with_nodes(self) -> None:
        """Graph with nodes should render content."""
        widget = GraphLayout(nodes=["K", "D"])
        widget._size = (40, 15)  # type: ignore
        result = str(widget.render())

        # Should contain node labels
        assert "K" in result
        assert "D" in result


class TestGraphLayoutBoundaryConditions:
    """Tests for boundary conditions and edge cases."""

    def test_many_nodes_performance(self) -> None:
        """Layout should handle many nodes without error."""
        # Create 50 nodes
        nodes = [f"N{i}" for i in range(50)]
        edges = [(f"N{i}", f"N{i + 1}") for i in range(49)]

        # Should complete without error
        positions = compute_semantic_layout(nodes, 200, 100)
        assert len(positions) == 50

        positions_tree = compute_tree_layout(nodes, edges, 200, 100)
        assert len(positions_tree) == 50

        # Force layout with fewer iterations for performance
        positions_force = compute_force_layout(nodes, edges, 200, 100, iterations=10)
        assert len(positions_force) == 50

    def test_negative_entropy_clamped(self) -> None:
        """Graph should handle unusual node IDs gracefully."""
        # Unusual but valid node IDs
        weird_nodes = [
            "",
            "  ",
            "123",
            "!@#",
            "very-long-node-name-that-exceeds-normal-limits",
        ]
        positions = compute_semantic_layout(weird_nodes, 100, 50)

        # Should have positions for all
        assert len(positions) == len(weird_nodes)

    def test_self_referential_edge(self) -> None:
        """Edge from node to itself should not crash."""
        nodes = ["A"]
        edges = [("A", "A")]  # Self-loop

        # Should not crash
        positions = compute_tree_layout(nodes, edges, 100, 50)
        assert "A" in positions

    def test_edge_to_nonexistent_node(self) -> None:
        """Edge to non-existent node should be handled gracefully."""
        nodes = ["A", "B"]
        edges = [("A", "B"), ("B", "NONEXISTENT")]

        # Should not crash
        positions = compute_tree_layout(nodes, edges, 100, 50)
        assert "A" in positions
        assert "B" in positions


class TestNodePosition:
    """Tests for NodePosition dataclass."""

    def test_default_dimensions(self) -> None:
        """NodePosition should have default width and height."""
        pos = NodePosition(x=10, y=20)
        assert pos.width == 7
        assert pos.height == 3

    def test_custom_dimensions(self) -> None:
        """NodePosition should accept custom dimensions."""
        pos = NodePosition(x=10, y=20, width=10, height=5)
        assert pos.width == 10
        assert pos.height == 5
