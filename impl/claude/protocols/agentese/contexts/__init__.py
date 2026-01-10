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

# Crown Jewels path registry (Brain + Design + Morpheus)
from .crown_jewels import (
    ALL_CROWN_JEWEL_PATHS,
    BRAIN_PATHS,
    DESIGN_PATHS,
    MORPHEUS_PATHS,
    CrownJewelRegistry,
    get_crown_jewel_registry,
    list_self_time_paths,
    register_crown_jewel_paths,
)

# Derivation Nodes (self.derivation.*, concept.constitution.*, world.kblock.derivation.*)
from .derivation import (
    CONSTITUTION_AFFORDANCES,
    CONSTITUTIONAL_PRINCIPLES,
    KBLOCK_DERIVATION_AFFORDANCES,
    SELF_DERIVATION_AFFORDANCES,
    ConstitutionNode,
    KBlockDerivationNode,
    SelfDerivationNode,
    get_constitution_node,
    get_kblock_derivation_node,
    get_self_derivation_node,
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

# Hyperedge Resolvers
from .hyperedge_resolvers import (
    ResolverRegistry,
    agentese_path_to_file,
    file_to_agentese_path,
    get_resolver_registry,
    register_resolver,
    resolve_all_edges,
    resolve_hyperedge,
)

# Note: Forest, Gardener, and Prompt contexts were deprecated 2025-12-21
# See: spec/protocols/_archive/gardener-evergreen-heritage.md
# Note: Chat, Citizen, Town, Park, Forge, Gestalt, Witness removed 2025-12-21
# See: plans/crown-jewel-cleanup.md
from .self_ import (
    BUS_AFFORDANCES,
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
    create_data_resolver,
    create_self_resolver,
    create_soul_node,
)

# Collaboration Context (self.collaboration.* - Phase 5C)
from .self_collaboration import (
    COLLABORATION_AFFORDANCES,
    CollaborationNode,
)

# Typed-Hypergraph Context (self.context.* - AD-009 Context Management)
from .self_context import (
    ALL_STANDARD_EDGES,
    CONTEXT_AFFORDANCES,
    EVIDENCE_EDGES,
    REVERSE_EDGES,
    SEMANTIC_EDGES,
    SPEC_EDGES,
    STRUCTURAL_EDGES,
    TEMPORAL_EDGES,
    TESTING_EDGES,
    ContextGraph,
    ContextNavNode,
    ContextNode,
    Trail,
    TrailStep,
    create_context_graph,
    create_context_node,
    get_context_nav_node,
    get_reverse_edge,
)

# Self Différance navigation (spec/impl traversal)
from .self_differance import (
    SELF_DIFFERANCE_AFFORDANCES,
    SelfDifferanceNode,
    create_self_differance_node,
    get_self_differance_node,
    set_self_differance_node,
)

# Exploration Harness Context (self.explore.* - Exploration with Safety)
from .self_explore import (
    EXPLORE_AFFORDANCES,
    ExploreNode,
    get_explore_node,
    set_explore_node,
)

# Jewel-Flow integration (F-gent Flow + Crown Jewels)
from .self_jewel_flow import (
    ALL_JEWEL_FLOW_PATHS,
    # Affordances
    BRAIN_FLOW_AFFORDANCES,
    # Path registries
    BRAIN_FLOW_PATHS,
    HERO_PATH_FLOW_PATHS,
    BrainFlowNode,
    # Nodes
    JewelFlowNode,
    # Factories
    create_brain_flow_node,
)
from .self_judgment import (
    CriticsLoop,
    Critique,
    CritiqueWeights,
    RefinedArtifact,
)

# Portal Token Context (self.portal.* - Portal Token Navigation)
from .self_portal import (
    PORTAL_AFFORDANCES,
    PortalNavNode,
    get_portal_nav_node,
    set_portal_nav_node,
)

# 3D Projection Context (concept.projection.three.*)
from .three import (
    EDGE_DEFAULTS,
    NODE_DEFAULTS,
    QUALITY_CONFIGS,
    THEME_REGISTRY,
    THREE_AFFORDANCES,
    Quality,
    ThemeName,
    ThreeContextResolver,
    ThreeEdgeNode,
    ThreeNodeNode,
    ThreeQualityNode,
    ThreeThemeNode,
    create_three_edge_node,
    create_three_node_node,
    create_three_quality_node,
    create_three_resolver,
    create_three_theme_node,
)
from .time import (
    TIME_AFFORDANCES,
    FutureNode,
    Mark,
    PastNode,
    ScheduledAction,
    ScheduleNode,
    TimeContextResolver,
    create_time_resolver,
)

# Différance Engine integration (Ghost Heritage DAG)
from .time_differance import (
    DIFFERANCE_BRANCH_AFFORDANCES,
    DIFFERANCE_TRACE_AFFORDANCES,
    BranchNode,
    DifferanceMark,
    create_differance_node,
    get_branch_node,
    get_differance_node,
    set_differance_node,
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

# Note: Emergence Node (world.emergence.*) removed 2025-12-21
# Gallery Node integration (Living Autopoietic Showcase)
from .world_gallery import (
    GALLERY_AFFORDANCES,
    GALLERY_CATEGORIES,
    GalleryNode,
    create_gallery_node,
    get_gallery_node,
    set_gallery_node,
)

# Repo Node (world.repo.* - Path validation for trail creation)
from .world_repo import (
    CREATABLE_EXTENSIONS,
    REPO_AFFORDANCES,
    RepoNode,
    create_repo_node,
    get_repo_node,
    set_repo_node,
)

# Note: Gestalt, Park, Town removed 2025-12-21 (Crown Jewel Cleanup)

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
        "world": create_world_resolver(registry=registry, narrator=narrator, purgatory=purgatory),
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
        "void": create_void_resolver(initial_budget=entropy_budget, ledger=capital_ledger),
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
    "Mark",
    "PastNode",
    "FutureNode",
    "ScheduleNode",
    "ScheduledAction",
    "create_time_resolver",
    # Différance Engine (time.differance.* - Ghost Heritage DAG)
    "DIFFERANCE_TRACE_AFFORDANCES",
    "DIFFERANCE_BRANCH_AFFORDANCES",
    "DifferanceMark",
    "BranchNode",
    "create_differance_node",
    "get_differance_node",
    "set_differance_node",
    "get_branch_node",
    # Self Différance (self.differance.* - Spec/Impl Navigation)
    "SELF_DIFFERANCE_AFFORDANCES",
    "SelfDifferanceNode",
    "create_self_differance_node",
    "get_self_differance_node",
    "set_self_differance_node",
    # Agent discovery (world.agent.*)
    "AgentContextResolver",
    "AgentNode",
    "AgentListNode",
    "create_agent_resolver",
    "create_agent_node",
    # Crown Jewels (Brain + Design + Morpheus)
    "ALL_CROWN_JEWEL_PATHS",
    "BRAIN_PATHS",
    "DESIGN_PATHS",
    "MORPHEUS_PATHS",
    "CrownJewelRegistry",
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
    "HERO_PATH_FLOW_PATHS",
    "ALL_JEWEL_FLOW_PATHS",
    "BRAIN_FLOW_AFFORDANCES",
    "JewelFlowNode",
    "BrainFlowNode",
    "create_brain_flow_node",
    # Note: Town, Park, Gestalt, Gardener Flow, Chat, Atelier removed 2025-12-21 (Crown Jewel Cleanup)
    # Note: Emergence Node (world.emergence.*) removed 2025-12-21
    # Gallery Node integration (Living Autopoietic Showcase)
    "GALLERY_AFFORDANCES",
    "GALLERY_CATEGORIES",
    "GalleryNode",
    "create_gallery_node",
    "get_gallery_node",
    "set_gallery_node",
    # 3D Projection Context (concept.projection.three.*)
    "THREE_AFFORDANCES",
    "THEME_REGISTRY",
    "QUALITY_CONFIGS",
    "NODE_DEFAULTS",
    "EDGE_DEFAULTS",
    "Quality",
    "ThemeName",
    "ThreeNodeNode",
    "ThreeEdgeNode",
    "ThreeThemeNode",
    "ThreeQualityNode",
    "ThreeContextResolver",
    "create_three_resolver",
    "create_three_node_node",
    "create_three_edge_node",
    "create_three_theme_node",
    "create_three_quality_node",
    # Unified factory
    "create_context_resolvers",
    # Typed-Hypergraph Context (self.context.* - AD-009 Context Management)
    "CONTEXT_AFFORDANCES",
    "ALL_STANDARD_EDGES",
    "EVIDENCE_EDGES",
    "REVERSE_EDGES",
    "SEMANTIC_EDGES",
    "SPEC_EDGES",
    "STRUCTURAL_EDGES",
    "TEMPORAL_EDGES",
    "TESTING_EDGES",
    "ContextGraph",
    "ContextNavNode",
    "ContextNode",
    "Trail",
    "TrailStep",
    "create_context_graph",
    "create_context_node",
    "get_context_nav_node",
    "get_reverse_edge",
    # Hyperedge Resolvers
    "ResolverRegistry",
    "agentese_path_to_file",
    "file_to_agentese_path",
    "get_resolver_registry",
    "register_resolver",
    "resolve_all_edges",
    "resolve_hyperedge",
    # Portal Token Context (self.portal.* - Portal Token Navigation)
    "PORTAL_AFFORDANCES",
    "PortalNavNode",
    "get_portal_nav_node",
    "set_portal_nav_node",
    # Exploration Harness Context (self.explore.* - Exploration with Safety)
    "EXPLORE_AFFORDANCES",
    "ExploreNode",
    "get_explore_node",
    "set_explore_node",
    # Collaboration Context (self.collaboration.* - Phase 5C)
    "COLLABORATION_AFFORDANCES",
    "CollaborationNode",
    # Repo Node (world.repo.* - Path validation for trail creation)
    "REPO_AFFORDANCES",
    "CREATABLE_EXTENSIONS",
    "RepoNode",
    "create_repo_node",
    "get_repo_node",
    "set_repo_node",
]
