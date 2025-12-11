"""Tests for VectorAgent - Semantic Manifold foundation."""

import tempfile
from pathlib import Path

import pytest

# Skip entire module if numpy not available
try:
    import numpy as np
except ImportError:
    pytest.skip("numpy not installed", allow_module_level=True)

from agents.d.errors import SemanticError, VoidNotFoundError
from agents.d.vector import (
    DistanceMetric,
    Point,
    VectorAgent,
    Void,
)


class TestVectorAgentBasics:
    """Basic VectorAgent operations."""

    @pytest.fixture
    def agent(self) -> VectorAgent:
        """Create a test vector agent."""
        return VectorAgent(dimension=4)

    @pytest.fixture
    def embedder(self):
        """Simple hash-based embedder for testing."""

        def embed(text: str) -> np.ndarray:
            # Deterministic embedding based on text
            np.random.seed(hash(text) % 2**32)
            return np.random.randn(4).astype(np.float32)

        return embed

    async def test_add_and_get(self, agent) -> None:
        """Test adding and retrieving entries."""
        embedding = np.array([1.0, 0.0, 0.0, 0.0], dtype=np.float32)
        await agent.add("test1", "Hello world", embedding)

        entry = await agent.get("test1")
        assert entry is not None
        assert entry.id == "test1"
        assert entry.state == "Hello world"
        assert np.allclose(entry.embedding, embedding)

    async def test_add_wrong_dimension_raises(self, agent) -> None:
        """Test that wrong dimension raises error."""
        wrong_dim = np.array([1.0, 0.0], dtype=np.float32)
        with pytest.raises(SemanticError, match="dimension"):
            await agent.add("test1", "Hello", wrong_dim)

    async def test_delete_entry(self, agent) -> None:
        """Test deleting entries."""
        embedding = np.array([1.0, 0.0, 0.0, 0.0], dtype=np.float32)
        await agent.add("test1", "Hello", embedding)

        assert await agent.delete("test1") is True
        assert await agent.get("test1") is None
        assert await agent.delete("test1") is False  # Already deleted

    async def test_load_returns_all_entries(self, agent) -> None:
        """Test that load returns all entries."""
        e1 = np.array([1.0, 0.0, 0.0, 0.0], dtype=np.float32)
        e2 = np.array([0.0, 1.0, 0.0, 0.0], dtype=np.float32)

        await agent.add("test1", "Hello", e1)
        await agent.add("test2", "World", e2)

        entries = await agent.load()
        assert len(entries) == 2
        assert "test1" in entries
        assert "test2" in entries

    async def test_history_returns_states(self, agent) -> None:
        """Test history returns states in reverse order."""
        e1 = np.array([1.0, 0.0, 0.0, 0.0], dtype=np.float32)
        e2 = np.array([0.0, 1.0, 0.0, 0.0], dtype=np.float32)

        await agent.add("test1", "First", e1)
        await agent.add("test2", "Second", e2)

        history = await agent.history()
        assert history == ["Second", "First"]

    async def test_history_limit(self, agent) -> None:
        """Test history respects limit."""
        for i in range(5):
            e = np.random.randn(4).astype(np.float32)
            await agent.add(f"test{i}", f"State{i}", e)

        history = await agent.history(limit=2)
        assert len(history) == 2


class TestVectorAgentNeighbors:
    """Neighbor search operations."""

    @pytest.fixture
    def agent_with_data(self) -> VectorAgent:
        """Create agent with test data."""
        agent = VectorAgent(dimension=4, distance=DistanceMetric.COSINE)
        return agent

    async def test_neighbors_cosine(self, agent_with_data) -> None:
        """Test k-NN with cosine distance."""
        agent = agent_with_data

        # Add orthogonal vectors
        await agent.add("north", "North", np.array([1, 0, 0, 0], dtype=np.float32))
        await agent.add("east", "East", np.array([0, 1, 0, 0], dtype=np.float32))
        await agent.add("south", "South", np.array([-1, 0, 0, 0], dtype=np.float32))
        await agent.add(
            "northeast", "NorthEast", np.array([0.7, 0.7, 0, 0], dtype=np.float32)
        )

        # Query close to north
        query = np.array([0.9, 0.1, 0, 0], dtype=np.float32)
        results = await agent.neighbors(query, k=2)

        assert len(results) == 2
        # North should be closest (most similar)
        assert results[0][0].id == "north"

    async def test_neighbors_euclidean(self) -> None:
        """Test k-NN with euclidean distance."""
        agent = VectorAgent(dimension=2, distance=DistanceMetric.EUCLIDEAN)

        await agent.add("origin", "Origin", np.array([0, 0], dtype=np.float32))
        await agent.add("near", "Near", np.array([1, 1], dtype=np.float32))
        await agent.add("far", "Far", np.array([10, 10], dtype=np.float32))

        query = np.array([0.5, 0.5], dtype=np.float32)
        results = await agent.neighbors(query, k=2)

        # Origin should be closest
        assert results[0][0].id == "origin"
        assert results[1][0].id == "near"

    async def test_neighbors_with_radius(self, agent_with_data) -> None:
        """Test neighbors with maximum radius."""
        agent = agent_with_data

        await agent.add("close", "Close", np.array([1, 0, 0, 0], dtype=np.float32))
        await agent.add("far", "Far", np.array([-1, 0, 0, 0], dtype=np.float32))

        query = np.array([0.9, 0.1, 0, 0], dtype=np.float32)
        results = await agent.neighbors(query, k=10, radius=0.5)

        # Only close should be within radius
        assert len(results) == 1
        assert results[0][0].id == "close"

    async def test_nearest_returns_states(self, agent_with_data) -> None:
        """Test nearest convenience method returns states."""
        agent = agent_with_data

        await agent.add("test1", "State1", np.array([1, 0, 0, 0], dtype=np.float32))
        await agent.add("test2", "State2", np.array([0, 1, 0, 0], dtype=np.float32))

        query = np.array([0.9, 0.1, 0, 0], dtype=np.float32)
        results = await agent.nearest(query, k=2)

        assert results[0][0] == "State1"  # Returns state, not VectorEntry


class TestSemanticManifoldOperations:
    """Semantic manifold operations: curvature, geodesic, voids."""

    @pytest.fixture
    def populated_agent(self) -> VectorAgent:
        """Create agent with clustered data."""
        agent = VectorAgent(dimension=4)
        return agent

    async def test_curvature_at_cluster(self, populated_agent) -> None:
        """Test curvature estimation at cluster center."""
        agent = populated_agent

        # Create tight cluster around [1, 0, 0, 0]
        for i in range(10):
            noise = np.random.randn(4) * 0.1
            vec = np.array([1, 0, 0, 0]) + noise
            await agent.add(f"cluster{i}", f"State{i}", vec.astype(np.float32))

        # Curvature at cluster center should be low
        center = np.array([1, 0, 0, 0], dtype=np.float32)
        curvature = await agent.curvature_at(center, radius=0.5)

        # Low variance = low curvature
        assert curvature < 0.5

    async def test_geodesic_path(self, populated_agent) -> None:
        """Test geodesic path between points."""
        agent = populated_agent

        start = np.array([0, 0, 0, 0], dtype=np.float32)
        end = np.array([1, 1, 0, 0], dtype=np.float32)

        path = await agent.geodesic(start, end, steps=5)

        assert len(path) == 6  # steps + 1
        assert np.allclose(path[0].coordinates, start)
        assert np.allclose(path[-1].coordinates, end)

        # Intermediate points should be interpolated
        mid = path[3].coordinates
        expected_mid = start * 0.4 + end * 0.6  # 3/5 of the way
        assert np.allclose(mid, expected_mid, atol=0.01)

    async def test_void_detection_empty(self, populated_agent) -> None:
        """Test void detection in empty space."""
        agent = populated_agent

        # Add just one point
        await agent.add("origin", "Origin", np.array([0, 0, 0, 0], dtype=np.float32))

        # Look for void far from origin
        query = np.array([5, 5, 5, 5], dtype=np.float32)
        void = await agent.void_nearby(query, search_radius=10.0)

        assert void is not None
        assert void.potential > 0.0

    async def test_void_detection_populated(self, populated_agent) -> None:
        """Test void detection in populated space."""
        agent = populated_agent

        # Fill space densely
        for x in range(-2, 3):
            for y in range(-2, 3):
                vec = np.array([x, y, 0, 0], dtype=np.float32)
                await agent.add(f"grid_{x}_{y}", f"({x},{y})", vec)

        # Look for void in covered area
        query = np.array([0, 0, 0, 0], dtype=np.float32)

        # Should raise VoidNotFoundError when densely populated
        # (or find small voids)
        try:
            void = await agent.void_nearby(
                query, search_radius=1.0, min_void_radius=2.0
            )
            # If found, potential should be low
            assert void.potential < 0.5
        except VoidNotFoundError:
            pass  # Expected when no significant void exists

    async def test_cluster_centers(self, populated_agent) -> None:
        """Test cluster center detection."""
        agent = populated_agent

        # Create two clear clusters
        for i in range(10):
            vec_a = (
                np.array([1, 0, 0, 0], dtype=np.float32)
                + np.random.randn(4).astype(np.float32) * 0.1
            )
            vec_b = (
                np.array([-1, 0, 0, 0], dtype=np.float32)
                + np.random.randn(4).astype(np.float32) * 0.1
            )
            await agent.add(f"a{i}", f"A{i}", vec_a)
            await agent.add(f"b{i}", f"B{i}", vec_b)

        centers = await agent.cluster_centers(k=2)
        assert len(centers) == 2

        # Centers should be near [1,0,0,0] and [-1,0,0,0]
        center_xs = sorted([c.coordinates[0] for c in centers])
        assert center_xs[0] < 0  # One negative
        assert center_xs[1] > 0  # One positive


class TestVectorAgentPersistence:
    """Persistence tests."""

    async def test_persistence_round_trip(self) -> None:
        """Test save and load from disk."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "vectors.json"

            # Create and populate
            agent1 = VectorAgent(dimension=4, persistence_path=path)
            await agent1.add("test1", "Hello", np.array([1, 0, 0, 0], dtype=np.float32))
            await agent1.add("test2", "World", np.array([0, 1, 0, 0], dtype=np.float32))

            # Create new instance from same path
            agent2 = VectorAgent(dimension=4, persistence_path=path)

            # Should have loaded data
            entries = await agent2.load()
            assert len(entries) == 2
            assert "test1" in entries
            assert "test2" in entries

            # Check values
            entry1 = await agent2.get("test1")
            assert entry1.state == "Hello"
            assert np.allclose(entry1.embedding, [1, 0, 0, 0])


class TestVectorAgentWithEmbedder:
    """Tests with auto-embedder."""

    async def test_save_with_embedder(self) -> None:
        """Test auto-embedding via save()."""

        def embedder(text: str) -> np.ndarray:
            # Simple deterministic embedder
            return np.array([len(text), 0, 0, 0], dtype=np.float32)

        agent = VectorAgent(dimension=4, embedder=embedder)

        await agent.save("Hi")  # Length 2
        await agent.save("Hello")  # Length 5

        entries = await agent.load()
        assert len(entries) == 2

    async def test_save_without_embedder_raises(self) -> None:
        """Test that save without embedder raises error."""
        agent = VectorAgent(dimension=4)  # No embedder

        with pytest.raises(SemanticError, match="No embedder"):
            await agent.save("Hello")

    async def test_embed_creates_point(self) -> None:
        """Test embed method creates Point."""

        def embedder(text: str) -> np.ndarray:
            return np.array([1, 2, 3, 4], dtype=np.float32)

        agent = VectorAgent(dimension=4, embedder=embedder)
        point = await agent.embed("test")

        assert isinstance(point, Point)
        assert np.allclose(point.coordinates, [1, 2, 3, 4])


class TestPointAndVoid:
    """Tests for Point and Void dataclasses."""

    def test_point_equality(self) -> None:
        """Test Point equality based on coordinates."""
        p1 = Point(coordinates=np.array([1, 2, 3]))
        p2 = Point(coordinates=np.array([1, 2, 3]))
        p3 = Point(coordinates=np.array([1, 2, 4]))

        assert p1 == p2
        assert p1 != p3

    def test_void_attributes(self) -> None:
        """Test Void dataclass."""
        void = Void(
            center=Point(coordinates=np.array([0, 0, 0])),
            radius=1.5,
            potential=0.8,
        )

        assert void.radius == 1.5
        assert void.potential == 0.8
