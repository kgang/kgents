#!/usr/bin/env python3
"""
Diagnostic TUI to understand Enter key black bar issue.

This reproduces the Dawn Cockpit structure and logs all key events.
"""

from textual.app import App
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.events import Key
from textual.widgets import Footer, Header, Static


class DiagnosticLog(Static):
    """Widget to show diagnostic logs."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._logs = []

    def log(self, message: str):
        """Add a log message."""
        self._logs.append(message)
        # Keep last 20 lines
        if len(self._logs) > 20:
            self._logs.pop(0)
        self.update("\n".join(self._logs))


class LeftPane(Static, can_focus=True):
    """Left pane that handles Enter."""

    is_active = False

    def render(self):
        if self.is_active:
            return "[bold cyan]LEFT PANE (active)\n\nPress Enter here[/bold cyan]"
        return "[dim]LEFT PANE\n\nNot active[/dim]"

    def on_key(self, event: Key):
        log = self.app.query_one(DiagnosticLog)
        log.log(f"[yellow]LeftPane.on_key: {event.key} (active={self.is_active})[/yellow]")

        if not self.is_active:
            return

        if event.key == "enter":
            log.log("[green]LeftPane: Enter handled![/green]")
            event.stop()


class RightPane(Static, can_focus=True):
    """Right pane that handles Enter."""

    is_active = False

    def render(self):
        if self.is_active:
            return "[bold green]RIGHT PANE (active)\n\nPress Enter here[/bold green]"
        return "[dim]RIGHT PANE\n\nNot active[/dim]"

    def on_key(self, event: Key):
        log = self.app.query_one(DiagnosticLog)
        log.log(f"[yellow]RightPane.on_key: {event.key} (active={self.is_active})[/yellow]")

        if not self.is_active:
            return

        if event.key == "enter":
            log.log("[green]RightPane: Enter copied![/green]")
            event.stop()


class DiagnosticApp(App):
    """Diagnostic app to test Enter behavior."""

    TITLE = "DIAGNOSTIC: Enter Key Behavior"

    BINDINGS = [
        Binding("q", "quit", "Quit", priority=True),
        Binding("tab", "switch_pane", "Switch", priority=True),
        Binding("enter", "activate", "Activate", priority=True),
    ]

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

    #left-pane {
        width: 50%;
        border: solid gray;
        padding: 1;
    }

    #left-pane.active {
        border: double cyan;
    }

    #right-pane {
        width: 50%;
        border: solid gray;
        padding: 1;
    }

    #right-pane.active {
        border: double green;
    }

    #log-pane {
        height: 10;
        border: solid magenta;
        padding: 1;
        overflow-y: auto;
    }
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.active_pane = ""

    def compose(self):
        yield Header()
        with Horizontal(id="main-container"):
            yield LeftPane(id="left-pane")
            yield RightPane(id="right-pane")
        yield DiagnosticLog(id="log-pane")
        yield Footer()

    def on_mount(self):
        self.active_pane = "left"
        self._update_active_pane()
        log = self.query_one(DiagnosticLog)
        log.log("[bold]Diagnostic App Started[/bold]")
        log.log("Press Tab to switch panes, Enter to test")

    def on_key(self, event: Key):
        """Log all key events at app level."""
        log = self.query_one(DiagnosticLog)
        log.log(f"[blue]App.on_key: {event.key}[/blue]")

    def action_switch_pane(self):
        """Switch panes."""
        log = self.query_one(DiagnosticLog)
        self.active_pane = "right" if self.active_pane == "left" else "left"
        self._update_active_pane()
        log.log(f"[cyan]Switched to {self.active_pane} pane[/cyan]")

    def action_activate(self):
        """Activate item in active pane."""
        log = self.query_one(DiagnosticLog)
        log.log(f"[magenta]App.action_activate called (active={self.active_pane})[/magenta]")

        if self.active_pane == "left":
            log.log("[green]→ Delegating to left pane[/green]")
        else:
            log.log("[green]→ Delegating to right pane[/green]")

    def _update_active_pane(self):
        """Update active pane visual state."""
        left = self.query_one("#left-pane", LeftPane)
        right = self.query_one("#right-pane", RightPane)

        if self.active_pane == "left":
            left.add_class("active")
            right.remove_class("active")
            left.is_active = True
            right.is_active = False
            left.focus()
        else:
            left.remove_class("active")
            right.add_class("active")
            left.is_active = False
            right.is_active = True
            right.focus()


if __name__ == "__main__":
    app = DiagnosticApp()
    app.run()
