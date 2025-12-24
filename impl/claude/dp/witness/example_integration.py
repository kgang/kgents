#!/usr/bin/env python3
"""
Integration example: Using DP solver with Witness bridge.

This example shows how PolicyTrace from DP solving can be converted to
Witness marks for persistence and analysis.

Usage:
    uv run python dp/witness/example_integration.py
"""

from typing import FrozenSet

from dp.witness.bridge import policy_trace_to_marks
from services.categorical.dp_bridge import (
    DPAction,
    DPSolver,
    Principle,
    PrincipleScore,
    ProblemFormulation,
    ValueFunction,
    ValueScore,
)


def main():
    print("=" * 70)
    print("DP Solver + Witness Bridge Integration Example")
    print("=" * 70)
    print()

    # =========================================================================
    # Define a simple problem: Building a feature
    # =========================================================================
    print("1. Defining the problem: Building a new feature")
    print("-" * 70)

    # States: different stages of feature development
    states = frozenset(
        [
            "start",
            "planned",
            "designed",
            "implemented",
            "tested",
            "documented",
            "done",
        ]
    )

    # Actions: development steps
    def available_actions(state: str) -> FrozenSet[DPAction]:
        """Define what actions are available from each state."""
        transitions = {
            "start": [DPAction("plan", "compose")],
            "planned": [DPAction("design", "compose"), DPAction("skip_design", "compose")],
            "designed": [DPAction("implement", "compose")],
            "implemented": [
                DPAction("write_tests", "compose"),
                DPAction("skip_tests", "compose"),
            ],
            "tested": [
                DPAction("write_docs", "compose"),
                DPAction("skip_docs", "compose"),
            ],
            "documented": [DPAction("finish", "compose")],
        }
        return frozenset(transitions.get(state, []))

    # Transition function: where each action leads
    def transition(state: str, action: DPAction) -> str:
        """Define state transitions."""
        transitions = {
            ("start", "plan"): "planned",
            ("planned", "design"): "designed",
            ("planned", "skip_design"): "implemented",
            ("designed", "implement"): "implemented",
            ("implemented", "write_tests"): "tested",
            ("implemented", "skip_tests"): "documented",
            ("tested", "write_docs"): "documented",
            ("tested", "skip_docs"): "documented",
            ("documented", "finish"): "done",
        }
        return transitions.get((state, action.name), state)

    # Reward function: based on kgents principles
    def reward(state: str, action: DPAction, next_state: str) -> float:
        """Assign rewards based on principle satisfaction."""
        # Higher rewards for actions that satisfy principles
        rewards = {
            "plan": 1.0,  # TASTEFUL: clear purpose
            "design": 1.0,  # GENERATIVE: thoughtful design
            "skip_design": -0.5,  # Violates TASTEFUL
            "implement": 1.0,  # Core work
            "write_tests": 1.5,  # ETHICAL: ensures correctness
            "skip_tests": -1.0,  # Violates ETHICAL
            "write_docs": 1.0,  # JOY_INDUCING: makes it learnable
            "skip_docs": -0.3,  # Reduces joy
            "finish": 0.5,  # Completion
        }
        return rewards.get(action.name, 0.0)

    # Create the problem formulation
    formulation: ProblemFormulation[str, DPAction] = ProblemFormulation(
        name="feature_development",
        description="Optimal path for building a new feature",
        state_type=str,
        initial_states=frozenset(["start"]),
        goal_states=frozenset(["done"]),
        available_actions=available_actions,
        transition=transition,
        reward=reward,
    )

    print(f"Problem: {formulation.name}")
    print(f"States: {len(states)}")
    print(f"Initial: {list(formulation.initial_states)}")
    print(f"Goal: {list(formulation.goal_states)}")
    print()

    # =========================================================================
    # Solve using DP
    # =========================================================================
    print("2. Solving with Dynamic Programming")
    print("-" * 70)

    solver: DPSolver[str, DPAction] = DPSolver(
        formulation=formulation,
        gamma=1.0,  # No discounting for clarity
        max_depth=10,
    )

    value, trace = solver.solve()

    print(f"Optimal value: {value:.2f}")
    print(f"Solution trace ({len(trace.log)} steps):")
    for i, entry in enumerate(trace.log, 1):
        print(f"  {i}. {entry.action}")
        print(f"     {entry.state_before} → {entry.state_after}")
        print(f"     Rationale: {entry.rationale}")
    print()

    # =========================================================================
    # Convert to Witness marks
    # =========================================================================
    print("3. Converting PolicyTrace to Witness Marks")
    print("-" * 70)

    marks = policy_trace_to_marks(trace, origin="feature_dev_session")

    print(f"Generated {len(marks)} Witness marks:")
    for i, mark in enumerate(marks, 1):
        action = mark["response"]["metadata"]["action"]
        qualifier = mark["proof"]["qualifier"]
        warrant = mark["proof"]["warrant"]
        print(f"\nMark {i}:")
        print(f"  Action: {action}")
        print(f"  Confidence: {qualifier}")
        print(f"  Reasoning: {warrant}")
    print()

    # =========================================================================
    # Summary
    # =========================================================================
    print("=" * 70)
    print("Summary")
    print("=" * 70)
    print()
    print("✓ DP solver found optimal policy")
    print("✓ Policy trace converted to Witness marks")
    print("✓ Marks can now be:")
    print("  - Persisted in MarkStore")
    print("  - Queried by principle satisfaction")
    print("  - Analyzed for decision patterns")
    print("  - Linked to future decisions (causal chains)")
    print()
    print("The proof IS the decision. The mark IS the witness.")
    print()


if __name__ == "__main__":
    main()
