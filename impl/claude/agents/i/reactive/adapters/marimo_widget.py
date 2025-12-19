"""
MarimoAdapter: Bridge KgentsWidget to anywidget for marimo/Jupyter notebooks.

Wave 11 of the reactive substrate unification.

This adapter bridges Signal[T] → Traitlets → JavaScript:
    KgentsWidget.state (Signal[S])
        ↓ subscribe
    MarimoAdapter._state_json (traitlet, sync=True)
        ↓ anywidget protocol
    JavaScript model.get("_state_json")
        ↓ render()
    DOM element

Usage:
    from agents.i.reactive.adapters import MarimoAdapter

    # Wrap a KgentsWidget
    adapter = MarimoAdapter(my_widget)

    # Use in marimo
    import marimo as mo
    mo.ui.anywidget(adapter)

The adapter calls widget.project(RenderTarget.JSON) to get the state,
then syncs it to JavaScript for rendering.
"""

from __future__ import annotations

import json
import pathlib
from typing import TYPE_CHECKING, Any, Callable, Generic, TypeVar

from agents.i.reactive.signal import Signal
from agents.i.reactive.widget import KgentsWidget, RenderTarget

if TYPE_CHECKING:
    pass

S = TypeVar("S")

# Path to ESM module
_ESM_PATH = pathlib.Path(__file__).parent / "marimo_esm" / "widget.js"
_CSS_PATH = pathlib.Path(__file__).parent / "marimo_esm" / "widget.css"


def _load_esm() -> str:
    """Load ESM module from file."""
    if _ESM_PATH.exists():
        return _ESM_PATH.read_text()
    # Fallback minimal ESM if file not found
    return """
    function render({ model, el }) {
        const state = JSON.parse(model.get("_state_json") || "{}");
        el.innerHTML = `<pre>${JSON.stringify(state, null, 2)}</pre>`;
        model.on("change:_state_json", () => {
            const newState = JSON.parse(model.get("_state_json") || "{}");
            el.innerHTML = `<pre>${JSON.stringify(newState, null, 2)}</pre>`;
        });
    }
    export default { render };
    """


def _load_css() -> str:
    """Load CSS from file."""
    if _CSS_PATH.exists():
        return _CSS_PATH.read_text()
    return ""


try:
    import anywidget
    import traitlets

    class MarimoAdapter(anywidget.AnyWidget, Generic[S]):  # type: ignore[misc]
        """
        Wraps any KgentsWidget for marimo/Jupyter rendering via anywidget.

        Architecture:
            KgentsWidget.state (Signal[S])
                ↓ subscribe
            MarimoAdapter._state_json (traitlet, sync=True)
                ↓ anywidget protocol
            JavaScript model.get("_state_json")
                ↓ render()
            DOM element

        The adapter:
        1. Projects widget state to JSON
        2. Syncs JSON to JavaScript via traitlets
        3. JavaScript renders based on widget type

        Example:
            from agents.i.reactive.primitives.agent_card import (
                AgentCardWidget,
                AgentCardState,
            )
            from agents.i.reactive.adapters import MarimoAdapter

            card = AgentCardWidget(AgentCardState(
                agent_id="kgent-1",
                name="Kent's Assistant",
                phase="active",
            ))

            import marimo as mo
            mo.ui.anywidget(MarimoAdapter(card))
        """

        # ESM module for rendering (loaded from file)
        _esm = traitlets.Unicode(_load_esm()).tag(sync=True)
        _css = traitlets.Unicode(_load_css()).tag(sync=True)

        # Synced state (JSON-serialized widget projection)
        _state_json = traitlets.Unicode("{}").tag(sync=True)
        _widget_type = traitlets.Unicode("generic").tag(sync=True)
        _widget_id = traitlets.Unicode("").tag(sync=True)

        def __init__(self, kgents_widget: KgentsWidget[S]) -> None:
            """
            Create a MarimoAdapter.

            Args:
                kgents_widget: The KgentsWidget to wrap
            """
            super().__init__()
            self._kgents_widget = kgents_widget
            self._unsubscribe: Callable[[], None] | None = None
            self._sync_state()
            self._subscribe_to_signal()

        @property
        def kgents_widget(self) -> KgentsWidget[S]:
            """Get the wrapped KgentsWidget."""
            return self._kgents_widget

        def _sync_state(self) -> None:
            """Sync KgentsWidget state to traitlet."""
            projection = self._kgents_widget.project(RenderTarget.JSON)

            if isinstance(projection, dict):
                self._state_json = json.dumps(projection, default=str)
                self._widget_type = projection.get("type", "generic")
                # Extract widget ID if available
                widget_id = projection.get("agent_id", projection.get("id", ""))
                self._widget_id = str(widget_id)
            else:
                self._state_json = json.dumps({"value": projection}, default=str)
                self._widget_type = "generic"
                self._widget_id = ""

        def _subscribe_to_signal(self) -> None:
            """Subscribe to Signal changes."""
            if hasattr(self._kgents_widget, "state"):
                state = getattr(self._kgents_widget, "state")
                if isinstance(state, Signal):
                    self._unsubscribe = state.subscribe(self._on_state_change)

        def _on_state_change(self, _: Any) -> None:
            """Handle state changes from the KgentsWidget."""
            self._sync_state()

        def refresh(self) -> None:
            """Force a refresh of the widget state."""
            self._sync_state()

        def close(self) -> None:
            """Clean up subscriptions when widget is closed."""
            if self._unsubscribe:
                self._unsubscribe()
                self._unsubscribe = None
            super().close()

except ImportError:
    # Fallback when anywidget is not installed
    class MarimoAdapter(Generic[S]):  # type: ignore[no-redef]
        """
        Fallback MarimoAdapter when anywidget is not installed.

        Returns HTML string representation instead of interactive widget.
        """

        def __init__(self, kgents_widget: KgentsWidget[S]) -> None:
            self._kgents_widget = kgents_widget

        @property
        def kgents_widget(self) -> KgentsWidget[S]:
            return self._kgents_widget

        def _repr_html_(self) -> str:
            """Return HTML representation for Jupyter display."""
            return str(self._kgents_widget.project(RenderTarget.MARIMO))

        def refresh(self) -> None:
            """No-op for fallback."""
            pass

        def close(self) -> None:
            """No-op for fallback."""
            pass


def create_marimo_adapter(widget: KgentsWidget[S]) -> MarimoAdapter[S]:
    """
    Create a Marimo adapter for a KgentsWidget.

    Args:
        widget: The KgentsWidget to wrap

    Returns:
        MarimoAdapter that can be used with marimo.ui.anywidget()
    """
    return MarimoAdapter(widget)


def is_anywidget_available() -> bool:
    """Check if anywidget is available."""
    try:
        import anywidget

        return True
    except ImportError:
        return False
