"""Tests for Layout System."""

import pytest
from agents.i.reactive.pipeline.layout import (
    Constraints,
    Edges,
    FlexAlign,
    FlexDirection,
    FlexLayout,
    FlexWrap,
    GridLayout,
    LayoutBox,
    LayoutNode,
    LayoutRect,
    LayoutTree,
    Sizing,
    SizingMode,
)


class TestSizing:
    """Tests for Sizing constraints."""

    def test_fixed_sizing(self) -> None:
        """Fixed sizing returns exact value."""
        sizing = Sizing.fixed(100)

        assert sizing.mode == SizingMode.FIXED
        assert sizing.resolve(200, 50) == 100

    def test_fill_sizing(self) -> None:
        """Fill sizing uses available space."""
        sizing = Sizing.fill()

        assert sizing.mode == SizingMode.FILL
        assert sizing.resolve(200, 50) == 200

    def test_fit_sizing(self) -> None:
        """Fit sizing uses content size."""
        sizing = Sizing.fit()

        assert sizing.mode == SizingMode.FIT_CONTENT
        assert sizing.resolve(200, 50) == 50

    def test_min_sizing(self) -> None:
        """Min sizing respects minimum."""
        sizing = Sizing.min(50)

        assert sizing.resolve(100, 30) == 100
        assert sizing.resolve(30, 30) == 50  # Clamped to min

    def test_max_sizing(self) -> None:
        """Max sizing respects maximum."""
        sizing = Sizing.max(50)

        assert sizing.resolve(100, 30) == 50  # Clamped to max
        assert sizing.resolve(30, 30) == 30

    def test_range_sizing(self) -> None:
        """Range sizing clamps to min/max."""
        sizing = Sizing.range(30, 70)

        assert sizing.resolve(50, 0) == 50  # Within range
        assert sizing.resolve(20, 0) == 30  # Below min
        assert sizing.resolve(100, 0) == 70  # Above max


class TestConstraints:
    """Tests for 2D Constraints."""

    def test_fixed_constraints(self) -> None:
        """Fixed constraints work in both dimensions."""
        constraints = Constraints.fixed(100, 50)

        width, height = constraints.resolve(200, 100)

        assert width == 100
        assert height == 50

    def test_fill_width_constraints(self) -> None:
        """Fill width with fixed height."""
        constraints = Constraints.fill_width(height=3)

        width, height = constraints.resolve(80, 24)

        assert width == 80
        assert height == 3

    def test_fill_both_constraints(self) -> None:
        """Fill both dimensions."""
        constraints = Constraints.fill_both()

        width, height = constraints.resolve(80, 24)

        assert width == 80
        assert height == 24


class TestEdges:
    """Tests for edge values."""

    def test_all_edges(self) -> None:
        """Edges.all sets all sides."""
        edges = Edges.all(5)

        assert edges.top == 5
        assert edges.right == 5
        assert edges.bottom == 5
        assert edges.left == 5

    def test_symmetric_edges(self) -> None:
        """Edges.symmetric sets horizontal/vertical pairs."""
        edges = Edges.symmetric(horizontal=3, vertical=2)

        assert edges.top == 2
        assert edges.bottom == 2
        assert edges.left == 3
        assert edges.right == 3

    def test_total_horizontal(self) -> None:
        """total_horizontal sums left and right."""
        edges = Edges(left=5, right=10, top=0, bottom=0)

        assert edges.total_horizontal == 15

    def test_total_vertical(self) -> None:
        """total_vertical sums top and bottom."""
        edges = Edges(left=0, right=0, top=3, bottom=7)

        assert edges.total_vertical == 10


class TestLayoutBox:
    """Tests for box model."""

    def test_simple_box(self) -> None:
        """Simple box creates uniform edges."""
        box = LayoutBox.simple(margin=1, padding=2, border=1)

        assert box.margin.top == 1
        assert box.padding.left == 2
        assert box.border.right == 1

    def test_content_width(self) -> None:
        """content_width subtracts all horizontal space."""
        box = LayoutBox.simple(margin=2, padding=1, border=1)

        # margin=2*2 + border=1*2 + padding=1*2 = 8 total
        assert box.content_width(100) == 92

    def test_outer_width(self) -> None:
        """outer_width adds all horizontal space."""
        box = LayoutBox.simple(margin=2, padding=1, border=1)

        # margin=2*2 + border=1*2 + padding=1*2 = 8 total
        assert box.outer_width(50) == 58

    def test_no_box(self) -> None:
        """LayoutBox.no_box creates empty box."""
        box = LayoutBox.no_box()

        assert box.total_horizontal == 0
        assert box.total_vertical == 0


class TestLayoutRect:
    """Tests for layout rectangles."""

    def test_right_bottom(self) -> None:
        """right and bottom are computed from position and size."""
        rect = LayoutRect(x=10, y=20, width=30, height=40)

        assert rect.right == 40
        assert rect.bottom == 60

    def test_contains(self) -> None:
        """contains checks if point is inside."""
        rect = LayoutRect(x=10, y=10, width=20, height=20)

        assert rect.contains(15, 15) is True
        assert rect.contains(10, 10) is True  # Top-left corner
        assert rect.contains(29, 29) is True  # Just inside
        assert rect.contains(30, 30) is False  # Outside
        assert rect.contains(5, 15) is False  # Left of rect


class TestLayoutNode:
    """Tests for layout nodes."""

    def test_create_node(self) -> None:
        """LayoutNode can be created."""
        node = LayoutNode(id="test")

        assert node.id == "test"
        assert node.rect.width == 0
        assert node.rect.height == 0

    def test_add_child(self) -> None:
        """Children can be added to node."""
        parent = LayoutNode(id="parent")
        child = LayoutNode(id="child")

        parent.add_child(child)

        assert len(parent.children) == 1
        assert parent.children[0].id == "child"

    def test_compute_layout(self) -> None:
        """compute_layout resolves constraints."""
        node = LayoutNode(
            id="test",
            constraints=Constraints.fixed(50, 10),
        )

        rect = node.compute_layout(100, 50, x=5, y=5)

        assert rect.x == 5
        assert rect.y == 5
        assert rect.width == 50
        assert rect.height == 10


class TestFlexLayout:
    """Tests for flex layout."""

    def test_row_layout(self) -> None:
        """Row layout positions horizontally."""
        flex = FlexLayout(direction=FlexDirection.ROW)
        flex.add_child(LayoutNode("a", Constraints.fixed(10, 3)))
        flex.add_child(LayoutNode("b", Constraints.fixed(20, 3)))
        flex.add_child(LayoutNode("c", Constraints.fixed(10, 3)))

        flex.compute(available_width=80, available_height=24)

        children = flex.children
        assert children[0].rect.x == 0
        assert children[1].rect.x == 10
        assert children[2].rect.x == 30

    def test_column_layout(self) -> None:
        """Column layout positions vertically."""
        flex = FlexLayout(direction=FlexDirection.COLUMN)
        flex.add_child(LayoutNode("a", Constraints.fixed(20, 3)))
        flex.add_child(LayoutNode("b", Constraints.fixed(20, 5)))
        flex.add_child(LayoutNode("c", Constraints.fixed(20, 2)))

        flex.compute(available_width=80, available_height=24)

        children = flex.children
        assert children[0].rect.y == 0
        assert children[1].rect.y == 3
        assert children[2].rect.y == 8

    def test_gap(self) -> None:
        """Gap adds space between items."""
        flex = FlexLayout(direction=FlexDirection.ROW, gap=5)
        flex.add_child(LayoutNode("a", Constraints.fixed(10, 3)))
        flex.add_child(LayoutNode("b", Constraints.fixed(10, 3)))
        flex.add_child(LayoutNode("c", Constraints.fixed(10, 3)))

        flex.compute(available_width=80, available_height=24)

        children = flex.children
        assert children[0].rect.x == 0
        assert children[1].rect.x == 15  # 10 + 5 gap
        assert children[2].rect.x == 30  # 10 + 5 + 10 + 5

    def test_justify_center(self) -> None:
        """justify=CENTER centers items."""
        flex = FlexLayout(
            direction=FlexDirection.ROW,
            justify=FlexAlign.CENTER,
        )
        flex.add_child(LayoutNode("a", Constraints.fixed(20, 3)))

        flex.compute(available_width=80, available_height=24)

        # 80 - 20 = 60 free, centered = start at 30
        assert flex.children[0].rect.x == 30

    def test_justify_end(self) -> None:
        """justify=END aligns items to end."""
        flex = FlexLayout(
            direction=FlexDirection.ROW,
            justify=FlexAlign.END,
        )
        flex.add_child(LayoutNode("a", Constraints.fixed(20, 3)))

        flex.compute(available_width=80, available_height=24)

        # 80 - 20 = 60 free, end = start at 60
        assert flex.children[0].rect.x == 60

    def test_justify_space_between(self) -> None:
        """justify=SPACE_BETWEEN distributes space."""
        flex = FlexLayout(
            direction=FlexDirection.ROW,
            justify=FlexAlign.SPACE_BETWEEN,
        )
        flex.add_child(LayoutNode("a", Constraints.fixed(10, 3)))
        flex.add_child(LayoutNode("b", Constraints.fixed(10, 3)))
        flex.add_child(LayoutNode("c", Constraints.fixed(10, 3)))

        flex.compute(available_width=80, available_height=24)

        children = flex.children
        # 80 - 30 = 50 free, between 3 items = 25 spacing
        assert children[0].rect.x == 0
        assert children[1].rect.x == 35  # 10 + 25
        assert children[2].rect.x == 70  # 10 + 25 + 10 + 25

    def test_align_center(self) -> None:
        """align=CENTER centers on cross axis."""
        flex = FlexLayout(
            direction=FlexDirection.ROW,
            align=FlexAlign.CENTER,
        )
        flex.add_child(LayoutNode("a", Constraints.fixed(10, 2)))

        flex.compute(available_width=80, available_height=10)

        # 10 - 2 = 8 free, centered = y=4
        assert flex.children[0].rect.y == 4

    def test_reverse_direction(self) -> None:
        """ROW_REVERSE lays out right to left."""
        flex = FlexLayout(direction=FlexDirection.ROW_REVERSE)
        flex.add_child(LayoutNode("a", Constraints.fixed(10, 3)))
        flex.add_child(LayoutNode("b", Constraints.fixed(10, 3)))

        flex.compute(available_width=80, available_height=24)

        # Items should be in reverse order (b first, then a)
        children = flex.children
        assert children[1].rect.x == 0  # b
        assert children[0].rect.x == 10  # a


class TestGridLayout:
    """Tests for grid layout."""

    def test_basic_grid(self) -> None:
        """Basic grid positions items in cells."""
        grid = GridLayout(columns=3)

        for i in range(6):
            grid.add_child(LayoutNode(f"cell-{i}", Constraints.fill_both()))

        grid.compute(available_width=60, available_height=20)

        children = grid.children
        # 60 / 3 = 20 per column
        # Row 1
        assert children[0].rect.x == 0
        assert children[1].rect.x == 20
        assert children[2].rect.x == 40
        # Row 2
        assert children[3].rect.x == 0
        assert children[3].rect.y == 10
        assert children[4].rect.x == 20
        assert children[5].rect.x == 40

    def test_grid_with_gaps(self) -> None:
        """Grid respects column and row gaps."""
        grid = GridLayout(columns=2, column_gap=4, row_gap=2)

        for i in range(4):
            grid.add_child(LayoutNode(f"cell-{i}", Constraints.fill_both()))

        grid.compute(available_width=44, available_height=22)

        # 44 - 4 gap = 40, / 2 = 20 per column
        # 22 - 2 gap = 20, / 2 = 10 per row
        children = grid.children
        assert children[0].rect.x == 0
        assert children[1].rect.x == 24  # 20 + 4 gap
        assert children[2].rect.y == 12  # 10 + 2 gap

    def test_fixed_column_widths(self) -> None:
        """Grid respects fixed column widths."""
        grid = GridLayout(columns=3, column_widths=[10, None, 20])

        grid.add_child(LayoutNode("a", Constraints.fill_both()))
        grid.add_child(LayoutNode("b", Constraints.fill_both()))
        grid.add_child(LayoutNode("c", Constraints.fill_both()))

        grid.compute(available_width=60, available_height=20)

        # Col 0: 10, Col 1: auto (60-10-20=30), Col 2: 20
        children = grid.children
        assert children[0].rect.width == 10
        assert children[1].rect.width == 30
        assert children[2].rect.width == 20


class TestLayoutTree:
    """Tests for layout tree."""

    def test_layout_tree(self) -> None:
        """LayoutTree manages multiple layouts."""
        tree = LayoutTree(root_width=80, root_height=24)

        header = FlexLayout(direction=FlexDirection.ROW)
        header.add_child(LayoutNode("logo", Constraints.fixed(10, 1)))
        header.add_child(LayoutNode("nav", Constraints.fill_width(height=1)))

        tree.add_layout("header", header)
        tree.compute()

        logo = tree.find("logo")
        nav = tree.find("nav")

        assert logo is not None
        assert nav is not None
        assert logo.rect.x == 0
        assert logo.rect.width == 10

    def test_resize(self) -> None:
        """LayoutTree can be resized."""
        tree = LayoutTree(root_width=80, root_height=24)

        flex = FlexLayout(direction=FlexDirection.ROW)
        flex.add_child(LayoutNode("item", Constraints.fill_both()))

        tree.add_layout("flex", flex)
        tree.compute()

        assert tree.find("item") is not None
        assert tree.find("item").rect.width == 80  # type: ignore[union-attr]

        tree.resize(100, 30)

        assert tree.find("item").rect.width == 100  # type: ignore[union-attr]

    def test_get_at(self) -> None:
        """LayoutTree.get_at finds node at position."""
        tree = LayoutTree(root_width=80, root_height=24)

        tree.add_node(LayoutNode("box", Constraints.fixed(20, 10)), x=10, y=5)
        tree.find("box").rect = LayoutRect(x=10, y=5, width=20, height=10)  # type: ignore[union-attr]

        result = tree.get_at(15, 8)
        assert result is not None
        assert result.id == "box"

        result = tree.get_at(0, 0)
        assert result is None
