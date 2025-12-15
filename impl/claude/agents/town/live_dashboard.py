"""
LiveDashboard: Unified visualization for live multi-agent orchestration.

Composes all Agent Town widgets into a unified dashboard:
- IsometricWidget (center) - Factory floor view
- EigenvectorScatterWidget (sidebar) - 7D personality space
- TimelineWidget (bottom) - Event history scrubber
- DialogueStreamWidget (overlay) - Live citizen dialogue

Architecture:
    EventBus[TownEvent]
         │
         ├──► IsometricWidget ─────► ASCII/SVG factory view
         │
         ├──► ScatterWidget ────────► ASCII/JS scatter plot
         │
         ├──► TimelineWidget ──────► Scrubber bar
         │
         └──► DialogueStream ──────► Chat bubbles

Render Targets:
- CLI: Composite ASCII art dashboard
- JSON: Unified state for web clients
- MARIMO: Compose anywidgets in notebook

See: plans/purring-squishing-duckling.md Phase 5
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from typing import TYPE_CHECKING, Any, Callable

if TYPE_CHECKING:
    from agents.i.reactive.signal import Signal
    from agents.i.reactive.widget import RenderTarget
    from agents.town.event_bus import EventBus, Subscription
    from agents.town.flux import TownEvent, TownFlux
    from agents.town.isometric import IsometricState, IsometricWidget
    from agents.town.orchestration_log import OrchestrationLog
    from agents.town.phase_governor import PhaseGovernor
    from agents.town.timeline_widget import TimelineWidget
    from agents.town.trace_bridge import TownTrace
    from agents.town.visualization import EigenvectorScatterWidgetImpl, ScatterState


# =============================================================================
# Dashboard State
# =============================================================================


class DashboardLayout(Enum):
    """Dashboard layout options."""

    FULL = auto()  # All widgets visible
    MINIMAL = auto()  # Isometric only
    COMPACT = auto()  # Isometric + timeline
    ANALYSIS = auto()  # Scatter + timeline


@dataclass
class DialogueMessage:
    """A single dialogue message in the stream."""

    speaker_id: str
    speaker_name: str
    message: str
    timestamp: datetime
    archetype: str = ""
    is_monologue: bool = False

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "speaker_id": self.speaker_id,
            "speaker_name": self.speaker_name,
            "message": self.message,
            "timestamp": self.timestamp.isoformat(),
            "archetype": self.archetype,
            "is_monologue": self.is_monologue,
        }


@dataclass
class DashboardState:
    """
    Unified dashboard state.

    Combines state from all composed widgets.
    """

    # Layout
    layout: DashboardLayout = DashboardLayout.FULL
    panel_visible: dict[str, bool] = field(
        default_factory=lambda: {
            "isometric": True,
            "scatter": True,
            "timeline": True,
            "dialogue": True,
        }
    )

    # Simulation state
    current_tick: int = 0
    current_phase: str = "MORNING"
    is_playing: bool = False
    playback_speed: float = 1.0

    # Selection (shared across widgets)
    selected_citizen_id: str | None = None
    hovered_citizen_id: str | None = None

    # Dialogue stream
    dialogue_messages: list[DialogueMessage] = field(default_factory=list)
    max_dialogue_messages: int = 10

    # Metrics
    total_events: int = 0
    total_tokens: int = 0
    citizen_count: int = 0

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "type": "dashboard_state",
            "layout": self.layout.name,
            "panel_visible": dict(self.panel_visible),
            "current_tick": self.current_tick,
            "current_phase": self.current_phase,
            "is_playing": self.is_playing,
            "playback_speed": self.playback_speed,
            "selected_citizen_id": self.selected_citizen_id,
            "hovered_citizen_id": self.hovered_citizen_id,
            "dialogue_messages": [m.to_dict() for m in self.dialogue_messages],
            "total_events": self.total_events,
            "total_tokens": self.total_tokens,
            "citizen_count": self.citizen_count,
        }


# =============================================================================
# Live Dashboard
# =============================================================================


@dataclass
class LiveDashboard:
    """
    Unified dashboard for live multi-agent orchestration.

    Composes widgets and provides:
    - Unified state management
    - Event routing to widgets
    - Multi-target rendering (CLI, JSON, MARIMO)
    - Playback control

    Example:
        from agents.town.live_dashboard import LiveDashboard

        # Create dashboard with flux
        dashboard = LiveDashboard.from_flux(flux)

        # Render to CLI
        print(dashboard.render_cli())

        # Control playback
        dashboard.play()
        dashboard.set_speed(2.0)

        # Select citizen
        dashboard.select_citizen("alice")
    """

    # Composed widgets
    isometric: "IsometricWidget | None" = None
    scatter: "EigenvectorScatterWidgetImpl | None" = None
    timeline: "TimelineWidget | None" = None

    # Data sources
    flux: "TownFlux | None" = None
    governor: "PhaseGovernor | None" = None
    event_bus: "EventBus[TownEvent] | None" = None
    trace: "TownTrace | None" = None
    log: "OrchestrationLog | None" = None

    # State
    _state: DashboardState = field(default_factory=DashboardState)

    # Event subscription
    _subscription: "Subscription[TownEvent] | None" = None
    _event_task: "asyncio.Task[None] | None" = None

    # Callbacks
    _on_state_change: list[Callable[[DashboardState], None]] = field(
        default_factory=list
    )
    _on_event: list[Callable[["TownEvent"], None]] = field(default_factory=list)

    # --- Initialization ---

    def __post_init__(self) -> None:
        """Wire up widget signals."""
        self._wire_widgets()

    def _wire_widgets(self) -> None:
        """Wire widget signals for unified state."""
        # Sync timeline state to dashboard
        if self.timeline:
            self.timeline.on_state_change(self._on_timeline_state_change)

    def _on_timeline_state_change(self, timeline_state: Any) -> None:
        """Sync timeline state to dashboard."""
        self._state.current_tick = timeline_state.current_tick
        self._state.is_playing = timeline_state.is_playing
        self._state.playback_speed = timeline_state.playback_speed
        self._notify_state_change()

    @classmethod
    def from_flux(
        cls,
        flux: "TownFlux",
        governor: "PhaseGovernor | None" = None,
        log: "OrchestrationLog | None" = None,
    ) -> "LiveDashboard":
        """
        Create dashboard from TownFlux.

        Sets up all widgets and wiring automatically.
        """
        from agents.town.event_bus import EventBus
        from agents.town.isometric import IsometricWidget
        from agents.town.timeline_widget import TimelineWidget
        from agents.town.trace_bridge import TownTrace
        from agents.town.visualization import EigenvectorScatterWidgetImpl

        # Create trace for timeline
        trace = TownTrace()

        # Create event bus if not provided by flux
        event_bus = flux.event_bus
        if event_bus is None:
            event_bus = EventBus()
            flux.set_event_bus(event_bus)

        # Create widgets
        isometric = IsometricWidget()
        scatter = EigenvectorScatterWidgetImpl()
        timeline = TimelineWidget(trace=trace, log=log)

        # Create dashboard
        dashboard = cls(
            isometric=isometric,
            scatter=scatter,
            timeline=timeline,
            flux=flux,
            governor=governor,
            event_bus=event_bus,
            trace=trace,
            log=log,
        )

        # Subscribe to events
        dashboard._subscribe_to_events()

        return dashboard

    def _subscribe_to_events(self) -> None:
        """Subscribe to event bus for live updates."""
        if self.event_bus is None:
            return

        self._subscription = self.event_bus.subscribe()

        async def process_events() -> None:
            if self._subscription is None:
                return
            async for event in self._subscription:
                if event is None:
                    break
                await self._handle_event(event)

        try:
            loop = asyncio.get_running_loop()
            self._event_task = loop.create_task(process_events())
        except RuntimeError:
            # No running loop - will start when loop available
            pass

    async def _handle_event(self, event: "TownEvent") -> None:
        """Process an incoming event."""
        # Update trace
        if self.trace:
            self.trace.append(event)

        # Update state
        self._state.total_events += 1
        self._state.total_tokens += event.tokens_used
        self._state.current_phase = event.phase.name

        # Add dialogue message if it's a dialogue event
        if event.operation in ("dialogue", "monologue") and event.message:
            self._add_dialogue_message(event)

        # Update timeline
        if self.timeline:
            self.timeline._state.max_tick = len(self.trace.events) if self.trace else 0
            self.timeline._notify_state_change()

        # Notify callbacks
        for callback in self._on_event:
            callback(event)
        self._notify_state_change()

    def _add_dialogue_message(self, event: "TownEvent") -> None:
        """Add dialogue event to message stream."""
        if not event.participants:
            return

        msg = DialogueMessage(
            speaker_id=event.participants[0],
            speaker_name=event.participants[0].title(),
            message=event.message,
            timestamp=event.timestamp,
            archetype=event.metadata.get("archetype", ""),
            is_monologue=event.operation == "monologue",
        )

        self._state.dialogue_messages.append(msg)

        # Keep only recent messages
        while len(self._state.dialogue_messages) > self._state.max_dialogue_messages:
            self._state.dialogue_messages.pop(0)

    # --- Playback Control ---

    def play(self) -> None:
        """Start playback."""
        self._state.is_playing = True
        if self.timeline:
            self.timeline.play()
        if self.governor:
            pass  # Governor handles its own playback
        self._notify_state_change()

    def pause(self) -> None:
        """Pause playback."""
        self._state.is_playing = False
        if self.timeline:
            self.timeline.pause()
        if self.governor:
            self.governor.pause()
        self._notify_state_change()

    def toggle_play(self) -> bool:
        """Toggle playback. Returns new is_playing state."""
        if self._state.is_playing:
            self.pause()
        else:
            self.play()
        return self._state.is_playing

    def set_speed(self, speed: float) -> None:
        """Set playback speed."""
        self._state.playback_speed = max(0.25, min(4.0, speed))
        if self.timeline:
            self.timeline.set_speed(self._state.playback_speed)
        if self.governor:
            self.governor.set_speed(self._state.playback_speed)
        self._notify_state_change()

    async def seek(self, tick: int) -> bool:
        """Seek to a specific tick."""
        if self.timeline:
            return await self.timeline.seek(tick)
        return False

    def step_forward(self) -> int:
        """Step forward one event."""
        if self.timeline:
            return self.timeline.step_forward()
        return self._state.current_tick

    def step_backward(self) -> int:
        """Step backward one event."""
        if self.timeline:
            return self.timeline.step_backward()
        return self._state.current_tick

    # --- Selection ---

    def select_citizen(self, citizen_id: str | None) -> None:
        """Select a citizen across all widgets."""
        self._state.selected_citizen_id = citizen_id

        if self.timeline:
            self.timeline.select_event(None)  # Clear event selection

        if self.scatter:
            self.scatter.select_citizen(citizen_id)

        self._notify_state_change()

    def hover_citizen(self, citizen_id: str | None) -> None:
        """Hover over a citizen across all widgets."""
        self._state.hovered_citizen_id = citizen_id

        if self.scatter:
            self.scatter.hover_citizen(citizen_id)

        self._notify_state_change()

    # --- Layout Control ---

    def set_layout(self, layout: DashboardLayout) -> None:
        """Set dashboard layout."""
        self._state.layout = layout

        # Update panel visibility based on layout
        if layout == DashboardLayout.MINIMAL:
            self._state.panel_visible = {
                "isometric": True,
                "scatter": False,
                "timeline": False,
                "dialogue": False,
            }
        elif layout == DashboardLayout.COMPACT:
            self._state.panel_visible = {
                "isometric": True,
                "scatter": False,
                "timeline": True,
                "dialogue": False,
            }
        elif layout == DashboardLayout.ANALYSIS:
            self._state.panel_visible = {
                "isometric": False,
                "scatter": True,
                "timeline": True,
                "dialogue": False,
            }
        else:  # FULL
            self._state.panel_visible = {
                "isometric": True,
                "scatter": True,
                "timeline": True,
                "dialogue": True,
            }

        self._notify_state_change()

    def toggle_panel(self, panel: str) -> bool:
        """Toggle a panel's visibility. Returns new state."""
        if panel in self._state.panel_visible:
            self._state.panel_visible[panel] = not self._state.panel_visible[panel]
            self._notify_state_change()
            return self._state.panel_visible[panel]
        return False

    # --- Rendering ---

    def project(self, target: "RenderTarget") -> Any:
        """
        Project dashboard to rendering target.

        CLI: Composite ASCII art dashboard
        JSON: Unified state dict
        MARIMO: Return component dict for notebook composition
        """
        from agents.i.reactive.widget import RenderTarget

        if target == RenderTarget.CLI:
            return self.render_cli()
        elif target == RenderTarget.JSON:
            return self.render_json()
        elif target == RenderTarget.MARIMO:
            return self.render_marimo()
        else:
            return self.render_json()

    def render_cli(self, width: int = 80) -> str:
        """
        Render dashboard as CLI output.

        Layout:
        ┌─────────────────────────────────────────────┐
        │ AGENT TOWN                          ▶ 1.0x │
        ├─────────────────────────────────────────────┤
        │                                             │
        │   Isometric View          │   Scatter      │
        │                           │                │
        │                           │                │
        ├─────────────────────────────────────────────┤
        │ [0042]───────────●────────────── [0100]    │
        └─────────────────────────────────────────────┘
        """
        lines = []

        # Header
        play_icon = "▶" if self._state.is_playing else "⏸"
        header = f"AGENT TOWN [{self._state.current_phase}]"
        status = f"{play_icon} {self._state.playback_speed}x"
        header_line = f"│ {header:<{width - len(status) - 5}}{status} │"

        lines.append("┌" + "─" * (width - 2) + "┐")
        lines.append(header_line)
        lines.append("├" + "─" * (width - 2) + "┤")

        # Main content area
        main_lines = []

        if self._state.panel_visible.get("isometric") and self.isometric:
            from agents.i.reactive.widget import RenderTarget

            iso_output = self.isometric.project(RenderTarget.CLI)
            iso_lines = str(iso_output).split("\n") if iso_output else []
            main_lines.extend(iso_lines[:10])  # Limit height

        if not main_lines:
            main_lines = ["  No visualization data"] * 5

        for line in main_lines:
            padded = f"│ {line:<{width - 4}} │"
            lines.append(padded[:width])

        # Timeline section
        lines.append("├" + "─" * (width - 2) + "┤")

        if self._state.panel_visible.get("timeline") and self.timeline:
            timeline_output = self.timeline.render_cli(width=width - 4)
            for tl_line in timeline_output.split("\n")[:3]:
                lines.append(f"│ {tl_line:<{width - 4}} │")
        else:
            lines.append(f"│ {'Tick: ' + str(self._state.current_tick):<{width - 4}} │")

        # Dialogue section (if visible)
        if self._state.panel_visible.get("dialogue") and self._state.dialogue_messages:
            lines.append("├" + "─" * (width - 2) + "┤")
            for msg in self._state.dialogue_messages[-3:]:
                prefix = "💭" if msg.is_monologue else "💬"
                dialogue_line = f"{prefix} {msg.speaker_name}: {msg.message[:40]}..."
                lines.append(f"│ {dialogue_line:<{width - 4}} │")

        # Footer with metrics
        lines.append("├" + "─" * (width - 2) + "┤")
        metrics = (
            f"Events: {self._state.total_events} | Tokens: {self._state.total_tokens}"
        )
        lines.append(f"│ {metrics:<{width - 4}} │")

        lines.append("└" + "─" * (width - 2) + "┘")

        return "\n".join(lines)

    def render_json(self) -> dict[str, Any]:
        """Render dashboard as JSON for web clients."""
        result: dict[str, Any] = {
            "dashboard": self._state.to_dict(),
        }

        if self.isometric:
            from agents.i.reactive.widget import RenderTarget

            result["isometric"] = self.isometric.project(RenderTarget.JSON)

        if self.scatter:
            from agents.i.reactive.widget import RenderTarget

            result["scatter"] = self.scatter.project(RenderTarget.JSON)

        if self.timeline:
            result["timeline"] = self.timeline.render_json()

        return result

    def render_marimo(self) -> dict[str, Any]:
        """
        Render for marimo notebook.

        Returns dict of components for notebook composition.
        """
        components: dict[str, Any] = {
            "state": self._state.to_dict(),
        }

        if self.isometric:
            from agents.i.reactive.widget import RenderTarget

            components["isometric"] = self.isometric.project(RenderTarget.MARIMO)

        if self.scatter:
            from agents.i.reactive.widget import RenderTarget

            components["scatter"] = self.scatter.project(RenderTarget.MARIMO)

        if self.timeline:
            components["timeline"] = self.timeline.render_json()

        return components

    # --- Callbacks ---

    def on_state_change(
        self, callback: Callable[[DashboardState], None]
    ) -> Callable[[], None]:
        """Register callback for state changes. Returns unsubscribe function."""
        self._on_state_change.append(callback)
        return lambda: self._on_state_change.remove(callback)

    def on_event(self, callback: Callable[["TownEvent"], None]) -> Callable[[], None]:
        """Register callback for events. Returns unsubscribe function."""
        self._on_event.append(callback)
        return lambda: self._on_event.remove(callback)

    def _notify_state_change(self) -> None:
        """Notify all state change listeners."""
        for callback in self._on_state_change:
            callback(self._state)

    # --- State Access ---

    @property
    def state(self) -> DashboardState:
        """Get current dashboard state."""
        return self._state

    @property
    def is_playing(self) -> bool:
        """Whether playback is active."""
        return self._state.is_playing

    @property
    def current_tick(self) -> int:
        """Current tick position."""
        return self._state.current_tick

    @property
    def playback_speed(self) -> float:
        """Current playback speed."""
        return self._state.playback_speed

    # --- Lifecycle ---

    def close(self) -> None:
        """Clean up resources."""
        if self._event_task:
            self._event_task.cancel()

        if self._subscription:
            self._subscription.close()


# =============================================================================
# Factory Functions
# =============================================================================


def create_live_dashboard(
    flux: "TownFlux | None" = None,
    governor: "PhaseGovernor | None" = None,
    log: "OrchestrationLog | None" = None,
) -> LiveDashboard:
    """
    Create a live dashboard.

    Args:
        flux: TownFlux for event generation
        governor: PhaseGovernor for playback control
        log: OrchestrationLog for persistence

    Returns:
        Configured LiveDashboard
    """
    if flux:
        return LiveDashboard.from_flux(flux, governor=governor, log=log)
    return LiveDashboard()


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    "DashboardLayout",
    "DashboardState",
    "DialogueMessage",
    "LiveDashboard",
    "create_live_dashboard",
]
