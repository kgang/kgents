"""
Tests for TraceMonoid - the mathematical foundation for concurrent history.

These tests verify:
- Event addition and retrieval
- Dependency tracking
- Concurrent vs dependent event identification
- Linearization (topological sort)
- Projection to agent perspectives
"""

from __future__ import annotations

import time

import pytest

from ..dependency import DependencyGraph
from ..event import Event, KnotEvent
from ..trace_monoid import TraceMonoid, agents_independent, all_agents_independent


class TestEvent:
    """Tests for Event class."""

    def test_create_event(self) -> None:
        """Event.create() creates valid event."""
        event = Event.create(
            content={"msg": "hello"},
            source="agent_a",
        )

        assert event.content == {"msg": "hello"}
        assert event.source == "agent_a"
        assert event.id is not None
        assert event.timestamp > 0

    def test_event_is_frozen(self) -> None:
        """Events are immutable."""
        event = Event.create(content="test", source="a")

        with pytest.raises(AttributeError):
            event.content = "changed"  # type: ignore[misc]

    def test_event_is_hashable(self) -> None:
        """Events can be used in sets."""
        event = Event.create(content="test", source="a")
        event_set = {event}

        assert event in event_set

    def test_create_with_custom_id(self) -> None:
        """Event can be created with explicit ID."""
        event = Event.create(
            content="test",
            source="a",
            event_id="custom-id",
        )

        assert event.id == "custom-id"

    def test_create_with_timestamp(self) -> None:
        """Event can be created with explicit timestamp."""
        ts = 1234567890.0
        event = Event.create(
            content="test",
            source="a",
            timestamp=ts,
        )

        assert event.timestamp == ts


class TestKnotEvent:
    """Tests for KnotEvent class."""

    def test_create_knot(self) -> None:
        """KnotEvent.create_knot() creates valid knot."""
        knot = KnotEvent.create_knot(
            event_ids=frozenset({"e1", "e2", "e3"}),
        )

        assert knot.content is None
        assert knot.source == "weave"
        assert "knot-" in knot.id

    def test_knot_is_frozen(self) -> None:
        """Knots are immutable."""
        knot = KnotEvent.create_knot(frozenset({"e1"}))

        with pytest.raises(AttributeError):
            knot.source = "changed"  # type: ignore[misc]


class TestTraceMonoidBasics:
    """Basic tests for TraceMonoid."""

    def test_empty_monoid(self) -> None:
        """Empty monoid has no events."""
        monoid: TraceMonoid[str] = TraceMonoid()

        assert len(monoid) == 0
        assert list(monoid) == []

    def test_append_event(self) -> None:
        """append() adds event (immutable)."""
        monoid: TraceMonoid[str] = TraceMonoid()
        event = Event.create(content="test", source="a")

        new_monoid = monoid.append(event)

        # Original unchanged
        assert len(monoid) == 0
        # New has event
        assert len(new_monoid) == 1
        assert event.id in new_monoid

    def test_append_mut(self) -> None:
        """append_mut() adds event (mutating)."""
        monoid: TraceMonoid[str] = TraceMonoid()
        event = Event.create(content="test", source="a")

        monoid.append_mut(event)

        assert len(monoid) == 1
        assert event.id in monoid

    def test_get_event(self) -> None:
        """get_event() retrieves by ID."""
        monoid: TraceMonoid[str] = TraceMonoid()
        event = Event.create(content="test", source="a")
        monoid.append_mut(event)

        retrieved = monoid.get_event(event.id)

        assert retrieved is event

    def test_get_event_not_found(self) -> None:
        """get_event() returns None for missing ID."""
        monoid: TraceMonoid[str] = TraceMonoid()

        assert monoid.get_event("nonexistent") is None

    def test_get_events_by_source(self) -> None:
        """get_events_by_source() filters by agent."""
        monoid: TraceMonoid[str] = TraceMonoid()
        e1 = Event.create(content="1", source="a")
        e2 = Event.create(content="2", source="b")
        e3 = Event.create(content="3", source="a")

        monoid.append_mut(e1)
        monoid.append_mut(e2)
        monoid.append_mut(e3)

        a_events = monoid.get_events_by_source("a")

        assert len(a_events) == 2
        assert e1 in a_events
        assert e3 in a_events
        assert e2 not in a_events

    def test_get_latest_event(self) -> None:
        """get_latest_event() returns most recent."""
        monoid: TraceMonoid[str] = TraceMonoid()
        e1 = Event.create(content="1", source="a", timestamp=1.0)
        e2 = Event.create(content="2", source="a", timestamp=3.0)
        e3 = Event.create(content="3", source="a", timestamp=2.0)

        monoid.append_mut(e1)
        monoid.append_mut(e2)
        monoid.append_mut(e3)

        latest = monoid.get_latest_event()

        assert latest is e2

    def test_get_latest_event_by_source(self) -> None:
        """get_latest_event() filters by source."""
        monoid: TraceMonoid[str] = TraceMonoid()
        e1 = Event.create(content="1", source="a", timestamp=1.0)
        e2 = Event.create(content="2", source="b", timestamp=3.0)
        e3 = Event.create(content="3", source="a", timestamp=2.0)

        monoid.append_mut(e1)
        monoid.append_mut(e2)
        monoid.append_mut(e3)

        latest_a = monoid.get_latest_event(source="a")

        assert latest_a is e3


class TestDependencies:
    """Tests for dependency tracking."""

    def test_independent_events(self) -> None:
        """Events without dependencies are concurrent."""
        monoid: TraceMonoid[str] = TraceMonoid()
        e1 = Event.create(content="1", source="a", event_id="e1")
        e2 = Event.create(content="2", source="b", event_id="e2")

        monoid.append_mut(e1)
        monoid.append_mut(e2)

        assert monoid.are_concurrent("e1", "e2")

    def test_dependent_events(self) -> None:
        """Events with dependency are not concurrent."""
        monoid: TraceMonoid[str] = TraceMonoid()
        e1 = Event.create(content="1", source="a", event_id="e1")
        e2 = Event.create(content="2", source="b", event_id="e2")

        monoid.append_mut(e1)
        monoid.append_mut(e2, depends_on={"e1"})

        assert not monoid.are_concurrent("e1", "e2")

    def test_transitive_dependency(self) -> None:
        """Transitive dependencies are tracked."""
        monoid: TraceMonoid[str] = TraceMonoid()
        e1 = Event.create(content="1", source="a", event_id="e1")
        e2 = Event.create(content="2", source="b", event_id="e2")
        e3 = Event.create(content="3", source="c", event_id="e3")

        monoid.append_mut(e1)
        monoid.append_mut(e2, depends_on={"e1"})
        monoid.append_mut(e3, depends_on={"e2"})

        # e3 depends on e1 transitively
        assert not monoid.are_concurrent("e1", "e3")

    def test_braid_returns_graph(self) -> None:
        """braid() returns dependency graph."""
        monoid: TraceMonoid[str] = TraceMonoid()
        e1 = Event.create(content="1", source="a", event_id="e1")
        monoid.append_mut(e1)

        graph = monoid.braid()

        assert isinstance(graph, DependencyGraph)
        assert "e1" in graph


class TestKnots:
    """Tests for synchronization knots."""

    def test_knot_creation(self) -> None:
        """knot() creates synchronization point."""
        monoid: TraceMonoid[str] = TraceMonoid()
        e1 = Event.create(content="1", source="a", event_id="e1", timestamp=1.0)
        e2 = Event.create(content="2", source="b", event_id="e2", timestamp=2.0)

        monoid.append_mut(e1)
        monoid.append_mut(e2)

        knot = monoid.knot({"e1", "e2"})

        assert isinstance(knot, KnotEvent)
        assert knot.timestamp == 2.0  # Max of specified events

    def test_knot_timestamp_is_max(self) -> None:
        """Knot timestamp is max of specified events."""
        monoid: TraceMonoid[str] = TraceMonoid()
        e1 = Event.create(content="1", source="a", event_id="e1", timestamp=5.0)
        e2 = Event.create(content="2", source="b", event_id="e2", timestamp=3.0)
        e3 = Event.create(content="3", source="c", event_id="e3", timestamp=7.0)

        monoid.append_mut(e1)
        monoid.append_mut(e2)
        monoid.append_mut(e3)

        knot = monoid.knot({"e1", "e2", "e3"})

        assert knot.timestamp == 7.0


class TestLinearization:
    """Tests for topological sort."""

    def test_linearize_empty(self) -> None:
        """Linearize empty monoid returns empty list."""
        monoid: TraceMonoid[str] = TraceMonoid()

        result = monoid.linearize()

        assert result == []

    def test_linearize_single(self) -> None:
        """Linearize single event returns that event."""
        monoid: TraceMonoid[str] = TraceMonoid()
        e1 = Event.create(content="1", source="a", event_id="e1")
        monoid.append_mut(e1)

        result = monoid.linearize()

        assert len(result) == 1
        assert result[0] is e1

    def test_linearize_respects_dependencies(self) -> None:
        """Linearize puts dependencies before dependents."""
        monoid: TraceMonoid[str] = TraceMonoid()
        e1 = Event.create(content="1", source="a", event_id="e1")
        e2 = Event.create(content="2", source="b", event_id="e2")

        monoid.append_mut(e1)
        monoid.append_mut(e2, depends_on={"e1"})

        result = monoid.linearize()

        e1_idx = result.index(e1)
        e2_idx = result.index(e2)

        assert e1_idx < e2_idx

    def test_linearize_chain(self) -> None:
        """Linearize respects chain of dependencies."""
        monoid: TraceMonoid[str] = TraceMonoid()
        e1 = Event.create(content="1", source="a", event_id="e1")
        e2 = Event.create(content="2", source="b", event_id="e2")
        e3 = Event.create(content="3", source="c", event_id="e3")

        monoid.append_mut(e1)
        monoid.append_mut(e2, depends_on={"e1"})
        monoid.append_mut(e3, depends_on={"e2"})

        result = monoid.linearize()

        assert result.index(e1) < result.index(e2) < result.index(e3)


class TestProjection:
    """Tests for agent perspective projection."""

    def test_project_own_events(self) -> None:
        """Agent sees their own events."""
        monoid: TraceMonoid[str] = TraceMonoid()
        e1 = Event.create(content="1", source="a", event_id="e1")
        e2 = Event.create(content="2", source="b", event_id="e2")

        monoid.append_mut(e1)
        monoid.append_mut(e2)

        a_view = monoid.project("a")

        assert e1 in a_view
        assert e2 not in a_view

    def test_project_sees_dependencies(self) -> None:
        """Agent sees events they depend on."""
        monoid: TraceMonoid[str] = TraceMonoid()
        e1 = Event.create(content="1", source="a", event_id="e1")
        e2 = Event.create(content="2", source="b", event_id="e2")

        monoid.append_mut(e1)
        monoid.append_mut(e2, depends_on={"e1"})

        b_view = monoid.project("b")

        assert e1 in b_view  # b depends on e1
        assert e2 in b_view  # b's own event


class TestIndependenceRelations:
    """Tests for independence relation helpers."""

    def test_agents_independent(self) -> None:
        """agents_independent creates symmetric relation."""
        rel = agents_independent("a", "b")

        assert ("a", "b") in rel
        assert ("b", "a") in rel

    def test_all_agents_independent(self) -> None:
        """all_agents_independent creates full independence."""
        rel = all_agents_independent(["a", "b", "c"])

        assert ("a", "b") in rel
        assert ("b", "a") in rel
        assert ("a", "c") in rel
        assert ("c", "a") in rel
        assert ("b", "c") in rel
        assert ("c", "b") in rel


class TestFilterByTime:
    """Tests for time-based filtering."""

    def test_filter_by_start(self) -> None:
        """filter_by_time respects start."""
        monoid: TraceMonoid[str] = TraceMonoid()
        e1 = Event.create(content="1", source="a", timestamp=1.0)
        e2 = Event.create(content="2", source="a", timestamp=2.0)
        e3 = Event.create(content="3", source="a", timestamp=3.0)

        monoid.append_mut(e1)
        monoid.append_mut(e2)
        monoid.append_mut(e3)

        result = monoid.filter_by_time(start=1.5)

        assert e1 not in result
        assert e2 in result
        assert e3 in result

    def test_filter_by_end(self) -> None:
        """filter_by_time respects end."""
        monoid: TraceMonoid[str] = TraceMonoid()
        e1 = Event.create(content="1", source="a", timestamp=1.0)
        e2 = Event.create(content="2", source="a", timestamp=2.0)
        e3 = Event.create(content="3", source="a", timestamp=3.0)

        monoid.append_mut(e1)
        monoid.append_mut(e2)
        monoid.append_mut(e3)

        result = monoid.filter_by_time(end=2.5)

        assert e1 in result
        assert e2 in result
        assert e3 not in result

    def test_filter_by_range(self) -> None:
        """filter_by_time respects both bounds."""
        monoid: TraceMonoid[str] = TraceMonoid()
        e1 = Event.create(content="1", source="a", timestamp=1.0)
        e2 = Event.create(content="2", source="a", timestamp=2.0)
        e3 = Event.create(content="3", source="a", timestamp=3.0)

        monoid.append_mut(e1)
        monoid.append_mut(e2)
        monoid.append_mut(e3)

        result = monoid.filter_by_time(start=1.5, end=2.5)

        assert e1 not in result
        assert e2 in result
        assert e3 not in result
