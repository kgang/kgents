"""
Tests for Atelier API endpoints.

Tests:
- GET /api/atelier/artisans - List artisans
- POST /api/atelier/commission - Commission (SSE stream)
- POST /api/atelier/collaborate - Collaboration (SSE stream)
- GET /api/atelier/gallery - Gallery listing
- GET /api/atelier/gallery/{id} - Piece details
- GET /api/atelier/gallery/{id}/lineage - Piece lineage
- POST /api/atelier/queue - Queue commission
- GET /api/atelier/queue/pending - Pending queue
- GET /api/atelier/status - Workshop status
"""

from __future__ import annotations

import tempfile
from collections.abc import Generator
from pathlib import Path

import pytest

pytest.importorskip("fastapi")

from fastapi.testclient import TestClient
from protocols.api.app import create_app


@pytest.fixture
def client() -> TestClient:
    """Create test client."""
    app = create_app()
    return TestClient(app)


@pytest.fixture
def temp_gallery(monkeypatch: pytest.MonkeyPatch) -> Generator[Path, None, None]:
    """Create a temporary gallery directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        gallery_path = Path(tmpdir) / "gallery"
        gallery_path.mkdir()

        # Patch the gallery singleton
        from agents.atelier.gallery import store

        original_gallery = store._default_gallery
        store._default_gallery = store.Gallery(gallery_path)

        yield gallery_path

        # Restore
        store._default_gallery = original_gallery


class TestArtisansEndpoint:
    """Tests for /api/atelier/artisans endpoint."""

    def test_list_artisans(self, client: TestClient) -> None:
        """Test listing available artisans."""
        response = client.get("/api/atelier/artisans")

        assert response.status_code == 200
        data = response.json()

        assert "artisans" in data
        assert "total" in data
        assert data["total"] > 0

        # Check artisan structure
        artisan = data["artisans"][0]
        assert "name" in artisan
        assert "specialty" in artisan

    def test_artisans_include_calligrapher(self, client: TestClient) -> None:
        """Test calligrapher is in the list."""
        response = client.get("/api/atelier/artisans")
        data = response.json()

        names = [a["name"] for a in data["artisans"]]
        assert "The Calligrapher" in names


class TestGalleryEndpoints:
    """Tests for gallery endpoints."""

    def test_list_gallery_empty(self, client: TestClient, temp_gallery: Path) -> None:
        """Test listing empty gallery."""
        response = client.get("/api/atelier/gallery")

        assert response.status_code == 200
        data = response.json()

        assert "pieces" in data
        assert "total" in data
        assert data["total"] == 0
        assert data["pieces"] == []

    def test_list_gallery_with_filters(
        self, client: TestClient, temp_gallery: Path
    ) -> None:
        """Test gallery filtering."""
        response = client.get(
            "/api/atelier/gallery",
            params={"artisan": "Calligrapher", "limit": 5},
        )

        assert response.status_code == 200
        data = response.json()
        assert "pieces" in data

    def test_get_piece_not_found(self, client: TestClient, temp_gallery: Path) -> None:
        """Test getting non-existent piece."""
        response = client.get("/api/atelier/gallery/nonexistent")

        assert response.status_code == 404

    def test_delete_piece_not_found(
        self, client: TestClient, temp_gallery: Path
    ) -> None:
        """Test deleting non-existent piece."""
        response = client.delete("/api/atelier/gallery/nonexistent")

        assert response.status_code == 404

    def test_search_gallery_empty(self, client: TestClient, temp_gallery: Path) -> None:
        """Test searching empty gallery."""
        response = client.get("/api/atelier/gallery/search", params={"query": "haiku"})

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0


class TestQueueEndpoints:
    """Tests for queue endpoints."""

    def test_get_pending_empty(self, client: TestClient) -> None:
        """Test getting empty pending queue."""
        response = client.get("/api/atelier/queue/pending")

        assert response.status_code == 200
        data = response.json()

        assert "items" in data
        assert "total" in data

    def test_queue_invalid_artisan(self, client: TestClient) -> None:
        """Test queuing with invalid artisan."""
        response = client.post(
            "/api/atelier/queue",
            json={
                "artisan": "nonexistent",
                "request": "test",
            },
        )

        assert response.status_code == 400
        assert "Unknown artisan" in response.json()["detail"]

    def test_queue_valid_commission(self, client: TestClient) -> None:
        """Test queuing a valid commission."""
        response = client.post(
            "/api/atelier/queue",
            json={
                "artisan": "calligrapher",
                "request": "a haiku about testing",
                "patron": "tester",
            },
        )

        assert response.status_code == 200
        data = response.json()

        assert "commission_id" in data
        assert data["artisan"] == "calligrapher"
        assert data["status"] == "queued"


class TestStatusEndpoint:
    """Tests for /api/atelier/status endpoint."""

    def test_get_status(self, client: TestClient) -> None:
        """Test getting workshop status."""
        response = client.get("/api/atelier/status")

        assert response.status_code == 200
        data = response.json()

        assert "status" in data
        assert data["status"] == "active"
        assert "total_commissions" in data
        assert "total_pieces" in data
        assert "pending_queue" in data
        assert "available_artisans" in data


class TestCommissionEndpoint:
    """Tests for /api/atelier/commission endpoint."""

    def test_commission_missing_fields(self, client: TestClient) -> None:
        """Test commission with missing required fields."""
        response = client.post(
            "/api/atelier/commission",
            json={"artisan": "calligrapher"},  # Missing request
        )

        assert response.status_code == 422

    def test_commission_sse_headers(self, client: TestClient) -> None:
        """Test commission returns SSE headers."""
        response = client.post(
            "/api/atelier/commission",
            json={
                "artisan": "calligrapher",
                "request": "test",
            },
        )

        assert response.status_code == 200
        assert response.headers["content-type"].startswith("text/event-stream")


class TestCollaborateEndpoint:
    """Tests for /api/atelier/collaborate endpoint."""

    def test_collaborate_missing_fields(self, client: TestClient) -> None:
        """Test collaboration with missing required fields."""
        response = client.post(
            "/api/atelier/collaborate",
            json={"artisans": ["calligrapher"]},  # Missing request
        )

        assert response.status_code == 422

    def test_collaborate_sse_headers(self, client: TestClient) -> None:
        """Test collaboration returns SSE headers."""
        response = client.post(
            "/api/atelier/collaborate",
            json={
                "artisans": ["calligrapher", "cartographer"],
                "request": "test",
                "mode": "duet",
            },
        )

        assert response.status_code == 200
        assert response.headers["content-type"].startswith("text/event-stream")


class TestRouterRegistration:
    """Tests for router registration."""

    def test_atelier_routes_registered(self, client: TestClient) -> None:
        """Test atelier routes are in OpenAPI."""
        response = client.get("/openapi.json")
        data = response.json()

        paths = data["paths"]

        assert "/api/atelier/artisans" in paths
        assert "/api/atelier/commission" in paths
        assert "/api/atelier/gallery" in paths
        assert "/api/atelier/status" in paths

    def test_atelier_in_root_endpoint(self, client: TestClient) -> None:
        """Test atelier is documented in root endpoint."""
        response = client.get("/")
        data = response.json()

        assert "atelier" in data["endpoints"]
        assert "artisans" in data["endpoints"]["atelier"]
        assert "commission" in data["endpoints"]["atelier"]
        assert "gallery" in data["endpoints"]["atelier"]
