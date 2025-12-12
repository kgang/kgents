"""
AGENTESE Lattice Error Types

Sympathetic errors for lineage and lattice violations.

The Transparent Infrastructure principle demands that errors
help the user understand WHY and suggest WHAT TO DO.
"""

from __future__ import annotations

from protocols.agentese.exceptions import AgentesError


class LineageError(AgentesError):
    """
    Raised when a concept has no valid lineage.

    Concepts cannot exist ex nihilo. Every concept must declare
    its parents and justify its existence.

    The Genealogical Constraint: No orphans in the family tree.
    """

    sympathetic_message: str = (
        "Concepts cannot exist ex nihilo. "
        "Provide at least one parent concept. "
        "Consider: What existing concept does this specialize?"
    )

    def __init__(
        self,
        message: str,
        *,
        handle: str = "",
        missing_parents: list[str] | None = None,
        why: str | None = None,
        suggestion: str | None = None,
    ) -> None:
        self.handle = handle
        self.missing_parents = missing_parents or []

        if not why:
            if missing_parents:
                why = f"Parent concept(s) do not exist: {', '.join(missing_parents)}"
            else:
                why = self.sympathetic_message

        if not suggestion:
            if missing_parents:
                suggestion = (
                    "Ensure parent concepts exist before defining children.\n"
                    f"    Missing: {', '.join(missing_parents)}\n"
                    "    Use concept.*.define to create parent concepts first."
                )
            else:
                suggestion = (
                    "Every concept needs at least one parent:\n"
                    "    - concept.entity for general entities\n"
                    "    - concept.process for procedures/actions\n"
                    "    - concept.relation for relationships\n"
                    "    - Or another domain-specific parent"
                )

        super().__init__(
            message,
            why=why,
            suggestion=suggestion,
            related=self.missing_parents[:5],
        )


class LatticeError(AgentesError):
    """
    Raised when a concept violates lattice properties.

    The lattice is a bounded meet-semilattice where:
    - Every node has at least one parent (except `concept` itself)
    - No cycles allowed (DAG property)
    - Affordances flow downward (children inherit)
    - Constraints flow upward (children must satisfy)
    """

    def __init__(
        self,
        message: str,
        *,
        handle: str = "",
        violation_type: str = "",
        conflicting_affordances: list[str] | None = None,
        empty_constraints: bool = False,
        cycle_path: list[str] | None = None,
        why: str | None = None,
        suggestion: str | None = None,
    ) -> None:
        self.handle = handle
        self.violation_type = violation_type
        self.conflicting_affordances = conflicting_affordances or []
        self.empty_constraints = empty_constraints
        self.cycle_path = cycle_path or []

        if not why:
            if violation_type == "cycle":
                path_str = " -> ".join(cycle_path or []) if cycle_path else handle
                why = f"Adding this concept would create a cycle: {path_str}"
            elif violation_type == "affordance_conflict":
                why = f"Parent affordances conflict: {', '.join(conflicting_affordances or [])}"
            elif violation_type == "empty_constraints":
                why = "Parent constraints have empty intersection (unsatisfiable)"
            else:
                why = "Concept violates lattice consistency requirements"

        if not suggestion:
            if violation_type == "cycle":
                suggestion = (
                    "Cycles violate the DAG property of the concept lattice.\n"
                    "    Consider:\n"
                    "    - Is this relationship truly parent-child?\n"
                    "    - Perhaps these concepts should be siblings instead\n"
                    "    - Use concept.*.relate for non-hierarchical connections"
                )
            elif violation_type == "affordance_conflict":
                suggestion = (
                    "Multiple inheritance requires compatible affordances.\n"
                    "    Options:\n"
                    "    - Choose one parent with compatible affordances\n"
                    "    - Create an intermediate concept to resolve conflict\n"
                    "    - Override conflicting affordances explicitly"
                )
            elif violation_type == "empty_constraints":
                suggestion = (
                    "Parent constraints must have non-empty intersection.\n"
                    "    The child cannot satisfy incompatible requirements.\n"
                    "    Consider choosing parents with compatible constraints."
                )
            else:
                suggestion = "Check the lattice position and try again."

        super().__init__(
            message,
            why=why,
            suggestion=suggestion,
            related=self.conflicting_affordances or self.cycle_path,
        )


# Convenience constructors


def lineage_missing(handle: str) -> LineageError:
    """Create a LineageError for missing lineage."""
    return LineageError(
        f"Concept '{handle}' has no lineage",
        handle=handle,
    )


def lineage_parents_missing(handle: str, missing: list[str]) -> LineageError:
    """Create a LineageError for missing parent concepts."""
    return LineageError(
        f"Cannot create '{handle}': parent concepts do not exist",
        handle=handle,
        missing_parents=missing,
    )


def lattice_cycle(handle: str, cycle_path: list[str]) -> LatticeError:
    """Create a LatticeError for cycle violation."""
    return LatticeError(
        f"Adding '{handle}' would create a cycle",
        handle=handle,
        violation_type="cycle",
        cycle_path=cycle_path,
    )


def lattice_affordance_conflict(
    handle: str,
    conflicts: list[str],
) -> LatticeError:
    """Create a LatticeError for affordance conflicts."""
    return LatticeError(
        f"Cannot create '{handle}': parent affordances conflict",
        handle=handle,
        violation_type="affordance_conflict",
        conflicting_affordances=conflicts,
    )


def lattice_unsatisfiable(handle: str) -> LatticeError:
    """Create a LatticeError for empty constraint intersection."""
    return LatticeError(
        f"Cannot create '{handle}': parent constraints are unsatisfiable",
        handle=handle,
        violation_type="empty_constraints",
        empty_constraints=True,
    )
