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

Integration:
- D-gent: Storage layer (UnifiedMemory, VectorAgent)
- L-gent: Embedding space (VectorBackend, Embedder)
- N-gent: Semantic traces (desire lines)
- B-gent: Memory economics (token budget)
"""

from .holographic import (
    HolographicMemory,
    MemoryPattern,
    ResonanceResult,
    CompressionLevel,
)
from .recollection import (
    RecollectionAgent,
    Recollection,
    Cue,
    ReconstructionRequest,
)
from .consolidation import (
    ConsolidationAgent,
    ConsolidationResult,
    TemperatureProfile,
)
from .tiered import (
    TieredMemory,
    MemoryTier,
    AttentionFilter,
)
from .dgent_backend import (
    DgentBackedHolographicMemory,
    AssociativeWebMemory,
    TemporalMemory,
    PersistenceConfig,
    create_dgent_memory,
    create_associative_memory,
    create_temporal_memory,
)
from .persistent_tiered import (
    PersistentTieredMemory,
    PersistentWorkingMemory,
    NarrativeMemory,
    TierConfig,
    TierStats,
    MemoryHierarchyStats,
    create_persistent_tiered_memory,
    create_narrative_memory,
)
from .prospective import (
    # ProspectiveAgent
    ProspectiveAgent,
    Situation,
    ActionRecord,
    ActionHistory,
    PredictedAction,
    # EthicalGeometryAgent
    EthicalGeometry,
    EthicalGeometryAgent,
    EthicalExperience,
    EthicalPosition,
    EthicalRegion,
    EthicalPath,
    ActionProposal,
    # ContextualRecallAgent
    ContextualQuery,
    ContextualRecallAgent,
    # Factory functions
    create_prospective_agent,
    create_ethical_agent,
)
from .vector_holographic import (
    VectorHolographicMemory,
    VectorMemoryConfig,
    VoidInfo,
    ClusterInfo,
    create_vector_holographic_memory,
    create_simple_vector_memory,
)
from .memory_budget import (
    BudgetedMemory,
    MemoryCostModel,
    MemoryReceipt,
    ResolutionBudget,
    ResolutionAllocation,
    MemoryEconomicsReport,
    MemoryEconomicsDashboard,
    InsufficientBudgetError,
    create_budgeted_memory,
    create_mock_bank,
)

# Phase 5: Holographic Cartography
from .cartography import (
    # Core types
    HoloMap,
    Attractor,
    WeightedEdge,
    ContextVector,
    Horizon,
    Region,
    Void,
    Resolution,
    # Navigation types
    Goal,
    NavigationPlan,
    # Context injection types
    FoveatedView,
    InjectionRequest,
    OptimalContext,
    # Factory functions
    create_empty_holomap,
    create_context_vector,
    create_attractor,
    create_desire_line,
)
from .cartographer import (
    CartographerAgent,
    CartographerConfig,
    DesireLineComputer,
    # Mock implementations
    MockVectorSearch,
    MockTraceStore,
    MockTrace,
    # Factory functions
    create_cartographer,
    create_mock_cartographer,
)
from .pathfinder import (
    PathfinderAgent,
    PathfinderConfig,
    PathAnalysis,
    analyze_path,
    create_pathfinder,
)
from .context_injector import (
    ContextInjector,
    InjectorConfig,
    inject_context,
    create_context_injector,
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
]
