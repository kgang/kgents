"""
Tests for the Gallery API endpoints.
"""

from __future__ import annotations

import pytest

from protocols.api._tests.conftest import skip_if_no_fastapi

# Conditional import for TestClient
try:
    from fastapi.testclient import TestClient

    HAS_FASTAPI = True
except ImportError:
    HAS_FASTAPI = False
    TestClient = None  # type: ignore[misc, assignment]


@pytest.fixture
def client():
    """Create test client for the API."""
    if not HAS_FASTAPI:
        pytest.skip("FastAPI not installed")

    from protocols.api.app import create_app

    app = create_app()
    return TestClient(app)


@skip_if_no_fastapi
class TestGalleryEndpoint:
    """Tests for GET /api/gallery."""

    def test_gallery_endpoint_returns_all_pilots(self, client):
        """Gallery endpoint should return all pilots."""
        response = client.get("/api/gallery")

        assert response.status_code == 200
        data = response.json()

        # Check structure
        assert "pilots" in data
        assert "categories" in data
        assert "total" in data

        # Check we have pilots
        assert len(data["pilots"]) > 0
        assert data["total"] == len(data["pilots"])

        # Check pilot structure
        pilot = data["pilots"][0]
        assert "name" in pilot
        assert "category" in pilot
        assert "description" in pilot
        assert "tags" in pilot
        assert "projections" in pilot

        # Check projections structure
        projections = pilot["projections"]
        assert "cli" in projections
        assert "html" in projections
        assert "json" in projections

    def test_gallery_has_expected_categories(self, client):
        """Gallery should include standard categories."""
        response = client.get("/api/gallery")
        data = response.json()

        expected_categories = ["PRIMITIVES", "CARDS", "CHROME", "STREAMING"]
        for cat in expected_categories:
            assert cat in data["categories"], f"Missing category: {cat}"

    def test_gallery_with_entropy_override(self, client):
        """Gallery should accept entropy override."""
        response = client.get("/api/gallery", params={"entropy": 0.5})

        assert response.status_code == 200
        data = response.json()
        assert len(data["pilots"]) > 0

    def test_gallery_with_seed_override(self, client):
        """Gallery should accept seed override for determinism."""
        response1 = client.get("/api/gallery", params={"seed": 42})
        response2 = client.get("/api/gallery", params={"seed": 42})

        assert response1.status_code == 200
        assert response2.status_code == 200

        # With same seed, results should be identical
        data1 = response1.json()
        data2 = response2.json()
        assert data1["total"] == data2["total"]

    def test_gallery_with_category_filter(self, client):
        """Gallery should filter by category."""
        response = client.get("/api/gallery", params={"category": "PRIMITIVES"})

        assert response.status_code == 200
        data = response.json()

        # All pilots should be PRIMITIVES
        for pilot in data["pilots"]:
            assert pilot["category"] == "PRIMITIVES"

    def test_gallery_with_invalid_entropy(self, client):
        """Gallery should reject invalid entropy values."""
        # Entropy > 1 should be rejected
        response = client.get("/api/gallery", params={"entropy": 1.5})
        assert response.status_code == 422  # Validation error


@skip_if_no_fastapi
class TestGalleryCategoriesEndpoint:
    """Tests for GET /api/gallery/categories."""

    def test_categories_endpoint(self, client):
        """Categories endpoint should return all categories with counts."""
        response = client.get("/api/gallery/categories")

        assert response.status_code == 200
        data = response.json()

        assert "categories" in data
        assert len(data["categories"]) > 0

        # Check category structure
        cat = data["categories"][0]
        assert "name" in cat
        assert "pilot_count" in cat
        assert "pilots" in cat
        assert isinstance(cat["pilots"], list)


@skip_if_no_fastapi
class TestGalleryPilotEndpoint:
    """Tests for GET /api/gallery/{pilot_name}."""

    def test_get_single_pilot(self, client):
        """Should return a single pilot by name."""
        response = client.get("/api/gallery/glyph_idle")

        assert response.status_code == 200
        data = response.json()

        assert data["name"] == "glyph_idle"
        assert data["category"] == "PRIMITIVES"
        assert "projections" in data

    def test_get_pilot_with_override(self, client):
        """Should apply overrides to single pilot."""
        response = client.get(
            "/api/gallery/glyph_entropy_sweep",
            params={"entropy": 0.8, "seed": 123},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "glyph_entropy_sweep"

    def test_get_nonexistent_pilot(self, client):
        """Should return 404 for unknown pilot."""
        response = client.get("/api/gallery/nonexistent_pilot")
        assert response.status_code == 404

    def test_pilot_has_all_projections(self, client):
        """Pilot response should include all projection types."""
        response = client.get("/api/gallery/bar_solid")

        assert response.status_code == 200
        data = response.json()

        projections = data["projections"]
        assert isinstance(projections["cli"], str)
        assert isinstance(projections["html"], str)
        assert isinstance(projections["json"], dict)
