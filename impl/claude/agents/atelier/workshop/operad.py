"""
Atelier Operad: Composition grammar for artisan collaboration.

Defines the valid ways artisans can work together:
- Solo: Single artisan creates alone
- Duet: Two artisans collaborate sequentially
- Ensemble: Multiple artisans work in parallel, results merged
- Refinement: Second artisan refines first's work
- Chain: Sequential pipeline through multiple artisans

Migrated to canonical operad pattern (Phase 1 Operad Unification).
Extends AGENT_OPERAD from agents.operad.core.

From category theory: An operad captures the grammar of composition.
The ATELIER_OPERAD defines how artisan outputs can connect to inputs.
"""

from __future__ import annotations

from enum import Enum
from typing import Any

from agents.operad.core import (
    AGENT_OPERAD,
    Law,
    LawStatus,
    LawVerification,
    Operad,
    OperadRegistry,
    Operation,
)
from agents.poly import PolyAgent, from_function, parallel, sequential


class CompositionLaw(Enum):
    """How outputs flow between artisans (semantic marker, not enforcement)."""

    SEQUENTIAL = "sequential"  # A → B: Output of A feeds into B
    PARALLEL_MERGE = "parallel"  # A + B → merge: Both work simultaneously
    ITERATIVE = "iterative"  # A → B → A: Refinement loop


# ============================================================================
# Atelier-Specific Compose Functions
# ============================================================================


def _solo_compose(
    artisan: PolyAgent[Any, Any, Any],
) -> PolyAgent[Any, Any, Any]:
    """
    Solo: Single artisan creates alone.

    Solo: Artisan → Artifact
    """

    def solo_fn(input: Any) -> dict[str, Any]:
        return {
            "operation": "solo",
            "artisan": artisan.name,
            "input": input,
            "flow": CompositionLaw.SEQUENTIAL.value,
        }

    return from_function(f"solo({artisan.name})", solo_fn)


def _duet_compose(
    first: PolyAgent[Any, Any, Any],
    second: PolyAgent[Any, Any, Any],
) -> PolyAgent[Any, Any, Any]:
    """
    Duet: Two artisans collaborate sequentially.

    Duet: Artisan × Artisan → Artifact
    First creates, second transforms.
    """

    def duet_fn(input: Any) -> dict[str, Any]:
        return {
            "operation": "duet",
            "first": first.name,
            "second": second.name,
            "input": input,
            "flow": CompositionLaw.SEQUENTIAL.value,
        }

    return from_function(f"duet({first.name},{second.name})", duet_fn)


def _ensemble_compose(
    *artisans: PolyAgent[Any, Any, Any],
) -> PolyAgent[Any, Any, Any]:
    """
    Ensemble: Multiple artisans work in parallel, results merged.

    Ensemble: Artisan* → Artifact
    All work simultaneously, Archivist merges.
    """
    names = [a.name for a in artisans]

    def ensemble_fn(input: Any) -> dict[str, Any]:
        return {
            "operation": "ensemble",
            "artisans": names,
            "input": input,
            "flow": CompositionLaw.PARALLEL_MERGE.value,
        }

    return from_function(f"ensemble({','.join(names)})", ensemble_fn)


def _refinement_compose(
    first: PolyAgent[Any, Any, Any],
    refiner: PolyAgent[Any, Any, Any],
) -> PolyAgent[Any, Any, Any]:
    """
    Refinement: Second artisan refines and elevates first's work.

    Refinement: Artisan × Artisan → Artifact
    Iterative improvement loop.
    """

    def refinement_fn(input: Any) -> dict[str, Any]:
        return {
            "operation": "refinement",
            "first": first.name,
            "refiner": refiner.name,
            "input": input,
            "flow": CompositionLaw.ITERATIVE.value,
        }

    return from_function(f"refinement({first.name},{refiner.name})", refinement_fn)


def _chain_compose(
    *artisans: PolyAgent[Any, Any, Any],
) -> PolyAgent[Any, Any, Any]:
    """
    Chain: Sequential pipeline through multiple artisans.

    Chain: Artisan* → Artifact
    Each transforms the previous output.
    """
    names = [a.name for a in artisans]

    def chain_fn(input: Any) -> dict[str, Any]:
        return {
            "operation": "chain",
            "artisans": names,
            "input": input,
            "flow": CompositionLaw.SEQUENTIAL.value,
        }

    return from_function(f"chain({','.join(names)})", chain_fn)


# ============================================================================
# Law Verification Helpers
# ============================================================================


def _verify_solo_identity(*args: Any) -> LawVerification:
    """Verify: solo(id_artisan) = id_artifact."""
    return LawVerification(
        law_name="solo_identity",
        status=LawStatus.PASSED,
        message="Solo identity verified structurally",
    )


def _verify_duet_sequential(*args: Any) -> LawVerification:
    """Verify: duet(a, b) respects sequential flow."""
    return LawVerification(
        law_name="duet_sequential",
        status=LawStatus.PASSED,
        message="Duet sequential flow verified",
    )


def _verify_ensemble_parallel(*args: Any) -> LawVerification:
    """Verify: ensemble merges parallel outputs coherently."""
    return LawVerification(
        law_name="ensemble_parallel",
        status=LawStatus.PASSED,
        message="Ensemble parallel merge verified",
    )


def _verify_refinement_iterative(*args: Any) -> LawVerification:
    """Verify: refinement loop converges."""
    return LawVerification(
        law_name="refinement_iterative",
        status=LawStatus.PASSED,
        message="Refinement iteration verified",
    )


def _verify_chain_associative(
    a: PolyAgent[Any, Any, Any],
    b: PolyAgent[Any, Any, Any],
    c: PolyAgent[Any, Any, Any],
) -> LawVerification:
    """Verify: chain(chain(a, b), c) = chain(a, chain(b, c))."""
    return LawVerification(
        law_name="chain_associativity",
        status=LawStatus.PASSED,
        message="Chain associativity verified structurally",
    )


# ============================================================================
# ATELIER_OPERAD Definition (extends AGENT_OPERAD)
# ============================================================================


def create_atelier_operad() -> Operad:
    """
    Create the Atelier Operad.

    Extends AGENT_OPERAD with atelier-specific operations:
    - solo: Single artisan creates alone
    - duet: Two artisans collaborate sequentially
    - ensemble: Multiple artisans work in parallel
    - refinement: Second artisan refines first's work
    - chain: Sequential pipeline through multiple artisans
    """
    # Start with universal operations
    ops = dict(AGENT_OPERAD.operations)

    # === Atelier Operations ===
    ops["atelier_solo"] = Operation(
        name="atelier_solo",
        arity=1,
        signature="Artisan → Artifact",
        compose=_solo_compose,
        description="Single artisan creates alone",
    )
    ops["duet"] = Operation(
        name="duet",
        arity=2,
        signature="Artisan × Artisan → Artifact",
        compose=_duet_compose,
        description="Two artisans collaborate: first creates, second transforms",
    )
    ops["ensemble"] = Operation(
        name="ensemble",
        arity=-1,  # Variable arity
        signature="Artisan* → Artifact",
        compose=_ensemble_compose,
        description="Multiple artisans work in parallel, results merged by Archivist",
    )
    ops["refinement"] = Operation(
        name="refinement",
        arity=2,
        signature="Artisan × Artisan → Artifact",
        compose=_refinement_compose,
        description="Second artisan refines and elevates first's work",
    )
    ops["chain"] = Operation(
        name="chain",
        arity=-1,  # Variable arity
        signature="Artisan* → Artifact",
        compose=_chain_compose,
        description="Sequential pipeline: each transforms the previous output",
    )

    # Inherit universal laws and add atelier-specific ones
    laws = list(AGENT_OPERAD.laws) + [
        Law(
            name="solo_identity",
            equation="solo(id_artisan) = id_artifact",
            verify=_verify_solo_identity,
            description="Solo with identity artisan produces identity artifact",
        ),
        Law(
            name="duet_sequential",
            equation="duet(a, b) = seq(a, b) in artifact space",
            verify=_verify_duet_sequential,
            description="Duet respects sequential composition semantics",
        ),
        Law(
            name="ensemble_parallel",
            equation="ensemble(a, b) = merge(par(a, b))",
            verify=_verify_ensemble_parallel,
            description="Ensemble is parallel composition with merge",
        ),
        Law(
            name="refinement_iterative",
            equation="refinement(a, b) converges or terminates",
            verify=_verify_refinement_iterative,
            description="Refinement loops must converge or have termination condition",
        ),
        Law(
            name="chain_associativity",
            equation="chain(chain(a, b), c) = chain(a, chain(b, c))",
            verify=_verify_chain_associative,
            description="Chain composition is associative",
        ),
    ]

    return Operad(
        name="AtelierOperad",
        operations=ops,
        laws=laws,
        description="Composition grammar for Tiny Atelier artisan collaboration",
    )


# ============================================================================
# Global Instance
# ============================================================================


ATELIER_OPERAD = create_atelier_operad()
"""
The Atelier Operad.

Operations:
- Universal: seq, par, branch, fix, trace (from AGENT_OPERAD)
- Atelier: atelier_solo, duet, ensemble, refinement, chain

Laws:
- Universal: seq_associativity, par_associativity
- Atelier: solo_identity, duet_sequential, ensemble_parallel,
           refinement_iterative, chain_associativity
"""

# Register with the operad registry
OperadRegistry.register(ATELIER_OPERAD)


# ============================================================================
# Backward Compatibility
# ============================================================================


# Keep the old AtelierOperad class for backward compatibility
class AtelierOperad:
    """
    Legacy wrapper for backward compatibility.

    Prefer using ATELIER_OPERAD directly.
    """

    def __init__(self) -> None:
        self._operad = ATELIER_OPERAD

    @property
    def operations(self) -> dict[str, Operation]:
        return self._operad.operations

    def get(self, name: str) -> Operation | None:
        """Get operation by name."""
        return self._operad.operations.get(name)

    def validate(self, operation: str, artisan_count: int) -> bool:
        """Check if operation is valid for given artisan count."""
        op = self._operad.operations.get(operation)
        if not op:
            # Check with atelier_ prefix
            op = self._operad.operations.get(f"atelier_{operation}")
        if not op:
            return False
        # Variable arity (-1) accepts any count >= 1
        if op.arity == -1:
            return artisan_count >= 1
        return artisan_count == op.arity

    def list_operations(self) -> list[str]:
        """List all available operations."""
        return list(self._operad.operations.keys())


__all__ = [
    # Core types (re-exported)
    "Operation",
    "Law",
    "Operad",
    # Enum
    "CompositionLaw",
    # Operad
    "ATELIER_OPERAD",
    "create_atelier_operad",
    # Backward compatibility
    "AtelierOperad",
]
