"""
LoomScreen - The Cognitive Loom.

Navigate agent decision history as a topological tree, not a linear log.
The key innovation: The Shadow (rejected branches) is visible.

Navigation:
  j/k: Move through time (up/down)
  h/l: Navigate branches (left/right)
  c:   Crystallize moment → D-gent memory
  g:   Toggle ghost branch visibility
  escape: Return to Flux view
"""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import TYPE_CHECKING

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container, Vertical
from textual.reactive import reactive
from textual.screen import Screen
from textual.widgets import Footer, Header, Static

from ..data.loom import CognitiveBranch, CognitiveTree
from ..widgets.branch_tree import BranchTree
from ..widgets.timeline import Timeline

if TYPE_CHECKING:
    pass


def create_demo_cognitive_tree() -> CognitiveTree:
    """
    Create a demo cognitive tree for testing.

    Shows a realistic decision-making scenario with branching.
    """
    now = datetime.now()

    # Root: Start of agent session
    root = CognitiveBranch(
        id="start",
        timestamp=now - timedelta(minutes=10),
        content="Initialize conversation",
        reasoning="User requested code analysis",
        selected=True,
    )

    # First decision: Approach selection
    approach_a = CognitiveBranch(
        id="approach-grep",
        timestamp=now - timedelta(minutes=9),
        content="Plan A: Use grep for pattern search",
        reasoning="Fast, direct, familiar tool",
        selected=True,
        parent_id="start",
    )

    approach_b = CognitiveBranch(
        id="approach-ast",
        timestamp=now - timedelta(minutes=9),
        content="Plan B: Parse AST for semantic search",
        reasoning="More accurate but slower",
        selected=False,  # Ghost branch - rejected
        parent_id="start",
    )

    root.children = [approach_a, approach_b]

    # Approach A leads to execution
    execute_grep = CognitiveBranch(
        id="exec-grep",
        timestamp=now - timedelta(minutes=8),
        content="Execute: grep -r 'def ' .",
        reasoning="Search for function definitions",
        selected=True,
        parent_id="approach-grep",
    )

    # Alternative execution (rejected)
    execute_find = CognitiveBranch(
        id="exec-find",
        timestamp=now - timedelta(minutes=8),
        content="Execute: find . -name '*.py' -exec grep ...",
        reasoning="More portable but verbose",
        selected=False,  # Ghost branch
        parent_id="approach-grep",
    )

    approach_a.children = [execute_grep, execute_find]

    # Results processing
    process_results = CognitiveBranch(
        id="process",
        timestamp=now - timedelta(minutes=7),
        content="Process 47 matches",
        reasoning="Filter false positives",
        selected=True,
        parent_id="exec-grep",
    )

    execute_grep.children = [process_results]

    # Current state
    current = CognitiveBranch(
        id="current",
        timestamp=now - timedelta(minutes=5),
        content="Synthesize findings into report",
        reasoning="User expects summary",
        selected=True,
        parent_id="process",
    )

    process_results.children = [current]

    # Create the tree with current state
    tree = CognitiveTree(root=root, current_id="current")

    return tree


class LoomScreen(Screen[None]):
    """
    The Cognitive Loom - navigate agent decision history topologically.

    This screen replaces the traditional linear "History Explorer" with
    a branching tree that shows not just what the agent did, but what
    it considered and rejected.

    The Shadow is made visible.
    """

    CSS = """
    LoomScreen {
        background: #1a1a1a;
    }

    LoomScreen #main-container {
        width: 100%;
        height: 100%;
        padding: 1;
    }

    LoomScreen #header-info {
        dock: top;
        height: 3;
        background: #252525;
        padding: 1 2;
        color: #f5f0e6;
        border-bottom: solid #4a4a5c;
    }

    LoomScreen #loom-container {
        height: 1fr;
        border: solid #4a4a5c;
        padding: 1;
        margin: 1 0;
    }

    LoomScreen #timeline-container {
        height: 5;
        border: solid #4a4a5c;
        padding: 1;
    }

    LoomScreen #status-bar {
        dock: bottom;
        height: 1;
        background: #252525;
        color: #6a6560;
        padding: 0 2;
    }

    LoomScreen .loom-title {
        text-style: bold;
        color: #e6a352;
    }

    LoomScreen .agent-name {
        color: #f5d08a;
        text-style: bold;
    }
    """

    BINDINGS = [
        Binding("j", "nav_down", "Down (time)", show=True),
        Binding("k", "nav_up", "Up (time)", show=True),
        Binding("h", "nav_left", "Left (branch)", show=True),
        Binding("l", "nav_right", "Right (branch)", show=True),
        Binding("c", "crystallize", "Crystallize", show=True),
        Binding("g", "toggle_ghosts", "Toggle ghosts", show=True),
        Binding("escape", "back", "Back", show=True),
        Binding("q", "quit", "Quit", show=False),
    ]

    # Reactive state
    show_ghosts: reactive[bool] = reactive(True)

    def __init__(
        self,
        agent_id: str = "",
        agent_name: str = "",
        tree: CognitiveTree | None = None,
        demo_mode: bool = False,
        name: str | None = None,
        id: str | None = None,  # noqa: A002
        classes: str | None = None,
    ) -> None:
        super().__init__(name=name, id=id, classes=classes)
        self.agent_id = agent_id
        self.agent_name = agent_name
        self._tree = tree or (create_demo_cognitive_tree() if demo_mode else None)
        self._demo_mode = demo_mode
        self._branch_tree: BranchTree | None = None
        self._timeline: Timeline | None = None

    def compose(self) -> ComposeResult:
        """Compose the Loom screen."""
        yield Header()

        # Header info
        with Container(id="header-info"):
            yield Static(
                f"[bold #e6a352]COGNITIVE LOOM[/]  │  Agent: [bold #f5d08a]{self.agent_name or self.agent_id or 'Demo'}[/]"
            )
            yield Static("Navigate decision history  │  j/k: time  h/l: branches  c: crystallize")

        # Main container
        with Container(id="main-container"):
            # Branch tree (main view)
            with Container(id="loom-container"):
                self._branch_tree = BranchTree(
                    cognitive_tree=self._tree,
                    show_ghosts=self.show_ghosts,
                    id="loom",
                )
                yield self._branch_tree

            # Timeline (temporal overview)
            with Container(id="timeline-container"):
                yield Static("[Timeline]", classes="loom-title")
                if self._tree:
                    # Extract timeline events from tree
                    events = self._extract_timeline_events()
                    self._timeline = Timeline(events=events, id="timeline")
                    yield self._timeline
                else:
                    yield Static("No timeline data available")

        # Status bar
        ghost_status = "visible" if self.show_ghosts else "hidden"
        yield Static(
            f"Ghost branches: {ghost_status}  │  Press 'g' to toggle",
            id="status-bar",
        )

        yield Footer()

    def _extract_timeline_events(self) -> list[tuple[datetime, float]]:
        """
        Extract timeline events from the cognitive tree.

        Returns a list of (timestamp, activity) tuples for the Timeline widget.
        """
        if not self._tree:
            return []

        events = []
        for node in self._tree.all_nodes():
            # Activity level based on whether it's selected (1.0) or ghost (0.3)
            activity = 1.0 if node.selected else 0.3
            events.append((node.timestamp, activity))

        # Sort by timestamp
        events.sort(key=lambda x: x[0])
        return events

    def action_nav_down(self) -> None:
        """Navigate down through time to child node (j key)."""
        if self._branch_tree and self._tree:
            if self._tree.navigate_down():
                # Refresh the branch tree display
                self._branch_tree.refresh()
                current = self._tree.get_current()
                if current:
                    self.notify(f"→ {current.content[:40]}...")
            else:
                self.notify("At leaf node (no children)")

    def action_nav_up(self) -> None:
        """Navigate up through time to parent node (k key)."""
        if self._branch_tree and self._tree:
            if self._tree.navigate_up():
                self._branch_tree.refresh()
                current = self._tree.get_current()
                if current:
                    self.notify(f"← {current.content[:40]}...")
            else:
                self.notify("At root node (no parent)")

    def action_nav_left(self) -> None:
        """Navigate left to previous sibling branch (h key)."""
        if self._branch_tree and self._tree:
            if self._tree.navigate_left():
                self._branch_tree.refresh()
                current = self._tree.get_current()
                if current:
                    ghost_marker = " [ghost]" if not current.selected else ""
                    self.notify(f"↰ {current.content[:40]}...{ghost_marker}")
            else:
                self.notify("No sibling to the left")

    def action_nav_right(self) -> None:
        """Navigate right to next sibling branch (l key)."""
        if self._branch_tree and self._tree:
            if self._tree.navigate_right():
                self._branch_tree.refresh()
                current = self._tree.get_current()
                if current:
                    ghost_marker = " [ghost]" if not current.selected else ""
                    self.notify(f"↱ {current.content[:40]}...{ghost_marker}")
            else:
                self.notify("No sibling to the right")

    def action_crystallize(self) -> None:
        """
        Crystallize current moment to D-gent memory (c key).

        This is a deliberate act - the user marks a decision point
        as worth remembering permanently.
        """
        if self._tree:
            current_node = self._tree.get_node(self._tree.current_id)
            if current_node:
                self.notify(
                    f"Crystallizing: {current_node.content[:40]}... (D-gent integration pending)"
                )
            else:
                self.notify("No node selected for crystallization")
        else:
            self.notify("No cognitive tree loaded")

    def action_toggle_ghosts(self) -> None:
        """Toggle visibility of ghost branches (g key)."""
        self.show_ghosts = not self.show_ghosts
        if self._branch_tree:
            self._branch_tree.show_ghosts = self.show_ghosts

        # Update status bar
        status_bar = self.query_one("#status-bar", Static)
        ghost_status = "visible" if self.show_ghosts else "hidden"
        status_bar.update(f"Ghost branches: {ghost_status}  │  Press 'g' to toggle")

    def action_back(self) -> None:
        """Return to previous screen (Escape)."""
        self.dismiss()

    def action_quit(self) -> None:
        """Quit the application (q key)."""
        self.app.exit()

    def set_tree(self, tree: CognitiveTree) -> None:
        """
        Update the cognitive tree being displayed.

        Args:
            tree: The new cognitive tree to display
        """
        self._tree = tree
        if self._branch_tree:
            self._branch_tree.cognitive_tree = tree

        # Update timeline
        if self._timeline:
            events = self._extract_timeline_events()
            self._timeline.events = events
