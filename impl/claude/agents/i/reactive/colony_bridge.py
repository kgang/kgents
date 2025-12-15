"""
ColonyDashboardBridge: Connect TownFlux to ColonyDashboard.

Wave 4 Component
================

The Bridge provides reactive binding between TownFlux simulation events
and ColonyDashboard visualization. It:

1. Subscribes to TownFlux events (via EventBus or direct iteration)
2. Maintains activity history per citizen
3. Updates ColonyState Signal when events occur
4. Enables real-time dashboard visualization

Architecture:
    TownFlux
        ↓ (events)
    ColonyDashboardBridge
        ↓ (Signal[ColonyState])
    ColonyDashboard
        ↓ (project)
    CLI/TUI/marimo/JSON/SSE

Quick Start:
    from agents.i.reactive.colony_bridge import ColonyDashboardBridge
    from agents.i.reactive.colony_dashboard import ColonyDashboard
    from agents.town.flux import TownFlux

    # Create bridge
    bridge = ColonyDashboardBridge(flux)

    # Create dashboard and bind to bridge signal
    dashboard = ColonyDashboard()
    dashboard.bind_signal(bridge.state_signal)

    # Process events (updates dashboard automatically)
    async for event in flux.step():
        await bridge.process_event(event)
        print(dashboard.project(RenderTarget.CLI))

See Also:
    - colony_dashboard.py: ColonyDashboard visualization
    - town/flux.py: TownFlux simulation
    - signal.py: Signal for reactive binding
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from typing import TYPE_CHECKING, Any

from agents.i.reactive.colony_dashboard import ColonyState, TownPhase
from agents.i.reactive.primitives.citizen_card import CitizenState
from agents.i.reactive.signal import Signal

if TYPE_CHECKING:
    from agents.town.flux import TownEvent, TownFlux


# =============================================================================
# Activity Buffer
# =============================================================================


@dataclass
class ActivityBuffer:
    """
    Circular buffer for citizen activity history.

    Tracks recent activity samples for sparkline visualization.
    Each sample is a float in [0.0, 1.0] representing activity intensity.
    """

    max_length: int = 20
    samples: list[float] = field(default_factory=list)

    def push(self, value: float) -> None:
        """Push a new activity sample."""
        clamped = max(0.0, min(1.0, value))
        self.samples.append(clamped)
        if len(self.samples) > self.max_length:
            self.samples = self.samples[-self.max_length :]

    def to_tuple(self) -> tuple[float, ...]:
        """Convert to immutable tuple for CitizenState."""
        return tuple(self.samples)

    def clear(self) -> None:
        """Clear all samples."""
        self.samples.clear()


# =============================================================================
# Activity Metrics
# =============================================================================


def _event_to_activity(event: TownEvent) -> float:
    """
    Convert TownEvent to activity intensity [0.0, 1.0].

    Higher intensity for:
    - Successful events
    - More tokens used
    - Higher drama contribution
    """
    if not event.success:
        return 0.1  # Failed events still show some activity

    # Base from operation type
    base_map = {
        "greet": 0.4,
        "gossip": 0.6,
        "trade": 0.7,
        "solo": 0.3,
    }
    base = base_map.get(event.operation, 0.5)

    # Boost from tokens (normalized)
    token_boost = min(0.3, event.tokens_used / 500.0)

    # Boost from drama
    drama_boost = min(0.2, event.drama_contribution)

    return min(1.0, base + token_boost + drama_boost)


def _map_flux_phase_to_town_phase(flux_phase: Any) -> TownPhase:
    """Map TownFlux.TownPhase to dashboard TownPhase."""
    phase_name = getattr(flux_phase, "name", "MORNING")
    mapping = {
        "MORNING": TownPhase.MORNING,
        "AFTERNOON": TownPhase.AFTERNOON,
        "EVENING": TownPhase.EVENING,
        "NIGHT": TownPhase.NIGHT,
    }
    return mapping.get(phase_name, TownPhase.MORNING)


# =============================================================================
# ColonyDashboardBridge
# =============================================================================


class ColonyDashboardBridge:
    """
    Bridge connecting TownFlux events to ColonyDashboard via Signal.

    Provides:
    - Activity history tracking per citizen
    - Automatic ColonyState updates from TownFlux
    - Signal for reactive dashboard binding
    - SSE-ready event streaming

    Usage:
        # Create bridge from flux
        bridge = ColonyDashboardBridge(flux)

        # Bind dashboard to bridge signal
        dashboard.bind_signal(bridge.state_signal)

        # Process events
        async for event in flux.step():
            await bridge.process_event(event)
    """

    def __init__(
        self,
        flux: TownFlux,
        activity_buffer_size: int = 20,
    ) -> None:
        self.flux = flux
        self._activity_buffers: dict[str, ActivityBuffer] = defaultdict(
            lambda: ActivityBuffer(max_length=activity_buffer_size)
        )
        self._total_events = 0
        self._total_tokens = 0

        # Signal for reactive binding
        self._state_signal = Signal.of(self._build_colony_state())

    @property
    def state_signal(self) -> Signal[ColonyState]:
        """Signal for reactive dashboard binding."""
        return self._state_signal

    @property
    def current_state(self) -> ColonyState:
        """Current ColonyState snapshot."""
        return self._state_signal.value

    def _build_colony_state(self) -> ColonyState:
        """Build ColonyState from current flux state."""
        citizens_state = []
        for citizen in self.flux.citizens:
            activity = self._activity_buffers[citizen.id].to_tuple()
            state = CitizenState.from_citizen(citizen, activity_samples=activity)
            citizens_state.append(state)

        return ColonyState(
            colony_id=f"colony-{id(self.flux) % 10000}",
            citizens=tuple(citizens_state),
            phase=_map_flux_phase_to_town_phase(self.flux.current_phase),
            day=self.flux.day,
            total_events=self._total_events,
            total_tokens=self._total_tokens,
            entropy_budget=self.flux.environment.total_accursed_surplus(),
        )

    async def process_event(self, event: TownEvent) -> ColonyState:
        """
        Process a TownEvent and update dashboard state.

        Updates activity buffers and emits new ColonyState via Signal.

        Args:
            event: The TownEvent from flux.step()

        Returns:
            Updated ColonyState
        """
        # Update totals
        self._total_events += 1
        self._total_tokens += event.tokens_used

        # Update activity buffers for participants
        activity = _event_to_activity(event)
        for participant_name in event.participants:
            # Find citizen by name
            for citizen in self.flux.citizens:
                if citizen.name == participant_name:
                    self._activity_buffers[citizen.id].push(activity)
                    break

        # Build new state and emit via Signal
        new_state = self._build_colony_state()
        self._state_signal.set(new_state)

        return new_state

    def process_event_sync(self, event: TownEvent) -> ColonyState:
        """
        Synchronous version of process_event.

        For use in contexts where async is not available.
        """
        self._total_events += 1
        self._total_tokens += event.tokens_used

        activity = _event_to_activity(event)
        for participant_name in event.participants:
            for citizen in self.flux.citizens:
                if citizen.name == participant_name:
                    self._activity_buffers[citizen.id].push(activity)
                    break

        new_state = self._build_colony_state()
        self._state_signal.set(new_state)
        return new_state

    def refresh(self) -> ColonyState:
        """
        Force refresh of ColonyState from flux.

        Use when flux state changed outside of event processing.
        """
        new_state = self._build_colony_state()
        self._state_signal.set(new_state)
        return new_state

    def clear_activity(self) -> None:
        """Clear all activity buffers."""
        for buffer in self._activity_buffers.values():
            buffer.clear()

    def reset(self) -> None:
        """Reset bridge state (counters, buffers)."""
        self._total_events = 0
        self._total_tokens = 0
        self._activity_buffers.clear()
        self.refresh()

    def to_sse_event(self) -> dict[str, Any]:
        """
        Convert current state to SSE-ready format.

        Returns dict suitable for Server-Sent Events streaming.
        """
        state = self.current_state
        return {
            "event": "colony_state",
            "id": f"{state.colony_id}-{self._total_events}",
            "data": {
                "colony_id": state.colony_id,
                "phase": state.phase.name,
                "day": state.day,
                "total_events": state.total_events,
                "total_tokens": state.total_tokens,
                "entropy_budget": state.entropy_budget,
                "citizens": [
                    {
                        "id": c.citizen_id,
                        "name": c.name,
                        "phase": c.phase.name,
                        "nphase": c.nphase.name,
                        "mood": c.mood,
                        "capability": c.capability,
                        "activity": list(c.activity[-10:]),  # Last 10 for SSE
                    }
                    for c in state.citizens
                ],
            },
            "timestamp": datetime.now().isoformat(),
        }

    def subscribe(self, callback: Any) -> Any:
        """
        Subscribe to state changes.

        Args:
            callback: Function(ColonyState) -> None

        Returns:
            Unsubscribe function
        """
        return self._state_signal.subscribe(callback)


# =============================================================================
# Factory Functions
# =============================================================================


def create_bridge_and_dashboard(
    flux: TownFlux,
    activity_buffer_size: int = 20,
) -> tuple[ColonyDashboardBridge, Any]:
    """
    Create a connected bridge and dashboard.

    Convenience function for setting up the reactive visualization.

    Args:
        flux: The TownFlux to visualize
        activity_buffer_size: Size of activity history per citizen

    Returns:
        Tuple of (bridge, dashboard) with dashboard already bound to bridge signal

    Example:
        bridge, dashboard = create_bridge_and_dashboard(flux)

        async for event in flux.step():
            await bridge.process_event(event)
            print(dashboard.project(RenderTarget.CLI))
    """
    from agents.i.reactive.colony_dashboard import ColonyDashboard

    bridge = ColonyDashboardBridge(flux, activity_buffer_size)
    dashboard = ColonyDashboard()
    dashboard.bind_signal(bridge.state_signal)

    return bridge, dashboard


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    "ActivityBuffer",
    "ColonyDashboardBridge",
    "create_bridge_and_dashboard",
]
