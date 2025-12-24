"""
Witness Dashboard TUI Application.

The main Textual application that composes the crystal navigator interface.

Layout (80x24):
    ┌─────────────────────────────────────────────────────────────────────────────┐
    │  WITNESS — Crystal Navigator                    💎 47 crystals   ◉ L0 filter │
    ├─────────────────────────────────────────────────────────────────────────────┤
    │                                                                             │
    │  HIERARCHY                                      │  DETAILS                  │
    │  ═══════════                                    │  ════════                 │
    │                                                 │                           │
    │  ▪ [SESSION] Completed extinction audit         │  Insight:                 │
    │              3m ago • 12 marks • 95%           │  Completed extinction     │
    │                                                 │  audit, removed 52K       │
    │  ▫ [SESSION] Hardened Brain persistence        │  lines of stale code.     │
    │              1h ago • 8 marks • 88%            │                           │
    │                                                 │  Significance:            │
    │  ▫ [DAY] Major codebase cleanup                │  Codebase is leaner,      │
    │          5h ago • 3 crystals • 92%             │  focus is sharper.        │
    │                                                 │                           │
    ├─────────────────────────────────────────────────────────────────────────────┤
    │  j/k: navigate  Enter: copy  0-3: filter level  q: quit                     │
    └─────────────────────────────────────────────────────────────────────────────┘

Key Bindings:
    j/k       Navigate crystals (vim-style)
    ↑/↓       Navigate crystals (arrows)
    Enter     Copy insight to clipboard
    0-3       Filter by level (SESSION/DAY/WEEK/EPOCH)
    a         Show all levels
    r         Refresh crystals
    q         Quit

See: plans/witness-dashboard-tui.md
AGENTESE: self.witness
"""

from __future__ import annotations

import logging
from datetime import datetime, timedelta
from typing import TYPE_CHECKING, Any

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal
from textual.reactive import reactive
from textual.widgets import Footer, Static

from .crystal_list import CrystalListPane
from .detail_pane import CrystalDetailPane
from .hint_bar import HintBar

if TYPE_CHECKING:
    from ..crystal import Crystal, CrystalLevel

logger = logging.getLogger(__name__)


class WitnessDashApp(App[None]):
    """
    Witness Dashboard: Crystal Navigator TUI.

    A quarter-screen TUI for navigating the crystal hierarchy with
    vim-style navigation, level filtering, and copy-to-clipboard.

    Teaching:
        gotcha: Use run_worker for async crystal loading to keep UI responsive.
                Never block the UI thread with asyncio.run().
                (Evidence: plans/witness-dashboard-tui.md § Key Decisions)
    """

    TITLE = "WITNESS"
    SUB_TITLE = "Crystal Navigator"

    CSS = """
    Screen {
        layout: grid;
        grid-size: 1 3;
        grid-rows: 1fr auto auto;
    }

    #header {
        height: 3;
        background: $surface;
        padding: 0 2;
        content-align: center middle;
    }

    #main-container {
        layout: horizontal;
        height: 100%;
    }

    #crystal-list {
        width: 55%;
        border: solid $primary;
        padding: 0 1;
    }

    #crystal-list.active {
        border: double $primary;
    }

    #detail-pane {
        width: 45%;
        border: solid $secondary;
        padding: 0 1;
    }

    .pane-title {
        text-style: bold;
        padding-bottom: 1;
    }

    .crystal-item {
        padding: 0 1;
    }

    .crystal-item.selected {
        background: $primary;
        color: $text;
    }

    .level-session {
        color: $primary;
    }

    .level-day {
        color: $success;
    }

    .level-week {
        color: $warning;
    }

    .level-epoch {
        color: $error;
    }

    .age {
        color: $text-muted;
    }

    .confidence-high {
        color: $success;
    }

    .confidence-medium {
        color: $warning;
    }

    .confidence-low {
        color: $error;
    }

    #hint-bar {
        height: 1;
        background: $surface;
        padding: 0 1;
    }
    """

    BINDINGS = [
        Binding("q", "quit", "Quit", priority=True),
        Binding("j", "move_down", "↓", show=False),
        Binding("k", "move_up", "↑", show=False),
        Binding("down", "move_down", show=False),
        Binding("up", "move_up", show=False),
        Binding("enter", "copy_insight", "Copy"),
        Binding("0", "filter_level_0", "SESSION"),
        Binding("1", "filter_level_1", "DAY"),
        Binding("2", "filter_level_2", "WEEK"),
        Binding("3", "filter_level_3", "EPOCH"),
        Binding("a", "filter_all", "All"),
        Binding("r", "refresh", "Refresh"),
    ]

    # Reactive state
    level_filter: reactive[int | None] = reactive(None)
    crystal_count: reactive[int] = reactive(0)

    def __init__(
        self,
        initial_level: int | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initialize Witness Dashboard.

        Args:
            initial_level: Optional initial level filter (0-3)
        """
        super().__init__(**kwargs)
        self._initial_level = initial_level
        self._crystals: list[Any] = []

    def compose(self) -> ComposeResult:
        """Compose the dashboard layout."""
        yield Static(self._render_header(), id="header")
        with Horizontal(id="main-container"):
            yield CrystalListPane(id="crystal-list")
            yield CrystalDetailPane(id="detail-pane")
        yield HintBar(id="hint-bar")
        yield Footer()

    def _render_header(self) -> str:
        """Render the header with stats."""
        level_indicator = ""
        if self.level_filter is not None:
            level_names = {0: "SESSION", 1: "DAY", 2: "WEEK", 3: "EPOCH"}
            level_indicator = f"◉ {level_names.get(self.level_filter, '?')}"
        else:
            level_indicator = "◯ All"

        return f"WITNESS — Crystal Navigator                    💎 {self.crystal_count} crystals   {level_indicator}"

    def watch_level_filter(self, level: int | None) -> None:
        """Update header when level filter changes."""
        try:
            header = self.query_one("#header", Static)
            header.update(self._render_header())
            # Refresh crystal list with new filter
            self.action_refresh()
        except Exception:
            pass  # Not mounted yet

    def watch_crystal_count(self, count: int) -> None:
        """Update header when crystal count changes."""
        try:
            header = self.query_one("#header", Static)
            header.update(self._render_header())
        except Exception:
            pass

    async def on_mount(self) -> None:
        """Handle app mount."""
        # Set initial level filter
        if self._initial_level is not None:
            self.level_filter = self._initial_level

        # Focus the crystal list
        self.query_one("#crystal-list").focus()
        self.query_one("#crystal-list").add_class("active")

        # Update hint bar
        self.query_one("#hint-bar", HintBar).set_hints(
            "j/k: navigate  Enter: copy  0-3: filter level  a: all  r: refresh  q: quit"
        )

        # Load crystals after refresh to ensure widgets are ready
        self.call_after_refresh(self._schedule_crystal_load)

    def _schedule_crystal_load(self) -> None:
        """Schedule crystal loading after UI is ready."""
        self.run_worker(self._load_crystals())

    async def _load_crystals(self) -> None:
        """Load crystals from the store (async worker)."""
        try:
            from ..crystal import CrystalLevel
            from ..crystal_store import get_crystal_store

            store = get_crystal_store()

            if self.level_filter is not None:
                level = CrystalLevel(self.level_filter)
                crystals = store.recent(limit=50, level=level)
            else:
                crystals = store.recent(limit=50)

            self._crystals = crystals
            self.crystal_count = len(crystals)

            logger.info(f"Loaded {len(crystals)} crystals")

            # Update the list pane
            list_pane = self.query_one("#crystal-list", CrystalListPane)
            list_pane.set_crystals(crystals)

            logger.info(f"Set {len(list_pane._crystals)} crystals on pane")

            # Force refresh of the list pane
            list_pane.refresh()

            # Show notification so user knows loading happened
            self.notify(f"Loaded {len(crystals)} crystals", severity="information")

            # Select first crystal if available
            if crystals:
                self._on_crystal_selected(crystals[0])
                logger.info(f"Selected first crystal: {crystals[0].insight[:30]}...")

        except Exception as e:
            logger.exception("Failed to load crystals: %s", e)
            self.notify(f"Error loading crystals: {e}", severity="error")

    def _on_crystal_selected(self, crystal: Any) -> None:
        """Handle crystal selection."""
        detail_pane = self.query_one("#detail-pane", CrystalDetailPane)
        detail_pane.set_crystal(crystal)

    def action_move_down(self) -> None:
        """Move selection down."""
        list_pane = self.query_one("#crystal-list", CrystalListPane)
        list_pane.select_next()
        if list_pane.selected_crystal:
            self._on_crystal_selected(list_pane.selected_crystal)

    def action_move_up(self) -> None:
        """Move selection up."""
        list_pane = self.query_one("#crystal-list", CrystalListPane)
        list_pane.select_previous()
        if list_pane.selected_crystal:
            self._on_crystal_selected(list_pane.selected_crystal)

    def action_copy_insight(self) -> None:
        """Copy selected crystal's insight to clipboard."""
        list_pane = self.query_one("#crystal-list", CrystalListPane)
        crystal = list_pane.selected_crystal
        if crystal:
            try:
                import pyperclip  # type: ignore[import-untyped]

                pyperclip.copy(crystal.insight)
                self.notify("📋 Copied insight to clipboard", severity="information")
            except ImportError:
                # Fallback if pyperclip not available
                self.notify("⚠️ pyperclip not installed", severity="warning")
            except Exception as e:
                self.notify(f"Copy failed: {e}", severity="error")

    def action_filter_level_0(self) -> None:
        """Filter to SESSION crystals."""
        self.level_filter = 0

    def action_filter_level_1(self) -> None:
        """Filter to DAY crystals."""
        self.level_filter = 1

    def action_filter_level_2(self) -> None:
        """Filter to WEEK crystals."""
        self.level_filter = 2

    def action_filter_level_3(self) -> None:
        """Filter to EPOCH crystals."""
        self.level_filter = 3

    def action_filter_all(self) -> None:
        """Show all levels."""
        self.level_filter = None

    def action_refresh(self) -> None:
        """Refresh crystals from store."""
        self.run_worker(self._load_crystals())
        self.notify("Refreshed", severity="information")

    def on_crystal_list_pane_crystal_selected(
        self, message: CrystalListPane.CrystalSelected
    ) -> None:
        """Handle crystal selection from list pane."""
        self._on_crystal_selected(message.crystal)


def run_witness_tui(initial_level: int | None = None) -> int:
    """
    Run the Witness Dashboard TUI.

    Args:
        initial_level: Optional initial level filter (0-3)

    Returns:
        Exit code (0 for success)

    Note:
        This must be called from the main thread with no running event loop.
        hollow.py ensures this by intercepting "witness dashboard" before
        daemon routing or asyncio.run() wrapping.
    """
    import sys

    # Check if we have a real terminal
    if not sys.stdin.isatty():
        print(
            "Error: TUI requires an interactive terminal.\n"
            "\n"
            "Or use the classic Rich dashboard:\n"
            "  kg witness dashboard --classic"
        )
        return 1

    app = WitnessDashApp(initial_level=initial_level)

    try:
        app.run()
        return 0
    except Exception as e:
        logger.exception("Witness TUI error: %s", e)
        return 1


__all__ = [
    "WitnessDashApp",
    "run_witness_tui",
]
