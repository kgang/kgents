"""ConflictModal: Resolve session conflicts via Contradict/Sublate pipeline."""

from dataclasses import dataclass

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Vertical, Horizontal, VerticalScroll
from textual.widgets import Static, Button

from ...conflicts import (
    SessionConflict,
    ConflictResolution,
    ConflictPipelineResult,
    ConflictType,
)
from ...types import SessionConfig
from ..events import NotificationRequest
from .base import ZenModalScreen


@dataclass
class ConflictModalResult:
    """Result from conflict resolution modal."""
    resolved: bool
    final_config: SessionConfig | None = None
    action: str = "cancel"  # "resolve", "rename", "cancel", "force"


class ConflictItem(Static):
    """Display a single conflict with resolution options."""

    DEFAULT_CSS = """
    ConflictItem {
        width: 100%;
        height: auto;
        padding: 1;
        margin-bottom: 1;
        background: $surface;
        border: round $surface-lighten-1;
    }

    ConflictItem .conflict-type {
        color: $warning;
    }

    ConflictItem .conflict-desc {
        margin-top: 0;
        color: $text;
    }

    ConflictItem .conflict-suggestion {
        margin-top: 0;
        color: $text-muted;
    }

    ConflictItem.unresolvable {
        border: round $error-darken-2;
    }

    ConflictItem.unresolvable .conflict-type {
        color: $error;
    }
    """

    def __init__(self, conflict: SessionConflict, resolution: ConflictResolution | None = None) -> None:
        super().__init__()
        self.conflict = conflict
        self.resolution = resolution
        if not conflict.resolvable:
            self.add_class("unresolvable")

    def compose(self) -> ComposeResult:
        type_icons = {
            ConflictType.NAME_COLLISION: "!!",
            ConflictType.PORT_CONFLICT: "@@",
            ConflictType.WORKTREE_CONFLICT: "//",
            ConflictType.RESOURCE_LIMIT: "##",
        }
        icon = type_icons.get(self.conflict.conflict_type, "??")
        type_label = self.conflict.conflict_type.replace("_", " ")

        yield Static(f"{icon} {type_label}", classes="conflict-type")
        yield Static(self.conflict.description, classes="conflict-desc")

        if self.resolution:
            status = "resolved" if self.resolution.resolved else "held"
            yield Static(f"  {status}: {self.resolution.message}", classes="conflict-suggestion")
        elif self.conflict.suggested_resolution:
            yield Static(f"  suggestion: {self.conflict.suggested_resolution}", classes="conflict-suggestion")


class ConflictModal(ZenModalScreen[ConflictModalResult]):
    """Modal for displaying and resolving session conflicts.

    Shows conflicts detected by SessionContradict and offers
    resolution options via SessionSublate.

    Keybindings:
    - Enter/r: Accept auto-resolution
    - f: Force create (ignore resolvable conflicts)
    - Escape: Cancel
    """

    BINDINGS = [
        Binding("escape", "cancel", "Cancel"),
        Binding("enter", "accept", "Accept", show=False),
        Binding("r", "accept", "Accept"),
        Binding("f", "force", "Force"),
    ]

    DEFAULT_CSS = """
    ConflictModal {
        align: center middle;
    }

    ConflictModal #dialog {
        width: 70;
        height: auto;
        max-height: 80%;
        padding: 1 2;
        background: $surface;
        border: round $warning-darken-2;
    }

    ConflictModal .dialog-title {
        text-align: center;
        width: 100%;
        margin-bottom: 1;
        color: $warning;
    }

    ConflictModal .conflict-summary {
        text-align: center;
        color: $text-muted;
        margin-bottom: 1;
    }

    ConflictModal .conflict-list {
        height: auto;
        max-height: 50vh;
        padding: 0 1;
    }

    ConflictModal .dialog-hint {
        text-align: center;
        color: $text-disabled;
        margin-top: 1;
    }

    ConflictModal #buttons {
        margin-top: 1;
        height: 3;
        align: center middle;
    }

    ConflictModal Button {
        margin: 0 1;
    }

    ConflictModal Button#force-btn {
        background: $error-darken-2;
    }
    """

    def __init__(
        self,
        pipeline_result: ConflictPipelineResult,
        original_config: SessionConfig,
    ) -> None:
        super().__init__()
        self._result = pipeline_result
        self._original_config = original_config

    def compose(self) -> ComposeResult:
        n = len(self._result.conflicts)
        can_proceed = self._result.can_proceed

        with Vertical(id="dialog"):
            title = "conflicts detected" if n > 1 else "conflict detected"
            yield Static(title, classes="dialog-title")

            if can_proceed:
                yield Static(
                    f"{n} conflict(s) found - auto-resolution available",
                    classes="conflict-summary"
                )
            else:
                yield Static(
                    f"{n} conflict(s) found - manual action required",
                    classes="conflict-summary"
                )

            with VerticalScroll(classes="conflict-list"):
                for conflict, resolution in zip(
                    self._result.conflicts,
                    self._result.resolutions
                ):
                    yield ConflictItem(conflict, resolution)

            with Horizontal(id="buttons"):
                if can_proceed:
                    yield Button("Accept Resolution", variant="primary", id="accept-btn")
                yield Button("Cancel", id="cancel-btn")
                # Force only for resolvable conflicts
                if all(c.resolvable for c in self._result.conflicts):
                    yield Button("Force", variant="error", id="force-btn")

            hint = "r: accept  esc: cancel"
            if all(c.resolvable for c in self._result.conflicts):
                hint += "  f: force"
            yield Static(hint, classes="dialog-hint")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        match event.button.id:
            case "accept-btn":
                self._do_accept()
            case "cancel-btn":
                self.dismiss(ConflictModalResult(resolved=False, action="cancel"))
            case "force-btn":
                self._do_force()

    def action_cancel(self) -> None:
        """Cancel and dismiss."""
        self.dismiss(ConflictModalResult(resolved=False, action="cancel"))

    def action_accept(self) -> None:
        """Accept the auto-resolution."""
        if self._result.can_proceed:
            self._do_accept()
        else:
            self.post_message(NotificationRequest("cannot auto-resolve", "error"))

    def action_force(self) -> None:
        """Force create despite conflicts."""
        if all(c.resolvable for c in self._result.conflicts):
            self._do_force()
        else:
            self.post_message(NotificationRequest("unresolvable conflicts", "error"))

    def _do_accept(self) -> None:
        """Accept resolution and return final config."""
        self.dismiss(ConflictModalResult(
            resolved=True,
            final_config=self._result.final_config,
            action="resolve",
        ))

    def _do_force(self) -> None:
        """Force create with original config."""
        self.dismiss(ConflictModalResult(
            resolved=True,
            final_config=self._original_config,
            action="force",
        ))
