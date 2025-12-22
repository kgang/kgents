"""
Collaboration Protocol: Turn-taking and agent proposals.

Phase 4C: Agent Collaboration Layer.

Implements:
- Turn-taking: Agents wait when human is typing
- Keystroke detection: Track human activity
- Proposal acceptance: Auto-accept after timeout
- Edit guards: Prevent race conditions

Philosophy:
    "Human agency preserved. Critical decisions remain with humans."
    - Article IV: The Disgust Veto

The collaboration protocol ensures:
1. Agents never interrupt active human typing
2. Proposals have clear accept/reject/timeout semantics
3. Edit conflicts are prevented through guards

Teaching:
    gotcha: AUTO_ACCEPT_DELAY is 5 seconds. This is intentional -
            long enough to reject if needed, short enough to not
            block workflow. Don't change without user consent.
            (Evidence: test_collaboration.py::test_auto_accept_timing)

    gotcha: Keystroke detection has 2-second grace period.
            Even if human stops typing, agent waits 2 more seconds.
            This prevents "jumping in" during pauses.
            (Evidence: test_collaboration.py::test_typing_grace_period)

See: spec/protocols/context-perception.md §6
"""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum, auto
from typing import Any, Callable, Awaitable
from uuid import uuid4

logger = logging.getLogger(__name__)


# =============================================================================
# Constants
# =============================================================================

# Time to wait after last keystroke before agent can edit
TYPING_GRACE_PERIOD = timedelta(seconds=2)

# Time before proposal auto-accepts
AUTO_ACCEPT_DELAY = timedelta(seconds=5)

# Minimum time between proposals from same agent
PROPOSAL_COOLDOWN = timedelta(seconds=1)


# =============================================================================
# Turn-Taking Protocol
# =============================================================================


class TurnState(Enum):
    """Who currently has the turn."""

    HUMAN = auto()  # Human is actively typing
    AGENT = auto()  # Agent is working
    OPEN = auto()  # Neither - anyone can start


@dataclass
class KeystrokeTracker:
    """
    Tracks human typing activity.

    Used to determine when agents should wait vs. proceed.
    """

    last_keystroke: datetime | None = None
    typing_locations: dict[str, datetime] = field(default_factory=dict)
    _lock: asyncio.Lock = field(default_factory=asyncio.Lock)

    async def record_keystroke(self, location: str) -> None:
        """Record a keystroke at a location (file path or AGENTESE path)."""
        async with self._lock:
            now = datetime.now()
            self.last_keystroke = now
            self.typing_locations[location] = now

    async def is_human_typing(self, location: str | None = None) -> bool:
        """
        Check if human is currently typing.

        Args:
            location: Optional specific location to check.
                      If None, checks any location.

        Returns:
            True if human has typed within TYPING_GRACE_PERIOD
        """
        async with self._lock:
            if location:
                last = self.typing_locations.get(location)
            else:
                last = self.last_keystroke

            if last is None:
                return False

            return datetime.now() - last < TYPING_GRACE_PERIOD

    async def get_active_locations(self) -> list[str]:
        """Get locations where human is actively typing."""
        async with self._lock:
            now = datetime.now()
            return [
                loc
                for loc, ts in self.typing_locations.items()
                if now - ts < TYPING_GRACE_PERIOD
            ]

    async def clear_stale(self) -> int:
        """Clear stale typing records. Returns number cleared."""
        async with self._lock:
            now = datetime.now()
            stale = [
                loc
                for loc, ts in self.typing_locations.items()
                if now - ts > TYPING_GRACE_PERIOD * 2
            ]
            for loc in stale:
                del self.typing_locations[loc]
            return len(stale)


# =============================================================================
# Proposal System
# =============================================================================


class ProposalStatus(Enum):
    """Status of an agent proposal."""

    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    EXPIRED = "expired"  # Auto-accepted after timeout


@dataclass
class ProposedEdit:
    """
    An agent's proposed edit awaiting acceptance.

    Philosophy: Proposals give humans veto power while keeping flow.
    """

    id: str
    agent_id: str
    agent_name: str
    location: str  # File path or AGENTESE path
    original: str  # Original content
    proposed: str  # Proposed content
    description: str  # What this change does
    created_at: datetime = field(default_factory=datetime.now)
    status: ProposalStatus = ProposalStatus.PENDING
    resolved_at: datetime | None = None

    @property
    def auto_accept_at(self) -> datetime:
        """When this proposal will auto-accept."""
        return self.created_at + AUTO_ACCEPT_DELAY

    @property
    def time_remaining(self) -> timedelta:
        """Time remaining before auto-accept."""
        remaining = self.auto_accept_at - datetime.now()
        return max(remaining, timedelta(0))

    @property
    def should_auto_accept(self) -> bool:
        """Whether this proposal should auto-accept now."""
        return (
            self.status == ProposalStatus.PENDING
            and datetime.now() >= self.auto_accept_at
        )

    def accept(self) -> None:
        """Accept this proposal."""
        self.status = ProposalStatus.ACCEPTED
        self.resolved_at = datetime.now()

    def reject(self) -> None:
        """Reject this proposal."""
        self.status = ProposalStatus.REJECTED
        self.resolved_at = datetime.now()

    def expire(self) -> None:
        """Mark as expired (auto-accepted)."""
        self.status = ProposalStatus.EXPIRED
        self.resolved_at = datetime.now()

    def to_dict(self) -> dict[str, Any]:
        """Serialize for API/frontend."""
        return {
            "id": self.id,
            "agent_id": self.agent_id,
            "agent_name": self.agent_name,
            "location": self.location,
            "original": self.original,
            "proposed": self.proposed,
            "description": self.description,
            "created_at": self.created_at.isoformat(),
            "status": self.status.value,
            "resolved_at": self.resolved_at.isoformat() if self.resolved_at else None,
            "auto_accept_at": self.auto_accept_at.isoformat(),
            "time_remaining_ms": int(self.time_remaining.total_seconds() * 1000),
        }


# =============================================================================
# Collaboration Protocol
# =============================================================================


class CollaborationProtocol:
    """
    Orchestrates turn-taking and proposals between humans and agents.

    Usage:
        protocol = CollaborationProtocol()

        # Agent wants to edit
        if await protocol.agent_can_edit(agent_id, location):
            # Proceed with edit
            ...
        else:
            # Human is typing, wait or propose

        # Create proposal
        proposal = await protocol.propose_edit(
            agent_id="k-gent",
            agent_name="K-gent",
            location="/path/to/file.py",
            original=original_content,
            proposed=new_content,
            description="Add docstring",
        )

        # Check for auto-accepts
        expired = await protocol.process_auto_accepts()
    """

    def __init__(self) -> None:
        """Initialize collaboration protocol."""
        self._keystroke_tracker = KeystrokeTracker()
        self._proposals: dict[str, ProposedEdit] = {}
        self._agent_last_proposal: dict[str, datetime] = {}
        self._lock = asyncio.Lock()
        self._on_accept_callbacks: list[Callable[[ProposedEdit], Awaitable[None]]] = []
        self._on_reject_callbacks: list[Callable[[ProposedEdit], Awaitable[None]]] = []

    @property
    def keystroke_tracker(self) -> KeystrokeTracker:
        """Get the keystroke tracker."""
        return self._keystroke_tracker

    async def record_keystroke(self, location: str) -> None:
        """Record human keystroke at location."""
        await self._keystroke_tracker.record_keystroke(location)

    async def agent_can_edit(self, agent_id: str, location: str) -> bool:
        """
        Check if agent can proceed with edit.

        Returns False if:
        - Human is actively typing at location
        - Agent is on proposal cooldown
        """
        # Check if human is typing
        if await self._keystroke_tracker.is_human_typing(location):
            logger.debug(f"Agent {agent_id} waiting: human typing at {location}")
            return False

        return True

    async def propose_edit(
        self,
        agent_id: str,
        agent_name: str,
        location: str,
        original: str,
        proposed: str,
        description: str,
    ) -> ProposedEdit | None:
        """
        Create a new edit proposal.

        Returns None if agent is on cooldown.
        """
        async with self._lock:
            # Check cooldown
            last = self._agent_last_proposal.get(agent_id)
            if last and datetime.now() - last < PROPOSAL_COOLDOWN:
                logger.debug(f"Agent {agent_id} on proposal cooldown")
                return None

            # Create proposal
            proposal = ProposedEdit(
                id=str(uuid4()),
                agent_id=agent_id,
                agent_name=agent_name,
                location=location,
                original=original,
                proposed=proposed,
                description=description,
            )

            self._proposals[proposal.id] = proposal
            self._agent_last_proposal[agent_id] = datetime.now()

            logger.info(
                f"Proposal created: {proposal.id} by {agent_name} for {location}"
            )
            return proposal

    async def accept_proposal(self, proposal_id: str) -> ProposedEdit | None:
        """
        Accept a proposal.

        Returns the proposal if found and pending, None otherwise.
        """
        async with self._lock:
            proposal = self._proposals.get(proposal_id)
            if proposal is None or proposal.status != ProposalStatus.PENDING:
                return None

            proposal.accept()

        # Fire callbacks outside lock
        for callback in self._on_accept_callbacks:
            try:
                await callback(proposal)
            except Exception as e:
                logger.error(f"Accept callback error: {e}")

        logger.info(f"Proposal accepted: {proposal_id}")
        return proposal

    async def reject_proposal(self, proposal_id: str) -> ProposedEdit | None:
        """
        Reject a proposal.

        Returns the proposal if found and pending, None otherwise.
        """
        async with self._lock:
            proposal = self._proposals.get(proposal_id)
            if proposal is None or proposal.status != ProposalStatus.PENDING:
                return None

            proposal.reject()

        # Fire callbacks outside lock
        for callback in self._on_reject_callbacks:
            try:
                await callback(proposal)
            except Exception as e:
                logger.error(f"Reject callback error: {e}")

        logger.info(f"Proposal rejected: {proposal_id}")
        return proposal

    async def process_auto_accepts(self) -> list[ProposedEdit]:
        """
        Process proposals that should auto-accept.

        Returns list of proposals that were auto-accepted.
        """
        expired: list[ProposedEdit] = []

        async with self._lock:
            for proposal in list(self._proposals.values()):
                if proposal.should_auto_accept:
                    proposal.expire()
                    expired.append(proposal)

        # Fire callbacks outside lock
        for proposal in expired:
            for callback in self._on_accept_callbacks:
                try:
                    await callback(proposal)
                except Exception as e:
                    logger.error(f"Auto-accept callback error: {e}")

        if expired:
            logger.info(f"Auto-accepted {len(expired)} proposals")

        return expired

    async def get_pending_proposals(
        self, location: str | None = None
    ) -> list[ProposedEdit]:
        """Get all pending proposals, optionally filtered by location."""
        async with self._lock:
            proposals = [
                p for p in self._proposals.values() if p.status == ProposalStatus.PENDING
            ]
            if location:
                proposals = [p for p in proposals if p.location == location]
            return proposals

    async def get_proposal(self, proposal_id: str) -> ProposedEdit | None:
        """Get a specific proposal by ID."""
        return self._proposals.get(proposal_id)

    def on_accept(
        self, callback: Callable[[ProposedEdit], Awaitable[None]]
    ) -> Callable[[], None]:
        """
        Register callback for proposal acceptance.

        Returns unsubscribe function.
        """
        self._on_accept_callbacks.append(callback)
        return lambda: self._on_accept_callbacks.remove(callback)

    def on_reject(
        self, callback: Callable[[ProposedEdit], Awaitable[None]]
    ) -> Callable[[], None]:
        """
        Register callback for proposal rejection.

        Returns unsubscribe function.
        """
        self._on_reject_callbacks.append(callback)
        return lambda: self._on_reject_callbacks.remove(callback)

    async def cleanup_old_proposals(self, max_age: timedelta | None = None) -> int:
        """
        Remove old resolved proposals.

        Args:
            max_age: Maximum age of resolved proposals to keep.
                    Default: 1 hour

        Returns:
            Number of proposals removed
        """
        if max_age is None:
            max_age = timedelta(hours=1)

        async with self._lock:
            now = datetime.now()
            old = [
                pid
                for pid, p in self._proposals.items()
                if p.status != ProposalStatus.PENDING
                and p.resolved_at
                and now - p.resolved_at > max_age
            ]
            for pid in old:
                del self._proposals[pid]

            # Also clean stale keystrokes
            await self._keystroke_tracker.clear_stale()

            return len(old)


# =============================================================================
# Singleton
# =============================================================================

_protocol: CollaborationProtocol | None = None


def get_collaboration_protocol() -> CollaborationProtocol:
    """Get or create the singleton CollaborationProtocol."""
    global _protocol
    if _protocol is None:
        _protocol = CollaborationProtocol()
    return _protocol


def reset_collaboration_protocol() -> None:
    """Reset the singleton (for testing)."""
    global _protocol
    _protocol = None


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    # Constants
    "TYPING_GRACE_PERIOD",
    "AUTO_ACCEPT_DELAY",
    "PROPOSAL_COOLDOWN",
    # Enums
    "TurnState",
    "ProposalStatus",
    # Data classes
    "KeystrokeTracker",
    "ProposedEdit",
    # Protocol
    "CollaborationProtocol",
    "get_collaboration_protocol",
    "reset_collaboration_protocol",
]
