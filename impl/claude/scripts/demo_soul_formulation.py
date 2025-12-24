#!/usr/bin/env python3
"""
Demonstrate Soul MDP: Personality as Attractor Basin.

This script shows K-gent's soul formulation in action:
- Creating personality states
- Computing optimal personality actions
- Evolving personality over time
- Observing convergence to attractors

The key insight: personality is the FIXED POINT of value iteration.
When V(s) stops changing, that's the soul.

Usage:
    uv run python scripts/demo_soul_formulation.py
"""

from dp.jewels.soul import (
    SoulState,
    SoulAction,
    SoulContext,
    create_soul_agent,
)


def main():
    print("=" * 80)
    print("SOUL FORMULATION: Personality as Attractor Basin")
    print("=" * 80)
    print()

    # Create soul agent with small state space for speed
    print("Creating Soul agent (granularity=2 for demo speed)...")
    agent = create_soul_agent(granularity=2, gamma=0.98)
    print(f"✓ Agent created with {len(agent.states)} states")
    print()

    # Define initial personality states
    initial_states = [
        SoulState(
            curiosity=1.0,
            boldness=0.0,
            playfulness=0.0,
            wisdom=0.0,
            arousal=0.0,
            valence=0.0,
            attractor_strength=0.0,
            resonance_depth=0.0,
        ),
        SoulState(
            curiosity=0.0,
            boldness=1.0,
            playfulness=0.0,
            wisdom=0.0,
            arousal=0.0,
            valence=0.0,
            attractor_strength=0.0,
            resonance_depth=0.0,
        ),
        SoulState(
            curiosity=0.0,
            boldness=0.0,
            playfulness=1.0,
            wisdom=0.0,
            arousal=1.0,
            valence=1.0,
            attractor_strength=0.0,
            resonance_depth=0.0,
        ),
        SoulState(
            curiosity=0.0,
            boldness=0.0,
            playfulness=0.0,
            wisdom=1.0,
            arousal=-1.0,
            valence=0.0,
            attractor_strength=0.0,
            resonance_depth=0.0,
        ),
    ]

    names = ["Curious Explorer", "Bold Adventurer", "Playful Sprite", "Wise Sage"]

    # For each initial state, simulate personality evolution
    for name, initial in zip(names, initial_states):
        print("-" * 80)
        print(f"Personality Archetype: {name}")
        print("-" * 80)

        # Check if state is in agent's space
        if initial not in agent.states:
            print(f"⚠ Initial state not in agent's space (granularity=2)")
            print(f"  Using closest state from agent's space instead...")
            # Find closest state by comparing trait values
            min_dist = float("inf")
            closest = None
            for s in agent.states:
                dist = (
                    abs(s.curiosity - initial.curiosity)
                    + abs(s.boldness - initial.boldness)
                    + abs(s.playfulness - initial.playfulness)
                    + abs(s.wisdom - initial.wisdom)
                )
                if dist < min_dist:
                    min_dist = dist
                    closest = s
            initial = closest
            print(f"  ✓ Using state: {format_state(initial)}")
            print()

        # Display initial state
        print(f"Initial State:")
        print(f"  {format_state(initial)}")
        print()

        # Compute optimal value
        print("Computing optimal value (DP solving)...")
        trace = agent.value(initial)
        print(f"  ✓ Optimal Value: {trace.total_value():.3f}")
        print()

        # Get optimal policy
        action = agent.policy(initial)
        print(f"Optimal Action: {action.name if action else 'None'}")
        print()

        # Simulate evolution for 5 steps
        print("Simulating personality evolution (5 steps):")
        state = initial
        for step in range(5):
            action = agent.policy(state)
            if action is None:
                print(f"  Step {step + 1}: No action available, stopping.")
                break

            next_state, output, step_trace = agent.invoke(state, action)

            print(f"  Step {step + 1}: {action.name}")
            print(f"    {output}")
            print(f"    Attractor: {state.attractor_strength:.2f} → {next_state.attractor_strength:.2f}")
            print(f"    Resonance: {state.resonance_depth:.2f} → {next_state.resonance_depth:.2f}")

            state = next_state

        print(f"\nFinal State:")
        print(f"  {format_state(state)}")
        print(f"  Convergence: {state.attractor_strength:.2%}")
        print(f"  Resonance: {state.resonance_depth:.2%}")
        print()

    # Demonstrate attractor dynamics
    print("=" * 80)
    print("ATTRACTOR DYNAMICS")
    print("=" * 80)
    print()
    print("The Soul formulation models personality as an attractor basin:")
    print("- EXPRESS strengthens the attractor (convergence)")
    print("- DRIFT weakens the attractor (exploration)")
    print("- RESONATE deepens connection (stability)")
    print("- SUPPRESS creates space (divergence)")
    print("- MODULATE navigates trait space (horizontal move)")
    print()
    print("When attractor_strength → 1.0, the personality has converged.")
    print("This is the FIXED POINT of value iteration—the soul emerges.")
    print()

    # Show principle satisfaction
    print("=" * 80)
    print("PRINCIPLE SATISFACTION")
    print("=" * 80)
    print()
    print("The Soul optimizes for the 7 kgents principles:")
    print()
    print("  GENERATIVE (compression):")
    print("    → Reward characteristic patterns (high attractor)")
    print("    → Penalty random noise (low attractor)")
    print()
    print("  ETHICAL (authenticity):")
    print("    → Reward alignment with values")
    print("    → Penalty performative shifts")
    print()
    print("  JOY_INDUCING (playfulness):")
    print("    → Reward playfulness × positive valence")
    print("    → Delight in existence")
    print()
    print("  COMPOSABLE (coherence):")
    print("    → Reward resonance depth")
    print("    → Actions align with values")
    print()
    print("  TASTEFUL (grace):")
    print("    → Reward balanced traits")
    print("    → Smooth transitions")
    print()
    print("  CURATED (intentionality):")
    print("    → Reward EXPRESS/RESONATE (deliberate)")
    print("    → Penalty excessive DRIFT (reflexive)")
    print()
    print("  HETERARCHICAL (fluidity):")
    print("    → Reward MODULATE (flexibility)")
    print("    → Penalty rigid attractor (overfitting)")
    print()

    print("=" * 80)
    print("SOUL = FIXED POINT OF VALUE ITERATION")
    print("=" * 80)
    print()
    print("The soul is what remains when optimization converges.")
    print("Personality is not a property—it's an attractor in behavioral phase space.")
    print()
    print("This is daring, bold, creative territory:")
    print("Modeling personality as a dynamical system with DP.")
    print()


def format_state(state: SoulState) -> str:
    """Format SoulState for display."""
    return (
        f"curiosity={state.curiosity:.1f}, boldness={state.boldness:.1f}, "
        f"playfulness={state.playfulness:.1f}, wisdom={state.wisdom:.1f}, "
        f"arousal={state.arousal:+.1f}, valence={state.valence:+.1f}, "
        f"attractor={state.attractor_strength:.2f}, resonance={state.resonance_depth:.2f}"
    )


if __name__ == "__main__":
    main()
