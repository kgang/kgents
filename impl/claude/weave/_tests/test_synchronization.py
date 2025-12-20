"""
Tests for synchronization in the Weave.

These tests verify:
- Knot creation (synchronization points)
- TheWeave high-level API
- Multi-agent synchronization scenarios
"""

from __future__ import annotations

import pytest

from ..event import Event, KnotEvent
from ..trace_monoid import TraceMonoid
from ..weave import TheWeave


class TestTheWeaveBasics:
    """Basic tests for TheWeave API."""

    @pytest.mark.asyncio
    async def test_record_event(self) -> None:
        """record() adds event to weave."""
        weave = TheWeave()

        event_id = await weave.record(
            content={"msg": "hello"},
            source="agent_a",
        )

        assert event_id in weave
        assert len(weave) == 1

    @pytest.mark.asyncio
    async def test_record_with_dependency(self) -> None:
        """record() with depends_on creates dependency."""
        weave = TheWeave()

        id_a = await weave.record(content="A", source="a")
        id_b = await weave.record(content="B", source="b", depends_on={id_a})

        braid = weave.braid()
        assert not braid.are_concurrent(id_a, id_b)

    @pytest.mark.asyncio
    async def test_get_event(self) -> None:
        """get_event() retrieves by ID."""
        weave = TheWeave()

        event_id = await weave.record(content="test", source="a")
        event = weave.get_event(event_id)

        assert event is not None
        assert event.content == "test"

    @pytest.mark.asyncio
    async def test_tip_returns_latest(self) -> None:
        """tip() returns latest event."""
        weave = TheWeave()

        await weave.record(content="1", source="a")
        await weave.record(content="2", source="b")
        id_3 = await weave.record(content="3", source="c")

        tip = weave.tip()

        assert tip is not None
        assert tip.id == id_3

    @pytest.mark.asyncio
    async def test_tip_by_source(self) -> None:
        """tip(source) returns latest for that agent."""
        weave = TheWeave()

        id_a1 = await weave.record(content="a1", source="a")
        await weave.record(content="b1", source="b")
        id_a2 = await weave.record(content="a2", source="a")

        tip = weave.tip(agent="a")

        assert tip is not None
        assert tip.id == id_a2


class TestSynchronization:
    """Tests for synchronize() and knots."""

    @pytest.mark.asyncio
    async def test_synchronize_creates_knot(self) -> None:
        """synchronize() creates a knot event."""
        weave = TheWeave()

        await weave.record(content="A", source="agent_a")
        await weave.record(content="B", source="agent_b")

        knot_id = await weave.synchronize({"agent_a", "agent_b"})

        # Knot is in the weave
        assert knot_id in weave

        # Knot depends on both agents' latest events
        braid = weave.braid()
        knot_deps = braid.get_dependencies(knot_id)
        assert len(knot_deps) == 2

    @pytest.mark.asyncio
    async def test_synchronize_empty(self) -> None:
        """synchronize() with no events creates empty knot."""
        weave = TheWeave()

        knot_id = await weave.synchronize({"agent_a", "agent_b"})

        # Knot exists even with no events
        assert knot_id in weave

    @pytest.mark.asyncio
    async def test_post_sync_events_depend_on_knot(self) -> None:
        """Events after sync can depend on the knot."""
        weave = TheWeave()

        await weave.record(content="A", source="agent_a")
        await weave.record(content="B", source="agent_b")

        knot_id = await weave.synchronize({"agent_a", "agent_b"})

        # New event depends on knot
        new_id = await weave.record(
            content="post-sync",
            source="agent_a",
            depends_on={knot_id},
        )

        braid = weave.braid()
        assert not braid.are_concurrent(knot_id, new_id)


class TestThread:
    """Tests for thread() (agent perspective)."""

    @pytest.mark.asyncio
    async def test_thread_shows_own_events(self) -> None:
        """thread() shows agent's own events."""
        weave = TheWeave()

        id_a = await weave.record(content="A", source="agent_a")
        await weave.record(content="B", source="agent_b")

        thread = weave.thread("agent_a")

        event_ids = {e.id for e in thread}
        assert id_a in event_ids

    @pytest.mark.asyncio
    async def test_thread_shows_dependencies(self) -> None:
        """thread() shows events the agent depends on."""
        weave = TheWeave()

        id_a = await weave.record(content="A", source="agent_a")
        id_b = await weave.record(
            content="B",
            source="agent_b",
            depends_on={id_a},
        )

        thread = weave.thread("agent_b")

        event_ids = {e.id for e in thread}
        assert id_a in event_ids  # B depends on A
        assert id_b in event_ids  # B's own event

    @pytest.mark.asyncio
    async def test_thread_excludes_unrelated(self) -> None:
        """thread() excludes unrelated events."""
        weave = TheWeave()

        id_a = await weave.record(content="A", source="agent_a")
        id_b = await weave.record(content="B", source="agent_b")
        id_c = await weave.record(content="C", source="agent_c")

        thread = weave.thread("agent_a")

        event_ids = {e.id for e in thread}
        assert id_a in event_ids
        assert id_b not in event_ids
        assert id_c not in event_ids


class TestBraid:
    """Tests for braid() (dependency structure)."""

    @pytest.mark.asyncio
    async def test_braid_returns_graph(self) -> None:
        """braid() returns dependency graph."""
        weave = TheWeave()

        await weave.record(content="A", source="agent_a")

        braid = weave.braid()

        assert len(braid) == 1

    @pytest.mark.asyncio
    async def test_braid_tracks_dependencies(self) -> None:
        """braid() tracks all dependencies."""
        weave = TheWeave()

        id_a = await weave.record(content="A", source="agent_a")
        id_b = await weave.record(
            content="B",
            source="agent_b",
            depends_on={id_a},
        )

        braid = weave.braid()

        deps = braid.get_dependencies(id_b)
        assert id_a in deps


class TestLinearize:
    """Tests for linearize()."""

    @pytest.mark.asyncio
    async def test_linearize_returns_valid_order(self) -> None:
        """linearize() returns topologically sorted events."""
        weave = TheWeave()

        id_a = await weave.record(content="A", source="agent_a")
        id_b = await weave.record(
            content="B",
            source="agent_b",
            depends_on={id_a},
        )

        linear = weave.linearize()

        ids = [e.id for e in linear]
        assert ids.index(id_a) < ids.index(id_b)


class TestMultiAgentScenarios:
    """Complex multi-agent scenarios."""

    @pytest.mark.asyncio
    async def test_conversation_chain(self) -> None:
        """A conversation: A->B, B->C, C->A."""
        weave = TheWeave()

        # A talks to B
        id_ab = await weave.record(
            content="A says hello to B",
            source="agent_a",
        )

        # B responds (depends on A)
        id_bc = await weave.record(
            content="B says hello to C",
            source="agent_b",
            depends_on={id_ab},
        )

        # C responds (depends on B)
        id_ca = await weave.record(
            content="C says hello to A",
            source="agent_c",
            depends_on={id_bc},
        )

        # Linear order must be: ab -> bc -> ca
        linear = weave.linearize()
        ids = [e.id for e in linear]

        assert ids.index(id_ab) < ids.index(id_bc)
        assert ids.index(id_bc) < ids.index(id_ca)

    @pytest.mark.asyncio
    async def test_parallel_work_then_sync(self) -> None:
        """Agents work in parallel, then synchronize."""
        weave = TheWeave()

        # Parallel work
        id_a = await weave.record(content="A works", source="agent_a")
        id_b = await weave.record(content="B works", source="agent_b")
        id_c = await weave.record(content="C works", source="agent_c")

        # These are all concurrent
        braid = weave.braid()
        assert braid.are_concurrent(id_a, id_b)
        assert braid.are_concurrent(id_b, id_c)

        # Synchronize
        knot_id = await weave.synchronize({"agent_a", "agent_b", "agent_c"})

        # Post-sync event
        id_post = await weave.record(
            content="All done",
            source="agent_a",
            depends_on={knot_id},
        )

        # Post-sync comes after all parallel work
        linear = weave.linearize()
        ids = [e.id for e in linear]

        assert ids.index(knot_id) > ids.index(id_a)
        assert ids.index(knot_id) > ids.index(id_b)
        assert ids.index(knot_id) > ids.index(id_c)
        assert ids.index(id_post) > ids.index(knot_id)

    @pytest.mark.asyncio
    async def test_fork_join(self) -> None:
        """Fork into parallel work, then join."""
        weave = TheWeave()

        # Initial event
        id_start = await weave.record(content="Start", source="coordinator")

        # Fork: two parallel tasks
        id_task1 = await weave.record(
            content="Task 1",
            source="worker_1",
            depends_on={id_start},
        )
        id_task2 = await weave.record(
            content="Task 2",
            source="worker_2",
            depends_on={id_start},
        )

        # Tasks are concurrent
        braid = weave.braid()
        assert braid.are_concurrent(id_task1, id_task2)

        # Join
        id_join = await weave.record(
            content="Join",
            source="coordinator",
            depends_on={id_task1, id_task2},
        )

        # Join comes after both tasks
        linear = weave.linearize()
        ids = [e.id for e in linear]

        assert ids.index(id_join) > ids.index(id_task1)
        assert ids.index(id_join) > ids.index(id_task2)


class TestExitCriteria:
    """
    Exit criteria test from the spec.

    Test: Concurrent events can be reordered
    """

    @pytest.mark.asyncio
    async def test_spec_exit_criteria(self) -> None:
        """
        Exit Criteria from topos-of-becoming.md:

        weave = TheWeave()

        # Two independent events
        id_a = await weave.record({"msg": "A to B"}, source="agent_a")
        id_c = await weave.record({"msg": "C to D"}, source="agent_c")

        # These are concurrent (no dependency)
        braid = weave.monoid.braid()
        assert braid.are_concurrent(id_a, id_c)

        # Dependent event
        id_b = await weave.record(
            {"msg": "B to C"},
            source="agent_b",
            depends_on={id_a}
        )
        assert not braid.are_concurrent(id_a, id_b)
        """
        weave = TheWeave()

        # Two independent events
        id_a = await weave.record({"msg": "A to B"}, source="agent_a")
        id_c = await weave.record({"msg": "C to D"}, source="agent_c")

        # These are concurrent (no dependency)
        braid = weave.monoid.braid()
        assert braid.are_concurrent(id_a, id_c)

        # Dependent event
        id_b = await weave.record({"msg": "B to C"}, source="agent_b", depends_on={id_a})

        # Refresh braid after adding new event
        braid = weave.monoid.braid()
        assert not braid.are_concurrent(id_a, id_b)
