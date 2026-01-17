"""
Zero Seed: The Minimal Generative Kernel with Galois Grounding.

"The proof IS the decision. The mark IS the witness. The seed IS the garden."

Zero Seed provides the foundation for the seven-layer epistemic holarchy,
derived from two axioms and one meta-principle, grounded in Galois
modularization theory:

**Core Axioms (discovered as zero-loss fixed points)**:
- A1 (Entity): Everything is a Node (L=0.002)
- A2 (Morphism): Everything Composes (L=0.003)
- G (Galois Ground): The loss function grounds the axioms (L=0.000)

**Meta-Principle**:
- M (Justification): Every node justifies its existence or admits it cannot

**Key Formulas**:
- Axiom = Zero-loss fixed point: L(P) < 0.01
- Layer = Convergence depth: L_i = min{k : L(R^k(P)) < epsilon}
- Loss = Semantic distance: L(P) = d(P, C(R(P)))

This module exports:
- Core: ZeroNode, ZeroEdge, Proof, EvidenceTier, EdgeKind
- Galois: GaloisLoss, Axiom classes, LayerType, AxiomGovernance
- Layer utilities: Mapping between layers and AGENTESE contexts

Philosophy:
    "Two axioms. One meta-principle. One ground. Seven layers. Infinite gardens."

See: spec/protocols/zero-seed1/axiomatics.md
See: spec/protocols/zero-seed1/core.md
See: docs/skills/crown-jewel-patterns.md
"""

from __future__ import annotations

# ASHC Self-Awareness: The system that knows why it exists
from .ashc_self_awareness import (
    ASHCSelfAwareness,
    ConsistencyReport,
    ConsistencyViolation,
    EvidenceTier as ASHCEvidenceTier,  # Avoid conflict with core.EvidenceTier
    GroundingResult,
    JustificationResult,
    create_ashc_self_awareness,
    get_ashc_self_awareness,
    reset_ashc_self_awareness,
)

# Axiom Discovery Pipeline: Personal axiom discovery from decisions
from .axiom_discovery_pipeline import (
    AxiomCandidate,
    AxiomDiscoveryPipeline,
    AxiomDiscoveryResult,
    ContradictionPair,
    DecisionPattern,
    discover_personal_axioms,
    validate_axiom_candidate,
)

# Axiom AGENTESE Node
from .axiom_node import (
    AxiomDiscoveryRendering,
    AxiomManifestRendering,
    AxiomNode,
)

# Core types
from .core import (
    # Constants
    AXIOM_KINDS,
    AXIOM_LAYERS,
    EDGE_INVERSES,
    EDGE_LAYER_DELTAS,
    LAYER_DESCRIPTIONS,
    LAYER_NAMES,
    VALUE_KINDS,
    # Errors
    CompositionError,
    # Type aliases
    EdgeId,
    # Edge kind taxonomy
    EdgeKind,
    # Evidence tier
    EvidenceTier,
    LayerViolationError,
    MarkIdType,
    NodeId,
    # Proof (Toulmin)
    Proof,
    ProofForbiddenError,
    ProofRequiredError,
    WitnessRequiredError,
    # Core types
    ZeroEdge,
    ZeroNode,
    ZeroSeedError,
    compose_edge_kinds,
    # Layer utilities
    compute_layer_from_proof,
    # AGENTESE mapping
    context_to_layers,
    generate_edge_id,
    generate_node_id,
    # Layer names
    get_layer_description,
    get_layer_name,
    # Identity
    identity_edge,
    layer_of,
    layer_to_context,
    parse_agentese_path,
    proof_depth,
)

# Galois axiomatics: The Galois-grounded minimal kernel
from .galois.axiomatics import (
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
    compute_layer,
    create_axiom_governance,
    create_axiom_kernel,
    stratify_by_loss,
)

# Genesis K-Block Factory: Self-describing seed K-Blocks
from .genesis_kblocks import (
    GenesisKBlock,
    GenesisKBlockFactory,
)

# Note: ZeroNode is imported from core.py, galois.axiomatics has its own ZeroNode
# that's used internally for axiom discovery. They serve different purposes:
# - core.ZeroNode: Runtime knowledge graph node with edges and proofs
# - galois.ZeroNode: Proposition representation for axiom discovery

__all__ = [
    # Type aliases
    "NodeId",
    "EdgeId",
    "MarkIdType",
    "generate_node_id",
    "generate_edge_id",
    # Constants
    "AXIOM_LAYERS",
    "AXIOM_KINDS",
    "VALUE_KINDS",
    "LAYER_NAMES",
    "LAYER_DESCRIPTIONS",
    "EDGE_INVERSES",
    "EDGE_LAYER_DELTAS",
    # Evidence tier
    "EvidenceTier",
    # Proof (Toulmin)
    "Proof",
    # Edge kind taxonomy
    "EdgeKind",
    "compose_edge_kinds",
    # Errors
    "ZeroSeedError",
    "CompositionError",
    "ProofRequiredError",
    "ProofForbiddenError",
    "LayerViolationError",
    "WitnessRequiredError",
    # Core types
    "ZeroNode",
    "ZeroEdge",
    # Layer utilities
    "layer_of",
    "proof_depth",
    "compute_layer_from_proof",
    # AGENTESE mapping
    "layer_to_context",
    "context_to_layers",
    "parse_agentese_path",
    # Layer names
    "get_layer_name",
    "get_layer_description",
    # Identity
    "identity_edge",
    # === Galois Axiomatics ===
    # Constants
    "FIXED_POINT_THRESHOLD",
    "MAX_DEPTH",
    "DRIFT_TOLERANCE",
    "DEFAULT_VOICE_ANCHORS",
    # Core types
    "GaloisLoss",
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
    # === Genesis K-Block Factory ===
    "GenesisKBlock",
    "GenesisKBlockFactory",
    # === ASHC Self-Awareness ===
    "ASHCSelfAwareness",
    "GroundingResult",
    "JustificationResult",
    "ConsistencyReport",
    "ConsistencyViolation",
    "ASHCEvidenceTier",
    "create_ashc_self_awareness",
    "get_ashc_self_awareness",
    "reset_ashc_self_awareness",
    # === Axiom Discovery Pipeline ===
    "AxiomCandidate",
    "AxiomDiscoveryPipeline",
    "AxiomDiscoveryResult",
    "ContradictionPair",
    "DecisionPattern",
    "discover_personal_axioms",
    "validate_axiom_candidate",
    # === Axiom AGENTESE Node ===
    "AxiomNode",
    "AxiomManifestRendering",
    "AxiomDiscoveryRendering",
]
