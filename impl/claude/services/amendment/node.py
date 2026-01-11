"""
Amendment AGENTESE Node: @node("self.amendment")

Exposes the Constitutional Amendment system via AGENTESE.

AGENTESE Paths:
- self.amendment.manifest  - Amendment system status and pending amendments
- self.amendment.propose   - Create and submit a new amendment
- self.amendment.review    - Add review notes to an amendment
- self.amendment.approve   - Approve an amendment for application
- self.amendment.reject    - Reject an amendment
- self.amendment.apply     - Apply an approved amendment to the K-Block
- self.amendment.revert    - Revert an applied amendment
- self.amendment.list      - List amendments (pending or history)
- self.amendment.get       - Get a specific amendment by ID

The Constitutional Model:
    - Amendments enable kgents to evolve its own constitution
    - All changes are witnessed and auditable
    - Strict state machine enforces proper workflow
    - Git integration enables version control

The Metaphysical Fullstack Pattern (AD-009):
    - The protocol IS the API
    - No explicit routes needed
    - All transports collapse to logos.invoke(path, observer, ...)

See: plans/self-reflective-os/ (Week 11-12: Amendment System)
See: docs/skills/metaphysical-fullstack.md
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from protocols.agentese.contract import Contract, Response
from protocols.agentese.node import (
    BaseLogosNode,
    Observer,
    Renderable,
)
from protocols.agentese.registry import node

from .model import AmendmentStatus, AmendmentType
from .workflow import AmendmentWorkflowService

if TYPE_CHECKING:
    from bootstrap.umwelt import Umwelt


# =============================================================================
# Contract Dataclasses
# =============================================================================


@dataclass(frozen=True)
class AmendmentManifestResponse:
    """Response for amendment manifest."""

    total_pending: int
    total_history: int
    drafts: int
    proposed: int
    under_review: int
    approved: int
    applied: int
    rejected: int
    reverted: int


@dataclass(frozen=True)
class ProposeRequest:
    """Request to create and propose an amendment."""

    title: str
    description: str
    amendment_type: str  # AmendmentType value
    target_kblock: str
    target_layer: int
    proposed_content: str
    reasoning: str
    principles_affected: list[str]


@dataclass(frozen=True)
class ProposeResponse:
    """Response after creating an amendment."""

    amendment_id: str
    title: str
    status: str
    diff: str


@dataclass(frozen=True)
class ReviewRequest:
    """Request to add a review note."""

    amendment_id: str
    note: str


@dataclass(frozen=True)
class ReviewResponse:
    """Response after adding a review note."""

    amendment_id: str
    review_count: int


@dataclass(frozen=True)
class ApproveRequest:
    """Request to approve an amendment."""

    amendment_id: str
    reasoning: str


@dataclass(frozen=True)
class RejectRequest:
    """Request to reject an amendment."""

    amendment_id: str
    reasoning: str


@dataclass(frozen=True)
class ApplyRevertRequest:
    """Request to apply or revert an amendment."""

    amendment_id: str


@dataclass(frozen=True)
class AmendmentResponse:
    """Response with amendment details."""

    amendment_id: str
    title: str
    status: str
    target_kblock: str
    diff: str | None = None


@dataclass(frozen=True)
class ListRequest:
    """Request to list amendments."""

    scope: str = "pending"  # "pending" | "history" | "all"
    limit: int = 50


@dataclass(frozen=True)
class GetRequest:
    """Request to get a specific amendment."""

    amendment_id: str


@dataclass(frozen=True)
class AmendmentListResponse:
    """Response for listing amendments."""

    amendments: list[dict[str, Any]]


# =============================================================================
# Rendering Classes
# =============================================================================


@dataclass(frozen=True)
class AmendmentManifestRendering:
    """Rendering for amendment status manifest."""

    total_pending: int
    total_history: int
    drafts: int
    proposed: int
    under_review: int
    approved: int
    applied: int
    rejected: int
    reverted: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": "amendment_manifest",
            "total_pending": self.total_pending,
            "total_history": self.total_history,
            "by_status": {
                "drafts": self.drafts,
                "proposed": self.proposed,
                "under_review": self.under_review,
                "approved": self.approved,
                "applied": self.applied,
                "rejected": self.rejected,
                "reverted": self.reverted,
            },
        }

    def to_text(self) -> str:
        lines = [
            "Amendment System Status",
            "=======================",
            f"Pending: {self.total_pending}",
            f"  Drafts: {self.drafts}",
            f"  Proposed: {self.proposed}",
            f"  Under Review: {self.under_review}",
            f"  Approved: {self.approved}",
            "",
            f"History: {self.total_history}",
            f"  Applied: {self.applied}",
            f"  Rejected: {self.rejected}",
            f"  Reverted: {self.reverted}",
        ]
        return "\n".join(lines)


# =============================================================================
# AmendmentNode
# =============================================================================


@node(
    "self.amendment",
    description="Constitutional amendment workflow - propose, review, apply, revert constitutional changes",
    dependencies=("amendment_service",),
    contracts={
        # Perception aspects (Response only)
        "manifest": Response(AmendmentManifestResponse),
        # Mutation aspects (Contract with request + response)
        "propose": Contract(ProposeRequest, ProposeResponse),
        "review": Contract(ReviewRequest, ReviewResponse),
        "approve": Contract(ApproveRequest, AmendmentResponse),
        "reject": Contract(RejectRequest, AmendmentResponse),
        "apply": Contract(ApplyRevertRequest, AmendmentResponse),
        "revert": Contract(ApplyRevertRequest, AmendmentResponse),
        "list": Contract(ListRequest, AmendmentListResponse),
        "get": Contract(GetRequest, AmendmentResponse),
    },
    examples=[
        ("manifest", {}, "View amendment system status"),
        (
            "propose",
            {
                "title": "Refine TASTEFUL principle",
                "description": "Add anti-pattern examples",
                "amendment_type": "principle_modification",
                "target_kblock": "principles/tasteful.md",
                "target_layer": 2,
                "proposed_content": "...",
                "reasoning": "Anti-patterns help prevent mistakes",
                "principles_affected": ["TASTEFUL"],
            },
            "Create a new amendment",
        ),
        ("list", {"scope": "pending"}, "List pending amendments"),
    ],
)
class AmendmentNode(BaseLogosNode):
    """
    AGENTESE node for Constitutional Amendments.

    Exposes AmendmentWorkflowService through the universal protocol.
    All transports (HTTP, WebSocket, CLI) collapse to this interface.

    The philosophical insight:
        The constitution is not frozen. It evolves through witnessed amendments.
        Every change is auditable, every revert is possible.

    Example:
        # Via AGENTESE gateway
        POST /agentese/self/amendment/propose
        {"title": "...", "description": "...", ...}

        # Via Logos directly
        await logos.invoke("self.amendment.propose", observer, title="...", ...)

        # Via CLI
        kgents amendment propose --title "..." --target-kblock "..."
    """

    def __init__(self, amendment_service: AmendmentWorkflowService) -> None:
        """
        Initialize AmendmentNode.

        Args:
            amendment_service: The AmendmentWorkflowService (injected by container)
        """
        self._service = amendment_service

    @property
    def handle(self) -> str:
        return "self.amendment"

    def _get_affordances_for_archetype(self, archetype: str) -> tuple[str, ...]:
        """
        Return archetype-specific affordances.

        Constitutional amendments are sensitive operations:
        - developer/operator: Full access (propose, review, approve, apply, revert)
        - architect: Can propose and review, but not approve/apply/revert
        - newcomer: Can view manifest and list only
        - guest: Manifest only
        """
        archetype_lower = archetype.lower() if archetype else "guest"

        # Full access: developers, operators (Kent's trusted proxies)
        if archetype_lower in ("developer", "operator", "admin", "system"):
            return (
                "manifest",
                "propose",
                "review",
                "approve",
                "reject",
                "apply",
                "revert",
                "list",
                "get",
            )

        # Architects: can propose and review, but not approve/apply/revert
        if archetype_lower in ("architect", "artist", "researcher", "technical"):
            return ("manifest", "propose", "review", "list", "get")

        # Newcomers/reviewers: read-only access
        if archetype_lower in ("newcomer", "casual", "reviewer", "security"):
            return ("manifest", "list", "get")

        # Guest (default): manifest only
        return ("manifest",)

    async def manifest(self, observer: "Observer | Umwelt[Any, Any]", **kwargs: Any) -> Renderable:
        """
        Manifest amendment system status to observer.

        AGENTESE: self.amendment.manifest
        """
        pending = self._service.list_pending()
        history = self._service.list_history(limit=1000)  # Get all for counts

        # Count by status
        drafts = sum(1 for a in pending if a.status == AmendmentStatus.DRAFT)
        proposed = sum(1 for a in pending if a.status == AmendmentStatus.PROPOSED)
        under_review = sum(1 for a in pending if a.status == AmendmentStatus.UNDER_REVIEW)
        approved = sum(1 for a in pending if a.status == AmendmentStatus.APPROVED)
        applied = sum(1 for a in history if a.status == AmendmentStatus.APPLIED)
        rejected = sum(1 for a in history if a.status == AmendmentStatus.REJECTED)
        reverted = sum(1 for a in history if a.status == AmendmentStatus.REVERTED)

        return AmendmentManifestRendering(
            total_pending=len(pending),
            total_history=len(history),
            drafts=drafts,
            proposed=proposed,
            under_review=under_review,
            approved=approved,
            applied=applied,
            rejected=rejected,
            reverted=reverted,
        )

    async def _invoke_aspect(
        self,
        aspect: str,
        observer: "Observer | Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> Any:
        """
        Route aspect invocations to service methods.

        Args:
            aspect: The aspect to invoke
            observer: The observer context
            **kwargs: Aspect-specific arguments
        """
        # Get proposer from observer
        proposer = self._get_proposer(observer)

        if aspect == "propose":
            return await self._handle_propose(proposer, **kwargs)
        elif aspect == "review":
            return await self._handle_review(proposer, **kwargs)
        elif aspect == "approve":
            return await self._handle_approve(**kwargs)
        elif aspect == "reject":
            return await self._handle_reject(**kwargs)
        elif aspect == "apply":
            return await self._handle_apply(**kwargs)
        elif aspect == "revert":
            return await self._handle_revert(**kwargs)
        elif aspect == "list":
            return await self._handle_list(**kwargs)
        elif aspect == "get":
            return await self._handle_get(**kwargs)
        else:
            return {"error": f"Unknown aspect: {aspect}"}

    def _get_proposer(self, observer: "Observer | Umwelt[Any, Any]") -> str:
        """Extract proposer identity from observer."""
        if isinstance(observer, Observer):
            return observer.archetype
        # For Umwelt, try to get agent name
        if hasattr(observer, "dna") and hasattr(observer.dna, "name"):
            name = observer.dna.name
            return str(name) if name else "unknown"
        return "unknown"

    async def _handle_propose(self, proposer: str, **kwargs: Any) -> dict[str, Any]:
        """Handle propose aspect."""
        title = kwargs.get("title", "")
        description = kwargs.get("description", "")
        amendment_type_str = kwargs.get("amendment_type", "")
        target_kblock = kwargs.get("target_kblock", "")
        target_layer = kwargs.get("target_layer", 2)
        proposed_content = kwargs.get("proposed_content", "")
        reasoning = kwargs.get("reasoning", "")
        principles_affected = kwargs.get("principles_affected", [])

        if not title or not target_kblock or not proposed_content:
            return {"error": "title, target_kblock, and proposed_content are required"}

        try:
            amendment_type = AmendmentType(amendment_type_str)
        except ValueError:
            return {
                "error": f"Invalid amendment_type: {amendment_type_str}. Valid values: {[t.value for t in AmendmentType]}"
            }

        # Create draft
        amendment = await self._service.create_draft(
            title=title,
            description=description,
            amendment_type=amendment_type,
            target_kblock=target_kblock,
            target_layer=target_layer,
            proposed_content=proposed_content,
            proposer=proposer,
            reasoning=reasoning,
            principles_affected=principles_affected,
        )

        # Immediately propose it
        amendment = await self._service.propose(amendment.id)

        return {
            "amendment_id": amendment.id,
            "title": amendment.title,
            "status": amendment.status.value,
            "diff": amendment.diff,
        }

    async def _handle_review(self, reviewer: str, **kwargs: Any) -> dict[str, Any]:
        """Handle review aspect."""
        amendment_id = kwargs.get("amendment_id", "")
        note = kwargs.get("note", "")

        if not amendment_id or not note:
            return {"error": "amendment_id and note are required"}

        try:
            amendment = await self._service.add_review_note(amendment_id, reviewer, note)
            return {
                "amendment_id": amendment.id,
                "review_count": len(amendment.review_notes),
            }
        except Exception as e:
            return {"error": str(e)}

    async def _handle_approve(self, **kwargs: Any) -> dict[str, Any]:
        """Handle approve aspect."""
        amendment_id = kwargs.get("amendment_id", "")
        reasoning = kwargs.get("reasoning", "")

        if not amendment_id or not reasoning:
            return {"error": "amendment_id and reasoning are required"}

        try:
            amendment = await self._service.approve(amendment_id, reasoning)
            return {
                "amendment_id": amendment.id,
                "title": amendment.title,
                "status": amendment.status.value,
                "target_kblock": amendment.target_kblock,
            }
        except Exception as e:
            return {"error": str(e)}

    async def _handle_reject(self, **kwargs: Any) -> dict[str, Any]:
        """Handle reject aspect."""
        amendment_id = kwargs.get("amendment_id", "")
        reasoning = kwargs.get("reasoning", "")

        if not amendment_id or not reasoning:
            return {"error": "amendment_id and reasoning are required"}

        try:
            amendment = await self._service.reject(amendment_id, reasoning)
            return {
                "amendment_id": amendment.id,
                "title": amendment.title,
                "status": amendment.status.value,
                "target_kblock": amendment.target_kblock,
            }
        except Exception as e:
            return {"error": str(e)}

    async def _handle_apply(self, **kwargs: Any) -> dict[str, Any]:
        """Handle apply aspect."""
        amendment_id = kwargs.get("amendment_id", "")

        if not amendment_id:
            return {"error": "amendment_id is required"}

        try:
            amendment = await self._service.apply(amendment_id)
            return {
                "amendment_id": amendment.id,
                "title": amendment.title,
                "status": amendment.status.value,
                "target_kblock": amendment.target_kblock,
                "diff": amendment.diff,
            }
        except Exception as e:
            return {"error": str(e)}

    async def _handle_revert(self, **kwargs: Any) -> dict[str, Any]:
        """Handle revert aspect."""
        amendment_id = kwargs.get("amendment_id", "")

        if not amendment_id:
            return {"error": "amendment_id is required"}

        try:
            amendment = await self._service.revert(amendment_id)
            return {
                "amendment_id": amendment.id,
                "title": amendment.title,
                "status": amendment.status.value,
                "target_kblock": amendment.target_kblock,
            }
        except Exception as e:
            return {"error": str(e)}

    async def _handle_list(self, **kwargs: Any) -> dict[str, Any]:
        """Handle list aspect."""
        scope = kwargs.get("scope", "pending")
        limit = kwargs.get("limit", 50)

        if scope == "pending":
            amendments = self._service.list_pending()
        elif scope == "history":
            amendments = self._service.list_history(limit=limit)
        else:  # "all"
            amendments = self._service.list_pending() + self._service.list_history(limit=limit)

        return {
            "amendments": [
                {
                    "id": a.id,
                    "title": a.title,
                    "status": a.status.value,
                    "amendment_type": a.amendment_type.value,
                    "target_kblock": a.target_kblock,
                    "proposer": a.proposer,
                    "created_at": a.created_at.isoformat(),
                }
                for a in amendments
            ]
        }

    async def _handle_get(self, **kwargs: Any) -> dict[str, Any]:
        """Handle get aspect."""
        amendment_id = kwargs.get("amendment_id", "")

        if not amendment_id:
            return {"error": "amendment_id is required"}

        amendment = self._service.get_amendment(amendment_id)
        if not amendment:
            return {"error": f"Amendment not found: {amendment_id}"}

        return amendment.to_dict()


# =============================================================================
# Module Exports
# =============================================================================

__all__ = [
    "AmendmentNode",
    "AmendmentManifestResponse",
    "ProposeRequest",
    "ProposeResponse",
    "ReviewRequest",
    "ReviewResponse",
    "ApproveRequest",
    "RejectRequest",
    "ApplyRevertRequest",
    "AmendmentResponse",
    "AmendmentListResponse",
    "ListRequest",
    "GetRequest",
]
