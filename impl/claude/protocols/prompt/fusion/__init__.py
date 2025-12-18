"""
Fusion Module: Multi-source semantic fusion for the Evergreen Prompt System.

Wave 5 of the Prompt Monad architecture.

This module provides:
- Semantic similarity computation between section contents
- Conflict detection (contradictions between sources)
- Policy-based resolution using HabitEncoder's PolicyVector
- The main PromptFusion class that ties it all together

Per taste decision: merge heuristically, not with hard precedence.
Semantic fusion uses similarity and policy vectors to intelligently
combine content from multiple sources.
"""

from .conflict import (
    MAX_CONTENT_LENGTH as CONFLICT_MAX_CONTENT_LENGTH,
    Conflict,
    ConflictDetector,
    ConflictError,
    ConflictSeverity,
    ConflictType,
    detect_conflicts,
)
from .fusioner import (
    MAX_CONTENT_LENGTH as FUSION_MAX_CONTENT_LENGTH,
    FusionError,
    FusionResult,
    PromptFusion,
    fuse_sources,
)
from .resolution import (
    MAX_RIGIDITY,
    MIN_RIGIDITY,
    PolicyResolver,
    Resolution,
    ResolutionError,
    ResolutionStrategy,
    resolve_conflict,
)
from .similarity import (
    MAX_CONTENT_LENGTH as SIMILARITY_MAX_CONTENT_LENGTH,
    SemanticSimilarity,
    SimilarityError,
    SimilarityResult,
    SimilarityStrategy,
    compute_similarity,
)

__all__ = [
    # Similarity
    "SemanticSimilarity",
    "SimilarityResult",
    "SimilarityStrategy",
    "SimilarityError",
    "compute_similarity",
    "SIMILARITY_MAX_CONTENT_LENGTH",
    # Conflicts
    "Conflict",
    "ConflictType",
    "ConflictSeverity",
    "ConflictError",
    "ConflictDetector",
    "detect_conflicts",
    "CONFLICT_MAX_CONTENT_LENGTH",
    # Resolution
    "Resolution",
    "ResolutionStrategy",
    "ResolutionError",
    "PolicyResolver",
    "resolve_conflict",
    "MIN_RIGIDITY",
    "MAX_RIGIDITY",
    # Fusioner
    "PromptFusion",
    "FusionResult",
    "FusionError",
    "fuse_sources",
    "FUSION_MAX_CONTENT_LENGTH",
]
