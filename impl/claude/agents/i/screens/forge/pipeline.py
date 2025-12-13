"""
PipelineBuilder - Visual composition widget.

Shows the pipeline being built with type validation and cost estimation.
Components flow left-to-right with arrows showing data flow.
"""

from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import VerticalScroll
from textual.widget import Widget
from textual.widgets import Static

from .types import (
    ComponentSpec,
    CostEstimate,
    PipelineComponent,
    ValidationError,
)


class PipelineBuilder(Widget):
    """
    Visual pipeline builder.

    Displays components in sequence with arrows showing flow.
    Validates type compatibility and estimates costs.
    """

    DEFAULT_CSS = """
    PipelineBuilder {
        width: 100%;
        height: 100%;
        border: solid #4a4a5c;
        padding: 1;
        background: #1a1a1a;
    }

    PipelineBuilder .pipeline-header {
        height: 1;
        color: #f5f0e6;
        text-style: bold;
        background: #252525;
        padding: 0 1;
        dock: top;
    }

    PipelineBuilder .pipeline-container {
        height: auto;
        padding: 2;
    }

    PipelineBuilder .component-box {
        width: auto;
        height: 5;
        border: solid #4a4a5c;
        padding: 0 1;
        margin: 1 0;
        background: #252525;
    }

    PipelineBuilder .component-box.--selected {
        border: solid #e6a352;
        background: #2a2a2a;
    }

    PipelineBuilder .component-name {
        color: #f5f0e6;
        text-style: bold;
    }

    PipelineBuilder .component-types {
        color: #b3a89a;
    }

    PipelineBuilder .arrow {
        color: #6a6560;
        text-align: center;
        height: 1;
    }

    PipelineBuilder .cost-section {
        height: 3;
        border-top: solid #4a4a5c;
        padding: 1;
        background: #1a1a1a;
        dock: bottom;
    }

    PipelineBuilder .validation-error {
        color: #ff6b6b;
        text-style: bold;
    }

    PipelineBuilder .validation-warning {
        color: #ffd93d;
    }

    PipelineBuilder .empty-state {
        width: 100%;
        height: 100%;
        align: center middle;
        text-align: center;
        color: #6a6560;
        padding: 4;
    }
    """

    def __init__(
        self,
        name: str | None = None,
        id: str | None = None,  # noqa: A002
        classes: str | None = None,
    ) -> None:
        super().__init__(name=name, id=id, classes=classes)
        self._components: list[PipelineComponent] = []
        self._selected_index: int = -1

    def compose(self) -> ComposeResult:
        """Compose the pipeline builder."""
        yield Static("PIPELINE", classes="pipeline-header")
        with VerticalScroll(classes="pipeline-container"):
            if not self._components:
                yield Static(
                    "Select components from the palette →\nPress Enter to add to pipeline",
                    classes="empty-state",
                )
        yield self._render_cost_section()

    def add_component(self, spec: ComponentSpec) -> None:
        """Add a component to the pipeline."""
        component = PipelineComponent(
            spec=spec,
            config={},
            index=len(self._components),
        )
        self._components.append(component)
        self._refresh_display()

    def remove_component(self, index: int) -> None:
        """Remove a component from the pipeline."""
        if 0 <= index < len(self._components):
            self._components.pop(index)
            # Re-index remaining components
            for i, comp in enumerate(self._components):
                comp.index = i
            self._refresh_display()

    def select_component(self, index: int) -> None:
        """Select a component in the pipeline."""
        if 0 <= index < len(self._components):
            self._selected_index = index
            self._refresh_display()

    def get_selected_index(self) -> int:
        """Get the currently selected component index."""
        return self._selected_index

    def validate(self) -> list[ValidationError]:
        """
        Validate the pipeline for type compatibility.

        Returns:
            List of validation errors (empty if valid)
        """
        errors: list[ValidationError] = []

        for i in range(len(self._components) - 1):
            current = self._components[i]
            next_comp = self._components[i + 1]

            # Check type compatibility
            if not self._types_compatible(
                current.spec.output_type,
                next_comp.spec.input_type,
            ):
                errors.append(
                    ValidationError(
                        component_index=i,
                        message=f"Type mismatch: {current.spec.name} outputs {current.spec.output_type}, "
                        f"but {next_comp.spec.name} expects {next_comp.spec.input_type}",
                        severity="error",
                    )
                )

        return errors

    def estimate_cost(self) -> CostEstimate:
        """
        Estimate the cost of running this pipeline.

        Returns:
            Cost estimate with entropy, tokens, and latency
        """
        # Simple heuristic: each component adds to the budget
        entropy = len(self._components) * 0.05  # 0.05 entropy per component
        tokens = len(self._components) * 500  # ~500 tokens per component
        latency = len(self._components) * 100.0  # ~100ms per component

        return CostEstimate(
            entropy_per_turn=entropy,
            token_budget=tokens,
            estimated_latency_ms=latency,
        )

    def get_components(self) -> list[PipelineComponent]:
        """Get all components in the pipeline."""
        return self._components.copy()

    def clear(self) -> None:
        """Clear all components from the pipeline."""
        self._components.clear()
        self._selected_index = -1
        self._refresh_display()

    def _types_compatible(self, output_type: str, input_type: str) -> bool:
        """
        Check if two types are compatible for composition.

        Args:
            output_type: The output type of the first component
            input_type: The input type of the second component

        Returns:
            True if types are compatible
        """
        # Any is compatible with everything
        if output_type == "Any" or input_type == "Any":
            return True

        # Exact match
        if output_type == input_type:
            return True

        # TODO: Add more sophisticated type checking
        # For now, just warn on mismatch
        return True  # Accept all for initial implementation

    def _refresh_display(self) -> None:
        """Refresh the pipeline display."""
        # Guard: only refresh if mounted
        try:
            container = self.query_one(VerticalScroll)
        except Exception:
            return  # Not mounted yet
        container.remove_children()

        if not self._components:
            container.mount(
                Static(
                    "Select components from the palette →\nPress Enter to add to pipeline",
                    classes="empty-state",
                )
            )
            return

        # Render each component
        for i, component in enumerate(self._components):
            # Component box
            is_selected = i == self._selected_index
            box = Static(classes="component-box")
            if is_selected:
                box.add_class("--selected")

            box_content = (
                f"{component.spec.display_name}\n"
                f"{component.spec.input_type} → {component.spec.output_type}"
            )
            container.mount(Static(box_content, classes="component-box"))

            # Arrow between components (except after last)
            if i < len(self._components) - 1:
                container.mount(Static("│\n▼", classes="arrow"))

        # Update cost display
        self._update_cost_section()

    def _render_cost_section(self) -> Static:
        """Render the cost estimation section."""
        cost = self.estimate_cost()
        content = (
            f"Entropy cost: {cost.entropy_per_turn:.2f}/turn\n"
            f"Token budget: ~{cost.token_budget:,}\n"
            f"Estimated latency: {cost.estimated_latency_ms:.0f}ms"
        )
        return Static(content, classes="cost-section")

    def _update_cost_section(self) -> None:
        """Update the cost section display."""
        cost_section = self.query_one(".cost-section", Static)
        cost = self.estimate_cost()
        cost_section.update(
            f"Entropy cost: {cost.entropy_per_turn:.2f}/turn\n"
            f"Token budget: ~{cost.token_budget:,}\n"
            f"Estimated latency: {cost.estimated_latency_ms:.0f}ms"
        )
