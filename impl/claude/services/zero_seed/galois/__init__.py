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
8. **Difficulty Measure**: Ground-truth D(P) = H(P) × (1 - S(P))

Key Formulas:
- Axiom = Zero-loss fixed point: L(P) < 0.01
- Layer = Convergence depth: L_i = min{k : L(R^k(P)) < epsilon}
- Loss = Semantic distance: L(P) = d(P, C(R(P)))
- Difficulty = Entropy × Failure: D(P) = H(P) × (1 - S(P))
- Coherence = 1 - galois_loss(P)
- Bootstrap: Zero Seed = Fix(R o describe), L(ZS) < 0.15 (85% regenerability)

The Three Axioms (discovered, not stipulated):
- A1: Entity Axiom - Universal representability (L=0.002)
- A2: Morphism Axiom - Composition primacy (L=0.003)
- G: Galois Ground - The loss function as axiomatic ground (L=0.000)

Difficulty Axioms (D(P) Axiomatization):
- A_D1: D(P) ∈ [0, ∞) — non-negative
- A_D2: D(trivial) ≈ 0 — trivial prompts have near-zero difficulty
- A_D3: D(P₁ ∘ P₂) ≤ D(P₁) + D(P₂) — composition sub-additive
- A_D4: D(impossible) = ∞ — impossible tasks have infinite difficulty

See: spec/protocols/zero-seed1/axiomatics.md
See: spec/protocols/zero-seed1/bootstrap.md
See: spec/protocols/zero-seed1/proof.md
See: spec/theory/galois-modularization.md
See: plans/theory-operationalization/02-galois-theory.md (D(P) Axiomatization)
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
    # Discovery (3-stage process from axiomatics.md)
    DiscoveryResult,
    EntityAxiom,
    GaloisAxiomDiscovery,
    GaloisGround,
    GaloisLaw,
    # Core types
    GaloisLoss,
    LayerType,
    MirrorTestOracle,
    MorphismAxiom,
    Restructurable,
    ZeroNode,
    compute_layer,
    create_axiom_governance,
    create_axiom_kernel,
    stratify_by_loss,
)

# Bootstrap: Lawvere fixed point verification
from .bootstrap import (
    DEVIATION_CATEGORIES,
    BootstrapMark,
    BootstrapReport,
    BootstrapWindow,
    ConvergenceReport,
    Deviation,
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

# Difficulty Measure (D(P) Axiomatization - Gap Fix)
from .difficulty import (
    DEFAULT_CLUSTER_THRESHOLD,
    DEFAULT_ENTROPY_SAMPLES,
    DEFAULT_SUCCESS_TRIALS,
    DifficultyComparison,
    DifficultyComputer,
    DifficultyMeasure,
    compute_shannon_entropy,
    create_difficulty_measure,
    estimate_entropy_from_clusters,
    verify_impossible_singularity,
    verify_sub_additivity,
    verify_trivial_grounding,
)

# Canonical Semantic Distance (Amendment B)
from .distance import (
    BidirectionalEntailmentDistance,
    CanonicalSemanticDistance,
    canonical_semantic_distance,
    get_canonical_metric,
    get_entailment_metric,
)

# Fixed-Point Detection (Amendment F)
from .fixed_point import (
    MAX_STABILITY_ITERATIONS,
    STABILITY_THRESHOLD,
    FixedPointMetrics,
    FixedPointResult,
    batch_detect_fixed_points,
    compute_fixed_point_metrics,
    detect_fixed_point,
    extract_axioms,
)

# Core Galois Loss Computer (DI integration)
# Note: GaloisLoss is imported from axiomatics above (the canonical source)
from .galois_loss import (  # type: ignore[assignment]
    EvidenceTier,
    GaloisLossComputer,
    classify_evidence_tier,
    compute_galois_loss_async,
)

# Layer Assignment (Amendment C)
from .layer_assignment import (
    CALIBRATION_CORPUS,
    CALIBRATION_CORPUS_PATH,
    LAYER_LOSS_BOUNDS,
    LAYER_NAMES,
    MIN_CORPUS_SIZE,
    CalibrationCorpus,
    CalibrationEntry,
    CalibrationReport,
    CalibrationResult,
    LayerAssigner,
    LayerAssignment,
    assign_layer_absolute,
    assign_layer_relative,
    load_calibration_corpus,
    validate_calibration,
    validate_calibration_full,
)

# Proof coherence: Toulmin proofs with Galois loss
from .proof import (
    Alternative,
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
    # === Galois Loss Computer (DI integration) ===
    "GaloisLossComputer",
    "classify_evidence_tier",
    "compute_galois_loss_async",
    # === Fixed-Point Detection (Amendment F) ===
    "STABILITY_THRESHOLD",
    "MAX_STABILITY_ITERATIONS",
    "FixedPointResult",
    "FixedPointMetrics",
    "detect_fixed_point",
    "extract_axioms",
    "batch_detect_fixed_points",
    "compute_fixed_point_metrics",
    # === Layer Assignment (Amendment C) ===
    "LAYER_NAMES",
    "LAYER_LOSS_BOUNDS",
    "MIN_CORPUS_SIZE",
    "CALIBRATION_CORPUS",
    "CALIBRATION_CORPUS_PATH",
    "LayerAssignment",
    "LayerAssigner",
    "assign_layer_absolute",
    "assign_layer_relative",
    "validate_calibration",
    "validate_calibration_full",
    "load_calibration_corpus",
    "CalibrationEntry",
    "CalibrationCorpus",
    "CalibrationResult",
    "CalibrationReport",
    # === Canonical Semantic Distance (Amendment B) ===
    "BidirectionalEntailmentDistance",
    "CanonicalSemanticDistance",
    "canonical_semantic_distance",
    "get_canonical_metric",
    "get_entailment_metric",
    # === Difficulty Measure (D(P) Axiomatization) ===
    "DEFAULT_ENTROPY_SAMPLES",
    "DEFAULT_SUCCESS_TRIALS",
    "DEFAULT_CLUSTER_THRESHOLD",
    "DifficultyMeasure",
    "DifficultyComparison",
    "DifficultyComputer",
    "compute_shannon_entropy",
    "estimate_entropy_from_clusters",
    "verify_sub_additivity",
    "verify_trivial_grounding",
    "verify_impossible_singularity",
    "create_difficulty_measure",
]
