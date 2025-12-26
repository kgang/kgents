"""
Trace: Immutable, Append-Only Sequence of Marks.

A Trace is a simpler, more generic version of Walk that just maintains
a sequence of Marks without Forest bindings or N-Phase workflow state.

Philosophy:
    "Every action leaves a mark. Every mark joins a trace."

    Traces are the fundamental unit of execution history. They are:
    - Immutable (append returns new Trace)
    - Typed (Generic[M] for different Mark types)
    - Filterable (supports predicate-based queries)
    - Composable (can merge traces)

Laws:
    - Law 1 (Immutability): Traces are frozen; append returns new Trace
    - Law 2 (Monotonicity): marks only grows, never shrinks
    - Law 3 (Homogeneity): All marks in a trace share the same type M

See: spec/protocols/witness-primitives.md
See: services/witness/mark.py (Mark pattern)
See: services/witness/walk.py (Walk pattern with N-Phase support)

Teaching:
    gotcha: Trace.add() returns a NEW Trace. Don't forget to capture:
            trace = trace.add(mark)  # ✓
            trace.add(mark)           # ✗ (discards result)
            (Evidence: test_trace.py::test_immutable_append)
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Generic, Iterator, TypeVar

from .mark import Mark

# Generic mark type
M = TypeVar("M", bound=Mark)


# =============================================================================
# Trace: Immutable Append-Only Sequence
# =============================================================================


@dataclass(frozen=True)
class Trace(Generic[M]):
    """
    Immutable, append-only sequence of marks.

    A Trace maintains execution history as a tuple of marks.
    All operations return new Traces (immutable pattern).

    Example:
        >>> trace = Trace[Mark]()
        >>> mark1 = Mark(origin="test", domain="system")
        >>> trace2 = trace.add(mark1)
        >>> len(trace2)  # 1
        >>> len(trace)   # 0 (original unchanged)

        >>> # Filter by domain
        >>> chat_marks = trace2.filter(lambda m: m.domain == "chat")

        >>> # Get latest
        >>> latest = trace2.latest
    """

    marks: tuple[M, ...] = ()

    def add(self, mark: M) -> Trace[M]:
        """
        Immutable append - returns NEW trace with mark added.

        This is the fundamental operation for building traces.
        The original trace is unchanged.

        Args:
            mark: The mark to append

        Returns:
            New Trace containing all previous marks plus the new mark
        """
        return Trace(marks=self.marks + (mark,))

    def extend(self, marks: tuple[M, ...]) -> Trace[M]:
        """
        Immutable extend - returns NEW trace with multiple marks added.

        Args:
            marks: Tuple of marks to append

        Returns:
            New Trace containing all previous marks plus the new marks
        """
        return Trace(marks=self.marks + marks)

    def filter(self, predicate: Callable[[M], bool]) -> Trace[M]:
        """
        Filter marks by predicate - returns NEW trace.

        Args:
            predicate: Function that returns True for marks to include

        Returns:
            New Trace containing only marks matching the predicate

        Example:
            >>> # Get only chat marks
            >>> chat_trace = trace.filter(lambda m: m.domain == "chat")

            >>> # Get marks from last hour
            >>> recent = trace.filter(
            ...     lambda m: (datetime.now() - m.timestamp).seconds < 3600
            ... )
        """
        return Trace(marks=tuple(m for m in self.marks if predicate(m)))

    def filter_by_domain(self, domain: str) -> Trace[M]:
        """
        Convenience filter for domain.

        Args:
            domain: Domain to filter by ("navigation", "portal", "chat", etc.)

        Returns:
            New Trace containing only marks with the specified domain
        """
        return self.filter(lambda m: m.domain == domain)

    def filter_by_origin(self, origin: str) -> Trace[M]:
        """
        Convenience filter for origin.

        Args:
            origin: Origin to filter by ("witness", "brain", "gardener", etc.)

        Returns:
            New Trace containing only marks with the specified origin
        """
        return self.filter(lambda m: m.origin == origin)

    def merge(self, other: Trace[M]) -> Trace[M]:
        """
        Merge two traces - returns NEW trace with combined marks.

        Marks are sorted by timestamp after merging to maintain temporal order.

        Args:
            other: Trace to merge with this one

        Returns:
            New Trace containing marks from both traces, sorted by timestamp
        """
        combined = self.marks + other.marks
        sorted_marks = tuple(sorted(combined, key=lambda m: m.timestamp))
        return Trace(marks=sorted_marks)

    @property
    def latest(self) -> M | None:
        """Get the most recent mark, or None if empty."""
        return self.marks[-1] if self.marks else None

    @property
    def earliest(self) -> M | None:
        """Get the earliest mark, or None if empty."""
        return self.marks[0] if self.marks else None

    def get(self, index: int) -> M | None:
        """
        Get mark at index, or None if out of bounds.

        Args:
            index: Index (0-based, supports negative indexing)

        Returns:
            Mark at index, or None if index is out of bounds
        """
        try:
            return self.marks[index]
        except IndexError:
            return None

    def slice(self, start: int | None = None, end: int | None = None) -> Trace[M]:
        """
        Slice the trace - returns NEW trace with subset of marks.

        Args:
            start: Start index (inclusive), None = beginning
            end: End index (exclusive), None = end

        Returns:
            New Trace containing marks in the specified range

        Example:
            >>> # Get last 10 marks
            >>> recent = trace.slice(-10)

            >>> # Get first 5 marks
            >>> early = trace.slice(0, 5)
        """
        return Trace(marks=self.marks[start:end])

    def __len__(self) -> int:
        """Return number of marks in the trace."""
        return len(self.marks)

    def __bool__(self) -> bool:
        """Return True if trace is non-empty."""
        return len(self.marks) > 0

    def __iter__(self) -> Iterator[M]:
        """Iterate over marks in temporal order."""
        return iter(self.marks)

    def __repr__(self) -> str:
        """Concise representation."""
        if not self.marks:
            return "Trace(empty)"
        first_domain = self.marks[0].domain if hasattr(self.marks[0], "domain") else "unknown"
        return f"Trace(marks={len(self.marks)}, first_domain={first_domain})"


# =============================================================================
# Module Exports
# =============================================================================

__all__ = [
    "Trace",
]
