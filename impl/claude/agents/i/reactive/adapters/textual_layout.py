"""
FlexContainer: Connect FlexLayout to Textual containers.

Maps FlexLayout properties to Textual CSS layout rules.

Usage:
    from agents.i.reactive.adapters import FlexContainer
    from agents.i.reactive.pipeline.layout import FlexLayout, FlexDirection

    # Create a flex layout
    layout = FlexLayout(
        direction=FlexDirection.ROW,
        gap=2,
        justify=FlexAlign.SPACE_BETWEEN,
    )

    # Create the Textual container
    container = FlexContainer(layout)

    # Add widgets in compose()
    with container:
        yield child1
        yield child2
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from textual.containers import Container, Horizontal, Vertical
from textual.widget import Widget

from agents.i.reactive.pipeline.layout import (
    Constraints,
    FlexAlign,
    FlexDirection,
    FlexLayout,
    FlexWrap,
    LayoutNode,
    LayoutRect,
)

if TYPE_CHECKING:
    from textual.app import ComposeResult
    from textual.events import Resize


class FlexContainer(Container):
    """
    Textual container using FlexLayout for positioning.

    Maps FlexLayout semantics to Textual CSS:
    - direction → layout: horizontal/vertical
    - gap → padding between children
    - justify → align-horizontal/align-vertical
    - wrap → (limited support via overflow)

    Example:
        layout = FlexLayout(
            direction=FlexDirection.ROW,
            gap=1,
            justify=FlexAlign.CENTER,
        )

        class MyScreen(Screen):
            def compose(self) -> ComposeResult:
                with FlexContainer(layout):
                    yield Button("A")
                    yield Button("B")
                    yield Button("C")
    """

    def __init__(
        self,
        layout: FlexLayout,
        *,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        """
        Create a FlexContainer.

        Args:
            layout: FlexLayout configuration
            name: Textual widget name
            id: Textual widget ID
            classes: Textual CSS classes
        """
        super().__init__(name=name, id=id, classes=classes)
        self._layout = layout
        self._computed_rects: dict[str, LayoutRect] = {}

    @property
    def flex_layout(self) -> FlexLayout:
        """Get the FlexLayout configuration."""
        return self._layout

    def get_css_styles(self) -> str:
        """Generate CSS rules based on FlexLayout configuration."""
        styles: list[str] = []

        # Direction
        if self._layout.direction in (FlexDirection.ROW, FlexDirection.ROW_REVERSE):
            styles.append("layout: horizontal;")
        else:
            styles.append("layout: vertical;")

        # Gap - use grid-gutter if available, or padding
        if self._layout.gap > 0:
            styles.append(f"grid-gutter: {self._layout.gap};")

        # Justify (main axis alignment)
        justify_map = {
            FlexAlign.START: "left" if self._is_row else "top",
            FlexAlign.END: "right" if self._is_row else "bottom",
            FlexAlign.CENTER: "center",
            FlexAlign.SPACE_BETWEEN: "center",  # CSS approximation
            FlexAlign.SPACE_AROUND: "center",
            FlexAlign.SPACE_EVENLY: "center",
        }
        justify = justify_map.get(self._layout.justify, "left")
        if self._is_row:
            styles.append(f"align-horizontal: {justify};")
        else:
            styles.append(f"align-vertical: {justify};")

        # Align (cross axis)
        align_map = {
            FlexAlign.START: "top" if self._is_row else "left",
            FlexAlign.END: "bottom" if self._is_row else "right",
            FlexAlign.CENTER: "center",
            FlexAlign.STRETCH: "center",  # Stretch needs different handling
        }
        align = align_map.get(self._layout.align, "top")
        if self._is_row:
            styles.append(f"align-vertical: {align};")
        else:
            styles.append(f"align-horizontal: {align};")

        return " ".join(styles)

    @property
    def _is_row(self) -> bool:
        """Check if layout direction is row-based."""
        return self._layout.direction in (FlexDirection.ROW, FlexDirection.ROW_REVERSE)

    def on_mount(self) -> None:
        """Apply CSS styles on mount."""
        css = self.get_css_styles()
        # Dynamic styles are set via inline styles
        self.styles.merge(self.styles.parse(css, ("inline", "")))

    def on_resize(self, event: Resize) -> None:
        """Recompute layout on resize."""
        self._recompute_layout(event.size.width, event.size.height)

    def _recompute_layout(self, width: int, height: int) -> None:
        """Recompute FlexLayout and cache rects."""
        self._layout.compute(width, height)
        self._computed_rects = {child.id: child.rect for child in self._layout.children}

    def get_child_rect(self, child_id: str) -> LayoutRect | None:
        """Get computed rect for a child by ID."""
        return self._computed_rects.get(child_id)


class ResponsiveFlexContainer(FlexContainer):
    """
    FlexContainer with responsive breakpoint support.

    Switches between row/column based on container width.

    Example:
        # Row layout above 80 chars, column below
        container = ResponsiveFlexContainer(
            layout=FlexLayout(direction=FlexDirection.ROW),
            breakpoint=80,
            narrow_direction=FlexDirection.COLUMN,
        )
    """

    def __init__(
        self,
        layout: FlexLayout,
        *,
        breakpoint: int = 80,
        narrow_direction: FlexDirection = FlexDirection.COLUMN,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        super().__init__(layout, name=name, id=id, classes=classes)
        self._breakpoint = breakpoint
        self._narrow_direction = narrow_direction
        self._wide_direction = layout.direction
        self._current_narrow = False

    def on_resize(self, event: Resize) -> None:
        """Handle resize with responsive direction switch."""
        is_narrow = event.size.width < self._breakpoint

        if is_narrow != self._current_narrow:
            self._current_narrow = is_narrow
            if is_narrow:
                self._layout.direction = self._narrow_direction
            else:
                self._layout.direction = self._wide_direction
            # Reapply CSS
            self.styles.merge(self.styles.parse(self.get_css_styles(), ("inline", "")))

        super().on_resize(event)


def create_flex_container(
    direction: FlexDirection = FlexDirection.ROW,
    gap: int = 0,
    justify: FlexAlign = FlexAlign.START,
    align: FlexAlign = FlexAlign.STRETCH,
    wrap: FlexWrap = FlexWrap.NO_WRAP,
    *,
    name: str | None = None,
    id: str | None = None,
    classes: str | None = None,
) -> FlexContainer:
    """
    Create a FlexContainer with specified properties.

    Args:
        direction: Layout direction
        gap: Gap between items
        justify: Main axis alignment
        align: Cross axis alignment
        wrap: Wrap behavior
        name: Textual widget name
        id: Textual widget ID
        classes: Textual CSS classes

    Returns:
        Configured FlexContainer
    """
    layout = FlexLayout(
        direction=direction,
        wrap=wrap,
        justify=justify,
        align=align,
        gap=gap,
    )
    return FlexContainer(layout, name=name, id=id, classes=classes)


def flex_row(
    gap: int = 0,
    justify: FlexAlign = FlexAlign.START,
    align: FlexAlign = FlexAlign.CENTER,
    **kwargs: Any,
) -> FlexContainer:
    """Create a horizontal flex container."""
    return create_flex_container(
        direction=FlexDirection.ROW,
        gap=gap,
        justify=justify,
        align=align,
        **kwargs,
    )


def flex_column(
    gap: int = 0,
    justify: FlexAlign = FlexAlign.START,
    align: FlexAlign = FlexAlign.STRETCH,
    **kwargs: Any,
) -> FlexContainer:
    """Create a vertical flex container."""
    return create_flex_container(
        direction=FlexDirection.COLUMN,
        gap=gap,
        justify=justify,
        align=align,
        **kwargs,
    )
