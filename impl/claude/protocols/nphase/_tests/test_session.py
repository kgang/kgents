"""
Tests for N-Phase Session Management.

Tests the session state management system including:
- Session lifecycle (create, get, list, delete)
- Phase advancement with validation
- Checkpoint/restore functionality
- Handle accumulation per phase
- Ledger recording for audit trail
- Serialization/deserialization

See: protocols/nphase/session.py
"""

from __future__ import annotations

from datetime import datetime

import pytest
from protocols.nphase.operad import NPhase
from protocols.nphase.session import (
    Handle,
    NPhaseSession,
    PhaseLedgerEntry,
    SessionCheckpoint,
    create_session,
    delete_session,
    get_session,
    list_sessions,
    reset_session_store,
)

# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture(autouse=True)
def clean_store() -> None:
    """Reset session store before each test."""
    reset_session_store()


@pytest.fixture
def session() -> NPhaseSession:
    """Create a fresh session for testing."""
    return create_session(title="Test Session")


# =============================================================================
# Session Creation Tests
# =============================================================================


class TestSessionCreation:
    """Tests for session creation."""

    def test_create_session_defaults(self) -> None:
        """Session created with default values."""
        session = create_session()

        assert session.id is not None
        assert len(session.id) == 36  # UUID format
        assert session.title == ""
        assert session.current_phase == NPhase.UNDERSTAND
        assert session.cycle_count == 0
        assert session.checkpoints == []
        assert session.handles == []
        assert session.ledger == []
        assert session.entropy_spent == {}

    def test_create_session_with_title(self) -> None:
        """Session created with specified title."""
        session = create_session(title="Feature Implementation")

        assert session.title == "Feature Implementation"

    def test_create_session_with_metadata(self) -> None:
        """Session created with metadata."""
        session = create_session(
            title="Test",
            metadata={"source": "api", "priority": "high"},
        )

        assert session.metadata == {"source": "api", "priority": "high"}

    def test_create_session_timestamps(self) -> None:
        """Session has creation and last_touched timestamps."""
        before = datetime.now()
        session = create_session()
        after = datetime.now()

        assert before <= session.created_at <= after
        assert before <= session.last_touched <= after

    def test_create_multiple_sessions(self) -> None:
        """Multiple sessions have unique IDs."""
        s1 = create_session(title="Session 1")
        s2 = create_session(title="Session 2")
        s3 = create_session(title="Session 3")

        assert s1.id != s2.id != s3.id
        assert len(list_sessions()) == 3


# =============================================================================
# Session Store Tests
# =============================================================================


class TestSessionStore:
    """Tests for session store operations."""

    def test_get_session_found(self) -> None:
        """Get session by ID returns session."""
        session = create_session(title="Test")
        retrieved = get_session(session.id)

        assert retrieved is not None
        assert retrieved.id == session.id
        assert retrieved.title == "Test"

    def test_get_session_not_found(self) -> None:
        """Get session with invalid ID returns None."""
        result = get_session("nonexistent-id")
        assert result is None

    def test_list_sessions_empty(self) -> None:
        """List sessions returns empty list when no sessions."""
        assert list_sessions() == []

    def test_list_sessions_multiple(self) -> None:
        """List sessions returns all sessions."""
        s1 = create_session(title="Session 1")
        s2 = create_session(title="Session 2")

        sessions = list_sessions()
        assert len(sessions) == 2
        assert s1 in sessions
        assert s2 in sessions

    def test_delete_session_success(self) -> None:
        """Delete session removes it from store."""
        session = create_session(title="Test")
        session_id = session.id

        result = delete_session(session_id)
        assert result is True
        assert get_session(session_id) is None

    def test_delete_session_not_found(self) -> None:
        """Delete nonexistent session returns False."""
        result = delete_session("nonexistent-id")
        assert result is False


# =============================================================================
# Phase Advancement Tests
# =============================================================================


class TestPhaseAdvancement:
    """Tests for phase transition logic."""

    def test_advance_phase_understand_to_act(self, session: NPhaseSession) -> None:
        """Valid transition: UNDERSTAND → ACT."""
        assert session.current_phase == NPhase.UNDERSTAND

        entry = session.advance_phase(NPhase.ACT, payload="Research complete")

        assert session.current_phase == NPhase.ACT  # type: ignore[comparison-overlap]
        assert entry.from_phase == NPhase.UNDERSTAND
        assert entry.to_phase == NPhase.ACT
        assert entry.payload == "Research complete"
        assert entry.cycle_count == 0

    def test_advance_phase_act_to_reflect(self, session: NPhaseSession) -> None:
        """Valid transition: ACT → REFLECT."""
        session.advance_phase(NPhase.ACT)
        entry = session.advance_phase(NPhase.REFLECT)

        assert session.current_phase == NPhase.REFLECT
        assert entry.from_phase == NPhase.ACT
        assert entry.to_phase == NPhase.REFLECT

    def test_advance_phase_reflect_to_understand_increments_cycle(
        self, session: NPhaseSession
    ) -> None:
        """Cycle completion: REFLECT → UNDERSTAND increments cycle_count."""
        session.advance_phase(NPhase.ACT)
        session.advance_phase(NPhase.REFLECT)

        assert session.cycle_count == 0

        session.advance_phase(NPhase.UNDERSTAND)

        assert session.cycle_count == 1
        assert session.current_phase == NPhase.UNDERSTAND

    def test_advance_phase_invalid_understand_to_reflect(
        self, session: NPhaseSession
    ) -> None:
        """Invalid transition: UNDERSTAND → REFLECT raises error."""
        with pytest.raises(ValueError, match="Invalid transition"):
            session.advance_phase(NPhase.REFLECT)

    def test_advance_phase_invalid_act_to_understand(
        self, session: NPhaseSession
    ) -> None:
        """Invalid transition: ACT → UNDERSTAND raises error."""
        session.advance_phase(NPhase.ACT)

        with pytest.raises(ValueError, match="Invalid transition"):
            session.advance_phase(NPhase.UNDERSTAND)

    def test_advance_phase_to_next_default(self, session: NPhaseSession) -> None:
        """Advance to next phase when target is None."""
        entry = session.advance_phase()  # None defaults to next

        assert session.current_phase == NPhase.ACT
        assert entry.to_phase == NPhase.ACT

    def test_advance_phase_same_phase_allowed(self, session: NPhaseSession) -> None:
        """Staying in same phase is allowed (no-op transition)."""
        entry = session.advance_phase(NPhase.UNDERSTAND)

        assert session.current_phase == NPhase.UNDERSTAND
        assert entry.from_phase == NPhase.UNDERSTAND
        assert entry.to_phase == NPhase.UNDERSTAND

    def test_advance_phase_records_to_ledger(self, session: NPhaseSession) -> None:
        """Phase advancement records entry in ledger."""
        assert len(session.ledger) == 0

        session.advance_phase(NPhase.ACT)
        session.advance_phase(NPhase.REFLECT)

        assert len(session.ledger) == 2
        assert session.ledger[0].to_phase == NPhase.ACT
        assert session.ledger[1].to_phase == NPhase.REFLECT

    def test_advance_phase_updates_last_touched(self, session: NPhaseSession) -> None:
        """Phase advancement updates last_touched timestamp."""
        original = session.last_touched
        session.advance_phase(NPhase.ACT)

        assert session.last_touched >= original

    def test_can_advance_to_valid(self, session: NPhaseSession) -> None:
        """can_advance_to returns True for valid transitions."""
        assert session.can_advance_to(NPhase.ACT) is True
        assert session.can_advance_to(NPhase.UNDERSTAND) is True  # Same phase

    def test_can_advance_to_invalid(self, session: NPhaseSession) -> None:
        """can_advance_to returns False for invalid transitions."""
        assert session.can_advance_to(NPhase.REFLECT) is False


# =============================================================================
# Checkpoint/Restore Tests
# =============================================================================


class TestCheckpointRestore:
    """Tests for checkpoint and restore functionality."""

    def test_checkpoint_basic(self, session: NPhaseSession) -> None:
        """Create a checkpoint at current state."""
        session.add_handle("world.file", {"content": "test"})

        cp = session.checkpoint({"reason": "before implementation"})

        assert cp.id is not None
        assert cp.session_id == session.id
        assert cp.phase == NPhase.UNDERSTAND
        assert cp.cycle_count == 0
        assert len(cp.handles) == 1
        assert cp.metadata == {"reason": "before implementation"}

    def test_checkpoint_stored_in_session(self, session: NPhaseSession) -> None:
        """Checkpoints are stored in session."""
        cp1 = session.checkpoint()
        cp2 = session.checkpoint()

        assert len(session.checkpoints) == 2
        assert session.checkpoints[0].id == cp1.id
        assert session.checkpoints[1].id == cp2.id

    def test_restore_from_checkpoint(self, session: NPhaseSession) -> None:
        """Restore session state from checkpoint."""
        # Add some state
        session.add_handle("world.file1", {"content": "original"})
        cp = session.checkpoint()

        # Modify state
        session.advance_phase(NPhase.ACT, auto_checkpoint=False)
        session.add_handle("world.file2", {"content": "new"})
        assert len(session.handles) == 2
        assert session.current_phase == NPhase.ACT

        # Restore
        session.restore(cp.id)

        assert session.current_phase == NPhase.UNDERSTAND  # type: ignore[comparison-overlap]
        assert len(session.handles) == 1
        assert session.handles[0].path == "world.file1"

    def test_restore_invalid_checkpoint(self, session: NPhaseSession) -> None:
        """Restore with invalid checkpoint ID raises error."""
        with pytest.raises(ValueError, match="Checkpoint not found"):
            session.restore("nonexistent-checkpoint")

    def test_restore_records_to_ledger(self, session: NPhaseSession) -> None:
        """Restore operation records entry in ledger."""
        cp = session.checkpoint()
        session.advance_phase(NPhase.ACT, auto_checkpoint=False)
        ledger_before = len(session.ledger)

        session.restore(cp.id)

        assert len(session.ledger) == ledger_before + 1
        assert session.ledger[-1].payload == {"restored_from": cp.id}

    def test_get_latest_checkpoint(self, session: NPhaseSession) -> None:
        """Get the most recent checkpoint."""
        assert session.get_latest_checkpoint() is None

        session.checkpoint()
        cp2 = session.checkpoint()

        assert session.get_latest_checkpoint() == cp2

    def test_get_checkpoint_for_phase(self, session: NPhaseSession) -> None:
        """Get latest checkpoint for a specific phase."""
        cp_understand = session.checkpoint()
        session.advance_phase(NPhase.ACT, auto_checkpoint=False)
        cp_act = session.checkpoint()

        assert session.get_checkpoint_for_phase(NPhase.UNDERSTAND) == cp_understand
        assert session.get_checkpoint_for_phase(NPhase.ACT) == cp_act
        assert session.get_checkpoint_for_phase(NPhase.REFLECT) is None

    def test_auto_checkpoint_on_advance(self, session: NPhaseSession) -> None:
        """Phase advancement auto-creates checkpoint by default."""
        assert len(session.checkpoints) == 0

        session.advance_phase(NPhase.ACT, auto_checkpoint=True)

        assert len(session.checkpoints) == 1
        assert session.checkpoints[0].phase == NPhase.UNDERSTAND

    def test_no_auto_checkpoint_when_disabled(self, session: NPhaseSession) -> None:
        """Phase advancement skips checkpoint when auto_checkpoint=False."""
        session.advance_phase(NPhase.ACT, auto_checkpoint=False)

        assert len(session.checkpoints) == 0


# =============================================================================
# Handle Tracking Tests
# =============================================================================


class TestHandleTracking:
    """Tests for handle accumulation."""

    def test_add_handle(self, session: NPhaseSession) -> None:
        """Add a handle in current phase."""
        handle = session.add_handle("world.file.manifest", {"path": "foo.py"})

        assert handle.path == "world.file.manifest"
        assert handle.phase == NPhase.UNDERSTAND
        assert handle.content == {"path": "foo.py"}
        assert handle in session.handles

    def test_add_handle_records_phase(self, session: NPhaseSession) -> None:
        """Handles record the phase when they were acquired."""
        session.add_handle("understand_handle", "understand_content")
        session.advance_phase(NPhase.ACT, auto_checkpoint=False)
        session.add_handle("act_handle", "act_content")

        assert session.handles[0].phase == NPhase.UNDERSTAND
        assert session.handles[1].phase == NPhase.ACT

    def test_get_handles_for_phase(self, session: NPhaseSession) -> None:
        """Get handles filtered by phase."""
        session.add_handle("h1", "content1")
        session.add_handle("h2", "content2")
        session.advance_phase(NPhase.ACT, auto_checkpoint=False)
        session.add_handle("h3", "content3")

        understand_handles = session.get_handles_for_phase(NPhase.UNDERSTAND)
        act_handles = session.get_handles_for_phase(NPhase.ACT)
        reflect_handles = session.get_handles_for_phase(NPhase.REFLECT)

        assert len(understand_handles) == 2
        assert len(act_handles) == 1
        assert len(reflect_handles) == 0

    def test_handle_timestamp(self, session: NPhaseSession) -> None:
        """Handles have creation timestamp."""
        before = datetime.now()
        handle = session.add_handle("path", "content")
        after = datetime.now()

        assert before <= handle.created_at <= after


# =============================================================================
# Ledger Tests
# =============================================================================


class TestLedger:
    """Tests for phase transition ledger."""

    def test_ledger_records_transitions(self, session: NPhaseSession) -> None:
        """Ledger records all phase transitions."""
        session.advance_phase(NPhase.ACT, payload="step1", auto_checkpoint=False)
        session.advance_phase(NPhase.REFLECT, payload="step2", auto_checkpoint=False)
        session.advance_phase(NPhase.UNDERSTAND, payload="step3", auto_checkpoint=False)

        assert len(session.ledger) == 3

        assert session.ledger[0].from_phase == NPhase.UNDERSTAND
        assert session.ledger[0].to_phase == NPhase.ACT
        assert session.ledger[0].payload == "step1"

        assert session.ledger[1].from_phase == NPhase.ACT
        assert session.ledger[1].to_phase == NPhase.REFLECT

        assert session.ledger[2].from_phase == NPhase.REFLECT
        assert session.ledger[2].to_phase == NPhase.UNDERSTAND

    def test_ledger_records_cycle_count(self, session: NPhaseSession) -> None:
        """Ledger entries include cycle count."""
        session.advance_phase(NPhase.ACT, auto_checkpoint=False)
        session.advance_phase(NPhase.REFLECT, auto_checkpoint=False)
        session.advance_phase(
            NPhase.UNDERSTAND, auto_checkpoint=False
        )  # Cycle 1 starts
        session.advance_phase(NPhase.ACT, auto_checkpoint=False)

        assert session.ledger[0].cycle_count == 0
        assert session.ledger[1].cycle_count == 0
        assert session.ledger[2].cycle_count == 1  # After cycle completion
        assert session.ledger[3].cycle_count == 1


# =============================================================================
# Entropy Tracking Tests
# =============================================================================


class TestEntropyTracking:
    """Tests for entropy expenditure tracking."""

    def test_spend_entropy(self, session: NPhaseSession) -> None:
        """Record entropy expenditure."""
        session.spend_entropy("llm", 100)
        session.spend_entropy("search", 50)

        assert session.entropy_spent == {"llm": 100, "search": 50}

    def test_spend_entropy_accumulates(self, session: NPhaseSession) -> None:
        """Multiple expenditures accumulate."""
        session.spend_entropy("llm", 100)
        session.spend_entropy("llm", 50)

        assert session.entropy_spent["llm"] == 150

    def test_spend_entropy_updates_timestamp(self, session: NPhaseSession) -> None:
        """Entropy spending updates last_touched."""
        original = session.last_touched
        session.spend_entropy("llm", 100)

        assert session.last_touched >= original


# =============================================================================
# Serialization Tests
# =============================================================================


class TestSerialization:
    """Tests for session serialization/deserialization."""

    def test_session_to_dict(self, session: NPhaseSession) -> None:
        """Session serializes to dictionary."""
        session.add_handle("test.path", {"data": "value"})
        session.advance_phase(NPhase.ACT, auto_checkpoint=False)
        session.spend_entropy("llm", 100)

        data = session.to_dict()

        assert data["id"] == session.id
        assert data["title"] == "Test Session"
        assert data["current_phase"] == "ACT"
        assert data["cycle_count"] == 0
        assert len(data["handles"]) == 1
        assert data["entropy_spent"] == {"llm": 100}

    def test_session_from_dict(self) -> None:
        """Session deserializes from dictionary."""
        data = {
            "id": "test-id-123",
            "title": "Restored Session",
            "current_phase": "ACT",
            "cycle_count": 2,
            "checkpoints": [],
            "handles": [
                {
                    "path": "test.path",
                    "phase": "UNDERSTAND",
                    "content": {"data": "value"},
                    "created_at": datetime.now().isoformat(),
                }
            ],
            "ledger": [],
            "entropy_spent": {"llm": 200},
            "created_at": datetime.now().isoformat(),
            "last_touched": datetime.now().isoformat(),
            "metadata": {"source": "test"},
        }

        session = NPhaseSession.from_dict(data)

        assert session.id == "test-id-123"
        assert session.title == "Restored Session"
        assert session.current_phase == NPhase.ACT
        assert session.cycle_count == 2
        assert len(session.handles) == 1
        assert session.entropy_spent == {"llm": 200}
        assert session.metadata == {"source": "test"}

    def test_roundtrip_serialization(self, session: NPhaseSession) -> None:
        """Session survives roundtrip serialization."""
        session.add_handle("path1", "content1")
        session.advance_phase(NPhase.ACT, auto_checkpoint=False)
        session.add_handle("path2", "content2")
        session.checkpoint({"reason": "test"})
        session.spend_entropy("llm", 150)

        # Roundtrip
        data = session.to_dict()
        restored = NPhaseSession.from_dict(data)

        assert restored.id == session.id
        assert restored.title == session.title
        assert restored.current_phase == session.current_phase
        assert restored.cycle_count == session.cycle_count
        assert len(restored.handles) == len(session.handles)
        assert len(restored.checkpoints) == len(session.checkpoints)
        assert restored.entropy_spent == session.entropy_spent

    def test_handle_serialization(self) -> None:
        """Handle serializes and deserializes correctly."""
        handle = Handle(
            path="world.file",
            phase=NPhase.ACT,
            content={"key": "value"},
        )

        data = handle.to_dict()
        restored = Handle.from_dict(data)

        assert restored.path == handle.path
        assert restored.phase == handle.phase
        assert restored.content == handle.content

    def test_checkpoint_serialization(self) -> None:
        """Checkpoint serializes and deserializes correctly."""
        cp = SessionCheckpoint(
            id="cp-123",
            session_id="session-456",
            phase=NPhase.REFLECT,
            cycle_count=3,
            handles=[Handle("path", NPhase.ACT, "content")],
            entropy_spent={"llm": 100},
            created_at=datetime.now(),
            metadata={"note": "test"},
        )

        data = cp.to_dict()
        restored = SessionCheckpoint.from_dict(data)

        assert restored.id == cp.id
        assert restored.session_id == cp.session_id
        assert restored.phase == cp.phase
        assert restored.cycle_count == cp.cycle_count
        assert len(restored.handles) == 1
        assert restored.metadata == {"note": "test"}

    def test_ledger_entry_serialization(self) -> None:
        """Ledger entry serializes and deserializes correctly."""
        entry = PhaseLedgerEntry(
            from_phase=NPhase.UNDERSTAND,
            to_phase=NPhase.ACT,
            timestamp=datetime.now(),
            payload={"trigger": "user"},
            cycle_count=1,
        )

        data = entry.to_dict()
        restored = PhaseLedgerEntry.from_dict(data)

        assert restored.from_phase == entry.from_phase
        assert restored.to_phase == entry.to_phase
        assert restored.payload == entry.payload
        assert restored.cycle_count == entry.cycle_count


# =============================================================================
# Session Summary Tests
# =============================================================================


class TestSessionSummary:
    """Tests for session summary (API response format)."""

    def test_summary_basic(self, session: NPhaseSession) -> None:
        """Summary returns expected fields."""
        summary = session.summary()

        assert summary["id"] == session.id
        assert summary["title"] == "Test Session"
        assert summary["current_phase"] == "UNDERSTAND"
        assert summary["cycle_count"] == 0
        assert summary["checkpoint_count"] == 0
        assert summary["handle_count"] == 0
        assert summary["ledger_count"] == 0

    def test_summary_with_state(self, session: NPhaseSession) -> None:
        """Summary reflects session state."""
        session.add_handle("h1", "c1")
        session.add_handle("h2", "c2")
        session.checkpoint()
        session.advance_phase(NPhase.ACT, auto_checkpoint=False)
        session.spend_entropy("llm", 100)

        summary = session.summary()

        assert summary["current_phase"] == "ACT"
        assert summary["checkpoint_count"] == 1
        assert summary["handle_count"] == 2
        assert summary["ledger_count"] == 1
        assert summary["entropy_spent"] == {"llm": 100}


# =============================================================================
# Full Cycle Integration Test
# =============================================================================


class TestFullCycleIntegration:
    """Integration tests for complete session workflows."""

    def test_complete_development_cycle(self) -> None:
        """Simulate a complete development cycle with all operations."""
        # Create session
        session = create_session(title="Feature Implementation")

        # UNDERSTAND phase
        session.add_handle("world.file.structure", {"files": ["a.py", "b.py"]})
        session.add_handle("concept.requirements", {"feature": "auth"})
        session.spend_entropy("llm", 50)
        session.checkpoint({"phase_note": "Research complete"})

        # Advance to ACT
        session.advance_phase(NPhase.ACT, payload="Design approved")
        session.add_handle("world.file.created", {"file": "auth.py"})
        session.add_handle("world.tests.written", {"count": 5})
        session.spend_entropy("llm", 100)

        # Advance to REFLECT
        session.advance_phase(NPhase.REFLECT, payload="Implementation done")
        session.add_handle("self.learnings", {"insight": "Use dependency injection"})
        session.spend_entropy("llm", 30)

        # Complete cycle
        session.advance_phase(NPhase.UNDERSTAND, payload="Ready for next iteration")

        # Verify state
        assert session.cycle_count == 1
        assert session.current_phase == NPhase.UNDERSTAND
        assert len(session.handles) == 5
        assert len(session.checkpoints) >= 1
        # 3 phase transitions: UNDERSTAND→ACT, ACT→REFLECT, REFLECT→UNDERSTAND
        assert len(session.ledger) == 3
        assert session.entropy_spent["llm"] == 180

        # Verify handles per phase
        understand_handles = session.get_handles_for_phase(NPhase.UNDERSTAND)
        act_handles = session.get_handles_for_phase(NPhase.ACT)
        reflect_handles = session.get_handles_for_phase(NPhase.REFLECT)

        assert len(understand_handles) == 2
        assert len(act_handles) == 2
        assert len(reflect_handles) == 1

    def test_checkpoint_recovery_workflow(self) -> None:
        """Test checkpoint-based recovery after failed work."""
        session = create_session(title="Risky Implementation")

        # Initial work
        session.add_handle("initial.work", "content")
        checkpoint_before_risk = session.checkpoint({"note": "safe state"})

        # Risky work that we might want to rollback
        session.advance_phase(NPhase.ACT, auto_checkpoint=False)
        session.add_handle("risky.change", "dangerous")

        # Decide to rollback
        session.restore(checkpoint_before_risk.id)

        # Verify rollback
        assert session.current_phase == NPhase.UNDERSTAND
        assert len(session.handles) == 1
        assert session.handles[0].path == "initial.work"
