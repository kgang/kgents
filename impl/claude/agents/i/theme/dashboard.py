"""
DashboardTheme - Unified theme for the I-gent dashboard.

Provides:
- Consistent colors across all screens
- Animation timing constants
- Spacing and typography
- Loading, error, and help overlays

Philosophy: "Joy comes from consistency and smooth transitions."
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass


@dataclass(frozen=True)
class DashboardTheme:
    """
    Unified theme for the I-gent dashboard.

    All colors, animations, and spacing in one place.
    """

    # ==========================================================================
    # Colors - Based on Deep Earth + Pink/Purple
    # ==========================================================================

    # Primary
    background: str = "#1a1a1a"
    background_dim: str = "#121212"
    surface: str = "#252525"
    border: str = "#4a4a5c"
    border_focus: str = "#e6a352"

    # Text
    text_primary: str = "#f5f0e6"
    text_secondary: str = "#b3a89a"
    text_muted: str = "#6a6560"

    # Accent
    accent: str = "#e6a352"
    accent_bright: str = "#f5d08a"
    accent_dim: str = "#d4a574"

    # Status
    success: str = "#6bcf7f"
    warning: str = "#ffd93d"
    error: str = "#ff6b6b"
    info: str = "#8ac4e8"

    # Semantic - Yield states
    yield_pending: str = "#ffd93d"
    yield_approved: str = "#6bcf7f"
    yield_rejected: str = "#ff6b6b"

    # Semantic - Agent states
    agent_dormant: str = "#4a4a5c"
    agent_waking: str = "#c97b84"
    agent_active: str = "#e6a352"
    agent_intense: str = "#f5d08a"
    agent_void: str = "#6b4b8a"

    # Semantic - Connections
    connection_high: str = "#e88a8a"
    connection_medium: str = "#d4a574"
    connection_low: str = "#8b7ba5"
    connection_lazy: str = "#5a5a6a"

    # Special
    glitch: str = "#9b59b6"
    oblique: str = "#8b7ba5"

    # ==========================================================================
    # Animation Timing (milliseconds)
    # ==========================================================================

    # Screen transitions
    zoom_duration: int = 150  # Smooth zoom in/out
    screen_fade_in: int = 100  # Screen appears
    screen_fade_out: int = 80  # Screen disappears

    # Widget animations
    materialize_duration: int = 500  # Agent appears
    dematerialize_duration: int = 500  # Agent disappears
    glitch_duration: int = 200  # Glitch flash
    heartbeat_period: int = 2000  # Breathing rate

    # Overlays
    overlay_fade_in: int = 120
    overlay_fade_out: int = 80

    # Loading states
    spinner_interval: int = 100  # Spinner frame rate
    progress_update: int = 50  # Progress bar smoothness

    # ==========================================================================
    # Spacing and Typography
    # ==========================================================================

    # Padding
    padding_small: int = 1
    padding_medium: int = 2
    padding_large: int = 3

    # Borders
    border_round: str = "round"
    border_solid: str = "solid"
    border_double: str = "double"
    border_thick: str = "thick"

    # Typography
    font_heading: str = "bold"
    font_body: str = "normal"
    font_code: str = "italic"

    # ==========================================================================
    # Animation Curves
    # ==========================================================================

    # Easing functions (for future use)
    ease_in_out: str = "cubic-bezier(0.4, 0.0, 0.2, 1.0)"
    ease_out: str = "cubic-bezier(0.0, 0.0, 0.2, 1.0)"
    ease_in: str = "cubic-bezier(0.4, 0.0, 1.0, 1.0)"

    # ==========================================================================
    # Semantic Color Helpers
    # ==========================================================================

    @staticmethod
    def get_status_color(status: str) -> str:
        """Get color for a status string."""
        status_map = {
            "success": "#6bcf7f",
            "error": "#ff6b6b",
            "warning": "#ffd93d",
            "info": "#8ac4e8",
            "pending": "#ffd93d",
            "approved": "#6bcf7f",
            "rejected": "#ff6b6b",
        }
        return status_map.get(status.lower(), "#b3a89a")

    @staticmethod
    def get_activity_color(activity: float) -> str:
        """Get color for agent activity level 0.0-1.0."""
        if activity >= 0.8:
            return "#f5d08a"  # intense
        elif activity >= 0.5:
            return "#e6a352"  # active
        elif activity >= 0.2:
            return "#c97b84"  # waking
        else:
            return "#4a4a5c"  # dormant

    @staticmethod
    def get_phase_color(phase: str) -> str:
        """Get color for agent phase."""
        phase_map = {
            "dormant": "#4a4a5c",
            "waking": "#c97b84",
            "active": "#e6a352",
            "intense": "#f5d08a",
            "void": "#6b4b8a",
        }
        return phase_map.get(phase.lower(), "#4a4a5c")

    # ==========================================================================
    # CSS Generation
    # ==========================================================================

    @classmethod
    def generate_css(cls) -> str:
        """Generate Textual CSS with all theme colors."""
        theme = cls()
        return f"""
/* Dashboard Theme - Generated from DashboardTheme */

Screen {{
    background: {theme.background};
}}

/* Text Styles */
.text-primary {{
    color: {theme.text_primary};
}}

.text-secondary {{
    color: {theme.text_secondary};
}}

.text-muted {{
    color: {theme.text_muted};
}}

/* Status Colors */
.status-success {{
    color: {theme.success};
}}

.status-warning {{
    color: {theme.warning};
}}

.status-error {{
    color: {theme.error};
}}

.status-info {{
    color: {theme.info};
}}

/* Agent States */
.agent-dormant {{
    color: {theme.agent_dormant};
}}

.agent-waking {{
    color: {theme.agent_waking};
}}

.agent-active {{
    color: {theme.agent_active};
}}

.agent-intense {{
    color: {theme.agent_intense};
}}

.agent-void {{
    color: {theme.agent_void};
}}

/* Focus States */
.focus-border {{
    border: {theme.border_solid} {theme.border_focus};
    background: {theme.surface};
}}

/* Standard Components */
#header {{
    dock: top;
    height: 1;
    background: {theme.surface};
    color: {theme.text_primary};
}}

#footer {{
    dock: bottom;
    height: 1;
    background: {theme.surface};
    color: {theme.text_secondary};
}}

/* Overlays */
.overlay-container {{
    background: {theme.background};
    border: {theme.border_solid} {theme.border};
}}

.overlay-header {{
    color: {theme.accent};
    text-style: bold;
}}

.overlay-body {{
    color: {theme.text_secondary};
}}

.overlay-footer {{
    color: {theme.text_muted};
    border-top: {theme.border_solid} {theme.border};
}}
"""


# Global singleton instance
THEME = DashboardTheme()


__all__ = ["DashboardTheme", "THEME"]
