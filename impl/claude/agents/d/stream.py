"""
StreamAgent: Event-sourced state with temporal operations.

Provides foundation for the Temporal Witness concept from noosphere.md.
Supports event sourcing, time-travel, drift detection, and momentum tracking.
"""

from __future__ import annotations

import json
import statistics
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Callable, Generic, List, Optional, Tuple, TypeVar, cast

from .errors import (
    DriftDetectionError,
    StorageError,
)

E = TypeVar("E")  # Event type
S = TypeVar("S")  # State type


@dataclass
class WitnessReport:
    """Observation metadata for an event."""

    observer_id: str
    confidence: float  # 0.0 to 1.0
    context: dict[str, Any] = field(default_factory=dict)  # Ambient conditions
    anomaly_score: float = 0.0  # How unexpected was this event?

    def __post_init__(self) -> None:
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError(f"Confidence must be 0.0-1.0, got {self.confidence}")


@dataclass
class DriftReport:
    """Analysis of behavioral divergence."""

    trajectory: str  # What aspect was analyzed
    drift_detected: bool
    drift_start: Optional[datetime] = None
    drift_magnitude: float = 0.0  # 0.0 to 1.0
    expected_value: Any = None
    actual_value: Any = None
    explanation: str = ""


@dataclass
class EventRecord(Generic[E, S]):
    """A witnessed event with full context."""

    event: E
    state_after: S
    timestamp: datetime
    witness: WitnessReport
    sequence: int  # Monotonic sequence number


@dataclass
class Vector:
    """Semantic velocity vector."""

    direction: str  # Qualitative direction
    magnitude: float  # Speed of change
    confidence: float  # How certain we are


class StreamAgent(Generic[E, S]):
    """
    Event-sourced D-gent with temporal witness capabilities.

    Features:
    - Event sourcing with full audit trail
    - Time-travel (replay to any point)
    - Drift detection (behavioral divergence)
    - Momentum tracking (semantic velocity)
    - Entropy measurement (chaos vs stability)

    This is the foundation for the Temporal Witness in the Noosphere layer.

    Example:
        >>> def apply_event(state: int, event: dict) -> int:
        ...     if event["type"] == "increment":
        ...         return state + event["amount"]
        ...     return state
        ...
        >>> agent = StreamAgent(fold=apply_event, initial=0)
        >>> await agent.append(
        ...     {"type": "increment", "amount": 5},
        ...     WitnessReport(observer_id="test", confidence=1.0)
        ... )
        >>> state = await agent.load()
        >>> # state == 5
    """

    def __init__(
        self,
        fold: Callable[[S, E], S],
        initial: S,
        persistence_path: Optional[Path] = None,
        max_events: int = 10000,
    ) -> None:
        """
        Initialize stream agent.

        Args:
            fold: Function to apply event to state: (state, event) -> new_state
            initial: Initial state value
            persistence_path: Optional path for persistent storage
            max_events: Maximum events to retain (for bounded memory)
        """
        self.fold = fold
        self.initial = initial
        self.persistence_path = persistence_path
        self.max_events = max_events

        # In-memory event log
        self._events: List[EventRecord[E, S]] = []
        self._current_state: S = initial
        self._sequence: int = 0

        # Load from persistence if exists
        if persistence_path and Path(persistence_path).exists():
            self._load_from_disk()

    # === DataAgent Protocol ===

    async def load(self) -> S:
        """Load current state (replay all events if needed)."""
        return self._current_state

    async def save(self, state: S) -> None:
        """
        Save state as a synthetic event.

        Note: Prefer append() for proper event sourcing.
        This method exists for DataAgent protocol compatibility.
        """
        # Create synthetic "state_set" event
        event = {"__synthetic__": "state_set", "value": state}
        await self.append(
            event,  # type: ignore
            WitnessReport(
                observer_id="system",
                confidence=1.0,
                context={"synthetic": True},
            ),
        )

    async def history(self, limit: int | None = None) -> List[S]:
        """Return historical states (newest first)."""
        states = [e.state_after for e in self._events]
        states.reverse()
        return states[:limit] if limit else states

    # === Event Sourcing Operations ===

    async def append(self, event: E, witness: WitnessReport) -> S:
        """
        Append event with witness observation.

        Args:
            event: The event to record
            witness: Observation metadata

        Returns:
            New state after applying event
        """
        # Check for synthetic state_set events
        if isinstance(event, dict) and event.get("__synthetic__") == "state_set":
            new_state = cast(S, event["value"])
        else:
            # Apply fold function
            new_state = self.fold(self._current_state, event)

        # Create record
        self._sequence += 1
        record = EventRecord(
            event=event,
            state_after=new_state,
            timestamp=datetime.now(),
            witness=witness,
            sequence=self._sequence,
        )

        self._events.append(record)
        self._current_state = new_state

        # Enforce max_events
        if len(self._events) > self.max_events:
            self._events = self._events[-self.max_events :]

        if self.persistence_path:
            self._save_to_disk()

        return new_state

    async def replay(
        self,
        from_time: datetime,
        to_time: datetime,
    ) -> S:
        """
        Reconstruct state at any moment in time.

        Time-travel for debugging, analysis, or rollback.
        """
        state = self.initial

        for record in self._events:
            if record.timestamp < from_time:
                continue
            if record.timestamp > to_time:
                break

            # Check for synthetic events
            if (
                isinstance(record.event, dict)
                and record.event.get("__synthetic__") == "state_set"
            ):
                state = cast(S, record.event["value"])
            else:
                state = self.fold(state, record.event)

        return state

    async def replay_to(self, timestamp: datetime) -> S:
        """Reconstruct state at specific time."""
        return await self.replay(datetime.min, timestamp)

    async def replay_with_witnesses(
        self,
        from_time: datetime,
        to_time: datetime,
    ) -> List[Tuple[E, S, WitnessReport]]:
        """
        Replay with full observation context.

        Returns: List of (event, state_after, witness_report) tuples.
        """
        results = []
        state = self.initial

        for record in self._events:
            if record.timestamp < from_time:
                continue
            if record.timestamp > to_time:
                break

            # Check for synthetic events
            if (
                isinstance(record.event, dict)
                and record.event.get("__synthetic__") == "state_set"
            ):
                state = cast(S, record.event["value"])
            else:
                state = self.fold(state, record.event)

            results.append((record.event, state, record.witness))

        return results

    # === Temporal Witness Operations ===

    async def detect_drift(
        self,
        trajectory: str,
        extractor: Callable[[S], Any],
        window: timedelta = timedelta(days=7),
    ) -> DriftReport:
        """
        Detect when behavior diverged from expectation.

        Args:
            trajectory: Name of aspect being analyzed
            extractor: Function to extract relevant value from state
            window: Time window for baseline

        Returns:
            DriftReport with analysis
        """
        now = datetime.now()
        window_start = now - window

        # Get states in window
        states_in_window = []
        for record in self._events:
            if record.timestamp >= window_start:
                states_in_window.append((record.timestamp, record.state_after))

        if len(states_in_window) < 3:
            raise DriftDetectionError(
                f"Insufficient data for drift detection: {len(states_in_window)} states"
            )

        # Extract values
        values = [(ts, extractor(s)) for ts, s in states_in_window]

        # Simple drift detection: compare first half vs second half
        mid = len(values) // 2
        first_half = [v for _, v in values[:mid]]
        second_half = [v for _, v in values[mid:]]

        # For numeric values, compute statistical drift
        try:
            first_values = [float(v) for v in first_half if v is not None]
            second_values = [float(v) for v in second_half if v is not None]

            if first_values and second_values:
                first_mean = statistics.mean(first_values)
                second_mean = statistics.mean(second_values)
                first_std = (
                    statistics.stdev(first_values) if len(first_values) > 1 else 0.1
                )

                # Z-score for drift
                if first_std > 0:
                    z_score = abs(second_mean - first_mean) / first_std
                    drift_detected = z_score > 2.0  # 2 standard deviations
                    drift_magnitude = min(1.0, z_score / 5.0)
                else:
                    z_score = float("inf") if first_mean != second_mean else 0.0
                    drift_detected = first_mean != second_mean
                    drift_magnitude = 1.0 if drift_detected else 0.0

                # Find drift start (when values started diverging)
                drift_start = None
                if drift_detected:
                    for i, (ts, v) in enumerate(values[mid:], mid):
                        if abs(float(v) - first_mean) > 2 * first_std:
                            drift_start = ts
                            break

                return DriftReport(
                    trajectory=trajectory,
                    drift_detected=drift_detected,
                    drift_start=drift_start,
                    drift_magnitude=drift_magnitude,
                    expected_value=first_mean,
                    actual_value=second_mean,
                    explanation=f"Value shifted from {first_mean:.2f} to {second_mean:.2f} (z={z_score:.2f})",
                )
        except (TypeError, ValueError):
            pass

        # For non-numeric: simple equality check
        first_common = (
            max(set(first_half), key=first_half.count) if first_half else None
        )
        second_common = (
            max(set(second_half), key=second_half.count) if second_half else None
        )
        drift_detected = first_common != second_common

        return DriftReport(
            trajectory=trajectory,
            drift_detected=drift_detected,
            drift_start=values[mid][0] if drift_detected else None,
            drift_magnitude=1.0 if drift_detected else 0.0,
            expected_value=first_common,
            actual_value=second_common,
            explanation=f"Value changed from {first_common} to {second_common}",
        )

    async def momentum(
        self,
        extractor: Callable[[S], float],
        window: timedelta = timedelta(hours=1),
    ) -> Vector:
        """
        Compute semantic velocity: where is state heading?

        From EventStream protocol: p⃗ = m · v⃗
        where:
        - m (mass) = confidence/certainty
        - v (velocity) = rate and direction of change

        High momentum = rapid change with high confidence
        Low momentum = stable or uncertain
        """
        now = datetime.now()
        window_start = now - window

        # Get recent events with values
        recent = []
        for record in self._events:
            if record.timestamp >= window_start:
                try:
                    value = extractor(record.state_after)
                    recent.append((record.timestamp, value, record.witness.confidence))
                except Exception:
                    continue

        if len(recent) < 2:
            return Vector(direction="stable", magnitude=0.0, confidence=0.0)

        # Compute velocity (rate of change)
        first_ts, first_val, _ = recent[0]
        last_ts, last_val, _ = recent[-1]

        time_delta = (last_ts - first_ts).total_seconds()
        if time_delta == 0:
            return Vector(direction="stable", magnitude=0.0, confidence=1.0)

        velocity = (last_val - first_val) / time_delta

        # Mass = average confidence
        avg_confidence = statistics.mean([c for _, _, c in recent])

        # Momentum = mass * velocity
        momentum_magnitude = abs(velocity * avg_confidence)

        # Direction
        if velocity > 0.001:
            direction = "increasing"
        elif velocity < -0.001:
            direction = "decreasing"
        else:
            direction = "stable"

        return Vector(
            direction=direction,
            magnitude=momentum_magnitude,
            confidence=avg_confidence,
        )

    async def entropy(self, window: timedelta = timedelta(hours=1)) -> float:
        """
        Rate of state change (chaos vs stability).

        High entropy (> 0.7): Rapid change, system in flux
        - Be careful with interventions
        - Wait for stability before acting

        Low entropy (< 0.3): Stable, predictable
        - Safe for reflection
        - Interventions have clearer impact

        Returns: Entropy value 0.0 to 1.0
        """
        now = datetime.now()
        window_start = now - window

        # Count events in window
        events_in_window = [r for r in self._events if r.timestamp >= window_start]

        if len(events_in_window) == 0:
            return 0.0  # No change = zero entropy

        # Compute event rate (events per second)
        window_seconds = window.total_seconds()
        event_rate = len(events_in_window) / window_seconds

        # Also consider anomaly scores
        avg_anomaly = statistics.mean(
            [e.witness.anomaly_score for e in events_in_window]
        )

        # Entropy = f(event_rate, anomaly)
        # Normalize event rate (assume 1 event/second = high entropy)
        normalized_rate = min(1.0, event_rate)

        # Combine with anomaly
        entropy = 0.6 * normalized_rate + 0.4 * avg_anomaly

        return min(1.0, entropy)

    async def event_history(
        self,
        limit: Optional[int] = None,
        filter_by: Optional[Callable[[E], bool]] = None,
    ) -> List[Tuple[datetime, E, S]]:
        """
        Query event history.

        Returns: List of (timestamp, event, state_after) tuples.
        """
        results = []
        for record in self._events:
            if filter_by is not None and not filter_by(record.event):
                continue
            results.append((record.timestamp, record.event, record.state_after))

        results.reverse()
        return results[:limit] if limit else results

    async def events_since(self, timestamp: datetime) -> List[EventRecord[E, S]]:
        """Get all events since timestamp."""
        return [r for r in self._events if r.timestamp >= timestamp]

    async def event_count(self) -> int:
        """Get total event count."""
        return len(self._events)

    # === Internal Methods ===

    def _save_to_disk(self) -> None:
        """Save events to disk."""
        if self.persistence_path is None:
            return

        path = Path(self.persistence_path)
        path.parent.mkdir(parents=True, exist_ok=True)

        data = {
            "initial": self.initial,
            "sequence": self._sequence,
            "events": [
                {
                    "event": record.event,
                    "state_after": record.state_after,
                    "timestamp": record.timestamp.isoformat(),
                    "witness": {
                        "observer_id": record.witness.observer_id,
                        "confidence": record.witness.confidence,
                        "context": record.witness.context,
                        "anomaly_score": record.witness.anomaly_score,
                    },
                    "sequence": record.sequence,
                }
                for record in self._events
            ],
        }

        # Atomic write
        temp_path = path.with_suffix(".tmp")
        with open(temp_path, "w") as f:
            json.dump(data, f, indent=2, default=str)
        temp_path.replace(path)

    def _load_from_disk(self) -> None:
        """Load events from disk and replay."""
        if self.persistence_path is None:
            return

        path = Path(self.persistence_path)
        if not path.exists():
            return

        try:
            with open(path) as f:
                data = json.load(f)

            self.initial = data["initial"]
            self._sequence = data.get("sequence", 0)
            self._current_state = self.initial

            for event_data in data["events"]:
                witness = WitnessReport(
                    observer_id=event_data["witness"]["observer_id"],
                    confidence=event_data["witness"]["confidence"],
                    context=event_data["witness"].get("context", {}),
                    anomaly_score=event_data["witness"].get("anomaly_score", 0.0),
                )

                record = EventRecord(
                    event=event_data["event"],
                    state_after=event_data["state_after"],
                    timestamp=datetime.fromisoformat(event_data["timestamp"]),
                    witness=witness,
                    sequence=event_data.get("sequence", 0),
                )

                self._events.append(record)
                self._current_state = record.state_after

        except Exception as e:
            raise StorageError(f"Failed to load stream: {e}")
