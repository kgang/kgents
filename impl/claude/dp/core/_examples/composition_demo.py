"""
Demo: ValueAgent Sequential Composition via >> Operator

This demonstrates the Bellman-based composition:
V_{f >> g}(s) = max_a [R_f(s,a) + γ * V_g(f(s,a))]

The composed agent's value function combines:
1. Immediate reward from first agent
2. Discounted future value from second agent
"""

from dp.core import Constitution, ValueAgent
from services.categorical.dp_bridge import Principle


def main():
    print("=" * 80)
    print("ValueAgent Sequential Composition Demo")
    print("=" * 80)
    print()

    # Create a constitution with high reward for forward progress
    constitution = Constitution()
    constitution.set_evaluator(
        Principle.COMPOSABLE,
        lambda s, a, ns: 1.0 if a == "forward" else 0.3,
        lambda s, a, ns: "Good progress!" if a == "forward" else "Meh",
    )

    # Agent f: moves from state 0 to 1
    agent_f = ValueAgent(
        name="Mover_f",
        states=frozenset({0, 1, 2}),
        actions=lambda s: frozenset({"forward", "stay"}) if s < 2 else frozenset(),
        transition=lambda s, a: (s + 1 if a == "forward" else s),
        output_fn=lambda s, a, ns: f"f: {s} --{a}--> {ns}",
        constitution=constitution,
        gamma=0.9,
    )

    # Agent g: continues from state 1 to 2
    agent_g = ValueAgent(
        name="Mover_g",
        states=frozenset({1, 2, 3}),
        actions=lambda s: frozenset({"forward", "stay"}) if s < 3 else frozenset(),
        transition=lambda s, a: (s + 1 if a == "forward" else s),
        output_fn=lambda s, a, ns: f"g: {s} --{a}--> {ns}",
        constitution=constitution,
        gamma=0.9,
    )

    print("Individual Agent Values:")
    print("-" * 80)

    # Compute value for agent f alone
    trace_f = agent_f.value(0)
    print(f"V_f(0) = {trace_f.total_value():.4f}")
    print(f"  Policy from 0: {agent_f.policy(0)}")
    print()

    # Compute value for agent g at state 1
    trace_g = agent_g.value(1)
    print(f"V_g(1) = {trace_g.total_value():.4f}")
    print(f"  Policy from 1: {agent_g.policy(1)}")
    print()

    print("=" * 80)
    print("Sequential Composition: f >> g")
    print("-" * 80)

    # Compose agents
    composed = agent_f >> agent_g

    print(f"Composed agent name: {composed.name}")
    print(f"Composed state space: {composed.states}")
    print()

    # Compute composed value
    trace_composed = composed.value(0)
    print(f"V_{{f >> g}}(0) = {trace_composed.total_value():.4f}")
    print(f"  Policy from 0: {composed.policy(0)}")
    print()

    # The key insight: composed value should be higher than f alone
    # because it includes g's future value
    print("Analysis:")
    print("-" * 80)
    print(f"V_f(0)          = {trace_f.total_value():.4f}")
    print(f"V_{{f >> g}}(0) = {trace_composed.total_value():.4f}")
    print()

    if trace_composed.total_value() > trace_f.total_value():
        improvement = trace_composed.total_value() - trace_f.total_value()
        print(f"✓ Composition adds value: +{improvement:.4f}")
        print(f"  This is because g provides continuation value from f's next state")
    else:
        print("✗ Composition did not increase value")

    print()
    print("=" * 80)
    print("Chaining Multiple Compositions: f >> g >> h")
    print("-" * 80)

    # Create a third agent
    agent_h = ValueAgent(
        name="Mover_h",
        states=frozenset({2, 3, 4}),
        actions=lambda s: frozenset({"forward", "stay"}) if s < 4 else frozenset(),
        transition=lambda s, a: (s + 1 if a == "forward" else s),
        output_fn=lambda s, a, ns: f"h: {s} --{a}--> {ns}",
        constitution=constitution,
        gamma=0.9,
    )

    # Chain composition
    triple_composed = agent_f >> agent_g >> agent_h

    print(f"Triple composition name: {triple_composed.name}")
    trace_triple = triple_composed.value(0)
    print(f"V_{{(f >> g) >> h}}(0) = {trace_triple.total_value():.4f}")
    print()

    print("Comparison:")
    print(f"  V_f(0)                = {trace_f.total_value():.4f}")
    print(f"  V_{{f >> g}}(0)        = {trace_composed.total_value():.4f}")
    print(f"  V_{{(f >> g) >> h}}(0) = {trace_triple.total_value():.4f}")
    print()

    if trace_triple.total_value() > trace_composed.total_value():
        print("✓ Each composition in the chain adds more future value")
    else:
        print("  (Note: h may not add value if state 2 not in h's reachable states)")

    print()
    print("=" * 80)


if __name__ == "__main__":
    main()
