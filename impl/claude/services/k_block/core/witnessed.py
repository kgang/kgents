"""
WitnessedCosmos: The integration layer between Cosmos and Witness.

Philosophy:
    "The proof IS the decision. The mark IS the witness."

Every commit to the cosmos can be witnessed — meaning it carries a Mark
that links to the full Witness trace with Toulmin proof structure.

This enables:
    - Audit trail: Who changed what, when, and WHY
    - Replay: Reconstruct editing sessions from marks
    - Blame: Trace any content to its justification
    - Accountability: Every decision is traceable

See: spec/protocols/k-block.md §5.1
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from .cosmos import BlameEntry, Cosmos, VersionId

if TYPE_CHECKING:
    from services.witness import Mark, MarkId, MarkStore, Proof


# -----------------------------------------------------------------------------
# Witness Trace (for commit operations)
# -----------------------------------------------------------------------------


@dataclass
class WitnessTrace:
    """
    Trace information for a cosmos commit.

    This is the bridge between K-Block operations and the Witness system.
    It captures enough context to create a proper Mark.

    Fields:
        actor: Who is making this change ("Kent", "Claude", "system")
        reasoning: Human-readable explanation
        proof: Optional Toulmin proof structure (for full justification)
        kblock_id: If coming from a K-Block save
        delta_summary: Brief description of what changed
        tags: Categorization tags
    """

    actor: str
    reasoning: str | None = None
    proof: "Proof | None" = None
    kblock_id: str | None = None
    delta_summary: str | None = None
    tags: tuple[str, ...] = ()

    @classmethod
    def simple(cls, actor: str, reasoning: str) -> "WitnessTrace":
        """Create a simple trace with just actor and reasoning."""
        return cls(actor=actor, reasoning=reasoning)

    @classmethod
    def from_kblock(
        cls,
        actor: str,
        kblock_id: str,
        reasoning: str | None = None,
        delta_summary: str | None = None,
    ) -> "WitnessTrace":
        """Create a trace from K-Block save operation."""
        return cls(
            actor=actor,
            reasoning=reasoning,
            kblock_id=kblock_id,
            delta_summary=delta_summary,
            tags=("kblock", "save"),
        )


# -----------------------------------------------------------------------------
# Witnessed Cosmos
# -----------------------------------------------------------------------------


@dataclass
class WitnessedCosmos:
    """
    Cosmos wrapper that emits Witness marks on commit.

    This is the "witnessed" version of cosmos.commit() that:
    1. Creates a Mark with the provided trace information
    2. Stores the Mark in the MarkStore
    3. Commits to cosmos with the mark_id linked
    4. Returns both version_id and mark_id

    Philosophy:
        The cosmos is a category where morphisms (saves) are witnessed.
        Every mutation carries proof of justification.

    Usage:
        >>> witnessed = WitnessedCosmos(cosmos, mark_store)
        >>> trace = WitnessTrace.from_kblock("Kent", block.id, "Fixed typo")
        >>> result = await witnessed.commit("path.md", content, trace)
        >>> print(result.version_id, result.mark_id)

    Teaching (gotcha):
        This does NOT replace cosmos.commit(). It wraps it.
        Use this when you want witness traces; use raw cosmos
        for internal operations where witnessing isn't needed.
    """

    cosmos: Cosmos
    mark_store: "MarkStore | None" = None
    _witness_enabled: bool = field(init=False, default=True)

    def __post_init__(self) -> None:
        """Enable witnessing only if mark_store is provided."""
        self._witness_enabled = self.mark_store is not None

    async def commit(
        self,
        path: str,
        content: str,
        trace: WitnessTrace,
    ) -> "CommitResult":
        """
        Commit with witness trace.

        Creates a Mark, stores it, then commits to cosmos with link.

        Args:
            path: Cosmos path
            content: Content to commit
            trace: Witness trace information

        Returns:
            CommitResult with version_id and mark_id
        """
        mark_id: str | None = None

        if self._witness_enabled and self.mark_store is not None:
            # Create the witness mark
            mark = await self._create_mark(path, content, trace)

            # Store the mark (MarkStore.append is synchronous)
            self.mark_store.append(mark)
            mark_id = str(mark.id)

        # Commit to cosmos with mark reference
        version_id = await self.cosmos.commit(
            path=path,
            content=content,
            actor=trace.actor,
            reasoning=trace.reasoning,
            mark_id=mark_id,
        )

        return CommitResult(
            version_id=version_id,
            mark_id=mark_id,
            path=path,
        )

    async def _create_mark(
        self,
        path: str,
        content: str,
        trace: WitnessTrace,
    ) -> "Mark":
        """
        Create a Witness Mark for the commit.

        The Mark captures:
        - What triggered it (cosmos commit)
        - What was changed (path, summary)
        - Who did it (actor)
        - Why (reasoning, proof)
        """
        from services.witness import (
            Mark,
            Proof,
            Response,
            Stimulus,
            UmweltSnapshot,
        )

        # Create stimulus (what triggered this)
        stimulus = Stimulus(
            kind="cosmos_commit",
            content=f"Commit to {path}",
            source="kblock" if trace.kblock_id else "direct",
            metadata={
                "path": path,
                "kblock_id": trace.kblock_id,
            },
        )

        # Create response (what happened)
        response = Response(
            kind="mutation",
            content=trace.delta_summary or f"Updated {path}",
            success=True,
            metadata={"path": path},
        )

        # Create umwelt (observer context)
        trust_level = 2 if trace.actor == "Kent" else 1 if trace.actor == "Claude" else 0
        umwelt = UmweltSnapshot(
            observer_id=trace.actor.lower(),
            role=trace.actor.lower(),
            capabilities=frozenset({"write", "observe"}),
            perceptions=frozenset({"cosmos", "kblock"}),
            trust_level=trust_level,
        )

        # Use provided proof or create default
        proof = trace.proof
        if proof is None and trace.reasoning:
            proof = Proof.empirical(
                data=f"Commit to {path}",
                warrant=trace.reasoning,
                claim=f"{trace.actor} updated {path}",
            )

        # Create the mark
        return Mark(
            origin="cosmos",
            stimulus=stimulus,
            response=response,
            umwelt=umwelt,
            proof=proof,
            tags=trace.tags,
            metadata={
                "path": path,
                "kblock_id": trace.kblock_id,
                "actor": trace.actor,
            },
        )

    async def blame(self, path: str, limit: int = 10) -> list[BlameEntry]:
        """
        Get blame trace (delegates to cosmos).

        See Cosmos.blame() for details.
        """
        return await self.cosmos.blame(path, limit)

    async def blame_with_marks(
        self,
        path: str,
        limit: int = 10,
    ) -> list["BlameEntryWithMark"]:
        """
        Get blame trace with full Mark objects loaded.

        This is the "rich" version of blame() that includes
        the full Witness Mark for each entry (where available).

        Useful for displaying full justification in UI.
        """
        blame_entries = await self.cosmos.blame(path, limit)
        result: list[BlameEntryWithMark] = []

        for entry in blame_entries:
            mark = None
            if entry.mark_id and self.mark_store:
                # MarkStore.get is synchronous, expects MarkId type
                from services.witness import MarkId

                mark = self.mark_store.get(MarkId(entry.mark_id))

            result.append(
                BlameEntryWithMark(
                    version_id=entry.version_id,
                    actor=entry.actor,
                    reasoning=entry.reasoning,
                    mark_id=entry.mark_id,
                    timestamp=entry.timestamp,
                    summary=entry.summary,
                    mark=mark,
                )
            )

        return result


# -----------------------------------------------------------------------------
# Result Types
# -----------------------------------------------------------------------------


@dataclass(frozen=True)
class CommitResult:
    """Result of a witnessed commit."""

    version_id: VersionId
    mark_id: str | None
    path: str

    @property
    def is_witnessed(self) -> bool:
        """Whether this commit was witnessed (has mark_id)."""
        return self.mark_id is not None


@dataclass(frozen=True)
class BlameEntryWithMark:
    """
    BlameEntry with the full Mark object loaded.

    Use this when you need access to the Toulmin proof,
    causal links, or other Mark details.
    """

    version_id: VersionId
    actor: str
    reasoning: str | None
    mark_id: str | None
    timestamp: "datetime"
    summary: str
    mark: "Mark | None"

    @property
    def has_proof(self) -> bool:
        """Whether this entry has a Toulmin proof."""
        return self.mark is not None and self.mark.proof is not None

    @property
    def proof_claim(self) -> str | None:
        """Get the proof's claim if available."""
        if self.mark and self.mark.proof:
            return self.mark.proof.claim
        return None


# Import datetime for type hint
from datetime import datetime  # noqa: E402

# -----------------------------------------------------------------------------
# Factory Functions
# -----------------------------------------------------------------------------


def create_witnessed_cosmos(cosmos: Cosmos) -> WitnessedCosmos:
    """
    Create a WitnessedCosmos with the global mark store.

    This is the recommended way to get a witnessed cosmos instance.
    """
    try:
        from services.witness import get_mark_store

        return WitnessedCosmos(cosmos=cosmos, mark_store=get_mark_store())
    except ImportError:
        # Witness service not available, return without marks
        return WitnessedCosmos(cosmos=cosmos, mark_store=None)


# -----------------------------------------------------------------------------
# Module Exports
# -----------------------------------------------------------------------------

__all__ = [
    "WitnessTrace",
    "WitnessedCosmos",
    "CommitResult",
    "BlameEntryWithMark",
    "create_witnessed_cosmos",
]
