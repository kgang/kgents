"""EventStream protocol base types and interfaces."""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import AsyncIterator, Iterator, Protocol, TypeVar


T = TypeVar("T", covariant=True)


class Reality(Enum):
    """J-gent reality classification for streams."""

    DETERMINISTIC = "deterministic"  # Bounded, single-step, predictable
    PROBABILISTIC = "probabilistic"  # Decomposable, multi-step, analyzable
    CHAOTIC = "chaotic"  # Unbounded, recursive, unstable


@dataclass(frozen=True)
class Event:
    """A discrete occurrence in time."""

    id: str  # Unique identifier
    timestamp: datetime  # When it occurred
    actor: str | None  # Who/what caused it
    event_type: str  # Classification (commit, edit, create, etc.)
    data: dict  # Event-specific payload
    metadata: dict = field(default_factory=dict)  # Additional context


class EventStream(Protocol[T]):
    """Protocol for temporal event sources.

    Pull-based (iterator) or push-based (async)
    Bounded (finite) or unbounded (infinite)
    Seekable (git) or append-only (live log)
    """

    def classify_reality(self) -> Reality:
        """Classify stream nature before processing."""
        ...

    def is_bounded(self) -> bool:
        """Can we determine stream will end?"""
        ...

    def estimate_size(self) -> int:
        """Approximate event count."""
        ...

    def has_cycles(self) -> bool:
        """Contains recursive/cyclic dependencies?"""
        ...

    def events(
        self,
        start: datetime | None = None,
        end: datetime | None = None,
        limit: int | None = None,
    ) -> Iterator[Event]:
        """Iterate events in temporal order."""
        ...

    async def events_async(
        self,
        start: datetime | None = None,
        end: datetime | None = None,
        limit: int | None = None,
    ) -> AsyncIterator[Event]:
        """Async variant for push-based streams."""
        ...

    def window(self, duration: timedelta) -> "SlidingWindow":
        """Create sliding window view."""
        ...

    def entropy_budget(self, depth: int = 0) -> float:
        """J-gent entropy budget: 1.0 / (depth + 1)"""
        return 1.0 / (depth + 1)


@dataclass(frozen=True)
class Window:
    """Temporal window of events."""

    start: datetime
    end: datetime
    events: tuple[Event, ...]

    @property
    def duration(self) -> timedelta:
        return self.end - self.start

    @property
    def event_count(self) -> int:
        return len(self.events)


class SlidingWindow:
    """Event stream with overlapping windows (e.g., 30-day windows, 7-day step)."""

    def __init__(
        self,
        stream: EventStream,
        window_size: timedelta,
        step_size: timedelta | None = None,
    ):
        self.stream = stream
        self.window_size = window_size
        self.step_size = step_size or window_size

    def windows(self) -> Iterator[Window]:
        """Iterate overlapping windows."""
        # Collect all events first
        all_events = list(self.stream.events())
        if not all_events:
            return

        # Sort by timestamp
        all_events.sort(key=lambda e: e.timestamp)

        # Find start and end times
        min_time = all_events[0].timestamp
        max_time = all_events[-1].timestamp

        # Generate windows
        current_start = min_time
        while current_start <= max_time:
            current_end = current_start + self.window_size

            # Collect events in this window
            window_events = tuple(
                event
                for event in all_events
                if current_start <= event.timestamp < current_end
            )

            if window_events:
                yield Window(start=current_start, end=current_end, events=window_events)

            current_start += self.step_size


@dataclass
class EntropyBudget:
    """Computational freedom budget. Diminishes with depth: 1.0→0.50→0.33→0.25"""

    depth: int
    max_depth: int = 3

    @property
    def remaining(self) -> float:
        """Remaining budget."""
        if self.depth >= self.max_depth:
            return 0.0
        return 1.0 / (self.depth + 1)

    def can_afford(self, cost: float) -> bool:
        """Can afford this computation?"""
        return self.remaining >= cost

    def descend(self) -> "EntropyBudget":
        """Create child budget (recursion)."""
        return EntropyBudget(depth=self.depth + 1, max_depth=self.max_depth)


def process_stream_with_budget(
    stream: EventStream, budget: EntropyBudget
) -> list[Event]:
    """Process stream respecting entropy budget. May truncate if exhausted."""
    reality = stream.classify_reality()

    if reality == Reality.CHAOTIC:
        return []

    if reality == Reality.DETERMINISTIC:
        return list(stream.events(limit=100))

    if not budget.can_afford(0.3):
        return []

    child_budget = budget.descend()
    events = []

    for event in stream.events(limit=1000):
        if not child_budget.can_afford(0.01):
            break
        events.append(event)

    return events
