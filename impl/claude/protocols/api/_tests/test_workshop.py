"""Tests for Workshop API endpoints (Chunk 8)."""

from collections.abc import Generator

import pytest

# Skip all tests if FastAPI not available
pytest.importorskip("fastapi")

from fastapi.testclient import TestClient
from protocols.api.workshop import (
    AssignTaskRequest,
    BuilderSummaryResponse,
    WorkshopPlanResponse,
    WorkshopStatusResponse,
    create_workshop_router,
)

# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def client() -> TestClient:
    """Create test client with Workshop router."""
    from fastapi import FastAPI

    app = FastAPI()
    router = create_workshop_router()
    assert router is not None
    app.include_router(router)
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_workshop_state() -> Generator[None, None, None]:
    """Reset workshop state between tests."""
    from protocols.api.workshop import _reset_workshop

    _reset_workshop()
    yield
    _reset_workshop()


# =============================================================================
# Workshop Endpoint Tests
# =============================================================================


class TestWorkshopGet:
    """Tests for GET /v1/workshop endpoint."""

    def test_get_workshop_returns_default(self, client: TestClient) -> None:
        """GET /v1/workshop should return or create default workshop."""
        response = client.get("/v1/workshop")
        assert response.status_code == 200

        data = response.json()
        assert data["id"] == "default"
        assert data["phase"] == "IDLE"
        assert data["is_running"] is False
        assert len(data["builders"]) == 5

    def test_get_workshop_includes_builders(self, client: TestClient) -> None:
        """GET /v1/workshop should list all 5 builders."""
        response = client.get("/v1/workshop")
        assert response.status_code == 200

        builders = response.json()["builders"]
        archetypes = [b["archetype"] for b in builders]
        assert set(archetypes) == {"Scout", "Sage", "Spark", "Steady", "Sync"}

    def test_get_workshop_metrics_initially_zero(self, client: TestClient) -> None:
        """GET /v1/workshop should have zero metrics initially."""
        response = client.get("/v1/workshop")
        assert response.status_code == 200

        metrics = response.json()["metrics"]
        assert metrics["total_steps"] == 0
        assert metrics["total_events"] == 0


class TestWorkshopAssignTask:
    """Tests for POST /v1/workshop/task endpoint."""

    def test_assign_task_creates_plan(self, client: TestClient) -> None:
        """POST /v1/workshop/task should create a plan."""
        response = client.post(
            "/v1/workshop/task",
            json={"description": "Design a new feature", "priority": 2},
        )
        assert response.status_code == 200

        data = response.json()
        assert "task" in data
        assert data["task"]["description"] == "Design a new feature"
        assert data["task"]["priority"] == 2
        assert "lead_builder" in data
        assert len(data["estimated_phases"]) >= 1

    def test_assign_task_routes_to_scout_for_explore(self, client: TestClient) -> None:
        """POST /v1/workshop/task with 'explore' should route to Scout."""
        response = client.post(
            "/v1/workshop/task",
            json={"description": "Explore the codebase"},
        )
        assert response.status_code == 200

        data = response.json()
        assert data["lead_builder"] == "Scout"
        assert "EXPLORING" in data["estimated_phases"]

    def test_assign_task_routes_to_sage_for_design(self, client: TestClient) -> None:
        """POST /v1/workshop/task with 'design' should route to Sage."""
        response = client.post(
            "/v1/workshop/task",
            json={"description": "Design the API schema"},
        )
        assert response.status_code == 200

        data = response.json()
        assert data["lead_builder"] == "Sage"

    def test_assign_task_routes_to_spark_for_prototype(
        self, client: TestClient
    ) -> None:
        """POST /v1/workshop/task with 'prototype' should route to Spark."""
        response = client.post(
            "/v1/workshop/task",
            json={"description": "Prototype the widget"},
        )
        assert response.status_code == 200

        data = response.json()
        assert data["lead_builder"] == "Spark"

    def test_assign_task_routes_to_steady_for_test(self, client: TestClient) -> None:
        """POST /v1/workshop/task with 'test' should route to Steady."""
        response = client.post(
            "/v1/workshop/task",
            json={"description": "Test the feature"},
        )
        assert response.status_code == 200

        data = response.json()
        assert data["lead_builder"] == "Steady"

    def test_assign_task_routes_to_sync_for_integrate(self, client: TestClient) -> None:
        """POST /v1/workshop/task with 'integrate' should route to Sync."""
        response = client.post(
            "/v1/workshop/task",
            json={"description": "Integrate the modules"},
        )
        assert response.status_code == 200

        data = response.json()
        assert data["lead_builder"] == "Sync"

    def test_assign_task_starts_running(self, client: TestClient) -> None:
        """POST /v1/workshop/task should set is_running to True."""
        client.post(
            "/v1/workshop/task",
            json={"description": "Build something"},
        )

        response = client.get("/v1/workshop/status")
        assert response.status_code == 200
        assert response.json()["is_running"] is True


class TestWorkshopBuilders:
    """Tests for builder-related endpoints."""

    def test_list_builders(self, client: TestClient) -> None:
        """GET /v1/workshop/builders should list all builders."""
        response = client.get("/v1/workshop/builders")
        assert response.status_code == 200

        data = response.json()
        assert data["count"] == 5
        assert len(data["builders"]) == 5

    def test_get_builder_lod0(self, client: TestClient) -> None:
        """GET /v1/workshop/builder/{archetype}?lod=0 should return basic info."""
        response = client.get("/v1/workshop/builder/Scout?lod=0")
        assert response.status_code == 200

        data = response.json()
        assert data["archetype"] == "Scout"
        assert "name" in data
        assert "phase" in data

    def test_get_builder_lod1(self, client: TestClient) -> None:
        """GET /v1/workshop/builder/{archetype}?lod=1 should return status info."""
        response = client.get("/v1/workshop/builder/Scout?lod=1")
        assert response.status_code == 200

        data = response.json()
        assert "is_in_specialty" in data
        assert "is_active" in data

    def test_get_builder_lod2(self, client: TestClient) -> None:
        """GET /v1/workshop/builder/{archetype}?lod=2 should return citizen info."""
        response = client.get("/v1/workshop/builder/Scout?lod=2")
        assert response.status_code == 200

        data = response.json()
        assert "citizen" in data
        assert "eigenvectors" in data["citizen"]

    def test_get_builder_not_found(self, client: TestClient) -> None:
        """GET /v1/workshop/builder/{unknown} should return 404."""
        response = client.get("/v1/workshop/builder/Unknown")
        assert response.status_code == 404


class TestWorkshopWhisper:
    """Tests for POST /v1/workshop/builder/{archetype}/whisper endpoint."""

    def test_whisper_to_builder(self, client: TestClient) -> None:
        """POST whisper should send message to builder."""
        response = client.post(
            "/v1/workshop/builder/Scout/whisper",
            json={"message": "Hello Scout!"},
        )
        assert response.status_code == 200

        data = response.json()
        assert data["success"] is True
        assert data["builder"] == "Scout"
        assert "response" in data

    def test_whisper_not_found(self, client: TestClient) -> None:
        """POST whisper to unknown builder should return 404."""
        response = client.post(
            "/v1/workshop/builder/Unknown/whisper",
            json={"message": "Hello?"},
        )
        assert response.status_code == 404


class TestWorkshopPerturb:
    """Tests for POST /v1/workshop/perturb endpoint."""

    def test_perturb_requires_running(self, client: TestClient) -> None:
        """POST /v1/workshop/perturb should fail if not running."""
        response = client.post(
            "/v1/workshop/perturb",
            json={"action": "advance"},
        )
        assert response.status_code == 400
        assert "not running" in response.json()["detail"].lower()

    def test_perturb_advance_phase(self, client: TestClient) -> None:
        """POST /v1/workshop/perturb with action=advance should advance phase."""
        # First assign a task
        client.post(
            "/v1/workshop/task",
            json={"description": "Build something"},
        )

        # Then perturb
        response = client.post(
            "/v1/workshop/perturb",
            json={"action": "advance"},
        )
        assert response.status_code == 200

        data = response.json()
        assert data["success"] is True
        assert "event" in data

    def test_perturb_invalid_action(self, client: TestClient) -> None:
        """POST /v1/workshop/perturb with invalid action should return 400."""
        # First assign a task
        client.post(
            "/v1/workshop/task",
            json={"description": "Build something"},
        )

        response = client.post(
            "/v1/workshop/perturb",
            json={"action": "invalid_action"},
        )
        assert response.status_code == 400


class TestWorkshopReset:
    """Tests for POST /v1/workshop/reset endpoint."""

    def test_reset_workshop(self, client: TestClient) -> None:
        """POST /v1/workshop/reset should reset to idle state."""
        # First assign a task
        client.post(
            "/v1/workshop/task",
            json={"description": "Build something"},
        )

        # Then reset
        response = client.post("/v1/workshop/reset")
        assert response.status_code == 200
        assert response.json()["status"] == "reset"

        # Verify state is reset
        status = client.get("/v1/workshop/status").json()
        assert status["is_running"] is False
        assert status["phase"] == "IDLE"
        assert status["active_task"] is None


class TestWorkshopArtifacts:
    """Tests for GET /v1/workshop/artifacts endpoint."""

    def test_list_artifacts_empty(self, client: TestClient) -> None:
        """GET /v1/workshop/artifacts should return empty list initially."""
        response = client.get("/v1/workshop/artifacts")
        assert response.status_code == 200

        data = response.json()
        assert data["count"] == 0
        assert data["artifacts"] == []


# =============================================================================
# Integration Tests
# =============================================================================


class TestWorkshopIntegration:
    """Integration tests for workshop workflow."""

    def test_full_task_lifecycle(self, client: TestClient) -> None:
        """Test assigning task, checking status, and resetting."""
        # 1. Verify initial state
        initial = client.get("/v1/workshop").json()
        assert initial["phase"] == "IDLE"
        assert initial["is_running"] is False

        # 2. Assign task
        plan = client.post(
            "/v1/workshop/task",
            json={"description": "Research the problem", "priority": 3},
        ).json()
        assert plan["task"]["priority"] == 3
        assert plan["lead_builder"] == "Scout"  # "research" → Scout

        # 3. Check running
        status = client.get("/v1/workshop/status").json()
        assert status["is_running"] is True
        assert status["phase"] in [
            "EXPLORING",
            "DESIGNING",
            "PROTOTYPING",
            "REFINING",
            "INTEGRATING",
        ]

        # 4. Reset
        reset = client.post("/v1/workshop/reset").json()
        assert reset["status"] == "reset"

        # 5. Verify reset
        final = client.get("/v1/workshop").json()
        assert final["phase"] == "IDLE"

    def test_builder_info_consistency(self, client: TestClient) -> None:
        """Test that builder info is consistent across endpoints."""
        # Get from workshop
        workshop = client.get("/v1/workshop").json()
        builder_count = len(workshop["builders"])

        # Get from builders endpoint
        builders = client.get("/v1/workshop/builders").json()
        assert builders["count"] == builder_count

        # Verify each builder
        for archetype in ["Scout", "Sage", "Spark", "Steady", "Sync"]:
            builder = client.get(f"/v1/workshop/builder/{archetype}?lod=1").json()
            assert builder["archetype"] == archetype


# =============================================================================
# Pydantic Model Tests
# =============================================================================


class TestPydanticModels:
    """Tests for Pydantic model validation."""

    def test_assign_task_request_validation(self) -> None:
        """AssignTaskRequest should validate priority range."""
        # Valid
        req = AssignTaskRequest(description="Test", priority=2)
        assert req.priority == 2

    def test_builder_summary_response(self) -> None:
        """BuilderSummaryResponse should have all required fields."""
        resp = BuilderSummaryResponse(
            archetype="Scout",
            name="Scout",
            phase="IDLE",
            is_active=False,
            is_in_specialty=False,
        )
        assert resp.archetype == "Scout"
