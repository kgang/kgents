"""
Dawn Cockpit Add Focus Modal: Modal for adding new focus items.

A simple modal that captures:
- Target (file path or AGENTESE path)
- Label (optional, inferred from target if not provided)
- Bucket (today/week/someday)

Layout:
    ┌─────────────────────────────────────────┐
    │  ADD FOCUS ITEM                         │
    │  ═══════════════                        │
    │                                         │
    │  Target: [________________________]     │
    │  Label:  [________________________]     │
    │  Bucket: [▼ today________________]     │
    │                                         │
    │        [Cancel]    [Add]               │
    └─────────────────────────────────────────┘

Key Bindings:
    Escape   Cancel and close modal
    Enter    Submit (when on Add button)

See: spec/protocols/dawn-cockpit.md
"""

from __future__ import annotations

from typing import Any

from textual.containers import Horizontal, Vertical
from textual.events import Key
from textual.screen import ModalScreen
from textual.widgets import Button, Input, Select, Static

from ..focus import Bucket


class AddFocusModal(ModalScreen[tuple[str, str, str] | None]):
    """
    Modal for adding a new focus item.

    Returns:
        tuple[target, label, bucket_value] on Add
        None on Cancel/Escape

    Teaching:
        gotcha: ModalScreen requires a result type parameter. The dismiss()
                method takes the result value, which is returned to the
                callback in push_screen().
                (Evidence: Textual docs on ModalScreen)
    """

    BINDINGS = [
        ("escape", "cancel", "Cancel"),
    ]
    # Note: Tab/Shift+Tab handled in on_key to prevent bubbling to parent app

    CSS = """
    AddFocusModal {
        align: center middle;
    }

    #modal-container {
        width: 50;
        height: auto;
        max-height: 24;
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

    Select {
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
            yield Static("ADD FOCUS ITEM", id="modal-title")
            yield Static("═" * 30, classes="modal-separator")
            yield Static("Target (file path or AGENTESE):", classes="modal-label")
            yield Input(placeholder="e.g., plans/my-plan.md", id="target-input")
            yield Static("Label (optional):", classes="modal-label")
            yield Input(placeholder="e.g., Portal Phase 4", id="label-input")
            yield Static("Bucket:", classes="modal-label")
            yield Select(
                [(b.value.capitalize(), b.value) for b in Bucket],
                value=Bucket.TODAY.value,
                id="bucket-select",
            )
            with Horizontal(id="button-row"):
                yield Button("Cancel", id="cancel-btn", variant="default")
                yield Button("Add", id="add-btn", variant="primary")

    def on_mount(self) -> None:
        """Focus the first input on mount."""
        self.query_one("#target-input", Input).focus()

    def action_cancel(self) -> None:
        """Cancel and close modal."""
        self.dismiss(None)

    def _submit(self) -> None:
        """Submit the form if valid."""
        target = self.query_one("#target-input", Input).value.strip()
        label = self.query_one("#label-input", Input).value.strip()
        bucket = self.query_one("#bucket-select", Select).value

        # Validate target is provided
        if not target:
            # Focus the input and provide feedback
            target_input = self.query_one("#target-input", Input)
            target_input.focus()
            return

        self.dismiss((target, label, str(bucket)))

    def _get_focusable(self) -> list[Any]:
        """Get list of focusable widgets in the modal."""
        return list(self.query("Input, Select, Button"))

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
            event.stop()
            self._submit()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "add-btn":
            self._submit()
        else:
            self.dismiss(None)


__all__ = [
    "AddFocusModal",
]
