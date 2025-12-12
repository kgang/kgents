"""
Tests for concurrency behavior in the Weave.

These tests verify the core Trace Monoid property:
- Independent events can be reordered (commute)
- Dependent events must maintain order

This is the mathematical foundation for multi-agent concurrent execution.
"""

from __future__ import annotations

import pytest

from ..dependency import DependencyGraph
from ..event import Event
from ..trace_monoid import TraceMonoid


class TestConcurrencyBasics:
    """Basic concurrency tests."""

    def test_no_dependency_implies_concurrent(self) -> None:
        """Events without dependency relation are concurrent."""
        monoid: TraceMonoid[str] = TraceMonoid()

        # Agent A talks to Agent B
        e_ab = Event.create(content="A->B", source="a", event_id="ab")
        # Agent C talks to Agent D (independent)
        e_cd = Event.create(content="C->D", source="c", event_id="cd")

        monoid.append_mut(e_ab)
        monoid.append_mut(e_cd)

        # These are concurrent (no causal connection)
        assert monoid.are_concurrent("ab", "cd")

    def test_dependency_implies_not_concurrent(self) -> None:
        """Events with dependency are not concurrent."""
        monoid: TraceMonoid[str] = TraceMonoid()

        # Agent A talks to Agent B
        e_ab = Event.create(content="A->B", source="a", event_id="ab")
        # Agent B talks to Agent C (depends on A->B)
        e_bc = Event.create(content="B->C", source="b", event_id="bc")

        monoid.append_mut(e_ab)
        monoid.append_mut(e_bc, depends_on={"ab"})

        # ab must precede bc
        assert not monoid.are_concurrent("ab", "bc")

    def test_concurrent_events_multiple_orderings(self) -> None:
        """Concurrent events admit multiple valid orderings."""
        monoid: TraceMonoid[str] = TraceMonoid()

        e1 = Event.create(content="1", source="a", event_id="e1")
        e2 = Event.create(content="2", source="b", event_id="e2")

        monoid.append_mut(e1)
        monoid.append_mut(e2)

        # Both [e1, e2] and [e2, e1] are valid
        linear = monoid.linearize()

        # One valid ordering is returned
        assert len(linear) == 2
        assert {e.id for e in linear} == {"e1", "e2"}


class TestDiamondDependency:
    """Test diamond-shaped dependency patterns."""

    def test_diamond_pattern(self) -> None:
        """
        Diamond pattern: A -> B, A -> C, B -> D, C -> D

              A
             / \\
            B   C
             \\ /
              D
        """
        monoid: TraceMonoid[str] = TraceMonoid()

        e_a = Event.create(content="A", source="a", event_id="a")
        e_b = Event.create(content="B", source="b", event_id="b")
        e_c = Event.create(content="C", source="c", event_id="c")
        e_d = Event.create(content="D", source="d", event_id="d")

        monoid.append_mut(e_a)
        monoid.append_mut(e_b, depends_on={"a"})
        monoid.append_mut(e_c, depends_on={"a"})
        monoid.append_mut(e_d, depends_on={"b", "c"})

        # B and C are concurrent (both depend on A, neither on each other)
        assert monoid.are_concurrent("b", "c")

        # A must come before B, C, D
        assert not monoid.are_concurrent("a", "b")
        assert not monoid.are_concurrent("a", "c")
        assert not monoid.are_concurrent("a", "d")

        # D must come after B and C
        assert not monoid.are_concurrent("b", "d")
        assert not monoid.are_concurrent("c", "d")

    def test_diamond_linearization(self) -> None:
        """Diamond linearization respects all constraints."""
        monoid: TraceMonoid[str] = TraceMonoid()

        e_a = Event.create(content="A", source="a", event_id="a")
        e_b = Event.create(content="B", source="b", event_id="b")
        e_c = Event.create(content="C", source="c", event_id="c")
        e_d = Event.create(content="D", source="d", event_id="d")

        monoid.append_mut(e_a)
        monoid.append_mut(e_b, depends_on={"a"})
        monoid.append_mut(e_c, depends_on={"a"})
        monoid.append_mut(e_d, depends_on={"b", "c"})

        linear = monoid.linearize()
        ids = [e.id for e in linear]

        # A must be first
        assert ids.index("a") == 0
        # D must be last
        assert ids.index("d") == 3
        # B and C in middle (either order)
        assert ids.index("b") < ids.index("d")
        assert ids.index("c") < ids.index("d")


class TestParallelChains:
    """Test parallel independent chains."""

    def test_parallel_chains(self) -> None:
        """
        Two independent chains:
        Chain 1: A1 -> B1 -> C1
        Chain 2: A2 -> B2 -> C2
        """
        monoid: TraceMonoid[str] = TraceMonoid()

        # Chain 1
        a1 = Event.create(content="A1", source="1", event_id="a1")
        b1 = Event.create(content="B1", source="1", event_id="b1")
        c1 = Event.create(content="C1", source="1", event_id="c1")

        # Chain 2
        a2 = Event.create(content="A2", source="2", event_id="a2")
        b2 = Event.create(content="B2", source="2", event_id="b2")
        c2 = Event.create(content="C2", source="2", event_id="c2")

        monoid.append_mut(a1)
        monoid.append_mut(a2)
        monoid.append_mut(b1, depends_on={"a1"})
        monoid.append_mut(b2, depends_on={"a2"})
        monoid.append_mut(c1, depends_on={"b1"})
        monoid.append_mut(c2, depends_on={"b2"})

        # Within chain: not concurrent
        assert not monoid.are_concurrent("a1", "b1")
        assert not monoid.are_concurrent("b1", "c1")

        # Across chains: concurrent
        assert monoid.are_concurrent("a1", "a2")
        assert monoid.are_concurrent("b1", "b2")
        assert monoid.are_concurrent("c1", "c2")
        assert monoid.are_concurrent("a1", "c2")

    def test_parallel_chains_linearization(self) -> None:
        """Linearization interleaves parallel chains validly."""
        monoid: TraceMonoid[str] = TraceMonoid()

        a1 = Event.create(content="A1", source="1", event_id="a1")
        b1 = Event.create(content="B1", source="1", event_id="b1")
        a2 = Event.create(content="A2", source="2", event_id="a2")
        b2 = Event.create(content="B2", source="2", event_id="b2")

        monoid.append_mut(a1)
        monoid.append_mut(a2)
        monoid.append_mut(b1, depends_on={"a1"})
        monoid.append_mut(b2, depends_on={"a2"})

        linear = monoid.linearize()
        ids = [e.id for e in linear]

        # Within-chain order preserved
        assert ids.index("a1") < ids.index("b1")
        assert ids.index("a2") < ids.index("b2")


class TestThreeWayConcurrency:
    """Test three-way concurrent scenarios."""

    def test_three_independent_agents(self) -> None:
        """Three agents acting independently are all pairwise concurrent."""
        monoid: TraceMonoid[str] = TraceMonoid()

        e1 = Event.create(content="1", source="a", event_id="e1")
        e2 = Event.create(content="2", source="b", event_id="e2")
        e3 = Event.create(content="3", source="c", event_id="e3")

        monoid.append_mut(e1)
        monoid.append_mut(e2)
        monoid.append_mut(e3)

        assert monoid.are_concurrent("e1", "e2")
        assert monoid.are_concurrent("e2", "e3")
        assert monoid.are_concurrent("e1", "e3")

    def test_three_way_join(self) -> None:
        """Three concurrent events joining at one point."""
        monoid: TraceMonoid[str] = TraceMonoid()

        e1 = Event.create(content="1", source="a", event_id="e1")
        e2 = Event.create(content="2", source="b", event_id="e2")
        e3 = Event.create(content="3", source="c", event_id="e3")
        join = Event.create(content="join", source="d", event_id="join")

        monoid.append_mut(e1)
        monoid.append_mut(e2)
        monoid.append_mut(e3)
        monoid.append_mut(join, depends_on={"e1", "e2", "e3"})

        # e1, e2, e3 are concurrent
        assert monoid.are_concurrent("e1", "e2")
        assert monoid.are_concurrent("e2", "e3")

        # All depend on join
        assert not monoid.are_concurrent("e1", "join")
        assert not monoid.are_concurrent("e2", "join")
        assert not monoid.are_concurrent("e3", "join")


class TestDependencyGraph:
    """Tests for DependencyGraph class."""

    def test_add_node(self) -> None:
        """add_node() adds to graph."""
        graph = DependencyGraph()
        graph.add_node("a")

        assert "a" in graph
        assert len(graph) == 1

    def test_add_node_with_deps(self) -> None:
        """add_node() tracks dependencies."""
        graph = DependencyGraph()
        graph.add_node("a")
        graph.add_node("b", depends_on={"a"})

        deps = graph.get_dependencies("b")
        assert "a" in deps

    def test_cycle_detection(self) -> None:
        """add_node() detects cycles."""
        graph = DependencyGraph()
        graph.add_node("a")
        graph.add_node("b", depends_on={"a"})

        with pytest.raises(ValueError, match="cycle"):
            graph.add_node("a", depends_on={"b"})

    def test_self_dependency_rejected(self) -> None:
        """add_node() rejects self-dependency."""
        graph = DependencyGraph()

        with pytest.raises(ValueError, match="itself"):
            graph.add_node("a", depends_on={"a"})

    def test_roots(self) -> None:
        """get_roots() returns nodes with no dependencies."""
        graph = DependencyGraph()
        graph.add_node("a")
        graph.add_node("b", depends_on={"a"})
        graph.add_node("c")

        roots = graph.get_roots()

        assert "a" in roots
        assert "c" in roots
        assert "b" not in roots

    def test_leaves(self) -> None:
        """get_leaves() returns nodes nothing depends on."""
        graph = DependencyGraph()
        graph.add_node("a")
        graph.add_node("b", depends_on={"a"})
        graph.add_node("c", depends_on={"a"})

        leaves = graph.get_leaves()

        assert "b" in leaves
        assert "c" in leaves
        assert "a" not in leaves

    def test_transitive_dependencies(self) -> None:
        """get_all_dependencies() returns transitive closure."""
        graph = DependencyGraph()
        graph.add_node("a")
        graph.add_node("b", depends_on={"a"})
        graph.add_node("c", depends_on={"b"})

        all_deps = graph.get_all_dependencies("c")

        assert "a" in all_deps
        assert "b" in all_deps

    def test_topological_sort(self) -> None:
        """topological_sort() returns valid ordering."""
        graph = DependencyGraph()
        graph.add_node("a")
        graph.add_node("b", depends_on={"a"})
        graph.add_node("c", depends_on={"b"})

        order = graph.topological_sort()

        assert order.index("a") < order.index("b") < order.index("c")


class TestConcurrencyEdgeCases:
    """Edge cases for concurrency."""

    def test_unknown_events_are_concurrent(self) -> None:
        """Unknown events are considered concurrent."""
        monoid: TraceMonoid[str] = TraceMonoid()

        # No events added
        assert monoid.are_concurrent("unknown1", "unknown2")

    def test_single_event_not_concurrent_with_self(self) -> None:
        """An event is not concurrent with itself (trivially)."""
        monoid: TraceMonoid[str] = TraceMonoid()
        e1 = Event.create(content="1", source="a", event_id="e1")
        monoid.append_mut(e1)

        # Conceptually, an event is not concurrent with itself
        # (the definition requires distinct events)
        # Our implementation returns False because the event exists
        # and trivially "reaches" itself in the graph check
        result = monoid.are_concurrent("e1", "e1")
        # This is a mathematical edge case - in Trace Theory,
        # we typically only ask about distinct events
        assert result is False  # Event trivially not concurrent with itself

    def test_many_concurrent_events(self) -> None:
        """Many independent events are all pairwise concurrent."""
        monoid: TraceMonoid[str] = TraceMonoid()

        events = []
        for i in range(10):
            e = Event.create(content=str(i), source=f"agent_{i}", event_id=f"e{i}")
            monoid.append_mut(e)
            events.append(e)

        # All pairwise concurrent
        for i in range(10):
            for j in range(i + 1, 10):
                assert monoid.are_concurrent(f"e{i}", f"e{j}")
