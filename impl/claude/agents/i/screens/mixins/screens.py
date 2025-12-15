"""
Screen factory methods for DashboardApp.

This mixin extracts all screen creation logic from DashboardApp,
providing a clean separation between screen factories and navigation.

Philosophy: Screens are created on-demand with the data they need.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from textual.screen import Screen

    from ...data.garden import GardenSnapshot
    from ...data.state import FluxState
    from ...navigation.state import StateManager


class DashboardScreensMixin:
    """Screen factory methods for creating and registering screens.

    This mixin handles creation of:
    - Observatory (LOD -1): Ecosystem view
    - Dashboard (LOD 0): System health
    - Cockpit (LOD 1): Single agent focus
    - Flux (LOD 1): Stream processing
    - Loom (LOD 1): Pattern weaving
    - MRI (LOD 1): Memory inspection
    - Debugger (LOD 2): Forensic analysis

    Expects the implementing class to have:
    - self.demo_mode: bool
    - self.refresh_interval: float
    - self._state_manager: StateManager
    - self._flux_state: FluxState | None
    - self._gardens: list[GardenSnapshot] | None
    - self.push_screen(screen): method to push screen (from App)
    """

    # Required attributes (must be provided by implementing class)
    # Note: push_screen() is inherited from App at runtime via multiple inheritance
    demo_mode: bool
    refresh_interval: float
    _state_manager: "StateManager"
    _flux_state: "FluxState | None"
    _gardens: "list[GardenSnapshot] | None"
    push_screen: Any  # Provided by App at runtime

    # ========================================================================
    # LOD -1: Observatory (Ecosystem View)
    # ========================================================================

    def _create_observatory(self) -> None:
        """Create and push Observatory screen (LOD -1).

        Observatory shows the full ecosystem of agents - all gardens,
        flux state, and high-level system metrics.

        In demo mode, creates synthetic gardens and flux state.
        """
        from ...data.garden import create_demo_gardens
        from ...data.state import create_demo_flux_state
        from ..observatory import ObservatoryScreen

        # Create demo data if needed
        if self.demo_mode and self._gardens is None:
            self._gardens = create_demo_gardens()
        if self.demo_mode and self._flux_state is None:
            self._flux_state = create_demo_flux_state()

        self.push_screen(
            ObservatoryScreen(
                gardens=self._gardens,
                flux_state=self._flux_state,
                demo_mode=self.demo_mode,
            )
        )

    # ========================================================================
    # LOD 0: Dashboard (System Health)
    # ========================================================================

    def _create_dashboard(self) -> None:
        """Create and push Dashboard screen (LOD 0).

        Dashboard shows real-time system health metrics:
        - K-gent soul state
        - Metabolism (pressure, temperature, fever)
        - Flux event processing
        - Database triad health
        - Recent AGENTESE traces
        """
        from ..dashboard import DashboardScreen

        self.push_screen(
            DashboardScreen(
                demo_mode=self.demo_mode,
                refresh_interval=self.refresh_interval,
            )
        )

    # ========================================================================
    # LOD 1: Cockpit (Single Agent Focus)
    # ========================================================================

    def _create_cockpit(self, agent_id: str | None = None) -> None:
        """Create and push Cockpit screen (LOD 1).

        Cockpit provides a focused view of a single agent:
        - Current state and mode
        - Recent actions and decisions
        - Performance metrics
        - Configuration

        Args:
            agent_id: The agent to focus on. If None, uses the focused
                agent from state manager (observatory or terrarium).
        """
        from ..cockpit import CockpitScreen

        # Get focused agent from state manager if not provided
        if agent_id is None:
            focus = self._state_manager.get_focus(
                "observatory"
            ) or self._state_manager.get_focus("terrarium")
            agent_id = focus or ""

        self.push_screen(
            CockpitScreen(
                agent_id=agent_id,
                demo_mode=self.demo_mode,
            )
        )

    # ========================================================================
    # LOD 1: Flux (Stream Processing)
    # ========================================================================

    def _create_flux(self) -> None:
        """Create and push Flux screen (LOD 1).

        Flux shows the event stream processing pipeline:
        - Event flow and throughput
        - Queue depths and backpressure
        - Agent subscriptions
        - Performance bottlenecks
        """
        from ..flux import FluxScreen

        self.push_screen(
            FluxScreen(
                demo_mode=self.demo_mode,
            )
        )

    # ========================================================================
    # LOD 1: Loom (Pattern Weaving)
    # ========================================================================

    def _create_loom(self) -> None:
        """Create and push Loom screen (LOD 1).

        Loom visualizes pattern emergence and weaving:
        - Pattern families and relationships
        - Weaving statistics
        - Garden growth over time
        - Semantic clustering
        """
        from ..loom import LoomScreen

        self.push_screen(
            LoomScreen(
                demo_mode=self.demo_mode,
            )
        )

    # ========================================================================
    # LOD 1: MRI (Memory Inspection)
    # ========================================================================

    def _create_mri(self) -> None:
        """Create and push MRI screen (LOD 1).

        MRI provides deep memory inspection:
        - Memory layout and structure
        - Pheromone trails
        - Association graphs
        - Memory health metrics
        """
        from ..mri import MRIScreen

        self.push_screen(
            MRIScreen(
                demo_mode=self.demo_mode,
            )
        )

    # ========================================================================
    # LOD 2: Debugger (Forensic Analysis)
    # ========================================================================

    def _create_debugger(self, turn_id: str | None = None) -> None:
        """Create and push Debugger screen (LOD 2).

        Debugger provides forensic analysis of agent execution:
        - Turn DAG visualization
        - Execution traces
        - State snapshots
        - Performance profiling

        Args:
            turn_id: The specific turn to debug. If None, creates
                a demo weave for exploration.
        """
        from weave import TheWeave

        from ..debugger_screen import DebuggerScreen

        # Create a demo weave for now
        # In production, this would come from the focused agent
        weave = TheWeave()

        self.push_screen(
            DebuggerScreen(
                weave=weave,
                agent_id=turn_id,
            )
        )


__all__ = ["DashboardScreensMixin"]
