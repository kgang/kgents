"""
MarkdownTable Token Implementation.

The MarkdownTable token represents GFM-style tables as structured data that
can be viewed, edited, and exported. Tables are parsed into rows/columns with
alignment information preserved.

Affordances:
- hover: Show table structure (rows, columns, alignment)
- click: Focus for structured editing
- right-click: Context menu with export options (CSV, JSON, HTML)

Table Structure:
Tables follow GitHub Flavored Markdown format:
- Header row: | col1 | col2 |
- Separator row: |------|------| (with optional alignment markers)
- Data rows: | data | data |

Alignment markers:
- :--- = left align
- :---: = center align
- ---: = right align

See: spec/protocols/interactive-text.md
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from services.interactive_text.contracts import (
    Affordance,
    AffordanceAction,
    Observer,
    ObserverRole,
)

from .base import BaseMeaningToken, filter_affordances_by_observer


class TableAlignment(str, Enum):
    """Column alignment options."""

    LEFT = "left"
    CENTER = "center"
    RIGHT = "right"


@dataclass(frozen=True)
class TableColumn:
    """A column in the table.

    Attributes:
        header: Column header text
        alignment: Column alignment
        index: Column index (0-based)
    """

    header: str
    alignment: TableAlignment
    index: int

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "header": self.header,
            "alignment": self.alignment.value,
            "index": self.index,
        }


@dataclass(frozen=True)
class TableCell:
    """A cell in the table.

    Attributes:
        value: Cell value (trimmed)
        row: Row index (0-based, excluding header)
        column: Column index (0-based)
    """

    value: str
    row: int
    column: int

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "value": self.value,
            "row": self.row,
            "column": self.column,
        }


@dataclass(frozen=True)
class TableHoverInfo:
    """Information displayed on table hover.

    Attributes:
        row_count: Number of data rows (excluding header)
        column_count: Number of columns
        columns: Column definitions with alignment
    """

    row_count: int
    column_count: int
    columns: tuple[TableColumn, ...]

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "row_count": self.row_count,
            "column_count": self.column_count,
            "columns": [c.to_dict() for c in self.columns],
        }


@dataclass(frozen=True)
class TableExportResult:
    """Result of exporting a table.

    Attributes:
        format: Export format (csv, json, html)
        content: Exported content
    """

    format: str
    content: str

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "format": self.format,
            "content": self.content,
        }


@dataclass(frozen=True)
class TableEditResult:
    """Result of focusing table for editing.

    Attributes:
        columns: Column definitions
        rows: List of row data (list of cell values)
        source_text: Original markdown source
    """

    columns: tuple[TableColumn, ...]
    rows: tuple[tuple[str, ...], ...]
    source_text: str

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "columns": [c.to_dict() for c in self.columns],
            "rows": [list(row) for row in self.rows],
            "source_text": self.source_text,
        }


class MarkdownTableToken(BaseMeaningToken[str]):
    """Token representing a GFM-style markdown table.

    Tables are parsed into structured data for interactive editing
    and export capabilities.

    Pattern: |header|header|\n|---|---|\n|data|data|
    """

    # Pattern for GFM tables
    PATTERN = re.compile(
        r"^\|?[^\n|]+(?:\|[^\n|]+)+\|?\n"  # Header row
        r"\|?[\s]*:?-{3,}:?[\s]*(?:\|[\s]*:?-{3,}:?[\s]*)+\|?\n"  # Separator row
        r"(?:\|?[^\n|]*(?:\|[^\n|]*)+\|?\n?)+",  # Data rows (1+)
        re.MULTILINE,
    )

    # Capabilities required for certain affordances
    REQUIRED_CAPABILITIES: dict[str, frozenset[str]] = {
        "hover": frozenset(),
        "edit": frozenset(),
        "export": frozenset(),
    }

    def __init__(
        self,
        source_text: str,
        source_position: tuple[int, int],
        columns: tuple[TableColumn, ...],
        rows: tuple[tuple[str, ...], ...],
    ) -> None:
        """Initialize a MarkdownTable token.

        Args:
            source_text: The original matched text
            source_position: (start, end) position in source document
            columns: Parsed column definitions
            rows: Parsed row data
        """
        self._source_text = source_text
        self._source_position = source_position
        self._columns = columns
        self._rows = rows

    @classmethod
    def from_match(cls, match: re.Match[str]) -> MarkdownTableToken:
        """Create token from regex match.

        Args:
            match: Regex match object from pattern matching

        Returns:
            New MarkdownTableToken instance
        """
        source_text = match.group(0)
        lines = source_text.strip().split("\n")

        # Parse header row
        headers = cls._parse_row(lines[0])

        # Parse separator row for alignment
        alignments = cls._parse_alignments(lines[1])

        # Ensure alignments match headers
        while len(alignments) < len(headers):
            alignments.append(TableAlignment.LEFT)

        # Build column definitions
        columns = tuple(
            TableColumn(header=h.strip(), alignment=alignments[i], index=i)
            for i, h in enumerate(headers)
        )

        # Parse data rows
        rows: list[tuple[str, ...]] = []
        for line in lines[2:]:
            if line.strip():
                cells = cls._parse_row(line)
                # Pad or truncate to match column count
                while len(cells) < len(columns):
                    cells.append("")
                rows.append(tuple(c.strip() for c in cells[: len(columns)]))

        return cls(
            source_text=source_text,
            source_position=(match.start(), match.end()),
            columns=columns,
            rows=tuple(rows),
        )

    @staticmethod
    def _parse_row(line: str) -> list[str]:
        """Parse a table row into cells.

        Args:
            line: Table row line

        Returns:
            List of cell values
        """
        # Strip leading/trailing pipes and split
        line = line.strip()
        if line.startswith("|"):
            line = line[1:]
        if line.endswith("|"):
            line = line[:-1]
        return line.split("|")

    @staticmethod
    def _parse_alignments(separator_line: str) -> list[TableAlignment]:
        """Parse alignment from separator row.

        Args:
            separator_line: The separator row (e.g., |:---|---:|)

        Returns:
            List of column alignments
        """
        alignments: list[TableAlignment] = []
        cells = MarkdownTableToken._parse_row(separator_line)

        for cell in cells:
            cell = cell.strip()
            if cell.startswith(":") and cell.endswith(":"):
                alignments.append(TableAlignment.CENTER)
            elif cell.endswith(":"):
                alignments.append(TableAlignment.RIGHT)
            else:
                alignments.append(TableAlignment.LEFT)

        return alignments

    @property
    def token_type(self) -> str:
        """Token type name from registry."""
        return "markdown_table"

    @property
    def source_text(self) -> str:
        """Original text that was recognized as this token."""
        return self._source_text

    @property
    def source_position(self) -> tuple[int, int]:
        """(start, end) position in source document."""
        return self._source_position

    @property
    def columns(self) -> tuple[TableColumn, ...]:
        """Column definitions."""
        return self._columns

    @property
    def rows(self) -> tuple[tuple[str, ...], ...]:
        """Row data."""
        return self._rows

    @property
    def row_count(self) -> int:
        """Number of data rows (excluding header)."""
        return len(self._rows)

    @property
    def column_count(self) -> int:
        """Number of columns."""
        return len(self._columns)

    async def get_affordances(self, observer: Observer) -> list[Affordance]:
        """Get available affordances for this observer.

        Args:
            observer: The observer requesting affordances

        Returns:
            List of available affordances
        """
        affordances = [
            Affordance(
                name="hover",
                action=AffordanceAction.HOVER,
                handler="self.document.table.hover",
                enabled=True,
                description="View table structure",
            ),
            Affordance(
                name="edit",
                action=AffordanceAction.CLICK,
                handler="self.document.table.edit",
                enabled=True,
                description="Edit table in structured editor",
            ),
            Affordance(
                name="export",
                action=AffordanceAction.RIGHT_CLICK,
                handler="self.document.table.export",
                enabled=True,
                description="Export table as CSV, JSON, or HTML",
            ),
        ]

        return affordances

    async def project(self, target: str, observer: Observer) -> str | dict[str, Any]:
        """Project token to target-specific rendering.

        Args:
            target: Target name (e.g., "cli", "web", "json")
            observer: The observer receiving the projection

        Returns:
            Target-specific rendering of this token
        """
        if target == "cli":
            # Rich table rendering
            return self._render_cli()

        elif target == "json":
            return {
                "type": "markdown_table",
                "columns": [c.to_dict() for c in self._columns],
                "rows": [list(row) for row in self._rows],
                "row_count": self.row_count,
                "column_count": self.column_count,
                "source_text": self._source_text,
            }

        else:  # web or default
            return self._source_text

    def _render_cli(self) -> str:
        """Render table for CLI using Rich formatting."""
        # Simple ASCII table for now
        lines = []

        # Header
        header = " | ".join(c.header for c in self._columns)
        lines.append(f"| {header} |")

        # Separator
        sep = " | ".join("-" * max(3, len(c.header)) for c in self._columns)
        lines.append(f"| {sep} |")

        # Rows
        for row in self._rows:
            row_str = " | ".join(row)
            lines.append(f"| {row_str} |")

        return "\n".join(lines)

    async def _execute_action(
        self,
        action: AffordanceAction,
        observer: Observer,
        **kwargs: Any,
    ) -> Any:
        """Execute the action for this token.

        Args:
            action: The action being performed
            observer: The observer performing the action
            **kwargs: Additional action-specific arguments

        Returns:
            Action-specific result
        """
        if action == AffordanceAction.HOVER:
            return await self._handle_hover(observer)
        elif action == AffordanceAction.CLICK:
            return await self._handle_edit(observer)
        elif action == AffordanceAction.RIGHT_CLICK:
            format_type = kwargs.get("format", "csv")
            return await self._handle_export(observer, format_type)
        else:
            return None

    async def _handle_hover(self, observer: Observer) -> TableHoverInfo:
        """Handle hover action - show table structure."""
        return TableHoverInfo(
            row_count=self.row_count,
            column_count=self.column_count,
            columns=self._columns,
        )

    async def _handle_edit(self, observer: Observer) -> TableEditResult:
        """Handle click action - focus for editing."""
        return TableEditResult(
            columns=self._columns,
            rows=self._rows,
            source_text=self._source_text,
        )

    async def _handle_export(
        self, observer: Observer, format_type: str = "csv"
    ) -> TableExportResult:
        """Handle export action.

        Args:
            observer: The observer requesting export
            format_type: Export format (csv, json, html)

        Returns:
            Exported content
        """
        if format_type == "csv":
            content = self._export_csv()
        elif format_type == "json":
            content = self._export_json()
        elif format_type == "html":
            content = self._export_html()
        else:
            content = self._export_csv()
            format_type = "csv"

        return TableExportResult(format=format_type, content=content)

    def _export_csv(self) -> str:
        """Export table as CSV."""
        import csv
        import io

        output = io.StringIO()
        writer = csv.writer(output)

        # Header
        writer.writerow([c.header for c in self._columns])

        # Rows
        for row in self._rows:
            writer.writerow(row)

        return output.getvalue()

    def _export_json(self) -> str:
        """Export table as JSON."""
        import json

        data = []
        for row in self._rows:
            row_dict = {}
            for i, col in enumerate(self._columns):
                row_dict[col.header] = row[i] if i < len(row) else ""
            data.append(row_dict)

        return json.dumps(data, indent=2)

    def _export_html(self) -> str:
        """Export table as HTML."""
        lines = ["<table>", "  <thead>", "    <tr>"]

        # Headers
        for col in self._columns:
            align = f' style="text-align: {col.alignment.value}"'
            lines.append(f"      <th{align}>{col.header}</th>")

        lines.extend(["    </tr>", "  </thead>", "  <tbody>"])

        # Rows
        for row in self._rows:
            lines.append("    <tr>")
            for i, cell in enumerate(row):
                align_style = ""
                if i < len(self._columns):
                    align_style = f' style="text-align: {self._columns[i].alignment.value}"'
                lines.append(f"      <td{align_style}>{cell}</td>")
            lines.append("    </tr>")

        lines.extend(["  </tbody>", "</table>"])

        return "\n".join(lines)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        base = super().to_dict()
        base.update(
            {
                "columns": [c.to_dict() for c in self._columns],
                "rows": [list(row) for row in self._rows],
                "row_count": self.row_count,
                "column_count": self.column_count,
            }
        )
        return base


# =============================================================================
# Factory Functions
# =============================================================================


def create_markdown_table_token(
    text: str,
    position: tuple[int, int] | None = None,
) -> MarkdownTableToken | None:
    """Create a MarkdownTable token from text.

    Args:
        text: Text that may contain a markdown table
        position: Optional (start, end) position override

    Returns:
        MarkdownTableToken if text matches pattern, None otherwise
    """
    match = MarkdownTableToken.PATTERN.search(text)
    if match is None:
        return None

    token = MarkdownTableToken.from_match(match)

    # Override position if provided
    if position is not None:
        return MarkdownTableToken(
            source_text=token.source_text,
            source_position=position,
            columns=token.columns,
            rows=token.rows,
        )

    return token


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    "MarkdownTableToken",
    "TableColumn",
    "TableCell",
    "TableAlignment",
    "TableHoverInfo",
    "TableEditResult",
    "TableExportResult",
    "create_markdown_table_token",
]
