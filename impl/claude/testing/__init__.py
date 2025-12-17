"""
kgents testing infrastructure.

Philosophy: Tests are the executable specification.

This package provides:
- Phase 2: Law marker system and templates
- Phase 3: Property-based testing strategies (Hypothesis)
- Phase 4: Autopoietic witnesses (pytest plugin)
- Phase 5: Accursed share exploratory tests
- Phase 8: Cortex Assurance System v2.0

Phase 8 (Cortex) Components:
- Oracle: Metamorphic Judge for fuzzy truth
- Topologist: Homotopic testing for composition
- Analyst: Counterfactual debugging and causation
- Market: Portfolio-optimized test scheduling
- Red Team: Adversarial evolutionary testing
- Cortex: Unified cybernetic immune system

See docs/cortex-assurance-system.md for the full strategy.
"""

from .accursed_share import Discovery, DiscoveryLog
from .analyst import (
    CausalAnalyst,
    CausalGraph,
    CounterfactualResult,
    DeltaDebugResult,
    FlakinessDiagnosis,
    TestWitness,
    WitnessStore,
    format_analyst_report,
)
from .cortex import (
    BriefingReport,
    Cortex,
    format_briefing_report,
    format_full_report,
)

# Type-safe fixtures
from .fixtures import as_agent, as_umwelt
from .flaky_registry import FlakyPattern, FlakyRegistry

# Phase 8: Integrations with kgents ecosystem
from .integrations import (
    BGENT_AVAILABLE,
    DGENT_AVAILABLE,
    LGENT_AVAILABLE,
    NGENT_AVAILABLE,
    OGENT_AVAILABLE,
    BudgetedMarket,
    IntegrationStatus,
    LatticeValidatedTopology,
    ObservedCortex,
    PersistentWitnessStore,
    create_enhanced_cortex,
    create_enhanced_oracle,
    create_persistent_analyst,
    format_integration_report,
    get_integration_status,
)
from .market import (
    BUDGET_TIERS,
    BudgetManager,
    BudgetTier,
    MarketReport,
    TestAsset,
    TestCost,
    TestMarket,
    format_market_report,
)

# Phase 8: Cortex Assurance System
from .oracle import (
    IdempotencyRelation,
    MetamorphicRelation,
    Oracle,
    OracleValidation,
    PermutationInvarianceRelation,
    RelationResult,
    SubsetRelation,
    cosine_similarity,
    format_validation_report,
)
from .pytest_witness import WitnessPlugin
from .red_team import (
    MUTATION_OPERATORS,
    AdversarialInput,
    MutationScore,
    RedTeam,
    RedTeamReport,
    Vulnerability,
    format_red_team_report,
)
from .strategies import (
    agent_chains,
    invalid_dna,
    simple_agents,
    type_names,
    valid_dna,
)
from .topologist import (
    AgentSignature,
    CommutativityResult,
    InvarianceResult,
    NoiseFunctor,
    Topologist,
    TopologistReport,
    TypeTopology,
    format_topologist_report,
)

__all__ = [
    # Fixtures (type-safe mocks)
    "as_umwelt",
    "as_agent",
    # Strategies (Phase 3)
    "simple_agents",
    "agent_chains",
    "valid_dna",
    "invalid_dna",
    "type_names",
    # Plugin (Phase 4)
    "WitnessPlugin",
    # Flaky Registry (Phase 4)
    "FlakyPattern",
    "FlakyRegistry",
    # Discovery (Phase 5)
    "Discovery",
    "DiscoveryLog",
    # Oracle (Phase 8.1)
    "Oracle",
    "MetamorphicRelation",
    "RelationResult",
    "OracleValidation",
    "SubsetRelation",
    "IdempotencyRelation",
    "PermutationInvarianceRelation",
    "cosine_similarity",
    "format_validation_report",
    # Topologist (Phase 8.1)
    "Topologist",
    "TypeTopology",
    "AgentSignature",
    "NoiseFunctor",
    "CommutativityResult",
    "InvarianceResult",
    "TopologistReport",
    "format_topologist_report",
    # Analyst (Phase 8.2)
    "CausalAnalyst",
    "WitnessStore",
    "TestWitness",
    "DeltaDebugResult",
    "CounterfactualResult",
    "CausalGraph",
    "FlakinessDiagnosis",
    "format_analyst_report",
    # Market (Phase 8.3)
    "TestMarket",
    "BudgetManager",
    "TestAsset",
    "TestCost",
    "BudgetTier",
    "BUDGET_TIERS",
    "MarketReport",
    "format_market_report",
    # Red Team (Phase 8.4)
    "RedTeam",
    "AdversarialInput",
    "MutationScore",
    "Vulnerability",
    "RedTeamReport",
    "MUTATION_OPERATORS",
    "format_red_team_report",
    # Cortex (Phase 8.5)
    "Cortex",
    "BriefingReport",
    "format_briefing_report",
    "format_full_report",
    # Integrations (Phase 8.6)
    "IntegrationStatus",
    "get_integration_status",
    "create_enhanced_oracle",
    "create_persistent_analyst",
    "create_enhanced_cortex",
    "PersistentWitnessStore",
    "LatticeValidatedTopology",
    "BudgetedMarket",
    "ObservedCortex",
    "format_integration_report",
    "LGENT_AVAILABLE",
    "DGENT_AVAILABLE",
    "NGENT_AVAILABLE",
    "BGENT_AVAILABLE",
    "OGENT_AVAILABLE",
]
