"""
Box Drawing: Unicode box characters for terminal UI.

Pure, deterministic box rendering. All boxes are built from immutable
character mappings. No side effects.

Supports:
- Multiple line styles (SINGLE, DOUBLE, ROUNDED, HEAVY, ASCII)
- Nested boxes with proper intersection handling
- Table layouts with columns
- Titles and labels

The box IS the border. Content flows inside.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import TYPE_CHECKING, Literal

if TYPE_CHECKING:
    pass


class BoxStyle(Enum):
    """
    Available box drawing styles.

    Each style maps to a set of Unicode box-drawing characters.
    ASCII provides maximum compatibility fallback.
    """

    SINGLE = auto()  # ─│┌┐└┘├┤┬┴┼
    DOUBLE = auto()  # ═║╔╗╚╝╠╣╦╩╬
    ROUNDED = auto()  # ─│╭╮╰╯├┤┬┴┼
    HEAVY = auto()  # ━┃┏┓┗┛┣┫┳┻╋
    ASCII = auto()  # -|++++++++++


@dataclass(frozen=True)
class BoxChars:
    """
    Character set for a box style.

    All characters needed to draw any box shape.
    """

    horizontal: str
    vertical: str
    top_left: str
    top_right: str
    bottom_left: str
    bottom_right: str
    left_tee: str  # ├
    right_tee: str  # ┤
    top_tee: str  # ┬
    bottom_tee: str  # ┴
    cross: str  # ┼

    def corner(self, position: Literal["tl", "tr", "bl", "br"]) -> str:
        """Get corner character by position."""
        return {
            "tl": self.top_left,
            "tr": self.top_right,
            "bl": self.bottom_left,
            "br": self.bottom_right,
        }[position]


# Character sets for each style
BOX_CHARS: dict[BoxStyle, BoxChars] = {
    BoxStyle.SINGLE: BoxChars(
        horizontal="─",
        vertical="│",
        top_left="┌",
        top_right="┐",
        bottom_left="└",
        bottom_right="┘",
        left_tee="├",
        right_tee="┤",
        top_tee="┬",
        bottom_tee="┴",
        cross="┼",
    ),
    BoxStyle.DOUBLE: BoxChars(
        horizontal="═",
        vertical="║",
        top_left="╔",
        top_right="╗",
        bottom_left="╚",
        bottom_right="╝",
        left_tee="╠",
        right_tee="╣",
        top_tee="╦",
        bottom_tee="╩",
        cross="╬",
    ),
    BoxStyle.ROUNDED: BoxChars(
        horizontal="─",
        vertical="│",
        top_left="╭",
        top_right="╮",
        bottom_left="╰",
        bottom_right="╯",
        left_tee="├",
        right_tee="┤",
        top_tee="┬",
        bottom_tee="┴",
        cross="┼",
    ),
    BoxStyle.HEAVY: BoxChars(
        horizontal="━",
        vertical="┃",
        top_left="┏",
        top_right="┓",
        bottom_left="┗",
        bottom_right="┛",
        left_tee="┣",
        right_tee="┫",
        top_tee="┳",
        bottom_tee="┻",
        cross="╋",
    ),
    BoxStyle.ASCII: BoxChars(
        horizontal="-",
        vertical="|",
        top_left="+",
        top_right="+",
        bottom_left="+",
        bottom_right="+",
        left_tee="+",
        right_tee="+",
        top_tee="+",
        bottom_tee="+",
        cross="+",
    ),
}


def get_chars(style: BoxStyle) -> BoxChars:
    """Get character set for a style."""
    return BOX_CHARS[style]


# === Box Rendering ===


@dataclass(frozen=True)
class BoxSpec:
    """
    Specification for a box to render.

    Immutable description of a box's dimensions and style.
    """

    width: int
    height: int
    style: BoxStyle = BoxStyle.SINGLE
    title: str | None = None
    title_align: Literal["left", "center", "right"] = "left"
    padding: int = 1  # Internal padding


@dataclass
class BoxRenderer:
    """
    Renders box drawings from specifications.

    Pure functions: same spec -> same output.

    Example:
        renderer = BoxRenderer()

        # Simple box
        lines = renderer.box(BoxSpec(width=20, height=5))
        for line in lines:
            print(line)

        # Box with title
        lines = renderer.box(BoxSpec(width=30, height=5, title="Status"))
    """

    def box(self, spec: BoxSpec) -> list[str]:
        """
        Render a box to lines.

        Returns list of strings, one per line.
        """
        chars = get_chars(spec.style)
        lines: list[str] = []

        # Top border (with optional title)
        lines.append(self._top_border(spec, chars))

        # Middle lines (empty interior)
        interior_height = spec.height - 2
        interior_width = spec.width - 2
        for _ in range(interior_height):
            lines.append(chars.vertical + " " * interior_width + chars.vertical)

        # Bottom border
        lines.append(chars.bottom_left + chars.horizontal * (spec.width - 2) + chars.bottom_right)

        return lines

    def box_with_content(
        self,
        spec: BoxSpec,
        content: list[str],
    ) -> list[str]:
        """
        Render a box with content inside.

        Content is padded and clipped to fit.
        """
        chars = get_chars(spec.style)
        lines: list[str] = []

        # Top border
        lines.append(self._top_border(spec, chars))

        # Content area
        interior_width = spec.width - 2 - (spec.padding * 2)
        interior_height = spec.height - 2

        # Pad content to fill height
        padded_content = content[:interior_height]
        while len(padded_content) < interior_height:
            padded_content.append("")

        for content_line in padded_content:
            # Clip/pad content to width
            if len(content_line) > interior_width:
                display = content_line[:interior_width]
            else:
                display = content_line.ljust(interior_width)

            padding = " " * spec.padding
            line = f"{chars.vertical}{padding}{display}{padding}{chars.vertical}"
            lines.append(line)

        # Bottom border
        lines.append(chars.bottom_left + chars.horizontal * (spec.width - 2) + chars.bottom_right)

        return lines

    def _top_border(self, spec: BoxSpec, chars: BoxChars) -> str:
        """Render top border with optional title."""
        inner_width = spec.width - 2

        if not spec.title:
            return chars.top_left + chars.horizontal * inner_width + chars.top_right

        # Title with separators
        title = f" {spec.title} "
        if len(title) > inner_width - 2:
            title = title[: inner_width - 2]

        remaining = inner_width - len(title)

        if spec.title_align == "left":
            left_width = 1
            right_width = remaining - 1
        elif spec.title_align == "right":
            left_width = remaining - 1
            right_width = 1
        else:  # center
            left_width = remaining // 2
            right_width = remaining - left_width

        return (
            chars.top_left
            + chars.horizontal * left_width
            + title
            + chars.horizontal * right_width
            + chars.top_right
        )


# === Table Layout ===


@dataclass(frozen=True)
class ColumnSpec:
    """Specification for a table column."""

    width: int
    align: Literal["left", "center", "right"] = "left"
    header: str = ""


@dataclass(frozen=True)
class TableSpec:
    """
    Specification for a table layout.

    Tables have headers, rows, and column definitions.
    """

    columns: tuple[ColumnSpec, ...]
    rows: tuple[tuple[str, ...], ...] = ()
    style: BoxStyle = BoxStyle.SINGLE
    show_header: bool = True
    row_separator: bool = False  # Lines between rows


@dataclass
class TableRenderer:
    """
    Renders tables with box drawing characters.

    Example:
        renderer = TableRenderer()

        spec = TableSpec(
            columns=(
                ColumnSpec(width=10, header="Name"),
                ColumnSpec(width=8, header="Status", align="center"),
                ColumnSpec(width=6, header="CPU", align="right"),
            ),
            rows=(
                ("Alpha", "active", "23%"),
                ("Beta", "idle", "5%"),
            )
        )

        for line in renderer.table(spec):
            print(line)
    """

    def table(self, spec: TableSpec) -> list[str]:
        """Render a table to lines."""
        chars = get_chars(spec.style)
        lines: list[str] = []

        # Top border
        lines.append(self._table_border("top", spec, chars))

        # Header row
        if spec.show_header:
            header_cells = [c.header for c in spec.columns]
            lines.append(self._table_row(header_cells, spec, chars))
            lines.append(self._table_border("mid", spec, chars))

        # Data rows
        for i, row in enumerate(spec.rows):
            lines.append(self._table_row(list(row), spec, chars))
            if spec.row_separator and i < len(spec.rows) - 1:
                lines.append(self._table_border("mid", spec, chars))

        # Bottom border
        lines.append(self._table_border("bottom", spec, chars))

        return lines

    def _table_border(
        self,
        position: Literal["top", "mid", "bottom"],
        spec: TableSpec,
        chars: BoxChars,
    ) -> str:
        """Render a table border line."""
        if position == "top":
            left, mid, right = chars.top_left, chars.top_tee, chars.top_right
        elif position == "mid":
            left, mid, right = chars.left_tee, chars.cross, chars.right_tee
        else:
            left, mid, right = chars.bottom_left, chars.bottom_tee, chars.bottom_right

        parts = [left]
        for i, col in enumerate(spec.columns):
            parts.append(chars.horizontal * col.width)
            if i < len(spec.columns) - 1:
                parts.append(mid)
        parts.append(right)

        return "".join(parts)

    def _table_row(
        self,
        cells: list[str],
        spec: TableSpec,
        chars: BoxChars,
    ) -> str:
        """Render a table data row."""
        parts = [chars.vertical]

        for i, col in enumerate(spec.columns):
            cell = cells[i] if i < len(cells) else ""

            # Clip if too long
            if len(cell) > col.width:
                cell = cell[: col.width - 1] + "…"

            # Align
            if col.align == "right":
                formatted = cell.rjust(col.width)
            elif col.align == "center":
                formatted = cell.center(col.width)
            else:
                formatted = cell.ljust(col.width)

            parts.append(formatted)
            parts.append(chars.vertical)

        return "".join(parts)


# === Nested Box Support ===


@dataclass
class NestedBox:
    """
    A box that can contain other boxes.

    Handles intersection resolution when boxes share edges.

    Example:
        outer = NestedBox(BoxSpec(width=40, height=10, title="Dashboard"))
        inner1 = BoxSpec(width=18, height=4, title="Status")
        inner2 = BoxSpec(width=18, height=4, title="Info")

        lines = outer.with_children([
            (1, 1, inner1),  # (x, y, spec)
            (20, 1, inner2),
        ])
    """

    spec: BoxSpec
    _renderer: BoxRenderer = field(default_factory=BoxRenderer)

    def render(self) -> list[str]:
        """Render this box alone."""
        return self._renderer.box(self.spec)

    def render_with_content(self, content: list[str]) -> list[str]:
        """Render with content inside."""
        return self._renderer.box_with_content(self.spec, content)

    def with_children(
        self,
        children: list[tuple[int, int, BoxSpec]],
    ) -> list[str]:
        """
        Render with child boxes at specified positions.

        Args:
            children: List of (x, y, spec) tuples for child boxes

        Returns:
            List of lines with nested boxes rendered
        """
        # Start with outer box
        grid = self._to_char_grid(self._renderer.box(self.spec))

        # Render each child
        for x, y, child_spec in children:
            child_lines = self._renderer.box(child_spec)
            child_grid = self._to_char_grid(child_lines)

            # Overlay child on grid
            for cy, child_row in enumerate(child_grid):
                for cx, char in enumerate(child_row):
                    gx, gy = x + cx, y + cy
                    if 0 <= gy < len(grid) and 0 <= gx < len(grid[gy]):
                        # Handle intersections
                        existing = grid[gy][gx]
                        grid[gy][gx] = self._resolve_intersection(existing, char)

        return ["".join(row) for row in grid]

    def _to_char_grid(self, lines: list[str]) -> list[list[str]]:
        """Convert lines to character grid."""
        return [list(line) for line in lines]

    def _resolve_intersection(self, existing: str, new: str) -> str:
        """
        Resolve character when boxes intersect.

        Returns the appropriate intersection character.
        """
        # If same, keep it
        if existing == new:
            return new

        # If either is a space, use the other
        if existing == " ":
            return new
        if new == " ":
            return existing

        # If new is a border character, it takes precedence
        # (child boxes draw over parent)
        return new


# === Convenience Functions ===


def simple_box(
    width: int,
    height: int,
    style: BoxStyle = BoxStyle.SINGLE,
    title: str | None = None,
) -> list[str]:
    """Quick box rendering."""
    renderer = BoxRenderer()
    return renderer.box(BoxSpec(width=width, height=height, style=style, title=title))


def content_box(
    content: list[str],
    style: BoxStyle = BoxStyle.SINGLE,
    title: str | None = None,
    padding: int = 1,
    min_width: int = 0,
) -> list[str]:
    """Create a box that fits content."""
    # Calculate required width
    content_width = max((len(line) for line in content), default=0)
    width = max(content_width + 2 + (padding * 2), min_width, 4)
    if title:
        width = max(width, len(title) + 6)

    height = len(content) + 2  # Top and bottom borders

    renderer = BoxRenderer()
    return renderer.box_with_content(
        BoxSpec(width=width, height=height, style=style, title=title, padding=padding),
        content,
    )


def horizontal_rule(width: int, style: BoxStyle = BoxStyle.SINGLE) -> str:
    """Draw a horizontal line."""
    return get_chars(style).horizontal * width


def vertical_rule(height: int, style: BoxStyle = BoxStyle.SINGLE) -> list[str]:
    """Draw a vertical line."""
    char = get_chars(style).vertical
    return [char] * height
