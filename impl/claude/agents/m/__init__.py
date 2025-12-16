"""
M-gents: Holographic Associative Memory.

Memory as generative reconstruction, not retrieval.
The hologram metaphor isn't decorative—it's architecturally load-bearing.

Key Components:
- HolographicMemory: The core memory substrate
- RecollectionAgent: Generative recall from cues
- ConsolidationAgent: Background memory processing (hypnagogic)
- TieredMemory: Sensory → Working → Long-term hierarchy

Phase 2 - D-gent Integration:
- DgentBackedHolographicMemory: Persistent holographic memory
- PersistentTieredMemory: Full tier persistence
- AssociativeWebMemory: Spreading activation
- TemporalMemory: Time-based navigation

Phase 3 - Advanced Primitives:
- ProspectiveAgent: Predictive memory (situation → predicted actions)
- EthicalGeometryAgent: Learned constraint manifold (memory as conscience)
- ContextualRecallAgent: Context-dependent memory retrieval

Phase 4 - L-gent + B-gent Integration:
- VectorHolographicMemory: L-gent vector backend integration
- BudgetedMemory: B-gent token economics integration
- ResolutionBudget: Resolution as economic resource
- MemoryEconomicsDashboard: Budget monitoring

Phase 5 - Holographic Cartography:
- CartographerAgent: Generate HoloMaps from memory space
- PathfinderAgent: Navigate via desire lines
- ContextInjector: Produce optimal context for any turn
- HoloMap: Fuzzy isomorphism of knowledge state
- Attractor: Dense memory cluster (landmark)
- WeightedEdge: Desire line (historical path)
- Horizon: Progressive disclosure boundary

Phase 6 - Four Pillars (Autopoietic Memory):
- MemoryCrystal: Holographic memory with graceful degradation
- PheromoneField: Stigmergic coordination via traces
- StigmergicAgent: Gradient-following navigation
- LanguageGame: Wittgensteinian memory access

Integration:
- D-gent: Storage layer (UnifiedMemory, VectorAgent)
- L-gent: Embedding space (VectorBackend, Embedder)
- N-gent: Semantic traces (desire lines)
- B-gent: Memory economics (token budget)
"""

from .cartographer import (
    CartographerAgent,
    CartographerConfig,
    DesireLineComputer,
    MockTrace,
    MockTraceStore,
    MockVectorSearch,
    create_cartographer,
    create_mock_cartographer,
)

# Phase 5: Holographic Cartography
from .cartography import (
    Attractor,
    ContextVector,
    # Context injection types
    FoveatedView,
    # Navigation types
    Goal,
    # Core types
    HoloMap,
    Horizon,
    InjectionRequest,
    NavigationPlan,
    OptimalContext,
    Region,
    Resolution,
    Void,
    WeightedEdge,
    create_attractor,
    create_context_vector,
    create_desire_line,
    # Factory functions
    create_empty_holomap,
)

# Phase 5 Polish: O-gent, Ψ-gent, I-gent Integrations
from .cartography_integrations import (
    # O-gent: Health monitoring
    CartographicObserver,
    EdgeHealth,
    LandmarkHealth,
    MapHealth,
    MapRenderConfig,
    # I-gent: Visualization
    MapRenderer,
    # Ψ-gent: Metaphor discovery
    MetaphorLocator,
    MetaphorMatch,
    MetaphorNeighborhood,
    annotate_and_render,
    # Factory functions
    create_cartographic_observer,
    create_map_renderer,
    create_metaphor_locator,
)

# Phase 5: Compaction
from .compaction import (
    AutoCompactionDaemon,
    CompactionEvent,
    CompactionPolicy,
    Compactor,
    StrategyResult,
    apply_pressure_based_strategy,
    apply_uniform_strategy,
    create_compactor,
    create_daemon,
)
from .consolidation import (
    ConsolidationAgent,
    ConsolidationResult,
    TemperatureProfile,
)
from .context_injector import (
    ContextInjector,
    InjectorConfig,
    create_context_injector,
    inject_context,
)

# Phase 6: Four Pillars (Autopoietic Memory)
from .crystal import (
    CrystalPattern,
    MemoryCrystal,
    NumPyCrystal,
    ResonanceMatch,
    create_crystal,
)

# Phase 7: Crystallization Integration
from .crystallization_integration import (
    CrystallizationEvent,
    KgentCrystallizer,
    ReaperIntegration,
    SubstrateCrystallizer,
    create_kgent_crystallizer,
    create_reaper_integration,
    create_substrate_crystallizer,
)
from .dgent_backend import (
    AssociativeWebMemory,
    DgentBackedHolographicMemory,
    PersistenceConfig,
    TemporalMemory,
    create_associative_memory,
    create_dgent_memory,
    create_temporal_memory,
)
from .games import (
    ComposedGame,
    Direction,
    LanguageGame,
    Move,
    PolynomialPosition,
    create_associative_game,
    create_dialectical_game,
    create_episodic_game,
    create_navigation_game,
    create_recall_game,
    game_to_polynomial,
    polynomial_signature,
)

# Phase 8: Ghost ↔ Substrate Sync
from .ghost_sync import (
    GhostAwareReaperIntegration,
    GhostSyncAllocation,
    GhostSyncEvent,
    GhostSyncManager,
    create_ghost_aware_reaper,
    create_ghost_sync_manager,
    wrap_with_ghost_sync,
)
from .holographic import (
    CompressionLevel,
    HolographicMemory,
    MemoryPattern,
    ResonanceResult,
)

# Phase 9: Importers (Spike 3A)
from .importers import (
    FrontmatterData,
    ImportProgress,
    MarkdownEngram,
    MarkdownImporter,
    ObsidianVaultParser,
    WikiLink,
    create_importer_with_best_embedder,
    create_lgent_embedder,
    extract_code_blocks,
    extract_frontmatter,
    extract_headings,
    extract_tags,
    extract_wikilinks,
    generate_concept_id,
    parse_markdown,
    strip_markdown_formatting,
)
from .inference import (
    ActiveInferenceAgent,
    Belief,
    FreeEnergyBudget,
    InferenceAction,
    InferenceGuidedCrystal,
    PredictiveMemory,
    create_guided_crystal,
    create_inference_agent,
)
from .memory_budget import (
    BudgetedMemory,
    InsufficientBudgetError,
    MemoryCostModel,
    MemoryEconomicsDashboard,
    MemoryEconomicsReport,
    MemoryReceipt,
    ResolutionAllocation,
    ResolutionBudget,
    create_budgeted_memory,
    create_mock_bank,
)
from .pathfinder import (
    PathAnalysis,
    PathfinderAgent,
    PathfinderConfig,
    analyze_path,
    create_pathfinder,
)
from .persistent_tiered import (
    MemoryHierarchyStats,
    NarrativeMemory,
    PersistentTieredMemory,
    PersistentWorkingMemory,
    TierConfig,
    TierStats,
    create_narrative_memory,
    create_persistent_tiered_memory,
)
from .polynomial import (
    MemoryDirection,
    MemoryMode,
    MemoryOutput,
    MemoryPolynomial,
    MemoryState,
    create_memory_polynomial,
)
from .polynomial import (
    game_to_polynomial as polynomial_game_to_polynomial,  # Rename to avoid conflict
)
from .prospective import (
    ActionHistory,
    ActionProposal,
    ActionRecord,
    # ContextualRecallAgent
    ContextualQuery,
    ContextualRecallAgent,
    EthicalExperience,
    # EthicalGeometryAgent
    EthicalGeometry,
    EthicalGeometryAgent,
    EthicalPath,
    EthicalPosition,
    EthicalRegion,
    PredictedAction,
    # ProspectiveAgent
    ProspectiveAgent,
    Situation,
    create_ethical_agent,
    # Factory functions
    create_prospective_agent,
)
from .recollection import (
    Cue,
    Recollection,
    RecollectionAgent,
    ReconstructionRequest,
)

# Phase 5: Routing
from .routing import (
    CategoricalRouter,
    GradientMap,
    RouteTrace,
    RoutingDecision,
    Task,
    TaskMorphism,
    create_router,
    create_task,
    verify_adjunction,
)

# Phase 6: Semantic Routing
from .semantic_routing import (
    EmbeddingSimilarity,
    FilteredSenseResult,
    GraphSimilarity,
    KeywordSimilarity,
    LocalityConfig,
    PrefixSimilarity,
    SemanticGradientMap,
    SemanticRouter,
    SimilarityProvider,
    create_lgent_semantic_router,
    create_semantic_router,
)
from .stigmergy import (
    EnhancedStigmergicAgent,
    PheromoneField,
    SenseResult,
    SimpleConceptSpace,
    StigmergicAgent,
    Trace,
    create_ant_colony_optimization,
)

# Phase 5: Substrate
from .substrate import (
    AgentId,
    Allocation,
    CompactionTrigger,
    CrystalPolicy,
    DedicatedCrystal,
    LifecyclePolicy,
    MemoryQuota,
    PromotionDecision,
    SharedSubstrate,
    create_allocation_for_agent,
    create_substrate,
)
from .tiered import (
    AttentionFilter,
    MemoryTier,
    TieredMemory,
)
from .vector_holographic import (
    ClusterInfo,
    VectorHolographicMemory,
    VectorMemoryConfig,
    VoidInfo,
    create_simple_vector_memory,
    create_vector_holographic_memory,
)

__all__ = [
    # Core
    "HolographicMemory",
    "MemoryPattern",
    "ResonanceResult",
    "CompressionLevel",
    # Recollection
    "RecollectionAgent",
    "Recollection",
    "Cue",
    "ReconstructionRequest",
    # Consolidation
    "ConsolidationAgent",
    "ConsolidationResult",
    "TemperatureProfile",
    # Tiered
    "TieredMemory",
    "MemoryTier",
    "AttentionFilter",
    # Phase 2: D-gent Integration
    "DgentBackedHolographicMemory",
    "AssociativeWebMemory",
    "TemporalMemory",
    "PersistenceConfig",
    "create_dgent_memory",
    "create_associative_memory",
    "create_temporal_memory",
    "PersistentTieredMemory",
    "PersistentWorkingMemory",
    "NarrativeMemory",
    "TierConfig",
    "TierStats",
    "MemoryHierarchyStats",
    "create_persistent_tiered_memory",
    "create_narrative_memory",
    # Phase 3: Prospective
    "ProspectiveAgent",
    "Situation",
    "ActionRecord",
    "ActionHistory",
    "PredictedAction",
    # Phase 3: Ethical Geometry
    "EthicalGeometry",
    "EthicalGeometryAgent",
    "EthicalExperience",
    "EthicalPosition",
    "EthicalRegion",
    "EthicalPath",
    "ActionProposal",
    # Phase 3: Contextual Recall
    "ContextualQuery",
    "ContextualRecallAgent",
    "create_prospective_agent",
    "create_ethical_agent",
    # Phase 4: L-gent VectorHolographicMemory
    "VectorHolographicMemory",
    "VectorMemoryConfig",
    "VoidInfo",
    "ClusterInfo",
    "create_vector_holographic_memory",
    "create_simple_vector_memory",
    # Phase 4: B-gent MemoryBudget
    "BudgetedMemory",
    "MemoryCostModel",
    "MemoryReceipt",
    "ResolutionBudget",
    "ResolutionAllocation",
    "MemoryEconomicsReport",
    "MemoryEconomicsDashboard",
    "InsufficientBudgetError",
    "create_budgeted_memory",
    "create_mock_bank",
    # Phase 5: Holographic Cartography
    "HoloMap",
    "Attractor",
    "WeightedEdge",
    "ContextVector",
    "Horizon",
    "Region",
    "Void",
    "Resolution",
    "Goal",
    "NavigationPlan",
    "FoveatedView",
    "InjectionRequest",
    "OptimalContext",
    "create_empty_holomap",
    "create_context_vector",
    "create_attractor",
    "create_desire_line",
    # Cartographer
    "CartographerAgent",
    "CartographerConfig",
    "DesireLineComputer",
    "MockVectorSearch",
    "MockTraceStore",
    "MockTrace",
    "create_cartographer",
    "create_mock_cartographer",
    # Pathfinder
    "PathfinderAgent",
    "PathfinderConfig",
    "PathAnalysis",
    "analyze_path",
    "create_pathfinder",
    # Context Injector
    "ContextInjector",
    "InjectorConfig",
    "inject_context",
    "create_context_injector",
    # Phase 5 Polish: Integrations
    # O-gent
    "CartographicObserver",
    "EdgeHealth",
    "LandmarkHealth",
    "MapHealth",
    "create_cartographic_observer",
    # Ψ-gent
    "MetaphorLocator",
    "MetaphorMatch",
    "MetaphorNeighborhood",
    "create_metaphor_locator",
    # I-gent
    "MapRenderer",
    "MapRenderConfig",
    "create_map_renderer",
    "annotate_and_render",
    # Phase 6: Four Pillars (Autopoietic Memory)
    # Memory Crystal
    "MemoryCrystal",
    "NumPyCrystal",
    "CrystalPattern",
    "ResonanceMatch",
    "create_crystal",
    # Active Inference
    "ActiveInferenceAgent",
    "Belief",
    "FreeEnergyBudget",
    "InferenceAction",
    "InferenceGuidedCrystal",
    "PredictiveMemory",
    "create_inference_agent",
    "create_guided_crystal",
    # Stigmergy
    "PheromoneField",
    "Trace",
    "SenseResult",
    "StigmergicAgent",
    "EnhancedStigmergicAgent",
    "SimpleConceptSpace",
    "create_ant_colony_optimization",
    # Language Games
    "LanguageGame",
    "Move",
    "Direction",
    "ComposedGame",
    "PolynomialPosition",
    "create_recall_game",
    "create_navigation_game",
    "create_dialectical_game",
    "create_associative_game",
    "create_episodic_game",
    "game_to_polynomial",
    "polynomial_signature",
    # Memory Polynomial
    "MemoryPolynomial",
    "MemoryState",
    "MemoryDirection",
    "MemoryOutput",
    "MemoryMode",
    "create_memory_polynomial",
    "polynomial_game_to_polynomial",
    # Phase 5: Substrate
    "AgentId",
    "MemoryQuota",
    "CompactionTrigger",
    "LifecyclePolicy",
    "Allocation",
    "PromotionDecision",
    "CrystalPolicy",
    "DedicatedCrystal",
    "SharedSubstrate",
    "create_substrate",
    "create_allocation_for_agent",
    # Phase 5: Routing
    "Task",
    "TaskMorphism",
    "RoutingDecision",
    "GradientMap",
    "RouteTrace",
    "CategoricalRouter",
    "verify_adjunction",
    "create_router",
    "create_task",
    # Phase 6: Semantic Routing
    "SimilarityProvider",
    "PrefixSimilarity",
    "KeywordSimilarity",
    "EmbeddingSimilarity",
    "GraphSimilarity",
    "LocalityConfig",
    "FilteredSenseResult",
    "SemanticGradientMap",
    "SemanticRouter",
    "create_semantic_router",
    "create_lgent_semantic_router",
    # Phase 5: Compaction
    "CompactionPolicy",
    "CompactionEvent",
    "Compactor",
    "AutoCompactionDaemon",
    "StrategyResult",
    "apply_uniform_strategy",
    "apply_pressure_based_strategy",
    "create_compactor",
    "create_daemon",
    # Phase 7: Crystallization Integration
    "CrystallizationEvent",
    "SubstrateCrystallizer",
    "ReaperIntegration",
    "KgentCrystallizer",
    "create_substrate_crystallizer",
    "create_reaper_integration",
    "create_kgent_crystallizer",
    # Phase 8: Ghost ↔ Substrate Sync
    "GhostSyncEvent",
    "GhostSyncManager",
    "GhostSyncAllocation",
    "GhostAwareReaperIntegration",
    "create_ghost_sync_manager",
    "create_ghost_aware_reaper",
    "wrap_with_ghost_sync",
    # Phase 9: Importers (Spike 3A)
    "MarkdownEngram",
    "FrontmatterData",
    "WikiLink",
    "ImportProgress",
    "ObsidianVaultParser",
    "MarkdownImporter",
    "create_importer_with_best_embedder",
    "create_lgent_embedder",
    "extract_frontmatter",
    "extract_wikilinks",
    "extract_tags",
    "extract_headings",
    "extract_code_blocks",
    "strip_markdown_formatting",
    "generate_concept_id",
    "parse_markdown",
]
