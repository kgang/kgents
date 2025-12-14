"""
Marimo anywidgets for kgents visualization.

This module provides anywidget-based components that work in:
- Marimo notebooks (reactive cells)
- Jupyter notebooks (classic interface)
- WASM-exported static sites

The key insight: anywidgets share data models with Textual widgets,
enabling the same underlying state to render in terminal OR browser.

Example:
    >>> import marimo as mo
    >>> from impl.claude.agents.i.marimo import StigmergicFieldWidget
    >>> field = StigmergicFieldWidget()
    >>> field  # Renders in marimo cell

See: plans/ui-ux-crown-jewel-strategy-v2.md
"""

from .logos_bridge import (
    AffordanceButton,
    LogosCell,
    MockUmwelt,
    ObserverState,
    affordances_to_buttons,
    create_marimo_affordances,
    invoke_sync,
    invoke_with_marimo_output,
)
from .widgets.base import KgentsWidget
from .widgets.dialectic import DialecticWidget
from .widgets.stigmergic_field import StigmergicFieldWidget
from .widgets.timeline import TimelineWidget

__all__ = [
    # Widgets
    "KgentsWidget",
    "StigmergicFieldWidget",
    "DialecticWidget",
    "TimelineWidget",
    # AGENTESE Bridge
    "LogosCell",
    "ObserverState",
    "MockUmwelt",
    "AffordanceButton",
    "affordances_to_buttons",
    "create_marimo_affordances",
    "invoke_with_marimo_output",
    "invoke_sync",
]
