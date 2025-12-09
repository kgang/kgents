"""TemporalWitness: W-gent for observing patterns across time windows."""

import itertools
from datetime import timedelta

from ..types import Antithesis, PatternObservation, PatternType
from .base import EventStream, Reality


class TemporalWitness:
    """
    W-gent that observes patterns across time windows.

    Compares behavior in different time periods to detect drift.
    """

    def __init__(self, stream: EventStream):
        self.stream = stream
        self.reality = stream.classify_reality()

    def observe_drift(
        self, window_size: timedelta, compare_periods: int = 2
    ) -> list[Antithesis]:
        """Detect behavioral drift across time windows."""
        if self.reality == Reality.CHAOTIC:
            return [
                Antithesis(
                    pattern="Stream is unbounded/chaotic",
                    evidence=(
                        PatternObservation(
                            pattern_type=PatternType.UPDATE_FREQUENCY,
                            value={"reality": "CHAOTIC"},
                            confidence=1.0,
                            context={"source": "reality_classification"},
                        ),
                    ),
                    frequency=1.0,
                    severity=1.0,
                )
            ]

        windowed = self.stream.window(window_size)
        windows = list(itertools.islice(windowed.windows(), compare_periods))

        if len(windows) < 2:
            return []

        antitheses = []
        recent_window = windows[-1]
        previous_window = windows[-2]

        # Calculate activity rates
        recent_days = max(recent_window.duration.days, 1)
        previous_days = max(previous_window.duration.days, 1)

        recent_rate = recent_window.event_count / recent_days
        previous_rate = previous_window.event_count / previous_days

        # Detect significant rate changes (>30%)
        if previous_rate > 0 and abs(recent_rate - previous_rate) / previous_rate > 0.3:
            antitheses.append(
                Antithesis(
                    pattern=f"Activity rate changed from {previous_rate:.1f} to {recent_rate:.1f} events/day",
                    evidence=(
                        PatternObservation(
                            pattern_type=PatternType.UPDATE_FREQUENCY,
                            value={
                                "previous_rate": previous_rate,
                                "recent_rate": recent_rate,
                                "change_pct": abs(recent_rate - previous_rate)
                                / previous_rate,
                            },
                            confidence=0.8,
                            context={
                                "period_1": f"{previous_window.event_count} events in {previous_days} days",
                                "period_2": f"{recent_window.event_count} events in {recent_days} days",
                                "window_start": str(recent_window.start),
                                "window_end": str(recent_window.end),
                            },
                        ),
                    ),
                    frequency=recent_rate,
                    severity=abs(recent_rate - previous_rate) / previous_rate,
                )
            )

        # Detect actor changes
        recent_actors = set(
            e.actor for e in recent_window.events if e.actor is not None
        )
        previous_actors = set(
            e.actor for e in previous_window.events if e.actor is not None
        )

        new_actors = recent_actors - previous_actors
        missing_actors = previous_actors - recent_actors

        if new_actors or missing_actors:
            changes = []
            if new_actors:
                changes.append(f"New actors: {', '.join(sorted(new_actors))}")
            if missing_actors:
                changes.append(f"Missing actors: {', '.join(sorted(missing_actors))}")

            antitheses.append(
                Antithesis(
                    pattern="Actor composition changed: " + "; ".join(changes),
                    evidence=(
                        PatternObservation(
                            pattern_type=PatternType.UPDATE_FREQUENCY,
                            value={
                                "previous_actors": sorted(previous_actors),
                                "recent_actors": sorted(recent_actors),
                                "new_actors": sorted(new_actors),
                                "missing_actors": sorted(missing_actors),
                            },
                            confidence=0.9,
                            context={
                                "window_start": str(recent_window.start),
                                "window_end": str(recent_window.end),
                            },
                        ),
                    ),
                    frequency=len(new_actors | missing_actors)
                    / max(len(recent_actors | previous_actors), 1),
                    severity=0.5,
                )
            )

        return antitheses

    def observe_event_type_drift(
        self, window_size: timedelta, compare_periods: int = 2
    ) -> list[Antithesis]:
        """Detect changes in event type distribution."""
        if self.reality == Reality.CHAOTIC:
            return []

        windowed = self.stream.window(window_size)
        windows = list(itertools.islice(windowed.windows(), compare_periods))

        if len(windows) < 2:
            return []

        antitheses = []
        recent_window = windows[-1]
        previous_window = windows[-2]

        # Count event types
        def count_types(window) -> dict[str, int]:
            counts: dict[str, int] = {}
            for event in window.events:
                counts[event.event_type] = counts.get(event.event_type, 0) + 1
            return counts

        recent_types = count_types(recent_window)
        previous_types = count_types(previous_window)

        # Find new and missing types
        new_types = set(recent_types.keys()) - set(previous_types.keys())
        missing_types = set(previous_types.keys()) - set(recent_types.keys())

        if new_types or missing_types:
            changes = []
            if new_types:
                changes.append(f"New event types: {', '.join(sorted(new_types))}")
            if missing_types:
                changes.append(
                    f"Missing event types: {', '.join(sorted(missing_types))}"
                )

            antitheses.append(
                Antithesis(
                    pattern="Event type distribution changed: " + "; ".join(changes),
                    evidence=(
                        PatternObservation(
                            pattern_type=PatternType.UPDATE_FREQUENCY,
                            value={
                                "previous_types": dict(previous_types),
                                "recent_types": dict(recent_types),
                                "new_types": sorted(new_types),
                                "missing_types": sorted(missing_types),
                            },
                            confidence=0.85,
                            context={
                                "window_start": str(recent_window.start),
                                "window_end": str(recent_window.end),
                            },
                        ),
                    ),
                    frequency=len(new_types | missing_types)
                    / max(
                        len(set(recent_types.keys()) | set(previous_types.keys())), 1
                    ),
                    severity=0.6,
                )
            )

        return antitheses
