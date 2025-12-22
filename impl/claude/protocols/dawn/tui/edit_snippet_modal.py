"""
Dawn Cockpit Edit Snippet Modal: Modal for editing custom snippets.

A modal that allows editing:
- Label
- Content

Layout:
    ┌─────────────────────────────────────────┐
    │  EDIT SNIPPET                           │
    │  ═══════════════                        │
    │                                         │
    │  Label:   [________________________]    │
    │  Content: [________________________]    │
    │           [________________________]    │
    │           [________________________]    │
    │                                         │
    │        [Cancel]    [Save]               │
    └─────────────────────────────────────────┘

Key Bindings:
    Escape   Cancel and close modal
    Enter    Submit (from any field)
    Tab      Cycle through fields

See: spec/protocols/dawn-cockpit.md
"""

from __future__ import annotations

from typing import Any

from textual.containers import Horizontal, Vertical
from textual.events import Key
from textual.screen import ModalScreen
from textual.widgets import Button, Input, Static, TextArea

from ..snippets import Snippet


class EditSnippetModal(ModalScreen[tuple[str, str] | None]):
    """
    Modal for editing an existing custom snippet.

    Returns:
        tuple[label, content] on Save
        None on Cancel/Escape

    Teaching:
        gotcha: Only custom snippets can be edited. Static and Query
                snippets are configured at startup and should not be
                modified through the UI.
                (Evidence: spec/protocols/dawn-cockpit.md)
    """

    BINDINGS = [
        ("escape", "cancel", "Cancel"),
    ]
    # Note: Tab/Shift+Tab handled in on_key to prevent bubbling to parent app

    CSS = """
    EditSnippetModal {
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

    def __init__(self, snippet: Snippet, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._snippet = snippet
        self._snippet_dict = snippet.to_dict()

    def compose(self) -> Any:
        """Compose the modal content."""
        with Vertical(id="modal-container"):
            yield Static("EDIT SNIPPET", id="modal-title")
            yield Static("═" * 40, classes="modal-separator")
            yield Static("Label:", classes="modal-label")
            yield Input(
                value=self._snippet_dict.get("label", ""),
                placeholder="Snippet label",
                id="label-input",
            )
            yield Static("Content:", classes="modal-label")
            yield TextArea(
                self._snippet_dict.get("content", ""),
                id="content-input",
            )
            with Horizontal(id="button-row"):
                yield Button("Cancel", id="cancel-btn", variant="default")
                yield Button("Save", id="save-btn", variant="primary")

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
        """
        Handle keyboard events for the modal.

        Tab/Shift+Tab cycle through modal widgets (must stop propagation
        to prevent parent app from switching panes).

        Enter submits from Input only (TextArea needs newlines).

        Teaching:
            gotcha: Binding Tab in BINDINGS isn't enough — the event still
                    bubbles to the parent app. Handle in on_key with event.stop()
                    to fully capture the key within the modal.
                    (Evidence: User report of Tab switching underlying panels)
        """
        if event.key == "tab":
            event.stop()
            event.prevent_default()
            self.action_focus_next_in_modal()
        elif event.key == "shift+tab":
            event.stop()
            event.prevent_default()
            self.action_focus_prev_in_modal()
        elif event.key == "enter":
            focused = self.focused
            if isinstance(focused, Input):
                event.stop()
                self._submit()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "save-btn":
            self._submit()
        else:
            self.dismiss(None)


__all__ = [
    "EditSnippetModal",
]
