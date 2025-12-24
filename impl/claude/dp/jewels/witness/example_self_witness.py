"""
Example: The Witness Witnesses Itself.

This demonstrates the delightful self-referential property of the Witness
formulation: every decision the Witness makes about what to mark is itself
recorded in the PolicyTrace.

The Witness witnesses its own witnessing, creating an infinite regress that
bottoms out in the PolicyTrace monad.

Run:
    uv run python -m dp.jewels.witness.example_self_witness

Expected Output:
    The Witness agent makes optimal decisions about when to mark, skip, or
    crystallize events. Each decision is recorded in the trace, which IS the
    witness of the witnessing process.
"""

from dp.jewels.witness import (
    WitnessAction,
    WitnessContext,
    WitnessState,
    create_witness_agent,
)


def demonstrate_self_witnessing():
    """
    Show the Witness witnessing itself via PolicyTrace.

    Scenario:
        1. Start in IDLE state
        2. Observe several events of varying significance
        3. Make optimal decisions about marking/skipping
        4. Crystallize when enough marks exist
        5. Examine the PolicyTrace: it contains the witness of all decisions
    """
    print("=" * 70)
    print("THE WITNESS WITNESSES ITSELF")
    print("=" * 70)
    print()

    # Create the Witness agent
    print("Creating Witness agent with optimal tracing policy...")
    agent = create_witness_agent(gamma=0.95)
    print(f"  Agent: {agent}")
    print()

    # Scenario: observe three events of varying significance
    events = [
        ("Low-significance event", 0.2),
        ("Medium-significance event", 0.5),
        ("High-significance event", 0.9),
    ]

    print("Simulating event stream...")
    print()

    # Start from IDLE
    state = WitnessState.IDLE
    all_trace_entries = []

    for event_name, significance in events:
        print(f"Event: {event_name} (significance={significance:.1f})")

        # Update context with event significance
        context = WitnessContext(
            event_significance=significance,
            mark_count=len(all_trace_entries),
            insight_density=0.7,
            trace_coherence=0.8,
        )

        # Recreate agent with updated context
        agent = create_witness_agent(context=context, gamma=0.95)

        # Get optimal action from current state
        if state == WitnessState.IDLE:
            # From IDLE, must OBSERVE first
            action = WitnessAction.OBSERVE
        else:
            action = agent.policy(state)

        print(f"  State: {state.name}")
        print(f"  Optimal action: {action.name if action else 'None'}")

        if action is None:
            print("  (No valid actions from this state)")
            print()
            continue

        # Execute the action
        next_state, output, trace = agent.invoke(state, action)
        all_trace_entries.extend(trace.log)

        print(f"  Output: {output}")
        print(f"  Next state: {next_state.name}")
        print(f"  Trace entries added: {len(trace.log)}")
        print()

        state = next_state

    # Summary: examine the full trace
    print("=" * 70)
    print("WITNESSING THE WITNESS")
    print("=" * 70)
    print()
    print(f"Total trace entries: {len(all_trace_entries)}")
    print()
    print("Each entry is a WITNESS of a witnessing decision:")
    print()

    for i, entry in enumerate(all_trace_entries, 1):
        print(f"  {i}. {entry.summary}")
        print(f"     Rationale: {entry.rationale}")
        print()

    print("=" * 70)
    print("SELF-REFERENTIAL INSIGHT")
    print("=" * 70)
    print()
    print("The PolicyTrace IS the proof of optimality.")
    print("Every decision the Witness made is recorded in the trace.")
    print("The Witness has witnessed itself witnessing.")
    print()
    print("This is the core of the DP-native approach:")
    print("  - The decision process (DP) generates the witness (PolicyTrace)")
    print("  - The witness records the decision process")
    print("  - Infinite regress bottoms out in the monad")
    print()


def demonstrate_optimal_policy():
    """
    Show what the optimal policy looks like for different contexts.

    This illustrates how the DP solution adapts to context:
    - High significance events → MARK
    - Low significance events → SKIP
    - Many marks accumulated → CRYSTALLIZE
    """
    print("=" * 70)
    print("OPTIMAL POLICY ACROSS CONTEXTS")
    print("=" * 70)
    print()

    contexts = [
        ("Low significance, few marks", WitnessContext(event_significance=0.2, mark_count=2)),
        ("High significance, few marks", WitnessContext(event_significance=0.9, mark_count=2)),
        ("Medium significance, many marks", WitnessContext(event_significance=0.5, mark_count=25)),
        ("High significance, medium marks", WitnessContext(event_significance=0.9, mark_count=10)),
    ]

    for context_name, context in contexts:
        agent = create_witness_agent(context=context)
        action = agent.policy(WitnessState.OBSERVING)

        print(f"Context: {context_name}")
        print(f"  Event significance: {context.event_significance:.1f}")
        print(f"  Mark count: {context.mark_count}")
        print(f"  Optimal action: {action.name if action else 'None'}")
        print()

    print("=" * 70)
    print()


def demonstrate_value_function():
    """
    Show the value function for different states.

    The value V(s) tells us: "What's the expected long-term principle
    satisfaction from state s?"
    """
    print("=" * 70)
    print("VALUE FUNCTION")
    print("=" * 70)
    print()

    agent = create_witness_agent()

    print("Computing optimal values for each state...")
    print()

    for state in WitnessState:
        trace = agent.value(state)
        value = trace.total_value()

        print(f"State: {state.name:15s} → Value: {value:6.3f}")

    print()
    print("Interpretation:")
    print("  Higher value = better long-term principle satisfaction from this state")
    print("  The optimal policy maximizes value across all states")
    print()
    print("=" * 70)
    print()


if __name__ == "__main__":
    demonstrate_self_witnessing()
    print("\n\n")
    demonstrate_optimal_policy()
    print("\n\n")
    demonstrate_value_function()
