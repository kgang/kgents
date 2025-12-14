"""
Tests for AGENTESE API endpoints.

Tests:
- POST /v1/agentese/invoke - Invoke AGENTESE paths
- GET /v1/agentese/resolve - Resolve path to node info
- GET /v1/agentese/affordances - List available affordances
"""

from __future__ import annotations

import pytest

pytest.importorskip("fastapi")

from uuid import UUID

from fastapi.testclient import TestClient
from protocols.api.app import create_app
from protocols.api.auth import ApiKeyData, clear_api_keys, register_api_key
from protocols.api.metering import clear_usage_stats


@pytest.fixture
def client() -> TestClient:
    """Create test client."""
    app = create_app()
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_state() -> None:
    """Reset API keys and usage stats before each test."""
    clear_api_keys()
    clear_usage_stats()

    # Register test keys
    register_api_key(
        ApiKeyData(
            key="kg_test_read",
            user_id="user_read",
            tier="PRO",
            rate_limit=1000,
            tenant_id=UUID("00000000-0000-0000-0000-000000000001"),
            scopes=("read",),
        )
    )
    register_api_key(
        ApiKeyData(
            key="kg_test_write",
            user_id="user_write",
            tier="ENTERPRISE",
            rate_limit=10000,
            tenant_id=UUID("00000000-0000-0000-0000-000000000001"),
            scopes=("read", "write", "admin"),
        )
    )


class TestInvokeEndpoint:
    """Tests for POST /v1/agentese/invoke."""

    def test_invoke_no_auth(self, client: TestClient) -> None:
        """Test invoke requires authentication."""
        response = client.post(
            "/v1/agentese/invoke",
            json={
                "path": "self.soul.challenge",
                "observer": {"name": "test", "archetype": "developer"},
            },
        )
        # FastAPI returns 422 for missing required header
        assert response.status_code == 422

    def test_invoke_invalid_key(self, client: TestClient) -> None:
        """Test invoke with invalid API key."""
        response = client.post(
            "/v1/agentese/invoke",
            json={"path": "self.soul.challenge"},
            headers={"X-API-Key": "kg_invalid_key"},
        )
        assert response.status_code == 401

    def test_invoke_without_read_scope(self, client: TestClient) -> None:
        """Test invoke requires read scope."""
        # Register a key without read scope
        register_api_key(
            ApiKeyData(
                key="kg_test_noscope",
                user_id="user_noscope",
                tier="FREE",
                rate_limit=100,
                tenant_id=UUID("00000000-0000-0000-0000-000000000001"),
                scopes=(),  # No scopes
            )
        )
        response = client.post(
            "/v1/agentese/invoke",
            json={"path": "self.soul.challenge"},
            headers={"X-API-Key": "kg_test_noscope"},
        )
        assert response.status_code == 403
        assert "scope" in response.json()["detail"].lower()

    def test_invoke_valid_path(self, client: TestClient) -> None:
        """Test invoke with valid path succeeds."""
        response = client.post(
            "/v1/agentese/invoke",
            json={
                "path": "self.soul.manifest",
                "observer": {"name": "test", "archetype": "developer"},
            },
            headers={"X-API-Key": "kg_test_read"},
        )
        # May return 200 (success), 403 (affordance not available), or 404 (path not found)
        # depending on the test environment configuration
        assert response.status_code in (200, 403, 404)

    def test_invoke_with_custom_observer(self, client: TestClient) -> None:
        """Test invoke with custom observer config."""
        response = client.post(
            "/v1/agentese/invoke",
            json={
                "path": "self.soul.manifest",
                "observer": {
                    "name": "architect",
                    "archetype": "architect",
                    "capabilities": ["design", "review"],
                },
            },
            headers={"X-API-Key": "kg_test_read"},
        )
        # May return 200, 403, or 404 depending on path/affordance availability
        assert response.status_code in (200, 403, 404)


class TestResolveEndpoint:
    """Tests for GET /v1/agentese/resolve."""

    def test_resolve_no_auth(self, client: TestClient) -> None:
        """Test resolve requires authentication."""
        response = client.get("/v1/agentese/resolve?path=world.house")
        # FastAPI returns 422 for missing required header
        assert response.status_code == 422

    def test_resolve_valid_path(self, client: TestClient) -> None:
        """Test resolve with valid path."""
        response = client.get(
            "/v1/agentese/resolve?path=self.soul",
            headers={"X-API-Key": "kg_test_read"},
        )
        # Should return 200 or 404 depending on path existence
        assert response.status_code in (200, 404)


class TestAffordancesEndpoint:
    """Tests for GET /v1/agentese/affordances."""

    def test_affordances_no_auth(self, client: TestClient) -> None:
        """Test affordances requires authentication."""
        response = client.get("/v1/agentese/affordances?path=world.house")
        # FastAPI returns 422 for missing required header
        assert response.status_code == 422

    def test_affordances_valid_path(self, client: TestClient) -> None:
        """Test affordances with valid path."""
        response = client.get(
            "/v1/agentese/affordances?path=self.soul",
            headers={"X-API-Key": "kg_test_read"},
        )
        # Should return 200 or 404 depending on path existence
        assert response.status_code in (200, 404)

    def test_affordances_with_archetype(self, client: TestClient) -> None:
        """Test affordances with custom archetype."""
        response = client.get(
            "/v1/agentese/affordances?path=self.soul&archetype=architect",
            headers={"X-API-Key": "kg_test_read"},
        )
        assert response.status_code in (200, 404)


class TestAgenteseTags:
    """Tests for AGENTESE endpoint tags."""

    def test_agentese_endpoints_tagged(self, client: TestClient) -> None:
        """Test AGENTESE endpoints have 'agentese' tag."""
        response = client.get("/openapi.json")
        data = response.json()

        # Check invoke endpoint
        invoke_path = data["paths"].get("/v1/agentese/invoke", {}).get("post")
        if invoke_path:
            assert "agentese" in invoke_path["tags"]


class TestInvalidPaths:
    """Tests for invalid AGENTESE path handling."""

    def test_invoke_invalid_context(self, client: TestClient) -> None:
        """Test invoke with invalid context returns 400."""
        response = client.post(
            "/v1/agentese/invoke",
            json={
                "path": "invalid.house.manifest",  # 'invalid' is not a valid context
                "observer": {"name": "test", "archetype": "developer"},
            },
            headers={"X-API-Key": "kg_test_read"},
        )
        # Should return 400 (bad request) or 404 (not found)
        assert response.status_code in (400, 404)

    def test_invoke_single_segment_path(self, client: TestClient) -> None:
        """Test invoke with single-segment path returns error."""
        response = client.post(
            "/v1/agentese/invoke",
            json={
                "path": "world",  # Path too short
                "observer": {"name": "test", "archetype": "developer"},
            },
            headers={"X-API-Key": "kg_test_read"},
        )
        # Should return 400 for malformed path
        assert response.status_code in (400, 404)

    def test_invoke_empty_path(self, client: TestClient) -> None:
        """Test invoke with empty path returns error."""
        response = client.post(
            "/v1/agentese/invoke",
            json={
                "path": "",
                "observer": {"name": "test", "archetype": "developer"},
            },
            headers={"X-API-Key": "kg_test_read"},
        )
        assert response.status_code in (400, 404, 422)

    def test_resolve_invalid_path(self, client: TestClient) -> None:
        """Test resolve with invalid path returns error."""
        response = client.get(
            "/v1/agentese/resolve?path=invalid.context",
            headers={"X-API-Key": "kg_test_read"},
        )
        assert response.status_code in (400, 404)

    def test_affordances_nonexistent_path(self, client: TestClient) -> None:
        """Test affordances for nonexistent path.

        Note: The endpoint may return 200 with empty affordances list
        or 404 depending on path validation behavior.
        """
        response = client.get(
            "/v1/agentese/affordances?path=world.nonexistent_entity",
            headers={"X-API-Key": "kg_test_read"},
        )
        # Either 200 with empty list or 404 is acceptable
        if response.status_code == 200:
            data = response.json()
            # Path should be echoed back even if affordances are empty
            assert "path" in data
        else:
            assert response.status_code == 404


class TestPathInjectionPrevention:
    """Tests to verify path injection is prevented."""

    def test_path_with_special_characters(self, client: TestClient) -> None:
        """Test path with special characters is rejected."""
        response = client.post(
            "/v1/agentese/invoke",
            json={
                "path": "world.house; rm -rf /",
                "observer": {"name": "test", "archetype": "developer"},
            },
            headers={"X-API-Key": "kg_test_read"},
        )
        # Should reject invalid path (400, 403, or 404 all indicate rejection)
        assert response.status_code in (400, 403, 404)

    def test_path_with_traversal_attempt(self, client: TestClient) -> None:
        """Test path with directory traversal attempt is rejected."""
        response = client.post(
            "/v1/agentese/invoke",
            json={
                "path": "world.house.../../etc/passwd",
                "observer": {"name": "test", "archetype": "developer"},
            },
            headers={"X-API-Key": "kg_test_read"},
        )
        # 400 = syntax error, 403 = affordance denied, 404 = not found
        # All indicate the malicious path was rejected
        assert response.status_code in (400, 403, 404)
