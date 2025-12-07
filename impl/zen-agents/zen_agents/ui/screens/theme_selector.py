"""ThemeSelectorModal: Pick a color theme."""

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Vertical
from textual.widgets import Static

from ..styles import ThemeName, THEMES, get_theme
from .base import ZenModalScreen


class ThemeOption(Static):
    """A selectable theme option with preview."""

    DEFAULT_CSS = """
    ThemeOption {
        width: 100%;
        height: 3;
        padding: 0 2;
        margin: 0;
    }

    ThemeOption.selected {
        background: $surface-lighten-1;
    }

    ThemeOption:hover {
        background: $surface-lighten-1;
    }

    ThemeOption .preview {
        height: 1;
    }
    """

    def __init__(self, theme_name: ThemeName, selected: bool = False) -> None:
        super().__init__()
        self.theme_name = theme_name
        self._theme = get_theme(theme_name)
        if selected:
            self.add_class("selected")

    def render(self) -> str:
        t = self._theme
        # Show theme name and color swatches
        check = ">" if "selected" in self.classes else " "
        return f"{check} {t.display_name:<15} [on {t.background}]  [/][on {t.primary}]  [/][on {t.success}]  [/][on {t.warning}]  [/][on {t.error}]  [/]"


class ThemeSelectorModal(ZenModalScreen[ThemeName | None]):
    """Modal for selecting a color theme.

    Keybindings:
    - j/k: Navigate themes
    - Enter: Select theme
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
    ThemeSelectorModal {
        align: center middle;
    }

    ThemeSelectorModal #dialog {
        width: 50;
        height: auto;
        max-height: 80%;
        padding: 1 2;
        background: $surface;
        border: round $surface-lighten-1;
    }

    ThemeSelectorModal .dialog-title {
        text-align: center;
        width: 100%;
        margin-bottom: 1;
        color: $text-muted;
    }

    ThemeSelectorModal .theme-list {
        height: auto;
        max-height: 20;
        margin-top: 1;
    }

    ThemeSelectorModal .dialog-hint {
        text-align: center;
        color: $text-disabled;
        margin-top: 1;
    }
    """

    def __init__(self, current: ThemeName | None = None) -> None:
        super().__init__()
        self._theme_names = list(THEMES.keys())
        self._selected_index = 0
        if current and current in self._theme_names:
            self._selected_index = self._theme_names.index(current)

    def compose(self) -> ComposeResult:
        with Vertical(id="dialog"):
            yield Static("select theme", classes="dialog-title")

            with Vertical(classes="theme-list"):
                for i, name in enumerate(self._theme_names):
                    yield ThemeOption(name, selected=(i == self._selected_index))

            yield Static("j/k: navigate  enter: select  esc: cancel", classes="dialog-hint")

    def action_cancel(self) -> None:
        self.dismiss(None)

    def action_select(self) -> None:
        self.dismiss(self._theme_names[self._selected_index])

    def action_move_down(self) -> None:
        if self._selected_index < len(self._theme_names) - 1:
            self._selected_index += 1
            self._update_selection()

    def action_move_up(self) -> None:
        if self._selected_index > 0:
            self._selected_index -= 1
            self._update_selection()

    def _update_selection(self) -> None:
        for i, option in enumerate(self.query(ThemeOption)):
            if i == self._selected_index:
                option.add_class("selected")
            else:
                option.remove_class("selected")
