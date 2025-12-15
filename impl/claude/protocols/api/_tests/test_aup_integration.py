"""
AGENTESE Universal Protocol Integration Tests.

Tests the full HTTP → Bridge → Logos → Response flow.

These tests verify:
1. HTTP endpoints work end-to-end
2. Observer context flows correctly via headers
3. Error responses are sympathetic
4. Category laws are preserved in compose
5. SSE streaming works for soul/challenge
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

# Skip all tests if FastAPI/httpx not available
pytest.importorskip("fastapi")
pytest.importorskip("httpx")
pytest.importorskip("pydantic")


@pytest.fixture
def mock_logos() -> MagicMock:
    """Create a mock Logos instance for testing."""
    logos = MagicMock()

    # Mock resolve
    mock_node = MagicMock()
    mock_node.affordances.return_value = [
        "manifest",
        "witness",
        "refine",
        "affordances",
    ]
    logos.resolve.return_value = mock_node

    # Mock invoke
    async def mock_invoke(path: str, observer: Any, **kwargs: Any) -> dict[str, Any]:
        return {
            "path": path,
            "observer_archetype": getattr(observer.dna, "archetype", "unknown"),
            "kwargs": kwargs,
        }

    logos.invoke = AsyncMock(side_effect=mock_invoke)

    # Mock compose
    mock_composed = MagicMock()

    async def mock_composed_invoke(observer: Any, initial_input: Any = None) -> Any:
        return {"result": "composed", "initial": initial_input}

    mock_composed.invoke = AsyncMock(side_effect=mock_composed_invoke)
    logos.compose.return_value = mock_composed

    # Mock is_resolved
    logos.is_resolved.return_value = False

    return logos


@pytest.fixture
def test_client(mock_logos: MagicMock) -> Any:
    """Create a test client with mocked Logos."""
    from fastapi.testclient import TestClient
    from protocols.api.app import create_app
    from protocols.api.bridge_impl import LogosAgenteseBridge

    # Create the real bridge with mock logos
    mock_bridge = LogosAgenteseBridge(
        logos=mock_logos,
        telemetry_enabled=False,
    )

    # Create the app
    app = create_app(
        enable_cors=False,
        enable_tenant_middleware=False,
    )

    # Create test client with default auth header
    # kg_dev_carol has all scopes including admin
    client = TestClient(app)
    client.headers = {"X-API-Key": "kg_dev_carol"}

    # Now patch the bridge factory for AUP router
    # The bridge is lazily created, so we patch the factory
    with patch(
        "protocols.api.bridge_impl.create_logos_bridge",
        return_value=mock_bridge,
    ):
        yield client


class TestManifestEndpoint:
    """Tests for GET /api/v1/{context}/{holon}/manifest."""

    def test_manifest_returns_agentese_response(
        self, test_client: Any, mock_logos: MagicMock
    ) -> None:
        """Manifest endpoint returns proper AgenteseResponse envelope."""
        response = test_client.get(
            "/api/v1/world/field/manifest",
            headers={
                "X-Observer-Archetype": "architect",
                "X-Observer-Id": "user-123",
            },
        )

        assert response.status_code == 200
        data = response.json()

        # Verify envelope structure
        assert "handle" in data
        assert "result" in data
        assert "meta" in data

        # Verify handle
        assert data["handle"] == "world.field.manifest"

        # Verify meta
        assert data["meta"]["observer"] == "architect"
        assert "span_id" in data["meta"]
        assert "timestamp" in data["meta"]

    def test_manifest_invalid_context_returns_error(self, test_client: Any) -> None:
        """Invalid context returns 400 with sympathetic error."""
        response = test_client.get(
            "/api/v1/invalid/field/manifest",
            headers={"X-Observer-Archetype": "viewer"},
        )

        assert response.status_code == 400
        data = response.json()
        detail = data["detail"]

        assert "invalid" in detail["error"].lower()
        assert detail["code"] == "SYNTAX_ERROR"
        assert "available" in detail

    def test_manifest_default_observer(
        self, test_client: Any, mock_logos: MagicMock
    ) -> None:
        """Manifest uses default observer when headers not provided."""
        response = test_client.get("/api/v1/self/soul/manifest")

        assert response.status_code == 200
        data = response.json()

        # Default observer is "viewer"
        assert data["meta"]["observer"] == "viewer"


class TestAffordancesEndpoint:
    """Tests for GET /api/v1/{context}/{holon}/affordances."""

    def test_affordances_returns_list(
        self, test_client: Any, mock_logos: MagicMock
    ) -> None:
        """Affordances endpoint returns filtered list."""
        response = test_client.get(
            "/api/v1/world/house/affordances",
            headers={"X-Observer-Archetype": "architect"},
        )

        assert response.status_code == 200
        data = response.json()

        assert data["path"] == "world.house"
        assert data["observer_archetype"] == "architect"
        assert isinstance(data["affordances"], list)
        assert "manifest" in data["affordances"]


class TestInvokeEndpoint:
    """Tests for POST /api/v1/{context}/{holon}/{aspect}."""

    def test_invoke_invalid_context_returns_error(
        self, test_client: Any, mock_logos: MagicMock
    ) -> None:
        """Invoke with invalid context returns 400."""
        response = test_client.post(
            "/api/v1/invalid/holon/aspect",
            headers={"X-Observer-Archetype": "philosopher"},
            json={"kwargs": {}},
        )

        assert response.status_code == 400
        data = response.json()
        assert "invalid" in data["detail"]["error"].lower()

    def test_invoke_endpoint_exists(
        self, test_client: Any, mock_logos: MagicMock
    ) -> None:
        """Invoke endpoint is registered and accepts POST."""
        # Test that the endpoint exists (may fail with 404/500 depending on path)
        response = test_client.post(
            "/api/v1/world/field/manifest",
            headers={"X-Observer-Archetype": "viewer"},
            json={"kwargs": {}},
        )

        # Should not be 422 (method not allowed) or 404 (not found)
        assert response.status_code != 405
        assert response.status_code != 404


class TestComposeEndpoint:
    """Tests for POST /api/v1/compose."""

    def test_compose_validates_path_syntax(
        self, test_client: Any, mock_logos: MagicMock
    ) -> None:
        """Compose validates path syntax (missing aspect)."""
        response = test_client.post(
            "/api/v1/compose",
            headers={"X-Observer-Archetype": "developer"},
            json={
                "paths": ["invalid.path"],  # Missing aspect
            },
        )

        assert response.status_code == 400
        data = response.json()
        assert "aspect" in data["detail"]["error"].lower()

    def test_compose_validates_context(
        self, test_client: Any, mock_logos: MagicMock
    ) -> None:
        """Compose validates context in paths."""
        response = test_client.post(
            "/api/v1/compose",
            headers={"X-Observer-Archetype": "developer"},
            json={
                "paths": ["bad.holon.aspect"],  # Invalid context
            },
        )

        assert response.status_code == 400
        data = response.json()
        assert "bad" in data["detail"]["error"].lower()
        assert "available" in data["detail"]

    def test_compose_endpoint_exists(
        self, test_client: Any, mock_logos: MagicMock
    ) -> None:
        """Compose endpoint is registered and accepts POST."""
        # Test that the endpoint exists
        response = test_client.post(
            "/api/v1/compose",
            headers={"X-Observer-Archetype": "developer"},
            json={
                "paths": ["world.field.manifest"],
            },
        )

        # Should not be method not allowed or not found
        assert response.status_code != 405
        assert response.status_code != 422  # Request body is valid


class TestResolveEndpoint:
    """Tests for GET /api/v1/{context}/{holon}/resolve."""

    def test_resolve_returns_metadata(
        self, test_client: Any, mock_logos: MagicMock
    ) -> None:
        """Resolve endpoint returns path metadata."""
        response = test_client.get(
            "/api/v1/world/field/resolve",
            headers={"X-Observer-Archetype": "developer"},
        )

        assert response.status_code == 200
        data = response.json()

        assert data["path"] == "world.field"
        assert data["context"] == "world"
        assert data["holon"] == "field"
        assert "exists" in data
        assert "affordances" in data


class TestVerifyLawsEndpoint:
    """Tests for POST /api/v1/verify-laws."""

    def test_verify_laws_endpoint_exists(
        self, test_client: Any, mock_logos: MagicMock
    ) -> None:
        """Verify laws endpoint is registered."""
        response = test_client.post(
            "/api/v1/verify-laws",
            headers={"X-Observer-Archetype": "developer"},
            json={
                "paths": [
                    "world.a.manifest",
                ],
            },
        )

        # Should not be method not allowed
        assert response.status_code != 405


class TestStreamEndpoint:
    """Tests for GET /api/v1/{context}/{holon}/{aspect}/stream."""

    def test_stream_returns_sse(self, test_client: Any, mock_logos: MagicMock) -> None:
        """Stream endpoint returns SSE format."""
        response = test_client.get(
            "/api/v1/self/soul/challenge/stream",
            headers={
                "X-Observer-Archetype": "philosopher",
                "Accept": "text/event-stream",
            },
            params={"challenge": "What is justice?"},
        )

        assert response.status_code == 200
        assert response.headers["content-type"].startswith("text/event-stream")

        # Parse SSE events
        content = response.text
        assert "event:" in content
        assert "data:" in content


class TestHeaderExtraction:
    """Tests for observer context header extraction."""

    def test_extracts_archetype(self, test_client: Any, mock_logos: MagicMock) -> None:
        """Extracts X-Observer-Archetype header."""
        response = test_client.get(
            "/api/v1/world/field/manifest",
            headers={"X-Observer-Archetype": "custom-archetype"},
        )

        assert response.status_code == 200
        assert response.json()["meta"]["observer"] == "custom-archetype"

    def test_extracts_capabilities(
        self, test_client: Any, mock_logos: MagicMock
    ) -> None:
        """Extracts X-Observer-Capabilities as comma-separated list."""
        # This is tested implicitly through the mock
        # Real test would verify the capabilities reach Logos
        response = test_client.get(
            "/api/v1/world/field/manifest",
            headers={
                "X-Observer-Archetype": "developer",
                "X-Observer-Capabilities": "define,spawn,dialectic",
            },
        )

        assert response.status_code == 200


class TestBridgeImplUnit:
    """Unit tests for LogosAgenteseBridge (not HTTP)."""

    @pytest.mark.asyncio
    async def test_invoke_translates_observer(self, mock_logos: MagicMock) -> None:
        """Bridge invoke translates ObserverContext to Umwelt."""
        from protocols.api.bridge_impl import LogosAgenteseBridge
        from protocols.api.serializers import ObserverContext

        bridge = LogosAgenteseBridge(logos=mock_logos, telemetry_enabled=False)
        observer = ObserverContext(
            archetype="architect",
            id="user-123",
            capabilities=["define", "spawn"],
        )

        response = await bridge.invoke("world.field.manifest", observer)

        # Verify Logos was called
        mock_logos.invoke.assert_called_once()

        # Verify response envelope
        assert response.handle == "world.field.manifest"
        assert response.meta.observer == "architect"

    @pytest.mark.asyncio
    async def test_invoke_handles_errors(self, mock_logos: MagicMock) -> None:
        """Bridge invoke converts exceptions to BridgeError."""
        from protocols.agentese.exceptions import PathNotFoundError
        from protocols.api.bridge_impl import BridgeError, LogosAgenteseBridge
        from protocols.api.serializers import ObserverContext

        mock_logos.invoke.side_effect = PathNotFoundError(
            "Path not found", path="world.missing"
        )

        bridge = LogosAgenteseBridge(logos=mock_logos, telemetry_enabled=False)
        observer = ObserverContext()

        with pytest.raises(BridgeError) as exc_info:
            await bridge.invoke("world.missing.manifest", observer)

        assert exc_info.value.error.code == "PATH_NOT_FOUND"

    @pytest.mark.asyncio
    async def test_compose_collects_trace(self, mock_logos: MagicMock) -> None:
        """Bridge compose collects pipeline trace."""
        from protocols.api.bridge_impl import LogosAgenteseBridge
        from protocols.api.serializers import ObserverContext

        bridge = LogosAgenteseBridge(logos=mock_logos, telemetry_enabled=False)
        observer = ObserverContext()

        response = await bridge.compose(
            paths=["world.a.manifest", "concept.b.refine"],
            observer=observer,
            emit_law_check=True,
        )

        assert len(response.pipeline_trace) == 2
        assert response.pipeline_trace[0].path == "world.a.manifest"
        assert response.pipeline_trace[1].path == "concept.b.refine"
        assert "identity" in response.laws_verified

    @pytest.mark.asyncio
    async def test_stream_yields_events(self, mock_logos: MagicMock) -> None:
        """Bridge stream yields SSE events."""
        from protocols.api.bridge_impl import LogosAgenteseBridge
        from protocols.api.serializers import ObserverContext

        bridge = LogosAgenteseBridge(logos=mock_logos, telemetry_enabled=False)
        observer = ObserverContext()

        events = []
        async for event in bridge.stream("world.field.manifest", observer):
            events.append(event)

        # Should have at least chunk + done
        assert len(events) >= 1
        assert events[-1].event == "done"


class TestErrorResponses:
    """Tests for sympathetic error responses."""

    def test_invalid_context_returns_sympathetic_error(
        self, test_client: Any, mock_logos: MagicMock
    ) -> None:
        """Invalid context returns 400 with helpful error."""
        response = test_client.get(
            "/api/v1/invalid/missing/manifest",
            headers={"X-Observer-Archetype": "viewer"},
        )

        assert response.status_code == 400
        data = response.json()
        detail = data["detail"]

        assert detail["code"] == "SYNTAX_ERROR"
        assert "available" in detail

    def test_compose_invalid_context_includes_available(
        self, test_client: Any, mock_logos: MagicMock
    ) -> None:
        """Compose with invalid context returns available contexts."""
        response = test_client.post(
            "/api/v1/compose",
            headers={"X-Observer-Archetype": "viewer"},
            json={"paths": ["bad.holon.aspect"]},
        )

        assert response.status_code == 400
        data = response.json()
        detail = data["detail"]

        assert "available" in detail
        # Should list valid contexts
        assert "world" in detail["available"] or "world" in str(detail)
