"""
Test suite for U-gent Server.

Tests for server.py:
- ExecuteRequest/ExecuteResponse validation
- Health endpoint
- Execute endpoint with Soul integration
- Server state management
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Optional
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

# --- Request/Response Model Tests ---


class TestExecuteRequest:
    """Tests for ExecuteRequest model."""

    def test_minimal_request(self) -> None:
        """Test minimal request with just prompt."""
        from agents.u.server import ExecuteRequest

        request = ExecuteRequest(
            prompt="test operation",
            tool_name=None,
            require_approval=True,
            severity=0.5,
        )
        assert request.prompt == "test operation"
        assert request.tool_name is None
        assert request.context == {}
        assert request.require_approval is True
        assert request.severity == 0.5

    def test_full_request(self) -> None:
        """Test request with all fields."""
        from agents.u.server import ExecuteRequest

        request = ExecuteRequest(
            prompt="delete user",
            tool_name="user_manager",
            context={"user_id": 123},
            require_approval=True,
            severity=0.9,
        )
        assert request.prompt == "delete user"
        assert request.tool_name == "user_manager"
        assert request.context == {"user_id": 123}
        assert request.severity == 0.9

    def test_severity_bounds(self) -> None:
        """Test severity is bounded 0-1."""
        from agents.u.server import ExecuteRequest

        # Valid bounds
        ExecuteRequest(
            prompt="test", tool_name=None, require_approval=True, severity=0.0
        )
        ExecuteRequest(
            prompt="test", tool_name=None, require_approval=True, severity=1.0
        )

        # Invalid bounds should raise
        with pytest.raises(ValueError):
            ExecuteRequest(
                prompt="test", tool_name=None, require_approval=True, severity=-0.1
            )
        with pytest.raises(ValueError):
            ExecuteRequest(
                prompt="test", tool_name=None, require_approval=True, severity=1.1
            )


class TestExecuteResponse:
    """Tests for ExecuteResponse model."""

    def test_approved_response(self) -> None:
        """Test approved response structure."""
        from agents.u.server import ExecuteResponse

        response = ExecuteResponse(
            status="approved",
            result={"data": "success"},
            confidence=0.95,
            execution_time_ms=42.5,
        )
        assert response.status == "approved"
        assert response.result == {"data": "success"}
        assert response.confidence == 0.95

    def test_escalated_response(self) -> None:
        """Test escalated response with annotation."""
        from agents.u.server import ExecuteResponse

        response = ExecuteResponse(
            status="escalated",
            annotation="Dangerous operation detected",
            reasoning="Contains 'delete' keyword",
            confidence=0.0,
        )
        assert response.status == "escalated"
        assert response.annotation is not None
        assert "Dangerous" in response.annotation


class TestHealthResponse:
    """Tests for HealthResponse model."""

    def test_healthy_response(self) -> None:
        """Test healthy response structure."""
        from agents.u.server import HealthResponse

        response = HealthResponse(
            status="healthy",
            soul_available=True,
            morpheus_available=True,
            timestamp=datetime.now().isoformat(),
        )
        assert response.status == "healthy"
        assert response.soul_available is True


# --- Server State Tests ---


class TestServerState:
    """Tests for ServerState management."""

    def test_initial_state(self) -> None:
        """Test initial server state."""
        from agents.u.server import ServerState

        state = ServerState()
        assert state.soul is None
        assert state.llm_client is None
        assert state.startup_time is not None

    def test_soul_availability(self) -> None:
        """Test soul availability detection."""
        from agents.u.server import ServerState

        state = ServerState()
        assert state.soul_available is False

        state.soul = MagicMock()
        assert state.soul_available is True

    def test_morpheus_availability(self) -> None:
        """Test Morpheus availability detection."""
        from agents.u.server import ServerState

        state = ServerState()

        # Without env var
        with patch.dict("os.environ", {}, clear=True):
            assert state.morpheus_available is False

        # With env var
        with patch.dict("os.environ", {"MORPHEUS_URL": "http://localhost:8080/v1"}):
            assert state.morpheus_available is True


# --- Mock Soul for Testing ---


@dataclass
class MockInterceptResult:
    """Mock intercept result for testing."""

    handled: bool
    annotation: Optional[str] = None
    recommendation: Optional[str] = None
    confidence: float = 0.0
    matching_principles: list[str] = None  # type: ignore
    reasoning: str = ""
    was_deep: bool = False

    def __post_init__(self) -> None:
        if self.matching_principles is None:
            self.matching_principles = []


class MockSoul:
    """Mock Soul for testing U-gent server."""

    def __init__(self, auto_approve: bool = False, has_llm: bool = False) -> None:
        self._auto_approve = auto_approve
        self.has_llm = has_llm
        self.intercept_calls: list[Any] = []

    async def intercept(self, token: Any) -> MockInterceptResult:
        self.intercept_calls.append(token)
        return MockInterceptResult(
            handled=self._auto_approve,
            annotation="Requires human review" if not self._auto_approve else None,
            recommendation="approve" if self._auto_approve else "escalate",
            confidence=0.9 if self._auto_approve else 0.3,
            reasoning="Mock reasoning",
        )

    async def intercept_deep(self, token: Any) -> MockInterceptResult:
        self.intercept_calls.append(token)
        return MockInterceptResult(
            handled=self._auto_approve,
            annotation="Deep analysis complete" if not self._auto_approve else None,
            recommendation="approve" if self._auto_approve else "escalate",
            confidence=0.95 if self._auto_approve else 0.2,
            reasoning="LLM-based reasoning",
            was_deep=True,
        )


# --- Integration Tests ---


class TestServerEndpoints:
    """Tests for server endpoints."""

    @pytest.fixture
    def app(self) -> Any:
        """Create test app."""
        from agents.u.server import create_app

        return create_app()

    @pytest.mark.asyncio
    async def test_root_endpoint(self, app: Any) -> None:
        """Test root endpoint returns API info."""
        from fastapi.testclient import TestClient

        client = TestClient(app)
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "U-gent Server"
        assert "endpoints" in data

    @pytest.mark.asyncio
    async def test_health_endpoint(self, app: Any) -> None:
        """Test health endpoint."""
        from fastapi.testclient import TestClient

        client = TestClient(app)
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "soul_available" in data
        assert "morpheus_available" in data

    @pytest.mark.asyncio
    async def test_tools_endpoint(self, app: Any) -> None:
        """Test tools listing endpoint."""
        from fastapi.testclient import TestClient

        client = TestClient(app)
        response = client.get("/tools")
        assert response.status_code == 200
        data = response.json()
        assert "tools" in data


class TestExecuteEndpoint:
    """Tests for execute endpoint."""

    @pytest.fixture
    def app_with_mock_soul(self) -> Any:
        """Create test app with mock Soul."""
        from agents.u.server import create_app, get_state

        app = create_app()
        state = get_state()
        state.soul = MockSoul(auto_approve=False, has_llm=False)
        return app

    @pytest.fixture
    def app_with_approving_soul(self) -> Any:
        """Create test app with auto-approving Soul."""
        from agents.u.server import create_app, get_state

        app = create_app()
        state = get_state()
        state.soul = MockSoul(auto_approve=True, has_llm=True)
        return app

    @pytest.mark.asyncio
    async def test_execute_escalates_without_soul(self) -> None:
        """Test execute escalates when Soul not available."""
        from agents.u.server import create_app, get_state
        from fastapi.testclient import TestClient

        app = create_app()
        state = get_state()
        state.soul = None

        client = TestClient(app)
        response = client.post(
            "/execute",
            json={"prompt": "test operation"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "escalated"
        assert "Soul not available" in data["annotation"]

    @pytest.mark.asyncio
    async def test_execute_escalates_on_rejection(
        self, app_with_mock_soul: Any
    ) -> None:
        """Test execute escalates when Soul rejects."""
        from fastapi.testclient import TestClient

        client = TestClient(app_with_mock_soul)
        response = client.post(
            "/execute",
            json={"prompt": "delete everything"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "escalated"
        assert data["annotation"] is not None

    @pytest.mark.asyncio
    async def test_execute_approves_when_soul_approves(
        self, app_with_approving_soul: Any
    ) -> None:
        """Test execute proceeds when Soul approves."""
        from fastapi.testclient import TestClient

        client = TestClient(app_with_approving_soul)
        response = client.post(
            "/execute",
            json={"prompt": "list files"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "approved"
        assert data["confidence"] > 0

    @pytest.mark.asyncio
    async def test_execute_skips_approval_when_not_required(self) -> None:
        """Test execute skips Soul check when not required."""
        from agents.u.server import create_app, get_state
        from fastapi.testclient import TestClient

        app = create_app()
        state = get_state()
        state.soul = MockSoul(auto_approve=False)

        client = TestClient(app)
        response = client.post(
            "/execute",
            json={
                "prompt": "test operation",
                "require_approval": False,
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "approved"
        # Soul should not have been called
        assert len(state.soul.intercept_calls) == 0


class TestSoulIntegration:
    """Tests for Soul library integration."""

    @pytest.mark.asyncio
    async def test_soul_uses_shallow_intercept_without_llm(self) -> None:
        """Test Soul uses shallow intercept when LLM not available."""
        from agents.u.server import create_app, get_state
        from fastapi.testclient import TestClient

        app = create_app()
        state = get_state()
        mock_soul = MockSoul(auto_approve=True, has_llm=False)
        state.soul = mock_soul

        client = TestClient(app)
        client.post("/execute", json={"prompt": "test"})

        # Check that intercept was called (not intercept_deep)
        assert len(mock_soul.intercept_calls) == 1

    @pytest.mark.asyncio
    async def test_soul_uses_deep_intercept_with_llm(self) -> None:
        """Test Soul uses deep intercept when LLM available."""
        from agents.u.server import create_app, get_state
        from fastapi.testclient import TestClient

        app = create_app()
        state = get_state()
        mock_soul = MockSoul(auto_approve=True, has_llm=True)
        state.soul = mock_soul

        client = TestClient(app)
        client.post("/execute", json={"prompt": "test"})

        # Check that intercept_deep was called
        assert len(mock_soul.intercept_calls) == 1
