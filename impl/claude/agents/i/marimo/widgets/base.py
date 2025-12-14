"""
Base anywidget class for kgents visualization.

All kgents widgets inherit from KgentsWidget, which provides:
- Common styling (earth theme colors)
- AGENTESE handle integration
- Shared JavaScript utilities
"""

from __future__ import annotations

import anywidget
import traitlets

# Earth theme colors from impl/claude/agents/i/theme/earth.py
EARTH_COLORS = {
    "idle": "#4a4a5c",  # Slate
    "waking": "#c97b84",  # Rose
    "active": "#e6a352",  # Amber
    "intense": "#f5d08a",  # Gold
    "void": "#6b4b8a",  # Purple
    "materializing": "#7d9c7a",  # Sage
    "background": "#1a1a2e",  # Deep night
    "surface": "#252525",  # Carbon
    "text": "#e0e0e0",  # Light gray
}


class KgentsWidget(anywidget.AnyWidget):
    """
    Base class for kgents anywidgets.

    Provides:
    - Earth theme color palette
    - Common CSS variables
    - Observer context for AGENTESE integration
    """

    # Shared CSS for all kgents widgets
    _css = """
    :root {
        --kg-idle: #4a4a5c;
        --kg-waking: #c97b84;
        --kg-active: #e6a352;
        --kg-intense: #f5d08a;
        --kg-void: #6b4b8a;
        --kg-materializing: #7d9c7a;
        --kg-background: #1a1a2e;
        --kg-surface: #252525;
        --kg-text: #e0e0e0;
    }

    .kgents-widget {
        font-family: 'JetBrains Mono', 'Fira Code', monospace;
        background: var(--kg-background);
        color: var(--kg-text);
        border-radius: 4px;
        padding: 8px;
    }
    """

    # Default ESM (to be overridden by subclasses - can be str or Path)
    _esm: str | object = """
    export function render({ model, el }) {
      el.innerHTML = '<div class="kgents-widget">KgentsWidget base - override in subclass</div>';
    }
    """

    # Observer context for AGENTESE integration
    observer_id = traitlets.Unicode("default").tag(sync=True)
    observer_role = traitlets.Unicode("viewer").tag(sync=True)

    # Widget state
    is_focused = traitlets.Bool(False).tag(sync=True)
    entropy = traitlets.Float(0.0).tag(sync=True)  # 0.0-1.0, affects visual noise

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} observer={self.observer_id}>"
