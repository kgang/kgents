"""
B-gents: Scientific Discovery + Banker Economics

Dual nature:
1. Bio/Scientific Discovery: Hypothesis generation, falsifiability, empirical inquiry
2. Banker Economics: Resource metering, value accounting, economic constraints

Core themes:
- Falsifiability (Popperian epistemology)
- Epistemic humility
- Transparent reasoning
- Resource-constrained systems (metabolic control)
- Linear Logic (tokens consumed, not copied)
- Value Tensor (multi-dimensional accounting)

Currently implemented:

**Bio/Scientific Discovery:**
- HypothesisEngine: Transforms observations into testable hypotheses
- Robin: Personalized scientific companion (composes K-gent + Hypothesis + Hegel)
- PersistentHypothesisStorage: D-gent backed hypothesis persistence with lineage
- Catalog Integration: L-gent registration and discovery for hypotheses

**Banker Economics (Phase 3):**
- Value Tensor: Multi-dimensional resource ontology (Physical, Semantic, Economic, Ethical)
- Metered Functor: Agent[A, B] → Agent[A, Receipt[B]]
- Central Bank: Token accounting with hydraulic refill
- Value Ledger: Universal Value Protocol (UVP) implementation
- RoC Monitor: Return on Compute tracking
"""

from .hypothesis import (
    HypothesisEngine,
    HypothesisInput,
    HypothesisOutput,
    Hypothesis,
    NoveltyLevel,
    hypothesis_engine,
    rigorous_engine,
    exploratory_engine,
)

from .robin import (
    RobinAgent,
    RobinInput,
    RobinOutput,
    robin,
    robin_with_persona,
    quick_robin,
    fallback_robin,
)

from .persistent_hypothesis import (
    HypothesisMemory,
    HypothesisLineageEdge,
    PersistentHypothesisStorage,
    persistent_hypothesis_storage,
)

from .catalog_integration import (
    # Types
    HypothesisCatalogEntry,
    TestResult,
    # Registration
    register_hypothesis,
    register_hypothesis_batch,
    # Discovery
    find_hypotheses,
    find_related_hypotheses,
    # Lineage
    record_hypothesis_evolution,
    record_hypothesis_fork,
    get_hypothesis_lineage,
    # Metrics
    update_hypothesis_metrics,
    mark_hypothesis_falsified,
)

# Banker Economics (Phase 3)
from .value_tensor import (
    # Dimensions
    PhysicalDimension,
    SemanticDimension,
    EconomicDimension,
    EthicalDimension,
    ImpactTier,
    # Exchange
    ExchangeRate,
    ExchangeMatrix,
    create_standard_exchange_rates,
    # Conservation
    ConservationLaw,
    Anomaly,
    AntiDelusionChecker,
    # Tensor
    ValueTensor,
    TensorAlgebra,
)

from .metered_functor import (
    # Currency types
    Gas,
    Impact,
    Receipt,
    # Token accounting
    TokenBucket,
    SinkingFund,
    Loan,
    Denial,
    TokenFuture,
    FuturesMarket,
    # Auction
    Bid,
    Allocation,
    priority_auction,
    # Central Bank
    CentralBank,
    InsufficientFundsError,
    # Budgets
    EntropyBudget,
    DualBudget,
    # Functor
    Metered,
    meter,
    metered_invoke,
)

from .value_ledger import (
    # Oracles
    ComplexityOracle,
    ValueOracle,
    # Output types
    SimpleOutput,
    # Regulation
    EthicalRegulator,
    # Accounting
    Treasury,
    BalanceSheet,
    TransactionReceipt,
    ValueLedger,
    # Monitoring
    RoCThresholds,
    RoCAssessment,
    RoCMonitor,
)

# Compression Economy (Phase 4: Structural Economics B×G Integration)
from .compression_economy import (
    # Types
    AdoptionStatus,
    CommunicationLog,
    CompressionROI,
    PidginMetadata,
    PidginAvailable,
    BudgetDecision,
    # Classes
    CommunicationTracker,
    CompressionROICalculator,
    CompressionEconomyMonitor,
    SemanticZipperBudget,
    # Convenience functions
    create_compression_monitor,
    create_zipper_budget,
    analyze_compression_opportunity,
)

__all__ = [
    # HypothesisEngine
    "HypothesisEngine",
    "HypothesisInput",
    "HypothesisOutput",
    "Hypothesis",
    "NoveltyLevel",
    "hypothesis_engine",
    "rigorous_engine",
    "exploratory_engine",
    # Robin (scientific companion)
    "RobinAgent",
    "RobinInput",
    "RobinOutput",
    "robin",
    "robin_with_persona",
    "quick_robin",
    "fallback_robin",
    # Persistent Storage (D-gent integration)
    "HypothesisMemory",
    "HypothesisLineageEdge",
    "PersistentHypothesisStorage",
    "persistent_hypothesis_storage",
    # Catalog Integration (L-gent integration)
    "HypothesisCatalogEntry",
    "TestResult",
    "register_hypothesis",
    "register_hypothesis_batch",
    "find_hypotheses",
    "find_related_hypotheses",
    "record_hypothesis_evolution",
    "record_hypothesis_fork",
    "get_hypothesis_lineage",
    "update_hypothesis_metrics",
    "mark_hypothesis_falsified",
    # Value Tensor (Phase 3)
    "PhysicalDimension",
    "SemanticDimension",
    "EconomicDimension",
    "EthicalDimension",
    "ImpactTier",
    "ExchangeRate",
    "ExchangeMatrix",
    "create_standard_exchange_rates",
    "ConservationLaw",
    "Anomaly",
    "AntiDelusionChecker",
    "ValueTensor",
    "TensorAlgebra",
    # Metered Functor (Phase 3)
    "Gas",
    "Impact",
    "Receipt",
    "TokenBucket",
    "SinkingFund",
    "Loan",
    "Denial",
    "TokenFuture",
    "FuturesMarket",
    "Bid",
    "Allocation",
    "priority_auction",
    "CentralBank",
    "InsufficientFundsError",
    "EntropyBudget",
    "DualBudget",
    "Metered",
    "meter",
    "metered_invoke",
    # Value Ledger (Phase 3)
    "ComplexityOracle",
    "ValueOracle",
    "SimpleOutput",
    "EthicalRegulator",
    "Treasury",
    "BalanceSheet",
    "TransactionReceipt",
    "ValueLedger",
    "RoCThresholds",
    "RoCAssessment",
    "RoCMonitor",
    # Compression Economy (Phase 4: Structural Economics B×G)
    "AdoptionStatus",
    "CommunicationLog",
    "CompressionROI",
    "PidginMetadata",
    "PidginAvailable",
    "BudgetDecision",
    "CommunicationTracker",
    "CompressionROICalculator",
    "CompressionEconomyMonitor",
    "SemanticZipperBudget",
    "create_compression_monitor",
    "create_zipper_budget",
    "analyze_compression_opportunity",
]
