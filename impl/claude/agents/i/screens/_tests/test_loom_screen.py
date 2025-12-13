"""
Tests for the LoomScreen - Cognitive Loom navigation.

The Loom screen replaces linear history with topological navigation
through the agent's decision tree.
"""

from __future__ import annotations

from datetime import datetime, timedelta

import pytest
from textual.widgets import Footer, Header, Static

from ...data.loom import CognitiveBranch, CognitiveTree
from ...widgets.branch_tree import BranchTree
from ...widgets.timeline import Timeline
from ..loom import LoomScreen, create_demo_cognitive_tree


class TestLoomScreenCreation:
    """Test LoomScreen initialization and composition."""

    def test_create_loom_screen_minimal(self):
        """Test creating LoomScreen with minimal parameters."""
        screen = LoomScreen()
        assert screen is not None
        assert screen.agent_id == ""
        assert screen.agent_name == ""

    def test_create_loom_screen_with_agent_info(self):
        """Test creating LoomScreen with agent information."""
        screen = LoomScreen(agent_id="test-agent", agent_name="TestAgent")
        assert screen.agent_id == "test-agent"
        assert screen.agent_name == "TestAgent"

    def test_create_loom_screen_with_tree(self):
        """Test creating LoomScreen with a cognitive tree."""
        tree = create_demo_cognitive_tree()
        screen = LoomScreen(tree=tree)
        assert screen._tree is not None
        assert screen._tree == tree

    def test_create_loom_screen_demo_mode(self):
        """Test creating LoomScreen in demo mode."""
        screen = LoomScreen(demo_mode=True)
        assert screen._demo_mode is True
        assert screen._tree is not None  # Should create demo tree

    def test_loom_screen_has_bindings(self):
        """Test that LoomScreen defines navigation bindings."""
        assert hasattr(LoomScreen, "BINDINGS")
        assert len(LoomScreen.BINDINGS) > 0

    def test_loom_screen_bindings_include_navigation(self):
        """Test that bindings include j/k/h/l navigation."""
        from textual.binding import Binding

        binding_keys = {b.key for b in LoomScreen.BINDINGS if isinstance(b, Binding)}
        assert "j" in binding_keys  # Down
        assert "k" in binding_keys  # Up
        assert "h" in binding_keys  # Left
        assert "l" in binding_keys  # Right

    def test_loom_screen_bindings_include_crystallize(self):
        """Test that bindings include crystallize action."""
        from textual.binding import Binding

        binding_keys = {b.key for b in LoomScreen.BINDINGS if isinstance(b, Binding)}
        assert "c" in binding_keys  # Crystallize

    def test_loom_screen_bindings_include_toggle_ghosts(self):
        """Test that bindings include toggle ghosts action."""
        from textual.binding import Binding

        binding_keys = {b.key for b in LoomScreen.BINDINGS if isinstance(b, Binding)}
        assert "g" in binding_keys  # Toggle ghosts


class TestLoomScreenComposition:
    """Test LoomScreen widget composition."""

    @pytest.fixture
    def screen(self):
        """Create a LoomScreen in demo mode."""
        return LoomScreen(demo_mode=True)

    def test_screen_has_compose_method(self, screen):
        """Test that screen has a compose method."""
        assert hasattr(screen, "compose")
        assert callable(screen.compose)

    def test_screen_initializes_tree_in_demo_mode(self, screen):
        """Test that demo mode initializes a tree."""
        assert screen._tree is not None
        assert screen._demo_mode is True

    def test_screen_initializes_branch_tree_reference(self, screen):
        """Test that screen has _branch_tree attribute."""
        assert hasattr(screen, "_branch_tree")

    def test_screen_initializes_timeline_reference(self, screen):
        """Test that screen has _timeline attribute."""
        assert hasattr(screen, "_timeline")


class TestDemoCognitiveTree:
    """Test the demo cognitive tree creation."""

    def test_create_demo_tree(self):
        """Test creating a demo cognitive tree."""
        tree = create_demo_cognitive_tree()
        assert tree is not None
        assert isinstance(tree, CognitiveTree)

    def test_demo_tree_has_root(self):
        """Test that demo tree has a root node."""
        tree = create_demo_cognitive_tree()
        assert tree.root is not None
        assert isinstance(tree.root, CognitiveBranch)

    def test_demo_tree_has_current_id(self):
        """Test that demo tree has a current_id set."""
        tree = create_demo_cognitive_tree()
        assert tree.current_id is not None
        assert tree.current_id != ""

    def test_demo_tree_has_branches(self):
        """Test that demo tree has child branches."""
        tree = create_demo_cognitive_tree()
        assert len(tree.root.children) > 0

    def test_demo_tree_has_ghost_branches(self):
        """Test that demo tree includes rejected (ghost) branches."""
        tree = create_demo_cognitive_tree()
        ghosts = tree.ghost_branches()
        assert len(ghosts) > 0

    def test_demo_tree_has_selected_path(self):
        """Test that demo tree has a selected main path."""
        tree = create_demo_cognitive_tree()
        main_path = tree.main_path()
        assert len(main_path) > 0
        # All nodes in main path should be selected
        assert all(node.selected for node in main_path)


class TestLoomScreenActions:
    """Test LoomScreen action methods."""

    @pytest.fixture
    def screen(self):
        """Create a LoomScreen in demo mode."""
        return LoomScreen(demo_mode=True, agent_id="test", agent_name="Test")

    def test_show_ghosts_attribute_exists(self, screen):
        """Test that show_ghosts attribute exists."""
        assert hasattr(screen, "show_ghosts")

    def test_show_ghosts_default_value(self, screen):
        """Test default value of show_ghosts."""
        assert screen.show_ghosts is True

    def test_can_manually_toggle_show_ghosts(self, screen):
        """Test that show_ghosts can be toggled manually."""
        initial_state = screen.show_ghosts
        screen.show_ghosts = not initial_state
        assert screen.show_ghosts != initial_state

    def test_action_nav_down_exists(self, screen):
        """Test that nav_down action exists."""
        assert hasattr(screen, "action_nav_down")

    def test_action_nav_up_exists(self, screen):
        """Test that nav_up action exists."""
        assert hasattr(screen, "action_nav_up")

    def test_action_nav_left_exists(self, screen):
        """Test that nav_left action exists."""
        assert hasattr(screen, "action_nav_left")

    def test_action_nav_right_exists(self, screen):
        """Test that nav_right action exists."""
        assert hasattr(screen, "action_nav_right")

    def test_action_crystallize_exists(self, screen):
        """Test that crystallize action exists."""
        assert hasattr(screen, "action_crystallize")


class TestLoomScreenTreeUpdate:
    """Test updating the cognitive tree in LoomScreen."""

    @pytest.fixture
    def screen(self):
        """Create a LoomScreen."""
        return LoomScreen()

    @pytest.fixture
    def sample_tree(self):
        """Create a sample cognitive tree."""
        now = datetime.now()
        root = CognitiveBranch(
            id="root",
            timestamp=now,
            content="Root node",
            reasoning="Start",
            selected=True,
        )
        child = CognitiveBranch(
            id="child",
            timestamp=now + timedelta(seconds=1),
            content="Child node",
            reasoning="Next",
            selected=True,
            parent_id="root",
        )
        root.children = [child]
        return CognitiveTree(root=root, current_id="child")

    def test_set_tree_updates_screen(self, screen, sample_tree):
        """Test that set_tree updates the screen's tree."""
        screen.set_tree(sample_tree)
        assert screen._tree == sample_tree

    def test_set_tree_method_exists(self, screen):
        """Test that set_tree method exists."""
        assert hasattr(screen, "set_tree")
        assert callable(screen.set_tree)


class TestTimelineEventExtraction:
    """Test extracting timeline events from cognitive tree."""

    @pytest.fixture
    def screen(self):
        """Create a LoomScreen in demo mode."""
        return LoomScreen(demo_mode=True)

    def test_extract_timeline_events_returns_list(self, screen):
        """Test that timeline extraction returns a list."""
        events = screen._extract_timeline_events()
        assert isinstance(events, list)

    def test_extract_timeline_events_with_tree(self, screen):
        """Test timeline extraction with a tree."""
        if screen._tree:
            events = screen._extract_timeline_events()
            assert len(events) > 0

    def test_extract_timeline_events_format(self, screen):
        """Test that events are (datetime, float) tuples."""
        if screen._tree:
            events = screen._extract_timeline_events()
            for event in events:
                assert isinstance(event, tuple)
                assert len(event) == 2
                assert isinstance(event[0], datetime)
                assert isinstance(event[1], float)

    def test_extract_timeline_events_sorted(self, screen):
        """Test that events are sorted by timestamp."""
        if screen._tree:
            events = screen._extract_timeline_events()
            if len(events) > 1:
                timestamps = [e[0] for e in events]
                assert timestamps == sorted(timestamps)

    def test_extract_timeline_without_tree(self):
        """Test timeline extraction without a tree returns empty list."""
        screen = LoomScreen()  # No demo mode, no tree
        events = screen._extract_timeline_events()
        assert events == []
