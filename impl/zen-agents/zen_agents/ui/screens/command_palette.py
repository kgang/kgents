"""Command palette for quick command access."""

from dataclasses import dataclass

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Vertical, VerticalScroll
from textual.screen import ModalScreen
from textual.widgets import Static, Input
from textual.reactive import reactive


@dataclass
class Command:
    """A command in the palette."""
    id: str
    name: str
    shortcut: str
    description: str


COMMANDS = [
    Command("new", "New Session", "n", "Create a new session"),
    Command("attach", "Attach", "a", "Attach to tmux session"),
    Command("pause", "Pause", "p", "Pause selected session"),
    Command("kill", "Kill", "x", "Kill selected session"),
    Command("clean", "Clean", "d", "Clean up dead session"),
    Command("revive", "Revive", "v", "Revive session"),
    Command("refresh", "Refresh", "r", "Refresh output"),
    Command("search", "Search", "/", "Search sessions"),
    Command("filter_claude", "Filter: Claude", "1", "Show Claude sessions"),
    Command("filter_shell", "Filter: Shell", "2", "Show Shell sessions"),
    Command("clear_filter", "Clear Filter", "0", "Show all sessions"),
    Command("help", "Help", "?", "Show help screen"),
    Command("quit", "Quit", "q", "Exit application"),
]


class CommandRow(Static):
    """A single command row in the palette."""

    DEFAULT_CSS = """
    CommandRow {
        width: 100%;
        height: 1;
        padding: 0 1;
    }

    CommandRow.selected {
        background: $surface-lighten-1;
    }

    CommandRow .shortcut {
        color: $text-disabled;
        width: 4;
    }

    CommandRow .name {
        color: $text;
    }
    """

    def __init__(self, command: Command, selected: bool = False) -> None:
        super().__init__()
        self.command = command
        if selected:
            self.add_class("selected")

    def render(self) -> str:
        return f"[dim]{self.command.shortcut:>3}[/dim]  {self.command.name}"


class CommandPaletteModal(ModalScreen[str | None]):
    """Command palette modal with fuzzy search."""

    BINDINGS = [
        Binding("escape", "dismiss", "Close"),
        Binding("enter", "select", "Select"),
        Binding("up", "move_up", "Up"),
        Binding("down", "move_down", "Down"),
        Binding("ctrl+p", "dismiss", "Close"),
    ]

    query: reactive[str] = reactive("")
    selected_index: reactive[int] = reactive(0)

    DEFAULT_CSS = """
    CommandPaletteModal {
        align: center top;
        padding-top: 3;
    }

    CommandPaletteModal #dialog {
        width: 50;
        height: auto;
        max-height: 60%;
        background: $surface;
        border: round $surface-lighten-1;
    }

    CommandPaletteModal #search-input {
        width: 100%;
        border: none;
        background: transparent;
        padding: 1 2;
        border-bottom: solid $surface-lighten-1;
    }

    CommandPaletteModal #search-input:focus {
        border: none;
        border-bottom: solid $surface-lighten-1;
    }

    CommandPaletteModal #commands {
        height: auto;
        max-height: 20;
        padding: 1 0;
    }

    CommandPaletteModal .empty {
        color: $text-disabled;
        padding: 1 2;
        text-align: center;
    }
    """

    def compose(self) -> ComposeResult:
        with Vertical(id="dialog"):
            yield Input(placeholder="Type to search commands...", id="search-input")
            yield VerticalScroll(id="commands")

    def on_mount(self) -> None:
        """Focus input and render commands."""
        self.query_one("#search-input", Input).focus()
        self._render_commands()

    def _get_filtered_commands(self) -> list[Command]:
        """Get commands filtered by query."""
        if not self.query:
            return COMMANDS
        q = self.query.lower()
        return [c for c in COMMANDS if q in c.name.lower() or q in c.description.lower()]

    def _render_commands(self) -> None:
        """Render the command list."""
        commands = self._get_filtered_commands()
        container = self.query_one("#commands", VerticalScroll)
        container.remove_children()

        if not commands:
            container.mount(Static("No matching commands", classes="empty"))
            return

        for i, cmd in enumerate(commands):
            container.mount(CommandRow(cmd, selected=(i == self.selected_index)))

    def on_input_changed(self, event: Input.Changed) -> None:
        """Handle search input changes."""
        if event.input.id == "search-input":
            self.query = event.value
            self.selected_index = 0
            self._render_commands()

    def action_move_up(self) -> None:
        """Move selection up."""
        commands = self._get_filtered_commands()
        if commands:
            self.selected_index = (self.selected_index - 1) % len(commands)
            self._render_commands()

    def action_move_down(self) -> None:
        """Move selection down."""
        commands = self._get_filtered_commands()
        if commands:
            self.selected_index = (self.selected_index + 1) % len(commands)
            self._render_commands()

    def action_select(self) -> None:
        """Select current command."""
        commands = self._get_filtered_commands()
        if commands and 0 <= self.selected_index < len(commands):
            self.dismiss(commands[self.selected_index].id)
        else:
            self.dismiss(None)

    def action_dismiss(self) -> None:
        """Close without selecting."""
        self.dismiss(None)
