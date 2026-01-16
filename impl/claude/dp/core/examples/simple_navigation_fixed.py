#!/usr/bin/env python3
"""
Simple Navigation Example using ValueAgent (Fixed).

This demonstrates the core ValueAgent API with a proper episodic task:
1. Defining state space, actions, transitions
2. Using Constitution for rewards (7 principles)
3. Computing value functions
4. Deriving optimal policies
5. Executing the agent

The scenario: Navigate from start to goal in 2 steps.
"""

from dp.core import Constitution, ValueAgent
from services.categorical.dp_bridge import Principle


def main() -> None:
    print("=" * 70)
    print("ValueAgent Example: Simple Navigation (Fixed)")
    print("=" * 70)
    print()

    # Create Constitution with custom evaluators
    constitution = Constitution()

    # COMPOSABLE: Strongly reward reaching the goal
    constitution.set_evaluator(
        Principle.COMPOSABLE,
        lambda s, a, ns: 10.0 if ns == "goal" else 0.0,
        lambda s, a, ns: "GOAL REACHED!" if ns == "goal" else "Not at goal",
    )

    # JOY_INDUCING: Reward forward moves
    constitution.set_evaluator(
        Principle.JOY_INDUCING,
        lambda s, a, ns: 0.5 if a == "forward" else 0.1,
        lambda s, a, ns: "Making progress" if a == "forward" else "Going backward",
    )

    print("Constitution configured:")
    print(f"  - COMPOSABLE (weight={Principle.COMPOSABLE.weight}): HUGE reward for goal")
    print(f"  - JOY_INDUCING (weight={Principle.JOY_INDUCING.weight}): Prefer forward")
    print()

    # Define the navigation agent
    # Key insight: The value function will prefer paths that lead to the goal
    navigator = ValueAgent(
        name="Navigator",
        states=frozenset({"start", "middle", "goal"}),
        actions=lambda s: (
            frozenset({"forward", "backward"})
            if s == "start" or s == "middle"
            else frozenset()  # No actions from goal (terminal)
        ),
        transition=lambda s, a: (
            "middle"
            if s == "start" and a == "forward"
            else "goal"
            if s == "middle" and a == "forward"
            else "start"
            if s == "middle" and a == "backward"
            else s  # Stay in same state if no valid transition
        ),
        output_fn=lambda s, a, ns: f"Moved from {s} to {ns} via {a}",
        constitution=constitution,
        gamma=0.9,  # Lower gamma to prefer shorter paths
    )

    print(f"Agent: {navigator}")
    print(f"  States: {navigator.states}")
    print(f"  Discount factor: {navigator.gamma}")
    print()

    # Analyze the reward structure
    print("-" * 70)
    print("Reward Structure Analysis")
    print("-" * 70)
    print()

    transitions = [
        ("start", "forward", "middle"),
        ("start", "backward", "start"),
        ("middle", "forward", "goal"),
        ("middle", "backward", "start"),
    ]

    for s, a, ns in transitions:
        reward = constitution.reward(s, a, ns)
        print(f"R({s}, {a}, {ns}) = {reward:.4f}")

    print()

    # Show that optimal policy should prefer: start -> middle -> goal
    print("-" * 70)
    print("Expected Optimal Path")
    print("-" * 70)
    print("start --forward--> middle --forward--> goal")
    print("This path has cumulative reward:")
    print("  R(start, forward, middle) + γ * R(middle, forward, goal)")
    r1 = constitution.reward("start", "forward", "middle")
    r2 = constitution.reward("middle", "forward", "goal")
    print(f"  = {r1:.4f} + {navigator.gamma} * {r2:.4f}")
    print(f"  = {r1 + navigator.gamma * r2:.4f}")
    print()

    # Compute value functions
    print("-" * 70)
    print("Value Functions (first invocation only)")
    print("-" * 70)
    print()

    # Just compute for start to demonstrate
    trace = navigator.value("start")
    print(f"V(start) = {trace.total_value():.4f}")
    print(f"  Policy trace has {len(trace.log)} steps")
    if trace.log:
        print("  First 5 steps:")
        for i, entry in enumerate(trace.log[:5], 1):
            print(f"    {i}. {entry.summary}")
    print()

    # Derive optimal policies (this will use cached values)
    print("-" * 70)
    print("Optimal Policies")
    print("-" * 70)
    print()

    for state in ["start", "middle"]:
        action = navigator.policy(state)
        print(f"π({state}) = {action}")

    print()

    # Execute the agent
    print("-" * 70)
    print("Executing Agent (using optimal policy)")
    print("-" * 70)
    print()

    current_state = "start"
    step = 0
    max_steps = 10

    while current_state != "goal" and step < max_steps:
        step += 1
        print(f"Step {step}: State = {current_state}")

        # Execute using optimal policy
        next_state, output, trace = navigator.invoke(current_state)

        print(f"  Action: {trace.log[0].action}")
        print(f"  Output: {output}")
        print(f"  Reward: {trace.log[0].value:.4f}")
        print(f"  Next state: {next_state}")
        print()

        current_state = next_state

    if current_state == "goal":
        print(f"✓ SUCCESS! Reached goal in {step} steps.")
    else:
        print(f"✗ Failed to reach goal after {max_steps} steps.")

    print()
    print("=" * 70)


if __name__ == "__main__":
    main()
