"""
TableWidget: Data table display with sorting and selection.

Supports column definitions, sorting, pagination, and row selection.

Example:
    widget = TableWidget(TableWidgetState(
        columns=(
            TableColumn(key="name", label="Name", sortable=True),
            TableColumn(key="score", label="Score", format="number"),
        ),
        rows=(
            {"name": "Alice", "score": 95},
            {"name": "Bob", "score": 87},
        ),
        sort_by="score",
        sort_direction="desc"
    ))
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal

from agents.i.reactive.signal import Signal
from agents.i.reactive.widget import KgentsWidget, RenderTarget


@dataclass(frozen=True)
class TableColumn:
    """
    Column definition for a table.

    Attributes:
        key: Data key in row dict
        label: Display header label
        sortable: Whether column is sortable
        width: Width in chars (CLI) or px (web)
        align: Text alignment
        format: Value format type
    """

    key: str
    label: str
    sortable: bool = False
    width: int | None = None
    align: Literal["left", "center", "right"] = "left"
    format: Literal["text", "number", "date", "code", "bar"] = "text"


@dataclass(frozen=True)
class TableWidgetState:
    """
    Immutable table widget state.

    Attributes:
        columns: Column definitions
        rows: Row data as tuple of dicts
        sort_by: Column key to sort by
        sort_direction: Sort direction
        page_size: Rows per page (0 = no pagination)
        current_page: Current page index
        selectable: Enable row selection
        selected_rows: Indices of selected rows
    """

    columns: tuple[TableColumn, ...]
    rows: tuple[dict[str, Any], ...]
    sort_by: str | None = None
    sort_direction: Literal["asc", "desc"] = "asc"
    page_size: int = 20
    current_page: int = 0
    selectable: bool = False
    selected_rows: tuple[int, ...] = ()

    @property
    def sorted_rows(self) -> tuple[dict[str, Any], ...]:
        """Get rows sorted by current sort settings."""
        if not self.sort_by:
            return self.rows

        reverse = self.sort_direction == "desc"
        return tuple(
            sorted(
                self.rows,
                key=lambda r: r.get(self.sort_by or "", ""),
                reverse=reverse,
            )
        )

    @property
    def page_rows(self) -> tuple[dict[str, Any], ...]:
        """Get rows for current page."""
        if self.page_size <= 0:
            return self.sorted_rows

        start = self.current_page * self.page_size
        end = start + self.page_size
        return self.sorted_rows[start:end]

    @property
    def total_pages(self) -> int:
        """Total number of pages."""
        if self.page_size <= 0:
            return 1
        return max(1, (len(self.rows) + self.page_size - 1) // self.page_size)


class TableWidget(KgentsWidget[TableWidgetState]):
    """
    Data table widget.

    Projections:
        - CLI: ASCII table with box drawing
        - TUI: Rich Table or Textual DataTable
        - MARIMO: HTML table with interactive features
        - JSON: State dict for API responses
    """

    def __init__(self, state: TableWidgetState | None = None) -> None:
        self.state = Signal.of(state or TableWidgetState(columns=(), rows=()))

    def project(self, target: RenderTarget) -> Any:
        """Project table to target surface."""
        match target:
            case RenderTarget.CLI:
                return self._to_cli()
            case RenderTarget.TUI:
                return self._to_tui()
            case RenderTarget.MARIMO:
                return self._to_marimo()
            case RenderTarget.JSON:
                return self._to_json()

    def _to_cli(self) -> str:
        """CLI projection: ASCII table."""
        s = self.state.value

        if not s.columns:
            return "(empty table)"

        # Calculate column widths
        widths = {}
        for col in s.columns:
            if col.width:
                widths[col.key] = col.width
            else:
                header_width = len(col.label)
                data_width = max(
                    (len(str(row.get(col.key, ""))) for row in s.page_rows),
                    default=0,
                )
                widths[col.key] = max(header_width, data_width, 3)

        # Build header
        header_cells = []
        for col in s.columns:
            w = widths[col.key]
            sort_indicator = ""
            if col.key == s.sort_by:
                sort_indicator = " ▲" if s.sort_direction == "asc" else " ▼"
            cell = f"{col.label}{sort_indicator}".ljust(w)[:w]
            header_cells.append(cell)

        header = " │ ".join(header_cells)
        separator = "─┼─".join("─" * widths[col.key] for col in s.columns)

        # Build rows
        row_lines = []
        for i, row in enumerate(s.page_rows):
            cells = []
            prefix = (
                "[x] "
                if i in s.selected_rows and s.selectable
                else "    "
                if s.selectable
                else ""
            )
            for col in s.columns:
                w = widths[col.key]
                value = str(row.get(col.key, ""))
                if col.align == "right":
                    cell = value.rjust(w)[:w]
                elif col.align == "center":
                    cell = value.center(w)[:w]
                else:
                    cell = value.ljust(w)[:w]
                cells.append(cell)
            row_lines.append(prefix + " │ ".join(cells))

        # Pagination info
        pagination = ""
        if s.page_size > 0 and s.total_pages > 1:
            pagination = f"\nPage {s.current_page + 1}/{s.total_pages}"

        return f"{header}\n{separator}\n" + "\n".join(row_lines) + pagination

    def _to_tui(self) -> Any:
        """TUI projection: Rich Table."""
        try:
            from rich.table import Table

            s = self.state.value
            table = Table(show_header=True)

            # Add columns
            from typing import Literal as TLiteral

            for col in s.columns:
                justify_map: dict[str, TLiteral["left", "center", "right"]] = {
                    "left": "left",
                    "center": "center",
                    "right": "right",
                }
                justify = justify_map.get(col.align, "left")
                sort_indicator = ""
                if col.key == s.sort_by:
                    sort_indicator = " ▲" if s.sort_direction == "asc" else " ▼"
                table.add_column(f"{col.label}{sort_indicator}", justify=justify)

            # Add rows
            for i, row in enumerate(s.page_rows):
                style = "bold" if i in s.selected_rows else ""
                cells = [str(row.get(col.key, "")) for col in s.columns]
                table.add_row(*cells, style=style)

            return table
        except ImportError:
            from rich.text import Text

            return Text(self._to_cli())

    def _to_marimo(self) -> str:
        """MARIMO projection: HTML table."""
        s = self.state.value

        # Header
        header_cells = []
        for col in s.columns:
            sort_class = "kgents-sortable" if col.sortable else ""
            sort_indicator = ""
            if col.key == s.sort_by:
                sort_indicator = " ▲" if s.sort_direction == "asc" else " ▼"
            header_cells.append(
                f'<th class="{sort_class}" data-key="{col.key}">'
                f"{col.label}{sort_indicator}</th>"
            )

        # Body rows
        body_rows = []
        for i, row in enumerate(s.page_rows):
            selected = "kgents-selected" if i in s.selected_rows else ""
            cells = []
            for col in s.columns:
                value = row.get(col.key, "")
                align_class = f"kgents-align-{col.align}"
                cells.append(f'<td class="{align_class}">{value}</td>')
            body_rows.append(f'<tr class="{selected}">{"".join(cells)}</tr>')

        # Pagination
        pagination = ""
        if s.page_size > 0 and s.total_pages > 1:
            pagination = f"""
            <div class="kgents-table-pagination">
                Page {s.current_page + 1} of {s.total_pages}
            </div>
            """

        return f"""
        <div class="kgents-table-container">
            <table class="kgents-table">
                <thead><tr>{"".join(header_cells)}</tr></thead>
                <tbody>{"".join(body_rows)}</tbody>
            </table>
            {pagination}
        </div>
        """

    def _to_json(self) -> dict[str, Any]:
        """JSON projection: state dict for API responses."""
        s = self.state.value
        return {
            "type": "table",
            "columns": [
                {
                    "key": col.key,
                    "label": col.label,
                    "sortable": col.sortable,
                    "width": col.width,
                    "align": col.align,
                    "format": col.format,
                }
                for col in s.columns
            ],
            "rows": [dict(row) for row in s.page_rows],
            "totalRows": len(s.rows),
            "sortBy": s.sort_by,
            "sortDirection": s.sort_direction,
            "pageSize": s.page_size,
            "currentPage": s.current_page,
            "totalPages": s.total_pages,
            "selectable": s.selectable,
            "selectedRows": list(s.selected_rows),
        }


__all__ = ["TableWidget", "TableWidgetState", "TableColumn"]
