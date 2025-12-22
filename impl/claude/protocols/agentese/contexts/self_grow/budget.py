"""
self.grow.budget - Growth Entropy Budget Management

Tracks and manages the entropy budget for growth operations.

AGENTESE: self.grow.budget
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from ...node import BaseLogosNode, BasicRendering, Renderable
from .schemas import SELF_GROW_AFFORDANCES, GrowthBudget, GrowthBudgetConfig

if TYPE_CHECKING:
    from bootstrap.umwelt import Umwelt


@dataclass
class BudgetNode(BaseLogosNode):
    """
    self.grow.budget - Growth entropy budget management.

    Affordances:
    - status: View current budget (all archetypes)
    - history: View spending history (all archetypes)
    - regenerate: Force regeneration (gardener/admin only)

    AGENTESE: self.grow.budget.*
    """

    _handle: str = "self.grow.budget"
    _budget: GrowthBudget = field(default_factory=GrowthBudget)

    @property
    def handle(self) -> str:
        return self._handle

    def _get_affordances_for_archetype(self, archetype: str) -> tuple[str, ...]:
        """All can view; only gardener/admin can force regenerate."""
        if archetype in ("gardener", "admin"):
            return ("status", "history", "regenerate")
        return ("status", "history")

    async def manifest(self, observer: "Umwelt[Any, Any]", **kwargs: Any) -> Renderable:
        """View budget status."""
        self._budget.regenerate()  # Apply pending regeneration

        pct = int(self._budget.remaining / self._budget.config.max_entropy_per_run * 100)

        return BasicRendering(
            summary=f"Growth Budget: {pct}%",
            content=(
                f"Remaining: {self._budget.remaining:.2f} / {self._budget.config.max_entropy_per_run}\n"
                f"Spent this run: {self._budget.spent_this_run:.2f}\n"
                f"Regeneration rate: {self._budget.config.regeneration_rate_per_hour}/hour"
            ),
            metadata=self._budget.status(),
        )

    async def _invoke_aspect(
        self,
        aspect: str,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> Any:
        """Handle budget-specific aspects."""
        match aspect:
            case "status":
                self._budget.regenerate()
                return self._budget.status()

            case "history":
                return {
                    "spent_by_operation": dict(self._budget.spent_by_operation),
                    "spent_this_run": self._budget.spent_this_run,
                    "last_regeneration": self._budget.last_regeneration.isoformat(),
                }

            case "regenerate":
                # Check affordance
                meta = self._umwelt_to_meta(observer)
                if meta.archetype not in ("gardener", "admin"):
                    return {
                        "error": f"Archetype '{meta.archetype}' cannot force regenerate",
                        "available": SELF_GROW_AFFORDANCES.get(meta.archetype, ()),
                    }

                # Force full regeneration
                old = self._budget.remaining
                self._budget.remaining = self._budget.config.max_entropy_per_run
                self._budget.spent_this_run = 0.0
                self._budget.spent_by_operation.clear()

                return {
                    "status": "regenerated",
                    "previous": old,
                    "current": self._budget.remaining,
                }

            case _:
                return {"aspect": aspect, "status": "not implemented"}


def create_budget_node(
    config: GrowthBudgetConfig | None = None,
    initial_budget: float | None = None,
) -> BudgetNode:
    """
    Create a BudgetNode with optional configuration.

    Args:
        config: Budget configuration (defaults to GrowthBudgetConfig())
        initial_budget: Initial budget amount (defaults to config.max_entropy_per_run)

    Returns:
        Configured BudgetNode
    """
    config = config or GrowthBudgetConfig()
    budget = GrowthBudget(config=config)
    if initial_budget is not None:
        budget.remaining = initial_budget
    return BudgetNode(_budget=budget)
