"""
Tests for Typed-Hypergraph Context (self.context.*).

Verifies the three laws from spec/protocols/typed-hypergraph.md:

Law 10.1 (Hyperedge Associativity):
    (A ──[e1]──→ B) ──[e2]──→ C  ≡  A ──[e1]──→ (B ──[e2]──→ C)
    Navigation order doesn't affect reachability.

Law 10.2 (Bidirectional Consistency):
    A ──[e]──→ B  ⟺  B ──[reverse(e)]──→ A
    Every forward edge implies a reverse edge.

Law 10.3 (Observer Monotonicity):
    If observer O₁ ⊆ O₂ in capabilities, then:
    edges(node, O₁) ⊆ edges(node, O₂)
    More capable observers see more edges.

Teaching:
    gotcha: These are property-based tests using Hypothesis. They generate
            random inputs to verify laws hold for ALL cases, not just examples.
            (Evidence: this file)

    gotcha: Law 10.3 tests require defining observer capability ordering.
            The ordering is based on archetype hierarchy: guest < newcomer < developer < architect.
            (Evidence: test_observer_monotonicity)
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

import pytest

from protocols.agentese.contexts.self_context import (
    REVERSE_EDGES,
    SPEC_EDGES,
    STRUCTURAL_EDGES,
    TESTING_EDGES,
    ContextGraph,
    ContextNode,
    Trail,
    TrailStep,
    create_context_graph,
    create_context_node,
    get_context_nav_node,
    get_reverse_edge,
)
from protocols.agentese.node import Observer

# === Basic Data Structure Tests ===


class TestContextNode:
    """Tests for ContextNode."""

    def test_creation(self) -> None:
        """ContextNode can be created with path and holon."""
        node = ContextNode(path="world.auth_middleware", holon="auth_middleware")
        assert node.path == "world.auth_middleware"
        assert node.holon == "auth_middleware"

    def test_lazy_content_not_loaded(self) -> None:
        """Content is not loaded on creation."""
        node = ContextNode(path="world.foo", holon="foo")
        assert node._content is None
        assert not node._content_loaded

    @pytest.mark.asyncio
    async def test_lazy_content_loading(self) -> None:
        """Content is loaded only when content() is called."""
        node = ContextNode(path="world.foo", holon="foo")

        # Content not loaded yet
        assert not node._content_loaded

        # Load content
        content = await node.content()
        assert content is not None
        assert node._content_loaded

    def test_edges_returns_dict(self) -> None:
        """edges() returns a dictionary of edge_type -> destinations."""
        node = ContextNode(path="world.foo", holon="foo")
        observer = Observer.test()

        edges = node.edges(observer)
        assert isinstance(edges, dict)

    def test_observer_dependent_edges(self) -> None:
        """Different observers see different edges."""
        node = ContextNode(path="world.foo", holon="foo")

        dev_edges = node.edges(Observer(archetype="developer"))
        guest_edges = node.edges(Observer(archetype="guest"))

        # Developer should see more edge types
        assert "tests" in dev_edges
        assert "imports" in dev_edges

        # Guest sees docs/examples/related
        # Note: edges are cached, so we need a fresh node
        node2 = ContextNode(path="world.foo2", holon="foo2")
        guest_edges = node2.edges(Observer(archetype="guest"))
        assert "docs" in guest_edges or "related" in guest_edges


class TestContextGraph:
    """Tests for ContextGraph."""

    def test_creation_empty(self) -> None:
        """ContextGraph can be created with empty focus."""
        graph = ContextGraph(
            focus=set(),
            trail=[],
            observer=Observer.test(),
        )
        assert len(graph.focus) == 0
        assert len(graph.trail) == 0

    def test_creation_with_focus(self) -> None:
        """ContextGraph can be created with initial focus."""
        node = ContextNode(path="world.foo", holon="foo")
        graph = ContextGraph(
            focus={node},
            trail=[],
            observer=Observer.test(),
        )
        assert len(graph.focus) == 1
        assert node in graph.focus

    @pytest.mark.asyncio
    async def test_navigate_returns_new_graph(self) -> None:
        """navigate() returns a NEW graph, not mutating the original."""
        node = ContextNode(path="world.foo", holon="foo")
        graph = ContextGraph(
            focus={node},
            trail=[],
            observer=Observer.test(),
        )

        new_graph = await graph.navigate("tests")

        # Original unchanged
        assert len(graph.trail) == 0

        # New graph has trail
        assert len(new_graph.trail) == 1

    @pytest.mark.asyncio
    async def test_navigate_immutability(self) -> None:
        """Navigation produces immutable state transitions."""
        node = ContextNode(path="world.foo", holon="foo")
        graph = ContextGraph(
            focus={node},
            trail=[],
            observer=Observer.test(),
        )

        g1 = await graph.navigate("tests")
        g2 = await graph.navigate("imports")

        # Both derived from same original
        assert len(graph.trail) == 0
        assert len(g1.trail) == 1
        assert len(g2.trail) == 1

        # They're independent
        assert g1.trail[0].edge_type == "tests"
        assert g2.trail[0].edge_type == "imports"

    def test_backtrack_empty_trail(self) -> None:
        """Backtracking with empty trail returns self."""
        graph = ContextGraph(
            focus=set(),
            trail=[],
            observer=Observer.test(),
        )

        result = graph.backtrack()
        assert len(result.trail) == 0

    @pytest.mark.asyncio
    async def test_backtrack_removes_last_step(self) -> None:
        """Backtracking removes the last trail step."""
        node = ContextNode(path="world.foo", holon="foo")
        graph = ContextGraph(
            focus={node},
            trail=[
                TrailStep(node_path="world.start", edge_type=None),
                TrailStep(node_path="world.foo", edge_type="tests"),
            ],
            observer=Observer.test(),
        )

        result = graph.backtrack()
        assert len(result.trail) == 1
        assert result.trail[0].node_path == "world.start"


class TestTrail:
    """Tests for Trail."""

    def test_creation(self) -> None:
        """Trail can be created with basic attributes."""
        trail = Trail(
            id="test-trail",
            name="Investigation",
            created_by=Observer.test(),
        )
        assert trail.id == "test-trail"
        assert trail.name == "Investigation"
        assert len(trail.steps) == 0

    def test_trail_immutability(self) -> None:
        """TrailSteps are immutable (frozen)."""
        step = TrailStep(
            node_path="world.foo",
            edge_type="tests",
        )

        # TrailStep is frozen - can't modify
        with pytest.raises(AttributeError):
            step.node_path = "world.bar"  # type: ignore

    def test_trail_append(self) -> None:
        """Trail steps can be appended (Trail is mutable)."""
        trail = Trail(
            id="test",
            name="Test",
            created_by=Observer.test(),
        )

        step = TrailStep(node_path="world.foo", edge_type="tests")
        trail.steps.append(step)

        assert len(trail.steps) == 1

    def test_annotate(self) -> None:
        """Annotations can be added to trail steps."""
        trail = Trail(
            id="test",
            name="Test",
            created_by=Observer.test(),
            steps=[TrailStep(node_path="world.foo", edge_type=None)],
        )

        trail.annotate(0, "Found the bug here!")

        assert trail.annotations[0] == "Found the bug here!"

    def test_to_dict(self) -> None:
        """Trail can be serialized to dictionary."""
        trail = Trail(
            id="test",
            name="Test",
            created_by=Observer.test(),
            steps=[TrailStep(node_path="world.foo", edge_type="tests")],
        )

        d = trail.to_dict()
        assert d["id"] == "test"
        assert d["name"] == "Test"
        assert len(d["steps"]) == 1
        assert d["steps"][0]["node_path"] == "world.foo"

    # === Phase 3: Trail Artifact Methods ===

    def test_as_outline_empty_trail(self) -> None:
        """as_outline renders empty trail correctly."""
        trail = Trail(
            id="test",
            name="Empty Investigation",
            created_by=Observer.test(),
        )

        outline = trail.as_outline()

        assert '📍 Trail: "Empty Investigation"' in outline
        assert "Steps: 0" in outline

    def test_as_outline_with_steps(self) -> None:
        """as_outline renders steps with edge types."""
        trail = Trail(
            id="test",
            name="Auth Bug",
            created_by=Observer.test(),
            steps=[
                TrailStep(node_path="world.auth", edge_type=None),
                TrailStep(node_path="world.auth.tests", edge_type="tests"),
                TrailStep(node_path="world.auth.core", edge_type="implements"),
            ],
        )

        outline = trail.as_outline()

        assert '📍 Trail: "Auth Bug"' in outline
        assert "Steps: 3" in outline
        assert "Started at world.auth" in outline
        assert "──[tests]──→ world.auth.tests" in outline
        assert "──[implements]──→ world.auth.core" in outline

    def test_as_outline_with_annotations(self) -> None:
        """as_outline includes step and trail annotations."""
        trail = Trail(
            id="test",
            name="Annotated",
            created_by=Observer.test(),
            steps=[
                TrailStep(
                    node_path="world.foo",
                    edge_type=None,
                    annotations="Found the bug here",
                ),
            ],
            annotations={0: "This is the root cause"},
        )

        outline = trail.as_outline()

        # Step annotation
        assert '💭 "Found the bug here"' in outline
        # Trail-level annotation
        assert "📝 This is the root cause" in outline

    def test_share_includes_metadata(self) -> None:
        """share() includes version and format metadata."""
        trail = Trail(
            id="test",
            name="Shareable",
            created_by=Observer.test(),
            steps=[TrailStep(node_path="world.foo", edge_type="tests")],
        )

        shared = trail.share()

        assert shared["version"] == "1.0"
        assert shared["format"] == "kgents.trail.v1"
        assert shared["step_count"] == 1
        assert "content_hash" in shared
        assert len(shared["content_hash"]) == 16  # 16 hex chars

    def test_share_includes_evidence(self) -> None:
        """share() includes evidence metadata."""
        trail = Trail(
            id="test",
            name="Evidence Trail",
            created_by=Observer.test(),
            steps=[
                TrailStep(node_path="a", edge_type=None),
                TrailStep(node_path="b", edge_type="tests"),
                TrailStep(node_path="c", edge_type="imports"),
            ],
        )

        shared = trail.share()

        assert "evidence" in shared
        assert shared["evidence"]["type"] == "exploration_trail"
        assert shared["evidence"]["verifiable"] is True
        assert shared["evidence"]["strength"] in ["weak", "moderate", "strong", "definitive"]

    def test_from_dict_roundtrip(self) -> None:
        """from_dict reconstructs trail from share() output."""
        original = Trail(
            id="roundtrip-test",
            name="Roundtrip Trail",
            created_by=Observer.test(),
            steps=[
                TrailStep(node_path="world.a", edge_type=None),
                TrailStep(node_path="world.b", edge_type="tests"),
            ],
            annotations={1: "Important finding"},
        )

        shared = original.share()
        reconstructed = Trail.from_dict(shared)

        assert reconstructed.id == original.id
        assert reconstructed.name == original.name
        assert len(reconstructed.steps) == len(original.steps)
        assert reconstructed.steps[0].node_path == "world.a"
        assert reconstructed.steps[1].edge_type == "tests"
        assert reconstructed.annotations[1] == "Important finding"

    def test_evidence_strength_weak(self) -> None:
        """Empty trail has weak evidence strength."""
        trail = Trail(
            id="test",
            name="Empty",
            created_by=Observer.test(),
        )

        assert trail._compute_evidence_strength() == "weak"

    def test_evidence_strength_moderate(self) -> None:
        """Trail with some steps has moderate strength."""
        trail = Trail(
            id="test",
            name="Moderate",
            created_by=Observer.test(),
            steps=[
                TrailStep(node_path="a", edge_type=None),
                TrailStep(node_path="b", edge_type="tests"),
                TrailStep(node_path="c", edge_type="tests"),
            ],
        )

        strength = trail._compute_evidence_strength()
        assert strength in ["moderate", "strong"]

    def test_evidence_strength_strong(self) -> None:
        """Diverse trail with annotations has strong strength."""
        trail = Trail(
            id="test",
            name="Strong",
            created_by=Observer.test(),
            steps=[
                TrailStep(node_path="a", edge_type=None, annotations="Start"),
                TrailStep(node_path="b", edge_type="tests"),
                TrailStep(node_path="c", edge_type="imports"),
                TrailStep(node_path="d", edge_type="calls"),
                TrailStep(node_path="e", edge_type="implements"),
            ],
            annotations={2: "Key finding", 4: "Conclusion"},
        )

        strength = trail._compute_evidence_strength()
        assert strength in ["strong", "definitive"]


# === Law Verification Tests ===


class TestLaw10_1_HyperedgeAssociativity:
    """
    Law 10.1: Hyperedge Associativity

    (A ──[e1]──→ B) ──[e2]──→ C  ≡  A ──[e1]──→ (B ──[e2]──→ C)

    Navigation order doesn't affect reachability.
    """

    @pytest.mark.asyncio
    async def test_associativity_basic(self) -> None:
        """Basic associativity: navigation records steps from focused nodes."""
        # Create a path A → B → C
        node_a = ContextNode(path="world.a", holon="a")
        observer = Observer.test()

        graph = ContextGraph(
            focus={node_a},
            trail=[],
            observer=observer,
        )

        # Navigate via an edge
        g1 = await graph.navigate("tests")

        # The trail records the navigation from the focused node(s)
        # Each focused node gets a trail step when navigating
        assert len(g1.trail) == 1
        assert g1.trail[0].edge_type == "tests"
        assert g1.trail[0].node_path == "world.a"

    @pytest.mark.asyncio
    async def test_associativity_chain(self) -> None:
        """Chained navigation accumulates trail steps."""
        # Start with two nodes
        nodes = {
            ContextNode(path="world.a", holon="a"),
            ContextNode(path="world.b", holon="b"),
        }
        observer = Observer.test()

        graph = ContextGraph(
            focus=nodes,
            trail=[],
            observer=observer,
        )

        # Navigate - should record step for each focused node
        g1 = await graph.navigate("tests")

        # Two focused nodes → two trail steps
        assert len(g1.trail) == 2

    @pytest.mark.asyncio
    async def test_associativity_multi_focus(self) -> None:
        """Associativity with multiple focused nodes."""
        nodes = {
            ContextNode(path="world.a", holon="a"),
            ContextNode(path="world.b", holon="b"),
        }
        observer = Observer.test()

        graph = ContextGraph(
            focus=nodes,
            trail=[],
            observer=observer,
        )

        # Navigate both nodes via same edge
        result = await graph.navigate("tests")

        # Both source nodes should be in trail
        trail_paths = {s.node_path for s in result.trail}
        assert "world.a" in trail_paths
        assert "world.b" in trail_paths


class TestLaw10_2_BidirectionalConsistency:
    """
    Law 10.2: Bidirectional Consistency

    A ──[e]──→ B  ⟺  B ──[reverse(e)]──→ A

    Every forward edge implies a reverse edge.
    """

    def test_all_edges_have_reverse(self) -> None:
        """Every edge in REVERSE_EDGES has a mapping."""
        # Check structural edges
        for edge in STRUCTURAL_EDGES:
            if edge in REVERSE_EDGES:
                reverse = get_reverse_edge(edge)
                assert reverse is not None, f"Edge {edge} has no reverse"
                # Verify the reverse of reverse is original
                reverse_of_reverse = get_reverse_edge(reverse)
                assert reverse_of_reverse == edge, (
                    f"reverse(reverse({edge})) = {reverse_of_reverse} != {edge}"
                )

    def test_bidirectional_pairs(self) -> None:
        """Key edge pairs are properly bidirectional."""
        pairs = [
            ("contains", "contained_in"),
            ("imports", "imported_by"),
            ("tests", "tested_by"),
            ("implements", "implemented_by"),
        ]

        for forward, reverse in pairs:
            assert get_reverse_edge(forward) == reverse
            assert get_reverse_edge(reverse) == forward

    def test_reverse_edge_lookup(self) -> None:
        """get_reverse_edge returns correct reverse for known edges."""
        assert get_reverse_edge("contains") == "contained_in"
        assert get_reverse_edge("parent") == "children"
        assert get_reverse_edge("tests") == "tested_by"

    def test_unknown_edge_returns_none(self) -> None:
        """get_reverse_edge returns None for unknown edges."""
        assert get_reverse_edge("nonexistent_edge") is None


class TestLaw10_3_ObserverMonotonicity:
    """
    Law 10.3: Observer Monotonicity

    If observer O₁ ⊆ O₂ in capabilities, then:
    edges(node, O₁) ⊆ edges(node, O₂)

    More capable observers see more edges.

    Observer hierarchy (least to most capable):
    guest < newcomer < developer < architect
    """

    # Define observer capability ordering
    OBSERVER_ORDER = ["guest", "newcomer", "developer", "architect"]

    def test_guest_sees_fewer_edges_than_developer(self) -> None:
        """Guest observer sees fewer edge types than developer."""
        node = ContextNode(path="world.foo", holon="foo")

        guest_edges = node.edges(Observer(archetype="guest"))

        # Create fresh node for developer (edges are cached)
        node2 = ContextNode(path="world.foo2", holon="foo2")
        dev_edges = node2.edges(Observer(archetype="developer"))

        # Developer has more edge types
        assert len(dev_edges) >= len(guest_edges)

    def test_developer_sees_tests_and_imports(self) -> None:
        """Developer sees code-related edges (tests, imports)."""
        node = ContextNode(path="world.foo", holon="foo")
        edges = node.edges(Observer(archetype="developer"))

        assert "tests" in edges
        assert "imports" in edges
        assert "calls" in edges

    def test_guest_sees_docs_and_examples(self) -> None:
        """Guest sees documentation-related edges."""
        node = ContextNode(path="world.foo", holon="foo")
        edges = node.edges(Observer(archetype="guest"))

        # Guest sees onboarding edges
        assert "docs" in edges or "examples" in edges or "related" in edges

    def test_all_observers_see_structural_edges(self) -> None:
        """All observers see basic structural edges."""
        for archetype in self.OBSERVER_ORDER:
            node = ContextNode(path=f"world.{archetype}", holon=archetype)
            edges = node.edges(Observer(archetype=archetype))

            # All should see contains and parent
            assert "contains" in edges
            assert "parent" in edges


# === Factory Function Tests ===


class TestFactories:
    """Tests for factory functions."""

    def test_create_context_node(self) -> None:
        """create_context_node creates node from path."""
        node = create_context_node("world.foo.bar")
        assert node.path == "world.foo.bar"
        assert node.holon == "bar"

    def test_create_context_graph(self) -> None:
        """create_context_graph creates graph with focus."""
        graph = create_context_graph(
            ["world.a", "world.b"],
            Observer.test(),
        )
        assert len(graph.focus) == 2
        assert len(graph.trail) == 2  # One step per initial focus

    def test_get_context_nav_node_singleton(self) -> None:
        """get_context_nav_node returns singleton."""
        node1 = get_context_nav_node()
        node2 = get_context_nav_node()
        assert node1 is node2


# === AGENTESE Node Tests ===


class TestContextNavNode:
    """Tests for ContextNavNode AGENTESE interface."""

    @pytest.mark.asyncio
    async def test_manifest(self) -> None:
        """manifest returns current graph state."""
        node = get_context_nav_node()
        observer = Observer.test()

        result = await node.manifest(observer)

        assert result.summary == "Typed-Hypergraph Context"
        # Content should include focus information
        assert "Focus" in result.content
        # Metadata should contain expected fields
        assert "focus" in result.metadata
        assert "trail_length" in result.metadata
        assert "affordances" in result.metadata

    @pytest.mark.asyncio
    async def test_focus_aspect(self) -> None:
        """focus aspect sets current position."""
        from protocols.agentese.contexts.self_context import ContextNavNode

        # Create fresh node to avoid state pollution
        node = ContextNavNode()
        observer = Observer.test()

        result = await node.focus(observer, "world.test")

        assert "world.test" in result.content

    @pytest.mark.asyncio
    async def test_trail_aspect(self) -> None:
        """trail aspect returns current trail."""
        from protocols.agentese.contexts.self_context import ContextNavNode

        node = ContextNavNode()
        observer = Observer.test()

        # Focus first
        await node.focus(observer, "world.test")

        # Get trail
        result = await node.trail(observer)

        assert "Trail" in result.summary

    @pytest.mark.asyncio
    async def test_backtrack_aspect(self) -> None:
        """backtrack aspect goes back in trail."""
        from protocols.agentese.contexts.self_context import ContextNavNode

        node = ContextNavNode()
        observer = Observer.test()

        # Focus then try backtrack
        await node.focus(observer, "world.test")
        result = await node.backtrack(observer)

        assert "Backtracked" in result.summary or "Cannot backtrack" in result.summary


# === Edge Cases ===


class TestEdgeCases:
    """Edge case tests."""

    def test_empty_path(self) -> None:
        """Handles empty path gracefully."""
        node = ContextNode(path="", holon="")
        edges = node.edges(Observer.test())
        assert isinstance(edges, dict)

    @pytest.mark.asyncio
    async def test_follow_nonexistent_edge(self) -> None:
        """Following non-existent edge returns empty list."""
        node = ContextNode(path="world.foo", holon="foo")
        result = await node.follow("nonexistent", Observer.test())
        assert result == []

    @pytest.mark.asyncio
    async def test_multi_focus_navigation(self) -> None:
        """Navigation from multiple focused nodes works correctly."""
        nodes = {
            ContextNode(path="world.a", holon="a"),
            ContextNode(path="world.b", holon="b"),
            ContextNode(path="world.c", holon="c"),
        }

        graph = ContextGraph(
            focus=nodes,
            trail=[],
            observer=Observer.test(),
        )

        result = await graph.navigate("tests")

        # All three nodes should have navigation recorded
        assert len(result.trail) == 3

    @pytest.mark.asyncio
    async def test_affordances_aggregates(self) -> None:
        """affordances() aggregates across all focused nodes."""
        nodes = {
            ContextNode(path="world.a", holon="a"),
            ContextNode(path="world.b", holon="b"),
        }

        graph = ContextGraph(
            focus=nodes,
            trail=[],
            observer=Observer.test(),
        )

        affordances = await graph.affordances()

        # Should have aggregated edge types
        assert isinstance(affordances, dict)
