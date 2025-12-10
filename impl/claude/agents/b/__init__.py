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

**Banker Economics (Phase 4):**
- VoI (Value of Information): Economics of observation for O-gent integration
- Epistemic Capital: Third currency for knowledge-about-the-system
- VoI Ledger: Observation economics tracking
- VoI Optimizer: Observation budget allocation
- Adaptive Observer: Dynamic observation frequency
- Unified Value Accounting: UVP + VoI integration

**Structural Economics B×G Phase 1 (Compression Economy):**
- Semantic Zipper: Compress inter-agent communication via domain-specific pidgins
- Natural Language Tax: Economic pressure to adopt compressed languages
- Communication Tracker: Monitor inter-agent message costs
- Compression ROI Calculator: Determine when pidgin synthesis is justified

**Structural Economics B×G Phase 2 (Fiscal Constitution):**
- LedgerTongue: Constitutional grammar where bankruptcy is grammatically impossible
- Parse-time Balance Checking: Invariants enforced BEFORE execution
- Constitutional Banker: Grammar-based financial safety enforcement
- Double-entry Bookkeeping: All transactions balance (credits = debits)

**Structural Economics B×G Phase 3 (Syntax Tax):**
- Chomsky-based Pricing: Price operations by grammar complexity (Type 0-3)
- Grammar Classifier: Analyze grammars to determine Chomsky level
- Syntax Tax Schedule: Cost tiers (Regular < Context-Free < Context-Sensitive < Turing-Complete)
- Escrow for Turing-Complete: Safety deposits for high-risk grammars
- Downgrade Negotiation: Help agents choose cheaper grammars when budget-constrained

**Structural Economics B×G Phase 4 (Semantic Inflation):**
- Complexity → Verbosity Pressure: Higher complexity demands more explanation tokens
- ComplexityVector: Multi-dimensional complexity measurement (structural, temporal, conceptual, etc.)
- AudienceProfile: Audience gap calculation for explanation targeting
- InflationBudget: Token allocation between content and explanation
- DeflationNegotiator: Compression strategies when budget constrained
- SemanticCPIMonitor: System-wide inflation tracking (like economic CPI)

**Structural Economics B×G Phase 5 (Grammar Insurance):**
- Grammar Volatility: Measure stability of grammar usage (parse failures, version changes)
- Insurance Policies: Coverage for grammar failures with fallback strategies
- Premium Pricing: Cost based on volatility, complexity, claims history
- Hedging Strategies: Fallback, Redundant, Versioned, Ensemble, Graceful
- Portfolio Analysis: Risk assessment for insured grammars

**Structural Economics B×G Phase 6 (JIT Efficiency):**
- G+J+B Trio: Grammar definition → JIT compilation → Latency value measurement
- JIT Compilers: Regex, JumpTable, Bytecode targets for fast parsing
- Latency Benchmarking: Compare baseline vs JIT with value projection
- Profit Sharing: 30% G-gent, 30% J-gent, 40% System from latency gains
- HF Tongues: High-Frequency Tongue builder for HFT scenarios
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

# VoI Economics (Phase 4: Value of Information for O-gent observation)
from .voi_economics import (
    # Enums
    ObservationDepth,
    FindingType,
    # Finding types
    ObservationFinding,
    ObservationRecord,
    Intervention,
    InterventionOutcome,
    VoIReceipt,
    # Epistemic Capital (third currency)
    EpistemicCapital,
    # Ledger
    VoILedger,
    # Optimizer
    VoIOptimizer,
    # Adaptive observation
    AdaptiveObserver,
    # Unified accounting
    UnifiedValueAccounting,
    SystemHealthReport,
    # Convenience functions
    create_voi_ledger,
    create_voi_optimizer,
    create_adaptive_observer,
    create_unified_accounting,
)

# Fiscal Constitution (B×G Phase 2: Grammar-based financial safety)
from .fiscal_constitution import (
    # Parse result types
    ParseError,
    ParseSuccess,
    # Operation types
    OperationType,
    # Account types
    AccountBalance,
    Account,
    LedgerState,
    LedgerTransaction,
    # Command AST nodes
    TransferCommand,
    QueryCommand,
    ReserveCommand,
    ReleaseCommand,
    # Parser and Tongue
    LedgerTongueParser,
    LedgerTongue,
    ExecutionResult,
    # Banker
    ConstitutionalBanker,
    TransactionResult,
    # Convenience functions
    create_ledger_tongue,
    create_constitutional_banker,
    create_fiscal_constitution,
)

# Syntax Tax (B×G Phase 3: Chomsky-based pricing)
from .syntax_tax import (
    # Chomsky hierarchy types
    ChomskyLevel,
    GrammarFeature,
    GrammarAnalysis,
    # Classifier
    GrammarClassifier,
    # Pricing
    SyntaxTaxSchedule,
    SyntaxTaxDecision,
    # Budget
    SyntaxTaxBudget,
    EscrowLease,
    # Downgrade
    DowngradeProposal,
    DowngradeNegotiator,
    # Convenience functions
    create_syntax_tax_budget,
    classify_grammar,
    calculate_syntax_tax,
    get_tier_costs,
)

# Semantic Inflation (B×G Phase 4: Complexity → Verbosity Pressure)
from .semantic_inflation import (
    # Complexity types
    ComplexityDimension,
    ComplexityVector,
    # Audience types
    AudienceLevel,
    AudienceProfile,
    # Inflation types
    InflationPressure,
    InflationCategory,
    InflationReport,
    # Allocation types
    TokenAllocation,
    AllocationDecision,
    # Deflation types
    DeflationStrategy,
    DeflationProposal,
    # CPI types
    CPISnapshot,
    # Classes
    InflationBudget,
    DeflationNegotiator as InflationDeflationNegotiator,  # Renamed to avoid collision
    ComplexityAnalyzer,
    SemanticCPIMonitor,
    # Convenience functions
    create_inflation_budget,
    analyze_complexity,
    calculate_inflation_pressure,
    get_deflation_recommendations,
    estimate_explanation_tokens,
)

# Grammar Insurance (B×G Phase 5: Volatility Hedging)
from .grammar_insurance import (
    # Volatility types
    VolatilityCategory,
    ParseEvent,
    VolatilityWindow,
    VolatilityMetrics,
    VolatilityMonitor,
    # Hedge types
    HedgeStrategy,
    GrammarHedge,
    # Insurance types
    InsurancePolicy,
    InsuranceClaim,
    PremiumQuote,
    PremiumCalculator,
    ClaimResult,
    # Main manager
    GrammarInsurance,
    # Portfolio analysis
    PortfolioRisk,
    PortfolioAnalyzer,
    # Convenience functions
    create_fallback_hedge,
    create_versioned_hedge,
    create_ensemble_hedge,
    estimate_annual_premium,
    calculate_hedge_cost,
)

# JIT Efficiency (B×G Phase 6: High-Frequency Trading Optimization)
from .jit_efficiency import (
    # Compilation targets
    JITCompilationTarget,
    OptimizationLevel,
    # Latency types
    LatencyMeasurement,
    LatencyReport,
    # Compilation types
    CompilationConfig,
    CompiledArtifact,
    CompiledTongue,
    # Compilers
    RegexJITCompiler,
    JumpTableJITCompiler,
    BytecodeJITCompiler,
    JITCompilerRegistry,
    # Benchmarking
    BenchmarkConfig,
    LatencyBenchmark,
    # Profit sharing
    ProfitShare,
    ProfitEntry,
    ProfitSharingLedger,
    # Monitor
    JITOpportunity,
    TongueUsageStats,
    JITEfficiencyMonitor,
    # HF Tongue
    HFTongueSpec,
    HFTongueBuilder,
    # Convenience functions
    create_jit_monitor,
    compile_grammar_jit,
    benchmark_jit_speedup,
    create_hf_tongue_builder,
    estimate_jit_value,
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
    # VoI Economics (Phase 4)
    "ObservationDepth",
    "FindingType",
    "ObservationFinding",
    "ObservationRecord",
    "Intervention",
    "InterventionOutcome",
    "VoIReceipt",
    "EpistemicCapital",
    "VoILedger",
    "VoIOptimizer",
    "AdaptiveObserver",
    "UnifiedValueAccounting",
    "SystemHealthReport",
    "create_voi_ledger",
    "create_voi_optimizer",
    "create_adaptive_observer",
    "create_unified_accounting",
    # Fiscal Constitution (B×G Phase 2)
    "ParseError",
    "ParseSuccess",
    "OperationType",
    "AccountBalance",
    "Account",
    "LedgerState",
    "LedgerTransaction",
    "TransferCommand",
    "QueryCommand",
    "ReserveCommand",
    "ReleaseCommand",
    "LedgerTongueParser",
    "LedgerTongue",
    "ExecutionResult",
    "ConstitutionalBanker",
    "TransactionResult",
    "create_ledger_tongue",
    "create_constitutional_banker",
    "create_fiscal_constitution",
    # Syntax Tax (B×G Phase 3)
    "ChomskyLevel",
    "GrammarFeature",
    "GrammarAnalysis",
    "GrammarClassifier",
    "SyntaxTaxSchedule",
    "SyntaxTaxDecision",
    "SyntaxTaxBudget",
    "EscrowLease",
    "DowngradeProposal",
    "DowngradeNegotiator",
    "create_syntax_tax_budget",
    "classify_grammar",
    "calculate_syntax_tax",
    "get_tier_costs",
    # Semantic Inflation (B×G Phase 4)
    "ComplexityDimension",
    "ComplexityVector",
    "AudienceLevel",
    "AudienceProfile",
    "InflationPressure",
    "InflationCategory",
    "InflationReport",
    "TokenAllocation",
    "AllocationDecision",
    "DeflationStrategy",
    "DeflationProposal",
    "CPISnapshot",
    "InflationBudget",
    "InflationDeflationNegotiator",
    "ComplexityAnalyzer",
    "SemanticCPIMonitor",
    "create_inflation_budget",
    "analyze_complexity",
    "calculate_inflation_pressure",
    "get_deflation_recommendations",
    "estimate_explanation_tokens",
    # Grammar Insurance (B×G Phase 5)
    "VolatilityCategory",
    "ParseEvent",
    "VolatilityWindow",
    "VolatilityMetrics",
    "VolatilityMonitor",
    "HedgeStrategy",
    "GrammarHedge",
    "InsurancePolicy",
    "InsuranceClaim",
    "PremiumQuote",
    "PremiumCalculator",
    "ClaimResult",
    "GrammarInsurance",
    "PortfolioRisk",
    "PortfolioAnalyzer",
    "create_fallback_hedge",
    "create_versioned_hedge",
    "create_ensemble_hedge",
    "estimate_annual_premium",
    "calculate_hedge_cost",
    # JIT Efficiency (B×G Phase 6)
    "JITCompilationTarget",
    "OptimizationLevel",
    "LatencyMeasurement",
    "LatencyReport",
    "CompilationConfig",
    "CompiledArtifact",
    "CompiledTongue",
    "RegexJITCompiler",
    "JumpTableJITCompiler",
    "BytecodeJITCompiler",
    "JITCompilerRegistry",
    "BenchmarkConfig",
    "LatencyBenchmark",
    "ProfitShare",
    "ProfitEntry",
    "ProfitSharingLedger",
    "JITOpportunity",
    "TongueUsageStats",
    "JITEfficiencyMonitor",
    "HFTongueSpec",
    "HFTongueBuilder",
    "create_jit_monitor",
    "compile_grammar_jit",
    "benchmark_jit_speedup",
    "create_hf_tongue_builder",
    "estimate_jit_value",
]
