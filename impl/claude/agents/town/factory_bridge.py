"""
Factory Bridge: Wire TownFlux to IsometricWidget.

This module bridges the TownFlux event stream to the IsometricWidget
visualization, enabling the Micro-Experience Factory demo.

Design Philosophy:
- FactoryBridge streams flux events to isometric state updates
- Perturbation Principle: pads inject events via flux.perturb(), never bypass
- Replay support via TownTrace integration

Heritage:
- S1: TownFlux (agents/town/flux.py)
- S2: IsometricWidget (agents/town/isometric.py)
- S3: TownTrace (agents/town/trace_bridge.py)
- S4: ScatterState → IsometricState mapping (agents/town/isometric.py)

Crown Jewel: plans/micro-experience-factory.md
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, AsyncIterator

from agents.town.isometric import (
    DEFAULT_PERTURBATION_PADS,
    IsometricConfig,
    IsometricState,
    IsometricWidget,
    PerturbationPad,
    scatter_to_isometric,
)
from agents.town.trace_bridge import ReplayState, TownTrace
from agents.town.visualization import ScatterPoint, ScatterState

if TYPE_CHECKING:
    from agents.town.citizen import Citizen
    from agents.town.environment import TownEnvironment
    from agents.town.flux import TownEvent, TownFlux


# =============================================================================
# FactoryBridge
# =============================================================================


@dataclass
class FactoryBridgeConfig:
    """Configuration for the factory bridge."""

    # Isometric grid configuration
    grid_width: int = 12
    grid_height: int = 12

    # Enable perturbation pads
    enable_pads: bool = True

    # Enable trace recording for replay
    enable_trace: bool = True

    # Default cooldown between perturbations (ms)
    perturbation_cooldown_ms: int = 2000


class FactoryBridge:
    """
    Bridge TownFlux events to IsometricWidget state.

    The bridge:
    1. Converts TownEnvironment citizens to ScatterState
    2. Maps ScatterState to IsometricState
    3. Updates IsometricWidget as events stream
    4. Handles HITL perturbation pad presses
    """

    def __init__(
        self,
        flux: "TownFlux",
        config: FactoryBridgeConfig | None = None,
    ) -> None:
        """
        Create a FactoryBridge.

        Args:
            flux: The TownFlux to bridge from
            config: Optional configuration (uses defaults if None)
        """
        self.flux = flux
        self.config = config or FactoryBridgeConfig()

        # Create isometric config
        iso_config = IsometricConfig(
            grid_width=self.config.grid_width,
            grid_height=self.config.grid_height,
        )

        # Create widget with initial state from environment
        initial_scatter = self._environment_to_scatter(flux.environment)
        initial_isometric = scatter_to_isometric(initial_scatter, iso_config)
        self.widget = IsometricWidget(initial_isometric)

        # Track perturbation pad cooldowns
        self._pad_cooldowns: dict[str, int] = {}

    def _environment_to_scatter(
        self,
        env: "TownEnvironment",
    ) -> ScatterState:
        """
        Convert TownEnvironment to ScatterState.

        Maps each citizen to a ScatterPoint based on their eigenvectors.
        Position is derived from warmth (x) and trust (y) by default.
        """
        points: list[ScatterPoint] = []

        for citizen in env.citizens.values():
            ev = citizen.eigenvectors
            point = ScatterPoint(
                citizen_id=citizen.id,
                citizen_name=citizen.name,
                archetype=citizen.archetype,
                warmth=ev.warmth,
                curiosity=ev.curiosity,
                trust=ev.trust,
                creativity=ev.creativity,
                patience=ev.patience,
                resilience=ev.resilience,
                ambition=ev.ambition,
                # Project to 2D using warmth vs trust
                x=(ev.warmth - 0.5) * 2,  # Scale to [-1, 1]
                y=(ev.trust - 0.5) * 2,
                # Visual properties
                color=self._archetype_color(citizen.archetype),
                is_evolving=citizen.phase.name == "WORKING",
                is_selected=False,
            )
            points.append(point)

        return ScatterState(points=tuple(points))

    def _archetype_color(self, archetype: str) -> str:
        """Get color for an archetype."""
        colors = {
            "Scholar": "#3b82f6",  # Blue
            "Artisan": "#f59e0b",  # Amber
            "Explorer": "#10b981",  # Emerald
            "Caretaker": "#ec4899",  # Pink
            "Thinker": "#8b5cf6",  # Violet
            "Builder": "#6b7280",  # Gray
            "Witness": "#06b6d4",  # Cyan
        }
        return colors.get(archetype, "#64748b")

    async def run(self, num_phases: int = 4) -> AsyncIterator[str]:
        """
        Run the flux and yield ASCII frames.

        Args:
            num_phases: Number of phases to run (default: 4 = one day)

        Yields:
            ASCII visualization strings
        """
        # Yield initial frame
        yield self.widget.to_cli()

        for _ in range(num_phases):
            async for event in self.flux.step():
                # Update scatter state from environment
                scatter = self._environment_to_scatter(self.flux.environment)
                self.widget.update_from_scatter(scatter)

                # Update from event (increments tick, updates entropy)
                self.widget.update_from_event(event)

                # Yield the updated frame
                yield self.widget.to_cli()

    async def perturb(self, pad_id: str) -> "TownEvent | None":
        """
        Handle a perturbation pad press.

        Respects cooldowns and injects via flux.perturb() (never bypasses state).

        Args:
            pad_id: The pad ID to trigger ("greet", "gossip", "trade", "solo")

        Returns:
            The generated TownEvent, or None if on cooldown/invalid
        """
        # Find the pad
        pad = None
        for p in DEFAULT_PERTURBATION_PADS:
            if p.pad_id == pad_id:
                pad = p
                break

        if pad is None:
            return None

        if not pad.is_enabled:
            return None

        # Check cooldown
        import time

        current_ms = int(time.time() * 1000)
        last_used = self._pad_cooldowns.get(pad_id, 0)
        if current_ms - last_used < self.config.perturbation_cooldown_ms:
            return None

        # Inject via flux (perturbation principle)
        event = await self.flux.perturb(pad.operation)

        if event is not None:
            # Update cooldown
            self._pad_cooldowns[pad_id] = current_ms

            # Update widget
            scatter = self._environment_to_scatter(self.flux.environment)
            self.widget.update_from_scatter(scatter)
            self.widget.update_from_event(event)

        return event

    def get_frame(self) -> str:
        """Get the current ASCII frame."""
        return self.widget.to_cli()

    def get_state(self) -> IsometricState:
        """Get the current isometric state."""
        return self.widget.state.value

    def get_replay_state(self) -> ReplayState:
        """Get replay state from the flux trace."""
        return self.flux.trace.create_replay_state()

    def toggle_bloom(self) -> None:
        """Toggle slop bloom mode."""
        self.widget.toggle_slop_bloom()


# =============================================================================
# Replay Scrubber Rendering
# =============================================================================


def render_replay_bar(trace: TownTrace, replay: ReplayState) -> str:
    """
    Render the replay scrubber bar.

    Args:
        trace: The town trace with events
        replay: Current replay state

    Returns:
        ASCII replay bar string
    """
    total = replay.max_tick
    current = replay.current_tick
    width = 40

    if total == 0:
        pos = 0
    else:
        pos = int((current / max(1, total)) * width)

    pos = min(pos, width - 1)
    bar = "─" * pos + "●" + "─" * (width - pos - 1)

    return f"◀ {bar} ▶  [{current}/{total}]"


# =============================================================================
# Exports
# =============================================================================


__all__ = [
    "FactoryBridge",
    "FactoryBridgeConfig",
    "render_replay_bar",
]
