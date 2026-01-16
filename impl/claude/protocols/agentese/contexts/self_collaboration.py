"""
AGENTESE Self Collaboration Context: Human-Agent Turn-Taking

Phase 5C: Collaborative Editing

The self.collaboration context enables human-agent collaboration:
- self.collaboration.manifest - View collaboration status
- self.collaboration.propose - Agent proposes an edit
- self.collaboration.respond - Human accepts/rejects proposal
- self.collaboration.keystroke - Record human keystroke
- self.collaboration.pending - Get pending proposals
- self.collaboration.status - Get turn-taking status
- self.collaboration.stream - SSE stream of proposals

Philosophy:
    "Human agency preserved. Critical decisions remain with humans."
    - Article IV: The Disgust Veto

Key Timing:
    - TYPING_GRACE_PERIOD: 2 seconds - agent waits after last keystroke
    - AUTO_ACCEPT_DELAY: 5 seconds - proposal auto-accepts after timeout
    - PROPOSAL_COOLDOWN: 1 second - between proposals from same agent

Teaching:
    gotcha: AUTO_ACCEPT_DELAY is 5 seconds by design. Long enough to reject,
            short enough to not block workflow. Don't change without consent.
            (Evidence: test_collaboration.py::test_auto_accept_timing)

    gotcha: Keystroke detection has 2-second grace period. Even if human
            stops typing, agent waits 2 more seconds to prevent "jumping in".
            (Evidence: test_collaboration.py::test_typing_grace_period)

AGENTESE: self.collaboration.*

See: spec/protocols/context-perception.md §6
"""

from __future__ import annotations

import asyncio
import json
import logging
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import TYPE_CHECKING, Any, AsyncGenerator

# Import from context protocol
from protocols.context.collaboration import (
    AUTO_ACCEPT_DELAY,
    PROPOSAL_COOLDOWN,
    TYPING_GRACE_PERIOD,
    CollaborationProtocol,
    ProposalStatus,
    ProposedEdit,
    TurnState,
    get_collaboration_protocol,
)

from ..affordances import AspectCategory, Effect, aspect
from ..contract import Contract
from ..node import BaseLogosNode, BasicRendering, Renderable
from ..registry import node

if TYPE_CHECKING:
    from bootstrap.umwelt import Umwelt

    Observer = Umwelt[Any, Any]

logger = logging.getLogger(__name__)

# Collaboration-specific affordances (beyond base affordances from BaseLogosNode)
# Note: Do NOT include "manifest" here - it's already in _base_affordances
COLLABORATION_AFFORDANCES: tuple[str, ...] = (
    "propose",
    "respond",
    "keystroke",
    "pending",
    "status",
    "stream",
)


# =============================================================================
# Contracts
# =============================================================================


@dataclass(frozen=True)
class CollaborationManifestResponse:
    """Response for manifest aspect."""

    status: str
    pending_count: int
    auto_accept_delay_ms: int
    typing_grace_period_ms: int
    proposal_cooldown_ms: int
    features: list[str]


@dataclass(frozen=True)
class ProposeRequest:
    """Request to create a new edit proposal."""

    agent_id: str
    agent_name: str
    location: str  # File path or AGENTESE path
    original: str
    proposed: str
    description: str


@dataclass(frozen=True)
class ProposeResponse:
    """Response for propose aspect."""

    success: bool
    proposal_id: str | None
    error: str | None
    auto_accept_at: str | None
    time_remaining_ms: int


@dataclass(frozen=True)
class RespondRequest:
    """Request to accept/reject a proposal."""

    proposal_id: str
    action: str  # "accept" or "reject"


@dataclass(frozen=True)
class RespondResponse:
    """Response for respond aspect."""

    success: bool
    proposal_id: str
    action: str
    status: str
    error: str | None


@dataclass(frozen=True)
class KeystrokeRequest:
    """Request to record a human keystroke."""

    location: str


@dataclass(frozen=True)
class KeystrokeResponse:
    """Response for keystroke aspect."""

    recorded: bool
    location: str
    timestamp: str


@dataclass(frozen=True)
class PendingResponse:
    """Response for pending aspect."""

    proposals: list[dict[str, Any]]
    count: int


@dataclass(frozen=True)
class StatusResponse:
    """Response for status aspect."""

    turn_state: str
    is_human_typing: bool
    active_typing_locations: list[str]
    pending_proposal_count: int


# =============================================================================
# Node Implementation
# =============================================================================


@node("self.collaboration")
class CollaborationNode(BaseLogosNode):
    """
    AGENTESE node for human-agent collaboration.

    Exposes the CollaborationProtocol via AGENTESE for:
    - Proposal creation and acceptance
    - Keystroke tracking
    - Turn-taking status
    """

    _handle: str = "self.collaboration"

    def __init__(self) -> None:
        """Initialize collaboration node."""
        super().__init__()
        self._protocol = get_collaboration_protocol()

    @property
    def handle(self) -> str:
        """AGENTESE path to this node."""
        return self._handle

    @property
    def description(self) -> str:
        """Node description."""
        return "Human-agent collaborative editing with turn-taking"

    def _get_affordances_for_archetype(self, archetype: str) -> tuple[str, ...]:
        """Return affordances (same for all archetypes).

        Note: We don't override the `affordances` property here!
        BaseLogosNode.affordances() is a METHOD that combines
        _base_affordances with this archetype-specific tuple.
        Overriding it as a @property would shadow the method.

        Teaching:
            gotcha: Never override BaseLogosNode.affordances() as a property!
                    It's a method expecting (self, observer: AgentMeta) -> list[str].
                    Shadowing it with @property causes 'tuple not callable' error.
                    (Evidence: test_self_collaboration.py::test_affordances_returns_list)
        """
        return COLLABORATION_AFFORDANCES

    async def _invoke_aspect(
        self,
        aspect: str,
        observer: "Observer",
        **kwargs: Any,
    ) -> Any:
        """Invoke an aspect method by name.

        Returns:
            Renderable for most aspects, AsyncGenerator for stream aspect.

        Teaching:
            gotcha: Async generator methods (like `stream`) must NOT be awaited.
                    Calling them returns the generator directly. Awaiting fails with:
                    "object async_generator can't be used in 'await' expression"
                    (Evidence: test_collaboration.py::test_stream_aspect_returns_generator)
        """
        method = getattr(self, aspect, None)
        if method is not None:
            # For stream aspect, return the generator directly (don't await)
            # Async generator functions return a generator when called, not awaited
            if aspect == "stream":
                return method(observer, **kwargs)
            return await method(observer, **kwargs)
        raise ValueError(f"Unknown aspect: {aspect}")

    # =========================================================================
    # Manifest
    # =========================================================================

    @aspect(
        category=AspectCategory.PERCEPTION,
        description="View collaboration status and configuration",
    )
    async def manifest(self, observer: "Observer", **kwargs: Any) -> Renderable:
        """Get collaboration manifest."""
        pending = await self._protocol.get_pending_proposals()

        response = CollaborationManifestResponse(
            status="active",
            pending_count=len(pending),
            auto_accept_delay_ms=int(AUTO_ACCEPT_DELAY.total_seconds() * 1000),
            typing_grace_period_ms=int(TYPING_GRACE_PERIOD.total_seconds() * 1000),
            proposal_cooldown_ms=int(PROPOSAL_COOLDOWN.total_seconds() * 1000),
            features=[
                "keystroke_tracking",
                "proposal_auto_accept",
                "turn_taking",
                "sse_streaming",
            ],
        )

        return BasicRendering(
            summary="Collaboration Protocol Active",
            content=f"Pending proposals: {len(pending)}",
            metadata={
                "status": response.status,
                "pending_count": response.pending_count,
                "auto_accept_delay_ms": response.auto_accept_delay_ms,
                "typing_grace_period_ms": response.typing_grace_period_ms,
                "proposal_cooldown_ms": response.proposal_cooldown_ms,
                "features": response.features,
            },
        )

    # =========================================================================
    # Propose
    # =========================================================================

    @aspect(
        category=AspectCategory.MUTATION,
        description="Agent proposes an edit for human approval",
        effects=[Effect.WRITES],
    )
    async def propose(self, observer: "Observer", **kwargs: Any) -> Renderable:
        """Create a new edit proposal."""
        # Extract request params
        agent_id = kwargs.get("agent_id", "unknown-agent")
        agent_name = kwargs.get("agent_name", "Unknown Agent")
        location = kwargs.get("location", "")
        original = kwargs.get("original", "")
        proposed = kwargs.get("proposed", "")
        description = kwargs.get("description", "")

        # Validate required fields
        if not location:
            return BasicRendering(
                summary="Proposal Failed",
                content="Location is required",
                metadata=ProposeResponse(
                    success=False,
                    proposal_id=None,
                    error="location is required",
                    auto_accept_at=None,
                    time_remaining_ms=0,
                ).__dict__,
            )

        # Check if agent can edit
        can_edit = await self._protocol.agent_can_edit(agent_id, location)
        if not can_edit:
            return BasicRendering(
                summary="Proposal Blocked",
                content="Human is currently typing at this location",
                metadata=ProposeResponse(
                    success=False,
                    proposal_id=None,
                    error="human_typing",
                    auto_accept_at=None,
                    time_remaining_ms=0,
                ).__dict__,
            )

        # Create proposal
        proposal = await self._protocol.propose_edit(
            agent_id=agent_id,
            agent_name=agent_name,
            location=location,
            original=original,
            proposed=proposed,
            description=description,
        )

        if proposal is None:
            return BasicRendering(
                summary="Proposal Cooldown",
                content="Agent is on proposal cooldown",
                metadata=ProposeResponse(
                    success=False,
                    proposal_id=None,
                    error="cooldown",
                    auto_accept_at=None,
                    time_remaining_ms=0,
                ).__dict__,
            )

        return BasicRendering(
            summary=f"Proposal Created: {proposal.id[:8]}...",
            content=f"{agent_name} proposes: {description}",
            metadata=ProposeResponse(
                success=True,
                proposal_id=proposal.id,
                error=None,
                auto_accept_at=proposal.auto_accept_at.isoformat(),
                time_remaining_ms=int(proposal.time_remaining.total_seconds() * 1000),
            ).__dict__,
        )

    # =========================================================================
    # Respond
    # =========================================================================

    @aspect(
        category=AspectCategory.MUTATION,
        description="Human accepts or rejects a proposal",
        effects=[Effect.WRITES],
    )
    async def respond(self, observer: "Observer", **kwargs: Any) -> Renderable:
        """Accept or reject a proposal."""
        proposal_id = kwargs.get("proposal_id", "")
        action = kwargs.get("action", "").lower()

        if not proposal_id:
            return BasicRendering(
                summary="Response Failed",
                content="proposal_id is required",
                metadata=RespondResponse(
                    success=False,
                    proposal_id="",
                    action=action,
                    status="error",
                    error="proposal_id is required",
                ).__dict__,
            )

        if action not in ("accept", "reject"):
            return BasicRendering(
                summary="Response Failed",
                content="action must be 'accept' or 'reject'",
                metadata=RespondResponse(
                    success=False,
                    proposal_id=proposal_id,
                    action=action,
                    status="error",
                    error="action must be 'accept' or 'reject'",
                ).__dict__,
            )

        # Perform action
        if action == "accept":
            proposal = await self._protocol.accept_proposal(proposal_id)
        else:
            proposal = await self._protocol.reject_proposal(proposal_id)

        if proposal is None:
            return BasicRendering(
                summary="Proposal Not Found",
                content=f"Proposal {proposal_id[:8]}... not found or already resolved",
                metadata=RespondResponse(
                    success=False,
                    proposal_id=proposal_id,
                    action=action,
                    status="not_found",
                    error="Proposal not found or already resolved",
                ).__dict__,
            )

        return BasicRendering(
            summary=f"Proposal {action.title()}ed",
            content=f"Proposal {proposal_id[:8]}... has been {action}ed",
            metadata=RespondResponse(
                success=True,
                proposal_id=proposal_id,
                action=action,
                status=proposal.status.value,
                error=None,
            ).__dict__,
        )

    # =========================================================================
    # Keystroke
    # =========================================================================

    @aspect(
        category=AspectCategory.MUTATION,
        description="Record human keystroke to block agent edits",
        effects=[Effect.WRITES],
    )
    async def keystroke(self, observer: "Observer", **kwargs: Any) -> Renderable:
        """Record a human keystroke."""
        location = kwargs.get("location", "")

        if not location:
            return BasicRendering(
                summary="Keystroke Failed",
                content="location is required",
                metadata=KeystrokeResponse(
                    recorded=False,
                    location="",
                    timestamp=datetime.now().isoformat(),
                ).__dict__,
            )

        await self._protocol.record_keystroke(location)

        return BasicRendering(
            summary="Keystroke Recorded",
            content=f"Human activity at {location}",
            metadata=KeystrokeResponse(
                recorded=True,
                location=location,
                timestamp=datetime.now().isoformat(),
            ).__dict__,
        )

    # =========================================================================
    # Pending
    # =========================================================================

    @aspect(
        category=AspectCategory.PERCEPTION,
        description="Get all pending proposals",
    )
    async def pending(self, observer: "Observer", **kwargs: Any) -> Renderable:
        """Get pending proposals."""
        location = kwargs.get("location")  # Optional filter
        proposals = await self._protocol.get_pending_proposals(location)

        # Process auto-accepts first
        expired = await self._protocol.process_auto_accepts()
        if expired:
            # Re-fetch after processing
            proposals = await self._protocol.get_pending_proposals(location)

        proposal_dicts = [p.to_dict() for p in proposals]

        return BasicRendering(
            summary=f"{len(proposals)} Pending Proposal(s)",
            content="\n".join(f"- {p.agent_name}: {p.description}" for p in proposals)
            if proposals
            else "No pending proposals",
            metadata=PendingResponse(
                proposals=proposal_dicts,
                count=len(proposals),
            ).__dict__,
        )

    # =========================================================================
    # Status
    # =========================================================================

    @aspect(
        category=AspectCategory.PERCEPTION,
        description="Get current collaboration status",
    )
    async def status(self, observer: "Observer", **kwargs: Any) -> Renderable:
        """Get collaboration status."""
        tracker = self._protocol.keystroke_tracker
        is_typing = await tracker.is_human_typing()
        active_locations = await tracker.get_active_locations()
        pending = await self._protocol.get_pending_proposals()

        # Determine turn state
        if is_typing:
            turn_state = "human"
        elif pending:
            turn_state = "agent"
        else:
            turn_state = "open"

        return BasicRendering(
            summary=f"Turn: {turn_state.title()}",
            content=f"Human typing: {is_typing}, Pending: {len(pending)}",
            metadata=StatusResponse(
                turn_state=turn_state,
                is_human_typing=is_typing,
                active_typing_locations=active_locations,
                pending_proposal_count=len(pending),
            ).__dict__,
        )

    # =========================================================================
    # Stream (SSE)
    # =========================================================================

    @aspect(
        category=AspectCategory.PERCEPTION,
        description="SSE stream of collaboration events",
        streaming=True,
    )
    async def stream(
        self, observer: "Observer", **kwargs: Any
    ) -> AsyncGenerator[dict[str, Any], None]:
        """Stream collaboration events via SSE.

        Yields raw dictionaries - the gateway's _generate_sse() handles formatting.

        Teaching:
            gotcha: Don't pre-format SSE data! The gateway wraps async generator
                    output with `data: {json}\n\n`. Pre-formatting causes double-wrap.
                    (Evidence: curl shows `data: "data: {...}"` if you format here)
        """
        # Send initial status
        # Cast to BasicRendering for metadata access (we know the concrete type)
        status_result = await self.status(observer)
        status_meta = getattr(status_result, "metadata", {})
        yield {"type": "status", "data": status_meta}

        # Send pending proposals
        pending_result = await self.pending(observer)
        pending_meta = getattr(pending_result, "metadata", {})
        yield {"type": "pending", "data": pending_meta}

        # Set up callback for new proposals
        proposal_queue: asyncio.Queue[ProposedEdit] = asyncio.Queue()

        async def on_proposal_change(proposal: ProposedEdit) -> None:
            await proposal_queue.put(proposal)

        # Register callbacks
        unsub_accept = self._protocol.on_accept(on_proposal_change)
        unsub_reject = self._protocol.on_reject(on_proposal_change)

        try:
            while True:
                # Check for new proposals (with timeout for heartbeat)
                try:
                    proposal = await asyncio.wait_for(proposal_queue.get(), timeout=5.0)
                    yield {"type": "proposal_update", "data": proposal.to_dict()}
                except asyncio.TimeoutError:
                    # Send heartbeat
                    yield {"type": "heartbeat", "timestamp": datetime.now().isoformat()}

                # Process auto-accepts
                expired = await self._protocol.process_auto_accepts()
                for p in expired:
                    yield {"type": "auto_accept", "data": p.to_dict()}

        finally:
            unsub_accept()
            unsub_reject()
