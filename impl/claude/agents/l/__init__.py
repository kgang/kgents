"""
L-gent: The Synaptic Librarian

Knowledge curation, semantic discovery, and ecosystem connectivity.

Phase 1 Implementation (for G-gent integration):
- Core types (EntityType.TONGUE support)
- Registry (in-memory catalog)
- Basic search (keyword matching)

Phase 2 Implementation (D-gent integration):
- PersistentRegistry: File-backed catalog with D-gent storage
- Auto-save strategies (ON_WRITE, MANUAL, ON_EXIT)
- Catalog history tracking

Phase 3 Implementation (Lineage Layer):
- LineageGraph: DAG-based provenance tracking
- Relationship types (successor_to, forked_from, depends_on, etc.)
- Ancestor/descendant traversal
- Cycle detection

Phase 4 Implementation (Lattice Layer):
- TypeLattice: Type compatibility and composition planning
- Type operations (is_subtype, meet, join)
- Composition verification (can_compose, verify_pipeline)
- Path finding (find_path, suggest_composition)

Phase 5 Implementation (Semantic Search):
- SemanticBrain: Vector-based intent matching (TF-IDF embeddings)
- SemanticRegistry: Registry + automatic semantic indexing
- Hybrid search: Combine keyword + semantic results
- Embedder protocol: Pluggable embedding backends

Future Phases:
- Advanced embeddings (sentence-transformers, OpenAI)
- Vector database integration (for large catalogs)
"""

from .registry import Registry
from .types import (
    Catalog,
    CatalogEntry,
    CompatibilityReport,
    EntityType,
    SearchResult,
    Status,
)
from .persistence import (
    PersistentRegistry,
    PersistenceConfig,
    SaveStrategy,
    create_persistent_registry,
    load_or_create_registry,
)
from .lineage import (
    LineageGraph,
    Relationship,
    RelationshipType,
    LineageError,
    record_evolution,
    record_fork,
    record_dependency,
)
from .lattice import (
    TypeLattice,
    TypeNode,
    TypeKind,
    SubtypeEdge,
    CompositionResult,
    CompositionStage,
    PipelineVerification,
    CompositionSuggestion,
    create_lattice,
)
from .semantic import (
    SemanticBrain,
    SemanticResult,
    Embedder,
    SimpleEmbedder,
    create_semantic_brain,
)
from .semantic_registry import (
    SemanticRegistry,
    create_semantic_registry,
)

__all__ = [
    # Core types
    "EntityType",
    "Status",
    "CatalogEntry",
    "Catalog",
    "SearchResult",
    "CompatibilityReport",
    # Registry (in-memory)
    "Registry",
    # Persistent Registry (D-gent integration)
    "PersistentRegistry",
    "PersistenceConfig",
    "SaveStrategy",
    "create_persistent_registry",
    "load_or_create_registry",
    # Lineage (Phase 3)
    "LineageGraph",
    "Relationship",
    "RelationshipType",
    "LineageError",
    "record_evolution",
    "record_fork",
    "record_dependency",
    # Lattice (Phase 4)
    "TypeLattice",
    "TypeNode",
    "TypeKind",
    "SubtypeEdge",
    "CompositionResult",
    "CompositionStage",
    "PipelineVerification",
    "CompositionSuggestion",
    "create_lattice",
    # Semantic (Phase 5)
    "SemanticBrain",
    "SemanticResult",
    "Embedder",
    "SimpleEmbedder",
    "create_semantic_brain",
    "SemanticRegistry",
    "create_semantic_registry",
]
