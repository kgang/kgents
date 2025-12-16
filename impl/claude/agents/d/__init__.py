"""
D-gents: Data Agents for stateful computation.

This package provides the core abstractions for state management in kgents:

- DataAgent[S]: The protocol all D-gents implement
- VolatileAgent[S]: In-memory state (fast, ephemeral)
- PersistentAgent[S]: File-backed state (durable)
- VectorAgent[S]: Semantic search via embeddings (Noosphere)
- GraphAgent[N]: Relational lattice with graph operations (Noosphere)
- StreamAgent[E,S]: Event-sourced state with time-travel (Noosphere)
- Symbiont[I,O,S]: Fuses pure logic with stateful memory

Phase 3 Extended Protocols:
- TransactionalDataAgent[S]: ACID transactions with savepoints (time-travel debugging)
- QueryableDataAgent[S]: Structured queries over state
- ObservableDataAgent[S]: Reactive subscriptions and change notifications
- UnifiedMemory[S]: Compose all memory modes through a single interface

Phase 4 Noosphere Layer:
- SemanticManifold[S]: Curved semantic space with curvature, voids, geodesics
- TemporalWitness[E,S]: Enhanced temporal observation with drift detection
- RelationalLattice[N]: Full lattice theory with meet, join, entailment
- MemoryGarden[S]: Joy-inducing memory lifecycle (seeds, saplings, trees, flowers, compost)

State management philosophy:
- Pure logic should be stateless
- D-gents contain the complexity of memory
- Symbiont makes stateful agents composable via >>
- Noosphere layer provides advanced memory modes (semantic, temporal, relational)

Example:
    >>> from agents.d import VolatileAgent, Symbiont
    >>>
    >>> def counter_logic(inc: int, count: int) -> tuple[int, int]:
    ...     new_count = count + inc
    ...     return new_count, new_count
    ...
    >>> memory = VolatileAgent(_state=0)
    >>> counter = Symbiont(logic=counter_logic, memory=memory)
    >>>
    >>> await counter.invoke(1)  # Returns 1
    >>> await counter.invoke(5)  # Returns 6 (remembers previous state)
"""

from .cached import CachedAgent

# Context Engineering (Phase 6: Context Protocol)
from .component_renderer import (
    ComponentRenderer,
    ContextProps,
    ContextStatus,
    MessageProps,
    create_component_renderer,
    render_for_frontend,
    render_minimal,
)
from .context_session import (
    ContextInput,
    ContextOutput,
    ContextPressureError,
    ContextSession,
    ContextState,
    create_context_session,
    from_messages,
)
from .context_window import (
    ContextMeta,
    ContextSnapshot,
    ContextWindow,
    Turn,
    TurnRole,
    create_context_window,
)
from .context_window import (
    from_messages as context_from_messages,
)
from .entropy import EntropyConstrainedAgent, entropy_constrained
from .errors import (
    DriftDetectionError,
    EdgeNotFoundError,
    LatticeError,
    NodeNotFoundError,
    # Noosphere errors
    NoosphereError,
    SemanticError,
    StateCorruptionError,
    StateError,
    StateNotFoundError,
    StateSerializationError,
    StorageError,
    TemporalError,
    VoidNotFoundError,
)
from .lens import (
    # Core Lens
    Lens,
    # Composed lens validation
    LensValidation,
    # Prism (optional fields)
    Prism,
    # Traversal (collections)
    Traversal,
    attr_lens,
    dict_items_traversal,
    dict_keys_traversal,
    dict_values_traversal,
    field_lens,
    identity_lens,
    index_lens,
    key_lens,
    list_traversal,
    optional_field_prism,
    optional_index_prism,
    optional_key_prism,
    validate_composed_lens,
    verify_get_put_law,
    verify_lens_laws,
    verify_prism_laws,
    verify_put_get_law,
    verify_put_put_law,
    verify_traversal_laws,
)
from .lens_agent import LensAgent, focused

# Persistence Extensions: Versioning, Backup, Compression
from .persistence_ext import (
    BackupManager,
    # Backup/restore
    BackupMetadata,
    CompressedPersistentAgent,
    CompressionConfig,
    # Compression
    CompressionLevel,
    Migration,
    MigrationDirection,
    MigrationRegistry,
    # Schema versioning
    SchemaVersion,
    VersionedPersistentAgent,
    VersionedState,
    create_compressed_agent,
    # Convenience functions
    create_versioned_agent,
)
from .persistent import PersistentAgent

# Phase 3 Polyfunctor: D-gent Polynomial (Memory States)
from .polynomial import (
    MEMORY_POLYNOMIAL,
    ForgetCommand,
    LoadCommand,
    MemoryPhase,
    MemoryPolynomialAgent,
    MemoryResponse,
    QueryCommand,
    StoreCommand,
    memory_directions,
    memory_transition,
    reset_memory,
)

# Context Projector (Galois Connection)
from .projector import (
    AdaptiveThreshold,
    CompressionResult,
    ContextCompressionConfig,
    ContextProjector,
    DefaultSummarizer,
    Summarizer,
    auto_compress,
    create_projector,
)

# Prompt Building (Context Protocol)
from .prompt_builder import (
    PromptBuilder,
    build_builder_prompt,
    build_citizen_prompt,
    build_kgent_prompt,
    create_prompt_builder,
    render_constraints,
    render_eigenvectors_6d,
    render_eigenvectors_7d,
)
from .protocol import DataAgent
from .symbiont import Symbiont
from .volatile import VolatileAgent

# Noosphere Layer: Advanced D-gent types
# Vector requires numpy (optional dependency)
try:
    from .vector import (
        DistanceMetric,
        Point,
        VectorAgent,
        VectorEntry,
        Void,
    )

    _VECTOR_AVAILABLE = True
except ImportError:
    _VECTOR_AVAILABLE = False
    VectorAgent = None  # type: ignore
    VectorEntry = None  # type: ignore
    Point = None  # type: ignore
    Void = None  # type: ignore
    DistanceMetric = None  # type: ignore

from .graph import (
    Edge,
    EdgeKind,
    GraphAgent,
    GraphNode,
    Subgraph,
)
from .observable import (
    Change,
    ChangeType,
    ObservableDataAgent,
    ObservableError,
    Subscription,
)
from .queryable import (
    Operator,
    PathNotFoundError,
    Predicate,
    Query,
    QueryableDataAgent,
    QueryError,
    QueryResult,
    contains,
    # Predicate helpers
    eq,
    exists,
    ge,
    gt,
    in_list,
    le,
    lt,
    matches,
    ne,
)
from .stream import (
    DriftReport,
    EventRecord,
    StreamAgent,
    Vector,
    WitnessReport,
)

# Phase 3: Extended Protocols
from .transactional import (
    RollbackError,
    Savepoint,
    SavepointError,
    Transaction,
    TransactionalDataAgent,
    TransactionError,
    TransactionState,
)
from .unified import (
    LayerNotAvailableError,
    LensedUnifiedMemory,
    MemoryConfig,
    MemoryEntry,
    MemoryLayer,
    UnifiedMemory,
    UnifiedMemoryError,
    create_unified_memory,
)

# Phase 4: Noosphere Layer
# SemanticManifold requires numpy (optional dependency)
try:
    from .manifold import (
        CurvatureRegion,
        Geodesic,
        ManifoldStats,
        SemanticCluster,
        SemanticManifold,
        SemanticPoint,
        SemanticVoid,
    )

    _MANIFOLD_AVAILABLE = True
except ImportError:
    _MANIFOLD_AVAILABLE = False
    SemanticManifold = None  # type: ignore
    SemanticPoint = None  # type: ignore
    SemanticVoid = None  # type: ignore
    Geodesic = None  # type: ignore
    SemanticCluster = None  # type: ignore
    ManifoldStats = None  # type: ignore
    CurvatureRegion = None  # type: ignore

# Phase 2.4: StateCrystal (Checkpoints with Comonadic Lineage)
from .crystal import (
    CrystallizationEngine,
    CrystallizationResult,
    CrystalReaper,
    FocusFragment,
    ReapResult,
    ResumeResult,
    StateCrystal,
    TaskState,
    TaskStatus,
    create_crystal_engine,
    create_task_state,
)
from .garden import (
    Contradiction,
    Evidence,
    EvidenceType,
    GardenEntry,
    GardenStats,
    Insight,
    Lifecycle,
    MemoryGarden,
    Nutrients,
)
from .lattice import (
    EntailmentProof,
    LatticeNode,
    LatticeRelation,
    LatticeStats,
    MeetJoinResult,
    RelationalLattice,
)

# Phase 2.3: Pulse (Zero-Cost Vitality Signals)
from .pulse import (
    AgentPhase,
    Pulse,
    VitalityAnalyzer,
    VitalityStatus,
    create_analyzer,
    create_pulse,
    create_pulse_from_window,
)
from .witness import (
    DriftSeverity,
    EntropyLevel,
    TemporalSnapshot,
    TemporalWitness,
    TimelineEntry,
    Trajectory,
    WitnessContext,
)

# Phase 5: Database Backends (optional dependencies)
try:
    from .sql_agent import (
        PostgreSQLBackend,
        SQLAgent,
        SQLBackend,
        SQLiteBackend,
        create_postgres_agent,
        create_sqlite_agent,
    )

    _SQL_AVAILABLE = True
except ImportError:
    _SQL_AVAILABLE = False
    SQLAgent = None  # type: ignore
    SQLBackend = None  # type: ignore
    SQLiteBackend = None  # type: ignore
    PostgreSQLBackend = None  # type: ignore
    create_sqlite_agent = None  # type: ignore
    create_postgres_agent = None  # type: ignore

try:
    from .redis_agent import (
        RedisAgent,
        create_redis_agent,
        create_valkey_agent,
    )

    _REDIS_AVAILABLE = True
except ImportError:
    _REDIS_AVAILABLE = False
    RedisAgent = None  # type: ignore
    create_redis_agent = None  # type: ignore
    create_valkey_agent = None  # type: ignore

# Phase 3+: Infrastructure Backends (Instance DB Integration)
try:
    from .infra_backends import (
        ContentHash,
        CortexAdapter,
        CortexAdapterConfig,
        GhostMemoryError,
        InfraBackendError,
        InstanceDBRelationalBackend,
        InstanceDBRelationalBackendConfig,
        InstanceDBVectorBackend,
        InstanceDBVectorBackendConfig,
        RecallResult,
        StaleEmbeddingError,
        VectorMetadata,
        create_cortex_adapter,
        create_relational_backend,
        create_vector_backend,
    )

    _INFRA_BACKENDS_AVAILABLE = True
except ImportError:
    _INFRA_BACKENDS_AVAILABLE = False
    InstanceDBVectorBackend = None  # type: ignore
    InstanceDBVectorBackendConfig = None  # type: ignore
    InstanceDBRelationalBackend = None  # type: ignore
    InstanceDBRelationalBackendConfig = None  # type: ignore
    CortexAdapter = None  # type: ignore
    CortexAdapterConfig = None  # type: ignore
    ContentHash = None  # type: ignore
    VectorMetadata = None  # type: ignore
    RecallResult = None  # type: ignore
    InfraBackendError = None  # type: ignore
    GhostMemoryError = None  # type: ignore
    StaleEmbeddingError = None  # type: ignore
    create_vector_backend = None  # type: ignore
    create_relational_backend = None  # type: ignore
    create_cortex_adapter = None  # type: ignore

# Phase 3+: Bicameral Memory (Ghost Detection + Self-Healing)
try:
    from .bicameral import (
        BicameralConfig,
        BicameralCortex,
        BicameralError,
        BicameralMemory,
        CoherencyError,
        CoherencyReport,
        GhostRecord,
        HemisphereRole,
        StaleRecord,
        create_bicameral_cortex,
        create_bicameral_memory,
    )

    _BICAMERAL_AVAILABLE = True
except ImportError:
    _BICAMERAL_AVAILABLE = False
    BicameralMemory = None  # type: ignore
    BicameralConfig = None  # type: ignore
    BicameralCortex = None  # type: ignore
    BicameralError = None  # type: ignore
    CoherencyError = None  # type: ignore
    CoherencyReport = None  # type: ignore
    GhostRecord = None  # type: ignore
    StaleRecord = None  # type: ignore
    HemisphereRole = None  # type: ignore
    create_bicameral_memory = None  # type: ignore
    create_bicameral_cortex = None  # type: ignore

__all__ = [
    # Protocol
    "DataAgent",
    # Context Engineering (Phase 6: Context Protocol)
    "ContextWindow",
    "ContextMeta",
    "ContextSnapshot",
    "Turn",
    "TurnRole",
    "create_context_window",
    "context_from_messages",
    "ContextSession",
    "ContextState",
    "ContextInput",
    "ContextOutput",
    "ContextPressureError",
    "create_context_session",
    "from_messages",
    "ComponentRenderer",
    "ContextProps",
    "ContextStatus",
    "MessageProps",
    "create_component_renderer",
    "render_for_frontend",
    "render_minimal",
    "PromptBuilder",
    "create_prompt_builder",
    "build_kgent_prompt",
    "build_builder_prompt",
    "build_citizen_prompt",
    "render_eigenvectors_6d",
    "render_eigenvectors_7d",
    "render_constraints",
    "ContextProjector",
    "CompressionResult",
    "ContextCompressionConfig",
    "AdaptiveThreshold",
    "DefaultSummarizer",
    "Summarizer",
    "auto_compress",
    "create_projector",
    # Errors
    "StateError",
    "StateNotFoundError",
    "StateCorruptionError",
    "StateSerializationError",
    "StorageError",
    # Noosphere errors
    "NoosphereError",
    "SemanticError",
    "TemporalError",
    "LatticeError",
    "VoidNotFoundError",
    "DriftDetectionError",
    "NodeNotFoundError",
    "EdgeNotFoundError",
    # Core Implementations
    "VolatileAgent",
    "PersistentAgent",
    "CachedAgent",
    "Symbiont",
    "EntropyConstrainedAgent",
    # Noosphere: Vector (Semantic Manifold)
    "VectorAgent",
    "VectorEntry",
    "Point",
    "Void",
    "DistanceMetric",
    # Noosphere: Graph (Relational Lattice)
    "GraphAgent",
    "GraphNode",
    "Edge",
    "Subgraph",
    "EdgeKind",
    # Noosphere: Stream (Temporal Witness)
    "StreamAgent",
    "WitnessReport",
    "DriftReport",
    "EventRecord",
    "Vector",
    # Core Lenses
    "Lens",
    "key_lens",
    "field_lens",
    "index_lens",
    "identity_lens",
    "attr_lens",
    "verify_lens_laws",
    "verify_get_put_law",
    "verify_put_get_law",
    "verify_put_put_law",
    "LensAgent",
    "focused",
    # Prism (optional fields)
    "Prism",
    "optional_key_prism",
    "optional_field_prism",
    "optional_index_prism",
    "verify_prism_laws",
    # Traversal (collections)
    "Traversal",
    "list_traversal",
    "dict_values_traversal",
    "dict_keys_traversal",
    "dict_items_traversal",
    "verify_traversal_laws",
    # Composed lens validation
    "LensValidation",
    "validate_composed_lens",
    # Convenience functions
    "entropy_constrained",
    # Persistence Extensions: Schema Versioning
    "SchemaVersion",
    "Migration",
    "MigrationRegistry",
    "MigrationDirection",
    "VersionedState",
    "VersionedPersistentAgent",
    "create_versioned_agent",
    # Persistence Extensions: Backup/Restore
    "BackupMetadata",
    "BackupManager",
    # Persistence Extensions: Compression
    "CompressionLevel",
    "CompressionConfig",
    "CompressedPersistentAgent",
    "create_compressed_agent",
    # Phase 3: Transactional
    "TransactionalDataAgent",
    "Transaction",
    "Savepoint",
    "TransactionState",
    "TransactionError",
    "SavepointError",
    "RollbackError",
    # Phase 3: Queryable
    "QueryableDataAgent",
    "Query",
    "QueryResult",
    "Predicate",
    "Operator",
    "QueryError",
    "PathNotFoundError",
    "eq",
    "ne",
    "lt",
    "le",
    "gt",
    "ge",
    "contains",
    "matches",
    "exists",
    "in_list",
    # Phase 3: Observable
    "ObservableDataAgent",
    "Change",
    "ChangeType",
    "Subscription",
    "ObservableError",
    # Phase 3: UnifiedMemory
    "UnifiedMemory",
    "MemoryConfig",
    "MemoryLayer",
    "MemoryEntry",
    "LensedUnifiedMemory",
    "UnifiedMemoryError",
    "LayerNotAvailableError",
    "create_unified_memory",
    # Phase 4: SemanticManifold
    "SemanticManifold",
    "SemanticPoint",
    "SemanticVoid",
    "Geodesic",
    "SemanticCluster",
    "ManifoldStats",
    "CurvatureRegion",
    # Phase 4: TemporalWitness
    "TemporalWitness",
    "Trajectory",
    "WitnessContext",
    "TemporalSnapshot",
    "TimelineEntry",
    "DriftSeverity",
    "EntropyLevel",
    # Phase 4: RelationalLattice
    "RelationalLattice",
    "LatticeNode",
    "LatticeRelation",
    "MeetJoinResult",
    "EntailmentProof",
    "LatticeStats",
    # Phase 4: MemoryGarden
    "MemoryGarden",
    "GardenEntry",
    "Lifecycle",
    "Evidence",
    "EvidenceType",
    "Contradiction",
    "Insight",
    "Nutrients",
    "GardenStats",
    # Phase 5: SQL Backends
    "SQLAgent",
    "SQLBackend",
    "SQLiteBackend",
    "PostgreSQLBackend",
    "create_sqlite_agent",
    "create_postgres_agent",
    # Phase 5: Redis/Valkey Backends
    "RedisAgent",
    "create_redis_agent",
    "create_valkey_agent",
    # Phase 3+: Infrastructure Backends (Instance DB Integration)
    "InstanceDBVectorBackend",
    "InstanceDBVectorBackendConfig",
    "InstanceDBRelationalBackend",
    "InstanceDBRelationalBackendConfig",
    "CortexAdapter",
    "CortexAdapterConfig",
    "ContentHash",
    "VectorMetadata",
    "RecallResult",
    "InfraBackendError",
    "GhostMemoryError",
    "StaleEmbeddingError",
    "create_vector_backend",
    "create_relational_backend",
    "create_cortex_adapter",
    # Phase 3+: Bicameral Memory (Ghost Detection + Self-Healing)
    "BicameralMemory",
    "BicameralConfig",
    "BicameralCortex",
    "BicameralError",
    "CoherencyError",
    "CoherencyReport",
    "GhostRecord",
    "StaleRecord",
    "HemisphereRole",
    "create_bicameral_memory",
    "create_bicameral_cortex",
    # Phase 2.3: Pulse (Zero-Cost Vitality Signals)
    "Pulse",
    "AgentPhase",
    "VitalityAnalyzer",
    "VitalityStatus",
    "create_pulse",
    "create_pulse_from_window",
    "create_analyzer",
    # Phase 2.4: StateCrystal (Checkpoints with Comonadic Lineage)
    "StateCrystal",
    "TaskState",
    "TaskStatus",
    "FocusFragment",
    "CrystallizationEngine",
    "CrystallizationResult",
    "CrystalReaper",
    "ReapResult",
    "ResumeResult",
    "create_crystal_engine",
    "create_task_state",
    # Phase 3 Polyfunctor: D-gent Polynomial
    "MemoryPhase",
    "LoadCommand",
    "StoreCommand",
    "QueryCommand",
    "ForgetCommand",
    "MemoryResponse",
    "MEMORY_POLYNOMIAL",
    "memory_directions",
    "memory_transition",
    "MemoryPolynomialAgent",
    "reset_memory",
]
