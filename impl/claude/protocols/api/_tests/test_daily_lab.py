"""
Test Daily Lab REST API endpoints.

Verifies:
- POST /api/witness/daily/capture - Capture a mark
- GET  /api/witness/daily/trail   - Get today's trail
- POST /api/witness/daily/crystallize - Crystallize day's marks
- GET  /api/witness/daily/export  - Export day's work

See: services/witness/daily_lab.py for the underlying service
"""

import pytest
from fastapi.testclient import TestClient

from protocols.api.app import create_app


@pytest.fixture
def client() -> TestClient:
    """Create test client."""
    app = create_app()
    return TestClient(app)


# =============================================================================
# Capture Tests
# =============================================================================


@pytest.mark.asyncio
async def test_capture_quick_mark(client: TestClient):
    """Test capturing a quick mark (no tag, no reasoning)."""
    response = client.post(
        "/api/witness/daily/capture",
        json={"content": "Found an interesting pattern in the code"},
    )

    assert response.status_code == 200
    data = response.json()

    assert "mark_id" in data
    assert data["content"] == "Found an interesting pattern in the code"
    assert data["tag"] is None
    assert "timestamp" in data
    assert data["warmth_response"] == "Got it."


@pytest.mark.asyncio
async def test_capture_tagged_mark(client: TestClient):
    """Test capturing a mark with a tag."""
    response = client.post(
        "/api/witness/daily/capture",
        json={
            "content": "Realized the Galois connection works!",
            "tag": "eureka",
        },
    )

    assert response.status_code == 200
    data = response.json()

    assert "mark_id" in data
    assert data["content"] == "Realized the Galois connection works!"
    assert data["tag"] == "eureka"
    assert "eureka" in data["warmth_response"]


@pytest.mark.asyncio
async def test_capture_with_reasoning(client: TestClient):
    """Test capturing a mark with reasoning."""
    response = client.post(
        "/api/witness/daily/capture",
        json={
            "content": "Chose to use SSE over WebSockets",
            "tag": "taste",
            "reasoning": "Simpler for unidirectional data flow",
        },
    )

    assert response.status_code == 200
    data = response.json()

    assert "mark_id" in data
    assert data["tag"] == "taste"
    assert "taste" in data["warmth_response"]


@pytest.mark.asyncio
async def test_capture_invalid_tag(client: TestClient):
    """Test capturing with an invalid tag returns 400."""
    response = client.post(
        "/api/witness/daily/capture",
        json={
            "content": "Some content",
            "tag": "invalid_tag",
        },
    )

    assert response.status_code == 400
    assert "Invalid tag" in response.json()["detail"]


@pytest.mark.asyncio
async def test_capture_missing_content(client: TestClient):
    """Test that content is required."""
    response = client.post(
        "/api/witness/daily/capture",
        json={},
    )

    # Pydantic validation error (422 Unprocessable Entity)
    assert response.status_code == 422


# =============================================================================
# Trail Tests
# =============================================================================


@pytest.mark.asyncio
async def test_get_trail_today(client: TestClient):
    """Test getting today's trail."""
    # First capture a mark to ensure there's at least one
    client.post(
        "/api/witness/daily/capture",
        json={"content": "Trail test mark"},
    )

    response = client.get("/api/witness/daily/trail")

    assert response.status_code == 200
    data = response.json()

    assert "marks" in data
    assert "date" in data
    assert "total" in data
    assert "position" in data
    assert "review_prompt" in data
    assert isinstance(data["marks"], list)


@pytest.mark.asyncio
async def test_get_trail_specific_date(client: TestClient):
    """Test getting trail for a specific date."""
    response = client.get("/api/witness/daily/trail?target_date=2025-01-15")

    assert response.status_code == 200
    data = response.json()

    assert data["date"] == "2025-01-15"


@pytest.mark.asyncio
async def test_get_trail_invalid_date(client: TestClient):
    """Test getting trail with invalid date format."""
    response = client.get("/api/witness/daily/trail?target_date=not-a-date")

    assert response.status_code == 400
    assert "Invalid date format" in response.json()["detail"]


@pytest.mark.asyncio
async def test_get_trail_important_only(client: TestClient):
    """Test filtering trail to important marks only."""
    # Capture some marks with different tags
    client.post(
        "/api/witness/daily/capture",
        json={"content": "A eureka moment", "tag": "eureka"},
    )
    client.post(
        "/api/witness/daily/capture",
        json={"content": "Some friction", "tag": "friction"},
    )

    response = client.get("/api/witness/daily/trail?important_only=true")

    assert response.status_code == 200
    data = response.json()

    # Important marks are: eureka, veto, taste
    for mark in data["marks"]:
        # At least one tag should be important if mark has tags
        if mark["tags"]:
            assert any(t in ["eureka", "veto", "taste"] for t in mark["tags"])


# =============================================================================
# Crystallize Tests
# =============================================================================


@pytest.mark.asyncio
async def test_crystallize_insufficient_marks(client: TestClient):
    """Test crystallization with insufficient marks."""
    # Get trail for a date in the past with likely no marks
    response = client.post(
        "/api/witness/daily/crystallize?target_date=2020-01-01",
    )

    assert response.status_code == 200
    data = response.json()

    assert data["success"] is False
    assert data["crystal_id"] is None
    assert "Not enough marks" in data["disclosure"]


@pytest.mark.asyncio
async def test_crystallize_with_marks(client: TestClient):
    """Test crystallization with sufficient marks."""
    # Capture at least 3 marks (minimum for crystallization)
    for i in range(4):
        client.post(
            "/api/witness/daily/capture",
            json={
                "content": f"Test mark {i} for crystallization",
                "tag": "eureka" if i == 0 else None,
            },
        )

    response = client.post("/api/witness/daily/crystallize")

    assert response.status_code == 200
    data = response.json()

    # Either success or not enough marks (depending on existing marks)
    assert "success" in data
    assert "disclosure" in data
    assert "warmth_response" in data

    if data["success"]:
        assert data["crystal_id"] is not None
        assert data["insight"] is not None or data["summary"] is not None
        assert "compression_honesty" in data


@pytest.mark.asyncio
async def test_crystallize_invalid_date(client: TestClient):
    """Test crystallization with invalid date."""
    response = client.post(
        "/api/witness/daily/crystallize?target_date=bad-date",
    )

    assert response.status_code == 400
    assert "Invalid date format" in response.json()["detail"]


# =============================================================================
# Export Tests
# =============================================================================


@pytest.mark.asyncio
async def test_export_markdown(client: TestClient):
    """Test exporting day's work as markdown."""
    # Capture a mark first
    client.post(
        "/api/witness/daily/capture",
        json={"content": "Export test mark"},
    )

    response = client.get("/api/witness/daily/export?format=markdown")

    assert response.status_code == 200
    data = response.json()

    assert data["format"] == "markdown"
    assert "content" in data
    assert "date" in data
    assert data["warmth_response"] == "Here's a snapshot you can share."

    # Check markdown structure
    assert "# Daily Review:" in data["content"] or "# " in data["content"]


@pytest.mark.asyncio
async def test_export_json(client: TestClient):
    """Test exporting day's work as JSON."""
    response = client.get("/api/witness/daily/export?format=json")

    assert response.status_code == 200
    data = response.json()

    assert data["format"] == "json"
    assert "content" in data

    # Content should be valid JSON string
    import json

    parsed = json.loads(data["content"])
    assert "title" in parsed
    assert "date_range" in parsed


@pytest.mark.asyncio
async def test_export_invalid_date(client: TestClient):
    """Test export with invalid date."""
    response = client.get("/api/witness/daily/export?target_date=invalid")

    assert response.status_code == 400
    assert "Invalid date format" in response.json()["detail"]


@pytest.mark.asyncio
async def test_export_specific_date(client: TestClient):
    """Test export for specific date."""
    response = client.get("/api/witness/daily/export?target_date=2025-01-15&format=markdown")

    assert response.status_code == 200
    data = response.json()

    assert data["date"] == "2025-01-15"


@pytest.mark.asyncio
async def test_export_without_crystal(client: TestClient):
    """Test export without including crystal."""
    response = client.get("/api/witness/daily/export?include_crystal=false&format=markdown")

    assert response.status_code == 200
    data = response.json()

    assert data["format"] == "markdown"
    assert "content" in data


# =============================================================================
# Integration Tests
# =============================================================================


@pytest.mark.asyncio
async def test_capture_trail_flow(client: TestClient):
    """Test the complete flow: capture marks then view trail."""
    # Capture multiple marks
    marks = []
    for tag in ["eureka", "gotcha", "taste"]:
        response = client.post(
            "/api/witness/daily/capture",
            json={
                "content": f"Test {tag} mark",
                "tag": tag,
            },
        )
        assert response.status_code == 200
        marks.append(response.json()["mark_id"])

    # View the trail
    response = client.get("/api/witness/daily/trail")
    assert response.status_code == 200

    data = response.json()
    trail_mark_ids = [m["mark_id"] for m in data["marks"]]

    # At least our new marks should be there
    for mark_id in marks:
        assert mark_id in trail_mark_ids
