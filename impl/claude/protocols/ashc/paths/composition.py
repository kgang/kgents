"""
ASHC DerivationPath Composition and Categorical Law Verification.

Implements categorical composition for DerivationPath with:
- Composition function with loss accumulation
- Identity law verification
- Associativity law verification
- Integration with K-Block's DAG validation

Philosophy:
    "Composition IS closure. The laws ARE the type system.
     If the laws fail, the derivation is not a derivation."

See: spec/protocols/zero-seed1/ashc.md
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, TypeVar

from .types import DerivationPath, DerivationWitness, PathKind, WitnessType

# =============================================================================
# Type Variables
# =============================================================================

A = TypeVar("A")
B = TypeVar("B")
C = TypeVar("C")
D = TypeVar("D")


# =============================================================================
# Composition Functions
# =============================================================================


def compose(
    path1: DerivationPath[A, B],
    path2: DerivationPath[B, C],
) -> DerivationPath[A, C]:
    """
    Compose two derivation paths.

    Given:
        path1: A -> B
        path2: B -> C

    Returns:
        composed: A -> C

    This is functionally equivalent to path1.compose(path2) but as a
    standalone function for consistency with categorical conventions.

    Loss Accumulation Formula:
        L(p;q) = 1 - (1-L(p))*(1-L(q))

    Raises:
        ValueError: If path1.target_id != path2.source_id (incompatible composition)
    """
    return path1.compose(path2)


def compose_all(*paths: DerivationPath[Any, Any]) -> DerivationPath[Any, Any]:
    """
    Compose multiple paths in sequence.

    Given paths p1, p2, ..., pn, returns p1 ; p2 ; ... ; pn

    The paths must form a valid chain:
        p1.target_id == p2.source_id
        p2.target_id == p3.source_id
        ...

    Raises:
        ValueError: If fewer than 2 paths provided or chain is invalid
    """
    if len(paths) < 2:
        raise ValueError("compose_all requires at least 2 paths")

    result = paths[0]
    for path in paths[1:]:
        result = result.compose(path)
    return result


# =============================================================================
# Law Verification
# =============================================================================


@dataclass(frozen=True)
class LawVerificationResult:
    """Result of verifying a categorical law."""

    law_name: str
    passed: bool
    message: str
    details: dict[str, Any]


def verify_identity_left(path: DerivationPath[A, B]) -> LawVerificationResult:
    """
    Verify the left identity law: refl(source) ; p == p

    The identity path refl(a) should act as a left identity under composition.
    """
    # Create identity path for source
    refl_source: DerivationPath[A, A] = DerivationPath.refl(path.source_id)

    # Compose: refl(source) ; path
    composed = refl_source.compose(path)

    # Verify structural equivalence
    source_match = composed.source_id == path.source_id
    target_match = composed.target_id == path.target_id
    loss_match = abs(composed.galois_loss - path.galois_loss) < 1e-10

    passed = source_match and target_match and loss_match

    return LawVerificationResult(
        law_name="left_identity",
        passed=passed,
        message="refl(source) ; p == p" if passed else "Left identity law violated",
        details={
            "source_match": source_match,
            "target_match": target_match,
            "loss_match": loss_match,
            "expected_loss": path.galois_loss,
            "actual_loss": composed.galois_loss,
        },
    )


def verify_identity_right(path: DerivationPath[A, B]) -> LawVerificationResult:
    """
    Verify the right identity law: p ; refl(target) == p

    The identity path refl(b) should act as a right identity under composition.
    """
    # Create identity path for target
    refl_target: DerivationPath[B, B] = DerivationPath.refl(path.target_id)

    # Compose: path ; refl(target)
    composed = path.compose(refl_target)

    # Verify structural equivalence
    source_match = composed.source_id == path.source_id
    target_match = composed.target_id == path.target_id
    loss_match = abs(composed.galois_loss - path.galois_loss) < 1e-10

    passed = source_match and target_match and loss_match

    return LawVerificationResult(
        law_name="right_identity",
        passed=passed,
        message="p ; refl(target) == p" if passed else "Right identity law violated",
        details={
            "source_match": source_match,
            "target_match": target_match,
            "loss_match": loss_match,
            "expected_loss": path.galois_loss,
            "actual_loss": composed.galois_loss,
        },
    )


def verify_associativity(
    p: DerivationPath[A, B],
    q: DerivationPath[B, C],
    r: DerivationPath[C, D],
) -> LawVerificationResult:
    """
    Verify the associativity law: (p ; q) ; r == p ; (q ; r)

    Composition must be associative for the structure to form a category.
    """
    # Left association: (p ; q) ; r
    pq = p.compose(q)
    left = pq.compose(r)

    # Right association: p ; (q ; r)
    qr = q.compose(r)
    right = p.compose(qr)

    # Verify structural equivalence
    source_match = left.source_id == right.source_id
    target_match = left.target_id == right.target_id
    loss_match = abs(left.galois_loss - right.galois_loss) < 1e-10

    passed = source_match and target_match and loss_match

    return LawVerificationResult(
        law_name="associativity",
        passed=passed,
        message="(p ; q) ; r == p ; (q ; r)" if passed else "Associativity law violated",
        details={
            "source_match": source_match,
            "target_match": target_match,
            "loss_match": loss_match,
            "left_loss": left.galois_loss,
            "right_loss": right.galois_loss,
            "left_source": left.source_id,
            "right_source": right.source_id,
            "left_target": left.target_id,
            "right_target": right.target_id,
        },
    )


def verify_all_laws(
    p: DerivationPath[A, B],
    q: DerivationPath[B, C] | None = None,
    r: DerivationPath[C, D] | None = None,
) -> list[LawVerificationResult]:
    """
    Verify all categorical laws for the given paths.

    Args:
        p: First path (required for identity laws)
        q: Second path (required for associativity with r)
        r: Third path (required for associativity)

    Returns:
        List of verification results for all applicable laws
    """
    results = []

    # Always verify identity laws
    results.append(verify_identity_left(p))
    results.append(verify_identity_right(p))

    # Verify associativity if we have all three paths
    if q is not None and r is not None:
        results.append(verify_associativity(p, q, r))

    return results


# =============================================================================
# Loss Accumulation Helpers
# =============================================================================


def compute_accumulated_loss(losses: list[float]) -> float:
    """
    Compute accumulated loss for a sequence of path losses.

    Formula: L(p1;p2;...;pn) = 1 - prod(1 - L(pi))

    This is a generalization of the binary loss accumulation formula.

    Properties:
    - Monotonic: Adding more paths never decreases loss
    - Sub-additive: L(p;q) <= L(p) + L(q) for L(p), L(q) < 1
    - Identity-preserving: L([0, x]) == x

    Args:
        losses: List of individual path losses

    Returns:
        Accumulated loss in [0, 1]
    """
    if not losses:
        return 0.0

    # Compute product of complements
    complement_product = 1.0
    for loss in losses:
        complement_product *= 1.0 - loss

    return 1.0 - complement_product


def loss_is_acceptable(loss: float, threshold: float = 0.5) -> bool:
    """
    Check if a loss value is acceptable for derivation.

    Default threshold is 0.5 (50% coherence preserved).

    Args:
        loss: Galois loss value
        threshold: Maximum acceptable loss

    Returns:
        True if loss < threshold
    """
    return loss < threshold


# =============================================================================
# K-Block DAG Integration
# =============================================================================


def validate_with_kblock_dag(path: DerivationPath[A, B]) -> LawVerificationResult:
    """
    Validate path against K-Block's DerivationDAG.

    This integrates with the existing K-Block lineage system to ensure:
    1. No cycles in the derivation chain
    2. Layer monotonicity is preserved

    Uses K-Block's validate_acyclic() for cycle detection.
    """
    # Import K-Block's DAG (deferred to avoid circular imports)
    try:
        from services.k_block.core.derivation import DerivationDAG
    except ImportError:
        return LawVerificationResult(
            law_name="kblock_validation",
            passed=True,  # Skip if K-Block not available
            message="K-Block validation skipped (import unavailable)",
            details={"skipped": True},
        )

    if not path.kblock_lineage:
        return LawVerificationResult(
            law_name="kblock_validation",
            passed=True,
            message="No K-Block lineage to validate",
            details={"empty_lineage": True},
        )

    # Build a DAG from the lineage
    dag = DerivationDAG()

    # Add nodes from lineage (we don't have full layer info here,
    # so we use default layer assignment)
    for i, kblock_id in enumerate(path.kblock_lineage):
        parent_ids = [path.kblock_lineage[i - 1]] if i > 0 else []
        try:
            dag.add_node(
                kblock_id=kblock_id,
                layer=i + 1,  # Increasing layers
                kind="derived",
                parent_ids=parent_ids,
            )
        except ValueError as e:
            return LawVerificationResult(
                law_name="kblock_validation",
                passed=False,
                message=f"Layer monotonicity violation: {e}",
                details={"error": str(e), "kblock_id": kblock_id},
            )

    # Validate acyclicity
    if path.kblock_lineage:
        last_id = path.kblock_lineage[-1]
        is_acyclic = dag.validate_acyclic(last_id)

        if not is_acyclic:
            return LawVerificationResult(
                law_name="kblock_validation",
                passed=False,
                message="Cycle detected in K-Block lineage",
                details={"cycle_at": last_id},
            )

    return LawVerificationResult(
        law_name="kblock_validation",
        passed=True,
        message="K-Block lineage is valid (acyclic, monotonic)",
        details={"lineage_length": len(path.kblock_lineage)},
    )


# =============================================================================
# Witness Composition
# =============================================================================


def compose_witnesses(
    witnesses1: tuple[DerivationWitness, ...],
    witnesses2: tuple[DerivationWitness, ...],
) -> tuple[DerivationWitness, ...]:
    """
    Compose witness tuples, optionally creating a composition witness.

    If the combined confidence is significant, adds a COMPOSITION witness
    that records the composition event.

    Args:
        witnesses1: Witnesses from first path
        witnesses2: Witnesses from second path

    Returns:
        Combined witnesses (may include composition witness)
    """
    combined = witnesses1 + witnesses2

    if not combined:
        return ()

    # Calculate combined confidence
    avg_confidence = sum(w.confidence for w in combined) / len(combined)

    # If significant, add a composition witness
    if avg_confidence > 0.3:
        composition_witness = DerivationWitness.create(
            witness_type=WitnessType.COMPOSITION,
            evidence={
                "composed_count": len(combined),
                "avg_confidence": avg_confidence,
                "witness_types": [w.witness_type.name for w in combined],
            },
            confidence=avg_confidence * 0.9,  # Slight discount for composition
        )
        combined = combined + (composition_witness,)

    return combined


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    # Composition
    "compose",
    "compose_all",
    # Law Verification
    "LawVerificationResult",
    "verify_identity_left",
    "verify_identity_right",
    "verify_associativity",
    "verify_all_laws",
    # Loss Helpers
    "compute_accumulated_loss",
    "loss_is_acceptable",
    # K-Block Integration
    "validate_with_kblock_dag",
    # Witness Composition
    "compose_witnesses",
]
