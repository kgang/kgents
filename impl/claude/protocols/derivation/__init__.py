"""
Derivation Framework: CONSTITUTION as Axiomatic Root.

The derivation DAG has a single root: CONSTITUTION (AXIOM tier).
All bootstrap agents derive from CONSTITUTION, making the hierarchy explicit:

    CONSTITUTION (AXIOM tier, confidence = 1.0)
         |
         +-- Id, Compose, Judge, Ground, Contradict, Sublate, Fix (BOOTSTRAP tier)
                   |
                   +-- Flux, Cooled, etc. (FUNCTOR tier)
                            |
                            +-- ... (lower tiers)

This module implements the Derivation Framework from
spec/protocols/derivation-framework.md:

Phase 1 (Core):
- Derivation: A morphism from bootstrap axioms to a derived agent
- PrincipleDraw: Evidence that an agent instantiates a principle
- DerivationRegistry: Global registry of agent derivations

Phase 2 (ASHC Integration):
- extract_principle_evidence: Map ASHC results to principle draws
- update_derivation_from_ashc: Bridge ASHC evidence to derivations
- sync_from_principle_registry: Bridge causal penalty credibility
- lemma_strengthens_derivation: Add categorical evidence from formal proofs

Phase 3 (Witness Integration):
- mark_updates_stigmergy: Marks increment agent usage counts
- denial_weakens_derivation: Challenges decay principle draws
- walk_updates_derivations: Batch updates from walks
- DifferentialDenial: Conceptual type for challenges

Phase 4 (Decay & Refresh):
- apply_evidence_decay: Time-based decay for non-categorical evidence
- apply_stigmergic_decay: Inactivity-based decay for unused agents
- apply_ashc_refresh: Periodic ASHC refresh to update empirical evidence
- run_decay_cycle: Full decay cycle (all three mechanisms)
- ActivityRecord, RefreshSchedule: Tracking types for decay

Phase 6 (Cross-Protocol Integration):
- TrailEvidence, apply_trail_evidence: Exploration Harness → Derivation bridge
- PortalOpenSignal, PortalDerivationSync: Portal Token ↔ Derivation bidirectional sync
- DerivationHyperedgeResolver: Typed-Hypergraph navigation layer for derivations
- ConfidenceGateResult, check_operation_confidence: File Operad confidence gating

The key insight: Bootstrap agents have categorical proofs (confidence = 1.0).
Derived agents inherit confidence probabilistically. Evidence accumulates,
decays, and updates via ASHC and Witness marks.

    "Bootstrap confidence is given. Derived confidence is earned."
    "Every agent can trace its lineage to Id, Compose, or Ground."
    "The proof IS the decision. The mark IS the witness."

Teaching:
    gotcha: Derivation.total_confidence has a tier ceiling. No amount of
            evidence lets an APP agent exceed 0.75 confidence.
            (Law 2: Confidence Ceiling)

    gotcha: The derivation graph is a DAG. Cycles are rejected at registration.
            (Law 4: Acyclicity)

    gotcha: Bootstrap agents are indefeasible. Their confidence never decays.
            (Law 3: Bootstrap Indefeasibility)

    gotcha: ASHC evidence is EMPIRICAL, not CATEGORICAL. Even 100% pass
            rate doesn't make it categorical—that requires formal proofs.
            (Phase 2: ASHC Integration)

    gotcha: Categorical evidence is never weakened by DifferentialDenials.
            If a principle has categorical evidence, denials are logged but
            the draw_strength remains 1.0.
            (Phase 3: Witness Integration)

    gotcha: Stigmergic decay has a grace period (14 days by default).
            Recently active agents don't decay even if usage is low.
            (Phase 4: Decay & Refresh)

See spec/protocols/derivation-framework.md for full specification.
See spec/bootstrap.md for the axiom base.
"""

# Phase 3B: Witnessed Edges (Evidence on Edges)
# Phase 2: ASHC Integration
from .ashc_bridge import (
    extract_principle_evidence,
    lemma_strengthens_derivation,
    merge_principle_draws,
    sync_from_principle_registry,
    sync_to_principle_registry,
    update_derivation_from_ashc,
)
from .bootstrap import (
    BOOTSTRAP_AGENT_NAMES,
    CONSTITUTION_DERIVATION,
    SEVEN_PRINCIPLES,
)

# Phase 4: Decay & Refresh
from .decay import (
    DEFAULT_CONFIG,
    # Activity tracking
    ActivityRecord,
    # Configuration
    DecayConfig,
    # Full cycle
    DecayCycleResult,
    InMemoryActivityStore,
    InMemoryRefreshStore,
    # ASHC refresh
    RefreshSchedule,
    apply_ashc_refresh,
    apply_evidence_decay,
    apply_stigmergic_decay,
    # Stigmergic decay
    calculate_stigmergic_decay,
    decay_derivation_evidence,
    # Evidence decay
    decay_principle_draw,
    get_activity_store,
    get_refresh_store,
    record_activity,
    reset_activity_store,
    reset_refresh_store,
    run_decay_cycle,
    set_activity_store,
    should_refresh_agent,
)
from .edges import (
    DerivationRationale,
    EdgeType,
    PrincipleFlow,
    WitnessedEdge,
)

# Phase 6: Cross-Protocol Integration
from .exploration_bridge import (
    TrailEvidence,
    apply_trail_evidence,
    apply_trail_evidence_async,
    batch_apply_trail_evidence,
    merge_trail_evidence,
    trail_to_derivation_evidence,
)
from .file_operad_bridge import (
    DEFAULT_THRESHOLDS,
    ConfidenceGateResult,
    FileOperationRequest,
    FileOperationResult,
    OperationThresholds,
    check_multiple_operations,
    check_operation_confidence,
    gate_and_execute,
    gate_file_operation,
    get_agent_capabilities,
)
from .hypergraph_bridge import (
    DERIVATION_EDGE_TYPES,
    ContextNode as DerivationContextNode,
    DerivationHyperedgeResolver,
    SimpleObserver,
    get_derivation_graph_for_agent,
    get_derivation_resolver,
    register_derivation_resolvers,
    reset_derivation_resolver,
    resolve_derivation_edge,
)
from .portal_bridge import (
    PortalDerivationSync,
    PortalOpenSignal,
    agent_name_to_paths,
    derivation_to_portal_trust,
    get_trust_for_path,
    path_to_agent_name,
    portal_expansion_to_derivation,
    sync_portal_expansion,
)
from .registry import DerivationRegistry, get_registry, reset_registry
from .types import (
    Derivation,
    DerivationTier,
    EvidenceType,
    PrincipleDraw,
)

# Phase 3: Witness Integration
from .witness_bridge import (
    DifferentialDenial,
    denial_weakens_derivation,
    extract_agents_from_mark,
    mark_updates_stigmergy,
    sync_witness_to_derivations,
    walk_updates_derivations,
)

__all__ = [
    # Phase 1: Core Types
    "Derivation",
    "DerivationTier",
    "PrincipleDraw",
    "EvidenceType",
    # Phase 1: Bootstrap (CONSTITUTION as Root)
    "CONSTITUTION_DERIVATION",
    "SEVEN_PRINCIPLES",
    "BOOTSTRAP_AGENT_NAMES",
    # Phase 1: Registry
    "DerivationRegistry",
    "get_registry",
    "reset_registry",
    # Phase 2: ASHC Bridge
    "extract_principle_evidence",
    "merge_principle_draws",
    "update_derivation_from_ashc",
    "sync_from_principle_registry",
    "sync_to_principle_registry",
    "lemma_strengthens_derivation",
    # Phase 3: Witness Bridge
    "DifferentialDenial",
    "extract_agents_from_mark",
    "mark_updates_stigmergy",
    "denial_weakens_derivation",
    "walk_updates_derivations",
    "sync_witness_to_derivations",
    # Phase 3B: Witnessed Edges
    "EdgeType",
    "PrincipleFlow",
    "DerivationRationale",
    "WitnessedEdge",
    # Phase 4: Decay & Refresh
    "DecayConfig",
    "DEFAULT_CONFIG",
    "ActivityRecord",
    "InMemoryActivityStore",
    "get_activity_store",
    "set_activity_store",
    "reset_activity_store",
    "record_activity",
    "decay_principle_draw",
    "decay_derivation_evidence",
    "apply_evidence_decay",
    "calculate_stigmergic_decay",
    "apply_stigmergic_decay",
    "RefreshSchedule",
    "InMemoryRefreshStore",
    "get_refresh_store",
    "reset_refresh_store",
    "should_refresh_agent",
    "apply_ashc_refresh",
    "DecayCycleResult",
    "run_decay_cycle",
    # Phase 6: Exploration Bridge
    "TrailEvidence",
    "apply_trail_evidence",
    "apply_trail_evidence_async",
    "trail_to_derivation_evidence",
    "merge_trail_evidence",
    "batch_apply_trail_evidence",
    # Phase 6: Portal Bridge
    "path_to_agent_name",
    "agent_name_to_paths",
    "PortalOpenSignal",
    "PortalDerivationSync",
    "portal_expansion_to_derivation",
    "derivation_to_portal_trust",
    "sync_portal_expansion",
    "get_trust_for_path",
    # Phase 6: Hypergraph Bridge
    "DERIVATION_EDGE_TYPES",
    "DerivationContextNode",
    "SimpleObserver",
    "DerivationHyperedgeResolver",
    "get_derivation_resolver",
    "reset_derivation_resolver",
    "register_derivation_resolvers",
    "resolve_derivation_edge",
    "get_derivation_graph_for_agent",
    # Phase 6: File Operad Bridge
    "OperationThresholds",
    "DEFAULT_THRESHOLDS",
    "ConfidenceGateResult",
    "FileOperationRequest",
    "FileOperationResult",
    "check_operation_confidence",
    "gate_file_operation",
    "gate_and_execute",
    "check_multiple_operations",
    "get_agent_capabilities",
]
