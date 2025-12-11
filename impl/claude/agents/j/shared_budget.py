"""
Shared Entropy Budget - Unified J-gent × B-gent budget integration.

This module provides a bridge between J-gent's recursion-based entropy budget
and B-gent's metered functor budget. By using the B-gent EntropyBudget as the
canonical implementation, we:

1. Eliminate duplication (DRY principle)
2. Enable cross-agent budget coordination
3. Provide a consistent API for entropy management

J-gent's `1/(depth+1)` formula is implemented as an adapter over B-gent's
`EntropyBudget.can_afford()` / `consume()` interface.

Usage:
    from agents.j.shared_budget import (
        SharedEntropyBudget,
        create_depth_based_budget,
        compute_depth_from_budget,
    )

    # Create budget with B-gent backing
    budget = create_depth_based_budget(depth=2)
    assert budget.remaining == 1/3  # 1/(2+1)

    # Use B-gent's API
    if budget.can_afford(0.1):
        budget.consume(0.1)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

# Import from B-gent (canonical implementation)
from agents.b.metered_functor import EntropyBudget as BgentEntropyBudget


@dataclass
class SharedEntropyBudget:
    """
    Shared entropy budget that bridges J-gent and B-gent.

    Uses B-gent's EntropyBudget as the backing store while providing
    J-gent's depth-based semantics.

    Attributes:
        depth: Current recursion depth (J-gent semantics)
        backing: B-gent EntropyBudget instance
        threshold: Budget level below which operations are denied
    """

    depth: int = 0
    backing: BgentEntropyBudget = field(default_factory=BgentEntropyBudget)
    threshold: float = 0.1

    def __post_init__(self) -> None:
        """Initialize backing budget based on depth."""
        if self.backing.initial == 1.0 and self.depth > 0:
            # Set initial budget based on depth: 1/(depth+1)
            initial = 1.0 / (self.depth + 1)
            self.backing = BgentEntropyBudget(initial=initial, remaining=initial)

    @property
    def remaining(self) -> float:
        """Get remaining budget (J-gent compatible)."""
        return self.backing.remaining

    @property
    def initial(self) -> float:
        """Get initial budget (J-gent compatible)."""
        return self.backing.initial

    @property
    def is_exhausted(self) -> bool:
        """Check if budget is below threshold."""
        return self.remaining < self.threshold

    def can_afford(self, cost: float) -> bool:
        """
        Check if we can afford a cost (B-gent API).

        Args:
            cost: The cost to check

        Returns:
            True if remaining >= cost
        """
        return self.backing.can_afford(cost)

    def consume(self, cost: float) -> "SharedEntropyBudget":
        """
        Consume budget and return new budget (B-gent API).

        Args:
            cost: The cost to consume

        Returns:
            New SharedEntropyBudget with reduced remaining
        """
        new_backing = self.backing.consume(cost)
        return SharedEntropyBudget(
            depth=self.depth,
            backing=new_backing,
            threshold=self.threshold,
        )

    def spawn_child(self) -> "SharedEntropyBudget":
        """
        Create a child budget at depth+1.

        This is the J-gent operation for recursive spawning.
        Child budget = 1/(parent_depth + 2) = 1/(child_depth + 1)

        Returns:
            New SharedEntropyBudget at increased depth
        """
        child_depth = self.depth + 1
        child_initial = 1.0 / (child_depth + 1)
        return SharedEntropyBudget(
            depth=child_depth,
            backing=BgentEntropyBudget(initial=child_initial, remaining=child_initial),
            threshold=self.threshold,
        )

    def to_dict(self) -> dict[str, Any]:
        """Serialize for reporting."""
        return {
            "depth": self.depth,
            "initial": self.initial,
            "remaining": self.remaining,
            "threshold": self.threshold,
            "is_exhausted": self.is_exhausted,
            "utilization": 1.0 - (self.remaining / self.initial)
            if self.initial > 0
            else 1.0,
        }


def create_depth_based_budget(
    depth: int = 0,
    threshold: float = 0.1,
) -> SharedEntropyBudget:
    """
    Create a depth-based entropy budget.

    This is the factory function for J-gent usage.

    Args:
        depth: Current recursion depth (0 = root)
        threshold: Budget level below which collapse occurs

    Returns:
        SharedEntropyBudget configured for the given depth

    Example:
        >>> budget = create_depth_based_budget(depth=0)
        >>> budget.remaining
        1.0
        >>> budget = create_depth_based_budget(depth=1)
        >>> budget.remaining
        0.5
        >>> budget = create_depth_based_budget(depth=2)
        >>> abs(budget.remaining - 0.333) < 0.01
        True
    """
    initial = 1.0 / (depth + 1)
    return SharedEntropyBudget(
        depth=depth,
        backing=BgentEntropyBudget(initial=initial, remaining=initial),
        threshold=threshold,
    )


def compute_depth_from_budget(budget: float) -> int:
    """
    Compute equivalent depth from a budget value.

    Inverse of 1/(depth+1).

    Args:
        budget: Budget value (0.0 to 1.0)

    Returns:
        Equivalent depth (0 for budget=1.0, higher for lower budgets)

    Example:
        >>> compute_depth_from_budget(1.0)
        0
        >>> compute_depth_from_budget(0.5)
        1
        >>> compute_depth_from_budget(0.333)
        2
    """
    if budget <= 0:
        return 999  # Effectively infinite depth (exhausted)
    depth = int(1.0 / budget) - 1
    return max(0, depth)


@dataclass
class DualEntropyBudget:
    """
    Dual budget tracking both B-gent economic and J-gent recursion constraints.

    This combines:
    - Economic budget (tokens, gas) from B-gent
    - Recursion budget (depth) from J-gent

    Both must be satisfied for an operation to proceed.
    """

    economic: BgentEntropyBudget
    recursion: SharedEntropyBudget

    def can_proceed(self, economic_cost: float, recursion_cost: float = 0.0) -> bool:
        """
        Check if both budgets allow proceeding.

        Args:
            economic_cost: Cost in economic terms (tokens)
            recursion_cost: Cost in recursion terms (entropy units)

        Returns:
            True if both budgets can afford the costs
        """
        return (
            self.economic.can_afford(economic_cost)
            and self.recursion.can_afford(recursion_cost)
            and not self.recursion.is_exhausted
        )

    def spend(
        self, economic_cost: float, recursion_cost: float = 0.0
    ) -> "DualEntropyBudget":
        """
        Spend from both budgets.

        Args:
            economic_cost: Cost in economic terms
            recursion_cost: Cost in recursion terms

        Returns:
            New DualEntropyBudget with updated values
        """
        return DualEntropyBudget(
            economic=self.economic.consume(economic_cost),
            recursion=self.recursion.consume(recursion_cost),
        )

    def spawn_child_recursion(self) -> "DualEntropyBudget":
        """
        Create a child with increased recursion depth.

        Economic budget is shared, recursion budget is derived.
        """
        return DualEntropyBudget(
            economic=self.economic,
            recursion=self.recursion.spawn_child(),
        )


def create_dual_budget(
    economic_budget: float = 1.0,
    recursion_depth: int = 0,
    threshold: float = 0.1,
) -> DualEntropyBudget:
    """
    Create a dual budget tracking both economic and recursion constraints.

    Args:
        economic_budget: Initial economic budget (0.0 to 1.0)
        recursion_depth: Initial recursion depth
        threshold: Recursion threshold

    Returns:
        Configured DualEntropyBudget
    """
    return DualEntropyBudget(
        economic=BgentEntropyBudget(initial=economic_budget, remaining=economic_budget),
        recursion=create_depth_based_budget(recursion_depth, threshold),
    )
