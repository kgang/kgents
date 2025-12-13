"""
Tests for BranchTree widget.

Verifies rendering of cognitive trees, ghost branch visibility,
and navigation through the Loom.
"""

from datetime import datetime

import pytest
from agents.i.data.loom import CognitiveBranch, CognitiveTree
from agents.i.widgets.branch_tree import LOOM_CHARS, BranchTree


class TestBranchTreeRendering:
    """Test BranchTree widget rendering."""

    def test_empty_tree(self) -> None:
        """Empty tree shows message."""
        tree_widget = BranchTree()

        output = tree_widget.render()
        assert output == "No cognitive history"

    def test_single_node(self) -> None:
        """Single node renders as root."""
        root = CognitiveBranch(
            id="root",
            timestamp=datetime.now(),
            content="Start",
            reasoning="Initial state",
        )

        tree = CognitiveTree(root=root, current_id="root")
        tree_widget = BranchTree(cognitive_tree=tree)

        output = str(tree_widget.render())

        # Should contain the root node with glyph
        assert "Start" in output
        # Current node should be bold
        assert "[bold]" in output

    def test_linear_path(self) -> None:
        """Linear path renders as vertical line."""
        root = CognitiveBranch(
            id="root",
            timestamp=datetime.now(),
            content="Start",
            reasoning="",
        )

        child1 = CognitiveBranch(
            id="child1",
            timestamp=datetime.now(),
            content="Step 1",
            reasoning="",
            selected=True,
            parent_id="root",
        )

        child2 = CognitiveBranch(
            id="child2",
            timestamp=datetime.now(),
            content="Step 2",
            reasoning="",
            selected=True,
            parent_id="child1",
        )

        root.children.append(child1)
        child1.children.append(child2)

        tree = CognitiveTree(root=root, current_id="child2")
        tree_widget = BranchTree(cognitive_tree=tree)

        output = str(tree_widget.render())

        # Should contain all nodes
        assert "Start" in output
        assert "Step 1" in output
        assert "Step 2" in output

        # Should have branch characters
        assert LOOM_CHARS["arrow"] in output

    def test_branching_tree(self) -> None:
        """Branching tree shows multiple paths."""
        root = CognitiveBranch(
            id="root",
            timestamp=datetime.now(),
            content="Start",
            reasoning="",
        )

        selected_child = CognitiveBranch(
            id="selected",
            timestamp=datetime.now(),
            content="Plan A",
            reasoning="Efficient",
            selected=True,
            parent_id="root",
        )

        rejected_child = CognitiveBranch(
            id="rejected",
            timestamp=datetime.now(),
            content="Plan B",
            reasoning="Too slow",
            selected=False,
            parent_id="root",
        )

        root.children.extend([selected_child, rejected_child])

        tree = CognitiveTree(root=root, current_id="selected")
        tree_widget = BranchTree(cognitive_tree=tree)

        output = str(tree_widget.render())

        # Should contain both branches
        assert "Plan A" in output
        assert "Plan B" in output

        # Should show reasoning for ghost branches
        # (reasoning for selected branches only shown at significant branch points)
        assert "Too slow" in output

    def test_ghost_visibility_toggle(self) -> None:
        """Ghost branches can be hidden."""
        root = CognitiveBranch(
            id="root",
            timestamp=datetime.now(),
            content="Start",
            reasoning="",
        )

        selected = CognitiveBranch(
            id="selected",
            timestamp=datetime.now(),
            content="Selected",
            reasoning="",
            selected=True,
            parent_id="root",
        )

        ghost = CognitiveBranch(
            id="ghost",
            timestamp=datetime.now(),
            content="Rejected",
            reasoning="Not viable",
            selected=False,
            parent_id="root",
        )

        root.children.extend([selected, ghost])

        tree = CognitiveTree(root=root, current_id="selected")
        tree_widget = BranchTree(cognitive_tree=tree, show_ghosts=True)

        # With ghosts visible
        output_with_ghosts = str(tree_widget.render())
        assert "Rejected" in output_with_ghosts

        # Hide ghosts
        tree_widget.show_ghosts = False
        output_without_ghosts = str(tree_widget.render())
        assert "Rejected" not in output_without_ghosts

    def test_current_node_highlighted(self) -> None:
        """Current node is highlighted."""
        root = CognitiveBranch(
            id="root",
            timestamp=datetime.now(),
            content="Start",
            reasoning="",
        )

        current = CognitiveBranch(
            id="current",
            timestamp=datetime.now(),
            content="Current State",
            reasoning="",
            selected=True,
            parent_id="root",
        )

        root.children.append(current)

        tree = CognitiveTree(root=root, current_id="current")
        tree_widget = BranchTree(cognitive_tree=tree)

        output = str(tree_widget.render())

        # Current node should have bold markup
        assert "[bold]" in output
        assert "Current State" in output

    def test_ghost_branches_dimmed(self) -> None:
        """Ghost branches have dim styling."""
        root = CognitiveBranch(
            id="root",
            timestamp=datetime.now(),
            content="Start",
            reasoning="",
        )

        ghost = CognitiveBranch(
            id="ghost",
            timestamp=datetime.now(),
            content="Ghost",
            reasoning="Rejected",
            selected=False,
            parent_id="root",
        )

        root.children.append(ghost)

        tree = CognitiveTree(root=root, current_id="root")
        tree_widget = BranchTree(cognitive_tree=tree)

        output = str(tree_widget.render())

        # Ghost should have dim markup
        assert "[dim]" in output
        assert "Ghost" in output

    def test_nested_branching(self) -> None:
        """Nested branches render with proper indentation."""
        root = CognitiveBranch(
            id="root",
            timestamp=datetime.now(),
            content="Root",
            reasoning="",
        )

        level1 = CognitiveBranch(
            id="level1",
            timestamp=datetime.now(),
            content="Level 1",
            reasoning="",
            selected=True,
            parent_id="root",
        )

        level2a = CognitiveBranch(
            id="level2a",
            timestamp=datetime.now(),
            content="Level 2A",
            reasoning="",
            selected=True,
            parent_id="level1",
        )

        level2b = CognitiveBranch(
            id="level2b",
            timestamp=datetime.now(),
            content="Level 2B",
            reasoning="",
            selected=False,
            parent_id="level1",
        )

        root.children.append(level1)
        level1.children.extend([level2a, level2b])

        tree = CognitiveTree(root=root, current_id="level2a")
        tree_widget = BranchTree(cognitive_tree=tree)

        output = str(tree_widget.render())

        # All levels should be present
        assert "Root" in output
        assert "Level 1" in output
        assert "Level 2A" in output
        assert "Level 2B" in output

        # Should have proper tree structure characters
        assert LOOM_CHARS["trunk"] in output or LOOM_CHARS["arrow"] in output

    def test_long_content_truncated(self) -> None:
        """Long content is truncated to fit."""
        root = CognitiveBranch(
            id="root",
            timestamp=datetime.now(),
            content="This is a very long content string that should be truncated to avoid rendering issues",
            reasoning="",
        )

        tree = CognitiveTree(root=root, current_id="root")
        tree_widget = BranchTree(cognitive_tree=tree)

        output = str(tree_widget.render())

        # Should not contain the full string
        assert len(output) < len(root.content) + 100

    def test_toggle_ghosts_method(self) -> None:
        """toggle_ghosts switches visibility."""
        tree_widget = BranchTree(show_ghosts=True)

        assert tree_widget.show_ghosts is True

        tree_widget.toggle_ghosts()
        assert tree_widget.show_ghosts is False

        tree_widget.toggle_ghosts()
        assert tree_widget.show_ghosts is True

    def test_set_tree_method(self) -> None:
        """set_tree updates the tree."""
        tree_widget = BranchTree()

        root = CognitiveBranch(
            id="root",
            timestamp=datetime.now(),
            content="New Tree",
            reasoning="",
        )
        tree = CognitiveTree(root=root, current_id="root")

        tree_widget.set_tree(tree)

        assert tree_widget.cognitive_tree is not None
        assert tree_widget.cognitive_tree.root.content == "New Tree"


class TestBranchTreeGlyphs:
    """Test glyph rendering in tree output."""

    def test_selected_glyph_in_output(self) -> None:
        """Selected nodes use circle glyphs."""
        root = CognitiveBranch(
            id="root",
            timestamp=datetime.now(),
            content="Root",
            reasoning="",
            selected=True,
        )

        tree = CognitiveTree(root=root, current_id="root")
        tree_widget = BranchTree(cognitive_tree=tree)

        output = str(tree_widget.render())

        # Should contain the filled circle (current leaf)
        assert "●" in output or "○" in output

    def test_rejected_glyph_in_output(self) -> None:
        """Rejected nodes use X glyph."""
        root = CognitiveBranch(
            id="root",
            timestamp=datetime.now(),
            content="Root",
            reasoning="",
        )

        rejected = CognitiveBranch(
            id="rejected",
            timestamp=datetime.now(),
            content="Rejected",
            reasoning="",
            selected=False,
            parent_id="root",
        )

        root.children.append(rejected)

        tree = CognitiveTree(root=root, current_id="root")
        tree_widget = BranchTree(cognitive_tree=tree)

        output = str(tree_widget.render())

        # Should contain the X mark for rejected
        assert "✖" in output
