"""
K-Block Crown Jewel: Transactional Hyperdimensional Editing.

The K-Block service provides transactional isolation for spec editing.
Changes happen inside K-Blocks without affecting the cosmos (shared reality)
until explicitly committed through harness operations.

Key Concepts:
- KBlock: Isolated editing container (the monad)
- Cosmos: Append-only shared reality (never overwrites)
- Harness: Boundary operations (create, save, discard, fork, merge)
- Polynomial: State machine for valid transitions

Philosophy:
    "The K-Block is not where you edit a document.
     It's where you edit a possible world."

    "Everything in the cosmos affects everything else.
     But inside the K-Block, you are sovereign."

See: spec/protocols/k-block.md
See: docs/skills/k-block-patterns.md (planned)
"""

from .core import (
    # Cosmos
    AppendOnlyLog,
    Checkpoint,
    # KBlock
    ContentDelta,
    Cosmos,
    CosmosEntry,
    CosmosView,
    EditDelta,
    EditingState,
    # Harness
    FileOperadHarness,
    IsolationState,
    KBlock,
    KBlockId,
    # Polynomial
    KBlockInput,
    KBlockOutput,
    KBlockPolynomial,
    KBlockState,
    MergeResult,
    SaveResult,
    SemanticIndex,
    VersionId,
    ViewType,
    describe_state,
    generate_kblock_id,
    generate_version_id,
    get_cosmos,
    get_harness,
    get_valid_actions,
    reset_cosmos,
    reset_harness,
    set_cosmos,
    set_harness,
)

__all__ = [
    # KBlock Core
    "Checkpoint",
    "ContentDelta",
    "EditDelta",
    "IsolationState",
    "KBlock",
    "KBlockId",
    "ViewType",
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
    "FileOperadHarness",
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
