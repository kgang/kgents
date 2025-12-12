"""
Help Overlay - Contextual keyboard shortcut reference.

Shows all available keybindings in a modal overlay.

Trigger: Press '?' key
Navigation: Escape to close
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container, Vertical
from textual.screen import ModalScreen
from textual.widgets import Static

if TYPE_CHECKING:
    pass


# All keybindings organized by category
KEYBINDINGS = {
    "Navigation": [
        ("h / Left", "Move left"),
        ("j / Down", "Move down"),
        ("k / Up", "Move up"),
        ("l / Right", "Move right"),
        ("Enter", "Focus agent"),
        ("Escape", "Zoom out / Back"),
        ("Tab", "Next agent"),
        ("Shift+Tab", "Previous agent"),
    ],
    "Overlays": [
        ("w", "WIRE overlay (event stream)"),
        ("b", "BODY overlay (proprioception)"),
        ("p", "Psi-gent insight"),
    ],
    "Actions": [
        ("g", "Trigger glitch"),
        ("/", "Search (L-gent)"),
        ("r", "Refresh data"),
        ("?", "Show this help"),
        ("q", "Quit"),
    ],
    "Within Overlays": [
        ("j / k", "Scroll up/down"),
        ("f", "Toggle follow mode"),
        ("e", "Export to markdown"),
        ("Escape", "Close overlay"),
    ],
}


class HelpOverlay(ModalScreen[None]):
    """
    Help overlay showing all keybindings.

    Press ? to open, Escape to close.
    """

    CSS = """
    HelpOverlay {
        align: center middle;
    }

    HelpOverlay #help-container {
        width: 60;
        height: auto;
        max-height: 80%;
        border: solid #4a4a5c;
        background: #1a1a1a;
        padding: 1;
    }

    HelpOverlay #help-header {
        height: 1;
        color: #f5f0e6;
        text-style: bold;
        text-align: center;
        margin-bottom: 1;
    }

    HelpOverlay .help-category {
        color: #e6a352;
        text-style: bold;
        margin-top: 1;
    }

    HelpOverlay .help-item {
        color: #b3a89a;
    }

    HelpOverlay .help-key {
        color: #8b7ba5;
    }

    HelpOverlay #help-footer {
        height: 1;
        color: #6a6560;
        text-align: center;
        margin-top: 1;
        border-top: solid #4a4a5c;
        padding-top: 1;
    }
    """

    BINDINGS = [
        Binding("escape", "dismiss", "Close", show=True),
        Binding("question_mark", "dismiss", "Close", show=False),
    ]

    def compose(self) -> ComposeResult:
        """Compose the help overlay."""
        with Container(id="help-container"):
            yield Static("[ KGENTS FLUX HELP ]", id="help-header")

            with Vertical(id="help-content"):
                for category, bindings in KEYBINDINGS.items():
                    yield Static(f"[{category}]", classes="help-category")
                    for key, description in bindings:
                        # Format: key (padded) - description
                        yield Static(
                            f"  {key:14} {description}",
                            classes="help-item",
                        )

            yield Static("Press [Escape] or [?] to close", id="help-footer")

    async def action_dismiss(self, result: None = None) -> None:
        """Dismiss the overlay."""
        self.dismiss()
