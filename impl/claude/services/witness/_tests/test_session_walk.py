"""
Tests for Session-Walk Bridge.

Verifies laws:
- Law 1 (Session Owns Walk): A CLI session can have at most one active Walk
- Law 2 (Walk Outlives Session): Walk persists after session ends
- Law 3 (Optional Binding): CLI sessions work without Walks

See: services/witness/session_walk.py
"""

from __future__ import annotations

import pytest

from services.witness.mark import Mark, NPhase
from services.witness.session_walk import (
    SessionWalkBridge,
    get_session_walk_bridge,
    reset_session_walk_bridge,
)
from services.witness.walk import WalkStatus, WalkStore, reset_walk_store

# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture(autouse=True)
def reset_stores() -> None:
    """Reset global stores before each test."""
    reset_walk_store()
    reset_session_walk_bridge()


@pytest.fixture
def bridge() -> SessionWalkBridge:
    """Create a fresh bridge with isolated store."""
    store = WalkStore()
    return SessionWalkBridge(walk_store=store)


# =============================================================================
# Law 1: Session Owns Walk
# =============================================================================


class TestLaw1SessionOwnsWalk:
    """Law 1: A CLI session can have at most one active Walk."""

    def test_session_can_have_one_walk(self, bridge: SessionWalkBridge) -> None:
        """A session can have exactly one Walk."""
        walk = bridge.start_walk_for_session(
            cli_session_id="cli_test123",
            goal="Test goal",
        )

        assert walk is not None
        assert bridge.has_walk("cli_test123")

        # Retrieve the same Walk
        retrieved = bridge.get_walk_for_session("cli_test123")
        assert retrieved is not None
        assert retrieved.id == walk.id

    def test_cannot_start_second_walk_when_active(self, bridge: SessionWalkBridge) -> None:
        """Cannot create a second Walk for a session with active Walk."""
        bridge.start_walk_for_session(
            cli_session_id="cli_test123",
            goal="First goal",
        )

        with pytest.raises(ValueError) as exc_info:
            bridge.start_walk_for_session(
                cli_session_id="cli_test123",
                goal="Second goal",
            )

        assert "already has active Walk" in str(exc_info.value)

    def test_can_start_new_walk_after_completion(self, bridge: SessionWalkBridge) -> None:
        """Can create new Walk after previous one completes."""
        first = bridge.start_walk_for_session(
            cli_session_id="cli_test123",
            goal="First goal",
        )

        # Complete the first Walk
        bridge.end_session("cli_test123", complete=True)
        assert first.is_complete

        # Now can create a new Walk
        second = bridge.start_walk_for_session(
            cli_session_id="cli_test123",
            goal="Second goal",
        )

        assert second is not None
        assert second.id != first.id


# =============================================================================
# Law 2: Walk Outlives Session
# =============================================================================


class TestLaw2WalkOutlivesSession:
    """Law 2: Walk persists after session ends for audit."""

    def test_walk_persists_after_session_end(self, bridge: SessionWalkBridge) -> None:
        """Walk data persists after session ends."""
        walk = bridge.start_walk_for_session(
            cli_session_id="cli_test123",
            goal="Test goal",
        )
        walk_id = walk.id

        # Add some traces
        trace = Mark.from_thought("Test thought", "test")
        bridge.advance_walk("cli_test123", trace)

        # End session
        ended_walk = bridge.end_session("cli_test123", complete=True)

        assert ended_walk is not None
        assert ended_walk.id == walk_id
        assert ended_walk.is_complete
        assert ended_walk.mark_count == 1

    def test_walk_marked_complete_on_session_end(self, bridge: SessionWalkBridge) -> None:
        """Walk is marked COMPLETE when session ends successfully."""
        bridge.start_walk_for_session(
            cli_session_id="cli_test123",
            goal="Test goal",
        )

        ended = bridge.end_session("cli_test123", complete=True)

        assert ended is not None
        assert ended.status == WalkStatus.COMPLETE

    def test_walk_marked_abandoned_on_session_failure(self, bridge: SessionWalkBridge) -> None:
        """Walk is marked ABANDONED when session ends unsuccessfully."""
        bridge.start_walk_for_session(
            cli_session_id="cli_test123",
            goal="Test goal",
        )

        ended = bridge.end_session("cli_test123", complete=False)

        assert ended is not None
        assert ended.status == WalkStatus.ABANDONED


# =============================================================================
# Law 3: Optional Binding
# =============================================================================


class TestLaw3OptionalBinding:
    """Law 3: CLI sessions work without Walks."""

    def test_session_without_walk_returns_none(self, bridge: SessionWalkBridge) -> None:
        """get_walk_for_session returns None for sessions without Walk."""
        walk = bridge.get_walk_for_session("nonexistent_session")
        assert walk is None

    def test_has_walk_false_for_session_without_walk(self, bridge: SessionWalkBridge) -> None:
        """has_walk returns False for sessions without Walk."""
        assert not bridge.has_walk("nonexistent_session")

    def test_advance_walk_returns_false_without_walk(self, bridge: SessionWalkBridge) -> None:
        """advance_walk returns False gracefully for sessions without Walk."""
        trace = Mark.from_thought("Test", "test")
        result = bridge.advance_walk("no_walk_session", trace)
        assert result is False

    def test_end_session_returns_none_without_walk(self, bridge: SessionWalkBridge) -> None:
        """end_session returns None for sessions without Walk."""
        result = bridge.end_session("no_walk_session")
        assert result is None


# =============================================================================
# Walk Operations
# =============================================================================


class TestWalkOperations:
    """Tests for Walk operations via bridge."""

    def test_advance_walk_adds_trace(self, bridge: SessionWalkBridge) -> None:
        """advance_walk adds Mark to Walk."""
        walk = bridge.start_walk_for_session(
            cli_session_id="cli_test123",
            goal="Test goal",
        )
        assert walk.mark_count == 0

        trace = Mark.from_thought("Test thought", "git")
        result = bridge.advance_walk("cli_test123", trace)

        assert result is True
        assert walk.mark_count == 1
        assert trace.id in walk.mark_ids

    def test_transition_phase_works(self, bridge: SessionWalkBridge) -> None:
        """transition_phase_for_session changes Walk phase."""
        walk = bridge.start_walk_for_session(
            cli_session_id="cli_test123",
            goal="Test goal",
        )
        assert walk.phase == NPhase.SENSE

        result = bridge.transition_phase_for_session("cli_test123", "ACT")

        assert result is True
        assert walk.phase == NPhase.ACT

    def test_transition_phase_without_walk_returns_false(self, bridge: SessionWalkBridge) -> None:
        """transition_phase returns False without Walk."""
        result = bridge.transition_phase_for_session("no_walk", "ACT")
        assert result is False

    def test_transition_invalid_phase_returns_false(self, bridge: SessionWalkBridge) -> None:
        """Invalid phase transition returns False."""
        bridge.start_walk_for_session(
            cli_session_id="cli_test123",
            goal="Test goal",
        )

        result = bridge.transition_phase_for_session("cli_test123", "INVALID_PHASE")
        assert result is False


# =============================================================================
# Pause/Resume
# =============================================================================


class TestPauseResume:
    """Tests for Walk pause/resume."""

    def test_pause_walk(self, bridge: SessionWalkBridge) -> None:
        """pause_walk changes Walk status to PAUSED."""
        walk = bridge.start_walk_for_session(
            cli_session_id="cli_test123",
            goal="Test goal",
        )
        assert walk.is_active

        result = bridge.pause_walk("cli_test123")

        assert result is True
        assert walk.status == WalkStatus.PAUSED

    def test_resume_walk(self, bridge: SessionWalkBridge) -> None:
        """resume_walk changes Walk status back to ACTIVE."""
        walk = bridge.start_walk_for_session(
            cli_session_id="cli_test123",
            goal="Test goal",
        )
        bridge.pause_walk("cli_test123")

        result = bridge.resume_walk("cli_test123")

        assert result is True
        assert walk.status == WalkStatus.ACTIVE

    def test_pause_without_walk_returns_false(self, bridge: SessionWalkBridge) -> None:
        """pause_walk returns False without Walk."""
        result = bridge.pause_walk("no_walk")
        assert result is False

    def test_resume_without_walk_returns_false(self, bridge: SessionWalkBridge) -> None:
        """resume_walk returns False without Walk."""
        result = bridge.resume_walk("no_walk")
        assert result is False


# =============================================================================
# Forest Integration
# =============================================================================


class TestForestIntegration:
    """Tests for Forest plan binding."""

    def test_walk_with_root_plan(self, bridge: SessionWalkBridge) -> None:
        """Walk can be created with a Forest plan reference."""
        walk = bridge.start_walk_for_session(
            cli_session_id="cli_test123",
            goal="Implement WARP",
            root_plan="plans/warp-servo.md",
        )

        assert walk.root_plan is not None
        assert str(walk.root_plan) == "plans/warp-servo.md"

    def test_walk_without_root_plan(self, bridge: SessionWalkBridge) -> None:
        """Walk can be created without Forest plan (optional)."""
        walk = bridge.start_walk_for_session(
            cli_session_id="cli_test123",
            goal="Simple task",
            # No root_plan
        )

        assert walk.root_plan is None


# =============================================================================
# Global Bridge
# =============================================================================


class TestGlobalBridge:
    """Tests for global bridge singleton."""

    def test_get_global_bridge(self) -> None:
        """get_session_walk_bridge returns singleton."""
        bridge1 = get_session_walk_bridge()
        bridge2 = get_session_walk_bridge()
        assert bridge1 is bridge2

    def test_reset_global_bridge(self) -> None:
        """reset_session_walk_bridge clears singleton."""
        bridge1 = get_session_walk_bridge()
        reset_session_walk_bridge()
        bridge2 = get_session_walk_bridge()
        assert bridge1 is not bridge2


# =============================================================================
# Statistics
# =============================================================================


class TestStatistics:
    """Tests for bridge statistics."""

    def test_active_sessions_with_walks(self, bridge: SessionWalkBridge) -> None:
        """active_sessions_with_walks returns correct list."""
        # No sessions
        assert bridge.active_sessions_with_walks() == []

        # Add two sessions with Walks
        bridge.start_walk_for_session("session1", "Goal 1")
        bridge.start_walk_for_session("session2", "Goal 2")

        active = bridge.active_sessions_with_walks()
        assert len(active) == 2
        assert "session1" in active
        assert "session2" in active

        # End one session
        bridge.end_session("session1")

        active = bridge.active_sessions_with_walks()
        assert len(active) == 1
        assert "session2" in active
