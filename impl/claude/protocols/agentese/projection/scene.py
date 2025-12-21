"""
SceneGraph: Target-Agnostic Visual Abstraction Layer.

The SceneGraph is the ontology. The projection target is the substrate.

Laws (verified in tests):
    Law 1 (Identity): SceneGraph.empty() >> G ≡ G ≡ G >> SceneGraph.empty()
    Law 2 (Associativity): (A >> B) >> C ≡ A >> (B >> C)
    Law 3 (Immutability): SceneGraph and SceneNode are frozen
    Law 4 (Node Kind Semantics): Each kind maps to specific visual semantics

Design Philosophy:
    - SceneGraph is the intermediate representation between WARP primitives
      and projection targets (React, Servo, CLI, etc.)
    - SceneNode kinds are semantic, not visual (TRACE means "trace visualization",
      not "blue box")
    - Layout is declarative (what, not how)
    - Composition is categorical (>> operator, functor laws)

See:
    - spec/protocols/servo-substrate.md (ServoScene spec)
    - spec/protocols/warp-primitives.md (WARP primitives)
    - docs/skills/projection-target.md (projection patterns)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum, auto
from typing import TYPE_CHECKING, Any, NewType
from uuid import uuid4

if TYPE_CHECKING:
    from services.witness.mark import Mark

# =============================================================================
# Type Aliases
# =============================================================================

SceneNodeId = NewType("SceneNodeId", str)
SceneGraphId = NewType("SceneGraphId", str)


def generate_node_id() -> SceneNodeId:
    """Generate a unique SceneNode ID."""
    return SceneNodeId(f"sn-{uuid4().hex[:12]}")


def generate_graph_id() -> SceneGraphId:
    """Generate a unique SceneGraph ID."""
    return SceneGraphId(f"sg-{uuid4().hex[:12]}")


# =============================================================================
# Node Kinds (Semantic, Not Visual)
# =============================================================================


class SceneNodeKind(Enum):
    """
    Semantic node types for scene rendering.

    Each kind maps to specific visual semantics:
    - PANEL: Container with borders and padding
    - TRACE: Mark visualization (timeline item)
    - INTENT: IntentTree node (task/goal)
    - OFFERING: Scope badge (context indicator)
    - COVENANT: Permission indicator (trust level)
    - WALK: Walk timeline (session progress)
    - RITUAL: Playbook state (workflow phase)
    - TEXT: Plain text content
    - GROUP: Grouping container (no visual, just structure)
    """

    PANEL = auto()  # Container with borders
    TRACE = auto()  # Mark visualization
    INTENT = auto()  # IntentTree node
    OFFERING = auto()  # Scope badge
    COVENANT = auto()  # Permission indicator
    WALK = auto()  # Walk timeline
    RITUAL = auto()  # Playbook state
    TEXT = auto()  # Plain text
    GROUP = auto()  # Structural grouping


# =============================================================================
# Layout Directives (Elastic, Declarative)
# =============================================================================


class LayoutMode(Enum):
    """
    Elastic layout modes (from elastic-ui-patterns.md).

    - COMPACT: Minimal, mobile-first (single column)
    - COMFORTABLE: Balanced, default (responsive)
    - SPACIOUS: Rich, desktop (multi-column, sidebars)
    """

    COMPACT = auto()
    COMFORTABLE = auto()
    SPACIOUS = auto()


@dataclass(frozen=True)
class LayoutDirective:
    """
    Declarative layout specification.

    Layouts are elastic: they adapt to the projection target's capabilities.
    A CLI target ignores spatial layout; a Servo target honors it fully.

    Philosophy:
        "What, not how" - declare relationships, let the target decide rendering.
    """

    direction: str = "vertical"  # "vertical", "horizontal", "grid", "free"
    mode: LayoutMode = LayoutMode.COMFORTABLE
    gap: float = 1.0  # Relative gap between children (1.0 = default)
    padding: float = 1.0  # Relative padding (1.0 = default)
    align: str = "start"  # "start", "center", "end", "stretch"
    wrap: bool = False  # Allow wrapping for horizontal layouts

    @classmethod
    def vertical(
        cls, gap: float = 1.0, mode: LayoutMode = LayoutMode.COMFORTABLE
    ) -> LayoutDirective:
        """Create vertical (column) layout."""
        return cls(direction="vertical", gap=gap, mode=mode)

    @classmethod
    def horizontal(cls, gap: float = 1.0, wrap: bool = False) -> LayoutDirective:
        """Create horizontal (row) layout."""
        return cls(direction="horizontal", gap=gap, wrap=wrap)

    @classmethod
    def grid(cls, gap: float = 1.0) -> LayoutDirective:
        """Create grid layout."""
        return cls(direction="grid", gap=gap)

    @classmethod
    def free(cls) -> LayoutDirective:
        """Create free-form layout (nodes position themselves)."""
        return cls(direction="free")

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "direction": self.direction,
            "mode": self.mode.name,
            "gap": self.gap,
            "padding": self.padding,
            "align": self.align,
            "wrap": self.wrap,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> LayoutDirective:
        """Create from dictionary."""
        return cls(
            direction=data.get("direction", "vertical"),
            mode=LayoutMode[data.get("mode", "COMFORTABLE")],
            gap=data.get("gap", 1.0),
            padding=data.get("padding", 1.0),
            align=data.get("align", "start"),
            wrap=data.get("wrap", False),
        )


# =============================================================================
# Style (Joy-Inducing)
# =============================================================================


@dataclass(frozen=True)
class NodeStyle:
    """
    Node visual style (joy-inducing, not mechanical).

    Philosophy (from crown-jewels-genesis-moodboard.md):
        "Warm, breathing machinery; organic motion"
        "Watercolor textures, hand-made softness"

    These are hints to the projection target. A CLI target ignores most;
    a Servo target honors them fully.
    """

    # Colors (Living Earth palette)
    background: str | None = None  # e.g., "soil", "sage", "amber"
    foreground: str | None = None  # e.g., "living_green", "copper"
    border: str | None = None

    # Animation hints
    breathing: bool = False  # Subtle pulse (3-4s period)
    unfurling: bool = False  # Organic expand animation

    # Texture hints
    paper_grain: bool = False  # Subtle texture overlay

    # Opacity
    opacity: float = 1.0

    @classmethod
    def default(cls) -> NodeStyle:
        """Default style (no overrides)."""
        return cls()

    @classmethod
    def breathing_panel(cls) -> NodeStyle:
        """Panel with breathing animation."""
        return cls(breathing=True)

    @classmethod
    def trace_item(cls) -> NodeStyle:
        """Style for trace timeline items."""
        return cls(background="sage", paper_grain=True)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "background": self.background,
            "foreground": self.foreground,
            "border": self.border,
            "breathing": self.breathing,
            "unfurling": self.unfurling,
            "paper_grain": self.paper_grain,
            "opacity": self.opacity,
        }


# =============================================================================
# Interaction (Observer-Dependent)
# =============================================================================


@dataclass(frozen=True)
class Interaction:
    """
    Node interaction hint.

    Interactions are observer-dependent: what's clickable for a tech_lead
    may be read-only for a reviewer.
    """

    kind: str  # "click", "hover", "focus", "drag"
    action: str  # AGENTESE path or callback name
    requires_trust: int = 0  # Minimum trust level (0-3)
    metadata: dict[str, Any] = field(default_factory=dict)


# =============================================================================
# SceneNode (Atomic Visual Element)
# =============================================================================


@dataclass(frozen=True)
class SceneNode:
    """
    Atomic visual element in the scene graph.

    Laws:
        Law 3 (Immutability): SceneNodes are frozen after creation
        Law 4 (Kind Semantics): Each kind maps to specific visual semantics

    A SceneNode captures:
        - WHAT it is (kind)
        - WHAT it contains (content)
        - HOW it looks (style)
        - WHAT can be done (interactions)

    Example:
        >>> node = SceneNode(
        ...     kind=SceneNodeKind.TRACE,
        ...     content={"trace_id": "abc", "origin": "witness"},
        ...     label="Mark #47",
        ...     style=NodeStyle.trace_item(),
        ... )
    """

    # Identity
    id: SceneNodeId = field(default_factory=generate_node_id)

    # Semantics
    kind: SceneNodeKind = SceneNodeKind.TEXT

    # Content (kind-specific)
    content: Any = None  # Mark, Intent, text, etc.
    label: str = ""  # Human-readable label

    # Visual
    style: NodeStyle = field(default_factory=NodeStyle.default)

    # Layout hints (for this node within parent)
    flex: float = 1.0  # Flex grow factor
    min_width: float | None = None
    min_height: float | None = None

    # Interactions
    interactions: tuple[Interaction, ...] = ()

    # Metadata
    metadata: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def text(cls, content: str, label: str = "") -> SceneNode:
        """Create text node."""
        return cls(kind=SceneNodeKind.TEXT, content=content, label=label)

    @classmethod
    def panel(cls, label: str, style: NodeStyle | None = None) -> SceneNode:
        """Create panel node."""
        return cls(
            kind=SceneNodeKind.PANEL,
            label=label,
            style=style or NodeStyle.default(),
        )

    @classmethod
    def from_trace(cls, trace_node: Mark, label: str = "") -> SceneNode:
        """Create scene node from Mark."""
        return cls(
            kind=SceneNodeKind.TRACE,
            content=trace_node.to_dict() if hasattr(trace_node, "to_dict") else trace_node,
            label=label or f"Trace: {trace_node.origin}",
            style=NodeStyle.trace_item(),
            metadata={"trace_id": str(trace_node.id), "origin": trace_node.origin},
        )

    def with_interaction(self, interaction: Interaction) -> SceneNode:
        """Return new node with added interaction (immutable pattern)."""
        return SceneNode(
            id=self.id,
            kind=self.kind,
            content=self.content,
            label=self.label,
            style=self.style,
            flex=self.flex,
            min_width=self.min_width,
            min_height=self.min_height,
            interactions=self.interactions + (interaction,),
            metadata=self.metadata,
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        content = self.content
        if hasattr(content, "to_dict"):
            content = content.to_dict()

        return {
            "id": str(self.id),
            "kind": self.kind.name,
            "content": content,
            "label": self.label,
            "style": self.style.to_dict(),
            "flex": self.flex,
            "min_width": self.min_width,
            "min_height": self.min_height,
            "interactions": [
                {"kind": i.kind, "action": i.action, "requires_trust": i.requires_trust}
                for i in self.interactions
            ],
            "metadata": self.metadata,
        }


# =============================================================================
# SceneEdge (Graph Connections)
# =============================================================================


@dataclass(frozen=True)
class SceneEdge:
    """
    Edge between SceneNodes in a graph layout.

    Used for:
    - Intent dependency visualization
    - Trace causality arrows
    - Walk progression lines
    """

    source: SceneNodeId
    target: SceneNodeId
    label: str = ""
    style: str = "solid"  # "solid", "dashed", "dotted"
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "source": str(self.source),
            "target": str(self.target),
            "label": self.label,
            "style": self.style,
            "metadata": self.metadata,
        }


# =============================================================================
# SceneGraph (Composable Scene Structure)
# =============================================================================


@dataclass(frozen=True)
class SceneGraph:
    """
    Composable scene structure with category laws.

    Laws:
        Law 1 (Identity): SceneGraph.empty() >> G ≡ G ≡ G >> SceneGraph.empty()
        Law 2 (Associativity): (A >> B) >> C ≡ A >> (B >> C)

    A SceneGraph is:
        - A list of SceneNodes
        - A list of SceneEdges (for graph layouts)
        - A LayoutDirective
        - Immutable (frozen)

    Composition:
        >>> header = SceneGraph(nodes=[header_node])
        >>> body = SceneGraph(nodes=[content_node])
        >>> page = header >> body  # Vertically stacked

    Example:
        >>> graph = SceneGraph(
        ...     nodes=[
        ...         SceneNode.panel("Dashboard"),
        ...         SceneNode.text("Welcome to kgents"),
        ...     ],
        ...     layout=LayoutDirective.vertical(),
        ... )
    """

    # Identity
    id: SceneGraphId = field(default_factory=generate_graph_id)

    # Content
    nodes: tuple[SceneNode, ...] = ()
    edges: tuple[SceneEdge, ...] = ()

    # Layout
    layout: LayoutDirective = field(default_factory=LayoutDirective.vertical)

    # Metadata
    title: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    # Temporal (for Walk/Playbook views)
    created_at: datetime = field(default_factory=datetime.now)

    @classmethod
    def empty(cls) -> SceneGraph:
        """
        Create empty scene graph (identity element for composition).

        Law 1: empty() >> G ≡ G ≡ G >> empty()
        """
        return cls(nodes=(), edges=(), title="empty")

    @classmethod
    def from_nodes(
        cls, nodes: list[SceneNode], layout: LayoutDirective | None = None
    ) -> SceneGraph:
        """Create scene graph from list of nodes."""
        return cls(
            nodes=tuple(nodes),
            layout=layout or LayoutDirective.vertical(),
        )

    @classmethod
    def panel(
        cls, label: str, *children: SceneNode, layout: LayoutDirective | None = None
    ) -> SceneGraph:
        """Create panel scene graph with children."""
        panel_node = SceneNode.panel(label)
        return cls(
            nodes=(panel_node,) + tuple(children),
            layout=layout or LayoutDirective.vertical(),
            title=label,
        )

    def __rshift__(self, other: SceneGraph) -> SceneGraph:
        """
        Compose two SceneGraphs (>> operator).

        Law 2 (Associativity): (A >> B) >> C ≡ A >> (B >> C)

        Composition strategy:
        - Nodes are concatenated (self.nodes + other.nodes)
        - Edges are concatenated
        - Layout of self is preserved (left-dominant)
        - New ID is generated
        """
        if not self.nodes:
            # Identity: empty >> G = G
            return other
        if not other.nodes:
            # Identity: G >> empty = G
            return self

        return SceneGraph(
            nodes=self.nodes + other.nodes,
            edges=self.edges + other.edges,
            layout=self.layout,  # Left-dominant layout
            title=f"{self.title} >> {other.title}"
            if self.title and other.title
            else self.title or other.title,
            metadata={**self.metadata, **other.metadata},
        )

    def is_empty(self) -> bool:
        """Check if this is an empty graph."""
        return len(self.nodes) == 0

    def node_count(self) -> int:
        """Return number of nodes."""
        return len(self.nodes)

    def find_node(self, node_id: SceneNodeId) -> SceneNode | None:
        """Find node by ID."""
        for node in self.nodes:
            if node.id == node_id:
                return node
        return None

    def nodes_by_kind(self, kind: SceneNodeKind) -> tuple[SceneNode, ...]:
        """Get all nodes of a specific kind."""
        return tuple(n for n in self.nodes if n.kind == kind)

    def with_node(self, node: SceneNode) -> SceneGraph:
        """Return new graph with added node (immutable pattern)."""
        return SceneGraph(
            id=self.id,
            nodes=self.nodes + (node,),
            edges=self.edges,
            layout=self.layout,
            title=self.title,
            metadata=self.metadata,
            created_at=self.created_at,
        )

    def with_edge(self, edge: SceneEdge) -> SceneGraph:
        """Return new graph with added edge (immutable pattern)."""
        return SceneGraph(
            id=self.id,
            nodes=self.nodes,
            edges=self.edges + (edge,),
            layout=self.layout,
            title=self.title,
            metadata=self.metadata,
            created_at=self.created_at,
        )

    def with_layout(self, layout: LayoutDirective) -> SceneGraph:
        """Return new graph with different layout."""
        return SceneGraph(
            id=self.id,
            nodes=self.nodes,
            edges=self.edges,
            layout=layout,
            title=self.title,
            metadata=self.metadata,
            created_at=self.created_at,
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "id": str(self.id),
            "nodes": [n.to_dict() for n in self.nodes],
            "edges": [e.to_dict() for e in self.edges],
            "layout": self.layout.to_dict(),
            "title": self.title,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
        }

    def __repr__(self) -> str:
        """Concise representation."""
        return f"SceneGraph(nodes={len(self.nodes)}, edges={len(self.edges)}, layout={self.layout.direction})"


# =============================================================================
# Composition Utilities
# =============================================================================


def compose_scenes(*scenes: SceneGraph) -> SceneGraph:
    """
    Compose multiple SceneGraphs left-to-right.

    This is the multi-arity version of >>:
        compose_scenes(A, B, C) ≡ A >> B >> C

    Law 2 ensures this is well-defined regardless of grouping.
    """
    if not scenes:
        return SceneGraph.empty()

    result = scenes[0]
    for scene in scenes[1:]:
        result = result >> scene

    return result


# =============================================================================
# Module Exports
# =============================================================================

__all__ = [
    # Type aliases
    "SceneNodeId",
    "SceneGraphId",
    "generate_node_id",
    "generate_graph_id",
    # Node kinds
    "SceneNodeKind",
    # Layout
    "LayoutMode",
    "LayoutDirective",
    # Style
    "NodeStyle",
    # Interaction
    "Interaction",
    # Core types
    "SceneNode",
    "SceneEdge",
    "SceneGraph",
    # Utilities
    "compose_scenes",
]
