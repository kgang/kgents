#!/usr/bin/env python3
"""
Demonstration of PolicyTrace ↔ Mark bridge.

Shows how DP traces can be witnessed as marks and vice versa.

Usage:
    uv run python dp/witness/demo_bridge.py
"""

from datetime import datetime, timezone

from dp.witness.bridge import (
    mark_to_trace_entry,
    policy_trace_to_marks,
    trace_entry_to_mark,
)
from services.categorical.dp_bridge import PolicyTrace, TraceEntry


def main():
    print("=" * 70)
    print("PolicyTrace ↔ Mark Bridge Demonstration")
    print("=" * 70)
    print()

    # =========================================================================
    # Example 1: Single TraceEntry → Mark
    # =========================================================================
    print("📊 Example 1: Converting a single TraceEntry to Mark")
    print("-" * 70)

    entry = TraceEntry(
        state_before="planning",
        action="design_api",
        state_after="implementing",
        value=0.85,
        rationale="API design follows REST principles and satisfies COMPOSABLE principle",
        timestamp=datetime(2025, 12, 24, 14, 30, 0, tzinfo=timezone.utc),
    )

    print("TraceEntry:")
    print(f"  State: {entry.state_before} → {entry.state_after}")
    print(f"  Action: {entry.action}")
    print(f"  Value: {entry.value}")
    print(f"  Rationale: {entry.rationale}")
    print()

    mark_dict = trace_entry_to_mark(entry, origin="design_session")

    print("Converted to Mark:")
    print(f"  Origin: {mark_dict['origin']}")
    print(f"  Stimulus: {mark_dict['stimulus']['content']}")
    print(f"  Response: {mark_dict['response']['content']}")
    print(f"  Proof qualifier: {mark_dict['proof']['qualifier']}")
    print(f"  Proof warrant: {mark_dict['proof']['warrant']}")
    print(f"  Tags: {', '.join(mark_dict['tags'])}")
    print()

    # =========================================================================
    # Example 2: PolicyTrace → Marks
    # =========================================================================
    print("📊 Example 2: Converting a PolicyTrace to multiple Marks")
    print("-" * 70)

    # Simulate a DP solution for a simple problem
    entries = [
        TraceEntry(
            state_before="problem_identified",
            action="analyze_requirements",
            state_after="requirements_clear",
            value=0.9,
            rationale="Requirements match user needs (TASTEFUL principle)",
        ),
        TraceEntry(
            state_before="requirements_clear",
            action="choose_architecture",
            state_after="architecture_decided",
            value=0.75,
            rationale="Architecture enables composition (COMPOSABLE principle)",
        ),
        TraceEntry(
            state_before="architecture_decided",
            action="implement_solution",
            state_after="solution_complete",
            value=0.8,
            rationale="Implementation is minimal and elegant (GENERATIVE principle)",
        ),
    ]

    trace = PolicyTrace(value="solution_complete", log=tuple(entries))

    print(f"PolicyTrace with {len(trace.log)} steps:")
    for i, entry in enumerate(trace.log, 1):
        print(f"  Step {i}: {entry.action} (value={entry.value:.2f})")
    print()

    marks = policy_trace_to_marks(trace, origin="solution_session")

    print(f"Converted to {len(marks)} Marks:")
    for i, mark in enumerate(marks, 1):
        action = mark["response"]["metadata"]["action"]
        qualifier = mark["proof"]["qualifier"]
        print(f"  Mark {i}: {action} ({qualifier})")
    print()

    # =========================================================================
    # Example 3: Round-trip conversion
    # =========================================================================
    print("📊 Example 3: Round-trip conversion (Mark → TraceEntry → Mark)")
    print("-" * 70)

    original_mark = marks[0]  # Use first mark from previous example
    print("Original Mark:")
    print(f"  Action: {original_mark['response']['metadata']['action']}")
    print(f"  Value: {original_mark['response']['metadata']['value']}")
    print()

    # Convert to TraceEntry
    recovered_entry = mark_to_trace_entry(original_mark)
    print("Recovered TraceEntry:")
    print(f"  Action: {recovered_entry.action}")
    print(f"  Value: {recovered_entry.value}")
    print(f"  State: {recovered_entry.state_before} → {recovered_entry.state_after}")
    print()

    # Convert back to Mark
    round_trip_mark = trace_entry_to_mark(recovered_entry)
    print("Round-trip Mark:")
    print(f"  Action: {round_trip_mark['response']['metadata']['action']}")
    print(f"  Value: {round_trip_mark['response']['metadata']['value']}")
    print()

    # Verify equivalence
    action_match = (
        original_mark["response"]["metadata"]["action"]
        == round_trip_mark["response"]["metadata"]["action"]
    )
    value_match = (
        original_mark["response"]["metadata"]["value"]
        == round_trip_mark["response"]["metadata"]["value"]
    )

    print(f"✓ Round-trip successful: action={action_match}, value={value_match}")
    print()

    # =========================================================================
    # Summary
    # =========================================================================
    print("=" * 70)
    print("Summary")
    print("=" * 70)
    print()
    print("The bridge enables:")
    print("  1. DP traces to be witnessed and stored as Marks")
    print("  2. Marks to be reconstructed as DP traces for analysis")
    print("  3. Queries like 'Show me all decisions that scored high on Tasteful'")
    print("  4. Lineage tracking: 'What policy led to this outcome?'")
    print()
    print("The proof IS the decision. The mark IS the witness.")
    print()


if __name__ == "__main__":
    main()
