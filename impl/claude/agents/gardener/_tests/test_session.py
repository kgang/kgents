"""
Tests for GardenerSession polynomial agent.

Covers:
- Session lifecycle (create, advance, complete)
- Phase transitions (SENSE → ACT → REFLECT)
- State management and persistence
- Resume across sessions
- Projections (ASCII, dict)

Per spike 7B requirements: 20+ tests.
"""

from __future__ import annotations

import tempfile
from datetime import datetime
from pathlib import Path

import pytest

from agents.gardener.persistence import (
    SessionHistoryEvent,
    SessionStore,
    StoredSession,
    create_session_store,
)
from agents.gardener.session import (
    GARDENER_SESSION_POLYNOMIAL,
    GardenerSession,
    SessionArtifact,
    SessionConfig,
    SessionIntent,
    SessionPhase,
    SessionState,
    create_gardener_session,
    project_session_to_ascii,
    project_session_to_dict,
)

# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def session() -> GardenerSession:
    """Create a fresh GardenerSession for testing."""
    return create_gardener_session(
        name="Test Session",
        plan_path="plans/test-plan.md",
    )


@pytest.fixture
def session_with_intent(session: GardenerSession) -> GardenerSession:
    """Session with intent already set."""
    session._state.intent = SessionIntent(
        description="Implement test feature",
        plan_path="plans/test-plan.md",
    )
    return session


@pytest.fixture
async def store() -> SessionStore:
    """Create a temporary SessionStore for testing."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        store = SessionStore(db_path=Path(f.name))
        await store.init()
        yield store


# =============================================================================
# Test: Session Creation
# =============================================================================


class TestSessionCreation:
    """Tests for session creation."""

    def test_create_session_has_unique_id(self) -> None:
        """Each session gets a unique ID."""
        s1 = create_gardener_session(name="Session 1")
        s2 = create_gardener_session(name="Session 2")
        assert s1.session_id != s2.session_id

    def test_create_session_starts_in_sense_phase(self) -> None:
        """New sessions start in SENSE phase."""
        session = create_gardener_session(name="Test")
        assert session.phase == SessionPhase.SENSE

    def test_create_session_with_plan_path(self) -> None:
        """Sessions can be linked to plan files."""
        session = create_gardener_session(
            name="Feature Session",
            plan_path="plans/core-apps/coalition-forge.md",
        )
        assert session.plan_path == "plans/core-apps/coalition-forge.md"

    def test_create_session_with_config(self) -> None:
        """Custom config is applied."""
        config = SessionConfig(sense_timeout=120.0)
        session = create_gardener_session(name="Test", config=config)
        assert session.config.sense_timeout == 120.0

    def test_session_has_initial_state(self) -> None:
        """Session has properly initialized state."""
        session = create_gardener_session(name="Test")
        assert session.state.session_id == session.session_id
        assert session.state.name == "Test"
        assert session.state.sense_count == 0
        assert session.state.artifacts == []
        assert session.state.learnings == []


# =============================================================================
# Test: Phase Transitions
# =============================================================================


class TestPhaseTransitions:
    """Tests for phase transitions."""

    @pytest.mark.asyncio
    async def test_sense_to_act(self, session: GardenerSession) -> None:
        """Can advance from SENSE to ACT."""
        assert session.phase == SessionPhase.SENSE
        result = await session.advance()
        assert session.phase == SessionPhase.ACT
        assert result["status"] == "advanced"
        assert result["to_phase"] == "ACT"

    @pytest.mark.asyncio
    async def test_act_to_reflect(self, session: GardenerSession) -> None:
        """Can advance from ACT to REFLECT."""
        await session.advance()  # SENSE → ACT
        assert session.phase == SessionPhase.ACT

        result = await session.advance()  # ACT → REFLECT
        assert session.phase == SessionPhase.REFLECT
        assert result["to_phase"] == "REFLECT"

    @pytest.mark.asyncio
    async def test_reflect_to_sense_cycles(self, session: GardenerSession) -> None:
        """REFLECT → SENSE creates a new cycle."""
        await session.advance()  # SENSE → ACT
        await session.advance()  # ACT → REFLECT
        assert session.phase == SessionPhase.REFLECT

        result = await session.advance()  # REFLECT → SENSE
        assert session.phase == SessionPhase.SENSE
        assert result.get("cycle_complete") is True

    @pytest.mark.asyncio
    async def test_full_cycle_increments_counters(self, session: GardenerSession) -> None:
        """Full cycle increments phase counters."""
        assert session.state.sense_count == 0

        # Complete one full cycle
        await session.advance()  # SENSE → ACT
        await session.advance()  # ACT → REFLECT
        await session.advance()  # REFLECT → SENSE

        assert session.state.sense_count == 1
        assert session.state.act_count == 1
        assert session.state.reflect_count == 1

    @pytest.mark.asyncio
    async def test_rollback_from_act_to_sense(self, session: GardenerSession) -> None:
        """Can rollback from ACT to SENSE."""
        await session.advance()  # SENSE → ACT
        assert session.phase == SessionPhase.ACT

        result = await session.rollback()
        assert session.phase == SessionPhase.SENSE
        assert result["status"] == "rolled_back"

    @pytest.mark.asyncio
    async def test_rollback_only_from_act(self, session: GardenerSession) -> None:
        """Rollback only works from ACT phase."""
        # In SENSE phase
        result = await session.rollback()
        assert result["status"] == "error"

        # Move to REFLECT
        await session.advance()  # SENSE → ACT
        await session.advance()  # ACT → REFLECT

        result = await session.rollback()
        assert result["status"] == "error"


# =============================================================================
# Test: SENSE Phase Operations
# =============================================================================


class TestSensePhase:
    """Tests for SENSE phase operations."""

    @pytest.mark.asyncio
    async def test_gather_context(self, session: GardenerSession) -> None:
        """Can gather context in SENSE phase."""
        result = await session.sense()
        assert result["status"] == "gathered"

    @pytest.mark.asyncio
    async def test_gather_specific_context_type(self, session: GardenerSession) -> None:
        """Can gather specific context types."""
        result = await session.sense(context_type="forest")
        assert result["status"] == "gathered"
        assert result["context"]["type"] == "forest"

    @pytest.mark.asyncio
    async def test_set_intent(self, session: GardenerSession) -> None:
        """Can set intent in SENSE phase."""
        intent = SessionIntent(
            description="Implement feature X",
            plan_path="plans/feature-x.md",
        )
        result = await session.set_intent(intent)
        assert result["status"] == "intent_set"
        assert session.intent is not None
        assert session.intent.description == "Implement feature X"

    @pytest.mark.asyncio
    async def test_set_intent_from_dict(self, session: GardenerSession) -> None:
        """Can set intent from dict."""
        result = await session.set_intent(
            {
                "description": "Build API",
                "priority": "high",
            }
        )
        assert result["status"] == "intent_set"
        assert session.intent.priority == "high"

    @pytest.mark.asyncio
    async def test_sense_not_available_in_other_phases(self, session: GardenerSession) -> None:
        """sense() only works in SENSE phase."""
        await session.advance()  # SENSE → ACT
        result = await session.sense()
        assert result["status"] == "error"


# =============================================================================
# Test: ACT Phase Operations
# =============================================================================


class TestActPhase:
    """Tests for ACT phase operations."""

    @pytest.mark.asyncio
    async def test_record_artifact(self, session: GardenerSession) -> None:
        """Can record artifacts in ACT phase."""
        await session.advance()  # SENSE → ACT

        artifact = SessionArtifact(
            artifact_type="code",
            path="agents/gardener/session.py",
            description="Implemented session module",
        )
        result = await session.record_artifact(artifact)
        assert result["status"] == "artifact_recorded"
        assert len(session.artifacts) == 1

    @pytest.mark.asyncio
    async def test_record_multiple_artifacts(self, session: GardenerSession) -> None:
        """Can record multiple artifacts."""
        await session.advance()

        for i in range(3):
            await session.record_artifact(
                SessionArtifact(
                    artifact_type="code",
                    path=f"file{i}.py",
                )
            )

        assert len(session.artifacts) == 3

    @pytest.mark.asyncio
    async def test_record_artifact_from_dict(self, session: GardenerSession) -> None:
        """Can record artifact from dict."""
        await session.advance()

        result = await session.record_artifact(
            {
                "artifact_type": "doc",
                "path": "README.md",
                "description": "Updated docs",
            }
        )
        assert result["status"] == "artifact_recorded"

    @pytest.mark.asyncio
    async def test_artifact_not_available_in_other_phases(self, session: GardenerSession) -> None:
        """record_artifact() only works in ACT phase."""
        # In SENSE phase
        result = await session.record_artifact(SessionArtifact(artifact_type="code"))
        assert result["status"] == "error"


# =============================================================================
# Test: REFLECT Phase Operations
# =============================================================================


class TestReflectPhase:
    """Tests for REFLECT phase operations."""

    @pytest.mark.asyncio
    async def test_record_learning(self, session: GardenerSession) -> None:
        """Can record learnings in REFLECT phase."""
        await session.advance()  # SENSE → ACT
        await session.advance()  # ACT → REFLECT

        result = await session.learn("Pattern X works well for Y")
        assert result["status"] == "learned"
        assert len(session.learnings) == 1

    @pytest.mark.asyncio
    async def test_record_multiple_learnings(self, session: GardenerSession) -> None:
        """Can record multiple learnings."""
        await session.advance()
        await session.advance()

        await session.learn("Learning 1")
        await session.learn("Learning 2")
        result = await session.learn(["Learning 3", "Learning 4"])

        assert len(session.learnings) == 4

    @pytest.mark.asyncio
    async def test_consolidate(self, session: GardenerSession) -> None:
        """Can consolidate learnings."""
        await session.advance()
        await session.advance()

        await session.learn("Test learning")
        result = await session.consolidate()

        assert result["status"] == "consolidated"
        assert "learnings" in result

    @pytest.mark.asyncio
    async def test_complete_session(self, session: GardenerSession) -> None:
        """Can complete session from REFLECT phase."""
        await session.advance()
        await session.advance()

        await session.learn("Final learning")
        result = await session.complete()

        assert result["status"] == "completed"
        assert "learnings" in result
        assert "artifacts" in result

    @pytest.mark.asyncio
    async def test_complete_only_from_reflect(self, session: GardenerSession) -> None:
        """complete() only works from REFLECT phase."""
        result = await session.complete()
        assert result["status"] == "error"

        await session.advance()  # ACT
        result = await session.complete()
        assert result["status"] == "error"

    @pytest.mark.asyncio
    async def test_learn_not_available_in_other_phases(self, session: GardenerSession) -> None:
        """learn() only works in REFLECT phase."""
        result = await session.learn("Test")
        assert result["status"] == "error"


# =============================================================================
# Test: State Management
# =============================================================================


class TestStateManagement:
    """Tests for state management."""

    def test_state_to_dict_and_back(self) -> None:
        """State can be serialized and deserialized."""
        state = SessionState(
            session_id="test-123",
            name="Test Session",
            plan_path="plans/test.md",
            intent=SessionIntent(description="Test intent"),
            artifacts=[SessionArtifact(artifact_type="code", path="test.py")],
            learnings=["Learning 1"],
        )

        state_dict = state.to_dict()
        restored = SessionState.from_dict(state_dict)

        assert restored.session_id == state.session_id
        assert restored.name == state.name
        assert restored.intent.description == "Test intent"
        assert len(restored.artifacts) == 1
        assert len(restored.learnings) == 1

    def test_intent_serialization(self) -> None:
        """Intent can be serialized and deserialized."""
        intent = SessionIntent(
            description="Test",
            plan_path="plans/test.md",
            target_files=["a.py", "b.py"],
            constraints=["No breaking changes"],
            priority="high",
            metadata={"key": "value"},
        )

        intent_dict = intent.to_dict()
        restored = SessionIntent.from_dict(intent_dict)

        assert restored.description == intent.description
        assert restored.target_files == intent.target_files
        assert restored.priority == "high"

    def test_artifact_serialization(self) -> None:
        """Artifact can be serialized and deserialized."""
        artifact = SessionArtifact(
            artifact_type="code",
            path="test.py",
            content="print('hello')",
            description="Test file",
            success=True,
            metadata={"lines": 1},
        )

        artifact_dict = artifact.to_dict()
        restored = SessionArtifact.from_dict(artifact_dict)

        assert restored.artifact_type == artifact.artifact_type
        assert restored.path == artifact.path
        assert restored.content == artifact.content

    @pytest.mark.asyncio
    async def test_manifest_returns_current_state(self, session: GardenerSession) -> None:
        """manifest() returns current state."""
        result = await session.manifest()
        assert result["status"] == "manifest"
        assert "state" in result


# =============================================================================
# Test: Persistence (SessionStore)
# =============================================================================


class TestPersistence:
    """Tests for SQLite persistence."""

    @pytest.mark.asyncio
    async def test_create_and_fetch_session(self, store: SessionStore) -> None:
        """Can create and fetch a session."""
        session = await store.create(
            session_id="test-123",
            name="Test Session",
            plan_path="plans/test.md",
        )

        fetched = await store.get("test-123")
        assert fetched is not None
        assert fetched.name == "Test Session"
        assert fetched.plan_path == "plans/test.md"

    @pytest.mark.asyncio
    async def test_get_active_session(self, store: SessionStore) -> None:
        """Can get the currently active session."""
        await store.create(session_id="s1", name="Session 1")
        await store.create(session_id="s2", name="Session 2")

        active = await store.get_active()
        assert active is not None
        assert active.id == "s2"  # Most recently created

    @pytest.mark.asyncio
    async def test_list_recent_sessions(self, store: SessionStore) -> None:
        """Can list recent sessions."""
        for i in range(5):
            await store.create(session_id=f"s{i}", name=f"Session {i}")

        sessions = await store.list_recent(limit=3)
        assert len(sessions) == 3

    @pytest.mark.asyncio
    async def test_update_session_phase(self, store: SessionStore) -> None:
        """Can update session phase."""
        await store.create(session_id="test", name="Test")

        updated = await store.update("test", phase="ACT")
        assert updated is True

        session = await store.get("test")
        assert session.phase == "ACT"

    @pytest.mark.asyncio
    async def test_advance_phase_records_history(self, store: SessionStore) -> None:
        """Phase advancement records history."""
        await store.create(session_id="test", name="Test")

        await store.advance_phase("test", "SENSE", "ACT")

        history = await store.get_history("test")
        assert len(history) >= 2  # created + advanced
        assert any(e.event_type == "advanced" for e in history)

    @pytest.mark.asyncio
    async def test_mark_resumed(self, store: SessionStore) -> None:
        """Can mark session as resumed."""
        await store.create(session_id="test", name="Test")

        result = await store.mark_resumed("test")
        assert result is True

        session = await store.get("test")
        assert session.resumed_at is not None

    @pytest.mark.asyncio
    async def test_complete_session(self, store: SessionStore) -> None:
        """Can complete a session."""
        await store.create(session_id="test", name="Test")

        result = await store.complete("test", final_artifact={"summary": "Done"})
        assert result is True

        session = await store.get("test")
        assert session.completed_at is not None
        assert session.is_active is False

    @pytest.mark.asyncio
    async def test_get_by_plan(self, store: SessionStore) -> None:
        """Can get session by plan path."""
        await store.create(
            session_id="test",
            name="Test",
            plan_path="plans/coalition-forge.md",
        )

        session = await store.get_by_plan("plans/coalition-forge.md")
        assert session is not None
        assert session.id == "test"

    @pytest.mark.asyncio
    async def test_delete_session(self, store: SessionStore) -> None:
        """Can delete a session."""
        await store.create(session_id="test", name="Test")

        result = await store.delete("test")
        assert result is True

        session = await store.get("test")
        assert session is None

    @pytest.mark.asyncio
    async def test_count_active(self, store: SessionStore) -> None:
        """Can count active sessions."""
        await store.create(session_id="s1", name="Session 1")
        await store.create(session_id="s2", name="Session 2")
        await store.complete("s1")

        count = await store.count_active()
        assert count == 1


# =============================================================================
# Test: Resume Functionality
# =============================================================================


class TestResume:
    """Tests for session resume functionality."""

    @pytest.mark.asyncio
    async def test_resume_session_from_state(self) -> None:
        """Can resume a session from persisted state."""
        # Create and advance a session
        original = create_gardener_session(name="Original")
        await original.advance()  # SENSE → ACT
        await original.record_artifact(SessionArtifact(artifact_type="code", path="test.py"))

        # Serialize state
        state_dict = original.state.to_dict()

        # Resume from state
        restored_state = SessionState.from_dict(state_dict)
        resumed = GardenerSession.from_state(
            state=restored_state,
            phase=SessionPhase.ACT,
        )

        assert resumed.phase == SessionPhase.ACT
        assert len(resumed.artifacts) == 1

    @pytest.mark.asyncio
    async def test_resume_preserves_counters(self) -> None:
        """Resume preserves phase counters."""
        original = create_gardener_session(name="Original")

        # Complete 2 full cycles
        for _ in range(2):
            await original.advance()  # SENSE → ACT
            await original.advance()  # ACT → REFLECT
            await original.advance()  # REFLECT → SENSE

        state_dict = original.state.to_dict()
        restored_state = SessionState.from_dict(state_dict)
        resumed = GardenerSession.from_state(
            state=restored_state,
            phase=SessionPhase.SENSE,
        )

        assert resumed.state.sense_count == 2
        assert resumed.state.act_count == 2
        assert resumed.state.reflect_count == 2


# =============================================================================
# Test: Projections
# =============================================================================


class TestProjections:
    """Tests for session projections."""

    def test_project_to_ascii(self, session: GardenerSession) -> None:
        """Can project session to ASCII art."""
        ascii_output = project_session_to_ascii(session)

        assert "SESSION" in ascii_output
        assert "SENSE" in ascii_output
        assert "Test Session" in ascii_output
        assert "┌" in ascii_output  # Has borders

    def test_project_to_dict(self, session: GardenerSession) -> None:
        """Can project session to dictionary."""
        dict_output = project_session_to_dict(session)

        assert dict_output["id"] == session.session_id
        assert dict_output["name"] == "Test Session"
        assert dict_output["phase"] == "SENSE"
        assert "timing" in dict_output
        assert "counters" in dict_output

    @pytest.mark.asyncio
    async def test_projection_updates_with_state(self, session: GardenerSession) -> None:
        """Projections reflect current state."""
        # Initial projection
        dict1 = project_session_to_dict(session)
        assert dict1["phase"] == "SENSE"

        # Advance and project again
        await session.advance()
        dict2 = project_session_to_dict(session)
        assert dict2["phase"] == "ACT"


# =============================================================================
# Test: Polynomial Protocol
# =============================================================================


class TestPolynomialProtocol:
    """Tests for polynomial agent protocol compliance."""

    def test_polynomial_has_all_positions(self) -> None:
        """Polynomial has all phase positions."""
        assert SessionPhase.SENSE in GARDENER_SESSION_POLYNOMIAL.positions
        assert SessionPhase.ACT in GARDENER_SESSION_POLYNOMIAL.positions
        assert SessionPhase.REFLECT in GARDENER_SESSION_POLYNOMIAL.positions

    def test_polynomial_directions_accept_any_input(self) -> None:
        """Directions accept Any input (validation in handler)."""
        from typing import Any

        from agents.gardener.session import _session_directions

        # All phases accept Any (command validation happens in handler)
        sense_dirs = _session_directions(SessionPhase.SENSE)
        assert Any in sense_dirs

        act_dirs = _session_directions(SessionPhase.ACT)
        assert Any in act_dirs

        reflect_dirs = _session_directions(SessionPhase.REFLECT)
        assert Any in reflect_dirs

    def test_polynomial_invoke_returns_valid_transitions(self) -> None:
        """Polynomial invoke returns valid phase transitions."""
        # Test SENSE → ACT
        new_phase, result = GARDENER_SESSION_POLYNOMIAL.invoke(SessionPhase.SENSE, "advance")
        assert new_phase == SessionPhase.ACT

        # Test manifest stays in same phase
        new_phase, result = GARDENER_SESSION_POLYNOMIAL.invoke(SessionPhase.ACT, "manifest")
        assert new_phase == SessionPhase.ACT


# =============================================================================
# Test: Error Handling
# =============================================================================


class TestErrorHandling:
    """Tests for error handling."""

    @pytest.mark.asyncio
    async def test_abort_session(self, session: GardenerSession) -> None:
        """Can abort session from any phase."""
        result = await session.abort()
        assert result["status"] == "aborted"

    @pytest.mark.asyncio
    async def test_unknown_command_handled(self, session: GardenerSession) -> None:
        """Unknown commands are handled gracefully."""
        phase, result = session._poly.invoke(session.phase, "invalid_command")
        assert result["status"] == "unknown_command"


# =============================================================================
# Test: StoredSession Model
# =============================================================================


class TestStoredSessionModel:
    """Tests for StoredSession data model."""

    def test_stored_session_to_row_and_back(self) -> None:
        """StoredSession can be converted to row and back."""
        session = StoredSession(
            id="test-123",
            name="Test",
            plan_path="plans/test.md",
            phase="ACT",
            state={"key": "value"},
            intent={"description": "Test intent"},
            created_at=datetime.now(),
            updated_at=datetime.now(),
            is_active=True,
        )

        row = session.to_row()
        restored = StoredSession.from_row(row)

        assert restored.id == session.id
        assert restored.name == session.name
        assert restored.phase == session.phase
        assert restored.state == session.state

    def test_session_history_event_serialization(self) -> None:
        """SessionHistoryEvent can be serialized."""
        event = SessionHistoryEvent(
            id=1,
            session_id="test-123",
            event_type="advanced",
            phase_from="SENSE",
            phase_to="ACT",
            artifact={"file": "test.py"},
            timestamp=datetime.now(),
        )

        row = event.to_row()
        assert row["session_id"] == "test-123"
        assert row["event_type"] == "advanced"
