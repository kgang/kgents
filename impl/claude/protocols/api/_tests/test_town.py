"""Tests for Agent Town API endpoints."""

import pytest

# Skip all tests if FastAPI not available
pytest.importorskip("fastapi")

from fastapi.testclient import TestClient
from protocols.api.town import (
    CitizenDetailResponse,
    CitizensResponse,
    CoalitionsResponse,
    CreateTownRequest,
    StepResponse,
    TownResponse,
    create_town_router,
)

# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def client() -> TestClient:
    """Create test client with Town router."""
    from fastapi import FastAPI

    app = FastAPI()
    router = create_town_router()
    assert router is not None
    app.include_router(router)
    return TestClient(app)


@pytest.fixture
def town_id(client: TestClient) -> str:
    """Create a town and return its ID."""
    response = client.post(
        "/v1/town",
        json={"phase": 4, "name": "test-town"},
    )
    assert response.status_code == 200
    town_id_str: str = response.json()["id"]
    return town_id_str


# =============================================================================
# Town CRUD Tests
# =============================================================================


class TestTownCRUD:
    """Tests for town creation, read, delete."""

    def test_create_town_phase4(self, client: TestClient) -> None:
        """POST /v1/town should create Phase 4 town."""
        response = client.post(
            "/v1/town",
            json={"phase": 4, "name": "my-town"},
        )
        assert response.status_code == 200

        data = response.json()
        assert data["name"] == "my-town"
        assert data["citizen_count"] == 25  # Phase 4 has 25 citizens
        assert data["region_count"] == 8  # Phase 4 has 8 regions
        assert data["status"] == "active"

    def test_create_town_phase3(self, client: TestClient) -> None:
        """POST /v1/town with phase=3 should create Phase 3 town."""
        response = client.post(
            "/v1/town",
            json={"phase": 3},
        )
        assert response.status_code == 200

        data = response.json()
        assert data["citizen_count"] == 10  # Phase 3 has 10 citizens

    def test_get_town(self, client: TestClient, town_id: str) -> None:
        """GET /v1/town/{id} should return town state."""
        response = client.get(f"/v1/town/{town_id}")
        assert response.status_code == 200

        data = response.json()
        assert data["id"] == town_id
        assert data["citizen_count"] == 25
        assert "coalition_count" in data

    def test_get_town_not_found(self, client: TestClient) -> None:
        """GET /v1/town/{id} should return 404 for unknown town."""
        response = client.get("/v1/town/nonexistent")
        assert response.status_code == 404

    def test_delete_town(self, client: TestClient, town_id: str) -> None:
        """DELETE /v1/town/{id} should remove town."""
        response = client.delete(f"/v1/town/{town_id}")
        assert response.status_code == 200
        assert response.json()["status"] == "deleted"

        # Verify deleted
        response = client.get(f"/v1/town/{town_id}")
        assert response.status_code == 404


# =============================================================================
# Citizens Tests
# =============================================================================


class TestCitizensEndpoint:
    """Tests for citizens endpoint."""

    def test_get_citizens(self, client: TestClient, town_id: str) -> None:
        """GET /v1/town/{id}/citizens should return citizen list."""
        response = client.get(f"/v1/town/{town_id}/citizens")
        assert response.status_code == 200

        data = response.json()
        assert data["town_id"] == town_id
        assert data["total"] == 25
        assert len(data["citizens"]) == 25

        # Check citizen structure
        citizen = data["citizens"][0]
        assert "id" in citizen
        assert "name" in citizen
        assert "archetype" in citizen
        assert "region" in citizen
        assert "is_evolving" in citizen

    def test_citizens_by_archetype(self, client: TestClient, town_id: str) -> None:
        """Citizens response should include archetype counts."""
        response = client.get(f"/v1/town/{town_id}/citizens")
        data = response.json()

        # Phase 4 has these archetypes
        archetypes = data["by_archetype"]
        assert "Builder" in archetypes
        assert "Trader" in archetypes
        assert "Healer" in archetypes
        assert "Scholar" in archetypes
        assert "Watcher" in archetypes

    def test_citizens_by_region(self, client: TestClient, town_id: str) -> None:
        """Citizens response should include region counts."""
        response = client.get(f"/v1/town/{town_id}/citizens")
        data = response.json()

        regions = data["by_region"]
        assert "inn" in regions
        assert "square" in regions
        assert "workshop" in regions  # Phase 4 region


# =============================================================================
# Citizen Detail Tests
# =============================================================================


class TestCitizenDetail:
    """Tests for citizen detail endpoint."""

    def test_get_citizen_lod_0(self, client: TestClient, town_id: str) -> None:
        """GET /v1/town/{id}/citizen/{name}?lod=0 should return silhouette."""
        response = client.get(f"/v1/town/{town_id}/citizen/Alice?lod=0")
        assert response.status_code == 200

        data = response.json()
        assert data["lod"] == 0
        assert data["citizen"]["name"] == "Alice"
        assert "region" in data["citizen"]
        # LOD 0 should not have eigenvectors
        assert "eigenvectors" not in data["citizen"]

    def test_get_citizen_lod_3(self, client: TestClient, town_id: str) -> None:
        """GET /v1/town/{id}/citizen/{name}?lod=3 should include eigenvectors."""
        response = client.get(f"/v1/town/{town_id}/citizen/Alice?lod=3")
        assert response.status_code == 200

        data = response.json()
        assert data["lod"] == 3
        assert "eigenvectors" in data["citizen"]
        assert "warmth" in data["citizen"]["eigenvectors"]
        # Phase 4: 7D eigenvectors
        assert "resilience" in data["citizen"]["eigenvectors"]
        assert "ambition" in data["citizen"]["eigenvectors"]

    def test_get_citizen_lod_5(self, client: TestClient, town_id: str) -> None:
        """GET /v1/town/{id}/citizen/{name}?lod=5 should include opacity."""
        response = client.get(f"/v1/town/{town_id}/citizen/Alice?lod=5")
        assert response.status_code == 200

        data = response.json()
        assert data["lod"] == 5
        assert "opacity" in data["citizen"]

    def test_get_citizen_not_found(self, client: TestClient, town_id: str) -> None:
        """GET /v1/town/{id}/citizen/{name} should return 404 for unknown."""
        response = client.get(f"/v1/town/{town_id}/citizen/Nonexistent")
        assert response.status_code == 404


# =============================================================================
# Coalitions Tests
# =============================================================================


class TestCoalitionsEndpoint:
    """Tests for coalitions endpoint."""

    def test_get_coalitions(self, client: TestClient, town_id: str) -> None:
        """GET /v1/town/{id}/coalitions should return coalition list."""
        response = client.get(f"/v1/town/{town_id}/coalitions")
        assert response.status_code == 200

        data = response.json()
        assert data["town_id"] == town_id
        assert "coalitions" in data
        assert "total" in data
        assert "bridge_citizens" in data

    def test_coalition_structure(self, client: TestClient, town_id: str) -> None:
        """Coalition entries should have correct structure."""
        response = client.get(f"/v1/town/{town_id}/coalitions")
        data = response.json()

        if data["coalitions"]:
            coalition = data["coalitions"][0]
            assert "id" in coalition
            assert "name" in coalition
            assert "members" in coalition
            assert "size" in coalition
            assert "strength" in coalition


# =============================================================================
# Step Simulation Tests
# =============================================================================


class TestStepEndpoint:
    """Tests for step simulation endpoint."""

    def test_step_one_cycle(self, client: TestClient, town_id: str) -> None:
        """POST /v1/town/{id}/step should advance simulation."""
        response = client.post(
            f"/v1/town/{town_id}/step",
            json={"cycles": 1},
        )
        assert response.status_code == 200

        data = response.json()
        assert data["town_id"] == town_id
        assert data["cycles_run"] == 1
        assert "evolving_citizens_updated" in data
        assert "coalitions_detected" in data

    def test_step_multiple_cycles(self, client: TestClient, town_id: str) -> None:
        """POST /v1/town/{id}/step should support multiple cycles."""
        response = client.post(
            f"/v1/town/{town_id}/step",
            json={"cycles": 5},
        )
        assert response.status_code == 200

        data = response.json()
        assert data["cycles_run"] == 5
        # 5 evolving citizens * 5 cycles = 25 updates
        assert data["evolving_citizens_updated"] == 25

    def test_step_without_decay(self, client: TestClient, town_id: str) -> None:
        """POST /v1/town/{id}/step with decay_coalitions=false."""
        response = client.post(
            f"/v1/town/{town_id}/step",
            json={"cycles": 1, "decay_coalitions": False},
        )
        assert response.status_code == 200

        data = response.json()
        assert data["coalitions_decayed"] == 0


# =============================================================================
# Reputation Tests
# =============================================================================


class TestReputationEndpoint:
    """Tests for reputation endpoint."""

    def test_get_reputation(self, client: TestClient, town_id: str) -> None:
        """GET /v1/town/{id}/reputation should return reputation scores."""
        response = client.get(f"/v1/town/{town_id}/reputation")
        assert response.status_code == 200

        data = response.json()
        assert data["town_id"] == town_id
        assert "reputation" in data
        assert data["total_citizens"] == 25

        if data["reputation"]:
            entry = data["reputation"][0]
            assert "citizen_id" in entry
            assert "name" in entry
            assert "reputation" in entry


# =============================================================================
# Integration Tests
# =============================================================================


class TestTownAPIIntegration:
    """Integration tests for Town API flow."""

    def test_full_lifecycle(self, client: TestClient) -> None:
        """Test complete town lifecycle: create -> step -> query -> delete."""
        # Create
        create_resp = client.post(
            "/v1/town",
            json={"phase": 4, "name": "lifecycle-test"},
        )
        assert create_resp.status_code == 200
        town_id = create_resp.json()["id"]

        # Get initial state
        state_resp = client.get(f"/v1/town/{town_id}")
        assert state_resp.json()["citizen_count"] == 25

        # Get citizens
        citizens_resp = client.get(f"/v1/town/{town_id}/citizens")
        assert citizens_resp.json()["total"] == 25

        # Step simulation
        step_resp = client.post(
            f"/v1/town/{town_id}/step",
            json={"cycles": 2},
        )
        assert step_resp.json()["cycles_run"] == 2

        # Get coalitions
        coalitions_resp = client.get(f"/v1/town/{town_id}/coalitions")
        assert "coalitions" in coalitions_resp.json()

        # Get reputation
        rep_resp = client.get(f"/v1/town/{town_id}/reputation")
        assert rep_resp.json()["total_citizens"] == 25

        # Delete
        delete_resp = client.delete(f"/v1/town/{town_id}")
        assert delete_resp.json()["status"] == "deleted"

        # Verify deleted
        get_resp = client.get(f"/v1/town/{town_id}")
        assert get_resp.status_code == 404


# =============================================================================
# Scatter Endpoint Tests (Phase 5)
# =============================================================================


class TestScatterEndpoint:
    """Tests for the scatter endpoint (Phase 5)."""

    def test_scatter_json_format(self, client: TestClient) -> None:
        """Scatter endpoint returns JSON by default."""
        # Create town
        create_resp = client.post("/v1/town", json={"phase": 4})
        assert create_resp.status_code == 200
        town_id = create_resp.json()["id"]

        # Get scatter
        scatter_resp = client.get(f"/v1/town/{town_id}/scatter")
        assert scatter_resp.status_code == 200

        data = scatter_resp.json()
        assert data["type"] == "eigenvector_scatter"
        assert "points" in data
        assert len(data["points"]) == 25  # Phase 4 has 25 citizens

        # Cleanup
        client.delete(f"/v1/town/{town_id}")

    def test_scatter_ascii_format(self, client: TestClient) -> None:
        """Scatter endpoint returns ASCII when format=ascii."""
        create_resp = client.post("/v1/town", json={"phase": 3})
        town_id = create_resp.json()["id"]

        scatter_resp = client.get(
            f"/v1/town/{town_id}/scatter",
            params={"format": "ascii"},
        )
        assert scatter_resp.status_code == 200

        data = scatter_resp.json()
        assert "scatter" in data
        assert "Eigenvector Space" in data["scatter"]
        assert "Citizens:" in data["scatter"]

        client.delete(f"/v1/town/{town_id}")

    def test_scatter_different_projections(self, client: TestClient) -> None:
        """Scatter endpoint respects projection parameter."""
        create_resp = client.post("/v1/town", json={"phase": 4})
        town_id = create_resp.json()["id"]

        # Test different projections
        for proj in ["PAIR_WT", "PAIR_CC", "PAIR_PR"]:
            scatter_resp = client.get(
                f"/v1/town/{town_id}/scatter",
                params={"projection": proj, "format": "json"},
            )
            assert scatter_resp.status_code == 200
            data = scatter_resp.json()
            assert data["projection"] == proj

        client.delete(f"/v1/town/{town_id}")

    def test_scatter_point_structure(self, client: TestClient) -> None:
        """Scatter points have correct structure."""
        create_resp = client.post("/v1/town", json={"phase": 4})
        town_id = create_resp.json()["id"]

        scatter_resp = client.get(f"/v1/town/{town_id}/scatter")
        data = scatter_resp.json()

        # Check first point structure
        point = data["points"][0]
        assert "citizen_id" in point
        assert "citizen_name" in point
        assert "archetype" in point
        assert "eigenvectors" in point
        assert "warmth" in point["eigenvectors"]
        assert "curiosity" in point["eigenvectors"]
        assert "trust" in point["eigenvectors"]
        assert "color" in point

        client.delete(f"/v1/town/{town_id}")

    def test_scatter_invalid_town(self, client: TestClient) -> None:
        """Scatter endpoint returns 404 for invalid town."""
        scatter_resp = client.get("/v1/town/invalid/scatter")
        assert scatter_resp.status_code == 404


# =============================================================================
# Events SSE Endpoint Tests (Phase 5)
# =============================================================================


class TestEventsEndpoint:
    """Tests for the SSE events endpoint (Phase 5)."""

    def test_events_invalid_town(self, client: TestClient) -> None:
        """Events endpoint returns 404 for invalid town."""
        events_resp = client.get("/v1/town/invalid/events")
        assert events_resp.status_code == 404

    def test_sse_endpoint_implementation(self) -> None:
        """Verify TownSSEEndpoint is properly integrated."""
        # Test the SSE endpoint implementation directly
        from agents.town.visualization import TownSSEEndpoint

        endpoint = TownSSEEndpoint("test-town")
        assert endpoint.town_id == "test-town"

        # Close without starting to avoid async issues
        endpoint.close()
        assert endpoint._closed is True
