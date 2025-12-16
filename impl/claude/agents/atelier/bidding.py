"""
Atelier Bidding: Spectator economy for constraint injection.

The spectator economy allows viewers to influence creation through tokens:
- BidQueue: Priority queue with costs (inject=10, direction=5, boost=3)
- SpectatorStats: Track individual spectator contributions
- Wire to Flux via Perturbation API for stream injection

From the plan:
    "Spectators bid on directions" — tokens → influence
    "Constraint injection" — bids become perturbations in the creative flux

The Categorical View:
    Bid : Spectator × Tokens → Constraint
    BidQueue : PriorityQueue[Bid] → Perturbation[Constraint]

    This is a coalgebraic structure where spectator state
    (token balance, bid history) unfolds through observations.

Hardening (Spike 1B+):
    - Input validation (content length, rate limiting)
    - TokenPool integration for actual token deduction
    - OTEL instrumentation for observability
    - Builder acknowledgment flow (accept/acknowledge/ignore)
    - Bonus tokens for accepted bids (1.5x per plan)
"""

from __future__ import annotations

import asyncio
import heapq
import logging
import re
import time
from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from enum import Enum, auto
from typing import TYPE_CHECKING, Any
from uuid import uuid4

if TYPE_CHECKING:
    from agents.atelier.economy import TokenPool
    from agents.flux.perturbation import Perturbation

logger = logging.getLogger(__name__)

# =============================================================================
# Validation Constants (Hardening)
# =============================================================================

# Content limits
MAX_BID_CONTENT_LENGTH = 500  # Max characters for bid content
MIN_BID_CONTENT_LENGTH = 3  # Min meaningful content
MAX_METADATA_SIZE = 1024  # Max bytes for metadata JSON

# Rate limiting
MAX_BIDS_PER_MINUTE = 10  # Per spectator
RATE_LIMIT_WINDOW_SECONDS = 60

# Bonus multipliers (from plan: 1.5x refund if accepted)
ACCEPTED_BID_BONUS_MULTIPLIER = Decimal("1.5")

# Sanitization patterns
PROHIBITED_PATTERNS = [
    r"<script",  # XSS
    r"javascript:",  # XSS
    r"on\w+\s*=",  # Event handlers
]


# =============================================================================
# Validation Errors
# =============================================================================


class BidValidationError(Exception):
    """Raised when bid validation fails."""

    def __init__(self, message: str, code: str) -> None:
        super().__init__(message)
        self.code = code


class RateLimitError(BidValidationError):
    """Raised when spectator exceeds rate limit."""

    def __init__(self, spectator_id: str, limit: int) -> None:
        super().__init__(
            f"Rate limit exceeded: {limit} bids per minute",
            code="RATE_LIMIT_EXCEEDED",
        )
        self.spectator_id = spectator_id


class InsufficientTokensError(BidValidationError):
    """Raised when spectator has insufficient tokens."""

    def __init__(self, required: int, available: int) -> None:
        super().__init__(
            f"Insufficient tokens: need {required}, have {available}",
            code="INSUFFICIENT_TOKENS",
        )
        self.required = required
        self.available = available


# =============================================================================
# Validation Functions
# =============================================================================


def validate_bid_content(content: str) -> tuple[bool, str | None]:
    """
    Validate bid content for safety and sanity.

    Returns:
        (is_valid, error_message or None)
    """
    # Length checks
    if len(content) < MIN_BID_CONTENT_LENGTH:
        return False, f"Content too short (min {MIN_BID_CONTENT_LENGTH} chars)"

    if len(content) > MAX_BID_CONTENT_LENGTH:
        return False, f"Content too long (max {MAX_BID_CONTENT_LENGTH} chars)"

    # Prohibited pattern checks
    content_lower = content.lower()
    for pattern in PROHIBITED_PATTERNS:
        if re.search(pattern, content_lower, re.IGNORECASE):
            return False, "Content contains prohibited patterns"

    return True, None


def sanitize_bid_content(content: str) -> str:
    """
    Sanitize bid content by stripping dangerous patterns.

    Returns sanitized content string.
    """
    # Strip HTML tags
    content = re.sub(r"<[^>]+>", "", content)

    # Truncate to max length
    if len(content) > MAX_BID_CONTENT_LENGTH:
        content = content[:MAX_BID_CONTENT_LENGTH]

    # Normalize whitespace
    content = " ".join(content.split())

    return content.strip()


# =============================================================================
# Bid Types and Costs
# =============================================================================


class BidType(Enum):
    """
    Types of spectator bids with associated token costs.

    Aligned with atelier-experience.md SPECTATOR_COSTS:
    - inject_constraint: 10 tokens
    - request_direction: 5 tokens
    - boost_builder: 3 tokens
    """

    INJECT_CONSTRAINT = auto()  # Direct creative constraint (10 tokens)
    REQUEST_DIRECTION = auto()  # Suggest direction (5 tokens)
    BOOST_BUILDER = auto()  # Reinforce current path (3 tokens)


# Token costs per bid type
BID_COSTS: dict[BidType, int] = {
    BidType.INJECT_CONSTRAINT: 10,
    BidType.REQUEST_DIRECTION: 5,
    BidType.BOOST_BUILDER: 3,
}

# Priority levels (higher = processed sooner)
BID_PRIORITIES: dict[BidType, int] = {
    BidType.INJECT_CONSTRAINT: 100,  # Highest priority
    BidType.REQUEST_DIRECTION: 50,
    BidType.BOOST_BUILDER: 25,
}


# =============================================================================
# Core Data Types
# =============================================================================


@dataclass(frozen=True)
class Bid:
    """
    A spectator bid to influence creation.

    Bids are immutable once created. They flow through the BidQueue
    and can be converted to Flux Perturbations for injection.

    Attributes:
        id: Unique bid identifier
        spectator_id: Who is bidding
        session_id: Target atelier session
        bid_type: Type of bid (constraint, direction, boost)
        content: The bid content (constraint text, direction, etc.)
        tokens_spent: Actual tokens deducted
        priority: Processing priority (derived from bid_type)
        timestamp: When the bid was created
        metadata: Optional additional data
    """

    id: str
    spectator_id: str
    session_id: str
    bid_type: BidType
    content: str
    tokens_spent: int
    priority: int
    timestamp: float
    metadata: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def create(
        cls,
        spectator_id: str,
        session_id: str,
        bid_type: BidType,
        content: str,
        *,
        metadata: dict[str, Any] | None = None,
    ) -> "Bid":
        """
        Create a new bid with automatic cost/priority calculation.

        Args:
            spectator_id: ID of the spectator making the bid
            session_id: Target atelier session
            bid_type: Type of bid
            content: Bid content (constraint, direction, etc.)
            metadata: Optional additional data

        Returns:
            New Bid instance with calculated cost and priority
        """
        return cls(
            id=uuid4().hex[:12],
            spectator_id=spectator_id,
            session_id=session_id,
            bid_type=bid_type,
            content=content,
            tokens_spent=BID_COSTS[bid_type],
            priority=BID_PRIORITIES[bid_type],
            timestamp=time.time(),
            metadata=metadata or {},
        )

    def to_dict(self) -> dict[str, Any]:
        """Serialize for streaming/persistence."""
        return {
            "id": self.id,
            "spectator_id": self.spectator_id,
            "session_id": self.session_id,
            "bid_type": self.bid_type.name,
            "content": self.content,
            "tokens_spent": self.tokens_spent,
            "priority": self.priority,
            "timestamp": self.timestamp,
            "metadata": dict(self.metadata),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Bid":
        """Deserialize from stored data."""
        return cls(
            id=data["id"],
            spectator_id=data["spectator_id"],
            session_id=data["session_id"],
            bid_type=BidType[data["bid_type"]],
            content=data["content"],
            tokens_spent=data["tokens_spent"],
            priority=data["priority"],
            timestamp=data["timestamp"],
            metadata=data.get("metadata", {}),
        )

    def __lt__(self, other: "Bid") -> bool:
        """For priority queue: higher priority first, then earlier timestamp."""
        if self.priority != other.priority:
            return self.priority > other.priority  # Higher priority first
        return self.timestamp < other.timestamp  # Earlier first for ties


@dataclass
class SpectatorStats:
    """
    Statistics for a single spectator in a session.

    Tracks:
    - Total tokens spent
    - Number of bids by type
    - Accepted/acknowledged bids
    - Watch time contribution

    Used for leaderboard ranking and rewards.
    """

    spectator_id: str
    session_id: str
    tokens_spent: int = 0
    bids_submitted: int = 0
    bids_accepted: int = 0
    bids_acknowledged: int = 0
    watch_time_seconds: float = 0.0
    constraint_bids: int = 0
    direction_bids: int = 0
    boost_bids: int = 0
    last_bid_at: datetime | None = None

    @property
    def influence_score(self) -> float:
        """
        Calculate influence score for leaderboard ranking.

        Formula: tokens_spent * acceptance_rate * (1 + log(bids))
        Rewards both quantity and quality of participation.
        """
        import math

        if self.bids_submitted == 0:
            return 0.0

        acceptance_rate = (
            self.bids_accepted + 0.5 * self.bids_acknowledged
        ) / self.bids_submitted
        bid_factor = 1 + math.log1p(self.bids_submitted)

        return self.tokens_spent * acceptance_rate * bid_factor

    def record_bid(self, bid: Bid) -> None:
        """Record a new bid in stats."""
        self.tokens_spent += bid.tokens_spent
        self.bids_submitted += 1
        self.last_bid_at = datetime.now()

        match bid.bid_type:
            case BidType.INJECT_CONSTRAINT:
                self.constraint_bids += 1
            case BidType.REQUEST_DIRECTION:
                self.direction_bids += 1
            case BidType.BOOST_BUILDER:
                self.boost_bids += 1

    def record_outcome(self, accepted: bool, acknowledged: bool = False) -> None:
        """Record bid outcome (accepted/acknowledged/ignored)."""
        if accepted:
            self.bids_accepted += 1
        elif acknowledged:
            self.bids_acknowledged += 1

    def to_dict(self) -> dict[str, Any]:
        """Serialize for API/storage."""
        return {
            "spectator_id": self.spectator_id,
            "session_id": self.session_id,
            "tokens_spent": self.tokens_spent,
            "bids_submitted": self.bids_submitted,
            "bids_accepted": self.bids_accepted,
            "bids_acknowledged": self.bids_acknowledged,
            "watch_time_seconds": self.watch_time_seconds,
            "constraint_bids": self.constraint_bids,
            "direction_bids": self.direction_bids,
            "boost_bids": self.boost_bids,
            "influence_score": self.influence_score,
            "last_bid_at": self.last_bid_at.isoformat() if self.last_bid_at else None,
        }


class BidOutcome(Enum):
    """Possible outcomes for a bid."""

    PENDING = auto()  # In queue, not yet processed
    ACCEPTED = auto()  # Builder accepted the constraint
    ACKNOWLEDGED = auto()  # Builder acknowledged but didn't commit
    IGNORED = auto()  # Builder ignored (timed out)
    REJECTED = auto()  # System rejected (invalid, insufficient tokens)


@dataclass
class BidResult:
    """Result of submitting a bid."""

    bid: Bid
    success: bool
    outcome: BidOutcome
    message: str
    refund_tokens: int = 0  # Tokens refunded (partial for acknowledged)


# =============================================================================
# BidQueue: Priority Queue for Spectator Bids
# =============================================================================


class BidQueue:
    """
    Priority queue for spectator bids with Flux integration.

    The queue:
    1. Accepts bids from spectators (with validation & rate limiting)
    2. Orders by priority (inject > direction > boost)
    3. Dequeues for builder consideration
    4. Can inject into Flux stream via Perturbation API
    5. Integrates with TokenPool for actual token deduction

    Thread-safe via asyncio primitives.

    Hardening Features:
    - Input validation (content length, prohibited patterns)
    - Rate limiting (MAX_BIDS_PER_MINUTE per spectator)
    - TokenPool integration for token deduction
    - Builder acknowledgment with bonus tokens (1.5x for accepted)

    Example:
        pool = TokenPool()
        queue = BidQueue(session_id="session-123", token_pool=pool)

        # Submit a bid (validates & deducts tokens)
        result = await queue.submit(
            spectator_id="alice",
            bid_type=BidType.INJECT_CONSTRAINT,
            content="Add more contrast",
        )

        # Dequeue for builder
        next_bid = await queue.dequeue()

        # Builder accepts → spectator gets 1.5x bonus
        queue.record_outcome(next_bid.id, BidOutcome.ACCEPTED)
    """

    def __init__(
        self,
        session_id: str,
        *,
        token_pool: "TokenPool | None" = None,
        max_queue_size: int = 100,
        bid_timeout_seconds: float = 300.0,  # 5 minutes
        validate_content: bool = True,
        rate_limit: bool = True,
        builder_id: str | None = None,
    ) -> None:
        """
        Initialize bid queue for a session.

        Args:
            session_id: Atelier session this queue belongs to
            token_pool: Optional TokenPool for token deduction/refund
            max_queue_size: Maximum bids in queue
            bid_timeout_seconds: How long before unprocessed bids expire
            validate_content: Whether to validate bid content
            rate_limit: Whether to apply rate limiting
            builder_id: ID of the builder (for tracking earnings)
        """
        self.session_id = session_id
        self.max_queue_size = max_queue_size
        self.bid_timeout_seconds = bid_timeout_seconds
        self.validate_content = validate_content
        self.rate_limit = rate_limit
        self.builder_id = builder_id

        # TokenPool integration
        self._token_pool = token_pool

        # Internal state
        self._heap: list[Bid] = []
        self._bids_by_id: dict[str, Bid] = {}
        self._outcomes: dict[str, BidOutcome] = {}
        self._spectator_stats: dict[str, SpectatorStats] = {}

        # Rate limiting: spectator_id → list of timestamps
        self._rate_limit_tracker: dict[str, list[float]] = {}

        # Lock for thread safety
        self._lock = asyncio.Lock()

        # Event for waiting on bids
        self._bid_available = asyncio.Event()

        # Statistics
        self.total_bids_received = 0
        self.total_tokens_collected = 0
        self.total_tokens_refunded = 0
        self.builder_tokens_earned = 0

    def _check_rate_limit(self, spectator_id: str) -> bool:
        """
        Check if spectator is within rate limit.

        Returns True if within limit, False if exceeded.
        """
        if not self.rate_limit:
            return True

        now = time.time()
        cutoff = now - RATE_LIMIT_WINDOW_SECONDS

        # Get or create tracking list
        if spectator_id not in self._rate_limit_tracker:
            self._rate_limit_tracker[spectator_id] = []

        # Clean old entries
        self._rate_limit_tracker[spectator_id] = [
            ts for ts in self._rate_limit_tracker[spectator_id] if ts > cutoff
        ]

        # Check limit
        if len(self._rate_limit_tracker[spectator_id]) >= MAX_BIDS_PER_MINUTE:
            return False

        # Record this bid attempt
        self._rate_limit_tracker[spectator_id].append(now)
        return True

    def _deduct_tokens(self, spectator_id: str, amount: int) -> tuple[bool, str | None]:
        """
        Deduct tokens from spectator via TokenPool.

        Returns:
            (success, error_message or None)
        """
        if self._token_pool is None:
            # No pool configured - allow bid without deduction
            return True, None

        spend_result = self._token_pool.spend(
            spectator_id,
            Decimal(str(amount)),
            reason=f"bid:{self.session_id}",
        )

        if not spend_result.success:
            return False, spend_result.reason

        return True, None

    def _refund_tokens(self, spectator_id: str, amount: int, reason: str) -> None:
        """Refund tokens to spectator via TokenPool."""
        if self._token_pool is None:
            return

        self._token_pool.grant(
            spectator_id,
            Decimal(str(amount)),
            reason=f"refund:{reason}",
        )
        self.total_tokens_refunded += amount

    def _grant_builder_tokens(self, amount: int, reason: str) -> None:
        """Grant tokens to builder for accepted bids."""
        if self._token_pool is None or self.builder_id is None:
            return

        self._token_pool.grant(
            self.builder_id,
            Decimal(str(amount)),
            reason=f"builder_earning:{reason}",
        )
        self.builder_tokens_earned += amount

    async def submit(
        self,
        spectator_id: str,
        bid_type: BidType,
        content: str,
        *,
        metadata: dict[str, Any] | None = None,
        skip_validation: bool = False,
        skip_token_deduction: bool = False,
    ) -> BidResult:
        """
        Submit a new bid to the queue.

        Hardened submission flow:
        1. Validate content (length, prohibited patterns)
        2. Check rate limit
        3. Check/deduct tokens via TokenPool
        4. Add to priority queue

        Args:
            spectator_id: ID of spectator submitting
            bid_type: Type of bid
            content: Bid content
            metadata: Optional additional data
            skip_validation: Skip content validation (testing only)
            skip_token_deduction: Skip token deduction (testing only)

        Returns:
            BidResult with success status and bid details
        """
        cost = BID_COSTS[bid_type]

        # Step 1: Validate content
        if self.validate_content and not skip_validation:
            is_valid, error = validate_bid_content(content)
            if not is_valid:
                logger.warning(
                    f"Bid validation failed for {spectator_id}: {error}",
                    extra={"session_id": self.session_id, "bid_type": bid_type.name},
                )
                return BidResult(
                    bid=Bid.create(spectator_id, self.session_id, bid_type, content),
                    success=False,
                    outcome=BidOutcome.REJECTED,
                    message=error or "Content validation failed",
                    refund_tokens=0,  # No tokens deducted yet
                )

            # Sanitize content
            content = sanitize_bid_content(content)

        async with self._lock:
            # Step 2: Check rate limit
            if not self._check_rate_limit(spectator_id):
                logger.warning(
                    f"Rate limit exceeded for {spectator_id}",
                    extra={"session_id": self.session_id},
                )
                return BidResult(
                    bid=Bid.create(spectator_id, self.session_id, bid_type, content),
                    success=False,
                    outcome=BidOutcome.REJECTED,
                    message=f"Rate limit exceeded: max {MAX_BIDS_PER_MINUTE} bids per minute",
                    refund_tokens=0,
                )

            # Step 3: Check queue capacity
            if len(self._heap) >= self.max_queue_size:
                return BidResult(
                    bid=Bid.create(spectator_id, self.session_id, bid_type, content),
                    success=False,
                    outcome=BidOutcome.REJECTED,
                    message="Queue is full. Try again later.",
                    refund_tokens=0,
                )

            # Step 4: Deduct tokens
            if not skip_token_deduction:
                success, error = self._deduct_tokens(spectator_id, cost)
                if not success:
                    return BidResult(
                        bid=Bid.create(
                            spectator_id, self.session_id, bid_type, content
                        ),
                        success=False,
                        outcome=BidOutcome.REJECTED,
                        message=error or "Insufficient tokens",
                        refund_tokens=0,
                    )

            # Step 5: Create and queue bid
            bid = Bid.create(
                spectator_id=spectator_id,
                session_id=self.session_id,
                bid_type=bid_type,
                content=content,
                metadata=metadata,
            )

            # Add to heap (priority queue)
            heapq.heappush(self._heap, bid)
            self._bids_by_id[bid.id] = bid
            self._outcomes[bid.id] = BidOutcome.PENDING

            # Update stats
            self.total_bids_received += 1
            self.total_tokens_collected += bid.tokens_spent

            # Update spectator stats
            if spectator_id not in self._spectator_stats:
                self._spectator_stats[spectator_id] = SpectatorStats(
                    spectator_id=spectator_id,
                    session_id=self.session_id,
                )
            self._spectator_stats[spectator_id].record_bid(bid)

            # Signal that a bid is available
            self._bid_available.set()

            logger.info(
                f"Bid submitted: {bid.id} by {spectator_id}",
                extra={
                    "session_id": self.session_id,
                    "bid_type": bid_type.name,
                    "tokens": cost,
                },
            )

            return BidResult(
                bid=bid,
                success=True,
                outcome=BidOutcome.PENDING,
                message=f"Bid submitted: {bid.id}",
            )

    async def dequeue(self, timeout: float | None = None) -> Bid | None:
        """
        Dequeue the highest priority bid.

        Args:
            timeout: Optional timeout in seconds to wait for a bid

        Returns:
            Highest priority bid, or None if queue is empty/timeout
        """
        start_time = time.time()

        while True:
            async with self._lock:
                # Clean up expired bids
                await self._cleanup_expired()

                if self._heap:
                    bid = heapq.heappop(self._heap)
                    return bid

                # Clear event if queue is now empty
                self._bid_available.clear()

            # Wait for new bid or timeout
            if timeout is not None:
                elapsed = time.time() - start_time
                remaining = timeout - elapsed
                if remaining <= 0:
                    return None
                try:
                    await asyncio.wait_for(
                        self._bid_available.wait(),
                        timeout=remaining,
                    )
                except asyncio.TimeoutError:
                    return None
            else:
                await self._bid_available.wait()

    async def peek(self) -> Bid | None:
        """Peek at highest priority bid without removing."""
        async with self._lock:
            await self._cleanup_expired()
            if self._heap:
                return self._heap[0]
            return None

    def record_outcome(self, bid_id: str, outcome: BidOutcome) -> int:
        """
        Record the outcome of a bid.

        This method handles the full outcome flow including:
        - Updating spectator stats
        - Refunding tokens (via TokenPool if configured)
        - Granting bonus tokens for accepted bids (1.5x)
        - Compensating builder for accepted bids

        Args:
            bid_id: ID of the bid
            outcome: What happened to the bid

        Returns:
            Tokens refunded to spectator (if any)
        """
        if bid_id not in self._bids_by_id:
            return 0

        bid = self._bids_by_id[bid_id]
        self._outcomes[bid_id] = outcome

        # Update spectator stats
        if bid.spectator_id in self._spectator_stats:
            stats = self._spectator_stats[bid.spectator_id]
            stats.record_outcome(
                accepted=(outcome == BidOutcome.ACCEPTED),
                acknowledged=(outcome == BidOutcome.ACKNOWLEDGED),
            )

        # Calculate refund and handle token flows
        refund_amount = 0
        match outcome:
            case BidOutcome.ACCEPTED:
                # Accepted bids: spectator gets 1.5x bonus, builder gets tokens
                bonus = int(bid.tokens_spent * float(ACCEPTED_BID_BONUS_MULTIPLIER))
                self._refund_tokens(bid.spectator_id, bonus, f"accepted_bonus:{bid_id}")
                self._grant_builder_tokens(bid.tokens_spent, f"accepted:{bid_id}")
                refund_amount = 0  # Bonus tracked separately

                logger.info(
                    f"Bid accepted: {bid_id}, bonus={bonus}",
                    extra={
                        "session_id": self.session_id,
                        "spectator_id": bid.spectator_id,
                        "builder_id": self.builder_id,
                    },
                )

            case BidOutcome.ACKNOWLEDGED:
                # Half refund for acknowledged
                refund_amount = bid.tokens_spent // 2
                self._refund_tokens(
                    bid.spectator_id, refund_amount, f"acknowledged:{bid_id}"
                )

            case BidOutcome.IGNORED:
                # Full refund for ignored
                refund_amount = bid.tokens_spent
                self._refund_tokens(
                    bid.spectator_id, refund_amount, f"ignored:{bid_id}"
                )

            case BidOutcome.REJECTED:
                # Full refund for rejected
                refund_amount = bid.tokens_spent
                self._refund_tokens(
                    bid.spectator_id, refund_amount, f"rejected:{bid_id}"
                )

            case _:
                pass

        return refund_amount

    def get_bid(self, bid_id: str) -> Bid | None:
        """Get a bid by ID."""
        return self._bids_by_id.get(bid_id)

    def get_outcome(self, bid_id: str) -> BidOutcome | None:
        """Get the outcome of a bid."""
        return self._outcomes.get(bid_id)

    def get_spectator_stats(self, spectator_id: str) -> SpectatorStats | None:
        """Get stats for a spectator."""
        return self._spectator_stats.get(spectator_id)

    def get_leaderboard(self, limit: int = 10) -> list[SpectatorStats]:
        """
        Get top spectators by influence score.

        Args:
            limit: Maximum number of entries

        Returns:
            List of SpectatorStats sorted by influence score (descending)
        """
        return sorted(
            self._spectator_stats.values(),
            key=lambda s: s.influence_score,
            reverse=True,
        )[:limit]

    @property
    def queue_size(self) -> int:
        """Current number of bids in queue."""
        return len(self._heap)

    @property
    def is_empty(self) -> bool:
        """Check if queue is empty."""
        return len(self._heap) == 0

    async def _cleanup_expired(self) -> None:
        """Remove expired bids from the queue."""
        now = time.time()
        cutoff = now - self.bid_timeout_seconds

        # Filter out expired bids
        valid_bids = [b for b in self._heap if b.timestamp > cutoff]
        expired = [b for b in self._heap if b.timestamp <= cutoff]

        if expired:
            # Mark expired as ignored
            for bid in expired:
                self._outcomes[bid.id] = BidOutcome.IGNORED

            # Rebuild heap
            self._heap = valid_bids
            heapq.heapify(self._heap)

    def to_perturbation(self, bid: Bid) -> "Perturbation":
        """
        Convert a bid to a Flux Perturbation for stream injection.

        This is the key integration point with the Flux streaming system.
        The bid becomes a high-priority event that flows through the
        artisan's processing pipeline.

        Args:
            bid: The bid to convert

        Returns:
            Perturbation ready for Flux injection
        """
        from agents.flux.perturbation import create_perturbation

        # Create perturbation with bid data
        perturbation_data = {
            "type": "spectator_bid",
            "bid": bid.to_dict(),
            "constraint": bid.content,
            "bid_type": bid.bid_type.name,
        }

        return create_perturbation(
            data=perturbation_data,
            priority=bid.priority,  # Use bid priority
        )

    async def inject_into_flux(
        self,
        bid: Bid,
        flux_queue: asyncio.Queue[Any],
    ) -> None:
        """
        Inject a bid into a Flux stream.

        Args:
            bid: The bid to inject
            flux_queue: The Flux perturbation queue
        """
        perturbation = self.to_perturbation(bid)
        await flux_queue.put(perturbation)

    def status(self) -> dict[str, Any]:
        """Get queue status for monitoring."""
        return {
            "session_id": self.session_id,
            "queue_size": self.queue_size,
            "total_bids_received": self.total_bids_received,
            "total_tokens_collected": self.total_tokens_collected,
            "spectator_count": len(self._spectator_stats),
            "pending_bids": sum(
                1 for o in self._outcomes.values() if o == BidOutcome.PENDING
            ),
        }


# =============================================================================
# Session-level Bid Manager
# =============================================================================


class AtelierBidManager:
    """
    Manages bid queues across multiple atelier sessions.

    Provides:
    - Session-scoped bid queues
    - Cross-session leaderboards
    - Global statistics

    Example:
        manager = AtelierBidManager()

        # Get or create queue for session
        queue = manager.get_queue("session-123")

        # Submit bid
        result = await queue.submit(...)

        # Get global leaderboard
        top_spectators = manager.global_leaderboard(limit=10)
    """

    def __init__(self) -> None:
        self._queues: dict[str, BidQueue] = {}
        self._lock = asyncio.Lock()

    async def get_queue(self, session_id: str) -> BidQueue:
        """Get or create a bid queue for a session."""
        async with self._lock:
            if session_id not in self._queues:
                self._queues[session_id] = BidQueue(session_id=session_id)
            return self._queues[session_id]

    async def close_queue(self, session_id: str) -> None:
        """Close a session's bid queue."""
        async with self._lock:
            if session_id in self._queues:
                del self._queues[session_id]

    def global_leaderboard(self, limit: int = 10) -> list[dict[str, Any]]:
        """
        Get global leaderboard across all sessions.

        Aggregates spectator stats across all active sessions.
        """
        # Aggregate stats by spectator across sessions
        aggregated: dict[str, dict[str, Any]] = {}

        for queue in self._queues.values():
            for stats in queue._spectator_stats.values():
                if stats.spectator_id not in aggregated:
                    aggregated[stats.spectator_id] = {
                        "spectator_id": stats.spectator_id,
                        "total_tokens_spent": 0,
                        "total_bids": 0,
                        "total_accepted": 0,
                        "sessions_participated": 0,
                    }

                agg = aggregated[stats.spectator_id]
                agg["total_tokens_spent"] += stats.tokens_spent
                agg["total_bids"] += stats.bids_submitted
                agg["total_accepted"] += stats.bids_accepted
                agg["sessions_participated"] += 1

        # Sort by tokens spent
        sorted_spectators = sorted(
            aggregated.values(),
            key=lambda x: x["total_tokens_spent"],
            reverse=True,
        )

        return sorted_spectators[:limit]

    def global_stats(self) -> dict[str, Any]:
        """Get global bidding statistics."""
        total_bids = sum(q.total_bids_received for q in self._queues.values())
        total_tokens = sum(q.total_tokens_collected for q in self._queues.values())

        return {
            "active_sessions": len(self._queues),
            "total_bids_received": total_bids,
            "total_tokens_collected": total_tokens,
            "queue_sizes": {sid: q.queue_size for sid, q in self._queues.items()},
        }


# =============================================================================
# Module Singleton
# =============================================================================


_bid_manager: AtelierBidManager | None = None


def get_bid_manager() -> AtelierBidManager:
    """Get the global bid manager instance."""
    global _bid_manager
    if _bid_manager is None:
        _bid_manager = AtelierBidManager()
    return _bid_manager


# =============================================================================
# Exports
# =============================================================================


__all__ = [
    # Types
    "BidType",
    "Bid",
    "BidOutcome",
    "BidResult",
    "SpectatorStats",
    # Costs & Constants
    "BID_COSTS",
    "BID_PRIORITIES",
    "MAX_BID_CONTENT_LENGTH",
    "MIN_BID_CONTENT_LENGTH",
    "MAX_BIDS_PER_MINUTE",
    "ACCEPTED_BID_BONUS_MULTIPLIER",
    # Validation
    "BidValidationError",
    "RateLimitError",
    "InsufficientTokensError",
    "validate_bid_content",
    "sanitize_bid_content",
    # Queue
    "BidQueue",
    # Manager
    "AtelierBidManager",
    "get_bid_manager",
]
