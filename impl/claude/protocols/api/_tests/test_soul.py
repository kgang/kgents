"""
Tests for Soul API endpoints.

Tests:
- Governance endpoint
- Dialogue endpoint
- Authentication integration
- Rate limiting integration
"""

from __future__ import annotations

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


@pytest.fixture
def setup_test_keys() -> None:
    """Set up test API keys."""
    clear_api_keys()
    clear_usage_stats()

    # Register test keys
    register_api_key(
        ApiKeyData(
            key="kg_test_free",
            user_id="test_free",
            tier="FREE",
            rate_limit=10,
            monthly_token_limit=1000,
        )
    )
    register_api_key(
        ApiKeyData(
            key="kg_test_pro",
            user_id="test_pro",
            tier="PRO",
            rate_limit=100,
            monthly_token_limit=10000,
        )
    )
    register_api_key(
        ApiKeyData(
            key="kg_test_enterprise",
            user_id="test_enterprise",
            tier="ENTERPRISE",
            rate_limit=1000,
            monthly_token_limit=0,  # Unlimited
        )
    )


class TestGovernanceEndpoint:
    """Tests for /v1/soul/governance endpoint."""

    def test_governance_basic(self, client: TestClient, setup_test_keys: None) -> None:
        """Test basic governance request."""
        response = client.post(
            "/v1/soul/governance",
            json={
                "action": "delete temporary files",
                "context": {},
            },
            headers={"X-API-Key": "kg_test_pro"},
        )

        assert response.status_code == 200
        data = response.json()

        assert "approved" in data
        assert "reasoning" in data
        assert "confidence" in data
        assert "tokens_used" in data
        assert "recommendation" in data
        assert isinstance(data["approved"], bool)
        assert isinstance(data["confidence"], float)
        assert 0.0 <= data["confidence"] <= 1.0

    def test_governance_dangerous_operation(
        self, client: TestClient, setup_test_keys: None
    ) -> None:
        """Test governance with dangerous operation."""
        response = client.post(
            "/v1/soul/governance",
            json={
                "action": "rm -rf /production/database",
                "context": {"environment": "production"},
            },
            headers={"X-API-Key": "kg_test_enterprise"},
        )

        assert response.status_code == 200
        data = response.json()

        # Should not be auto-approved
        assert data["approved"] is False
        assert data["recommendation"] in ["reject", "escalate"]

    def test_governance_no_auth(self, client: TestClient) -> None:
        """Test governance without authentication."""
        response = client.post(
            "/v1/soul/governance",
            json={
                "action": "test",
                "context": {},
            },
        )

        assert response.status_code == 401  # Auth middleware returns 401 for missing API key

    def test_governance_invalid_api_key(
        self, client: TestClient, setup_test_keys: None
    ) -> None:
        """Test governance with invalid API key."""
        response = client.post(
            "/v1/soul/governance",
            json={
                "action": "test",
                "context": {},
            },
            headers={"X-API-Key": "kg_invalid"},
        )

        assert response.status_code == 401

    def test_governance_budget_tier_restriction(
        self, client: TestClient, setup_test_keys: None
    ) -> None:
        """Test FREE tier cannot use deep budget."""
        response = client.post(
            "/v1/soul/governance",
            json={
                "action": "test",
                "context": {},
                "budget": "deep",
            },
            headers={"X-API-Key": "kg_test_free"},
        )

        assert response.status_code == 403
        assert "not available" in response.json()["detail"].lower()

    def test_governance_with_context(
        self, client: TestClient, setup_test_keys: None
    ) -> None:
        """Test governance with rich context."""
        response = client.post(
            "/v1/soul/governance",
            json={
                "action": "deploy new feature",
                "context": {
                    "environment": "staging",
                    "reason": "testing",
                    "severity": 0.3,
                },
                "budget": "dialogue",
            },
            headers={"X-API-Key": "kg_test_pro"},
        )

        assert response.status_code == 200
        data = response.json()

        assert "reasoning" in data
        assert len(data["reasoning"]) > 0


class TestDialogueEndpoint:
    """Tests for /v1/soul/dialogue endpoint."""

    def test_dialogue_basic(self, client: TestClient, setup_test_keys: None) -> None:
        """Test basic dialogue request."""
        response = client.post(
            "/v1/soul/dialogue",
            json={
                "prompt": "What patterns am I avoiding?",
                "mode": "reflect",
            },
            headers={"X-API-Key": "kg_test_pro"},
        )

        assert response.status_code == 200
        data = response.json()

        assert "response" in data
        assert "mode" in data
        assert "eigenvectors" in data
        assert "tokens_used" in data
        assert data["mode"] == "reflect"
        assert len(data["response"]) > 0

    def test_dialogue_all_modes(
        self, client: TestClient, setup_test_keys: None
    ) -> None:
        """Test dialogue with all modes."""
        modes = ["reflect", "advise", "challenge", "explore"]

        for mode in modes:
            response = client.post(
                "/v1/soul/dialogue",
                json={
                    "prompt": f"Test {mode}",
                    "mode": mode,
                },
                headers={"X-API-Key": "kg_test_pro"},
            )

            assert response.status_code == 200
            data = response.json()
            assert data["mode"] == mode

    def test_dialogue_invalid_mode(
        self, client: TestClient, setup_test_keys: None
    ) -> None:
        """Test dialogue with invalid mode."""
        response = client.post(
            "/v1/soul/dialogue",
            json={
                "prompt": "Test",
                "mode": "invalid_mode",
            },
            headers={"X-API-Key": "kg_test_pro"},
        )

        assert response.status_code == 400
        assert "mode" in response.json()["detail"].lower()

    def test_dialogue_budget_tiers(
        self, client: TestClient, setup_test_keys: None
    ) -> None:
        """Test dialogue with different budget tiers."""
        budgets = ["dormant", "whisper", "dialogue"]

        for budget in budgets:
            response = client.post(
                "/v1/soul/dialogue",
                json={
                    "prompt": "Test",
                    "budget": budget,
                },
                headers={"X-API-Key": "kg_test_pro"},
            )

            assert response.status_code == 200

    def test_dialogue_invalid_budget(
        self, client: TestClient, setup_test_keys: None
    ) -> None:
        """Test dialogue with invalid budget."""
        response = client.post(
            "/v1/soul/dialogue",
            json={
                "prompt": "Test",
                "budget": "invalid_budget",
            },
            headers={"X-API-Key": "kg_test_pro"},
        )

        assert response.status_code == 400
        assert "budget" in response.json()["detail"].lower()

    def test_dialogue_no_auth(self, client: TestClient) -> None:
        """Test dialogue without authentication."""
        response = client.post(
            "/v1/soul/dialogue",
            json={
                "prompt": "Test",
            },
        )

        assert response.status_code == 401  # Auth middleware returns 401 for missing API key

    def test_dialogue_tier_restrictions(
        self, client: TestClient, setup_test_keys: None
    ) -> None:
        """Test tier-based budget restrictions."""
        # FREE tier cannot use dialogue
        response = client.post(
            "/v1/soul/dialogue",
            json={
                "prompt": "Test",
                "budget": "dialogue",
            },
            headers={"X-API-Key": "kg_test_free"},
        )

        assert response.status_code == 403

        # PRO tier can use dialogue
        response = client.post(
            "/v1/soul/dialogue",
            json={
                "prompt": "Test",
                "budget": "dialogue",
            },
            headers={"X-API-Key": "kg_test_pro"},
        )

        assert response.status_code == 200

    def test_dialogue_eigenvectors_included(
        self, client: TestClient, setup_test_keys: None
    ) -> None:
        """Test that eigenvectors are included in response."""
        response = client.post(
            "/v1/soul/dialogue",
            json={
                "prompt": "Test",
            },
            headers={"X-API-Key": "kg_test_pro"},
        )

        assert response.status_code == 200
        data = response.json()

        assert isinstance(data["eigenvectors"], dict)
        # Should have some eigenvector data
        assert len(data["eigenvectors"]) > 0


class TestRateLimiting:
    """Tests for rate limiting."""

    def test_rate_limit_enforcement(
        self, client: TestClient, setup_test_keys: None
    ) -> None:
        """Test rate limit is enforced."""
        # FREE tier has limit of 10 requests/day
        # Make 10 successful requests
        for _ in range(10):
            response = client.post(
                "/v1/soul/dialogue",
                json={
                    "prompt": "Test",
                    "budget": "whisper",
                },
                headers={"X-API-Key": "kg_test_free"},
            )
            assert response.status_code == 200

        # 11th request should fail
        response = client.post(
            "/v1/soul/dialogue",
            json={
                "prompt": "Test",
                "budget": "whisper",
            },
            headers={"X-API-Key": "kg_test_free"},
        )

        assert response.status_code == 429
        assert "rate limit" in response.json()["detail"].lower()

    def test_rate_limit_per_user(
        self, client: TestClient, setup_test_keys: None
    ) -> None:
        """Test rate limits are per-user."""
        # User 1 hits limit
        for _ in range(10):
            client.post(
                "/v1/soul/dialogue",
                json={"prompt": "Test", "budget": "whisper"},
                headers={"X-API-Key": "kg_test_free"},
            )

        # User 1 should be blocked
        response = client.post(
            "/v1/soul/dialogue",
            json={"prompt": "Test", "budget": "whisper"},
            headers={"X-API-Key": "kg_test_free"},
        )
        assert response.status_code == 429

        # User 2 should still work
        response = client.post(
            "/v1/soul/dialogue",
            json={"prompt": "Test"},
            headers={"X-API-Key": "kg_test_pro"},
        )
        assert response.status_code == 200


class TestResponseHeaders:
    """Tests for response headers."""

    def test_usage_headers(self, client: TestClient, setup_test_keys: None) -> None:
        """Test usage headers are included."""
        response = client.post(
            "/v1/soul/dialogue",
            json={
                "prompt": "Test",
            },
            headers={"X-API-Key": "kg_test_pro"},
        )

        assert response.status_code == 200

        # Check for timing header
        assert "x-response-time" in response.headers

    def test_cors_headers(self, client: TestClient) -> None:
        """Test CORS headers are present."""
        # Make a preflight request with Origin header
        response = client.options(
            "/v1/soul/dialogue",
            headers={"Origin": "http://localhost:3000"},
        )

        assert "access-control-allow-origin" in response.headers
