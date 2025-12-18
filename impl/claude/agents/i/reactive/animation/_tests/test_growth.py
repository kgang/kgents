"""Tests for the Growth Engine - differential growth simulation.

Philosophy verification:
    - Nodes emerge and grow organically
    - Edges grow progressively from source to target
    - Forces create natural structure (attraction, repulsion, alignment)
    - Randomness prevents sterile uniformity
"""

import math

import pytest

from agents.i.reactive.animation.growth import (
    GrowthEdge,
    GrowthEngine,
    GrowthNode,
    GrowthRules,
)


class TestGrowthRules:
    """Test GrowthRules configuration."""

    def test_default_values(self) -> None:
        """Default rules should have reasonable values."""
        rules = GrowthRules()
        assert 0 <= rules.attraction <= 1
        assert 0 <= rules.repulsion <= 1
        assert 0 <= rules.alignment <= 1
        assert 0 <= rules.randomness <= 1
        assert rules.growth_rate > 0
        assert rules.min_distance > 0
        assert 0 <= rules.damping <= 1

    def test_organic_preset(self) -> None:
        """Organic preset should have high randomness."""
        rules = GrowthRules.organic()
        assert rules.randomness >= 0.15

    def test_crystalline_preset(self) -> None:
        """Crystalline preset should have low randomness."""
        rules = GrowthRules.crystalline()
        assert rules.randomness <= 0.1

    def test_fluid_preset(self) -> None:
        """Fluid preset should have high alignment."""
        rules = GrowthRules.fluid()
        assert rules.alignment >= 0.3


class TestGrowthNode:
    """Test GrowthNode operations."""

    def test_create_node(self) -> None:
        """Node should be created with position."""
        node = GrowthNode(id="a", position=(1.0, 2.0, 3.0))
        assert node.id == "a"
        assert node.position == (1.0, 2.0, 3.0)
        assert node.velocity == (0.0, 0.0, 0.0)

    def test_distance_to_self(self) -> None:
        """Distance to self should be zero."""
        node = GrowthNode(id="a", position=(1.0, 0.0, 0.0))
        assert node.distance_to(node) == 0.0

    def test_distance_to_other(self) -> None:
        """Distance to another node should be correct."""
        a = GrowthNode(id="a", position=(0.0, 0.0, 0.0))
        b = GrowthNode(id="b", position=(3.0, 4.0, 0.0))
        assert abs(a.distance_to(b) - 5.0) < 0.001

    def test_distance_to_point(self) -> None:
        """Distance to a point should be correct."""
        node = GrowthNode(id="a", position=(0.0, 0.0, 0.0))
        assert abs(node.distance_to_point((1.0, 0.0, 0.0)) - 1.0) < 0.001


class TestGrowthEdge:
    """Test GrowthEdge operations."""

    def test_create_edge(self) -> None:
        """Edge should be created with source and target."""
        edge = GrowthEdge(id="e", source_id="a", target_id="b")
        assert edge.id == "e"
        assert edge.source_id == "a"
        assert edge.target_id == "b"
        assert edge.progress == 0.0

    def test_is_complete(self) -> None:
        """Edge should be complete when progress >= 1."""
        edge = GrowthEdge(id="e", source_id="a", target_id="b", progress=0.5)
        assert not edge.is_complete

        edge.progress = 1.0
        assert edge.is_complete

        edge.progress = 1.5
        assert edge.is_complete


class TestGrowthEngine:
    """Test GrowthEngine simulation."""

    def test_create_empty(self) -> None:
        """Created engine should be empty."""
        engine = GrowthEngine.create()
        assert engine.node_count == 0
        assert engine.edge_count == 0
        assert engine.time == 0.0

    def test_create_with_rules(self) -> None:
        """Engine should accept custom rules."""
        rules = GrowthRules.organic()
        engine = GrowthEngine.create(rules=rules)
        assert engine.rules.randomness == rules.randomness

    def test_seed_creates_node(self) -> None:
        """Seeding should create a node at position."""
        engine = GrowthEngine.create()
        node_id = engine.seed((1.0, 2.0, 3.0))

        assert engine.node_count == 1
        node = engine.get_node(node_id)
        assert node is not None
        assert node.position == (1.0, 2.0, 3.0)

    def test_seed_with_custom_id(self) -> None:
        """Seeding should accept custom node ID."""
        engine = GrowthEngine.create()
        node_id = engine.seed((0, 0, 0), node_id="my_node")
        assert node_id == "my_node"

    def test_remove_node(self) -> None:
        """Removing node should decrease count."""
        engine = GrowthEngine.create()
        nid = engine.seed((0, 0, 0))
        assert engine.node_count == 1

        assert engine.remove_node(nid)
        assert engine.node_count == 0

    def test_remove_nonexistent_node(self) -> None:
        """Removing nonexistent node should return False."""
        engine = GrowthEngine.create()
        assert not engine.remove_node("nonexistent")

    def test_remove_node_removes_edges(self) -> None:
        """Removing a node should remove connected edges."""
        engine = GrowthEngine.create()
        a = engine.seed((0, 0, 0))
        b = engine.seed((1, 0, 0))
        engine.connect(a, b)
        assert engine.edge_count == 1

        engine.remove_node(a)
        assert engine.edge_count == 0

    def test_connect_creates_edge(self) -> None:
        """Connecting nodes should create an edge."""
        engine = GrowthEngine.create()
        a = engine.seed((0, 0, 0))
        b = engine.seed((1, 0, 0))

        edge_id = engine.connect(a, b)
        assert engine.edge_count == 1

        edge = engine.get_edge(edge_id)
        assert edge is not None
        assert edge.source_id == a
        assert edge.target_id == b
        assert edge.progress == 0.0

    def test_connect_nonexistent_fails(self) -> None:
        """Connecting nonexistent nodes should fail."""
        engine = GrowthEngine.create()
        a = engine.seed((0, 0, 0))

        with pytest.raises(KeyError):
            engine.connect(a, "nonexistent")

        with pytest.raises(KeyError):
            engine.connect("nonexistent", a)

    def test_disconnect(self) -> None:
        """Disconnecting should remove the edge."""
        engine = GrowthEngine.create()
        a = engine.seed((0, 0, 0))
        b = engine.seed((1, 0, 0))
        edge_id = engine.connect(a, b)

        assert engine.disconnect(edge_id)
        assert engine.edge_count == 0

    def test_disconnect_nonexistent(self) -> None:
        """Disconnecting nonexistent edge should return False."""
        engine = GrowthEngine.create()
        assert not engine.disconnect("nonexistent")


class TestGrowthSimulation:
    """Test growth simulation mechanics."""

    def test_step_advances_time(self) -> None:
        """Step should advance simulation time."""
        engine = GrowthEngine.create()
        engine.step(0.1)
        assert abs(engine.time - 0.1) < 0.001

    def test_step_grows_edges(self) -> None:
        """Step should increase edge progress."""
        engine = GrowthEngine.create()
        a = engine.seed((0, 0, 0))
        b = engine.seed((1, 0, 0))
        edge_id = engine.connect(a, b)

        edge = engine.get_edge(edge_id)
        assert edge is not None
        initial_progress = edge.progress

        # Multiple steps
        for _ in range(10):
            engine.step(0.1)

        assert edge.progress > initial_progress

    def test_edge_completes(self) -> None:
        """Edge should eventually complete."""
        # Use higher growth rate for faster test
        rules = GrowthRules(growth_rate=0.5)
        engine = GrowthEngine.create(rules=rules)
        a = engine.seed((0, 0, 0), fixed=True)
        b = engine.seed((1, 0, 0), fixed=True)
        edge_id = engine.connect(a, b)

        # Run until complete
        for _ in range(500):
            engine.step(0.016)
            edge = engine.get_edge(edge_id)
            if edge and edge.is_complete:
                break

        edge = engine.get_edge(edge_id)
        assert edge is not None
        assert edge.is_complete

    def test_fixed_node_doesnt_move(self) -> None:
        """Fixed nodes should not move."""
        engine = GrowthEngine.create()
        node_id = engine.seed((1.0, 2.0, 3.0), fixed=True)

        engine.relax(iterations=50)

        node = engine.get_node(node_id)
        assert node is not None
        assert node.position == (1.0, 2.0, 3.0)

    def test_attraction_toward_target(self) -> None:
        """Nodes should move toward their targets."""
        # Higher attraction, lower damping for more movement
        rules = GrowthRules(attraction=0.8, repulsion=0, randomness=0, damping=0.95)
        engine = GrowthEngine.create(rules=rules)

        node_id = engine.seed((0, 0, 0))
        engine.set_target(node_id, (1.0, 0, 0))

        # More iterations for convergence
        engine.relax(iterations=500)

        node = engine.get_node(node_id)
        assert node is not None
        # Should have moved closer to target (at least some progress)
        assert node.position[0] > 0.1

    def test_repulsion_separates_nodes(self) -> None:
        """Close nodes should be pushed apart by repulsion."""
        rules = GrowthRules(attraction=0, repulsion=0.5, randomness=0)
        engine = GrowthEngine.create(rules=rules)

        # Two very close nodes
        a = engine.seed((0, 0, 0))
        b = engine.seed((0.05, 0, 0))

        initial_dist = 0.05

        engine.relax(iterations=100)

        node_a = engine.get_node(a)
        node_b = engine.get_node(b)
        assert node_a is not None
        assert node_b is not None

        final_dist = node_a.distance_to(node_b)
        # Should have separated
        assert final_dist > initial_dist

    def test_relax_reduces_energy(self) -> None:
        """Relaxation should reduce kinetic energy."""
        engine = GrowthEngine.create()

        # Create several random nodes
        for i in range(5):
            engine.seed((i * 0.2, 0, 0))

        # Give initial velocity
        for node in engine.all_nodes():
            node.velocity = (0.5, 0.3, 0)

        initial_energy = engine.total_kinetic_energy()
        engine.relax(iterations=50)
        final_energy = engine.total_kinetic_energy()

        # Energy should decrease due to damping
        assert final_energy < initial_energy


class TestEdgePath:
    """Test edge path generation."""

    def test_get_edge_path_empty(self) -> None:
        """Edge with zero progress should have minimal path."""
        engine = GrowthEngine.create()
        a = engine.seed((0, 0, 0), fixed=True)
        b = engine.seed((1, 0, 0), fixed=True)
        edge_id = engine.connect(a, b)

        path = engine.get_edge_path(edge_id, segments=5)
        assert len(path) == 6  # segments + 1 points

        # All points should be at source (progress=0)
        for point in path:
            assert abs(point[0] - 0.0) < 0.1  # Near source

    def test_get_edge_path_complete(self) -> None:
        """Complete edge should have full path."""
        engine = GrowthEngine.create()
        a = engine.seed((0, 0, 0), fixed=True)
        b = engine.seed((1, 0, 0), fixed=True)
        edge_id = engine.connect(a, b)

        # Manually set edge to complete
        edge = engine.get_edge(edge_id)
        assert edge is not None
        edge.progress = 1.0

        path = engine.get_edge_path(edge_id, segments=5)

        # First point should be at source
        assert abs(path[0][0] - 0.0) < 0.1
        # Last point should be at target
        assert abs(path[-1][0] - 1.0) < 0.1

    def test_get_edge_path_partial(self) -> None:
        """Partial edge should have partial path."""
        engine = GrowthEngine.create()
        a = engine.seed((0, 0, 0), fixed=True)
        b = engine.seed((1, 0, 0), fixed=True)
        edge_id = engine.connect(a, b)

        edge = engine.get_edge(edge_id)
        assert edge is not None
        edge.progress = 0.5

        path = engine.get_edge_path(edge_id, segments=10)

        # Last point should be at midpoint
        assert abs(path[-1][0] - 0.5) < 0.1

    def test_get_edge_path_nonexistent(self) -> None:
        """Getting path for nonexistent edge should fail."""
        engine = GrowthEngine.create()
        with pytest.raises(KeyError):
            engine.get_edge_path("nonexistent")


class TestIterators:
    """Test iteration over nodes and edges."""

    def test_all_nodes(self) -> None:
        """Should iterate over all nodes."""
        engine = GrowthEngine.create()
        engine.seed((0, 0, 0))
        engine.seed((1, 0, 0))
        engine.seed((2, 0, 0))

        nodes = list(engine.all_nodes())
        assert len(nodes) == 3

    def test_all_edges(self) -> None:
        """Should iterate over all edges."""
        engine = GrowthEngine.create()
        a = engine.seed((0, 0, 0))
        b = engine.seed((1, 0, 0))
        c = engine.seed((2, 0, 0))

        engine.connect(a, b)
        engine.connect(b, c)

        edges = list(engine.all_edges())
        assert len(edges) == 2


class TestGrowToward:
    """Test the grow_toward convenience method."""

    def test_grow_toward_moves_node(self) -> None:
        """grow_toward should move node closer to target."""
        rules = GrowthRules(attraction=0.5, repulsion=0, randomness=0)
        engine = GrowthEngine.create(rules=rules)

        node_id = engine.seed((0, 0, 0))
        initial_pos = (0, 0, 0)

        engine.grow_toward(node_id, (1, 0, 0), iterations=50)

        node = engine.get_node(node_id)
        assert node is not None
        # Should have moved toward target
        assert node.position[0] > initial_pos[0]
