"""
Tests for MetabolicSession Polynomial: Checkpoint 0.3 verification.

User Journey:
    begin → greeting → hydrated → working → compost → reflect → dormant

Teaching:
    gotcha: Session allows rehydration during work (WORKING → HYDRATED).
            This models the real workflow: deep work → stuck → context refresh.
"""

from __future__ import annotations

import pytest

from ..polynomial import (
    SESSION_POLYNOMIAL,
    session_directions,
    session_transition,
)
from ..types import (
    CompostEntry,
    EnergyLevel,
    SessionEvent,
    SessionOutput,
    SessionState,
    WorkMode,
)


class TestSessionDirections:
    """Test valid commands per state."""

    def test_dormant_can_begin(self) -> None:
        """DORMANT allows begin and quick_start."""
        cmds = session_directions(SessionState.DORMANT)
        assert "begin" in cmds
        assert "quick_start" in cmds

    def test_greeting_can_complete(self) -> None:
        """GREETING allows completing coffee or skipping."""
        cmds = session_directions(SessionState.GREETING)
        assert "complete_greeting" in cmds
        assert "skip_to_hydrate" in cmds
        assert "coffee_continue" in cmds

    def test_hydrated_can_work(self) -> None:
        """HYDRATED allows starting work."""
        cmds = session_directions(SessionState.HYDRATED)
        assert "start_work" in cmds
        assert "rehydrate" in cmds

    def test_working_allows_rehydrate(self) -> None:
        """WORKING allows going back to hydration."""
        cmds = session_directions(SessionState.WORKING)
        assert "rehydrate" in cmds
        assert "checkpoint" in cmds
        assert "compost" in cmds

    def test_composting_can_learn(self) -> None:
        """COMPOSTING allows adding learnings."""
        cmds = session_directions(SessionState.COMPOSTING)
        assert "add_learning" in cmds
        assert "finish_compost" in cmds

    def test_reflecting_can_complete(self) -> None:
        """REFLECTING allows completion."""
        cmds = session_directions(SessionState.REFLECTING)
        assert "complete" in cmds
        assert "linger" in cmds

    def test_abort_always_valid(self) -> None:
        """abort is valid in all non-DORMANT states."""
        for state in SessionState:
            cmds = session_directions(state)
            assert "abort" in cmds

    def test_status_always_valid(self) -> None:
        """status is valid in all states."""
        for state in SessionState:
            cmds = session_directions(state)
            assert "status" in cmds


class TestBasicTransitions:
    """Test basic state transitions."""

    def test_begin_from_dormant(self) -> None:
        """begin moves from DORMANT to GREETING."""
        state, output = session_transition(SessionState.DORMANT, "begin")

        assert state == SessionState.GREETING
        assert output.status == "ok"
        assert output.metadata is not None
        assert "Coffee" in output.message

    def test_quick_start_skips_greeting(self) -> None:
        """quick_start goes directly to HYDRATED."""
        state, output = session_transition(SessionState.DORMANT, "quick_start")

        assert state == SessionState.HYDRATED
        assert output.status == "ok"

    def test_complete_greeting_to_hydrated(self) -> None:
        """complete_greeting moves to HYDRATED."""
        state, output = session_transition(
            SessionState.GREETING,
            {"command": "complete_greeting", "task_focus": "testing"},
        )

        assert state == SessionState.HYDRATED
        assert output.status == "ok"
        assert "testing" in output.message

    def test_start_work_from_hydrated(self) -> None:
        """start_work moves to WORKING."""
        state, output = session_transition(
            SessionState.HYDRATED,
            {"command": "start_work", "mode": "deep"},
        )

        assert state == SessionState.WORKING
        assert output.status == "ok"
        assert output.metadata is not None
        assert output.metadata.work_mode == WorkMode.DEEP

    def test_compost_from_working(self) -> None:
        """compost moves from WORKING to COMPOSTING."""
        state, output = session_transition(SessionState.WORKING, "compost")

        assert state == SessionState.COMPOSTING
        assert output.status == "ok"

    def test_finish_compost_to_reflecting(self) -> None:
        """finish_compost moves to REFLECTING."""
        state, output = session_transition(SessionState.COMPOSTING, "finish_compost")

        assert state == SessionState.REFLECTING
        assert output.status == "ok"

    def test_complete_from_reflecting(self) -> None:
        """complete moves to DORMANT."""
        state, output = session_transition(SessionState.REFLECTING, "complete")

        assert state == SessionState.DORMANT
        assert output.status == "ok"


class TestRehydrateDuringWork:
    """Test the key insight: rehydration is allowed during work."""

    def test_rehydrate_during_work(self) -> None:
        """WORKING → HYDRATED transition is allowed."""
        state, output = session_transition(
            SessionState.WORKING,
            {"command": "rehydrate", "task": "understanding the new API"},
        )

        assert state == SessionState.HYDRATED
        assert output.status == "ok"
        assert output.data.get("from_working") is True

    def test_rehydrate_preserves_context(self) -> None:
        """Rehydration returns to HYDRATED with task context."""
        state, output = session_transition(
            SessionState.WORKING,
            {"command": "rehydrate", "task": "need more context on X"},
        )

        assert state == SessionState.HYDRATED
        assert "X" in output.message


class TestComposting:
    """Test learning capture during composting."""

    def test_add_learning(self) -> None:
        """add_learning captures a compost entry."""
        state, output = session_transition(
            SessionState.COMPOSTING,
            {
                "command": "add_learning",
                "insight": "Always check for None before accessing",
                "severity": "warning",
                "evidence": "test_foo.py::test_none_check",
            },
        )

        assert state == SessionState.COMPOSTING
        assert len(output.compost) == 1
        assert output.compost[0].insight == "Always check for None before accessing"
        assert output.compost[0].severity == "warning"

    def test_skip_reflect(self) -> None:
        """skip_reflect ends the session."""
        state, output = session_transition(SessionState.COMPOSTING, "skip_reflect")

        assert state == SessionState.DORMANT
        assert output.status == "ok"


class TestUniversalCommands:
    """Test commands valid in all states."""

    def test_abort_returns_to_dormant(self) -> None:
        """abort from any state returns to DORMANT."""
        for start_state in [
            SessionState.GREETING,
            SessionState.HYDRATED,
            SessionState.WORKING,
            SessionState.COMPOSTING,
            SessionState.REFLECTING,
        ]:
            state, output = session_transition(start_state, "abort")
            assert state == SessionState.DORMANT
            assert output.status == "aborted"

    def test_status_returns_current_state(self) -> None:
        """status returns current state info."""
        for start_state in SessionState:
            state, output = session_transition(start_state, "status")
            assert state == start_state
            assert output.status == "ok"
            assert start_state.name in output.message


class TestWorkModes:
    """Test different work modes."""

    def test_deep_work_mode(self) -> None:
        """Can start in deep work mode."""
        state, output = session_transition(
            SessionState.HYDRATED,
            {"command": "start_work", "mode": "deep"},
        )

        assert output.metadata is not None
        assert output.metadata.work_mode == WorkMode.DEEP

    def test_exploration_mode(self) -> None:
        """Can start in exploration mode."""
        state, output = session_transition(
            SessionState.HYDRATED,
            {"command": "start_work", "mode": "exploration"},
        )

        assert output.metadata is not None
        assert output.metadata.work_mode == WorkMode.EXPLORATION


class TestEnergyTracking:
    """Test energy level logging."""

    def test_log_energy(self) -> None:
        """Can log energy level during work."""
        state, output = session_transition(
            SessionState.WORKING,
            {"command": "log_energy", "level": "low"},
        )

        assert state == SessionState.WORKING
        assert output.data.get("energy_level") == "low"


class TestSessionEvent:
    """Test SessionEvent input format."""

    def test_event_input(self) -> None:
        """Can use SessionEvent as input."""
        event = SessionEvent(command="begin", data={})
        state, output = session_transition(SessionState.DORMANT, event)

        assert state == SessionState.GREETING


class TestPolynomialAgent:
    """Test the polynomial agent itself."""

    def test_polynomial_has_all_states(self) -> None:
        """Polynomial includes all session states."""
        for state in SessionState:
            assert state in SESSION_POLYNOMIAL.positions

    def test_polynomial_name(self) -> None:
        """Polynomial has descriptive name."""
        assert "Metabolic" in SESSION_POLYNOMIAL.name


class TestFullCycle:
    """Integration test for a complete session cycle."""

    def test_full_cycle(self) -> None:
        """Test the complete developer day cycle."""
        state = SessionState.DORMANT

        # Begin session
        state, output = session_transition(state, "begin")
        assert state == SessionState.GREETING

        # Complete coffee
        state, output = session_transition(
            state,
            {"command": "complete_greeting", "task_focus": "implement feature X"},
        )
        assert state == SessionState.HYDRATED

        # Start working
        state, output = session_transition(
            state,
            {"command": "start_work", "mode": "deep"},
        )
        assert state == SessionState.WORKING

        # Rehydrate (got stuck)
        state, output = session_transition(
            state,
            {"command": "rehydrate", "task": "understanding edge case"},
        )
        assert state == SessionState.HYDRATED

        # Back to work
        state, output = session_transition(
            state,
            {"command": "start_work", "mode": "deep"},
        )
        assert state == SessionState.WORKING

        # Compost
        state, output = session_transition(state, "compost")
        assert state == SessionState.COMPOSTING

        # Add learning
        state, output = session_transition(
            state,
            {
                "command": "add_learning",
                "insight": "Edge cases need explicit handling",
                "severity": "warning",
            },
        )
        assert state == SessionState.COMPOSTING
        assert len(output.compost) == 1

        # Finish compost
        state, output = session_transition(state, "finish_compost")
        assert state == SessionState.REFLECTING

        # Complete
        state, output = session_transition(
            state,
            {"command": "complete", "accomplished": True},
        )
        assert state == SessionState.DORMANT
        assert output.data.get("accomplished") is True
