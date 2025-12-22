"""
Dawn Cockpit Help Modal: Comprehensive help panel.

Shows all keybindings and usage information.

See: spec/protocols/dawn-cockpit.md
"""

from __future__ import annotations

from typing import Any

from textual.containers import Vertical, VerticalScroll
from textual.screen import ModalScreen
from textual.widgets import Static

HELP_TEXT = """\
[bold cyan]DAWN COCKPIT[/bold cyan]
Quarter-screen focus management + snippet button pad

[bold]GLOBAL[/bold]
  [cyan]Tab[/cyan]      Switch between Focus and Snippets pane
  [cyan]?[/cyan]        Show this help
  [cyan]q[/cyan]        Quit
  [cyan]r[/cyan]        Refresh
  [cyan]/[/cyan]        Search (coming soon)

[bold]FOCUS PANE[/bold] (when active)
  [cyan]↑/k[/cyan]      Move selection up
  [cyan]↓/j[/cyan]      Move selection down
  [cyan]1-9[/cyan]      Quick select by number
  [cyan]Enter[/cyan]    Open/activate item
  [cyan]a[/cyan]        Add new focus item
  [cyan]d[/cyan]        Mark selected as done
  [cyan]u[/cyan]        Undo last done
  [cyan]h[/cyan]        Run hygiene check

[bold]SNIPPETS PANE[/bold] (when active)
  [cyan]↑/k[/cyan]      Move selection up
  [cyan]↓/j[/cyan]      Move selection down
  [cyan]1-9[/cyan]      Quick select by number
  [cyan]Enter[/cyan]    Copy snippet to clipboard
  [cyan]n[/cyan]        New custom snippet
  [cyan]e[/cyan]        Edit custom snippet
  [cyan]x[/cyan]        Delete custom snippet

[bold]MODALS[/bold]
  [cyan]Tab[/cyan]      Cycle through fields
  [cyan]Enter[/cyan]    Submit (from input fields)
  [cyan]Escape[/cyan]   Cancel

[dim]Press Escape or ? to close this help[/dim]
"""


class HelpModal(ModalScreen[None]):
    """
    Modal showing comprehensive help information.

    Teaching:
        gotcha: This replaces the per-pane footers with a unified
                help panel accessible via '?'.
    """

    BINDINGS = [
        ("escape", "close", "Close"),
        ("question_mark", "close", "Close"),
    ]

    CSS = """
    HelpModal {
        align: center middle;
    }

    #help-container {
        width: 60;
        height: auto;
        max-height: 30;
        border: thick $primary;
        background: $surface;
        padding: 1 2;
    }

    #help-scroll {
        height: auto;
        max-height: 26;
    }

    #help-title {
        text-align: center;
        text-style: bold;
        padding-bottom: 1;
    }
    """

    def compose(self) -> Any:
        """Compose the help content."""
        with Vertical(id="help-container"):
            yield Static("HELP", id="help-title")
            yield Static("═" * 50)
            with VerticalScroll(id="help-scroll"):
                yield Static(HELP_TEXT)

    def action_close(self) -> None:
        """Close the help modal."""
        self.dismiss(None)


__all__ = [
    "HelpModal",
]
