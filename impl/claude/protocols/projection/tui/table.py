"""
TUI Table Widget: Data table with sorting and selection.

Wraps Rich Table with Textual interactivity.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal

from protocols.projection.tui.base import TUIWidget
from rich.console import RenderableType
from rich.table import Table
from rich.text import Text
from textual.widgets import Static


@dataclass(frozen=True)
class TableColumn:
    """Column definition for table."""

    key: str
    label: str
    sortable: bool = True
    width: int | None = None
    align: Literal["left", "center", "right"] = "left"


@dataclass(frozen=True)
class TableState:
    """State for table widget."""

    columns: tuple[TableColumn, ...]
    rows: tuple[dict[str, Any], ...]
    sort_by: str | None = None
    sort_direction: Literal["asc", "desc"] = "asc"
    page_size: int = 10
    current_page: int = 0
    selectable: bool = False
    selected_keys: frozenset[str] = field(default_factory=frozenset)
    row_key: str = "id"


class TUITableWidget(TUIWidget[TableState]):
    """
    TUI data table widget.

    Renders tabular data with Rich Table formatting.
    """

    DEFAULT_CSS = """
    TUITableWidget {
        height: auto;
        width: 100%;
        margin: 1 0;
    }
    """

    def render_content(self) -> RenderableType:
        """Render table content."""
        if self.state is None:
            return Text("(no data)")

        # Create Rich table
        table = Table(
            show_header=True,
            header_style="bold cyan",
            border_style="dim",
            expand=True,
        )

        # Add columns
        for col in self.state.columns:
            justify = col.align
            table.add_column(
                col.label,
                justify=justify,
                width=col.width,
                no_wrap=col.width is not None,
            )

        # Sort rows if needed
        rows = list(self.state.rows)
        if self.state.sort_by:
            sort_key = self.state.sort_by
            rows.sort(
                key=lambda r: r.get(sort_key, ""),
                reverse=self.state.sort_direction == "desc",
            )

        # Paginate
        if self.state.page_size > 0:
            start = self.state.current_page * self.state.page_size
            end = start + self.state.page_size
            rows = rows[start:end]

        # Add rows
        for row in rows:
            row_key = str(row.get(self.state.row_key, ""))
            is_selected = row_key in self.state.selected_keys

            cells = []
            for col in self.state.columns:
                value = str(row.get(col.key, ""))
                if is_selected:
                    cells.append(Text(value, style="bold reverse"))
                else:
                    cells.append(Text(value))

            table.add_row(*cells)

        return table

    def render(self) -> RenderableType:
        """Render the widget."""
        return self.render_content()


class TUISimpleTable(Static):
    """
    Simple table widget for quick rendering.

    Use this when you don't need full TUIWidget features.
    """

    def __init__(
        self,
        columns: list[str],
        rows: list[list[str]],
        title: str | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self._columns = columns
        self._rows = rows
        self._title = title

    def render(self) -> RenderableType:
        table = Table(
            title=self._title,
            show_header=True,
            header_style="bold cyan",
        )

        for col in self._columns:
            table.add_column(col)

        for row in self._rows:
            table.add_row(*row)

        return table
