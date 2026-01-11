"""
Amendment model for constitutional changes.

This module defines the data structures for proposing, reviewing, and
applying amendments to kgents constitutional K-Blocks.

The Amendment Model:
    - Amendment: A proposed change to a K-Block
    - AmendmentStatus: Lifecycle states (DRAFT -> APPLIED/REVERTED)
    - AmendmentType: What kind of change (principle, axiom, layer, etc.)

Every amendment creates a complete audit trail:
    - original_content: What was there before
    - proposed_content: What we want to change it to
    - diff: Unified diff for review
    - reasoning: Why this change is needed
    - review_notes: Feedback from reviewers
    - approval/rejection_reasoning: Final decision rationale
    - pre/post_commit_sha: Git integration for version control

Philosophy:
    "Constitutional changes are not casual. Every change is witnessed,
     reviewed, and traceable to its reasoning."

See: spec/protocols/zero-seed1/galois.md (constitutional evaluation)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class AmendmentStatus(Enum):
    """
    Lifecycle states for an amendment.

    State Machine:
        DRAFT -> PROPOSED -> UNDER_REVIEW -> APPROVED -> APPLIED
                                          -> REJECTED
        APPLIED -> REVERTED

    Teaching:
        gotcha: Only APPROVED amendments can be APPLIED.
                Only APPLIED amendments can be REVERTED.
                State transitions are enforced in AmendmentWorkflowService.
    """

    DRAFT = "draft"
    PROPOSED = "proposed"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    APPLIED = "applied"
    REVERTED = "reverted"


class AmendmentType(Enum):
    """
    Types of constitutional changes.

    Categories:
        PRINCIPLE_*: Changes to core principles (L2)
        AXIOM_REFINEMENT: Changes to axioms (L0-L1)
        DERIVATION_CORRECTION: Fixes to derived content (L3-L4)
        LAYER_RESTRUCTURE: Structural changes to K-Block organization

    Teaching:
        gotcha: PRINCIPLE_REMOVAL requires careful review—it may affect
                derived K-Blocks that depend on that principle.
    """

    PRINCIPLE_ADDITION = "principle_addition"
    PRINCIPLE_MODIFICATION = "principle_modification"
    PRINCIPLE_REMOVAL = "principle_removal"
    AXIOM_REFINEMENT = "axiom_refinement"
    DERIVATION_CORRECTION = "derivation_correction"
    LAYER_RESTRUCTURE = "layer_restructure"


@dataclass
class Amendment:
    """
    A proposed change to a constitutional K-Block.

    An Amendment captures the complete context of a proposed change:
    - What is being changed (target_kblock, target_layer)
    - Who proposed it (proposer)
    - Why it's needed (reasoning)
    - The actual change (original_content -> proposed_content, diff)
    - Review history (review_notes)
    - Final decision (approval/rejection_reasoning)
    - Git integration (pre/post_commit_sha)

    Attributes:
        id: Unique identifier (amendment-{uuid8})
        title: Human-readable title for the amendment
        description: Detailed description of what's being changed
        amendment_type: Category of change (see AmendmentType)
        status: Current lifecycle state (see AmendmentStatus)
        target_kblock: Path to K-Block being amended (e.g., "principles/tasteful.md")
        target_layer: Constitutional layer (L0-L4)
        original_content: Content before the amendment
        proposed_content: Content after the amendment
        diff: Unified diff format showing changes
        proposer: Who created this ("kent", "claude", or agent id)
        reasoning: Why this change is needed
        principles_affected: List of principle names touched by this change
        review_notes: List of {reviewer, note, timestamp} dicts
        approval_reasoning: Rationale for approval (if approved)
        rejection_reasoning: Rationale for rejection (if rejected)
        created_at: When the amendment was created
        proposed_at: When moved to PROPOSED status
        reviewed_at: When final decision was made
        applied_at: When the change was applied to the K-Block
        pre_commit_sha: Git commit SHA before applying
        post_commit_sha: Git commit SHA after applying

    Example:
        >>> amendment = Amendment(
        ...     id="amendment-a1b2c3d4",
        ...     title="Add anti-patterns to TASTEFUL",
        ...     description="Explicit anti-patterns help prevent common mistakes",
        ...     amendment_type=AmendmentType.PRINCIPLE_MODIFICATION,
        ...     status=AmendmentStatus.DRAFT,
        ...     target_kblock="principles/tasteful.md",
        ...     target_layer=2,
        ...     original_content="## TASTEFUL\n...",
        ...     proposed_content="## TASTEFUL\n...\n### Anti-Patterns\n...",
        ...     diff="@@ -1,5 +1,10 @@\n ...",
        ...     proposer="kent",
        ...     reasoning="Anti-patterns help prevent common mistakes",
        ...     principles_affected=["TASTEFUL"],
        ...     review_notes=[],
        ... )
    """

    id: str
    title: str
    description: str
    amendment_type: AmendmentType
    status: AmendmentStatus
    target_kblock: str  # K-Block path being amended
    target_layer: int  # L0-L4

    # The change
    original_content: str
    proposed_content: str
    diff: str  # unified diff format

    # Reasoning
    proposer: str  # "kent" | "claude" | agent id
    reasoning: str
    principles_affected: list[str]  # Which principles this touches

    # Review
    review_notes: list[dict[str, Any]]  # {reviewer, note, timestamp}
    approval_reasoning: str | None = None
    rejection_reasoning: str | None = None

    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)
    proposed_at: datetime | None = None
    reviewed_at: datetime | None = None
    applied_at: datetime | None = None

    # Git integration
    pre_commit_sha: str | None = None
    post_commit_sha: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """
        Convert to JSON-serializable dictionary.

        Used for API responses and persistence.
        """
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "amendment_type": self.amendment_type.value,
            "status": self.status.value,
            "target_kblock": self.target_kblock,
            "target_layer": self.target_layer,
            "original_content": self.original_content,
            "proposed_content": self.proposed_content,
            "diff": self.diff,
            "proposer": self.proposer,
            "reasoning": self.reasoning,
            "principles_affected": self.principles_affected,
            "review_notes": self.review_notes,
            "approval_reasoning": self.approval_reasoning,
            "rejection_reasoning": self.rejection_reasoning,
            "created_at": self.created_at.isoformat(),
            "proposed_at": self.proposed_at.isoformat() if self.proposed_at else None,
            "reviewed_at": self.reviewed_at.isoformat() if self.reviewed_at else None,
            "applied_at": self.applied_at.isoformat() if self.applied_at else None,
            "pre_commit_sha": self.pre_commit_sha,
            "post_commit_sha": self.post_commit_sha,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Amendment":
        """
        Create an Amendment from a dictionary.

        Used for loading from persistence.
        """
        return cls(
            id=data["id"],
            title=data["title"],
            description=data["description"],
            amendment_type=AmendmentType(data["amendment_type"]),
            status=AmendmentStatus(data["status"]),
            target_kblock=data["target_kblock"],
            target_layer=data["target_layer"],
            original_content=data["original_content"],
            proposed_content=data["proposed_content"],
            diff=data["diff"],
            proposer=data["proposer"],
            reasoning=data["reasoning"],
            principles_affected=data["principles_affected"],
            review_notes=data.get("review_notes", []),
            approval_reasoning=data.get("approval_reasoning"),
            rejection_reasoning=data.get("rejection_reasoning"),
            created_at=datetime.fromisoformat(data["created_at"]),
            proposed_at=(
                datetime.fromisoformat(data["proposed_at"]) if data.get("proposed_at") else None
            ),
            reviewed_at=(
                datetime.fromisoformat(data["reviewed_at"]) if data.get("reviewed_at") else None
            ),
            applied_at=(
                datetime.fromisoformat(data["applied_at"]) if data.get("applied_at") else None
            ),
            pre_commit_sha=data.get("pre_commit_sha"),
            post_commit_sha=data.get("post_commit_sha"),
        )


# =============================================================================
# Module Exports
# =============================================================================

__all__ = [
    "Amendment",
    "AmendmentStatus",
    "AmendmentType",
]
