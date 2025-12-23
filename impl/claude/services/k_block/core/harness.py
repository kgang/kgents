"""
FileOperadHarness: The boundary between K-Blocks and Cosmos.

The harness is the ONLY way to cross the K-Block boundary.
It implements the HARNESS_OPERAD operations:
- create: Lift cosmos content into K-Block isolation
- save: Commit K-Block changes to cosmos
- discard: Abandon K-Block without cosmic effects
- fork: Create parallel editing universe
- merge: Combine two K-Blocks

Philosophy:
    "The harness is the gate. Only the gatekeeper may open it."
    "The proof IS the decision. The mark IS the witness." (Phase 2)

Phase 2 Enhancement:
    The harness can emit Witness marks on save(), enabling full
    audit trail with Toulmin proof structure.

See: spec/protocols/k-block.md
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any

from .cosmos import Cosmos, VersionId, get_cosmos
from .kblock import (
    ContentDelta,
    IsolationState,
    KBlock,
    KBlockId,
    generate_kblock_id,
)
from .witnessed import WitnessedCosmos, WitnessTrace, create_witnessed_cosmos

if TYPE_CHECKING:
    from services.witness import MarkStore, Proof


# -----------------------------------------------------------------------------
# Result Types
# -----------------------------------------------------------------------------


@dataclass(frozen=True)
class SaveResult:
    """
    Result of a save operation.

    Phase 2 Enhancement:
        mark_id links to the Witness trace for this save.
        Use this to navigate to the full Toulmin proof.
    """

    success: bool
    path: str
    version_id: VersionId | None = None
    mark_id: str | None = None  # Phase 2: Link to Witness trace
    no_changes: bool = False
    dependents_marked: int = 0
    error: str | None = None

    @property
    def is_witnessed(self) -> bool:
        """Whether this save was witnessed (has mark_id)."""
        return self.mark_id is not None

    @classmethod
    def ok(
        cls,
        path: str,
        version_id: VersionId,
        dependents_marked: int = 0,
        mark_id: str | None = None,
    ) -> "SaveResult":
        return cls(
            success=True,
            path=path,
            version_id=version_id,
            mark_id=mark_id,
            dependents_marked=dependents_marked,
        )

    @classmethod
    def unchanged(cls, path: str) -> "SaveResult":
        return cls(success=True, path=path, no_changes=True)

    @classmethod
    def err(cls, path: str, error: str) -> "SaveResult":
        return cls(success=False, path=path, error=error)


@dataclass(frozen=True)
class MergeResult:
    """Result of a merge operation."""

    success: bool
    block_id: KBlockId | None = None
    has_conflicts: bool = False
    conflict_count: int = 0
    error: str | None = None


# -----------------------------------------------------------------------------
# Harness Errors
# -----------------------------------------------------------------------------


class HarnessError(Exception):
    """Base error for harness operations."""

    pass


class ConflictError(HarnessError):
    """Raised when K-Block has conflicts that must be resolved."""

    def __init__(self, path: str, message: str):
        self.path = path
        super().__init__(f"{path}: {message}")


class EntanglementError(HarnessError):
    """Raised for invalid entanglement operations."""

    pass


# -----------------------------------------------------------------------------
# FileOperadHarness
# -----------------------------------------------------------------------------


@dataclass
class FileOperadHarness:
    """
    Boundary operations that connect K-Blocks to cosmos.

    This is the implementation of HARNESS_OPERAD.

    Laws (verified by tests):
    - create_discard_identity: discard(create(p)) == id
    - save_idempotence: save(save(kb)) == save(kb)
    - fork_merge_identity: merge(fork(kb)) == kb
    - checkpoint_rewind_identity: rewind(kb, checkpoint(kb)) == kb

    Phase 2 Enhancement:
        When witness_enabled=True, saves emit Witness marks with
        Toulmin proof structure for full audit trail.
    """

    cosmos: Cosmos = field(default_factory=get_cosmos)
    _blocks: dict[KBlockId, KBlock] = field(default_factory=dict)
    _blocks_by_path: dict[str, KBlockId] = field(default_factory=dict)

    # Phase 2: Witness integration
    witness_enabled: bool = True  # Enable witness marks on save
    _witnessed_cosmos: WitnessedCosmos | None = field(default=None, repr=False)

    def __post_init__(self) -> None:
        """Initialize witnessed cosmos if enabled."""
        if self.witness_enabled and self._witnessed_cosmos is None:
            self._witnessed_cosmos = create_witnessed_cosmos(self.cosmos)

    # ---------------------------------------------------------------------
    # HARNESS_OPERAD.create
    # ---------------------------------------------------------------------

    async def create(self, path: str) -> KBlock:
        """
        Lift cosmos content into K-Block isolation.

        Signature: Path -> KBlock

        This is the 'return' operation of the K-Block monad.
        It lifts a document from the cosmos into an isolated editing context.
        """
        # Read current content from cosmos (or empty if new)
        content = await self.cosmos.read(path) or ""

        # Create K-Block
        block = KBlock(
            id=generate_kblock_id(),
            path=path,
            content=content,
            base_content=content,
            isolation=IsolationState.PRISTINE,
        )

        # Set cosmos reference
        block._cosmos = self.cosmos

        # Register
        self._blocks[block.id] = block
        self._blocks_by_path[path] = block.id
        self.cosmos.register_block(path, block.id)

        return block

    # ---------------------------------------------------------------------
    # HARNESS_OPERAD.save
    # ---------------------------------------------------------------------

    async def save(
        self,
        block: KBlock,
        actor: str = "system",
        reasoning: str | None = None,
        proof: "Proof | None" = None,
    ) -> SaveResult:
        """
        Commit K-Block changes to cosmos.

        Signature: KBlock -> Cosmos

        This is the key boundary crossing — changes escape K-Block isolation
        and become visible in the shared reality.

        Effects on save:
        1. Content written to cosmos (append-only)
        2. Witness mark emitted (if witness_enabled)
        3. Dependents marked stale
        4. K-Block state reset to PRISTINE

        Args:
            block: The K-Block to save
            actor: Who is saving ("Kent", "Claude", "system")
            reasoning: Human-readable explanation of why
            proof: Optional Toulmin proof for full justification (Phase 2)

        Phase 2 Enhancement:
            When witness_enabled=True, creates a Witness Mark with the
            provided reasoning/proof, enabling full audit trail.
        """
        # Validate state
        if block.isolation == IsolationState.CONFLICTING:
            return SaveResult.err(block.path, "Resolve conflicts before saving")

        if block.isolation == IsolationState.ENTANGLED:
            return SaveResult.err(block.path, "Disentangle before saving individually")

        # Check for changes
        if not block.is_dirty:
            return SaveResult.unchanged(block.path)

        # Compute delta summary for witness
        delta = block.compute_delta()
        delta_summary = f"+{delta.additions}/-{delta.deletions} lines"

        # Commit to cosmos (with or without witness)
        mark_id: str | None = None

        if self.witness_enabled and self._witnessed_cosmos is not None:
            # Use witnessed cosmos for audit trail
            # Include file:{path} tag so WitnessSource can create graph edges
            # This closes the loop: K-Block save → Witness mark → WitnessedGraph edge
            path_tag = (
                f"file:{block.path}" if not block.path.startswith("spec/") else f"spec:{block.path}"
            )
            trace = WitnessTrace(
                actor=actor,
                reasoning=reasoning,
                proof=proof,
                kblock_id=str(block.id),
                delta_summary=delta_summary,
                tags=("kblock", "save", path_tag),
            )
            result = await self._witnessed_cosmos.commit(
                path=block.path,
                content=block.content,
                trace=trace,
            )
            version_id = result.version_id
            mark_id = result.mark_id
        else:
            # Direct cosmos commit (no witness)
            version_id = await self.cosmos.commit(
                path=block.path,
                content=block.content,
                actor=actor,
                reasoning=reasoning,
            )

        # Mark dependents stale
        dependents_marked = await self._mark_dependents_stale(block.path)

        # Reset K-Block state
        block.base_content = block.content
        block.isolation = IsolationState.PRISTINE
        block.checkpoints.clear()
        block.modified_at = datetime.now(timezone.utc)

        # Emit KBLOCK_SAVED event to bus (closes the loop: save → witness → graph)
        await self._emit_kblock_saved_event(block, version_id, mark_id, reasoning)

        return SaveResult.ok(
            path=block.path,
            version_id=version_id,
            dependents_marked=dependents_marked,
            mark_id=mark_id,
        )

    async def _emit_kblock_saved_event(
        self,
        block: KBlock,
        version_id: VersionId,
        mark_id: str | None,
        reasoning: str | None,
    ) -> None:
        """
        Emit KBLOCK_SAVED event to the Witness bus.

        This closes the loop: K-Block save → Bus event → Graph update → UI refresh
        """
        try:
            from services.witness.bus import WitnessTopics, get_synergy_bus

            bus = get_synergy_bus()
            await bus.publish(
                WitnessTopics.KBLOCK_SAVED,
                {
                    "path": block.path,
                    "kblock_id": str(block.id),
                    "version_id": str(version_id),
                    "mark_id": mark_id,
                    "reasoning": reasoning,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                },
            )
        except ImportError:
            # Bus not available (testing without full infrastructure)
            pass
        except Exception:
            # Non-critical - don't fail save on bus error
            pass

    async def _mark_dependents_stale(self, path: str) -> int:
        """Mark K-Blocks that depend on this path as stale."""
        dependent_paths = self.cosmos.get_dependents(path)
        count = 0

        for dep_path in dependent_paths:
            block_id = self._blocks_by_path.get(dep_path)
            if block_id:
                block = self._blocks.get(block_id)
                if block and block.isolation == IsolationState.PRISTINE:
                    block.isolation = IsolationState.STALE
                    count += 1
                elif block and block.isolation == IsolationState.DIRTY:
                    block.isolation = IsolationState.CONFLICTING
                    count += 1

        return count

    # ---------------------------------------------------------------------
    # HARNESS_OPERAD.discard
    # ---------------------------------------------------------------------

    async def discard(self, block: KBlock) -> None:
        """
        Abandon K-Block without cosmic effects.

        Signature: KBlock -> ()

        This is the "abort" operation — all edits are lost, cosmos unchanged.
        Combined with create, this satisfies: discard(create(p)) == id
        """
        if block.isolation == IsolationState.ENTANGLED:
            raise EntanglementError("Cannot discard entangled K-Block")

        # Unregister
        self._blocks.pop(block.id, None)
        self._blocks_by_path.pop(block.path, None)
        self.cosmos.unregister_block(block.path)

        # Clear cosmos reference
        block._cosmos = None

    # ---------------------------------------------------------------------
    # HARNESS_OPERAD.fork
    # ---------------------------------------------------------------------

    async def fork(self, block: KBlock) -> tuple[KBlock, KBlock]:
        """
        Create parallel editing universe.

        Signature: KBlock -> (KBlock, KBlock)

        Both K-Blocks share the same base content but can be edited
        independently. Changes to one don't affect the other.

        Law: merge(fork(kb)) == kb
        """
        # Clone the block
        clone = KBlock(
            id=generate_kblock_id(),
            path=block.path,
            content=block.content,
            base_content=block.base_content,
            isolation=block.isolation,
            created_at=datetime.now(timezone.utc),
            modified_at=datetime.now(timezone.utc),
            checkpoints=list(block.checkpoints),  # Copy checkpoints
        )

        # Set cosmos reference
        clone._cosmos = self.cosmos

        # Register clone (but not as primary for path)
        self._blocks[clone.id] = clone

        return (block, clone)

    # ---------------------------------------------------------------------
    # HARNESS_OPERAD.merge
    # ---------------------------------------------------------------------

    async def merge(self, kb1: KBlock, kb2: KBlock) -> MergeResult:
        """
        Combine two K-Blocks.

        Signature: KBlock x KBlock -> KBlock

        Uses three-way merge with base content as common ancestor.
        If conflicts, kb1 is marked CONFLICTING and contains markers.

        Law: merge(fork(kb)) == kb (when no independent edits)
        """
        if kb1.path != kb2.path:
            return MergeResult(
                success=False,
                error="Cannot merge K-Blocks with different paths",
            )

        # If same content, trivial merge
        if kb1.content == kb2.content:
            return MergeResult(success=True, block_id=kb1.id)

        # If one is unchanged from base, take the other
        if kb1.content == kb1.base_content:
            kb1.content = kb2.content
            kb1._mark_dirty()
            return MergeResult(success=True, block_id=kb1.id)

        if kb2.content == kb2.base_content:
            # kb1 has the changes, keep it
            return MergeResult(success=True, block_id=kb1.id)

        # Three-way merge needed
        merged, has_conflicts, conflict_count = self._three_way_merge(
            base=kb1.base_content,
            left=kb1.content,
            right=kb2.content,
        )

        kb1.content = merged
        if has_conflicts:
            kb1.isolation = IsolationState.CONFLICTING
        else:
            kb1._mark_dirty()

        # Clean up kb2 (it's been merged into kb1)
        self._blocks.pop(kb2.id, None)

        return MergeResult(
            success=True,
            block_id=kb1.id,
            has_conflicts=has_conflicts,
            conflict_count=conflict_count,
        )

    def _three_way_merge(
        self,
        base: str,
        left: str,
        right: str,
    ) -> tuple[str, bool, int]:
        """
        Perform three-way merge.

        Returns (merged_content, has_conflicts, conflict_count).
        """
        import difflib

        base_lines = base.splitlines(keepends=True)
        left_lines = left.splitlines(keepends=True)
        right_lines = right.splitlines(keepends=True)

        # Use difflib's SequenceMatcher for basic merge
        # This is a simplified implementation; production would use diff3
        merger = difflib.Differ()

        # Check if changes are in different areas (no conflict)
        left_changes = set(i for i, (a, b) in enumerate(zip(base_lines, left_lines)) if a != b)
        right_changes = set(i for i, (a, b) in enumerate(zip(base_lines, right_lines)) if a != b)

        # If changes are disjoint, simple merge
        if not left_changes.intersection(right_changes):
            # Apply both sets of changes
            result = list(base_lines)
            for i in left_changes:
                if i < len(result) and i < len(left_lines):
                    result[i] = left_lines[i]
            for i in right_changes:
                if i < len(result) and i < len(right_lines):
                    result[i] = right_lines[i]
            return "".join(result), False, 0

        # Conflicts exist — create conflict markers
        conflict_count = len(left_changes.intersection(right_changes))
        result_lines = []
        in_conflict = False

        for i, base_line in enumerate(base_lines):
            left_line = left_lines[i] if i < len(left_lines) else ""
            right_line = right_lines[i] if i < len(right_lines) else ""

            if i in left_changes and i in right_changes:
                if left_line != right_line:
                    # Conflict
                    result_lines.append("<<<<<<< LOCAL\n")
                    result_lines.append(left_line)
                    result_lines.append("=======\n")
                    result_lines.append(right_line)
                    result_lines.append(">>>>>>> REMOTE\n")
                    in_conflict = True
                else:
                    result_lines.append(left_line)
            elif i in left_changes:
                result_lines.append(left_line)
            elif i in right_changes:
                result_lines.append(right_line)
            else:
                result_lines.append(base_line)

        return "".join(result_lines), in_conflict, conflict_count

    # ---------------------------------------------------------------------
    # HARNESS_OPERAD.checkpoint / rewind
    # ---------------------------------------------------------------------

    async def checkpoint(self, block: KBlock, name: str) -> str:
        """
        Create named restore point within K-Block.

        Signature: KBlock -> Checkpoint

        Checkpoints exist only within K-Block lifetime (not persisted to cosmos).
        """
        cp = block.checkpoint(name)
        return cp.id

    async def rewind(self, block: KBlock, checkpoint_id: str) -> None:
        """
        Restore K-Block to checkpoint state.

        Signature: KBlock x Checkpoint -> KBlock

        Law: rewind(kb, checkpoint(kb)) == kb (immediate rewind)
        """
        block.rewind(checkpoint_id)

    # ---------------------------------------------------------------------
    # Block Registry
    # ---------------------------------------------------------------------

    def get_block(self, block_id: KBlockId) -> KBlock | None:
        """Get K-Block by ID."""
        return self._blocks.get(block_id)

    def get_block_for_path(self, path: str) -> KBlock | None:
        """Get K-Block for a path (if one exists)."""
        block_id = self._blocks_by_path.get(path)
        return self._blocks.get(block_id) if block_id else None

    def list_blocks(self) -> list[KBlock]:
        """List all active K-Blocks."""
        return list(self._blocks.values())

    # ---------------------------------------------------------------------
    # Refresh (for stale K-Blocks)
    # ---------------------------------------------------------------------

    async def refresh(self, block: KBlock) -> ContentDelta | None:
        """
        Refresh K-Block with latest cosmos content.

        If STALE and no local edits: updates both base and content, becomes PRISTINE
        If STALE with local edits: updates base only, becomes DIRTY
        If CONFLICTING: updates base_content, stays CONFLICTING

        Returns delta between old and new base (for UI to show what changed).
        """
        if block.isolation not in (IsolationState.STALE, IsolationState.CONFLICTING):
            return None

        # Get latest from cosmos
        new_base = await self.cosmos.read(block.path) or ""

        # Compute delta (between old base and new base)
        delta = ContentDelta.compute(block.base_content, new_base)

        # Check if user has local edits (content differs from OLD base)
        has_local_edits = block.content != block.base_content

        # Update base
        old_base = block.base_content
        block.base_content = new_base

        # Update isolation state based on whether user has local changes
        if not has_local_edits:
            # User hasn't edited - update content to new base, become PRISTINE
            block.content = new_base
            block.isolation = IsolationState.PRISTINE
        elif block.content == new_base:
            # User edited to same content as new base - PRISTINE
            block.isolation = IsolationState.PRISTINE
        else:
            # User has local edits that differ from new base - DIRTY
            block.isolation = IsolationState.DIRTY

        return delta


# -----------------------------------------------------------------------------
# Global Harness Instance
# -----------------------------------------------------------------------------

_harness: FileOperadHarness | None = None


def get_harness() -> FileOperadHarness:
    """Get the global harness instance."""
    global _harness
    if _harness is None:
        _harness = FileOperadHarness()
    return _harness


def set_harness(harness: FileOperadHarness) -> None:
    """Set the global harness instance (for testing)."""
    global _harness
    _harness = harness


def reset_harness() -> None:
    """Reset the global harness instance (for testing)."""
    global _harness
    _harness = None
