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

Projection Integration (v2):
    Widgets now integrate with the Projection Component Library for unified
    rendering with metadata (status, cache, errors, refusals).

    # Get wrapped result with metadata
    envelope = widget.to_envelope(RenderTarget.JSON)
    if envelope.meta.has_error:
        show_error(envelope.meta.error)
    else:
        render(envelope.data)
"""

from __future__ import annotations

import os
from abc import ABC, abstractmethod
from enum import Enum, auto
from typing import TYPE_CHECKING, Any, Generic, TypeVar

if TYPE_CHECKING:
    from collections.abc import AsyncIterator

    from protocols.projection.schema import WidgetEnvelope, WidgetMeta

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

    # =========================================================================
    # Projection Integration (v2)
    # =========================================================================

    def to_envelope(
        self,
        target: RenderTarget = RenderTarget.JSON,
        *,
        meta: "WidgetMeta | None" = None,
        source_path: str | None = None,
    ) -> "WidgetEnvelope[Any]":
        """
        Project to target wrapped in a WidgetEnvelope with metadata.

        This integrates with the Projection Component Library, providing
        unified metadata (status, cache, errors, refusals) alongside the
        projected data.

        **Error Boundary**: This method never raises exceptions. If projection
        fails, the envelope contains an ErrorInfo with details, and data is None.

        Args:
            target: Which rendering target to project to
            meta: Optional metadata to include (defaults to WidgetMeta.done())
            source_path: Optional AGENTESE path that produced this widget

        Returns:
            WidgetEnvelope containing the projection and metadata.
            On error: data=None, meta.status=ERROR, meta.error contains details.

        Example:
            envelope = widget.to_envelope(RenderTarget.JSON)
            if envelope.meta.has_error:
                show_error(envelope.meta.error)
            elif envelope.meta.status == WidgetStatus.DONE:
                api_response = envelope.to_dict()
        """
        from protocols.projection.schema import ErrorInfo, WidgetEnvelope, WidgetMeta

        try:
            # Get the projection
            data = self.project(target)

            # Use provided meta or default to done
            if meta is None:
                meta = WidgetMeta.done()

            return WidgetEnvelope(
                data=data,
                meta=meta,
                source_path=source_path,
            )
        except Exception as e:
            # Error boundary: wrap exceptions in envelope
            error_info = ErrorInfo(
                category="unknown",
                code=type(e).__name__,
                message=str(e) or f"Projection to {target.name} failed",
                fallback_action=f"Try {target.name} projection again or use a different target",
            )
            return WidgetEnvelope(
                data=None,
                meta=WidgetMeta.with_error(error_info),
                source_path=source_path,
            )

    def to_json_envelope(
        self,
        *,
        meta: "WidgetMeta | None" = None,
        source_path: str | None = None,
    ) -> "WidgetEnvelope[dict[str, Any]]":
        """
        Convenience: project to JSON wrapped in envelope.

        Equivalent to to_envelope(RenderTarget.JSON) but with better typing.
        """
        return self.to_envelope(RenderTarget.JSON, meta=meta, source_path=source_path)

    def widget_type(self) -> str:
        """
        Return the widget type name for projection hints.

        Override in subclasses to customize. Default is class name
        converted to snake_case.

        Example:
            class AgentCardWidget -> "agent_card"
        """
        import re

        name = self.__class__.__name__
        if name.endswith("Widget"):
            name = name[:-6]
        # Convert CamelCase to snake_case
        return re.sub(r"(?<!^)(?=[A-Z])", "_", name).lower()

    def ui_hint(self) -> str | None:
        """
        Return the UI hint for projection.

        Override in subclasses to provide specific hints.
        Valid values: "form", "stream", "table", "graph", "card", "text"

        Default returns None (let projection adapter infer from path).
        """
        return None

    async def to_streaming_envelope(
        self,
        target: RenderTarget = RenderTarget.JSON,
        *,
        source_path: str | None = None,
        total_expected: int | None = None,
    ) -> "AsyncIterator[WidgetEnvelope[Any]]":
        """
        Yield streaming envelopes as projection progresses.

        For widgets that support incremental rendering, this yields
        envelopes with STREAMING status until complete, then DONE.

        Default implementation yields a single DONE envelope (non-streaming).
        Override in subclasses to provide true streaming behavior.

        Args:
            target: Which rendering target to project to
            source_path: Optional AGENTESE path that produced this widget
            total_expected: Optional total chunks expected (for progress)

        Yields:
            WidgetEnvelope with STREAMING status, then final DONE envelope

        Example:
            async for envelope in widget.to_streaming_envelope():
                if envelope.meta.status == WidgetStatus.STREAMING:
                    update_progress(envelope.meta.stream.progress)
                else:
                    render_final(envelope.data)
        """
        from datetime import datetime, timezone

        from protocols.projection.schema import StreamMeta, WidgetEnvelope, WidgetMeta

        # Default: non-streaming widget yields single envelope
        # Subclasses can override for true streaming behavior

        # Start streaming
        started_at = datetime.now(timezone.utc)
        stream_meta = StreamMeta(
            total_expected=total_expected or 1,
            received=0,
            started_at=started_at,
        )

        # Yield initial streaming state
        yield WidgetEnvelope(
            data=None,
            meta=WidgetMeta.streaming(stream_meta),
            source_path=source_path,
        )

        # Get actual projection (with error boundary)
        final_envelope = self.to_envelope(target, source_path=source_path)

        # Yield final result
        yield final_envelope


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
