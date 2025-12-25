"""
Derivation Service - Crown Jewel for causal lineage tracking.

The DerivationService tracks derivation relationships across the Crystal taxonomy,
forming a causal DAG from axioms (L1-L2) to implementations (L5-L7).

Every Crystal has a derivation path tracing back to foundational axioms:
    Constitution (L1) → Value (L2) → Prompt (L3) → Spec (L4)
    → Code (L5) → Test (L5) → Reflection (L6) → Interpretation (L7)

Architecture:
    - Uses Universe for Crystal storage/retrieval
    - Uses KBlockEdge for relationship tracking
    - Uses GaloisLossComputer for coherence measurement
    - Provides drift detection (spec/impl divergence)
    - Tracks orphaned crystals (no axiomatic grounding)

Teaching:
    gotcha: Derivation edges flow DOWNWARD in layer numbers
            (L1 axioms → L2 values → ... → L7 interpretations)
            Parent layer must be < child layer for valid derivation.
            (Evidence: k_block/core/derivation.py::validate_derivation)

    gotcha: Galois loss accumulates along derivation chains.
            Total loss = sum of edge losses from target to axiom.
            High accumulated loss = coherence drift = needs refactoring.
            (Evidence: agents/d/galois.py::GaloisLossComputer)

    gotcha: is_grounded checks if lineage reaches L1-L2 (axioms/values).
            NOT grounded = orphaned crystal = needs justification.
            (Evidence: k_block/core/derivation.py::DerivationDAG.is_grounded)

See: spec/protocols/zero-seed.md
See: docs/skills/crown-jewel-patterns.md
"""

from .service import (
    CrystalRef,
    DerivationChain,
    DerivationService,
    DerivationTree,
    DriftReport,
)

__all__ = [
    "DerivationService",
    "DerivationChain",
    "DerivationTree",
    "CrystalRef",
    "DriftReport",
]
