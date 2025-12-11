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
# Dimension Z: Axiology
from .axiological import (
    AgentRanking,
    # Axiological observer
    AxiologicalObserver,
    EconomicAnomaly,
    EconomicHealthReport,
    # Economic types
    EconomicStatus,
    # Auditing
    LedgerAuditor,
    # RoC monitoring
    RoCAlert,
    RoCMonitor,
    RoCSnapshot,
    RoCThresholds,
    SimpleBalanceSheet,
    # Simple ledger (standalone)
    SimpleTreasury,
    SimpleValueLedger,
    TensorValidationReport,
    TensorValidator,
    # Value observers
    ValueLedgerObserver,
    create_axiological_observer,
    create_ledger_auditor,
    create_roc_monitor,
    create_tensor_validator,
    # Convenience
    create_value_ledger,
    create_value_ledger_observer,
)
from .observer import (
    # Protocols and base types
    Agent,
    BaseObserver,
    # Composite
    CompositeObserver,
    EntropyEvent,
    ObservationContext,
    ObservationResult,
    # Context and result types
    ObservationStatus,
    Observer,
    # Observer functor
    ObserverFunctor,
    ObserverHierarchy,
    # Hierarchy
    ObserverLevel,
    ProprioceptiveWrapper,
    StratifiedObserver,
    create_composite,
    create_functor,
    create_hierarchy,
    # Convenience
    create_observer,
    observe,
)

# Dimension Y: Semantics
from .semantic import (
    BorromeanObserver,
    DriftAlert,
    DriftDetector,
    DriftMeasurer,
    DriftReport,
    # Drift detection
    DriftSeverity,
    HallucinationDetector,
    # Hallucination detection
    HallucinationReport,
    ImaginaryHealth,
    KnotHealth,
    PsychosisAlert,
    RealHealth,
    # Semantic observer
    SemanticObserver,
    SimpleDriftMeasurer,
    # Borromean knot
    SymbolicHealth,
    create_borromean_observer,
    # Convenience
    create_drift_detector,
    create_hallucination_detector,
    create_semantic_observer,
)

# Dimension X: Telemetry
from .telemetry import (
    # Topology mapping
    CompositionEdge,
    CompositionGraph,
    HistogramBucket,
    HistogramValue,
    MetricsCollector,
    # Metrics types
    MetricType,
    MetricValue,
    # Telemetry observer
    TelemetryObserver,
    TopologyMapper,
    TopologyNode,
    TopologyObserver,
    # Convenience
    create_metrics_collector,
    create_telemetry_observer,
    create_topology_mapper,
    create_topology_observer,
)

# VoI Integration
from .voi_observer import (
    Panopticon,
    # Panopticon dashboard
    PanopticonStatus,
    # VoI observer
    VoIAwareObserver,
    VoIBudgetAllocation,
    # VoI types
    VoIObservationConfig,
    VoIObservationResult,
    create_full_observer_stack,
    create_panopticon,
    # Convenience
    create_voi_aware_observer,
)

# Re-export ObservationDepth and FindingType for VoI integration
try:
    from .voi_observer import FindingType, ObservationDepth
except ImportError:
    pass  # Already defined in voi_observer.py

# Panopticon Integration (O-gent Phase 3)
# Bootstrap Witness (O-gent Phase 2)
from .bootstrap_witness import (
    # Result types
    AgentExistenceResult,
    BootstrapAgent,
    BootstrapObserver,
    BootstrapVerificationResult,
    # Observers
    BootstrapWitness,
    ComposedAgent,
    CompositionLawResult,
    # Agents
    IdentityAgent,
    IdentityLawResult,
    TestAgent,
    # Verdict types
    Verdict,
    create_bootstrap_observer,
    # Convenience
    create_bootstrap_witness,
    render_verification_dashboard,
    verify_bootstrap,
    verify_composition_laws,
    verify_identity_laws,
)

# Cortex Observer (Instance DB Phase 6)
from .cortex_observer import (
    CoherencyStatus,
    # Health enums
    CortexHealth,
    CortexHealthSnapshot,
    # Observer
    CortexObserver,
    # Config
    CortexObserverConfig,
    DreamerStatus,
    HippocampusStatus,
    # Status types
    LeftHemisphereStatus,
    RightHemisphereStatus,
    SynapseStatus,
    # Factory
    create_cortex_observer,
    create_mock_cortex_observer,
)

# Metrics Export (Instance DB Phase 6)
from .metrics_export import (
    JSONExporter,
    # Types
    Metric,
    MetricsExportConfig,
    # Exporters
    MetricsExporter,
    OpenTelemetryExporter,
    PrometheusExporter,
    # Factory
    create_metrics_exporter,
    create_otel_exporter,
)
from .panopticon import (
    AlertSeverity,
    AxiologicalStatus,
    BootstrapStatus,
    # Integrated Panopticon
    IntegratedPanopticon,
    # Alert type
    PanopticonAlert,
    # Observer wrapper
    PanopticonObserver,
    SemanticStatus,
    # Status enums
    SystemStatus,
    # Dimension status types
    TelemetryStatus,
    # Unified status
    UnifiedPanopticonStatus,
    VoIStatus,
    # Factory functions
    create_integrated_panopticon,
    create_minimal_panopticon,
    create_panopticon_observer,
    create_verified_panopticon,
    render_compact_status,
    render_dimensions_summary,
    # Rendering functions
    render_unified_dashboard,
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
    # === Panopticon Integration (O-gent Phase 3) ===
    # Status enums
    "SystemStatus",
    "AlertSeverity",
    # Alert type
    "PanopticonAlert",
    # Dimension status types
    "TelemetryStatus",
    "SemanticStatus",
    "AxiologicalStatus",
    "BootstrapStatus",
    "VoIStatus",
    # Unified status
    "UnifiedPanopticonStatus",
    # Integrated Panopticon
    "IntegratedPanopticon",
    # Observer wrapper
    "PanopticonObserver",
    # Rendering functions
    "render_unified_dashboard",
    "render_compact_status",
    "render_dimensions_summary",
    # Factory functions
    "create_integrated_panopticon",
    "create_minimal_panopticon",
    "create_verified_panopticon",
    "create_panopticon_observer",
    # === Cortex Observer (Instance DB Phase 6) ===
    # Health enums
    "CortexHealth",
    # Status types
    "LeftHemisphereStatus",
    "RightHemisphereStatus",
    "CoherencyStatus",
    "SynapseStatus",
    "HippocampusStatus",
    "DreamerStatus",
    "CortexHealthSnapshot",
    # Config
    "CortexObserverConfig",
    # Observer
    "CortexObserver",
    # Factory
    "create_cortex_observer",
    "create_mock_cortex_observer",
    # === Metrics Export (Instance DB Phase 6) ===
    # Types
    "Metric",
    "MetricsExportConfig",
    # Exporters
    "MetricsExporter",
    "PrometheusExporter",
    "OpenTelemetryExporter",
    "JSONExporter",
    # Factory
    "create_metrics_exporter",
    "create_otel_exporter",
]
