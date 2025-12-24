"""
Galois: Coherence Measurement, Axiomatic Grounding, and Bootstrap.

The Galois module implements:
1. **Axiomatics**: The Galois-grounded minimal kernel (A1, A2, G)
2. **Proof Coherence**: Toulmin proof extended with loss metrics
3. **Bootstrap**: Lawvere fixed point verification for Zero Seed
4. Evidence tier classification via loss bounds
5. Witness mode triage (SINGLE/SESSION/LAZY)
6. Ghost alternative generation from loss decomposition
7. Contradiction detection via super-additive loss

Key Formulas:
- Axiom = Zero-loss fixed point: L(P) < 0.01
- Layer = Convergence depth: L_i = min{k : L(R^k(P)) < epsilon}
- Loss = Semantic distance: L(P) = d(P, C(R(P)))
- Coherence = 1 - galois_loss(P)
- Bootstrap: Zero Seed = Fix(R o describe), L(ZS) < 0.15 (85% regenerability)

The Three Axioms (discovered, not stipulated):
- A1: Entity Axiom - Universal representability (L=0.002)
- A2: Morphism Axiom - Composition primacy (L=0.003)
- G: Galois Ground - The loss function as axiomatic ground (L=0.000)

See: spec/protocols/zero-seed1/axiomatics.md
See: spec/protocols/zero-seed1/bootstrap.md
See: spec/protocols/zero-seed1/proof.md
See: spec/theory/galois-modularization.md
"""

from __future__ import annotations

# Axiomatics: The Galois-grounded minimal kernel
from .axiomatics import (
    # Constants
    DEFAULT_VOICE_ANCHORS,
    DRIFT_TOLERANCE,
    FIXED_POINT_THRESHOLD,
    GALOIS_LAWS,
    MAX_DEPTH,
    # Axioms
    Axiom,
    AxiomGovernance,
    AxiomHealth,
    AxiomStatus,
    EntityAxiom,
    GaloisGround,
    GaloisLaw,
    # Core types
    GaloisLoss,
    LayerType,
    MorphismAxiom,
    Restructurable,
    ZeroNode,
    compute_layer,
    create_axiom_governance,
    create_axiom_kernel,
    stratify_by_loss,
    # Discovery (3-stage process from axiomatics.md)
    DiscoveryResult,
    GaloisAxiomDiscovery,
    MirrorTestOracle,
)

# Bootstrap: Lawvere fixed point verification
from .bootstrap import (
    BootstrapMark,
    BootstrapReport,
    BootstrapWindow,
    ConvergenceReport,
    Deviation,
    DEVIATION_CATEGORIES,
    EdgeKind,
    FixedPointVerification,
    GaloisOperations,
    Layer,
    NodeKind,
    SimpleGaloisLoss,
    StrangeLoopResolution,
    ZeroSeedPolynomial,
    extract_deviations,
    retroactive_witness_bootstrap,
    verify_convergence,
    verify_zero_seed_fixed_point,
)

# Proof coherence: Toulmin proofs with Galois loss
from .proof import (
    Alternative,
    EvidenceTier,
    GaloisWitnessedProof,
    ProofLossDecomposition,
    ProofValidation,
    TierBounds,
    WitnessMode,
    classify_by_loss,
    select_witness_mode_from_loss,
)

__all__ = [
    # === Axiomatics ===
    # Constants
    "FIXED_POINT_THRESHOLD",
    "MAX_DEPTH",
    "DRIFT_TOLERANCE",
    "DEFAULT_VOICE_ANCHORS",
    # Core types
    "GaloisLoss",
    "ZeroNode",
    "Restructurable",
    # Layers
    "LayerType",
    "compute_layer",
    "stratify_by_loss",
    # Axioms
    "Axiom",
    "EntityAxiom",
    "MorphismAxiom",
    "GaloisGround",
    # Health and governance
    "AxiomHealth",
    "AxiomStatus",
    "AxiomGovernance",
    # Laws
    "GaloisLaw",
    "GALOIS_LAWS",
    # Discovery (3-stage process)
    "MirrorTestOracle",
    "DiscoveryResult",
    "GaloisAxiomDiscovery",
    # Factories
    "create_axiom_kernel",
    "create_axiom_governance",
    # === Bootstrap ===
    # Core types
    "Layer",
    "NodeKind",
    "EdgeKind",
    "Deviation",
    "DEVIATION_CATEGORIES",
    "GaloisOperations",
    "SimpleGaloisLoss",
    "FixedPointVerification",
    "ConvergenceReport",
    "BootstrapWindow",
    "BootstrapReport",
    "BootstrapMark",
    "ZeroSeedPolynomial",
    "StrangeLoopResolution",
    # Functions
    "verify_zero_seed_fixed_point",
    "verify_convergence",
    "extract_deviations",
    "retroactive_witness_bootstrap",
    # === Proof Coherence ===
    # Core types
    "GaloisWitnessedProof",
    "ProofLossDecomposition",
    "Alternative",
    "ProofValidation",
    # Enums
    "EvidenceTier",
    "WitnessMode",
    "TierBounds",
    # Functions
    "classify_by_loss",
    "select_witness_mode_from_loss",
]
