"""
Tests for FastAPI application.

Tests:
- Application creation
- Health endpoint
- Root endpoint
- Middleware integration
- OpenAPI documentation
"""

from __future__ import annotations

import pytest

pytest.importorskip("fastapi")

from fastapi.testclient import TestClient

from protocols.api.app import create_app


@pytest.fixture
def client() -> TestClient:
    """Create test client."""
    app = create_app()
    return TestClient(app)


class TestApplicationCreation:
    """Tests for application creation."""

    def test_create_app_default(self) -> None:
        """Test creating app with defaults."""
        app = create_app()

        assert app is not None
        assert app.title == "kgents SaaS API"
        assert app.version == "v1"

    def test_create_app_custom(self) -> None:
        """Test creating app with custom config."""
        app = create_app(
            title="Custom API",
            version="v2",
            description="Custom description",
            enable_cors=False,
        )

        assert app.title == "Custom API"
        assert app.version == "v2"
        assert app.description == "Custom description"

    def test_app_has_routes(self) -> None:
        """Test app has expected routes."""
        app = create_app()

        # Get all routes
        routes = [getattr(route, "path", None) for route in app.routes]

        # Check key endpoints exist
        assert "/health" in routes
        assert "/" in routes
        # AGENTESE gateway routes (soul endpoints migrated to gateway)
        # The internal FastAPI path uses {path:path} but check any agentese route exists
        agentese_routes = [r for r in routes if r and r.startswith("/agentese")]
        assert len(agentese_routes) > 0


class TestRootEndpoint:
    """Tests for root (/) endpoint."""

    def test_root_endpoint(self, client: TestClient) -> None:
        """Test root endpoint returns API info."""
        response = client.get("/")

        assert response.status_code == 200
        data = response.json()

        assert "name" in data
        assert "version" in data
        assert "description" in data
        assert "docs" in data
        assert "health" in data
        assert "endpoints" in data

    def test_root_endpoint_structure(self, client: TestClient) -> None:
        """Test root endpoint has correct structure."""
        response = client.get("/")
        data = response.json()

        # Check endpoints - now nested by service
        endpoints = data["endpoints"]
        assert "soul" in endpoints
        assert "gateway" in endpoints  # AGENTESE Universal Gateway
        assert "kgent" in endpoints
        # Soul endpoints now use AGENTESE gateway (AD-009 Phase 2)
        assert "POST /agentese/self/soul/governance" in endpoints["soul"]["governance"]
        assert "POST /agentese/self/soul/dialogue" in endpoints["soul"]["dialogue"]
        assert endpoints["gateway"]["invoke"] == "POST /agentese/{context}/{holon}/{aspect}"
        # K-gent sessions now use AGENTESE gateway (AD-009 Phase 2)
        assert "POST /agentese/self/kgent/create" in endpoints["kgent"]["create"]


class TestHealthEndpoint:
    """Tests for /health endpoint."""

    def test_health_endpoint_basic(self, client: TestClient) -> None:
        """Test health endpoint returns status."""
        response = client.get("/health")

        assert response.status_code == 200
        data = response.json()

        assert "status" in data
        assert "version" in data
        assert "has_llm" in data
        assert "components" in data

    def test_health_endpoint_components(self, client: TestClient) -> None:
        """Test health endpoint includes component status."""
        response = client.get("/health")
        data = response.json()

        components = data["components"]
        assert "soul" in components
        assert "llm" in components
        assert "auth" in components
        assert "metering" in components

    def test_health_endpoint_status_values(self, client: TestClient) -> None:
        """Test health status is one of expected values."""
        response = client.get("/health")
        data = response.json()

        assert data["status"] in ["ok", "degraded", "error"]

    def test_health_endpoint_no_auth(self, client: TestClient) -> None:
        """Test health endpoint doesn't require auth."""
        # Should work without X-API-Key header
        response = client.get("/health")

        assert response.status_code == 200


class TestOpenAPIDocumentation:
    """Tests for OpenAPI documentation."""

    def test_openapi_endpoint(self, client: TestClient) -> None:
        """Test OpenAPI schema endpoint."""
        response = client.get("/openapi.json")

        assert response.status_code == 200
        data = response.json()

        assert "openapi" in data
        assert "info" in data
        assert "paths" in data

    def test_openapi_paths(self, client: TestClient) -> None:
        """Test OpenAPI includes all paths."""
        response = client.get("/openapi.json")
        data = response.json()

        paths = data["paths"]

        assert "/health" in paths
        # Soul endpoints now use AGENTESE gateway (AD-009 Phase 2)
        # OpenAPI shows path params as {path} not {path:path}
        assert "/agentese/{path}/manifest" in paths
        assert "/agentese/{path}/{aspect}" in paths

    def test_openapi_info(self, client: TestClient) -> None:
        """Test OpenAPI info section."""
        response = client.get("/openapi.json")
        data = response.json()

        info = data["info"]

        assert "title" in info
        assert "version" in info
        assert info["title"] == "kgents SaaS API"
        assert info["version"] == "v1"

    def test_docs_ui_available(self, client: TestClient) -> None:
        """Test Swagger UI is available."""
        response = client.get("/docs")

        assert response.status_code == 200

    def test_redoc_ui_available(self, client: TestClient) -> None:
        """Test ReDoc UI is available."""
        response = client.get("/redoc")

        assert response.status_code == 200


class TestMiddleware:
    """Tests for middleware integration."""

    def test_cors_middleware(self, client: TestClient) -> None:
        """Test CORS middleware is active."""
        # Make a preflight request with Origin header
        response = client.options(
            "/health",
            headers={"Origin": "http://localhost:3000"},
        )

        # CORS headers should be present for preflight
        assert "access-control-allow-origin" in response.headers

    def test_metering_middleware(self, client: TestClient) -> None:
        """Test metering middleware adds headers."""
        response = client.get("/health")

        # Timing header should be present
        assert "x-response-time" in response.headers
        assert "ms" in response.headers["x-response-time"]

    def test_cors_disabled(self) -> None:
        """Test app with CORS disabled."""
        app = create_app(enable_cors=False)
        client = TestClient(app)

        response = client.get("/health")

        # Should still work, just no CORS headers from middleware
        assert response.status_code == 200


class TestErrorHandling:
    """Tests for error handling."""

    def test_404_for_unknown_path(self, client: TestClient) -> None:
        """Test 404 for unknown paths."""
        response = client.get("/unknown/path")

        assert response.status_code == 404

    def test_405_for_wrong_method(self, client: TestClient) -> None:
        """Test 405 for wrong HTTP method."""
        # POST to root which only accepts GET
        response = client.post("/")

        assert response.status_code == 405

    def test_422_for_invalid_body(self, client: TestClient) -> None:
        """Test 422 for invalid request body - uses AGENTESE gateway."""
        from protocols.api.auth import ApiKeyData, register_api_key

        # Register a test key
        register_api_key(
            ApiKeyData(
                key="kg_test",
                user_id="test",
                tier="PRO",
                rate_limit=100,
            )
        )

        # Send invalid body via AGENTESE gateway (AD-009 Phase 2)
        # The AUP router still validates composition requests
        response = client.post(
            "/api/v1/compose",
            json={},  # Missing 'paths'
            headers={"X-API-Key": "kg_test"},
        )

        assert response.status_code == 422


class TestAppMetadata:
    """Tests for application metadata."""

    def test_app_title(self, client: TestClient) -> None:
        """Test app title is set correctly."""
        response = client.get("/openapi.json")
        data = response.json()

        assert data["info"]["title"] == "kgents SaaS API"

    def test_app_version(self, client: TestClient) -> None:
        """Test app version is set correctly."""
        response = client.get("/openapi.json")
        data = response.json()

        assert data["info"]["version"] == "v1"

    def test_app_description(self, client: TestClient) -> None:
        """Test app description is set correctly."""
        response = client.get("/openapi.json")
        data = response.json()

        # Updated for multi-tenant API
        assert "AGENTESE" in data["info"]["description"]


class TestEndpointTags:
    """Tests for endpoint tags."""

    def test_agentese_gateway_tagged(self, client: TestClient) -> None:
        """Test AGENTESE gateway endpoints have proper tag."""
        response = client.get("/openapi.json")
        data = response.json()

        # Check gateway discover endpoint
        discover_path = data["paths"]["/agentese/discover"]["get"]
        assert "agentese-gateway" in discover_path["tags"]

        # Check gateway manifest endpoint (OpenAPI shows {path} not {path:path})
        manifest_path = data["paths"]["/agentese/{path}/manifest"]["get"]
        assert "agentese-gateway" in manifest_path["tags"]

    def test_system_endpoints_tagged(self, client: TestClient) -> None:
        """Test system endpoints have 'system' tag."""
        response = client.get("/openapi.json")
        data = response.json()

        # Check health endpoint
        health_path = data["paths"]["/health"]["get"]
        assert "system" in health_path["tags"]

        # Check root endpoint
        root_path = data["paths"]["/"]["get"]
        assert "system" in root_path["tags"]
