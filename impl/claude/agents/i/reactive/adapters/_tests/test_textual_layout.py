"""Tests for FlexContainer - FlexLayout → Textual bridge."""

from __future__ import annotations

import pytest
from agents.i.reactive.adapters.textual_layout import (
    FlexContainer,
    ResponsiveFlexContainer,
    create_flex_container,
    flex_column,
    flex_row,
)
from agents.i.reactive.pipeline.layout import (
    Constraints,
    FlexAlign,
    FlexDirection,
    FlexLayout,
    FlexWrap,
    LayoutNode,
)

# =============================================================================
# FlexContainer Creation Tests
# =============================================================================


class TestFlexContainerCreation:
    """Test FlexContainer creation."""

    def test_create_with_layout(self) -> None:
        """Create container with FlexLayout."""
        layout = FlexLayout(direction=FlexDirection.ROW)
        container = FlexContainer(layout)

        assert container.layout is layout

    def test_create_with_column_layout(self) -> None:
        """Create container with column direction."""
        layout = FlexLayout(direction=FlexDirection.COLUMN)
        container = FlexContainer(layout)

        assert container.layout.direction == FlexDirection.COLUMN

    def test_create_with_name(self) -> None:
        """Create container with name."""
        layout = FlexLayout()
        container = FlexContainer(layout, name="my-flex")

        assert container.name == "my-flex"

    def test_create_with_id(self) -> None:
        """Create container with ID."""
        layout = FlexLayout()
        container = FlexContainer(layout, id="flex-1")

        assert container.id == "flex-1"

    def test_create_with_classes(self) -> None:
        """Create container with CSS classes."""
        layout = FlexLayout()
        container = FlexContainer(layout, classes="flex card")

        assert "flex" in container.classes
        assert "card" in container.classes


# =============================================================================
# CSS Generation Tests
# =============================================================================


class TestFlexContainerCSS:
    """Test CSS generation from FlexLayout."""

    def test_row_direction_css(self) -> None:
        """Row direction generates horizontal layout."""
        layout = FlexLayout(direction=FlexDirection.ROW)
        container = FlexContainer(layout)

        css = container.get_css_styles()
        assert "layout: horizontal" in css

    def test_column_direction_css(self) -> None:
        """Column direction generates vertical layout."""
        layout = FlexLayout(direction=FlexDirection.COLUMN)
        container = FlexContainer(layout)

        css = container.get_css_styles()
        assert "layout: vertical" in css

    def test_row_reverse_css(self) -> None:
        """Row reverse generates horizontal layout."""
        layout = FlexLayout(direction=FlexDirection.ROW_REVERSE)
        container = FlexContainer(layout)

        css = container.get_css_styles()
        assert "layout: horizontal" in css

    def test_column_reverse_css(self) -> None:
        """Column reverse generates vertical layout."""
        layout = FlexLayout(direction=FlexDirection.COLUMN_REVERSE)
        container = FlexContainer(layout)

        css = container.get_css_styles()
        assert "layout: vertical" in css

    def test_gap_css(self) -> None:
        """Gap generates grid-gutter."""
        layout = FlexLayout(gap=2)
        container = FlexContainer(layout)

        css = container.get_css_styles()
        assert "grid-gutter: 2" in css

    def test_no_gap_css(self) -> None:
        """No gap omits grid-gutter."""
        layout = FlexLayout(gap=0)
        container = FlexContainer(layout)

        css = container.get_css_styles()
        assert "grid-gutter" not in css


class TestFlexAlignCSS:
    """Test alignment CSS generation."""

    def test_justify_start_row(self) -> None:
        """Justify start in row generates left align."""
        layout = FlexLayout(direction=FlexDirection.ROW, justify=FlexAlign.START)
        container = FlexContainer(layout)

        css = container.get_css_styles()
        assert "align-horizontal: left" in css

    def test_justify_end_row(self) -> None:
        """Justify end in row generates right align."""
        layout = FlexLayout(direction=FlexDirection.ROW, justify=FlexAlign.END)
        container = FlexContainer(layout)

        css = container.get_css_styles()
        assert "align-horizontal: right" in css

    def test_justify_center_row(self) -> None:
        """Justify center in row generates center align."""
        layout = FlexLayout(direction=FlexDirection.ROW, justify=FlexAlign.CENTER)
        container = FlexContainer(layout)

        css = container.get_css_styles()
        assert "align-horizontal: center" in css

    def test_justify_start_column(self) -> None:
        """Justify start in column generates top align."""
        layout = FlexLayout(direction=FlexDirection.COLUMN, justify=FlexAlign.START)
        container = FlexContainer(layout)

        css = container.get_css_styles()
        assert "align-vertical: top" in css

    def test_justify_end_column(self) -> None:
        """Justify end in column generates bottom align."""
        layout = FlexLayout(direction=FlexDirection.COLUMN, justify=FlexAlign.END)
        container = FlexContainer(layout)

        css = container.get_css_styles()
        assert "align-vertical: bottom" in css

    def test_align_center_row(self) -> None:
        """Align center in row generates vertical center."""
        layout = FlexLayout(direction=FlexDirection.ROW, align=FlexAlign.CENTER)
        container = FlexContainer(layout)

        css = container.get_css_styles()
        assert "align-vertical: center" in css

    def test_align_center_column(self) -> None:
        """Align center in column generates horizontal center."""
        layout = FlexLayout(direction=FlexDirection.COLUMN, align=FlexAlign.CENTER)
        container = FlexContainer(layout)

        css = container.get_css_styles()
        assert "align-horizontal: center" in css


# =============================================================================
# Layout Computation Tests
# =============================================================================


class TestFlexContainerLayout:
    """Test layout computation."""

    def test_recompute_layout(self) -> None:
        """Container recomputes layout on resize."""
        layout = FlexLayout(direction=FlexDirection.ROW)
        layout.add_child(LayoutNode("item-1", Constraints.fixed(10, 3)))
        layout.add_child(LayoutNode("item-2", Constraints.fixed(15, 3)))

        container = FlexContainer(layout)
        container._recompute_layout(80, 24)

        assert "item-1" in container._computed_rects
        assert "item-2" in container._computed_rects

    def test_get_child_rect(self) -> None:
        """Container returns child rect by ID."""
        layout = FlexLayout()
        layout.add_child(LayoutNode("child-1", Constraints.fixed(20, 5)))

        container = FlexContainer(layout)
        container._recompute_layout(80, 24)

        rect = container.get_child_rect("child-1")
        assert rect is not None
        assert rect.width == 20
        # Note: FlexLayout stretches to available height with STRETCH align
        assert rect.height >= 5

    def test_get_missing_child_rect(self) -> None:
        """Container returns None for missing child."""
        layout = FlexLayout()
        container = FlexContainer(layout)

        rect = container.get_child_rect("nonexistent")
        assert rect is None


# =============================================================================
# ResponsiveFlexContainer Tests
# =============================================================================


class TestResponsiveFlexContainer:
    """Test responsive container."""

    def test_create_responsive(self) -> None:
        """Create responsive container."""
        layout = FlexLayout(direction=FlexDirection.ROW)
        container = ResponsiveFlexContainer(
            layout,
            breakpoint=80,
            narrow_direction=FlexDirection.COLUMN,
        )

        assert container._breakpoint == 80
        assert container._narrow_direction == FlexDirection.COLUMN
        assert container._wide_direction == FlexDirection.ROW

    def test_starts_in_wide_mode(self) -> None:
        """Container starts in wide mode."""
        layout = FlexLayout(direction=FlexDirection.ROW)
        container = ResponsiveFlexContainer(layout)

        assert not container._current_narrow

    def test_default_breakpoint(self) -> None:
        """Container has default breakpoint of 80."""
        layout = FlexLayout(direction=FlexDirection.ROW)
        container = ResponsiveFlexContainer(layout)

        assert container._breakpoint == 80


# =============================================================================
# Factory Function Tests
# =============================================================================


class TestCreateFlexContainer:
    """Test create_flex_container factory."""

    def test_creates_container(self) -> None:
        """Factory creates FlexContainer."""
        container = create_flex_container()

        assert isinstance(container, FlexContainer)

    def test_with_direction(self) -> None:
        """Factory sets direction."""
        container = create_flex_container(direction=FlexDirection.COLUMN)

        assert container.layout.direction == FlexDirection.COLUMN

    def test_with_gap(self) -> None:
        """Factory sets gap."""
        container = create_flex_container(gap=4)

        assert container.layout.gap == 4

    def test_with_justify(self) -> None:
        """Factory sets justify."""
        container = create_flex_container(justify=FlexAlign.CENTER)

        assert container.layout.justify == FlexAlign.CENTER

    def test_with_align(self) -> None:
        """Factory sets align."""
        container = create_flex_container(align=FlexAlign.END)

        assert container.layout.align == FlexAlign.END

    def test_with_wrap(self) -> None:
        """Factory sets wrap."""
        container = create_flex_container(wrap=FlexWrap.WRAP)

        assert container.layout.wrap == FlexWrap.WRAP


class TestFlexRowColumn:
    """Test flex_row and flex_column helpers."""

    def test_flex_row(self) -> None:
        """flex_row creates horizontal container."""
        container = flex_row()

        assert container.layout.direction == FlexDirection.ROW

    def test_flex_row_with_gap(self) -> None:
        """flex_row respects gap."""
        container = flex_row(gap=2)

        assert container.layout.gap == 2

    def test_flex_row_default_align(self) -> None:
        """flex_row defaults to center align."""
        container = flex_row()

        assert container.layout.align == FlexAlign.CENTER

    def test_flex_column(self) -> None:
        """flex_column creates vertical container."""
        container = flex_column()

        assert container.layout.direction == FlexDirection.COLUMN

    def test_flex_column_with_gap(self) -> None:
        """flex_column respects gap."""
        container = flex_column(gap=3)

        assert container.layout.gap == 3

    def test_flex_column_default_align(self) -> None:
        """flex_column defaults to stretch align."""
        container = flex_column()

        assert container.layout.align == FlexAlign.STRETCH


# =============================================================================
# Integration Tests
# =============================================================================


class TestFlexContainerIntegration:
    """Test FlexContainer integration scenarios."""

    def test_row_layout_with_children(self) -> None:
        """Row layout positions children horizontally."""
        layout = FlexLayout(direction=FlexDirection.ROW, gap=1)
        layout.add_child(LayoutNode("a", Constraints.fixed(10, 3)))
        layout.add_child(LayoutNode("b", Constraints.fixed(10, 3)))
        layout.add_child(LayoutNode("c", Constraints.fixed(10, 3)))

        container = FlexContainer(layout)
        container._recompute_layout(80, 24)

        rects = [container.get_child_rect(x) for x in ["a", "b", "c"]]
        assert all(r is not None for r in rects)

        # All should be at same y (horizontal layout)
        assert rects[0].y == rects[1].y == rects[2].y
        # X should increase
        assert rects[0].x < rects[1].x < rects[2].x

    def test_column_layout_with_children(self) -> None:
        """Column layout positions children vertically."""
        layout = FlexLayout(direction=FlexDirection.COLUMN, gap=1)
        layout.add_child(LayoutNode("a", Constraints.fixed(10, 3)))
        layout.add_child(LayoutNode("b", Constraints.fixed(10, 3)))
        layout.add_child(LayoutNode("c", Constraints.fixed(10, 3)))

        container = FlexContainer(layout)
        container._recompute_layout(80, 24)

        rects = [container.get_child_rect(x) for x in ["a", "b", "c"]]
        assert all(r is not None for r in rects)

        # All should be at same x (vertical layout)
        assert rects[0].x == rects[1].x == rects[2].x
        # Y should increase
        assert rects[0].y < rects[1].y < rects[2].y
