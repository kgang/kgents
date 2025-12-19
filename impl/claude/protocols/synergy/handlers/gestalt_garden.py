"""
Gestalt to Garden Handler: Update garden plots when Gestalt analyzes.

When Gestalt completes an analysis, this handler automatically
applies observation gestures to relevant garden plots.

This enables:
- Automatic plot observation when related modules are analyzed
- Health grade synchronization between Gestalt and Garden
- Cross-jewel awareness of codebase health
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import TYPE_CHECKING, Any

from ..events import SynergyEvent, SynergyEventType, SynergyResult
from .base import BaseSynergyHandler

if TYPE_CHECKING:
    from protocols.gardener_logos.garden import GardenState
    from protocols.gardener_logos.plots import PlotState


logger = logging.getLogger("kgents.synergy.gestalt_garden")


class GestaltToGardenHandler(BaseSynergyHandler):
    """
    Handler that updates garden plots when Gestalt analyzes.

    When Gestalt completes analysis on a path:
    1. Finds garden plots that match the analyzed path
    2. Applies OBSERVE gesture with the analysis summary
    3. Updates plot metadata with health information

    Path matching uses the AGENTESE path conventions:
    - world.forge → impl/claude/agents/forge
    - self.memory → impl/claude/protocols/brain
    - etc.
    """

    def __init__(self, auto_observe: bool = True) -> None:
        """
        Initialize the handler.

        Args:
            auto_observe: If True, automatically applies observe gestures.
                         If False, just logs (useful for testing).
        """
        super().__init__()
        self._auto_observe = auto_observe

    @property
    def name(self) -> str:
        return "GestaltToGardenHandler"

    async def handle(self, event: SynergyEvent) -> SynergyResult:
        """Handle a Gestalt analysis complete event."""
        if event.event_type != SynergyEventType.ANALYSIS_COMPLETE:
            return self.skip(f"Not handling {event.event_type.value}")

        payload = event.payload
        root_path = payload.get("root_path", "")
        health_grade = payload.get("health_grade", "?")
        average_health = payload.get("average_health", 0)
        module_count = payload.get("module_count", 0)
        drift_count = payload.get("drift_count", 0)

        # Try to find the current garden
        garden = await self._get_current_garden()
        if garden is None:
            return self.skip("No active garden found")

        # Find matching plots
        matching_plots = self._find_matching_plots(garden, root_path)
        if not matching_plots:
            return self.skip(f"No plots match path: {root_path}")

        if not self._auto_observe:
            plot_names = [p.name for p in matching_plots]
            self._logger.info(f"Would update plots: {plot_names}")
            return self.success(
                message=f"Dry run - would update {len(matching_plots)} plots",
                metadata={"plots": plot_names, "health_grade": health_grade},
            )

        # Apply observe gesture to each matching plot
        updated_plots: list[str] = []
        for plot in matching_plots:
            try:
                await self._observe_plot(
                    garden=garden,
                    plot=plot,
                    health_grade=health_grade,
                    average_health=average_health,
                    module_count=module_count,
                    drift_count=drift_count,
                )
                updated_plots.append(plot.name)
            except Exception as e:
                self._logger.warning(f"Failed to observe plot {plot.name}: {e}")

        if updated_plots:
            return self.success(
                message=f"Updated {len(updated_plots)} plots with Gestalt analysis",
                metadata={
                    "plots": updated_plots,
                    "health_grade": health_grade,
                    "root_path": root_path,
                },
            )
        else:
            return self.failure("Failed to update any plots")

    async def _get_current_garden(self) -> "GardenState | None":
        """
        Get the current active garden.

        Attempts to load from:
        1. Global garden store (if available)
        2. Default garden in session context

        Returns None if no garden is active.
        """
        try:
            # Try to get from the global garden store
            from protocols.gardener_logos.persistence import get_default_store

            store = get_default_store()
            gardens = await store.list_gardens()

            if not gardens:
                return None

            # Return the most recently tended garden
            # (gardens are sorted by last_tended descending)
            return gardens[0]

        except ImportError:
            logger.debug("Garden store not available")
            return None
        except Exception as e:
            logger.warning(f"Failed to get current garden: {e}")
            return None

    def _find_matching_plots(
        self,
        garden: "GardenState",
        root_path: str,
    ) -> list["PlotState"]:
        """
        Find plots that match the analyzed path.

        Uses the plot's AGENTESE path to match against the file path:
        - world.forge → looks for "forge" in path
        - self.memory → looks for "brain" in path
        - world.town → looks for "town" or "park" in path

        Args:
            garden: The garden to search
            root_path: The analyzed file path

        Returns:
            List of matching plots
        """
        if not root_path:
            return []

        matching: list["PlotState"] = []
        root_path_lower = root_path.lower()
        path_parts = Path(root_path).parts

        # Build a set of path components for matching
        path_components = {part.lower() for part in path_parts}

        for plot in garden.plots.values():
            if self._plot_matches_path(plot, root_path_lower, path_components):
                matching.append(plot)

        return matching

    def _plot_matches_path(
        self,
        plot: "PlotState",
        root_path_lower: str,
        path_components: set[str],
    ) -> bool:
        """
        Check if a plot matches a file path.

        Matching rules:
        1. If plot has crown_jewel, match against jewel-specific paths
        2. If plot has plan_path, check if it overlaps with root_path
        3. Otherwise, match plot name against path components
        """
        # Crown jewel mapping to expected path components
        jewel_paths: dict[str, list[str]] = {
            "Atelier": ["atelier"],
            "Coalition": ["forge", "coalition"],
            "Brain": ["brain", "memory"],
            "Park": ["park", "town"],
            "Domain": ["domain", "simulation"],
            "Gestalt": ["gestalt"],
            "Gardener": ["gardener", "garden"],
        }

        # Check crown jewel mapping
        if plot.crown_jewel:
            expected_parts = jewel_paths.get(plot.crown_jewel, [])
            if any(part in path_components for part in expected_parts):
                return True

        # Check plan_path overlap
        if plot.plan_path:
            plan_name = Path(plot.plan_path).stem.lower().replace("-", "_")
            if plan_name in root_path_lower:
                return True

        # Check plot name as fallback
        plot_name_normalized = plot.name.lower().replace("-", "_")
        if plot_name_normalized in path_components:
            return True
        if any(plot_name_normalized in comp for comp in path_components):
            return True

        return False

    async def _observe_plot(
        self,
        garden: "GardenState",
        plot: "PlotState",
        health_grade: str,
        average_health: float,
        module_count: int,
        drift_count: int,
    ) -> None:
        """
        Apply an observation gesture to a plot with Gestalt data.

        Args:
            garden: The garden containing the plot
            plot: The plot to observe
            health_grade: Gestalt health grade (A+, A, B+, etc.)
            average_health: Numeric health score (0-1)
            module_count: Number of modules analyzed
            drift_count: Number of drift violations
        """
        from protocols.gardener_logos.tending import apply_gesture, observe

        # Create observation summary
        summary = (
            f"Gestalt analysis: Grade {health_grade} "
            f"({module_count} modules, {drift_count} drift violations)"
        )

        # Create and apply observe gesture
        # emit_event=False to avoid infinite loop
        gesture = observe(plot.path, summary)
        await apply_gesture(garden, gesture, emit_event=False)

        # Update plot metadata with health info
        plot.metadata["gestalt_health_grade"] = health_grade
        plot.metadata["gestalt_average_health"] = average_health
        plot.metadata["gestalt_module_count"] = module_count
        plot.metadata["gestalt_drift_count"] = drift_count
        plot.metadata["gestalt_last_analysis"] = __import__("datetime").datetime.now().isoformat()

        self._logger.info(f"Observed plot {plot.name} with Gestalt grade {health_grade}")


__all__ = ["GestaltToGardenHandler"]
