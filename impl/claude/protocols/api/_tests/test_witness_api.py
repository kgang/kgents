"""
Test Witness REST API endpoints.

Verifies:
- POST /api/witness/marks - Create mark
- GET /api/witness/marks - List marks with filters
- GET /api/witness/stream - SSE stream
"""

import pytest
from fastapi.testclient import TestClient

from protocols.api.app import create_app


@pytest.fixture
def client() -> TestClient:
    """Create test client."""
    app = create_app()
    return TestClient(app)


@pytest.mark.asyncio
async def test_create_mark(client: TestClient):
    """Test creating a witness mark."""
    response = client.post(
        "/api/witness/marks",
        json={
            "action": "Test action",
            "reasoning": "Test reasoning",
            "principles": ["composable", "tasteful"],
            "author": "claude",
        },
    )

    assert response.status_code == 200
    data = response.json()

    assert "id" in data
    assert data["action"] == "Test action"
    assert data["reasoning"] == "Test reasoning"
    assert "composable" in data["principles"]
    assert data["author"] == "claude"
    assert "timestamp" in data


@pytest.mark.asyncio
async def test_list_marks(client: TestClient):
    """Test listing marks."""
    # Create a mark first
    client.post(
        "/api/witness/marks",
        json={
            "action": "List test action",
            "reasoning": "Testing list",
            "author": "kent",
        },
    )

    # List marks
    response = client.get("/api/witness/marks?limit=10")
    assert response.status_code == 200

    data = response.json()
    assert "marks" in data
    assert "total" in data
    assert isinstance(data["marks"], list)


@pytest.mark.asyncio
async def test_filter_marks_by_author(client: TestClient):
    """Test filtering marks by author."""
    # Create marks with different authors
    client.post(
        "/api/witness/marks",
        json={"action": "Kent action", "author": "kent"},
    )
    client.post(
        "/api/witness/marks",
        json={"action": "Claude action", "author": "claude"},
    )

    # Filter by author
    response = client.get("/api/witness/marks?author=kent")
    assert response.status_code == 200

    data = response.json()
    for mark in data["marks"]:
        assert mark["author"] == "kent"


@pytest.mark.asyncio
async def test_filter_marks_today(client: TestClient):
    """Test filtering marks from today."""
    client.post(
        "/api/witness/marks",
        json={"action": "Today's action", "author": "system"},
    )

    response = client.get("/api/witness/marks?today=true")
    assert response.status_code == 200

    data = response.json()
    assert len(data["marks"]) >= 1


@pytest.mark.asyncio
async def test_filter_marks_by_principle(client: TestClient):
    """Test filtering marks by principle."""
    client.post(
        "/api/witness/marks",
        json={
            "action": "Composable action",
            "principles": ["composable"],
        },
    )

    response = client.get("/api/witness/marks?principle=composable")
    assert response.status_code == 200

    data = response.json()
    for mark in data["marks"]:
        assert "composable" in mark["principles"]


@pytest.mark.asyncio
async def test_grep_marks(client: TestClient):
    """Test text search in marks."""
    client.post(
        "/api/witness/marks",
        json={
            "action": "Unique searchable text",
            "reasoning": "Should be found",
        },
    )

    response = client.get("/api/witness/marks?grep=searchable")
    assert response.status_code == 200

    data = response.json()
    assert len(data["marks"]) >= 1
    assert any("searchable" in m["action"].lower() for m in data["marks"])


@pytest.mark.asyncio
async def test_create_dialectic_decision(client: TestClient):
    """Test creating a dialectic decision."""
    response = client.post(
        "/api/witness/decisions",
        json={
            "thesis_content": "Use React",
            "thesis_reasoning": "Fast development",
            "antithesis_content": "Use Svelte",
            "antithesis_reasoning": "Smaller bundle",
            "synthesis": "Use React with code splitting",
            "why": "Best of both worlds",
            "tags": ["frontend", "architecture"],
        },
    )

    assert response.status_code == 200
    data = response.json()

    assert "id" in data
    assert data["thesis"]["content"] == "Use React"
    assert data["antithesis"]["content"] == "Use Svelte"
    assert data["synthesis"] == "Use React with code splitting"
    assert "frontend" in data["tags"]


@pytest.mark.asyncio
async def test_list_dialectic_decisions(client: TestClient):
    """Test listing dialectic decisions."""
    # Create a decision first
    client.post(
        "/api/witness/decisions",
        json={
            "thesis_content": "Decision A",
            "thesis_reasoning": "Reasoning A",
            "antithesis_content": "Decision B",
            "antithesis_reasoning": "Reasoning B",
            "synthesis": "Decision C",
            "why": "Because",
        },
    )

    response = client.get("/api/witness/decisions?limit=10")
    assert response.status_code == 200

    data = response.json()
    assert "decisions" in data
    assert "total" in data
    assert len(data["decisions"]) >= 1


@pytest.mark.asyncio
async def test_witness_stream_connection(client: TestClient):
    """Test SSE stream connection."""
    with client.stream("GET", "/api/witness/stream") as response:
        assert response.status_code == 200
        assert response.headers["content-type"] == "text/event-stream; charset=utf-8"

        # Read first event (should be connected event)
        chunk = next(response.iter_lines())
        assert b"connected" in chunk or b"event:" in chunk
