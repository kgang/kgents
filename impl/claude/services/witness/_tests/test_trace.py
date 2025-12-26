"""
Tests for Trace: Immutable Append-Only Mark Sequence.

Verifies:
- Trace immutability (add returns new Trace)
- Filtering by domain, origin, predicate
- Merging traces
- Slicing and indexing
"""

from datetime import datetime, timedelta, timezone

import pytest

from services.witness import (
    Mark,
    Response,
    Stimulus,
    Trace,
)


@pytest.fixture
def sample_marks() -> tuple[Mark, Mark, Mark, Mark]:
    """Create sample marks across different domains."""
    now = datetime.now(timezone.utc)

    nav_mark = Mark(
        origin="navigator",
        domain="navigation",
        stimulus=Stimulus(kind="route", content="Navigate to /chat"),
        response=Response(kind="navigation", content="Navigated"),
        timestamp=now,
    )

    portal_mark = Mark(
        origin="context_perception",
        domain="portal",
        stimulus=Stimulus(kind="portal", content="Expand imports"),
        response=Response(kind="exploration", content="Expanded"),
        timestamp=now + timedelta(seconds=1),
    )

    chat_mark = Mark(
        origin="chat_session",
        domain="chat",
        stimulus=Stimulus(kind="prompt", content="Hello"),
        response=Response(kind="text", content="Hi!"),
        timestamp=now + timedelta(seconds=2),
    )

    edit_mark = Mark(
        origin="editor",
        domain="edit",
        stimulus=Stimulus(kind="kblock", content="Edit block"),
        response=Response(kind="mutation", content="Updated"),
        timestamp=now + timedelta(seconds=3),
    )

    return nav_mark, portal_mark, chat_mark, edit_mark


class TestTraceImmutability:
    """Tests for Trace immutability."""

    def test_empty_trace(self) -> None:
        """Can create empty trace."""
        trace = Trace[Mark]()
        assert len(trace) == 0
        assert not trace  # Empty trace is falsy
        assert trace.latest is None

    def test_add_returns_new_trace(self, sample_marks: tuple[Mark, ...]) -> None:
        """add() returns new trace, original unchanged."""
        trace1 = Trace[Mark]()
        mark = sample_marks[0]

        trace2 = trace1.add(mark)

        assert len(trace1) == 0  # Original unchanged
        assert len(trace2) == 1  # New trace has mark
        assert trace2.latest == mark

    def test_multiple_adds(self, sample_marks: tuple[Mark, ...]) -> None:
        """Can chain multiple adds."""
        trace = Trace[Mark]()

        for mark in sample_marks:
            trace = trace.add(mark)

        assert len(trace) == len(sample_marks)
        assert trace.latest == sample_marks[-1]
        assert trace.earliest == sample_marks[0]

    def test_extend_multiple_marks(self, sample_marks: tuple[Mark, ...]) -> None:
        """extend() adds multiple marks at once."""
        trace1 = Trace[Mark]()
        trace2 = trace1.extend(sample_marks)

        assert len(trace1) == 0  # Original unchanged
        assert len(trace2) == len(sample_marks)


class TestTraceFiltering:
    """Tests for Trace filtering operations."""

    def test_filter_by_domain(self, sample_marks: tuple[Mark, ...]) -> None:
        """filter_by_domain() returns only marks with specified domain."""
        trace = Trace[Mark]().extend(sample_marks)

        chat_trace = trace.filter_by_domain("chat")
        assert len(chat_trace) == 1
        assert chat_trace.latest.domain == "chat"

    def test_filter_by_origin(self, sample_marks: tuple[Mark, ...]) -> None:
        """filter_by_origin() returns only marks with specified origin."""
        trace = Trace[Mark]().extend(sample_marks)

        navigator_trace = trace.filter_by_origin("navigator")
        assert len(navigator_trace) == 1
        assert navigator_trace.latest.origin == "navigator"

    def test_filter_by_predicate(self, sample_marks: tuple[Mark, ...]) -> None:
        """filter() accepts arbitrary predicate."""
        trace = Trace[Mark]().extend(sample_marks)

        # Filter for marks where domain starts with "c"
        filtered = trace.filter(lambda m: m.domain.startswith("c"))
        # Only "chat" starts with "c"
        assert len(filtered) == 1
        assert filtered.latest.domain == "chat"

    def test_filter_returns_new_trace(self, sample_marks: tuple[Mark, ...]) -> None:
        """filter() returns new trace, original unchanged."""
        trace = Trace[Mark]().extend(sample_marks)
        filtered = trace.filter_by_domain("chat")

        assert len(trace) == len(sample_marks)  # Original unchanged
        assert len(filtered) == 1  # Filtered has subset

    def test_filter_empty_result(self, sample_marks: tuple[Mark, ...]) -> None:
        """filter() with no matches returns empty trace."""
        trace = Trace[Mark]().extend(sample_marks)
        filtered = trace.filter_by_domain("nonexistent")

        assert len(filtered) == 0
        assert not filtered  # Empty trace is falsy


class TestTraceMerging:
    """Tests for merging traces."""

    def test_merge_two_traces(self, sample_marks: tuple[Mark, ...]) -> None:
        """merge() combines marks from two traces."""
        nav, portal, chat, edit = sample_marks

        trace1 = Trace[Mark]().add(nav).add(portal)
        trace2 = Trace[Mark]().add(chat).add(edit)

        merged = trace1.merge(trace2)

        assert len(merged) == 4
        assert len(trace1) == 2  # Originals unchanged
        assert len(trace2) == 2

    def test_merge_preserves_temporal_order(self, sample_marks: tuple[Mark, ...]) -> None:
        """merge() sorts by timestamp."""
        nav, portal, chat, edit = sample_marks

        # Add in reverse order to each trace
        trace1 = Trace[Mark]().add(edit).add(portal)
        trace2 = Trace[Mark]().add(chat).add(nav)

        merged = trace1.merge(trace2)

        # Should be sorted: nav < portal < chat < edit
        assert merged.marks[0] == nav
        assert merged.marks[1] == portal
        assert merged.marks[2] == chat
        assert merged.marks[3] == edit

    def test_merge_empty_traces(self) -> None:
        """merge() with empty traces works."""
        trace1 = Trace[Mark]()
        trace2 = Trace[Mark]()

        merged = trace1.merge(trace2)
        assert len(merged) == 0


class TestTraceSlicing:
    """Tests for slicing and indexing."""

    def test_get_by_index(self, sample_marks: tuple[Mark, ...]) -> None:
        """get() retrieves mark by index."""
        trace = Trace[Mark]().extend(sample_marks)

        assert trace.get(0) == sample_marks[0]
        assert trace.get(1) == sample_marks[1]
        assert trace.get(-1) == sample_marks[-1]  # Negative indexing

    def test_get_out_of_bounds(self, sample_marks: tuple[Mark, ...]) -> None:
        """get() returns None for out of bounds."""
        trace = Trace[Mark]().extend(sample_marks)

        assert trace.get(100) is None
        assert trace.get(-100) is None

    def test_slice_range(self, sample_marks: tuple[Mark, ...]) -> None:
        """slice() returns subset of marks."""
        trace = Trace[Mark]().extend(sample_marks)

        first_two = trace.slice(0, 2)
        assert len(first_two) == 2
        assert first_two.marks[0] == sample_marks[0]
        assert first_two.marks[1] == sample_marks[1]

    def test_slice_last_n(self, sample_marks: tuple[Mark, ...]) -> None:
        """slice() with negative index gets last N."""
        trace = Trace[Mark]().extend(sample_marks)

        last_two = trace.slice(-2)
        assert len(last_two) == 2
        assert last_two.marks[0] == sample_marks[-2]
        assert last_two.marks[1] == sample_marks[-1]

    def test_slice_returns_new_trace(self, sample_marks: tuple[Mark, ...]) -> None:
        """slice() returns new trace, original unchanged."""
        trace = Trace[Mark]().extend(sample_marks)
        sliced = trace.slice(0, 2)

        assert len(trace) == len(sample_marks)  # Original unchanged
        assert len(sliced) == 2


class TestTraceIteration:
    """Tests for iterating over traces."""

    def test_iteration(self, sample_marks: tuple[Mark, ...]) -> None:
        """Can iterate over marks in trace."""
        trace = Trace[Mark]().extend(sample_marks)

        collected = [m for m in trace]
        assert collected == list(sample_marks)

    def test_enumerate(self, sample_marks: tuple[Mark, ...]) -> None:
        """Can enumerate marks in trace."""
        trace = Trace[Mark]().extend(sample_marks)

        for i, mark in enumerate(trace):
            assert mark == sample_marks[i]


class TestTraceProperties:
    """Tests for trace properties."""

    def test_latest_mark(self, sample_marks: tuple[Mark, ...]) -> None:
        """latest returns most recent mark."""
        trace = Trace[Mark]().extend(sample_marks)
        assert trace.latest == sample_marks[-1]

    def test_earliest_mark(self, sample_marks: tuple[Mark, ...]) -> None:
        """earliest returns oldest mark."""
        trace = Trace[Mark]().extend(sample_marks)
        assert trace.earliest == sample_marks[0]

    def test_len(self, sample_marks: tuple[Mark, ...]) -> None:
        """len() returns number of marks."""
        trace = Trace[Mark]().extend(sample_marks)
        assert len(trace) == len(sample_marks)

    def test_bool_empty(self) -> None:
        """Empty trace is falsy."""
        trace = Trace[Mark]()
        assert not trace

    def test_bool_non_empty(self, sample_marks: tuple[Mark, ...]) -> None:
        """Non-empty trace is truthy."""
        trace = Trace[Mark]().add(sample_marks[0])
        assert trace

    def test_repr(self, sample_marks: tuple[Mark, ...]) -> None:
        """repr() shows useful info."""
        empty = Trace[Mark]()
        assert "empty" in repr(empty)

        trace = Trace[Mark]().add(sample_marks[0])
        r = repr(trace)
        assert "marks=1" in r
        assert "navigation" in r  # First domain


# =============================================================================
# Integration Tests
# =============================================================================


class TestTraceIntegration:
    """Integration tests for Trace."""

    def test_build_trace_incrementally(self, sample_marks: tuple[Mark, ...]) -> None:
        """Can build trace step by step."""
        trace = Trace[Mark]()

        for mark in sample_marks:
            trace = trace.add(mark)

        assert len(trace) == len(sample_marks)
        assert trace.earliest == sample_marks[0]
        assert trace.latest == sample_marks[-1]

    def test_filter_chain(self, sample_marks: tuple[Mark, ...]) -> None:
        """Can chain multiple filters."""
        trace = Trace[Mark]().extend(sample_marks)

        # Filter for portal OR chat
        filtered = trace.filter(lambda m: m.domain in ("portal", "chat"))
        assert len(filtered) == 2

    def test_complex_query(self, sample_marks: tuple[Mark, ...]) -> None:
        """Can perform complex queries."""
        nav, portal, chat, edit = sample_marks
        trace = Trace[Mark]().extend(sample_marks)

        # Get marks from last 2 seconds
        cutoff = chat.timestamp
        recent = trace.filter(lambda m: m.timestamp >= cutoff)

        assert len(recent) == 2  # chat and edit
        assert chat in recent.marks
        assert edit in recent.marks

    def test_merge_and_filter(self, sample_marks: tuple[Mark, ...]) -> None:
        """Can merge traces then filter."""
        nav, portal, chat, edit = sample_marks

        trace1 = Trace[Mark]().add(nav).add(chat)
        trace2 = Trace[Mark]().add(portal).add(edit)

        merged = trace1.merge(trace2)
        chat_only = merged.filter_by_domain("chat")

        assert len(chat_only) == 1
        assert chat_only.latest == chat
