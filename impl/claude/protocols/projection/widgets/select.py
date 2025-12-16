"""
SelectWidget: Single and multi-select dropdown.

Supports single selection, multi-selection, and searchable options.

Example:
    widget = SelectWidget(SelectWidgetState(
        options=(
            SelectOption(value="a", label="Option A"),
            SelectOption(value="b", label="Option B"),
        ),
        selected=("a",),
        multiple=False,
    ))
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from agents.i.reactive.signal import Signal
from agents.i.reactive.widget import KgentsWidget, RenderTarget


@dataclass(frozen=True)
class SelectOption:
    """
    Single option in a select widget.

    Attributes:
        value: Internal value (sent to server)
        label: Display label
        description: Optional help text
        disabled: Whether option is selectable
        icon: Optional icon identifier
    """

    value: str
    label: str
    description: str | None = None
    disabled: bool = False
    icon: str | None = None


@dataclass(frozen=True)
class SelectWidgetState:
    """
    Immutable select widget state.

    Attributes:
        options: Available options
        selected: Currently selected value(s)
        placeholder: Placeholder text when nothing selected
        multiple: Allow multiple selections
        searchable: Enable search/filter
        max_selections: Max selections for multi-select (None = unlimited)
    """

    options: tuple[SelectOption, ...]
    selected: tuple[str, ...] = ()
    placeholder: str = "Select..."
    multiple: bool = False
    searchable: bool = False
    max_selections: int | None = None

    def with_selected(self, values: tuple[str, ...]) -> SelectWidgetState:
        """Return new state with updated selection."""
        return SelectWidgetState(
            options=self.options,
            selected=values,
            placeholder=self.placeholder,
            multiple=self.multiple,
            searchable=self.searchable,
            max_selections=self.max_selections,
        )

    @property
    def selected_labels(self) -> tuple[str, ...]:
        """Get labels for selected options."""
        value_to_label = {opt.value: opt.label for opt in self.options}
        return tuple(value_to_label.get(v, v) for v in self.selected)


class SelectWidget(KgentsWidget[SelectWidgetState]):
    """
    Select dropdown widget.

    Projections:
        - CLI: Numbered list with [x] markers for selected
        - TUI: Textual Select or SelectionList
        - MARIMO: mo.ui.dropdown or mo.ui.multiselect
        - JSON: State dict for API responses
    """

    def __init__(self, state: SelectWidgetState | None = None) -> None:
        self.state = Signal.of(state or SelectWidgetState(options=()))

    def project(self, target: RenderTarget) -> Any:
        """Project select to target surface."""
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
        """CLI projection: numbered list."""
        s = self.state.value
        lines = []

        if not s.options:
            return s.placeholder

        for i, opt in enumerate(s.options, 1):
            marker = "[x]" if opt.value in s.selected else "[ ]"
            disabled = " (disabled)" if opt.disabled else ""
            lines.append(f"  {i}. {marker} {opt.label}{disabled}")
            if opt.description:
                lines.append(f"      {opt.description}")

        return "\n".join(lines)

    def _to_tui(self) -> Any:
        """TUI projection: Textual Select widget."""
        try:
            from textual.widgets import Select, SelectionList

            s = self.state.value

            if s.multiple:
                # Multi-select uses SelectionList
                multi_options: list[tuple[str, str, bool]] = [
                    (opt.label, opt.value, opt.value in s.selected)
                    for opt in s.options
                    if not opt.disabled
                ]
                return SelectionList(*multi_options)
            else:
                # Single select
                single_options: list[tuple[str, str]] = [
                    (opt.label, opt.value) for opt in s.options if not opt.disabled
                ]
                return Select(
                    single_options,
                    prompt=s.placeholder,
                    value=s.selected[0] if s.selected else None,
                )
        except ImportError:
            from rich.text import Text

            return Text(self._to_cli())

    def _to_marimo(self) -> str:
        """MARIMO projection: HTML for mo.ui integration."""
        s = self.state.value

        options_html = []
        for opt in s.options:
            selected = "selected" if opt.value in s.selected else ""
            disabled = "disabled" if opt.disabled else ""
            options_html.append(
                f'<option value="{opt.value}" {selected} {disabled}>'
                f"{opt.label}</option>"
            )

        multiple = "multiple" if s.multiple else ""
        return f"""
        <select class="kgents-select" {multiple}>
            <option value="" disabled>{s.placeholder}</option>
            {"".join(options_html)}
        </select>
        """

    def _to_json(self) -> dict[str, Any]:
        """JSON projection: state dict for API responses."""
        s = self.state.value
        return {
            "type": "select",
            "options": [
                {
                    "value": opt.value,
                    "label": opt.label,
                    "description": opt.description,
                    "disabled": opt.disabled,
                    "icon": opt.icon,
                }
                for opt in s.options
            ],
            "selected": list(s.selected),
            "placeholder": s.placeholder,
            "multiple": s.multiple,
            "searchable": s.searchable,
            "maxSelections": s.max_selections,
        }


__all__ = ["SelectWidget", "SelectWidgetState", "SelectOption"]
