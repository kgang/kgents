"""
Deep Earth + Pink/Purple color palette for I-gent v2.5.

The Semantic Flux interface uses warm, organic tones
that evoke earth and cognition.
"""

from dataclasses import dataclass

EARTH_PALETTE = {
    # Base
    "background": "#1a1a1a",  # Deep charcoal
    "background_dim": "#121212",  # Darker for contrast
    "surface": "#252525",  # Slightly lighter surface
    # Agent States
    "active": "#e6a352",  # Warm amber
    "dormant": "#4a4a5c",  # Cool slate
    "waking": "#c97b84",  # Dusty rose
    "waning": "#7d9c7a",  # Muted sage
    "void": "#6b4b8a",  # Deep purple
    # Connections
    "connection_high": "#e88a8a",  # Salmon pink
    "connection_medium": "#d4a574",  # Warm tan
    "connection_low": "#8b7ba5",  # Muted violet
    "connection_lazy": "#5a5a6a",  # Dim gray
    # Focus/Highlight
    "focus": "#f5d08a",  # Pale gold
    "focus_glow": "#f5d08a40",  # Pale gold with alpha
    "selection": "#e6a35240",  # Amber with alpha
    # Text
    "text_primary": "#f5f0e6",  # Warm white
    "text_secondary": "#b3a89a",  # Dusty tan
    "text_dim": "#6a6560",  # Muted
    # Status
    "success": "#7d9c7a",  # Sage green
    "warning": "#e6a352",  # Amber
    "error": "#c97b84",  # Dusty rose
    "info": "#8b7ba5",  # Muted violet
    # Special
    "glitch": "#9b59b6",  # Purple for void/glitch
    "morphism_arrow": "#e88a8a",  # Salmon for AGENTESE arrows
}


@dataclass(frozen=True)
class EarthTheme:
    """
    Semantic theme wrapper for the Earth palette.

    Provides semantic access to colors by purpose rather than name.
    """

    # Density field colors (by activity level)
    @staticmethod
    def density_color(activity: float) -> str:
        """Get color for agent density based on activity level 0.0-1.0."""
        if activity >= 0.8:
            return EARTH_PALETTE["active"]
        elif activity >= 0.5:
            return EARTH_PALETTE["waking"]
        elif activity >= 0.2:
            return EARTH_PALETTE["waning"]
        else:
            return EARTH_PALETTE["dormant"]

    @staticmethod
    def phase_color(phase: str) -> str:
        """Get color for agent phase."""
        phase_map = {
            "DORMANT": EARTH_PALETTE["dormant"],
            "WAKING": EARTH_PALETTE["waking"],
            "ACTIVE": EARTH_PALETTE["active"],
            "WANING": EARTH_PALETTE["waning"],
            "VOID": EARTH_PALETTE["void"],
        }
        return phase_map.get(phase.upper(), EARTH_PALETTE["dormant"])

    @staticmethod
    def connection_color(throughput: float) -> str:
        """Get color for connection based on throughput 0.0-1.0."""
        if throughput >= 0.7:
            return EARTH_PALETTE["connection_high"]
        elif throughput >= 0.3:
            return EARTH_PALETTE["connection_medium"]
        elif throughput > 0:
            return EARTH_PALETTE["connection_low"]
        else:
            return EARTH_PALETTE["connection_lazy"]


# CSS for Textual apps
EARTH_CSS = """
Screen {
    background: #1a1a1a;
}

.density-idle {
    color: #4a4a5c;
}

.density-waking {
    color: #c97b84;
}

.density-active {
    color: #e6a352;
}

.density-intense {
    color: #f5d08a;
}

.density-void {
    color: #6b4b8a;
}

.connection-high {
    color: #e88a8a;
}

.connection-medium {
    color: #d4a574;
}

.connection-low {
    color: #8b7ba5;
}

.text-primary {
    color: #f5f0e6;
}

.text-secondary {
    color: #b3a89a;
}

.focus-highlight {
    background: #e6a35240;
}

#header {
    dock: top;
    height: 1;
    background: #252525;
    color: #f5f0e6;
}

#footer {
    dock: bottom;
    height: 1;
    background: #252525;
    color: #b3a89a;
}

#main-content {
    width: 100%;
    height: 100%;
}

.agent-card {
    border: solid #4a4a5c;
    padding: 1;
    margin: 1;
}

.agent-card:focus {
    border: solid #e6a352;
    background: #252525;
}

.agent-name {
    text-style: bold;
    color: #f5f0e6;
}

.agent-phase {
    color: #b3a89a;
}
"""
