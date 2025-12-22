"""
self.grow.nursery - Germinating Holon Management

The nursery holds holons that have passed validation but are not yet
fully promoted. During this phase, they are used experimentally and
their usage patterns are tracked.

AGENTESE: self.grow.nursery
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import TYPE_CHECKING, Any

from ...node import BaseLogosNode, BasicRendering, Renderable
from .exceptions import AffordanceError, NurseryCapacityError
from .schemas import (
    SELF_GROW_AFFORDANCES,
    GerminatingHolon,
    GrowthBudget,
    HolonProposal,
    NurseryConfig,
    ValidationResult,
)
from .telemetry import metrics, tracer

if TYPE_CHECKING:
    from bootstrap.umwelt import Umwelt


# === Nursery Node ===


@dataclass
class NurseryNode(BaseLogosNode):
    """
    self.grow.nursery - Germinating holon management.

    Holds holons that have passed validation but are not yet
    fully promoted.

    Affordances:
    - manifest: View nursery status
    - list: List germinating holons
    - status: Get status of a specific holon
    - stats: Get nursery statistics

    AGENTESE: self.grow.nursery.*
    """

    _handle: str = "self.grow.nursery"

    # Configuration
    _config: NurseryConfig = field(default_factory=NurseryConfig)

    # Budget for entropy tracking
    _budget: GrowthBudget | None = None

    # Germinating holons
    _holons: dict[str, GerminatingHolon] = field(default_factory=dict)

    @property
    def handle(self) -> str:
        return self._handle

    @property
    def count(self) -> int:
        """Current number of germinating holons."""
        return len(self._holons)

    @property
    def active(self) -> list[GerminatingHolon]:
        """Get list of active (not promoted/pruned) holons."""
        return [h for h in self._holons.values() if h.promoted_at is None and h.pruned_at is None]

    @property
    def capacity_pct(self) -> float:
        """Capacity percentage."""
        return (self.count / self._config.max_capacity) * 100

    def _get_affordances_for_archetype(self, archetype: str) -> tuple[str, ...]:
        """All can view nursery; only gardener/architect can germinate."""
        return ("list", "status", "stats")

    async def manifest(self, observer: "Umwelt[Any, Any]", **kwargs: Any) -> Renderable:
        """View nursery status."""
        # Update metrics
        metrics.gauge("growth.nursery.count").set(self.count)
        metrics.gauge("growth.nursery.capacity_pct").set(self.capacity_pct)

        return BasicRendering(
            summary=f"Nursery: {self.count}/{self._config.max_capacity}",
            content=self._format_holons(list(self._holons.values())[:5]),
            metadata={
                "count": self.count,
                "capacity": self._config.max_capacity,
                "capacity_pct": self.capacity_pct,
                "holons": [
                    {
                        "germination_id": h.germination_id,
                        "handle": f"{h.proposal.context}.{h.proposal.entity}",
                        "usage_count": h.usage_count,
                        "success_rate": h.success_rate,
                        "age_days": h.age_days,
                    }
                    for h in list(self._holons.values())[:10]
                ],
            },
        )

    async def _invoke_aspect(
        self,
        aspect: str,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> Any:
        """Handle nursery aspects."""
        match aspect:
            case "list":
                return self._list(**kwargs)
            case "status":
                return self._status(**kwargs)
            case "stats":
                return self._stats()
            case _:
                return {"aspect": aspect, "status": "not implemented"}

    def add(
        self,
        proposal: HolonProposal,
        validation: ValidationResult,
        germinated_by: str,
        jit_source: str = "",
    ) -> GerminatingHolon:
        """
        Add a holon to the nursery.

        Args:
            proposal: The validated proposal
            validation: The validation result
            germinated_by: Observer name who germinated
            jit_source: Optional JIT-compiled source

        Returns:
            GerminatingHolon in the nursery

        Raises:
            NurseryCapacityError: If nursery is full
        """
        # Check capacity
        if self.count >= self._config.max_capacity:
            raise NurseryCapacityError(
                "Nursery at capacity",
                current=self.count,
                max_capacity=self._config.max_capacity,
            )

        # Check per-context limit
        context = proposal.context
        context_count = sum(1 for h in self._holons.values() if h.proposal.context == context)
        if context_count >= self._config.max_per_context:
            raise NurseryCapacityError(
                f"Nursery at capacity for context '{context}'",
                current=context_count,
                max_capacity=self._config.max_per_context,
            )

        # Create germinating holon
        holon = GerminatingHolon(
            germination_id=str(uuid.uuid4()),
            proposal=proposal,
            validation=validation,
            jit_source=jit_source,
            germinated_at=datetime.now(),
            germinated_by=germinated_by,
        )

        self._holons[holon.germination_id] = holon
        return holon

    def remove(self, germination_id: str) -> GerminatingHolon | None:
        """Remove a holon from the nursery."""
        return self._holons.pop(germination_id, None)

    def get(self, germination_id: str) -> GerminatingHolon | None:
        """Get a holon by ID."""
        return self._holons.get(germination_id)

    def get_by_handle(self, handle: str) -> GerminatingHolon | None:
        """Get a holon by its handle."""
        for holon in self._holons.values():
            if f"{holon.proposal.context}.{holon.proposal.entity}" == handle:
                return holon
        return None

    def record_usage(
        self,
        germination_id: str,
        success: bool,
        failure_pattern: str | None = None,
    ) -> None:
        """Record usage of a germinating holon."""
        holon = self._holons.get(germination_id)
        if holon is None:
            return

        holon.usage_count += 1
        if success:
            holon.success_count += 1
        elif failure_pattern:
            holon.failure_patterns.append(failure_pattern)

    def get_ready_for_promotion(self) -> list[GerminatingHolon]:
        """Get holons ready for promotion."""
        return [h for h in self._holons.values() if h.should_promote(self._config)]

    def get_ready_for_pruning(self) -> list[GerminatingHolon]:
        """Get holons ready for pruning."""
        return [h for h in self._holons.values() if h.should_prune(self._config)]

    def _list(self, **kwargs: Any) -> dict[str, Any]:
        """List germinating holons."""
        limit = kwargs.get("limit", 20)
        context = kwargs.get("context")

        holons = list(self._holons.values())
        if context:
            holons = [h for h in holons if h.proposal.context == context]

        return {
            "holons": [
                {
                    "germination_id": h.germination_id,
                    "handle": f"{h.proposal.context}.{h.proposal.entity}",
                    "usage_count": h.usage_count,
                    "success_rate": h.success_rate,
                    "age_days": h.age_days,
                    "should_promote": h.should_promote(self._config),
                    "should_prune": h.should_prune(self._config),
                }
                for h in holons[:limit]
            ],
            "total": len(holons),
        }

    def _status(self, **kwargs: Any) -> dict[str, Any]:
        """Get status of a specific holon."""
        germination_id = kwargs.get("germination_id")
        handle = kwargs.get("handle")

        if germination_id:
            holon = self.get(germination_id)
        elif handle:
            holon = self.get_by_handle(handle)
        else:
            return {"error": "germination_id or handle required"}

        if holon is None:
            return {"error": "Holon not found"}

        return {
            "germination_id": holon.germination_id,
            "handle": f"{holon.proposal.context}.{holon.proposal.entity}",
            "usage_count": holon.usage_count,
            "success_count": holon.success_count,
            "success_rate": holon.success_rate,
            "failure_patterns": holon.failure_patterns[-5:],  # Last 5
            "age_days": holon.age_days,
            "germinated_by": holon.germinated_by,
            "germinated_at": holon.germinated_at.isoformat(),
            "promoted_at": holon.promoted_at.isoformat() if holon.promoted_at else None,
            "pruned_at": holon.pruned_at.isoformat() if holon.pruned_at else None,
            "should_promote": holon.should_promote(self._config),
            "should_prune": holon.should_prune(self._config),
        }

    def _stats(self) -> dict[str, Any]:
        """Get nursery statistics."""
        by_context: dict[str, int] = {}
        total_usage = 0
        total_success = 0
        ages: list[int] = []

        for holon in self._holons.values():
            context = holon.proposal.context
            by_context[context] = by_context.get(context, 0) + 1
            total_usage += holon.usage_count
            total_success += holon.success_count
            ages.append(holon.age_days)

        return {
            "count": self.count,
            "capacity": self._config.max_capacity,
            "capacity_pct": self.capacity_pct,
            "by_context": by_context,
            "total_usage": total_usage,
            "total_success": total_success,
            "overall_success_rate": total_success / max(total_usage, 1),
            "avg_age_days": sum(ages) / max(len(ages), 1),
            "ready_for_promotion": len(self.get_ready_for_promotion()),
            "ready_for_pruning": len(self.get_ready_for_pruning()),
        }

    def _format_holons(self, holons: list[GerminatingHolon]) -> str:
        """Format holons for display."""
        if not holons:
            return "Nursery is empty"

        lines = []
        for h in holons:
            lines.append(
                f"  {h.proposal.context}.{h.proposal.entity}"
                + f" usage={h.usage_count}"
                + f" success={h.success_rate:.1%}"
                + f" age={h.age_days}d"
            )
        return "\n".join(lines)


# === Factory ===


def create_nursery_node(
    config: NurseryConfig | None = None,
    budget: GrowthBudget | None = None,
) -> NurseryNode:
    """
    Create a NurseryNode with optional configuration.

    Args:
        config: Nursery configuration
        budget: Growth budget for entropy tracking

    Returns:
        Configured NurseryNode
    """
    return NurseryNode(
        _config=config or NurseryConfig(),
        _budget=budget,
    )
