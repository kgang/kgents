"""
YieldHandler - Manages YIELD turn approval flow.

The YieldHandler is the runtime component that manages YIELD turns,
blocking execution until approval or rejection.

This implements Phase 5 of the Turn-gents Protocol:
- YIELD turns block until approval/rejection/timeout
- Multiple approval strategies (All, Any, Majority)
- Integration with K-gent soul intercept

The key insight: YIELD turns preserve human agency for high-risk actions.
They operationalize the "ethical" principle of the kgents spec.

Example:
    handler = YieldHandler()

    # Create a yield turn
    yield_turn = YieldTurn.create_yield(
        content="Deploy to production",
        source="deployer-agent",
        yield_reason="Production deployment requires approval",
        required_approvers={"k-gent", "human"},
    )

    # Request approval (blocks)
    result = await handler.request_approval(yield_turn, timeout=300.0)

    if result.is_approved:
        # Proceed with action
        ...
    else:
        # Handle rejection or timeout
        ...

References:
- Turn-gents Plan: Phase 5 (Yield Governance)
- principles.md: Ethical - preserve human agency
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import TYPE_CHECKING, Any, Generic, TypeVar

if TYPE_CHECKING:
    from .turn import YieldTurn

T = TypeVar("T")


class ApprovalStrategy(Enum):
    """
    Strategies for determining when a YIELD is approved.

    | Strategy | Description |
    |----------|-------------|
    | ALL      | All required approvers must approve |
    | ANY      | First approval wins |
    | MAJORITY | >50% of required approvers must approve |
    """

    ALL = auto()  # All required must approve
    ANY = auto()  # First approval wins
    MAJORITY = auto()  # >50% must approve


class ApprovalStatus(Enum):
    """Status of an approval request."""

    PENDING = auto()  # Awaiting approval
    APPROVED = auto()  # Fully approved
    REJECTED = auto()  # Explicitly rejected
    TIMEOUT = auto()  # Timed out without resolution


@dataclass
class ApprovalResult(Generic[T]):
    """
    Result of an approval request.

    Contains the final status and the turn (potentially with
    updated approvals if partially approved before rejection/timeout).
    """

    status: ApprovalStatus
    turn: YieldTurn[T]
    rejection_reason: str | None = None
    rejected_by: str | None = None
    timeout_duration: float | None = None

    @property
    def is_approved(self) -> bool:
        """Check if the request was fully approved."""
        return self.status == ApprovalStatus.APPROVED

    @property
    def is_rejected(self) -> bool:
        """Check if the request was rejected."""
        return self.status == ApprovalStatus.REJECTED

    @property
    def is_timeout(self) -> bool:
        """Check if the request timed out."""
        return self.status == ApprovalStatus.TIMEOUT

    @property
    def is_pending(self) -> bool:
        """Check if the request is still pending."""
        return self.status == ApprovalStatus.PENDING


@dataclass
class PendingApproval(Generic[T]):
    """
    Internal state for a pending approval request.

    Tracks the current state of approval and provides
    synchronization primitives for async waiting.
    """

    turn: YieldTurn[T]
    strategy: ApprovalStrategy
    event: asyncio.Event = field(default_factory=asyncio.Event)
    rejector: str | None = None
    rejection_reason: str | None = None

    def is_satisfied(self) -> bool:
        """Check if the approval requirement is satisfied based on strategy."""
        if self.rejector is not None:
            return True  # Rejection always terminates

        if self.strategy == ApprovalStrategy.ALL:
            return self.turn.is_approved()
        elif self.strategy == ApprovalStrategy.ANY:
            return len(self.turn.approved_by) > 0
        elif self.strategy == ApprovalStrategy.MAJORITY:
            required_count = len(self.turn.required_approvers)
            approved_count = len(self.turn.approved_by)
            return approved_count > required_count / 2
        return False


@dataclass
class YieldHandler:
    """
    Manages YIELD turn approval flow.

    The YieldHandler:
    1. Tracks pending approval requests
    2. Provides async approval/rejection methods
    3. Supports configurable approval strategies
    4. Handles timeouts gracefully

    Thread Safety:
    - Uses asyncio.Event for synchronization
    - Turn state is immutable (new YieldTurn on each approval)
    - Pending state protected by dict isolation

    Example:
        handler = YieldHandler()

        # In agent code
        result = await handler.request_approval(yield_turn)

        # From approver (human or K-gent)
        await handler.approve("turn-123", "k-gent")
    """

    # Pending approvals by turn ID
    _pending: dict[str, PendingApproval[Any]] = field(default_factory=dict)

    # Default approval strategy
    default_strategy: ApprovalStrategy = ApprovalStrategy.ALL

    # Callbacks for observability
    _on_approval: list[Any] = field(default_factory=list)
    _on_rejection: list[Any] = field(default_factory=list)
    _on_timeout: list[Any] = field(default_factory=list)

    async def request_approval(
        self,
        turn: YieldTurn[T],
        *,
        timeout: float | None = None,
        strategy: ApprovalStrategy | None = None,
    ) -> ApprovalResult[T]:
        """
        Block until approval/rejection/timeout.

        This is the main entry point for YIELD turns. It blocks
        the caller until one of:
        1. All required approvals granted (or strategy satisfied)
        2. Any approver rejects
        3. Timeout expires

        Args:
            turn: The YieldTurn requesting approval
            timeout: Optional timeout in seconds (None = wait forever)
            strategy: Approval strategy (default: ALL)

        Returns:
            ApprovalResult with final status and (possibly updated) turn
        """
        strat = strategy or self.default_strategy

        # Create pending record
        pending = PendingApproval(
            turn=turn,
            strategy=strat,
        )
        self._pending[turn.id] = pending

        try:
            # Check if already satisfied (e.g., no approvers required)
            if pending.is_satisfied():
                return ApprovalResult(
                    status=ApprovalStatus.APPROVED,
                    turn=pending.turn,
                )

            # Wait for approval/rejection/timeout
            if timeout is not None:
                try:
                    await asyncio.wait_for(pending.event.wait(), timeout=timeout)
                except asyncio.TimeoutError:
                    # Timeout - return current state
                    for callback in self._on_timeout:
                        await self._safe_callback(callback, pending.turn)

                    return ApprovalResult(
                        status=ApprovalStatus.TIMEOUT,
                        turn=pending.turn,
                        timeout_duration=timeout,
                    )
            else:
                await pending.event.wait()

            # Check final status
            if pending.rejector is not None:
                for callback in self._on_rejection:
                    await self._safe_callback(
                        callback,
                        pending.turn,
                        pending.rejector,
                        pending.rejection_reason,
                    )

                return ApprovalResult(
                    status=ApprovalStatus.REJECTED,
                    turn=pending.turn,
                    rejection_reason=pending.rejection_reason,
                    rejected_by=pending.rejector,
                )
            else:
                for callback in self._on_approval:
                    await self._safe_callback(callback, pending.turn)

                return ApprovalResult(
                    status=ApprovalStatus.APPROVED,
                    turn=pending.turn,
                )

        finally:
            # Clean up pending record
            self._pending.pop(turn.id, None)

    async def approve(self, turn_id: str, approver: str) -> bool:
        """
        Grant approval from an approver.

        Args:
            turn_id: The ID of the YieldTurn
            approver: The agent ID granting approval

        Returns:
            True if approval was recorded, False if turn not found
            or approver not in required_approvers

        Raises:
            ValueError: If approver not in required_approvers
        """
        pending = self._pending.get(turn_id)
        if pending is None:
            return False

        # Update the turn (immutable - creates new YieldTurn)
        try:
            pending.turn = pending.turn.approve(approver)
        except ValueError:
            # Approver not in required_approvers
            raise

        # Check if now satisfied
        if pending.is_satisfied():
            pending.event.set()

        return True

    async def reject(self, turn_id: str, rejector: str, reason: str = "") -> bool:
        """
        Reject an approval request.

        Args:
            turn_id: The ID of the YieldTurn
            rejector: The agent ID rejecting
            reason: Optional rejection reason

        Returns:
            True if rejection was recorded, False if turn not found
        """
        pending = self._pending.get(turn_id)
        if pending is None:
            return False

        pending.rejector = rejector
        pending.rejection_reason = reason
        pending.event.set()

        return True

    def get_pending(self, turn_id: str) -> YieldTurn[Any] | None:
        """
        Get the current state of a pending approval.

        Args:
            turn_id: The ID of the YieldTurn

        Returns:
            The current YieldTurn state, or None if not found
        """
        pending = self._pending.get(turn_id)
        return pending.turn if pending else None

    def list_pending(self) -> list[YieldTurn[Any]]:
        """
        List all pending approval requests.

        Returns:
            List of YieldTurns awaiting approval
        """
        return [p.turn for p in self._pending.values()]

    def is_pending(self, turn_id: str) -> bool:
        """Check if a turn is pending approval."""
        return turn_id in self._pending

    def on_approval(self, callback: Any) -> None:
        """Register a callback for approval events."""
        self._on_approval.append(callback)

    def on_rejection(self, callback: Any) -> None:
        """Register a callback for rejection events."""
        self._on_rejection.append(callback)

    def on_timeout(self, callback: Any) -> None:
        """Register a callback for timeout events."""
        self._on_timeout.append(callback)

    async def _safe_callback(self, callback: Any, *args: Any) -> None:
        """Safely invoke a callback, handling both sync and async."""
        try:
            result = callback(*args)
            if asyncio.iscoroutine(result):
                await result
        except Exception:
            # Callbacks should not break the approval flow
            pass


def should_yield(
    confidence: float,
    yield_threshold: float,
    turn_type: str = "ACTION",
) -> bool:
    """
    Determine if an action should generate a YIELD turn.

    This is the "soul intercept" heuristic:
    - Low confidence actions should yield for approval
    - Only ACTION turns are considered for auto-yield

    Args:
        confidence: The action's confidence score [0.0, 1.0]
        yield_threshold: Threshold below which to yield
        turn_type: The type of turn being evaluated

    Returns:
        True if the action should generate a YIELD turn
    """
    if turn_type != "ACTION":
        return False

    return confidence < yield_threshold


def compute_risk_score(
    confidence: float,
    entropy_cost: float,
    is_destructive: bool = False,
    has_external_effects: bool = False,
) -> float:
    """
    Compute a risk score for an action.

    Higher risk scores indicate more need for approval.

    The formula:
        risk = (1 - confidence) * (1 + entropy_cost) * modifiers

    Args:
        confidence: Action confidence [0.0, 1.0]
        entropy_cost: Action entropy cost
        is_destructive: Whether action is destructive (delete, etc.)
        has_external_effects: Whether action affects external systems

    Returns:
        Risk score >= 0.0 (higher = riskier)
    """
    base_risk = (1.0 - confidence) * (1.0 + entropy_cost)

    modifier = 1.0
    if is_destructive:
        modifier *= 2.0
    if has_external_effects:
        modifier *= 1.5

    return base_risk * modifier


__all__ = [
    "YieldHandler",
    "ApprovalStrategy",
    "ApprovalStatus",
    "ApprovalResult",
    "PendingApproval",
    "should_yield",
    "compute_risk_score",
]
