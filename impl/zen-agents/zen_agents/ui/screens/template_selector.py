"""TemplateSelectorModal: Quick-create sessions from templates."""

from dataclasses import dataclass
from pathlib import Path

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Vertical, Horizontal
from textual.widgets import Static, Input

from ...templates import SessionTemplate, get_templates
from ...types import SessionConfig
from ..events import NotificationRequest
from .base import ZenModalScreen


@dataclass
class TemplateResult:
    """Result from template selector."""
    selected: bool
    config: SessionConfig | None = None


class TemplateOption(Static):
    """A selectable template option."""

    DEFAULT_CSS = """
    TemplateOption {
        width: 100%;
        height: 2;
        padding: 0 1;
    }

    TemplateOption.selected {
        background: $surface-lighten-1;
    }

    TemplateOption:hover {
        background: $surface-lighten-1;
    }
    """

    def __init__(self, template: SessionTemplate, selected: bool = False) -> None:
        super().__init__()
        self.template = template
        if selected:
            self.add_class("selected")

    def render(self) -> str:
        t = self.template
        check = ">" if "selected" in self.classes else " "
        return f"{check} {t.icon}  {t.display_name}\n    [dim]{t.description}[/dim]"


class TemplateSelectorModal(ZenModalScreen[TemplateResult]):
    """Modal for creating a session from a template.

    Keybindings:
    - j/k: Navigate templates
    - Enter: Select template and create session
    - Escape: Cancel
    """

    BINDINGS = [
        Binding("escape", "cancel", "Cancel"),
        Binding("enter", "select", "Select"),
        Binding("j", "move_down", "Down", show=False),
        Binding("k", "move_up", "Up", show=False),
        Binding("down", "move_down", "Down", show=False),
        Binding("up", "move_up", "Up", show=False),
    ]

    DEFAULT_CSS = """
    TemplateSelectorModal {
        align: center middle;
    }

    TemplateSelectorModal #dialog {
        width: 60;
        height: auto;
        max-height: 85%;
        padding: 1 2;
        background: $surface;
        border: round $surface-lighten-1;
    }

    TemplateSelectorModal .dialog-title {
        text-align: center;
        width: 100%;
        margin-bottom: 1;
        color: $text-muted;
    }

    TemplateSelectorModal .field-label {
        margin-top: 1;
        color: $text-disabled;
    }

    TemplateSelectorModal Input {
        width: 100%;
    }

    TemplateSelectorModal .template-list {
        height: auto;
        max-height: 30;
        margin-top: 1;
        overflow-y: auto;
        border: round $surface-lighten-1;
    }

    TemplateSelectorModal .dialog-hint {
        text-align: center;
        color: $text-disabled;
        margin-top: 1;
    }
    """

    def __init__(self, working_dir: Path | None = None) -> None:
        super().__init__()
        self._working_dir = working_dir or Path.cwd()
        self._templates = get_templates()
        self._selected_index = 0

    def compose(self) -> ComposeResult:
        with Vertical(id="dialog"):
            yield Static("new from template", classes="dialog-title")

            yield Static("session name", classes="field-label")
            yield Input(placeholder="my-session", id="name-input")

            yield Static("template", classes="field-label")
            with Vertical(classes="template-list"):
                for i, t in enumerate(self._templates):
                    yield TemplateOption(t, selected=(i == 0))

            yield Static("j/k: navigate  enter: create  esc: cancel", classes="dialog-hint")

    def on_mount(self) -> None:
        self.query_one("#name-input", Input).focus()

    def action_cancel(self) -> None:
        self.dismiss(TemplateResult(selected=False))

    def action_select(self) -> None:
        name_input = self.query_one("#name-input", Input)
        name = name_input.value.strip()

        if not name:
            self.post_message(NotificationRequest("name required", "error"))
            name_input.focus()
            return

        template = self._templates[self._selected_index]
        config = template.to_config(
            name=name,
            working_dir=str(self._working_dir),
        )
        self.dismiss(TemplateResult(selected=True, config=config))

    def action_move_down(self) -> None:
        if self._selected_index < len(self._templates) - 1:
            self._selected_index += 1
            self._update_selection()

    def action_move_up(self) -> None:
        if self._selected_index > 0:
            self._selected_index -= 1
            self._update_selection()

    def _update_selection(self) -> None:
        for i, option in enumerate(self.query(TemplateOption)):
            if i == self._selected_index:
                option.add_class("selected")
            else:
                option.remove_class("selected")
