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

from .protocol import DataAgent
from .errors import (
    StateError,
    StateNotFoundError,
    StateCorruptionError,
    StateSerializationError,
    StorageError,
    # Noosphere errors
    NoosphereError,
    SemanticError,
    TemporalError,
    LatticeError,
    VoidNotFoundError,
    DriftDetectionError,
    NodeNotFoundError,
    EdgeNotFoundError,
)
from .volatile import VolatileAgent
from .persistent import PersistentAgent
from .symbiont import Symbiont
from .lens import (
    Lens,
    key_lens,
    field_lens,
    index_lens,
    identity_lens,
    verify_lens_laws,
)
from .lens_agent import LensAgent, focused
from .cached import CachedAgent
from .entropy import EntropyConstrainedAgent, entropy_constrained

# Noosphere Layer: Advanced D-gent types
# Vector requires numpy (optional dependency)
try:
    from .vector import (
        VectorAgent,
        VectorEntry,
        Point,
        Void,
        DistanceMetric,
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
    GraphAgent,
    GraphNode,
    Edge,
    Subgraph,
    EdgeKind,
)
from .stream import (
    StreamAgent,
    WitnessReport,
    DriftReport,
    EventRecord,
    Vector,
)

# Phase 3: Extended Protocols
from .transactional import (
    TransactionalDataAgent,
    Transaction,
    Savepoint,
    TransactionState,
    TransactionError,
    SavepointError,
    RollbackError,
)
from .queryable import (
    QueryableDataAgent,
    Query,
    QueryResult,
    Predicate,
    Operator,
    QueryError,
    PathNotFoundError,
    # Predicate helpers
    eq,
    ne,
    lt,
    le,
    gt,
    ge,
    contains,
    matches,
    exists,
    in_list,
)
from .observable import (
    ObservableDataAgent,
    Change,
    ChangeType,
    Subscription,
    ObservableError,
)
from .unified import (
    UnifiedMemory,
    MemoryConfig,
    MemoryLayer,
    MemoryEntry,
    LensedUnifiedMemory,
    UnifiedMemoryError,
    LayerNotAvailableError,
    create_unified_memory,
)

__all__ = [
    # Protocol
    "DataAgent",
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
    # Lenses
    "Lens",
    "key_lens",
    "field_lens",
    "index_lens",
    "identity_lens",
    "verify_lens_laws",
    "LensAgent",
    "focused",
    # Convenience functions
    "entropy_constrained",
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
]
