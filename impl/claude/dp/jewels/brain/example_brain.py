#!/usr/bin/env python3
"""
Example: Brain Crown Jewel as DP Formulation.

This demonstrates how to use Brain's memory management as a DP problem:
1. Create the Brain agent
2. Explore the state space
3. Examine transitions
4. Inspect the reward function (7 principles)

Note: Value computation is intentionally skipped as it's computationally expensive
      for continuous state spaces. This example focuses on the formulation itself.
"""

from dp.jewels.brain import BrainAction, BrainFormulation, BrainState, create_brain_agent


def main() -> None:
    print("=" * 70)
    print("Brain Crown Jewel as DP Formulation")
    print("=" * 70)
    print()

    # Create the formulation
    formulation = BrainFormulation()

    print("1. State Space")
    print("-" * 70)
    states = formulation.generate_states(granularity=2)
    print(f"Generated {len(states)} discrete states")
    print(f"Granularity: 2 → 2×2×2 = {len(states)} states")
    print()
    print("Sample states:")
    for i, state in enumerate(list(states)[:4]):
        print(f"  {i+1}. {state}")
    print()

    # Pick an example state
    example_state = BrainState(memory_load=0.5, relevance_decay=0.3, query_pending=True)
    print("2. Actions (state-dependent)")
    print("-" * 70)
    print(f"Current state: {example_state}")
    available = formulation.available_actions(example_state)
    print(f"Available actions: {[a.name for a in available]}")
    print()

    # Show transitions
    print("3. State Transitions")
    print("-" * 70)
    for action in available:
        next_state = formulation.transition(example_state, action)
        output = formulation.output_fn(example_state, action, next_state)
        print(f"  {action.name}:")
        print(f"    Next state: {next_state}")
        print(f"    Output: {output}")
    print()

    # Show constitution (reward function)
    print("4. Constitution (Reward Function)")
    print("-" * 70)
    constitution = formulation.create_constitution()

    # Evaluate a specific action
    action = BrainAction.CONSOLIDATE
    next_state = formulation.transition(example_state, action)
    value_score = constitution.evaluate(example_state, action, next_state)

    print(f"Action: {action.name}")
    print(f"Total reward: {value_score.total_score:.3f}")
    print()
    print("Per-principle scores:")
    for ps in value_score.principle_scores:
        print(f"  {ps.principle.name:15s}: {ps.score:.3f} (weight={ps.weight}) → {ps.weighted_score:.3f}")
        print(f"    Evidence: {ps.evidence}")
    print()

    # Create the agent (demonstrates full wiring)
    print("5. Brain ValueAgent")
    print("-" * 70)
    brain = create_brain_agent(granularity=2)
    print(f"Agent: {brain}")
    print(f"  States: {len(brain.states)}")
    print(f"  Discount factor (gamma): {brain.gamma}")
    print()

    # Show a manual transition (without DP solving)
    print("6. Manual Transition (No DP)")
    print("-" * 70)
    state = BrainState(0.0, 0.0, True)
    print(f"Start state: {state}")

    available_actions = brain.actions(state)
    print(f"Available actions: {[a.name for a in available_actions]}")

    # Pick an action manually
    action = BrainAction.RECALL
    next_state = brain.transition(state, action)
    output = brain.output_fn(state, action, next_state)

    print(f"Action chosen: {action.name}")
    print(f"Next state: {next_state}")
    print(f"Output: {output}")
    print()

    print("=" * 70)
    print("Note: Value computation and policy derivation are computationally")
    print("      expensive for continuous state spaces. For production use,")
    print("      consider:")
    print("      1. Smaller granularity (fewer states)")
    print("      2. Approximate methods (function approximation)")
    print("      3. Model-free RL (Q-learning, policy gradient)")
    print("=" * 70)


if __name__ == "__main__":
    main()
