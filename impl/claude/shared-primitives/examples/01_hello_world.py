#!/usr/bin/env python3
"""
kgents-foundation: Hello World

The simplest possible example. Copy-paste this and it works.
Time to understand: < 1 minute.

This is THE canonical way to create agents in kgents.
All future kgents development builds on this foundation.
"""

from kgents_poly import PolyAgent, from_function

# Create an agent from any function
double: PolyAgent[str, int, int] = from_function("double", lambda x: x * 2)

# Run it
state, result = double.invoke("ready", 21)
print(f"Result: {result}")  # Result: 42

# That's it. You've created your first agent.
