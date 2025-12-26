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
    generate_kblock_id,
    kblock_from_zero_node,
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
    "generate_kblock_id",
    # Unification: KBlock ≅ ZeroNode isomorphism
    "kblock_from_zero_node",
    "zero_node_from_kblock",
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
]
