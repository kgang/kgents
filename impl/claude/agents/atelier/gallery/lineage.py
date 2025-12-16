"""
Lineage Graph: Track relationships between pieces.

Provides a graph view of how pieces inspire each other,
enabling visualization and traversal of creative lineage.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from agents.atelier.artisan import Piece


@dataclass
class LineageNode:
    """A node in the lineage graph."""

    piece_id: str
    artisan: str
    form: str
    preview: str  # First 50 chars of content
    children: list[str] = field(default_factory=list)  # Pieces inspired by this one
    parents: list[str] = field(default_factory=list)  # Pieces that inspired this one

    def to_dict(self) -> dict[str, Any]:
        return {
            "piece_id": self.piece_id,
            "artisan": self.artisan,
            "form": self.form,
            "preview": self.preview,
            "children": list(self.children),
            "parents": list(self.parents),
        }


class LineageGraph:
    """
    Graph of creative lineage between pieces.

    Enables:
    - Finding all descendants of a piece
    - Finding common ancestors
    - Visualizing creative trees
    """

    def __init__(self) -> None:
        self.nodes: dict[str, LineageNode] = {}

    def add_piece(self, piece: Piece) -> LineageNode:
        """
        Add a piece to the graph.

        Updates both the new piece's node and its ancestors' children lists.
        """
        preview = (
            str(piece.content)[:50] + "..."
            if len(str(piece.content)) > 50
            else str(piece.content)
        )
        preview = preview.replace("\n", " ")

        node = LineageNode(
            piece_id=piece.id,
            artisan=piece.artisan,
            form=piece.form,
            preview=preview,
            parents=list(piece.provenance.inspirations),
        )

        self.nodes[piece.id] = node

        # Update parents' children lists
        for parent_id in piece.provenance.inspirations:
            if parent_id in self.nodes:
                if piece.id not in self.nodes[parent_id].children:
                    self.nodes[parent_id].children.append(piece.id)

        return node

    def get_ancestors(self, piece_id: str) -> list[LineageNode]:
        """Get all ancestors (transitive parents) of a piece."""
        if piece_id not in self.nodes:
            return []

        visited: set[str] = set()
        ancestors: list[LineageNode] = []

        def traverse(pid: str) -> None:
            node = self.nodes.get(pid)
            if not node:
                return
            for parent_id in node.parents:
                if parent_id not in visited:
                    visited.add(parent_id)
                    parent = self.nodes.get(parent_id)
                    if parent:
                        ancestors.append(parent)
                        traverse(parent_id)

        traverse(piece_id)
        return ancestors

    def get_descendants(self, piece_id: str) -> list[LineageNode]:
        """Get all descendants (transitive children) of a piece."""
        if piece_id not in self.nodes:
            return []

        visited: set[str] = set()
        descendants: list[LineageNode] = []

        def traverse(pid: str) -> None:
            node = self.nodes.get(pid)
            if not node:
                return
            for child_id in node.children:
                if child_id not in visited:
                    visited.add(child_id)
                    child = self.nodes.get(child_id)
                    if child:
                        descendants.append(child)
                        traverse(child_id)

        traverse(piece_id)
        return descendants

    def get_roots(self) -> list[LineageNode]:
        """Get all pieces with no parents (root creations)."""
        return [node for node in self.nodes.values() if not node.parents]

    def get_leaves(self) -> list[LineageNode]:
        """Get all pieces with no children (terminal creations)."""
        return [node for node in self.nodes.values() if not node.children]

    def common_ancestors(self, piece_a: str, piece_b: str) -> list[LineageNode]:
        """Find common ancestors of two pieces."""
        ancestors_a = {n.piece_id for n in self.get_ancestors(piece_a)}
        ancestors_b = {n.piece_id for n in self.get_ancestors(piece_b)}
        common = ancestors_a & ancestors_b
        return [self.nodes[pid] for pid in common if pid in self.nodes]

    def to_dict(self) -> dict[str, Any]:
        """Serialize the graph for storage or visualization."""
        return {
            "nodes": {pid: node.to_dict() for pid, node in self.nodes.items()},
        }

    @classmethod
    def from_pieces(cls, pieces: list[Piece]) -> "LineageGraph":
        """Build a lineage graph from a list of pieces."""
        graph = cls()
        for piece in pieces:
            graph.add_piece(piece)
        return graph

    def render_tree(self, root_id: str | None = None, indent: int = 0) -> str:
        """
        Render the graph as an ASCII tree.

        If root_id is None, renders from all roots.
        """
        lines: list[str] = []

        def render_node(pid: str, depth: int, prefix: str = "") -> None:
            node = self.nodes.get(pid)
            if not node:
                return

            indicator = "├─" if depth > 0 else "◇"
            lines.append(f"{prefix}{indicator} [{node.artisan}] {node.preview}")

            children = node.children
            for i, child_id in enumerate(children):
                is_last = i == len(children) - 1
                child_prefix = prefix + (
                    "   " if depth == 0 else ("│  " if not is_last else "   ")
                )
                render_node(child_id, depth + 1, child_prefix)

        if root_id:
            render_node(root_id, 0)
        else:
            for root in self.get_roots():
                render_node(root.piece_id, 0)
                lines.append("")

        return "\n".join(lines)


__all__ = ["LineageGraph", "LineageNode"]
