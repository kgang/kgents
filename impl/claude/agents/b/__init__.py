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

from .catalog_integration import (
    # Types
    HypothesisCatalogEntry,
    TestResult,
    # Discovery
    find_hypotheses,
    find_related_hypotheses,
    get_hypothesis_lineage,
    mark_hypothesis_falsified,
    # Lineage
    record_hypothesis_evolution,
    record_hypothesis_fork,
    # Registration
    register_hypothesis,
    register_hypothesis_batch,
    # Metrics
    update_hypothesis_metrics,
)

# Compression Economy (Phase 4: Structural Economics B×G Integration)
from .compression_economy import (
    # Types
    AdoptionStatus,
    BudgetDecision,
    CommunicationLog,
    # Classes
    CommunicationTracker,
    CompressionEconomyMonitor,
    CompressionROI,
    CompressionROICalculator,
    PidginAvailable,
    PidginMetadata,
    SemanticZipperBudget,
    analyze_compression_opportunity,
    # Convenience functions
    create_compression_monitor,
    create_zipper_budget,
)

# Evolution Economics (E-gent archived 2025-12-16, module kept for utility)
from .egent_integration import (
    # Prediction Market
    BetOutcome,
    # Combined
    EvolutionEconomics,
    Grant,
    GrantConsumption,
    # Grant System (Sun)
    GrantStatus,
    MarketQuote,
    MutationBet,
    # Staking
    PhageStake,
    PredictionMarket,
    SettlementResult,
    StakingPool,
    Sun,
    create_evolution_economics,
)

# Fiscal Constitution (B×G Phase 2: Grammar-based financial safety)
from .fiscal_constitution import (
    Account,
    # Account types
    AccountBalance,
    # Banker
    ConstitutionalBanker,
    ExecutionResult,
    LedgerState,
    LedgerTongue,
    # Parser and Tongue
    LedgerTongueParser,
    LedgerTransaction,
    # Operation types
    OperationType,
    # Parse result types
    ParseError,
    ParseSuccess,
    QueryCommand,
    ReleaseCommand,
    ReserveCommand,
    TransactionResult,
    # Command AST nodes
    TransferCommand,
    create_constitutional_banker,
    create_fiscal_constitution,
    # Convenience functions
    create_ledger_tongue,
)

# Grammar Insurance (B×G Phase 5: Volatility Hedging)
from .grammar_insurance import (
    ClaimResult,
    GrammarHedge,
    # Main manager
    GrammarInsurance,
    # Hedge types
    HedgeStrategy,
    InsuranceClaim,
    # Insurance types
    InsurancePolicy,
    ParseEvent,
    PortfolioAnalyzer,
    # Portfolio analysis
    PortfolioRisk,
    PremiumCalculator,
    PremiumQuote,
    # Volatility types
    VolatilityCategory,
    VolatilityMetrics,
    VolatilityMonitor,
    VolatilityWindow,
    calculate_hedge_cost,
    create_ensemble_hedge,
    # Convenience functions
    create_fallback_hedge,
    create_versioned_hedge,
    estimate_annual_premium,
)
from .hypothesis import (
    HypothesisEngine,
    HypothesisInput,
    HypothesisOutput,
    exploratory_engine,
    hypothesis_engine,
    rigorous_engine,
)
from .hypothesis_parser import (
    Hypothesis,
    NoveltyLevel,
)

# JIT Efficiency (B×G Phase 6: High-Frequency Trading Optimization)
from .jit_efficiency import (
    # Benchmarking
    BenchmarkConfig,
    BytecodeJITCompiler,
    # Compilation types
    CompilationConfig,
    CompiledArtifact,
    CompiledTongue,
    HFTongueBuilder,
    # HF Tongue
    HFTongueSpec,
    # Compilation targets
    JITCompilationTarget,
    JITCompilerRegistry,
    JITEfficiencyMonitor,
    # Monitor
    JITOpportunity,
    JumpTableJITCompiler,
    LatencyBenchmark,
    # Latency types
    LatencyMeasurement,
    LatencyReport,
    OptimizationLevel,
    ProfitEntry,
    # Profit sharing
    ProfitShare,
    ProfitSharingLedger,
    # Compilers
    RegexJITCompiler,
    TongueUsageStats,
    benchmark_jit_speedup,
    compile_grammar_jit,
    create_hf_tongue_builder,
    # Convenience functions
    create_jit_monitor,
    estimate_jit_value,
)
from .metered_functor import (
    Allocation,
    # Auction
    Bid,
    # Central Bank
    CentralBank,
    Denial,
    DualBudget,
    # Budgets
    EntropyBudget,
    FuturesMarket,
    # Currency types
    Gas,
    Impact,
    InsufficientFundsError,
    Loan,
    # Functor
    Metered,
    Receipt,
    SinkingFund,
    # Token accounting
    TokenBucket,
    TokenFuture,
    meter,
    metered_invoke,
    priority_auction,
)
from .persistent_hypothesis import (
    HypothesisLineageEdge,
    HypothesisMemory,
    PersistentHypothesisStorage,
    persistent_hypothesis_storage,
)
from .robin_integration import (
    RobinAgent,
    RobinInput,
    RobinOutput,
    fallback_robin,
    quick_robin,
    robin,
    robin_with_persona,
)

# Semantic Inflation (B×G Phase 4: Complexity → Verbosity Pressure)
from .semantic_inflation import (
    AllocationDecision,
    # Audience types
    AudienceLevel,
    AudienceProfile,
    ComplexityAnalyzer,
    # Complexity types
    ComplexityDimension,
    ComplexityVector,
    # CPI types
    CPISnapshot,
    DeflationProposal,
    # Deflation types
    DeflationStrategy,
    # Classes
    InflationBudget,
    InflationCategory,
    # Inflation types
    InflationPressure,
    InflationReport,
    SemanticCPIMonitor,
    # Allocation types
    TokenAllocation,
    analyze_complexity,
    calculate_inflation_pressure,
    # Convenience functions
    create_inflation_budget,
    estimate_explanation_tokens,
    get_deflation_recommendations,
)
from .semantic_inflation import (
    DeflationNegotiator as InflationDeflationNegotiator,  # Renamed to avoid collision
)

# Syntax Tax (B×G Phase 3: Chomsky-based pricing)
from .syntax_tax import (
    # Chomsky hierarchy types
    ChomskyLevel,
    DowngradeNegotiator,
    # Downgrade
    DowngradeProposal,
    EscrowLease,
    GrammarAnalysis,
    # Classifier
    GrammarClassifier,
    GrammarFeature,
    # Budget
    SyntaxTaxBudget,
    SyntaxTaxDecision,
    # Pricing
    SyntaxTaxSchedule,
    calculate_syntax_tax,
    classify_grammar,
    # Convenience functions
    create_syntax_tax_budget,
    get_tier_costs,
)
from .value_ledger import (
    BalanceSheet,
    # Oracles
    ComplexityOracle,
    # Regulation
    EthicalRegulator,
    RoCAssessment,
    RoCMonitor,
    # Monitoring
    RoCThresholds,
    # Output types
    SimpleOutput,
    TransactionReceipt,
    # Accounting
    Treasury,
    ValueLedger,
    ValueOracle,
)

# Banker Economics (Phase 3)
from .value_tensor import (
    Anomaly,
    AntiDelusionChecker,
    # Conservation
    ConservationLaw,
    EconomicDimension,
    EthicalDimension,
    ExchangeMatrix,
    # Exchange
    ExchangeRate,
    ImpactTier,
    # Dimensions
    PhysicalDimension,
    SemanticDimension,
    TensorAlgebra,
    # Tensor
    ValueTensor,
    create_standard_exchange_rates,
)

# VoI Economics (Phase 4: Value of Information for O-gent observation)
from .voi_economics import (
    # Adaptive observation
    AdaptiveObserver,
    # Epistemic Capital (third currency)
    EpistemicCapital,
    FindingType,
    Intervention,
    InterventionOutcome,
    # Enums
    ObservationDepth,
    # Finding types
    ObservationFinding,
    ObservationRecord,
    SystemHealthReport,
    # Unified accounting
    UnifiedValueAccounting,
    # Ledger
    VoILedger,
    # Optimizer
    VoIOptimizer,
    VoIReceipt,
    create_adaptive_observer,
    create_unified_accounting,
    # Convenience functions
    create_voi_ledger,
    create_voi_optimizer,
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
    # Evolution Economics (E-gent archived 2025-12-16, module kept for utility)
    "BetOutcome",
    "MutationBet",
    "MarketQuote",
    "SettlementResult",
    "PredictionMarket",
    "GrantStatus",
    "Grant",
    "GrantConsumption",
    "Sun",
    "PhageStake",
    "StakingPool",
    "EvolutionEconomics",
    "create_evolution_economics",
]
