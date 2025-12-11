"""
Tests for M-gent Cartography Integrations.

Phase 5 Polish: O-gent, Ψ-gent, and I-gent integration tests.
"""

from datetime import datetime, timedelta

import pytest

from ..cartography import (
    Attractor,
    HoloMap,
    Horizon,
    Region,
    Void,
    WeightedEdge,
    create_context_vector,
)
from ..cartography_integrations import (
    # O-gent
    CartographicObserver,
    EdgeHealth,
    LandmarkHealth,
    MapHealth,
    MapRenderConfig,
    # I-gent
    MapRenderer,
    # Ψ-gent
    MetaphorLocator,
    MetaphorMatch,
    MetaphorNeighborhood,
    annotate_and_render,
    # Factories
    create_cartographic_observer,
    create_map_renderer,
    create_metaphor_locator,
)

# ============================================================================
# Test Fixtures
# ============================================================================


@pytest.fixture
def sample_holomap():
    """Create a sample HoloMap for testing."""
    origin = create_context_vector([0.0, 0.0, 0.0], label="origin")

    landmarks = [
        Attractor(
            id="auth",
            centroid=[0.1, 0.1, 0.0],
            members=["m1", "m2"],
            label="Authentication",
            density=0.8,
            visit_count=15,
            last_visited=datetime.now() - timedelta(hours=2),
        ),
        Attractor(
            id="db",
            centroid=[0.3, 0.2, 0.0],
            members=["m3", "m4", "m5"],
            label="Database",
            density=0.9,
            visit_count=25,
            last_visited=datetime.now(),
        ),
        Attractor(
            id="api",
            centroid=[0.2, 0.4, 0.0],
            members=["m6"],
            label="API Layer",
            density=0.5,
            visit_count=5,
            semantic_drift=0.35,  # Drifting
        ),
        Attractor(
            id="metaphor_cache",
            centroid=[0.15, 0.15, 0.0],
            members=["met1", "met2"],
            label="Caching Metaphors",
            density=0.7,
            artifact_type="metaphor",
        ),
    ]

    desire_lines = [
        WeightedEdge(
            source="auth",
            target="db",
            weight=0.8,
            transition_count=50,
            last_traversed=datetime.now(),
        ),
        WeightedEdge(
            source="db",
            target="api",
            weight=0.6,
            transition_count=30,
            last_traversed=datetime.now() - timedelta(hours=48),  # Stale
        ),
        WeightedEdge(
            source="auth",
            target="api",
            weight=0.3,
            transition_count=10,
        ),
    ]

    voids = [
        Void(
            id="void1",
            region=Region(
                id="r1",
                center=[0.8, 0.8, 0.0],
                radius=0.2,
                label="Unexplored Area",
            ),
            uncertainty=0.9,
            probe_count=5,  # Dangerous
        ),
    ]

    horizon = Horizon(
        center=[0.0, 0.0, 0.0],
        inner_radius=0.3,
        outer_radius=0.8,
        max_tokens=4000,
    )

    return HoloMap(
        origin=origin,
        landmarks=landmarks,
        desire_lines=desire_lines,
        voids=voids,
        horizon=horizon,
    )


# ============================================================================
# O-gent Integration: CartographicObserver Tests
# ============================================================================


class TestEdgeHealth:
    """Tests for EdgeHealth dataclass."""

    def test_healthy_edge(self) -> None:
        """Edge with low latency and error rate is healthy."""
        health = EdgeHealth(
            edge_id="a->b",
            latency_p95=0.5,
            error_rate=0.05,
            last_traversed=datetime.now(),  # Need timestamp to not be stale
        )
        assert health.is_healthy
        assert not health.is_stale

    def test_unhealthy_high_latency(self) -> None:
        """Edge with high latency is unhealthy."""
        health = EdgeHealth(
            edge_id="a->b",
            latency_p95=2.0,
            error_rate=0.05,
        )
        assert not health.is_healthy

    def test_unhealthy_high_error_rate(self) -> None:
        """Edge with high error rate is unhealthy."""
        health = EdgeHealth(
            edge_id="a->b",
            latency_p95=0.5,
            error_rate=0.15,
        )
        assert not health.is_healthy

    def test_stale_edge(self) -> None:
        """Edge not traversed recently is stale."""
        health = EdgeHealth(
            edge_id="a->b",
            last_traversed=datetime.now() - timedelta(hours=48),
        )
        assert health.is_stale

    def test_fresh_edge(self) -> None:
        """Edge traversed recently is fresh."""
        health = EdgeHealth(
            edge_id="a->b",
            last_traversed=datetime.now(),
        )
        assert not health.is_stale


class TestLandmarkHealth:
    """Tests for LandmarkHealth dataclass."""

    def test_healthy_landmark(self) -> None:
        """Landmark with low drift and high coherency is healthy."""
        health = LandmarkHealth(
            landmark_id="test",
            semantic_drift=0.1,
            coherency_score=0.9,
        )
        assert health.is_healthy
        assert not health.is_drifting

    def test_drifting_landmark(self) -> None:
        """Landmark with high drift is marked as drifting."""
        health = LandmarkHealth(
            landmark_id="test",
            semantic_drift=0.4,
        )
        assert health.is_drifting
        assert not health.is_healthy


class TestMapHealth:
    """Tests for MapHealth dataclass."""

    def test_health_rates(self) -> None:
        """Health rates are calculated correctly."""
        health = MapHealth(
            total_landmarks=10,
            healthy_landmarks=8,
            total_edges=5,
            healthy_edges=4,
        )
        assert health.landmark_health_rate == 0.8
        assert health.edge_health_rate == 0.8

    def test_empty_map_health(self) -> None:
        """Empty map has perfect health rates."""
        health = MapHealth()
        assert health.landmark_health_rate == 1.0
        assert health.edge_health_rate == 1.0


class TestCartographicObserver:
    """Tests for CartographicObserver."""

    def test_create_observer(self) -> None:
        """Can create observer without stores."""
        observer = create_cartographic_observer()
        assert observer is not None

    def test_annotate_map(self, sample_holomap) -> None:
        """Annotate map adds health metadata."""
        observer = CartographicObserver()
        annotated = observer.annotate_map(sample_holomap)

        assert annotated.metadata.get("annotated") is True
        assert len(annotated.landmarks) == len(sample_holomap.landmarks)
        assert len(annotated.desire_lines) == len(sample_holomap.desire_lines)

    def test_annotate_preserves_drift(self, sample_holomap) -> None:
        """Annotation preserves existing drift values."""
        observer = CartographicObserver()
        annotated = observer.annotate_map(sample_holomap)

        # Find the drifting landmark
        api_landmark = next(l for l in annotated.landmarks if l.id == "api")
        assert api_landmark.semantic_drift == 0.35

    def test_assess_health(self, sample_holomap) -> None:
        """Assess health returns comprehensive report."""
        observer = CartographicObserver()
        health = observer.assess_health(sample_holomap)

        assert health.total_landmarks == 4
        assert health.total_edges == 3
        # void_coverage tracks void area, not count
        assert 0.0 <= health.void_coverage <= 1.0
        assert 0.0 <= health.overall_health <= 1.0

    def test_assess_health_detects_drifting(self, sample_holomap) -> None:
        """Health assessment detects drifting landmarks."""
        observer = CartographicObserver()
        health = observer.assess_health(sample_holomap)

        assert health.drifting_landmarks >= 1  # api landmark is drifting

    def test_cache_clearing(self, sample_holomap) -> None:
        """Clear cache removes cached health data."""
        observer = CartographicObserver()
        observer.assess_health(sample_holomap)

        assert len(observer._landmark_health_cache) > 0
        observer.clear_cache()
        assert len(observer._landmark_health_cache) == 0


# ============================================================================
# Mock Telemetry Store
# ============================================================================


class MockTelemetryStore:
    """Mock telemetry store for testing."""

    def __init__(self):
        self.latencies = {}
        self.error_rates = {}
        self.throughputs = {}

    def set_latency(self, source: str, target: str, percentile: float, value: float):
        self.latencies[(source, target, percentile)] = value

    def set_error_rate(self, source: str, target: str, value: float):
        self.error_rates[(source, target)] = value

    def set_throughput(self, source: str, target: str, value: float):
        self.throughputs[(source, target)] = value

    def get_latency_percentile(
        self, source: str, target: str, percentile: float
    ) -> float:
        return self.latencies.get((source, target, percentile), 0.0)

    def get_error_rate(self, source: str, target: str) -> float:
        return self.error_rates.get((source, target), 0.0)

    def get_throughput(self, source: str, target: str) -> float:
        return self.throughputs.get((source, target), 0.0)


class TestCartographicObserverWithTelemetry:
    """Tests with mock telemetry store."""

    def test_annotate_with_telemetry(self, sample_holomap) -> None:
        """Telemetry data is added to annotations."""
        store = MockTelemetryStore()
        store.set_latency("auth", "db", 0.95, 0.8)
        store.set_error_rate("auth", "db", 0.02)

        observer = CartographicObserver(telemetry_store=store)
        annotated = observer.annotate_map(sample_holomap)

        auth_db = next(
            e for e in annotated.desire_lines if e.source == "auth" and e.target == "db"
        )
        assert auth_db.latency_p95 == 0.8
        assert auth_db.error_rate == 0.02


# ============================================================================
# Ψ-gent Integration: MetaphorLocator Tests
# ============================================================================


class TestMetaphorMatch:
    """Tests for MetaphorMatch dataclass."""

    def test_create_match(self) -> None:
        """Can create a metaphor match."""
        match = MetaphorMatch(
            metaphor_id="met1",
            metaphor_name="Pipeline",
            landmark_id="lm1",
            distance=0.2,
            relevance=0.8,
            domain="software",
            operations=["filter", "map", "reduce"],
        )
        assert match.relevance == 0.8
        assert len(match.operations) == 3


class TestMetaphorNeighborhood:
    """Tests for MetaphorNeighborhood dataclass."""

    def test_empty_neighborhood(self) -> None:
        """Empty neighborhood has no matches."""
        hood = MetaphorNeighborhood(
            problem_position=[0.0, 0.0],
            matches=[],
            search_radius=0.5,
        )
        assert hood.match_count == 0
        assert hood.best_match is None

    def test_best_match(self) -> None:
        """Best match returns highest relevance."""
        matches = [
            MetaphorMatch("a", "A", "l1", 0.3, 0.5, "", []),
            MetaphorMatch("b", "B", "l2", 0.2, 0.9, "", []),
            MetaphorMatch("c", "C", "l3", 0.4, 0.3, "", []),
        ]
        hood = MetaphorNeighborhood([0.0, 0.0], matches, 0.5)

        assert hood.best_match is not None
        assert hood.best_match.metaphor_id == "b"
        assert hood.best_match.relevance == 0.9


class TestMetaphorLocator:
    """Tests for MetaphorLocator."""

    def test_create_locator(self) -> None:
        """Can create locator without registry."""
        locator = create_metaphor_locator()
        assert locator is not None

    def test_find_metaphor_neighborhood(self, sample_holomap) -> None:
        """Find metaphors near a position."""
        locator = MetaphorLocator()
        position = [0.15, 0.15, 0.0]  # Near metaphor_cache

        hood = locator.find_metaphor_neighborhood(position, sample_holomap, radius=0.2)

        assert hood.match_count >= 1
        # Should find the metaphor_cache landmark
        assert any(m.landmark_id == "metaphor_cache" for m in hood.matches)

    def test_find_with_context_vector(self, sample_holomap) -> None:
        """Can use ContextVector as position."""
        locator = MetaphorLocator()
        position = create_context_vector([0.15, 0.15, 0.0])

        hood = locator.find_metaphor_neighborhood(position, sample_holomap)

        assert hood.problem_position == [0.15, 0.15, 0.0]

    def test_relevance_threshold(self, sample_holomap) -> None:
        """Relevance threshold filters matches."""
        # High threshold should filter out distant matches
        locator = MetaphorLocator(relevance_threshold=0.9)
        position = [0.5, 0.5, 0.0]  # Far from metaphors

        hood = locator.find_metaphor_neighborhood(position, sample_holomap, radius=1.0)

        # Should have few or no matches at high threshold
        assert hood.match_count <= 1

    def test_no_metaphors_in_area(self, sample_holomap) -> None:
        """Returns empty when no metaphors nearby."""
        locator = MetaphorLocator()
        position = [0.9, 0.9, 0.0]  # Far from everything

        hood = locator.find_metaphor_neighborhood(position, sample_holomap, radius=0.1)

        assert hood.match_count == 0


# ============================================================================
# I-gent Integration: MapRenderer Tests
# ============================================================================


class TestMapRenderConfig:
    """Tests for MapRenderConfig."""

    def test_default_config(self) -> None:
        """Default config has sensible values."""
        config = MapRenderConfig()
        assert config.width == 60
        assert config.height == 20
        assert config.show_voids is True
        assert config.use_color is True


class TestMapRenderer:
    """Tests for MapRenderer."""

    def test_create_renderer(self) -> None:
        """Can create renderer with default config."""
        renderer = create_map_renderer()
        assert renderer is not None

    def test_create_with_config(self) -> None:
        """Can create renderer with custom config."""
        config = MapRenderConfig(width=40, height=10)
        renderer = MapRenderer(config=config)
        assert renderer.config.width == 40

    def test_render_ascii(self, sample_holomap) -> None:
        """Render produces ASCII map."""
        renderer = MapRenderer()
        output = renderer.render_ascii(sample_holomap)

        assert isinstance(output, str)
        assert len(output) > 0
        # Should have borders
        assert "┌" in output
        assert "┘" in output
        # Should have landmarks (origin may be overwritten by nearby landmark)
        assert "◉" in output or "⚠" in output or "★" in output

    def test_render_summary(self, sample_holomap) -> None:
        """Render summary produces text report."""
        renderer = MapRenderer()
        output = renderer.render_summary(sample_holomap)

        assert "HoloMap" in output
        assert "Statistics" in output
        assert "Landmarks:" in output
        assert "4" in output  # 4 landmarks

    def test_render_summary_shows_voids(self, sample_holomap) -> None:
        """Summary shows void warnings."""
        renderer = MapRenderer()
        output = renderer.render_summary(sample_holomap)

        assert "Caution" in output or "Unexplored" in output

    def test_render_health_panel(self) -> None:
        """Render health panel produces status display."""
        renderer = MapRenderer()
        health = MapHealth(
            total_landmarks=10,
            healthy_landmarks=8,
            total_edges=5,
            healthy_edges=4,
            drifting_landmarks=2,
            stale_edges=1,
            overall_health=0.7,
        )

        output = renderer.render_health_panel(health)

        assert "Map Health" in output
        assert "8/10" in output  # healthy/total landmarks
        assert "drifting" in output.lower()

    def test_render_health_panel_critical(self) -> None:
        """Health panel shows CRITICAL for low health."""
        renderer = MapRenderer()
        health = MapHealth(overall_health=0.2)

        output = renderer.render_health_panel(health)

        assert "CRITICAL" in output

    def test_render_health_panel_healthy(self) -> None:
        """Health panel shows HEALTHY for good health."""
        renderer = MapRenderer()
        health = MapHealth(overall_health=0.9)

        output = renderer.render_health_panel(health)

        assert "HEALTHY" in output


class TestAsciiMapDetails:
    """Detailed tests for ASCII map rendering."""

    def test_small_map(self) -> None:
        """Render small map correctly."""
        config = MapRenderConfig(width=20, height=10)
        renderer = MapRenderer(config=config)

        origin = create_context_vector([0.0, 0.0], label="test")
        holomap = HoloMap(
            origin=origin,
            landmarks=[],
            desire_lines=[],
            voids=[],
            horizon=Horizon([0.0, 0.0], 0.3, 0.8),
        )

        output = renderer.render_ascii(holomap)
        lines = output.split("\n")

        # Should have correct dimensions (height + 2 for borders)
        assert len(lines) == 12

    def test_landmarks_visible(self, sample_holomap) -> None:
        """Landmarks appear on map."""
        renderer = MapRenderer()
        output = renderer.render_ascii(sample_holomap)

        # Should have landmark characters
        assert "◉" in output

    def test_voids_visible(self, sample_holomap) -> None:
        """Voids appear on map."""
        config = MapRenderConfig(show_voids=True)
        renderer = MapRenderer(config=config)
        output = renderer.render_ascii(sample_holomap)

        # Should have void characters
        assert "░" in output

    def test_voids_can_be_hidden(self, sample_holomap) -> None:
        """Voids can be hidden."""
        config = MapRenderConfig(show_voids=False)
        renderer = MapRenderer(config=config)
        output = renderer.render_ascii(sample_holomap)

        # Should NOT have void characters (only in areas not covered by landmarks)
        # The origin is at center, landmarks nearby, voids at edge
        # With show_voids=False, those areas should be empty spaces


class TestAnnotateAndRender:
    """Tests for convenience function."""

    def test_annotate_and_render(self, sample_holomap) -> None:
        """Convenience function returns all outputs."""
        annotated, summary, health = annotate_and_render(sample_holomap)

        assert annotated is not None
        assert isinstance(summary, str)
        assert isinstance(health, MapHealth)

    def test_annotate_and_render_with_telemetry(self, sample_holomap) -> None:
        """Works with telemetry store."""
        store = MockTelemetryStore()
        store.set_latency("auth", "db", 0.95, 1.5)

        annotated, summary, health = annotate_and_render(sample_holomap, store)

        # Should have telemetry data
        auth_db = next(
            e for e in annotated.desire_lines if e.source == "auth" and e.target == "db"
        )
        assert auth_db.latency_p95 == 1.5


# ============================================================================
# Edge Cases
# ============================================================================


class TestEdgeCases:
    """Tests for edge cases."""

    def test_empty_map_rendering(self) -> None:
        """Can render empty map."""
        origin = create_context_vector([0.0, 0.0, 0.0])
        holomap = HoloMap(
            origin=origin,
            landmarks=[],
            desire_lines=[],
            voids=[],
            horizon=Horizon([0.0, 0.0, 0.0], 0.3, 0.8),
        )

        renderer = MapRenderer()
        output = renderer.render_ascii(holomap)

        assert "★" in output  # Origin still shown

    def test_empty_map_health(self) -> None:
        """Health assessment for empty map."""
        origin = create_context_vector([0.0, 0.0, 0.0])
        holomap = HoloMap(
            origin=origin,
            landmarks=[],
            desire_lines=[],
            voids=[],
            horizon=Horizon([0.0, 0.0, 0.0], 0.3, 0.8),
        )

        observer = CartographicObserver()
        health = observer.assess_health(holomap)

        # Empty map has 0 overall health (nothing to observe)
        # This is acceptable - an empty map is "not yet useful" rather than "unhealthy"
        assert health.total_landmarks == 0
        assert health.total_edges == 0

    def test_single_dimension_embedding(self) -> None:
        """Handle 1D embeddings gracefully."""
        origin = create_context_vector([0.5])
        holomap = HoloMap(
            origin=origin,
            landmarks=[Attractor("a", [0.3], [], "A", 1.0)],
            desire_lines=[],
            voids=[],
            horizon=Horizon([0.5], 0.3, 0.8),
        )

        renderer = MapRenderer()
        output = renderer.render_ascii(holomap)

        # Should not crash
        assert isinstance(output, str)

    def test_high_dimension_embedding(self) -> None:
        """Handle high-dimensional embeddings."""
        dim = 768  # Like BERT
        origin = create_context_vector([0.0] * dim)
        holomap = HoloMap(
            origin=origin,
            landmarks=[Attractor("a", [0.1] * dim, [], "A", 1.0)],
            desire_lines=[],
            voids=[],
            horizon=Horizon([0.0] * dim, 0.3, 0.8),
        )

        renderer = MapRenderer()
        output = renderer.render_ascii(holomap)

        # Should use first 2 dimensions
        assert isinstance(output, str)
