"""
Dawn Cockpit TUI Application.

The main Textual application that composes the quarter-screen interface.

Layout (80x24):
    ┌─────────────────────────────────────────────────────────────────────────────┐
    │  DAWN COCKPIT                                    ☕ 7:42am    📍 Session 47  │
    ├─────────────────────────────────────────────────────────────────────────────┤
    │                                                                             │
    │  TODAY'S FOCUS                          │  SNIPPETS (↑↓ select, ⏎ copy)    │
    │  ═══════════════                        │  ═══════════════════════════════ │
    │                                         │                                   │
    │  🔥 [1] Trail Persistence              │  ▶ Voice: "Depth > breadth"       │
    │      self.trail.persistence            │  ...                              │
    │                                         │                                   │
    ├─────────────────────────────────────────────────────────────────────────────┤
    │  GARDEN (what grew overnight)                                               │
    │  • 3 files changed → Portal Phase 5 completion                              │
    └─────────────────────────────────────────────────────────────────────────────┘

Key Bindings:
    ↑↓        Navigate items
    ⏎ Enter   Copy selected snippet / Open selected focus
    Tab       Switch panes (Focus ↔ Snippets)
    a         Add focus item
    d         Mark focus done (archive)
    h         Run hygiene check
    c         Morning Coffee overlay (Phase 5)
    /         Search
    r         Refresh
    q         Quit

See: spec/protocols/dawn-cockpit.md
AGENTESE: time.dawn
"""

from __future__ import annotations

import logging
from datetime import datetime
from typing import TYPE_CHECKING, Any

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal
from textual.message import Message
from textual.reactive import reactive
from textual.widgets import Footer, Header, Static

from ..focus import Bucket, FocusManager
from ..snippets import SnippetLibrary
from .add_focus_modal import AddFocusModal
from .focus_pane import FocusPane
from .garden_view import GardenView
from .snippet_pane import SnippetPane

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)


class DawnCockpit(App[None]):
    """
    Dawn Cockpit: Kent's daily operating surface.

    A quarter-screen TUI that composes focus management and snippet copying
    into a unified daily interface.

    Teaching:
        gotcha: Quarter-screen means 80x24. Don't expand to fill the terminal.
                This is a persistent overlay, not a full-screen app.
                (Evidence: spec/protocols/dawn-cockpit.md § Law 6)
    """

    TITLE = "DAWN COCKPIT"
    SUB_TITLE = "The gardener tends the garden."

    # Enforce quarter-screen dimensions
    CSS = """
    Screen {
        layout: grid;
        grid-size: 1 3;
        grid-rows: 1fr auto auto;
    }

    #main-container {
        layout: horizontal;
        height: 100%;
    }

    #focus-pane {
        width: 50%;
        border: solid gray;
        padding: 0 1;
        margin: 0 0 0 1;
    }

    #focus-pane.active {
        border: double cyan;
    }

    #snippet-pane {
        width: 50%;
        border: solid gray;
        padding: 0 1;
        margin: 0 1 0 0;
    }

    #snippet-pane.active {
        border: double green;
    }

    #garden-view {
        height: 4;
        border: solid magenta;
        padding: 0 1;
        margin: 0 1;
    }

    .pane-title {
        text-style: bold;
        padding-bottom: 1;
    }

    .pane-title-active {
        text-style: bold reverse;
        padding-bottom: 1;
    }

    .focus-item {
        padding: 0 1;
    }

    .focus-item.selected {
        background: $primary;
    }

    .focus-item.stale {
        color: $warning;
    }

    .snippet-item {
        padding: 0 1;
    }

    .snippet-item.selected {
        background: $primary;
    }

    .snippet-item.static {
        color: $text;
    }

    .snippet-item.query {
        color: $secondary;
    }

    .snippet-item.custom {
        color: $success;
    }
    """

    BINDINGS = [
        Binding("q", "quit", "Quit", priority=True),
        Binding("tab", "switch_pane", "Switch", priority=True),
        # NOTE: Enter is handled by individual panes (FocusPane, SnippetPane)
        # Not defined at app level - this prevents double-handling and lets
        # the widget's on_key method have full control with event.stop()
        Binding("a", "add_focus", "Add"),
        Binding("d", "done_focus", "Done"),
        Binding("h", "hygiene", "Hygiene"),
        # Binding("c", "coffee", "Coffee"),  # Phase 5
        Binding("slash", "search", "Search"),
        Binding("r", "refresh", "Refresh"),
    ]

    # Track active pane (empty default so watcher fires on first set)
    active_pane: reactive[str] = reactive("")

    def __init__(
        self,
        focus_manager: FocusManager | None = None,
        snippet_library: SnippetLibrary | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initialize Dawn Cockpit.

        Args:
            focus_manager: Optional FocusManager (creates default if None)
            snippet_library: Optional SnippetLibrary (creates default if None)
        """
        super().__init__(**kwargs)
        self._focus_manager = focus_manager or FocusManager()
        self._snippet_library = snippet_library or SnippetLibrary()
        if snippet_library is None:
            self._snippet_library.load_defaults()
        self._dawn_start_time = datetime.now()

    @property
    def focus_manager(self) -> FocusManager:
        """Get the focus manager."""
        return self._focus_manager

    @property
    def snippet_library(self) -> SnippetLibrary:
        """Get the snippet library."""
        return self._snippet_library

    def compose(self) -> ComposeResult:
        """Compose the Dawn Cockpit layout."""
        yield Header()
        with Horizontal(id="main-container"):
            yield FocusPane(
                self._focus_manager,
                id="focus-pane",
            )
            yield SnippetPane(
                self._snippet_library,
                id="snippet-pane",
            )
        yield GardenView(id="garden-view")
        yield Footer()

    def watch_active_pane(self, pane: str) -> None:
        """Update focus styling when active pane changes."""
        # Guard: might be called before widgets are mounted
        if not pane:
            return
        try:
            focus_pane = self.query_one("#focus-pane", FocusPane)
            snippet_pane = self.query_one("#snippet-pane", SnippetPane)
        except Exception:
            return  # Not mounted yet

        if pane == "focus":
            focus_pane.add_class("active")
            snippet_pane.remove_class("active")
            focus_pane.is_active = True
            snippet_pane.is_active = False
        else:
            focus_pane.remove_class("active")
            snippet_pane.add_class("active")
            focus_pane.is_active = False
            snippet_pane.is_active = True

    def action_switch_pane(self) -> None:
        """Switch between Focus and Snippet panes."""
        self.active_pane = "snippet" if self.active_pane == "focus" else "focus"
        # Focus the appropriate widget
        if self.active_pane == "focus":
            self.query_one("#focus-pane").focus()
        else:
            self.query_one("#snippet-pane").focus()

    def action_activate_item(self) -> None:
        """Activate the selected item in the active pane."""
        if self.active_pane == "focus":
            focus_pane = self.query_one("#focus-pane", FocusPane)
            if focus_pane.selected_item:
                focus_pane.post_message(focus_pane.ItemActivated(focus_pane.selected_item))
        else:
            snippet_pane = self.query_one("#snippet-pane", SnippetPane)
            snippet_pane._copy_selected()

    def action_add_focus(self) -> None:
        """Add a new focus item (opens modal)."""
        self.push_screen(AddFocusModal(), self._handle_add_focus)

    def _handle_add_focus(self, result: tuple[str, str, str] | None) -> None:
        """Handle result from AddFocusModal."""
        if result is None:
            # User cancelled
            return

        target, label, bucket_value = result
        bucket = Bucket(bucket_value)
        item = self._focus_manager.add(target, label=label or None, bucket=bucket)
        self.query_one("#focus-pane", FocusPane).refresh_items()
        garden = self.query_one("#garden-view", GardenView)
        garden.add_event(f"✅ Added: {item.label}")

    def action_done_focus(self) -> None:
        """Mark current focus item as done."""
        focus_pane = self.query_one("#focus-pane", FocusPane)
        if focus_pane.selected_item:
            self._focus_manager.remove(focus_pane.selected_item.id)
            focus_pane.refresh_items()
            garden = self.query_one("#garden-view", GardenView)
            garden.add_event(f"Archived: {focus_pane.selected_item.label}")

    def action_hygiene(self) -> None:
        """Run hygiene check on focus items."""
        stale = self._focus_manager.get_stale()
        garden = self.query_one("#garden-view", GardenView)
        if stale:
            garden.add_event(f"Hygiene: {len(stale)} stale items found")
        else:
            garden.add_event("Hygiene: All items fresh!")

    def action_search(self) -> None:
        """Open search prompt."""
        # TODO: Implement search
        garden = self.query_one("#garden-view", GardenView)
        garden.add_event("Search: Coming soon...")

    def action_refresh(self) -> None:
        """Refresh all panes."""
        self.query_one("#focus-pane", FocusPane).refresh_items()
        self.query_one("#snippet-pane", SnippetPane).refresh_items()
        garden = self.query_one("#garden-view", GardenView)
        garden.add_event("Refreshed")

    def on_snippet_pane_snippet_copied(self, message: SnippetPane.SnippetCopied) -> None:
        """Handle snippet copied event — show confirmation in Garden."""
        garden = self.query_one("#garden-view", GardenView)
        label = message.snippet.to_dict().get("label", "snippet")
        garden.add_event(f"📋 Copied: {label}")

    async def on_mount(self) -> None:
        """Handle app mount."""
        # Start with focus pane active
        self.active_pane = "focus"
        self.query_one("#focus-pane").focus()

        # Add startup message to garden
        garden = self.query_one("#garden-view", GardenView)
        garden.add_event("Dawn awakened. Tab to switch panes, Enter to copy.")


def run_dawn_tui(
    focus_manager: FocusManager | None = None,
    snippet_library: SnippetLibrary | None = None,
) -> int:
    """
    Run the Dawn Cockpit TUI.

    Args:
        focus_manager: Optional FocusManager (creates default if None)
        snippet_library: Optional SnippetLibrary (creates default if None)

    Returns:
        Exit code (0 for success)
    """
    app = DawnCockpit(focus_manager, snippet_library)
    try:
        app.run()
        return 0
    except Exception as e:
        logger.exception("Dawn TUI error: %s", e)
        return 1


__all__ = [
    "DawnCockpit",
    "run_dawn_tui",
]
