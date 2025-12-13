"""
Cognitive Loom data structures.

Represents agent cognition as a tree, not a log.
The key insight: decision-making is tree search. The main trunk shows
selected actions, while ghost branches show rejected hypotheses (the Shadow).

This makes bugs visible - they often live in "the path not taken."
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Optional


@dataclass
class CognitiveBranch:
    """
    A node in the cognitive tree.

    Each branch represents a decision point, hypothesis, or action.
    The selected path forms the main trunk; rejected paths are ghost branches.
    """

    id: str
    timestamp: datetime
    content: str
    reasoning: str
    selected: bool = True  # Main trunk or ghost branch?
    children: list["CognitiveBranch"] = field(default_factory=list)
    parent_id: Optional[str] = None

    @property
    def glyph(self) -> str:
        """
        Visual glyph for this node.

        Returns:
            "●" for current leaf on selected path
            "○" for non-current node on selected path
            "✖" for rejected (ghost) branches
        """
        if not self.selected:
            return "✖"
        # If this node has no children, it's a leaf
        if not self.children:
            return "●"
        return "○"

    @property
    def is_leaf(self) -> bool:
        """Check if this is a leaf node (no children)."""
        return len(self.children) == 0

    @property
    def opacity(self) -> float:
        """
        Ghost branches fade over time.

        This creates a temporal gradient: recent rejections are visible,
        old ones fade into the background. The Shadow is always there,
        but older shadows are dimmer.

        Returns:
            1.0 for selected branches
            0.2-1.0 for ghost branches (fades over 1 hour)
        """
        if self.selected:
            return 1.0

        # Ghost branches fade over time
        age = (datetime.now() - self.timestamp).total_seconds()
        # Fade over 1 hour (3600 seconds)
        fade_factor = max(0.2, 1.0 - age / 3600)
        return fade_factor


@dataclass
class CognitiveTree:
    """
    The full cognitive history tree.

    This is the Loom - the woven fabric of decisions made and not made.
    Navigate through it with h/j/k/l to understand how the agent arrived
    at its current state.
    """

    root: CognitiveBranch
    current_id: str  # Currently focused node

    def get_node(self, node_id: str) -> Optional[CognitiveBranch]:
        """
        Find a node by ID.

        Args:
            node_id: The ID to search for

        Returns:
            The node if found, None otherwise
        """
        return self._find_node(self.root, node_id)

    def _find_node(
        self, node: CognitiveBranch, target_id: str
    ) -> Optional[CognitiveBranch]:
        """Recursively search for a node."""
        if node.id == target_id:
            return node
        for child in node.children:
            result = self._find_node(child, target_id)
            if result:
                return result
        return None

    def main_path(self) -> list[CognitiveBranch]:
        """
        Get the selected path from root to current.

        This is the "main trunk" - the sequence of decisions the agent
        actually took, ignoring ghost branches.

        Returns:
            List of nodes from root to current selected leaf
        """
        path: list[CognitiveBranch] = []
        node: CognitiveBranch | None = self.root
        while node:
            path.append(node)
            # Find the selected child (if any)
            selected_children = [c for c in node.children if c.selected]
            node = selected_children[0] if selected_children else None
        return path

    def ghost_branches(self) -> list[CognitiveBranch]:
        """
        Get all ghost branches (rejected hypotheses).

        These are the paths not taken - the Shadow made visible.
        Bugs often hide here: the action the agent considered but rejected
        might have been the right one.

        Returns:
            List of all rejected nodes in the tree
        """
        ghosts: list[CognitiveBranch] = []
        self._collect_ghosts(self.root, ghosts)
        return ghosts

    def _collect_ghosts(
        self, node: CognitiveBranch, ghosts: list[CognitiveBranch]
    ) -> None:
        """Recursively collect all ghost branches."""
        if not node.selected:
            ghosts.append(node)
        for child in node.children:
            self._collect_ghosts(child, ghosts)

    def all_nodes(self) -> list[CognitiveBranch]:
        """
        Get all nodes in the tree (main path + ghosts).

        Returns:
            List of all nodes
        """
        nodes: list[CognitiveBranch] = []
        self._collect_all(self.root, nodes)
        return nodes

    def _collect_all(self, node: CognitiveBranch, nodes: list[CognitiveBranch]) -> None:
        """Recursively collect all nodes."""
        nodes.append(node)
        for child in node.children:
            self._collect_all(child, nodes)

    def depth_of(self, node_id: str) -> int:
        """
        Get the depth of a node in the tree.

        Args:
            node_id: The node to measure

        Returns:
            Distance from root (root is depth 0)
        """
        return self._depth_of_node(self.root, node_id, 0)

    def _depth_of_node(
        self, node: CognitiveBranch, target_id: str, current_depth: int
    ) -> int:
        """Recursively calculate depth."""
        if node.id == target_id:
            return current_depth
        for child in node.children:
            result = self._depth_of_node(child, target_id, current_depth + 1)
            if result >= 0:
                return result
        return -1  # Not found

    # ─────────────────────────────────────────────────────────────
    # Navigation Methods (for Loom screen)
    # ─────────────────────────────────────────────────────────────

    def get_parent(self, node_id: str) -> Optional[CognitiveBranch]:
        """
        Get the parent of a node.

        Args:
            node_id: The node to find parent for

        Returns:
            Parent node, or None if at root
        """
        node = self.get_node(node_id)
        if node and node.parent_id:
            return self.get_node(node.parent_id)
        return None

    def get_siblings(self, node_id: str) -> list[CognitiveBranch]:
        """
        Get sibling nodes (same parent, including self).

        Args:
            node_id: The node to find siblings for

        Returns:
            List of sibling nodes
        """
        parent = self.get_parent(node_id)
        if parent:
            return parent.children
        # Root has no siblings
        node = self.get_node(node_id)
        return [node] if node else []

    def navigate_up(self) -> bool:
        """
        Navigate up to parent node (k key).

        Returns:
            True if navigation succeeded
        """
        parent = self.get_parent(self.current_id)
        if parent:
            self.current_id = parent.id
            return True
        return False

    def navigate_down(self) -> bool:
        """
        Navigate down to first child (j key).

        Prefers selected children over ghost branches.

        Returns:
            True if navigation succeeded
        """
        current = self.get_node(self.current_id)
        if current and current.children:
            # Prefer selected children first
            selected = [c for c in current.children if c.selected]
            if selected:
                self.current_id = selected[0].id
                return True
            # Fall back to first ghost
            self.current_id = current.children[0].id
            return True
        return False

    def navigate_left(self) -> bool:
        """
        Navigate to previous sibling (h key).

        Returns:
            True if navigation succeeded
        """
        siblings = self.get_siblings(self.current_id)
        if len(siblings) <= 1:
            return False

        # Find current index
        current_idx = next(
            (i for i, s in enumerate(siblings) if s.id == self.current_id), -1
        )
        if current_idx > 0:
            self.current_id = siblings[current_idx - 1].id
            return True
        return False

    def navigate_right(self) -> bool:
        """
        Navigate to next sibling (l key).

        Returns:
            True if navigation succeeded
        """
        siblings = self.get_siblings(self.current_id)
        if len(siblings) <= 1:
            return False

        # Find current index
        current_idx = next(
            (i for i, s in enumerate(siblings) if s.id == self.current_id), -1
        )
        if current_idx < len(siblings) - 1:
            self.current_id = siblings[current_idx + 1].id
            return True
        return False

    def get_current(self) -> Optional[CognitiveBranch]:
        """Get the currently focused node."""
        return self.get_node(self.current_id)
