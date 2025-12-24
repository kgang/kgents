#!/usr/bin/env python3
"""
Coin Collector Example using ValueAgent.

This is a simpler example that demonstrates ValueAgent correctly:
- A finite horizon problem (collect coins in limited steps)
- Clear state space and transitions
- Optimal policy derivation

The scenario: Collect coins at different locations.
Each location has a coin value, and we can move between locations.
"""

from dp.core import Constitution, ValueAgent
from services.categorical.dp_bridge import Principle


def main() -> None:
    print("=" * 70)
    print("ValueAgent Example: Coin Collector")
    print("=" * 70)
    print()

    # Create Constitution
    constitution = Constitution()

    # COMPOSABLE: Reward collecting valuable coins
    constitution.set_evaluator(
        Principle.COMPOSABLE,
        lambda s, a, ns: {
            "gold": 1.0,
            "silver": 0.6,
            "bronze": 0.3,
            "empty": 0.0,
        }.get(ns, 0.0),
        lambda s, a, ns: f"Collected {ns} coin" if ns != "empty" else "No coin here",
    )

    print("Constitution configured:")
    print("  - COMPOSABLE: Reward coin collection")
    print("    - gold: 1.0")
    print("    - silver: 0.6")
    print("    - bronze: 0.3")
    print("    - empty: 0.0")
    print()

    # Define the coin collector agent
    # States represent which location we're at
    # Actions represent which location to move to
    collector = ValueAgent(
        name="CoinCollector",
        states=frozenset({"empty", "bronze", "silver", "gold"}),
        actions=lambda s: frozenset({"empty", "bronze", "silver", "gold"}) - {s},
        transition=lambda s, a: a,  # Moving to a location means going to that state
        output_fn=lambda s, a, ns: f"Moved from {s} to {ns}",
        constitution=constitution,
        gamma=0.8,  # Discount future rewards
    )

    print(f"Agent: {collector}")
    print(f"  States: {collector.states}")
    print(f"  Actions from 'empty': {collector.actions('empty')}")
    print(f"  Discount factor: {collector.gamma}")
    print()

    # Analyze the reward structure
    print("-" * 70)
    print("Reward Structure")
    print("-" * 70)
    print()

    from_state = "empty"
    for to_state in ["bronze", "silver", "gold"]:
        reward = constitution.reward(from_state, to_state, to_state)
        print(f"R({from_state}, move_to_{to_state}, {to_state}) = {reward:.4f}")

    print()

    # Show optimal policy
    print("-" * 70)
    print("Optimal Policies")
    print("-" * 70)
    print()
    print("From any state, the agent should prefer moving to 'gold' (highest reward)")
    print()

    for state in ["empty", "bronze", "silver"]:
        action = collector.policy(state)
        print(f"π({state}) = move to {action}")

    print()

    # Execute the agent for a few steps
    print("-" * 70)
    print("Execution Example")
    print("-" * 70)
    print()

    current_state = "empty"
    total_reward = 0.0

    for step in range(1, 4):
        print(f"Step {step}: State = {current_state}")

        # Execute using optimal policy
        next_state, output, trace = collector.invoke(current_state)
        reward = trace.log[0].value

        print(f"  Action: move to {trace.log[0].state_after}")
        print(f"  Reward: {reward:.4f}")
        print(f"  Cumulative reward: {total_reward:.4f}")
        print()

        total_reward += reward
        current_state = next_state

    print(f"Final cumulative reward: {total_reward:.4f}")
    print()

    # Demonstrate value function
    print("-" * 70)
    print("Value Functions")
    print("-" * 70)
    print()
    print("V(state) = expected cumulative reward from that state")
    print()

    for state in ["empty", "bronze", "silver", "gold"]:
        trace = collector.value(state)
        print(f"V({state}) = {trace.total_value():.4f}")

    print()
    print("Notice: V(gold) > V(silver) > V(bronze) > V(empty)")
    print("The value function encodes which states are 'better' to be in.")
    print()
    print("=" * 70)


if __name__ == "__main__":
    main()
