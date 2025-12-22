"""
Navigation Budget: Bounded exploration resources.

Agents have finite resources for hypergraph exploration:
- max_steps: Total hyperedge traversals allowed
- max_depth: Maximum nesting depth
- max_nodes: Nodes in focus set
- time_budget_ms: Wall clock limit

The budget is consumed as navigation proceeds. When exhausted,
the agent receives a signal with options: return findings, request
extension, or backtrack.

Teaching:
    gotcha: NavigationBudget is immutable—consume() returns a new budget.
            This enables budget sharing/snapshotting without mutation.

    gotcha: Time budget is wall-clock, not CPU. Long I/O operations
            count against it. Design for network-aware budgets.
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from datetime import datetime, timezone
from enum import Enum, auto

from .types import Trail


class ExhaustionReason(str, Enum):
    """Why the budget was exhausted."""

    STEPS = "steps"
    DEPTH = "depth"
    NODES = "nodes"
    TIME = "time"


@dataclass(frozen=True)
class NavigationBudget:
    """
    Resource limits for hypergraph navigation.

    Immutable: consume() returns new budget with updated usage.

    Laws:
        1. Monotonicity: Usage can only increase
        2. Conservation: Budget doesn't regenerate automatically
        3. Transparency: can_navigate() reflects true state
    """

    # Limits
    max_steps: int = 100
    max_depth: int = 10
    max_nodes: int = 50
    time_budget_ms: int = 30000

    # Current usage
    steps_taken: int = 0
    current_depth: int = 0
    nodes_visited: frozenset[str] = field(default_factory=frozenset)
    start_time: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def can_navigate(self) -> bool:
        """Check if we have budget remaining."""
        return self.exhaustion_reason() is None

    def exhaustion_reason(self) -> ExhaustionReason | None:
        """Return why budget is exhausted, or None if still available."""
        elapsed_ms = self._elapsed_ms()

        if self.steps_taken >= self.max_steps:
            return ExhaustionReason.STEPS
        if self.current_depth >= self.max_depth:
            return ExhaustionReason.DEPTH
        if len(self.nodes_visited) >= self.max_nodes:
            return ExhaustionReason.NODES
        if elapsed_ms >= self.time_budget_ms:
            return ExhaustionReason.TIME

        return None

    def consume(self, node_path: str, depth: int) -> NavigationBudget:
        """
        Record a navigation step, returning new budget.

        Args:
            node_path: AGENTESE path of the visited node
            depth: Current navigation depth
        """
        return replace(
            self,
            steps_taken=self.steps_taken + 1,
            current_depth=max(self.current_depth, depth),
            nodes_visited=self.nodes_visited | {node_path},
        )

    def remaining(self) -> dict[str, int | float]:
        """Return remaining budget in each category."""
        elapsed_ms = self._elapsed_ms()
        return {
            "steps": self.max_steps - self.steps_taken,
            "depth": self.max_depth - self.current_depth,
            "nodes": self.max_nodes - len(self.nodes_visited),
            "time_ms": max(0, self.time_budget_ms - elapsed_ms),
        }

    def usage_fraction(self) -> float:
        """
        Overall usage as fraction (0.0 to 1.0).

        Uses max of all resource types—if any is exhausted, we're at 1.0.
        """
        elapsed_ms = self._elapsed_ms()
        fractions = [
            self.steps_taken / self.max_steps if self.max_steps > 0 else 0,
            self.current_depth / self.max_depth if self.max_depth > 0 else 0,
            len(self.nodes_visited) / self.max_nodes if self.max_nodes > 0 else 0,
            elapsed_ms / self.time_budget_ms if self.time_budget_ms > 0 else 0,
        ]
        return min(1.0, max(fractions))

    def extend(
        self,
        steps: int = 0,
        depth: int = 0,
        nodes: int = 0,
        time_ms: int = 0,
    ) -> NavigationBudget:
        """
        Extend the budget (with justification required by caller).

        Returns new budget with extended limits.
        """
        return replace(
            self,
            max_steps=self.max_steps + steps,
            max_depth=self.max_depth + depth,
            max_nodes=self.max_nodes + nodes,
            time_budget_ms=self.time_budget_ms + time_ms,
        )

    def _elapsed_ms(self) -> float:
        """Milliseconds since start."""
        now = datetime.now(timezone.utc)
        return (now - self.start_time).total_seconds() * 1000


@dataclass(frozen=True)
class BudgetExhausted:
    """
    Signal that navigation budget is exhausted.

    Contains information for the agent to decide next steps:
    - Return findings from exploration so far
    - Request budget extension (with justification)
    - Backtrack to a productive node
    """

    reason: ExhaustionReason
    remaining: NavigationBudget
    trail: Trail  # What was explored before exhaustion

    @property
    def message(self) -> str:
        """Human-readable exhaustion message."""
        messages = {
            ExhaustionReason.STEPS: f"Step limit reached ({self.remaining.max_steps} steps)",
            ExhaustionReason.DEPTH: f"Depth limit reached ({self.remaining.max_depth} levels)",
            ExhaustionReason.NODES: f"Node limit reached ({self.remaining.max_nodes} nodes)",
            ExhaustionReason.TIME: f"Time limit reached ({self.remaining.time_budget_ms}ms)",
        }
        return messages.get(self.reason, "Budget exhausted")


# =============================================================================
# Budget Presets
# =============================================================================


def quick_budget() -> NavigationBudget:
    """Quick exploration: shallow, fast."""
    return NavigationBudget(
        max_steps=20,
        max_depth=3,
        max_nodes=15,
        time_budget_ms=5000,
    )


def standard_budget() -> NavigationBudget:
    """Standard exploration budget."""
    return NavigationBudget(
        max_steps=100,
        max_depth=10,
        max_nodes=50,
        time_budget_ms=30000,
    )


def thorough_budget() -> NavigationBudget:
    """Thorough exploration: deep, patient."""
    return NavigationBudget(
        max_steps=500,
        max_depth=20,
        max_nodes=200,
        time_budget_ms=120000,
    )


def unlimited_budget() -> NavigationBudget:
    """Unlimited budget (use with caution)."""
    return NavigationBudget(
        max_steps=999999,
        max_depth=999,
        max_nodes=999999,
        time_budget_ms=3600000,  # 1 hour
    )


__all__ = [
    "NavigationBudget",
    "BudgetExhausted",
    "ExhaustionReason",
    # Presets
    "quick_budget",
    "standard_budget",
    "thorough_budget",
    "unlimited_budget",
]
