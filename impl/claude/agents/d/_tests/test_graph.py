"""Tests for GraphAgent - Relational Lattice foundation."""

import tempfile
from pathlib import Path

import pytest
import pytest_asyncio
from agents.d.errors import NodeNotFoundError
from agents.d.graph import (
    Edge,
    EdgeKind,
    GraphAgent,
)


class TestGraphAgentBasics:
    """Basic GraphAgent operations."""

    @pytest.fixture
    def agent(self) -> GraphAgent:
        """Create a test graph agent."""
        return GraphAgent()

    async def test_add_and_get_node(self, agent) -> None:
        """Test adding and retrieving nodes."""
        await agent.add_node("test1", {"name": "Test"})

        node = await agent.get_node("test1")
        assert node is not None
        assert node.id == "test1"
        assert node.state == {"name": "Test"}

    async def test_node_exists(self, agent) -> None:
        """Test node existence check."""
        assert await agent.node_exists("test1") is False
        await agent.add_node("test1", "state")
        assert await agent.node_exists("test1") is True

    async def test_delete_node(self, agent) -> None:
        """Test deleting nodes."""
        await agent.add_node("test1", "state")
        assert await agent.delete_node("test1") is True
        assert await agent.get_node("test1") is None
        assert await agent.delete_node("test1") is False  # Already deleted

    async def test_list_nodes(self, agent) -> None:
        """Test listing all nodes."""
        await agent.add_node("a", "A")
        await agent.add_node("b", "B")
        await agent.add_node("c", "C")

        nodes = await agent.list_nodes()
        assert set(nodes) == {"a", "b", "c"}

    async def test_load_returns_all_nodes(self, agent) -> None:
        """Test that load returns all nodes."""
        await agent.add_node("test1", "State1")
        await agent.add_node("test2", "State2")

        nodes = await agent.load()
        assert len(nodes) == 2
        assert "test1" in nodes
        assert "test2" in nodes

    async def test_history_returns_states(self, agent) -> None:
        """Test history returns states in reverse order."""
        await agent.add_node("test1", "First")
        await agent.add_node("test2", "Second")

        history = await agent.history()
        assert history == ["Second", "First"]

    async def test_save_creates_node(self, agent) -> None:
        """Test save creates node with auto ID."""
        node_id = await agent.save("Test State")
        assert node_id is not None

        node = await agent.get_node(node_id)
        assert node.state == "Test State"


class TestGraphAgentEdges:
    """Edge operations."""

    @pytest_asyncio.fixture
    async def agent_with_nodes(self):
        """Create agent with test nodes."""
        agent = GraphAgent()
        await agent.add_node("parent", "Parent")
        await agent.add_node("child1", "Child 1")
        await agent.add_node("child2", "Child 2")
        return agent

    async def test_add_edge(self, agent_with_nodes) -> None:
        """Test adding edges between nodes."""
        agent = agent_with_nodes

        await agent.add_edge("child1", EdgeKind.IS_A, "parent")

        edges = await agent.get_edges("child1", direction="out")
        assert len(edges) == 1
        assert edges[0].kind == EdgeKind.IS_A
        assert edges[0].target == "parent"

    async def test_add_edge_missing_source_raises(self, agent_with_nodes) -> None:
        """Test that adding edge with missing source raises error."""
        agent = agent_with_nodes

        with pytest.raises(NodeNotFoundError, match="Source"):
            await agent.add_edge("nonexistent", EdgeKind.IS_A, "parent")

    async def test_add_edge_missing_target_raises(self, agent_with_nodes) -> None:
        """Test that adding edge with missing target raises error."""
        agent = agent_with_nodes

        with pytest.raises(NodeNotFoundError, match="Target"):
            await agent.add_edge("child1", EdgeKind.IS_A, "nonexistent")

    async def test_bidirectional_edge(self, agent_with_nodes) -> None:
        """Test bidirectional edges."""
        agent = agent_with_nodes

        await agent.add_edge(
            "child1", EdgeKind.RELATED_TO, "child2", bidirectional=True
        )

        edges1 = await agent.get_edges("child1", direction="out")
        edges2 = await agent.get_edges("child2", direction="out")

        assert any(e.target == "child2" for e in edges1)
        assert any(e.target == "child1" for e in edges2)

    async def test_get_edges_by_direction(self, agent_with_nodes) -> None:
        """Test getting edges by direction."""
        agent = agent_with_nodes

        await agent.add_edge("child1", EdgeKind.IS_A, "parent")
        await agent.add_edge("child2", EdgeKind.IS_A, "child1")  # child2 -> child1

        # Outgoing from child1
        out_edges = await agent.get_edges("child1", direction="out")
        assert len(out_edges) == 1
        assert out_edges[0].target == "parent"

        # Incoming to child1
        in_edges = await agent.get_edges("child1", direction="in")
        assert len(in_edges) == 1
        assert in_edges[0].source == "child2"

        # Both directions
        both_edges = await agent.get_edges("child1", direction="both")
        assert len(both_edges) == 2

    async def test_get_edges_by_kind(self, agent_with_nodes) -> None:
        """Test filtering edges by kind."""
        agent = agent_with_nodes

        await agent.add_edge("child1", EdgeKind.IS_A, "parent")
        await agent.add_edge("child1", EdgeKind.USES, "child2")

        is_a_edges = await agent.get_edges("child1", kind=EdgeKind.IS_A)
        assert len(is_a_edges) == 1
        assert is_a_edges[0].kind == EdgeKind.IS_A

    async def test_remove_edge(self, agent_with_nodes) -> None:
        """Test removing edges."""
        agent = agent_with_nodes

        await agent.add_edge("child1", EdgeKind.IS_A, "parent")
        assert await agent.remove_edge("child1", EdgeKind.IS_A, "parent") is True

        edges = await agent.get_edges("child1", direction="out")
        assert len(edges) == 0

    async def test_delete_node_removes_edges(self, agent_with_nodes) -> None:
        """Test that deleting node removes connected edges."""
        agent = agent_with_nodes

        await agent.add_edge("child1", EdgeKind.IS_A, "parent")
        await agent.add_edge("child2", EdgeKind.IS_A, "child1")

        await agent.delete_node("child1")

        # child2's edge should be cleaned up
        edges = await agent.get_edges("child2", direction="out")
        assert len(edges) == 0


class TestLatticeOperations:
    """Lattice operations: meet, join, entails."""

    @pytest_asyncio.fixture
    async def taxonomy(self):
        """Create a simple taxonomy (ontology).

        Structure:
            Thing
            ├── Animal
            │   ├── Dog
            │   └── Cat
            └── Vehicle
                ├── Car
                └── Bike
        """
        agent = GraphAgent()

        # Add nodes
        await agent.add_node("thing", "Thing")
        await agent.add_node("animal", "Animal")
        await agent.add_node("vehicle", "Vehicle")
        await agent.add_node("dog", "Dog")
        await agent.add_node("cat", "Cat")
        await agent.add_node("car", "Car")
        await agent.add_node("bike", "Bike")

        # Add IS_A relationships (child -> parent)
        await agent.add_edge("animal", EdgeKind.IS_A, "thing")
        await agent.add_edge("vehicle", EdgeKind.IS_A, "thing")
        await agent.add_edge("dog", EdgeKind.IS_A, "animal")
        await agent.add_edge("cat", EdgeKind.IS_A, "animal")
        await agent.add_edge("car", EdgeKind.IS_A, "vehicle")
        await agent.add_edge("bike", EdgeKind.IS_A, "vehicle")

        return agent

    async def test_entails_direct(self, taxonomy) -> None:
        """Test direct entailment."""
        # Dog IS_A Animal
        assert await taxonomy.entails("dog", "animal") is True
        # Animal IS_A Thing
        assert await taxonomy.entails("animal", "thing") is True

    async def test_entails_transitive(self, taxonomy) -> None:
        """Test transitive entailment."""
        # Dog IS_A Thing (via Animal)
        assert await taxonomy.entails("dog", "thing") is True

    async def test_entails_not_related(self, taxonomy) -> None:
        """Test non-entailment."""
        # Dog is not a Vehicle
        assert await taxonomy.entails("dog", "vehicle") is False
        # Car is not an Animal
        assert await taxonomy.entails("car", "animal") is False

    async def test_entails_self(self, taxonomy) -> None:
        """Test self-entailment."""
        assert await taxonomy.entails("dog", "dog") is True

    async def test_meet_siblings(self, taxonomy) -> None:
        """Test meet (greatest common ancestor) of siblings."""
        # Dog and Cat both are Animals
        # Meet finds common ancestors - both "animal" and "thing" are valid
        meet = await taxonomy.meet("dog", "cat")
        assert meet in ("animal", "thing")

    async def test_meet_cousins(self, taxonomy) -> None:
        """Test meet of cousins."""
        # Dog and Car meet at Thing
        meet = await taxonomy.meet("dog", "car")
        assert meet == "thing"

    async def test_meet_no_common_ancestor(self) -> None:
        """Test meet when no common ancestor."""
        agent = GraphAgent()
        await agent.add_node("a", "A")
        await agent.add_node("b", "B")

        meet = await agent.meet("a", "b")
        assert meet is None

    async def test_compare_below(self, taxonomy) -> None:
        """Test compare when one is below the other."""
        result = await taxonomy.compare("dog", "animal")
        assert result == "a ≤ b"

    async def test_compare_above(self, taxonomy) -> None:
        """Test compare when one is above the other."""
        result = await taxonomy.compare("animal", "dog")
        assert result == "b ≤ a"

    async def test_compare_equal(self, taxonomy) -> None:
        """Test compare when equal."""
        result = await taxonomy.compare("dog", "dog")
        assert result == "a = b"

    async def test_compare_incomparable(self, taxonomy) -> None:
        """Test compare when incomparable."""
        result = await taxonomy.compare("dog", "car")
        assert result == "incomparable"


class TestProvenanceOperations:
    """Provenance tracking: lineage, descendants."""

    @pytest_asyncio.fixture
    async def derivation_chain(self):
        """Create a derivation chain.

        v1 -> v2 -> v3 -> v4
        """
        agent = GraphAgent()

        await agent.add_node("v1", "Version 1")
        await agent.add_node("v2", "Version 2")
        await agent.add_node("v3", "Version 3")
        await agent.add_node("v4", "Version 4")

        await agent.add_edge("v2", EdgeKind.DERIVES_FROM, "v1")
        await agent.add_edge("v3", EdgeKind.DERIVES_FROM, "v2")
        await agent.add_edge("v4", EdgeKind.DERIVES_FROM, "v3")

        return agent

    async def test_lineage(self, derivation_chain) -> None:
        """Test lineage (ancestors)."""
        lineage = await derivation_chain.lineage("v4")
        assert lineage == ["v3", "v2", "v1"]

    async def test_lineage_root(self, derivation_chain) -> None:
        """Test lineage of root has no ancestors."""
        lineage = await derivation_chain.lineage("v1")
        assert lineage == []

    async def test_descendants(self, derivation_chain) -> None:
        """Test descendants."""
        desc = await derivation_chain.descendants("v1")
        assert set(desc) == {"v2", "v3", "v4"}

    async def test_descendants_leaf(self, derivation_chain) -> None:
        """Test descendants of leaf has none."""
        desc = await derivation_chain.descendants("v4")
        assert desc == []

    async def test_derivation_path(self, derivation_chain) -> None:
        """Test finding derivation path."""
        path = await derivation_chain.derivation_path("v1", "v4")
        assert path is None  # v1 can't reach v4 (edges go the other way)

        # But v4 can reach v1
        path = await derivation_chain.derivation_path("v4", "v1")
        assert path == ["v4", "v3", "v2", "v1"]


class TestTraversalOperations:
    """Graph traversal operations."""

    @pytest_asyncio.fixture
    async def connected_graph(self):
        """Create a connected graph."""
        agent = GraphAgent()

        await agent.add_node("a", "A")
        await agent.add_node("b", "B")
        await agent.add_node("c", "C")
        await agent.add_node("d", "D")

        await agent.add_edge("a", EdgeKind.RELATED_TO, "b")
        await agent.add_edge("b", EdgeKind.RELATED_TO, "c")
        await agent.add_edge("c", EdgeKind.RELATED_TO, "d")

        return agent

    async def test_traverse(self, connected_graph) -> None:
        """Test graph traversal."""
        subgraph = await connected_graph.traverse("a", depth=2)

        assert "a" in subgraph.nodes
        assert "b" in subgraph.nodes
        assert "c" in subgraph.nodes
        assert len(subgraph.edges) >= 2

    async def test_traverse_depth_limit(self, connected_graph) -> None:
        """Test traversal respects depth limit."""
        subgraph = await connected_graph.traverse("a", depth=1)

        assert "a" in subgraph.nodes
        assert "b" in subgraph.nodes
        assert "c" not in subgraph.nodes  # Too far

    async def test_find_path(self, connected_graph) -> None:
        """Test finding shortest path."""
        path = await connected_graph.find_path("a", "c")

        assert path is not None
        assert len(path) == 2
        assert path[0].source == "a"
        assert path[-1].target == "c"

    async def test_find_path_no_route(self, connected_graph) -> None:
        """Test finding path when no route exists."""
        # Add isolated node
        await connected_graph.add_node("isolated", "Isolated")

        path = await connected_graph.find_path("a", "isolated")
        assert path is None

    async def test_connected_components(self) -> None:
        """Test finding connected components."""
        agent = GraphAgent()

        # Component 1
        await agent.add_node("a1", "A1")
        await agent.add_node("a2", "A2")
        await agent.add_edge("a1", EdgeKind.RELATED_TO, "a2")

        # Component 2 (isolated)
        await agent.add_node("b1", "B1")
        await agent.add_node("b2", "B2")
        await agent.add_edge("b1", EdgeKind.RELATED_TO, "b2")

        components = await agent.connected_components()

        assert len(components) == 2
        component_ids = [frozenset(c) for c in components]
        assert frozenset({"a1", "a2"}) in component_ids
        assert frozenset({"b1", "b2"}) in component_ids


class TestGraphAgentPersistence:
    """Persistence tests."""

    async def test_persistence_round_trip(self) -> None:
        """Test save and load from disk."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "graph.json"

            # Create and populate
            agent1 = GraphAgent(persistence_path=path)
            await agent1.add_node("test1", "State1")
            await agent1.add_node("test2", "State2")
            await agent1.add_edge("test1", EdgeKind.IS_A, "test2")

            # Create new instance from same path
            agent2 = GraphAgent(persistence_path=path)

            # Should have loaded data
            nodes = await agent2.load()
            assert len(nodes) == 2

            edges = await agent2.get_edges("test1", direction="out")
            assert len(edges) == 1
            assert edges[0].kind == EdgeKind.IS_A


class TestEdgeKind:
    """Tests for EdgeKind enum."""

    def test_all_edge_kinds_defined(self) -> None:
        """Test all expected edge kinds exist."""
        assert EdgeKind.IS_A.value == "is_a"
        assert EdgeKind.HAS_A.value == "has_a"
        assert EdgeKind.USES.value == "uses"
        assert EdgeKind.DERIVES_FROM.value == "derives_from"
        assert EdgeKind.CONTRADICTS.value == "contradicts"
        assert EdgeKind.SYNTHESIZES.value == "synthesizes"
        assert EdgeKind.RELATED_TO.value == "related_to"

    def test_edge_reverse(self) -> None:
        """Test Edge reverse method."""
        edge = Edge(
            source="a",
            kind=EdgeKind.IS_A,
            target="b",
            metadata={"key": "value"},
        )

        reversed_edge = edge.reverse()
        assert reversed_edge.source == "b"
        assert reversed_edge.target == "a"
        assert reversed_edge.kind == EdgeKind.IS_A
        assert reversed_edge.metadata == {"key": "value"}
