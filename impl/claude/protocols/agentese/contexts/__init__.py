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

# Crown Jewels path registry (Seven Crown Jewel apps + Emergence + Gestalt Live + Design)
from .crown_jewels import (
    ALL_CROWN_JEWEL_PATHS,
    ATELIER_PATHS,
    BRAIN_PATHS,
    COALITION_PATHS,
    DESIGN_PATHS,
    EMERGENCE_PATHS,
    GARDENER_PATHS,
    GESTALT_LIVE_PATHS,
    GESTALT_PATHS,
    PARK_PATHS,
    SIMULATION_PATHS,
    CrownJewelRegistry,
    get_crown_jewel_registry,
    list_self_time_paths,
    register_crown_jewel_paths,
)

# Design context (concept.design.* - Design Language System)
from .design import (
    DESIGN_AFFORDANCES,
    ContentDesignNode,
    DesignContextNode,
    DesignContextResolver,
    DesignOperadNode,
    LayoutDesignNode,
    MotionDesignNode,
    create_design_node,
    create_design_resolver,
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

# Gardener context (The 7th Crown Jewel)
from .gardener import (
    COMMAND_TO_PATH,
    GARDENER_ROLE_AFFORDANCES,
    NL_PATTERN_HINTS,
    GardenerContextResolver,
    GardenerNode,
    GardenerSession,
    RouteMethod,
    RouteResult,
    create_gardener_node,
    create_gardener_resolver,
    get_all_command_mappings,
    resolve_command_to_path,
)

# Prompt context (concept.prompt.* - Evergreen Prompt System Wave 6)
from .prompt import (
    PROMPT_ROLE_AFFORDANCES,
    CheckpointSummaryDTO,
    DiffResult,
    EvolutionResult,
    PromptContextResolver,
    PromptNode,
    ValidationResult,
    create_prompt_node,
    create_prompt_resolver,
)
from .self_ import (
    BUS_AFFORDANCES,
    # Town Citizen integration (Phase 3 Crown Jewels)
    CITIZEN_AFFORDANCES,
    CITIZEN_MEMORY_AFFORDANCES,
    CITIZEN_PERSONALITY_AFFORDANCES,
    # Data architecture rewrite (Phase 2)
    DATA_AFFORDANCES,
    SELF_AFFORDANCES,
    # Soul integration (Chat Protocol - Phase 2)
    SOUL_AFFORDANCES,
    SOUL_CHAT_AFFORDANCES,
    # V-gent Vector integration (Phase 7)
    VECTOR_AFFORDANCES,
    BusNode,
    CapabilitiesNode,
    # Chat resolver (Chat Protocol - Phase 2)
    ChatNode,
    ChatResolver,
    CitizenMemoryNode,
    CitizenNode,
    CitizenPersonalityNode,
    DataNode,
    IdentityNode,
    JudgmentNode,
    MemoryNode,
    SelfContextResolver,
    SemaphoreNode,
    # Soul integration (Chat Protocol - Phase 2)
    SoulNode,
    StateNode,
    VectorNode,
    create_bus_resolver,
    create_chat_node,
    create_citizen_memory_node,
    create_citizen_node,
    create_citizen_personality_node,
    create_data_resolver,
    create_self_resolver,
    create_soul_node,
    get_chat_resolver,
)

# Jewel-Flow integration (F-gent Flow + Crown Jewels)
from .self_jewel_flow import (
    ALL_JEWEL_FLOW_PATHS,
    # Affordances
    BRAIN_FLOW_AFFORDANCES,
    # Path registries
    BRAIN_FLOW_PATHS,
    GARDENER_FLOW_AFFORDANCES,
    GARDENER_FLOW_PATHS,
    GESTALT_FLOW_AFFORDANCES,
    GESTALT_FLOW_PATHS,
    HERO_PATH_FLOW_PATHS,
    BrainFlowNode,
    GardenerFlowNode,
    GestaltFlowNode,
    # Nodes
    JewelFlowNode,
    # Factories
    create_brain_flow_node,
    create_gardener_flow_node,
    create_gestalt_flow_node,
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

# Town Citizen integration (Chat Protocol - Phase 2.5)
from .town_citizen import (
    ARCHETYPE_PROMPTS,
    CITIZEN_CHAT_AFFORDANCES,
    DEFAULT_CITIZEN_PROMPT,
    TownCitizenNode,
    TownCitizenResolver,
    build_citizen_system_prompt,
    create_citizen_chat_node,
    create_town_citizen_node,
    get_citizen_resolver,
    set_citizen_resolver,
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

# Atelier Node integration (Crown Jewels Metaphysical Upgrade)
from .world_atelier import (
    ATELIER_AFFORDANCES,
    AtelierNode,
    create_atelier_node,
    get_atelier_node,
    set_atelier_node,
)

# Emergence Node integration (Cymatics Design Sampler)
from .world_emergence import (
    EMERGENCE_AFFORDANCES,
    PATTERN_FAMILIES,
    EmergenceNode,
    create_emergence_node,
    get_emergence_node,
    set_emergence_node,
)

# Gallery Node integration (Living Autopoietic Showcase)
from .world_gallery import (
    GALLERY_AFFORDANCES,
    GALLERY_CATEGORIES,
    GalleryNode,
    create_gallery_node,
    get_gallery_node,
    set_gallery_node,
)

# Gestalt Live Node integration (Real-time Infrastructure Visualizer)
from .world_gestalt_live import (
    ENTITY_KINDS,
    GESTALT_LIVE_AFFORDANCES,
    GestaltLiveNode,
    create_gestalt_live_node,
    get_gestalt_live_node,
    set_gestalt_live_node,
)

# Park Node integration (Crisis Practice Scenarios)
from .world_park import (
    PARK_AFFORDANCES,
    ForceNode,
    MaskNode,
    ParkNode,
    ScenarioNode,
    get_force_node,
    get_mask_node,
    get_park_node,
    get_scenario_node,
)

# Town Node integration (Crown Jewels Metaphysical Upgrade)
from .world_town import (
    TOWN_AFFORDANCES,
    TownNode,
    create_town_node,
    get_town_node,
    set_town_node,
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
    # V-gent Vector integration (Phase 7)
    vgent: Any = None,
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
        vgent: V-gent backend (VgentProtocol) for vector operations (Phase 7)

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
            # V-gent Vector integration (Phase 7)
            vgent=vgent,
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
    # Data architecture rewrite (Phase 2)
    "DATA_AFFORDANCES",
    "BUS_AFFORDANCES",
    "DataNode",
    "BusNode",
    "create_data_resolver",
    "create_bus_resolver",
    # V-gent Vector integration (Phase 7)
    "VECTOR_AFFORDANCES",
    "VectorNode",
    # Town Citizen integration (Phase 3 Crown Jewels)
    "CITIZEN_AFFORDANCES",
    "CITIZEN_MEMORY_AFFORDANCES",
    "CITIZEN_PERSONALITY_AFFORDANCES",
    "CitizenNode",
    "CitizenMemoryNode",
    "CitizenPersonalityNode",
    "create_citizen_node",
    "create_citizen_memory_node",
    "create_citizen_personality_node",
    # Chat resolver (Chat Protocol - Phase 2)
    "ChatNode",
    "ChatResolver",
    "create_chat_node",
    "get_chat_resolver",
    # Soul integration (Chat Protocol - Phase 2)
    "SOUL_AFFORDANCES",
    "SOUL_CHAT_AFFORDANCES",
    "SoulNode",
    "create_soul_node",
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
    # Gardener context (concept.gardener.* - The 7th Crown Jewel)
    "COMMAND_TO_PATH",
    "GARDENER_ROLE_AFFORDANCES",
    "NL_PATTERN_HINTS",
    "GardenerContextResolver",
    "GardenerNode",
    "GardenerSession",
    "RouteMethod",
    "RouteResult",
    "create_gardener_node",
    "create_gardener_resolver",
    "get_all_command_mappings",
    "resolve_command_to_path",
    # Crown Jewels (Seven Crown Jewel applications + Emergence + Gestalt Live + Design)
    "ALL_CROWN_JEWEL_PATHS",
    "ATELIER_PATHS",
    "BRAIN_PATHS",
    "COALITION_PATHS",
    "CrownJewelRegistry",
    "DESIGN_PATHS",
    "EMERGENCE_PATHS",
    "GARDENER_PATHS",
    "GESTALT_LIVE_PATHS",
    "GESTALT_PATHS",
    "PARK_PATHS",
    "SIMULATION_PATHS",
    "get_crown_jewel_registry",
    "list_self_time_paths",
    "register_crown_jewel_paths",
    # Design context (concept.design.* - Design Language System)
    "DESIGN_AFFORDANCES",
    "LayoutDesignNode",
    "ContentDesignNode",
    "MotionDesignNode",
    "DesignOperadNode",
    "DesignContextNode",
    "DesignContextResolver",
    "create_design_resolver",
    "create_design_node",
    # Jewel-Flow integration (F-gent Flow + Crown Jewels)
    "BRAIN_FLOW_PATHS",
    "GARDENER_FLOW_PATHS",
    "GESTALT_FLOW_PATHS",
    "HERO_PATH_FLOW_PATHS",
    "ALL_JEWEL_FLOW_PATHS",
    "BRAIN_FLOW_AFFORDANCES",
    "GARDENER_FLOW_AFFORDANCES",
    "GESTALT_FLOW_AFFORDANCES",
    "JewelFlowNode",
    "BrainFlowNode",
    "GardenerFlowNode",
    "GestaltFlowNode",
    "create_brain_flow_node",
    "create_gardener_flow_node",
    "create_gestalt_flow_node",
    # Prompt context (concept.prompt.* - Evergreen Prompt System Wave 6)
    "PROMPT_ROLE_AFFORDANCES",
    "CheckpointSummaryDTO",
    "DiffResult",
    "EvolutionResult",
    "PromptContextResolver",
    "PromptNode",
    "ValidationResult",
    "create_prompt_node",
    "create_prompt_resolver",
    # Town Citizen integration (Chat Protocol - Phase 2.5)
    "ARCHETYPE_PROMPTS",
    "CITIZEN_CHAT_AFFORDANCES",
    "DEFAULT_CITIZEN_PROMPT",
    "TownCitizenNode",
    "TownCitizenResolver",
    "build_citizen_system_prompt",
    "create_citizen_chat_node",
    "create_town_citizen_node",
    "get_citizen_resolver",
    "set_citizen_resolver",
    # Town Node integration (Crown Jewels Metaphysical Upgrade)
    "TOWN_AFFORDANCES",
    "TownNode",
    "create_town_node",
    "get_town_node",
    "set_town_node",
    # Atelier Node integration (Crown Jewels Metaphysical Upgrade)
    "ATELIER_AFFORDANCES",
    "AtelierNode",
    "create_atelier_node",
    "get_atelier_node",
    "set_atelier_node",
    # Park Node integration (Crisis Practice Scenarios)
    "PARK_AFFORDANCES",
    "ParkNode",
    "ScenarioNode",
    "MaskNode",
    "ForceNode",
    "get_park_node",
    "get_scenario_node",
    "get_mask_node",
    "get_force_node",
    # Emergence Node integration (Cymatics Design Sampler)
    "EMERGENCE_AFFORDANCES",
    "PATTERN_FAMILIES",
    "EmergenceNode",
    "create_emergence_node",
    "get_emergence_node",
    "set_emergence_node",
    # Gestalt Live Node integration (Real-time Infrastructure Visualizer)
    "ENTITY_KINDS",
    "GESTALT_LIVE_AFFORDANCES",
    "GestaltLiveNode",
    "create_gestalt_live_node",
    "get_gestalt_live_node",
    "set_gestalt_live_node",
    # Gallery Node integration (Living Autopoietic Showcase)
    "GALLERY_AFFORDANCES",
    "GALLERY_CATEGORIES",
    "GalleryNode",
    "create_gallery_node",
    "get_gallery_node",
    "set_gallery_node",
    # Unified factory
    "create_context_resolvers",
]
