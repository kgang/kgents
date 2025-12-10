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

from .strategies import (
    simple_agents,
    agent_chains,
    valid_dna,
    invalid_dna,
    type_names,
)
from .pytest_witness import WitnessPlugin
from .flaky_registry import FlakyPattern, FlakyRegistry
from .accursed_share import Discovery, DiscoveryLog

# Phase 8: Cortex Assurance System
from .oracle import (
    Oracle,
    MetamorphicRelation,
    RelationResult,
    OracleValidation,
    SubsetRelation,
    IdempotencyRelation,
    PermutationInvarianceRelation,
    cosine_similarity,
    format_validation_report,
)
from .topologist import (
    Topologist,
    TypeTopology,
    AgentSignature,
    NoiseFunctor,
    CommutativityResult,
    InvarianceResult,
    TopologistReport,
    format_topologist_report,
)
from .analyst import (
    CausalAnalyst,
    WitnessStore,
    TestWitness,
    DeltaDebugResult,
    CounterfactualResult,
    CausalGraph,
    FlakinessDiagnosis,
    format_analyst_report,
)
from .market import (
    TestMarket,
    BudgetManager,
    TestAsset,
    TestCost,
    BudgetTier,
    BUDGET_TIERS,
    MarketReport,
    format_market_report,
)
from .red_team import (
    RedTeam,
    AdversarialInput,
    MutationScore,
    Vulnerability,
    RedTeamReport,
    MUTATION_OPERATORS,
    format_red_team_report,
)
from .cortex import (
    Cortex,
    BriefingReport,
    format_briefing_report,
    format_full_report,
)

# Phase 8: Integrations with kgents ecosystem
from .integrations import (
    IntegrationStatus,
    get_integration_status,
    create_enhanced_oracle,
    create_persistent_analyst,
    create_enhanced_cortex,
    PersistentWitnessStore,
    LatticeValidatedTopology,
    BudgetedMarket,
    TeleologicalRedTeam,
    ObservedCortex,
    format_integration_report,
    LGENT_AVAILABLE,
    DGENT_AVAILABLE,
    NGENT_AVAILABLE,
    BGENT_AVAILABLE,
    EGENT_AVAILABLE,
    OGENT_AVAILABLE,
)

__all__ = [
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
    "TeleologicalRedTeam",
    "ObservedCortex",
    "format_integration_report",
    "LGENT_AVAILABLE",
    "DGENT_AVAILABLE",
    "NGENT_AVAILABLE",
    "BGENT_AVAILABLE",
    "EGENT_AVAILABLE",
    "OGENT_AVAILABLE",
]
