"""
K-Block Core: Transactional Hyperdimensional Editing.

Core types and data structures for K-Block isolation.

Philosophy:
    "The K-Block is not where you edit a document.
     It's where you edit a possible world."

See: spec/protocols/k-block.md
"""

from .cosmos import (
    AppendOnlyLog,
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
    generate_kblock_id,
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

__all__ = [
    # KBlock
    "Checkpoint",
    "ContentDelta",
    "EditDelta",
    "IsolationState",
    "KBlock",
    "KBlockId",
    "generate_kblock_id",
    # Cosmos
    "AppendOnlyLog",
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
]
