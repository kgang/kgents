"""
Dawn Cockpit Add Snippet Modal: Modal for adding new custom snippets.

A modal that captures:
- Label
- Content

Layout:
    ┌─────────────────────────────────────────┐
    │  NEW SNIPPET                            │
    │  ═══════════════                        │
    │                                         │
    │  Label:   [________________________]    │
    │  Content: [________________________]    │
    │           [________________________]    │
    │                                         │
    │        [Cancel]    [Add]                │
    └─────────────────────────────────────────┘

Key Bindings:
    Escape   Cancel and close modal
    Enter    Submit (from label input)
    Tab      Cycle through fields

See: spec/protocols/dawn-cockpit.md
"""

from __future__ import annotations

from typing import Any

from textual.containers import Horizontal, Vertical
from textual.events import Key
from textual.screen import ModalScreen
from textual.widgets import Button, Input, Static, TextArea


class AddSnippetModal(ModalScreen[tuple[str, str] | None]):
    """
    Modal for adding a new custom snippet.

    Returns:
        tuple[label, content] on Add
        None on Cancel/Escape
    """

    BINDINGS = [
        ("escape", "cancel", "Cancel"),
        ("tab", "focus_next_in_modal", "Next"),
        ("shift+tab", "focus_prev_in_modal", "Prev"),
    ]

    CSS = """
    AddSnippetModal {
        align: center middle;
    }

    #modal-container {
        width: 60;
        height: auto;
        max-height: 20;
        border: thick $primary;
        background: $surface;
        padding: 1 2;
        overflow-y: auto;
    }

    #modal-title {
        text-align: center;
        text-style: bold;
        padding-bottom: 1;
    }

    .modal-separator {
        margin-bottom: 1;
    }

    .modal-label {
        padding: 0 0 0 0;
        margin-bottom: 0;
    }

    Input {
        margin-bottom: 1;
    }

    #content-input {
        height: 5;
        margin-bottom: 1;
    }

    #button-row {
        align: center middle;
        padding-top: 1;
    }

    #button-row Button {
        margin: 0 1;
    }
    """

    def compose(self) -> Any:
        """Compose the modal content."""
        with Vertical(id="modal-container"):
            yield Static("NEW SNIPPET", id="modal-title")
            yield Static("═" * 40, classes="modal-separator")
            yield Static("Label:", classes="modal-label")
            yield Input(
                placeholder="e.g., My Note",
                id="label-input",
            )
            yield Static("Content:", classes="modal-label")
            yield TextArea(
                "",
                id="content-input",
            )
            with Horizontal(id="button-row"):
                yield Button("Cancel", id="cancel-btn", variant="default")
                yield Button("Add", id="add-btn", variant="primary")

    def on_mount(self) -> None:
        """Focus the label input on mount."""
        self.query_one("#label-input", Input).focus()

    def action_cancel(self) -> None:
        """Cancel and close modal."""
        self.dismiss(None)

    def _submit(self) -> None:
        """Submit the form if valid."""
        label = self.query_one("#label-input", Input).value.strip()
        content = self.query_one("#content-input", TextArea).text.strip()

        # Validate - both required
        if not label:
            self.query_one("#label-input", Input).focus()
            return
        if not content:
            self.query_one("#content-input", TextArea).focus()
            return

        self.dismiss((label, content))

    def _get_focusable(self) -> list[Any]:
        """Get list of focusable widgets in the modal."""
        return list(self.query("Input, TextArea, Button"))

    def action_focus_next_in_modal(self) -> None:
        """Cycle focus to next widget in modal."""
        focusable = self._get_focusable()
        if not focusable:
            return
        try:
            current = self.focused
            if current in focusable:
                idx = focusable.index(current)
                next_idx = (idx + 1) % len(focusable)
            else:
                next_idx = 0
            focusable[next_idx].focus()
        except Exception:
            focusable[0].focus()

    def action_focus_prev_in_modal(self) -> None:
        """Cycle focus to previous widget in modal."""
        focusable = self._get_focusable()
        if not focusable:
            return
        try:
            current = self.focused
            if current in focusable:
                idx = focusable.index(current)
                prev_idx = (idx - 1) % len(focusable)
            else:
                prev_idx = len(focusable) - 1
            focusable[prev_idx].focus()
        except Exception:
            focusable[-1].focus()

    def on_key(self, event: Key) -> None:
        """Handle Enter key - submit from Input only (TextArea needs newlines)."""
        if event.key == "enter":
            focused = self.focused
            if isinstance(focused, Input):
                event.stop()
                self._submit()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "add-btn":
            self._submit()
        else:
            self.dismiss(None)


__all__ = [
    "AddSnippetModal",
]
