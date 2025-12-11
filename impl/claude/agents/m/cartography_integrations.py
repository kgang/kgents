"""
M-gent Cartography Integrations.

Phase 5 Polish: O-gent, Ψ-gent, and I-gent integrations for cartography.

- CartographicObserver: O-gent annotations for map health
- MetaphorLocator: Ψ-gent metaphor neighborhood discovery
- MapRenderer: I-gent visualization components

These integrations are optional enhancements to the core cartography system.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Protocol, runtime_checkable

from .cartography import (
    Attractor,
    ContextVector,
    HoloMap,
    WeightedEdge,
)

# ============================================================================
# O-gent Integration: Cartographic Observer
# ============================================================================


@dataclass
class EdgeHealth:
    """Health metrics for a desire line edge."""

    edge_id: str  # "{source}->{target}"
    latency_p50: float = 0.0
    latency_p95: float = 0.0
    latency_p99: float = 0.0
    error_rate: float = 0.0
    throughput: float = 0.0  # Transitions per hour
    last_traversed: datetime | None = None
    sample_count: int = 0

    @property
    def is_healthy(self) -> bool:
        """Edge is healthy if low latency and low error rate."""
        return self.latency_p95 < 1.0 and self.error_rate < 0.1

    @property
    def is_stale(self) -> bool:
        """Edge hasn't been traversed recently."""
        if self.last_traversed is None:
            return True
        return datetime.now() - self.last_traversed > timedelta(hours=24)


@dataclass
class LandmarkHealth:
    """Health metrics for a landmark."""

    landmark_id: str
    semantic_drift: float = 0.0  # Embedding drift since last observation
    staleness: float = 0.0  # 0.0 = fresh, 1.0 = very stale
    access_count: int = 0
    last_accessed: datetime | None = None
    coherency_score: float = 1.0  # How consistent are members?

    @property
    def is_healthy(self) -> bool:
        """Landmark is healthy if low drift and high coherency."""
        return self.semantic_drift < 0.2 and self.coherency_score > 0.7

    @property
    def is_drifting(self) -> bool:
        """Semantic content has changed significantly."""
        return self.semantic_drift > 0.3


@dataclass
class MapHealth:
    """Overall health of a HoloMap."""

    timestamp: datetime = field(default_factory=datetime.now)
    total_landmarks: int = 0
    healthy_landmarks: int = 0
    drifting_landmarks: int = 0
    total_edges: int = 0
    healthy_edges: int = 0
    stale_edges: int = 0
    void_coverage: float = 0.0  # Fraction of space that is void
    overall_health: float = 1.0  # 0.0 = critical, 1.0 = perfect

    @property
    def landmark_health_rate(self) -> float:
        """Fraction of healthy landmarks."""
        if self.total_landmarks == 0:
            return 1.0
        return self.healthy_landmarks / self.total_landmarks

    @property
    def edge_health_rate(self) -> float:
        """Fraction of healthy edges."""
        if self.total_edges == 0:
            return 1.0
        return self.healthy_edges / self.total_edges


@runtime_checkable
class TelemetryStore(Protocol):
    """Protocol for O-gent telemetry storage."""

    def get_latency_percentile(
        self, source: str, target: str, percentile: float
    ) -> float:
        """Get latency percentile for a path."""
        ...

    def get_error_rate(self, source: str, target: str) -> float:
        """Get error rate for a path."""
        ...

    def get_throughput(self, source: str, target: str) -> float:
        """Get throughput for a path."""
        ...


@runtime_checkable
class DriftMeasurer(Protocol):
    """Protocol for semantic drift measurement."""

    def measure_drift(self, landmark_id: str, embedding: list[float]) -> float:
        """Measure semantic drift for a landmark."""
        ...


class CartographicObserver:
    """
    O-gent integration for map health monitoring.

    Provides three dimensions of observation:
    - X (Telemetric): Path latencies, throughput, error rates
    - Y (Semantic): Drift detection, coherency checks
    - Z (Axiological): Coverage, budget efficiency

    Example:
        observer = CartographicObserver()
        annotated_map = observer.annotate_map(holo_map)
        health = observer.assess_health(holo_map)
    """

    def __init__(
        self,
        telemetry_store: TelemetryStore | None = None,
        drift_measurer: DriftMeasurer | None = None,
    ):
        self.telemetry_store = telemetry_store
        self.drift_measurer = drift_measurer
        self._edge_health_cache: dict[str, EdgeHealth] = {}
        self._landmark_health_cache: dict[str, LandmarkHealth] = {}

    def annotate_map(self, holo_map: HoloMap) -> HoloMap:
        """
        Annotate a HoloMap with O-gent health metrics.

        Adds:
        - Edge annotations (latency, error rate)
        - Landmark annotations (semantic drift)

        Returns a new map with annotations.
        """
        # Annotate edges
        annotated_edges = []
        for edge in holo_map.desire_lines:
            health = self._get_edge_health(edge)
            annotated_edge = WeightedEdge(
                source=edge.source,
                target=edge.target,
                weight=edge.weight,
                bidirectional=edge.bidirectional,
                trace_ids=edge.trace_ids,
                transition_count=edge.transition_count,
                latency_p95=health.latency_p95,
                error_rate=health.error_rate,
                last_traversed=health.last_traversed,
                metadata={**edge.metadata, "health": health},
            )
            annotated_edges.append(annotated_edge)

        # Annotate landmarks
        annotated_landmarks = []
        for landmark in holo_map.landmarks:
            landmark_health = self._get_landmark_health(landmark)
            annotated_landmark = Attractor(
                id=landmark.id,
                centroid=landmark.centroid,
                members=landmark.members,
                label=landmark.label,
                density=landmark.density,
                member_count=landmark.member_count,
                variance=landmark.variance,
                semantic_drift=landmark_health.semantic_drift,
                last_visited=landmark_health.last_accessed,
                visit_count=landmark_health.access_count,
                artifact_type=landmark.artifact_type,
                metadata={**landmark.metadata, "health": landmark_health},
            )
            annotated_landmarks.append(annotated_landmark)

        # Create annotated map
        return HoloMap(
            origin=holo_map.origin,
            landmarks=annotated_landmarks,
            desire_lines=annotated_edges,
            voids=holo_map.voids,
            horizon=holo_map.horizon,
            created_at=holo_map.created_at,
            resolution=holo_map.resolution,
            metadata={**holo_map.metadata, "annotated": True},
        )

    def assess_health(self, holo_map: HoloMap) -> MapHealth:
        """
        Assess overall health of a HoloMap.

        Returns comprehensive health metrics.
        """
        healthy_landmarks = 0
        drifting_landmarks = 0

        for landmark in holo_map.landmarks:
            health = self._get_landmark_health(landmark)
            if health.is_healthy:
                healthy_landmarks += 1
            if health.is_drifting:
                drifting_landmarks += 1

        healthy_edges = 0
        stale_edges = 0

        for edge in holo_map.desire_lines:
            edge_health = self._get_edge_health(edge)
            if edge_health.is_healthy:
                healthy_edges += 1
            if edge_health.is_stale:
                stale_edges += 1

        # Calculate void coverage
        void_coverage = 0.0
        if holo_map.voids:
            total_void_area = sum(v.region.radius**2 for v in holo_map.voids)
            total_area = holo_map.horizon.outer_radius**2
            if total_area > 0:
                void_coverage = min(1.0, total_void_area / total_area)

        # Calculate overall health
        landmark_health_rate = healthy_landmarks / max(1, len(holo_map.landmarks))
        edge_health_rate = healthy_edges / max(1, len(holo_map.desire_lines))
        void_penalty = void_coverage * 0.3
        overall_health = max(
            0.0, (landmark_health_rate + edge_health_rate) / 2 - void_penalty
        )

        return MapHealth(
            total_landmarks=len(holo_map.landmarks),
            healthy_landmarks=healthy_landmarks,
            drifting_landmarks=drifting_landmarks,
            total_edges=len(holo_map.desire_lines),
            healthy_edges=healthy_edges,
            stale_edges=stale_edges,
            void_coverage=void_coverage,
            overall_health=overall_health,
        )

    def _get_edge_health(self, edge: WeightedEdge) -> EdgeHealth:
        """Get or compute edge health."""
        edge_id = f"{edge.source}->{edge.target}"

        if edge_id in self._edge_health_cache:
            return self._edge_health_cache[edge_id]

        health = EdgeHealth(edge_id=edge_id)

        if self.telemetry_store:
            health.latency_p50 = self.telemetry_store.get_latency_percentile(
                edge.source, edge.target, 0.50
            )
            health.latency_p95 = self.telemetry_store.get_latency_percentile(
                edge.source, edge.target, 0.95
            )
            health.latency_p99 = self.telemetry_store.get_latency_percentile(
                edge.source, edge.target, 0.99
            )
            health.error_rate = self.telemetry_store.get_error_rate(
                edge.source, edge.target
            )
            health.throughput = self.telemetry_store.get_throughput(
                edge.source, edge.target
            )

        health.last_traversed = edge.last_traversed
        health.sample_count = edge.transition_count

        self._edge_health_cache[edge_id] = health
        return health

    def _get_landmark_health(self, landmark: Attractor) -> LandmarkHealth:
        """Get or compute landmark health."""
        if landmark.id in self._landmark_health_cache:
            return self._landmark_health_cache[landmark.id]

        health = LandmarkHealth(landmark_id=landmark.id)

        if self.drift_measurer:
            health.semantic_drift = self.drift_measurer.measure_drift(
                landmark.id, landmark.centroid
            )

        # Use existing annotations if available
        if landmark.semantic_drift is not None:
            health.semantic_drift = landmark.semantic_drift
        health.last_accessed = landmark.last_visited
        health.access_count = landmark.visit_count

        # Calculate staleness
        if landmark.last_visited:
            age = datetime.now() - landmark.last_visited
            health.staleness = min(1.0, age.total_seconds() / (24 * 3600))

        self._landmark_health_cache[landmark.id] = health
        return health

    def clear_cache(self) -> None:
        """Clear health caches."""
        self._edge_health_cache.clear()
        self._landmark_health_cache.clear()


# ============================================================================
# Ψ-gent Integration: Metaphor Locator
# ============================================================================


@dataclass
class MetaphorMatch:
    """A metaphor found near a problem."""

    metaphor_id: str
    metaphor_name: str
    landmark_id: str
    distance: float  # Distance from problem position
    relevance: float  # 0.0-1.0 relevance score
    domain: str = ""
    operations: list[str] = field(default_factory=list)


@dataclass
class MetaphorNeighborhood:
    """The metaphor neighborhood around a problem."""

    problem_position: list[float]
    matches: list[MetaphorMatch]
    search_radius: float
    timestamp: datetime = field(default_factory=datetime.now)

    @property
    def best_match(self) -> MetaphorMatch | None:
        """Get the highest relevance match."""
        if not self.matches:
            return None
        return max(self.matches, key=lambda m: m.relevance)

    @property
    def match_count(self) -> int:
        """Number of matches found."""
        return len(self.matches)


@runtime_checkable
class MetaphorRegistry(Protocol):
    """Protocol for Ψ-gent metaphor storage."""

    def get_metaphor(self, metaphor_id: str) -> Any | None:
        """Get a metaphor by ID."""
        ...

    def get_metaphor_for_landmark(self, landmark_id: str) -> Any | None:
        """Get metaphor associated with a landmark."""
        ...


class MetaphorLocator:
    """
    Ψ-gent integration for metaphor discovery.

    Uses the HoloMap to locate relevant metaphors near a problem position.
    This bridges M-gent cartography with Ψ-gent's metaphorical reasoning.

    Example:
        locator = MetaphorLocator(metaphor_registry)
        neighborhood = locator.find_metaphor_neighborhood(problem_embedding, holo_map)
        best = neighborhood.best_match
    """

    def __init__(
        self,
        metaphor_registry: MetaphorRegistry | None = None,
        relevance_threshold: float = 0.3,
    ):
        self.metaphor_registry = metaphor_registry
        self.relevance_threshold = relevance_threshold

    def find_metaphor_neighborhood(
        self,
        problem_position: list[float] | ContextVector,
        holo_map: HoloMap,
        radius: float = 0.5,
    ) -> MetaphorNeighborhood:
        """
        Find metaphors near a problem position.

        Uses the HoloMap to:
        1. Locate nearby landmarks
        2. Filter for metaphor-type artifacts
        3. Compute relevance scores

        Args:
            problem_position: Problem embedding or ContextVector
            holo_map: The semantic map to search
            radius: Search radius from problem position

        Returns:
            MetaphorNeighborhood with matching metaphors
        """
        if isinstance(problem_position, ContextVector):
            position = problem_position.embedding
        else:
            position = problem_position

        # Find nearby landmarks
        nearby = holo_map.landmarks_within(position, radius)

        # Filter for metaphor-type landmarks
        matches = []
        for landmark in nearby:
            if self._is_metaphor_landmark(landmark):
                match = self._create_match(landmark, position)
                if match.relevance >= self.relevance_threshold:
                    matches.append(match)

        # Sort by relevance
        matches.sort(key=lambda m: m.relevance, reverse=True)

        return MetaphorNeighborhood(
            problem_position=position,
            matches=matches,
            search_radius=radius,
        )

    def _is_metaphor_landmark(self, landmark: Attractor) -> bool:
        """Check if a landmark contains metaphor artifacts."""
        if landmark.artifact_type == "metaphor":
            return True
        # Check metadata
        if landmark.metadata.get("artifact_type") == "metaphor":
            return True
        # Check if any member is a metaphor
        if self.metaphor_registry:
            for member_id in landmark.members[:5]:  # Check first 5
                if self.metaphor_registry.get_metaphor(member_id):
                    return True
        return False

    def _create_match(
        self, landmark: Attractor, problem_position: list[float]
    ) -> MetaphorMatch:
        """Create a MetaphorMatch from a landmark."""
        distance = landmark.distance_to(problem_position)

        # Compute relevance based on distance and density
        # Closer + denser = more relevant
        distance_score = 1.0 / (1.0 + distance)
        density_score = min(1.0, landmark.density)
        relevance = distance_score * 0.7 + density_score * 0.3

        # Get metaphor details from registry
        domain = ""
        operations: list[str] = []
        metaphor_name = landmark.label

        if self.metaphor_registry:
            metaphor = self.metaphor_registry.get_metaphor_for_landmark(landmark.id)
            if metaphor:
                domain = getattr(metaphor, "domain", "")
                metaphor_name = getattr(metaphor, "name", landmark.label)
                ops = getattr(metaphor, "operations", ())
                operations = [getattr(op, "name", str(op)) for op in ops]

        return MetaphorMatch(
            metaphor_id=landmark.id,
            metaphor_name=metaphor_name,
            landmark_id=landmark.id,
            distance=distance,
            relevance=relevance,
            domain=domain,
            operations=operations,
        )


# ============================================================================
# I-gent Integration: Map Renderer
# ============================================================================


@dataclass
class MapRenderConfig:
    """Configuration for map rendering."""

    width: int = 60
    height: int = 20
    show_voids: bool = True
    show_desire_lines: bool = True
    show_health: bool = True
    use_color: bool = True
    landmark_char: str = "◉"
    void_char: str = "░"
    origin_char: str = "★"
    path_chars: str = "─│┌┐└┘"


class MapRenderer:
    """
    I-gent integration for HoloMap visualization.

    Renders HoloMaps to terminal-friendly text representations.

    Example:
        renderer = MapRenderer()
        ascii_map = renderer.render_ascii(holo_map)
        print(ascii_map)
    """

    def __init__(self, config: MapRenderConfig | None = None):
        self.config = config or MapRenderConfig()

    def render_ascii(self, holo_map: HoloMap) -> str:
        """
        Render a HoloMap as ASCII art.

        Creates a simplified 2D projection of the semantic space.
        """
        lines = []
        w, h = self.config.width, self.config.height

        # Create grid
        grid = [[" " for _ in range(w)] for _ in range(h)]

        # Place origin at center
        cx, cy = w // 2, h // 2
        grid[cy][cx] = self.config.origin_char

        # Place landmarks (project to 2D using first two embedding dimensions)
        for landmark in holo_map.landmarks:
            x, y = self._project_to_grid(
                landmark.centroid, holo_map.origin.embedding, w, h
            )
            if 0 <= x < w and 0 <= y < h:
                char = self.config.landmark_char
                if self.config.show_health and landmark.is_drifting:
                    char = "⚠"
                grid[y][x] = char

        # Place voids
        if self.config.show_voids:
            for void in holo_map.voids:
                x, y = self._project_to_grid(
                    void.region.center, holo_map.origin.embedding, w, h
                )
                radius = int(void.region.radius * 5)
                for dy in range(-radius, radius + 1):
                    for dx in range(-radius, radius + 1):
                        if dx * dx + dy * dy <= radius * radius:
                            vx, vy = x + dx, y + dy
                            if 0 <= vx < w and 0 <= vy < h and grid[vy][vx] == " ":
                                grid[vy][vx] = self.config.void_char

        # Build output
        lines.append("┌" + "─" * w + "┐")
        for row in grid:
            lines.append("│" + "".join(row) + "│")
        lines.append("└" + "─" * w + "┘")

        return "\n".join(lines)

    def render_summary(self, holo_map: HoloMap) -> str:
        """
        Render a text summary of the HoloMap.

        Shows key statistics and navigation hints.
        """
        lines = []

        # Header
        lines.append(f"HoloMap: {holo_map.origin.label or 'Unnamed'}")
        lines.append("=" * 40)

        # Position
        lines.append(f"Origin: {holo_map.origin.label or 'Current position'}")

        # Statistics
        lines.append("")
        lines.append("Statistics:")
        lines.append(f"  Landmarks: {holo_map.landmark_count}")
        lines.append(f"  Desire Lines: {holo_map.edge_count}")
        lines.append(f"  Voids: {holo_map.void_count}")
        lines.append(f"  Coverage: {holo_map.coverage:.1%}")

        # Focal landmarks
        focal = holo_map.get_focal_landmarks()
        if focal:
            lines.append("")
            lines.append("Focal Zone (high detail):")
            for landmark in focal[:5]:
                drift = "⚠" if landmark.is_drifting else "✓"
                lines.append(f"  {drift} {landmark.label}")

        # Adjacent landmarks
        adjacent = holo_map.adjacent_to(holo_map.origin)
        if adjacent:
            lines.append("")
            lines.append("Adjacent:")
            for landmark in adjacent[:5]:
                lines.append(f"  → {landmark.label}")

        # Top desire lines
        if holo_map.desire_lines:
            lines.append("")
            lines.append("Common Paths:")
            top_edges = sorted(
                holo_map.desire_lines, key=lambda e: e.weight, reverse=True
            )[:3]
            for edge in top_edges:
                src = holo_map.get_landmark(edge.source)
                tgt = holo_map.get_landmark(edge.target)
                src_label = src.label if src else edge.source
                tgt_label = tgt.label if tgt else edge.target
                pct = edge.weight * 100
                lines.append(f"  {src_label} → {tgt_label} ({pct:.0f}%)")

        # Void warnings
        if holo_map.voids:
            dangerous = [v for v in holo_map.voids if v.is_dangerous]
            if dangerous:
                lines.append("")
                lines.append("⚠ Caution:")
                for void in dangerous[:3]:
                    lines.append(f"  Unexplored: {void.region.label or void.id}")

        return "\n".join(lines)

    def render_health_panel(self, health: MapHealth) -> str:
        """
        Render a health status panel.

        Uses I-gent component styling.
        """
        lines = []

        # Health bar
        health_pct = health.overall_health * 100
        bar_width = 20
        filled = int(health.overall_health * bar_width)
        bar = "█" * filled + "░" * (bar_width - filled)

        status = "HEALTHY" if health.overall_health > 0.7 else "DEGRADED"
        if health.overall_health < 0.3:
            status = "CRITICAL"

        lines.append(f"Map Health: [{bar}] {health_pct:.0f}% {status}")
        lines.append("")
        lines.append(
            f"Landmarks: {health.healthy_landmarks}/{health.total_landmarks} healthy"
        )
        lines.append(f"Edges: {health.healthy_edges}/{health.total_edges} healthy")

        if health.drifting_landmarks > 0:
            lines.append(f"⚠ {health.drifting_landmarks} drifting landmarks")
        if health.stale_edges > 0:
            lines.append(f"⚠ {health.stale_edges} stale edges")
        if health.void_coverage > 0.3:
            lines.append(f"⚠ {health.void_coverage:.0%} void coverage")

        return "\n".join(lines)

    def _project_to_grid(
        self,
        embedding: list[float],
        origin: list[float],
        width: int,
        height: int,
    ) -> tuple[int, int]:
        """
        Project an embedding to 2D grid coordinates.

        Uses first two dimensions relative to origin.
        """
        if len(embedding) < 2 or len(origin) < 2:
            return width // 2, height // 2

        # Relative position
        dx = embedding[0] - origin[0]
        dy = embedding[1] - origin[1]

        # Scale to grid (assuming embeddings in [-1, 1] range)
        scale = min(width, height) // 4
        x = int(width // 2 + dx * scale)
        y = int(height // 2 + dy * scale)

        return x, y


# ============================================================================
# Factory Functions
# ============================================================================


def create_cartographic_observer(
    telemetry_store: TelemetryStore | None = None,
    drift_measurer: DriftMeasurer | None = None,
) -> CartographicObserver:
    """Create a CartographicObserver for map health monitoring."""
    return CartographicObserver(
        telemetry_store=telemetry_store,
        drift_measurer=drift_measurer,
    )


def create_metaphor_locator(
    metaphor_registry: MetaphorRegistry | None = None,
    relevance_threshold: float = 0.3,
) -> MetaphorLocator:
    """Create a MetaphorLocator for finding metaphors near problems."""
    return MetaphorLocator(
        metaphor_registry=metaphor_registry,
        relevance_threshold=relevance_threshold,
    )


def create_map_renderer(config: MapRenderConfig | None = None) -> MapRenderer:
    """Create a MapRenderer for HoloMap visualization."""
    return MapRenderer(config=config)


# ============================================================================
# Convenience: Annotate and Render
# ============================================================================


def annotate_and_render(
    holo_map: HoloMap,
    telemetry_store: TelemetryStore | None = None,
) -> tuple[HoloMap, str, MapHealth]:
    """
    Convenience function to annotate a map and render it.

    Returns:
        tuple of (annotated_map, summary_text, health_report)
    """
    observer = CartographicObserver(telemetry_store=telemetry_store)
    renderer = MapRenderer()

    annotated = observer.annotate_map(holo_map)
    health = observer.assess_health(annotated)
    summary = renderer.render_summary(annotated)

    return annotated, summary, health
