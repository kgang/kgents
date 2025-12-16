"""
TopologyGraphWidget: System topology visualization.

Visualizes agent systems, services, and their connections as a graph.
Uses semantic zoom (C4 model inspired) where zoom level = semantic depth.

Projections:
    - CLI: ASCII art graph with nodes and edges
    - TUI: Rich Panel with tree structure
    - MARIMO: Cytoscape.js or d3.js graph configuration
    - JSON: State dict for API/React rendering

Example:
    widget = TopologyGraphWidget(TopologyGraphState(
        nodes=(
            TopologyNode(id="soul", label="K-gent Soul", type="agent", status="active"),
            TopologyNode(id="memory", label="M-gent Memory", type="agent", status="idle"),
            TopologyNode(id="api", label="API Gateway", type="service", status="healthy"),
        ),
        edges=(
            TopologyEdge(source="soul", target="memory", label="queries"),
            TopologyEdge(source="api", target="soul", label="governs"),
        ),
    ))
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Literal

from agents.i.reactive.signal import Signal
from agents.i.reactive.widget import KgentsWidget, RenderTarget

if TYPE_CHECKING:
    from protocols.projection.schema import UIHint

NodeType = Literal["agent", "service", "external", "user", "database", "queue"]
NodeStatus = Literal["active", "idle", "healthy", "degraded", "error", "unknown"]
EdgeStyle = Literal["solid", "dashed", "dotted"]


@dataclass(frozen=True)
class TopologyNode:
    """
    A node in the topology graph.

    Attributes:
        id: Unique identifier
        label: Display label
        type: Node type (agent, service, etc.)
        status: Current health/activity status
        group: Optional grouping (for clustering)
        metadata: Additional key-value pairs
    """

    id: str
    label: str
    type: NodeType = "agent"
    status: NodeStatus = "unknown"
    group: str | None = None
    metadata: tuple[tuple[str, str], ...] = ()


@dataclass(frozen=True)
class TopologyEdge:
    """
    An edge (connection) in the topology graph.

    Attributes:
        source: Source node ID
        target: Target node ID
        label: Edge label (relationship type)
        style: Line style
        weight: Edge weight (thickness)
        bidirectional: Whether edge goes both ways
    """

    source: str
    target: str
    label: str = ""
    style: EdgeStyle = "solid"
    weight: float = 1.0
    bidirectional: bool = False


@dataclass(frozen=True)
class TopologyGraphState:
    """
    Immutable topology graph state.

    Attributes:
        nodes: All nodes in the graph
        edges: All edges in the graph
        title: Graph title
        highlight_node: ID of highlighted node (for focus)
        zoom_level: Semantic zoom level (1=overview, 3=detailed)
        layout: Graph layout algorithm hint
    """

    nodes: tuple[TopologyNode, ...] = ()
    edges: tuple[TopologyEdge, ...] = ()
    title: str = "System Topology"
    highlight_node: str | None = None
    zoom_level: int = 1  # 1=overview, 2=moderate, 3=detailed
    layout: Literal["hierarchical", "circular", "force", "grid"] = "hierarchical"


# Node type to emoji mapping for CLI/TUI
NODE_EMOJIS: dict[NodeType, str] = {
    "agent": "🤖",
    "service": "⚙️",
    "external": "🌐",
    "user": "👤",
    "database": "🗄️",
    "queue": "📬",
}

# Status to indicator mapping
STATUS_INDICATORS: dict[NodeStatus, str] = {
    "active": "●",
    "idle": "○",
    "healthy": "✓",
    "degraded": "⚠",
    "error": "✗",
    "unknown": "?",
}


class TopologyGraphWidget(KgentsWidget[TopologyGraphState]):
    """
    System topology visualization widget.

    Renders agents, services, and their connections as a graph.
    Supports semantic zoom where zoom level controls detail level.
    """

    def __init__(self, state: TopologyGraphState | None = None) -> None:
        self.state = Signal.of(state or TopologyGraphState())

    def project(self, target: RenderTarget) -> Any:
        """Project topology to target surface."""
        match target:
            case RenderTarget.CLI:
                return self._to_cli()
            case RenderTarget.TUI:
                return self._to_tui()
            case RenderTarget.MARIMO:
                return self._to_marimo()
            case RenderTarget.JSON:
                return self._to_json()

    def _to_cli(self) -> str:
        """CLI projection: ASCII graph representation."""
        s = self.state.value

        if not s.nodes:
            return "(empty topology)"

        lines = []
        if s.title:
            lines.append(f"╔{'═' * (len(s.title) + 2)}╗")
            lines.append(f"║ {s.title} ║")
            lines.append(f"╚{'═' * (len(s.title) + 2)}╝")
            lines.append("")

        # Group nodes by group attribute
        groups: dict[str | None, list[TopologyNode]] = {}
        for node in s.nodes:
            if node.group not in groups:
                groups[node.group] = []
            groups[node.group].append(node)

        # Render nodes by group
        for group, nodes in groups.items():
            if group:
                lines.append(f"┌─ {group} ──────────────────")

            for node in nodes:
                emoji = NODE_EMOJIS.get(node.type, "•")
                status = STATUS_INDICATORS.get(node.status, "?")
                highlight = "→" if node.id == s.highlight_node else " "
                lines.append(f"{highlight} {emoji} [{status}] {node.label} ({node.id})")

                # Show metadata at zoom level 3
                if s.zoom_level >= 3 and node.metadata:
                    for key, value in node.metadata:
                        lines.append(f"      └─ {key}: {value}")

            if group:
                lines.append("└────────────────────────────")
            lines.append("")

        # Render edges
        if s.edges and s.zoom_level >= 2:
            lines.append("Connections:")
            for edge in s.edges:
                arrow = "↔" if edge.bidirectional else "→"
                style_char = {
                    "solid": "─",
                    "dashed": "╌",
                    "dotted": "┄",
                }.get(edge.style, "─")
                label = f" ({edge.label})" if edge.label else ""
                lines.append(
                    f"  {edge.source} {style_char}{arrow} {edge.target}{label}"
                )

        return "\n".join(lines)

    def _to_tui(self) -> Any:
        """TUI projection: Rich Panel with tree structure."""
        try:
            from rich.panel import Panel
            from rich.tree import Tree

            s = self.state.value

            tree = Tree(f"🌐 {s.title}")

            # Group nodes
            groups: dict[str | None, list[TopologyNode]] = {}
            for node in s.nodes:
                if node.group not in groups:
                    groups[node.group] = []
                groups[node.group].append(node)

            for group, nodes in groups.items():
                if group:
                    branch = tree.add(f"📁 {group}")
                else:
                    branch = tree

                for node in nodes:
                    emoji = NODE_EMOJIS.get(node.type, "•")
                    status = STATUS_INDICATORS.get(node.status, "?")
                    style = "bold" if node.id == s.highlight_node else ""
                    node_branch = branch.add(
                        f"{emoji} [{status}] {node.label}", style=style
                    )

                    if s.zoom_level >= 3 and node.metadata:
                        for key, value in node.metadata:
                            node_branch.add(f"{key}: {value}", style="dim")

            return Panel(tree, title="Topology", border_style="blue")

        except ImportError:
            from rich.text import Text

            return Text(self._to_cli())

    def _to_marimo(self) -> str:
        """MARIMO projection: Cytoscape.js configuration."""
        import json

        s = self.state.value

        # Build Cytoscape.js elements
        elements = []

        # Nodes
        for node in s.nodes:
            elements.append(
                {
                    "data": {
                        "id": node.id,
                        "label": node.label,
                        "type": node.type,
                        "status": node.status,
                        "parent": node.group,
                    },
                    "classes": f"{node.type} {node.status}",
                }
            )

        # Add group nodes if groups exist
        groups_seen = set()
        for node in s.nodes:
            if node.group and node.group not in groups_seen:
                groups_seen.add(node.group)
                elements.append(
                    {
                        "data": {"id": node.group, "label": node.group},
                        "classes": "group",
                    }
                )

        # Edges
        for edge in s.edges:
            elements.append(
                {
                    "data": {
                        "id": f"{edge.source}-{edge.target}",
                        "source": edge.source,
                        "target": edge.target,
                        "label": edge.label,
                    },
                    "classes": edge.style,
                }
            )

        config_json = json.dumps(
            {
                "elements": elements,
                "layout": {"name": s.layout},
                "style": [
                    {"selector": "node", "style": {"label": "data(label)"}},
                    {
                        "selector": ".agent",
                        "style": {"background-color": "#3b82f6"},
                    },
                    {
                        "selector": ".service",
                        "style": {"background-color": "#22c55e"},
                    },
                    {
                        "selector": ".active",
                        "style": {"border-color": "#22c55e", "border-width": 3},
                    },
                    {
                        "selector": ".error",
                        "style": {"border-color": "#ef4444", "border-width": 3},
                    },
                ],
            }
        )

        return f"""
        <div class="kgents-topology-graph" data-cytoscape-config='{config_json}'>
            <div id="kgents-topology-{id(self)}" style="width: 100%; height: 400px;"></div>
        </div>
        <script>
            (function() {{
                const config = {config_json};
                config.container = document.getElementById('kgents-topology-{id(self)}');
                cytoscape(config);
            }})();
        </script>
        """

    def _to_json(self) -> dict[str, Any]:
        """JSON projection: state dict for API responses."""
        s = self.state.value
        return {
            "type": "topology_graph",
            "title": s.title,
            "nodes": [
                {
                    "id": n.id,
                    "label": n.label,
                    "type": n.type,
                    "status": n.status,
                    "group": n.group,
                    "metadata": dict(n.metadata),
                }
                for n in s.nodes
            ],
            "edges": [
                {
                    "source": e.source,
                    "target": e.target,
                    "label": e.label,
                    "style": e.style,
                    "weight": e.weight,
                    "bidirectional": e.bidirectional,
                }
                for e in s.edges
            ],
            "highlightNode": s.highlight_node,
            "zoomLevel": s.zoom_level,
            "layout": s.layout,
        }

    def ui_hint(self) -> "UIHint":
        """Return 'graph' UI hint for projection system."""
        return "graph"

    def widget_type(self) -> str:
        """Return widget type identifier."""
        return "topology_graph"


__all__ = [
    "TopologyGraphWidget",
    "TopologyGraphState",
    "TopologyNode",
    "TopologyEdge",
    "NodeType",
    "NodeStatus",
    "EdgeStyle",
]
