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

Phase 6 Implementation (Advanced Embeddings & Vector DBs):
- SentenceTransformerEmbedder: Transformer-based embeddings (all-MiniLM-L6-v2, etc.)
- OpenAIEmbedder: OpenAI embedding API (text-embedding-3-small/large)
- CachedEmbedder: D-gent caching wrapper for API cost reduction
- ChromaDBBackend: Persistent vector DB (SQLite + vectors)
- FAISSBackend: High-performance in-memory index
- VectorBackend protocol: Pluggable vector database interface

Phase 7 Implementation (Three-Brain Hybrid):
- GraphBrain: Graph search using LineageGraph + TypeLattice (Brain 3)
- QueryFusion: Three-brain fusion layer (keyword + semantic + graph)
- VectorSemanticBrain: SemanticBrain with VectorBackend support
- Adaptive weighting based on query type classification
- Serendipity suggestions for unexpected discoveries

Phase 8 Implementation (D-gent Vector DB Integration):
- DgentVectorBackend: VectorBackend using D-gent's VectorAgent
- VectorCatalog: Unified catalog + vector DB with sync
- D-gent semantic features: curvature, voids, geodesics
- Migration utilities: Move between backends
- Tight L-gent + D-gent integration as per spec
"""

from .registry import Registry
from .search import Search
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
from .embedders import (
    EmbeddingMetadata,
    CachedEmbedder,
    create_best_available_embedder,
    compare_embedders,
    SENTENCE_TRANSFORMERS_AVAILABLE,
    OPENAI_AVAILABLE,
)
from .vector_backend import (
    VectorBackend,
    VectorSearchResult,
    create_vector_backend,
    CHROMADB_AVAILABLE,
    FAISS_AVAILABLE,
)
from .graph_search import (
    GraphBrain,
    GraphResult,
    SearchDirection,
    create_graph_brain,
)
from .fusion import (
    QueryFusion,
    FusedResult,
    QueryResponse,
    QueryType,
    create_query_fusion,
)
from .semantic_vector import (
    VectorSemanticBrain,
    create_vector_semantic_brain,
    create_best_semantic_brain,
)

# Check for D-gent VectorAgent availability
try:
    import numpy as np
    from agents.d.vector import NUMPY_AVAILABLE as DGENT_VECTOR_AVAILABLE
except ImportError:
    DGENT_VECTOR_AVAILABLE = False

# D-gent Vector DB integration (Phase 8)
if DGENT_VECTOR_AVAILABLE:
    from .vector_db import (
        DgentVectorBackend,
        VectorCatalog,
        VectorSyncState,
        create_dgent_vector_backend,
        create_vector_catalog,
        migrate_to_dgent_backend,
    )

# Conditional imports for optional dependencies
if SENTENCE_TRANSFORMERS_AVAILABLE:
    from .embedders import SentenceTransformerEmbedder
if OPENAI_AVAILABLE:
    from .embedders import OpenAIEmbedder
if CHROMADB_AVAILABLE:
    from .vector_backend import ChromaDBBackend
if FAISS_AVAILABLE:
    from .vector_backend import FAISSBackend

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
    "Search",
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
    # Advanced Embedders (Phase 6)
    "EmbeddingMetadata",
    "CachedEmbedder",
    "create_best_available_embedder",
    "compare_embedders",
    "SENTENCE_TRANSFORMERS_AVAILABLE",
    "OPENAI_AVAILABLE",
    # Vector Backends (Phase 6)
    "VectorBackend",
    "VectorSearchResult",
    "create_vector_backend",
    "CHROMADB_AVAILABLE",
    "FAISS_AVAILABLE",
    # Graph Search (Phase 7)
    "GraphBrain",
    "GraphResult",
    "SearchDirection",
    "create_graph_brain",
    # Fusion Layer (Phase 7)
    "QueryFusion",
    "FusedResult",
    "QueryResponse",
    "QueryType",
    "create_query_fusion",
    # Vector Semantic (Phase 7)
    "VectorSemanticBrain",
    "create_vector_semantic_brain",
    "create_best_semantic_brain",
    # D-gent Vector DB (Phase 8)
    "DGENT_VECTOR_AVAILABLE",
]

# Add conditional exports
if SENTENCE_TRANSFORMERS_AVAILABLE:
    __all__.append("SentenceTransformerEmbedder")
if OPENAI_AVAILABLE:
    __all__.append("OpenAIEmbedder")
if CHROMADB_AVAILABLE:
    __all__.append("ChromaDBBackend")
if FAISS_AVAILABLE:
    __all__.append("FAISSBackend")
if DGENT_VECTOR_AVAILABLE:
    __all__.extend(
        [
            "DgentVectorBackend",
            "VectorCatalog",
            "VectorSyncState",
            "create_dgent_vector_backend",
            "create_vector_catalog",
            "migrate_to_dgent_backend",
        ]
    )
