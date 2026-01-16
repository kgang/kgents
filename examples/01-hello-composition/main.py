"""
Example 01: Hello Composition
=============================

DEMONSTRATES: How two polynomial agents compose with >> operator.

kgents is built on category theory. The fundamental insight is that agents
are morphisms (arrows) in a category, and they compose like functions.

KEY CONCEPTS:
- PolyAgent: A state machine with mode-dependent inputs/outputs
- Sequential composition (>>): Output of left feeds into input of right
- Category laws: Identity and associativity must hold

RUN: cd impl/claude && uv run python ../../examples/01-hello-composition/main.py
"""

import sys
from pathlib import Path

# Add impl/claude to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "impl" / "claude"))

from agents.poly import from_function, identity, sequential


def main() -> None:
    # Create two simple agents from pure functions
    double = from_function("Double", lambda x: x * 2)
    add_one = from_function("AddOne", lambda x: x + 1)

    # Compose them: double >> add_one means "double first, then add one"
    composed = sequential(double, add_one)

    # Test the composition
    initial_state = ("ready", "ready")
    new_state, result = composed.invoke(initial_state, 5)
    print(f"double(5) >> add_one = {result}")  # Should be 11 (5*2 + 1)

    # === Verify Category Laws ===

    # Law 1: Identity - composing with identity changes nothing
    id_agent = identity("Id")
    left_id = sequential(id_agent, double)
    right_id = sequential(double, id_agent)

    _, result_left = left_id.invoke(("ready", "ready"), 7)
    _, result_right = right_id.invoke(("ready", "ready"), 7)
    _, result_bare = double.invoke("ready", 7)

    identity_law = result_left == result_right == result_bare
    print(f"Identity law: Id >> f == f == f >> Id? {identity_law}")

    # Law 2: Associativity - grouping doesn't matter
    triple = from_function("Triple", lambda x: x * 3)

    # (double >> add_one) >> triple
    left_grouped = sequential(sequential(double, add_one), triple)
    # double >> (add_one >> triple)
    right_grouped = sequential(double, sequential(add_one, triple))

    state_l = (("ready", "ready"), "ready")
    state_r = ("ready", ("ready", "ready"))

    _, result_l = left_grouped.invoke(state_l, 2)
    _, result_r = right_grouped.invoke(state_r, 2)

    associativity_law = result_l == result_r
    print(f"Associativity law: (f >> g) >> h == f >> (g >> h)? {associativity_law}")

    # Final verification
    if identity_law and associativity_law:
        print("\nComposition verified!")
    else:
        print("\nComposition laws FAILED!")
        sys.exit(1)


if __name__ == "__main__":
    main()
