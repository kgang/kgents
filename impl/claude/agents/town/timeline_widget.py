"""
TimelineWidget: Unified timeline for time-travel debugging.

The timeline scrubber provides:
- Visual event history with scrub bar
- seek(tick) to restore state at any point
- Dependency chain highlighting (Mazurkiewicz traces)
- Step forward/backward navigation
- Integration with Signal snapshots

Architecture:
    EventBus
        │
        ▼
    TimelineWidget ─────► TownTrace (event history)
        │
        ├─► OrchestrationLog (checkpoints)
        │
        └─► Signal snapshots (widget state)

See: plans/purring-squishing-duckling.md Phase 4
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from datetime import datetime
from typing import TYPE_CHECKING, Any, Callable, Generic, TypeVar

if TYPE_CHECKING:
    from agents.i.reactive.signal import Signal, Snapshot
    from agents.town.event_bus import EventBus, Subscription
    from agents.town.flux import TownEvent
    from agents.town.orchestration_log import Checkpoint, OrchestrationLog
    from agents.town.trace_bridge import ReplayState, TownTrace, TownTraceEvent


T = TypeVar("T")


# =============================================================================
# Timeline State
# =============================================================================


@dataclass
class TimelineState:
    """
    Current state of the timeline widget.

    Captures position, selection, and display options.
    """

    # Current position
    current_tick: int = 0
    max_tick: int = 0

    # Playback state
    is_playing: bool = False
    playback_speed: float = 1.0

    # Selection
    selected_event_id: str | None = None
    hovered_event_id: str | None = None

    # Display options
    show_dependent_chain: bool = True
    highlight_independent: bool = True
    show_phase_markers: bool = True

    # Time bounds
    start_time: datetime | None = None
    end_time: datetime | None = None

    # Checkpoint info
    nearest_checkpoint_tick: int | None = None
    checkpoint_count: int = 0

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "type": "timeline_state",
            "current_tick": self.current_tick,
            "max_tick": self.max_tick,
            "is_playing": self.is_playing,
            "playback_speed": self.playback_speed,
            "selected_event_id": self.selected_event_id,
            "hovered_event_id": self.hovered_event_id,
            "show_dependent_chain": self.show_dependent_chain,
            "highlight_independent": self.highlight_independent,
            "show_phase_markers": self.show_phase_markers,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "nearest_checkpoint_tick": self.nearest_checkpoint_tick,
            "checkpoint_count": self.checkpoint_count,
        }


@dataclass(frozen=True)
class TimelineEvent:
    """
    A single event in the timeline view.

    Includes rendering metadata for visualization.
    """

    tick: int
    event_id: str
    phase: str
    operation: str
    participants: tuple[str, ...]
    timestamp: datetime
    success: bool
    message: str = ""

    # Rendering metadata
    is_dependent: bool = False  # Part of selected event's dependency chain
    is_independent: bool = False  # Can commute with selected event
    is_checkpoint: bool = False  # Has checkpoint at this tick

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "tick": self.tick,
            "event_id": self.event_id,
            "phase": self.phase,
            "operation": self.operation,
            "participants": list(self.participants),
            "timestamp": self.timestamp.isoformat(),
            "success": self.success,
            "message": self.message,
            "is_dependent": self.is_dependent,
            "is_independent": self.is_independent,
            "is_checkpoint": self.is_checkpoint,
        }


# =============================================================================
# Widget Snapshot Manager
# =============================================================================


@dataclass
class WidgetSnapshotManager:
    """
    Manages Signal snapshots for time-travel.

    Tracks registered widgets and their snapshots at each tick.
    """

    # Registered signals: name → Signal
    _signals: dict[str, "Signal[Any]"] = field(default_factory=dict)

    # Snapshots at each tick: tick → {name → snapshot_dict}
    _snapshots: dict[int, dict[str, Any]] = field(default_factory=dict)

    def register(self, name: str, signal: "Signal[Any]") -> None:
        """Register a signal for snapshot management."""
        self._signals[name] = signal

    def unregister(self, name: str) -> None:
        """Unregister a signal."""
        self._signals.pop(name, None)

    def capture(self, tick: int) -> dict[str, Any]:
        """
        Capture snapshots of all registered signals at this tick.

        Returns dict of {name: snapshot_dict} for serialization.
        """
        snapshots = {}
        for name, signal in self._signals.items():
            snap = signal.snapshot()
            snapshots[name] = {
                "value": snap.value,
                "timestamp": snap.timestamp,
                "generation": snap.generation,
            }
        self._snapshots[tick] = snapshots
        return snapshots

    def restore(self, tick: int) -> bool:
        """
        Restore all signals to their state at the given tick.

        Returns True if successful, False if no snapshot exists.
        """
        snapshots = self._snapshots.get(tick)
        if not snapshots:
            return False

        for name, snap_dict in snapshots.items():
            signal = self._signals.get(name)
            if signal:
                signal.set(snap_dict["value"])

        return True

    def get_nearest_tick(self, target_tick: int) -> int | None:
        """Find the nearest tick with a snapshot."""
        if not self._snapshots:
            return None

        ticks = sorted(self._snapshots.keys())

        # Binary search for nearest
        for i, tick in enumerate(ticks):
            if tick >= target_tick:
                if i == 0:
                    return tick
                # Check which is closer
                if target_tick - ticks[i - 1] <= tick - target_tick:
                    return ticks[i - 1]
                return tick

        return ticks[-1]

    def prune_before(self, tick: int) -> int:
        """Remove snapshots before a tick. Returns count pruned."""
        to_remove = [t for t in self._snapshots if t < tick]
        for t in to_remove:
            del self._snapshots[t]
        return len(to_remove)

    @property
    def tick_count(self) -> int:
        """Number of ticks with snapshots."""
        return len(self._snapshots)


# =============================================================================
# Timeline Widget
# =============================================================================


@dataclass
class TimelineWidget:
    """
    Unified timeline for time-travel debugging.

    Provides:
    - Event history visualization
    - seek(tick) to restore state
    - Dependency chain highlighting
    - Step forward/backward

    Example:
        from agents.town.timeline_widget import TimelineWidget

        timeline = TimelineWidget(trace=trace, log=log)
        timeline.register_signal("scatter_zoom", zoom_signal)

        # Seek to tick 50
        await timeline.seek(50)

        # Step through events
        timeline.step_forward()
        timeline.step_backward()
    """

    # Core data sources
    trace: "TownTrace | None" = None
    log: "OrchestrationLog | None" = None

    # State
    _state: TimelineState = field(default_factory=TimelineState)
    _snapshot_manager: WidgetSnapshotManager = field(default_factory=WidgetSnapshotManager)

    # Checkpoint ticks (from log)
    _checkpoint_ticks: set[int] = field(default_factory=set)

    # Callbacks
    _on_seek: list[Callable[[int], None]] = field(default_factory=list)
    _on_state_change: list[Callable[[TimelineState], None]] = field(default_factory=list)

    # --- Initialization ---

    def __post_init__(self) -> None:
        """Initialize from trace and log."""
        self._sync_from_trace()
        self._sync_from_log()

    def _sync_from_trace(self) -> None:
        """Sync state from trace."""
        if self.trace:
            self._state.max_tick = len(self.trace.events)
            if self.trace.events:
                self._state.start_time = self.trace.events[0].timestamp
                self._state.end_time = self.trace.events[-1].timestamp

    def _sync_from_log(self) -> None:
        """Sync checkpoint info from log."""
        if self.log:
            checkpoints = self.log.list_checkpoints()
            self._state.checkpoint_count = len(checkpoints)

            # Extract tick numbers from checkpoint IDs (format: cp_000042)
            self._checkpoint_ticks = set()
            for cp_id in checkpoints:
                try:
                    tick = int(cp_id.split("_")[1])
                    self._checkpoint_ticks.add(tick)
                except (IndexError, ValueError):
                    pass

    # --- Signal Registration ---

    def register_signal(self, name: str, signal: "Signal[Any]") -> None:
        """Register a signal for snapshot management."""
        self._snapshot_manager.register(name, signal)

    def unregister_signal(self, name: str) -> None:
        """Unregister a signal."""
        self._snapshot_manager.unregister(name)

    def capture_snapshot(self) -> dict[str, Any]:
        """Capture current state of all registered signals."""
        return self._snapshot_manager.capture(self._state.current_tick)

    # --- Navigation ---

    async def seek(self, tick: int) -> bool:
        """
        Seek to a specific tick, restoring state.

        Process:
        1. Find nearest checkpoint before target tick
        2. Restore checkpoint state via OrchestrationLog
        3. Replay events from checkpoint to target
        4. Restore widget snapshots

        Returns True if successful.
        """
        if tick < 0 or tick > self._state.max_tick:
            return False

        # Update position
        self._state.current_tick = tick

        # Find nearest checkpoint
        nearest_checkpoint = self._find_nearest_checkpoint(tick)
        self._state.nearest_checkpoint_tick = nearest_checkpoint

        # Try to restore widget snapshots
        if not self._snapshot_manager.restore(tick):
            # Try nearest available
            nearest_snap = self._snapshot_manager.get_nearest_tick(tick)
            if nearest_snap is not None:
                self._snapshot_manager.restore(nearest_snap)

        # Notify listeners
        for callback in self._on_seek:
            callback(tick)
        self._notify_state_change()

        return True

    def step_forward(self, count: int = 1) -> int:
        """Step forward by count events. Returns new tick."""
        new_tick = min(self._state.current_tick + count, self._state.max_tick)
        self._state.current_tick = new_tick
        self._notify_state_change()
        return new_tick

    def step_backward(self, count: int = 1) -> int:
        """Step backward by count events. Returns new tick."""
        new_tick = max(self._state.current_tick - count, 0)
        self._state.current_tick = new_tick
        self._notify_state_change()
        return new_tick

    def go_to_start(self) -> int:
        """Jump to the start. Returns new tick (0)."""
        self._state.current_tick = 0
        self._notify_state_change()
        return 0

    def go_to_end(self) -> int:
        """Jump to the end. Returns new tick."""
        self._state.current_tick = self._state.max_tick
        self._notify_state_change()
        return self._state.max_tick

    def go_to_checkpoint(self, checkpoint_id: str) -> int | None:
        """Jump to a specific checkpoint. Returns tick or None if not found."""
        try:
            tick = int(checkpoint_id.split("_")[1])
            if tick in self._checkpoint_ticks:
                self._state.current_tick = tick
                self._notify_state_change()
                return tick
        except (IndexError, ValueError):
            pass
        return None

    def _find_nearest_checkpoint(self, tick: int) -> int | None:
        """Find nearest checkpoint at or before tick."""
        if not self._checkpoint_ticks:
            return None

        candidates = [t for t in self._checkpoint_ticks if t <= tick]
        return max(candidates) if candidates else None

    # --- Selection ---

    def select_event(self, event_id: str | None) -> None:
        """Select an event (for dependency highlighting)."""
        self._state.selected_event_id = event_id
        self._notify_state_change()

    def hover_event(self, event_id: str | None) -> None:
        """Hover over an event."""
        self._state.hovered_event_id = event_id
        self._notify_state_change()

    # --- Playback ---

    def play(self) -> None:
        """Start playback."""
        self._state.is_playing = True
        self._notify_state_change()

    def pause(self) -> None:
        """Pause playback."""
        self._state.is_playing = False
        self._notify_state_change()

    def toggle_play(self) -> bool:
        """Toggle playback. Returns new is_playing state."""
        self._state.is_playing = not self._state.is_playing
        self._notify_state_change()
        return self._state.is_playing

    def set_speed(self, speed: float) -> None:
        """Set playback speed (0.25 to 4.0)."""
        self._state.playback_speed = max(0.25, min(4.0, speed))
        self._notify_state_change()

    # --- Display Options ---

    def toggle_dependent_chain(self) -> bool:
        """Toggle dependency chain display. Returns new state."""
        self._state.show_dependent_chain = not self._state.show_dependent_chain
        self._notify_state_change()
        return self._state.show_dependent_chain

    def toggle_independent_highlight(self) -> bool:
        """Toggle independent event highlighting. Returns new state."""
        self._state.highlight_independent = not self._state.highlight_independent
        self._notify_state_change()
        return self._state.highlight_independent

    def toggle_phase_markers(self) -> bool:
        """Toggle phase markers display. Returns new state."""
        self._state.show_phase_markers = not self._state.show_phase_markers
        self._notify_state_change()
        return self._state.show_phase_markers

    # --- Event Retrieval ---

    def get_events_in_range(self, start_tick: int, end_tick: int) -> list[TimelineEvent]:
        """
        Get events in a tick range with rendering metadata.

        Includes dependency/independence highlighting based on selection.
        """
        if not self.trace:
            return []

        events = []
        selected_id = self._state.selected_event_id

        # Get dependency info if event is selected
        dependent_ids: set[str] = set()
        independent_ids: set[str] = set()

        if selected_id and self.trace:
            chain = self.trace.find_dependent_chain(selected_id)
            dependent_ids = {e.event_id for e in chain}

            # Independent = not in chain and can commute
            for trace_event in self.trace.events:
                if trace_event.event_id != selected_id:
                    if trace_event.event_id not in dependent_ids:
                        if self.trace.can_commute(selected_id, trace_event.event_id):
                            independent_ids.add(trace_event.event_id)

        # Build timeline events
        for tick in range(start_tick, min(end_tick, len(self.trace.events))):
            trace_event = self.trace.events[tick]
            events.append(
                TimelineEvent(
                    tick=tick,
                    event_id=trace_event.event_id,
                    phase=trace_event.phase,
                    operation=trace_event.operation,
                    participants=trace_event.participants,
                    timestamp=trace_event.timestamp,
                    success=trace_event.success,
                    message=trace_event.message,
                    is_dependent=trace_event.event_id in dependent_ids,
                    is_independent=trace_event.event_id in independent_ids,
                    is_checkpoint=tick in self._checkpoint_ticks,
                )
            )

        return events

    def get_current_event(self) -> TimelineEvent | None:
        """Get the event at the current tick."""
        events = self.get_events_in_range(self._state.current_tick, self._state.current_tick + 1)
        return events[0] if events else None

    def get_visible_events(self, window_size: int = 20) -> list[TimelineEvent]:
        """Get events around the current tick for display."""
        half = window_size // 2
        start = max(0, self._state.current_tick - half)
        end = min(self._state.max_tick, start + window_size)
        return self.get_events_in_range(start, end)

    # --- Callbacks ---

    def on_seek(self, callback: Callable[[int], None]) -> Callable[[], None]:
        """
        Register callback for seek events.

        Returns unsubscribe function.
        """
        self._on_seek.append(callback)
        return lambda: self._on_seek.remove(callback)

    def on_state_change(self, callback: Callable[[TimelineState], None]) -> Callable[[], None]:
        """
        Register callback for state changes.

        Returns unsubscribe function.
        """
        self._on_state_change.append(callback)
        return lambda: self._on_state_change.remove(callback)

    def _notify_state_change(self) -> None:
        """Notify all state change listeners."""
        for callback in self._on_state_change:
            callback(self._state)

    # --- State Access ---

    @property
    def state(self) -> TimelineState:
        """Get current timeline state."""
        return self._state

    @property
    def current_tick(self) -> int:
        """Get current tick position."""
        return self._state.current_tick

    @property
    def max_tick(self) -> int:
        """Get maximum tick."""
        return self._state.max_tick

    @property
    def is_playing(self) -> bool:
        """Whether playback is active."""
        return self._state.is_playing

    @property
    def playback_speed(self) -> float:
        """Current playback speed."""
        return self._state.playback_speed

    @property
    def progress(self) -> float:
        """Progress through timeline (0.0 to 1.0)."""
        if self._state.max_tick == 0:
            return 0.0
        return self._state.current_tick / self._state.max_tick

    # --- Rendering ---

    def render_cli(self, width: int = 60) -> str:
        """
        Render timeline as CLI string.

        Shows scrubber bar with tick markers and current position.
        """
        lines = []

        # Header
        current = self.get_current_event()
        if current:
            lines.append(f"[{current.tick:04d}] {current.phase}: {current.operation}")
            if current.participants:
                lines.append(f"        {', '.join(current.participants)}")
        else:
            lines.append(f"[{self._state.current_tick:04d}] (no event)")

        # Scrubber bar
        bar_width = width - 10
        if self._state.max_tick > 0:
            pos = int(self.progress * (bar_width - 1))
            bar = "─" * pos + "●" + "─" * (bar_width - pos - 1)
        else:
            bar = "─" * bar_width

        # Add checkpoint markers
        if self._checkpoint_ticks and self._state.max_tick > 0:
            bar_chars = list(bar)
            for tick in self._checkpoint_ticks:
                cp_pos = int((tick / self._state.max_tick) * (bar_width - 1))
                if 0 <= cp_pos < len(bar_chars) and bar_chars[cp_pos] != "●":
                    bar_chars[cp_pos] = "◆"
            bar = "".join(bar_chars)

        lines.append(f"├{bar}┤")
        lines.append(f" 0{' ' * (bar_width - 6)}{self._state.max_tick:4d}")

        # Status
        status_parts = []
        if self._state.is_playing:
            status_parts.append(f"▶ {self._state.playback_speed}x")
        else:
            status_parts.append("⏸")
        if self._state.checkpoint_count:
            status_parts.append(f"◆×{self._state.checkpoint_count}")
        lines.append(" ".join(status_parts))

        return "\n".join(lines)

    def render_json(self) -> dict[str, Any]:
        """Render timeline state as JSON for web clients."""
        current = self.get_current_event()
        return {
            "state": self._state.to_dict(),
            "current_event": current.to_dict() if current else None,
            "checkpoint_ticks": sorted(self._checkpoint_ticks),
            "progress": self.progress,
        }


# =============================================================================
# Factory Functions
# =============================================================================


def create_timeline_widget(
    trace: "TownTrace | None" = None,
    log: "OrchestrationLog | None" = None,
) -> TimelineWidget:
    """
    Create a timeline widget.

    Args:
        trace: TownTrace for event history
        log: OrchestrationLog for checkpoints

    Returns:
        Configured TimelineWidget
    """
    return TimelineWidget(trace=trace, log=log)


def create_timeline_from_events(
    events: list["TownEvent"],
) -> TimelineWidget:
    """
    Create a timeline widget from a list of events.

    Convenience function that creates a TownTrace internally.
    """
    from agents.town.trace_bridge import TownTrace

    trace = TownTrace()
    for event in events:
        trace.append(event)

    return TimelineWidget(trace=trace)


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    "TimelineState",
    "TimelineEvent",
    "TimelineWidget",
    "WidgetSnapshotManager",
    "create_timeline_widget",
    "create_timeline_from_events",
]
