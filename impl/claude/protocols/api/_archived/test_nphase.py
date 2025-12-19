"""
Tests for N-Phase Session API Endpoints.

Tests REST endpoints for:
- Session management (CRUD)
- Phase advancement
- Checkpoint/restore
- Handle tracking
- Phase detection

See: protocols/api/nphase.py
"""

from __future__ import annotations

import pytest

try:
    from fastapi.testclient import TestClient

    HAS_FASTAPI = True
except ImportError:
    HAS_FASTAPI = False
    TestClient = None  # type: ignore

from protocols.api.app import create_app
from protocols.nphase.session import reset_session_store


@pytest.fixture(autouse=True)
def clean_store() -> None:
    """Reset session store before each test."""
    reset_session_store()


@pytest.fixture
def client() -> "TestClient":
    """Create test client."""
    if not HAS_FASTAPI:
        pytest.skip("FastAPI not installed")

    app = create_app(enable_tenant_middleware=False)
    return TestClient(app)


# =============================================================================
# Session CRUD Tests
# =============================================================================


class TestSessionCRUD:
    """Tests for session CRUD operations."""

    def test_create_session(self, client: "TestClient") -> None:
        """Create a new session."""
        response = client.post(
            "/v1/nphase/sessions",
            json={"title": "Feature Implementation"},
        )

        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert data["title"] == "Feature Implementation"
        assert data["current_phase"] == "UNDERSTAND"
        assert data["cycle_count"] == 0

    def test_create_session_with_metadata(self, client: "TestClient") -> None:
        """Create session with metadata."""
        response = client.post(
            "/v1/nphase/sessions",
            json={
                "title": "Test",
                "metadata": {"source": "api", "priority": "high"},
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert "id" in data

    def test_get_session(self, client: "TestClient") -> None:
        """Get session by ID."""
        # Create session
        create_response = client.post(
            "/v1/nphase/sessions",
            json={"title": "Test Session"},
        )
        session_id = create_response.json()["id"]

        # Get session
        response = client.get(f"/v1/nphase/sessions/{session_id}")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == session_id
        assert data["title"] == "Test Session"

    def test_get_session_not_found(self, client: "TestClient") -> None:
        """Get nonexistent session returns 404."""
        response = client.get("/v1/nphase/sessions/nonexistent-id")

        assert response.status_code == 404

    def test_list_sessions_empty(self, client: "TestClient") -> None:
        """List sessions when empty."""
        response = client.get("/v1/nphase/sessions")

        assert response.status_code == 200
        data = response.json()
        assert data["sessions"] == []
        assert data["total"] == 0

    def test_list_sessions_multiple(self, client: "TestClient") -> None:
        """List multiple sessions."""
        # Create sessions
        client.post("/v1/nphase/sessions", json={"title": "Session 1"})
        client.post("/v1/nphase/sessions", json={"title": "Session 2"})
        client.post("/v1/nphase/sessions", json={"title": "Session 3"})

        response = client.get("/v1/nphase/sessions")

        assert response.status_code == 200
        data = response.json()
        assert len(data["sessions"]) == 3
        assert data["total"] == 3

    def test_list_sessions_pagination(self, client: "TestClient") -> None:
        """List sessions with pagination."""
        # Create 5 sessions
        for i in range(5):
            client.post("/v1/nphase/sessions", json={"title": f"Session {i}"})

        # Get first 2
        response = client.get("/v1/nphase/sessions?limit=2&offset=0")
        data = response.json()
        assert len(data["sessions"]) == 2
        assert data["total"] == 5

        # Get next 2
        response = client.get("/v1/nphase/sessions?limit=2&offset=2")
        data = response.json()
        assert len(data["sessions"]) == 2

    def test_delete_session(self, client: "TestClient") -> None:
        """Delete a session."""
        # Create session
        create_response = client.post(
            "/v1/nphase/sessions",
            json={"title": "To Delete"},
        )
        session_id = create_response.json()["id"]

        # Delete
        response = client.delete(f"/v1/nphase/sessions/{session_id}")

        assert response.status_code == 200
        assert response.json()["deleted"] is True

        # Verify deleted
        get_response = client.get(f"/v1/nphase/sessions/{session_id}")
        assert get_response.status_code == 404

    def test_delete_session_not_found(self, client: "TestClient") -> None:
        """Delete nonexistent session returns 404."""
        response = client.delete("/v1/nphase/sessions/nonexistent-id")

        assert response.status_code == 404


# =============================================================================
# Phase Advancement Tests
# =============================================================================


class TestPhaseAdvancement:
    """Tests for phase advancement endpoint."""

    def test_advance_to_next(self, client: "TestClient") -> None:
        """Advance to next phase (default)."""
        # Create session
        create_response = client.post(
            "/v1/nphase/sessions",
            json={"title": "Test"},
        )
        session_id = create_response.json()["id"]

        # Advance (UNDERSTAND → ACT)
        response = client.post(
            f"/v1/nphase/sessions/{session_id}/advance",
            json={},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["from_phase"] == "UNDERSTAND"
        assert data["to_phase"] == "ACT"
        assert data["cycle_count"] == 0

    def test_advance_to_specific_phase(self, client: "TestClient") -> None:
        """Advance to specific phase."""
        # Create session
        create_response = client.post(
            "/v1/nphase/sessions",
            json={"title": "Test"},
        )
        session_id = create_response.json()["id"]

        # Advance to ACT
        response = client.post(
            f"/v1/nphase/sessions/{session_id}/advance",
            json={"target_phase": "ACT", "payload": "Research complete"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["to_phase"] == "ACT"

    def test_advance_invalid_transition(self, client: "TestClient") -> None:
        """Invalid transition returns 400."""
        # Create session
        create_response = client.post(
            "/v1/nphase/sessions",
            json={"title": "Test"},
        )
        session_id = create_response.json()["id"]

        # Try UNDERSTAND → REFLECT (invalid)
        response = client.post(
            f"/v1/nphase/sessions/{session_id}/advance",
            json={"target_phase": "REFLECT"},
        )

        assert response.status_code == 400

    def test_advance_invalid_phase_name(self, client: "TestClient") -> None:
        """Invalid phase name returns 400."""
        # Create session
        create_response = client.post(
            "/v1/nphase/sessions",
            json={"title": "Test"},
        )
        session_id = create_response.json()["id"]

        response = client.post(
            f"/v1/nphase/sessions/{session_id}/advance",
            json={"target_phase": "INVALID"},
        )

        assert response.status_code == 400

    def test_advance_with_auto_checkpoint(self, client: "TestClient") -> None:
        """Advance creates checkpoint by default."""
        # Create session
        create_response = client.post(
            "/v1/nphase/sessions",
            json={"title": "Test"},
        )
        session_id = create_response.json()["id"]

        # Advance
        response = client.post(
            f"/v1/nphase/sessions/{session_id}/advance",
            json={"auto_checkpoint": True},
        )

        assert response.status_code == 200
        data = response.json()
        assert "checkpoint_id" in data
        assert data["checkpoint_id"] is not None

    def test_complete_cycle(self, client: "TestClient") -> None:
        """Complete full cycle and verify cycle_count."""
        # Create session
        create_response = client.post(
            "/v1/nphase/sessions",
            json={"title": "Test"},
        )
        session_id = create_response.json()["id"]

        # UNDERSTAND → ACT
        client.post(
            f"/v1/nphase/sessions/{session_id}/advance",
            json={"target_phase": "ACT"},
        )

        # ACT → REFLECT
        client.post(
            f"/v1/nphase/sessions/{session_id}/advance",
            json={"target_phase": "REFLECT"},
        )

        # REFLECT → UNDERSTAND (cycle complete)
        response = client.post(
            f"/v1/nphase/sessions/{session_id}/advance",
            json={"target_phase": "UNDERSTAND"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["cycle_count"] == 1


# =============================================================================
# Checkpoint Tests
# =============================================================================


class TestCheckpoints:
    """Tests for checkpoint endpoints."""

    def test_create_checkpoint(self, client: "TestClient") -> None:
        """Create a checkpoint."""
        # Create session
        create_response = client.post(
            "/v1/nphase/sessions",
            json={"title": "Test"},
        )
        session_id = create_response.json()["id"]

        # Create checkpoint
        response = client.post(
            f"/v1/nphase/sessions/{session_id}/checkpoint",
            json={"metadata": {"reason": "before risky operation"}},
        )

        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert data["session_id"] == session_id
        assert data["phase"] == "UNDERSTAND"

    def test_list_checkpoints(self, client: "TestClient") -> None:
        """List checkpoints for session."""
        # Create session and checkpoints
        create_response = client.post(
            "/v1/nphase/sessions",
            json={"title": "Test"},
        )
        session_id = create_response.json()["id"]

        client.post(
            f"/v1/nphase/sessions/{session_id}/checkpoint",
            json={},
        )
        client.post(
            f"/v1/nphase/sessions/{session_id}/checkpoint",
            json={},
        )

        response = client.get(f"/v1/nphase/sessions/{session_id}/checkpoints")

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 2

    def test_restore_checkpoint(self, client: "TestClient") -> None:
        """Restore from checkpoint."""
        # Create session
        create_response = client.post(
            "/v1/nphase/sessions",
            json={"title": "Test"},
        )
        session_id = create_response.json()["id"]

        # Create checkpoint
        cp_response = client.post(
            f"/v1/nphase/sessions/{session_id}/checkpoint",
            json={},
        )
        checkpoint_id = cp_response.json()["id"]

        # Advance phase
        client.post(
            f"/v1/nphase/sessions/{session_id}/advance",
            json={"target_phase": "ACT", "auto_checkpoint": False},
        )

        # Verify current phase is ACT
        get_response = client.get(f"/v1/nphase/sessions/{session_id}")
        assert get_response.json()["current_phase"] == "ACT"

        # Restore
        restore_response = client.post(
            f"/v1/nphase/sessions/{session_id}/restore",
            json={"checkpoint_id": checkpoint_id},
        )

        assert restore_response.status_code == 200
        assert restore_response.json()["current_phase"] == "UNDERSTAND"

    def test_restore_invalid_checkpoint(self, client: "TestClient") -> None:
        """Restore with invalid checkpoint ID returns 404."""
        # Create session
        create_response = client.post(
            "/v1/nphase/sessions",
            json={"title": "Test"},
        )
        session_id = create_response.json()["id"]

        response = client.post(
            f"/v1/nphase/sessions/{session_id}/restore",
            json={"checkpoint_id": "nonexistent"},
        )

        assert response.status_code == 404


# =============================================================================
# Handle Tests
# =============================================================================


class TestHandles:
    """Tests for handle endpoints."""

    def test_add_handle(self, client: "TestClient") -> None:
        """Add a handle to session."""
        # Create session
        create_response = client.post(
            "/v1/nphase/sessions",
            json={"title": "Test"},
        )
        session_id = create_response.json()["id"]

        # Add handle
        response = client.post(
            f"/v1/nphase/sessions/{session_id}/handles",
            json={
                "path": "world.file.manifest",
                "content": {"file": "session.py", "lines": 100},
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["path"] == "world.file.manifest"
        assert data["phase"] == "UNDERSTAND"

    def test_list_handles(self, client: "TestClient") -> None:
        """List handles for session."""
        # Create session and handles
        create_response = client.post(
            "/v1/nphase/sessions",
            json={"title": "Test"},
        )
        session_id = create_response.json()["id"]

        client.post(
            f"/v1/nphase/sessions/{session_id}/handles",
            json={"path": "h1", "content": "c1"},
        )
        client.post(
            f"/v1/nphase/sessions/{session_id}/handles",
            json={"path": "h2", "content": "c2"},
        )

        response = client.get(f"/v1/nphase/sessions/{session_id}/handles")

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 2

    def test_list_handles_by_phase(self, client: "TestClient") -> None:
        """List handles filtered by phase."""
        # Create session
        create_response = client.post(
            "/v1/nphase/sessions",
            json={"title": "Test"},
        )
        session_id = create_response.json()["id"]

        # Add handle in UNDERSTAND
        client.post(
            f"/v1/nphase/sessions/{session_id}/handles",
            json={"path": "understand_handle", "content": "c1"},
        )

        # Advance to ACT
        client.post(
            f"/v1/nphase/sessions/{session_id}/advance",
            json={"target_phase": "ACT", "auto_checkpoint": False},
        )

        # Add handle in ACT
        client.post(
            f"/v1/nphase/sessions/{session_id}/handles",
            json={"path": "act_handle", "content": "c2"},
        )

        # Filter by UNDERSTAND
        response = client.get(f"/v1/nphase/sessions/{session_id}/handles?phase=UNDERSTAND")
        data = response.json()
        assert data["total"] == 1
        assert data["handles"][0]["path"] == "understand_handle"


# =============================================================================
# Phase Detection Tests
# =============================================================================


class TestPhaseDetection:
    """Tests for phase detection endpoint."""

    def test_detect_explicit_signifier(self, client: "TestClient") -> None:
        """Detect explicit ⟿[ACT] signifier."""
        # Create session
        create_response = client.post(
            "/v1/nphase/sessions",
            json={"title": "Test"},
        )
        session_id = create_response.json()["id"]

        response = client.post(
            f"/v1/nphase/sessions/{session_id}/detect",
            json={"output": "Research complete. ⟿[ACT]"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["action"] == "CONTINUE"
        assert data["target_phase"] == "ACT"
        assert data["confidence"] == 1.0
        assert data["auto_advanced"] is False

    def test_detect_with_auto_advance(self, client: "TestClient") -> None:
        """Auto-advance on high confidence signal."""
        # Create session
        create_response = client.post(
            "/v1/nphase/sessions",
            json={"title": "Test"},
        )
        session_id = create_response.json()["id"]

        response = client.post(
            f"/v1/nphase/sessions/{session_id}/detect",
            json={
                "output": "⟿[ACT]",
                "auto_advance": True,
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["auto_advanced"] is True
        assert data["current_phase"] == "ACT"

    def test_detect_no_signal(self, client: "TestClient") -> None:
        """No signal detected from plain text."""
        # Create session
        create_response = client.post(
            "/v1/nphase/sessions",
            json={"title": "Test"},
        )
        session_id = create_response.json()["id"]

        response = client.post(
            f"/v1/nphase/sessions/{session_id}/detect",
            json={"output": "Just some random text without signals."},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["action"] == "NONE"

    def test_detect_halt_signifier(self, client: "TestClient") -> None:
        """Detect ⟂[REASON] halt signifier."""
        # Create session
        create_response = client.post(
            "/v1/nphase/sessions",
            json={"title": "Test"},
        )
        session_id = create_response.json()["id"]

        response = client.post(
            f"/v1/nphase/sessions/{session_id}/detect",
            json={"output": "Need clarification. ⟂[awaiting input]"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["action"] == "HALT"
        assert data["reason"] == "awaiting input"


# =============================================================================
# Ledger Tests
# =============================================================================


class TestLedger:
    """Tests for ledger endpoint."""

    def test_get_ledger(self, client: "TestClient") -> None:
        """Get phase transition ledger."""
        # Create session and make transitions
        create_response = client.post(
            "/v1/nphase/sessions",
            json={"title": "Test"},
        )
        session_id = create_response.json()["id"]

        client.post(
            f"/v1/nphase/sessions/{session_id}/advance",
            json={"target_phase": "ACT", "auto_checkpoint": False},
        )
        client.post(
            f"/v1/nphase/sessions/{session_id}/advance",
            json={"target_phase": "REFLECT", "auto_checkpoint": False},
        )

        response = client.get(f"/v1/nphase/sessions/{session_id}/ledger")

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 2
        assert data["ledger"][0]["from_phase"] == "UNDERSTAND"
        assert data["ledger"][0]["to_phase"] == "ACT"


# =============================================================================
# Entropy Tests
# =============================================================================


class TestEntropy:
    """Tests for entropy tracking endpoint."""

    def test_spend_entropy(self, client: "TestClient") -> None:
        """Record entropy expenditure."""
        # Create session
        create_response = client.post(
            "/v1/nphase/sessions",
            json={"title": "Test"},
        )
        session_id = create_response.json()["id"]

        response = client.post(f"/v1/nphase/sessions/{session_id}/entropy?category=llm&amount=100")

        assert response.status_code == 200
        data = response.json()
        assert data["category"] == "llm"
        assert data["amount"] == 100
        assert data["total"]["llm"] == 100

    def test_spend_entropy_accumulates(self, client: "TestClient") -> None:
        """Entropy accumulates across calls."""
        # Create session
        create_response = client.post(
            "/v1/nphase/sessions",
            json={"title": "Test"},
        )
        session_id = create_response.json()["id"]

        client.post(f"/v1/nphase/sessions/{session_id}/entropy?category=llm&amount=100")
        response = client.post(f"/v1/nphase/sessions/{session_id}/entropy?category=llm&amount=50")

        data = response.json()
        assert data["total"]["llm"] == 150
