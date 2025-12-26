"""
Timeline Service: Track coherence score evolution over time.

Provides:
- Coherence score history from witness marks
- Breakthrough moment detection (significant jumps)
- Layer distribution across timeline
- Narrative export ("Tell my story")

Philosophy:
    "Growth is not linear. Breakthroughs are discontinuous."

See: plans/zero-seed-creative-strategy.md (Journey 5: Meta)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from services.k_block.zero_seed_storage import ZeroSeedStorage
    from services.witness.persistence import WitnessPersistence


# =============================================================================
# Types
# =============================================================================


@dataclass
class CoherencePoint:
    """A single point on the coherence timeline."""

    timestamp: datetime
    score: float  # 0.0-1.0
    commit_id: str | None = None
    layer_distribution: dict[int, int] = field(default_factory=dict)
    total_nodes: int = 0
    total_edges: int = 0


@dataclass
class BreakthroughMoment:
    """A significant jump in coherence score."""

    timestamp: datetime
    old_score: float
    new_score: float
    delta: float
    commit_id: str | None = None
    description: str = ""


@dataclass
class CoherenceTimeline:
    """Complete coherence timeline with analytics."""

    points: list[CoherencePoint]
    breakthroughs: list[BreakthroughMoment]
    current_score: float
    average_score: float
    layer_distribution: dict[int, int]  # Total across all time
    total_nodes: int
    total_edges: int
    start_date: datetime | None = None
    end_date: datetime | None = None


# =============================================================================
# TimelineService
# =============================================================================


class TimelineService:
    """
    Service for tracking coherence evolution over time.

    Integrates:
    - ZeroSeedStorage for coherence calculation
    - WitnessPersistence for historical marks
    - Breakthrough detection algorithm

    Example:
        service = TimelineService(storage, witness)
        timeline = await service.get_timeline()
        print(f"Current: {timeline.current_score:.2%}")
        print(f"Breakthroughs: {len(timeline.breakthroughs)}")
    """

    def __init__(
        self,
        storage: ZeroSeedStorage,
        witness: WitnessPersistence | None = None,
    ):
        """
        Initialize TimelineService.

        Args:
            storage: K-Block storage backend for coherence
            witness: Witness persistence for historical marks (optional)
        """
        self._storage = storage
        self._witness = witness

    async def get_timeline(
        self,
        since: datetime | None = None,
        until: datetime | None = None,
    ) -> CoherenceTimeline:
        """
        Get coherence timeline with breakthroughs.

        Args:
            since: Start date (inclusive), or None for all time
            until: End date (inclusive), or None for now

        Returns:
            CoherenceTimeline with points and analytics
        """
        # Get all K-Blocks from storage
        kblocks = list(self._storage._kblocks.values())

        # Calculate current coherence and layer distribution
        current_score = await self._calculate_coherence(kblocks)
        layer_dist = self._calculate_layer_distribution(kblocks)

        # Build coherence points (for now, single snapshot)
        # TODO: In future, query witness marks for historical coherence
        now = datetime.now(timezone.utc)
        points = [
            CoherencePoint(
                timestamp=now,
                score=current_score,
                layer_distribution=layer_dist,
                total_nodes=len(kblocks),
                total_edges=sum(len(kb.edges) for kb in kblocks),
            )
        ]

        # Filter by date range
        if since:
            points = [p for p in points if p.timestamp >= since]
        if until:
            points = [p for p in points if p.timestamp <= until]

        # Detect breakthroughs
        breakthroughs = self._detect_breakthroughs(points)

        # Calculate analytics
        avg_score = sum(p.score for p in points) / len(points) if points else 0.0
        start_date = points[0].timestamp if points else None
        end_date = points[-1].timestamp if points else None

        return CoherenceTimeline(
            points=points,
            breakthroughs=breakthroughs,
            current_score=current_score,
            average_score=avg_score,
            layer_distribution=layer_dist,
            total_nodes=len(kblocks),
            total_edges=sum(len(kb.edges) for kb in kblocks),
            start_date=start_date,
            end_date=end_date,
        )

    async def tell_story(self, timeline: CoherenceTimeline) -> str:
        """
        Generate narrative description of coherence journey.

        Args:
            timeline: CoherenceTimeline to narrate

        Returns:
            Prose description of user's growth journey
        """
        if not timeline.points:
            return "Your journey is just beginning. No coherence data yet."

        # Calculate growth
        if len(timeline.points) > 1:
            start = timeline.points[0].score
            end = timeline.points[-1].score
            growth = end - start
            growth_pct = (growth / start * 100) if start > 0 else 0
        else:
            start = end = timeline.points[0].score
            growth = 0
            growth_pct = 0

        # Build narrative
        story_parts = []

        # Opening
        story_parts.append(
            f"Your journey began on {timeline.start_date.strftime('%B %d, %Y') if timeline.start_date else 'recently'}."
        )

        # Current state
        if timeline.current_score >= 0.8:
            quality = "highly coherent"
        elif timeline.current_score >= 0.6:
            quality = "coherent"
        elif timeline.current_score >= 0.4:
            quality = "developing"
        else:
            quality = "emerging"

        story_parts.append(
            f"Your knowledge garden is {quality}, with a coherence score of {timeline.current_score:.1%}."
        )

        # Growth trajectory
        if growth > 0.1:
            story_parts.append(
                f"You've grown significantly ({growth_pct:+.1f}%), demonstrating systematic refinement."
            )
        elif growth > 0:
            story_parts.append(
                f"You've shown steady growth ({growth_pct:+.1f}%), building foundations carefully."
            )
        elif growth < -0.1:
            story_parts.append(
                f"You've been exploring ({growth_pct:+.1f}%), prioritizing breadth over coherence."
            )
        else:
            story_parts.append(
                "You've maintained steady coherence, balancing exploration and structure."
            )

        # Breakthroughs
        if timeline.breakthroughs:
            story_parts.append(
                f"\n\nYou've had {len(timeline.breakthroughs)} breakthrough moment(s):"
            )
            for i, bt in enumerate(timeline.breakthroughs[:3], 1):  # Top 3
                story_parts.append(
                    f"- {bt.timestamp.strftime('%b %d')}: "
                    f"+{bt.delta:.1%} leap "
                    f"({bt.old_score:.1%} → {bt.new_score:.1%})"
                )

        # Layer distribution insights
        dominant_layer = max(
            timeline.layer_distribution.items(), key=lambda x: x[1], default=(4, 0)
        )[0]
        layer_names = {
            1: "Axioms",
            2: "Values",
            3: "Goals",
            4: "Specifications",
            5: "Actions",
            6: "Reflections",
            7: "Representations",
        }
        story_parts.append(
            f"\n\nYour dominant layer is L{dominant_layer} ({layer_names.get(dominant_layer, 'Unknown')}), "
            f"representing your epistemic center of gravity."
        )

        # Stats
        story_parts.append(
            f"\n\nYou've created {timeline.total_nodes} nodes and {timeline.total_edges} connections."
        )

        # Closing
        story_parts.append("\n\nThe garden grows. The proof IS the journey.")

        return " ".join(story_parts)

    # =========================================================================
    # Private Helpers
    # =========================================================================

    async def _calculate_coherence(self, kblocks: list) -> float:
        """
        Calculate overall coherence score.

        Coherence = 1 - average_loss across all K-Blocks

        Returns:
            Float in range [0.0, 1.0]
        """
        if not kblocks:
            return 0.0

        # Sum all losses
        total_loss = sum(kb.layer_loss for kb in kblocks)
        avg_loss = total_loss / len(kblocks)

        # Coherence is inverse of loss
        coherence = max(0.0, min(1.0, 1.0 - avg_loss))
        return coherence

    def _calculate_layer_distribution(self, kblocks: list) -> dict[int, int]:
        """
        Calculate distribution of K-Blocks across layers.

        Returns:
            Dict mapping layer (1-7) to count
        """
        distribution: dict[int, int] = {}
        for kb in kblocks:
            layer = kb.layer
            distribution[layer] = distribution.get(layer, 0) + 1
        return distribution

    def _detect_breakthroughs(
        self, points: list[CoherencePoint]
    ) -> list[BreakthroughMoment]:
        """
        Detect significant coherence jumps (breakthroughs).

        Breakthrough = delta > 2× average delta

        Args:
            points: Sorted coherence points

        Returns:
            List of BreakthroughMoment instances
        """
        if len(points) < 2:
            return []

        # Calculate deltas
        deltas = [
            points[i].score - points[i - 1].score for i in range(1, len(points))
        ]

        # Calculate average absolute delta
        avg_delta = sum(abs(d) for d in deltas) / len(deltas) if deltas else 0

        # Breakthrough threshold: 2x average
        threshold = avg_delta * 2

        # Find breakthroughs
        breakthroughs: list[BreakthroughMoment] = []
        for i, delta in enumerate(deltas):
            if delta > threshold:
                old_point = points[i]
                new_point = points[i + 1]
                breakthroughs.append(
                    BreakthroughMoment(
                        timestamp=new_point.timestamp,
                        old_score=old_point.score,
                        new_score=new_point.score,
                        delta=delta,
                        commit_id=new_point.commit_id,
                        description=f"Coherence leap: +{delta:.1%}",
                    )
                )

        return breakthroughs
