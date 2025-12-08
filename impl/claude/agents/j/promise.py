"""
Promise[T] - Lazy computation with Ground fallback.

A Promise represents a deferred computation that:
1. Carries an intent describing what should be computed
2. Has a Ground fallback for safety on failure
3. Can decompose into child promises (tree structure)
4. Validates results via generated tests before acceptance

See spec/j-gents/lazy.md for the full specification.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Generic, Optional, TypeVar

T = TypeVar("T")


class PromiseState(Enum):
    """States a promise can be in during its lifecycle."""

    PENDING = "pending"  # Initial state, not yet resolved
    RESOLVING = "resolving"  # Computation in progress
    RESOLVED = "resolved"  # Successfully computed and validated
    COLLAPSED = "collapsed"  # Failed validation, returned Ground
    FAILED = "failed"  # Error during computation (returns Ground)


@dataclass
class Promise(Generic[T]):
    """
    A deferred computation with Ground fallback.

    Promises separate forward responsibility (what should happen) from
    backward accountability (proving it happened correctly).

    Type parameter T is the expected result type.
    """

    # Core identity
    intent: str  # What this promise commits to deliver
    ground: T  # Fallback value if promise fails (the "golden parachute")

    # Context and budget
    context: dict[str, Any] = field(default_factory=dict)
    depth: int = 0  # Recursion depth (affects entropy budget)

    # State tracking
    state: PromiseState = PromiseState.PENDING

    # Lazily populated on resolution
    resolved_value: Optional[T] = None
    proof: Optional[Callable[[T], bool]] = None  # Validation test
    collapse_reason: Optional[str] = None

    # Tree structure (for PROBABILISTIC decomposition)
    children: list[Promise[Any]] = field(default_factory=list)
    parent: Optional[Promise[Any]] = field(default=None, repr=False)

    @property
    def entropy_budget(self) -> float:
        """
        Compute entropy budget based on depth.

        Budget diminishes with depth: 1/(depth+1)
        - depth 0: budget 1.0 (full freedom)
        - depth 1: budget 0.5
        - depth 2: budget 0.33
        - depth 3: budget 0.25
        """
        return 1.0 / (self.depth + 1)

    @property
    def is_leaf(self) -> bool:
        """True if this promise has no children."""
        return len(self.children) == 0

    @property
    def is_resolved(self) -> bool:
        """True if promise is in a terminal state."""
        return self.state in (
            PromiseState.RESOLVED,
            PromiseState.COLLAPSED,
            PromiseState.FAILED,
        )

    def value_or_ground(self) -> T:
        """
        Get the resolved value or ground.

        Returns resolved_value if RESOLVED, otherwise returns ground.
        """
        if self.state == PromiseState.RESOLVED and self.resolved_value is not None:
            return self.resolved_value
        return self.ground

    def add_child(self, child: Promise[Any]) -> None:
        """Add a child promise to this promise's tree."""
        child.parent = self
        child.depth = self.depth + 1
        self.children.append(child)

    def mark_resolving(self) -> None:
        """Transition to RESOLVING state."""
        if self.state != PromiseState.PENDING:
            raise ValueError(f"Cannot mark_resolving from state {self.state}")
        self.state = PromiseState.RESOLVING

    def mark_resolved(self, value: T, proof: Optional[Callable[[T], bool]] = None) -> None:
        """
        Transition to RESOLVED state with validated value.

        Args:
            value: The computed result
            proof: Optional validation function that was used
        """
        self.state = PromiseState.RESOLVED
        self.resolved_value = value
        self.proof = proof

    def mark_collapsed(self, reason: str) -> None:
        """
        Transition to COLLAPSED state (validation failed).

        The ground value will be returned instead.
        """
        self.state = PromiseState.COLLAPSED
        self.collapse_reason = reason

    def mark_failed(self, reason: str) -> None:
        """
        Transition to FAILED state (exception during computation).

        The ground value will be returned instead.
        """
        self.state = PromiseState.FAILED
        self.collapse_reason = reason


@dataclass(frozen=True)
class PromiseMetrics:
    """Metrics about a promise tree's execution."""

    total_promises: int = 0
    resolved_count: int = 0
    collapsed_count: int = 0
    failed_count: int = 0
    max_depth_reached: int = 0

    @property
    def success_rate(self) -> float:
        """Proportion of promises that resolved successfully."""
        if self.total_promises == 0:
            return 1.0
        return self.resolved_count / self.total_promises


def collect_metrics(root: Promise[Any]) -> PromiseMetrics:
    """
    Collect execution metrics from a promise tree.

    Traverses the tree and counts promise states.
    """
    total = 0
    resolved = 0
    collapsed = 0
    failed = 0
    max_depth = 0

    def traverse(p: Promise[Any]) -> None:
        nonlocal total, resolved, collapsed, failed, max_depth
        total += 1
        max_depth = max(max_depth, p.depth)

        if p.state == PromiseState.RESOLVED:
            resolved += 1
        elif p.state == PromiseState.COLLAPSED:
            collapsed += 1
        elif p.state == PromiseState.FAILED:
            failed += 1

        for child in p.children:
            traverse(child)

    traverse(root)

    return PromiseMetrics(
        total_promises=total,
        resolved_count=resolved,
        collapsed_count=collapsed,
        failed_count=failed,
        max_depth_reached=max_depth,
    )


# --- Promise Creation Helpers ---


def promise(intent: str, ground: T, context: Optional[dict[str, Any]] = None) -> Promise[T]:
    """
    Create a new promise with sensible defaults.

    Args:
        intent: What this promise commits to deliver
        ground: Fallback value on failure
        context: Optional context dictionary

    Returns:
        A new PENDING promise
    """
    return Promise(
        intent=intent,
        ground=ground,
        context=context or {},
    )


def child_promise(
    parent: Promise[Any],
    intent: str,
    ground: T,
    context: Optional[dict[str, Any]] = None,
) -> Promise[T]:
    """
    Create a child promise and attach to parent.

    Automatically sets depth based on parent.

    Args:
        parent: The parent promise
        intent: What this child promises to deliver
        ground: Fallback value on failure
        context: Optional additional context (inherits from parent)

    Returns:
        A new PENDING child promise attached to parent
    """
    merged_context = {**parent.context, **(context or {})}
    child: Promise[T] = Promise(
        intent=intent,
        ground=ground,
        context=merged_context,
        depth=parent.depth + 1,
        parent=parent,
    )
    parent.children.append(child)
    return child
