#!/usr/bin/env python3
"""
Operad Laws: Composition Has Rules

An operad isn't just operations—it's operations WITH LAWS.
The laws aren't aspirational; they're verified at runtime.

    "An operad O defines a theory or grammar of composition."
    — Spivak et al.

Run: python docs/examples/operad_laws.py
"""

import sys

sys.path.insert(0, "impl/claude")

from agents.operad.core import AGENT_OPERAD, LawStatus
from agents.poly import from_function

# Create test agents
double = from_function("double", lambda x: x * 2)
add_one = from_function("+1", lambda x: x + 1)
square = from_function("square", lambda x: x**2)

print("The Agent Operad")
print("=" * 40)
print(f"Name: {AGENT_OPERAD.name}")
print(f"Operations: {', '.join(AGENT_OPERAD.operations.keys())}")
print()

# Verify all laws
print("Law Verification:")
results = AGENT_OPERAD.verify_all_laws(double, add_one, square)

for result in results:
    status = "PASS" if result.passed else "FAIL"
    print(f"  [{status}] {result.law_name}: {result.message}")

print()
print("Operations Demonstrated:")

# Show the operations working
composed = AGENT_OPERAD.compose("seq", double, add_one)
init = next(iter(composed.positions))
_, out = composed.invoke(init, 5)
print(f"  seq(double, +1)(5) = {out}")  # (5*2)+1 = 11

par = AGENT_OPERAD.compose("par", double, add_one)
init = next(iter(par.positions))
_, out = par.invoke(init, 5)
print(f"  par(double, +1)(5) = {out}")  # (10, 6)
