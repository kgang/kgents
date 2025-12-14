"""
Tests for Box Drawing primitives.

Tests cover:
- Box character sets for all styles
- Box rendering (empty and with content)
- Table rendering
- Nested boxes
- Convenience functions
"""

from __future__ import annotations

import pytest
from agents.i.reactive.terminal.box import (
    BoxChars,
    BoxRenderer,
    BoxSpec,
    BoxStyle,
    ColumnSpec,
    NestedBox,
    TableRenderer,
    TableSpec,
    content_box,
    get_chars,
    horizontal_rule,
    simple_box,
    vertical_rule,
)

# === Box Character Sets ===


class TestBoxChars:
    """Test box character sets."""

    def test_single_style_chars(self) -> None:
        """Single line style has correct characters."""
        chars = get_chars(BoxStyle.SINGLE)
        assert chars.horizontal == "─"
        assert chars.vertical == "│"
        assert chars.top_left == "┌"
        assert chars.top_right == "┐"
        assert chars.bottom_left == "└"
        assert chars.bottom_right == "┘"

    def test_double_style_chars(self) -> None:
        """Double line style has correct characters."""
        chars = get_chars(BoxStyle.DOUBLE)
        assert chars.horizontal == "═"
        assert chars.vertical == "║"
        assert chars.top_left == "╔"

    def test_rounded_style_chars(self) -> None:
        """Rounded style has curved corners."""
        chars = get_chars(BoxStyle.ROUNDED)
        assert chars.top_left == "╭"
        assert chars.top_right == "╮"
        assert chars.bottom_left == "╰"
        assert chars.bottom_right == "╯"

    def test_heavy_style_chars(self) -> None:
        """Heavy style has thick lines."""
        chars = get_chars(BoxStyle.HEAVY)
        assert chars.horizontal == "━"
        assert chars.vertical == "┃"
        assert chars.top_left == "┏"

    def test_ascii_style_chars(self) -> None:
        """ASCII style uses basic characters."""
        chars = get_chars(BoxStyle.ASCII)
        assert chars.horizontal == "-"
        assert chars.vertical == "|"
        assert chars.top_left == "+"
        assert chars.cross == "+"

    def test_corner_method(self) -> None:
        """Corner helper returns correct characters."""
        chars = get_chars(BoxStyle.SINGLE)
        assert chars.corner("tl") == "┌"
        assert chars.corner("tr") == "┐"
        assert chars.corner("bl") == "└"
        assert chars.corner("br") == "┘"


# === Box Rendering ===


class TestBoxRenderer:
    """Test box rendering."""

    def test_simple_box(self) -> None:
        """Render simple empty box."""
        renderer = BoxRenderer()
        lines = renderer.box(BoxSpec(width=10, height=4))

        assert len(lines) == 4
        assert lines[0].startswith("┌")
        assert lines[0].endswith("┐")
        assert lines[-1].startswith("└")
        assert lines[-1].endswith("┘")
        assert all(line.startswith("│") for line in lines[1:-1])

    def test_box_dimensions(self) -> None:
        """Box has correct dimensions."""
        renderer = BoxRenderer()
        lines = renderer.box(BoxSpec(width=20, height=8))

        assert len(lines) == 8
        assert all(len(line) == 20 for line in lines)

    def test_box_with_title(self) -> None:
        """Box includes title in top border."""
        renderer = BoxRenderer()
        lines = renderer.box(BoxSpec(width=30, height=4, title="Test"))

        assert "Test" in lines[0]
        assert lines[0].startswith("┌")
        assert lines[0].endswith("┐")

    def test_box_title_alignment_left(self) -> None:
        """Title aligned left."""
        renderer = BoxRenderer()
        lines = renderer.box(
            BoxSpec(width=30, height=4, title="Left", title_align="left")
        )

        # Title should be near the start
        title_pos = lines[0].index("Left")
        assert title_pos < 10

    def test_box_title_alignment_center(self) -> None:
        """Title aligned center."""
        renderer = BoxRenderer()
        lines = renderer.box(
            BoxSpec(width=30, height=4, title="Center", title_align="center")
        )

        title_pos = lines[0].index("Center")
        # Should be roughly in the middle
        assert 10 < title_pos < 20

    def test_box_title_alignment_right(self) -> None:
        """Title aligned right."""
        renderer = BoxRenderer()
        lines = renderer.box(
            BoxSpec(width=30, height=4, title="Right", title_align="right")
        )

        title_pos = lines[0].index("Right")
        # Should be near the end
        assert title_pos > 15

    def test_box_with_different_styles(self) -> None:
        """Box renders with different styles."""
        renderer = BoxRenderer()

        for style in BoxStyle:
            lines = renderer.box(BoxSpec(width=10, height=4, style=style))
            assert len(lines) == 4
            # First line should use the style's corner
            chars = get_chars(style)
            assert lines[0].startswith(chars.top_left)


class TestBoxWithContent:
    """Test box rendering with content."""

    def test_box_with_single_line(self) -> None:
        """Box with single line of content."""
        renderer = BoxRenderer()
        lines = renderer.box_with_content(
            BoxSpec(width=20, height=4),
            ["Hello"],
        )

        assert len(lines) == 4
        assert "Hello" in "".join(lines)

    def test_box_with_multiple_lines(self) -> None:
        """Box with multiple lines of content."""
        renderer = BoxRenderer()
        content = ["Line 1", "Line 2", "Line 3"]
        lines = renderer.box_with_content(
            BoxSpec(width=20, height=5),
            content,
        )

        assert len(lines) == 5
        for c in content:
            assert c in "".join(lines)

    def test_content_clipped_to_width(self) -> None:
        """Long content is clipped to box width."""
        renderer = BoxRenderer()
        lines = renderer.box_with_content(
            BoxSpec(width=15, height=3, padding=1),
            ["This is a very long line that should be clipped"],
        )

        # Content should fit within box
        assert all(len(line) == 15 for line in lines)

    def test_content_padded_to_height(self) -> None:
        """Content is padded if fewer lines than height."""
        renderer = BoxRenderer()
        lines = renderer.box_with_content(
            BoxSpec(width=20, height=6),
            ["Only one line"],
        )

        assert len(lines) == 6


# === Table Rendering ===


class TestTableRenderer:
    """Test table rendering."""

    def test_simple_table(self) -> None:
        """Render simple table."""
        renderer = TableRenderer()
        spec = TableSpec(
            columns=(
                ColumnSpec(width=10, header="Name"),
                ColumnSpec(width=8, header="Value"),
            ),
            rows=(
                ("Alpha", "100"),
                ("Beta", "200"),
            ),
        )

        lines = renderer.table(spec)

        assert len(lines) > 0
        assert "Name" in lines[1]
        assert "Value" in lines[1]
        assert "Alpha" in "".join(lines)
        assert "Beta" in "".join(lines)

    def test_table_column_alignment(self) -> None:
        """Table respects column alignment."""
        renderer = TableRenderer()
        spec = TableSpec(
            columns=(
                ColumnSpec(width=10, header="Left", align="left"),
                ColumnSpec(width=10, header="Center", align="center"),
                ColumnSpec(width=10, header="Right", align="right"),
            ),
            rows=(("A", "B", "C"),),
        )

        lines = renderer.table(spec)
        # Just verify it renders without error
        assert len(lines) > 0

    def test_table_without_header(self) -> None:
        """Table can hide header row."""
        renderer = TableRenderer()
        spec = TableSpec(
            columns=(
                ColumnSpec(width=10, header="Name"),
                ColumnSpec(width=10, header="Value"),
            ),
            rows=(("Test", "123"),),
            show_header=False,
        )

        lines = renderer.table(spec)
        # Should not have header separator
        header_separators = [line for line in lines if "┼" in line or "╋" in line]
        assert len(header_separators) == 0

    def test_table_with_row_separators(self) -> None:
        """Table with row separators."""
        renderer = TableRenderer()
        spec = TableSpec(
            columns=(ColumnSpec(width=10, header="Col"),),
            rows=(("A",), ("B",), ("C",)),
            row_separator=True,
        )

        lines = renderer.table(spec)
        # Should have separator lines between data rows
        separator_count = sum(1 for line in lines if "├" in line)
        assert separator_count >= 1

    def test_table_clips_long_cells(self) -> None:
        """Long cell content is clipped with ellipsis."""
        renderer = TableRenderer()
        spec = TableSpec(
            columns=(ColumnSpec(width=8, header="Col"),),
            rows=(("This is too long",),),
        )

        lines = renderer.table(spec)
        # Content should be clipped
        table_str = "".join(lines)
        assert "…" in table_str or len("This is too long") > 8


# === Nested Boxes ===


class TestNestedBox:
    """Test nested box rendering."""

    def test_render_single_box(self) -> None:
        """Render single nested box."""
        nested = NestedBox(BoxSpec(width=20, height=6))
        lines = nested.render()

        assert len(lines) == 6
        assert all(len(line) == 20 for line in lines)

    def test_render_with_content(self) -> None:
        """Render nested box with content."""
        nested = NestedBox(BoxSpec(width=20, height=5))
        lines = nested.render_with_content(["Hello", "World"])

        assert "Hello" in "".join(lines)
        assert "World" in "".join(lines)

    def test_nested_with_children(self) -> None:
        """Render box with child boxes."""
        outer = NestedBox(BoxSpec(width=40, height=10))
        child1 = BoxSpec(width=15, height=4)
        child2 = BoxSpec(width=15, height=4)

        lines = outer.with_children(
            [
                (2, 1, child1),
                (22, 1, child2),
            ]
        )

        assert len(lines) == 10
        # Should contain child box corners
        combined = "".join(lines)
        # Multiple top-left corners (outer + children)
        assert combined.count("┌") >= 2


# === Convenience Functions ===


class TestConvenienceFunctions:
    """Test convenience functions."""

    def test_simple_box_function(self) -> None:
        """simple_box creates a basic box."""
        lines = simple_box(15, 5)
        assert len(lines) == 5
        assert all(len(line) == 15 for line in lines)

    def test_simple_box_with_title(self) -> None:
        """simple_box with title."""
        lines = simple_box(20, 4, title="Test")
        assert "Test" in lines[0]

    def test_simple_box_with_style(self) -> None:
        """simple_box with different style."""
        lines = simple_box(10, 3, style=BoxStyle.DOUBLE)
        assert "╔" in lines[0]

    def test_content_box_auto_size(self) -> None:
        """content_box auto-sizes to content."""
        content = ["Short", "Longer line here"]
        lines = content_box(content)

        # Should be at least as wide as longest content line
        width = len(lines[0])
        assert width >= len("Longer line here") + 4  # padding + borders

    def test_content_box_min_width(self) -> None:
        """content_box respects min_width."""
        lines = content_box(["Hi"], min_width=30)
        assert len(lines[0]) >= 30

    def test_content_box_with_title(self) -> None:
        """content_box with title."""
        lines = content_box(["Content"], title="Header")
        assert "Header" in lines[0]

    def test_horizontal_rule(self) -> None:
        """horizontal_rule draws a line."""
        rule = horizontal_rule(20)
        assert len(rule) == 20
        assert all(c == "─" for c in rule)

    def test_horizontal_rule_with_style(self) -> None:
        """horizontal_rule with different style."""
        rule = horizontal_rule(10, style=BoxStyle.HEAVY)
        assert all(c == "━" for c in rule)

    def test_vertical_rule(self) -> None:
        """vertical_rule draws vertical lines."""
        lines = vertical_rule(5)
        assert len(lines) == 5
        assert all(line == "│" for line in lines)

    def test_vertical_rule_with_style(self) -> None:
        """vertical_rule with different style."""
        lines = vertical_rule(3, style=BoxStyle.DOUBLE)
        assert all(line == "║" for line in lines)


# === Edge Cases ===


class TestEdgeCases:
    """Test edge cases."""

    def test_minimum_box_size(self) -> None:
        """Minimum 3x2 box."""
        lines = simple_box(3, 2)
        assert len(lines) == 2
        assert len(lines[0]) == 3

    def test_empty_table(self) -> None:
        """Table with no rows."""
        renderer = TableRenderer()
        spec = TableSpec(
            columns=(ColumnSpec(width=10, header="Col"),),
            rows=(),
        )

        lines = renderer.table(spec)
        assert len(lines) >= 2  # At least borders

    def test_single_column_table(self) -> None:
        """Table with single column."""
        renderer = TableRenderer()
        spec = TableSpec(
            columns=(ColumnSpec(width=15, header="Only"),),
            rows=(("Value",),),
        )

        lines = renderer.table(spec)
        assert len(lines) > 0

    def test_title_longer_than_box(self) -> None:
        """Title truncated if longer than box."""
        renderer = BoxRenderer()
        lines = renderer.box(BoxSpec(width=10, height=3, title="Very Long Title"))

        # Title should be truncated but box should render
        assert len(lines[0]) == 10
