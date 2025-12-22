"""GraphView: Concept DAG view for K-Block content.

Renders content as a directed acyclic graph of concepts:
- Nodes: Headings and type definitions
- Edges: References and containment relationships
"""

from dataclasses import dataclass, field
from typing import Any, FrozenSet

from .base import ViewType
from .tokens import SemanticToken, TokenKind


@dataclass(frozen=True)
class GraphNode:
    """A node in the concept graph."""

    id: str
    label: str
    kind: str  # "heading", "type", "field"
    level: int = 0  # Heading level or nesting depth


@dataclass(frozen=True)
class GraphEdge:
    """An edge in the concept graph."""

    source: str
    target: str
    kind: str  # "contains", "references", "typed_as"


@dataclass
class GraphView:
    """Concept DAG view of K-Block content.

    Extracts a graph structure from markdown:
    - Headings become nodes
    - Fields become child nodes of their parent heading
    - References ([[target]]) become edges
    """

    _content: str = ""
    _tokens: FrozenSet[SemanticToken] = field(default_factory=frozenset)
    _nodes: list[GraphNode] = field(default_factory=list)
    _edges: list[GraphEdge] = field(default_factory=list)

    @property
    def view_type(self) -> ViewType:
        """Return GRAPH view type."""
        return ViewType.GRAPH

    @property
    def nodes(self) -> list[GraphNode]:
        """Return extracted graph nodes."""
        return self._nodes

    @property
    def edges(self) -> list[GraphEdge]:
        """Return extracted graph edges."""
        return self._edges

    def render(self, content: str, *args: Any, **kwargs: Any) -> str:
        """Parse content and extract graph structure.

        Args:
            content: Markdown content to parse

        Returns:
            DOT-format representation of the graph
        """
        self._content = content
        self._extract_graph(content)
        self._tokens = self._extract_tokens()
        return self._to_dot()

    def tokens(self) -> FrozenSet[SemanticToken]:
        """Return semantic tokens (nodes as tokens)."""
        return self._tokens

    def to_canonical(self) -> str:
        """Return original content (graph cannot be converted back)."""
        return self._content

    def _extract_graph(self, content: str) -> None:
        """Extract nodes and edges from markdown."""
        self._nodes = []
        self._edges = []

        current_heading: str | None = None
        heading_stack: list[tuple[int, str]] = []  # (level, id)

        for line_num, line in enumerate(content.split("\n")):
            stripped = line.strip()

            # Headings become nodes
            if stripped.startswith("#"):
                level = len(stripped) - len(stripped.lstrip("#"))
                text = stripped.lstrip("#").strip()
                node_id = f"h-{line_num}"

                self._nodes.append(GraphNode(id=node_id, label=text, kind="heading", level=level))

                # Update heading stack for containment edges
                while heading_stack and heading_stack[-1][0] >= level:
                    heading_stack.pop()

                if heading_stack:
                    # Add containment edge from parent heading
                    self._edges.append(
                        GraphEdge(source=heading_stack[-1][1], target=node_id, kind="contains")
                    )

                heading_stack.append((level, node_id))
                current_heading = node_id

            # Fields become child nodes
            elif stripped.startswith(("-", "*")) and ":" in stripped:
                field_part = stripped.lstrip("-*").strip()
                if ":" in field_part:
                    field_name = field_part.split(":", 1)[0].strip()
                    if field_name and not field_name.startswith("http"):
                        node_id = f"f-{field_name}"
                        self._nodes.append(GraphNode(id=node_id, label=field_name, kind="field"))
                        if current_heading:
                            self._edges.append(
                                GraphEdge(
                                    source=current_heading,
                                    target=node_id,
                                    kind="contains",
                                )
                            )

            # References become edges
            if "[[" in stripped and "]]" in stripped:
                import re

                for match in re.finditer(r"\[\[([^\]]+)\]\]", stripped):
                    ref = match.group(1)
                    if current_heading:
                        self._edges.append(
                            GraphEdge(
                                source=current_heading,
                                target=f"r-{ref}",
                                kind="references",
                            )
                        )

    def _extract_tokens(self) -> FrozenSet[SemanticToken]:
        """Convert nodes to semantic tokens."""
        tokens: set[SemanticToken] = set()
        for node in self._nodes:
            kind = TokenKind.HEADING if node.kind == "heading" else TokenKind.FIELD
            tokens.add(SemanticToken(id=node.id, kind=kind, value=node.label, position=None))
        return frozenset(tokens)

    def _to_dot(self) -> str:
        """Render graph as DOT format."""
        lines = ["digraph G {"]
        lines.append("  rankdir=TB;")

        for node in self._nodes:
            shape = "box" if node.kind == "heading" else "ellipse"
            lines.append(f'  "{node.id}" [label="{node.label}" shape={shape}];')

        for edge in self._edges:
            style = "solid" if edge.kind == "contains" else "dashed"
            lines.append(f'  "{edge.source}" -> "{edge.target}" [style={style}];')

        lines.append("}")
        return "\n".join(lines)
