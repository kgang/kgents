"""
Tests for WitnessPolynomial.

Verifies:
1. State machine transitions
2. Trust-gated behavior
3. Instance isolation
4. Bounded history
5. Forbidden actions

See: docs/skills/polynomial-agent.md
See: docs/skills/test-patterns.md
"""

from __future__ import annotations

import pytest

from services.witness import (
    WITNESS_POLYNOMIAL,
    EscalateCommand,
    GitEvent,
    StartCommand,
    StopCommand,
    TrustLevel,
    WitnessInputFactory,
    WitnessPhase,
    WitnessPolynomial,
    WitnessState,
)
from services.witness.polynomial import (
    ActCommand,
    ConfirmCommand,
    Suggestion,
)

# =============================================================================
# Trust Level Tests
# =============================================================================


class TestTrustLevel:
    """Test TrustLevel enum behavior."""

    def test_trust_levels_ordered(self) -> None:
        """Trust levels are ordered L0 < L1 < L2 < L3."""
        assert TrustLevel.READ_ONLY < TrustLevel.BOUNDED
        assert TrustLevel.BOUNDED < TrustLevel.SUGGESTION
        assert TrustLevel.SUGGESTION < TrustLevel.AUTONOMOUS

    def test_can_write_kgents_gated(self) -> None:
        """Only L1+ can write to .kgents/."""
        assert not TrustLevel.READ_ONLY.can_write_kgents
        assert TrustLevel.BOUNDED.can_write_kgents
        assert TrustLevel.SUGGESTION.can_write_kgents
        assert TrustLevel.AUTONOMOUS.can_write_kgents

    def test_can_suggest_gated(self) -> None:
        """Only L2+ can suggest."""
        assert not TrustLevel.READ_ONLY.can_suggest
        assert not TrustLevel.BOUNDED.can_suggest
        assert TrustLevel.SUGGESTION.can_suggest
        assert TrustLevel.AUTONOMOUS.can_suggest

    def test_can_act_gated(self) -> None:
        """Only L3 can act autonomously."""
        assert not TrustLevel.READ_ONLY.can_act
        assert not TrustLevel.BOUNDED.can_act
        assert not TrustLevel.SUGGESTION.can_act
        assert TrustLevel.AUTONOMOUS.can_act

    def test_emoji_defined_for_all_levels(self) -> None:
        """All trust levels have emojis."""
        for level in TrustLevel:
            assert level.emoji, f"Missing emoji for {level}"

    def test_description_defined_for_all_levels(self) -> None:
        """All trust levels have descriptions."""
        for level in TrustLevel:
            assert level.description, f"Missing description for {level}"


# =============================================================================
# Polynomial Basic Tests
# =============================================================================


class TestWitnessPolynomial:
    """Test WitnessPolynomial state machine."""

    def test_start_command_transitions_to_observing(self) -> None:
        """Start command moves from IDLE to OBSERVING."""
        poly = WITNESS_POLYNOMIAL
        state = WitnessState()
        assert state.phase == WitnessPhase.IDLE

        new_state, output = poly.invoke(state, StartCommand())

        assert output.success
        assert new_state.phase == WitnessPhase.OBSERVING
        assert output.thought is not None
        assert "start" in output.thought.tags

    def test_stop_command_transitions_to_idle(self) -> None:
        """Stop command moves from OBSERVING to IDLE."""
        poly = WITNESS_POLYNOMIAL
        state = WitnessState(phase=WitnessPhase.OBSERVING)

        new_state, output = poly.invoke(state, StopCommand())

        assert output.success
        assert new_state.phase == WitnessPhase.IDLE

    def test_git_event_creates_thought(self) -> None:
        """Git events create thoughts in the stream."""
        poly = WITNESS_POLYNOMIAL
        state = WitnessState(phase=WitnessPhase.OBSERVING)

        event = WitnessInputFactory.git_commit(sha="abc1234", message="Fix bug")
        new_state, output = poly.invoke(state, event)

        assert output.success
        assert output.thought is not None
        assert "abc1234" in output.thought.content
        assert "git" in output.thought.tags
        assert len(new_state.thoughts) == 1

    def test_multiple_events_accumulate_thoughts(self) -> None:
        """Multiple events accumulate in thought history."""
        poly = WITNESS_POLYNOMIAL
        state = WitnessState(phase=WitnessPhase.OBSERVING)

        for i in range(5):
            event = WitnessInputFactory.git_commit(sha=f"sha{i}")
            state, _ = poly.invoke(state, event)

        assert len(state.thoughts) == 5

    def test_thought_history_bounded(self) -> None:
        """Thought history is bounded to MAX_THOUGHTS."""
        poly = WITNESS_POLYNOMIAL
        state = WitnessState(phase=WitnessPhase.OBSERVING)

        # Add more than MAX_THOUGHTS
        for i in range(60):
            event = WitnessInputFactory.git_commit(sha=f"sha{i}")
            state, _ = poly.invoke(state, event)

        assert len(state.thoughts) == WitnessState.MAX_THOUGHTS


# =============================================================================
# Trust Escalation Tests
# =============================================================================


class TestTrustEscalation:
    """Test trust level escalation mechanics."""

    def test_cannot_escalate_without_meeting_requirements(self) -> None:
        """Escalation fails if requirements not met."""
        poly = WITNESS_POLYNOMIAL
        state = WitnessState(trust=TrustLevel.READ_ONLY)

        new_state, output = poly.invoke(state, EscalateCommand())

        assert not output.success
        assert "requirements not met" in output.message
        assert new_state.trust == TrustLevel.READ_ONLY

    def test_l0_to_l1_requires_observations(self) -> None:
        """L0 → L1 requires 100 observations."""
        state = WitnessState(trust=TrustLevel.READ_ONLY)

        # Not enough observations
        state.observation_count = 50
        assert not state.can_escalate_to_bounded

        # Enough observations
        state.observation_count = 100
        assert state.can_escalate_to_bounded

    def test_l1_to_l2_requires_successful_ops(self) -> None:
        """L1 → L2 requires 100 successful operations."""
        state = WitnessState(trust=TrustLevel.BOUNDED)

        # Not enough operations
        state.successful_operations = 50
        assert not state.can_escalate_to_suggestion

        # Enough operations
        state.successful_operations = 100
        assert state.can_escalate_to_suggestion

    def test_l2_to_l3_requires_accepted_suggestions(self) -> None:
        """L2 → L3 requires 50 suggestions with >90% acceptance."""
        state = WitnessState(trust=TrustLevel.SUGGESTION)

        # Not enough suggestions
        state.total_suggestions = 30
        state.confirmed_suggestions = 28
        assert not state.can_escalate_to_autonomous

        # Enough suggestions but low acceptance
        state.total_suggestions = 50
        state.confirmed_suggestions = 40  # 80%
        assert not state.can_escalate_to_autonomous

        # Enough suggestions with high acceptance
        state.confirmed_suggestions = 46  # 92%
        assert state.can_escalate_to_autonomous


# =============================================================================
# Trust-Gated Action Tests
# =============================================================================


class TestTrustGatedActions:
    """Test that actions are properly gated by trust level."""

    def test_act_command_requires_l3(self) -> None:
        """Act commands require AUTONOMOUS trust level."""
        poly = WITNESS_POLYNOMIAL
        state = WitnessState(trust=TrustLevel.SUGGESTION)

        _, output = poly.invoke(state, ActCommand(action="git status"))

        assert not output.success
        assert "AUTONOMOUS" in output.message

    def test_act_command_works_at_l3(self) -> None:
        """Act commands work at AUTONOMOUS trust level."""
        poly = WITNESS_POLYNOMIAL
        state = WitnessState(trust=TrustLevel.AUTONOMOUS)

        new_state, output = poly.invoke(state, ActCommand(action="git status"))

        assert output.success
        assert output.action_result is not None
        assert len(new_state.actions) == 1

    def test_forbidden_actions_blocked(self) -> None:
        """Forbidden actions are blocked even at L3."""
        poly = WITNESS_POLYNOMIAL
        state = WitnessState(trust=TrustLevel.AUTONOMOUS)

        forbidden_actions = [
            "git push --force origin main",
            "rm -rf /",
            "DROP DATABASE users",
            "DELETE FROM accounts",
            "kubectl delete namespace production",
        ]

        for action in forbidden_actions:
            _, output = poly.invoke(state, ActCommand(action=action))
            assert not output.success, f"Should block: {action}"
            assert "forbidden" in output.message.lower()

    def test_confirm_requires_l2(self) -> None:
        """Confirm commands require SUGGESTION trust level."""
        poly = WITNESS_POLYNOMIAL
        state = WitnessState(trust=TrustLevel.BOUNDED)

        _, output = poly.invoke(state, ConfirmCommand(suggestion_id="s1", approved=True))

        assert not output.success
        assert "SUGGESTION" in output.message


# =============================================================================
# Instance Isolation Tests
# =============================================================================


class TestInstanceIsolation:
    """Test that polynomial instances are properly isolated."""

    def test_state_objects_are_independent(self) -> None:
        """Different state objects don't share data."""
        poly = WITNESS_POLYNOMIAL
        state1 = WitnessState()
        state2 = WitnessState()

        # Modify state1
        event = WitnessInputFactory.git_commit(sha="abc123")
        state1, _ = poly.invoke(state1, event)

        # state2 should be unaffected
        assert len(state1.thoughts) == 1
        assert len(state2.thoughts) == 0

    def test_polynomial_singleton_is_stateless(self) -> None:
        """The polynomial singleton doesn't hold state."""
        poly1 = WITNESS_POLYNOMIAL
        poly2 = WITNESS_POLYNOMIAL

        # Should be same instance
        assert poly1 is poly2

        # Creating state objects should be independent
        state1 = WitnessState()
        state2 = WitnessState()

        state1, _ = poly1.invoke(state1, WitnessInputFactory.git_commit(sha="s1"))
        state2, _ = poly2.invoke(state2, WitnessInputFactory.git_commit(sha="s2"))

        # Each state should have its own thought
        assert len(state1.thoughts) == 1
        assert len(state2.thoughts) == 1
        assert state1.thoughts[0].content != state2.thoughts[0].content


# =============================================================================
# Thought Stream Tests
# =============================================================================


class TestThoughtStream:
    """Test thought stream behavior."""

    def test_thought_to_diary_line_format(self) -> None:
        """Thoughts format correctly as diary entries."""
        from services.witness.polynomial import Thought

        thought = Thought(
            content="Noticed commit abc123",
            source="git",
            tags=("git", "commit"),
        )

        line = thought.to_diary_line()

        assert "[git]" in line
        assert "Noticed commit abc123" in line
        assert "`git`" in line
        assert "`commit`" in line

    def test_observation_count_increments(self) -> None:
        """Observation count increments with each event."""
        poly = WITNESS_POLYNOMIAL
        state = WitnessState(phase=WitnessPhase.OBSERVING)
        assert state.observation_count == 0

        for i in range(5):
            event = WitnessInputFactory.git_commit(sha=f"sha{i}")
            state, _ = poly.invoke(state, event)

        assert state.observation_count == 5


# =============================================================================
# Event Handling Tests
# =============================================================================


class TestEventHandling:
    """Test handling of different event types."""

    def test_git_commit_event(self) -> None:
        """Git commit events are processed correctly."""
        poly = WITNESS_POLYNOMIAL
        state = WitnessState(phase=WitnessPhase.OBSERVING)

        event = GitEvent(event_type="commit", sha="abc1234", message="Fix bug")
        state, output = poly.invoke(state, event)

        assert output.success
        assert "commit" in output.thought.tags

    def test_test_failure_event(self) -> None:
        """Test failure events are processed correctly."""
        poly = WITNESS_POLYNOMIAL
        state = WitnessState(phase=WitnessPhase.OBSERVING)

        event = WitnessInputFactory.test_failed(
            test_id="test_foo::test_bar", error="AssertionError"
        )
        state, output = poly.invoke(state, event)

        assert output.success
        assert "tests" in output.thought.tags
        assert "failure" in output.thought.tags

    def test_test_session_event(self) -> None:
        """Test session events are processed correctly."""
        poly = WITNESS_POLYNOMIAL
        state = WitnessState(phase=WitnessPhase.OBSERVING)

        event = WitnessInputFactory.test_session(passed=100, failed=2, skipped=5)
        state, output = poly.invoke(state, event)

        assert output.success
        assert "100 passed" in output.thought.content
        assert "2 failed" in output.thought.content


# =============================================================================
# Acceptance Rate Tests
# =============================================================================


class TestAcceptanceRate:
    """Test suggestion acceptance rate calculation."""

    def test_acceptance_rate_zero_when_no_suggestions(self) -> None:
        """Acceptance rate is 0 when no suggestions made."""
        state = WitnessState()
        assert state.acceptance_rate == 0.0

    def test_acceptance_rate_calculation(self) -> None:
        """Acceptance rate calculated correctly."""
        state = WitnessState()
        state.total_suggestions = 10
        state.confirmed_suggestions = 8

        assert state.acceptance_rate == 0.8

    def test_confirm_updates_acceptance_rate(self) -> None:
        """Confirming suggestions updates acceptance rate."""
        poly = WITNESS_POLYNOMIAL
        state = WitnessState(trust=TrustLevel.SUGGESTION)
        state.total_suggestions = 10
        state.confirmed_suggestions = 8

        # Approve a suggestion
        state, _ = poly.invoke(state, ConfirmCommand(suggestion_id="s1", approved=True))

        assert state.confirmed_suggestions == 9
        # Note: total_suggestions doesn't change on confirm, only when suggestion is made
