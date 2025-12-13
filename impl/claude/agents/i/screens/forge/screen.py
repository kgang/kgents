"""
ForgeScreen - Agent creation and composition.

The Forge is a visual environment for building, testing, and exporting
agent pipelines. It embodies JOY in creation.

Modes:
- compose: Build pipelines from components
- simulate: Test pipelines with sample input
- refine: Iterate on failures
- export: Generate Python code

Navigation:
  Tab/Shift+Tab - Switch between panels
  Enter         - Add selected component to pipeline
  x             - Remove selected component from pipeline
  r             - Run simulation
  s             - Step through simulation
  e             - Export to code
  c/m/f/x       - Switch modes
  Esc           - Back to previous screen
"""

from __future__ import annotations

from typing import Literal

from textual import on, work
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import Button, Footer, Header, Static

from .exporter import CodeExporter
from .palette import AgentPalette, ComponentSelected
from .pipeline import PipelineBuilder
from .simulator import SimulationRunner
from .types import (
    ComponentSpec,
    PipelineComponent,
    SimulationResult,
    StepResult,
)


class ModeIndicator(Static):
    """Shows the current Forge mode."""

    DEFAULT_CSS = """
    ModeIndicator {
        height: 1;
        background: #252525;
        color: #f5f0e6;
        padding: 0 2;
        dock: top;
    }

    ModeIndicator .mode-active {
        text-style: bold;
        color: #e6a352;
    }

    ModeIndicator .mode-inactive {
        color: #6a6560;
    }
    """

    def __init__(
        self,
        mode: Literal["compose", "simulate", "refine", "export"] = "compose",
    ) -> None:
        super().__init__()
        self._mode = mode

    def render(self) -> str:
        """Render the mode indicator."""
        modes = ["compose", "simulate", "refine", "export"]
        parts = []
        for m in modes:
            if m == self._mode:
                parts.append(f"[●{m}]")
            else:
                parts.append(f"[○{m}]")
        return "  ".join(parts)

    def set_mode(
        self, mode: Literal["compose", "simulate", "refine", "export"]
    ) -> None:
        """Set the current mode."""
        self._mode = mode
        self.refresh()


class ForgeScreen(Screen[None]):
    """
    The Forge - Agent creation and composition.

    A delightful visual environment for building agent pipelines.
    """

    CSS = """
    ForgeScreen {
        background: #1a1a1a;
    }

    ForgeScreen #main-layout {
        width: 100%;
        height: 100%;
    }

    ForgeScreen #left-panel {
        width: 32;
        height: 100%;
        background: #1a1a1a;
    }

    ForgeScreen #right-panel {
        width: 1fr;
        height: 100%;
        background: #1a1a1a;
    }

    ForgeScreen #pipeline-container {
        height: 1fr;
    }

    ForgeScreen #simulation-container {
        height: auto;
        min-height: 15;
    }

    ForgeScreen #help-bar {
        height: 1;
        background: #1a1a1a;
        color: #6a6560;
        padding: 0 2;
        dock: bottom;
    }

    ForgeScreen #export-panel {
        width: 100%;
        height: 100%;
        background: #1a1a1a;
        border: solid #4a4a5c;
        padding: 2;
    }

    ForgeScreen .export-header {
        height: 1;
        color: #f5f0e6;
        text-style: bold;
        margin-bottom: 1;
    }

    ForgeScreen .export-code {
        width: 100%;
        height: 1fr;
        border: solid #4a4a5c;
        padding: 1;
        background: #252525;
        color: #b3a89a;
    }
    """

    BINDINGS = [
        Binding("tab", "focus_next", "Next Panel", show=False),
        Binding("shift+tab", "focus_previous", "Prev Panel", show=False),
        Binding("enter", "add_to_pipeline", "Add Component"),
        Binding("x", "remove_from_pipeline", "Remove Component"),
        Binding("r", "run_simulation", "Run"),
        Binding("s", "step_simulation", "Step"),
        Binding("c", "mode_compose", "Compose Mode"),
        Binding("m", "mode_simulate", "Simulate Mode"),
        Binding("f", "mode_refine", "Refine Mode", show=False),
        Binding("e", "mode_export", "Export Mode"),
        Binding("escape", "back", "Back"),
        Binding("question_mark", "show_help", "Help"),
    ]

    def __init__(
        self,
        name: str | None = None,
        id: str | None = None,  # noqa: A002
        classes: str | None = None,
    ) -> None:
        super().__init__(name=name, id=id, classes=classes)
        self.mode: Literal["compose", "simulate", "refine", "export"] = "compose"
        self._palette: AgentPalette | None = None
        self._pipeline: PipelineBuilder | None = None
        self._simulator: SimulationRunner | None = None
        self._mode_indicator: ModeIndicator | None = None
        self._exporter = CodeExporter()

    def compose(self) -> ComposeResult:
        """Compose the Forge screen."""
        yield Header()
        self._mode_indicator = ModeIndicator(mode=self.mode)
        yield self._mode_indicator

        with Container(id="main-layout"):
            with Horizontal():
                # Left panel: Component palette
                with Vertical(id="left-panel"):
                    self._palette = AgentPalette()
                    yield self._palette

                # Right panel: Pipeline and simulation
                with Vertical(id="right-panel"):
                    with Container(id="pipeline-container"):
                        self._pipeline = PipelineBuilder()
                        yield self._pipeline

                    with Container(id="simulation-container"):
                        self._simulator = SimulationRunner()
                        yield self._simulator

        yield Static(
            "Tab: switch panels  Enter: add  x: remove  r: run  e: export  Esc: back",
            id="help-bar",
        )
        yield Footer()

    @on(ComponentSelected)
    def on_component_selected(self, event: ComponentSelected) -> None:
        """Handle component selection from palette."""
        # Store the selected component for later use
        if self._palette:
            self._palette._selected_spec = event.spec
            self.notify(f"Selected: {event.spec.display_name}")

    def action_add_to_pipeline(self) -> None:
        """Add the selected component to the pipeline (Enter)."""
        if self.mode != "compose":
            self.notify("Switch to compose mode first (c)")
            return

        if not self._palette or not self._pipeline:
            return

        selected = self._palette.get_selected()
        if selected:
            self._pipeline.add_component(selected)
            self.notify(f"Added {selected.display_name} to pipeline")

            # Update simulator with new pipeline
            if self._simulator:
                self._simulator.set_pipeline(self._pipeline.get_components())
        else:
            self.notify("Select a component first")

    def action_remove_from_pipeline(self) -> None:
        """Remove the selected component from the pipeline (x)."""
        if self.mode != "compose":
            self.notify("Switch to compose mode first (c)")
            return

        if not self._pipeline:
            return

        index = self._pipeline.get_selected_index()
        if index >= 0:
            self._pipeline.remove_component(index)
            self.notify(f"Removed component at index {index}")

            # Update simulator
            if self._simulator:
                self._simulator.set_pipeline(self._pipeline.get_components())
        else:
            self.notify("No component selected")

    def action_run_simulation(self) -> None:
        """Run the full simulation (r)."""
        if not self._simulator or not self._pipeline:
            return

        # Get input from simulator
        input_widget = self._simulator.query_one("#sim-input")
        if not hasattr(input_widget, "value"):
            self.notify("No input field found")
            return

        input_text = input_widget.value  # pyright: ignore
        if not input_text:
            self.notify("Enter input text first")
            return

        # Run simulation
        result = self._simulator.run_simulation(input_text)

        if result.success:
            self.notify(f"Simulation complete ({result.elapsed_ms:.0f}ms)")
        else:
            self.notify(f"Simulation failed: {result.error}")

    def action_step_simulation(self) -> None:
        """Step through the simulation (s)."""
        if not self._simulator:
            return

        step_result = self._simulator.step_simulation()
        if step_result:
            self.notify(
                f"Step {step_result.component_index + 1}: {step_result.component_name}"
            )
        else:
            self.notify("No more steps")

    def action_mode_compose(self) -> None:
        """Switch to compose mode (c)."""
        self.mode = "compose"
        if self._mode_indicator:
            self._mode_indicator.set_mode("compose")
        self.notify("Mode: COMPOSE")

    def action_mode_simulate(self) -> None:
        """Switch to simulate mode (m)."""
        self.mode = "simulate"
        if self._mode_indicator:
            self._mode_indicator.set_mode("simulate")
        self.notify("Mode: SIMULATE")

    def action_mode_refine(self) -> None:
        """Switch to refine mode (f)."""
        self.mode = "refine"
        if self._mode_indicator:
            self._mode_indicator.set_mode("refine")
        self.notify("Mode: REFINE (not yet implemented)")

    def action_mode_export(self) -> None:
        """Switch to export mode (e)."""
        self.mode = "export"
        if self._mode_indicator:
            self._mode_indicator.set_mode("export")

        # Generate and show code
        if self._pipeline:
            code = self.export_code()
            self._show_export_view(code)

    def action_back(self) -> None:
        """Go back to previous screen (Esc)."""
        self.app.pop_screen()

    def action_show_help(self) -> None:
        """Show help overlay (?)."""
        # TODO: Implement help overlay
        self.notify("Help overlay (not yet implemented)")

    # ========================================================================
    # Public Interface Methods
    # ========================================================================

    def add_to_pipeline(self, component: str) -> None:
        """
        Add a component to the pipeline by ID.

        Args:
            component: Component ID (e.g., "a-alethic", "ground")
        """
        # Find the component spec
        from .palette import AGENT_CATALOG, PRIMITIVE_CATALOG

        all_components = AGENT_CATALOG + PRIMITIVE_CATALOG
        spec = next((c for c in all_components if c.id == component), None)

        if spec and self._pipeline:
            self._pipeline.add_component(spec)

    def remove_from_pipeline(self, index: int) -> None:
        """
        Remove a component from the pipeline.

        Args:
            index: Component index to remove
        """
        if self._pipeline:
            self._pipeline.remove_component(index)

    def run_simulation(self, input_text: str) -> SimulationResult:
        """
        Run the pipeline simulation.

        Args:
            input_text: Input text to process

        Returns:
            SimulationResult with output and steps
        """
        if self._simulator:
            return self._simulator.run_simulation(input_text)
        return SimulationResult(
            success=False,
            output=None,
            error="Simulator not initialized",
        )

    def step_simulation(self) -> StepResult | None:
        """
        Step through the simulation.

        Returns:
            StepResult for the current step, or None
        """
        if self._simulator:
            return self._simulator.step_simulation()
        return None

    def export_code(self) -> str:
        """
        Export the pipeline as Python code.

        Returns:
            Valid Python code as string
        """
        if self._pipeline:
            components = self._pipeline.get_components()
            return self._exporter.export(components)
        return self._exporter.export([])

    # ========================================================================
    # Internal Methods
    # ========================================================================

    def _show_export_view(self, code: str) -> None:
        """Show the export view with generated code."""
        # For now, just notify with a preview
        lines = code.split("\n")
        preview = "\n".join(lines[:10])
        if len(lines) > 10:
            preview += f"\n... ({len(lines) - 10} more lines)"

        self.notify(f"Generated code:\n{preview}")
        # TODO: Add copy to clipboard functionality
        # TODO: Add write to file functionality
