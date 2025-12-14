"""
KgentsWidget[S]: Base class for target-agnostic widgets.

A widget is:
1. A state machine (Signal[S])
2. Derived computations (Computed[...])
3. Side effects (Effect)
4. A projection function per target

The widget definition is TARGET-AGNOSTIC.
Projectors handle target-specific rendering.

This is categorically beautiful:
    Widget[S] : State -> UI
    project : Widget[S] -> Target -> UI[Target]

The state machine IS the widget. The rendering IS a functor application.

Instrumentation:
    Metrics can be enabled via KGENTS_REACTIVE_METRICS=1 env var.
    When enabled, render durations are tracked via OpenTelemetry.
"""

from __future__ import annotations

import os
from abc import ABC, abstractmethod
from enum import Enum, auto
from typing import TYPE_CHECKING, Any, Generic, TypeVar

if TYPE_CHECKING:
    pass

# Check if metrics are enabled (opt-in for zero overhead by default)
_METRICS_ENABLED = os.environ.get("KGENTS_REACTIVE_METRICS", "").lower() in (
    "1",
    "true",
    "yes",
)

S = TypeVar("S")  # State type


class RenderTarget(Enum):
    """
    Supported rendering targets.

    Each target represents a different way to visualize the widget:
    - CLI: Plain text / ASCII for terminal output
    - TUI: Rich/Textual widget for interactive TUI
    - MARIMO: anywidget for Jupyter/marimo notebooks
    - JSON: Serializable dict for API responses
    """

    CLI = auto()
    TUI = auto()
    MARIMO = auto()
    JSON = auto()


class KgentsWidget(ABC, Generic[S]):
    """
    Base class for all kgents widgets.

    A widget is:
    1. A state machine (holds Signal[S])
    2. Optional derived computations (Computed[...])
    3. Optional side effects (Effect)
    4. A project() method that renders to any target

    The widget definition is TARGET-AGNOSTIC.
    The project() method handles target-specific rendering.

    Example:
        @dataclass(frozen=True)
        class CounterState:
            count: int = 0

        class CounterWidget(KgentsWidget[CounterState]):
            def __init__(self, initial: int = 0):
                self.state = Signal.of(CounterState(count=initial))

            def project(self, target: RenderTarget) -> str | dict | object:
                count = self.state.value.count
                match target:
                    case RenderTarget.CLI:
                        return f"Count: {count}"
                    case RenderTarget.JSON:
                        return {"type": "counter", "count": count}
                    case _:
                        return f"Count: {count}"

            def increment(self) -> None:
                self.state.update(lambda s: CounterState(count=s.count + 1))
    """

    @abstractmethod
    def project(self, target: RenderTarget) -> Any:
        """
        Project this widget to a rendering target.

        This IS the AGENTESE `manifest` aspect operationalized.
        Same state, different targets -> different representations.

        Args:
            target: Which rendering target to project to

        Returns:
            - CLI: str (ASCII art / text)
            - TUI: textual.widget.Widget or rich.text.Text
            - MARIMO: anywidget.AnyWidget or HTML string
            - JSON: dict (serializable for API)
        """
        ...

    def to_cli(self) -> str:
        """Convenience: project to CLI (returns string)."""
        if _METRICS_ENABLED:
            from agents.i.reactive._metrics import RenderTimer

            with RenderTimer(self.__class__.__name__, "CLI"):
                result = self.project(RenderTarget.CLI)
            return str(result)
        result = self.project(RenderTarget.CLI)
        return str(result)

    def to_tui(self) -> Any:
        """Convenience: project to Textual (returns widget/text)."""
        if _METRICS_ENABLED:
            from agents.i.reactive._metrics import RenderTimer

            with RenderTimer(self.__class__.__name__, "TUI"):
                return self.project(RenderTarget.TUI)
        return self.project(RenderTarget.TUI)

    def to_marimo(self) -> Any:
        """Convenience: project to marimo (returns anywidget/HTML)."""
        if _METRICS_ENABLED:
            from agents.i.reactive._metrics import RenderTimer

            with RenderTimer(self.__class__.__name__, "MARIMO"):
                return self.project(RenderTarget.MARIMO)
        return self.project(RenderTarget.MARIMO)

    def to_json(self) -> dict[str, Any]:
        """Convenience: project to JSON (returns dict)."""
        if _METRICS_ENABLED:
            from agents.i.reactive._metrics import RenderTimer

            with RenderTimer(self.__class__.__name__, "JSON"):
                result = self.project(RenderTarget.JSON)
        else:
            result = self.project(RenderTarget.JSON)
        if isinstance(result, dict):
            return result
        return {"value": result}


class CompositeWidget(KgentsWidget[S]):
    """
    A widget that composes other widgets.

    CompositeWidget holds child widgets in slots and delegates rendering
    to them. This implements operad-like composition where slots define
    arity and fillers provide the operations.

    Example:
        class CardWidget(CompositeWidget[CardState]):
            def __init__(self, state: CardState):
                super().__init__(state)
                self.slots = {
                    "header": GlyphWidget(GlyphState(phase=state.phase)),
                    "body": TextWidget(state.content),
                }

            def project(self, target: RenderTarget) -> Any:
                header = self.slots["header"].project(target)
                body = self.slots["body"].project(target)
                match target:
                    case RenderTarget.CLI:
                        return f"[{header}] {body}"
                    case RenderTarget.JSON:
                        return {"header": header, "body": body}
                    case _:
                        return f"[{header}] {body}"
    """

    slots: dict[str, KgentsWidget[Any]]

    def __init__(self, initial_state: S) -> None:
        from agents.i.reactive.signal import Signal

        self.state = Signal.of(initial_state)
        self.slots = {}

    @abstractmethod
    def project(self, target: RenderTarget) -> Any:
        """Compose children projections based on target."""
        ...
