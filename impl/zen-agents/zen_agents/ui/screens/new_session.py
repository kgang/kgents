"""NewSessionModal: Create new sessions via NewSessionPipeline."""

from dataclasses import dataclass
from pathlib import Path

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Vertical, Horizontal
from textual.widgets import Static, Input, Select, Button

from ...types import SessionConfig, SessionType
from ...ground import ZenGround, zen_ground
from ..events import NotificationRequest
from .base import ZenModalScreen


@dataclass
class NewSessionResult:
    """Result returned from NewSessionModal."""
    created: bool
    config: SessionConfig | None = None
    error: str | None = None


class SessionTypeOption(Static):
    """A selectable session type option."""

    DEFAULT_CSS = """
    SessionTypeOption {
        width: 100%;
        height: 1;
        padding: 0 1;
    }

    SessionTypeOption.selected {
        background: $surface-lighten-1;
    }

    SessionTypeOption:hover {
        background: $surface-lighten-1;
    }
    """

    def __init__(self, session_type: SessionType, selected: bool = False) -> None:
        super().__init__()
        self.session_type = session_type
        if selected:
            self.add_class("selected")

    def render(self) -> str:
        icons = {
            SessionType.CLAUDE: ">>>",
            SessionType.SHELL: "$",
            SessionType.CODEX: "cx",
            SessionType.GEMINI: "gm",
            SessionType.CUSTOM: "*",
        }
        icon = icons.get(self.session_type, "?")
        return f"  {icon}  {self.session_type.value}"


class NewSessionModal(ZenModalScreen[NewSessionResult]):
    """Modal for creating a new session.

    Integrates with:
    - ZenGround: Get working directory default
    - NewSessionPipeline: Execute creation
    - SessionConflictPipeline: Handle conflicts

    Keybindings:
    - Tab/Shift+Tab: Navigate fields
    - j/k: Select session type
    - Enter: Create session
    - Escape: Cancel
    """

    BINDINGS = [
        Binding("escape", "cancel", "Cancel"),
        Binding("enter", "create", "Create", show=False),
        Binding("j", "type_down", "Down", show=False),
        Binding("k", "type_up", "Up", show=False),
        Binding("down", "type_down", "Down", show=False),
        Binding("up", "type_up", "Up", show=False),
    ]

    DEFAULT_CSS = """
    NewSessionModal {
        align: center middle;
    }

    NewSessionModal #dialog {
        width: 60;
        height: auto;
        max-height: 80%;
        padding: 1 2;
        background: $surface;
        border: round $surface-lighten-1;
    }

    NewSessionModal .dialog-title {
        text-align: center;
        width: 100%;
        margin-bottom: 1;
        color: $text-muted;
    }

    NewSessionModal .field-label {
        margin-top: 1;
        color: $text-disabled;
    }

    NewSessionModal Input {
        margin-top: 0;
        width: 100%;
    }

    NewSessionModal .type-list {
        height: auto;
        max-height: 10;
        margin-top: 0;
        border: round $surface-lighten-1;
    }

    NewSessionModal .dialog-hint {
        text-align: center;
        color: $text-disabled;
        margin-top: 1;
    }

    NewSessionModal #buttons {
        margin-top: 1;
        height: 3;
        align: center middle;
    }

    NewSessionModal Button {
        margin: 0 1;
    }
    """

    def __init__(
        self,
        ground: ZenGround | None = None,
        working_dir: Path | None = None,
    ) -> None:
        super().__init__()
        self._ground = ground or zen_ground
        self._working_dir = working_dir or Path.cwd()
        self._selected_type_index = 0
        self._session_types = list(SessionType)

    def compose(self) -> ComposeResult:
        with Vertical(id="dialog"):
            yield Static("new session", classes="dialog-title")

            yield Static("name", classes="field-label")
            yield Input(placeholder="session name", id="name-input")

            yield Static("type", classes="field-label")
            with Vertical(classes="type-list"):
                for i, st in enumerate(self._session_types):
                    yield SessionTypeOption(st, selected=(i == 0))

            yield Static("working directory", classes="field-label")
            yield Input(
                value=str(self._working_dir),
                placeholder="/path/to/project",
                id="workdir-input",
            )

            with Horizontal(id="buttons"):
                yield Button("Create", variant="primary", id="create-btn")
                yield Button("Cancel", id="cancel-btn")

            yield Static("tab: next field  j/k: type  enter: create", classes="dialog-hint")

    def on_mount(self) -> None:
        """Focus the name input on mount."""
        self.query_one("#name-input", Input).focus()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "create-btn":
            self._do_create()
        elif event.button.id == "cancel-btn":
            self.dismiss(NewSessionResult(created=False))

    def action_cancel(self) -> None:
        """Cancel and dismiss."""
        self.dismiss(NewSessionResult(created=False))

    def action_create(self) -> None:
        """Create the session."""
        self._do_create()

    def action_type_down(self) -> None:
        """Move type selection down."""
        if self._selected_type_index < len(self._session_types) - 1:
            self._selected_type_index += 1
            self._update_type_selection()

    def action_type_up(self) -> None:
        """Move type selection up."""
        if self._selected_type_index > 0:
            self._selected_type_index -= 1
            self._update_type_selection()

    def _update_type_selection(self) -> None:
        """Update the visual selection of session types."""
        for i, option in enumerate(self.query(SessionTypeOption)):
            if i == self._selected_type_index:
                option.add_class("selected")
            else:
                option.remove_class("selected")

    def _do_create(self) -> None:
        """Validate and create the session."""
        name_input = self.query_one("#name-input", Input)
        workdir_input = self.query_one("#workdir-input", Input)

        name = name_input.value.strip()
        working_dir = workdir_input.value.strip()

        # Validate name
        if not name:
            self.post_message(NotificationRequest("name required", "error"))
            name_input.focus()
            return

        # Validate working directory
        if working_dir and not Path(working_dir).exists():
            self.post_message(NotificationRequest("directory not found", "warning"))

        # Build config
        config = SessionConfig(
            name=name,
            session_type=self._session_types[self._selected_type_index],
            working_dir=working_dir if working_dir else None,
        )

        self.dismiss(NewSessionResult(created=True, config=config))
