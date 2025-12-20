"""
BranchTree Widget - Git-graph style cognitive history.

Renders the Cognitive Loom as navigable ASCII tree.
The key innovation: the Shadow (rejected hypotheses) is visible.

Bugs often live in "the path not taken" - making ghost branches visible
helps debug agent cognition.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from textual.reactive import reactive
from textual.widget import Widget

if TYPE_CHECKING:
    from textual.app import RenderResult

from ..data.loom import CognitiveBranch, CognitiveTree

# Box-drawing characters for tree structure (git-graph style)
LOOM_CHARS = {
    "trunk": "│",
    "branch_start": "├",
    "branch_end": "└",
    "arrow": "─",
    "selected": "●",
    "ghost": "○",
    "rejected": "✖",
    "forecast": ":",
}


class BranchTree(Widget):
    """
    Render cognitive tree as navigable graph.

    The tree shows:
    - Main trunk: Selected actions (the path taken)
    - Ghost branches: Rejected hypotheses (the Shadow)
    - Current state: Highlighted node

    Navigation:
      j/k: Move through time (up/down)
      h/l: Navigate branches (left/right)
      c:   Crystallize moment → D-gent memory
    """

    DEFAULT_CSS = """
    BranchTree {
        width: 100%;
        height: auto;
        padding: 1;
        color: #d4a574;
    }

    BranchTree .selected {
        color: #f5d08a;
        text-style: bold;
    }

    BranchTree .ghost {
        color: #6a6560;
    }

    BranchTree .rejected {
        color: #8b7ba5;
    }
    """

    # Reactive properties
    cognitive_tree: reactive[CognitiveTree | None] = reactive(None)
    show_ghosts: reactive[bool] = reactive(True)

    def __init__(
        self,
        cognitive_tree: CognitiveTree | None = None,
        show_ghosts: bool = True,
        name: str | None = None,
        id: str | None = None,  # noqa: A002
        classes: str | None = None,
    ) -> None:
        super().__init__(name=name, id=id, classes=classes)
        self.cognitive_tree = cognitive_tree
        self.show_ghosts = show_ghosts

    def render(self) -> "RenderResult":
        """Render the cognitive tree as ASCII art."""
        if not self.cognitive_tree:
            return "No cognitive history"

        lines: list[str] = []
        self._render_node(self.cognitive_tree.root, lines, prefix="", is_last=True)
        return "\n".join(lines)

    def _render_node(
        self,
        node: CognitiveBranch,
        lines: list[str],
        prefix: str,
        is_last: bool,
    ) -> None:
        """
        Recursively render a node and its children.

        Args:
            node: The node to render
            lines: Accumulator for output lines
            prefix: The prefix for this line (tree structure)
            is_last: Whether this is the last child of its parent
        """
        # Skip ghosts if not showing
        if not node.selected and not self.show_ghosts:
            return

        # Build the line
        connector = LOOM_CHARS["branch_end"] if is_last else LOOM_CHARS["branch_start"]
        glyph = node.glyph
        is_current = self.cognitive_tree and node.id == self.cognitive_tree.current_id

        # Truncate content to reasonable length
        content = node.content[:60] if len(node.content) > 60 else node.content

        # Build the line with markup for styling
        if is_current:
            line = f"{prefix}{connector}{LOOM_CHARS['arrow']}{glyph} [bold]{content}[/bold]"
        elif not node.selected:
            # Ghost branch
            line = f"{prefix}{connector}{LOOM_CHARS['arrow']}{glyph} [dim]{content}[/dim]"
        else:
            line = f"{prefix}{connector}{LOOM_CHARS['arrow']}{glyph} {content}"

        # Add reasoning if it's a significant branch point or ghost
        if node.reasoning and (not node.selected or len(node.children) > 1):
            reason_preview = (
                node.reasoning[:40] + "..." if len(node.reasoning) > 40 else node.reasoning
            )
            if not node.selected:
                line += f" [dim]({reason_preview})[/dim]"
            else:
                line += f" ({reason_preview})"

        lines.append(line)

        # Recurse into children
        # The prefix for children depends on whether this node is the last child
        child_prefix = prefix + ("  " if is_last else LOOM_CHARS["trunk"] + " ")

        for i, child in enumerate(node.children):
            self._render_node(
                child,
                lines,
                child_prefix,
                i == len(node.children) - 1,
            )

    def watch_cognitive_tree(self, new_tree: CognitiveTree | None) -> None:
        """React to tree changes."""
        self.refresh()

    def watch_show_ghosts(self, new_value: bool) -> None:
        """React to ghost visibility toggle."""
        self.refresh()

    def set_tree(self, tree: CognitiveTree | None) -> None:
        """Set the cognitive tree to display."""
        self.cognitive_tree = tree

    def toggle_ghosts(self) -> None:
        """Toggle visibility of ghost branches."""
        self.show_ghosts = not self.show_ghosts
