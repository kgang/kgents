"""
self.grow.prune - Holon Pruning (Composting)

Removes failed or stale holons from the nursery, extracting
learnings to improve future proposals.

AGENTESE: self.grow.prune
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import TYPE_CHECKING, Any

from ...node import BaseLogosNode, BasicRendering, Renderable
from .exceptions import AffordanceError
from .nursery import NurseryNode
from .schemas import (
    SELF_GROW_AFFORDANCES,
    GerminatingHolon,
    GrowthBudget,
)
from .telemetry import metrics, tracer

if TYPE_CHECKING:
    from bootstrap.umwelt import Umwelt


# === Compost Schemas ===


@dataclass
class CompostEntry:
    """Record of a pruned holon for learning."""

    handle: str
    germination_id: str
    pruned_at: datetime
    reason: str

    # Usage stats at time of pruning
    usage_count: int
    success_rate: float
    age_days: int

    # Failure patterns
    failure_patterns: list[str]

    # Lessons learned (extracted from failures)
    lessons: list[str] = field(default_factory=list)


# === Prune Node ===


@dataclass
class PruneNode(BaseLogosNode):
    """
    self.grow.prune - Holon pruning (composting) node.

    Removes failed or stale holons from the nursery,
    extracting learnings to improve future proposals.

    Affordances:
    - manifest: View pruning status
    - sweep: Prune all eligible holons
    - compost: View compost pile (pruned holons)
    - learn: Extract lessons from compost

    AGENTESE: self.grow.prune.*
    """

    _handle: str = "self.grow.prune"

    # Integration points
    _budget: GrowthBudget | None = None
    _nursery: NurseryNode | None = None

    # Compost pile (pruned holons)
    _compost: list[CompostEntry] = field(default_factory=list)

    @property
    def handle(self) -> str:
        return self._handle

    def _get_affordances_for_archetype(self, archetype: str) -> tuple[str, ...]:
        """Pruning requires gardener or admin affordance."""
        affordances = SELF_GROW_AFFORDANCES.get(archetype, ())
        if "prune" in affordances:
            return ("sweep", "compost", "learn", "remove")
        return ("compost",)  # Read-only for others

    async def manifest(self, observer: "Umwelt[Any, Any]", **kwargs: Any) -> Renderable:
        """View pruning status."""
        ready = []
        if self._nursery is not None:
            ready = self._nursery.get_ready_for_pruning()

        return BasicRendering(
            summary=f"Pruning: {len(ready)} ready, {len(self._compost)} composted",
            content=self._format_ready(ready[:5]),
            metadata={
                "ready_count": len(ready),
                "compost_count": len(self._compost),
                "ready": [
                    {
                        "handle": f"{h.proposal.context}.{h.proposal.entity}",
                        "success_rate": h.success_rate,
                        "age_days": h.age_days,
                    }
                    for h in ready[:10]
                ],
            },
        )

    async def _invoke_aspect(
        self,
        aspect: str,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> Any:
        """Handle pruning aspects."""
        match aspect:
            case "sweep":
                return await self._sweep(observer, **kwargs)
            case "compost":
                return self._get_compost(**kwargs)
            case "learn":
                return self._extract_lessons(**kwargs)
            case "remove":
                return await self._remove(observer, **kwargs)
            case _:
                return {"aspect": aspect, "status": "not implemented"}

    async def _sweep(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Prune all eligible holons.

        Args:
            force: If True, prune all regardless of thresholds

        Returns:
            Dict with pruning results
        """
        meta = self._umwelt_to_meta(observer)

        # Check affordance
        if "prune" not in SELF_GROW_AFFORDANCES.get(meta.archetype, ()):
            raise AffordanceError(
                f"Archetype '{meta.archetype}' cannot prune",
                available=SELF_GROW_AFFORDANCES.get(meta.archetype, ()),
            )

        # Check nursery
        if self._nursery is None:
            return {"error": "Nursery not configured"}

        force = kwargs.get("force", False)

        async with tracer.start_span_async("growth.prune") as span:
            span.set_attribute("growth.phase", "prune")
            span.set_attribute("growth.prune.force", force)

            # Get holons ready for pruning
            if force:
                ready = list(self._nursery._holons.values())
            else:
                ready = self._nursery.get_ready_for_pruning()

            pruned = []
            for holon in ready:
                # Determine reason
                if holon.age_days > self._nursery._config.max_age_days:
                    reason = f"Too old ({holon.age_days} days)"
                elif holon.success_rate < self._nursery._config.min_success_rate_for_survival:
                    reason = f"Low success rate ({holon.success_rate:.1%})"
                elif force:
                    reason = "Force pruned"
                else:
                    reason = "Unknown"

                # Create compost entry
                entry = self._create_compost_entry(holon, reason)
                self._compost.append(entry)
                pruned.append(entry)

                # Remove from nursery
                self._nursery.remove(holon.germination_id)

                # Spend entropy
                if self._budget is not None and self._budget.can_afford("prune"):
                    self._budget.spend("prune")

            span.set_attribute("growth.prune.count", len(pruned))

            # Record metrics
            metrics.counter("growth.prune.invocations").add(1)
            metrics.gauge("growth.nursery.count").set(self._nursery.count)

        return {
            "status": "swept",
            "pruned_count": len(pruned),
            "pruned": [
                {
                    "handle": e.handle,
                    "reason": e.reason,
                    "success_rate": e.success_rate,
                    "age_days": e.age_days,
                }
                for e in pruned
            ],
            "nursery_count": self._nursery.count,
        }

    async def _remove(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Remove a specific holon.

        Args:
            germination_id: ID of holon to remove
            handle: Handle of holon to remove
            reason: Reason for removal

        Returns:
            Dict with removal result
        """
        meta = self._umwelt_to_meta(observer)

        # Check affordance
        if "prune" not in SELF_GROW_AFFORDANCES.get(meta.archetype, ()):
            raise AffordanceError(
                f"Archetype '{meta.archetype}' cannot prune",
                available=SELF_GROW_AFFORDANCES.get(meta.archetype, ()),
            )

        # Check nursery
        if self._nursery is None:
            return {"error": "Nursery not configured"}

        germination_id = kwargs.get("germination_id")
        handle = kwargs.get("handle")
        reason = kwargs.get("reason", "Manually removed")

        # Find holon
        holon: GerminatingHolon | None = None
        if germination_id:
            holon = self._nursery.get(germination_id)
        elif handle:
            holon = self._nursery.get_by_handle(handle)

        if holon is None:
            return {"error": "Holon not found"}

        # Create compost entry
        entry = self._create_compost_entry(holon, reason)
        self._compost.append(entry)

        # Remove from nursery
        self._nursery.remove(holon.germination_id)

        return {
            "status": "removed",
            "handle": entry.handle,
            "reason": reason,
            "nursery_count": self._nursery.count,
        }

    def _get_compost(self, **kwargs: Any) -> dict[str, Any]:
        """Get compost pile."""
        limit = kwargs.get("limit", 20)

        return {
            "compost": [
                {
                    "handle": e.handle,
                    "pruned_at": e.pruned_at.isoformat(),
                    "reason": e.reason,
                    "success_rate": e.success_rate,
                    "age_days": e.age_days,
                    "failure_count": len(e.failure_patterns),
                    "lessons": e.lessons,
                }
                for e in self._compost[-limit:]
            ],
            "total": len(self._compost),
        }

    def _extract_lessons(self, **kwargs: Any) -> dict[str, Any]:
        """
        Extract lessons from the compost pile.

        Analyzes failure patterns to generate insights.
        """
        if not self._compost:
            return {"lessons": [], "note": "Compost pile is empty"}

        # Aggregate failure patterns
        pattern_counts: dict[str, int] = {}
        for entry in self._compost:
            for pattern in entry.failure_patterns:
                pattern_counts[pattern] = pattern_counts.get(pattern, 0) + 1

        # Sort by frequency
        sorted_patterns = sorted(
            pattern_counts.items(),
            key=lambda x: x[1],
            reverse=True,
        )

        # Generate lessons
        lessons = []
        for pattern, count in sorted_patterns[:10]:
            if count >= 2:
                lessons.append(
                    {
                        "pattern": pattern,
                        "occurrences": count,
                        "lesson": self._pattern_to_lesson(pattern),
                    }
                )

        # Calculate aggregate stats
        total_usage = sum(e.usage_count for e in self._compost)
        avg_success_rate = sum(e.success_rate for e in self._compost) / len(self._compost)
        avg_age = sum(e.age_days for e in self._compost) / len(self._compost)

        return {
            "lessons": lessons,
            "stats": {
                "total_pruned": len(self._compost),
                "total_usage": total_usage,
                "avg_success_rate": avg_success_rate,
                "avg_age_days": avg_age,
            },
        }

    def _create_compost_entry(
        self,
        holon: GerminatingHolon,
        reason: str,
    ) -> CompostEntry:
        """Create a compost entry from a holon."""
        handle = f"{holon.proposal.context}.{holon.proposal.entity}"

        # Extract lessons from failure patterns
        lessons = [self._pattern_to_lesson(p) for p in holon.failure_patterns[:5] if p]

        return CompostEntry(
            handle=handle,
            germination_id=holon.germination_id,
            pruned_at=datetime.now(),
            reason=reason,
            usage_count=holon.usage_count,
            success_rate=holon.success_rate,
            age_days=holon.age_days,
            failure_patterns=holon.failure_patterns,
            lessons=lessons,
        )

    def _pattern_to_lesson(self, pattern: str) -> str:
        """Convert a failure pattern to a lesson."""
        pattern_lower = pattern.lower()

        if "affordance" in pattern_lower:
            return "Consider expanding affordances for more archetypes"
        elif "observer" in pattern_lower:
            return "Ensure observer context is properly handled"
        elif "composition" in pattern_lower:
            return "Review composition relations for consistency"
        elif "timeout" in pattern_lower:
            return "Consider adding timeout handling"
        elif "not found" in pattern_lower:
            return "Check dependencies exist before invocation"
        else:
            return f"Investigate pattern: {pattern[:50]}..."

    def _format_ready(self, holons: list[GerminatingHolon]) -> str:
        """Format ready-for-pruning holons for display."""
        if not holons:
            return "No holons ready for pruning"

        lines = []
        for h in holons:
            lines.append(
                f"  {h.proposal.context}.{h.proposal.entity}"
                + f" success={h.success_rate:.1%}"
                + f" age={h.age_days}d"
            )
        return "\n".join(lines)


# === Factory ===


def create_prune_node(
    budget: GrowthBudget | None = None,
    nursery: NurseryNode | None = None,
) -> PruneNode:
    """
    Create a PruneNode with optional configuration.

    Args:
        budget: Growth budget for entropy tracking
        nursery: NurseryNode for holon lookup

    Returns:
        Configured PruneNode
    """
    return PruneNode(
        _budget=budget,
        _nursery=nursery,
    )
