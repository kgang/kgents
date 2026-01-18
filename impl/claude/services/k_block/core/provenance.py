"""
KBlockProvenance: Anti-Sloppification Tracking for K-Block Content.

Tracks who authored/edited content to defend against the Sloppification Axiom (L1.9):

    "LLMs touching something inherently sloppifies it."

This module provides provenance tracking for K-Block content, distinguishing:
- Human-authored content (Kent): Needs no review
- AI-generated content (Claude): Needs review before confirmation
- Fusion content: Result of dialectic synthesis, needs review

Philosophy:
    "The proof IS the decision. The mark IS the witness."
    "Claude is evaluated, not trusted." (L1.13)

See: CLAUDE.md (Anti-Sausage Protocol, Sloppification Axiom)
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from datetime import datetime, timezone
from enum import Enum
from typing import Any


class ReviewStatus(Enum):
    """
    Review status for AI-generated or fusion content.

    The Anti-Sausage Protocol requires human review of AI output.
    This enum tracks where content is in the review pipeline.

    States:
        UNREVIEWED: Content has not been reviewed by a human
        REVIEWED: Content has been seen by human but not confirmed
        CONFIRMED: Content has been explicitly confirmed as acceptable

    Philosophy:
        "Claude is evaluated, not trusted." (L1.13)
        The transition from UNREVIEWED → CONFIRMED requires human judgment.
    """

    UNREVIEWED = "unreviewed"
    REVIEWED = "reviewed"
    CONFIRMED = "confirmed"

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class KBlockProvenance:
    """
    Provenance tracking for K-Block content.

    This frozen dataclass tracks authorship and review status to defend
    against the Sloppification Axiom. Every K-Block should have provenance
    metadata to enable:

    1. Trust attribution: Who created this content?
    2. Review tracking: Has AI-generated content been verified?
    3. Fusion lineage: Was this synthesized from dialectic?

    Attributes:
        created_by: Who created the content ('kent' | 'claude' | 'fusion')
        created_at: When the content was created
        last_edited_by: Who last edited the content
        last_edited_at: When the content was last edited
        edit_count: Number of edits since creation
        fusion_result_of: FusionId if this content is from dialectic synthesis
        review_status: Review status for AI-generated content
        reviewed_at: When content was reviewed (if applicable)
        reviewed_by: Who reviewed the content (if applicable)

    Example:
        >>> prov = KBlockProvenance(
        ...     created_by="claude",
        ...     created_at=datetime.now(timezone.utc),
        ...     last_edited_by="claude",
        ...     last_edited_at=datetime.now(timezone.utc),
        ... )
        >>> assert prov.is_ai_generated
        >>> assert prov.needs_review
        >>> reviewed = prov.with_review("kent", confirmed=True)
        >>> assert not reviewed.needs_review

    See: CLAUDE.md (Anti-Sausage Protocol, Authority Axiom L1.13)
    """

    # Authorship
    created_by: str  # 'kent' | 'claude' | 'fusion'
    created_at: datetime
    last_edited_by: str
    last_edited_at: datetime

    # Edit tracking
    edit_count: int = 0

    # Fusion lineage (for dialectic synthesis results)
    fusion_result_of: str | None = None  # FusionId if from dialectic

    # Review tracking (Anti-Sausage Protocol)
    review_status: ReviewStatus = ReviewStatus.UNREVIEWED
    reviewed_at: datetime | None = None
    reviewed_by: str | None = None

    # -------------------------------------------------------------------------
    # Properties: Trust Attribution
    # -------------------------------------------------------------------------

    @property
    def is_human_authored(self) -> bool:
        """
        Check if content was originally created by a human (Kent).

        Human-authored content is presumed trustworthy and doesn't require
        AI-specific review (though it can still be edited and reviewed).

        Returns:
            True if created_by == 'kent'
        """
        return self.created_by == "kent"

    @property
    def is_ai_generated(self) -> bool:
        """
        Check if content was originally created by AI (Claude).

        AI-generated content is subject to the Sloppification Axiom and
        should be reviewed before confirmation.

        Philosophy:
            "The sloppification is the signal that human input remains essential."

        Returns:
            True if created_by == 'claude'
        """
        return self.created_by == "claude"

    @property
    def is_fusion(self) -> bool:
        """
        Check if content is the result of dialectic synthesis.

        Fusion content arises from thesis-antithesis-synthesis processes.
        It may be created by any author but is marked by having a
        fusion_result_of reference.

        Returns:
            True if created_by == 'fusion' or fusion_result_of is not None
        """
        return self.created_by == "fusion" or self.fusion_result_of is not None

    @property
    def needs_review(self) -> bool:
        """
        Check if content requires human review.

        AI-generated content that hasn't been reviewed needs human attention
        to defend against sloppification.

        The Anti-Sausage Check (from CLAUDE.md):
            - Did I smooth anything that should stay rough?
            - Did I add words Kent wouldn't use?
            - Did I lose any opinionated stances?
            - Is this still daring, bold, creative—or did I make it safe?

        Returns:
            True if AI-generated AND review_status == UNREVIEWED
        """
        return self.is_ai_generated and self.review_status == ReviewStatus.UNREVIEWED

    # -------------------------------------------------------------------------
    # Mutation Methods (Return New Instances)
    # -------------------------------------------------------------------------

    def with_edit(self, editor: str) -> KBlockProvenance:
        """
        Record an edit and return new provenance.

        Since KBlockProvenance is frozen, this creates a new instance with
        the edit recorded. The edit_count is incremented and last_edited_*
        fields are updated.

        Args:
            editor: Who made the edit ('kent' | 'claude' | 'fusion')

        Returns:
            New KBlockProvenance with the edit recorded

        Example:
            >>> prov = KBlockProvenance(...)
            >>> updated = prov.with_edit("kent")
            >>> assert updated.edit_count == prov.edit_count + 1
            >>> assert updated.last_edited_by == "kent"
        """
        return replace(
            self,
            last_edited_by=editor,
            last_edited_at=datetime.now(timezone.utc),
            edit_count=self.edit_count + 1,
        )

    def with_review(self, reviewer: str, confirmed: bool = False) -> KBlockProvenance:
        """
        Record a review and return new provenance.

        This implements the Anti-Sausage Protocol review step. A review can
        mark content as REVIEWED (seen but not confirmed) or CONFIRMED
        (explicitly approved).

        Args:
            reviewer: Who reviewed the content (typically 'kent')
            confirmed: If True, set status to CONFIRMED; otherwise REVIEWED

        Returns:
            New KBlockProvenance with review recorded

        Example:
            >>> prov = KBlockProvenance(created_by="claude", ...)
            >>> assert prov.needs_review
            >>> reviewed = prov.with_review("kent", confirmed=True)
            >>> assert reviewed.review_status == ReviewStatus.CONFIRMED
            >>> assert not reviewed.needs_review
        """
        status = ReviewStatus.CONFIRMED if confirmed else ReviewStatus.REVIEWED
        return replace(
            self,
            review_status=status,
            reviewed_at=datetime.now(timezone.utc),
            reviewed_by=reviewer,
        )

    # -------------------------------------------------------------------------
    # Factory Methods
    # -------------------------------------------------------------------------

    @classmethod
    def human_created(cls, author: str = "kent") -> KBlockProvenance:
        """
        Create provenance for human-authored content.

        Convenience factory for content created by a human. Defaults to
        'kent' as the author.

        Args:
            author: The human author (default: 'kent')

        Returns:
            New KBlockProvenance for human-authored content

        Example:
            >>> prov = KBlockProvenance.human_created()
            >>> assert prov.is_human_authored
            >>> assert not prov.needs_review
        """
        now = datetime.now(timezone.utc)
        return cls(
            created_by=author,
            created_at=now,
            last_edited_by=author,
            last_edited_at=now,
            review_status=ReviewStatus.CONFIRMED,  # Human content is pre-confirmed
        )

    @classmethod
    def ai_generated(cls, model: str = "claude") -> KBlockProvenance:
        """
        Create provenance for AI-generated content.

        Convenience factory for content created by an AI. Defaults to
        'claude' as the model. AI-generated content starts as UNREVIEWED.

        Args:
            model: The AI model (default: 'claude')

        Returns:
            New KBlockProvenance for AI-generated content

        Example:
            >>> prov = KBlockProvenance.ai_generated()
            >>> assert prov.is_ai_generated
            >>> assert prov.needs_review
        """
        now = datetime.now(timezone.utc)
        return cls(
            created_by=model,
            created_at=now,
            last_edited_by=model,
            last_edited_at=now,
            review_status=ReviewStatus.UNREVIEWED,
        )

    @classmethod
    def from_fusion(cls, fusion_id: str, synthesizer: str = "claude") -> KBlockProvenance:
        """
        Create provenance for dialectic synthesis result.

        Convenience factory for content created through thesis-antithesis-synthesis.
        Fusion content is linked to the FusionId and starts as UNREVIEWED.

        Args:
            fusion_id: The FusionId linking to the dialectic process
            synthesizer: Who performed the synthesis (default: 'claude')

        Returns:
            New KBlockProvenance for fusion content

        Example:
            >>> prov = KBlockProvenance.from_fusion("fusion-abc123")
            >>> assert prov.is_fusion
            >>> assert prov.fusion_result_of == "fusion-abc123"
        """
        now = datetime.now(timezone.utc)
        return cls(
            created_by="fusion",
            created_at=now,
            last_edited_by=synthesizer,
            last_edited_at=now,
            fusion_result_of=fusion_id,
            review_status=ReviewStatus.UNREVIEWED,
        )

    # -------------------------------------------------------------------------
    # Serialization
    # -------------------------------------------------------------------------

    def to_dict(self) -> dict[str, Any]:
        """Serialize provenance to dictionary."""
        return {
            "created_by": self.created_by,
            "created_at": self.created_at.isoformat(),
            "last_edited_by": self.last_edited_by,
            "last_edited_at": self.last_edited_at.isoformat(),
            "edit_count": self.edit_count,
            "fusion_result_of": self.fusion_result_of,
            "review_status": self.review_status.value,
            "reviewed_at": self.reviewed_at.isoformat() if self.reviewed_at else None,
            "reviewed_by": self.reviewed_by,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> KBlockProvenance:
        """Deserialize provenance from dictionary."""
        return cls(
            created_by=data["created_by"],
            created_at=datetime.fromisoformat(data["created_at"]),
            last_edited_by=data["last_edited_by"],
            last_edited_at=datetime.fromisoformat(data["last_edited_at"]),
            edit_count=data.get("edit_count", 0),
            fusion_result_of=data.get("fusion_result_of"),
            review_status=ReviewStatus(data.get("review_status", "unreviewed")),
            reviewed_at=(
                datetime.fromisoformat(data["reviewed_at"]) if data.get("reviewed_at") else None
            ),
            reviewed_by=data.get("reviewed_by"),
        )

    # -------------------------------------------------------------------------
    # String Representation
    # -------------------------------------------------------------------------

    def __repr__(self) -> str:
        """Readable representation."""
        review_str = f", review={self.review_status.value}" if self.is_ai_generated else ""
        fusion_str = f", fusion={self.fusion_result_of[:12]}..." if self.fusion_result_of else ""
        return f"KBlockProvenance(by={self.created_by}, edits={self.edit_count}{review_str}{fusion_str})"


__all__ = [
    "KBlockProvenance",
    "ReviewStatus",
]
