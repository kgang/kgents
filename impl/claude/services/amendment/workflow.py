"""
Amendment workflow service for constitutional evolution.

This service manages the complete lifecycle of constitutional amendments:
    DRAFT -> PROPOSED -> UNDER_REVIEW -> APPROVED/REJECTED -> APPLIED/REVERTED

All state transitions are atomic and witnessed, creating an auditable
trail of constitutional evolution.

The Workflow:
    1. create_draft() - Create a new amendment in DRAFT state
    2. propose() - Submit draft for review (DRAFT -> PROPOSED)
    3. start_review() - Begin formal review (PROPOSED -> UNDER_REVIEW)
    4. add_review_note() - Add feedback during review
    5. approve() - Approve for application (UNDER_REVIEW -> APPROVED)
       reject() - Reject the amendment (UNDER_REVIEW -> REJECTED)
    6. apply() - Apply approved amendment to K-Block (APPROVED -> APPLIED)
    7. revert() - Revert an applied amendment (APPLIED -> REVERTED)

Philosophy:
    "Constitutional changes are not casual. Every transition is witnessed,
     every decision is recorded, every revert is possible."

Example:
    >>> svc = AmendmentWorkflowService()
    >>> amendment = await svc.create_draft(
    ...     title="Refine TASTEFUL principle",
    ...     description="Add explicit anti-pattern examples",
    ...     amendment_type=AmendmentType.PRINCIPLE_MODIFICATION,
    ...     target_kblock="principles/tasteful.md",
    ...     target_layer=2,
    ...     proposed_content="...",
    ...     proposer="kent",
    ...     reasoning="Anti-patterns help prevent common mistakes",
    ...     principles_affected=["TASTEFUL"],
    ... )
    >>> await svc.propose(amendment.id)
    >>> await svc.start_review(amendment.id)
    >>> await svc.add_review_note(amendment.id, "claude", "Looks good!")
    >>> await svc.approve(amendment.id, "Clear improvement")
    >>> await svc.apply(amendment.id)

See: spec/protocols/zero-seed1/galois.md (constitutional evaluation)
"""

from __future__ import annotations

import difflib
import logging
import subprocess
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING

from .model import Amendment, AmendmentStatus, AmendmentType

if TYPE_CHECKING:
    from services.witness import WitnessCrystalAdapter

logger = logging.getLogger(__name__)


# =============================================================================
# Exceptions
# =============================================================================


class AmendmentError(Exception):
    """Base exception for amendment errors."""

    pass


class AmendmentNotFoundError(AmendmentError):
    """Raised when an amendment is not found."""

    pass


class InvalidStateTransitionError(AmendmentError):
    """Raised when a state transition is invalid."""

    pass


# =============================================================================
# AmendmentWorkflowService
# =============================================================================


@dataclass
class AmendmentWorkflowService:
    """
    Manages the lifecycle of constitutional amendments.

    This service is the single point of control for all amendment operations.
    It enforces the state machine, generates diffs, and integrates with
    Git for version control.

    Attributes:
        spec_root: Path to the spec/ directory (default: "spec")
        witness: Optional WitnessCrystalAdapter for creating witness marks

    State Machine:
        DRAFT -> PROPOSED -> UNDER_REVIEW -> APPROVED -> APPLIED
                                          -> REJECTED
        APPLIED -> REVERTED

    Teaching:
        gotcha: The service maintains in-memory storage for amendments.
                Phase 2 will add D-gent persistence for durability.
                (Evidence: _amendments and _history dicts)

        gotcha: Rejected and applied amendments move to _history.
                Only pending amendments remain in _amendments.
                Query both using get_amendment().
    """

    spec_root: Path = field(default_factory=lambda: Path("spec"))
    witness: "WitnessCrystalAdapter | None" = None

    # Phase 1: In-memory storage
    _amendments: dict[str, Amendment] = field(default_factory=dict, repr=False)
    _history: list[Amendment] = field(default_factory=list, repr=False)  # Applied/rejected

    # ==========================================================================
    # Lifecycle Methods
    # ==========================================================================

    async def create_draft(
        self,
        title: str,
        description: str,
        amendment_type: AmendmentType,
        target_kblock: str,
        target_layer: int,
        proposed_content: str,
        proposer: str,
        reasoning: str,
        principles_affected: list[str],
    ) -> Amendment:
        """
        Create a draft amendment.

        This is the entry point for proposing a constitutional change.
        The amendment starts in DRAFT status and must be proposed before review.

        Args:
            title: Human-readable title for the amendment
            description: Detailed description of what's being changed
            amendment_type: Category of change (see AmendmentType)
            target_kblock: Path to K-Block being amended
            target_layer: Constitutional layer (L0-L4)
            proposed_content: New content for the K-Block
            proposer: Who is proposing ("kent", "claude", or agent id)
            reasoning: Why this change is needed
            principles_affected: List of principle names affected

        Returns:
            A new Amendment in DRAFT status

        Example:
            >>> amendment = await svc.create_draft(
            ...     title="Add anti-patterns",
            ...     description="Document common mistakes",
            ...     amendment_type=AmendmentType.PRINCIPLE_MODIFICATION,
            ...     target_kblock="principles/tasteful.md",
            ...     target_layer=2,
            ...     proposed_content="...",
            ...     proposer="kent",
            ...     reasoning="Prevention is better than cure",
            ...     principles_affected=["TASTEFUL"],
            ... )
        """
        # Get original content
        original_content = await self._get_kblock_content(target_kblock)

        # Generate diff
        diff = self._generate_diff(original_content, proposed_content, target_kblock)

        amendment = Amendment(
            id=f"amendment-{uuid.uuid4().hex[:8]}",
            title=title,
            description=description,
            amendment_type=amendment_type,
            status=AmendmentStatus.DRAFT,
            target_kblock=target_kblock,
            target_layer=target_layer,
            original_content=original_content,
            proposed_content=proposed_content,
            diff=diff,
            proposer=proposer,
            reasoning=reasoning,
            principles_affected=principles_affected,
            review_notes=[],
        )

        self._amendments[amendment.id] = amendment

        # Witness the creation
        await self._witness_event(
            "amendment_created",
            amendment,
            f"Amendment '{title}' created by {proposer}",
        )

        logger.info(f"Created draft amendment: {amendment.id} - {title}")
        return amendment

    async def propose(self, amendment_id: str) -> Amendment:
        """
        Submit a draft for review.

        Transitions: DRAFT -> PROPOSED

        Args:
            amendment_id: The amendment to propose

        Returns:
            The updated Amendment

        Raises:
            AmendmentNotFoundError: If amendment not found
            InvalidStateTransitionError: If not in DRAFT status
        """
        amendment = self._get_or_raise(amendment_id)

        if amendment.status != AmendmentStatus.DRAFT:
            raise InvalidStateTransitionError(
                f"Can only propose drafts, current status: {amendment.status.value}"
            )

        amendment.status = AmendmentStatus.PROPOSED
        amendment.proposed_at = datetime.now()

        await self._witness_event(
            "amendment_proposed",
            amendment,
            f"Amendment '{amendment.title}' proposed for review",
        )

        logger.info(f"Amendment proposed: {amendment_id}")
        return amendment

    async def start_review(self, amendment_id: str) -> Amendment:
        """
        Begin formal review of a proposed amendment.

        Transitions: PROPOSED -> UNDER_REVIEW

        Args:
            amendment_id: The amendment to review

        Returns:
            The updated Amendment

        Raises:
            AmendmentNotFoundError: If amendment not found
            InvalidStateTransitionError: If not in PROPOSED status
        """
        amendment = self._get_or_raise(amendment_id)

        if amendment.status != AmendmentStatus.PROPOSED:
            raise InvalidStateTransitionError(
                f"Can only review proposed amendments, current status: {amendment.status.value}"
            )

        amendment.status = AmendmentStatus.UNDER_REVIEW

        await self._witness_event(
            "amendment_review_started",
            amendment,
            f"Review started for amendment '{amendment.title}'",
        )

        logger.info(f"Amendment review started: {amendment_id}")
        return amendment

    async def add_review_note(
        self,
        amendment_id: str,
        reviewer: str,
        note: str,
    ) -> Amendment:
        """
        Add a review note to an amendment.

        Can be added at any stage (even after approval/rejection for audit).

        Args:
            amendment_id: The amendment to add note to
            reviewer: Who is adding the note ("kent", "claude", or agent id)
            note: The review feedback

        Returns:
            The updated Amendment

        Raises:
            AmendmentNotFoundError: If amendment not found
        """
        amendment = self._get_or_raise(amendment_id)

        amendment.review_notes.append(
            {
                "reviewer": reviewer,
                "note": note,
                "timestamp": datetime.now().isoformat(),
            }
        )

        await self._witness_event(
            "amendment_review_note",
            amendment,
            f"{reviewer} added review note to '{amendment.title}'",
        )

        logger.info(f"Review note added to {amendment_id} by {reviewer}")
        return amendment

    async def approve(
        self,
        amendment_id: str,
        approval_reasoning: str,
    ) -> Amendment:
        """
        Approve an amendment for application.

        Transitions: PROPOSED|UNDER_REVIEW -> APPROVED

        Args:
            amendment_id: The amendment to approve
            approval_reasoning: Why this amendment is approved

        Returns:
            The updated Amendment

        Raises:
            AmendmentNotFoundError: If amendment not found
            InvalidStateTransitionError: If not in PROPOSED or UNDER_REVIEW status
        """
        amendment = self._get_or_raise(amendment_id)

        valid_states = {AmendmentStatus.PROPOSED, AmendmentStatus.UNDER_REVIEW}
        if amendment.status not in valid_states:
            raise InvalidStateTransitionError(
                f"Cannot approve amendment in status: {amendment.status.value}"
            )

        amendment.status = AmendmentStatus.APPROVED
        amendment.approval_reasoning = approval_reasoning
        amendment.reviewed_at = datetime.now()

        await self._witness_event(
            "amendment_approved",
            amendment,
            f"Amendment '{amendment.title}' approved: {approval_reasoning}",
        )

        logger.info(f"Amendment approved: {amendment_id}")
        return amendment

    async def reject(
        self,
        amendment_id: str,
        rejection_reasoning: str,
    ) -> Amendment:
        """
        Reject an amendment.

        Transitions: PROPOSED|UNDER_REVIEW -> REJECTED

        The rejected amendment moves to history.

        Args:
            amendment_id: The amendment to reject
            rejection_reasoning: Why this amendment is rejected

        Returns:
            The rejected Amendment

        Raises:
            AmendmentNotFoundError: If amendment not found
            InvalidStateTransitionError: If not in PROPOSED or UNDER_REVIEW status
        """
        amendment = self._get_or_raise(amendment_id)

        valid_states = {AmendmentStatus.PROPOSED, AmendmentStatus.UNDER_REVIEW}
        if amendment.status not in valid_states:
            raise InvalidStateTransitionError(
                f"Cannot reject amendment in status: {amendment.status.value}"
            )

        amendment.status = AmendmentStatus.REJECTED
        amendment.rejection_reasoning = rejection_reasoning
        amendment.reviewed_at = datetime.now()

        # Move to history
        self._history.append(amendment)
        del self._amendments[amendment_id]

        await self._witness_event(
            "amendment_rejected",
            amendment,
            f"Amendment '{amendment.title}' rejected: {rejection_reasoning}",
        )

        logger.info(f"Amendment rejected: {amendment_id}")
        return amendment

    async def apply(self, amendment_id: str) -> Amendment:
        """
        Apply an approved amendment to the spec.

        Transitions: APPROVED -> APPLIED

        This actually modifies the K-Block file. The pre-commit SHA is
        recorded for potential reversion.

        Args:
            amendment_id: The amendment to apply

        Returns:
            The applied Amendment

        Raises:
            AmendmentNotFoundError: If amendment not found
            InvalidStateTransitionError: If not in APPROVED status
        """
        amendment = self._get_or_raise(amendment_id)

        if amendment.status != AmendmentStatus.APPROVED:
            raise InvalidStateTransitionError(
                f"Can only apply approved amendments, current status: {amendment.status.value}"
            )

        # Get current commit SHA before applying
        amendment.pre_commit_sha = await self._get_current_commit()

        # Write the new content
        await self._write_kblock_content(amendment.target_kblock, amendment.proposed_content)

        amendment.status = AmendmentStatus.APPLIED
        amendment.applied_at = datetime.now()

        # Move to history
        self._history.append(amendment)
        del self._amendments[amendment_id]

        await self._witness_event(
            "amendment_applied",
            amendment,
            f"Amendment '{amendment.title}' applied to {amendment.target_kblock}",
        )

        logger.info(f"Amendment applied: {amendment_id} -> {amendment.target_kblock}")
        return amendment

    async def revert(self, amendment_id: str) -> Amendment:
        """
        Revert an applied amendment.

        Transitions: APPLIED -> REVERTED

        This restores the original content of the K-Block.

        Args:
            amendment_id: The amendment to revert

        Returns:
            The reverted Amendment

        Raises:
            AmendmentNotFoundError: If amendment not found in history
            InvalidStateTransitionError: If not in APPLIED status
        """
        # Find in history
        amendment = next((a for a in self._history if a.id == amendment_id), None)
        if not amendment:
            raise AmendmentNotFoundError(f"Amendment {amendment_id} not found in history")

        if amendment.status != AmendmentStatus.APPLIED:
            raise InvalidStateTransitionError(
                f"Can only revert applied amendments, current status: {amendment.status.value}"
            )

        # Restore original content
        await self._write_kblock_content(amendment.target_kblock, amendment.original_content)

        amendment.status = AmendmentStatus.REVERTED

        await self._witness_event(
            "amendment_reverted",
            amendment,
            f"Amendment '{amendment.title}' reverted on {amendment.target_kblock}",
        )

        logger.info(f"Amendment reverted: {amendment_id}")
        return amendment

    # ==========================================================================
    # Query Methods
    # ==========================================================================

    def list_pending(self) -> list[Amendment]:
        """
        List all pending amendments (draft, proposed, under_review, approved).

        Returns:
            List of pending amendments
        """
        return list(self._amendments.values())

    def list_history(self, limit: int = 50) -> list[Amendment]:
        """
        List applied/rejected amendments from history.

        Args:
            limit: Maximum number of amendments to return (default 50)

        Returns:
            List of historical amendments, most recent first
        """
        return self._history[-limit:]

    def get_amendment(self, amendment_id: str) -> Amendment | None:
        """
        Get a specific amendment by ID.

        Searches both pending and historical amendments.

        Args:
            amendment_id: The amendment ID to find

        Returns:
            The Amendment if found, None otherwise
        """
        return self._amendments.get(amendment_id) or next(
            (a for a in self._history if a.id == amendment_id), None
        )

    def get_amendments_for_kblock(self, kblock_path: str) -> list[Amendment]:
        """
        Get all amendments (pending and historical) for a K-Block.

        Useful for viewing the amendment history of a specific constitutional document.

        Args:
            kblock_path: The K-Block path to search

        Returns:
            List of amendments targeting this K-Block
        """
        pending = [a for a in self._amendments.values() if a.target_kblock == kblock_path]
        historical = [a for a in self._history if a.target_kblock == kblock_path]
        return pending + historical

    # ==========================================================================
    # Private Methods
    # ==========================================================================

    def _get_or_raise(self, amendment_id: str) -> Amendment:
        """Get an amendment or raise AmendmentNotFoundError."""
        amendment = self._amendments.get(amendment_id)
        if not amendment:
            raise AmendmentNotFoundError(f"Amendment {amendment_id} not found")
        return amendment

    async def _get_kblock_content(self, kblock_path: str) -> str:
        """
        Read K-Block content from spec.

        Handles both kblock:// paths and file paths.
        """
        # Handle both kblock:// paths and file paths
        if kblock_path.startswith("kblock://"):
            path = kblock_path.replace("kblock://", "")
        else:
            path = kblock_path

        full_path = self.spec_root / path
        if full_path.exists():
            return full_path.read_text()
        return ""

    async def _write_kblock_content(self, kblock_path: str, content: str) -> None:
        """
        Write K-Block content to spec.

        Creates parent directories if needed.
        """
        if kblock_path.startswith("kblock://"):
            path = kblock_path.replace("kblock://", "")
        else:
            path = kblock_path

        full_path = self.spec_root / path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.write_text(content)

    async def _get_current_commit(self) -> str:
        """Get current git commit SHA."""
        try:
            result = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                capture_output=True,
                text=True,
                cwd=self.spec_root,
            )
            return result.stdout.strip()
        except Exception:
            return "unknown"

    def _generate_diff(self, original: str, proposed: str, filename: str) -> str:
        """Generate unified diff between original and proposed content."""
        original_lines = original.splitlines(keepends=True)
        proposed_lines = proposed.splitlines(keepends=True)

        diff_lines = difflib.unified_diff(
            original_lines,
            proposed_lines,
            fromfile=f"a/{filename}",
            tofile=f"b/{filename}",
        )
        return "".join(diff_lines)

    async def _witness_event(
        self,
        event_type: str,
        amendment: Amendment,
        message: str,
    ) -> None:
        """
        Create a witness mark for an amendment event.

        Integrates with WitnessCrystalAdapter if available.
        """
        if self.witness is None:
            logger.debug(f"Witness unavailable, skipping mark: {event_type}")
            return

        try:
            await self.witness.create_mark(
                action=event_type,
                reasoning=message,
                metadata={
                    "amendment_id": amendment.id,
                    "amendment_type": amendment.amendment_type.value,
                    "status": amendment.status.value,
                    "target_kblock": amendment.target_kblock,
                    "proposer": amendment.proposer,
                },
                tags=["amendment", event_type, f"layer:{amendment.target_layer}"],
                author=amendment.proposer,
            )
        except Exception as e:
            logger.warning(f"Failed to create witness mark: {e}")


# =============================================================================
# Module Exports
# =============================================================================

__all__ = [
    "AmendmentWorkflowService",
    "AmendmentError",
    "AmendmentNotFoundError",
    "InvalidStateTransitionError",
]
