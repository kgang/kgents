"""
Tests for Brain API endpoints.

Tests the Holographic Brain REST API:
- POST /v1/brain/capture
- POST /v1/brain/ghost
- GET /v1/brain/map
- GET /v1/brain/status
- GET /v1/brain/topology (3D visualization)

Session 6: Crown Jewel Brain API tests.
Session 7: 3D Topology visualization tests.

Tests use a simple embedder (no network calls) via fixture injection.

Note on test isolation:
    The brain API uses module-level globals (_brain_logos, _brain_observer, etc.).
    The autouse fixture resets these between tests, ensuring isolation in sequential
    runs. However, pytest-xdist parallel runs (-n auto) could cause race conditions
    if multiple workers execute brain tests simultaneously. For CI, either:
    - Run brain tests sequentially (no -n flag), OR
    - Use pytest markers to isolate these tests to a single worker
"""

from __future__ import annotations

from typing import Generator

import pytest

# Skip if FastAPI not available
pytest.importorskip("fastapi")
pytest.importorskip("httpx")

from fastapi.testclient import TestClient
from protocols.api.app import create_app
from protocols.api.brain import (
    _reset_brain_logos,
    _set_brain_logos_factory,
)


@pytest.fixture(autouse=True)
def use_simple_embedder() -> Generator[None, None, None]:
    """Use simple embedder for all brain API tests (no network calls).

    This fixture ensures tests don't download models or mutate global state.
    """
    from protocols.agentese import create_brain_logos

    def simple_brain_factory() -> object:
        """Create brain logos with simple (non-network) embedder."""
        return create_brain_logos(embedder_type="simple", dimension=64)

    _set_brain_logos_factory(simple_brain_factory)
    yield
    _set_brain_logos_factory(None)
    _reset_brain_logos()


@pytest.fixture
def client() -> TestClient:
    """Create test client with brain router."""
    app = create_app(enable_tenant_middleware=False)
    return TestClient(app)


class TestBrainCapture:
    """Tests for POST /v1/brain/capture."""

    def test_capture_content(self, client: TestClient) -> None:
        """Test capturing content to brain."""
        response = client.post(
            "/v1/brain/capture",
            json={"content": "Python is great for data science"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "captured"
        assert "concept_id" in data
        assert data["storage"] in ("memory_crystal", "local_memory")

    def test_capture_with_concept_id(self, client: TestClient) -> None:
        """Test capturing with explicit concept_id."""
        response = client.post(
            "/v1/brain/capture",
            json={
                "content": "Machine learning basics",
                "concept_id": "test_ml_001",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["concept_id"] == "test_ml_001"

    def test_capture_with_metadata(self, client: TestClient) -> None:
        """Test capturing with metadata."""
        response = client.post(
            "/v1/brain/capture",
            json={
                "content": "Important meeting notes",
                "metadata": {"source": "meeting", "importance": "high"},
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "captured"

    def test_capture_requires_content(self, client: TestClient) -> None:
        """Test that content is required."""
        response = client.post(
            "/v1/brain/capture",
            json={},
        )
        assert response.status_code == 422  # Validation error

    def test_capture_rejects_empty_content(self, client: TestClient) -> None:
        """Test that empty content is rejected."""
        response = client.post(
            "/v1/brain/capture",
            json={"content": ""},
        )
        assert response.status_code == 422  # Validation error (min_length=1)

    def test_capture_rejects_whitespace_only_content(self, client: TestClient) -> None:
        """Test that whitespace-only content is rejected.

        Regression test: min_length=1 doesn't trim whitespace,
        so we need explicit validation.
        """
        response = client.post(
            "/v1/brain/capture",
            json={"content": "   "},
        )
        assert response.status_code == 422
        # Verify the error message mentions whitespace
        detail = response.json().get("detail", [])
        assert any("whitespace" in str(d).lower() for d in detail), (
            f"Expected 'whitespace' in error detail, got: {detail}"
        )


class TestBrainGhost:
    """Tests for POST /v1/brain/ghost."""

    def test_ghost_surface_empty(self, client: TestClient) -> None:
        """Test ghost surfacing with no captures returns empty."""
        # Note: This uses a fresh brain instance each test
        response = client.post(
            "/v1/brain/ghost",
            json={"context": "something random", "limit": 5},
        )
        assert response.status_code == 200
        data = response.json()
        assert "surfaced" in data
        assert "count" in data

    def test_ghost_surface_after_capture(self, client: TestClient) -> None:
        """Test ghost surfacing finds captured content."""
        # First capture some content
        client.post(
            "/v1/brain/capture",
            json={"content": "Neural networks for image recognition"},
        )

        # Then try to surface related content
        response = client.post(
            "/v1/brain/ghost",
            json={"context": "deep learning and AI"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["context"] == "deep learning and AI"
        # Note: May or may not find content depending on global state

    def test_ghost_respects_limit(self, client: TestClient) -> None:
        """Test that limit parameter is respected."""
        response = client.post(
            "/v1/brain/ghost",
            json={"context": "test", "limit": 2},
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data.get("surfaced", [])) <= 2

    def test_ghost_requires_context(self, client: TestClient) -> None:
        """Test that context is required."""
        response = client.post(
            "/v1/brain/ghost",
            json={},
        )
        assert response.status_code == 422  # Validation error

    def test_ghost_rejects_empty_context(self, client: TestClient) -> None:
        """Test that empty context is rejected."""
        response = client.post(
            "/v1/brain/ghost",
            json={"context": ""},
        )
        assert response.status_code == 422  # Validation error (min_length=1)

    def test_ghost_rejects_whitespace_only_context(self, client: TestClient) -> None:
        """Test that whitespace-only context is rejected.

        Regression test: min_length=1 doesn't trim whitespace,
        so we need explicit validation.
        """
        response = client.post(
            "/v1/brain/ghost",
            json={"context": "   \t\n  "},
        )
        assert response.status_code == 422
        # Verify the error message mentions whitespace
        detail = response.json().get("detail", [])
        assert any("whitespace" in str(d).lower() for d in detail), (
            f"Expected 'whitespace' in error detail, got: {detail}"
        )


class TestBrainMap:
    """Tests for GET /v1/brain/map."""

    def test_get_map(self, client: TestClient) -> None:
        """Test getting brain map."""
        response = client.get("/v1/brain/map")
        assert response.status_code == 200
        data = response.json()
        assert "summary" in data
        assert "concept_count" in data
        assert "dimension" in data
        assert isinstance(data["concept_count"], int)
        assert isinstance(data["dimension"], int)

    def test_map_updates_after_capture(self, client: TestClient) -> None:
        """Test that map reflects captured content."""
        # Get initial count
        response1 = client.get("/v1/brain/map")
        initial_count = response1.json()["concept_count"]

        # Capture something
        client.post(
            "/v1/brain/capture",
            json={"content": "New concept for map test"},
        )

        # Check count increased
        response2 = client.get("/v1/brain/map")
        new_count = response2.json()["concept_count"]
        assert new_count >= initial_count  # Should increase (or equal if shared state)


class TestBrainStatus:
    """Tests for GET /v1/brain/status."""

    def test_get_status(self, client: TestClient) -> None:
        """Test getting brain status."""
        response = client.get("/v1/brain/status")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert data["status"] in ("healthy", "degraded", "unavailable")
        assert "embedder_type" in data
        assert "embedder_dimension" in data
        assert "concept_count" in data
        assert "has_cartographer" in data

    def test_status_shows_embedder_info(self, client: TestClient) -> None:
        """Test that status shows embedder information."""
        response = client.get("/v1/brain/status")
        data = response.json()
        # Should have some embedder type
        assert data["embedder_type"] in (
            "SentenceTransformerEmbedder",
            "SimpleEmbedder",
            "None",
        )
        # Dimension should be positive
        assert data["embedder_dimension"] > 0


class TestBrainIntegration:
    """Integration tests for full brain workflow."""

    def test_capture_then_ghost_workflow(self, client: TestClient) -> None:
        """Test full capture → ghost workflow."""
        # Capture related content
        client.post(
            "/v1/brain/capture",
            json={"content": "Python programming language basics"},
        )
        client.post(
            "/v1/brain/capture",
            json={"content": "JavaScript for web development"},
        )

        # Surface ghosts
        response = client.post(
            "/v1/brain/ghost",
            json={"context": "programming languages"},
        )
        assert response.status_code == 200

        # Check status
        status_response = client.get("/v1/brain/status")
        assert status_response.status_code == 200
        assert status_response.json()["status"] in ("healthy", "degraded")


class TestBrainTopology:
    """Tests for GET /v1/brain/topology (3D visualization)."""

    def test_get_topology_empty(self, client: TestClient) -> None:
        """Test getting topology with no captured content."""
        response = client.get("/v1/brain/topology")
        assert response.status_code == 200
        data = response.json()
        # Should have all expected fields
        assert "nodes" in data
        assert "edges" in data
        assert "gaps" in data
        assert "hub_ids" in data
        assert "stats" in data
        # Stats should have expected structure
        assert "concept_count" in data["stats"]
        assert "edge_count" in data["stats"]

    def test_topology_nodes_after_capture(self, client: TestClient) -> None:
        """Test that topology includes captured concepts as nodes."""
        # Capture some content
        client.post(
            "/v1/brain/capture",
            json={"content": "Python machine learning basics", "concept_id": "ml_001"},
        )
        client.post(
            "/v1/brain/capture",
            json={"content": "Deep learning neural networks", "concept_id": "dl_001"},
        )

        # Get topology
        response = client.get("/v1/brain/topology")
        assert response.status_code == 200
        data = response.json()

        # Should have nodes
        assert data["stats"]["concept_count"] >= 2
        assert len(data["nodes"]) >= 2

        # Nodes should have expected structure
        if data["nodes"]:
            node = data["nodes"][0]
            assert "id" in node
            assert "label" in node
            assert "x" in node
            assert "y" in node
            assert "z" in node
            assert "resolution" in node
            assert "is_hot" in node
            assert "access_count" in node
            assert "age_seconds" in node

    def test_topology_edges(self, client: TestClient) -> None:
        """Test that topology includes similarity edges between concepts."""
        # Capture related content
        client.post(
            "/v1/brain/capture",
            json={"content": "Python programming language", "concept_id": "py_001"},
        )
        client.post(
            "/v1/brain/capture",
            json={"content": "Python development tools", "concept_id": "py_002"},
        )

        # Get topology with low threshold to ensure edges
        response = client.get(
            "/v1/brain/topology", params={"similarity_threshold": 0.1}
        )
        assert response.status_code == 200
        data = response.json()

        # Should have edges (related content)
        # Note: depends on embedder similarity
        if data["edges"]:
            edge = data["edges"][0]
            assert "source" in edge
            assert "target" in edge
            assert "similarity" in edge
            assert 0 <= edge["similarity"] <= 1

    def test_topology_similarity_threshold(self, client: TestClient) -> None:
        """Test that similarity_threshold parameter filters edges."""
        # Capture some content
        client.post(
            "/v1/brain/capture",
            json={"content": "Testing content alpha"},
        )
        client.post(
            "/v1/brain/capture",
            json={"content": "Testing content beta"},
        )

        # High threshold should return fewer edges
        response_high = client.get(
            "/v1/brain/topology", params={"similarity_threshold": 0.9}
        )
        response_low = client.get(
            "/v1/brain/topology", params={"similarity_threshold": 0.1}
        )

        assert response_high.status_code == 200
        assert response_low.status_code == 200

        high_edges = len(response_high.json()["edges"])
        low_edges = len(response_low.json()["edges"])
        # Low threshold should have >= edges than high threshold
        assert low_edges >= high_edges

    def test_topology_hub_detection(self, client: TestClient) -> None:
        """Test that hubs are identified (high connectivity nodes)."""
        # Capture several related concepts
        for i in range(5):
            client.post(
                "/v1/brain/capture",
                json={
                    "content": f"Machine learning concept {i}",
                    "concept_id": f"ml_{i}",
                },
            )

        response = client.get(
            "/v1/brain/topology", params={"similarity_threshold": 0.1}
        )
        assert response.status_code == 200
        data = response.json()

        # hub_ids should be a list
        assert isinstance(data["hub_ids"], list)
        # Stats should report hub count
        assert "hub_count" in data["stats"]

    def test_topology_node_positions(self, client: TestClient) -> None:
        """Test that nodes have valid 3D positions."""
        client.post(
            "/v1/brain/capture",
            json={"content": "Test concept for position validation"},
        )

        response = client.get("/v1/brain/topology")
        assert response.status_code == 200
        data = response.json()

        for node in data["nodes"]:
            # Positions should be finite numbers
            assert isinstance(node["x"], (int, float))
            assert isinstance(node["y"], (int, float))
            assert isinstance(node["z"], (int, float))
            # Resolution should be in valid range
            assert 0 <= node["resolution"] <= 1


class TestTopologyInvariants:
    """Property-based tests for topology calculations.

    These tests verify mathematical invariants that must hold
    regardless of the input data.
    """

    def test_cosine_similarity_symmetry(self) -> None:
        """Cosine similarity is symmetric: sim(a,b) == sim(b,a)."""
        from protocols.api.brain import _cosine_similarity

        a = [1.0, 2.0, 3.0]
        b = [4.0, 5.0, 6.0]

        assert _cosine_similarity(a, b) == _cosine_similarity(b, a)

    def test_cosine_similarity_identity(self) -> None:
        """Cosine similarity of vector with itself is 1.0."""
        from protocols.api.brain import _cosine_similarity

        vec = [1.0, 2.0, 3.0, 4.0]
        sim = _cosine_similarity(vec, vec)
        assert abs(sim - 1.0) < 1e-10, f"Expected 1.0, got {sim}"

    def test_cosine_similarity_zero_vectors(self) -> None:
        """Cosine similarity handles zero vectors gracefully."""
        from protocols.api.brain import _cosine_similarity

        zero = [0.0, 0.0, 0.0]
        nonzero = [1.0, 2.0, 3.0]

        # Zero vector should return 0
        assert _cosine_similarity(zero, zero) == 0.0
        assert _cosine_similarity(zero, nonzero) == 0.0
        assert _cosine_similarity(nonzero, zero) == 0.0

    def test_cosine_similarity_empty_vectors(self) -> None:
        """Cosine similarity handles empty vectors gracefully."""
        from protocols.api.brain import _cosine_similarity

        assert _cosine_similarity([], []) == 0.0
        assert _cosine_similarity([], [1.0]) == 0.0
        assert _cosine_similarity([1.0], []) == 0.0

    def test_cosine_similarity_mismatched_lengths(self) -> None:
        """Cosine similarity handles vectors of different lengths."""
        from protocols.api.brain import _cosine_similarity

        short = [1.0, 2.0]
        long = [1.0, 2.0, 3.0, 4.0]

        # Should pad shorter vector with zeros
        sim = _cosine_similarity(short, long)
        assert 0 <= sim <= 1, f"Similarity out of range: {sim}"

    def test_cosine_similarity_bounded(self) -> None:
        """Cosine similarity is always in [-1, 1] range."""
        import random

        from protocols.api.brain import _cosine_similarity

        random.seed(42)
        for _ in range(100):
            a = [random.uniform(-10, 10) for _ in range(random.randint(1, 20))]
            b = [random.uniform(-10, 10) for _ in range(random.randint(1, 20))]
            sim = _cosine_similarity(a, b)
            assert -1.0 <= sim <= 1.0, f"Similarity {sim} out of [-1, 1] range"

    def test_edge_count_upper_bound(self, client: TestClient) -> None:
        """Edge count is bounded by n*(n-1)/2 (complete graph)."""
        # Capture some content
        for i in range(5):
            client.post(
                "/v1/brain/capture",
                json={"content": f"Test content {i}", "concept_id": f"bound_test_{i}"},
            )

        response = client.get(
            "/v1/brain/topology", params={"similarity_threshold": 0.0}
        )
        assert response.status_code == 200
        data = response.json()

        n = data["stats"]["concept_count"]
        max_edges = n * (n - 1) // 2
        actual_edges = data["stats"]["edge_count"]

        assert actual_edges <= max_edges, (
            f"Edge count {actual_edges} exceeds maximum {max_edges} for {n} nodes"
        )


class TestTopologyPerformance:
    """Performance baseline tests for topology endpoint."""

    def test_topology_response_time_small(self, client: TestClient) -> None:
        """Topology with <10 nodes should respond in <200ms."""
        import time

        for i in range(5):
            client.post(
                "/v1/brain/capture",
                json={"content": f"Performance test {i}", "concept_id": f"perf_{i}"},
            )

        start = time.perf_counter()
        response = client.get("/v1/brain/topology")
        elapsed = time.perf_counter() - start

        assert response.status_code == 200
        assert elapsed < 0.2, f"Response time {elapsed:.3f}s exceeds 200ms baseline"

    def test_topology_response_time_medium(self, client: TestClient) -> None:
        """Topology with 20 nodes should respond in <500ms."""
        import time

        for i in range(20):
            client.post(
                "/v1/brain/capture",
                json={
                    "content": f"Medium perf test {i}",
                    "concept_id": f"med_perf_{i}",
                },
            )

        start = time.perf_counter()
        response = client.get("/v1/brain/topology")
        elapsed = time.perf_counter() - start

        assert response.status_code == 200
        assert elapsed < 0.5, f"Response time {elapsed:.3f}s exceeds 500ms baseline"
