#!/usr/bin/env python3
"""
Composition: Agents as Morphisms

The key insight: Agent[A, B] isn't just a function—it's a dynamical system.
Composition isn't just piping; it's building wiring diagrams.

    "The noun is a lie. There is only the rate of change."

Run: python docs/examples/composition.py
"""

import sys

sys.path.insert(0, "impl/claude")

from agents.poly import from_function, sequential

# Lift pure functions to polynomial agents
double = from_function("double", lambda x: x * 2)
add_one = from_function("add_one", lambda x: x + 1)
square = from_function("square", lambda x: x**2)

# Compose: (x * 2) + 1
pipeline = sequential(double, add_one)

# Run through the pipeline
state, outputs = pipeline.run(
    initial=("ready", "ready"),  # Product of states
    inputs=[5, 10, 0],
)

print("Pipeline: double >> add_one")
print(f"  5 -> {outputs[0]}")  # 5*2+1 = 11
print(f" 10 -> {outputs[1]}")  # 10*2+1 = 21
print(f"  0 -> {outputs[2]}")  # 0*2+1 = 1

# Composition is associative: (a >> b) >> c = a >> (b >> c)
left = sequential(sequential(double, add_one), square)
right = sequential(double, sequential(add_one, square))

# Get initial states from the composed agent's positions
left_init = next(iter(left.positions))
right_init = next(iter(right.positions))

# Both give same result
_, [left_out] = left.run(left_init, [3])
_, [right_out] = right.run(right_init, [3])

print("\nAssociativity: (double >> add_one) >> square = double >> (add_one >> square)")
print(f"  3 -> {left_out} = {right_out}  {'OK' if left_out == right_out else 'FAIL'}")
