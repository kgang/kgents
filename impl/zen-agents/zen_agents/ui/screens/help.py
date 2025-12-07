"""Help screen for zen-agents."""

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Vertical, VerticalScroll
from textual.screen import ModalScreen
from textual.widgets import Static


HELP_TEXT = """
[bold]zen-agents[/bold] - Agent-based session management

[underline]Navigation[/underline]
  j/k or ↑↓       Move selection up/down
  space/l         Toggle grab mode (reorder sessions)
  escape          Exit current mode / clear filter

[underline]Session Actions[/underline]
  n               New session
  a               Attach to tmux session
  p               Pause session
  x               Kill session
  d               Clean up dead session
  v               Revive session

[underline]Search & Filter[/underline]
  /               Search sessions by name
  f               Cycle type filter
  1-5             Quick filter (1=Claude 2=Shell 3=Codex 4=Gemini 5=Custom)
  0               Clear all filters

[underline]View[/underline]
  r               Refresh output
  s               Toggle streaming mode

[underline]Commands[/underline]
  ctrl+p          Open command palette
  ?/F1            Show this help
  q               Quit

[dim]Built on kgents bootstrap agents: Compose, Judge, Ground,
Contradict, Sublate, Fix[/dim]
"""


class HelpScreen(ModalScreen[None]):
    """Help modal showing keybindings."""

    BINDINGS = [
        Binding("escape", "dismiss", "Close"),
        Binding("q", "dismiss", "Close"),
        Binding("?", "dismiss", "Close"),
    ]

    DEFAULT_CSS = """
    HelpScreen {
        align: center middle;
    }

    HelpScreen #dialog {
        width: 60;
        height: auto;
        max-height: 80%;
        padding: 1 2;
        background: $surface;
        border: round $surface-lighten-1;
    }

    HelpScreen #help-content {
        height: auto;
        max-height: 100%;
        padding: 1;
    }

    HelpScreen .dialog-hint {
        text-align: center;
        color: $text-disabled;
        margin-top: 1;
    }
    """

    def compose(self) -> ComposeResult:
        with Vertical(id="dialog"):
            with VerticalScroll(id="help-content"):
                yield Static(HELP_TEXT, markup=True)
            yield Static("press q or esc to close", classes="dialog-hint")

    def action_dismiss(self) -> None:
        """Close help screen."""
        self.app.pop_screen()
