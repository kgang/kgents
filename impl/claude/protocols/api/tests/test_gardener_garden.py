"""
Tests for Gardener Garden API endpoints (Phase 7: Web Visualization).

Tests the garden state and tending endpoints:
- GET /v1/gardener/garden
- POST /v1/gardener/garden/tend
- POST /v1/gardener/garden/season
- POST /v1/gardener/garden/plot/{name}/focus
"""

from datetime import datetime

import pytest

# Skip tests if FastAPI not available
pytest.importorskip("fastapi")

from fastapi.testclient import TestClient

from protocols.api.app import create_app
from protocols.api.models import (
    GardenSeason,
    SeasonTransitionRequest,
    TendingVerb,
    TendRequest,
)


@pytest.fixture
def client():
    """Create test client."""
    app = create_app()
    return TestClient(app)


class TestGardenGet:
    """Tests for GET /v1/gardener/garden."""

    def test_get_garden_returns_state(self, client):
        """Should return garden state."""
        response = client.get("/v1/gardener/garden")

        assert response.status_code == 200
        data = response.json()

        # Check required fields
        assert "garden_id" in data
        assert "name" in data
        assert "season" in data
        assert "plots" in data
        assert "metrics" in data
        assert "computed" in data

    def test_get_garden_has_default_plots(self, client):
        """Should have crown jewel plots by default."""
        response = client.get("/v1/gardener/garden")
        data = response.json()

        # Should have crown jewel plots
        plots = data["plots"]
        assert len(plots) > 0

        # Check for expected plots
        plot_names = list(plots.keys())
        assert "atelier" in plot_names or any("atelier" in p for p in plot_names)

    def test_get_garden_has_computed_fields(self, client):
        """Should include computed fields."""
        response = client.get("/v1/gardener/garden")
        data = response.json()

        computed = data["computed"]
        assert "health_score" in computed
        assert "entropy_remaining" in computed
        assert "entropy_percentage" in computed
        assert "season_plasticity" in computed

    def test_get_garden_season_is_valid(self, client):
        """Season should be a valid enum value."""
        response = client.get("/v1/gardener/garden")
        data = response.json()

        valid_seasons = ["DORMANT", "SPROUTING", "BLOOMING", "HARVEST", "COMPOSTING"]
        assert data["season"] in valid_seasons


class TestGardenTend:
    """Tests for POST /v1/gardener/garden/tend."""

    def test_tend_observe_succeeds(self, client):
        """OBSERVE gesture should succeed."""
        response = client.post(
            "/v1/gardener/garden/tend",
            json={
                "verb": "OBSERVE",
                "target": "concept.gardener",
                "tone": 0.5,
                "reasoning": "Observing garden state",
            },
        )

        assert response.status_code == 200
        data = response.json()

        assert data["accepted"] is True
        assert data["gesture"]["verb"] == "OBSERVE"
        assert data["gesture"]["target"] == "concept.gardener"

    def test_tend_water_triggers_synergy(self, client):
        """WATER gesture on prompt should trigger TextGRAD synergy."""
        response = client.post(
            "/v1/gardener/garden/tend",
            json={
                "verb": "WATER",
                "target": "concept.prompt.task.test",
                "tone": 0.7,
                "reasoning": "Improving prompt with feedback",
            },
        )

        assert response.status_code == 200
        data = response.json()

        assert data["accepted"] is True
        # WATER on prompt should trigger TextGRAD synergy
        assert "textgrad:improvement_proposed" in data["synergies_triggered"]

    def test_tend_graft_records_change(self, client):
        """GRAFT gesture should record state change."""
        response = client.post(
            "/v1/gardener/garden/tend",
            json={
                "verb": "GRAFT",
                "target": "concept.prompt.new_task",
                "tone": 0.8,
                "reasoning": "Adding new prompt type",
            },
        )

        assert response.status_code == 200
        data = response.json()

        assert data["accepted"] is True
        assert data["state_changed"] is True
        assert len(data["changes"]) > 0

    def test_tend_wait_is_free(self, client):
        """WAIT gesture should have zero entropy cost."""
        response = client.post(
            "/v1/gardener/garden/tend",
            json={
                "verb": "WAIT",
                "target": "",
                "tone": 0.0,
                "reasoning": "Allowing time to pass",
            },
        )

        assert response.status_code == 200
        data = response.json()

        assert data["accepted"] is True
        assert data["gesture"]["entropy_cost"] == 0.0

    def test_tend_requires_verb(self, client):
        """Should require verb field."""
        response = client.post(
            "/v1/gardener/garden/tend",
            json={
                "target": "concept.gardener",
            },
        )

        assert response.status_code == 422  # Validation error

    def test_tend_validates_tone_range(self, client):
        """Tone should be between 0 and 1."""
        response = client.post(
            "/v1/gardener/garden/tend",
            json={
                "verb": "OBSERVE",
                "target": "concept.gardener",
                "tone": 1.5,  # Invalid - out of range
            },
        )

        assert response.status_code == 422


class TestGardenSeasonTransition:
    """Tests for POST /v1/gardener/garden/season."""

    def test_transition_to_sprouting(self, client):
        """Should transition to SPROUTING season."""
        response = client.post(
            "/v1/gardener/garden/season",
            json={
                "new_season": "SPROUTING",
                "reason": "Starting new development phase",
            },
        )

        assert response.status_code == 200
        data = response.json()

        assert data["season"] == "SPROUTING"

    def test_transition_updates_plasticity(self, client):
        """Season transition should update plasticity."""
        # First set to DORMANT (low plasticity)
        client.post(
            "/v1/gardener/garden/season",
            json={"new_season": "DORMANT", "reason": "Resting"},
        )

        response = client.get("/v1/gardener/garden")
        dormant_plasticity = response.json()["computed"]["season_plasticity"]

        # Now transition to SPROUTING (high plasticity)
        client.post(
            "/v1/gardener/garden/season",
            json={"new_season": "SPROUTING", "reason": "Growing"},
        )

        response = client.get("/v1/gardener/garden")
        sprouting_plasticity = response.json()["computed"]["season_plasticity"]

        # SPROUTING should have higher plasticity than DORMANT
        assert sprouting_plasticity > dormant_plasticity

    def test_transition_records_gesture(self, client):
        """Season transition should record a ROTATE gesture."""
        response = client.post(
            "/v1/gardener/garden/season",
            json={"new_season": "HARVEST", "reason": "Time to gather"},
        )

        assert response.status_code == 200

        # Get garden and check gestures
        garden = client.get("/v1/gardener/garden").json()
        recent_gestures = garden["recent_gestures"]

        # Should have a ROTATE gesture for season change
        rotate_gestures = [g for g in recent_gestures if g["verb"] == "ROTATE"]
        assert len(rotate_gestures) > 0

    def test_invalid_season_fails(self, client):
        """Invalid season should fail validation."""
        response = client.post(
            "/v1/gardener/garden/season",
            json={"new_season": "INVALID_SEASON"},
        )

        assert response.status_code == 422


class TestGardenPlotFocus:
    """Tests for POST /v1/gardener/garden/plot/{name}/focus."""

    def test_focus_existing_plot(self, client):
        """Should set active plot."""
        # First get available plots
        garden = client.get("/v1/gardener/garden").json()
        plot_names = list(garden["plots"].keys())

        if len(plot_names) == 0:
            pytest.skip("No plots available")

        plot_name = plot_names[0]

        response = client.post(f"/v1/gardener/garden/plot/{plot_name}/focus")

        assert response.status_code == 200
        data = response.json()

        assert data["active_plot"] == plot_name

    def test_focus_nonexistent_plot_fails(self, client):
        """Should return 404 for nonexistent plot."""
        response = client.post("/v1/gardener/garden/plot/nonexistent-plot-xyz/focus")

        assert response.status_code == 404


class TestGardenIntegration:
    """Integration tests for garden workflow."""

    def test_full_tending_workflow(self, client):
        """Test a complete tending workflow."""
        # 1. Get initial garden state
        initial = client.get("/v1/gardener/garden").json()
        initial_health = initial["computed"]["health_score"]

        # 2. Transition to SPROUTING for active development
        client.post(
            "/v1/gardener/garden/season",
            json={"new_season": "SPROUTING", "reason": "Starting work"},
        )

        # 3. Focus on a plot
        plot_names = list(initial["plots"].keys())
        if plot_names:
            client.post(f"/v1/gardener/garden/plot/{plot_names[0]}/focus")

        # 4. Apply some tending gestures
        client.post(
            "/v1/gardener/garden/tend",
            json={
                "verb": "OBSERVE",
                "target": "concept.gardener",
                "reasoning": "Surveying the garden",
            },
        )

        client.post(
            "/v1/gardener/garden/tend",
            json={
                "verb": "WATER",
                "target": "concept.prompt.task",
                "tone": 0.6,
                "reasoning": "Nurturing prompts",
            },
        )

        # 5. Verify state was updated
        final = client.get("/v1/gardener/garden").json()

        # Should have more gestures
        assert len(final["recent_gestures"]) > len(initial["recent_gestures"])

        # Should still be in SPROUTING
        assert final["season"] == "SPROUTING"
