"""
ComposableWidget: Widget composition with >> and // operators.

Wave 2.1 Composition System
===========================

Composition is categorically beautiful:
    widget_a >> widget_b  -> HStack (horizontal composition)
    widget_a // widget_b  -> VStack (vertical composition)

Both operators are associative:
    (a >> b) >> c ≡ a >> (b >> c)  (HStack fusion)
    (a // b) // c ≡ a // (b // c)  (VStack fusion)

Theme propagates downward through the composition tree.

Quick Start
-----------
    from agents.i.reactive.composable import HStack, VStack
    from agents.i.reactive.primitives.glyph import GlyphState, GlyphWidget
    from agents.i.reactive.primitives.bar import BarState, BarWidget

    # Horizontal: place widgets side by side
    status = GlyphWidget(GlyphState(char="◉"))
    label = GlyphWidget(GlyphState(char="Active"))
    header = status >> label  # HStack([status, label])

    # Vertical: stack widgets top to bottom
    cpu = BarWidget(BarState(value=0.7, label="CPU"))
    mem = BarWidget(BarState(value=0.4, label="MEM"))
    metrics = cpu // mem  # VStack([cpu, mem])

    # Mixed: create layouts
    dashboard = header // metrics  # VStack([header, metrics])

Performance (1603 tests, stress-verified)
-----------------------------------------
    - 100-widget >> chain: <1s for 200 renders
    - 50-level // nesting: passes stress tests
    - 10x10 grid: correct JSON projection
    - Dashboard composition: 50 iterations in <2s

See Also
--------
    - presets.py: High-level layout functions (metric_row, panel, status_row)
    - widget.py: Base KgentsWidget protocol
    - signal.py: Reactive Signal/Computed/Effect primitives
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Protocol, TypeVar, cast, runtime_checkable

from agents.i.reactive.signal import Signal
from agents.i.reactive.widget import KgentsWidget, RenderTarget

if TYPE_CHECKING:
    from textual.widget import Widget as TextualWidget

    from agents.i.reactive.pipeline.theme import Theme

S = TypeVar("S")
W = TypeVar("W", bound="ComposableWidget")


# =============================================================================
# ComposableWidget Protocol
# =============================================================================


@runtime_checkable
class ComposableWidget(Protocol):
    """
    Protocol for widgets that support >> and // composition operators.

    This is the fundamental composition abstraction:
    - >> creates horizontal stacks (HStack)
    - // creates vertical stacks (VStack)

    Both operators are associative, enabling arbitrary nesting
    without parenthesis ambiguity.
    """

    def project(self, target: RenderTarget) -> Any:
        """Project this widget to a rendering target."""
        ...

    def __rshift__(self, other: ComposableWidget) -> HStack:
        """Horizontal composition: self >> other"""
        ...

    def __floordiv__(self, other: ComposableWidget) -> VStack:
        """Vertical composition: self // other"""
        ...


# =============================================================================
# HStack: Horizontal Composition
# =============================================================================


@dataclass
class HStack(KgentsWidget[None]):
    """
    Horizontal composition container.

    Arranges widgets left-to-right. Created via >> operator:
        widget_a >> widget_b  -> HStack([widget_a, widget_b])

    Associativity: (a >> b) >> c automatically flattens to HStack([a, b, c])
    This is the monoidal property - HStack is the free monoid on widgets.

    Attributes:
        children: List of composed widgets
        gap: Horizontal gap between children (in characters)
        separator: Optional separator string between children
    """

    children: list[ComposableWidget] = field(default_factory=list)
    gap: int = 1
    separator: str | None = None

    # Satisfy KgentsWidget by providing a state signal (even though unused)
    def __post_init__(self) -> None:
        self.state = Signal.of(None)

    def __rshift__(self, other: ComposableWidget) -> HStack:
        """
        Associative horizontal composition.

        If other is an HStack, flatten to preserve associativity:
            (a >> b) >> (c >> d) -> HStack([a, b, c, d])
        """
        if isinstance(other, HStack):
            # Flatten: absorb other's children
            return HStack(
                children=self.children + other.children,
                gap=self.gap,
                separator=self.separator,
            )
        return HStack(
            children=[*self.children, other],
            gap=self.gap,
            separator=self.separator,
        )

    def __floordiv__(self, other: ComposableWidget) -> VStack:
        """Vertical composition: creates VStack with self as first child."""
        return VStack(children=[self, other])

    def project(self, target: RenderTarget, theme: Theme | None = None) -> Any:
        """
        Project all children to target, arranged horizontally.

        Theme propagates to all children.
        """
        if not self.children:
            return "" if target in (RenderTarget.CLI, RenderTarget.MARIMO) else {}

        match target:
            case RenderTarget.CLI:
                return self._to_cli(theme)
            case RenderTarget.TUI:
                return self._to_tui(theme)
            case RenderTarget.MARIMO:
                return self._to_marimo(theme)
            case RenderTarget.JSON:
                return self._to_json(theme)

    def _project_child(
        self, child: ComposableWidget, target: RenderTarget, theme: Theme | None
    ) -> Any:
        """Project a single child with theme if it supports it."""
        # Protocol defines project(target) only; some widgets may accept theme
        # Use duck typing for extended interface
        if hasattr(child.project, "__code__") and "theme" in child.project.__code__.co_varnames:
            return child.project(target, theme=theme)  # type: ignore[call-arg]
        return child.project(target)

    def _to_cli(self, theme: Theme | None) -> str:
        """CLI: Join with spaces or separator."""
        sep = self.separator if self.separator else " " * self.gap
        parts = [str(self._project_child(c, RenderTarget.CLI, theme)) for c in self.children]
        return sep.join(parts)

    def _to_tui(self, theme: Theme | None) -> Any:
        """TUI: Rich Text horizontal concatenation."""
        try:
            from rich.text import Text

            result = Text()
            sep = self.separator if self.separator else " " * self.gap

            for i, child in enumerate(self.children):
                if i > 0:
                    result.append(sep)
                child_text = self._project_child(child, RenderTarget.TUI, theme)
                if isinstance(child_text, Text):
                    result.append_text(child_text)
                else:
                    result.append(str(child_text))

            return result
        except ImportError:
            return self._to_cli(theme)

    def _to_marimo(self, theme: Theme | None) -> str:
        """MARIMO: HTML div with inline-flex."""
        gap_px = self.gap * 8  # Rough character-to-pixel conversion
        parts = [self._project_child(c, RenderTarget.MARIMO, theme) for c in self.children]

        html = f'<div class="kgents-hstack" style="display: inline-flex; gap: {gap_px}px; align-items: center;">'
        html += "".join(str(p) for p in parts)
        html += "</div>"
        return html

    def _to_json(self, theme: Theme | None) -> dict[str, Any]:
        """JSON: Array of child projections."""
        return {
            "type": "hstack",
            "gap": self.gap,
            "separator": self.separator,
            "children": [self._project_child(c, RenderTarget.JSON, theme) for c in self.children],
        }

    def with_gap(self, gap: int) -> HStack:
        """Return new HStack with different gap."""
        return HStack(children=self.children, gap=gap, separator=self.separator)

    def with_separator(self, separator: str) -> HStack:
        """Return new HStack with separator string."""
        return HStack(children=self.children, gap=self.gap, separator=separator)

    def to_textual(self, *, id: str | None = None, classes: str | None = None) -> TextualWidget:
        """
        Convert this HStack to a Textual widget tree.

        Creates a Horizontal container with TextualAdapter-wrapped children.
        Leaf widgets are wrapped in TextualAdapter; nested HStack/VStack recurse.

        Args:
            id: Textual widget ID
            classes: Textual CSS classes

        Returns:
            Textual Horizontal container with children
        """
        from textual.containers import Horizontal

        from agents.i.reactive.adapters.textual_widget import TextualAdapter

        children: list[TextualWidget] = []
        for child in self.children:
            if hasattr(child, "to_textual"):
                # Recursive: HStack/VStack have to_textual()
                children.append(child.to_textual())
            elif isinstance(child, KgentsWidget):
                # Leaf: wrap in TextualAdapter
                children.append(TextualAdapter(child))
            else:
                # Fallback: cast to KgentsWidget for duck typing
                children.append(TextualAdapter(cast(KgentsWidget[Any], child)))

        return Horizontal(*children, id=id, classes=classes)

    def to_marimo(self, *, use_anywidget: bool = True) -> Any:
        """
        Convert this HStack to a marimo-compatible widget.

        Args:
            use_anywidget: If True and anywidget available, return MarimoAdapter.
                           Otherwise, return HTML string.

        Returns:
            MarimoAdapter (if anywidget available) or HTML string

        Example:
            dashboard = header >> body >> footer

            # In marimo cell
            mo.ui.anywidget(dashboard.to_marimo())
            # Or for HTML fallback
            mo.Html(dashboard.to_marimo(use_anywidget=False))
        """
        from agents.i.reactive.adapters.marimo_widget import (
            MarimoAdapter,
            is_anywidget_available,
        )

        if use_anywidget and is_anywidget_available():
            return MarimoAdapter(self)
        return self._to_marimo(None)


# =============================================================================
# VStack: Vertical Composition
# =============================================================================


@dataclass
class VStack(KgentsWidget[None]):
    """
    Vertical composition container.

    Arranges widgets top-to-bottom. Created via // operator:
        widget_a // widget_b  -> VStack([widget_a, widget_b])

    Associativity: (a // b) // c automatically flattens to VStack([a, b, c])

    Attributes:
        children: List of composed widgets
        gap: Vertical gap between children (in lines)
        separator: Optional separator line between children
    """

    children: list[ComposableWidget] = field(default_factory=list)
    gap: int = 0
    separator: str | None = None

    def __post_init__(self) -> None:
        self.state = Signal.of(None)

    def __rshift__(self, other: ComposableWidget) -> HStack:
        """Horizontal composition: creates HStack with self as first child."""
        return HStack(children=[self, other])

    def __floordiv__(self, other: ComposableWidget) -> VStack:
        """
        Associative vertical composition.

        If other is a VStack, flatten to preserve associativity:
            (a // b) // (c // d) -> VStack([a, b, c, d])
        """
        if isinstance(other, VStack):
            # Flatten: absorb other's children
            return VStack(
                children=self.children + other.children,
                gap=self.gap,
                separator=self.separator,
            )
        return VStack(
            children=[*self.children, other],
            gap=self.gap,
            separator=self.separator,
        )

    def project(self, target: RenderTarget, theme: Theme | None = None) -> Any:
        """
        Project all children to target, arranged vertically.

        Theme propagates to all children.
        """
        if not self.children:
            return "" if target in (RenderTarget.CLI, RenderTarget.MARIMO) else {}

        match target:
            case RenderTarget.CLI:
                return self._to_cli(theme)
            case RenderTarget.TUI:
                return self._to_tui(theme)
            case RenderTarget.MARIMO:
                return self._to_marimo(theme)
            case RenderTarget.JSON:
                return self._to_json(theme)

    def _project_child(
        self, child: ComposableWidget, target: RenderTarget, theme: Theme | None
    ) -> Any:
        """Project a single child with theme if it supports it."""
        # Protocol defines project(target) only; some widgets may accept theme
        # Use duck typing for extended interface
        if hasattr(child.project, "__code__") and "theme" in child.project.__code__.co_varnames:
            return child.project(target, theme=theme)  # type: ignore[call-arg]
        return child.project(target)

    def _to_cli(self, theme: Theme | None) -> str:
        """CLI: Join with newlines."""
        sep_lines = "\n" * (self.gap + 1)
        if self.separator:
            sep_lines = f"\n{self.separator}\n"

        parts = [str(self._project_child(c, RenderTarget.CLI, theme)) for c in self.children]
        return sep_lines.join(parts)

    def _to_tui(self, theme: Theme | None) -> Any:
        """TUI: Rich Group for vertical layout."""
        try:
            from rich.console import Group

            parts = [self._project_child(c, RenderTarget.TUI, theme) for c in self.children]
            return Group(*parts)
        except ImportError:
            return self._to_cli(theme)

    def _to_marimo(self, theme: Theme | None) -> str:
        """MARIMO: HTML div with flex-column."""
        gap_px = self.gap * 16  # Line height approximation
        parts = [self._project_child(c, RenderTarget.MARIMO, theme) for c in self.children]

        html = f'<div class="kgents-vstack" style="display: flex; flex-direction: column; gap: {gap_px}px;">'
        html += "".join(str(p) for p in parts)
        html += "</div>"
        return html

    def _to_json(self, theme: Theme | None) -> dict[str, Any]:
        """JSON: Array of child projections."""
        return {
            "type": "vstack",
            "gap": self.gap,
            "separator": self.separator,
            "children": [self._project_child(c, RenderTarget.JSON, theme) for c in self.children],
        }

    def with_gap(self, gap: int) -> VStack:
        """Return new VStack with different gap."""
        return VStack(children=self.children, gap=gap, separator=self.separator)

    def with_separator(self, separator: str) -> VStack:
        """Return new VStack with separator line."""
        return VStack(children=self.children, gap=self.gap, separator=separator)

    def to_textual(self, *, id: str | None = None, classes: str | None = None) -> TextualWidget:
        """
        Convert this VStack to a Textual widget tree.

        Creates a Vertical container with TextualAdapter-wrapped children.
        Leaf widgets are wrapped in TextualAdapter; nested HStack/VStack recurse.

        Args:
            id: Textual widget ID
            classes: Textual CSS classes

        Returns:
            Textual Vertical container with children
        """
        from textual.containers import Vertical

        from agents.i.reactive.adapters.textual_widget import TextualAdapter

        children: list[TextualWidget] = []
        for child in self.children:
            if hasattr(child, "to_textual"):
                # Recursive: HStack/VStack have to_textual()
                children.append(child.to_textual())
            elif isinstance(child, KgentsWidget):
                # Leaf: wrap in TextualAdapter
                children.append(TextualAdapter(child))
            else:
                # Fallback: cast to KgentsWidget for duck typing
                children.append(TextualAdapter(cast(KgentsWidget[Any], child)))

        return Vertical(*children, id=id, classes=classes)

    def to_marimo(self, *, use_anywidget: bool = True) -> Any:
        """
        Convert this VStack to a marimo-compatible widget.

        Args:
            use_anywidget: If True and anywidget available, return MarimoAdapter.
                           Otherwise, return HTML string.

        Returns:
            MarimoAdapter (if anywidget available) or HTML string

        Example:
            dashboard = header // body // footer

            # In marimo cell
            mo.ui.anywidget(dashboard.to_marimo())
            # Or for HTML fallback
            mo.Html(dashboard.to_marimo(use_anywidget=False))
        """
        from agents.i.reactive.adapters.marimo_widget import (
            MarimoAdapter,
            is_anywidget_available,
        )

        if use_anywidget and is_anywidget_available():
            return MarimoAdapter(self)
        return self._to_marimo(None)


# =============================================================================
# ComposableMixin: Add >> and // to existing widgets
# =============================================================================


class ComposableMixin:
    """
    Mixin that adds >> and // composition operators to any KgentsWidget.

    Usage:
        class MyWidget(ComposableMixin, KgentsWidget[MyState]):
            ...

    The mixin adds:
        __rshift__: widget >> other -> HStack
        __floordiv__: widget // other -> VStack
    """

    def __rshift__(self, other: ComposableWidget) -> HStack:
        """Horizontal composition: self >> other"""
        self_widget = cast(ComposableWidget, self)
        if isinstance(other, HStack):
            # Put self at front, absorb other's children
            return HStack(children=[self_widget, *other.children])
        return HStack(children=[self_widget, other])

    def __floordiv__(self, other: ComposableWidget) -> VStack:
        """Vertical composition: self // other"""
        self_widget = cast(ComposableWidget, self)
        if isinstance(other, VStack):
            # Put self at front, absorb other's children
            return VStack(children=[self_widget, *other.children])
        return VStack(children=[self_widget, other])


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    "ComposableWidget",
    "ComposableMixin",
    "HStack",
    "VStack",
]
