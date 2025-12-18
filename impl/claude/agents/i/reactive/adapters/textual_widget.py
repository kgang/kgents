"""
TextualAdapter: Bridge KgentsWidget to Textual Widget.

The TextualAdapter wraps any KgentsWidget and renders it as a Textual Widget.
It subscribes to state changes and automatically re-renders when the state updates.

This is the core adapter - all other adapters build on this foundation.

Usage:
    from agents.i.reactive.adapters import TextualAdapter

    # Wrap a KgentsWidget
    adapter = TextualAdapter(my_widget)

    # Use in Textual compose()
    yield adapter

The adapter calls widget.project(RenderTarget.TUI) to get the output.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Callable, Generic, TypeVar

from rich.text import Text
from textual.widget import Widget
from textual.widgets import Static

from agents.i.reactive.signal import Signal
from agents.i.reactive.widget import KgentsWidget, RenderTarget

if TYPE_CHECKING:
    from textual.app import ComposeResult
    from textual.reactive import reactive


S = TypeVar("S")


class TextualAdapter(Static, Generic[S]):
    """
    Wraps a KgentsWidget for Textual rendering.

    The adapter:
    1. Subscribes to the widget's state Signal
    2. Re-renders when state changes
    3. Calls project(TUI) to get output

    Example:
        class CounterWidget(KgentsWidget[CounterState]):
            def __init__(self) -> None:
                self.state = Signal.of(CounterState(count=0))

            def project(self, target: RenderTarget) -> str:
                return f"Count: {self.state.value.count}"

        counter = CounterWidget()
        adapter = TextualAdapter(counter)

        # In your App.compose():
        yield adapter
    """

    DEFAULT_CSS = """
    TextualAdapter {
        height: auto;
        width: auto;
    }
    """

    def __init__(
        self,
        kgents_widget: KgentsWidget[S],
        *,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        """
        Create a TextualAdapter.

        Args:
            kgents_widget: The KgentsWidget to wrap
            name: Textual widget name
            id: Textual widget ID
            classes: Textual CSS classes
        """
        super().__init__(name=name, id=id, classes=classes)
        self._kgents_widget = kgents_widget
        self._unsubscribe: Callable[[], None] | None = None
        self._render_version: int = 0

    @property
    def kgents_widget(self) -> KgentsWidget[S]:
        """Get the wrapped KgentsWidget."""
        return self._kgents_widget

    def on_mount(self) -> None:
        """Subscribe to state changes when mounted."""
        # Initial render
        self._update_content()

        # Subscribe to state changes if widget has a Signal state
        if hasattr(self._kgents_widget, "state"):
            state = getattr(self._kgents_widget, "state")
            if isinstance(state, Signal):
                self._unsubscribe = state.subscribe(self._on_state_change)

    def on_unmount(self) -> None:
        """Unsubscribe when unmounted."""
        if self._unsubscribe:
            self._unsubscribe()
            self._unsubscribe = None

    def _on_state_change(self, _: Any) -> None:
        """Handle state changes from the KgentsWidget."""
        self._update_content()

    def _update_content(self) -> None:
        """Project the widget and update display."""
        # Get TUI projection
        output = self._kgents_widget.project(RenderTarget.TUI)

        # Static.update() accepts any Rich renderable (str, Text, Panel, etc.)
        # We pass it directly and track a version for change detection
        # since Rich objects don't compare well
        self._render_version = getattr(self, "_render_version", 0) + 1
        self.update(output)

    def refresh_widget(self) -> None:
        """Force a refresh of the widget."""
        self._update_content()


class ReactiveTextualAdapter(Static, Generic[S]):
    """
    TextualAdapter with Textual's native reactive system bridge.

    This variant uses Textual's reactive() for the bridge, which may
    integrate better with Textual's compositor but adds overhead.

    Use TextualAdapter for most cases. Use ReactiveTextualAdapter
    if you need tighter Textual reactive integration.
    """

    # Use Textual's reactive for bridge
    _reactive_version: int = 0  # Triggers re-render on increment

    DEFAULT_CSS = """
    ReactiveTextualAdapter {
        height: auto;
        width: auto;
    }
    """

    def __init__(
        self,
        kgents_widget: KgentsWidget[S],
        *,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        super().__init__(name=name, id=id, classes=classes)
        self._kgents_widget = kgents_widget
        self._unsubscribe: Callable[[], None] | None = None
        self._reactive_version = 0

    @property
    def kgents_widget(self) -> KgentsWidget[S]:
        return self._kgents_widget

    def on_mount(self) -> None:
        self._update_content()
        if hasattr(self._kgents_widget, "state"):
            state = getattr(self._kgents_widget, "state")
            if isinstance(state, Signal):
                self._unsubscribe = state.subscribe(self._on_state_change)

    def on_unmount(self) -> None:
        if self._unsubscribe:
            self._unsubscribe()
            self._unsubscribe = None

    def _on_state_change(self, _: Any) -> None:
        # Increment reactive version to trigger Textual's refresh
        self._reactive_version += 1
        self._update_content()

    def _update_content(self) -> None:
        output = self._kgents_widget.project(RenderTarget.TUI)
        # Static.update() accepts any Rich renderable
        self.update(output)


def create_textual_adapter(
    widget: KgentsWidget[S],
    *,
    name: str | None = None,
    id: str | None = None,
    classes: str | None = None,
    use_reactive: bool = False,
) -> TextualAdapter[S] | ReactiveTextualAdapter[S]:
    """
    Create a Textual adapter for a KgentsWidget.

    Args:
        widget: The KgentsWidget to wrap
        name: Textual widget name
        id: Textual widget ID
        classes: Textual CSS classes
        use_reactive: Use ReactiveTextualAdapter variant

    Returns:
        TextualAdapter or ReactiveTextualAdapter
    """
    if use_reactive:
        return ReactiveTextualAdapter(widget, name=name, id=id, classes=classes)
    return TextualAdapter(widget, name=name, id=id, classes=classes)


def to_textual(
    widget: Any,
    *,
    id: str | None = None,
    classes: str | None = None,
) -> Widget:
    """
    Convert any KgentsWidget or composed widget to a Textual widget tree.

    This is the universal entry point for composed widget conversion:
    - HStack/VStack: calls to_textual() recursively
    - KgentsWidget: wraps in TextualAdapter
    - Already a Textual Widget: returns as-is

    Args:
        widget: Any KgentsWidget, HStack, VStack, or Textual Widget
        id: Textual widget ID (for composed widgets)
        classes: Textual CSS classes

    Returns:
        Textual Widget (Horizontal, Vertical, or TextualAdapter)

    Example:
        # From composition
        dashboard = header // (cpu >> mem) // footer
        textual_tree = to_textual(dashboard, id="dash")

        # In compose()
        yield textual_tree
    """
    # Check for to_textual method (HStack, VStack)
    if hasattr(widget, "to_textual"):
        result: Widget = widget.to_textual(id=id, classes=classes)
        return result

    # KgentsWidget: wrap in TextualAdapter
    if isinstance(widget, KgentsWidget):
        return TextualAdapter(widget, id=id, classes=classes)

    # Already a Textual Widget
    if isinstance(widget, Widget):
        return widget

    # Fallback: try TextualAdapter (duck typing for non-standard widgets)
    return TextualAdapter(widget, id=id, classes=classes)


def to_marimo(
    widget: Any,
    *,
    use_anywidget: bool = True,
) -> Any:
    """
    Convert any KgentsWidget or composed widget to a marimo-compatible output.

    This is the universal entry point for marimo rendering:
    - HStack/VStack: calls to_marimo() for MarimoAdapter or HTML
    - KgentsWidget: wraps in MarimoAdapter
    - Already has _repr_html_: returns as-is

    Args:
        widget: Any KgentsWidget, HStack, VStack, or marimo-compatible object
        use_anywidget: If True, prefer anywidget for interactive rendering

    Returns:
        MarimoAdapter (if anywidget available) or HTML string

    Example:
        # From composition
        dashboard = header // (cpu >> mem) // footer

        # In marimo cell
        mo.ui.anywidget(to_marimo(dashboard))
        # Or for HTML
        mo.Html(to_marimo(dashboard, use_anywidget=False))
    """
    from agents.i.reactive.adapters.marimo_widget import (
        MarimoAdapter,
        is_anywidget_available,
    )
    from agents.i.reactive.composable import HStack, VStack

    # Check for HStack/VStack which have use_anywidget parameter
    if isinstance(widget, (HStack, VStack)):
        return widget.to_marimo(use_anywidget=use_anywidget)

    # KgentsWidget: wrap in MarimoAdapter or project to MARIMO
    if isinstance(widget, KgentsWidget):
        if use_anywidget and is_anywidget_available():
            return MarimoAdapter(widget)
        return widget.project(RenderTarget.MARIMO)

    # Already marimo-compatible (_repr_html_)
    if hasattr(widget, "_repr_html_"):
        return widget

    # Fallback: string representation
    return str(widget)
