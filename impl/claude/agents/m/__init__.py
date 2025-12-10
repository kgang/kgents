"""
M-gents: Holographic Associative Memory.

Memory as generative reconstruction, not retrieval.
The hologram metaphor isn't decorative—it's architecturally load-bearing.

Key Components:
- HolographicMemory: The core memory substrate
- RecollectionAgent: Generative recall from cues
- ConsolidationAgent: Background memory processing (hypnagogic)
- TieredMemory: Sensory → Working → Long-term hierarchy

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
]
