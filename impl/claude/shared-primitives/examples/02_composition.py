#!/usr/bin/env python3
"""
kgents-foundation: Composition

The key insight: Agents compose with >>
No glue code. No boilerplate. Just chain them.

Time to understand: < 3 minutes.

This is THE canonical way to compose agents in kgents.
All future kgents development uses this pattern.
"""

from typing import Any

from kgents_poly import PolyAgent, from_function, identity, parallel

# Create some agents
double: PolyAgent[str, int, int] = from_function("double", lambda x: x * 2)
add_one: PolyAgent[str, int, int] = from_function("add_one", lambda x: x + 1)
square: PolyAgent[str, int, int] = from_function("square", lambda x: x * x)

# =============================================================================
# SEQUENTIAL COMPOSITION: Output of first feeds into second
# =============================================================================

# The >> operator chains agents: output of left becomes input of right
pipeline = double >> add_one
_, result1 = pipeline.invoke(("ready", "ready"), 10)
print(f"Sequential: 10 * 2 + 1 = {result1}")  # 21

# Chain as many as you want
long_pipeline = double >> add_one >> square
state2, result2 = long_pipeline.invoke((("ready", "ready"), "ready"), 5)
print(f"Long chain: ((5 * 2) + 1)^2 = {result2}")  # 121

# =============================================================================
# PARALLEL COMPOSITION: Same input, multiple outputs
# =============================================================================

# parallel() runs both agents on the same input, returns tuple of outputs
both = parallel(double, square)
_, result3 = both.invoke(("ready", "ready"), 4)
print(f"Parallel: (4*2, 4^2) = {result3}")  # (8, 16)

# =============================================================================
# IDENTITY: The do-nothing agent (useful in pipelines)
# =============================================================================

# Identity passes input through unchanged
id_agent: PolyAgent[Any, Any, Any] = identity()
state4, result4 = id_agent.invoke("ready", "hello")
print(f"Identity: {result4}")  # hello

# Identity law: Id >> f == f == f >> Id
# This means identity has no effect when composed
pipeline_with_id = identity() >> double >> identity()
state5, result5 = pipeline_with_id.invoke((("ready", "ready"), "ready"), 5)
print(f"With identity: {result5}")  # 10 (same as just double)

print("\nComposition just works. No glue code needed.")
