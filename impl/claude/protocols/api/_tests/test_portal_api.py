"""
Tests for Portal Tool API endpoints.

Verifies:
- Portal emission endpoint (/api/chat/portal/emit)
- Portal write endpoint (/api/chat/portal/write)
- Portal emissions in turn responses
- Error handling for invalid portals

See: services/tooling/tools/portal.py
See: protocols/api/chat.py
"""

from __future__ import annotations

from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest

pytestmark = pytest.mark.asyncio


@pytest.fixture
def sample_file(tmp_path: Path) -> Path:
    """Create a sample file for testing."""
    file = tmp_path / "test.txt"
    file.write_text("Line 1\nLine 2\nLine 3\n")
    return file


@pytest.fixture
def app():
    """Create FastAPI app for testing."""
    from protocols.api.app import create_app

    return create_app()


@pytest.fixture
async def client(app):
    """Create async test client."""
    from httpx import ASGITransport, AsyncClient

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


class TestPortalEmitEndpoint:
    """Tests for POST /api/chat/portal/emit."""

    async def test_emit_portal_success(self, client, sample_file: Path):
        """Test emitting a portal to an existing file."""
        response = await client.post(
            "/api/chat/portal/emit",
            json={
                "destination": str(sample_file),
                "edge_type": "context",
                "access": "read",
                "auto_expand": True,
            },
        )

        assert response.status_code == 200
        data = response.json()

        assert "portal_id" in data
        assert data["destination"] == str(sample_file)
        assert data["edge_type"] == "context"
        assert data["access"] == "read"
        assert data["exists"] is True
        assert data["auto_expand"] is True
        assert data["line_count"] == 3
        assert data["content_full"] == "Line 1\nLine 2\nLine 3\n"

    async def test_emit_portal_nonexistent_file(self, client, tmp_path: Path):
        """Test emitting a portal to a nonexistent file."""
        nonexistent = tmp_path / "does_not_exist.txt"

        response = await client.post(
            "/api/chat/portal/emit",
            json={
                "destination": str(nonexistent),
                "edge_type": "context",
                "access": "read",
            },
        )

        assert response.status_code == 200
        data = response.json()

        assert data["exists"] is False
        assert data["content_preview"] is None
        assert data["content_full"] is None
        assert data["line_count"] == 0

    async def test_emit_portal_readwrite_access(self, client, sample_file: Path):
        """Test emitting a portal with readwrite access."""
        response = await client.post(
            "/api/chat/portal/emit",
            json={
                "destination": str(sample_file),
                "edge_type": "edits",
                "access": "readwrite",
                "auto_expand": False,
            },
        )

        assert response.status_code == 200
        data = response.json()

        assert data["access"] == "readwrite"
        assert data["auto_expand"] is False
        assert data["edge_type"] == "edits"

    async def test_emit_portal_default_values(self, client, sample_file: Path):
        """Test emitting a portal with default values."""
        response = await client.post(
            "/api/chat/portal/emit",
            json={"destination": str(sample_file)},
        )

        assert response.status_code == 200
        data = response.json()

        # Check defaults
        assert data["edge_type"] == "context"
        assert data["access"] == "read"
        assert data["auto_expand"] is True


class TestPortalWriteEndpoint:
    """Tests for POST /api/chat/portal/write."""

    async def test_write_portal_success(self, client, sample_file: Path):
        """Test writing through an open portal."""
        # First, emit a portal with readwrite access
        emit_response = await client.post(
            "/api/chat/portal/emit",
            json={
                "destination": str(sample_file),
                "access": "readwrite",
            },
        )
        assert emit_response.status_code == 200
        portal_id = emit_response.json()["portal_id"]

        # Now write through the portal
        new_content = "Updated Line 1\nUpdated Line 2\n"
        write_response = await client.post(
            "/api/chat/portal/write",
            json={
                "portal_id": portal_id,
                "content": new_content,
            },
        )

        assert write_response.status_code == 200
        data = write_response.json()

        assert data["success"] is True
        assert data["portal_id"] == portal_id
        assert data["bytes_written"] == len(new_content.encode())

        # Verify file was updated
        assert sample_file.read_text() == new_content

    async def test_write_portal_read_only_fails(self, client, sample_file: Path):
        """Test writing through a read-only portal fails."""
        # Emit a read-only portal
        emit_response = await client.post(
            "/api/chat/portal/emit",
            json={
                "destination": str(sample_file),
                "access": "read",
            },
        )
        assert emit_response.status_code == 200
        portal_id = emit_response.json()["portal_id"]

        # Attempt to write (should fail)
        write_response = await client.post(
            "/api/chat/portal/write",
            json={
                "portal_id": portal_id,
                "content": "Should fail",
            },
        )

        assert write_response.status_code == 500
        assert "Portal is read-only" in write_response.json()["detail"]

    async def test_write_portal_not_open(self, client):
        """Test writing through a portal that was never opened."""
        write_response = await client.post(
            "/api/chat/portal/write",
            json={
                "portal_id": "fake-portal-id",
                "content": "Should fail",
            },
        )

        assert write_response.status_code == 500
        assert "Portal not open" in write_response.json()["detail"]


class TestPortalInTurns:
    """Tests for portal emissions in turn responses."""

    async def test_turn_includes_portal_emissions(self, client, sample_file: Path):
        """Test that turns include portal_emissions field."""
        # Create a session
        session_response = await client.post(
            "/api/chat/session",
            json={"branch_name": "main"},
        )
        assert session_response.status_code == 201
        session_id = session_response.json()["id"]

        # Mock K-gent bridge to emit a portal
        with patch("protocols.api.chat.get_kgent_bridge") as mock_bridge:
            # Create mock stream that includes portal emission
            async def mock_stream(context):
                # Simulate portal tool use
                yield 'data: {"type": "content", "content": "Opening portal..."}\n\n'
                yield f'data: {{"type": "done", "turn": {{"completed_at": "2025-12-25T10:00:00Z", "mark_id": "mark_123", "tools_used": [{{"name": "portal.emit", "success": true, "input": {{"destination": "{sample_file}"}}, "output": {{"portal_id": "portal_123"}}, "duration_ms": 10.0}}]}}}}\n\n'

            mock_instance = AsyncMock()
            mock_instance.stream_response = mock_stream
            mock_bridge.return_value = mock_instance

            # Send a message
            response = await client.post(
                f"/api/chat/{session_id}/send",
                json={"message": "Open portal to test.txt"},
            )

            assert response.status_code == 200

        # Verify session has the turn
        session = await client.get(f"/api/chat/session/{session_id}")
        assert session.status_code == 200
        data = session.json()

        assert len(data["turns"]) == 1
        turn = data["turns"][0]

        # Verify portal_emissions field exists (even if empty in this mock)
        assert "portal_emissions" in turn
        assert isinstance(turn["portal_emissions"], list)


class TestPortalErrorHandling:
    """Tests for portal error handling."""

    async def test_emit_portal_missing_destination(self, client):
        """Test emitting portal without destination."""
        response = await client.post(
            "/api/chat/portal/emit",
            json={
                "edge_type": "context",
            },
        )

        assert response.status_code == 422  # Validation error

    async def test_write_portal_missing_content(self, client):
        """Test writing portal without content."""
        response = await client.post(
            "/api/chat/portal/write",
            json={
                "portal_id": "some-id",
            },
        )

        assert response.status_code == 422  # Validation error

    async def test_emit_portal_invalid_access(self, client, sample_file: Path):
        """Test emitting portal with invalid access level."""
        response = await client.post(
            "/api/chat/portal/emit",
            json={
                "destination": str(sample_file),
                "access": "invalid",
            },
        )

        assert response.status_code == 422  # Validation error


class TestPortalContentPreview:
    """Tests for portal content preview behavior."""

    async def test_portal_preview_short_file(self, client, tmp_path: Path):
        """Test portal preview for short files."""
        file = tmp_path / "short.txt"
        file.write_text("Line 1\nLine 2\n")

        response = await client.post(
            "/api/chat/portal/emit",
            json={"destination": str(file)},
        )

        assert response.status_code == 200
        data = response.json()

        # Short files don't need preview (full content is small)
        assert data["line_count"] == 2
        assert data["content_full"] == "Line 1\nLine 2\n"

    async def test_portal_preview_long_file(self, client, tmp_path: Path):
        """Test portal preview for long files."""
        file = tmp_path / "long.txt"
        lines = [f"Line {i}\n" for i in range(50)]
        file.write_text("".join(lines))

        response = await client.post(
            "/api/chat/portal/emit",
            json={"destination": str(file)},
        )

        assert response.status_code == 200
        data = response.json()

        assert data["line_count"] == 50
        # Preview should be first N lines (default 10)
        if data["content_preview"] is not None:
            preview_lines = data["content_preview"].split("\n")
            assert len(preview_lines) <= 11  # 10 lines + potential empty line


# =============================================================================
# Integration Tests
# =============================================================================


class TestPortalWorkflow:
    """End-to-end tests for portal workflow."""

    async def test_full_portal_workflow(self, client, sample_file: Path):
        """Test complete portal workflow: emit -> read -> write."""
        # 1. Emit portal
        emit_response = await client.post(
            "/api/chat/portal/emit",
            json={
                "destination": str(sample_file),
                "access": "readwrite",
            },
        )
        assert emit_response.status_code == 200
        portal_data = emit_response.json()
        portal_id = portal_data["portal_id"]

        # Verify initial content
        assert portal_data["content_full"] == "Line 1\nLine 2\nLine 3\n"

        # 2. Write through portal
        new_content = "Modified content\n"
        write_response = await client.post(
            "/api/chat/portal/write",
            json={
                "portal_id": portal_id,
                "content": new_content,
            },
        )
        assert write_response.status_code == 200
        assert write_response.json()["success"] is True

        # 3. Emit portal again to see updated content
        emit_response2 = await client.post(
            "/api/chat/portal/emit",
            json={"destination": str(sample_file)},
        )
        assert emit_response2.status_code == 200
        assert emit_response2.json()["content_full"] == new_content

    async def test_multiple_portals_same_file(self, client, sample_file: Path):
        """Test opening multiple portals to the same file."""
        # Open first portal (read)
        response1 = await client.post(
            "/api/chat/portal/emit",
            json={
                "destination": str(sample_file),
                "access": "read",
            },
        )
        assert response1.status_code == 200
        portal1_id = response1.json()["portal_id"]

        # Open second portal (readwrite)
        response2 = await client.post(
            "/api/chat/portal/emit",
            json={
                "destination": str(sample_file),
                "access": "readwrite",
            },
        )
        assert response2.status_code == 200
        portal2_id = response2.json()["portal_id"]

        # Portals should have different IDs
        assert portal1_id != portal2_id

        # Should be able to write through portal2
        write_response = await client.post(
            "/api/chat/portal/write",
            json={
                "portal_id": portal2_id,
                "content": "Updated via portal2\n",
            },
        )
        assert write_response.status_code == 200
        assert write_response.json()["success"] is True


__all__ = [
    "TestPortalEmitEndpoint",
    "TestPortalWriteEndpoint",
    "TestPortalInTurns",
    "TestPortalErrorHandling",
    "TestPortalContentPreview",
    "TestPortalWorkflow",
]
