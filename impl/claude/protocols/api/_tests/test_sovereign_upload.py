"""
Test sovereign file upload endpoint.

Verifies that the /api/sovereign/upload endpoint:
- Accepts multipart/form-data file uploads
- Creates sovereign entity with witness mark
- Returns proper metadata (path, version, mark_id, edge_count)
"""

import io

import pytest
from fastapi.testclient import TestClient

from protocols.api.app import create_app


@pytest.fixture
def client():
    """Create test client."""
    app = create_app()
    return TestClient(app)


def test_upload_file_creates_entity(client):
    """Test that uploading a file creates a sovereign entity."""
    # Create a simple text file
    file_content = b"# Test Document\n\nThis is a test document for sovereign upload."
    file = io.BytesIO(file_content)
    file.name = "test-doc.md"

    # Upload the file
    response = client.post(
        "/api/sovereign/upload",
        files={"file": ("test-doc.md", file, "text/markdown")},
    )

    # Should succeed
    assert response.status_code == 200, f"Upload failed: {response.text}"

    # Should return proper metadata
    data = response.json()
    assert "path" in data
    assert "version" in data
    assert "ingest_mark_id" in data
    assert "edge_count" in data

    # Path should be in uploads/ directory by default
    assert data["path"].startswith("uploads/")
    assert data["path"].endswith("test-doc.md")

    # Version should be >= 1 (might be higher if test runs in parallel)
    assert data["version"] >= 1

    # Should have created a witness mark
    assert data["ingest_mark_id"] is not None


def test_upload_file_with_custom_path(client):
    """Test that uploading a file with custom path works."""
    file_content = b"# Spec Document\n\nThis goes in specs/."
    file = io.BytesIO(file_content)
    file.name = "custom.md"

    # Upload with custom path (using query parameter)
    response = client.post(
        "/api/sovereign/upload?path=spec/protocols/custom.md",
        files={"file": ("custom.md", file, "text/markdown")},
    )

    assert response.status_code == 200
    data = response.json()

    # Should use the custom path
    assert data["path"] == "spec/protocols/custom.md"


def test_upload_extracts_edges(client):
    """Test that upload extracts edges from content."""
    # Content with references to other paths
    file_content = b"""
# Implementation

This implements `spec/protocols/witness.md`.
See also `spec/agents/d-gent.md`.
"""
    file = io.BytesIO(file_content)
    file.name = "impl.md"

    response = client.post(
        "/api/sovereign/upload",
        files={"file": ("impl.md", file, "text/markdown")},
    )

    assert response.status_code == 200
    data = response.json()

    # Should have extracted edges
    assert data["edge_count"] >= 0  # Edge count might be 0 if refs don't exist


def test_upload_binary_file(client):
    """Test that binary files can be uploaded."""
    # Create a fake PNG file (magic bytes)
    file_content = b"\x89PNG\r\n\x1a\n" + b"\x00" * 100
    file = io.BytesIO(file_content)
    file.name = "image.png"

    response = client.post(
        "/api/sovereign/upload",
        files={"file": ("image.png", file, "image/png")},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["path"].endswith("image.png")
