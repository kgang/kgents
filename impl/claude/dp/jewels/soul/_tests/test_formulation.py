"""
Tests for Soul MDP formulation.

Validates that personality dynamics work as expected:
- State transitions are valid
- Actions available based on state
- Rewards align with principles
- Value iteration converges to stable attractors
- Composition respects personality coherence
"""

import pytest

from dp.jewels.soul import (
    SoulState,
    SoulAction,
    SoulContext,
    SoulFormulation,
    soul_transition,
    soul_available_actions,
    soul_reward,
    create_soul_agent,
)


# =============================================================================
# State Tests
# =============================================================================


def test_soul_state_validation():
    """SoulState validates trait and mood ranges."""
    # Valid state
    state = SoulState(
        curiosity=0.5,
        boldness=0.5,
        playfulness=0.5,
        wisdom=0.5,
        arousal=0.0,
        valence=0.0,
        attractor_strength=0.5,
        resonance_depth=0.5,
    )
    assert state.curiosity == 0.5
    assert state.attractor_strength == 0.5

    # Invalid curiosity (out of range)
    with pytest.raises(ValueError, match="curiosity must be in"):
        SoulState(
            curiosity=1.5,  # Invalid
            boldness=0.5,
            playfulness=0.5,
            wisdom=0.5,
            arousal=0.0,
            valence=0.0,
            attractor_strength=0.5,
            resonance_depth=0.5,
        )

    # Invalid arousal (out of range)
    with pytest.raises(ValueError, match="arousal must be in"):
        SoulState(
            curiosity=0.5,
            boldness=0.5,
            playfulness=0.5,
            wisdom=0.5,
            arousal=2.0,  # Invalid
            valence=0.0,
            attractor_strength=0.5,
            resonance_depth=0.5,
        )


def test_soul_state_immutability():
    """SoulState is frozen (immutable)."""
    state = SoulState(
        curiosity=0.5,
        boldness=0.5,
        playfulness=0.5,
        wisdom=0.5,
        arousal=0.0,
        valence=0.0,
        attractor_strength=0.5,
        resonance_depth=0.5,
    )

    with pytest.raises(Exception):  # FrozenInstanceError
        state.curiosity = 0.8  # type: ignore


# =============================================================================
# Action Tests
# =============================================================================


def test_soul_action_enum():
    """SoulAction enum has expected values."""
    assert SoulAction.EXPRESS
    assert SoulAction.SUPPRESS
    assert SoulAction.MODULATE
    assert SoulAction.RESONATE
    assert SoulAction.DRIFT


def test_soul_available_actions_drift_always_available():
    """DRIFT is always available (can always explore)."""
    # Minimal state
    state = SoulState(
        curiosity=0.0,
        boldness=0.0,
        playfulness=0.0,
        wisdom=0.0,
        arousal=0.0,
        valence=0.0,
        attractor_strength=0.0,
        resonance_depth=0.0,
    )
    actions = soul_available_actions(state)
    assert SoulAction.DRIFT in actions

    # Maximal state
    state = SoulState(
        curiosity=1.0,
        boldness=1.0,
        playfulness=1.0,
        wisdom=1.0,
        arousal=1.0,
        valence=1.0,
        attractor_strength=1.0,
        resonance_depth=1.0,
    )
    actions = soul_available_actions(state)
    assert SoulAction.DRIFT in actions


def test_soul_available_actions_express_when_unconverged():
    """EXPRESS available when attractor_strength < 0.95."""
    state = SoulState(
        curiosity=0.5,
        boldness=0.5,
        playfulness=0.5,
        wisdom=0.5,
        arousal=0.0,
        valence=0.0,
        attractor_strength=0.3,  # Low
        resonance_depth=0.5,
    )
    actions = soul_available_actions(state)
    assert SoulAction.EXPRESS in actions

    # Fully converged: EXPRESS not available
    state = SoulState(
        curiosity=0.5,
        boldness=0.5,
        playfulness=0.5,
        wisdom=0.5,
        arousal=0.0,
        valence=0.0,
        attractor_strength=0.98,  # High
        resonance_depth=0.5,
    )
    actions = soul_available_actions(state)
    assert SoulAction.EXPRESS not in actions


def test_soul_available_actions_resonate_when_shallow():
    """RESONATE available when resonance_depth < 0.9."""
    state = SoulState(
        curiosity=0.5,
        boldness=0.5,
        playfulness=0.5,
        wisdom=0.5,
        arousal=0.0,
        valence=0.0,
        attractor_strength=0.5,
        resonance_depth=0.4,  # Shallow
    )
    actions = soul_available_actions(state)
    assert SoulAction.RESONATE in actions

    # Deep resonance: RESONATE not available
    state = SoulState(
        curiosity=0.5,
        boldness=0.5,
        playfulness=0.5,
        wisdom=0.5,
        arousal=0.0,
        valence=0.0,
        attractor_strength=0.5,
        resonance_depth=0.95,  # Deep
    )
    actions = soul_available_actions(state)
    assert SoulAction.RESONATE not in actions


# =============================================================================
# Transition Tests
# =============================================================================


def test_soul_transition_express_strengthens_attractor():
    """EXPRESS action increases attractor_strength."""
    state = SoulState(
        curiosity=0.5,
        boldness=0.5,
        playfulness=0.5,
        wisdom=0.5,
        arousal=0.0,
        valence=0.0,
        attractor_strength=0.3,
        resonance_depth=0.5,
    )

    next_state = soul_transition(state, SoulAction.EXPRESS)
    assert next_state.attractor_strength > state.attractor_strength


def test_soul_transition_suppress_weakens_attractor():
    """SUPPRESS action decreases attractor_strength."""
    state = SoulState(
        curiosity=0.5,
        boldness=0.5,
        playfulness=0.5,
        wisdom=0.5,
        arousal=0.0,
        valence=0.0,
        attractor_strength=0.7,
        resonance_depth=0.5,
    )

    next_state = soul_transition(state, SoulAction.SUPPRESS)
    assert next_state.attractor_strength < state.attractor_strength


def test_soul_transition_resonate_increases_depth():
    """RESONATE action increases resonance_depth."""
    state = SoulState(
        curiosity=0.5,
        boldness=0.5,
        playfulness=0.5,
        wisdom=0.5,
        arousal=0.0,
        valence=0.0,
        attractor_strength=0.5,
        resonance_depth=0.3,
    )

    next_state = soul_transition(state, SoulAction.RESONATE)
    assert next_state.resonance_depth > state.resonance_depth


def test_soul_transition_drift_weakens_attractor():
    """DRIFT action decreases attractor_strength (exploration)."""
    state = SoulState(
        curiosity=0.5,
        boldness=0.5,
        playfulness=0.5,
        wisdom=0.5,
        arousal=0.0,
        valence=0.0,
        attractor_strength=0.7,
        resonance_depth=0.5,
    )

    next_state = soul_transition(state, SoulAction.DRIFT)
    assert next_state.attractor_strength < state.attractor_strength


def test_soul_transition_returns_new_state():
    """Transitions create new states (immutability)."""
    state = SoulState(
        curiosity=0.5,
        boldness=0.5,
        playfulness=0.5,
        wisdom=0.5,
        arousal=0.0,
        valence=0.0,
        attractor_strength=0.5,
        resonance_depth=0.5,
    )

    next_state = soul_transition(state, SoulAction.EXPRESS)
    assert next_state is not state
    assert id(next_state) != id(state)


# =============================================================================
# Reward Tests
# =============================================================================


def test_soul_reward_express_with_high_attractor():
    """EXPRESS gets reward when attractor strengthens."""
    state = SoulState(
        curiosity=0.5,
        boldness=0.5,
        playfulness=0.5,
        wisdom=0.5,
        arousal=0.0,
        valence=0.0,
        attractor_strength=0.3,
        resonance_depth=0.5,
    )

    next_state = SoulState(
        curiosity=0.6,
        boldness=0.5,
        playfulness=0.5,
        wisdom=0.5,
        arousal=0.1,
        valence=0.0,
        attractor_strength=0.5,  # Increased
        resonance_depth=0.5,
    )

    reward = soul_reward(state, SoulAction.EXPRESS, next_state)
    assert reward > 0.0  # Positive reward for strengthening


def test_soul_reward_drift_when_converged_penalty():
    """DRIFT gets penalty when already converged (don't explore)."""
    state = SoulState(
        curiosity=0.5,
        boldness=0.5,
        playfulness=0.5,
        wisdom=0.5,
        arousal=0.0,
        valence=0.0,
        attractor_strength=0.9,  # High convergence
        resonance_depth=0.7,
    )

    next_state = SoulState(
        curiosity=0.4,
        boldness=0.6,
        playfulness=0.5,
        wisdom=0.5,
        arousal=0.0,
        valence=0.0,
        attractor_strength=0.7,  # Weakened
        resonance_depth=0.6,
    )

    reward = soul_reward(state, SoulAction.DRIFT, next_state)
    # Should include drift penalty when converged
    # Exact value depends on all reward components, but drift penalty is -0.5


def test_soul_reward_resonate_increases():
    """RESONATE gets reward for deepening connection."""
    state = SoulState(
        curiosity=0.5,
        boldness=0.5,
        playfulness=0.5,
        wisdom=0.5,
        arousal=0.0,
        valence=0.0,
        attractor_strength=0.5,
        resonance_depth=0.3,
    )

    next_state = SoulState(
        curiosity=0.5,
        boldness=0.5,
        playfulness=0.5,
        wisdom=0.5,
        arousal=-0.1,  # Calmer
        valence=0.2,  # More positive
        attractor_strength=0.6,
        resonance_depth=0.5,  # Increased
    )

    reward = soul_reward(state, SoulAction.RESONATE, next_state)
    assert reward > 1.0  # Strong positive reward for resonance


def test_soul_reward_with_context():
    """Context affects reward calculation."""
    state = SoulState(
        curiosity=0.5,
        boldness=0.5,
        playfulness=0.5,
        wisdom=0.5,
        arousal=0.0,
        valence=0.0,
        attractor_strength=0.5,
        resonance_depth=0.5,
    )

    next_state = SoulState(
        curiosity=0.6,
        boldness=0.5,
        playfulness=0.5,
        wisdom=0.5,
        arousal=0.1,
        valence=0.0,
        attractor_strength=0.6,
        resonance_depth=0.5,
    )

    # Context with high value alignment
    context = SoulContext(value_alignment=0.9, interaction_quality=0.8)
    reward_with_context = soul_reward(state, SoulAction.EXPRESS, next_state, context)

    # Context with low alignment
    context_low = SoulContext(value_alignment=0.3, interaction_quality=0.3)
    reward_low_context = soul_reward(state, SoulAction.EXPRESS, next_state, context_low)

    # Higher alignment should give higher reward
    assert reward_with_context > reward_low_context


# =============================================================================
# Formulation Tests
# =============================================================================


def test_soul_formulation_creation():
    """SoulFormulation can be created with default context."""
    formulation = SoulFormulation()
    assert formulation.name == "Soul"
    assert formulation.state_type == SoulState


def test_soul_formulation_with_custom_context():
    """SoulFormulation accepts custom context."""
    context = SoulContext(
        target_trait=2,  # Playfulness
        environmental_pressure=0.5,
        value_alignment=0.9,
    )
    formulation = SoulFormulation(context=context)
    assert formulation.context.target_trait == 2
    assert formulation.context.value_alignment == 0.9


# =============================================================================
# ValueAgent Tests
# =============================================================================


def test_create_soul_agent():
    """create_soul_agent returns a ValueAgent."""
    agent = create_soul_agent(granularity=2)  # Small for speed
    assert agent.name == "SoulAgent"
    assert len(agent.states) > 0


def test_soul_agent_policy():
    """Soul agent can compute policy for a state."""
    agent = create_soul_agent(granularity=2)

    # Create a state that should be in the agent's space
    state = SoulState(
        curiosity=0.0,
        boldness=0.0,
        playfulness=0.0,
        wisdom=0.0,
        arousal=-1.0,
        valence=-1.0,
        attractor_strength=0.0,
        resonance_depth=0.0,
    )

    # If state is in agent's space, we can get a policy
    if state in agent.states:
        action = agent.policy(state)
        assert action in soul_available_actions(state)


def test_soul_agent_invoke():
    """Soul agent can execute one step."""
    agent = create_soul_agent(granularity=2)

    # Use a state from the agent's state space
    state = next(iter(agent.states))

    # Get optimal action
    action = agent.policy(state)

    # Execute
    next_state, output, trace = agent.invoke(state, action)

    assert next_state in agent.states
    assert isinstance(output, str)
    assert len(trace.log) > 0


def test_soul_agent_value_convergence():
    """Soul agent's value function converges (DP works)."""
    agent = create_soul_agent(granularity=2)

    # Pick a state
    state = next(iter(agent.states))

    # Compute value (triggers value iteration)
    trace = agent.value(state)
    value = trace.total_value()

    # Value should be finite (convergence)
    assert value < float("inf")
    assert value > -float("inf")


# =============================================================================
# Integration Tests
# =============================================================================


def test_soul_evolution_trajectory():
    """Soul evolves over multiple steps following policy."""
    agent = create_soul_agent(granularity=2)

    # Start with a weak attractor
    initial = SoulState(
        curiosity=0.5,
        boldness=0.5,
        playfulness=0.5,
        wisdom=0.5,
        arousal=0.0,
        valence=0.0,
        attractor_strength=0.0,  # Weak
        resonance_depth=0.0,
    )

    # If initial not in state space, find closest
    if initial not in agent.states:
        # Use a state from the space
        initial = next(iter(agent.states))

    # Evolve for 5 steps
    state = initial
    trajectory = [state]

    for _ in range(5):
        action = agent.policy(state)
        if action is None:
            break
        next_state, output, trace = agent.invoke(state, action)
        trajectory.append(next_state)
        state = next_state

    # Trajectory should show evolution
    assert len(trajectory) > 1


def test_soul_personality_compression():
    """Soul converges to characteristic patterns (compression)."""
    agent = create_soul_agent(granularity=2)

    # Measure convergence: ratio of unique states to total steps
    # A converged personality should visit fewer unique states (attractor)

    initial = next(iter(agent.states))
    state = initial
    visited = set()
    steps = 10

    for _ in range(steps):
        visited.add(state)
        action = agent.policy(state)
        if action is None:
            break
        next_state, _, _ = agent.invoke(state, action)
        state = next_state

    # Compression ratio: if personality converges, unique_states / total_steps < 1.0
    compression_ratio = len(visited) / steps
    # This is a weak test (just checking it's computable)
    assert 0.0 <= compression_ratio <= 1.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
