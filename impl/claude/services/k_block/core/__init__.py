"""
K-Block Core: Transactional Hyperdimensional Editing.

Core types and data structures for K-Block isolation.

Philosophy:
    "The K-Block is not where you edit a document.
     It's where you edit a possible world."
    "The proof IS the decision. The mark IS the witness." (Phase 2)

See: spec/protocols/k-block.md
"""

from .cosmos import (
    AppendOnlyLog,
    BlameEntry,
    Cosmos,
    CosmosEntry,
    CosmosView,
    SemanticIndex,
    VersionId,
    generate_version_id,
    get_cosmos,
    reset_cosmos,
    set_cosmos,
)
from .edge import KBlockEdge
from .edge_discovery import (
    ConceptSignature,
    DiscoveredEdge,
    EdgeDiscoveryService,
    EdgeKind,
    get_edge_discovery_service,
    reset_edge_discovery_service,
)
from .errors import (
    GluingError,
    PropagationError,
    SheafConditionError,
    SheafError,
    TokenConflict,
)

# Event Sourcing (Kent's decision 2025-01-17: "Every edit is an event")
# HEAD-FIRST DESIGN: Current state is O(1), history reconstructed on demand
from .events import (
    # Store Protocol & Implementations
    EventStoreProtocol,
    FileEventStore,
    InMemoryEventStore,
    # Data Types
    KBlockEvent,
    KBlockEventEmitter,
    KBlockEventType,
    KBlockHead,  # Current canonical state (O(1) access)
    # HEAD-FIRST: Primary access patterns
    get_content_at_sequence,  # Rewind from head to get historical state
    get_current_content,  # O(1) current state
    # Module-level store
    get_emitter,
    get_event_store,
    get_links_at_sequence,  # Rewind links
    # Legacy (forward replay)
    replay_content,
    replay_links,
    set_event_store,
)
from .harness import (
    ConflictError,
    EntanglementError,
    FileOperadHarness,
    HarnessError,
    MergeResult,
    SaveResult,
    get_harness,
    reset_harness,
    set_harness,
)
from .kblock import (
    Checkpoint,
    ContentDelta,
    EditDelta,
    IsolationState,
    KBlock,
    KBlockId,
    KBlockKind,
    LineageEdge,  # Amendment D: Monad lineage tracking
    WitnessBridgeProtocol,  # P2: K-Block → Witness bridge
    generate_kblock_id,
    get_witness_bridge,  # P2: K-Block → Witness bridge
    kblock_from_zero_node,
    set_witness_bridge,  # P2: K-Block → Witness bridge
    zero_node_from_kblock,
)
from .polynomial import (
    EditingState,
    KBlockInput,
    KBlockOutput,
    KBlockPolynomial,
    KBlockState,
    describe_state,
    get_valid_actions,
)
from .provenance import (
    KBlockProvenance,
    ReviewStatus,
)
from .sheaf import KBlockSheaf
from .verification import SheafVerification
from .witnessed import (
    BlameEntryWithMark,
    CommitResult,
    WitnessedCosmos,
    WitnessTrace,
    create_witnessed_cosmos,
)
from .witnessed_sheaf import (
    ViewEditTrace,
    WitnessedSheaf,
)

__all__ = [
    # KBlock
    "Checkpoint",
    "ContentDelta",
    "EditDelta",
    "IsolationState",
    "KBlock",
    "KBlockEdge",
    "KBlockId",
    "KBlockKind",  # Unification: Kind taxonomy
    "LineageEdge",  # Amendment D: Monad lineage tracking
    "WitnessBridgeProtocol",  # P2: K-Block → Witness bridge
    "generate_kblock_id",
    "get_witness_bridge",  # P2: K-Block → Witness bridge
    "set_witness_bridge",  # P2: K-Block → Witness bridge
    # Unification: KBlock ≅ ZeroNode isomorphism
    "kblock_from_zero_node",
    "zero_node_from_kblock",
    # Provenance (Anti-Sloppification Tracking)
    "KBlockProvenance",
    "ReviewStatus",
    # Edge Discovery
    "ConceptSignature",
    "DiscoveredEdge",
    "EdgeDiscoveryService",
    "EdgeKind",
    "get_edge_discovery_service",
    "reset_edge_discovery_service",
    # Cosmos
    "AppendOnlyLog",
    "BlameEntry",
    "Cosmos",
    "CosmosEntry",
    "CosmosView",
    "SemanticIndex",
    "VersionId",
    "generate_version_id",
    "get_cosmos",
    "reset_cosmos",
    "set_cosmos",
    # Harness
    "ConflictError",
    "EntanglementError",
    "FileOperadHarness",
    "HarnessError",
    "MergeResult",
    "SaveResult",
    "get_harness",
    "reset_harness",
    "set_harness",
    # Polynomial
    "EditingState",
    "KBlockInput",
    "KBlockOutput",
    "KBlockPolynomial",
    "KBlockState",
    "describe_state",
    "get_valid_actions",
    # Sheaf
    "GluingError",
    "KBlockSheaf",
    "PropagationError",
    "SheafConditionError",
    "SheafError",
    "SheafVerification",
    "TokenConflict",
    # Witness Integration (Phase 2)
    "BlameEntryWithMark",
    "CommitResult",
    "WitnessedCosmos",
    "WitnessTrace",
    "create_witnessed_cosmos",
    # Witness Integration (Phase 3)
    "ViewEditTrace",
    "WitnessedSheaf",
    # Event Sourcing (Kent's decision 2025-01-17: HEAD-FIRST DESIGN)
    "EventStoreProtocol",
    "FileEventStore",
    "InMemoryEventStore",
    "KBlockEvent",
    "KBlockEventEmitter",
    "KBlockEventType",
    "KBlockHead",  # Current canonical state (O(1) access)
    "get_content_at_sequence",  # Rewind from head
    "get_current_content",  # O(1) current state
    "get_emitter",
    "get_event_store",
    "get_links_at_sequence",  # Rewind links
    "replay_content",  # Legacy forward replay
    "replay_links",  # Legacy forward replay
    "set_event_store",
]
