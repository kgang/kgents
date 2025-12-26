"""
DP-Native kgents: Dynamic Programming as the foundation.

The core insight: Agent composition IS dynamic programming.
- States = Agent positions
- Actions = Operad operations
- Rewards = Constitutional principle satisfaction
- Traces = Witness marks

"The proof IS the decision. The mark IS the witness. The value IS the agent."
"""

from services.categorical.dp_bridge import (
    DPSolver,
    PolicyTrace,
    Principle,
    PrincipleScore,
    ProblemFormulation,
    TraceEntry,
    ValueFunction,
    ValueScore,
)

__all__ = [
    "PolicyTrace",
    "TraceEntry",
    "Principle",
    "PrincipleScore",
    "ValueScore",
    "ValueFunction",
    "ProblemFormulation",
    "DPSolver",
]
