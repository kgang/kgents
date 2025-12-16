"""
Widget Vocabulary: Core widget types for projection.

This module defines the shared widget vocabulary that works across
CLI, Web, and marimo surfaces. Each widget has:

1. A state dataclass (FooWidgetState) - immutable data
2. A widget class (FooWidget) - extends KgentsWidget with projections

Widgets:
    - TextWidget: Simple text display with formatting
    - SelectWidget: Single/multi-select dropdown
    - ConfirmWidget: Binary confirm/deny prompt
    - ProgressWidget: Progress bars and step indicators
    - TableWidget: Data table display
    - GraphWidget: Charts and graphs (Chart.js for web)
    - StreamWidget: Streaming text display

Usage:
    from protocols.projection.widgets import TextWidget, TextWidgetState

    widget = TextWidget(TextWidgetState(content="Hello", variant="heading"))
    print(widget.to_cli())  # "# Hello"
"""

from protocols.projection.widgets.confirm import ConfirmWidget, ConfirmWidgetState
from protocols.projection.widgets.graph import (
    GraphDataset,
    GraphType,
    GraphWidget,
    GraphWidgetState,
)
from protocols.projection.widgets.progress import (
    ProgressStep,
    ProgressVariant,
    ProgressWidget,
    ProgressWidgetState,
)
from protocols.projection.widgets.select import (
    SelectOption,
    SelectWidget,
    SelectWidgetState,
)
from protocols.projection.widgets.stream import StreamWidget, StreamWidgetState
from protocols.projection.widgets.table import (
    TableColumn,
    TableWidget,
    TableWidgetState,
)
from protocols.projection.widgets.text import TextVariant, TextWidget, TextWidgetState

__all__ = [
    # Text
    "TextWidget",
    "TextWidgetState",
    "TextVariant",
    # Select
    "SelectWidget",
    "SelectWidgetState",
    "SelectOption",
    # Confirm
    "ConfirmWidget",
    "ConfirmWidgetState",
    # Progress
    "ProgressWidget",
    "ProgressWidgetState",
    "ProgressVariant",
    "ProgressStep",
    # Table
    "TableWidget",
    "TableWidgetState",
    "TableColumn",
    # Graph
    "GraphWidget",
    "GraphWidgetState",
    "GraphType",
    "GraphDataset",
    # Stream
    "StreamWidget",
    "StreamWidgetState",
]
