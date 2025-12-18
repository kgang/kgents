"""
Tests for Cognitive Loom data structures.

Verifies tree construction, traversal, and the Shadow (ghost branches).
"""

from datetime import datetime, timedelta

import pytest

from agents.i.data.loom import CognitiveBranch, CognitiveTree


class TestCognitiveBranch:
    """Test CognitiveBranch node."""

    def test_initial_state(self) -> None:
        """Branch initializes with correct properties."""
        now = datetime.now()
        branch = CognitiveBranch(
            id="test-1",
            timestamp=now,
            content="Test action",
            reasoning="Because reasons",
            selected=True,
        )

        assert branch.id == "test-1"
        assert branch.timestamp == now
        assert branch.content == "Test action"
        assert branch.reasoning == "Because reasons"
        assert branch.selected is True
        assert branch.children == []
        assert branch.parent_id is None

    def test_glyph_selected_leaf(self) -> None:
        """Selected leaf node shows filled circle."""
        branch = CognitiveBranch(
            id="leaf",
            timestamp=datetime.now(),
            content="Leaf",
            reasoning="",
            selected=True,
        )

        assert branch.glyph == "●"

    def test_glyph_selected_parent(self) -> None:
        """Selected parent node shows hollow circle."""
        parent = CognitiveBranch(
            id="parent",
            timestamp=datetime.now(),
            content="Parent",
            reasoning="",
            selected=True,
        )

        child = CognitiveBranch(
            id="child",
            timestamp=datetime.now(),
            content="Child",
            reasoning="",
            selected=True,
            parent_id="parent",
        )

        parent.children.append(child)

        assert parent.glyph == "○"

    def test_glyph_rejected(self) -> None:
        """Rejected node shows X mark."""
        branch = CognitiveBranch(
            id="rejected",
            timestamp=datetime.now(),
            content="Rejected",
            reasoning="Not good enough",
            selected=False,
        )

        assert branch.glyph == "✖"

    def test_is_leaf_true(self) -> None:
        """Node with no children is a leaf."""
        branch = CognitiveBranch(
            id="leaf",
            timestamp=datetime.now(),
            content="Leaf",
            reasoning="",
        )

        assert branch.is_leaf is True

    def test_is_leaf_false(self) -> None:
        """Node with children is not a leaf."""
        parent = CognitiveBranch(
            id="parent",
            timestamp=datetime.now(),
            content="Parent",
            reasoning="",
        )

        child = CognitiveBranch(
            id="child",
            timestamp=datetime.now(),
            content="Child",
            reasoning="",
        )

        parent.children.append(child)

        assert parent.is_leaf is False

    def test_opacity_selected(self) -> None:
        """Selected branches have full opacity."""
        branch = CognitiveBranch(
            id="selected",
            timestamp=datetime.now(),
            content="Selected",
            reasoning="",
            selected=True,
        )

        assert branch.opacity == 1.0

    def test_opacity_recent_ghost(self) -> None:
        """Recent ghost branches have high opacity."""
        branch = CognitiveBranch(
            id="ghost",
            timestamp=datetime.now(),
            content="Ghost",
            reasoning="",
            selected=False,
        )

        # Recent ghost should have opacity close to 1.0
        assert branch.opacity > 0.9

    def test_opacity_old_ghost(self) -> None:
        """Old ghost branches fade."""
        # Create a branch from 2 hours ago
        old_time = datetime.now() - timedelta(hours=2)
        branch = CognitiveBranch(
            id="old-ghost",
            timestamp=old_time,
            content="Old Ghost",
            reasoning="",
            selected=False,
        )

        # Should be faded (minimum opacity is 0.2)
        assert branch.opacity == 0.2


class TestCognitiveTree:
    """Test CognitiveTree traversal and queries."""

    def test_get_node_root(self) -> None:
        """Can find root node."""
        root = CognitiveBranch(
            id="root",
            timestamp=datetime.now(),
            content="Root",
            reasoning="",
        )

        tree = CognitiveTree(root=root, current_id="root")

        found = tree.get_node("root")
        assert found is not None
        assert found.id == "root"

    def test_get_node_child(self) -> None:
        """Can find child node."""
        root = CognitiveBranch(
            id="root",
            timestamp=datetime.now(),
            content="Root",
            reasoning="",
        )

        child = CognitiveBranch(
            id="child",
            timestamp=datetime.now(),
            content="Child",
            reasoning="",
            parent_id="root",
        )

        root.children.append(child)

        tree = CognitiveTree(root=root, current_id="root")

        found = tree.get_node("child")
        assert found is not None
        assert found.id == "child"

    def test_get_node_not_found(self) -> None:
        """Returns None for missing node."""
        root = CognitiveBranch(
            id="root",
            timestamp=datetime.now(),
            content="Root",
            reasoning="",
        )

        tree = CognitiveTree(root=root, current_id="root")

        found = tree.get_node("missing")
        assert found is None

    def test_main_path_single_node(self) -> None:
        """Main path of single node is just the root."""
        root = CognitiveBranch(
            id="root",
            timestamp=datetime.now(),
            content="Root",
            reasoning="",
        )

        tree = CognitiveTree(root=root, current_id="root")

        path = tree.main_path()
        assert len(path) == 1
        assert path[0].id == "root"

    def test_main_path_linear(self) -> None:
        """Main path follows selected children."""
        root = CognitiveBranch(
            id="root",
            timestamp=datetime.now(),
            content="Root",
            reasoning="",
        )

        child1 = CognitiveBranch(
            id="child1",
            timestamp=datetime.now(),
            content="Child 1",
            reasoning="",
            selected=True,
            parent_id="root",
        )

        child2 = CognitiveBranch(
            id="child2",
            timestamp=datetime.now(),
            content="Child 2",
            reasoning="",
            selected=True,
            parent_id="child1",
        )

        root.children.append(child1)
        child1.children.append(child2)

        tree = CognitiveTree(root=root, current_id="child2")

        path = tree.main_path()
        assert len(path) == 3
        assert path[0].id == "root"
        assert path[1].id == "child1"
        assert path[2].id == "child2"

    def test_main_path_with_branching(self) -> None:
        """Main path only follows selected branches."""
        root = CognitiveBranch(
            id="root",
            timestamp=datetime.now(),
            content="Root",
            reasoning="",
        )

        # Selected path
        selected_child = CognitiveBranch(
            id="selected",
            timestamp=datetime.now(),
            content="Selected",
            reasoning="",
            selected=True,
            parent_id="root",
        )

        # Ghost branch
        rejected_child = CognitiveBranch(
            id="rejected",
            timestamp=datetime.now(),
            content="Rejected",
            reasoning="Not good",
            selected=False,
            parent_id="root",
        )

        root.children.append(selected_child)
        root.children.append(rejected_child)

        tree = CognitiveTree(root=root, current_id="selected")

        path = tree.main_path()
        assert len(path) == 2
        assert path[0].id == "root"
        assert path[1].id == "selected"

    def test_ghost_branches_empty(self) -> None:
        """No ghosts when all branches selected."""
        root = CognitiveBranch(
            id="root",
            timestamp=datetime.now(),
            content="Root",
            reasoning="",
            selected=True,
        )

        tree = CognitiveTree(root=root, current_id="root")

        ghosts = tree.ghost_branches()
        assert len(ghosts) == 0

    def test_ghost_branches_finds_rejected(self) -> None:
        """Finds all rejected branches."""
        root = CognitiveBranch(
            id="root",
            timestamp=datetime.now(),
            content="Root",
            reasoning="",
            selected=True,
        )

        selected = CognitiveBranch(
            id="selected",
            timestamp=datetime.now(),
            content="Selected",
            reasoning="",
            selected=True,
            parent_id="root",
        )

        ghost1 = CognitiveBranch(
            id="ghost1",
            timestamp=datetime.now(),
            content="Ghost 1",
            reasoning="Too slow",
            selected=False,
            parent_id="root",
        )

        ghost2 = CognitiveBranch(
            id="ghost2",
            timestamp=datetime.now(),
            content="Ghost 2",
            reasoning="Too risky",
            selected=False,
            parent_id="selected",
        )

        root.children.extend([selected, ghost1])
        selected.children.append(ghost2)

        tree = CognitiveTree(root=root, current_id="selected")

        ghosts = tree.ghost_branches()
        assert len(ghosts) == 2
        ghost_ids = {g.id for g in ghosts}
        assert ghost_ids == {"ghost1", "ghost2"}

    def test_all_nodes(self) -> None:
        """all_nodes returns everything."""
        root = CognitiveBranch(
            id="root",
            timestamp=datetime.now(),
            content="Root",
            reasoning="",
            selected=True,
        )

        child1 = CognitiveBranch(
            id="child1",
            timestamp=datetime.now(),
            content="Child 1",
            reasoning="",
            selected=True,
            parent_id="root",
        )

        child2 = CognitiveBranch(
            id="child2",
            timestamp=datetime.now(),
            content="Child 2",
            reasoning="",
            selected=False,
            parent_id="root",
        )

        root.children.extend([child1, child2])

        tree = CognitiveTree(root=root, current_id="child1")

        nodes = tree.all_nodes()
        assert len(nodes) == 3
        node_ids = {n.id for n in nodes}
        assert node_ids == {"root", "child1", "child2"}

    def test_depth_of_root(self) -> None:
        """Root has depth 0."""
        root = CognitiveBranch(
            id="root",
            timestamp=datetime.now(),
            content="Root",
            reasoning="",
        )

        tree = CognitiveTree(root=root, current_id="root")

        assert tree.depth_of("root") == 0

    def test_depth_of_child(self) -> None:
        """Child depth is 1 + parent depth."""
        root = CognitiveBranch(
            id="root",
            timestamp=datetime.now(),
            content="Root",
            reasoning="",
        )

        child = CognitiveBranch(
            id="child",
            timestamp=datetime.now(),
            content="Child",
            reasoning="",
            parent_id="root",
        )

        grandchild = CognitiveBranch(
            id="grandchild",
            timestamp=datetime.now(),
            content="Grandchild",
            reasoning="",
            parent_id="child",
        )

        root.children.append(child)
        child.children.append(grandchild)

        tree = CognitiveTree(root=root, current_id="grandchild")

        assert tree.depth_of("child") == 1
        assert tree.depth_of("grandchild") == 2

    def test_depth_of_missing(self) -> None:
        """Missing node has depth -1."""
        root = CognitiveBranch(
            id="root",
            timestamp=datetime.now(),
            content="Root",
            reasoning="",
        )

        tree = CognitiveTree(root=root, current_id="root")

        assert tree.depth_of("missing") == -1


class TestCognitiveTreeNavigation:
    """Test CognitiveTree navigation methods."""

    @pytest.fixture
    def branching_tree(self) -> CognitiveTree:
        """Create a tree with branches for navigation tests."""
        root = CognitiveBranch(
            id="root",
            timestamp=datetime.now(),
            content="Root",
            reasoning="Start",
            selected=True,
        )

        # Two children: selected and ghost
        selected_child = CognitiveBranch(
            id="selected",
            timestamp=datetime.now(),
            content="Selected path",
            reasoning="Good choice",
            selected=True,
            parent_id="root",
        )

        ghost_child = CognitiveBranch(
            id="ghost",
            timestamp=datetime.now(),
            content="Rejected path",
            reasoning="Too risky",
            selected=False,
            parent_id="root",
        )

        # Grandchild on selected path
        grandchild = CognitiveBranch(
            id="grandchild",
            timestamp=datetime.now(),
            content="Final action",
            reasoning="Conclusion",
            selected=True,
            parent_id="selected",
        )

        root.children = [selected_child, ghost_child]
        selected_child.children = [grandchild]

        return CognitiveTree(root=root, current_id="selected")

    def test_get_parent_of_child(self, branching_tree: CognitiveTree) -> None:
        """Get parent of a child node."""
        parent = branching_tree.get_parent("selected")
        assert parent is not None
        assert parent.id == "root"

    def test_get_parent_of_root_is_none(self, branching_tree: CognitiveTree) -> None:
        """Root has no parent."""
        parent = branching_tree.get_parent("root")
        assert parent is None

    def test_get_siblings_includes_self(self, branching_tree: CognitiveTree) -> None:
        """Siblings include the node itself."""
        siblings = branching_tree.get_siblings("selected")
        assert len(siblings) == 2
        sibling_ids = {s.id for s in siblings}
        assert sibling_ids == {"selected", "ghost"}

    def test_get_siblings_root_is_alone(self, branching_tree: CognitiveTree) -> None:
        """Root has no siblings."""
        siblings = branching_tree.get_siblings("root")
        assert len(siblings) == 1
        assert siblings[0].id == "root"

    def test_navigate_up_from_child(self, branching_tree: CognitiveTree) -> None:
        """Navigate up moves to parent."""
        branching_tree.current_id = "grandchild"
        assert branching_tree.navigate_up() is True
        assert branching_tree.current_id == "selected"

    def test_navigate_up_from_root_fails(self, branching_tree: CognitiveTree) -> None:
        """Cannot navigate up from root."""
        branching_tree.current_id = "root"
        assert branching_tree.navigate_up() is False
        assert branching_tree.current_id == "root"

    def test_navigate_down_from_parent(self, branching_tree: CognitiveTree) -> None:
        """Navigate down moves to first selected child."""
        branching_tree.current_id = "root"
        assert branching_tree.navigate_down() is True
        # Should prefer selected child over ghost
        assert branching_tree.current_id == "selected"

    def test_navigate_down_from_leaf_fails(self, branching_tree: CognitiveTree) -> None:
        """Cannot navigate down from leaf."""
        branching_tree.current_id = "grandchild"
        assert branching_tree.navigate_down() is False
        assert branching_tree.current_id == "grandchild"

    def test_navigate_left_to_sibling(self, branching_tree: CognitiveTree) -> None:
        """Navigate left moves to previous sibling."""
        branching_tree.current_id = "ghost"  # Second sibling
        assert branching_tree.navigate_left() is True
        assert branching_tree.current_id == "selected"  # First sibling

    def test_navigate_left_from_first_fails(self, branching_tree: CognitiveTree) -> None:
        """Cannot navigate left from first sibling."""
        branching_tree.current_id = "selected"  # First sibling
        assert branching_tree.navigate_left() is False
        assert branching_tree.current_id == "selected"

    def test_navigate_right_to_sibling(self, branching_tree: CognitiveTree) -> None:
        """Navigate right moves to next sibling."""
        branching_tree.current_id = "selected"  # First sibling
        assert branching_tree.navigate_right() is True
        assert branching_tree.current_id == "ghost"  # Second sibling

    def test_navigate_right_from_last_fails(self, branching_tree: CognitiveTree) -> None:
        """Cannot navigate right from last sibling."""
        branching_tree.current_id = "ghost"  # Last sibling
        assert branching_tree.navigate_right() is False
        assert branching_tree.current_id == "ghost"

    def test_navigate_left_no_siblings(self, branching_tree: CognitiveTree) -> None:
        """Cannot navigate left without siblings."""
        branching_tree.current_id = "root"
        assert branching_tree.navigate_left() is False

    def test_get_current(self, branching_tree: CognitiveTree) -> None:
        """get_current returns the focused node."""
        branching_tree.current_id = "ghost"
        current = branching_tree.get_current()
        assert current is not None
        assert current.id == "ghost"
        assert current.content == "Rejected path"

    def test_full_navigation_sequence(self, branching_tree: CognitiveTree) -> None:
        """Test a complete navigation sequence: down, down, up, right, left."""
        # Start at root
        branching_tree.current_id = "root"

        # Down to selected child
        assert branching_tree.navigate_down() is True
        assert branching_tree.current_id == "selected"

        # Down to grandchild
        assert branching_tree.navigate_down() is True
        assert branching_tree.current_id == "grandchild"

        # Up back to selected
        assert branching_tree.navigate_up() is True
        assert branching_tree.current_id == "selected"

        # Up to root
        assert branching_tree.navigate_up() is True
        assert branching_tree.current_id == "root"

        # Down, then right to ghost sibling
        assert branching_tree.navigate_down() is True
        assert branching_tree.navigate_right() is True
        assert branching_tree.current_id == "ghost"

        # Left back to selected
        assert branching_tree.navigate_left() is True
        assert branching_tree.current_id == "selected"
