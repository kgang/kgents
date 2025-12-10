"""
E-gent: Teleological Thermodynamic Evolution

A principled approach to code evolution following spec/e-gents/.

Architecture:
    ☀️ SUN → MUTATE → SELECT → WAGER → INFECT → PAYOFF
         ↑                                      |
         └──────────────────────────────────────┘

The system operates as a thermodynamic cycle:
- Sun: Provides exogenous energy (grants) for ambitious work
- Mutate: L-gent schema-driven semantic mutations
- Select: Teleological Demon (5-layer filter with intent alignment)
- Wager: Prediction market for mutation success
- Infect: Apply mutations to codebase (staked)
- Payoff: Settle bets, update viral library fitness

Key principles:
- Market-driven resource allocation
- Intent-aligned evolution (prevents parasitic code)
- Fitness-evolving patterns (living library)
- Phage-based mutation vectors (active, not passive)

Spec Reference: spec/e-gents/
"""

from .types import (
    # Core types
    Phage,
    PhageStatus,
    PhageLineage,
    MutationVector,
    InfectionResult,
    InfectionStatus,
    # Intent
    Intent,
    # Thermodynamics
    ThermodynamicState,
    GibbsEnergy,
    # Evolution cycle
    EvolutionCycleState,
)

from .demon import (
    # Demon
    TeleologicalDemon,
    DemonConfig,
    DemonStats,
    SelectionResult,
    RejectionReason,
    # Parasitic patterns
    ParasiticPattern,
    PARASITIC_PATTERNS,
    # Factory functions
    create_demon,
    create_strict_demon,
    create_lenient_demon,
)

from .mutator import (
    # Mutator
    Mutator,
    MutatorConfig,
    MutatorStats,
    # Schemas
    SchemaCategory,
    MutationSchema,
    # Hot spots
    CodeHotSpot,
    ApplicationResult,
    analyze_hot_spots,
    # Standard schemas
    STANDARD_SCHEMA_APPLICATORS,
    SCHEMA_LOOP_TO_COMPREHENSION,
    SCHEMA_EXTRACT_CONSTANT,
    SCHEMA_FLATTEN_NESTING,
    SCHEMA_INLINE_SINGLE_USE,
    # Factory functions
    create_mutator,
    create_conservative_mutator,
    create_exploratory_mutator,
)

from .library import (
    # Viral Library
    ViralLibrary,
    ViralLibraryConfig,
    ViralPattern,
    LibraryStats,
    MutationSuggestion,
    PruneReport,
    # Factory functions
    create_library,
    create_strict_library,
    create_exploratory_library,
    # Market integration
    fitness_to_odds,
    odds_from_library,
)

from .phage import (
    # Phage operations
    infect,
    spawn_child,
    get_lineage_chain,
    calculate_lineage_fitness,
    analyze_lineage,
    infect_batch,
    # Environment
    InfectionEnvironment,
    InfectionConfig,
    StakeRecord,
    LineageReport,
    # Factory functions
    create_infection_env,
    create_test_only_env,
    create_production_env,
)

from .cycle import (
    # Cycle
    ThermodynamicCycle,
    CycleConfig,
    CyclePhase,
    CycleResult,
    PhaseResult,
    # High-level agent
    EvolutionAgent,
    # Factory functions
    create_cycle,
    create_conservative_cycle,
    create_exploratory_cycle,
    create_grant_funded_cycle,
    create_full_cycle,
)

from .safety import (
    # Rollback
    AtomicCheckpoint,
    AtomicMutationManager,
    FileCheckpoint,
    RollbackStatus,
    # Rate limiting
    RateLimiter,
    RateLimitConfig,
    RateLimitExceeded,
    # Audit logging
    AuditEvent,
    AuditEventType,
    AuditLogger,
    InMemoryAuditSink,
    FileAuditSink,
    # Sandbox
    Sandbox,
    SandboxConfig,
    SandboxResult,
    SandboxViolation,
    # Unified
    SafetySystem,
    SafetyConfig,
    create_safety_system,
    create_test_safety_system,
)

__all__ = [
    # Core types
    "Phage",
    "PhageStatus",
    "PhageLineage",
    "MutationVector",
    "InfectionResult",
    "InfectionStatus",
    # Intent
    "Intent",
    # Thermodynamics
    "ThermodynamicState",
    "GibbsEnergy",
    # Evolution cycle
    "EvolutionCycleState",
    # Demon
    "TeleologicalDemon",
    "DemonConfig",
    "DemonStats",
    "SelectionResult",
    "RejectionReason",
    "ParasiticPattern",
    "PARASITIC_PATTERNS",
    "create_demon",
    "create_strict_demon",
    "create_lenient_demon",
    # Mutator
    "Mutator",
    "MutatorConfig",
    "MutatorStats",
    "SchemaCategory",
    "MutationSchema",
    "CodeHotSpot",
    "ApplicationResult",
    "analyze_hot_spots",
    "STANDARD_SCHEMA_APPLICATORS",
    "SCHEMA_LOOP_TO_COMPREHENSION",
    "SCHEMA_EXTRACT_CONSTANT",
    "SCHEMA_FLATTEN_NESTING",
    "SCHEMA_INLINE_SINGLE_USE",
    "create_mutator",
    "create_conservative_mutator",
    "create_exploratory_mutator",
    # Viral Library
    "ViralLibrary",
    "ViralLibraryConfig",
    "ViralPattern",
    "LibraryStats",
    "MutationSuggestion",
    "PruneReport",
    "create_library",
    "create_strict_library",
    "create_exploratory_library",
    "fitness_to_odds",
    "odds_from_library",
    # Phage operations
    "infect",
    "spawn_child",
    "get_lineage_chain",
    "calculate_lineage_fitness",
    "analyze_lineage",
    "infect_batch",
    "InfectionEnvironment",
    "InfectionConfig",
    "StakeRecord",
    "LineageReport",
    "create_infection_env",
    "create_test_only_env",
    "create_production_env",
    # Cycle
    "ThermodynamicCycle",
    "CycleConfig",
    "CyclePhase",
    "CycleResult",
    "PhaseResult",
    "EvolutionAgent",
    "create_cycle",
    "create_conservative_cycle",
    "create_exploratory_cycle",
    "create_grant_funded_cycle",
    "create_full_cycle",
    # Safety
    "AtomicCheckpoint",
    "AtomicMutationManager",
    "FileCheckpoint",
    "RollbackStatus",
    "RateLimiter",
    "RateLimitConfig",
    "RateLimitExceeded",
    "AuditEvent",
    "AuditEventType",
    "AuditLogger",
    "InMemoryAuditSink",
    "FileAuditSink",
    "Sandbox",
    "SandboxConfig",
    "SandboxResult",
    "SandboxViolation",
    "SafetySystem",
    "SafetyConfig",
    "create_safety_system",
    "create_test_safety_system",
]
