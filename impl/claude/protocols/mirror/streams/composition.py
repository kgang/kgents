"""Stream composition utilities: functors and combinators."""

import heapq
from datetime import datetime, timedelta
from typing import AsyncIterator, Callable, Iterator

from .base import Event, EventStream, Reality, SlidingWindow


class ComposedStream:
    """Compose multiple streams, merged and sorted by timestamp."""

    def __init__(self, *streams: EventStream):
        self.streams = streams

    def classify_reality(self) -> Reality:
        """Composition inherits most chaotic reality."""
        realities = [s.classify_reality() for s in self.streams]
        if Reality.CHAOTIC in realities:
            return Reality.CHAOTIC
        if Reality.PROBABILISTIC in realities:
            return Reality.PROBABILISTIC
        return Reality.DETERMINISTIC

    def is_bounded(self) -> bool:
        """Bounded if all streams are bounded."""
        return all(s.is_bounded() for s in self.streams)

    def estimate_size(self) -> int:
        """Sum of all stream sizes."""
        return sum(s.estimate_size() for s in self.streams)

    def has_cycles(self) -> bool:
        """Has cycles if any stream has cycles."""
        return any(s.has_cycles() for s in self.streams)

    def events(
        self,
        start: datetime | None = None,
        end: datetime | None = None,
        limit: int | None = None,
    ) -> Iterator[Event]:
        """Merge using heap (priority queue)."""
        iterators = [s.events(start=start, end=end, limit=limit) for s in self.streams]
        count = 0
        for event in heapq.merge(*iterators, key=lambda e: e.timestamp):
            yield event
            count += 1
            if limit and count >= limit:
                break

    async def events_async(
        self,
        start: datetime | None = None,
        end: datetime | None = None,
        limit: int | None = None,
    ) -> AsyncIterator[Event]:
        """Async merge (simplified - collects all then yields)."""
        events = list(self.events(start=start, end=end, limit=limit))
        for event in events:
            yield event

    def window(self, duration: timedelta) -> SlidingWindow:
        """Create sliding window view."""
        return SlidingWindow(self, window_size=duration)


class FilteredStream:
    """Filter events by predicate."""

    def __init__(self, stream: EventStream, predicate: Callable[[Event], bool]):
        self.stream = stream
        self.predicate = predicate

    def classify_reality(self) -> Reality:
        """Inherit stream's reality."""
        return self.stream.classify_reality()

    def is_bounded(self) -> bool:
        """Inherit boundedness."""
        return self.stream.is_bounded()

    def estimate_size(self) -> int:
        """Estimate is upper bound (may be less after filtering)."""
        return self.stream.estimate_size()

    def has_cycles(self) -> bool:
        """Inherit cycle property."""
        return self.stream.has_cycles()

    def events(
        self,
        start: datetime | None = None,
        end: datetime | None = None,
        limit: int | None = None,
    ) -> Iterator[Event]:
        """Filter events."""
        count = 0
        for event in self.stream.events(start=start, end=end):
            if self.predicate(event):
                yield event
                count += 1
                if limit and count >= limit:
                    break

    async def events_async(
        self,
        start: datetime | None = None,
        end: datetime | None = None,
        limit: int | None = None,
    ) -> AsyncIterator[Event]:
        """Async filter."""
        count = 0
        async for event in self.stream.events_async(start=start, end=end):
            if self.predicate(event):
                yield event
                count += 1
                if limit and count >= limit:
                    break

    def window(self, duration: timedelta) -> SlidingWindow:
        """Create sliding window view."""
        return SlidingWindow(self, window_size=duration)


class MappedStream:
    """Transform events."""

    def __init__(self, stream: EventStream, transform: Callable[[Event], Event]):
        self.stream = stream
        self.transform = transform

    def classify_reality(self) -> Reality:
        """Inherit stream's reality."""
        return self.stream.classify_reality()

    def is_bounded(self) -> bool:
        """Inherit boundedness."""
        return self.stream.is_bounded()

    def estimate_size(self) -> int:
        """Same size as source."""
        return self.stream.estimate_size()

    def has_cycles(self) -> bool:
        """Inherit cycle property."""
        return self.stream.has_cycles()

    def events(
        self,
        start: datetime | None = None,
        end: datetime | None = None,
        limit: int | None = None,
    ) -> Iterator[Event]:
        """Transform events."""
        for event in self.stream.events(start=start, end=end, limit=limit):
            yield self.transform(event)

    async def events_async(
        self,
        start: datetime | None = None,
        end: datetime | None = None,
        limit: int | None = None,
    ) -> AsyncIterator[Event]:
        """Async transform."""
        async for event in self.stream.events_async(start=start, end=end, limit=limit):
            yield self.transform(event)

    def window(self, duration: timedelta) -> SlidingWindow:
        """Create sliding window view."""
        return SlidingWindow(self, window_size=duration)
