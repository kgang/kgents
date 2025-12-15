"""
anywidget components for marimo/Jupyter visualization.

These widgets use traitlets for reactive state synchronization
between Python and JavaScript, enabling live updates without
page reloads.

Design principle: Each widget's Python state can also be consumed
by the Textual TUI, creating a unified data model across surfaces.
"""

from .base import KgentsWidget
from .dialectic import DialecticWidget
from .scatter import EigenvectorScatterWidgetMarimo
from .stigmergic_field import StigmergicFieldWidget
from .timeline import TimelineWidget

__all__ = [
    "KgentsWidget",
    "StigmergicFieldWidget",
    "DialecticWidget",
    "TimelineWidget",
    "EigenvectorScatterWidgetMarimo",
]
