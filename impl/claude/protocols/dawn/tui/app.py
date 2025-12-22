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
from textual.widgets import Header, Static

from ..focus import Bucket, FocusManager
from ..snippets import Snippet, SnippetLibrary
from .add_focus_modal import AddFocusModal
from .add_snippet_modal import AddSnippetModal
from .coffee_overlay import CoffeeOverlay, CoffeeResult
from .edit_snippet_modal import EditSnippetModal
from .focus_pane import FocusPane
from .garden_view import GardenView
from .help_modal import HelpModal
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

    # Use dock layout - Header docks top, GardenView docks bottom
    CSS = """
    #main-container {
        layout: horizontal;
        width: 100%;
        height: 1fr;
    }

    #focus-pane {
        width: 50%;
        border: solid gray;
        padding: 0 1;
    }

    #focus-pane.active {
        border: double cyan;
    }

    #snippet-pane {
        width: 50%;
        border: solid gray;
        padding: 0 1;
    }

    #snippet-pane.active {
        border: double green;
    }

    #garden-view {
        dock: bottom;
        height: 5;
        border: solid magenta;
        padding: 0 1;
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
        # Global bindings (shown in sidebar)
        Binding("question_mark", "help", "Help", priority=True),
        Binding("q", "quit", "Quit", priority=True),
        Binding("tab", "switch_pane", "Switch Pane", priority=True),
        Binding("r", "refresh", "Refresh"),
        Binding("slash", "search", "Search"),
        Binding("c", "coffee", "Coffee"),  # Morning Coffee ritual
        # Focus pane actions (context-sensitive, hidden from sidebar)
        Binding("a", "add_focus", "Add Focus", show=False),
        Binding("d", "done_focus", "Done", show=False),
        Binding("h", "hygiene", "Hygiene", show=False),
        Binding("u", "undo", "Undo", show=False),
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
            self._snippet_library.load_custom()  # Load persisted custom snippets
        self._dawn_start_time = datetime.now()
        self._last_archived_focus: Any = None  # For undo functionality

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
        # Footer removed - was intercepting Enter key
        # yield Footer()

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

    def action_add_focus(self) -> None:
        """Add a new focus item (opens modal) - only when focus pane is active."""
        if self.active_pane != "focus":
            return  # Ignore when snippet pane is active
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
        self._notify_garden(f"✅ Added: {item.label}")

    def action_done_focus(self) -> None:
        """Mark current focus item as done - only when focus pane is active."""
        if self.active_pane != "focus":
            return  # Ignore when snippet pane is active
        focus_pane = self.query_one("#focus-pane", FocusPane)
        item = focus_pane.selected_item
        if item:
            # Store for undo
            self._last_archived_focus = item
            self._focus_manager.remove(item.id)
            focus_pane.refresh_items()
            self._notify_garden(f"✅ Done: {item.label} [u] undo")

    def action_undo(self) -> None:
        """Undo last archive action."""
        if not hasattr(self, "_last_archived_focus") or self._last_archived_focus is None:
            return
        item = self._last_archived_focus
        self._last_archived_focus = None
        # Re-add the item
        restored = self._focus_manager.add(
            item.target,
            label=item.label,
            bucket=item.bucket,
        )
        self.query_one("#focus-pane", FocusPane).refresh_items()
        self._notify_garden(f"↩️ Restored: {restored.label}")

    def action_hygiene(self) -> None:
        """Run hygiene check on focus items - only when focus pane is active."""
        if self.active_pane != "focus":
            return  # Ignore when snippet pane is active
        stale = self._focus_manager.get_stale()
        if stale:
            self._notify_garden(f"Hygiene: {len(stale)} stale items found")
        else:
            self._notify_garden("Hygiene: All items fresh!")

    def action_help(self) -> None:
        """Show comprehensive help panel."""
        self.push_screen(HelpModal())

    def action_coffee(self) -> None:
        """
        Start the Morning Coffee ritual.

        Opens the coffee overlay which guides through four movements:
        1. Garden View — What grew overnight
        2. Hygiene Pass — Stale items needing attention
        3. Focus Set — Confirm today's 1-3 items
        4. Snippet Prime — Prepare button pad for day

        See: spec/protocols/dawn-cockpit.md § Morning Coffee Integration
        """
        self.push_screen(
            CoffeeOverlay(
                focus_manager=self._focus_manager,
                snippet_library=self._snippet_library,
            ),
            self._handle_coffee,
        )

    def _handle_coffee(self, result: CoffeeResult | None) -> None:
        """Handle result from CoffeeOverlay."""
        if result is None:
            return

        if result.completed:
            # Full ritual complete
            minutes = int(result.time_spent_seconds / 60)
            seconds = int(result.time_spent_seconds % 60)
            self._notify_garden(f"☕ Coffee complete! ({minutes}:{seconds:02d})")
            # Refresh panes to show any updates
            self.query_one("#focus-pane", FocusPane).refresh_items()
            self.query_one("#snippet-pane", SnippetPane).refresh_items()
        else:
            # Partial ritual
            self._notify_garden(f"☕ Coffee paused at {result.movement_reached.title}")

    def action_search(self) -> None:
        """Open search prompt."""
        # TODO: Implement search
        self._notify_garden("Search: Coming soon...")

    def action_refresh(self) -> None:
        """Refresh all panes (no event emitted - just re-render)."""
        self.query_one("#focus-pane", FocusPane).refresh_items()
        self.query_one("#snippet-pane", SnippetPane).refresh_items()
        # Re-render garden without adding event
        try:
            garden = self.query_one("#garden-view", GardenView)
            garden._update_display()
        except Exception:
            pass

    def on_focus_pane_item_activated(self, message: FocusPane.ItemActivated) -> None:
        """Handle focus item activation (Enter) — copy target path to clipboard."""
        item = message.item
        target = item.target

        # Copy to clipboard
        try:
            # Try pyperclip first, fall back to pbcopy on macOS
            copied = False
            try:
                import pyperclip  # type: ignore[import-untyped]

                pyperclip.copy(target)
                copied = True
            except ImportError:
                pass
            except Exception:
                pass

            if not copied:
                # macOS fallback
                try:
                    import subprocess

                    process = subprocess.Popen(["pbcopy"], stdin=subprocess.PIPE)
                    process.communicate(target.encode("utf-8"))
                except Exception:
                    pass

            self._notify_garden(f"📋 {target}")
        except Exception as e:
            logger.error(f"Failed to copy focus target: {e}")

    def on_snippet_pane_snippet_copied(self, message: SnippetPane.SnippetCopied) -> None:
        """Handle snippet copied event — show confirmation in Garden."""
        label = message.snippet.to_dict().get("label", "snippet") if message.snippet else "snippet"
        self._notify_garden(f"📋 {label}")

    def on_snippet_pane_snippet_add_requested(
        self, message: SnippetPane.SnippetAddRequested
    ) -> None:
        """Handle snippet add request — open add modal."""
        self.push_screen(AddSnippetModal(), self._handle_add_snippet)

    def _handle_add_snippet(self, result: tuple[str, str] | None) -> None:
        """Handle result from AddSnippetModal."""
        if result is None:
            return  # User cancelled

        label, content = result
        self._snippet_library.add_custom(label, content)
        self.query_one("#snippet-pane", SnippetPane).refresh_items()
        self._notify_garden(f"★ Added: {label}")

    def on_snippet_pane_snippet_edit_requested(
        self, message: SnippetPane.SnippetEditRequested
    ) -> None:
        """Handle snippet edit request — open edit modal."""
        self.push_screen(
            EditSnippetModal(message.snippet),
            lambda result: self._handle_edit_snippet(message.snippet, result),
        )

    def _handle_edit_snippet(self, snippet: Snippet, result: tuple[str, str] | None) -> None:
        """Handle result from EditSnippetModal."""
        if result is None:
            return  # User cancelled

        label, content = result
        snippet_dict = snippet.to_dict()
        updated = self._snippet_library.update_custom(
            snippet_dict["id"],
            label=label,
            content=content,
        )
        if updated:
            self.query_one("#snippet-pane", SnippetPane).refresh_items()
            self._notify_garden(f"✏️ Edited: {label}")

    async def on_mount(self) -> None:
        """Handle app mount."""
        # Start with focus pane active
        self.active_pane = "focus"
        self.query_one("#focus-pane").focus()

        # Add startup message to garden
        self._notify_garden("Dawn awakened. Tab to switch panes, Enter to copy.")

    def _notify_garden(self, text: str) -> None:
        """
        Directly update the garden view with a message.

        This bypasses the message bus for immediate, synchronous updates.

        Teaching:
            gotcha: Textual's message bus can delay delivery, causing UI to feel
                    unresponsive. For immediate feedback (like copy confirmation),
                    call add_event directly instead of posting GardenEvent.
                    (Evidence: User report of events not appearing until refresh)
        """
        try:
            garden = self.query_one("#garden-view", GardenView)
            garden.add_event(text)
        except Exception as e:
            logger.warning(f"Failed to update garden: {e}")


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
