"""
ASHC Paths Module.

This module provides two complementary systems:

1. **DerivationPath (types.py)**: Categorical morphisms with evidence.
   - DerivationPath: A -> B with witnesses and Galois loss
   - PathWitness: Evidence supporting a derivation step (uses PathWitnessType)
   - Composition with categorical laws (identity, associativity)

2. **Witness Bridge (witness_bridge.py)**: ASHC evidence -> Mark integration.
   - WitnessType: ASHC action classification (TEST, LLM, COMPOSITION, etc.)
   - DerivationWitness: Bridge between ASHC evidence and Mark system
   - emit_ashc_mark: Store ASHC evidence as witness marks

The two systems work together:
- types.py provides the categorical foundation (DerivationPath)
- witness_bridge.py provides the storage/retrieval layer via Marks

Example:
    >>> from protocols.ashc.paths import (
    ...     DerivationPath, PathKind, PathWitnessType,
    ...     emit_ashc_mark, WitnessType,
    ... )
    >>>
    >>> # Create a categorical derivation path
    >>> path = DerivationPath.derive("spec", "impl", galois_loss=0.1)
    >>>
    >>> # Emit an ASHC mark for the derivation
    >>> mark, witness = await emit_ashc_mark(
    ...     action="Derived implementation from spec",
    ...     evidence={"path_id": path.path_id},
    ...     witness_type=WitnessType.COMPOSITION,
    ... )
"""

# Core categorical types (DerivationPath system)
# Composition and law verification
from .composition import (
    LawVerificationResult,
    compose,
    compose_all,
    compose_witnesses,
    compute_accumulated_loss,
    loss_is_acceptable,
    validate_with_kblock_dag,
    verify_all_laws,
    verify_associativity,
    verify_identity_left,
    verify_identity_right,
)
from .types import (
    DerivationPath,
    DerivationWitness as PathWitness,  # Renamed to avoid conflict
    PathKind,
    WitnessType as PathWitnessType,  # Renamed to avoid conflict
)

# Witness bridge (ASHC -> Mark integration)
from .witness_bridge import (
    DerivationWitness,
    WitnessType,
    batch_emit_ashc_marks,
    derivation_to_mark,
    emit_ashc_mark,
    mark_to_derivation,
)

__all__ = [
    # Core categorical types (DerivationPath system)
    "DerivationPath",
    "PathKind",
    "PathWitnessType",  # From types.py (categorical witness type)
    "PathWitness",  # From types.py (categorical witness)
    # Composition
    "compose",
    "compose_all",
    "compose_witnesses",
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
    # Witness bridge (backward compatible)
    "WitnessType",  # From witness_bridge.py (ASHC action type)
    "DerivationWitness",  # From witness_bridge.py (Mark bridge)
    "emit_ashc_mark",
    "derivation_to_mark",
    "mark_to_derivation",
    "batch_emit_ashc_marks",
]
