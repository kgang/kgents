"""
Integration tests for Onboarding API.

Tests the complete FTUE flow:
1. Start onboarding session
2. Create first K-Block from declaration
3. Mark onboarding complete

Validates that K-Blocks are properly persisted to PostgreSQL storage.
"""

import pytest

pytest.importorskip("fastapi")

from fastapi.testclient import TestClient

from protocols.api.app import create_app

pytestmark = pytest.mark.tier2


@pytest.fixture
def client():
    """Create test client."""
    app = create_app(
        enable_cors=False,
        enable_tenant_middleware=False,
    )
    return TestClient(app)


def test_onboarding_start(client: TestClient):
    """Test starting onboarding session."""
    response = client.post("/api/onboarding/start", json={})
    assert response.status_code == 200

    data = response.json()
    assert "session_id" in data
    assert "started_at" in data
    assert isinstance(data["session_id"], str)


def test_first_declaration_creates_kblock(client: TestClient):
    """Test that first declaration creates a real K-Block."""
    # Start session
    start_response = client.post("/api/onboarding/start", json={})
    session_id = start_response.json()["session_id"]

    # Create first declaration
    declaration = "I want to build a personal knowledge base"
    response = client.post(
        "/api/onboarding/first-declaration",
        json={
            "declaration": declaration,
            "session_id": session_id,
        },
    )

    assert response.status_code == 200
    data = response.json()

    # Validate response structure
    assert "kblock_id" in data
    assert "layer" in data
    assert "loss" in data
    assert "justification" in data
    assert "celebration" in data

    # Validate K-Block metadata
    assert isinstance(data["kblock_id"], str)
    assert data["layer"] == 1  # FTUE always assigns to L1 Axiom (foundational, no lineage)
    assert 0.0 <= data["loss"] <= 1.0
    assert isinstance(data["justification"], str)

    # Validate celebration data
    celebration = data["celebration"]
    assert celebration["confetti"] is True
    assert "emoji" in celebration
    assert "message" in celebration
    assert "color" in celebration
    assert celebration["intensity"] in ["high", "medium", "low"]


def test_layer_assignment_logic(client: TestClient):
    """Test that layer assignment always returns L1 for FTUE."""
    # All FTUE declarations go to L1 Axiom (foundational, no lineage required)
    test_cases = [
        "I believe in open source",
        "I want to learn Python",
        "I'm exploring what matters to me",
    ]

    for declaration in test_cases:
        response = client.post(
            "/api/onboarding/first-declaration",
            json={"declaration": declaration},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["layer"] == 1, \
            f"FTUE declaration '{declaration}' should be L1 Axiom, got L{data['layer']}"


def test_loss_computation(client: TestClient):
    """Test that loss computation varies with specificity."""
    # Very specific (long) - should have lower loss
    specific = "I want to build a personal knowledge management system that uses spaced repetition and connects ideas through bidirectional links, inspired by Zettelkasten"

    # Vague (short) - should have higher loss
    vague = "I'm exploring"

    specific_response = client.post(
        "/api/onboarding/first-declaration",
        json={"declaration": specific},
    )
    vague_response = client.post(
        "/api/onboarding/first-declaration",
        json={"declaration": vague},
    )

    assert specific_response.status_code == 200
    assert vague_response.status_code == 200

    specific_loss = specific_response.json()["loss"]
    vague_loss = vague_response.json()["loss"]

    # More specific = lower loss
    assert specific_loss < vague_loss


def test_onboarding_status(client: TestClient):
    """Test onboarding status endpoint."""
    # Before any declaration
    status = client.get("/api/onboarding/status")
    assert status.status_code == 200
    assert status.json()["completed"] is False

    # After declaration
    start = client.post("/api/onboarding/start", json={})
    session_id = start.json()["session_id"]

    client.post(
        "/api/onboarding/first-declaration",
        json={
            "declaration": "I want to test the system",
            "session_id": session_id,
        },
    )

    # Check session status
    status_with_session = client.get(
        "/api/onboarding/status",
        params={"session_id": session_id},
    )
    assert status_with_session.status_code == 200
    data = status_with_session.json()
    assert data["completed"] is True
    assert data["session_id"] == session_id
    assert data["first_kblock_id"] is not None


def test_onboarding_complete(client: TestClient):
    """Test marking onboarding as complete."""
    response = client.post("/api/onboarding/complete")

    assert response.status_code == 200
    data = response.json()

    assert data["success"] is True
    assert "completed_at" in data
    assert "message" in data
    assert "kgents" in data["message"].lower()


def test_celebration_intensity_varies_with_loss(client: TestClient):
    """Test that celebration intensity correlates with loss score."""
    # Clear declaration (low loss) - should get high intensity
    clear = "I value clarity and simplicity in design"

    # Vague declaration (high loss) - should get low intensity
    vague = "I'm exploring some things maybe"

    clear_response = client.post(
        "/api/onboarding/first-declaration",
        json={"declaration": clear},
    )
    vague_response = client.post(
        "/api/onboarding/first-declaration",
        json={"declaration": vague},
    )

    clear_celebration = clear_response.json()["celebration"]
    vague_celebration = vague_response.json()["celebration"]

    intensity_order = {"high": 3, "medium": 2, "low": 1}

    clear_intensity = intensity_order[clear_celebration["intensity"]]
    vague_intensity = intensity_order[vague_celebration["intensity"]]

    # Better coherence = more intense celebration
    assert clear_intensity >= vague_intensity
