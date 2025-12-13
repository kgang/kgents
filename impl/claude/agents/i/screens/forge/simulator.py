"""
SimulationRunner - Test harness for composed pipelines.

Runs the pipeline with test input and displays step-by-step results.
"""

from __future__ import annotations

import time
from typing import Any

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widget import Widget
from textual.widgets import Button, Input, Static

from .types import PipelineComponent, SimulationResult, StepResult


class SimulationRunner(Widget):
    """
    Simulation runner widget.

    Provides:
    - Input field for test data
    - Run/Step/Reset controls
    - Output display
    """

    DEFAULT_CSS = """
    SimulationRunner {
        width: 100%;
        height: auto;
        border: solid #4a4a5c;
        padding: 1;
        background: #1a1a1a;
    }

    SimulationRunner .sim-header {
        height: 1;
        color: #f5f0e6;
        text-style: bold;
        background: #252525;
        padding: 0 1;
        dock: top;
    }

    SimulationRunner .sim-status {
        height: 1;
        color: #b3a89a;
        padding: 0 1;
        margin-bottom: 1;
    }

    SimulationRunner .sim-input-label {
        height: 1;
        color: #f5f0e6;
        padding: 0 1;
        margin-top: 1;
    }

    SimulationRunner Input {
        width: 100%;
        margin: 0 1;
    }

    SimulationRunner .sim-output-label {
        height: 1;
        color: #f5f0e6;
        padding: 0 1;
        margin-top: 1;
    }

    SimulationRunner .sim-output {
        width: 100%;
        min-height: 5;
        border: solid #4a4a5c;
        padding: 1;
        margin: 0 1;
        background: #252525;
        color: #b3a89a;
    }

    SimulationRunner .sim-controls {
        height: auto;
        padding: 1;
        margin-top: 1;
    }

    SimulationRunner Button {
        margin: 0 1;
    }

    SimulationRunner .sim-error {
        color: #ff6b6b;
        text-style: bold;
    }

    SimulationRunner .sim-success {
        color: #6bcf7f;
        text-style: bold;
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
        self._current_result: SimulationResult | None = None
        self._current_step: int = 0

    def compose(self) -> ComposeResult:
        """Compose the simulation runner."""
        yield Static("SIMULATION", classes="sim-header")
        yield Static("Status: READY", classes="sim-status", id="status")

        yield Static("Input:", classes="sim-input-label")
        yield Input(placeholder="Enter test input...", id="sim-input")

        yield Static("Output:", classes="sim-output-label")
        yield Static("(awaiting input)", classes="sim-output", id="sim-output")

        with Horizontal(classes="sim-controls"):
            yield Button("Run", id="btn-run", variant="primary")
            yield Button("Step", id="btn-step", variant="default")
            yield Button("Reset", id="btn-reset", variant="default")

    def set_pipeline(self, components: list[PipelineComponent]) -> None:
        """Set the pipeline to simulate."""
        self._components = components
        self._current_step = 0

    def run_simulation(self, input_text: str) -> SimulationResult:
        """
        Run the full pipeline simulation.

        Args:
            input_text: The input text to process

        Returns:
            SimulationResult with output and steps
        """
        start_time = time.time()
        steps: list[StepResult] = []
        current_value: Any = input_text

        try:
            for i, component in enumerate(self._components):
                step_start = time.time()

                # Simulate component execution
                # In a real implementation, this would invoke the actual agent
                step_output = self._simulate_component(component, current_value)

                step_elapsed = (time.time() - step_start) * 1000

                steps.append(
                    StepResult(
                        component_index=i,
                        component_name=component.spec.name,
                        input=current_value,
                        output=step_output,
                        elapsed_ms=step_elapsed,
                    )
                )

                current_value = step_output

            elapsed = (time.time() - start_time) * 1000

            result = SimulationResult(
                success=True,
                output=current_value,
                steps=steps,
                elapsed_ms=elapsed,
            )

        except Exception as e:
            elapsed = (time.time() - start_time) * 1000
            result = SimulationResult(
                success=False,
                output=None,
                error=str(e),
                steps=steps,
                elapsed_ms=elapsed,
            )

        self._current_result = result
        self._update_display(result)
        return result

    def step_simulation(self) -> StepResult | None:
        """
        Execute one step of the simulation.

        Returns:
            StepResult for the current step, or None if no more steps
        """
        if self._current_step >= len(self._components):
            return None

        # Get input
        input_widget = self.query_one("#sim-input", Input)
        input_text = input_widget.value

        if not input_text:
            self._set_status("Error: No input provided", is_error=True)
            return None

        # Execute current step
        component = self._components[self._current_step]
        step_start = time.time()

        try:
            # Get input from previous step or initial input
            if self._current_step == 0:
                current_input = input_text
            elif self._current_result and self._current_result.steps:
                current_input = self._current_result.steps[-1].output
            else:
                current_input = input_text

            step_output = self._simulate_component(component, current_input)
            step_elapsed = (time.time() - step_start) * 1000

            step_result = StepResult(
                component_index=self._current_step,
                component_name=component.spec.name,
                input=current_input,
                output=step_output,
                elapsed_ms=step_elapsed,
            )

            # Initialize or update result
            if not self._current_result:
                self._current_result = SimulationResult(
                    success=True,
                    output=step_output,
                    steps=[step_result],
                )
            else:
                self._current_result.steps.append(step_result)
                self._current_result.output = step_output

            self._current_step += 1
            self._update_display(self._current_result)

            return step_result

        except Exception as e:
            self._set_status(f"Error: {e}", is_error=True)
            return None

    def reset(self) -> None:
        """Reset the simulation."""
        self._current_result = None
        self._current_step = 0

        # Clear output (guard for unmounted widget)
        try:
            output = self.query_one("#sim-output", Static)
            output.update("(awaiting input)")
            self._set_status("Status: READY")
        except Exception:
            pass  # Not mounted yet

    def _simulate_component(
        self, component: PipelineComponent, input_value: Any
    ) -> Any:
        """
        Simulate a component's execution.

        In a real implementation, this would invoke the actual agent.
        For now, we just transform the input symbolically.

        Args:
            component: The component to simulate
            input_value: The input to the component

        Returns:
            Simulated output
        """
        # Simple mock: just append the component name to the input
        return f"{input_value} → [{component.spec.name}]"

    def _update_display(self, result: SimulationResult) -> None:
        """Update the display with simulation results."""
        # Guard: only update if mounted
        try:
            output = self.query_one("#sim-output", Static)
        except Exception:
            return  # Not mounted yet

        if result.success:
            # Show steps and final output
            display = ""
            for step in result.steps:
                display += f"[{step.component_name}] {step.input} → {step.output}\n"
            display += f"\nFinal output: {result.output}\n"
            display += f"Elapsed: {result.elapsed_ms:.0f}ms"

            output.update(display)
            self._set_status("Status: SUCCESS", is_success=True)
        else:
            output.update(f"ERROR: {result.error}")
            output.add_class("sim-error")
            self._set_status("Status: FAILED", is_error=True)

    def _set_status(
        self,
        message: str,
        is_error: bool = False,
        is_success: bool = False,
    ) -> None:
        """Update the status message."""
        status = self.query_one("#status", Static)
        status.update(message)

        # Update styling
        status.remove_class("sim-error")
        status.remove_class("sim-success")

        if is_error:
            status.add_class("sim-error")
        elif is_success:
            status.add_class("sim-success")
