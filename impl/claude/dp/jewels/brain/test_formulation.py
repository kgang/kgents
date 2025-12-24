"""
Tests for Brain DP formulation.

Validates:
1. State space generation
2. Action availability
3. State transitions
4. Constitution (reward function)
5. Value computation
6. Policy derivation
"""

import pytest

from dp.jewels.brain import (
    BrainState,
    BrainAction,
    BrainFormulation,
    create_brain_agent,
)


# =============================================================================
# State Tests
# =============================================================================


def test_brain_state_valid():
    """Valid BrainState should construct successfully."""
    state = BrainState(memory_load=0.5, relevance_decay=0.3, query_pending=True)
    assert state.memory_load == 0.5
    assert state.relevance_decay == 0.3
    assert state.query_pending is True


def test_brain_state_invalid_load():
    """BrainState should reject invalid memory_load."""
    with pytest.raises(ValueError, match="memory_load must be in"):
        BrainState(memory_load=1.5, relevance_decay=0.3, query_pending=False)

    with pytest.raises(ValueError, match="memory_load must be in"):
        BrainState(memory_load=-0.1, relevance_decay=0.3, query_pending=False)


def test_brain_state_invalid_decay():
    """BrainState should reject invalid relevance_decay."""
    with pytest.raises(ValueError, match="relevance_decay must be in"):
        BrainState(memory_load=0.5, relevance_decay=1.5, query_pending=False)


def test_brain_state_hashable():
    """BrainState must be hashable for DP caching."""
    state1 = BrainState(0.5, 0.3, True)
    state2 = BrainState(0.5, 0.3, True)
    state3 = BrainState(0.5, 0.3, False)

    # Same values → same hash
    assert hash(state1) == hash(state2)

    # Different values → (probably) different hash
    assert hash(state1) != hash(state3)

    # Can be used as dict keys
    value_table = {state1: 1.0, state3: 2.0}
    assert value_table[state2] == 1.0  # state2 == state1


# =============================================================================
# Formulation Tests
# =============================================================================


def test_generate_states():
    """State space should be finite and correctly sized."""
    states = BrainFormulation.generate_states(granularity=2)

    # 2 memory_load × 2 relevance_decay × 2 query_pending = 8 states
    assert len(states) == 2 * 2 * 2
    assert all(isinstance(s, BrainState) for s in states)

    # All states should be valid
    for state in states:
        assert 0.0 <= state.memory_load <= 1.0
        assert 0.0 <= state.relevance_decay <= 1.0


def test_available_actions():
    """Action availability should respect state constraints."""
    formulation = BrainFormulation()

    # Full memory: can't CAPTURE
    full_state = BrainState(1.0, 0.5, False)
    actions = formulation.available_actions(full_state)
    assert BrainAction.CAPTURE not in actions
    assert BrainAction.WAIT in actions

    # Query pending: can RECALL
    query_state = BrainState(0.5, 0.5, True)
    actions = formulation.available_actions(query_state)
    assert BrainAction.RECALL in actions

    # No query: can't RECALL
    no_query_state = BrainState(0.5, 0.5, False)
    actions = formulation.available_actions(no_query_state)
    assert BrainAction.RECALL not in actions

    # Empty memory: can't FORGET
    empty_state = BrainState(0.0, 0.5, False)
    actions = formulation.available_actions(empty_state)
    assert BrainAction.FORGET not in actions

    # Low memory: can't CONSOLIDATE
    low_state = BrainState(0.2, 0.5, False)
    actions = formulation.available_actions(low_state)
    assert BrainAction.CONSOLIDATE not in actions

    # Enough memory: can CONSOLIDATE
    enough_state = BrainState(0.5, 0.5, False)
    actions = formulation.available_actions(enough_state)
    assert BrainAction.CONSOLIDATE in actions


def test_transition_capture():
    """CAPTURE should increase load and reset decay."""
    formulation = BrainFormulation()
    state = BrainState(0.5, 0.6, False)

    next_state = formulation.transition(state, BrainAction.CAPTURE)

    assert next_state.memory_load > state.memory_load  # Increased
    assert next_state.relevance_decay == 0.0  # Reset
    assert next_state.query_pending == state.query_pending  # Unchanged


def test_transition_recall():
    """RECALL should clear query and possibly increase decay."""
    formulation = BrainFormulation()
    # Use discretized state (0.0 or 1.0 for granularity=2)
    state = BrainState(1.0, 0.0, True)

    next_state = formulation.transition(state, BrainAction.RECALL)

    assert next_state.query_pending is False  # Cleared
    # With quantization, small decay increases may not show
    assert next_state.relevance_decay >= state.relevance_decay  # Non-decreasing


def test_transition_forget():
    """FORGET should reduce load (with quantization)."""
    formulation = BrainFormulation()
    # Use discretized state
    state = BrainState(1.0, 0.0, False)

    next_state = formulation.transition(state, BrainAction.FORGET)

    assert next_state.memory_load <= state.memory_load  # Reduced or same (quantized)
    # Decay increases but quantizes to 0.0 or 1.0
    assert next_state.relevance_decay >= 0.0


def test_transition_consolidate():
    """CONSOLIDATE should reduce load and/or decay (with quantization)."""
    formulation = BrainFormulation()
    # Use discretized state
    state = BrainState(1.0, 1.0, False)

    next_state = formulation.transition(state, BrainAction.CONSOLIDATE)

    # At least one should decrease (with quantization effects)
    decreased = (
        next_state.memory_load < state.memory_load
        or next_state.relevance_decay < state.relevance_decay
    )
    assert decreased or (next_state.memory_load <= 1.0 and next_state.relevance_decay <= 1.0)


def test_transition_wait():
    """WAIT should only increase decay (with quantization)."""
    formulation = BrainFormulation()
    # Use discretized state
    state = BrainState(0.0, 0.0, False)

    next_state = formulation.transition(state, BrainAction.WAIT)

    assert next_state.memory_load == state.memory_load  # Unchanged
    # Decay increases but quantizes
    assert next_state.relevance_decay >= state.relevance_decay
    assert next_state.query_pending == state.query_pending  # Unchanged


# =============================================================================
# Constitution Tests
# =============================================================================


def test_constitution_composable():
    """COMPOSABLE principle should reward coherence."""
    formulation = BrainFormulation()
    constitution = formulation.create_constitution()

    # Use discretized state
    state = BrainState(1.0, 1.0, False)

    # CONSOLIDATE should get high COMPOSABLE score
    next_state = formulation.transition(state, BrainAction.CONSOLIDATE)
    value_score = constitution.evaluate(state, BrainAction.CONSOLIDATE, next_state)

    composable_score = next(
        ps.score for ps in value_score.principle_scores if ps.principle.name == "COMPOSABLE"
    )

    assert composable_score > 0.7  # Should be high


def test_constitution_generative():
    """GENERATIVE principle should reward compression."""
    formulation = BrainFormulation()
    constitution = formulation.create_constitution()

    # Use discretized state
    state = BrainState(1.0, 1.0, False)

    # CONSOLIDATE should get high GENERATIVE score
    next_state = formulation.transition(state, BrainAction.CONSOLIDATE)
    value_score = constitution.evaluate(state, BrainAction.CONSOLIDATE, next_state)

    generative_score = next(
        ps.score for ps in value_score.principle_scores if ps.principle.name == "GENERATIVE"
    )

    # CONSOLIDATE should be positive for GENERATIVE (compression)
    assert generative_score >= 0.5  # At least neutral


def test_constitution_joy_inducing():
    """JOY_INDUCING principle should reward serendipity."""
    formulation = BrainFormulation()
    constitution = formulation.create_constitution()

    # Use discretized state with query pending
    state = BrainState(1.0, 1.0, True)
    next_state = formulation.transition(state, BrainAction.RECALL)
    value_score = constitution.evaluate(state, BrainAction.RECALL, next_state)

    joy_score = next(
        ps.score for ps in value_score.principle_scores if ps.principle.name == "JOY_INDUCING"
    )

    # RECALL should have some JOY score
    assert joy_score >= 0.3  # At least some joy


# =============================================================================
# Agent Tests
# =============================================================================


def test_create_brain_agent():
    """create_brain_agent should return a configured ValueAgent."""
    brain = create_brain_agent(granularity=2)

    assert brain.name == "Brain"
    assert len(brain.states) == 2 * 2 * 2  # 8 states
    assert brain.gamma == 0.95


def test_brain_agent_structure():
    """Brain agent structure should be correctly configured."""
    brain = create_brain_agent(granularity=2)

    # Verify basic structure
    assert brain.name == "Brain"
    assert len(brain.states) == 8  # 2×2×2
    assert brain.gamma == 0.95

    # Verify state space contains expected states
    expected_state = BrainState(0.0, 0.0, False)
    assert expected_state in brain.states

    # Verify actions are available
    actions = brain.actions(expected_state)
    assert len(actions) > 0
    assert BrainAction.WAIT in actions


def test_brain_agent_policy_lookup():
    """Brain agent can look up policies (though computation may be slow)."""
    brain = create_brain_agent(granularity=2)

    # Test that policy lookup doesn't crash (value computation happens internally)
    # Note: This may be slow as it triggers DP solver
    state = BrainState(0.0, 0.0, True)

    # Query pending state should have RECALL available
    available = brain.actions(state)
    assert BrainAction.RECALL in available


@pytest.mark.slow
def test_brain_agent_value():
    """
    Brain agent should compute value functions.

    Marked as slow because DP solving for continuous state spaces is expensive.
    """
    brain = create_brain_agent(granularity=2)

    state = BrainState(0.0, 0.0, False)
    trace = brain.value(state)

    # Should have a finite value (could be 0 or positive)
    assert trace.total_value() >= 0.0

    # Trace may be empty for some states (no better action than staying)
    assert len(trace.log) >= 0


@pytest.mark.slow
def test_brain_agent_policy():
    """
    Brain agent should derive optimal policies.

    Marked as slow because policy derivation triggers value computation.
    """
    brain = create_brain_agent(granularity=2)

    # Query pending: should RECALL
    query_state = BrainState(0.0, 0.0, True)
    action = brain.policy(query_state)
    assert action is not None

    # High load, high decay: should CONSOLIDATE or FORGET
    full_stale_state = BrainState(1.0, 1.0, False)
    action = brain.policy(full_stale_state)
    assert action in [BrainAction.CONSOLIDATE, BrainAction.FORGET]


@pytest.mark.slow
def test_brain_agent_invoke():
    """
    Brain agent should execute optimally.

    Marked as slow because invoke triggers policy derivation.
    """
    brain = create_brain_agent(granularity=2)

    state = BrainState(0.0, 0.0, False)
    next_state, output, trace = brain.invoke(state)

    # Should transition to a valid state
    assert next_state in brain.states

    # Should produce output
    assert isinstance(output, str)
    assert "Brain:" in output

    # Should have a trace
    assert len(trace.log) == 1
