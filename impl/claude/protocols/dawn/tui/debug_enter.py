#!/usr/bin/env python3
"""
Debug script to test Enter key behavior in Dawn TUI.
"""

from textual.app import App
from textual.binding import Binding
from textual.widgets import Footer, Header, Static
from textual.containers import Horizontal


class DebugApp(App):
    """Minimal app to debug Enter key."""

    TITLE = "DEBUG ENTER KEY"

    BINDINGS = [
        Binding("q", "quit", "Quit", priority=True),
        Binding("enter", "test_enter", "Test", priority=True),
    ]

    CSS = """
    Screen {
        layout: grid;
        grid-size: 1 2;
        grid-rows: 1fr auto;
    }

    #main {
        height: 100%;
        border: solid cyan;
        padding: 1;
    }
    """

    def compose(self):
        yield Header()
        yield Static("Press Enter to test", id="main")
        yield Footer()

    def action_test_enter(self):
        """Test Enter action."""
        main = self.query_one("#main", Static)
        main.update(f"[green]Enter pressed! Count: {getattr(self, '_count', 0) + 1}[/green]")
        self._count = getattr(self, '_count', 0) + 1


if __name__ == "__main__":
    app = DebugApp()
    app.run()
