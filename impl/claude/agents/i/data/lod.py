"""
Level of Detail (LOD) Projection for Semantic Zoom.

The key abstraction that replaces discrete screens with continuous zoom.
Instead of having separate "overview", "detail", and "debug" screens,
we have a single LODProjector functor that maps:

    AgentState × LODLevel → Widget

This enables smooth transitions from orbit (overview) to surface (cockpit)
to internal (MRI) views.

The principle: Zoom is semantic, not just spatial. Each LOD reveals
different aspects of agent cognition.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from textual.widget import Widget

    from .state import AgentSnapshot


class LODLevel(Enum):
    """
    Level of Detail for agent visualization.

    ORBIT: 10,000 ft view - density card, health at a glance
    SURFACE: Operational view - cockpit, metrics, semaphores
    INTERNAL: Debug view - token context, vector store, entropy internals
    """

    ORBIT = 0  # Density card (overview)
    SURFACE = 1  # Cockpit (operational)
    INTERNAL = 2  # MRI scan (debugging)

    def zoom_in(self) -> "LODLevel | None":
        """Return the next LOD level (deeper), or None if at max zoom."""
        if self == LODLevel.ORBIT:
            return LODLevel.SURFACE
        elif self == LODLevel.SURFACE:
            return LODLevel.INTERNAL
        return None

    def zoom_out(self) -> "LODLevel | None":
        """Return the previous LOD level (shallower), or None if at min zoom."""
        if self == LODLevel.INTERNAL:
            return LODLevel.SURFACE
        elif self == LODLevel.SURFACE:
            return LODLevel.ORBIT
        return None


@dataclass
class LODProjector:
    """
    Functor: AgentState × LODLevel → Widget

    Projects agent state to appropriate detail level.
    This is the key abstraction that replaces discrete screens
    with continuous zoom.

    The functor maintains the structure of the agent state while
    transforming it to different visual representations.
    """

    def project(self, state: AgentSnapshot, level: LODLevel) -> Widget:
        """
        Generate the widget for this LOD level.

        This is a morphism in the category of widgets:
          - Objects: Widget types
          - Morphisms: Transformations between representations
          - Identity: Same LOD returns same widget type
          - Composition: LOD transitions compose naturally
        """
        from ..screens.flux import AgentCard
        from ..widgets.density_field import DensityField

        match level:
            case LODLevel.ORBIT:
                # Density card - minimal, glanceable
                return self._project_orbit(state)
            case LODLevel.SURFACE:
                # Cockpit view - operational metrics
                return self._project_surface(state)
            case LODLevel.INTERNAL:
                # MRI view - token-level internals
                return self._project_internal(state)

    def _project_orbit(self, state: AgentSnapshot) -> Widget:
        """
        Project to ORBIT level - density card.

        This is the existing AgentCard from FluxScreen.
        Shows: name, phase, density field, health, summary.
        """
        from ..screens.flux import AgentCard

        return AgentCard(state)

    def _project_surface(self, state: AgentSnapshot) -> Widget:
        """
        Project to SURFACE level - cockpit view.

        Shows:
        - Larger density field
        - Detailed metrics (temp, pressure, flow)
        - Active semaphores
        - Recent thoughts/events
        - Connection graph
        """
        from textual.widgets import Static

        # For testing, return a simple static widget
        # In a real implementation, this would be a custom CockpitView widget
        content = f"=== COCKPIT: {state.name} ===\n"
        content += f"Phase: {state.phase.value}  |  Activity: {state.activity:.2f}\n"
        content += f"Summary: {state.summary}\n"
        content += f"Children: {len(state.children)}\n"
        content += f"Connections: {len(state.connections)}\n"

        return Static(content, classes="cockpit-view")

    def _project_internal(self, state: AgentSnapshot) -> Widget:
        """
        Project to INTERNAL level - MRI scan.

        Shows:
        - Token context window visualization (mocked for now)
        - Vector store retrieval (mocked for now)
        - Entropy panel
        - Memory crystal list
        - Full event stream
        """
        from textual.widgets import Static

        # For testing, return a simple static widget
        # In a real implementation, this would be a custom MRIView widget
        entropy = state.activity * 0.3
        content = f"=== MRI SCAN: {state.name} ===\n\n"
        content += "[Token Context Window]\n"
        content += "  (Token heatmap visualization - not yet implemented)\n\n"
        content += "[Vector Store Retrieval]\n"
        content += "  (Retrieval visualization - not yet implemented)\n\n"
        content += "[Entropy Panel]\n"
        content += f"  Current entropy: {entropy:.3f}  (derived from activity)\n\n"
        content += "[Memory Crystals]\n"
        content += "  (Memory list - not yet implemented)\n\n"
        content += "[Full State]\n"
        content += f"  ID: {state.id}\n"
        content += f"  Grid Position: ({state.grid_x}, {state.grid_y})\n"
        content += f"  Phase: {state.phase.value}\n"
        content += f"  Activity: {state.activity:.3f}\n"

        return Static(content, classes="mri-view")

    def interpolate(
        self, from_level: LODLevel, to_level: LODLevel, progress: float
    ) -> dict[str, float]:
        """
        Calculate interpolation parameters between two LOD levels.

        Returns a dict of visual parameters that can be used to
        smoothly transition between levels.

        Args:
            from_level: Starting LOD level
            to_level: Target LOD level
            progress: Interpolation progress (0.0 to 1.0)

        Returns:
            Dict of parameters like opacity, scale, etc.
        """
        # Linear interpolation for now
        # Could be enhanced with easing functions
        return {
            "opacity": 1.0 - progress
            if from_level.value < to_level.value
            else progress,
            "scale": 1.0 + progress * 0.5
            if from_level.value < to_level.value
            else 1.5 - progress * 0.5,
            "detail_level": from_level.value
            + (to_level.value - from_level.value) * progress,
        }


def get_default_lod() -> LODLevel:
    """Get the default LOD level for initial view."""
    return LODLevel.ORBIT


def can_zoom_in(current_level: LODLevel) -> bool:
    """Check if zoom in is possible from current level."""
    return current_level.zoom_in() is not None


def can_zoom_out(current_level: LODLevel) -> bool:
    """Check if zoom out is possible from current level."""
    return current_level.zoom_out() is not None
