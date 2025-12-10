"""
M-gent ContextInjector.

THE ANSWER TO: "What is the most perfect context injection
that can be given to an agent for any given turn?"

Uses the HoloMap to produce a foveated, budget-constrained view
of the agent's semantic space.

Key Insight:
We don't dump everything relevant into context.
We show a FOVEATED rendering that respects the budget.
Like human vision: sharp in center, blurry at edges.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import TYPE_CHECKING, Callable

from .cartography import (
    Attractor,
    ContextVector,
    FoveatedView,
    Goal,
    HoloMap,
    Horizon,
    InjectionRequest,
    OptimalContext,
    Void,
    WeightedEdge,
)

if TYPE_CHECKING:
    from .cartographer import CartographerAgent
    from .pathfinder import PathfinderAgent


# ============================================================================
# Context Injector Configuration
# ============================================================================


@dataclass
class InjectorConfig:
    """Configuration for ContextInjector."""

    # Resolution thresholds
    focal_threshold: float = 0.7  # Resolution above this = focal zone
    blur_threshold: float = 0.3  # Resolution below this = omit

    # Token costs (approximate)
    tokens_per_landmark_full: int = 100  # Full detail landmark
    tokens_per_landmark_blur: int = 30  # Summary landmark
    tokens_per_edge: int = 15  # Desire line hint
    tokens_per_void: int = 20  # Void warning

    # Content generation
    include_position: bool = True
    include_focal: bool = True
    include_peripheral: bool = True
    include_paths: bool = True
    include_voids: bool = True

    # Summary generation
    summary_max_length: int = 50  # Characters for blur summaries


# ============================================================================
# ContextInjector
# ============================================================================


class ContextInjector:
    """
    THE ANSWER TO: "What is the most perfect context injection
    that can be given to an agent for any given turn?"

    Uses the HoloMap to select:
    1. WHERE the agent is (current landmark)
    2. WHERE the agent is going (goal landmarks)
    3. WHAT paths exist (desire lines)
    4. WHAT to avoid (voids)
    5. HOW MUCH to show (budget-constrained foveation)
    """

    def __init__(
        self,
        cartographer: CartographerAgent | None = None,
        pathfinder: PathfinderAgent | None = None,
        config: InjectorConfig | None = None,
        memory_renderer: Callable[[str], str] | None = None,
    ):
        self.cartographer = cartographer
        self.pathfinder = pathfinder
        self.config = config or InjectorConfig()
        self.memory_renderer = memory_renderer or self._default_renderer

    async def invoke(
        self,
        request: InjectionRequest,
        holo_map: HoloMap | None = None,
    ) -> OptimalContext:
        """
        Produce optimal, budget-constrained context for injection.

        Args:
            request: Injection request with context, goal, and budget
            holo_map: Optional pre-computed map

        Returns:
            OptimalContext with foveated view of semantic space
        """
        # Get or generate map
        if holo_map is None:
            if self.cartographer is not None:
                holo_map = await self.cartographer.invoke(
                    request.current_context,
                    budget_tokens=request.budget_tokens,
                )
            else:
                # No cartographer, return minimal context
                return OptimalContext(
                    position="Position unknown (no map available)",
                    focal_memories=[],
                    peripheral_summaries=[],
                    desire_lines=[],
                    void_warnings=[],
                    tokens_used=0,
                    tokens_remaining=request.budget_tokens,
                )

        # Find relevant landmarks
        if request.goal is not None and self.pathfinder is not None:
            # Use pathfinder to determine relevant landmarks
            goal = Goal(
                current_context=request.current_context,
                target=request.goal,
            )
            plan = await self.pathfinder.invoke(goal, holo_map)
            relevant_landmarks = plan.waypoints
        else:
            # No specific goal - show adjacent territory
            relevant_landmarks = self._get_adjacent_landmarks(
                request.current_context, holo_map
            )

        # Apply foveation (budget-constrained detail)
        foveated = self._foveate(
            landmarks=relevant_landmarks,
            origin=request.current_context,
            horizon=holo_map.horizon,
            budget=request.budget_tokens,
        )

        # Render to context
        return self._render_context(
            foveated=foveated,
            holo_map=holo_map,
            request=request,
        )

    def _get_adjacent_landmarks(
        self,
        context: ContextVector,
        holo_map: HoloMap,
    ) -> list[Attractor]:
        """Get landmarks adjacent to current context."""
        # Start with nearest landmark
        nearest = holo_map.nearest_landmark(context)
        if nearest is None:
            return []

        # Get connected landmarks via desire lines
        adjacent = holo_map.adjacent_to(context)

        # Also include landmarks in focal zone
        focal = holo_map.get_focal_landmarks(threshold=self.config.focal_threshold)

        # Combine, dedup, sort by distance
        all_landmarks = {l.id: l for l in [nearest] + adjacent + focal}
        landmarks = list(all_landmarks.values())

        # Sort by distance to context
        landmarks.sort(key=lambda l: l.distance_to(context.embedding))

        return landmarks

    def _foveate(
        self,
        landmarks: list[Attractor],
        origin: ContextVector,
        horizon: Horizon,
        budget: int,
    ) -> FoveatedView:
        """
        Apply foveation: Full detail near origin, blur at distance.

        This is the key innovation—we don't dump everything into context.
        We show a FOVEATED rendering that respects the budget.
        """
        focal_zone: list[tuple[Attractor, float]] = []
        blur_zone: list[tuple[Attractor, float]] = []
        tokens_used = 0

        # Sort by distance from origin
        sorted_landmarks = sorted(
            landmarks,
            key=lambda l: self._distance(origin, l.centroid),
        )

        for landmark in sorted_landmarks:
            distance = self._distance(origin, landmark.centroid)
            resolution = horizon.resolution_at(distance)

            # Skip if below blur threshold
            if resolution < self.config.blur_threshold:
                continue

            # Estimate token cost at this resolution
            if resolution >= self.config.focal_threshold:
                token_cost = self.config.tokens_per_landmark_full
            else:
                token_cost = self.config.tokens_per_landmark_blur

            # Check budget
            if tokens_used + token_cost > budget:
                break  # Budget exhausted

            # Add to appropriate zone
            if resolution >= self.config.focal_threshold:
                focal_zone.append((landmark, resolution))
            else:
                blur_zone.append((landmark, resolution))

            tokens_used += token_cost

        return FoveatedView(
            focal_zone=focal_zone,
            blur_zone=blur_zone,
            tokens_used=tokens_used,
        )

    def _render_context(
        self,
        foveated: FoveatedView,
        holo_map: HoloMap,
        request: InjectionRequest,
    ) -> OptimalContext:
        """Render foveated view to context strings."""
        tokens_used = foveated.tokens_used

        # Position
        position = ""
        if self.config.include_position:
            position = self._render_position(holo_map.origin, holo_map)

        # Focal memories (full detail)
        focal_memories = []
        if self.config.include_focal:
            for landmark, resolution in foveated.focal_zone:
                focal_memories.append(self._render_landmark_full(landmark))

        # Peripheral summaries (blurred)
        peripheral_summaries = []
        if self.config.include_peripheral:
            for landmark, resolution in foveated.blur_zone:
                peripheral_summaries.append(
                    self._render_landmark_summary(landmark, resolution)
                )

        # Desire lines
        desire_lines = []
        if self.config.include_paths and request.include_paths:
            # Get edges relevant to focal landmarks
            focal_ids = {l.id for l, _ in foveated.focal_zone}
            for edge in holo_map.desire_lines:
                if edge.source in focal_ids or edge.target in focal_ids:
                    desire_lines.append(self._render_edge(edge, holo_map))
                    tokens_used += self.config.tokens_per_edge

        # Void warnings
        void_warnings = []
        if self.config.include_voids and request.include_voids:
            for void in holo_map.voids:
                void_warnings.append(self._render_void(void))
                tokens_used += self.config.tokens_per_void

        return OptimalContext(
            position=position,
            focal_memories=focal_memories,
            peripheral_summaries=peripheral_summaries,
            desire_lines=desire_lines,
            void_warnings=void_warnings,
            tokens_used=tokens_used,
            tokens_remaining=request.budget_tokens - tokens_used,
        )

    def _render_position(
        self,
        origin: ContextVector,
        holo_map: HoloMap,
    ) -> str:
        """Render the 'You are here' marker."""
        nearest = holo_map.nearest_landmark(origin)
        if nearest:
            return f"At: {nearest.label}"
        return f"At: {origin.label or 'Unknown position'}"

    def _render_landmark_full(self, landmark: Attractor) -> str:
        """Render a landmark at full detail."""
        parts = [f"**{landmark.label}**"]

        # Member count
        if landmark.member_count > 0:
            parts.append(f"({landmark.member_count} items)")

        # Density indicator
        if landmark.density > 0.8:
            parts.append("[Dense cluster]")
        elif landmark.density < 0.3:
            parts.append("[Sparse cluster]")

        # Drift warning
        if landmark.is_drifting:
            parts.append("[Drifting]")

        # Hot indicator
        if landmark.is_hot:
            parts.append("[Frequently accessed]")

        # Member IDs (truncated)
        if landmark.members:
            member_preview = ", ".join(landmark.members[:3])
            if len(landmark.members) > 3:
                member_preview += f", ... (+{len(landmark.members) - 3})"
            parts.append(f"Contains: {member_preview}")

        return " ".join(parts)

    def _render_landmark_summary(self, landmark: Attractor, resolution: float) -> str:
        """Render a landmark at reduced detail (summary)."""
        # Truncate label based on resolution
        max_len = int(self.config.summary_max_length * resolution)
        label = landmark.label[:max_len]
        if len(landmark.label) > max_len:
            label += "..."

        return f"- {label} ({landmark.member_count} items)"

    def _render_edge(self, edge: WeightedEdge, holo_map: HoloMap) -> str:
        """Render a desire line."""
        source = holo_map.get_landmark(edge.source)
        target = holo_map.get_landmark(edge.target)

        source_label = source.label if source else edge.source
        target_label = target.label if target else edge.target

        percentage = int(edge.weight * 100)
        direction = "↔" if edge.bidirectional else "→"

        return f"- {source_label} {direction} {target_label} ({percentage}%)"

    def _render_void(self, void: Void) -> str:
        """Render a void warning."""
        return f"- Unknown: {void.region.label} (uncertainty: {int(void.uncertainty * 100)}%)"

    def _distance(self, origin: ContextVector, embedding: list[float]) -> float:
        """Euclidean distance from origin to embedding."""
        if len(origin.embedding) != len(embedding):
            return float("inf")
        return math.sqrt(sum((a - b) ** 2 for a, b in zip(origin.embedding, embedding)))

    def _default_renderer(self, memory_id: str) -> str:
        """Default memory renderer (just returns ID)."""
        return memory_id


# ============================================================================
# Convenience Functions
# ============================================================================


async def inject_context(
    context: ContextVector,
    goal: ContextVector | None = None,
    budget: int = 4000,
    cartographer: CartographerAgent | None = None,
    pathfinder: PathfinderAgent | None = None,
) -> str:
    """
    Convenience function to get optimal context as a string.

    Args:
        context: Current position
        goal: Optional goal position
        budget: Token budget
        cartographer: Optional CartographerAgent
        pathfinder: Optional PathfinderAgent

    Returns:
        Context string ready for injection
    """
    injector = ContextInjector(
        cartographer=cartographer,
        pathfinder=pathfinder,
    )

    request = InjectionRequest(
        current_context=context,
        goal=goal,
        budget_tokens=budget,
    )

    result = await injector.invoke(request)
    return result.to_context_string()


# ============================================================================
# Factory Functions
# ============================================================================


def create_context_injector(
    cartographer: CartographerAgent | None = None,
    pathfinder: PathfinderAgent | None = None,
    config: InjectorConfig | None = None,
) -> ContextInjector:
    """Create a ContextInjector."""
    return ContextInjector(
        cartographer=cartographer,
        pathfinder=pathfinder,
        config=config,
    )
