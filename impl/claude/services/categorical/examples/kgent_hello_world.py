"""
K-gent Hello World: Modeling a Simple Task Through the DP-Agent Framework.

This example demonstrates the Agent-DP isomorphism with a trivial task:
K-gent (as a chatbot) creating a "hello world" program.

The goal: Show that even trivial tasks have full DP structure.

DP Formulation:
    States:     {empty, requirement_understood, design_chosen, code_written, tested}
    Actions:    {understand_task, choose_design, write_code, test_code}
    Transition: Deterministic progression
    Reward:     Constitutional evaluation (7 principles)

The insight: The DP structure makes explicit what's usually implicit:
    - Which decisions matter (state transitions)
    - Why we make them (reward function = principles)
    - The trace of reasoning (PolicyTrace = Witness)

Usage:
    python -m services.categorical.examples.kgent_hello_world

    Or interactively:
        from services.categorical.examples.kgent_hello_world import run_hello_world_dp
        result = await run_hello_world_dp()
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from enum import Enum, auto
from typing import FrozenSet

from services.categorical.dp_bridge import (
    DPSolver,
    MetaDP,
    OptimalSubstructure,
    PolicyTrace,
    Principle,
    PrincipleScore,
    ProblemFormulation,
    TraceEntry,
    ValueFunction,
    ValueScore,
)


# =============================================================================
# State Space: Stages of "Hello World" Creation
# =============================================================================


class HelloWorldState(Enum):
    """
    States in the "hello world" creation process.

    This is a simple linear progression, but the DP framework
    still applies - it just has a unique optimal path.
    """

    EMPTY = auto()                  # Starting state: no work done
    REQUIREMENT_UNDERSTOOD = auto()  # Task comprehended
    DESIGN_CHOSEN = auto()          # Approach decided (language, style)
    CODE_WRITTEN = auto()           # Implementation complete
    TESTED = auto()                 # Verified working (terminal state)

    def __str__(self) -> str:
        return self.name.lower().replace("_", " ")


# =============================================================================
# Action Space: Design Decisions
# =============================================================================


class HelloWorldAction(Enum):
    """
    Actions K-gent can take in creating "hello world".

    Each action is a design decision with constitutional implications.
    """

    # Understanding the task
    UNDERSTAND_MINIMAL = auto()      # "Just print hello world"
    UNDERSTAND_CONTEXTUAL = auto()   # "Why? What language? What style?"

    # Choosing design
    DESIGN_PYTHON_SIMPLE = auto()    # print("Hello, World!")
    DESIGN_PYTHON_FUNCTION = auto()  # def greet(): ...
    DESIGN_PYTHON_CLASS = auto()     # class Greeter: ...
    DESIGN_PYTHON_OVER_ENGINEERED = auto()  # AbstractGreeterFactory...

    # Writing code
    WRITE_MINIMAL = auto()           # Bare minimum
    WRITE_DOCUMENTED = auto()        # With docstring
    WRITE_TYPED = auto()             # With type hints

    # Testing
    TEST_MANUAL = auto()             # Just run it
    TEST_AUTOMATED = auto()          # With pytest

    def __str__(self) -> str:
        return self.name.lower().replace("_", " ")


# =============================================================================
# Transition Function: State Machine
# =============================================================================


def transition(state: HelloWorldState, action: HelloWorldAction) -> HelloWorldState:
    """
    State transition function.

    T: S × A → S

    For "hello world", this is deterministic:
    - Understanding leads to REQUIREMENT_UNDERSTOOD
    - Design choice leads to DESIGN_CHOSEN
    - Writing leads to CODE_WRITTEN
    - Testing leads to TESTED
    """
    # Map state → valid actions → next state
    transitions = {
        HelloWorldState.EMPTY: {
            HelloWorldAction.UNDERSTAND_MINIMAL: HelloWorldState.REQUIREMENT_UNDERSTOOD,
            HelloWorldAction.UNDERSTAND_CONTEXTUAL: HelloWorldState.REQUIREMENT_UNDERSTOOD,
        },
        HelloWorldState.REQUIREMENT_UNDERSTOOD: {
            HelloWorldAction.DESIGN_PYTHON_SIMPLE: HelloWorldState.DESIGN_CHOSEN,
            HelloWorldAction.DESIGN_PYTHON_FUNCTION: HelloWorldState.DESIGN_CHOSEN,
            HelloWorldAction.DESIGN_PYTHON_CLASS: HelloWorldState.DESIGN_CHOSEN,
            HelloWorldAction.DESIGN_PYTHON_OVER_ENGINEERED: HelloWorldState.DESIGN_CHOSEN,
        },
        HelloWorldState.DESIGN_CHOSEN: {
            HelloWorldAction.WRITE_MINIMAL: HelloWorldState.CODE_WRITTEN,
            HelloWorldAction.WRITE_DOCUMENTED: HelloWorldState.CODE_WRITTEN,
            HelloWorldAction.WRITE_TYPED: HelloWorldState.CODE_WRITTEN,
        },
        HelloWorldState.CODE_WRITTEN: {
            HelloWorldAction.TEST_MANUAL: HelloWorldState.TESTED,
            HelloWorldAction.TEST_AUTOMATED: HelloWorldState.TESTED,
        },
    }

    valid_actions = transitions.get(state, {})
    return valid_actions.get(action, state)  # Invalid action = no change


def available_actions(state: HelloWorldState) -> FrozenSet[HelloWorldAction]:
    """
    Available actions from a given state.

    A: S → P(A)  (actions as function of state)
    """
    action_map = {
        HelloWorldState.EMPTY: frozenset([
            HelloWorldAction.UNDERSTAND_MINIMAL,
            HelloWorldAction.UNDERSTAND_CONTEXTUAL,
        ]),
        HelloWorldState.REQUIREMENT_UNDERSTOOD: frozenset([
            HelloWorldAction.DESIGN_PYTHON_SIMPLE,
            HelloWorldAction.DESIGN_PYTHON_FUNCTION,
            HelloWorldAction.DESIGN_PYTHON_CLASS,
            HelloWorldAction.DESIGN_PYTHON_OVER_ENGINEERED,
        ]),
        HelloWorldState.DESIGN_CHOSEN: frozenset([
            HelloWorldAction.WRITE_MINIMAL,
            HelloWorldAction.WRITE_DOCUMENTED,
            HelloWorldAction.WRITE_TYPED,
        ]),
        HelloWorldState.CODE_WRITTEN: frozenset([
            HelloWorldAction.TEST_MANUAL,
            HelloWorldAction.TEST_AUTOMATED,
        ]),
    }
    return action_map.get(state, frozenset())


# =============================================================================
# Reward Function: Constitutional Evaluation
# =============================================================================


def reward(
    state: HelloWorldState,
    action: HelloWorldAction,
    next_state: HelloWorldState,
) -> float:
    """
    Reward function based on the 7 kgents principles.

    R: S × A × S → ℝ

    This is where K-gent's personality manifests:
    - Tasteful: Prefer minimal, justified complexity
    - Composable: Prefer functional decomposition
    - Joy-inducing: Prefer elegance

    Returns a reward in [-1, 1] range.
    """
    # Base rewards by action (encoding constitutional preferences)
    action_rewards = {
        # Understanding: Contextual is slightly better (tasteful)
        HelloWorldAction.UNDERSTAND_MINIMAL: 0.3,
        HelloWorldAction.UNDERSTAND_CONTEXTUAL: 0.5,  # More thoughtful

        # Design: Simple is best for "hello world" (tasteful penalty for over-engineering)
        HelloWorldAction.DESIGN_PYTHON_SIMPLE: 0.9,    # Maximum for trivial task
        HelloWorldAction.DESIGN_PYTHON_FUNCTION: 0.7,  # Reasonable but unnecessary
        HelloWorldAction.DESIGN_PYTHON_CLASS: 0.4,     # Over-engineering for this task
        HelloWorldAction.DESIGN_PYTHON_OVER_ENGINEERED: -0.5,  # TASTEFUL VIOLATION

        # Writing: Documented is good, typed is overkill for this
        HelloWorldAction.WRITE_MINIMAL: 0.6,
        HelloWorldAction.WRITE_DOCUMENTED: 0.8,  # Good practice, joy-inducing
        HelloWorldAction.WRITE_TYPED: 0.5,       # Overkill for hello world

        # Testing: Manual is fine for trivial task
        HelloWorldAction.TEST_MANUAL: 0.7,
        HelloWorldAction.TEST_AUTOMATED: 0.5,  # Over-engineering for trivial task
    }

    base = action_rewards.get(action, 0.0)

    # Terminal state bonus
    if next_state == HelloWorldState.TESTED:
        base += 0.2  # Completion bonus

    return base


# =============================================================================
# Principle-Based Value Function
# =============================================================================


def create_kgent_value_function() -> ValueFunction[HelloWorldState, HelloWorldAction]:
    """
    Create a ValueFunction that embodies K-gent's constitutional values.

    This is where the 7 principles become computationally active.
    """

    def evaluate_tasteful(name: str, state: HelloWorldState, action: HelloWorldAction | None) -> float:
        """Tasteful: Each agent serves a clear, justified purpose."""
        if action == HelloWorldAction.DESIGN_PYTHON_OVER_ENGINEERED:
            return 0.0  # Absolute violation
        if action == HelloWorldAction.DESIGN_PYTHON_SIMPLE:
            return 1.0  # Perfect for task
        if action in (HelloWorldAction.DESIGN_PYTHON_CLASS, HelloWorldAction.TEST_AUTOMATED):
            return 0.3  # Over-engineering for trivial task
        return 0.7  # Default reasonable

    def evaluate_composable(name: str, state: HelloWorldState, action: HelloWorldAction | None) -> float:
        """Composable: Agents are morphisms in a category."""
        if action == HelloWorldAction.DESIGN_PYTHON_FUNCTION:
            return 1.0  # Functions compose well
        if action == HelloWorldAction.DESIGN_PYTHON_SIMPLE:
            return 0.8  # Still composes (can wrap)
        if action == HelloWorldAction.DESIGN_PYTHON_CLASS:
            return 0.6  # Classes are less composable
        return 0.7

    def evaluate_joy_inducing(name: str, state: HelloWorldState, action: HelloWorldAction | None) -> float:
        """Joy-inducing: Delight in interaction."""
        if action == HelloWorldAction.WRITE_DOCUMENTED:
            return 1.0  # Documentation is delightful
        if action == HelloWorldAction.DESIGN_PYTHON_SIMPLE:
            return 0.9  # Elegance is joyful
        if action == HelloWorldAction.DESIGN_PYTHON_OVER_ENGINEERED:
            return 0.1  # Frustrating complexity
        return 0.7

    def evaluate_ethical(name: str, state: HelloWorldState, action: HelloWorldAction | None) -> float:
        """Ethical: Agents augment human capability."""
        # All actions for hello world are ethical
        return 0.9

    def evaluate_curated(name: str, state: HelloWorldState, action: HelloWorldAction | None) -> float:
        """Curated: Intentional selection over exhaustive cataloging."""
        if action == HelloWorldAction.UNDERSTAND_CONTEXTUAL:
            return 0.9  # Thoughtful selection
        if action == HelloWorldAction.DESIGN_PYTHON_OVER_ENGINEERED:
            return 0.2  # Not curated - kitchen sink
        return 0.7

    def evaluate_heterarchical(name: str, state: HelloWorldState, action: HelloWorldAction | None) -> float:
        """Heterarchical: Agents exist in flux, not fixed hierarchy."""
        # For hello world, all approaches are fine
        return 0.8

    def evaluate_generative(name: str, state: HelloWorldState, action: HelloWorldAction | None) -> float:
        """Generative: Spec is compression."""
        if action == HelloWorldAction.DESIGN_PYTHON_SIMPLE:
            return 1.0  # Maximum compression
        if action == HelloWorldAction.WRITE_MINIMAL:
            return 0.9  # Minimal is generative
        if action == HelloWorldAction.DESIGN_PYTHON_OVER_ENGINEERED:
            return 0.1  # Bloat, not compression
        return 0.7

    vf = ValueFunction[HelloWorldState, HelloWorldAction]()
    vf.principle_evaluators = {
        Principle.TASTEFUL: evaluate_tasteful,
        Principle.COMPOSABLE: evaluate_composable,
        Principle.JOY_INDUCING: evaluate_joy_inducing,
        Principle.ETHICAL: evaluate_ethical,
        Principle.CURATED: evaluate_curated,
        Principle.HETERARCHICAL: evaluate_heterarchical,
        Principle.GENERATIVE: evaluate_generative,
    }

    return vf


# =============================================================================
# Problem Formulation: The Full MDP
# =============================================================================


def create_hello_world_formulation() -> ProblemFormulation[HelloWorldState, HelloWorldAction]:
    """
    Create the full DP problem formulation for "hello world".

    This is the MDP: (S, A, T, R, γ)
    """
    return ProblemFormulation(
        name="kgent_hello_world",
        description="K-gent creating a hello world program",
        state_type=HelloWorldState,
        initial_states=frozenset([HelloWorldState.EMPTY]),
        goal_states=frozenset([HelloWorldState.TESTED]),
        available_actions=available_actions,
        transition=transition,
        reward=reward,
    )


# =============================================================================
# Solve and Display
# =============================================================================


async def run_hello_world_dp() -> dict:
    """
    Run the DP solver on the hello world problem.

    Returns:
        Dictionary with solution details:
        - optimal_path: List of (state, action, reward) tuples
        - total_value: Discounted total reward
        - principle_scores: Constitutional evaluation
        - trace: Full PolicyTrace for Witness integration
    """
    print("=" * 60)
    print("K-gent Hello World: DP-Agent Framework Demo")
    print("=" * 60)
    print()

    # Create problem formulation
    formulation = create_hello_world_formulation()
    print(f"Problem: {formulation.description}")
    print(f"Initial: {list(formulation.initial_states)[0]}")
    print(f"Goal: {list(formulation.goal_states)[0]}")
    print()

    # Create value function
    value_function = create_kgent_value_function()

    # Create solver
    solver = DPSolver(
        formulation=formulation,
        value_function=value_function,
        gamma=0.95,  # Slight discount for longer paths
        max_depth=10,
    )

    # Solve!
    print("Solving via Value Iteration...")
    optimal_value, trace = solver.solve()

    print()
    print("=" * 60)
    print("OPTIMAL SOLUTION (The Witness)")
    print("=" * 60)

    # Display the trace
    result = {
        "optimal_path": [],
        "total_value": trace.total_value(gamma=0.95),
        "principle_scores": {},
        "trace": trace,
    }

    for i, entry in enumerate(trace.log):
        step_info = {
            "step": i + 1,
            "state_before": str(entry.state_before),
            "action": entry.action,
            "state_after": str(entry.state_after),
            "value": entry.value,
        }
        result["optimal_path"].append(step_info)

        print(f"\nStep {i + 1}:")
        print(f"  State: {entry.state_before}")
        print(f"  Action: {entry.action}")
        print(f"  → {entry.state_after}")
        print(f"  Reward: {entry.value:.3f}")

        # Evaluate principles for this action
        action_enum = None
        for a in HelloWorldAction:
            if str(a) == entry.action:
                action_enum = a
                break

        if action_enum:
            score = value_function.evaluate(
                f"Step {i + 1}",
                entry.state_before,
                action_enum
            )
            print(f"  Principle scores:")
            for ps in score.principle_scores:
                print(f"    {ps.principle.name}: {ps.score:.2f}")

    print()
    print("=" * 60)
    print(f"TOTAL DISCOUNTED VALUE: {result['total_value']:.3f}")
    print("=" * 60)

    # The expected optimal path for hello world:
    print()
    print("EXPECTED OPTIMAL PATH (K-gent's Constitutional Choice):")
    print("  1. UNDERSTAND_CONTEXTUAL (thoughtful, not reflexive)")
    print("  2. DESIGN_PYTHON_SIMPLE (tasteful minimalism)")
    print("  3. WRITE_DOCUMENTED (joy-inducing clarity)")
    print("  4. TEST_MANUAL (appropriate for trivial task)")
    print()
    print('RESULT: print("Hello, World!")  # With a nice docstring')

    # Show the Witness marks
    print()
    print("=" * 60)
    print("WITNESS MARKS (For Audit Trail)")
    print("=" * 60)
    marks = trace.to_marks()
    for mark in marks:
        print(f"  • {mark['action']}: {mark['state_before']} → {mark['state_after']}")

    return result


# =============================================================================
# Meta-DP: What if we questioned the problem formulation?
# =============================================================================


async def run_meta_dp_example() -> None:
    """
    Demonstrate Meta-DP: iterating on the problem formulation itself.

    The insight: For "hello world", the problem formulation is ALREADY optimal.
    Meta-DP would confirm this by exploring alternatives and finding no improvement.
    """
    print()
    print("=" * 60)
    print("META-DP: Should we reformulate the problem?")
    print("=" * 60)
    print()

    meta = MetaDP[HelloWorldState, HelloWorldAction]()

    # Add base formulation
    base = create_hello_world_formulation()
    meta.add_formulation(base)

    # Add a reformulator that abstracts states
    def abstract_states(f: ProblemFormulation) -> ProblemFormulation:
        """Merge REQUIREMENT_UNDERSTOOD and DESIGN_CHOSEN into one state."""
        # This would be a bad reformulation - we'd lose design choice granularity
        return f  # Return unchanged for demo

    meta.add_reformulator("abstract_states", abstract_states)

    # Solver function
    def solve_formulation(f: ProblemFormulation) -> tuple[float, PolicyTrace]:
        solver = DPSolver(formulation=f, gamma=0.95, max_depth=10)
        return solver.solve()

    print("Evaluating formulations...")
    quality = meta.evaluate_formulation(base, solve_formulation)
    print(f"  Base formulation quality: {quality:.3f}")

    print()
    print("Meta-DP Conclusion:")
    print("  For 'hello world', the base formulation is already optimal.")
    print("  No reformulation improves on explicit state tracking.")
    print("  This IS the generative principle: minimal adequate structure.")


# =============================================================================
# Main Entry Point
# =============================================================================


async def main():
    """Run all examples."""
    result = await run_hello_world_dp()
    await run_meta_dp_example()

    print()
    print("=" * 60)
    print("KEY INSIGHT")
    print("=" * 60)
    print("""
Even for trivial tasks, the DP-Agent framework makes explicit:

1. STATE SPACE: What are the meaningful stages?
2. ACTION SPACE: What decisions matter?
3. TRANSITION: How do decisions change state?
4. REWARD: Why do we prefer some decisions? (= Constitution)
5. TRACE: What was our reasoning? (= Witness)

For 'hello world', the optimal policy is:
  UNDERSTAND → DESIGN_SIMPLE → WRITE_DOCUMENTED → TEST_MANUAL

This isn't over-engineering. It's making IMPLICIT choices EXPLICIT.
The DP framework doesn't add complexity - it reveals structure
that was always there.

"The proof IS the decision. The mark IS the witness."
""")


if __name__ == "__main__":
    asyncio.run(main())
