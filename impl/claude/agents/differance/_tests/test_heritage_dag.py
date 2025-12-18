"""
Tests for GhostHeritageDAG: Heritage visualization for the Différance Engine.

This module tests:
1. HeritageNode creation and properties
2. HeritageEdge creation and classification
3. GhostHeritageDAG construction and queries
4. Builder function correctness
5. Property-based tests for DAG laws
6. Store integration

Phase 3 Exit Criteria:
- Can build DAG from trace log
- chosen_path() returns correct linear sequence
- ghost_paths() captures all alternatives
- at_depth(d) filters correctly
- All tests pass

See: spec/protocols/differance.md
"""

from __future__ import annotations

from datetime import datetime, timezone

import pytest
from hypothesis import given, settings, strategies as st

from agents.differance.heritage import (
    EdgeType,
    GhostHeritageDAG,
    HeritageEdge,
    HeritageNode,
    NodeType,
    build_heritage_dag,
    build_heritage_dag_from_traces,
)
from agents.differance.trace import Alternative, TraceMonoid, WiringTrace

# =============================================================================
# Test Fixtures
# =============================================================================


def make_trace(
    trace_id: str,
    operation: str = "seq",
    inputs: tuple[str, ...] = ("A", "B"),
    output: str = "AB",
    context: str = "test",
    alternatives: tuple[Alternative, ...] = (),
    parent_trace_id: str | None = None,
) -> WiringTrace:
    """Create a test trace with sensible defaults."""
    return WiringTrace(
        trace_id=trace_id,
        timestamp=datetime.now(timezone.utc),
        operation=operation,
        inputs=inputs,
        output=output,
        context=context,
        alternatives=alternatives,
        parent_trace_id=parent_trace_id,
    )


def make_ghost(
    operation: str = "par",
    inputs: tuple[str, ...] = ("A", "B"),
    reason: str = "Order matters",
    could_revisit: bool = True,
) -> Alternative:
    """Create a test alternative (ghost)."""
    return Alternative(
        operation=operation,
        inputs=inputs,
        reason_rejected=reason,
        could_revisit=could_revisit,
    )


def make_linear_chain(length: int = 3) -> TraceMonoid:
    """Create a linear chain of traces without ghosts."""
    traces: list[WiringTrace] = []
    for i in range(length):
        parent_id = traces[-1].trace_id if traces else None
        trace = make_trace(
            trace_id=f"trace_{i}",
            operation=f"op_{i}",
            output=f"output_{i}",
            parent_trace_id=parent_id,
        )
        traces.append(trace)
    return TraceMonoid(traces=tuple(traces))


def make_chain_with_ghosts(length: int = 3, ghosts_per_trace: int = 1) -> TraceMonoid:
    """Create a linear chain with ghost alternatives at each step."""
    traces: list[WiringTrace] = []
    for i in range(length):
        parent_id = traces[-1].trace_id if traces else None
        alts = tuple(
            make_ghost(
                operation=f"alt_{i}_{j}",
                reason=f"Rejected alternative {j} at step {i}",
                could_revisit=(j % 2 == 0),  # Alternate explorable
            )
            for j in range(ghosts_per_trace)
        )
        trace = make_trace(
            trace_id=f"trace_{i}",
            operation=f"op_{i}",
            output=f"output_{i}",
            alternatives=alts,
            parent_trace_id=parent_id,
        )
        traces.append(trace)
    return TraceMonoid(traces=tuple(traces))


# =============================================================================
# HeritageNode Tests
# =============================================================================


class TestHeritageNode:
    """Tests for HeritageNode dataclass."""

    def test_create_chosen_node(self) -> None:
        """Can create a chosen node."""
        node = HeritageNode(
            id="trace_abc",
            node_type="chosen",
            operation="seq",
            timestamp=datetime.now(timezone.utc),
            depth=0,
            output="result",
        )
        assert node.id == "trace_abc"
        assert node.node_type == "chosen"
        assert node.output == "result"
        assert node.reason is None

    def test_create_ghost_node(self) -> None:
        """Can create a ghost node."""
        node = HeritageNode(
            id="trace_abc_ghost_0",
            node_type="ghost",
            operation="par",
            timestamp=datetime.now(timezone.utc),
            depth=0,
            reason="Order matters",
            explorable=False,
        )
        assert node.node_type == "ghost"
        assert node.reason == "Order matters"
        assert node.output is None

    def test_create_deferred_node(self) -> None:
        """Can create a deferred (explorable ghost) node."""
        node = HeritageNode(
            id="trace_abc_ghost_0",
            node_type="deferred",
            operation="branch",
            timestamp=datetime.now(timezone.utc),
            depth=1,
            reason="Not needed yet",
            explorable=True,
        )
        assert node.node_type == "deferred"
        assert node.explorable is True

    def test_is_chosen_true_for_chosen_nodes(self) -> None:
        """is_chosen() returns True for chosen nodes."""
        node = HeritageNode(
            id="trace_abc",
            node_type="chosen",
            operation="seq",
            timestamp=datetime.now(timezone.utc),
            depth=0,
        )
        assert node.is_chosen() is True
        assert node.is_ghost() is False

    def test_is_ghost_true_for_ghost_and_deferred(self) -> None:
        """is_ghost() returns True for ghost and deferred nodes."""
        ghost = HeritageNode(
            id="g1",
            node_type="ghost",
            operation="op",
            timestamp=datetime.now(timezone.utc),
            depth=0,
        )
        deferred = HeritageNode(
            id="g2",
            node_type="deferred",
            operation="op",
            timestamp=datetime.now(timezone.utc),
            depth=0,
        )
        assert ghost.is_ghost() is True
        assert deferred.is_ghost() is True

    def test_can_explore_for_explorable_ghost(self) -> None:
        """can_explore() returns True only for explorable ghosts."""
        explorable = HeritageNode(
            id="g1",
            node_type="deferred",
            operation="op",
            timestamp=datetime.now(timezone.utc),
            depth=0,
            explorable=True,
        )
        non_explorable = HeritageNode(
            id="g2",
            node_type="ghost",
            operation="op",
            timestamp=datetime.now(timezone.utc),
            depth=0,
            explorable=False,
        )
        chosen = HeritageNode(
            id="c1",
            node_type="chosen",
            operation="op",
            timestamp=datetime.now(timezone.utc),
            depth=0,
            explorable=True,  # Even with explorable=True, chosen can't explore
        )

        assert explorable.can_explore() is True
        assert non_explorable.can_explore() is False
        assert chosen.can_explore() is False

    def test_node_is_frozen(self) -> None:
        """HeritageNode is immutable (frozen dataclass)."""
        node = HeritageNode(
            id="trace_abc",
            node_type="chosen",
            operation="seq",
            timestamp=datetime.now(timezone.utc),
            depth=0,
        )
        with pytest.raises(AttributeError):
            node.id = "new_id"  # type: ignore


# =============================================================================
# HeritageEdge Tests
# =============================================================================


class TestHeritageEdge:
    """Tests for HeritageEdge dataclass."""

    def test_create_produced_edge(self) -> None:
        """Can create a produced edge."""
        edge = HeritageEdge(
            source="trace_1",
            target="trace_2",
            edge_type="produced",
        )
        assert edge.source == "trace_1"
        assert edge.target == "trace_2"
        assert edge.edge_type == "produced"

    def test_create_ghosted_edge(self) -> None:
        """Can create a ghosted edge."""
        edge = HeritageEdge(
            source="trace_1",
            target="trace_1_ghost_0",
            edge_type="ghosted",
        )
        assert edge.edge_type == "ghosted"

    def test_create_deferred_edge(self) -> None:
        """Can create a deferred edge."""
        edge = HeritageEdge(
            source="trace_1",
            target="trace_1_ghost_0",
            edge_type="deferred",
        )
        assert edge.edge_type == "deferred"

    def test_is_causal_for_produced_and_concretized(self) -> None:
        """is_causal() returns True for produced and concretized edges."""
        produced = HeritageEdge("a", "b", "produced")
        concretized = HeritageEdge("a", "b", "concretized")
        ghosted = HeritageEdge("a", "b", "ghosted")
        deferred = HeritageEdge("a", "b", "deferred")

        assert produced.is_causal() is True
        assert concretized.is_causal() is True
        assert ghosted.is_causal() is False
        assert deferred.is_causal() is False

    def test_is_ghost_edge_for_ghosted_and_deferred(self) -> None:
        """is_ghost_edge() returns True for ghosted and deferred edges."""
        produced = HeritageEdge("a", "b", "produced")
        ghosted = HeritageEdge("a", "b", "ghosted")
        deferred = HeritageEdge("a", "b", "deferred")

        assert produced.is_ghost_edge() is False
        assert ghosted.is_ghost_edge() is True
        assert deferred.is_ghost_edge() is True

    def test_edge_is_frozen(self) -> None:
        """HeritageEdge is immutable (frozen dataclass)."""
        edge = HeritageEdge("a", "b", "produced")
        with pytest.raises(AttributeError):
            edge.source = "new_source"  # type: ignore


# =============================================================================
# GhostHeritageDAG Basic Tests
# =============================================================================


class TestGhostHeritageDAGBasic:
    """Tests for GhostHeritageDAG structure."""

    def test_empty_dag(self) -> None:
        """Can create an empty DAG."""
        dag = GhostHeritageDAG(nodes={}, edges=(), root_id="")
        assert dag.node_count == 0
        assert dag.edge_count == 0
        assert dag.max_depth == 0
        assert dag.root_id == ""

    def test_single_node_dag(self) -> None:
        """Can create a DAG with one node."""
        node = HeritageNode(
            id="root",
            node_type="chosen",
            operation="seq",
            timestamp=datetime.now(timezone.utc),
            depth=0,
        )
        dag = GhostHeritageDAG(
            nodes={"root": node},
            edges=(),
            root_id="root",
        )
        assert dag.node_count == 1
        assert dag.edge_count == 0
        assert dag.max_depth == 0

    def test_linear_chain_dag(self) -> None:
        """Can create a linear chain DAG."""
        now = datetime.now(timezone.utc)
        n1 = HeritageNode("n1", "chosen", "op1", now, 0)
        n2 = HeritageNode("n2", "chosen", "op2", now, 1)
        n3 = HeritageNode("n3", "chosen", "op3", now, 2)

        e1 = HeritageEdge("n1", "n2", "produced")
        e2 = HeritageEdge("n2", "n3", "produced")

        dag = GhostHeritageDAG(
            nodes={"n1": n1, "n2": n2, "n3": n3},
            edges=(e1, e2),
            root_id="n1",
        )

        assert dag.node_count == 3
        assert dag.edge_count == 2
        assert dag.max_depth == 2

    def test_dag_with_ghosts(self) -> None:
        """Can create a DAG with ghost nodes."""
        now = datetime.now(timezone.utc)
        n1 = HeritageNode("n1", "chosen", "op1", now, 0)
        g1 = HeritageNode("n1_ghost_0", "ghost", "alt1", now, 0, reason="Not chosen")
        n2 = HeritageNode("n2", "chosen", "op2", now, 1)

        e1 = HeritageEdge("n1", "n1_ghost_0", "ghosted")
        e2 = HeritageEdge("n1", "n2", "produced")

        dag = GhostHeritageDAG(
            nodes={"n1": n1, "n1_ghost_0": g1, "n2": n2},
            edges=(e1, e2),
            root_id="n1",
        )

        assert dag.node_count == 3
        assert dag.edge_count == 2

    def test_repr_shows_counts(self) -> None:
        """repr() shows chosen and ghost counts."""
        now = datetime.now(timezone.utc)
        n1 = HeritageNode("n1", "chosen", "op1", now, 0)
        g1 = HeritageNode("g1", "ghost", "alt1", now, 0)

        dag = GhostHeritageDAG(
            nodes={"n1": n1, "g1": g1},
            edges=(),
            root_id="n1",
        )

        r = repr(dag)
        assert "chosen=1" in r
        assert "ghosts=1" in r


# =============================================================================
# GhostHeritageDAG Query Tests
# =============================================================================


class TestGhostHeritageDAGQueries:
    """Tests for DAG query methods."""

    def test_chosen_path_linear(self) -> None:
        """chosen_path() returns linear sequence for simple chain."""
        now = datetime.now(timezone.utc)
        n1 = HeritageNode("n1", "chosen", "op1", now, 0)
        n2 = HeritageNode("n2", "chosen", "op2", now, 1)
        n3 = HeritageNode("n3", "chosen", "op3", now, 2)

        e1 = HeritageEdge("n1", "n2", "produced")
        e2 = HeritageEdge("n2", "n3", "produced")

        dag = GhostHeritageDAG(
            nodes={"n1": n1, "n2": n2, "n3": n3},
            edges=(e1, e2),
            root_id="n1",
        )

        path = dag.chosen_path()
        assert path == ("n1", "n2", "n3")

    def test_chosen_path_excludes_ghosts(self) -> None:
        """chosen_path() does not include ghost nodes."""
        now = datetime.now(timezone.utc)
        n1 = HeritageNode("n1", "chosen", "op1", now, 0)
        g1 = HeritageNode("n1_ghost_0", "ghost", "alt1", now, 0)
        n2 = HeritageNode("n2", "chosen", "op2", now, 1)

        e1 = HeritageEdge("n1", "n1_ghost_0", "ghosted")
        e2 = HeritageEdge("n1", "n2", "produced")

        dag = GhostHeritageDAG(
            nodes={"n1": n1, "n1_ghost_0": g1, "n2": n2},
            edges=(e1, e2),
            root_id="n1",
        )

        path = dag.chosen_path()
        assert "n1_ghost_0" not in path
        assert path == ("n1", "n2")

    def test_ghost_paths_captures_all_ghosts(self) -> None:
        """ghost_paths() returns all ghost branches."""
        now = datetime.now(timezone.utc)
        n1 = HeritageNode("n1", "chosen", "op1", now, 0)
        g1 = HeritageNode("n1_ghost_0", "ghost", "alt1", now, 0)
        n2 = HeritageNode("n2", "chosen", "op2", now, 1)
        g2 = HeritageNode("n2_ghost_0", "deferred", "alt2", now, 1)

        e1 = HeritageEdge("n1", "n1_ghost_0", "ghosted")
        e2 = HeritageEdge("n1", "n2", "produced")
        e3 = HeritageEdge("n2", "n2_ghost_0", "deferred")

        dag = GhostHeritageDAG(
            nodes={"n1": n1, "n1_ghost_0": g1, "n2": n2, "n2_ghost_0": g2},
            edges=(e1, e2, e3),
            root_id="n1",
        )

        paths = dag.ghost_paths()
        assert len(paths) == 2
        assert ("n1", "n1_ghost_0") in paths
        assert ("n2", "n2_ghost_0") in paths

    def test_at_depth_returns_all_at_depth(self) -> None:
        """at_depth() returns all nodes at specified depth."""
        now = datetime.now(timezone.utc)
        n1 = HeritageNode("n1", "chosen", "op1", now, 0)
        g1 = HeritageNode("g1", "ghost", "alt1", now, 0)  # Same depth as n1
        n2 = HeritageNode("n2", "chosen", "op2", now, 1)

        dag = GhostHeritageDAG(
            nodes={"n1": n1, "g1": g1, "n2": n2},
            edges=(),
            root_id="n1",
        )

        depth_0 = dag.at_depth(0)
        depth_1 = dag.at_depth(1)
        depth_2 = dag.at_depth(2)

        assert len(depth_0) == 2  # n1 and g1
        assert len(depth_1) == 1  # n2
        assert len(depth_2) == 0

    def test_ghosts_of_returns_ghost_children(self) -> None:
        """ghosts_of() returns ghost nodes attached to a chosen node."""
        now = datetime.now(timezone.utc)
        n1 = HeritageNode("n1", "chosen", "op1", now, 0)
        g1 = HeritageNode("g1", "ghost", "alt1", now, 0)
        g2 = HeritageNode("g2", "deferred", "alt2", now, 0)
        n2 = HeritageNode("n2", "chosen", "op2", now, 1)

        e1 = HeritageEdge("n1", "g1", "ghosted")
        e2 = HeritageEdge("n1", "g2", "deferred")
        e3 = HeritageEdge("n1", "n2", "produced")

        dag = GhostHeritageDAG(
            nodes={"n1": n1, "g1": g1, "g2": g2, "n2": n2},
            edges=(e1, e2, e3),
            root_id="n1",
        )

        ghosts = dag.ghosts_of("n1")
        ghost_ids = {g.id for g in ghosts}

        assert len(ghosts) == 2
        assert "g1" in ghost_ids
        assert "g2" in ghost_ids
        assert "n2" not in ghost_ids

    def test_explorable_ghosts(self) -> None:
        """explorable_ghosts() returns only ghosts that can be explored."""
        now = datetime.now(timezone.utc)
        n1 = HeritageNode("n1", "chosen", "op1", now, 0)
        g1 = HeritageNode("g1", "ghost", "alt1", now, 0, explorable=False)
        g2 = HeritageNode("g2", "deferred", "alt2", now, 0, explorable=True)
        g3 = HeritageNode("g3", "ghost", "alt3", now, 0, explorable=True)

        dag = GhostHeritageDAG(
            nodes={"n1": n1, "g1": g1, "g2": g2, "g3": g3},
            edges=(),
            root_id="n1",
        )

        explorable = dag.explorable_ghosts()
        explorable_ids = {g.id for g in explorable}

        # Only g2 and g3 have explorable=True AND are ghost types
        assert "g1" not in explorable_ids
        assert "g2" in explorable_ids
        assert "g3" in explorable_ids

    def test_get_node(self) -> None:
        """get_node() retrieves node by ID."""
        now = datetime.now(timezone.utc)
        n1 = HeritageNode("n1", "chosen", "op1", now, 0)

        dag = GhostHeritageDAG(nodes={"n1": n1}, edges=(), root_id="n1")

        assert dag.get_node("n1") is n1
        assert dag.get_node("nonexistent") is None

    def test_parent_of(self) -> None:
        """parent_of() returns parent node."""
        now = datetime.now(timezone.utc)
        n1 = HeritageNode("n1", "chosen", "op1", now, 0)
        n2 = HeritageNode("n2", "chosen", "op2", now, 1)

        e1 = HeritageEdge("n1", "n2", "produced")

        dag = GhostHeritageDAG(
            nodes={"n1": n1, "n2": n2},
            edges=(e1,),
            root_id="n1",
        )

        assert dag.parent_of("n2") is n1
        assert dag.parent_of("n1") is None

    def test_children_of(self) -> None:
        """children_of() returns all child nodes."""
        now = datetime.now(timezone.utc)
        n1 = HeritageNode("n1", "chosen", "op1", now, 0)
        n2 = HeritageNode("n2", "chosen", "op2", now, 1)
        g1 = HeritageNode("g1", "ghost", "alt1", now, 0)

        e1 = HeritageEdge("n1", "n2", "produced")
        e2 = HeritageEdge("n1", "g1", "ghosted")

        dag = GhostHeritageDAG(
            nodes={"n1": n1, "n2": n2, "g1": g1},
            edges=(e1, e2),
            root_id="n1",
        )

        children = dag.children_of("n1")
        child_ids = {c.id for c in children}

        assert len(children) == 2
        assert "n2" in child_ids
        assert "g1" in child_ids


# =============================================================================
# DAG Integrity Tests
# =============================================================================


class TestGhostHeritageDAGIntegrity:
    """Tests for DAG integrity verification."""

    def test_empty_dag_is_valid(self) -> None:
        """Empty DAG passes integrity check."""
        dag = GhostHeritageDAG(nodes={}, edges=(), root_id="")
        valid, msg = dag.verify_integrity()
        assert valid is True

    def test_valid_dag_passes_integrity(self) -> None:
        """Well-formed DAG passes integrity check."""
        now = datetime.now(timezone.utc)
        n1 = HeritageNode("n1", "chosen", "op1", now, 0)
        n2 = HeritageNode("n2", "chosen", "op2", now, 1)

        e1 = HeritageEdge("n1", "n2", "produced")

        dag = GhostHeritageDAG(
            nodes={"n1": n1, "n2": n2},
            edges=(e1,),
            root_id="n1",
        )

        valid, msg = dag.verify_integrity()
        assert valid is True

    def test_missing_root_fails_integrity(self) -> None:
        """DAG with missing root fails integrity check."""
        now = datetime.now(timezone.utc)
        n1 = HeritageNode("n1", "chosen", "op1", now, 0)

        dag = GhostHeritageDAG(
            nodes={"n1": n1},
            edges=(),
            root_id="nonexistent",  # Root doesn't exist
        )

        valid, msg = dag.verify_integrity()
        assert valid is False
        assert "Root" in msg

    def test_orphan_edge_source_fails_integrity(self) -> None:
        """DAG with edge from nonexistent source fails integrity."""
        now = datetime.now(timezone.utc)
        n1 = HeritageNode("n1", "chosen", "op1", now, 0)

        e1 = HeritageEdge("nonexistent", "n1", "produced")

        dag = GhostHeritageDAG(
            nodes={"n1": n1},
            edges=(e1,),
            root_id="n1",
        )

        valid, msg = dag.verify_integrity()
        assert valid is False
        assert "source" in msg.lower()

    def test_orphan_edge_target_fails_integrity(self) -> None:
        """DAG with edge to nonexistent target fails integrity."""
        now = datetime.now(timezone.utc)
        n1 = HeritageNode("n1", "chosen", "op1", now, 0)

        e1 = HeritageEdge("n1", "nonexistent", "produced")

        dag = GhostHeritageDAG(
            nodes={"n1": n1},
            edges=(e1,),
            root_id="n1",
        )

        valid, msg = dag.verify_integrity()
        assert valid is False
        assert "target" in msg.lower()


# =============================================================================
# Builder Tests
# =============================================================================


class TestBuildHeritageDAG:
    """Tests for build_heritage_dag function."""

    def test_build_from_empty_monoid(self) -> None:
        """Building from empty monoid returns empty DAG."""
        monoid = TraceMonoid(traces=())
        dag = build_heritage_dag(monoid)

        assert dag.node_count == 0
        assert dag.root_id == ""

    def test_build_from_single_trace(self) -> None:
        """Building from single trace creates single-node DAG."""
        trace = make_trace("trace_0")
        monoid = TraceMonoid(traces=(trace,))

        dag = build_heritage_dag(monoid)

        assert dag.node_count == 1
        assert dag.root_id == "trace_0"
        assert dag.chosen_path() == ("trace_0",)

    def test_build_from_linear_chain(self) -> None:
        """Building from chain creates linear DAG."""
        monoid = make_linear_chain(length=3)
        dag = build_heritage_dag(monoid)

        assert dag.node_count == 3
        assert dag.edge_count == 2  # 2 produced edges
        assert dag.max_depth == 2

        path = dag.chosen_path()
        assert path == ("trace_0", "trace_1", "trace_2")

    def test_build_with_alternatives(self) -> None:
        """Building with alternatives creates ghost nodes."""
        monoid = make_chain_with_ghosts(length=2, ghosts_per_trace=2)
        dag = build_heritage_dag(monoid)

        # 2 chosen + 4 ghosts = 6 nodes
        assert dag.node_count == 6
        # 1 produced + 4 ghost edges = 5 edges
        assert dag.edge_count == 5

        # Ghost paths should include all 4 ghosts
        ghost_paths = dag.ghost_paths()
        assert len(ghost_paths) == 4

    def test_build_respects_max_depth(self) -> None:
        """Building respects max_depth parameter."""
        monoid = make_linear_chain(length=10)
        dag = build_heritage_dag(monoid, max_depth=3)

        # Only 3 nodes due to depth limit
        assert dag.node_count == 3
        assert dag.max_depth == 2

    def test_build_assigns_correct_depths(self) -> None:
        """Builder assigns correct depth to each node."""
        monoid = make_linear_chain(length=4)
        dag = build_heritage_dag(monoid)

        for i in range(4):
            node = dag.get_node(f"trace_{i}")
            assert node is not None
            assert node.depth == i

    def test_build_preserves_ghost_explorability(self) -> None:
        """Builder preserves could_revisit flag as explorable."""
        alt_explorable = make_ghost("alt1", could_revisit=True)
        alt_not_explorable = make_ghost("alt2", could_revisit=False)

        trace = make_trace(
            "trace_0",
            alternatives=(alt_explorable, alt_not_explorable),
        )
        monoid = TraceMonoid(traces=(trace,))

        dag = build_heritage_dag(monoid)

        ghost1 = dag.get_node("trace_0_ghost_0")
        ghost2 = dag.get_node("trace_0_ghost_1")

        assert ghost1 is not None
        assert ghost2 is not None
        assert ghost1.explorable is True
        assert ghost2.explorable is False

    def test_build_deferred_vs_ghosted_edge_types(self) -> None:
        """Builder uses correct edge types for explorable vs non-explorable."""
        alt_explorable = make_ghost("alt1", could_revisit=True)
        alt_not_explorable = make_ghost("alt2", could_revisit=False)

        trace = make_trace(
            "trace_0",
            alternatives=(alt_explorable, alt_not_explorable),
        )
        monoid = TraceMonoid(traces=(trace,))

        dag = build_heritage_dag(monoid)

        # Find edges to ghosts
        ghost_edges = [e for e in dag.edges if e.is_ghost_edge()]

        edge_types = {e.edge_type for e in ghost_edges}
        assert "deferred" in edge_types
        assert "ghosted" in edge_types

    def test_build_from_traces_convenience(self) -> None:
        """build_heritage_dag_from_traces is a convenient wrapper."""
        traces = [
            make_trace("t0"),
            make_trace("t1", parent_trace_id="t0"),
        ]
        dag = build_heritage_dag_from_traces(traces)

        assert dag.node_count == 2
        assert dag.chosen_path() == ("t0", "t1")

    def test_build_with_target_id(self) -> None:
        """Can build DAG targeting specific trace."""
        traces = [
            make_trace("t0"),
            make_trace("t1", parent_trace_id="t0"),
            make_trace("t2", parent_trace_id="t1"),
        ]
        monoid = TraceMonoid(traces=tuple(traces))

        # Target middle trace
        dag = build_heritage_dag(monoid, target_id="t1")

        # Should only include t0 and t1 (chain to t1)
        assert dag.chosen_path() == ("t0", "t1")


# =============================================================================
# Property-Based Tests
# =============================================================================


@st.composite
def trace_strategy(draw: st.DrawFn, depth: int = 0, parent_id: str | None = None) -> WiringTrace:
    """Generate a random trace."""
    trace_id = f"trace_{draw(st.uuids()).hex[:8]}"
    operation = draw(st.sampled_from(["seq", "par", "branch", "fix"]))

    # Generate 0-2 alternatives
    num_alts = draw(st.integers(min_value=0, max_value=2))
    alts = tuple(
        Alternative(
            operation=draw(st.sampled_from(["alt_a", "alt_b", "alt_c"])),
            inputs=("x",),
            reason_rejected=draw(st.text(min_size=3, max_size=20)),
            could_revisit=draw(st.booleans()),
        )
        for _ in range(num_alts)
    )

    return WiringTrace(
        trace_id=trace_id,
        timestamp=datetime.now(timezone.utc),
        operation=operation,
        inputs=("A", "B"),
        output=f"output_{trace_id}",
        context="test",
        alternatives=alts,
        parent_trace_id=parent_id,
    )


@st.composite
def trace_chain_strategy(draw: st.DrawFn) -> TraceMonoid:
    """Generate a chain of traces."""
    length = draw(st.integers(min_value=1, max_value=5))
    traces: list[WiringTrace] = []

    for _ in range(length):
        parent_id = traces[-1].trace_id if traces else None
        trace = draw(trace_strategy(parent_id=parent_id))
        traces.append(trace)

    return TraceMonoid(traces=tuple(traces))


class TestHeritageDAGLaws:
    """Property-based tests for DAG invariants."""

    @given(trace_chain_strategy())
    @settings(max_examples=30)
    def test_chosen_path_is_linear(self, monoid: TraceMonoid) -> None:
        """chosen_path forms a linear sequence (no branches)."""
        dag = build_heritage_dag(monoid)
        path = dag.chosen_path()

        # Path should have no duplicates
        assert len(path) == len(set(path))

        # Each node in path should be chosen
        for node_id in path:
            node = dag.get_node(node_id)
            assert node is not None
            assert node.is_chosen()

    @given(trace_chain_strategy())
    @settings(max_examples=30)
    def test_all_ghosts_have_parent(self, monoid: TraceMonoid) -> None:
        """Every ghost node has exactly one incoming edge from a chosen node."""
        dag = build_heritage_dag(monoid)

        for node_id, node in dag.nodes.items():
            if node.is_ghost():
                parent = dag.parent_of(node_id)
                assert parent is not None, f"Ghost {node_id} has no parent"
                assert parent.is_chosen(), f"Ghost {node_id} parent is not chosen"

    @given(trace_chain_strategy())
    @settings(max_examples=30)
    def test_depth_consistency(self, monoid: TraceMonoid) -> None:
        """Node depth = parent depth + 1 for all non-root nodes."""
        dag = build_heritage_dag(monoid)

        for node_id, node in dag.nodes.items():
            parent = dag.parent_of(node_id)
            if parent is not None:
                # Ghosts have same depth as parent (branch at same level)
                if node.is_ghost():
                    assert node.depth == parent.depth
                else:
                    assert node.depth == parent.depth + 1

    @given(trace_chain_strategy())
    @settings(max_examples=30)
    def test_ghost_count_matches_alternatives(self, monoid: TraceMonoid) -> None:
        """Number of ghost nodes equals total alternatives in chain."""
        dag = build_heritage_dag(monoid)

        # Count alternatives in monoid
        total_alts = sum(len(t.alternatives) for t in monoid.traces)

        # Count ghost nodes in DAG
        ghost_count = sum(1 for n in dag.nodes.values() if n.is_ghost())

        assert ghost_count == total_alts

    @given(trace_chain_strategy())
    @settings(max_examples=30)
    def test_dag_integrity_always_passes(self, monoid: TraceMonoid) -> None:
        """Built DAGs always pass integrity check."""
        dag = build_heritage_dag(monoid)
        valid, msg = dag.verify_integrity()
        assert valid is True, f"DAG integrity failed: {msg}"


# =============================================================================
# Integration Tests (Store)
# =============================================================================


class TestHeritageDAGStoreIntegration:
    """Integration tests with DifferanceStore."""

    @pytest.mark.asyncio
    async def test_store_heritage_dag(self) -> None:
        """DifferanceStore.heritage_dag() builds correct DAG."""
        from agents.differance.store import DifferanceStore

        store = DifferanceStore()

        # Create chain of traces
        t0 = make_trace("t0")
        t1 = make_trace("t1", parent_trace_id="t0")
        t2 = make_trace("t2", parent_trace_id="t1")

        await store.append(t0)
        await store.append(t1)
        await store.append(t2)

        # Build DAG
        dag = await store.heritage_dag("t2")

        assert dag.node_count == 3
        assert dag.chosen_path() == ("t0", "t1", "t2")

    @pytest.mark.asyncio
    async def test_store_heritage_dag_with_ghosts(self) -> None:
        """DifferanceStore.heritage_dag() includes ghost alternatives."""
        from agents.differance.store import DifferanceStore

        store = DifferanceStore()

        ghost = make_ghost("alt_op", reason="Not needed")
        t0 = make_trace("t0", alternatives=(ghost,))

        await store.append(t0)

        dag = await store.heritage_dag("t0")

        # Should have chosen + ghost
        assert dag.node_count == 2
        assert len(dag.ghost_paths()) == 1

    @pytest.mark.asyncio
    async def test_store_heritage_dag_nonexistent(self) -> None:
        """heritage_dag() returns empty DAG for nonexistent trace."""
        from agents.differance.store import DifferanceStore

        store = DifferanceStore()

        dag = await store.heritage_dag("nonexistent")

        assert dag.node_count == 0
        assert dag.root_id == ""

    @pytest.mark.asyncio
    async def test_round_trip_append_and_heritage(self) -> None:
        """Can append traces and retrieve heritage DAG."""
        from agents.differance.store import DifferanceStore

        store = DifferanceStore()

        # Build traces with alternatives
        alt1 = make_ghost("par", reason="Order matters", could_revisit=True)
        alt2 = make_ghost("branch", reason="Simpler", could_revisit=False)

        t0 = make_trace("t0", alternatives=(alt1,))
        t1 = make_trace("t1", parent_trace_id="t0", alternatives=(alt2,))

        await store.append(t0)
        await store.append(t1)

        # Get DAG
        dag = await store.heritage_dag("t1")

        # Verify structure
        assert dag.node_count == 4  # 2 chosen + 2 ghosts
        assert dag.chosen_path() == ("t0", "t1")

        # Verify ghost paths
        ghost_paths = dag.ghost_paths()
        assert len(ghost_paths) == 2

        # Verify explorability
        explorable = dag.explorable_ghosts()
        assert len(explorable) == 1  # Only alt1 is explorable
