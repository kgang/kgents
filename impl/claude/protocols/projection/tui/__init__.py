"""
TUI Projection Widgets.

Textual-based widgets for terminal rendering of projection components.
Provides consistent TUI experience with full keyboard navigation.
"""

from protocols.projection.tui.base import TUIProjector, TUIWidget
from protocols.projection.tui.chrome import (
    TUICachedBadge,
    TUIErrorPanel,
    TUIRefusalPanel,
)
from protocols.projection.tui.progress import TUIProgressWidget
from protocols.projection.tui.stream import TUIStreamWidget
from protocols.projection.tui.table import TUITableWidget
from protocols.projection.tui.text import TUITextWidget

__all__ = [
    "TUIProjector",
    "TUIWidget",
    "TUITextWidget",
    "TUIProgressWidget",
    "TUITableWidget",
    "TUIStreamWidget",
    "TUIErrorPanel",
    "TUIRefusalPanel",
    "TUICachedBadge",
]
