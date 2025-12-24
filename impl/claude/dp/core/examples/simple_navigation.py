#!/usr/bin/env python3
"""
Simple Navigation Example using ValueAgent.

This demonstrates the core ValueAgent API:
1. Defining state space, actions, transitions
2. Using Constitution for rewards (7 principles)
3. Computing value functions
4. Deriving optimal policies
5. Executing the agent

The scenario: A simple grid navigation where the agent must reach a goal.
"""

from dp.core import Constitution, ValueAgent
from services.categorical.dp_bridge import Principle


def main() -> None:
    print("=" * 70)
    print("ValueAgent Example: Simple Navigation")
    print("=" * 70)
    print()

    # Create Constitution with custom evaluators
    constitution = Constitution()

    # COMPOSABLE: Reward reaching the goal
    constitution.set_evaluator(
        Principle.COMPOSABLE,
        lambda s, a, ns: 1.0 if ns == "goal" else 0.2,
        lambda s, a, ns: "Goal reached!" if ns == "goal" else "Still navigating",
    )

    # JOY_INDUCING: Reward forward progress
    constitution.set_evaluator(
        Principle.JOY_INDUCING,
        lambda s, a, ns: 0.8 if a == "forward" else 0.5,
        lambda s, a, ns: "Making progress" if a == "forward" else "Neutral move",
    )

    print("Constitution configured:")
    print(f"  - COMPOSABLE (weight={Principle.COMPOSABLE.weight}): Goal-oriented")
    print(f"  - JOY_INDUCING (weight={Principle.JOY_INDUCING.weight}): Forward progress")
    print()

    # Define the navigation agent
    navigator = ValueAgent(
        name="Navigator",
        states=frozenset({"start", "middle", "goal"}),
        actions=lambda s: frozenset({"forward", "backward"}) if s != "goal" else frozenset(),
        transition=lambda s, a: (
            "middle" if s == "start" and a == "forward" else
            "goal" if s == "middle" and a == "forward" else
            "start" if s == "middle" and a == "backward" else
            s
        ),
        output_fn=lambda s, a, ns: f"Moved from {s} to {ns} via {a}",
        constitution=constitution,
        gamma=0.95,
    )

    print(f"Agent: {navigator}")
    print(f"  States: {navigator.states}")
    print(f"  Discount factor: {navigator.gamma}")
    print()

    # Compute value functions for all states
    print("-" * 70)
    print("Computing Value Functions")
    print("-" * 70)
    print()

    for state in ["start", "middle", "goal"]:
        trace = navigator.value(state)
        print(f"V({state}) = {trace.total_value():.4f}")
        print(f"  Optimal path has {len(trace.log)} steps")
        if trace.log:
            print("  Trace:")
            for i, entry in enumerate(trace.log, 1):
                print(f"    {i}. {entry.summary}")
        print()

    # Derive optimal policies
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
        print(f"Step {step}: Current state = {current_state}")

        # Execute using optimal policy
        next_state, output, trace = navigator.invoke(current_state)

        print(f"  Action: {trace.log[0].action}")
        print(f"  Output: {output}")
        print(f"  Reward: {trace.log[0].value:.4f}")
        print(f"  Next state: {next_state}")
        print()

        current_state = next_state

    if current_state == "goal":
        print(f"SUCCESS! Reached goal in {step} steps.")
    else:
        print(f"Failed to reach goal after {max_steps} steps.")

    print()
    print("=" * 70)


if __name__ == "__main__":
    main()
