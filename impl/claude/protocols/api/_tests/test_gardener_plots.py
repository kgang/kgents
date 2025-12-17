"""
Tests for Gardener plot CRUD endpoints.

Phase 2 of Crown Jewels completion: Plot API.

Tests:
- List plots
- Get plot by name
- Create plot
- Update plot
- Delete plot
"""

from __future__ import annotations

import pytest

# Skip all tests if FastAPI not available
pytest.importorskip("fastapi")

from fastapi.testclient import TestClient

from protocols.api.app import create_app


# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def client():
    """Create test client."""
    app = create_app(enable_cors=False, enable_tenant_middleware=False)
    return TestClient(app)


@pytest.fixture
def reset_garden():
    """Reset garden state between tests."""
    from protocols.api import gardener

    # Reset the global garden state
    gardener._garden_state = None
    yield
    gardener._garden_state = None


# =============================================================================
# List Plots Tests
# =============================================================================


class TestListPlots:
    """Tests for GET /v1/gardener/garden/plots."""

    def test_list_plots_returns_plots(self, client, reset_garden):
        """Test listing all plots."""
        response = client.get("/v1/gardener/garden/plots")
        assert response.status_code == 200

        data = response.json()
        assert "plots" in data
        assert "total_count" in data
        assert isinstance(data["plots"], list)
        # Default garden has Crown Jewel plots
        assert data["total_count"] > 0

    def test_list_plots_includes_active(self, client, reset_garden):
        """Test that list includes active_plot field."""
        response = client.get("/v1/gardener/garden/plots")
        data = response.json()
        assert "active_plot" in data


# =============================================================================
# Get Plot Tests
# =============================================================================


class TestGetPlot:
    """Tests for GET /v1/gardener/garden/plots/{plot_name}."""

    def test_get_existing_plot(self, client, reset_garden):
        """Test getting an existing plot."""
        # First list to get a plot name
        list_response = client.get("/v1/gardener/garden/plots")
        plots = list_response.json()["plots"]
        assert len(plots) > 0

        plot_name = plots[0]["name"]
        response = client.get(f"/v1/gardener/garden/plots/{plot_name}")
        assert response.status_code == 200

        data = response.json()
        assert data["name"] == plot_name
        assert "path" in data
        assert "rigidity" in data
        assert "progress" in data

    def test_get_nonexistent_plot_returns_404(self, client, reset_garden):
        """Test getting a nonexistent plot returns 404."""
        response = client.get("/v1/gardener/garden/plots/nonexistent-plot-xyz")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()


# =============================================================================
# Create Plot Tests
# =============================================================================


class TestCreatePlot:
    """Tests for POST /v1/gardener/garden/plots."""

    def test_create_plot_success(self, client, reset_garden):
        """Test creating a new plot."""
        response = client.post(
            "/v1/gardener/garden/plots",
            json={
                "name": "test-plot",
                "path": "world.test.feature",
                "description": "A test plot",
                "rigidity": 0.7,
                "tags": ["test", "feature"],
            },
        )
        assert response.status_code == 200

        data = response.json()
        assert data["name"] == "test-plot"
        assert data["path"] == "world.test.feature"
        assert data["description"] == "A test plot"
        assert data["rigidity"] == 0.7
        assert data["tags"] == ["test", "feature"]
        assert data["progress"] == 0.0
        assert "created_at" in data
        assert "last_tended" in data

    def test_create_duplicate_plot_returns_400(self, client, reset_garden):
        """Test creating a duplicate plot returns 400."""
        # Create first plot
        client.post(
            "/v1/gardener/garden/plots",
            json={
                "name": "duplicate-plot",
                "path": "world.dup.test",
            },
        )

        # Try to create duplicate
        response = client.post(
            "/v1/gardener/garden/plots",
            json={
                "name": "duplicate-plot",
                "path": "world.dup.test2",
            },
        )
        assert response.status_code == 400
        assert "already exists" in response.json()["detail"].lower()

    def test_create_plot_with_crown_jewel(self, client, reset_garden):
        """Test creating a plot linked to a Crown Jewel."""
        response = client.post(
            "/v1/gardener/garden/plots",
            json={
                "name": "jewel-plot",
                "path": "world.jewel.test",
                "crown_jewel": "brain",
            },
        )
        assert response.status_code == 200
        assert response.json()["crown_jewel"] == "brain"


# =============================================================================
# Update Plot Tests
# =============================================================================


class TestUpdatePlot:
    """Tests for PATCH /v1/gardener/garden/plots/{plot_name}."""

    def test_update_plot_progress(self, client, reset_garden):
        """Test updating plot progress."""
        # Create a plot first
        client.post(
            "/v1/gardener/garden/plots",
            json={"name": "update-test", "path": "world.update.test"},
        )

        # Update progress
        response = client.patch(
            "/v1/gardener/garden/plots/update-test",
            json={"progress": 0.75},
        )
        assert response.status_code == 200
        assert response.json()["progress"] == 0.75

    def test_update_plot_rigidity(self, client, reset_garden):
        """Test updating plot rigidity."""
        # Create a plot first
        client.post(
            "/v1/gardener/garden/plots",
            json={"name": "rigidity-test", "path": "world.rigidity.test"},
        )

        # Update rigidity
        response = client.patch(
            "/v1/gardener/garden/plots/rigidity-test",
            json={"rigidity": 0.2},
        )
        assert response.status_code == 200
        assert response.json()["rigidity"] == 0.2

    def test_update_nonexistent_plot_returns_404(self, client, reset_garden):
        """Test updating a nonexistent plot returns 404."""
        response = client.patch(
            "/v1/gardener/garden/plots/nonexistent-plot-xyz",
            json={"progress": 0.5},
        )
        assert response.status_code == 404

    def test_update_plot_updates_last_tended(self, client, reset_garden):
        """Test that updating a plot updates last_tended."""
        # Create a plot first
        create_response = client.post(
            "/v1/gardener/garden/plots",
            json={"name": "tended-test", "path": "world.tended.test"},
        )
        original_tended = create_response.json()["last_tended"]

        # Small delay to ensure timestamp difference
        import time

        time.sleep(0.01)

        # Update the plot
        update_response = client.patch(
            "/v1/gardener/garden/plots/tended-test",
            json={"description": "updated"},
        )
        new_tended = update_response.json()["last_tended"]

        assert new_tended >= original_tended


# =============================================================================
# Delete Plot Tests
# =============================================================================


class TestDeletePlot:
    """Tests for DELETE /v1/gardener/garden/plots/{plot_name}."""

    def test_delete_plot_success(self, client, reset_garden):
        """Test deleting a plot."""
        # Create a plot first
        client.post(
            "/v1/gardener/garden/plots",
            json={"name": "delete-test", "path": "world.delete.test"},
        )

        # Delete it
        response = client.delete("/v1/gardener/garden/plots/delete-test")
        assert response.status_code == 200
        assert response.json()["status"] == "deleted"
        assert response.json()["plot"] == "delete-test"

        # Verify it's gone
        get_response = client.get("/v1/gardener/garden/plots/delete-test")
        assert get_response.status_code == 404

    def test_delete_nonexistent_plot_returns_404(self, client, reset_garden):
        """Test deleting a nonexistent plot returns 404."""
        response = client.delete("/v1/gardener/garden/plots/nonexistent-plot-xyz")
        assert response.status_code == 404

    def test_delete_active_plot_clears_active(self, client, reset_garden):
        """Test that deleting the active plot clears active_plot."""
        # Create and focus a plot
        client.post(
            "/v1/gardener/garden/plots",
            json={"name": "active-delete-test", "path": "world.active.delete"},
        )
        client.post("/v1/gardener/garden/plot/active-delete-test/focus")

        # Verify it's active
        list_response = client.get("/v1/gardener/garden/plots")
        assert list_response.json()["active_plot"] == "active-delete-test"

        # Delete it
        client.delete("/v1/gardener/garden/plots/active-delete-test")

        # Verify active_plot is cleared
        list_response = client.get("/v1/gardener/garden/plots")
        assert list_response.json()["active_plot"] is None
