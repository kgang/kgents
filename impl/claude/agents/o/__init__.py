"""
O-gents: The Epistemic Substrate

Systemic Proprioception for Agent Systems.

O-gents provide the innate ability of the system to sense its own cognitive posture.
Like biological proprioception enables body coordination, O-gents enable system
self-awareness across three dimensions:

- **Dimension X (Telemetry)**: "Is it running?" - Latency, errors, throughput
- **Dimension Y (Semantics)**: "Does it mean what it says?" - Drift, hallucinations
- **Dimension Z (Axiology)**: "Is it worth the cost?" - RoC, conservation laws

Key Principles:
1. Observation doesn't mutate (outputs unchanged)
2. Observation doesn't block (async, non-blocking)
3. Observation doesn't leak (data stays within boundaries)
4. Observation enables (self-knowledge enables improvement)

VoI Integration:
O-gents are subject to the Value of Information framework from B-gents.
Each observation must justify its cost.

Example:
    from agents.o import (
        observe,
        create_panopticon,
        create_voi_aware_observer,
    )

    # Simple observation
    observed_agent = observe(my_agent)
    result = await observed_agent.invoke(input_data)

    # Full observation stack with dashboard
    composite, panopticon = create_full_observer_stack()
    print(panopticon.render_dashboard())
"""

# Core observer types
from .observer import (
    # Protocols and base types
    Agent,
    Observer,
    BaseObserver,
    # Context and result types
    ObservationStatus,
    ObservationContext,
    ObservationResult,
    EntropyEvent,
    # Observer functor
    ObserverFunctor,
    ProprioceptiveWrapper,
    # Hierarchy
    ObserverLevel,
    StratifiedObserver,
    ObserverHierarchy,
    # Composite
    CompositeObserver,
    # Convenience
    create_observer,
    create_functor,
    observe,
    create_hierarchy,
    create_composite,
)

# Dimension X: Telemetry
from .telemetry import (
    # Metrics types
    MetricType,
    MetricValue,
    HistogramBucket,
    HistogramValue,
    MetricsCollector,
    # Telemetry observer
    TelemetryObserver,
    # Topology mapping
    CompositionEdge,
    TopologyNode,
    CompositionGraph,
    TopologyMapper,
    TopologyObserver,
    # Convenience
    create_metrics_collector,
    create_telemetry_observer,
    create_topology_mapper,
    create_topology_observer,
)

# Dimension Y: Semantics
from .semantic import (
    # Drift detection
    DriftSeverity,
    DriftAlert,
    DriftReport,
    DriftMeasurer,
    SimpleDriftMeasurer,
    DriftDetector,
    # Borromean knot
    SymbolicHealth,
    RealHealth,
    ImaginaryHealth,
    PsychosisAlert,
    KnotHealth,
    BorromeanObserver,
    # Semantic observer
    SemanticObserver,
    # Hallucination detection
    HallucinationReport,
    HallucinationDetector,
    # Convenience
    create_drift_detector,
    create_borromean_observer,
    create_semantic_observer,
    create_hallucination_detector,
)

# Dimension Z: Axiology
from .axiological import (
    # Economic types
    EconomicStatus,
    AgentRanking,
    EconomicAnomaly,
    EconomicHealthReport,
    # Simple ledger (standalone)
    SimpleTreasury,
    SimpleBalanceSheet,
    SimpleValueLedger,
    # Value observers
    ValueLedgerObserver,
    TensorValidator,
    TensorValidationReport,
    # RoC monitoring
    RoCAlert,
    RoCSnapshot,
    RoCThresholds,
    RoCMonitor,
    # Auditing
    LedgerAuditor,
    # Axiological observer
    AxiologicalObserver,
    # Convenience
    create_value_ledger,
    create_value_ledger_observer,
    create_tensor_validator,
    create_roc_monitor,
    create_ledger_auditor,
    create_axiological_observer,
)

# VoI Integration
from .voi_observer import (
    # VoI types
    VoIObservationConfig,
    VoIObservationResult,
    VoIBudgetAllocation,
    # VoI observer
    VoIAwareObserver,
    # Panopticon dashboard
    PanopticonStatus,
    Panopticon,
    # Convenience
    create_voi_aware_observer,
    create_panopticon,
    create_full_observer_stack,
)

# Re-export ObservationDepth and FindingType for VoI integration
try:
    from .voi_observer import ObservationDepth, FindingType
except ImportError:
    pass  # Already defined in voi_observer.py

# Bootstrap Witness (O-gent Phase 2)
from .bootstrap_witness import (
    # Verdict types
    Verdict,
    BootstrapAgent,
    # Result types
    AgentExistenceResult,
    IdentityLawResult,
    CompositionLawResult,
    BootstrapVerificationResult,
    # Agents
    IdentityAgent,
    ComposedAgent,
    TestAgent,
    # Observers
    BootstrapWitness,
    BootstrapObserver,
    # Convenience
    create_bootstrap_witness,
    create_bootstrap_observer,
    verify_bootstrap,
    verify_identity_laws,
    verify_composition_laws,
    render_verification_dashboard,
)


__all__ = [
    # === Core Observer ===
    # Protocols and base types
    "Agent",
    "Observer",
    "BaseObserver",
    # Context and result types
    "ObservationStatus",
    "ObservationContext",
    "ObservationResult",
    "EntropyEvent",
    # Observer functor
    "ObserverFunctor",
    "ProprioceptiveWrapper",
    # Hierarchy
    "ObserverLevel",
    "StratifiedObserver",
    "ObserverHierarchy",
    # Composite
    "CompositeObserver",
    # Core convenience
    "create_observer",
    "create_functor",
    "observe",
    "create_hierarchy",
    "create_composite",
    # === Dimension X: Telemetry ===
    # Metrics types
    "MetricType",
    "MetricValue",
    "HistogramBucket",
    "HistogramValue",
    "MetricsCollector",
    # Telemetry observer
    "TelemetryObserver",
    # Topology mapping
    "CompositionEdge",
    "TopologyNode",
    "CompositionGraph",
    "TopologyMapper",
    "TopologyObserver",
    # Telemetry convenience
    "create_metrics_collector",
    "create_telemetry_observer",
    "create_topology_mapper",
    "create_topology_observer",
    # === Dimension Y: Semantics ===
    # Drift detection
    "DriftSeverity",
    "DriftAlert",
    "DriftReport",
    "DriftMeasurer",
    "SimpleDriftMeasurer",
    "DriftDetector",
    # Borromean knot
    "SymbolicHealth",
    "RealHealth",
    "ImaginaryHealth",
    "PsychosisAlert",
    "KnotHealth",
    "BorromeanObserver",
    # Semantic observer
    "SemanticObserver",
    # Hallucination detection
    "HallucinationReport",
    "HallucinationDetector",
    # Semantic convenience
    "create_drift_detector",
    "create_borromean_observer",
    "create_semantic_observer",
    "create_hallucination_detector",
    # === Dimension Z: Axiology ===
    # Economic types
    "EconomicStatus",
    "AgentRanking",
    "EconomicAnomaly",
    "EconomicHealthReport",
    # Simple ledger (standalone)
    "SimpleTreasury",
    "SimpleBalanceSheet",
    "SimpleValueLedger",
    # Value observers
    "ValueLedgerObserver",
    "TensorValidator",
    "TensorValidationReport",
    # RoC monitoring
    "RoCAlert",
    "RoCSnapshot",
    "RoCThresholds",
    "RoCMonitor",
    # Auditing
    "LedgerAuditor",
    # Axiological observer
    "AxiologicalObserver",
    # Axiological convenience
    "create_value_ledger",
    "create_value_ledger_observer",
    "create_tensor_validator",
    "create_roc_monitor",
    "create_ledger_auditor",
    "create_axiological_observer",
    # === VoI Integration ===
    # VoI types
    "VoIObservationConfig",
    "VoIObservationResult",
    "VoIBudgetAllocation",
    "ObservationDepth",
    "FindingType",
    # VoI observer
    "VoIAwareObserver",
    # Panopticon dashboard
    "PanopticonStatus",
    "Panopticon",
    # VoI convenience
    "create_voi_aware_observer",
    "create_panopticon",
    "create_full_observer_stack",
    # === Bootstrap Witness (O-gent Phase 2) ===
    # Verdict types
    "Verdict",
    "BootstrapAgent",
    # Result types
    "AgentExistenceResult",
    "IdentityLawResult",
    "CompositionLawResult",
    "BootstrapVerificationResult",
    # Agents
    "IdentityAgent",
    "ComposedAgent",
    "TestAgent",
    # Observers
    "BootstrapWitness",
    "BootstrapObserver",
    # Bootstrap convenience
    "create_bootstrap_witness",
    "create_bootstrap_observer",
    "verify_bootstrap",
    "verify_identity_laws",
    "verify_composition_laws",
    "render_verification_dashboard",
]
