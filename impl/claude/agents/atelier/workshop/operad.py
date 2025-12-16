"""
Atelier Operad: Composition grammar for artisan collaboration.

Defines the valid ways artisans can work together:
- Solo: Single artisan creates alone
- Duet: Two artisans collaborate sequentially
- Ensemble: Multiple artisans work in parallel, results merged
- Refinement: Second artisan refines first's work

From category theory: An operad captures the grammar of composition.
The ATELIER_OPERAD defines how artisan outputs can connect to inputs.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class CompositionLaw(Enum):
    """How outputs flow between artisans."""

    SEQUENTIAL = "sequential"  # A → B: Output of A feeds into B
    PARALLEL_MERGE = "parallel"  # A + B → merge: Both work simultaneously
    ITERATIVE = "iterative"  # A → B → A: Refinement loop


@dataclass(frozen=True)
class Operation:
    """
    An operation in the atelier operad.

    Describes a valid composition pattern for artisans.
    """

    name: str
    arity: int | str  # int for fixed, "*" for variadic
    description: str
    law: CompositionLaw

    def accepts_arity(self, n: int) -> bool:
        """Check if this operation accepts n artisans."""
        if self.arity == "*":
            return n >= 1
        return n == self.arity


@dataclass
class AtelierOperad:
    """
    The composition grammar for Tiny Atelier.

    Defines valid operations and their composition laws.
    """

    operations: dict[str, Operation]

    def get(self, name: str) -> Operation | None:
        """Get operation by name."""
        return self.operations.get(name)

    def validate(self, operation: str, artisan_count: int) -> bool:
        """Check if operation is valid for given artisan count."""
        op = self.operations.get(operation)
        if not op:
            return False
        return op.accepts_arity(artisan_count)

    def list_operations(self) -> list[str]:
        """List all available operations."""
        return list(self.operations.keys())


# =============================================================================
# The Atelier Operad
# =============================================================================

ATELIER_OPERAD = AtelierOperad(
    operations={
        "solo": Operation(
            name="solo",
            arity=1,
            description="Single artisan creates alone",
            law=CompositionLaw.SEQUENTIAL,
        ),
        "duet": Operation(
            name="duet",
            arity=2,
            description="Two artisans collaborate: first creates, second transforms",
            law=CompositionLaw.SEQUENTIAL,
        ),
        "ensemble": Operation(
            name="ensemble",
            arity="*",
            description="Multiple artisans work in parallel, results merged by Archivist",
            law=CompositionLaw.PARALLEL_MERGE,
        ),
        "refinement": Operation(
            name="refinement",
            arity=2,
            description="Second artisan refines and elevates first's work",
            law=CompositionLaw.ITERATIVE,
        ),
        "chain": Operation(
            name="chain",
            arity="*",
            description="Sequential pipeline: each transforms the previous output",
            law=CompositionLaw.SEQUENTIAL,
        ),
    }
)


__all__ = ["AtelierOperad", "ATELIER_OPERAD", "Operation", "CompositionLaw"]
