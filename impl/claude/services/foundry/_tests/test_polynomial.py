"""
Tests for FoundryPolynomial state machine.

Tests state transitions and polynomial structure.
"""

import pytest

from services.foundry import (
    FOUNDRY_POLYNOMIAL,
    VALID_TRANSITIONS,
    FoundryEvent,
    FoundryState,
    FoundryStateMachine,
    can_transition,
    get_valid_next_states,
)


class TestFoundryState:
    """Test FoundryState enum."""

    def test_all_states_defined(self) -> None:
        """All expected states are defined."""
        states = list(FoundryState)
        assert len(states) == 8

        assert FoundryState.IDLE in states
        assert FoundryState.CLASSIFYING in states
        assert FoundryState.GENERATING in states
        assert FoundryState.VALIDATING in states
        assert FoundryState.SELECTING in states
        assert FoundryState.PROJECTING in states
        assert FoundryState.CACHING in states
        assert FoundryState.FAILED in states

    def test_terminal_states(self) -> None:
        """IDLE and FAILED are terminal states."""
        assert FoundryState.IDLE.is_terminal
        assert FoundryState.FAILED.is_terminal

        assert not FoundryState.CLASSIFYING.is_terminal
        assert not FoundryState.GENERATING.is_terminal

    def test_processing_states(self) -> None:
        """Processing states are correctly identified."""
        assert not FoundryState.IDLE.is_processing
        assert not FoundryState.FAILED.is_processing

        assert FoundryState.CLASSIFYING.is_processing
        assert FoundryState.GENERATING.is_processing
        assert FoundryState.VALIDATING.is_processing
        assert FoundryState.SELECTING.is_processing
        assert FoundryState.PROJECTING.is_processing
        assert FoundryState.CACHING.is_processing


class TestTransitions:
    """Test state transition logic."""

    def test_valid_transitions_from_idle(self) -> None:
        """From IDLE, can only transition to CLASSIFYING."""
        assert can_transition(FoundryState.IDLE, FoundryState.CLASSIFYING)
        assert not can_transition(FoundryState.IDLE, FoundryState.GENERATING)
        assert not can_transition(FoundryState.IDLE, FoundryState.FAILED)

    def test_valid_transitions_from_classifying(self) -> None:
        """From CLASSIFYING, can go to GENERATING, SELECTING, or FAILED."""
        assert can_transition(FoundryState.CLASSIFYING, FoundryState.GENERATING)
        assert can_transition(FoundryState.CLASSIFYING, FoundryState.SELECTING)
        assert can_transition(FoundryState.CLASSIFYING, FoundryState.FAILED)

        assert not can_transition(FoundryState.CLASSIFYING, FoundryState.CACHING)

    def test_valid_transitions_from_failed(self) -> None:
        """From FAILED, can only reset to IDLE."""
        assert can_transition(FoundryState.FAILED, FoundryState.IDLE)
        assert not can_transition(FoundryState.FAILED, FoundryState.CLASSIFYING)

    def test_get_valid_next_states(self) -> None:
        """get_valid_next_states returns correct set."""
        next_states = get_valid_next_states(FoundryState.CLASSIFYING)
        assert next_states == {
            FoundryState.GENERATING,
            FoundryState.SELECTING,
            FoundryState.FAILED,
        }


class TestStateMachine:
    """Test FoundryStateMachine."""

    @pytest.fixture
    def machine(self) -> FoundryStateMachine:
        """Create a fresh state machine."""
        return FoundryStateMachine()

    def test_initial_state(self, machine: FoundryStateMachine) -> None:
        """Initial state is IDLE."""
        assert machine.state == FoundryState.IDLE

    def test_valid_transition(self, machine: FoundryStateMachine) -> None:
        """Valid transitions succeed."""
        result = machine.transition(FoundryState.CLASSIFYING, FoundryEvent.START_FORGE)
        assert result is True
        assert machine.state == FoundryState.CLASSIFYING

    def test_invalid_transition(self, machine: FoundryStateMachine) -> None:
        """Invalid transitions fail and don't change state."""
        result = machine.transition(FoundryState.PROJECTING, FoundryEvent.START_FORGE)
        assert result is False
        assert machine.state == FoundryState.IDLE

    def test_transition_history(self, machine: FoundryStateMachine) -> None:
        """Transitions are recorded in history."""
        machine.transition(FoundryState.CLASSIFYING, FoundryEvent.START_FORGE)
        machine.transition(FoundryState.SELECTING, FoundryEvent.REALITY_CLASSIFIED)

        history = machine.history
        assert len(history) == 2
        assert history[0].from_state == FoundryState.IDLE
        assert history[0].to_state == FoundryState.CLASSIFYING
        assert history[1].from_state == FoundryState.CLASSIFYING
        assert history[1].to_state == FoundryState.SELECTING

    def test_reset(self, machine: FoundryStateMachine) -> None:
        """Reset returns to IDLE."""
        machine.transition(FoundryState.CLASSIFYING, FoundryEvent.START_FORGE)
        machine.reset()

        assert machine.state == FoundryState.IDLE

    def test_fail(self, machine: FoundryStateMachine) -> None:
        """Fail transitions to FAILED state."""
        machine.transition(FoundryState.CLASSIFYING, FoundryEvent.START_FORGE)
        machine.fail("Something went wrong")

        assert machine.state == FoundryState.FAILED

        # Check error in history
        history = machine.history
        last = history[-1]
        assert last.to_state == FoundryState.FAILED
        assert last.payload == {"error": "Something went wrong"}


class TestPolynomial:
    """Test FoundryPolynomial structure."""

    def test_all_states_are_positions(self) -> None:
        """All states are positions in the polynomial."""
        for state in FoundryState:
            assert state in FOUNDRY_POLYNOMIAL.positions

    def test_valid_inputs_for_idle(self) -> None:
        """IDLE accepts only START_FORGE."""
        inputs = FOUNDRY_POLYNOMIAL.valid_inputs(FoundryState.IDLE)
        assert inputs == frozenset({FoundryEvent.START_FORGE})

    def test_valid_inputs_for_failed(self) -> None:
        """FAILED accepts only RESET."""
        inputs = FOUNDRY_POLYNOMIAL.valid_inputs(FoundryState.FAILED)
        assert inputs == frozenset({FoundryEvent.RESET})

    def test_valid_inputs_for_processing_states(self) -> None:
        """Processing states accept their completion event and ERROR."""
        for state in [
            FoundryState.CLASSIFYING,
            FoundryState.GENERATING,
            FoundryState.VALIDATING,
            FoundryState.SELECTING,
            FoundryState.PROJECTING,
            FoundryState.CACHING,
        ]:
            inputs = FOUNDRY_POLYNOMIAL.valid_inputs(state)
            assert FoundryEvent.ERROR in inputs
            assert len(inputs) == 2  # Completion event + ERROR
