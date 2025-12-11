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

from .cycle import (
    CycleConfig,
    CyclePhase,
    CycleResult,
    # High-level agent
    EvolutionAgent,
    PhaseResult,
    # Cycle
    ThermodynamicCycle,
    create_conservative_cycle,
    # Factory functions
    create_cycle,
    create_exploratory_cycle,
    create_full_cycle,
    create_grant_funded_cycle,
)
from .demon import (
    PARASITIC_PATTERNS,
    DemonConfig,
    DemonStats,
    # Parasitic patterns
    ParasiticPattern,
    RejectionReason,
    SelectionResult,
    # Demon
    TeleologicalDemon,
    # Factory functions
    create_demon,
    create_lenient_demon,
    create_strict_demon,
)
from .library import (
    LibraryStats,
    MutationSuggestion,
    PruneReport,
    # Viral Library
    ViralLibrary,
    ViralLibraryConfig,
    ViralPattern,
    create_exploratory_library,
    # Factory functions
    create_library,
    create_strict_library,
    # Market integration
    fitness_to_odds,
    odds_from_library,
)
from .mutator import (
    SCHEMA_EXTRACT_CONSTANT,
    SCHEMA_FLATTEN_NESTING,
    SCHEMA_INLINE_SINGLE_USE,
    SCHEMA_LOOP_TO_COMPREHENSION,
    # Standard schemas
    STANDARD_SCHEMA_APPLICATORS,
    ApplicationResult,
    # Hot spots
    CodeHotSpot,
    MutationSchema,
    # Mutator
    Mutator,
    MutatorConfig,
    MutatorStats,
    # Schemas
    SchemaCategory,
    analyze_hot_spots,
    create_conservative_mutator,
    create_exploratory_mutator,
    # Factory functions
    create_mutator,
)
from .phage import (
    InfectionConfig,
    # Environment
    InfectionEnvironment,
    LineageReport,
    StakeRecord,
    analyze_lineage,
    calculate_lineage_fitness,
    # Factory functions
    create_infection_env,
    create_production_env,
    create_test_only_env,
    get_lineage_chain,
    # Phage operations
    infect,
    infect_batch,
    spawn_child,
)
from .safety import (
    # Rollback
    AtomicCheckpoint,
    AtomicMutationManager,
    # Audit logging
    AuditEvent,
    AuditEventType,
    AuditLogger,
    FileAuditSink,
    FileCheckpoint,
    InMemoryAuditSink,
    RateLimitConfig,
    # Rate limiting
    RateLimiter,
    RateLimitExceeded,
    RollbackStatus,
    SafetyConfig,
    # Unified
    SafetySystem,
    # Sandbox
    Sandbox,
    SandboxConfig,
    SandboxResult,
    SandboxViolation,
    create_safety_system,
    create_test_safety_system,
)
from .types import (
    # Evolution cycle
    EvolutionCycleState,
    GibbsEnergy,
    InfectionResult,
    InfectionStatus,
    # Intent
    Intent,
    MutationVector,
    # Core types
    Phage,
    PhageLineage,
    PhageStatus,
    # Thermodynamics
    ThermodynamicState,
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
