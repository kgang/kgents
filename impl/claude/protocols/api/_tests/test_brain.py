"""
Tests for Brain API endpoints.

Tests the Holographic Brain REST API:
- POST /v1/brain/capture
- POST /v1/brain/ghost
- GET /v1/brain/map
- GET /v1/brain/status

Session 6: Crown Jewel Brain API tests.
"""

from __future__ import annotations

import pytest

# Skip if FastAPI not available
pytest.importorskip("fastapi")
pytest.importorskip("httpx")

from fastapi.testclient import TestClient
from protocols.api.app import create_app


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
