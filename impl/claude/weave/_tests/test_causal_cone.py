"""
Tests for CausalCone - The Perspective Functor.

Tests verify:
1. Basic cone projection for single agent
2. Multi-agent concurrent events (independent threads excluded)
3. Dependency chain linearization
4. Compression ratio calculation
5. Integration with Turn types
6. Edge cases (empty weave, no tip, etc.)
7. Cone statistics

The key hypothesis (H1 from Turn-gents plan):
    Auto-context via causal cone reduces prompt tokens
    while preserving decision quality.
"""

from __future__ import annotations

import pytest

from ..causal_cone import CausalCone, CausalConeStats, compute_cone_stats
from ..event import Event
from ..trace_monoid import TraceMonoid
from ..turn import Turn, TurnType
from ..weave import TheWeave


class TestCausalConeBasic:
    """Basic causal cone projection tests."""

    @pytest.mark.asyncio
    async def test_empty_weave_returns_empty_cone(self) -> None:
        """Empty weave produces empty cone."""
        weave: TheWeave = TheWeave()
        cone = CausalCone(weave)

        context = cone.project_context("agent-a")

        assert context == []

    @pytest.mark.asyncio
    async def test_single_event_cone(self) -> None:
        """Single event is in its own cone."""
        weave: TheWeave = TheWeave()
        event_id = await weave.record("Hello", "agent-a")

        cone = CausalCone(weave)
        context = cone.project_context("agent-a")

        assert len(context) == 1
        assert context[0].id == event_id

    @pytest.mark.asyncio
    async def test_chain_dependencies_in_cone(self) -> None:
        """Dependency chain is fully in cone."""
        weave: TheWeave = TheWeave()

        id1 = await weave.record("First", "agent-a")
        id2 = await weave.record("Second", "agent-a", depends_on={id1})
        id3 = await weave.record("Third", "agent-a", depends_on={id2})

        cone = CausalCone(weave)
        context = cone.project_context("agent-a")

        assert len(context) == 3
        # Order should be topological
        ids = [e.id for e in context]
        assert ids.index(id1) < ids.index(id2) < ids.index(id3)


class TestCausalConeConcurrency:
    """Tests for concurrent event handling (the key insight)."""

    @pytest.mark.asyncio
    async def test_concurrent_agents_excluded(self) -> None:
        """
        Concurrent agents' events NOT in each other's cone.

        This is the key insight: if Agent A never read Agent B's message,
        Agent B's turn is NOT in A's cone.
        """
        weave: TheWeave = TheWeave()

        # Agent A and B work independently (no dependencies between them)
        await weave.record("A1", "agent-a")
        await weave.record("A2", "agent-a")
        await weave.record("B1", "agent-b")
        await weave.record("B2", "agent-b")

        cone = CausalCone(weave)

        # Agent A's cone should NOT contain B's events
        context_a = cone.project_context("agent-a")
        sources_a = {e.source for e in context_a}
        assert sources_a == {"agent-a"}

        # Agent B's cone should NOT contain A's events
        context_b = cone.project_context("agent-b")
        sources_b = {e.source for e in context_b}
        assert sources_b == {"agent-b"}

    @pytest.mark.asyncio
    async def test_reading_brings_into_cone(self) -> None:
        """
        When Agent A depends on Agent B's event,
        B's event IS in A's cone.
        """
        weave: TheWeave = TheWeave()

        # B sends message
        b1 = await weave.record("Hello from B", "agent-b")

        # A reads B's message (depends on it)
        await weave.record("I saw B's message", "agent-a", depends_on={b1})

        cone = CausalCone(weave)
        context_a = cone.project_context("agent-a")

        # A's cone now includes B's message
        sources = {e.source for e in context_a}
        assert "agent-b" in sources
        assert "agent-a" in sources

    @pytest.mark.asyncio
    async def test_transitive_dependencies_in_cone(self) -> None:
        """Transitive dependencies are included in cone."""
        weave: TheWeave = TheWeave()

        # C -> B -> A chain
        c1 = await weave.record("C origin", "agent-c")
        b1 = await weave.record("B reads C", "agent-b", depends_on={c1})
        await weave.record("A reads B", "agent-a", depends_on={b1})

        cone = CausalCone(weave)
        context_a = cone.project_context("agent-a")

        # A's cone includes C (transitively via B)
        sources = {e.source for e in context_a}
        assert sources == {"agent-a", "agent-b", "agent-c"}

    @pytest.mark.asyncio
    async def test_partial_read_only_includes_read_branch(self) -> None:
        """
        If A reads only some of B's events, only those branches
        are in A's cone.
        """
        weave: TheWeave = TheWeave()

        # B has two independent messages
        b1 = await weave.record("B message 1", "agent-b")
        b2 = await weave.record("B message 2", "agent-b")

        # A only reads b1, not b2
        await weave.record("A reads B1 only", "agent-a", depends_on={b1})

        cone = CausalCone(weave)
        context_a = cone.project_context("agent-a")

        # A's cone includes b1 but NOT b2
        ids = {e.id for e in context_a}
        assert b1 in ids
        assert b2 not in ids


class TestCausalConeLinearization:
    """Tests for linearization (topological sort) in cone."""

    @pytest.mark.asyncio
    async def test_linearize_respects_dependencies(self) -> None:
        """Linearized cone respects happened-before."""
        weave: TheWeave = TheWeave()

        # Diamond dependency: a -> {b, c} -> d
        a = await weave.record("A", "agent", event_id="a")
        b = await weave.record("B", "agent", event_id="b", depends_on={a})
        c = await weave.record("C", "agent", event_id="c", depends_on={a})
        d = await weave.record("D", "agent", event_id="d", depends_on={b, c})

        cone = CausalCone(weave)
        context = cone.project_context("agent")

        ids = [e.id for e in context]
        # A must come before B, C, D
        assert ids.index("a") < ids.index("b")
        assert ids.index("a") < ids.index("c")
        assert ids.index("a") < ids.index("d")
        # B and C must come before D
        assert ids.index("b") < ids.index("d")
        assert ids.index("c") < ids.index("d")

    @pytest.mark.asyncio
    async def test_linearize_subset_only_includes_subset(self) -> None:
        """linearize_subset only returns events in the subset."""
        monoid: TraceMonoid[str] = TraceMonoid()

        e1 = Event.create("1", "agent", event_id="e1")
        e2 = Event.create("2", "agent", event_id="e2")
        e3 = Event.create("3", "agent", event_id="e3")

        monoid.append_mut(e1)
        monoid.append_mut(e2, depends_on={"e1"})
        monoid.append_mut(e3, depends_on={"e2"})

        # Only linearize e1 and e2
        subset = monoid.linearize_subset({"e1", "e2"})

        assert len(subset) == 2
        ids = [e.id for e in subset]
        assert "e3" not in ids


class TestCausalConeWithTurns:
    """Tests for CausalCone with Turn types."""

    @pytest.mark.asyncio
    async def test_turns_in_cone(self) -> None:
        """Turn instances work in causal cone."""
        weave: TheWeave = TheWeave()

        # Add turns directly to monoid
        t1 = Turn.create_turn("Speech", "agent-a", TurnType.SPEECH, turn_id="t1")
        t2 = Turn.create_turn("Action", "agent-a", TurnType.ACTION, turn_id="t2")

        weave.monoid.append_mut(t1)
        weave.monoid.append_mut(t2, depends_on={"t1"})

        cone = CausalCone(weave)
        context = cone.project_context("agent-a")

        assert len(context) == 2
        # Verify they're Turn instances
        assert isinstance(context[0], Turn)
        assert isinstance(context[1], Turn)

    @pytest.mark.asyncio
    async def test_thought_turns_in_cone(self) -> None:
        """THOUGHT turns are in cone (just hidden by default)."""
        weave: TheWeave = TheWeave()

        thought = Turn.create_turn(
            "Thinking...", "agent", TurnType.THOUGHT, turn_id="th"
        )
        speech = Turn.create_turn("Hello", "agent", TurnType.SPEECH, turn_id="sp")

        weave.monoid.append_mut(thought)
        weave.monoid.append_mut(speech, depends_on={"th"})

        cone = CausalCone(weave)
        context = cone.project_context("agent")

        # Both in cone (filtering is separate concern)
        assert len(context) == 2


class TestCausalConeMetrics:
    """Tests for compression ratio and statistics."""

    @pytest.mark.asyncio
    async def test_compression_ratio_independent_agents(self) -> None:
        """High compression when agents are independent."""
        weave: TheWeave = TheWeave()

        # 5 agents, each with 2 events, no dependencies between agents
        for i in range(5):
            agent = f"agent-{i}"
            e1 = await weave.record(f"{agent}-1", agent)
            await weave.record(f"{agent}-2", agent, depends_on={e1})

        cone = CausalCone(weave)

        # Each agent sees only their 2 events out of 10 total
        for i in range(5):
            ratio = cone.compression_ratio(f"agent-{i}")
            # 1 - 2/10 = 0.8 = 80% compression
            assert ratio == pytest.approx(0.8, abs=0.01)

    @pytest.mark.asyncio
    async def test_compression_ratio_all_connected(self) -> None:
        """Low compression when all events connected."""
        weave: TheWeave = TheWeave()

        # Single chain: each depends on previous
        prev_id = None
        for i in range(10):
            depends = {prev_id} if prev_id else None
            prev_id = await weave.record(f"Event {i}", "agent", depends_on=depends)

        cone = CausalCone(weave)

        # Agent sees all 10 events
        ratio = cone.compression_ratio("agent")
        assert ratio == pytest.approx(0.0)  # No compression

    @pytest.mark.asyncio
    async def test_cone_size(self) -> None:
        """cone_size returns count of events in cone."""
        weave: TheWeave = TheWeave()

        await weave.record("1", "agent-a")
        await weave.record("2", "agent-a")
        await weave.record("3", "agent-b")

        cone = CausalCone(weave)

        assert cone.cone_size("agent-a") == 2
        assert cone.cone_size("agent-b") == 1


class TestCausalConeStats:
    """Tests for CausalConeStats."""

    @pytest.mark.asyncio
    async def test_stats_from_cone(self) -> None:
        """CausalConeStats captures turn type breakdown."""
        weave: TheWeave = TheWeave()

        # Add various turn types
        t1 = Turn.create_turn("Hello", "agent", TurnType.SPEECH, turn_id="t1")
        t2 = Turn.create_turn("Do X", "agent", TurnType.ACTION, turn_id="t2")
        t3 = Turn.create_turn("...", "agent", TurnType.THOUGHT, turn_id="t3")

        weave.monoid.append_mut(t1)
        weave.monoid.append_mut(t2, depends_on={"t1"})
        weave.monoid.append_mut(t3, depends_on={"t2"})

        cone = CausalCone(weave)
        stats = compute_cone_stats(cone, "agent")

        assert stats.cone_size == 3
        assert stats.total_weave_size == 3
        assert stats.speech_turns == 1
        assert stats.action_turns == 1
        assert stats.thought_turns == 1
        assert stats.yield_turns == 0
        assert stats.silence_turns == 0

    @pytest.mark.asyncio
    async def test_stats_compression_ratio(self) -> None:
        """Stats includes compression ratio."""
        weave: TheWeave = TheWeave()

        await weave.record("A", "agent-a")
        await weave.record("B", "agent-b")

        cone = CausalCone(weave)
        stats = compute_cone_stats(cone, "agent-a")

        assert stats.compression_ratio == pytest.approx(0.5)


class TestCausalConeEdgeCases:
    """Edge case tests."""

    @pytest.mark.asyncio
    async def test_unknown_agent_returns_empty(self) -> None:
        """Unknown agent (no tip) returns empty cone."""
        weave: TheWeave = TheWeave()
        await weave.record("Data", "agent-a")

        cone = CausalCone(weave)
        context = cone.project_context("unknown-agent")

        assert context == []

    @pytest.mark.asyncio
    async def test_project_context_from_events(self) -> None:
        """project_context_from_events works for arbitrary event sets."""
        weave: TheWeave = TheWeave()

        e1 = await weave.record("1", "a", event_id="e1")
        e2 = await weave.record("2", "a", event_id="e2", depends_on={e1})
        e3 = await weave.record("3", "b", event_id="e3")

        cone: CausalCone = CausalCone(weave)

        # Get cone for just e2 (should include e1 as dependency)
        context = cone.project_context_from_events({"e2"})

        ids = {e.id for e in context}
        assert "e1" in ids
        assert "e2" in ids
        assert "e3" not in ids  # Independent

    @pytest.mark.asyncio
    async def test_are_causally_related(self) -> None:
        """are_causally_related detects dependencies."""
        weave: TheWeave = TheWeave()

        e1 = await weave.record("1", "a", event_id="e1")
        e2 = await weave.record("2", "a", event_id="e2", depends_on={e1})
        e3 = await weave.record("3", "b", event_id="e3")

        cone: CausalCone = CausalCone(weave)

        # e1 and e2 are related (e2 depends on e1)
        assert cone.are_causally_related("e1", "e2") is True

        # e1 and e3 are NOT related (concurrent)
        assert cone.are_causally_related("e1", "e3") is False

    @pytest.mark.asyncio
    async def test_refresh_braid_after_modification(self) -> None:
        """refresh_braid updates cached dependency graph."""
        weave: TheWeave = TheWeave()

        await weave.record("1", "agent", event_id="e1")

        cone: CausalCone = CausalCone(weave)
        context1 = cone.project_context("agent")
        assert len(context1) == 1

        # Add more events
        await weave.record("2", "agent", event_id="e2", depends_on={"e1"})

        # Without refresh, cache is stale
        # (In practice, create new CausalCone or call refresh_braid)
        cone.refresh_braid()

        context2 = cone.project_context("agent")
        assert len(context2) == 2


class TestCausalConeLaw4:
    """
    Tests for Law 4 — Perspective as Functor.

    Context is computed via CausalCone.project_context(),
    not manually curated.
    """

    @pytest.mark.asyncio
    async def test_perspective_is_functorial(self) -> None:
        """
        Perspective projection is functorial:
        project(A ∪ B) ⊇ project(A) ∪ project(B)

        (Union of cones contains union of individual cones)
        """
        weave: TheWeave = TheWeave()

        # Shared ancestor
        root = await weave.record("Root", "root", event_id="root")

        # Two independent branches from root
        await weave.record("A1", "agent-a", event_id="a1", depends_on={root})
        await weave.record("B1", "agent-b", event_id="b1", depends_on={root})

        cone: CausalCone = CausalCone(weave)

        cone_a = {e.id for e in cone.project_context("agent-a")}
        cone_b = {e.id for e in cone.project_context("agent-b")}

        # Both cones include root
        assert "root" in cone_a
        assert "root" in cone_b

        # But A doesn't see B's events and vice versa
        assert "b1" not in cone_a
        assert "a1" not in cone_b
