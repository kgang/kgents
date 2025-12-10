"""
E-gent v2: Teleological Thermodynamic Evolution

A complete rebuild of E-gent following spec/e-gents/.

Architecture:
    Sun → Mutate → Select → Wager → Infect → Payoff

The system operates as a thermodynamic cycle:
- Sun: Provides exogenous energy (grants) for ambitious work
- Mutate: L-gent schema-driven semantic mutations
- Select: Teleological Demon (5-layer filter with intent alignment)
- Wager: Prediction market for mutation success
- Infect: Apply mutations to codebase (staked)
- Payoff: Settle bets, update viral library fitness

Key differences from v1:
- Market-driven (not budget-driven)
- Intent-aligned (not just test-passing)
- Fitness-evolving (not just outcome-recording)
- Phage-based (active vectors, not passive experiments)

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
]
