"""
Tests for Portal Resolver API endpoints.

Verifies:
- POST /api/portal/resolve - Resolve portal URIs
- GET /api/portal/health - Health check
- Error handling for invalid URIs
- Resource type resolution

See: spec/protocols/portal-resource-system.md
See: protocols/api/portal.py
"""

from __future__ import annotations

from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest

pytest.importorskip("fastapi")

from fastapi.testclient import TestClient


@pytest.fixture
def sample_file(tmp_path: Path) -> Path:
    """Create a sample file for testing."""
    file = tmp_path / "test.md"
    file.write_text("# Test Document\n\nThis is a test.\n")
    return file


@pytest.fixture
def client() -> TestClient:
    """Create test client."""
    from protocols.api.app import create_app

    app = create_app()
    return TestClient(app)


class TestPortalResolveEndpoint:
    """Tests for POST /api/portal/resolve."""

    def test_resolve_file_uri_success(self, client: TestClient, sample_file: Path):
        """Test resolving a file: URI to an existing file."""
        uri = f"file:{sample_file}"

        response = client.post(
            "/api/portal/resolve",
            json={"uri": uri},
        )

        assert response.status_code == 200
        data = response.json()

        assert data["uri"] == uri
        assert data["resource_type"] == "file"
        assert data["exists"] is True
        assert data["title"] == "test.md"
        assert "Test Document" in data["preview"]
        # Content can be str or dict depending on FileResolver implementation
        assert data["content"] is not None
        assert "expand" in data["actions"]

    def test_resolve_file_uri_nonexistent(self, client: TestClient, tmp_path: Path):
        """Test resolving a file: URI to a nonexistent file."""
        nonexistent = tmp_path / "does_not_exist.md"
        uri = f"file:{nonexistent}"

        response = client.post(
            "/api/portal/resolve",
            json={"uri": uri},
        )

        # FileResolver raises ResourceNotFound, which becomes 404
        assert response.status_code == 404

    def test_resolve_malformed_uri(self, client: TestClient):
        """Test resolving a malformed URI."""
        response = client.post(
            "/api/portal/resolve",
            json={"uri": "not::a::valid::uri"},
        )

        # URI parser treats "not" as resource type
        # This will fail with "Unknown resource type"
        assert response.status_code == 400

    def test_resolve_unknown_resource_type(self, client: TestClient):
        """Test resolving a URI with unknown resource type."""
        response = client.post(
            "/api/portal/resolve",
            json={"uri": "unknown:resource"},
        )

        assert response.status_code == 400
        assert "Unknown resource type" in response.json()["detail"]

    def test_resolve_missing_uri(self, client: TestClient):
        """Test resolving without providing URI."""
        response = client.post(
            "/api/portal/resolve",
            json={},
        )

        assert response.status_code == 422  # Validation error

    def test_resolve_chat_uri(self, client: TestClient):
        """Test resolving a chat: URI."""
        # Chat resolver requires session_store dependency which might not be available
        # Just test that the endpoint handles it gracefully
        response = client.post(
            "/api/portal/resolve",
            json={"uri": "chat:session-123"},
        )

        # Either succeeds or fails gracefully
        # ChatResolver might not be registered if dependencies are missing
        assert response.status_code in (200, 400, 404)

    def test_resolve_mark_uri(self, client: TestClient):
        """Test resolving a mark: URI."""
        # Mark URIs resolve through MarkResolver (no dependencies)
        response = client.post(
            "/api/portal/resolve",
            json={"uri": "mark:mark-123"},
        )

        # Should succeed (even if mark doesn't exist, resolver handles it)
        assert response.status_code in (200, 404)

        if response.status_code == 200:
            data = response.json()
            assert data["resource_type"] == "mark"


class TestPortalHealthEndpoint:
    """Tests for GET /api/portal/health."""

    def test_portal_health(self, client: TestClient):
        """Test portal health check."""
        response = client.get("/api/portal/health")

        assert response.status_code == 200
        data = response.json()

        assert "status" in data
        assert data["status"] in ("ok", "error")
        assert "registered_types" in data

        # Should have at least file resolver registered
        if data["status"] == "ok":
            assert isinstance(data["registered_types"], list)
            assert "file" in data["registered_types"]


class TestPortalResolverIntegration:
    """Integration tests for portal resolver."""

    def test_multiple_resolvers_registered(self, client: TestClient):
        """Test that multiple resolver types are registered."""
        response = client.get("/api/portal/health")
        assert response.status_code == 200
        data = response.json()

        # Should have several resolvers
        if data["status"] == "ok":
            registered = data["registered_types"]
            assert len(registered) > 0

            # Core resolvers that don't require dependencies
            expected_core = ["file", "mark", "trace", "evidence", "constitutional", "crystal"]
            for resolver_type in expected_core:
                assert resolver_type in registered

    def test_resolve_different_resource_types(self, client: TestClient, sample_file: Path):
        """Test resolving different resource types."""
        test_cases = [
            (f"file:{sample_file}", "file"),
            ("mark:mark-123", "mark"),
            ("trace:trace-456", "trace"),
            ("evidence:evidence-789", "evidence"),
            ("constitutional:const-abc", "constitutional"),
            ("crystal:crystal-xyz", "crystal"),
        ]

        for uri, expected_type in test_cases:
            response = client.post(
                "/api/portal/resolve",
                json={"uri": uri},
            )

            # Should either resolve or return 404 (but not error)
            assert response.status_code in (200, 404), f"Failed for {uri}"

            if response.status_code == 200:
                data = response.json()
                assert data["resource_type"] == expected_type


class TestPortalResolverErrorHandling:
    """Tests for error handling in portal resolver."""

    def test_resolve_empty_uri(self, client: TestClient):
        """Test resolving empty URI."""
        response = client.post(
            "/api/portal/resolve",
            json={"uri": ""},
        )

        assert response.status_code in (400, 422)

    def test_resolve_invalid_json(self, client: TestClient):
        """Test resolving with invalid JSON."""
        response = client.post(
            "/api/portal/resolve",
            content=b"not json",
            headers={"Content-Type": "application/json"},
        )

        assert response.status_code == 422

    def test_resolve_uri_with_special_chars(self, client: TestClient):
        """Test resolving URI with special characters."""
        # Some special chars might be valid in resource paths
        response = client.post(
            "/api/portal/resolve",
            json={"uri": "file:spec/protocols/portal-resource-system.md#section"},
        )

        # Should either resolve or fail gracefully
        assert response.status_code in (200, 400, 404)


__all__ = [
    "TestPortalResolveEndpoint",
    "TestPortalHealthEndpoint",
    "TestPortalResolverIntegration",
    "TestPortalResolverErrorHandling",
]
