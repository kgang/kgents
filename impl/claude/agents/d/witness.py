"""
TemporalWitness: Memory as witnessed time, not stored snapshots.

The Temporal Witness extends StreamAgent with enhanced observation:
- Not just "what" but "how confidently"
- Not just "when" but "in what context"
- Not just "change" but "drift from expectation"

Philosophy: "Memory is not what happened—it is what was witnessed."

Part of the Noosphere Layer (D-gent Phase 4).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Callable, Generic, List, Optional, Tuple, TypeVar

from .errors import (
    DriftDetectionError,
    TemporalError,
)
from .stream import DriftReport, EventRecord, StreamAgent, Vector, WitnessReport

E = TypeVar("E")  # Event type
S = TypeVar("S")  # State type


class DriftSeverity(Enum):
    """Severity classification for behavioral drift."""

    NONE = "none"  # No drift detected
    MINOR = "minor"  # < 0.3: Small deviation, likely noise
    MODERATE = "moderate"  # 0.3-0.6: Notable change, worth monitoring
    SIGNIFICANT = "significant"  # 0.6-0.8: Substantial shift, investigate
    CRITICAL = "critical"  # > 0.8: Major divergence, immediate attention


class EntropyLevel(Enum):
    """Entropy classification for system stability."""

    CALM = "calm"  # < 0.2: Very stable, safe for reflection
    STABLE = "stable"  # 0.2-0.4: Normal operation
    ACTIVE = "active"  # 0.4-0.6: Moderate activity
    TURBULENT = "turbulent"  # 0.6-0.8: High activity, careful with interventions
    CHAOTIC = "chaotic"  # > 0.8: System in flux, wait for stability


@dataclass
class Trajectory(Generic[S]):
    """
    A tracked aspect of state evolution.

    Trajectories allow monitoring specific aspects over time:
    - "tone": How the system's communication style evolves
    - "decisions": Pattern of choices made
    - "preferences": User/system preferences
    """

    name: str
    extractor: Callable[[S], Any]
    description: str = ""
    current_value: Any = None
    baseline_value: Any = None
    last_drift_check: Optional[datetime] = None
    drift_history: List[DriftReport] = field(default_factory=list)


@dataclass
class WitnessContext:
    """
    Rich context for a witnessed event.

    Beyond WitnessReport, captures:
    - Preceding events for causality analysis
    - Entropy at time of observation
    - Trajectory impacts
    """

    witness: WitnessReport
    preceding_events: int  # How many events in recent window
    entropy_at_time: float
    affected_trajectories: List[str]


@dataclass
class TemporalSnapshot:
    """A point-in-time snapshot of state with full context."""

    timestamp: datetime
    state: Any
    entropy: float
    momentum: Vector
    active_drifts: List[str]  # Names of trajectories currently drifting


@dataclass
class TimelineEntry:
    """Entry in a state timeline."""

    timestamp: datetime
    state: Any
    event: Any
    witness: WitnessReport
    curvature: float  # Rate of change at this point


class TemporalWitness(Generic[E, S]):
    """
    Memory as witnessed time with enhanced observation.

    The Temporal Witness extends StreamAgent with:
    - Trajectory tracking: Monitor specific aspects of state
    - Drift detection: Detect when behavior diverges from baseline
    - Momentum analysis: Understand where state is heading
    - Entropy monitoring: Assess system stability
    - Time-travel: Reconstruct state at any point

    Philosophy: "Memory is not what happened—it is what was witnessed."

    Example:
        >>> def apply_event(state, event):
        ...     return {**state, **event}
        ...
        >>> witness = TemporalWitness(fold=apply_event, initial={"mood": "neutral"})
        >>>
        >>> # Add trajectory for mood
        >>> witness.add_trajectory("mood", lambda s: s.get("mood"), "User's emotional state")
        >>>
        >>> # Record events
        >>> await witness.observe(
        ...     {"mood": "happy"},
        ...     WitnessReport(observer_id="user", confidence=0.9)
        ... )
        >>>
        >>> # Check for drift
        >>> drift = await witness.check_drift("mood")
        >>> print(f"Drift detected: {drift.drift_detected}")
        >>>
        >>> # Get momentum
        >>> momentum = await witness.momentum_for("mood")
        >>> print(f"Mood trending: {momentum.direction}")
    """

    def __init__(
        self,
        fold: Callable[[S, E], S],
        initial: S,
        persistence_path: Optional[str] = None,
        max_events: int = 10000,
        drift_window: timedelta = timedelta(days=7),
        entropy_window: timedelta = timedelta(hours=1),
    ) -> None:
        """
        Initialize temporal witness.

        Args:
            fold: Function to apply event to state: (state, event) -> new_state
            initial: Initial state value
            persistence_path: Optional path for persistent storage
            max_events: Maximum events to retain
            drift_window: Default window for drift detection
            entropy_window: Default window for entropy calculation
        """
        from pathlib import Path

        self._stream = StreamAgent(
            fold=fold,
            initial=initial,
            persistence_path=Path(persistence_path) if persistence_path else None,
            max_events=max_events,
        )

        self.drift_window = drift_window
        self.entropy_window = entropy_window

        # Trajectory tracking
        self._trajectories: dict[str, Trajectory[S]] = {}

        # Caches
        self._entropy_cache: Optional[Tuple[datetime, float]] = None
        self._momentum_cache: dict[str, Tuple[datetime, Vector]] = {}

    @property
    def initial(self) -> S:
        """Initial state value."""
        return self._stream.initial

    # === Core Operations ===

    async def observe(
        self,
        event: E,
        witness: WitnessReport,
        context: Optional[dict[str, Any]] = None,
    ) -> S:
        """
        Observe and record an event with witness metadata.

        This is the primary way to record state changes.
        Returns the new state after applying the event.
        """
        # Enrich witness context if provided
        if context:
            witness = WitnessReport(
                observer_id=witness.observer_id,
                confidence=witness.confidence,
                context={**witness.context, **context},
                anomaly_score=witness.anomaly_score,
            )

        # Record via underlying stream
        new_state = await self._stream.append(event, witness)

        # Update trajectory values
        for name, trajectory in self._trajectories.items():
            try:
                trajectory.current_value = trajectory.extractor(new_state)
            except Exception:
                pass

        # Invalidate caches
        self._entropy_cache = None
        self._momentum_cache.clear()

        return new_state

    async def load(self) -> S:
        """Load current state."""
        return await self._stream.load()

    async def history(self, limit: Optional[int] = None) -> List[S]:
        """Return historical states (newest first)."""
        return await self._stream.history(limit)

    # === Trajectory Management ===

    def add_trajectory(
        self,
        name: str,
        extractor: Callable[[S], Any],
        description: str = "",
    ) -> None:
        """
        Add a trajectory to track.

        A trajectory monitors a specific aspect of state over time.
        The extractor function extracts the relevant value from state.
        """
        self._trajectories[name] = Trajectory(
            name=name,
            extractor=extractor,
            description=description,
        )

    def remove_trajectory(self, name: str) -> bool:
        """Remove a trajectory. Returns True if it existed."""
        return self._trajectories.pop(name, None) is not None

    def list_trajectories(self) -> List[str]:
        """List all tracked trajectory names."""
        return list(self._trajectories.keys())

    def get_trajectory(self, name: str) -> Optional[Trajectory[S]]:
        """Get trajectory by name."""
        return self._trajectories.get(name)

    # === Drift Detection ===

    async def check_drift(
        self,
        trajectory_name: str,
        window: Optional[timedelta] = None,
    ) -> DriftReport:
        """
        Check for behavioral drift in a trajectory.

        Compares recent behavior to baseline, detecting when
        the trajectory has diverged from expectations.
        """
        trajectory = self._trajectories.get(trajectory_name)
        if trajectory is None:
            raise TemporalError(f"Unknown trajectory: {trajectory_name}")

        window = window or self.drift_window

        try:
            drift = await self._stream.detect_drift(
                trajectory=trajectory_name,
                extractor=trajectory.extractor,
                window=window,
            )

            # Update trajectory
            trajectory.last_drift_check = datetime.now()
            trajectory.drift_history.append(drift)

            return drift
        except DriftDetectionError:
            # Not enough data
            return DriftReport(
                trajectory=trajectory_name,
                drift_detected=False,
                explanation="Insufficient data for drift detection",
            )

    async def check_all_drifts(
        self,
        window: Optional[timedelta] = None,
    ) -> dict[str, DriftReport]:
        """Check drift for all tracked trajectories."""
        results = {}
        for name in self._trajectories:
            results[name] = await self.check_drift(name, window)
        return results

    def classify_drift(self, drift: DriftReport) -> DriftSeverity:
        """Classify drift severity."""
        if not drift.drift_detected:
            return DriftSeverity.NONE
        mag = drift.drift_magnitude
        if mag < 0.3:
            return DriftSeverity.MINOR
        elif mag < 0.6:
            return DriftSeverity.MODERATE
        elif mag < 0.8:
            return DriftSeverity.SIGNIFICANT
        else:
            return DriftSeverity.CRITICAL

    # === Momentum Analysis ===

    async def momentum_for(
        self,
        trajectory_name: str,
        window: Optional[timedelta] = None,
    ) -> Vector:
        """
        Get momentum (semantic velocity) for a trajectory.

        Momentum = mass × velocity where:
        - mass = confidence/certainty of observations
        - velocity = rate and direction of change

        High momentum = rapid, confident change
        Low momentum = stable or uncertain
        """
        trajectory = self._trajectories.get(trajectory_name)
        if trajectory is None:
            raise TemporalError(f"Unknown trajectory: {trajectory_name}")

        window = window or self.entropy_window

        # Check cache
        cache_key = trajectory_name
        if cache_key in self._momentum_cache:
            cached_time, cached_value = self._momentum_cache[cache_key]
            if datetime.now() - cached_time < timedelta(seconds=30):
                return cached_value

        try:
            momentum = await self._stream.momentum(
                extractor=lambda s: float(trajectory.extractor(s)),
                window=window,
            )
            self._momentum_cache[cache_key] = (datetime.now(), momentum)
            return momentum
        except (TypeError, ValueError):
            # Non-numeric trajectory
            return Vector(direction="unknown", magnitude=0.0, confidence=0.0)

    async def overall_momentum(
        self,
        window: Optional[timedelta] = None,
    ) -> dict[str, Vector]:
        """Get momentum for all trajectories."""
        results = {}
        for name in self._trajectories:
            results[name] = await self.momentum_for(name, window)
        return results

    # === Entropy Analysis ===

    async def entropy(self, window: Optional[timedelta] = None) -> float:
        """
        Get system entropy (rate of change).

        High entropy (> 0.7): System in flux, careful with interventions
        Low entropy (< 0.3): Stable, safe for reflection
        """
        window = window or self.entropy_window

        # Check cache
        if self._entropy_cache:
            cached_time, cached_value = self._entropy_cache
            if datetime.now() - cached_time < timedelta(seconds=30):
                return cached_value

        entropy = await self._stream.entropy(window)
        self._entropy_cache = (datetime.now(), entropy)
        return entropy

    def classify_entropy(self, entropy: float) -> EntropyLevel:
        """Classify entropy level."""
        if entropy < 0.2:
            return EntropyLevel.CALM
        elif entropy < 0.4:
            return EntropyLevel.STABLE
        elif entropy < 0.6:
            return EntropyLevel.ACTIVE
        elif entropy < 0.8:
            return EntropyLevel.TURBULENT
        else:
            return EntropyLevel.CHAOTIC

    # === Time Travel ===

    async def replay(
        self,
        from_time: datetime,
        to_time: datetime,
    ) -> S:
        """Reconstruct state at any moment in time."""
        return await self._stream.replay(from_time, to_time)

    async def replay_to(self, timestamp: datetime) -> S:
        """Reconstruct state at specific time."""
        return await self._stream.replay_to(timestamp)

    async def snapshot_at(self, timestamp: datetime) -> TemporalSnapshot:
        """Get full snapshot at a point in time."""
        state = await self.replay_to(timestamp)
        entropy = await self.entropy()  # Current entropy as approximation
        momentum = Vector(direction="unknown", magnitude=0.0, confidence=0.0)

        # Check for active drifts
        active_drifts = []
        for name, trajectory in self._trajectories.items():
            for drift in trajectory.drift_history:
                if drift.drift_detected and drift.drift_start:
                    if drift.drift_start <= timestamp:
                        active_drifts.append(name)

        return TemporalSnapshot(
            timestamp=timestamp,
            state=state,
            entropy=entropy,
            momentum=momentum,
            active_drifts=active_drifts,
        )

    async def timeline(
        self,
        window: timedelta,
        max_entries: int = 100,
    ) -> List[TimelineEntry]:
        """
        Get state timeline for a time window.

        Returns list of (timestamp, state, event, witness) entries
        with curvature (rate of change) at each point.
        """
        now = datetime.now()
        from_time = now - window

        records = await self._stream.replay_with_witnesses(from_time, now)

        entries = []
        prev_state = None

        for event, state, witness in records[-max_entries:]:
            # Estimate curvature from state change
            if prev_state is not None and hasattr(state, "__eq__"):
                curvature = 0.5 if state != prev_state else 0.0
            else:
                curvature = 0.3  # Default moderate curvature

            entries.append(
                TimelineEntry(
                    timestamp=datetime.now(),  # Approximate
                    state=state,
                    event=event,
                    witness=witness,
                    curvature=curvature,
                )
            )
            prev_state = state

        return entries

    # === Event History ===

    async def events_since(self, timestamp: datetime) -> List[EventRecord[E, S]]:
        """Get all events since timestamp."""
        return await self._stream.events_since(timestamp)

    async def event_count(self) -> int:
        """Get total event count."""
        return await self._stream.event_count()

    async def recent_witnesses(
        self,
        limit: int = 10,
    ) -> List[Tuple[E, WitnessReport]]:
        """Get recent events with their witness reports."""
        history = await self._stream.event_history(limit=limit)
        return [
            (
                e,
                WitnessReport(
                    observer_id="unknown",
                    confidence=1.0,
                ),
            )
            for _, e, _ in history
        ]

    # === Context Analysis ===

    async def witness_context(self, event: E) -> WitnessContext:
        """
        Get rich context for a witnessed event.

        Includes entropy, preceding events, and affected trajectories.
        """
        now = datetime.now()
        entropy = await self.entropy()

        # Count recent events
        recent_events = await self._stream.events_since(now - self.entropy_window)
        preceding = len(recent_events)

        # Determine affected trajectories
        affected = []
        current_state = await self.load()
        for name, trajectory in self._trajectories.items():
            try:
                trajectory.extractor(current_state)
                affected.append(name)
            except Exception:
                pass

        return WitnessContext(
            witness=WitnessReport(observer_id="system", confidence=1.0),
            preceding_events=preceding,
            entropy_at_time=entropy,
            affected_trajectories=affected,
        )

    # === Utility ===

    async def is_stable(self, threshold: float = 0.3) -> bool:
        """Check if system is currently stable."""
        entropy = await self.entropy()
        return entropy < threshold

    async def wait_for_stability(
        self,
        threshold: float = 0.3,
        timeout: timedelta = timedelta(minutes=5),
        check_interval: timedelta = timedelta(seconds=10),
    ) -> bool:
        """
        Wait for system to stabilize.

        Returns True if stability achieved, False if timeout.
        """
        import asyncio

        start = datetime.now()
        while datetime.now() - start < timeout:
            if await self.is_stable(threshold):
                return True
            await asyncio.sleep(check_interval.total_seconds())
        return False
