"""
Adapters: Bridge reactive widgets to rendering targets.

Wave 10-11 of the reactive substrate unification.

These adapters provide thin layers between KgentsWidget and target systems:

TUI (Textual):
- TextualAdapter: Wraps any KgentsWidget for Textual rendering
- FlexContainer: Connects FlexLayout to Textual containers
- ThemeBinding: Generates Textual CSS from Theme tokens
- FocusSync: Syncs AnimatedFocus with Textual focus

Notebook (marimo/Jupyter via anywidget):
- MarimoAdapter: Wraps any KgentsWidget for anywidget rendering
- NotebookTheme: CSS generation for notebook contexts
- AgentTraceWidget: Agent observability visualization

The adapter is invisible when working - just reactive widgets rendered.
"""

from __future__ import annotations

from agents.i.reactive.adapters.marimo_theme import (
    NotebookTheme,
    create_notebook_theme,
    inject_theme_css,
)
from agents.i.reactive.adapters.marimo_trace import (
    AgentTraceState,
    AgentTraceWidget,
    SpanData,
    create_trace_widget,
)

# Marimo/Notebook adapters (Wave 11)
from agents.i.reactive.adapters.marimo_widget import (
    MarimoAdapter,
    create_marimo_adapter,
    is_anywidget_available,
)
from agents.i.reactive.adapters.textual_focus import FocusSync, create_focus_sync
from agents.i.reactive.adapters.textual_layout import (
    FlexContainer,
    create_flex_container,
)
from agents.i.reactive.adapters.textual_theme import ThemeBinding, create_theme_binding
from agents.i.reactive.adapters.textual_widget import (
    TextualAdapter,
    create_textual_adapter,
)

__all__ = [
    # Textual adapters
    "TextualAdapter",
    "create_textual_adapter",
    "FlexContainer",
    "create_flex_container",
    "ThemeBinding",
    "create_theme_binding",
    "FocusSync",
    "create_focus_sync",
    # Marimo adapters
    "MarimoAdapter",
    "create_marimo_adapter",
    "is_anywidget_available",
    "NotebookTheme",
    "create_notebook_theme",
    "inject_theme_css",
    "AgentTraceWidget",
    "AgentTraceState",
    "SpanData",
    "create_trace_widget",
]
