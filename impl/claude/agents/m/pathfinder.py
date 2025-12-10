"""
M-gent PathfinderAgent.

Uses the HoloMap to find semantic paths from current state to goal.

Key Insight:
Unlike a planner that INVENTS steps, the Pathfinder
RECALLS steps that have worked before (following Desire Lines).

"The road less traveled is less traveled for a reason."
"""

from __future__ import annotations

import heapq
import math
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from .cartography import (
    Attractor,
    Goal,
    HoloMap,
    NavigationPlan,
)

if TYPE_CHECKING:
    from .cartographer import CartographerAgent


# ============================================================================
# PathfinderAgent
# ============================================================================


@dataclass
class PathfinderConfig:
    """Configuration for PathfinderAgent."""

    # Path finding
    max_path_length: int = 20  # Maximum waypoints
    bushwhack_penalty: float = 2.0  # Cost multiplier for unexplored paths

    # Confidence thresholds
    high_confidence_threshold: float = 0.7  # Above = safe path
    low_confidence_threshold: float = 0.3  # Below = dangerous

    # Exploration
    allow_exploration: bool = True  # Allow bushwhacking
    exploration_warning: str = "No historical path. This is uncharted territory."


class PathfinderAgent:
    """
    Uses the HoloMap to find the semantic path from current state to goal.

    Unlike a planner that INVENTS steps, the Pathfinder
    RECALLS steps that have worked before (following Desire Lines).

    Two modes:
    1. Desire Line Navigation: Follow historical paths (safe)
    2. Bushwhacking: No history, must explore (risky)
    """

    def __init__(
        self,
        cartographer: CartographerAgent | None = None,
        config: PathfinderConfig | None = None,
    ):
        self.cartographer = cartographer
        self.config = config or PathfinderConfig()

    async def invoke(
        self,
        goal: Goal,
        holo_map: HoloMap | None = None,
    ) -> NavigationPlan:
        """
        Find a path from current context to goal.

        Args:
            goal: Navigation goal with current context and target
            holo_map: Optional pre-computed map. If None, will generate one.

        Returns:
            NavigationPlan with waypoints, confidence, and mode
        """
        # Get or generate map
        if holo_map is None:
            if self.cartographer is None:
                # No cartographer, can't generate map
                return NavigationPlan(
                    waypoints=[],
                    confidence=0.0,
                    mode="exploration",
                    warning="No map available. Cannot navigate.",
                )
            holo_map = await self.cartographer.invoke(goal.current_context)

        # Find path via desire lines
        if holo_map.has_path(goal.current_context, goal.target):
            return self._follow_desire_lines(goal, holo_map)
        else:
            # Off-road: No historical precedent
            if self.config.allow_exploration:
                return self._bushwhack(goal, holo_map)
            else:
                return NavigationPlan(
                    waypoints=[],
                    confidence=0.0,
                    mode="exploration",
                    warning="No path exists and exploration is disabled.",
                )

    def _follow_desire_lines(
        self,
        goal: Goal,
        holo_map: HoloMap,
    ) -> NavigationPlan:
        """
        Navigate using desire lines (historical paths).

        This is the safe mode - we're following paths that have worked before.
        """
        path = holo_map.get_paved_path(goal.current_context, goal.target)

        if not path:
            return NavigationPlan(
                waypoints=[],
                confidence=0.0,
                mode="desire_line",
                warning="Path exists but could not be computed.",
            )

        # Compute confidence from edge weights along path
        confidence = self._compute_path_confidence(path, holo_map)
        total_cost = self._compute_path_cost(path, holo_map)

        # Check for void crossings
        warning = None
        for waypoint in path:
            if holo_map.is_in_void(waypoint.centroid):
                warning = f"Path crosses void region near '{waypoint.label}'."
                confidence *= 0.8  # Reduce confidence
                break

        return NavigationPlan(
            waypoints=path,
            confidence=confidence,
            mode="desire_line",
            warning=warning,
            total_cost=total_cost,
        )

    def _bushwhack(
        self,
        goal: Goal,
        holo_map: HoloMap,
    ) -> NavigationPlan:
        """
        Navigate without desire lines.

        This is exploration—expensive, uncertain, but necessary
        for reaching new territory.
        """
        # Find nearest landmarks to start and end
        start_landmark = holo_map.nearest_landmark(goal.current_context)
        end_landmark = holo_map.nearest_landmark(goal.target)

        if start_landmark is None or end_landmark is None:
            return NavigationPlan(
                waypoints=[],
                confidence=0.0,
                mode="exploration",
                warning="Cannot locate start or end position.",
            )

        # Use A* with embedding distance heuristic
        path = self._astar_path(
            start_landmark,
            end_landmark,
            holo_map,
        )

        if not path:
            # Last resort: direct line
            path = [start_landmark, end_landmark]

        return NavigationPlan(
            waypoints=path,
            confidence=self.config.low_confidence_threshold,  # Low - no history
            mode="exploration",
            warning=self.config.exploration_warning,
            total_cost=self._estimate_exploration_cost(path),
        )

    def _astar_path(
        self,
        start: Attractor,
        end: Attractor,
        holo_map: HoloMap,
    ) -> list[Attractor]:
        """
        A* pathfinding using embedding distance as heuristic.

        Falls back to pure distance if no edges available.
        """
        # If same landmark, done
        if start.id == end.id:
            return [start]

        # Priority queue: (f_score, g_score, landmark_id, path)
        # f = g + h where g = cost so far, h = heuristic (distance to goal)
        start_h = self._embedding_distance(start.centroid, end.centroid)
        pq = [(start_h, 0.0, start.id, [start])]
        visited = set()
        g_scores = {start.id: 0.0}

        while pq:
            f, g, current_id, path = heapq.heappop(pq)

            if current_id in visited:
                continue
            visited.add(current_id)

            current = holo_map.get_landmark(current_id)
            if current is None:
                continue

            if current_id == end.id:
                return path

            # Check path length limit
            if len(path) >= self.config.max_path_length:
                continue

            # Explore neighbors via desire lines
            for edge in holo_map.edges_from(current_id):
                neighbor_id = edge.target
                if neighbor_id in visited:
                    continue

                neighbor = holo_map.get_landmark(neighbor_id)
                if neighbor is None:
                    continue

                # Cost = edge cost (or penalty for missing edge)
                edge_cost = (
                    edge.cost() if edge.weight > 0 else self.config.bushwhack_penalty
                )

                new_g = g + edge_cost
                if neighbor_id in g_scores and new_g >= g_scores[neighbor_id]:
                    continue

                g_scores[neighbor_id] = new_g
                h = self._embedding_distance(neighbor.centroid, end.centroid)
                f = new_g + h

                heapq.heappush(pq, (f, new_g, neighbor_id, path + [neighbor]))

        # No path found via edges, try direct if landmarks exist
        return []

    def _compute_path_confidence(
        self,
        path: list[Attractor],
        holo_map: HoloMap,
    ) -> float:
        """
        Compute confidence score for a path.

        Based on edge weights (transition probabilities).
        """
        if len(path) <= 1:
            return 1.0  # Single landmark = certain

        total_weight = 0.0
        edge_count = 0

        for i in range(len(path) - 1):
            source_id = path[i].id
            target_id = path[i + 1].id

            # Find edge
            for edge in holo_map.edges_from(source_id):
                if edge.target == target_id:
                    total_weight += edge.weight
                    edge_count += 1
                    break
            else:
                # No edge found - low confidence segment
                total_weight += 0.1
                edge_count += 1

        if edge_count == 0:
            return 0.5

        return total_weight / edge_count

    def _compute_path_cost(
        self,
        path: list[Attractor],
        holo_map: HoloMap,
    ) -> float:
        """Compute total cost for a path."""
        if len(path) <= 1:
            return 0.0

        total_cost = 0.0

        for i in range(len(path) - 1):
            source_id = path[i].id
            target_id = path[i + 1].id

            # Find edge
            for edge in holo_map.edges_from(source_id):
                if edge.target == target_id:
                    total_cost += edge.cost()
                    break
            else:
                # No edge - use bushwhack penalty
                total_cost += self.config.bushwhack_penalty

        return total_cost

    def _estimate_exploration_cost(
        self,
        path: list[Attractor],
    ) -> float:
        """Estimate cost for exploration path (no historical data)."""
        if len(path) <= 1:
            return 0.0

        # Use embedding distances with penalty
        total_cost = 0.0
        for i in range(len(path) - 1):
            dist = self._embedding_distance(path[i].centroid, path[i + 1].centroid)
            total_cost += dist * self.config.bushwhack_penalty

        return total_cost

    def _embedding_distance(self, a: list[float], b: list[float]) -> float:
        """Euclidean distance between embeddings."""
        if len(a) != len(b):
            return float("inf")
        return math.sqrt(sum((x - y) ** 2 for x, y in zip(a, b)))


# ============================================================================
# PathfinderResult Analysis
# ============================================================================


@dataclass
class PathAnalysis:
    """Detailed analysis of a navigation path."""

    plan: NavigationPlan
    total_distance: float = 0.0
    void_crossings: int = 0
    hotspots: list[str] = field(default_factory=list)  # High-traffic landmarks
    coldspots: list[str] = field(default_factory=list)  # Low-traffic landmarks
    estimated_tokens: int = 0


def analyze_path(
    plan: NavigationPlan,
    holo_map: HoloMap,
) -> PathAnalysis:
    """Analyze a navigation plan."""
    total_distance = 0.0
    void_crossings = 0
    hotspots = []
    coldspots = []

    for i, waypoint in enumerate(plan.waypoints):
        # Track hotspots/coldspots
        if waypoint.is_hot:
            hotspots.append(waypoint.label)
        elif waypoint.visit_count < 3:
            coldspots.append(waypoint.label)

        # Check void crossings
        if holo_map.is_in_void(waypoint.centroid):
            void_crossings += 1

        # Accumulate distance
        if i > 0:
            prev = plan.waypoints[i - 1]
            dist = math.sqrt(
                sum((a - b) ** 2 for a, b in zip(prev.centroid, waypoint.centroid))
            )
            total_distance += dist

    # Estimate tokens based on detail level
    # Each landmark contributes ~50 tokens at full detail
    estimated_tokens = len(plan.waypoints) * 50

    return PathAnalysis(
        plan=plan,
        total_distance=total_distance,
        void_crossings=void_crossings,
        hotspots=hotspots,
        coldspots=coldspots,
        estimated_tokens=estimated_tokens,
    )


# ============================================================================
# Factory Functions
# ============================================================================


def create_pathfinder(
    cartographer: CartographerAgent | None = None,
    config: PathfinderConfig | None = None,
) -> PathfinderAgent:
    """Create a PathfinderAgent."""
    return PathfinderAgent(cartographer=cartographer, config=config)
