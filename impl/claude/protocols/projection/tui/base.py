"""
TUI Base: Base classes for Textual TUI widgets.

Provides the foundation for all projection TUI components.
"""

from __future__ import annotations

from abc import abstractmethod
from typing import Any, Generic, TypeVar

from rich.console import RenderableType
from textual.reactive import reactive
from textual.widget import Widget

from protocols.projection.schema import WidgetMeta, WidgetStatus

T = TypeVar("T")


class TUIWidget(Widget, Generic[T]):
    """
    Base class for TUI projection widgets.

    Wraps Textual Widget with projection metadata handling.

    Type Parameters:
        T: The state type for this widget.
    """

    # Reactive state
    state: reactive[T | None] = reactive(None)
    meta: reactive[WidgetMeta] = reactive(WidgetMeta())

    def __init__(
        self,
        state: T | None = None,
        meta: WidgetMeta | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initialize TUI widget.

        Args:
            state: Initial widget state.
            meta: Widget metadata (status, cache, error, etc.).
            **kwargs: Additional Textual Widget arguments.
        """
        super().__init__(**kwargs)
        if state is not None:
            self.state = state
        if meta is not None:
            self.meta = meta

    @property
    def is_loading(self) -> bool:
        """Check if widget is in loading state."""
        return self.meta.status == WidgetStatus.LOADING

    @property
    def is_streaming(self) -> bool:
        """Check if widget is streaming."""
        return self.meta.status == WidgetStatus.STREAMING

    @property
    def has_error(self) -> bool:
        """Check if widget has an error."""
        return self.meta.status == WidgetStatus.ERROR and self.meta.error is not None

    @property
    def has_refusal(self) -> bool:
        """Check if widget has a refusal."""
        return self.meta.status == WidgetStatus.REFUSAL and self.meta.refusal is not None

    @property
    def is_cached(self) -> bool:
        """Check if response is cached."""
        return self.meta.cache is not None and self.meta.cache.is_cached

    @abstractmethod
    def render_content(self) -> RenderableType:
        """
        Render the widget content.

        Returns:
            Rich renderable (str, Text, Panel, etc.).
        """
        ...

    def compose(self) -> Any:
        """Textual compose method - subclasses should override if needed."""
        yield from []


class TUIProjector:
    """
    Projects widget states to Textual TUI.

    Handles widget creation and state updates for the TUI surface.
    """

    @staticmethod
    def create_widget(
        widget_type: str, state: Any, meta: WidgetMeta | None = None
    ) -> "TUIWidget[Any]":
        """
        Create a TUI widget from type and state.

        Args:
            widget_type: Widget type name (text, progress, table, etc.).
            state: Widget state data.
            meta: Optional widget metadata.

        Returns:
            Configured TUI widget.

        Raises:
            ValueError: If widget type is unknown.
        """
        from protocols.projection.tui.progress import TUIProgressWidget
        from protocols.projection.tui.stream import TUIStreamWidget
        from protocols.projection.tui.table import TUITableWidget
        from protocols.projection.tui.text import TUITextWidget

        widget_map = {
            "text": TUITextWidget,
            "progress": TUIProgressWidget,
            "table": TUITableWidget,
            "stream": TUIStreamWidget,
        }

        widget_class = widget_map.get(widget_type.lower())
        if widget_class is None:
            raise ValueError(f"Unknown widget type: {widget_type}")

        return widget_class(state=state, meta=meta)
