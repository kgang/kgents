"""
AGENTESE Context Resolvers

The Five Strict Contexts:
- world.*   - The External (Heterarchical)
- self.*    - The Internal (Ethical)
- concept.* - The Abstract (Generative)
- void.*    - The Accursed Share (Meta-Principle)
- time.*    - The Temporal (Heterarchical)

No sixth context allowed without spec change.
"""

from typing import Any

# Valid context names (immutable)
VALID_CONTEXTS = frozenset({"world", "self", "concept", "void", "time"})

# Import context resolvers
# Agent discovery (world.agent.* namespace)
from .agents import (
    AGENT_REGISTRY,
    AgentContextResolver,
    AgentListNode,
    AgentNode,
    create_agent_node,
    create_agent_resolver,
)
from .concept import (
    CONCEPT_ARCHETYPE_AFFORDANCES,
    ConceptContextResolver,
    ConceptNode,
    create_concept_node,
    create_concept_resolver,
    define_concept,
    get_concept_tree,
    render_concept_lattice,
)
from .concept_blend import (
    BLEND_AFFORDANCES,
    BlendNode,
    BlendResult,
    create_blend_node,
    forge_blend,
)

# Crown Jewels path registry (Seven Crown Jewel apps)
from .crown_jewels import (
    ALL_CROWN_JEWEL_PATHS,
    ATELIER_PATHS,
    BRAIN_PATHS,
    COALITION_PATHS,
    GARDENER_PATHS,
    GESTALT_PATHS,
    PARK_PATHS,
    SIMULATION_PATHS,
    CrownJewelRegistry,
    # Crown Symbiont integration
    create_crown_symbiont_for_path,
    get_crown_jewel_registry,
    get_dgent_config_for_path,
    list_self_time_paths,
    register_crown_jewel_paths,
)
from .crown_mappings import (
    CROWN_DGENT_MAPPINGS,
    MappingStats,
    get_mapping_stats,
    get_triple_config,
    is_crown_path,
    list_paths_by_aspect,
    list_paths_by_context,
    needs_lattice,
    needs_manifold,
    needs_witness,
)

# Crown Symbiont: Pure logic + D-gent triple infrastructure
from .crown_symbiont import (
    CrownSymbiont,
    CrownTripleConfig,
    compose_crown_symbionts,
    create_crown_symbiont,
)
from .forest import (
    FOREST_ROLE_AFFORDANCES,
    EpilogueEntry,
    ForestContextResolver,
    ForestLawCheck,
    ForestManifest,
    ForestNode,
    ParsedTree,
    create_forest_node,
    create_forest_resolver,
    parse_forest_md,
)
from .self_ import (
    SELF_AFFORDANCES,
    CapabilitiesNode,
    IdentityNode,
    JudgmentNode,
    MemoryNode,
    SelfContextResolver,
    SemaphoreNode,
    StateNode,
    create_self_resolver,
)
from .self_judgment import (
    CriticsLoop,
    Critique,
    CritiqueWeights,
    RefinedArtifact,
)
from .time import (
    TIME_AFFORDANCES,
    FutureNode,
    PastNode,
    ScheduledAction,
    ScheduleNode,
    TimeContextResolver,
    TraceNode,
    create_time_resolver,
)
from .triple_backed_memory import (
    TripleBackedMemory,
    WitnessReport,
    create_triple_backed_memory,
)
from .void import (
    CapitalNode,
    EntropyNode,
    EntropyPool,
    GratitudeNode,
    RandomnessGrant,
    SerendipityNode,
    VoidContextResolver,
    create_entropy_pool,
    create_void_resolver,
)
from .world import (
    PURGATORY_AFFORDANCES,
    WORLD_ARCHETYPE_AFFORDANCES,
    PurgatoryNode,
    WorldContextResolver,
    WorldNode,
    create_world_node,
    create_world_resolver,
)

# === Unified Resolver Factory ===


def create_context_resolvers(
    registry: Any = None,
    narrator: Any = None,
    d_gent: Any = None,
    b_gent: Any = None,
    grammarian: Any = None,
    entropy_budget: float = 100.0,
    capital_ledger: Any = None,
    purgatory: Any = None,
    # Phase 5: Substrate integration
    substrate: Any = None,
    compactor: Any = None,
    router: Any = None,
    # Four Pillars (Phase 6)
    memory_crystal: Any = None,
    pheromone_field: Any = None,
    inference_agent: Any = None,
    # Crown Jewel Brain (Session 3-4)
    cartographer: Any = None,
    embedder: Any = None,
) -> dict[str, Any]:
    """
    Create all five context resolvers with unified configuration.

    Args:
        registry: L-gent registry for entity lookup
        narrator: N-gent for narrative traces
        d_gent: D-gent for persistence and temporal projection
        b_gent: B-gent for budgeting and forecasting
        grammarian: G-gent for validation
        entropy_budget: Initial entropy budget for void context
        capital_ledger: EventSourcedLedger for void.capital.* (injected for testing)
        purgatory: Purgatory for semaphore management (self.semaphore.*, world.purgatory.*)
        substrate: SharedSubstrate for memory allocation (self.memory.allocate/substrate_stats)
        compactor: Compactor for memory compaction (self.memory.compact)
        router: CategoricalRouter for task routing (self.memory.route)
        memory_crystal: MemoryCrystal for Four Pillars holographic memory
        pheromone_field: PheromoneField for stigmergic coordination
        inference_agent: ActiveInferenceAgent for free energy-based retention
        cartographer: CartographerAgent for holographic memory navigation
        embedder: L-gent Embedder for semantic embeddings (Session 4)

    Returns:
        Dictionary mapping context names to resolvers
    """
    return {
        "world": create_world_resolver(
            registry=registry, narrator=narrator, purgatory=purgatory
        ),
        "self": create_self_resolver(
            d_gent=d_gent,
            n_gent=narrator,
            purgatory=purgatory,
            # Substrate integration (Phase 5)
            substrate=substrate,
            compactor=compactor,
            router=router,
            # Four Pillars (Phase 6)
            memory_crystal=memory_crystal,
            pheromone_field=pheromone_field,
            inference_agent=inference_agent,
            # Crown Jewel Brain (Session 3-4)
            cartographer=cartographer,
            embedder=embedder,
        ),
        "concept": create_concept_resolver(registry=registry, grammarian=grammarian),
        "void": create_void_resolver(
            initial_budget=entropy_budget, ledger=capital_ledger
        ),
        "time": create_time_resolver(narrator=narrator, d_gent=d_gent, b_gent=b_gent),
    }


__all__ = [
    # Constants
    "VALID_CONTEXTS",
    "WORLD_ARCHETYPE_AFFORDANCES",
    "PURGATORY_AFFORDANCES",
    "SELF_AFFORDANCES",
    "CONCEPT_ARCHETYPE_AFFORDANCES",
    "TIME_AFFORDANCES",
    "AGENT_REGISTRY",
    # World context
    "WorldContextResolver",
    "WorldNode",
    "PurgatoryNode",
    "create_world_resolver",
    "create_world_node",
    # Self context
    "SelfContextResolver",
    "MemoryNode",
    "CapabilitiesNode",
    "StateNode",
    "IdentityNode",
    "JudgmentNode",
    "SemaphoreNode",
    "create_self_resolver",
    # Self judgment (SPECS critique)
    "Critique",
    "CritiqueWeights",
    "CriticsLoop",
    "RefinedArtifact",
    # Concept context
    "ConceptContextResolver",
    "ConceptNode",
    "create_concept_resolver",
    "create_concept_node",
    "define_concept",
    "get_concept_tree",
    "render_concept_lattice",
    # Concept blending (concept.blend.*)
    "BLEND_AFFORDANCES",
    "BlendNode",
    "BlendResult",
    "create_blend_node",
    "forge_blend",
    # Void context
    "VoidContextResolver",
    "EntropyPool",
    "EntropyNode",
    "SerendipityNode",
    "GratitudeNode",
    "CapitalNode",
    "RandomnessGrant",
    "create_void_resolver",
    "create_entropy_pool",
    # Time context
    "TimeContextResolver",
    "TraceNode",
    "PastNode",
    "FutureNode",
    "ScheduleNode",
    "ScheduledAction",
    "create_time_resolver",
    # Agent discovery (world.agent.*)
    "AgentContextResolver",
    "AgentNode",
    "AgentListNode",
    "create_agent_resolver",
    "create_agent_node",
    # Forest context (concept.forest.*)
    "FOREST_ROLE_AFFORDANCES",
    "EpilogueEntry",
    "ForestContextResolver",
    "ForestLawCheck",
    "ForestManifest",
    "ForestNode",
    "ParsedTree",
    "create_forest_node",
    "create_forest_resolver",
    "parse_forest_md",
    # Crown Jewels (Seven Crown Jewel applications)
    "ALL_CROWN_JEWEL_PATHS",
    "ATELIER_PATHS",
    "BRAIN_PATHS",
    "COALITION_PATHS",
    "CrownJewelRegistry",
    "GARDENER_PATHS",
    "GESTALT_PATHS",
    "PARK_PATHS",
    "SIMULATION_PATHS",
    "get_crown_jewel_registry",
    "register_crown_jewel_paths",
    # Crown Symbiont: Pure logic + D-gent triple
    "CrownSymbiont",
    "CrownTripleConfig",
    "CROWN_DGENT_MAPPINGS",
    "MappingStats",
    "TripleBackedMemory",
    "WitnessReport",
    "compose_crown_symbionts",
    "create_crown_symbiont",
    "create_crown_symbiont_for_path",
    "create_triple_backed_memory",
    "get_dgent_config_for_path",
    "get_mapping_stats",
    "get_triple_config",
    "is_crown_path",
    "list_paths_by_aspect",
    "list_paths_by_context",
    "list_self_time_paths",
    "needs_lattice",
    "needs_manifold",
    "needs_witness",
    # Unified factory
    "create_context_resolvers",
]
