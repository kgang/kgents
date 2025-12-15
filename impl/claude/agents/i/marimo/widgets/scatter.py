"""
Eigenvector Scatter Widget for Marimo (Phase 6 DEVELOP).

Live scatter plot of Agent Town citizens in 7D eigenvector space.
Integrates with SSE for real-time updates.

Heritage:
- S1: visualization.py (ScatterPoint, ScatterState, EigenvectorScatterWidgetImpl)
- S2: base.py (KgentsWidget, EARTH_COLORS)
- S3: stigmergic_field.js (Canvas patterns, model sync)
- S4: town.py API (/events SSE, /scatter JSON)

Laws:
- L1: `points` serialization matches ScatterPoint.to_dict() schema
- L2: `sse_connected` reflects actual EventSource state
- L3: `clicked_citizen_id` update triggers marimo cell re-run
- L4: SVG viewBox maintains 400x300 aspect ratio
- L5: Point transitions animate via CSS (0.3s ease-out)
- L6: SSE disconnect → browser auto-reconnect via EventSource
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Any

import traitlets
from agents.i.marimo.widgets.base import KgentsWidget

if TYPE_CHECKING:
    from agents.town.visualization import (
        EigenvectorScatterWidgetImpl,
        ProjectionMethod,
        ScatterPoint,
    )


class EigenvectorScatterWidgetMarimo(KgentsWidget):
    """
    Live scatter plot with SSE integration for marimo.

    Usage:
        import marimo as mo
        from agents.i.marimo.widgets import EigenvectorScatterWidgetMarimo

        scatter = EigenvectorScatterWidgetMarimo(town_id="abc123")
        widget = mo.ui.anywidget(scatter)
        widget  # Display in cell

    The widget connects to /v1/town/{town_id}/events for real-time updates
    and renders citizens as SVG circles in 2D projected eigenvector space.
    """

    # ESM module path (relative to this file)
    _esm = Path(__file__).parent / "js" / "scatter.js"

    # --- Connection Properties ---

    town_id = traitlets.Unicode(
        default_value="",
        help="Town ID to connect to",
    ).tag(sync=True)

    api_base = traitlets.Unicode(
        default_value="/v1/town",
        help="API base URL for town endpoints",
    ).tag(sync=True)

    # --- Scatter State (synced to JS) ---

    points = traitlets.List(
        trait=traitlets.Dict(),
        default_value=[],
        help="List of ScatterPoint.to_dict() for each citizen",
    ).tag(sync=True)

    projection = traitlets.Unicode(
        default_value="PAIR_WT",
        help="ProjectionMethod name (PAIR_WT, PAIR_CC, PCA, etc.)",
    ).tag(sync=True)

    selected_citizen_id = traitlets.Unicode(
        default_value="",
        allow_none=True,
        help="Currently selected citizen ID",
    ).tag(sync=True)

    hovered_citizen_id = traitlets.Unicode(
        default_value="",
        allow_none=True,
        help="Currently hovered citizen ID",
    ).tag(sync=True)

    # --- SSE Status (set from JS) ---

    sse_connected = traitlets.Bool(
        default_value=False,
        help="Whether SSE EventSource is connected",
    ).tag(sync=True)

    sse_error = traitlets.Unicode(
        default_value="",
        help="Last SSE error message, if any",
    ).tag(sync=True)

    # --- Interaction (set from JS on click) ---

    clicked_citizen_id = traitlets.Unicode(
        default_value="",
        help="Last clicked citizen ID (triggers cell re-run)",
    ).tag(sync=True)

    # --- Display Options ---

    show_labels = traitlets.Bool(
        default_value=True,
        help="Whether to show citizen name labels",
    ).tag(sync=True)

    show_coalition_colors = traitlets.Bool(
        default_value=True,
        help="Whether to color by coalition membership",
    ).tag(sync=True)

    animate_transitions = traitlets.Bool(
        default_value=True,
        help="Whether to animate point position changes",
    ).tag(sync=True)

    # --- Filter State ---

    show_evolving_only = traitlets.Bool(
        default_value=False,
        help="Only show evolving citizens",
    ).tag(sync=True)

    archetype_filter = traitlets.List(
        trait=traitlets.Unicode(),
        default_value=[],
        help="Filter to specific archetypes (empty = show all)",
    ).tag(sync=True)

    coalition_filter = traitlets.Unicode(
        default_value="",
        help="Filter to specific coalition ID",
    ).tag(sync=True)

    # --- Methods ---

    def connect_to_town(self, town_id: str) -> None:
        """
        Connect to a town's SSE stream.

        This triggers the JS EventSource to connect to:
            {api_base}/{town_id}/events

        Args:
            town_id: Town ID to connect to
        """
        self.town_id = town_id

    def set_projection(self, method: "ProjectionMethod") -> None:
        """
        Change the projection method.

        Args:
            method: ProjectionMethod enum value
        """
        self.projection = method.name

    def load_from_widget(self, impl: "EigenvectorScatterWidgetImpl") -> None:
        """
        Load state from an EigenvectorScatterWidgetImpl.

        Converts ScatterState to the format expected by JS.

        Args:
            impl: The widget implementation to load from
        """
        state = impl.state.value
        self.points = [p.to_dict() for p in state.points]
        self.projection = state.projection.name
        self.selected_citizen_id = state.selected_citizen_id or ""
        self.hovered_citizen_id = state.hovered_citizen_id or ""
        self.show_evolving_only = state.show_evolving_only
        self.archetype_filter = list(state.archetype_filter)
        self.coalition_filter = state.coalition_filter or ""
        self.show_labels = state.show_labels
        self.show_coalition_colors = state.show_coalition_colors
        self.animate_transitions = state.animate_transitions

    def load_from_points(self, points: list["ScatterPoint"]) -> None:
        """
        Load points directly.

        Args:
            points: List of ScatterPoint objects
        """
        self.points = [p.to_dict() for p in points]

    def select_citizen(self, citizen_id: str | None) -> None:
        """Select a citizen by ID."""
        self.selected_citizen_id = citizen_id or ""

    def filter_by_archetype(self, archetypes: list[str]) -> None:
        """Filter to specific archetypes."""
        self.archetype_filter = archetypes

    def filter_by_coalition(self, coalition_id: str | None) -> None:
        """Filter to members of a coalition."""
        self.coalition_filter = coalition_id or ""

    def toggle_evolving_only(self) -> None:
        """Toggle showing only evolving citizens."""
        self.show_evolving_only = not self.show_evolving_only


# --- Exports ---

__all__ = [
    "EigenvectorScatterWidgetMarimo",
]
