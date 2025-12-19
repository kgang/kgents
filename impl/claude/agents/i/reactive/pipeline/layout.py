"""
Layout System: Widget positioning and sizing.

Provides constraint-based layout with:
- Box model (margin, padding, border)
- Flex layout (row, column, wrap)
- Grid layout for structured positioning
- Constraint-based sizing (min/max/fixed/fill)

The layout is pure computation: same inputs -> same outputs.
No side effects in layout calculation.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import TYPE_CHECKING, Any, Generic, TypeVar

if TYPE_CHECKING:
    pass

T = TypeVar("T")


# =============================================================================
# Sizing Constraints
# =============================================================================


class SizingMode(Enum):
    """How a dimension should be sized."""

    FIXED = auto()  # Exact size
    MIN = auto()  # Minimum size (can grow)
    MAX = auto()  # Maximum size (can shrink)
    FILL = auto()  # Fill available space
    FIT_CONTENT = auto()  # Size to content


@dataclass(frozen=True)
class Sizing:
    """
    Sizing constraint for a single dimension.

    Examples:
        Sizing.fixed(100)     # Exactly 100
        Sizing.min(50)        # At least 50
        Sizing.max(200)       # At most 200
        Sizing.fill()         # Fill available
        Sizing.fit()          # Fit to content
        Sizing.range(50, 200) # Between 50 and 200
    """

    mode: SizingMode
    value: int = 0
    min_value: int = 0
    max_value: int = 999999

    @classmethod
    def fixed(cls, value: int) -> Sizing:
        """Fixed size constraint."""
        return cls(mode=SizingMode.FIXED, value=value, min_value=value, max_value=value)

    @classmethod
    def min(cls, value: int) -> Sizing:
        """Minimum size constraint."""
        return cls(mode=SizingMode.MIN, value=value, min_value=value)

    @classmethod
    def max(cls, value: int) -> Sizing:
        """Maximum size constraint."""
        return cls(mode=SizingMode.MAX, value=value, max_value=value)

    @classmethod
    def fill(cls) -> Sizing:
        """Fill available space."""
        return cls(mode=SizingMode.FILL)

    @classmethod
    def fit(cls) -> Sizing:
        """Fit to content size."""
        return cls(mode=SizingMode.FIT_CONTENT)

    @classmethod
    def range(cls, min_val: int, max_val: int) -> Sizing:
        """Size between min and max."""
        return cls(mode=SizingMode.MIN, value=min_val, min_value=min_val, max_value=max_val)

    def resolve(self, available: int, content: int = 0) -> int:
        """
        Resolve the sizing to an actual value.

        Args:
            available: Available space
            content: Content size (for FIT_CONTENT)

        Returns:
            Resolved size
        """
        if self.mode == SizingMode.FIXED:
            return self.value
        elif self.mode == SizingMode.FILL:
            return max(self.min_value, min(self.max_value, available))
        elif self.mode == SizingMode.FIT_CONTENT:
            return max(self.min_value, min(self.max_value, content))
        elif self.mode == SizingMode.MIN:
            return max(self.min_value, min(self.max_value, available))
        elif self.mode == SizingMode.MAX:
            return max(self.min_value, min(self.max_value, available))
        return available


@dataclass(frozen=True)
class Constraints:
    """
    2D sizing constraints (width and height).

    Example:
        constraints = Constraints(
            width=Sizing.fill(),
            height=Sizing.fixed(3),
        )
    """

    width: Sizing = field(default_factory=Sizing.fill)
    height: Sizing = field(default_factory=Sizing.fit)

    @classmethod
    def fixed(cls, width: int, height: int) -> Constraints:
        """Fixed size constraints."""
        return cls(width=Sizing.fixed(width), height=Sizing.fixed(height))

    @classmethod
    def fill_width(cls, height: int) -> Constraints:
        """Fill width, fixed height."""
        return cls(width=Sizing.fill(), height=Sizing.fixed(height))

    @classmethod
    def fill_height(cls, width: int) -> Constraints:
        """Fixed width, fill height."""
        return cls(width=Sizing.fixed(width), height=Sizing.fill())

    @classmethod
    def fill_both(cls) -> Constraints:
        """Fill both dimensions."""
        return cls(width=Sizing.fill(), height=Sizing.fill())

    def resolve(
        self,
        available_width: int,
        available_height: int,
        content_width: int = 0,
        content_height: int = 0,
    ) -> tuple[int, int]:
        """Resolve to actual width and height."""
        return (
            self.width.resolve(available_width, content_width),
            self.height.resolve(available_height, content_height),
        )


# =============================================================================
# Box Model
# =============================================================================


@dataclass(frozen=True)
class Edges:
    """
    Edge values (margin, padding, border width).

    Can specify all four edges or use shortcuts.
    """

    top: int = 0
    right: int = 0
    bottom: int = 0
    left: int = 0

    @classmethod
    def all(cls, value: int) -> Edges:
        """Same value on all edges."""
        return cls(top=value, right=value, bottom=value, left=value)

    @classmethod
    def symmetric(cls, horizontal: int, vertical: int) -> Edges:
        """Symmetric horizontal and vertical."""
        return cls(top=vertical, right=horizontal, bottom=vertical, left=horizontal)

    @classmethod
    def horizontal(cls, value: int) -> Edges:
        """Only horizontal edges."""
        return cls(left=value, right=value)

    @classmethod
    def vertical(cls, value: int) -> Edges:
        """Only vertical edges."""
        return cls(top=value, bottom=value)

    @property
    def total_horizontal(self) -> int:
        """Total horizontal space (left + right)."""
        return self.left + self.right

    @property
    def total_vertical(self) -> int:
        """Total vertical space (top + bottom)."""
        return self.top + self.bottom


@dataclass(frozen=True)
class LayoutBox:
    """
    Box model for layout calculation.

    Content is surrounded by padding, border, and margin:

        ┌─────────────── margin ──────────────┐
        │ ┌─────────── border ──────────────┐ │
        │ │ ┌──────── padding ─────────────┐ │ │
        │ │ │                              │ │ │
        │ │ │         content              │ │ │
        │ │ │                              │ │ │
        │ │ └──────────────────────────────┘ │ │
        │ └──────────────────────────────────┘ │
        └──────────────────────────────────────┘
    """

    margin: Edges = field(default_factory=Edges)
    padding: Edges = field(default_factory=Edges)
    border: Edges = field(default_factory=Edges)

    @classmethod
    def simple(cls, margin: int = 0, padding: int = 1, border: int = 1) -> LayoutBox:
        """Create a box with uniform edges."""
        return cls(
            margin=Edges.all(margin),
            padding=Edges.all(padding),
            border=Edges.all(border),
        )

    @classmethod
    def no_box(cls) -> LayoutBox:
        """No box (content only)."""
        return cls()

    def content_width(self, outer_width: int) -> int:
        """Calculate content width from outer width."""
        return outer_width - self.total_horizontal

    def content_height(self, outer_height: int) -> int:
        """Calculate content height from outer height."""
        return outer_height - self.total_vertical

    def outer_width(self, content_width: int) -> int:
        """Calculate outer width from content width."""
        return content_width + self.total_horizontal

    def outer_height(self, content_height: int) -> int:
        """Calculate outer height from content height."""
        return content_height + self.total_vertical

    @property
    def total_horizontal(self) -> int:
        """Total horizontal space used by box."""
        return (
            self.margin.total_horizontal
            + self.border.total_horizontal
            + self.padding.total_horizontal
        )

    @property
    def total_vertical(self) -> int:
        """Total vertical space used by box."""
        return self.margin.total_vertical + self.border.total_vertical + self.padding.total_vertical


# =============================================================================
# Layout Node
# =============================================================================


@dataclass
class LayoutRect:
    """
    Computed layout rectangle.

    The result of layout calculation.
    """

    x: int = 0
    y: int = 0
    width: int = 0
    height: int = 0

    @property
    def right(self) -> int:
        return self.x + self.width

    @property
    def bottom(self) -> int:
        return self.y + self.height

    def contains(self, x: int, y: int) -> bool:
        """Check if point is inside rectangle."""
        return self.x <= x < self.right and self.y <= y < self.bottom


@dataclass
class LayoutNode:
    """
    A node in the layout tree.

    Each node has constraints and box model, producing a computed rect.

    Example:
        node = LayoutNode(
            id="header",
            constraints=Constraints.fill_width(height=3),
            box=LayoutBox.simple(padding=1),
        )

        # After layout computation
        print(node.rect.width, node.rect.height)
    """

    id: str
    constraints: Constraints = field(default_factory=Constraints)
    box: LayoutBox = field(default_factory=LayoutBox)
    rect: LayoutRect = field(default_factory=LayoutRect)
    content_size: tuple[int, int] = (0, 0)  # (width, height) of content
    _children: list[LayoutNode] = field(default_factory=list)

    def add_child(self, child: LayoutNode) -> None:
        """Add a child node."""
        self._children.append(child)

    def remove_child(self, child_id: str) -> None:
        """Remove a child by ID."""
        self._children = [c for c in self._children if c.id != child_id]

    @property
    def children(self) -> list[LayoutNode]:
        """Get child nodes."""
        return list(self._children)

    def compute_layout(
        self,
        available_width: int,
        available_height: int,
        x: int = 0,
        y: int = 0,
    ) -> LayoutRect:
        """
        Compute layout for this node and children.

        Args:
            available_width: Available width
            available_height: Available height
            x: Starting X position
            y: Starting Y position

        Returns:
            Computed layout rectangle
        """
        # Resolve constraints
        width, height = self.constraints.resolve(
            available_width,
            available_height,
            self.content_size[0],
            self.content_size[1],
        )

        self.rect = LayoutRect(x=x, y=y, width=width, height=height)
        return self.rect


# =============================================================================
# Flex Layout
# =============================================================================


class FlexDirection(Enum):
    """Direction of flex layout."""

    ROW = auto()  # Left to right
    COLUMN = auto()  # Top to bottom
    ROW_REVERSE = auto()  # Right to left
    COLUMN_REVERSE = auto()  # Bottom to top


class FlexWrap(Enum):
    """How flex items wrap."""

    NO_WRAP = auto()  # Single line
    WRAP = auto()  # Wrap to next line
    WRAP_REVERSE = auto()  # Wrap in reverse


class FlexAlign(Enum):
    """Alignment of flex items."""

    START = auto()  # Align to start
    END = auto()  # Align to end
    CENTER = auto()  # Center align
    STRETCH = auto()  # Stretch to fill
    SPACE_BETWEEN = auto()  # Space between items
    SPACE_AROUND = auto()  # Space around items
    SPACE_EVENLY = auto()  # Even space


@dataclass
class FlexLayout:
    """
    Flexbox-style layout container.

    Arranges children in rows or columns with alignment and wrapping.

    Example:
        flex = FlexLayout(
            direction=FlexDirection.ROW,
            justify=FlexAlign.SPACE_BETWEEN,
            align=FlexAlign.CENTER,
            gap=2,
        )

        # Add children
        flex.add_child(LayoutNode("item1", Constraints.fixed(10, 3)))
        flex.add_child(LayoutNode("item2", Constraints.fixed(15, 3)))
        flex.add_child(LayoutNode("item3", Constraints.fixed(10, 3)))

        # Compute layout
        flex.compute(available_width=80, available_height=24)

        for child in flex.children:
            print(f"{child.id}: x={child.rect.x}, y={child.rect.y}")
    """

    direction: FlexDirection = FlexDirection.ROW
    wrap: FlexWrap = FlexWrap.NO_WRAP
    justify: FlexAlign = FlexAlign.START  # Main axis alignment
    align: FlexAlign = FlexAlign.STRETCH  # Cross axis alignment
    gap: int = 0  # Gap between items
    _children: list[LayoutNode] = field(default_factory=list)
    _rect: LayoutRect = field(default_factory=LayoutRect)

    def add_child(self, child: LayoutNode) -> None:
        """Add a child to the flex container."""
        self._children.append(child)

    def remove_child(self, child_id: str) -> None:
        """Remove a child by ID."""
        self._children = [c for c in self._children if c.id != child_id]

    @property
    def children(self) -> list[LayoutNode]:
        """Get children."""
        return list(self._children)

    @property
    def rect(self) -> LayoutRect:
        """Get computed layout rect."""
        return self._rect

    def compute(
        self,
        available_width: int,
        available_height: int,
        x: int = 0,
        y: int = 0,
    ) -> LayoutRect:
        """
        Compute layout for all children.

        Args:
            available_width: Available width
            available_height: Available height
            x: Starting X position
            y: Starting Y position

        Returns:
            Container's layout rect
        """
        self._rect = LayoutRect(x=x, y=y, width=available_width, height=available_height)

        if not self._children:
            return self._rect

        is_row = self.direction in (FlexDirection.ROW, FlexDirection.ROW_REVERSE)
        is_reverse = self.direction in (
            FlexDirection.ROW_REVERSE,
            FlexDirection.COLUMN_REVERSE,
        )

        # Calculate child sizes
        child_sizes: list[tuple[int, int]] = []
        total_main = 0
        max_cross = 0

        for child in self._children:
            # Compute child's preferred size
            if is_row:
                child_width = child.constraints.width.resolve(
                    available_width, child.content_size[0]
                )
                child_height = child.constraints.height.resolve(
                    available_height, child.content_size[1]
                )
            else:
                child_width = child.constraints.width.resolve(
                    available_width, child.content_size[0]
                )
                child_height = child.constraints.height.resolve(
                    available_height, child.content_size[1]
                )

            child_sizes.append((child_width, child_height))

            if is_row:
                total_main += child_width
                max_cross = max(max_cross, child_height)
            else:
                total_main += child_height
                max_cross = max(max_cross, child_width)

        # Add gaps
        total_main += self.gap * (len(self._children) - 1) if self._children else 0

        # Calculate available space and starting position
        if is_row:
            main_size = available_width
            cross_size = available_height
        else:
            main_size = available_height
            cross_size = available_width

        # Calculate justification offset and spacing
        main_offset, main_spacing = self._calculate_justify(
            total_main, main_size, len(self._children)
        )

        # Position children
        current_main = main_offset
        children_order = list(range(len(self._children)))
        if is_reverse:
            children_order.reverse()

        for idx in children_order:
            child = self._children[idx]
            child_w, child_h = child_sizes[idx]

            # Calculate cross-axis position based on alignment
            if is_row:
                cross_offset = self._calculate_align_offset(child_h, cross_size)
                child.rect = LayoutRect(
                    x=x + current_main,
                    y=y + cross_offset,
                    width=child_w,
                    height=child_h if self.align != FlexAlign.STRETCH else cross_size,
                )
                current_main += child_w + self.gap + main_spacing
            else:
                cross_offset = self._calculate_align_offset(child_w, cross_size)
                child.rect = LayoutRect(
                    x=x + cross_offset,
                    y=y + current_main,
                    width=child_w if self.align != FlexAlign.STRETCH else cross_size,
                    height=child_h,
                )
                current_main += child_h + self.gap + main_spacing

        return self._rect

    def _calculate_justify(
        self, content_size: int, container_size: int, item_count: int
    ) -> tuple[int, int]:
        """
        Calculate justification offset and spacing.

        Returns:
            (initial_offset, between_spacing)
        """
        if item_count == 0:
            return (0, 0)

        free_space = max(0, container_size - content_size)

        if self.justify == FlexAlign.START:
            return (0, 0)
        elif self.justify == FlexAlign.END:
            return (free_space, 0)
        elif self.justify == FlexAlign.CENTER:
            return (free_space // 2, 0)
        elif self.justify == FlexAlign.SPACE_BETWEEN:
            if item_count <= 1:
                return (0, 0)
            spacing = free_space // (item_count - 1)
            return (0, spacing)
        elif self.justify == FlexAlign.SPACE_AROUND:
            spacing = free_space // (item_count * 2)
            return (spacing, spacing * 2)
        elif self.justify == FlexAlign.SPACE_EVENLY:
            spacing = free_space // (item_count + 1)
            return (spacing, spacing)
        else:
            return (0, 0)

    def _calculate_align_offset(self, item_size: int, container_size: int) -> int:
        """Calculate cross-axis alignment offset."""
        if self.align == FlexAlign.START:
            return 0
        elif self.align == FlexAlign.END:
            return container_size - item_size
        elif self.align == FlexAlign.CENTER:
            return (container_size - item_size) // 2
        else:  # STRETCH handled elsewhere
            return 0


# =============================================================================
# Grid Layout
# =============================================================================


@dataclass
class GridLayout:
    """
    Grid-based layout container.

    Arranges children in a grid with fixed columns/rows.

    Example:
        grid = GridLayout(
            columns=3,
            column_gap=2,
            row_gap=1,
        )

        # Add children (will flow into grid)
        for i in range(9):
            grid.add_child(LayoutNode(f"cell-{i}", Constraints.fill_both()))

        # Compute layout
        grid.compute(available_width=80, available_height=24)
    """

    columns: int = 1
    rows: int | None = None  # None = auto based on children
    column_gap: int = 0
    row_gap: int = 0
    column_widths: list[int | None] = field(default_factory=list)  # None = auto
    row_heights: list[int | None] = field(default_factory=list)  # None = auto
    _children: list[LayoutNode] = field(default_factory=list)
    _rect: LayoutRect = field(default_factory=LayoutRect)

    def add_child(self, child: LayoutNode) -> None:
        """Add a child to the grid."""
        self._children.append(child)

    def remove_child(self, child_id: str) -> None:
        """Remove a child by ID."""
        self._children = [c for c in self._children if c.id != child_id]

    @property
    def children(self) -> list[LayoutNode]:
        """Get children."""
        return list(self._children)

    @property
    def rect(self) -> LayoutRect:
        """Get computed layout rect."""
        return self._rect

    def compute(
        self,
        available_width: int,
        available_height: int,
        x: int = 0,
        y: int = 0,
    ) -> LayoutRect:
        """
        Compute layout for all children.

        Children flow into grid cells left-to-right, top-to-bottom.
        """
        self._rect = LayoutRect(x=x, y=y, width=available_width, height=available_height)

        if not self._children:
            return self._rect

        # Calculate number of rows
        num_children = len(self._children)
        num_rows = self.rows or ((num_children + self.columns - 1) // self.columns)

        # Calculate cell sizes
        total_col_gap = self.column_gap * (self.columns - 1) if self.columns > 1 else 0
        total_row_gap = self.row_gap * (num_rows - 1) if num_rows > 1 else 0

        available_cell_width = available_width - total_col_gap
        available_cell_height = available_height - total_row_gap

        # Calculate column widths
        col_widths: list[int] = []
        fixed_width = 0
        auto_cols = 0

        for i in range(self.columns):
            if i < len(self.column_widths) and self.column_widths[i] is not None:
                col_widths.append(self.column_widths[i])  # type: ignore[arg-type]
                fixed_width += self.column_widths[i]  # type: ignore[operator]
            else:
                col_widths.append(0)  # Placeholder
                auto_cols += 1

        if auto_cols > 0:
            auto_width = (available_cell_width - fixed_width) // auto_cols
            col_widths = [w if w > 0 else auto_width for w in col_widths]

        # Calculate row heights
        row_heights: list[int] = []
        fixed_height = 0
        auto_rows = 0

        for i in range(num_rows):
            if i < len(self.row_heights) and self.row_heights[i] is not None:
                row_heights.append(self.row_heights[i])  # type: ignore[arg-type]
                fixed_height += self.row_heights[i]  # type: ignore[operator]
            else:
                row_heights.append(0)
                auto_rows += 1

        if auto_rows > 0:
            auto_height = (available_cell_height - fixed_height) // auto_rows
            row_heights = [h if h > 0 else auto_height for h in row_heights]

        # Position children in grid
        for i, child in enumerate(self._children):
            col = i % self.columns
            row = i // self.columns

            if row >= num_rows:
                break  # Exceeded row count

            # Calculate position
            cell_x = x + sum(col_widths[:col]) + col * self.column_gap
            cell_y = y + sum(row_heights[:row]) + row * self.row_gap
            cell_w = col_widths[col]
            cell_h = row_heights[row]

            # Resolve child constraints within cell
            child_w = child.constraints.width.resolve(cell_w, child.content_size[0])
            child_h = child.constraints.height.resolve(cell_h, child.content_size[1])

            child.rect = LayoutRect(
                x=cell_x,
                y=cell_y,
                width=min(child_w, cell_w),
                height=min(child_h, cell_h),
            )

        return self._rect


# =============================================================================
# Layout Tree
# =============================================================================


@dataclass
class LayoutTree:
    """
    Complete layout tree with root and computed positions.

    Manages the entire layout hierarchy.

    Example:
        tree = LayoutTree(root_width=80, root_height=24)

        # Add a flex container
        header = FlexLayout(direction=FlexDirection.ROW, justify=FlexAlign.SPACE_BETWEEN)
        header.add_child(LayoutNode("logo", Constraints.fixed(10, 1)))
        header.add_child(LayoutNode("nav", Constraints.fill_width(height=1)))

        tree.add_layout("header", header)

        # Compute all layouts
        tree.compute()

        # Get node by ID
        logo = tree.find("logo")
        print(logo.rect)
    """

    root_width: int
    root_height: int
    _layouts: dict[str, FlexLayout | GridLayout] = field(default_factory=dict)
    _nodes: dict[str, LayoutNode] = field(default_factory=dict)
    _layout_order: list[str] = field(default_factory=list)

    def add_layout(
        self,
        layout_id: str,
        layout: FlexLayout | GridLayout,
        position: LayoutRect | None = None,
    ) -> None:
        """
        Add a layout container.

        Args:
            layout_id: Unique identifier
            layout: The layout container
            position: Optional fixed position
        """
        self._layouts[layout_id] = layout
        self._layout_order.append(layout_id)

        # Register all children
        for child in layout.children:
            self._nodes[child.id] = child

    def add_node(
        self,
        node: LayoutNode,
        x: int = 0,
        y: int = 0,
    ) -> None:
        """Add a standalone node at fixed position."""
        node.rect = LayoutRect(x=x, y=y, width=0, height=0)
        self._nodes[node.id] = node

    def compute(self) -> None:
        """Compute layout for all containers."""
        y_offset = 0

        for layout_id in self._layout_order:
            layout = self._layouts[layout_id]

            # Compute layout
            rect = layout.compute(
                available_width=self.root_width,
                available_height=self.root_height - y_offset,
                x=0,
                y=y_offset,
            )

            # Advance y_offset for stacking
            y_offset += rect.height

    def find(self, node_id: str) -> LayoutNode | None:
        """Find a node by ID."""
        return self._nodes.get(node_id)

    def get_at(self, x: int, y: int) -> LayoutNode | None:
        """Get the node at a screen position."""
        for node in self._nodes.values():
            if node.rect.contains(x, y):
                return node
        return None

    def resize(self, width: int, height: int) -> None:
        """Resize the layout and recompute."""
        self.root_width = width
        self.root_height = height
        self.compute()
