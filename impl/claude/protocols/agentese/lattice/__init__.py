"""
AGENTESE Concept Lattice - Genealogical Enforcement System

The Lattice ensures every concept in AGENTESE has lineage,
every definition has justification, and every new idea
connects to what came before.

> "No concept born without parents. No orphan in the family tree."

Components:
- lineage: ConceptLineage dataclass and inheritance computation
- checker: LatticeConsistencyChecker for position validation
- errors: LineageError and LatticeError exceptions
"""

from .checker import (
    ConsistencyResult,
    LatticeConsistencyChecker,
    get_lattice_checker,
)
from .errors import (
    LatticeError,
    LineageError,
)
from .lineage import (
    ConceptLineage,
    compute_affordances,
    compute_constraints,
)

__all__ = [
    # Lineage
    "ConceptLineage",
    "compute_affordances",
    "compute_constraints",
    # Checker
    "ConsistencyResult",
    "LatticeConsistencyChecker",
    "get_lattice_checker",
    # Errors
    "LineageError",
    "LatticeError",
]
