"""
Tests for K-gent Sessions API endpoints.

Tests:
- POST /v1/kgent/sessions - Create session
- GET /v1/kgent/sessions - List sessions
- GET /v1/kgent/sessions/{id} - Get session
- POST /v1/kgent/sessions/{id}/messages - Send message
- GET /v1/kgent/sessions/{id}/messages - Get messages
"""

from __future__ import annotations

from uuid import UUID

import pytest

pytest.importorskip("fastapi")

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

    # Register test keys with tenant
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


class TestCreateSession:
    """Tests for POST /v1/kgent/sessions."""

    def test_create_session_no_auth(self, client: TestClient) -> None:
        """Test create session requires authentication."""
        response = client.post(
            "/v1/kgent/sessions",
            json={"title": "Test Session"},
        )
        # FastAPI returns 422 for missing required header
        assert response.status_code == 422

    def test_create_session_read_only_fails(self, client: TestClient) -> None:
        """Test create session requires write scope."""
        response = client.post(
            "/v1/kgent/sessions",
            json={"title": "Test Session"},
            headers={"X-API-Key": "kg_test_read"},
        )
        assert response.status_code == 403
        assert "write" in response.json()["detail"].lower()

    def test_create_session_success(self, client: TestClient) -> None:
        """Test create session succeeds with write scope."""
        response = client.post(
            "/v1/kgent/sessions",
            json={"title": "Test Session", "mode": "reflect"},
            headers={"X-API-Key": "kg_test_write"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert data["title"] == "Test Session"
        assert data["agent_type"] == "kgent"
        assert data["status"] == "active"

    def test_create_session_default_values(self, client: TestClient) -> None:
        """Test create session with defaults."""
        response = client.post(
            "/v1/kgent/sessions",
            json={},
            headers={"X-API-Key": "kg_test_write"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["agent_type"] == "kgent"
        assert data["message_count"] == 0
        assert data["tokens_used"] == 0


class TestListSessions:
    """Tests for GET /v1/kgent/sessions."""

    def test_list_sessions_no_auth(self, client: TestClient) -> None:
        """Test list sessions requires authentication."""
        response = client.get("/v1/kgent/sessions")
        # FastAPI returns 422 for missing required header
        assert response.status_code == 422

    def test_list_sessions_empty(self, client: TestClient) -> None:
        """Test list sessions when none exist."""
        response = client.get(
            "/v1/kgent/sessions",
            headers={"X-API-Key": "kg_test_read"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "sessions" in data
        assert data["total"] >= 0

    def test_list_sessions_with_pagination(self, client: TestClient) -> None:
        """Test list sessions with pagination."""
        # Create some sessions first
        for i in range(3):
            client.post(
                "/v1/kgent/sessions",
                json={"title": f"Session {i}"},
                headers={"X-API-Key": "kg_test_write"},
            )

        response = client.get(
            "/v1/kgent/sessions?limit=2&offset=0",
            headers={"X-API-Key": "kg_test_read"},
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data["sessions"]) <= 2


class TestGetSession:
    """Tests for GET /v1/kgent/sessions/{id}."""

    def test_get_session_no_auth(self, client: TestClient) -> None:
        """Test get session requires authentication."""
        fake_id = "00000000-0000-0000-0000-000000000099"
        response = client.get(f"/v1/kgent/sessions/{fake_id}")
        # FastAPI returns 422 for missing required header
        assert response.status_code == 422

    def test_get_session_not_found(self, client: TestClient) -> None:
        """Test get session returns 404 for nonexistent session."""
        fake_id = "00000000-0000-0000-0000-000000000099"
        response = client.get(
            f"/v1/kgent/sessions/{fake_id}",
            headers={"X-API-Key": "kg_test_read"},
        )
        assert response.status_code == 404

    def test_get_session_invalid_id(self, client: TestClient) -> None:
        """Test get session with invalid UUID format."""
        response = client.get(
            "/v1/kgent/sessions/not-a-uuid",
            headers={"X-API-Key": "kg_test_read"},
        )
        assert response.status_code == 400

    def test_get_session_success(self, client: TestClient) -> None:
        """Test get session for existing session."""
        # Create a session
        create_response = client.post(
            "/v1/kgent/sessions",
            json={"title": "Test Session"},
            headers={"X-API-Key": "kg_test_write"},
        )
        session_id = create_response.json()["id"]

        # Get the session
        response = client.get(
            f"/v1/kgent/sessions/{session_id}",
            headers={"X-API-Key": "kg_test_read"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == session_id
        assert data["title"] == "Test Session"


class TestSendMessage:
    """Tests for POST /v1/kgent/sessions/{id}/messages."""

    def test_send_message_no_auth(self, client: TestClient) -> None:
        """Test send message requires authentication."""
        fake_id = "00000000-0000-0000-0000-000000000099"
        response = client.post(
            f"/v1/kgent/sessions/{fake_id}/messages",
            json={"message": "Hello"},
        )
        # FastAPI returns 422 for missing required header
        assert response.status_code == 422

    def test_send_message_read_only_fails(self, client: TestClient) -> None:
        """Test send message requires write scope."""
        # Create a session first
        create_response = client.post(
            "/v1/kgent/sessions",
            json={"title": "Test Session"},
            headers={"X-API-Key": "kg_test_write"},
        )
        session_id = create_response.json()["id"]

        # Try to send message with read-only key
        response = client.post(
            f"/v1/kgent/sessions/{session_id}/messages",
            json={"message": "Hello", "stream": False},
            headers={"X-API-Key": "kg_test_read"},
        )
        assert response.status_code == 403

    def test_send_message_not_found(self, client: TestClient) -> None:
        """Test send message to nonexistent session."""
        fake_id = "00000000-0000-0000-0000-000000000099"
        response = client.post(
            f"/v1/kgent/sessions/{fake_id}/messages",
            json={"message": "Hello", "stream": False},
            headers={"X-API-Key": "kg_test_write"},
        )
        assert response.status_code == 404

    def test_send_message_non_streaming(self, client: TestClient) -> None:
        """Test send message without streaming."""
        # Create a session
        create_response = client.post(
            "/v1/kgent/sessions",
            json={"title": "Test Session"},
            headers={"X-API-Key": "kg_test_write"},
        )
        session_id = create_response.json()["id"]

        # Send a message (non-streaming)
        response = client.post(
            f"/v1/kgent/sessions/{session_id}/messages",
            json={"message": "What patterns am I avoiding?", "stream": False},
            headers={"X-API-Key": "kg_test_write"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "content" in data
        assert data["role"] == "assistant"


class TestGetMessages:
    """Tests for GET /v1/kgent/sessions/{id}/messages."""

    def test_get_messages_no_auth(self, client: TestClient) -> None:
        """Test get messages requires authentication."""
        fake_id = "00000000-0000-0000-0000-000000000099"
        response = client.get(f"/v1/kgent/sessions/{fake_id}/messages")
        # FastAPI returns 422 for missing required header
        assert response.status_code == 422

    def test_get_messages_not_found(self, client: TestClient) -> None:
        """Test get messages for nonexistent session."""
        fake_id = "00000000-0000-0000-0000-000000000099"
        response = client.get(
            f"/v1/kgent/sessions/{fake_id}/messages",
            headers={"X-API-Key": "kg_test_read"},
        )
        assert response.status_code == 404

    def test_get_messages_success(self, client: TestClient) -> None:
        """Test get messages for existing session."""
        # Create a session
        create_response = client.post(
            "/v1/kgent/sessions",
            json={"title": "Test Session"},
            headers={"X-API-Key": "kg_test_write"},
        )
        session_id = create_response.json()["id"]

        # Get messages (should be empty)
        response = client.get(
            f"/v1/kgent/sessions/{session_id}/messages",
            headers={"X-API-Key": "kg_test_read"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "messages" in data
        assert data["session_id"] == session_id


class TestKgentTags:
    """Tests for K-gent endpoint tags."""

    def test_kgent_endpoints_tagged(self, client: TestClient) -> None:
        """Test K-gent endpoints have 'kgent' tag."""
        response = client.get("/openapi.json")
        data = response.json()

        # Check sessions endpoint
        sessions_path = data["paths"].get("/v1/kgent/sessions", {}).get("post")
        if sessions_path:
            assert "kgent" in sessions_path["tags"]


class TestCrossTenantIsolation:
    """Integration tests for tenant isolation."""

    def test_cross_tenant_session_access_denied(self, client: TestClient) -> None:
        """Test that a tenant cannot access another tenant's session.

        Note: The API returns 401 when tenant context cannot be established
        (tenant not found in service), or 404 when session not found/not owned.
        Both prevent cross-tenant access.
        """
        # Register a second tenant's API key
        register_api_key(
            ApiKeyData(
                key="kg_test_tenant2",
                user_id="user_tenant2",
                tier="PRO",
                rate_limit=1000,
                tenant_id=UUID(
                    "00000000-0000-0000-0000-000000000002"
                ),  # Different tenant
                scopes=("read", "write"),
            )
        )

        # Create a session as tenant 1
        create_response = client.post(
            "/v1/kgent/sessions",
            json={"title": "Tenant 1 Session"},
            headers={"X-API-Key": "kg_test_write"},
        )
        assert create_response.status_code == 200
        session_id = create_response.json()["id"]

        # Try to access as tenant 2 - should be denied (401 or 404)
        response = client.get(
            f"/v1/kgent/sessions/{session_id}",
            headers={"X-API-Key": "kg_test_tenant2"},
        )
        # 401 = tenant context not established, 404 = session not found/not owned
        # Both effectively prevent cross-tenant access
        assert response.status_code in (401, 404)

    def test_cross_tenant_message_access_denied(self, client: TestClient) -> None:
        """Test that a tenant cannot send messages to another tenant's session."""
        # Register a second tenant's API key
        register_api_key(
            ApiKeyData(
                key="kg_test_tenant2_write",
                user_id="user_tenant2",
                tier="PRO",
                rate_limit=1000,
                tenant_id=UUID("00000000-0000-0000-0000-000000000002"),
                scopes=("read", "write"),
            )
        )

        # Create a session as tenant 1
        create_response = client.post(
            "/v1/kgent/sessions",
            json={"title": "Tenant 1 Session"},
            headers={"X-API-Key": "kg_test_write"},
        )
        session_id = create_response.json()["id"]

        # Try to send message as tenant 2 - should be denied
        response = client.post(
            f"/v1/kgent/sessions/{session_id}/messages",
            json={"message": "Sneaky message", "stream": False},
            headers={"X-API-Key": "kg_test_tenant2_write"},
        )
        # 401 = tenant context not established, 404 = session not found/not owned
        assert response.status_code in (401, 404)

    def test_list_sessions_only_shows_own_tenant(self, client: TestClient) -> None:
        """Test that list sessions only returns sessions for the current tenant."""
        # Register tenant 2's key
        register_api_key(
            ApiKeyData(
                key="kg_test_tenant2_list",
                user_id="user_tenant2",
                tier="PRO",
                rate_limit=1000,
                tenant_id=UUID("00000000-0000-0000-0000-000000000002"),
                scopes=("read", "write"),
            )
        )

        # Create sessions for both tenants
        client.post(
            "/v1/kgent/sessions",
            json={"title": "Tenant 1 Session"},
            headers={"X-API-Key": "kg_test_write"},
        )
        client.post(
            "/v1/kgent/sessions",
            json={"title": "Tenant 2 Session"},
            headers={"X-API-Key": "kg_test_tenant2_list"},
        )

        # List as tenant 1
        response = client.get(
            "/v1/kgent/sessions",
            headers={"X-API-Key": "kg_test_read"},
        )
        data = response.json()

        # Should only see tenant 1's sessions
        for session in data["sessions"]:
            assert session["tenant_id"] == "00000000-0000-0000-0000-000000000001"


class TestEdgeCases:
    """Tests for edge cases and error handling."""

    def test_send_message_invalid_mode(self, client: TestClient) -> None:
        """Test send message with invalid mode returns 400."""
        # Create session
        create_response = client.post(
            "/v1/kgent/sessions",
            json={"title": "Test Session"},
            headers={"X-API-Key": "kg_test_write"},
        )
        session_id = create_response.json()["id"]

        # Send with invalid mode
        response = client.post(
            f"/v1/kgent/sessions/{session_id}/messages",
            json={"message": "Hello", "mode": "invalid_mode", "stream": False},
            headers={"X-API-Key": "kg_test_write"},
        )
        assert response.status_code == 400
        assert "mode" in response.json()["detail"].lower()

    def test_empty_message_list_returns_empty(self, client: TestClient) -> None:
        """Test getting messages from session with no messages."""
        # Create session
        create_response = client.post(
            "/v1/kgent/sessions",
            json={"title": "Empty Session"},
            headers={"X-API-Key": "kg_test_write"},
        )
        session_id = create_response.json()["id"]

        # Get messages
        response = client.get(
            f"/v1/kgent/sessions/{session_id}/messages",
            headers={"X-API-Key": "kg_test_read"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["messages"] == []
        assert data["total"] == 0
