"""
ConfirmWidget: Binary confirm/deny prompt.

Used for yes/no decisions, with support for destructive action warnings
and typed confirmation requirements.

Example:
    widget = ConfirmWidget(ConfirmWidgetState(
        message="Delete all data?",
        destructive=True,
        requires_type_confirm="DELETE"
    ))
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from agents.i.reactive.signal import Signal
from agents.i.reactive.widget import KgentsWidget, RenderTarget


@dataclass(frozen=True)
class ConfirmWidgetState:
    """
    Immutable confirm widget state.

    Attributes:
        message: The confirmation message
        confirm_label: Label for confirm button
        cancel_label: Label for cancel button
        destructive: Whether this is a destructive action (red styling)
        requires_type_confirm: Text user must type to confirm (None = no typing required)
    """

    message: str
    confirm_label: str = "Confirm"
    cancel_label: str = "Cancel"
    destructive: bool = False
    requires_type_confirm: str | None = None


class ConfirmWidget(KgentsWidget[ConfirmWidgetState]):
    """
    Binary confirmation widget.

    Projections:
        - CLI: Question with [y/n] or type-to-confirm prompt
        - TUI: Textual Buttons or Input
        - MARIMO: HTML with buttons or input
        - JSON: State dict for API responses
    """

    def __init__(self, state: ConfirmWidgetState | None = None) -> None:
        self.state = Signal.of(state or ConfirmWidgetState(message="Confirm?"))

    def project(self, target: RenderTarget) -> Any:
        """Project confirm to target surface."""
        match target:
            case RenderTarget.CLI:
                return self._to_cli()
            case RenderTarget.TUI:
                return self._to_tui()
            case RenderTarget.MARIMO:
                return self._to_marimo()
            case RenderTarget.JSON:
                return self._to_json()

    def _to_cli(self) -> str:
        """CLI projection: question with prompt."""
        s = self.state.value
        lines = []

        if s.destructive:
            lines.append("!!! WARNING: DESTRUCTIVE ACTION !!!")

        lines.append(s.message)

        if s.requires_type_confirm:
            lines.append(f'Type "{s.requires_type_confirm}" to confirm:')
        else:
            lines.append(
                f"[{s.confirm_label[0].lower()}] {s.confirm_label} / "
                f"[{s.cancel_label[0].lower()}] {s.cancel_label}"
            )

        return "\n".join(lines)

    def _to_tui(self) -> Any:
        """TUI projection: Textual confirmation dialog."""
        try:
            from textual.containers import Horizontal
            from textual.widgets import Button, Input, Label, Static

            s = self.state.value

            class ConfirmDialog:
                """Pseudo-widget for TUI confirmation."""

                def __init__(self, state: ConfirmWidgetState) -> None:
                    self.state = state

                def compose(self):
                    yield Static(state.message)
                    if state.requires_type_confirm:
                        yield Input(placeholder=f"Type '{state.requires_type_confirm}'")
                    with Horizontal():
                        variant = "error" if state.destructive else "primary"
                        yield Button(state.confirm_label, variant=variant)
                        yield Button(state.cancel_label, variant="default")

            return ConfirmDialog(s)
        except ImportError:
            from rich.text import Text

            return Text(self._to_cli())

    def _to_marimo(self) -> str:
        """MARIMO projection: HTML with buttons."""
        s = self.state.value

        warning_class = "kgents-confirm-destructive" if s.destructive else ""
        confirm_class = "kgents-btn-danger" if s.destructive else "kgents-btn-primary"

        html = f'<div class="kgents-confirm {warning_class}">'
        html += f'<p class="kgents-confirm-message">{s.message}</p>'

        if s.requires_type_confirm:
            html += f"""
            <input type="text" class="kgents-confirm-input"
                   placeholder="Type '{s.requires_type_confirm}' to confirm" />
            """

        html += f"""
        <div class="kgents-confirm-buttons">
            <button class="{confirm_class}">{s.confirm_label}</button>
            <button class="kgents-btn-secondary">{s.cancel_label}</button>
        </div>
        </div>
        """
        return html

    def _to_json(self) -> dict[str, Any]:
        """JSON projection: state dict for API responses."""
        s = self.state.value
        return {
            "type": "confirm",
            "message": s.message,
            "confirmLabel": s.confirm_label,
            "cancelLabel": s.cancel_label,
            "destructive": s.destructive,
            "requiresTypeConfirm": s.requires_type_confirm,
        }


__all__ = ["ConfirmWidget", "ConfirmWidgetState"]
