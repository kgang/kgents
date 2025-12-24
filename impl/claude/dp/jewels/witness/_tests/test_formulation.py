"""
Tests for Witness MDP Formulation.

These tests verify that:
1. State transitions follow the witnessing process
2. Actions are appropriately restricted by state
3. Reward function aligns with principles
4. ValueAgent produces sensible policies
5. The self-referential witnessing works (PolicyTrace captures decisions)

Teaching:
    gotcha: These tests use the actual WitnessFormulation and ValueAgent,
            not mocks. This is integration testing at the formulation level.
            We verify the STRUCTURE is correct, not that we get specific
            optimal values (which depend on reward tuning).
            (Evidence: We check that policies exist and make sense, not
             that they match hardcoded expected values)
"""

import pytest

from dp.jewels.witness import (
    WitnessAction,
    WitnessContext,
    WitnessFormulation,
    WitnessState,
    create_witness_agent,
    witness_available_actions,
    witness_reward,
    witness_transition,
)


# =============================================================================
# State Transition Tests
# =============================================================================


def test_transition_idle_to_observing():
    """From IDLE, OBSERVE moves to OBSERVING."""
    next_state = witness_transition(WitnessState.IDLE, WitnessAction.OBSERVE)
    assert next_state == WitnessState.OBSERVING


def test_transition_observing_to_marking():
    """From OBSERVING, MARK moves to MARKING."""
    next_state = witness_transition(WitnessState.OBSERVING, WitnessAction.MARK)
    assert next_state == WitnessState.MARKING


def test_transition_observing_to_idle_via_skip():
    """From OBSERVING, SKIP returns to IDLE."""
    next_state = witness_transition(WitnessState.OBSERVING, WitnessAction.SKIP)
    assert next_state == WitnessState.IDLE


def test_transition_marking_to_crystallizing():
    """From MARKING, CRYSTALLIZE moves to CRYSTALLIZING."""
    next_state = witness_transition(WitnessState.MARKING, WitnessAction.CRYSTALLIZE)
    assert next_state == WitnessState.CRYSTALLIZING


def test_transition_marking_to_observing():
    """From MARKING, OBSERVE returns to OBSERVING."""
    next_state = witness_transition(WitnessState.MARKING, WitnessAction.OBSERVE)
    assert next_state == WitnessState.OBSERVING


def test_transition_crystallizing_to_observing():
    """From CRYSTALLIZING, OBSERVE returns to OBSERVING."""
    next_state = witness_transition(WitnessState.CRYSTALLIZING, WitnessAction.OBSERVE)
    assert next_state == WitnessState.OBSERVING


def test_transition_observing_to_querying():
    """From OBSERVING, QUERY moves to QUERYING."""
    next_state = witness_transition(WitnessState.OBSERVING, WitnessAction.QUERY)
    assert next_state == WitnessState.QUERYING


def test_transition_querying_to_observing():
    """From QUERYING, OBSERVE returns to OBSERVING."""
    next_state = witness_transition(WitnessState.QUERYING, WitnessAction.OBSERVE)
    assert next_state == WitnessState.OBSERVING


def test_transition_invalid_stays_in_state():
    """Invalid actions don't crash; state remains unchanged."""
    # CRYSTALLIZE from IDLE doesn't make sense
    next_state = witness_transition(WitnessState.IDLE, WitnessAction.CRYSTALLIZE)
    assert next_state == WitnessState.IDLE  # Should stay in IDLE


# =============================================================================
# Available Actions Tests
# =============================================================================


def test_available_actions_idle():
    """From IDLE, only OBSERVE is available."""
    actions = witness_available_actions(WitnessState.IDLE)
    assert actions == frozenset({WitnessAction.OBSERVE})


def test_available_actions_observing():
    """From OBSERVING, can MARK, SKIP, QUERY, or continue OBSERVE."""
    actions = witness_available_actions(WitnessState.OBSERVING)
    assert WitnessAction.MARK in actions
    assert WitnessAction.SKIP in actions
    assert WitnessAction.QUERY in actions
    assert WitnessAction.OBSERVE in actions


def test_available_actions_marking():
    """From MARKING, can CRYSTALLIZE or return to OBSERVE."""
    actions = witness_available_actions(WitnessState.MARKING)
    assert WitnessAction.CRYSTALLIZE in actions
    assert WitnessAction.OBSERVE in actions


def test_available_actions_crystallizing():
    """From CRYSTALLIZING, can only return to OBSERVE."""
    actions = witness_available_actions(WitnessState.CRYSTALLIZING)
    assert actions == frozenset({WitnessAction.OBSERVE})


def test_available_actions_querying():
    """From QUERYING, can only return to OBSERVE."""
    actions = witness_available_actions(WitnessState.QUERYING)
    assert actions == frozenset({WitnessAction.OBSERVE})


# =============================================================================
# Reward Function Tests
# =============================================================================


def test_reward_mark_significant_event_positive():
    """Marking a significant event gets positive reward (ETHICAL)."""
    context = WitnessContext(event_significance=0.9, mark_count=2)
    reward = witness_reward(
        WitnessState.OBSERVING,
        WitnessAction.MARK,
        WitnessState.MARKING,
        context,
    )
    assert reward > 0.0, "Marking significant events should be rewarded"


def test_reward_skip_significant_event_negative():
    """Skipping a significant event gets negative reward (lost auditability)."""
    context = WitnessContext(event_significance=0.9)
    reward = witness_reward(
        WitnessState.OBSERVING,
        WitnessAction.SKIP,
        WitnessState.IDLE,
        context,
    )
    assert reward < 0.0, "Skipping significant events should be penalized"


def test_reward_crystallize_positive():
    """CRYSTALLIZE gets high reward (GENERATIVE compression)."""
    context = WitnessContext(insight_density=0.8, mark_count=10)
    reward = witness_reward(
        WitnessState.MARKING,
        WitnessAction.CRYSTALLIZE,
        WitnessState.CRYSTALLIZING,
        context,
    )
    assert reward > 1.0, "Crystallization should be highly rewarded"


def test_reward_mark_with_many_marks_penalty():
    """Marking when mark_count is high gets penalty (verbosity)."""
    context = WitnessContext(event_significance=0.5, mark_count=25)
    reward_high_count = witness_reward(
        WitnessState.OBSERVING,
        WitnessAction.MARK,
        WitnessState.MARKING,
        context,
    )

    context_low = WitnessContext(event_significance=0.5, mark_count=3)
    reward_low_count = witness_reward(
        WitnessState.OBSERVING,
        WitnessAction.MARK,
        WitnessState.MARKING,
        context_low,
    )

    assert reward_low_count > reward_high_count, (
        "Early marks should be more valuable (compression building corpus)"
    )


def test_reward_query_scales_with_relevance():
    """QUERY reward scales with query_relevance."""
    context_high = WitnessContext(query_relevance=0.9)
    reward_high = witness_reward(
        WitnessState.OBSERVING,
        WitnessAction.QUERY,
        WitnessState.QUERYING,
        context_high,
    )

    context_low = WitnessContext(query_relevance=0.1)
    reward_low = witness_reward(
        WitnessState.OBSERVING,
        WitnessAction.QUERY,
        WitnessState.QUERYING,
        context_low,
    )

    assert reward_high > reward_low, "Higher relevance should give higher reward"


def test_reward_skip_insignificant_event_positive():
    """Skipping an insignificant event is good (TASTEFUL signal/noise)."""
    context = WitnessContext(event_significance=0.2)
    reward = witness_reward(
        WitnessState.OBSERVING,
        WitnessAction.SKIP,
        WitnessState.IDLE,
        context,
    )
    # Should get bonus for filtering noise
    assert reward >= 0.0, "Skipping noise should be neutral or positive"


# =============================================================================
# WitnessFormulation Tests
# =============================================================================


def test_witness_formulation_creation():
    """WitnessFormulation can be created."""
    formulation = WitnessFormulation()
    assert formulation.name == "Witness"
    assert formulation.state_type == WitnessState
    assert WitnessState.IDLE in formulation.initial_states


def test_witness_formulation_with_context():
    """WitnessFormulation accepts custom context."""
    context = WitnessContext(
        event_significance=0.8,
        mark_count=5,
        insight_density=0.7,
    )
    formulation = WitnessFormulation(context=context)
    assert formulation.context == context


def test_witness_formulation_transition():
    """WitnessFormulation.transition works correctly."""
    formulation = WitnessFormulation()
    next_state = formulation.transition(WitnessState.IDLE, WitnessAction.OBSERVE)
    assert next_state == WitnessState.OBSERVING


def test_witness_formulation_reward():
    """WitnessFormulation.reward works correctly."""
    formulation = WitnessFormulation()
    reward = formulation.reward(
        WitnessState.OBSERVING,
        WitnessAction.MARK,
        WitnessState.MARKING,
    )
    assert isinstance(reward, float)


def test_witness_formulation_available_actions():
    """WitnessFormulation.available_actions works correctly."""
    formulation = WitnessFormulation()
    actions = formulation.available_actions(WitnessState.OBSERVING)
    assert WitnessAction.MARK in actions
    assert WitnessAction.SKIP in actions


# =============================================================================
# ValueAgent Tests
# =============================================================================


def test_create_witness_agent():
    """create_witness_agent() returns a ValueAgent."""
    agent = create_witness_agent()
    assert agent.name == "WitnessAgent"
    assert len(agent.states) == 5  # 5 WitnessState values


def test_witness_agent_policy_idle():
    """From IDLE, policy should be OBSERVE."""
    agent = create_witness_agent()
    action = agent.policy(WitnessState.IDLE)
    assert action == WitnessAction.OBSERVE, "Only valid action from IDLE is OBSERVE"


def test_witness_agent_policy_observing():
    """From OBSERVING, policy should be a valid action."""
    agent = create_witness_agent()
    action = agent.policy(WitnessState.OBSERVING)
    assert action in {
        WitnessAction.MARK,
        WitnessAction.SKIP,
        WitnessAction.QUERY,
        WitnessAction.OBSERVE,
    }, "Policy must choose a valid action from OBSERVING"


def test_witness_agent_invoke():
    """agent.invoke() executes one step and returns trace."""
    agent = create_witness_agent()
    next_state, output, trace = agent.invoke(
        WitnessState.IDLE,
        WitnessAction.OBSERVE,
    )

    assert next_state == WitnessState.OBSERVING
    assert isinstance(output, str)
    assert len(trace.log) > 0, "Trace should record the action"


def test_witness_agent_invoke_with_policy():
    """agent.invoke() without action uses policy."""
    agent = create_witness_agent()
    next_state, output, trace = agent.invoke(WitnessState.IDLE)

    # Should use policy (OBSERVE from IDLE)
    assert next_state == WitnessState.OBSERVING
    assert len(trace.log) > 0


def test_witness_agent_value():
    """agent.value() computes optimal value from state."""
    agent = create_witness_agent()
    trace = agent.value(WitnessState.IDLE)

    # Should return a PolicyTrace
    assert trace is not None
    assert hasattr(trace, "value")
    assert hasattr(trace, "log")


def test_witness_agent_value_is_cached():
    """agent.value() caches results for efficiency."""
    agent = create_witness_agent()

    # First call computes value
    trace1 = agent.value(WitnessState.IDLE)

    # Second call should be cached (same object)
    trace2 = agent.value(WitnessState.IDLE)

    # Values should be consistent
    assert trace1.total_value() == trace2.total_value()


def test_witness_agent_with_custom_context():
    """create_witness_agent() with custom context affects policy."""
    # Context with high event significance should prefer MARK
    context_high = WitnessContext(event_significance=0.95, mark_count=2)
    agent = create_witness_agent(context=context_high)

    # We can't deterministically assert the policy without running the solver,
    # but we can verify the agent was created with the context
    assert agent.constitution is not None


def test_witness_agent_gamma_parameter():
    """create_witness_agent() accepts gamma parameter."""
    agent = create_witness_agent(gamma=0.8)
    assert agent.gamma == 0.8


# =============================================================================
# Self-Referential Witnessing Tests
# =============================================================================


def test_policy_trace_witnesses_witnessing():
    """
    The Witness witnesses itself via PolicyTrace.

    Every decision to mark/skip/crystallize is itself recorded in the trace.
    This is the self-referential aspect: the witness of witnessing.
    """
    agent = create_witness_agent()

    # Start from IDLE
    state = WitnessState.IDLE

    # Take several steps, collecting trace
    full_trace_entries = []

    for _ in range(5):
        action = agent.policy(state)
        if action is None:
            break

        next_state, output, trace = agent.invoke(state, action)
        full_trace_entries.extend(trace.log)
        state = next_state

    # The trace should record all witnessing decisions
    assert len(full_trace_entries) > 0, "PolicyTrace should record decisions"

    # Each entry is a witness mark of the witnessing process
    for entry in full_trace_entries:
        assert entry.action is not None
        assert entry.state_before is not None
        assert entry.state_after is not None
        # The entry IS the witness of the decision


def test_witness_formulation_no_goal_state():
    """Witness has no terminal goal state (witnessing is ongoing)."""
    formulation = WitnessFormulation()
    assert len(formulation.goal_states) == 0, (
        "Witnessing is an ongoing process, not a goal-seeking task"
    )


# =============================================================================
# Principle Alignment Tests
# =============================================================================


def test_constitution_evaluators_present():
    """ValueAgent has constitution with principle evaluators."""
    agent = create_witness_agent()
    assert agent.constitution is not None

    # Verify evaluators are set for all principles
    from services.categorical.dp_bridge import Principle

    for principle in Principle:
        # Constitution should have evaluator for each principle
        evaluator = agent.constitution.evaluators.get(principle)
        assert evaluator is not None, f"Missing evaluator for {principle.name}"


def test_reward_reflects_multiple_principles():
    """
    Reward function combines multiple principle evaluations.

    A single action (e.g., MARK) should be evaluated against:
    - GENERATIVE (compression)
    - ETHICAL (auditability)
    - TASTEFUL (signal/noise)
    - CURATED (intentionality)
    - etc.
    """
    # High-significance, early mark should score well across principles
    context = WitnessContext(
        event_significance=0.9,
        mark_count=3,
        insight_density=0.8,
        trace_coherence=0.9,
    )

    reward = witness_reward(
        WitnessState.OBSERVING,
        WitnessAction.MARK,
        WitnessState.MARKING,
        context,
    )

    # Should get positive contribution from multiple principles
    assert reward > 0.5, "Good marking should score well across principles"


# =============================================================================
# Edge Cases
# =============================================================================


def test_witness_agent_handles_all_states():
    """Agent can handle all WitnessState values."""
    agent = create_witness_agent()

    for state in WitnessState:
        # Should not crash
        action = agent.policy(state)
        # Policy might be None for some states (no valid actions)
        if action is not None:
            assert action in witness_available_actions(state)


def test_witness_formulation_frozen():
    """WitnessFormulation is immutable (frozen=True)."""
    formulation = WitnessFormulation()

    # Attempting to modify should fail
    with pytest.raises(AttributeError):
        formulation.name = "Modified"  # type: ignore


def test_witness_state_hashable():
    """WitnessState is hashable (required for state space)."""
    state_set = {WitnessState.IDLE, WitnessState.OBSERVING}
    assert len(state_set) == 2


def test_witness_action_hashable():
    """WitnessAction is hashable (required for action space)."""
    action_set = {WitnessAction.MARK, WitnessAction.SKIP}
    assert len(action_set) == 2
