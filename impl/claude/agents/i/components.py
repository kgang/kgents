"""
UI Components for I-gent.

Reusable terminal UI components for building agent interfaces:
- ProgressBar: Animated progress indicator
- Panel: Bordered content container
- StatusLine: Compact status display
- Meter: Value gauge with thresholds
- Table: Tabular data display

These components are building blocks for TUI applications.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class Color(Enum):
    """ANSI color codes."""

    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    ITALIC = "\033[3m"
    UNDERLINE = "\033[4m"

    BLACK = "\033[30m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"

    BG_BLACK = "\033[40m"
    BG_RED = "\033[41m"
    BG_GREEN = "\033[42m"
    BG_YELLOW = "\033[43m"
    BG_BLUE = "\033[44m"
    BG_MAGENTA = "\033[45m"
    BG_CYAN = "\033[46m"
    BG_WHITE = "\033[47m"


def colorize(text: str, *colors: Color, enabled: bool = True) -> str:
    """Apply colors to text."""
    if not enabled:
        return text
    prefix = "".join(c.value for c in colors)
    return f"{prefix}{text}{Color.RESET.value}"


# ─────────────────────────────────────────────────────────────
# Progress Bar
# ─────────────────────────────────────────────────────────────


@dataclass
class ProgressBarStyle:
    """Style configuration for progress bar."""

    fill_char: str = "█"
    empty_char: str = "░"
    left_cap: str = "["
    right_cap: str = "]"
    fill_color: Color = Color.GREEN
    empty_color: Color = Color.DIM
    show_percentage: bool = True
    show_label: bool = True


@dataclass
class ProgressBar:
    """
    Animated progress bar component.

    Example:
        >>> bar = ProgressBar(width=20, label="Loading")
        >>> bar.update(0.5)
        >>> print(bar.render())
        Loading [██████████░░░░░░░░░░] 50%
    """

    width: int = 20
    label: str = ""
    value: float = 0.0  # 0.0 to 1.0
    style: ProgressBarStyle = field(default_factory=ProgressBarStyle)
    use_color: bool = True

    def update(self, value: float) -> None:
        """Update progress value (0.0 to 1.0)."""
        self.value = max(0.0, min(1.0, value))

    def render(self) -> str:
        """Render the progress bar."""
        filled = int(self.value * self.width)
        empty = self.width - filled

        fill = self.style.fill_char * filled
        rest = self.style.empty_char * empty

        if self.use_color:
            fill = colorize(fill, self.style.fill_color)
            rest = colorize(rest, self.style.empty_color)

        bar = f"{self.style.left_cap}{fill}{rest}{self.style.right_cap}"

        parts = []
        if self.style.show_label and self.label:
            parts.append(self.label)
        parts.append(bar)
        if self.style.show_percentage:
            parts.append(f"{int(self.value * 100)}%")

        return " ".join(parts)


class SpinnerStyle(Enum):
    """Spinner animation styles."""

    DOTS = ("⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏")
    LINE = ("-", "\\", "|", "/")
    CIRCLE = ("◐", "◓", "◑", "◒")
    ARROW = ("←", "↖", "↑", "↗", "→", "↘", "↓", "↙")
    BOUNCE = ("⠁", "⠂", "⠄", "⠂")


@dataclass
class Spinner:
    """
    Animated spinner for indeterminate progress.

    Example:
        >>> spinner = Spinner(label="Processing")
        >>> for _ in range(10):
        ...     print(spinner.render())
        ...     spinner.tick()
    """

    label: str = ""
    style: SpinnerStyle = SpinnerStyle.DOTS
    frame: int = 0
    color: Color = Color.CYAN
    use_color: bool = True

    def tick(self) -> None:
        """Advance to next frame."""
        self.frame = (self.frame + 1) % len(self.style.value)

    def render(self) -> str:
        """Render the spinner."""
        char = str(self.style.value[self.frame])
        if self.use_color:
            char = colorize(char, self.color)

        if self.label:
            return f"{char} {self.label}"
        return char


# ─────────────────────────────────────────────────────────────
# Panel
# ─────────────────────────────────────────────────────────────


@dataclass
class BorderStyle:
    """Border characters for panels."""

    top_left: str = "┌"
    top_right: str = "┐"
    bottom_left: str = "└"
    bottom_right: str = "┘"
    horizontal: str = "─"
    vertical: str = "│"

    @classmethod
    def single(cls) -> "BorderStyle":
        """Single-line border."""
        return cls()

    @classmethod
    def double(cls) -> "BorderStyle":
        """Double-line border."""
        return cls(
            top_left="╔",
            top_right="╗",
            bottom_left="╚",
            bottom_right="╝",
            horizontal="═",
            vertical="║",
        )

    @classmethod
    def rounded(cls) -> "BorderStyle":
        """Rounded corner border."""
        return cls(
            top_left="╭",
            top_right="╮",
            bottom_left="╰",
            bottom_right="╯",
        )

    @classmethod
    def none(cls) -> "BorderStyle":
        """No border (spaces)."""
        return cls(
            top_left=" ",
            top_right=" ",
            bottom_left=" ",
            bottom_right=" ",
            horizontal=" ",
            vertical=" ",
        )


@dataclass
class Panel:
    """
    Bordered content container.

    Example:
        >>> panel = Panel(title="Status", width=30)
        >>> panel.add_line("CPU: 45%")
        >>> panel.add_line("Memory: 2.1GB")
        >>> print(panel.render())
        ┌─ Status ──────────────────┐
        │ CPU: 45%                  │
        │ Memory: 2.1GB             │
        └───────────────────────────┘
    """

    width: int = 40
    title: str = ""
    lines: list[str] = field(default_factory=list)
    border: BorderStyle = field(default_factory=BorderStyle.single)
    padding: int = 1
    title_color: Color = Color.BOLD
    border_color: Color = Color.DIM
    use_color: bool = True

    def add_line(self, line: str) -> None:
        """Add a line of content."""
        self.lines.append(line)

    def clear(self) -> None:
        """Clear all content."""
        self.lines.clear()

    def _colorize(self, text: str, *colors: Color) -> str:
        """Apply colors if enabled."""
        return colorize(text, *colors, enabled=self.use_color)

    def render(self) -> str:
        """Render the panel."""
        result = []
        inner_width = self.width - 2  # Account for borders
        pad = " " * self.padding

        # Top border with title
        if self.title:
            title_text = f" {self.title} "
            title_len = len(title_text)
            remaining = inner_width - title_len
            left_bar = self.border.horizontal
            right_bar = self.border.horizontal * remaining

            title_display = self._colorize(title_text, self.title_color)
            top = (
                self._colorize(self.border.top_left + left_bar, self.border_color)
                + title_display
                + self._colorize(right_bar + self.border.top_right, self.border_color)
            )
        else:
            bar = self.border.horizontal * inner_width
            top = self._colorize(
                f"{self.border.top_left}{bar}{self.border.top_right}",
                self.border_color,
            )
        result.append(top)

        # Content lines
        content_width = inner_width - (self.padding * 2)
        for line in self.lines:
            # Truncate or pad line
            if len(line) > content_width:
                line = line[: content_width - 3] + "..."
            line = line.ljust(content_width)

            border_char = self._colorize(self.border.vertical, self.border_color)
            result.append(f"{border_char}{pad}{line}{pad}{border_char}")

        # Bottom border
        bar = self.border.horizontal * inner_width
        bottom = self._colorize(
            f"{self.border.bottom_left}{bar}{self.border.bottom_right}",
            self.border_color,
        )
        result.append(bottom)

        return "\n".join(result)


# ─────────────────────────────────────────────────────────────
# Meter
# ─────────────────────────────────────────────────────────────


@dataclass
class MeterThreshold:
    """Threshold for meter coloring."""

    value: float
    color: Color


@dataclass
class Meter:
    """
    Value gauge with thresholds.

    Example:
        >>> meter = Meter(
        ...     label="CPU",
        ...     min_value=0,
        ...     max_value=100,
        ...     thresholds=[
        ...         MeterThreshold(70, Color.YELLOW),
        ...         MeterThreshold(90, Color.RED),
        ...     ],
        ... )
        >>> meter.set_value(85)
        >>> print(meter.render())
        CPU: [████████░░] 85%
    """

    label: str = ""
    value: float = 0.0
    min_value: float = 0.0
    max_value: float = 100.0
    width: int = 10
    thresholds: list[MeterThreshold] = field(default_factory=list)
    default_color: Color = Color.GREEN
    show_value: bool = True
    unit: str = "%"
    use_color: bool = True

    def set_value(self, value: float) -> None:
        """Set the current value."""
        self.value = max(self.min_value, min(self.max_value, value))

    def _get_color(self) -> Color:
        """Get color based on thresholds."""
        for threshold in sorted(self.thresholds, key=lambda t: t.value, reverse=True):
            if self.value >= threshold.value:
                return threshold.color
        return self.default_color

    def render(self) -> str:
        """Render the meter."""
        # Normalize value to 0-1
        range_size = self.max_value - self.min_value
        if range_size == 0:
            normalized = 0.0
        else:
            normalized = (self.value - self.min_value) / range_size

        filled = int(normalized * self.width)
        empty = self.width - filled

        bar_fill = "█" * filled
        bar_empty = "░" * empty

        if self.use_color:
            color = self._get_color()
            bar_fill = colorize(bar_fill, color)
            bar_empty = colorize(bar_empty, Color.DIM)

        bar = f"[{bar_fill}{bar_empty}]"

        parts = []
        if self.label:
            parts.append(f"{self.label}:")
        parts.append(bar)
        if self.show_value:
            parts.append(f"{int(self.value)}{self.unit}")

        return " ".join(parts)


# ─────────────────────────────────────────────────────────────
# Status Line
# ─────────────────────────────────────────────────────────────


@dataclass
class StatusItem:
    """Individual status indicator."""

    label: str
    value: str
    color: Color = Color.WHITE


@dataclass
class StatusLine:
    """
    Compact status bar with multiple items.

    Example:
        >>> status = StatusLine()
        >>> status.add("Mode", "NORMAL", Color.GREEN)
        >>> status.add("Branch", "main", Color.CYAN)
        >>> status.add("Line", "42", Color.WHITE)
        >>> print(status.render())
        Mode: NORMAL | Branch: main | Line: 42
    """

    items: list[StatusItem] = field(default_factory=list)
    separator: str = " | "
    use_color: bool = True

    def add(self, label: str, value: str, color: Color = Color.WHITE) -> None:
        """Add a status item."""
        self.items.append(StatusItem(label=label, value=value, color=color))

    def update(self, label: str, value: str, color: Color | None = None) -> None:
        """Update an existing item by label."""
        for item in self.items:
            if item.label == label:
                item.value = value
                if color:
                    item.color = color
                return
        # Not found, add it
        self.add(label, value, color or Color.WHITE)

    def clear(self) -> None:
        """Clear all items."""
        self.items.clear()

    def render(self) -> str:
        """Render the status line."""
        parts = []
        for item in self.items:
            if self.use_color:
                value = colorize(item.value, item.color)
            else:
                value = item.value
            parts.append(f"{item.label}: {value}")
        return self.separator.join(parts)


# ─────────────────────────────────────────────────────────────
# Table
# ─────────────────────────────────────────────────────────────


@dataclass
class TableColumn:
    """Column definition for table."""

    header: str
    width: int | None = None  # Auto-size if None
    align: str = "left"  # "left", "right", "center"
    color: Color | None = None


@dataclass
class Table:
    """
    Simple table display.

    Example:
        >>> table = Table(
        ...     columns=[
        ...         TableColumn("Name", width=15),
        ...         TableColumn("Status", width=10),
        ...         TableColumn("Count", width=8, align="right"),
        ...     ]
        ... )
        >>> table.add_row(["Agent-1", "Active", "42"])
        >>> table.add_row(["Agent-2", "Idle", "0"])
        >>> print(table.render())
        Name            Status     Count
        ─────────────────────────────────
        Agent-1         Active        42
        Agent-2         Idle           0
    """

    columns: list[TableColumn] = field(default_factory=list)
    rows: list[list[str]] = field(default_factory=list)
    header_color: Color = Color.BOLD
    separator: str = "─"
    use_color: bool = True

    def add_row(self, row: list[str]) -> None:
        """Add a data row."""
        self.rows.append(row)

    def clear(self) -> None:
        """Clear all rows."""
        self.rows.clear()

    def _get_widths(self) -> list[int]:
        """Calculate column widths."""
        widths = []
        for i, col in enumerate(self.columns):
            if col.width:
                widths.append(col.width)
            else:
                # Auto-size: max of header and all row values
                max_width = len(col.header)
                for row in self.rows:
                    if i < len(row):
                        max_width = max(max_width, len(row[i]))
                widths.append(max_width)
        return widths

    def _align_cell(self, value: str, width: int, align: str) -> str:
        """Align a cell value."""
        if align == "right":
            return value.rjust(width)
        elif align == "center":
            return value.center(width)
        else:
            return value.ljust(width)

    def render(self) -> str:
        """Render the table."""
        widths = self._get_widths()
        result = []

        # Header row
        header_parts = []
        for col, width in zip(self.columns, widths):
            cell = self._align_cell(col.header, width, "left")
            if self.use_color:
                cell = colorize(cell, self.header_color)
            header_parts.append(cell)
        result.append("  ".join(header_parts))

        # Separator
        total_width = sum(widths) + (len(widths) - 1) * 2  # 2 spaces between columns
        result.append(self.separator * total_width)

        # Data rows
        for row in self.rows:
            row_parts = []
            for i, (col, width) in enumerate(zip(self.columns, widths)):
                value = row[i] if i < len(row) else ""
                cell = self._align_cell(value, width, col.align)
                if self.use_color and col.color:
                    cell = colorize(cell, col.color)
                row_parts.append(cell)
            result.append("  ".join(row_parts))

        return "\n".join(result)


# ─────────────────────────────────────────────────────────────
# Composite Components
# ─────────────────────────────────────────────────────────────


@dataclass
class DashboardPanel:
    """
    A dashboard panel with header, meters, and status.

    Combines Panel, Meter, and StatusLine for agent dashboards.
    """

    title: str
    width: int = 40
    meters: list[Meter] = field(default_factory=list)
    status: StatusLine = field(default_factory=StatusLine)
    use_color: bool = True

    def add_meter(
        self,
        label: str,
        value: float,
        max_value: float = 100,
        thresholds: list[MeterThreshold] | None = None,
    ) -> None:
        """Add a meter to the dashboard."""
        meter = Meter(
            label=label,
            value=value,
            max_value=max_value,
            thresholds=thresholds or [],
            width=self.width - len(label) - 15,  # Account for label, value, brackets
            use_color=self.use_color,
        )
        self.meters.append(meter)

    def render(self) -> str:
        """Render the dashboard panel."""
        panel = Panel(
            title=self.title,
            width=self.width,
            use_color=self.use_color,
        )

        for meter in self.meters:
            panel.add_line(meter.render())

        if self.status.items:
            panel.add_line("")  # Blank line
            panel.add_line(self.status.render())

        return panel.render()


# ─────────────────────────────────────────────────────────────
# Factory Functions
# ─────────────────────────────────────────────────────────────


def create_progress_bar(
    label: str = "",
    width: int = 20,
    initial: float = 0.0,
) -> ProgressBar:
    """Create a progress bar."""
    bar = ProgressBar(width=width, label=label)
    bar.update(initial)
    return bar


def create_panel(
    title: str = "",
    width: int = 40,
    border: str = "single",
) -> Panel:
    """Create a panel with specified border style."""
    border_style = {
        "single": BorderStyle.single(),
        "double": BorderStyle.double(),
        "rounded": BorderStyle.rounded(),
        "none": BorderStyle.none(),
    }.get(border, BorderStyle.single())

    return Panel(title=title, width=width, border=border_style)


def create_dashboard(
    title: str,
    metrics: dict[str, float],
    width: int = 50,
) -> DashboardPanel:
    """
    Create a dashboard panel from metrics.

    Args:
        title: Panel title
        metrics: Dict of metric_name -> value
        width: Panel width

    Returns:
        Configured DashboardPanel
    """
    dashboard = DashboardPanel(title=title, width=width)

    for label, value in metrics.items():
        dashboard.add_meter(label, value)

    return dashboard
