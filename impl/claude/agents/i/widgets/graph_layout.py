"""
GraphLayout Widget - 2D node-edge graph visualization.

Renders agents as nodes in a semantic layout with FlowArrow connections.
The Garden View needs this: agents are nodes, connections are FlowArrows.

WHAT: Layouts nodes (agents) in 2D space with edges (connections).
WHY: The ecosystem is not flat - agents relate topologically.
     Semantic positioning respects agent taxonomy (A-gents left, D-gents right).
HOW: GraphLayout(nodes=["K", "L", "D"], edges=[("K", "L"), ("L", "D")])
FEEL: Like looking down at a city from above - seeing the flow of traffic
      between districts. The topology IS the insight.

Layout algorithms:
  - semantic: Positions based on agent type (A-gents left, D-gents right, K center)
  - tree: Hierarchical top-down layout
  - force: Force-directed (springs between connected nodes)

Principle 5 (Composable): Composes with FlowArrow for edges.
Principle 7 (Generative): Minimal parameters generate complex layouts.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import TYPE_CHECKING

from textual.reactive import reactive
from textual.widget import Widget

if TYPE_CHECKING:
    from textual.app import RenderResult


class LayoutAlgorithm(Enum):
    """Layout algorithm for node positioning."""

    SEMANTIC = "semantic"  # Position based on agent type
    TREE = "tree"  # Hierarchical top-down
    FORCE = "force"  # Force-directed spring layout


@dataclass
class NodePosition:
    """Position of a node in the graph."""

    x: int
    y: int
    width: int = 7
    height: int = 3


# Semantic positions for agent types (by first letter)
# These map agent type to (x_weight, y_weight) where:
# - x_weight: 0.0 = left, 1.0 = right
# - y_weight: 0.0 = top, 1.0 = bottom
SEMANTIC_POSITIONS: dict[str, tuple[float, float]] = {
    # A-gents: Abstract architectures (upper left)
    "A": (0.15, 0.2),
    # B-gents: Bio/Economic (upper middle-left)
    "B": (0.3, 0.15),
    # C-gents: Category theory (upper middle)
    "C": (0.5, 0.1),
    # D-gents: Data/State (right side, near K)
    "D": (0.8, 0.4),
    # E-gents: Evolution (lower left)
    "E": (0.2, 0.7),
    # K-gent: Kent simulacra (CENTER - the fixed point)
    "K": (0.5, 0.5),
    # L-gents: Lattice/Library (left of D)
    "L": (0.65, 0.5),
    # M-gents: Memory/Map (below K)
    "M": (0.5, 0.7),
    # N-gents: Narrative (lower right)
    "N": (0.75, 0.7),
    # T-gents: Testing (lower middle)
    "T": (0.4, 0.8),
    # U-gents: Utility (right side)
    "U": (0.85, 0.5),
    # Y-gent: Y-Combinator (top)
    "Y": (0.5, 0.05),
}


def get_semantic_position(node_id: str) -> tuple[float, float]:
    """
    Get semantic position for a node based on its ID.

    The first character determines the agent type.
    Unknown types default to center-ish with slight randomization.

    Args:
        node_id: Node identifier (e.g., "K-gent", "Dgent", "L")

    Returns:
        (x_weight, y_weight) tuple where 0.0 = left/top, 1.0 = right/bottom
    """
    if not node_id:
        return (0.5, 0.5)

    # Get first character (uppercase)
    first_char = node_id[0].upper()

    if first_char in SEMANTIC_POSITIONS:
        return SEMANTIC_POSITIONS[first_char]

    # Default: hash-based position for unknown types
    # This ensures consistent positioning for the same unknown node
    hash_val = hash(node_id)
    x = 0.3 + (hash_val % 100) / 250  # Range: 0.3-0.7
    y = 0.3 + ((hash_val >> 8) % 100) / 250  # Range: 0.3-0.7
    return (x, y)


def compute_tree_layout(
    nodes: list[str],
    edges: list[tuple[str, str]],
    width: int,
    height: int,
) -> dict[str, NodePosition]:
    """
    Compute tree layout (hierarchical top-down).

    Assumes edges point from parent to child.
    Nodes with no incoming edges are roots.
    """
    # Find roots (nodes with no incoming edges)
    children_of: dict[str, list[str]] = {n: [] for n in nodes}
    has_parent: set[str] = set()

    for src, dst in edges:
        if src in children_of:
            children_of[src].append(dst)
        has_parent.add(dst)

    roots = [n for n in nodes if n not in has_parent]
    if not roots:
        roots = nodes[:1] if nodes else []

    # BFS to assign levels
    levels: dict[str, int] = {}
    level_nodes: dict[int, list[str]] = {}
    queue = [(r, 0) for r in roots]
    visited: set[str] = set()

    while queue:
        node, level = queue.pop(0)
        if node in visited:
            continue
        visited.add(node)
        levels[node] = level
        level_nodes.setdefault(level, []).append(node)

        for child in children_of.get(node, []):
            if child not in visited:
                queue.append((child, level + 1))

    # Handle disconnected nodes
    for node in nodes:
        if node not in levels:
            max_level = max(level_nodes.keys()) if level_nodes else 0
            levels[node] = max_level + 1
            level_nodes.setdefault(max_level + 1, []).append(node)

    # Compute positions
    positions: dict[str, NodePosition] = {}
    num_levels = max(level_nodes.keys()) + 1 if level_nodes else 1

    for level, level_node_list in level_nodes.items():
        y = int(height * (level + 0.5) / num_levels)
        num_in_level = len(level_node_list)

        for i, node in enumerate(level_node_list):
            x = int(width * (i + 0.5) / num_in_level)
            positions[node] = NodePosition(x=x, y=y)

    return positions


def compute_semantic_layout(
    nodes: list[str],
    width: int,
    height: int,
) -> dict[str, NodePosition]:
    """
    Compute semantic layout based on agent taxonomy.

    K-gent is always at center. Other agents positioned by type.
    """
    positions: dict[str, NodePosition] = {}
    node_width = 7
    node_height = 3

    for node in nodes:
        x_weight, y_weight = get_semantic_position(node)

        # Convert weight to actual position (with margin)
        margin_x = node_width
        margin_y = node_height
        usable_width = width - 2 * margin_x
        usable_height = height - 2 * margin_y

        x = int(margin_x + x_weight * usable_width)
        y = int(margin_y + y_weight * usable_height)

        positions[node] = NodePosition(x=x, y=y, width=node_width, height=node_height)

    return positions


def compute_force_layout(
    nodes: list[str],
    edges: list[tuple[str, str]],
    width: int,
    height: int,
    iterations: int = 50,
) -> dict[str, NodePosition]:
    """
    Compute force-directed layout.

    Edges act as springs pulling connected nodes together.
    All nodes repel each other (prevent overlap).
    """
    import math

    # Initialize random positions
    positions: dict[str, tuple[float, float]] = {}
    for i, node in enumerate(nodes):
        # Spread initially in a circle
        angle = 2 * math.pi * i / len(nodes) if nodes else 0
        radius = min(width, height) / 3
        x = width / 2 + radius * math.cos(angle)
        y = height / 2 + radius * math.sin(angle)
        positions[node] = (x, y)

    # Force-directed iterations
    for _ in range(iterations):
        forces: dict[str, tuple[float, float]] = {n: (0.0, 0.0) for n in nodes}

        # Repulsion between all pairs
        for i, n1 in enumerate(nodes):
            for n2 in nodes[i + 1 :]:
                x1, y1 = positions[n1]
                x2, y2 = positions[n2]
                dx = x2 - x1
                dy = y2 - y1
                dist = math.sqrt(dx * dx + dy * dy) + 0.1

                # Repulsion force (inverse square)
                repulsion = 500 / (dist * dist)
                fx = -repulsion * dx / dist
                fy = -repulsion * dy / dist

                f1x, f1y = forces[n1]
                f2x, f2y = forces[n2]
                forces[n1] = (f1x + fx, f1y + fy)
                forces[n2] = (f2x - fx, f2y - fy)

        # Attraction along edges
        for src, dst in edges:
            if src not in positions or dst not in positions:
                continue
            x1, y1 = positions[src]
            x2, y2 = positions[dst]
            dx = x2 - x1
            dy = y2 - y1
            dist = math.sqrt(dx * dx + dy * dy) + 0.1

            # Spring force
            attraction = dist * 0.05
            fx = attraction * dx / dist
            fy = attraction * dy / dist

            f1x, f1y = forces[src]
            f2x, f2y = forces[dst]
            forces[src] = (f1x + fx, f1y + fy)
            forces[dst] = (f2x - fx, f2y - fy)

        # Apply forces
        for node in nodes:
            x, y = positions[node]
            fx, fy = forces[node]

            # Damping
            x += fx * 0.1
            y += fy * 0.1

            # Keep in bounds
            x = max(5, min(width - 5, x))
            y = max(2, min(height - 2, y))

            positions[node] = (x, y)

    # Convert to NodePosition
    result: dict[str, NodePosition] = {}
    for node, (x, y) in positions.items():
        result[node] = NodePosition(x=int(x), y=int(y))

    return result


def render_graph_to_lines(
    nodes: list[str],
    edges: list[tuple[str, str]],
    positions: dict[str, NodePosition],
    width: int,
    height: int,
    focused_node: str | None = None,
) -> list[str]:
    """
    Render graph to ASCII lines.

    Nodes are rendered as boxes, edges as lines between them.
    """
    # Initialize canvas
    canvas: list[list[str]] = [[" " for _ in range(width)] for _ in range(height)]

    def safe_set(x: int, y: int, char: str) -> None:
        """Set character if within bounds."""
        if 0 <= x < width and 0 <= y < height:
            canvas[y][x] = char

    # Draw edges first (so nodes draw over them)
    edge_char = "·"  # Dotted line for edges
    for src, dst in edges:
        if src not in positions or dst not in positions:
            continue

        src_pos = positions[src]
        dst_pos = positions[dst]

        # Calculate center points
        x1 = src_pos.x + src_pos.width // 2
        y1 = src_pos.y + src_pos.height // 2
        x2 = dst_pos.x + dst_pos.width // 2
        y2 = dst_pos.y + dst_pos.height // 2

        # Draw line using Bresenham's algorithm (simplified)
        dx = abs(x2 - x1)
        dy = abs(y2 - y1)
        steps = max(dx, dy)

        if steps > 0:
            x_step = (x2 - x1) / steps
            y_step = (y2 - y1) / steps

            for i in range(steps + 1):
                x = int(x1 + x_step * i)
                y = int(y1 + y_step * i)
                safe_set(x, y, edge_char)

        # Draw arrow at destination
        if x2 > x1:
            safe_set(x2 - 1, y2, "►")
        elif x2 < x1:
            safe_set(x2 + 1, y2, "◄")
        elif y2 > y1:
            safe_set(x2, y2 - 1, "▼")
        elif y2 < y1:
            safe_set(x2, y2 + 1, "▲")

    # Draw nodes
    for node in nodes:
        if node not in positions:
            continue

        pos = positions[node]
        is_focused = node == focused_node

        # Draw box
        # Top border
        top_left = "┏" if is_focused else "┌"
        top_right = "┓" if is_focused else "┐"
        h_line = "━" if is_focused else "─"
        v_line = "┃" if is_focused else "│"
        bot_left = "┗" if is_focused else "└"
        bot_right = "┛" if is_focused else "┘"

        # Top
        safe_set(pos.x, pos.y, top_left)
        for dx in range(1, pos.width - 1):
            safe_set(pos.x + dx, pos.y, h_line)
        safe_set(pos.x + pos.width - 1, pos.y, top_right)

        # Sides and content
        for dy in range(1, pos.height - 1):
            safe_set(pos.x, pos.y + dy, v_line)
            safe_set(pos.x + pos.width - 1, pos.y + dy, v_line)

        # Bottom
        safe_set(pos.x, pos.y + pos.height - 1, bot_left)
        for dx in range(1, pos.width - 1):
            safe_set(pos.x + dx, pos.y + pos.height - 1, h_line)
        safe_set(pos.x + pos.width - 1, pos.y + pos.height - 1, bot_right)

        # Node label (centered in box)
        label = node[: pos.width - 2]  # Truncate if too long
        label_x = pos.x + 1 + (pos.width - 2 - len(label)) // 2
        label_y = pos.y + pos.height // 2

        for i, char in enumerate(label):
            safe_set(label_x + i, label_y, char)

    return ["".join(row) for row in canvas]


class GraphLayout(Widget):
    """
    2D graph layout widget.

    Renders a node-edge graph with semantic or algorithmic positioning.
    The Garden View uses this to show agent relationships.

    Nodes are rendered as boxes, edges as lines with arrows.
    Layout algorithm determines positioning:
    - semantic: Based on agent taxonomy (K at center)
    - tree: Hierarchical top-down
    - force: Spring-based physics

    Principle 5 (Composable): Composes with existing FlowArrow for edges.
    Principle 7 (Generative): Minimal spec generates full layout.
    """

    DEFAULT_CSS = """
    GraphLayout {
        width: 100%;
        height: 100%;
        min-width: 40;
        min-height: 15;
        color: #d4a574;
    }

    GraphLayout .node {
        color: #f5d08a;
    }

    GraphLayout .edge {
        color: #6a6560;
    }

    GraphLayout .focused {
        color: #e6a352;
        text-style: bold;
    }
    """

    # Reactive properties
    nodes: reactive[list[str]] = reactive(list, init=False)
    edges: reactive[list[tuple[str, str]]] = reactive(list, init=False)
    layout_algorithm: reactive[LayoutAlgorithm] = reactive(LayoutAlgorithm.SEMANTIC)
    focused_node: reactive[str | None] = reactive(None)

    def __init__(
        self,
        nodes: list[str] | None = None,
        edges: list[tuple[str, str]] | None = None,
        layout: LayoutAlgorithm | str = LayoutAlgorithm.SEMANTIC,
        focused_node: str | None = None,
        name: str | None = None,
        id: str | None = None,  # noqa: A002
        classes: str | None = None,
    ) -> None:
        """
        Initialize graph layout widget.

        Args:
            nodes: List of node IDs (e.g., ["K", "L", "D"])
            edges: List of (source, destination) tuples
            layout: Layout algorithm ("semantic", "tree", "force")
            focused_node: Currently focused node (highlighted)
            name: Widget name
            id: Widget ID
            classes: CSS classes
        """
        super().__init__(name=name, id=id, classes=classes)
        self.nodes = nodes if nodes is not None else []
        self.edges = edges if edges is not None else []

        # Handle string layout
        if isinstance(layout, str):
            layout = LayoutAlgorithm(layout.lower())
        self.layout_algorithm = layout
        self.focused_node = focused_node

    def render(self) -> "RenderResult":
        """Render the graph layout."""
        if not self.nodes:
            return "No nodes to display"

        width = max(40, self.size.width)
        height = max(15, self.size.height)

        # Compute positions based on layout algorithm
        if self.layout_algorithm == LayoutAlgorithm.SEMANTIC:
            positions = compute_semantic_layout(self.nodes, width, height)
        elif self.layout_algorithm == LayoutAlgorithm.TREE:
            positions = compute_tree_layout(self.nodes, self.edges, width, height)
        else:  # FORCE
            positions = compute_force_layout(self.nodes, self.edges, width, height)

        # Render to lines
        lines = render_graph_to_lines(
            self.nodes,
            self.edges,
            positions,
            width,
            height,
            self.focused_node,
        )

        return "\n".join(lines)

    def watch_nodes(self, new_nodes: list[str]) -> None:
        """React to node changes."""
        self.refresh()

    def watch_edges(self, new_edges: list[tuple[str, str]]) -> None:
        """React to edge changes."""
        self.refresh()

    def watch_layout_algorithm(self, new_layout: LayoutAlgorithm) -> None:
        """React to layout changes."""
        self.refresh()

    def watch_focused_node(self, new_focused: str | None) -> None:
        """React to focus changes."""
        self.refresh()

    def add_node(self, node_id: str) -> None:
        """Add a node to the graph."""
        if node_id not in self.nodes:
            self.nodes = self.nodes + [node_id]

    def remove_node(self, node_id: str) -> None:
        """Remove a node from the graph."""
        self.nodes = [n for n in self.nodes if n != node_id]
        # Also remove edges involving this node
        self.edges = [(s, d) for s, d in self.edges if s != node_id and d != node_id]

    def add_edge(self, source: str, destination: str) -> None:
        """Add an edge to the graph."""
        edge = (source, destination)
        if edge not in self.edges:
            self.edges = self.edges + [edge]

    def remove_edge(self, source: str, destination: str) -> None:
        """Remove an edge from the graph."""
        self.edges = [(s, d) for s, d in self.edges if not (s == source and d == destination)]

    def set_focus(self, node_id: str | None) -> None:
        """Set the focused node."""
        self.focused_node = node_id

    def cycle_layout(self) -> None:
        """Cycle through layout algorithms."""
        layouts = list(LayoutAlgorithm)
        current_idx = layouts.index(self.layout_algorithm)
        next_idx = (current_idx + 1) % len(layouts)
        self.layout_algorithm = layouts[next_idx]


# Export public API
__all__ = [
    "GraphLayout",
    "LayoutAlgorithm",
    "NodePosition",
    "get_semantic_position",
    "compute_semantic_layout",
    "compute_tree_layout",
    "compute_force_layout",
    "render_graph_to_lines",
    "SEMANTIC_POSITIONS",
]
