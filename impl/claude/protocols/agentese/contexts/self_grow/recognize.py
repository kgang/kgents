"""
self.grow.recognize - Gap Recognition

Scans for ontological gaps - places where the current taxonomy
fails to capture needed distinctions.

AGENTESE: self.grow.recognize
"""

from __future__ import annotations

import uuid
from collections import defaultdict
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from ...node import BaseLogosNode, BasicRendering, Renderable
from .exceptions import AffordanceError, BudgetExhaustedError
from .schemas import (
    SELF_GROW_AFFORDANCES,
    GapRecognition,
    GrowthBudget,
    GrowthRelevantError,
    RecognitionQuery,
)
from .telemetry import metrics, tracer

if TYPE_CHECKING:
    from bootstrap.umwelt import Umwelt

    from ...logos import Logos


# === Gap Clustering ===


def cluster_errors_into_gaps(
    errors: list[GrowthRelevantError],
    seed: int | None = None,
) -> list[GapRecognition]:
    """
    Cluster errors into gap recognitions.

    Groups errors by (context, holon, aspect) and computes confidence
    based on evidence count and archetype diversity.

    Args:
        errors: List of relevant errors to cluster
        seed: Optional random seed for reproducibility

    Returns:
        List of gap recognitions sorted by confidence
    """
    # Group by location
    groups: dict[tuple[str, str, str | None], list[GrowthRelevantError]] = defaultdict(list)

    for error in errors:
        key = (error.context, error.holon, error.aspect)
        groups[key].append(error)

    # Create gaps from groups
    gaps = []
    for (context, holon, aspect), group_errors in groups.items():
        # Compute archetype diversity
        archetypes = set(e.observer_archetype for e in group_errors)

        # Compute confidence
        evidence_count = sum(e.occurrence_count for e in group_errors)
        archetype_diversity = len(archetypes)

        # Confidence formula:
        # - Base: 0.3
        # - +0.1 per 5 occurrences (max 0.3)
        # - +0.1 per archetype (max 0.3)
        # - +0.1 if suggestions available
        base = 0.3
        occurrence_bonus = min(0.3, (evidence_count // 5) * 0.1)
        diversity_bonus = min(0.3, archetype_diversity * 0.1)
        suggestion_bonus = 0.1 if any(e.suggestion for e in group_errors) else 0.0

        confidence = base + occurrence_bonus + diversity_bonus + suggestion_bonus

        # Determine gap type
        if aspect:
            gap_type = "missing_affordance"
        else:
            gap_type = "missing_holon"

        # Extract pattern
        pattern = group_errors[0].attempted_path if group_errors else f"{context}.{holon}"

        gap = GapRecognition(
            gap_id=str(uuid.uuid4()),
            context=context,
            holon=holon,
            aspect=aspect,
            pattern=pattern,
            evidence=group_errors,
            evidence_count=evidence_count,
            archetype_diversity=archetype_diversity,
            confidence=confidence,
            confidence_factors={
                "base": base,
                "occurrence_bonus": occurrence_bonus,
                "diversity_bonus": diversity_bonus,
                "suggestion_bonus": suggestion_bonus,
            },
            gap_type=gap_type,  # type: ignore[arg-type]
        )
        gaps.append(gap)

    # Sort by confidence
    gaps.sort(key=lambda g: g.confidence, reverse=True)
    return gaps


async def find_analogues(
    gap: GapRecognition,
    logos: "Logos | None" = None,
) -> list[str]:
    """
    Find similar holons that might suggest structure.

    Args:
        gap: The gap to find analogues for
        logos: Optional Logos instance for registry lookup

    Returns:
        List of analogous handles
    """
    analogues = []

    if logos is None:
        return analogues

    try:
        # Get holons in same context
        result = await logos.invoke("world.registry.list", None, context=gap.context)
        if isinstance(result, list):
            # Simple string matching for analogues
            for handle in result:
                entity = handle.split(".")[-1] if "." in handle else handle
                # Check for common prefixes or suffixes
                if (
                    entity.startswith(gap.holon[:3])
                    or entity.endswith(gap.holon[-3:])
                    or gap.holon in entity
                    or entity in gap.holon
                ):
                    analogues.append(handle)
    except Exception:
        pass

    return analogues[:5]  # Max 5 analogues


# === Recognition Node ===


@dataclass
class RecognizeNode(BaseLogosNode):
    """
    self.grow.recognize - Gap recognition node.

    Scans for ontological gaps using error stream analysis.

    Affordances:
    - manifest: View recent gaps (read-only)
    - scan: Run gap recognition scan
    - history: View recognition history

    AGENTESE: self.grow.recognize.*
    """

    _handle: str = "self.grow.recognize"

    # Integration points
    _logos: "Logos | None" = None
    _budget: GrowthBudget | None = None

    # Error stream (injected for testing, or fetched from telemetry)
    _error_stream: list[GrowthRelevantError] = field(default_factory=list)

    # Cache of recognized gaps
    _recognized_gaps: list[GapRecognition] = field(default_factory=list)

    @property
    def handle(self) -> str:
        return self._handle

    def _get_affordances_for_archetype(self, archetype: str) -> tuple[str, ...]:
        """Recognition requires gardener or architect affordance."""
        affordances = SELF_GROW_AFFORDANCES.get(archetype, ())
        if "recognize" in affordances:
            return ("scan", "history")
        return ("history",)  # Read-only for others

    async def manifest(self, observer: "Umwelt[Any, Any]") -> Renderable:
        """View recognized gaps."""
        return BasicRendering(
            summary=f"Recognized Gaps: {len(self._recognized_gaps)}",
            content=self._format_gaps(self._recognized_gaps[:5]),
            metadata={
                "gap_count": len(self._recognized_gaps),
                "gaps": [
                    {
                        "gap_id": g.gap_id,
                        "handle": f"{g.context}.{g.holon}",
                        "confidence": g.confidence,
                        "evidence_count": g.evidence_count,
                    }
                    for g in self._recognized_gaps[:10]
                ],
            },
        )

    async def _invoke_aspect(
        self,
        aspect: str,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> Any:
        """Handle recognition aspects."""
        match aspect:
            case "scan":
                return await self._scan(observer, **kwargs)
            case "history":
                return self._get_history(**kwargs)
            case _:
                return {"aspect": aspect, "status": "not implemented"}

    async def _scan(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Run gap recognition scan.

        Args:
            query: Optional RecognitionQuery (uses defaults if not provided)

        Returns:
            Dict with recognized gaps
        """
        meta = self._umwelt_to_meta(observer)

        # Check affordance
        if "recognize" not in SELF_GROW_AFFORDANCES.get(meta.archetype, ()):
            raise AffordanceError(
                f"Archetype '{meta.archetype}' cannot recognize gaps",
                available=SELF_GROW_AFFORDANCES.get(meta.archetype, ()),
            )

        # Get query
        query = kwargs.get("query") or RecognitionQuery()

        # Check budget
        if self._budget is not None:
            if self._budget.remaining < query.max_entropy_cost:
                raise BudgetExhaustedError(
                    f"Recognition requires {query.max_entropy_cost} entropy, "
                    f"only {self._budget.remaining} available",
                    remaining=self._budget.remaining,
                    requested=query.max_entropy_cost,
                )
            self._budget.spend("recognize")

        # Start span
        async with tracer.start_span_async("growth.recognize") as span:
            span.set_attribute("growth.phase", "recognize")
            span.set_attribute("growth.entropy.spent", query.max_entropy_cost)

            # Filter errors
            filtered_errors = [
                e
                for e in self._error_stream
                if e.error_type in query.error_types
                and not any(p in e.attempted_path for p in query.exclude_patterns)
            ]
            span.set_attribute("growth.recognize.errors_scanned", len(filtered_errors))

            # Cluster into gaps
            gaps = cluster_errors_into_gaps(filtered_errors)

            # Filter by confidence
            confident_gaps = [g for g in gaps if g.confidence >= 0.6]

            # Find analogues for each gap
            for gap in confident_gaps:
                gap.analogues = await find_analogues(gap, self._logos)

            # Update cache
            self._recognized_gaps = confident_gaps[: query.max_gaps_returned]

            # Record metrics
            metrics.counter("growth.recognize.invocations").add(1)
            metrics.counter("growth.recognize.gaps_found").add(len(self._recognized_gaps))
            span.set_attribute("growth.recognize.gaps_found", len(self._recognized_gaps))

        return {
            "status": "scanned",
            "gaps_found": len(self._recognized_gaps),
            "gaps": [
                {
                    "gap_id": g.gap_id,
                    "handle": f"{g.context}.{g.holon}",
                    "aspect": g.aspect,
                    "confidence": g.confidence,
                    "evidence_count": g.evidence_count,
                    "gap_type": g.gap_type,
                    "analogues": g.analogues,
                }
                for g in self._recognized_gaps
            ],
            "entropy_spent": query.max_entropy_cost,
        }

    def _get_history(self, **kwargs: Any) -> dict[str, Any]:
        """Get recognition history."""
        limit = kwargs.get("limit", 20)
        return {
            "gaps": [
                {
                    "gap_id": g.gap_id,
                    "handle": f"{g.context}.{g.holon}",
                    "confidence": g.confidence,
                    "evidence_count": g.evidence_count,
                    "gap_type": g.gap_type,
                }
                for g in self._recognized_gaps[:limit]
            ],
            "total": len(self._recognized_gaps),
        }

    def _format_gaps(self, gaps: list[GapRecognition]) -> str:
        """Format gaps for display."""
        if not gaps:
            return "No gaps recognized"

        lines = []
        for gap in gaps:
            lines.append(
                f"  {gap.context}.{gap.holon}"
                + (f".{gap.aspect}" if gap.aspect else "")
                + f" [{gap.gap_type}]"
                + f" confidence={gap.confidence:.2f}"
                + f" evidence={gap.evidence_count}"
            )
        return "\n".join(lines)


# === Factory ===


def create_recognize_node(
    logos: "Logos | None" = None,
    budget: GrowthBudget | None = None,
    error_stream: list[GrowthRelevantError] | None = None,
) -> RecognizeNode:
    """
    Create a RecognizeNode with optional configuration.

    Args:
        logos: Logos instance for registry lookup
        budget: Growth budget for entropy tracking
        error_stream: Error stream for gap recognition (for testing)

    Returns:
        Configured RecognizeNode
    """
    return RecognizeNode(
        _logos=logos,
        _budget=budget,
        _error_stream=error_stream or [],
    )
