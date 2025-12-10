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

Integration:
- D-gent: Storage layer (UnifiedMemory, VectorAgent)
- L-gent: Embedding space (VectorBackend, Embedder)
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
]
