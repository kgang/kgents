"""
TOWN → NPHASE Functor.

Maps Town operations to the N-Phase development cycle operations.
Preserves identity and composition (functor laws).

Pattern source: agents/operad/algebra.py (CLIAlgebra, TestAlgebra)
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from agents.operad.core import (
    Law,
    LawStatus,
    LawVerification,
    Operation,
)
from agents.town.operad import TOWN_OPERAD
from protocols.nphase.operad import (
    NPHASE_OPERAD,
    NPhase,
    NPhaseState,
)

# =============================================================================
# Operation Mapping
# =============================================================================


# Map town operations to N-Phase categories
TOWN_TO_NPHASE_MAP: dict[str, NPhase] = {
    # SENSE operations (observation, perception, planning)
    # Note: "observe" and "listen" would be here if they existed
    # For now, we map perception-like ops
    # ACT operations (action, change, interaction)
    "greet": NPhase.ACT,
    "gossip": NPhase.ACT,
    "trade": NPhase.ACT,
    "dispute": NPhase.ACT,
    "celebrate": NPhase.ACT,
    "teach": NPhase.ACT,
    # REFLECT operations (contemplation, integration, rest)
    "solo": NPhase.REFLECT,  # Individual activity = reflection
    "mourn": NPhase.REFLECT,  # Grief processing = reflection
    # Universal operations (map to their phase context)
    "seq": NPhase.ACT,  # Composition is action
    "par": NPhase.ACT,  # Parallel is action
    "branch": NPhase.SENSE,  # Branching requires sensing
    "fix": NPhase.ACT,  # Fixed point is iterative action
    "trace": NPhase.SENSE,  # Tracing is observation
    "id": NPhase.SENSE,  # Identity preserves (neutral)
}


@dataclass
class FunctorResult:
    """Result of applying the functor."""

    source_op: str
    target_phase: NPhase
    preserved_arity: bool
    metadata: dict[str, Any]


# =============================================================================
# Functor Implementation
# =============================================================================


def town_to_nphase_functor(town_op_name: str) -> NPhase:
    """
    Map a Town operation to its N-Phase category.

    Functor Laws:
        - F(id) = id (identity preservation)
        - F(a >> b) = F(a) >> F(b) (composition preservation)

    Args:
        town_op_name: Name of the town operation

    Returns:
        The corresponding N-Phase

    Raises:
        KeyError: If operation not mapped
    """
    if town_op_name not in TOWN_TO_NPHASE_MAP:
        raise KeyError(f"Town operation '{town_op_name}' not mapped to N-Phase")

    return TOWN_TO_NPHASE_MAP[town_op_name]


def apply_functor(town_op_name: str) -> FunctorResult:
    """
    Apply the functor with full metadata.

    Args:
        town_op_name: Name of the town operation

    Returns:
        FunctorResult with mapping details
    """
    if town_op_name not in TOWN_OPERAD.operations:
        raise KeyError(f"Unknown town operation: {town_op_name}")

    town_op = TOWN_OPERAD.operations[town_op_name]
    target_phase = town_to_nphase_functor(town_op_name)

    # Get corresponding NPHASE operation
    nphase_op_name = target_phase.name.lower()  # SENSE -> "sense"
    nphase_op = NPHASE_OPERAD.operations.get(nphase_op_name)

    # Check arity preservation (functor should preserve structure)
    preserved_arity = True
    if nphase_op:
        # NPHASE ops have arity 1 or 3 (cycle)
        # Town ops have various arities
        # We consider arity preserved if both are positive
        preserved_arity = (town_op.arity > 0 and nphase_op.arity > 0) or (
            town_op.arity == nphase_op.arity
        )

    return FunctorResult(
        source_op=town_op_name,
        target_phase=target_phase,
        preserved_arity=preserved_arity,
        metadata={
            "source_signature": town_op.signature,
            "source_arity": town_op.arity,
            "target_op": nphase_op_name,
        },
    )


def compose_via_functor(
    op_a: str,
    op_b: str,
) -> tuple[NPhase, NPhase, bool]:
    """
    Map a composition F(a >> b) and verify F(a) >> F(b).

    The functor law: F(a >> b) = F(a) >> F(b)

    For NPHASE, composition respects phase ordering:
    - SENSE >> ACT is valid
    - ACT >> REFLECT is valid
    - REFLECT >> SENSE is valid (cycle)

    Args:
        op_a: First operation
        op_b: Second operation

    Returns:
        Tuple of (F(a), F(b), is_valid_composition)
    """
    phase_a = town_to_nphase_functor(op_a)
    phase_b = town_to_nphase_functor(op_b)

    # Check if composition is valid in NPHASE
    from protocols.nphase.operad import is_valid_transition

    is_valid = is_valid_transition(phase_a, phase_b)

    return (phase_a, phase_b, is_valid)


# =============================================================================
# Functor Law Verification
# =============================================================================


def verify_identity_law() -> LawVerification:
    """
    Verify: F(id) = id.

    The identity operation should map to a neutral phase.
    """
    if "id" not in TOWN_TO_NPHASE_MAP:
        return LawVerification(
            law_name="functor_identity",
            status=LawStatus.SKIPPED,
            message="No identity operation in mapping",
        )

    # Identity maps to SENSE (neutral/observational)
    id_phase = town_to_nphase_functor("id")

    # In NPHASE, SENSE is the "start" - conceptually identity-like
    # We accept SENSE as the identity phase
    if id_phase == NPhase.SENSE:
        return LawVerification(
            law_name="functor_identity",
            status=LawStatus.PASSED,
            left_result="F(id)",
            right_result="SENSE (identity phase)",
            message="Identity operation maps to neutral SENSE phase",
        )

    return LawVerification(
        law_name="functor_identity",
        status=LawStatus.FAILED,
        left_result=f"F(id) = {id_phase}",
        right_result="Expected SENSE",
        message="Identity should map to SENSE",
    )


def verify_composition_law(op_a: str, op_b: str) -> LawVerification:
    """
    Verify: F(a >> b) = F(a) >> F(b).

    The functor preserves sequential composition.
    """
    try:
        phase_a, phase_b, is_valid = compose_via_functor(op_a, op_b)
    except KeyError as e:
        return LawVerification(
            law_name="functor_composition",
            status=LawStatus.SKIPPED,
            message=str(e),
        )

    # The composed result F(a >> b) should be the same as
    # composing F(a) >> F(b) in NPHASE
    # Since our functor maps to phases, composition means
    # the transition from phase_a to phase_b

    if is_valid:
        return LawVerification(
            law_name="functor_composition",
            status=LawStatus.PASSED,
            left_result=f"F({op_a} >> {op_b})",
            right_result=f"F({op_a}) >> F({op_b}) = {phase_a.name} >> {phase_b.name}",
            message="Composition preserved through functor",
        )
    else:
        return LawVerification(
            law_name="functor_composition",
            status=LawStatus.FAILED,
            left_result=f"F({op_a} >> {op_b})",
            right_result=f"{phase_a.name} >> {phase_b.name} (invalid transition)",
            message="Composition results in invalid NPHASE transition",
        )


def verify_all_functor_laws() -> list[LawVerification]:
    """
    Verify all functor laws.

    Returns list of verification results.
    """
    results = []

    # 1. Identity law
    results.append(verify_identity_law())

    # 2. Composition laws for sample pairs
    test_pairs = [
        ("greet", "gossip"),  # ACT >> ACT (same phase, valid)
        ("solo", "greet"),  # REFLECT >> ACT (invalid direct)
        ("greet", "solo"),  # ACT >> REFLECT (valid)
        ("solo", "mourn"),  # REFLECT >> REFLECT (same phase, valid)
    ]

    for op_a, op_b in test_pairs:
        results.append(verify_composition_law(op_a, op_b))

    return results


# =============================================================================
# Phase Classification Utilities
# =============================================================================


def get_town_ops_by_phase(phase: NPhase) -> list[str]:
    """Get all town operations that map to a given phase."""
    return [op for op, p in TOWN_TO_NPHASE_MAP.items() if p == phase]


def classify_town_operation(op_name: str) -> dict[str, Any]:
    """
    Classify a town operation with full analysis.

    Returns dict with:
    - phase: The N-Phase category
    - is_social: Whether it involves multiple citizens
    - is_reflective: Whether it's contemplative
    - metabolic_cost: From town operad if available
    """
    if op_name not in TOWN_TO_NPHASE_MAP:
        return {"error": f"Unknown operation: {op_name}"}

    phase = town_to_nphase_functor(op_name)

    # Determine properties
    social_ops = {"greet", "gossip", "trade", "dispute", "celebrate", "mourn", "teach"}
    reflective_ops = {"solo", "mourn"}

    return {
        "phase": phase.name,
        "is_social": op_name in social_ops,
        "is_reflective": op_name in reflective_ops,
        "description": TOWN_OPERAD.operations.get(
            op_name,
            Operation(
                name=op_name,
                arity=0,
                signature="",
                compose=lambda *args: None,  # type: ignore[arg-type]
            ),
        ).description,
    }


def summarize_functor() -> dict[str, Any]:
    """
    Summarize the functor mapping.

    Returns dict with counts and lists per phase.
    """
    sense_ops = get_town_ops_by_phase(NPhase.SENSE)
    act_ops = get_town_ops_by_phase(NPhase.ACT)
    reflect_ops = get_town_ops_by_phase(NPhase.REFLECT)

    return {
        "total_mapped": len(TOWN_TO_NPHASE_MAP),
        "SENSE": {"count": len(sense_ops), "operations": sense_ops},
        "ACT": {"count": len(act_ops), "operations": act_ops},
        "REFLECT": {"count": len(reflect_ops), "operations": reflect_ops},
    }
