"""
Atelier Bidding Service: BidQueue wrapper for spectator constraint injection.

Wraps agents/atelier/bidding.py BidQueue with service-level interface.
Owns domain semantics for Atelier bidding:
- WHEN to accept bids (active workshops, rate limits)
- WHY to bid (influence creation through constraints)
- HOW to process outcomes (accept/acknowledge/reject with refunds)

AGENTESE aspects exposed:
- world.atelier.bid.submit - Submit a spectator bid
- world.atelier.bid.status - Get bid status
- world.atelier.bid.leaderboard - Get spectator leaderboard

The Categorical View:
    Bid : Spectator x Tokens -> Constraint
    BidQueue : PriorityQueue[Bid] -> Perturbation[Constraint]

See: docs/skills/metaphysical-fullstack.md
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from agents.atelier.bidding import (
    BID_COSTS,
    BID_PRIORITIES,
    Bid,
    BidOutcome,
    BidQueue,
    BidResult,
    BidType,
    SpectatorStats,
)

if TYPE_CHECKING:
    from agents.atelier.economy import TokenPool


@dataclass
class BidView:
    """View of a single bid."""

    id: str
    spectator_id: str
    session_id: str
    bid_type: str
    content: str
    tokens_spent: int
    priority: int
    outcome: str | None
    timestamp: float

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "spectator_id": self.spectator_id,
            "session_id": self.session_id,
            "bid_type": self.bid_type,
            "content": self.content[:100] + ("..." if len(self.content) > 100 else ""),
            "tokens_spent": self.tokens_spent,
            "priority": self.priority,
            "outcome": self.outcome,
            "timestamp": self.timestamp,
        }

    def to_text(self) -> str:
        outcome_str = f" [{self.outcome}]" if self.outcome else ""
        return (
            f"Bid {self.id}{outcome_str}: {self.bid_type} by {self.spectator_id} "
            f"({self.tokens_spent} tokens)"
        )


@dataclass
class SpectatorStatsView:
    """View of spectator statistics."""

    spectator_id: str
    session_id: str
    tokens_spent: int
    bids_submitted: int
    bids_accepted: int
    bids_acknowledged: int
    influence_score: float

    def to_dict(self) -> dict[str, Any]:
        return {
            "spectator_id": self.spectator_id,
            "session_id": self.session_id,
            "tokens_spent": self.tokens_spent,
            "bids_submitted": self.bids_submitted,
            "bids_accepted": self.bids_accepted,
            "bids_acknowledged": self.bids_acknowledged,
            "influence_score": round(self.influence_score, 2),
        }

    def to_text(self) -> str:
        acceptance = (
            f"{self.bids_accepted}/{self.bids_submitted}"
            if self.bids_submitted > 0
            else "0/0"
        )
        return (
            f"{self.spectator_id}: {self.tokens_spent} tokens, "
            f"{acceptance} accepted, score {self.influence_score:.1f}"
        )


@dataclass
class QueueStatusView:
    """View of bid queue status."""

    session_id: str
    queue_size: int
    total_bids_received: int
    total_tokens_collected: int
    spectator_count: int
    pending_bids: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "session_id": self.session_id,
            "queue_size": self.queue_size,
            "total_bids_received": self.total_bids_received,
            "total_tokens_collected": self.total_tokens_collected,
            "spectator_count": self.spectator_count,
            "pending_bids": self.pending_bids,
        }

    def to_text(self) -> str:
        return (
            f"Queue {self.session_id}: {self.queue_size} pending, "
            f"{self.total_bids_received} total, {self.spectator_count} spectators"
        )


class AtelierBiddingService:
    """
    Service layer for Atelier spectator bidding.

    Wraps BidQueue with service-level methods for:
    - Bid submission with validation
    - Queue management
    - Outcome recording
    - Leaderboard queries

    Usage:
        service = AtelierBiddingService.create("session-123")

        # Submit a bid
        result = await service.submit_bid(
            spectator_id="alice",
            bid_type="inject_constraint",
            content="Add more contrast",
        )

        # Get next bid for builder
        bid = await service.dequeue()

        # Record outcome
        service.record_outcome(bid.id, "accepted")
    """

    def __init__(
        self,
        queue: BidQueue,
    ) -> None:
        """
        Initialize with a BidQueue.

        Args:
            queue: The underlying bid queue
        """
        self._queue = queue

    @classmethod
    def create(
        cls,
        session_id: str,
        token_pool: "TokenPool | None" = None,
        builder_id: str | None = None,
        max_queue_size: int = 100,
    ) -> "AtelierBiddingService":
        """
        Factory method to create a new bidding service.

        Args:
            session_id: Atelier session this queue belongs to
            token_pool: Optional TokenPool for token deduction
            builder_id: ID of the builder (for tracking earnings)
            max_queue_size: Maximum bids in queue

        Returns:
            New AtelierBiddingService instance
        """
        queue = BidQueue(
            session_id=session_id,
            token_pool=token_pool,
            builder_id=builder_id,
            max_queue_size=max_queue_size,
        )
        return cls(queue)

    @property
    def session_id(self) -> str:
        """Get the session ID this queue belongs to."""
        return self._queue.session_id

    # === Bid Submission ===

    async def submit_bid(
        self,
        spectator_id: str,
        bid_type: str | BidType,
        content: str,
        metadata: dict[str, Any] | None = None,
    ) -> BidResult:
        """
        Submit a new bid to the queue.

        Args:
            spectator_id: ID of spectator submitting
            bid_type: Type of bid (string or BidType enum)
            content: Bid content
            metadata: Optional additional data

        Returns:
            BidResult with success status and bid details
        """
        # Parse bid type
        if isinstance(bid_type, str):
            try:
                bt = BidType[bid_type.upper()]
            except KeyError:
                return BidResult(
                    bid=Bid.create(
                        spectator_id, self._queue.session_id, BidType.BOOST_BUILDER, ""
                    ),
                    success=False,
                    outcome=BidOutcome.REJECTED,
                    message=f"Invalid bid type: {bid_type}",
                )
        else:
            bt = bid_type

        return await self._queue.submit(
            spectator_id=spectator_id,
            bid_type=bt,
            content=content,
            metadata=metadata,
        )

    # === Queue Operations ===

    async def dequeue(
        self,
        timeout: float | None = None,
    ) -> Bid | None:
        """
        Dequeue the highest priority bid for builder consideration.

        Args:
            timeout: Optional timeout in seconds

        Returns:
            Highest priority bid, or None if queue is empty/timeout
        """
        return await self._queue.dequeue(timeout=timeout)

    async def peek(self) -> Bid | None:
        """
        Peek at highest priority bid without removing.

        Returns:
            Highest priority bid, or None if queue is empty
        """
        return await self._queue.peek()

    @property
    def queue_size(self) -> int:
        """Current number of bids in queue."""
        return self._queue.queue_size

    @property
    def is_empty(self) -> bool:
        """Check if queue is empty."""
        return self._queue.is_empty

    # === Outcome Recording ===

    def record_outcome(
        self,
        bid_id: str,
        outcome: str | BidOutcome,
    ) -> int:
        """
        Record the outcome of a bid.

        Args:
            bid_id: ID of the bid
            outcome: What happened (string or BidOutcome enum)

        Returns:
            Tokens refunded to spectator (if any)
        """
        # Parse outcome
        if isinstance(outcome, str):
            try:
                bo = BidOutcome[outcome.upper()]
            except KeyError:
                return 0
        else:
            bo = outcome

        return self._queue.record_outcome(bid_id, bo)

    # === Query Operations ===

    def get_bid(self, bid_id: str) -> BidView | None:
        """
        Get a bid by ID.

        Args:
            bid_id: ID of the bid

        Returns:
            BidView or None if not found
        """
        bid = self._queue.get_bid(bid_id)
        if bid is None:
            return None

        outcome = self._queue.get_outcome(bid_id)

        return BidView(
            id=bid.id,
            spectator_id=bid.spectator_id,
            session_id=bid.session_id,
            bid_type=bid.bid_type.name,
            content=bid.content,
            tokens_spent=bid.tokens_spent,
            priority=bid.priority,
            outcome=outcome.name if outcome else None,
            timestamp=bid.timestamp,
        )

    def get_spectator_stats(
        self,
        spectator_id: str,
    ) -> SpectatorStatsView | None:
        """
        Get stats for a spectator.

        Args:
            spectator_id: ID of the spectator

        Returns:
            SpectatorStatsView or None if not found
        """
        stats = self._queue.get_spectator_stats(spectator_id)
        if stats is None:
            return None

        return SpectatorStatsView(
            spectator_id=stats.spectator_id,
            session_id=stats.session_id,
            tokens_spent=stats.tokens_spent,
            bids_submitted=stats.bids_submitted,
            bids_accepted=stats.bids_accepted,
            bids_acknowledged=stats.bids_acknowledged,
            influence_score=stats.influence_score,
        )

    def get_leaderboard(
        self,
        limit: int = 10,
    ) -> list[SpectatorStatsView]:
        """
        Get top spectators by influence score.

        Args:
            limit: Maximum number of entries

        Returns:
            List of SpectatorStatsView sorted by influence
        """
        stats_list = self._queue.get_leaderboard(limit=limit)
        return [
            SpectatorStatsView(
                spectator_id=s.spectator_id,
                session_id=s.session_id,
                tokens_spent=s.tokens_spent,
                bids_submitted=s.bids_submitted,
                bids_accepted=s.bids_accepted,
                bids_acknowledged=s.bids_acknowledged,
                influence_score=s.influence_score,
            )
            for s in stats_list
        ]

    def status(self) -> QueueStatusView:
        """
        Get queue status.

        Returns:
            QueueStatusView with queue statistics
        """
        data = self._queue.status()
        return QueueStatusView(
            session_id=data["session_id"],
            queue_size=data["queue_size"],
            total_bids_received=data["total_bids_received"],
            total_tokens_collected=data["total_tokens_collected"],
            spectator_count=data["spectator_count"],
            pending_bids=data["pending_bids"],
        )

    # === Flux Integration ===

    def to_perturbation(self, bid: Bid) -> Any:
        """
        Convert a bid to a Flux Perturbation for stream injection.

        Args:
            bid: The bid to convert

        Returns:
            Perturbation ready for Flux injection
        """
        return self._queue.to_perturbation(bid)

    @property
    def queue(self) -> BidQueue:
        """Access the underlying bid queue."""
        return self._queue


# === Bid Costs Helper ===


def get_bid_cost(bid_type: str | BidType) -> int:
    """
    Get the token cost for a bid type.

    Args:
        bid_type: Type of bid (string or enum)

    Returns:
        Token cost
    """
    if isinstance(bid_type, str):
        bt = BidType[bid_type.upper()]
    else:
        bt = bid_type
    return BID_COSTS[bt]


def get_bid_priority(bid_type: str | BidType) -> int:
    """
    Get the priority for a bid type.

    Args:
        bid_type: Type of bid (string or enum)

    Returns:
        Priority level (higher = processed first)
    """
    if isinstance(bid_type, str):
        bt = BidType[bid_type.upper()]
    else:
        bt = bid_type
    return BID_PRIORITIES[bt]


__all__ = [
    "AtelierBiddingService",
    "BidView",
    "SpectatorStatsView",
    "QueueStatusView",
    "get_bid_cost",
    "get_bid_priority",
]
