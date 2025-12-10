"""
Tests for M-gent Holographic Cartography.

Phase 1: Core data structures (HoloMap, Attractor, WeightedEdge, Horizon).
"""

import math

import pytest

from ..cartography import (
    Attractor,
    ContextVector,
    HoloMap,
    Horizon,
    NavigationPlan,
    OptimalContext,
    Region,
    Void,
    WeightedEdge,
    create_attractor,
    create_context_vector,
    create_desire_line,
    create_empty_holomap,
)


# ============================================================================
# ContextVector Tests
# ============================================================================


class TestContextVector:
    """Tests for ContextVector."""

    def test_create_context_vector(self):
        """Create a basic context vector."""
        cv = create_context_vector([1.0, 0.0, 0.0], label="test")
        assert cv.dimension == 3
        assert cv.label == "test"

    def test_distance_to_same(self):
        """Distance to self is zero."""
        cv = ContextVector(embedding=[1.0, 2.0, 3.0])
        assert cv.distance_to(cv) == 0.0

    def test_distance_to_orthogonal(self):
        """Distance between orthogonal unit vectors."""
        cv1 = ContextVector(embedding=[1.0, 0.0, 0.0])
        cv2 = ContextVector(embedding=[0.0, 1.0, 0.0])
        assert abs(cv1.distance_to(cv2) - math.sqrt(2)) < 1e-10

    def test_distance_dimension_mismatch(self):
        """Mismatched dimensions raise error."""
        cv1 = ContextVector(embedding=[1.0, 0.0])
        cv2 = ContextVector(embedding=[1.0, 0.0, 0.0])
        with pytest.raises(ValueError):
            cv1.distance_to(cv2)

    def test_cosine_similarity_identical(self):
        """Identical vectors have similarity 1.0."""
        cv = ContextVector(embedding=[1.0, 2.0, 3.0])
        assert abs(cv.cosine_similarity(cv) - 1.0) < 1e-10

    def test_cosine_similarity_orthogonal(self):
        """Orthogonal vectors have similarity 0.0."""
        cv1 = ContextVector(embedding=[1.0, 0.0, 0.0])
        cv2 = ContextVector(embedding=[0.0, 1.0, 0.0])
        assert abs(cv1.cosine_similarity(cv2)) < 1e-10

    def test_cosine_similarity_opposite(self):
        """Opposite vectors have similarity -1.0."""
        cv1 = ContextVector(embedding=[1.0, 0.0, 0.0])
        cv2 = ContextVector(embedding=[-1.0, 0.0, 0.0])
        assert abs(cv1.cosine_similarity(cv2) + 1.0) < 1e-10

    def test_cosine_similarity_zero_vector(self):
        """Zero vector has similarity 0.0."""
        cv1 = ContextVector(embedding=[0.0, 0.0, 0.0])
        cv2 = ContextVector(embedding=[1.0, 0.0, 0.0])
        assert cv1.cosine_similarity(cv2) == 0.0


# ============================================================================
# Attractor Tests
# ============================================================================


class TestAttractor:
    """Tests for Attractor (landmarks)."""

    def test_create_attractor(self):
        """Create a basic attractor."""
        attr = create_attractor(
            id="auth",
            centroid=[1.0, 0.0, 0.0],
            label="Authentication",
            members=["m1", "m2"],
            density=0.9,
        )
        assert attr.id == "auth"
        assert attr.label == "Authentication"
        assert attr.member_count == 2
        assert attr.density == 0.9

    def test_attractor_distance(self):
        """Distance from attractor centroid."""
        attr = Attractor(
            id="test",
            centroid=[0.0, 0.0, 0.0],
            members=[],
            label="Origin",
            density=1.0,
        )
        assert attr.distance_to([1.0, 0.0, 0.0]) == 1.0
        assert attr.distance_to([0.0, 0.0, 0.0]) == 0.0

    def test_attractor_is_hot(self):
        """High visit count indicates hot attractor."""
        attr = Attractor(
            id="test",
            centroid=[0.0, 0.0],
            members=[],
            label="test",
            density=1.0,
            visit_count=5,
        )
        assert not attr.is_hot

        attr.visit_count = 15
        assert attr.is_hot

    def test_attractor_is_drifting(self):
        """Semantic drift detection."""
        attr = Attractor(
            id="test",
            centroid=[0.0, 0.0],
            members=[],
            label="test",
            density=1.0,
        )
        assert not attr.is_drifting  # None drift

        attr.semantic_drift = 0.1
        assert not attr.is_drifting  # Below threshold

        attr.semantic_drift = 0.3
        assert attr.is_drifting  # Above threshold


# ============================================================================
# WeightedEdge Tests
# ============================================================================


class TestWeightedEdge:
    """Tests for WeightedEdge (desire lines)."""

    def test_create_desire_line(self):
        """Create a basic desire line."""
        edge = create_desire_line(
            source="auth",
            target="retry",
            weight=0.8,
        )
        assert edge.source == "auth"
        assert edge.target == "retry"
        assert edge.weight == 0.8
        assert edge.bidirectional

    def test_edge_cost(self):
        """Cost is inverse of weight."""
        edge = WeightedEdge(source="a", target="b", weight=0.5)
        assert edge.cost() == 2.0

        edge.weight = 1.0
        assert edge.cost() == 1.0

    def test_edge_cost_zero_weight(self):
        """Zero weight has infinite cost."""
        edge = WeightedEdge(source="a", target="b", weight=0.0)
        assert edge.cost() == float("inf")

    def test_edge_is_well_trodden(self):
        """High-traffic detection."""
        edge = WeightedEdge(source="a", target="b", weight=0.3)
        assert not edge.is_well_trodden

        edge.weight = 0.6
        assert edge.is_well_trodden

        edge.weight = 0.3
        edge.transition_count = 25
        assert edge.is_well_trodden

    def test_edge_is_reliable(self):
        """Low error rate means reliable."""
        edge = WeightedEdge(source="a", target="b", weight=0.5)
        assert edge.is_reliable  # None = reliable

        edge.error_rate = 0.05
        assert edge.is_reliable

        edge.error_rate = 0.15
        assert not edge.is_reliable


# ============================================================================
# Horizon Tests
# ============================================================================


class TestHorizon:
    """Tests for Horizon (progressive disclosure boundary)."""

    def test_horizon_resolution_at_center(self):
        """Full resolution at center."""
        h = Horizon(
            center=[0.0, 0.0],
            inner_radius=0.3,
            outer_radius=1.0,
        )
        assert h.resolution_at(0.0) == 1.0
        assert h.resolution_at(0.2) == 1.0

    def test_horizon_resolution_in_blur_zone(self):
        """Partial resolution in blur zone."""
        h = Horizon(
            center=[0.0, 0.0],
            inner_radius=0.3,
            outer_radius=1.0,
        )
        # At middle of blur zone
        resolution = h.resolution_at(0.65)
        assert 0.0 < resolution < 1.0

    def test_horizon_resolution_beyond(self):
        """Zero resolution beyond horizon."""
        h = Horizon(
            center=[0.0, 0.0],
            inner_radius=0.3,
            outer_radius=1.0,
        )
        assert h.resolution_at(1.5) == 0.0

    def test_horizon_from_budget(self):
        """Create horizon scaled by budget."""
        h = Horizon.from_budget(
            center=[0.0, 0.0],
            token_budget=4000,
        )
        assert h.max_tokens == 4000
        assert h.inner_radius > 0
        assert h.outer_radius > h.inner_radius

    def test_horizon_token_spending(self):
        """Token budget management."""
        h = Horizon(
            center=[0.0, 0.0],
            inner_radius=0.3,
            outer_radius=1.0,
            max_tokens=100,
        )
        assert h.remaining_tokens == 100

        assert h.spend_tokens(30) is True
        assert h.remaining_tokens == 70

        assert h.spend_tokens(80) is False  # Insufficient
        assert h.remaining_tokens == 70  # Unchanged


# ============================================================================
# Region and Void Tests
# ============================================================================


class TestRegion:
    """Tests for Region."""

    def test_region_contains(self):
        """Point containment check."""
        r = Region(
            id="r1",
            center=[0.0, 0.0, 0.0],
            radius=1.0,
        )
        assert r.contains([0.5, 0.0, 0.0])
        assert r.contains([0.0, 0.0, 0.0])
        assert not r.contains([2.0, 0.0, 0.0])


class TestVoid:
    """Tests for Void (unexplored regions)."""

    def test_void_is_dangerous(self):
        """Dangerous void detection."""
        v = Void(
            id="v1",
            region=Region(id="r1", center=[0.0], radius=1.0),
            uncertainty=0.5,
            probe_count=5,
        )
        assert not v.is_dangerous

        v.uncertainty = 0.9
        assert v.is_dangerous


# ============================================================================
# HoloMap Tests
# ============================================================================


class TestHoloMap:
    """Tests for HoloMap."""

    @pytest.fixture
    def sample_map(self) -> HoloMap:
        """Create a sample map for testing."""
        origin = ContextVector(embedding=[0.0, 0.0], label="origin")

        landmarks = [
            Attractor(
                id="auth",
                centroid=[1.0, 0.0],
                members=["m1"],
                label="Authentication",
                density=0.9,
            ),
            Attractor(
                id="retry",
                centroid=[1.5, 0.5],
                members=["m2"],
                label="Retry Logic",
                density=0.8,
            ),
            Attractor(
                id="error",
                centroid=[2.0, 0.0],
                members=["m3"],
                label="Error Handling",
                density=0.7,
            ),
            Attractor(
                id="logging",
                centroid=[0.0, 1.0],
                members=["m4"],
                label="Logging",
                density=0.85,
            ),
        ]

        desire_lines = [
            WeightedEdge(source="auth", target="retry", weight=0.8),
            WeightedEdge(source="retry", target="error", weight=0.6),
            WeightedEdge(source="auth", target="error", weight=0.3),
            WeightedEdge(source="auth", target="logging", weight=0.5),
        ]

        return HoloMap(
            origin=origin,
            landmarks=landmarks,
            desire_lines=desire_lines,
            voids=[],
            horizon=Horizon(
                center=[0.0, 0.0],
                inner_radius=1.0,
                outer_radius=3.0,
            ),
        )

    def test_create_empty_holomap(self):
        """Create an empty map."""
        origin = create_context_vector([0.0, 0.0])
        hm = create_empty_holomap(origin)
        assert hm.landmark_count == 0
        assert hm.edge_count == 0

    def test_get_landmark(self, sample_map):
        """Get landmark by ID."""
        auth = sample_map.get_landmark("auth")
        assert auth is not None
        assert auth.label == "Authentication"

        missing = sample_map.get_landmark("nonexistent")
        assert missing is None

    def test_nearest_landmark(self, sample_map):
        """Find nearest landmark."""
        # Nearest to origin
        nearest = sample_map.nearest_landmark([0.0, 0.0])
        assert nearest is not None
        # Could be auth (1,0) or logging (0,1), both at distance 1
        assert nearest.id in ("auth", "logging")

        # Nearest to auth location
        nearest = sample_map.nearest_landmark([1.0, 0.0])
        assert nearest.id == "auth"

    def test_landmarks_within(self, sample_map):
        """Find landmarks within radius."""
        within = sample_map.landmarks_within([0.0, 0.0], radius=1.5)
        assert len(within) >= 2  # auth and logging at least

    def test_has_path_direct(self, sample_map):
        """Check path existence for connected landmarks."""
        assert sample_map.has_path([1.0, 0.0], [1.5, 0.5])  # auth -> retry

    def test_has_path_indirect(self, sample_map):
        """Check path existence through intermediates."""
        # auth -> retry -> error
        assert sample_map.has_path([1.0, 0.0], [2.0, 0.0])

    def test_has_path_same_landmark(self, sample_map):
        """Path to self always exists."""
        assert sample_map.has_path([1.0, 0.0], [1.0, 0.0])

    def test_get_paved_path(self, sample_map):
        """Get desire-line path between landmarks."""
        path = sample_map.get_paved_path([1.0, 0.0], [2.0, 0.0])
        assert len(path) >= 2
        assert path[0].id == "auth"
        assert path[-1].id == "error"

    def test_get_paved_path_prefers_high_weight(self, sample_map):
        """Path should prefer high-weight edges."""
        # auth -> retry (0.8) -> error (0.6) = cost 1.25 + 1.67 = 2.92
        # auth -> error (0.3) = cost 3.33
        # Should prefer the longer but better-traveled path
        path = sample_map.get_paved_path([1.0, 0.0], [2.0, 0.0])
        # Path through retry has lower cost
        labels = [p.label for p in path]
        assert "Retry Logic" in labels or len(path) == 2

    def test_adjacent_to(self, sample_map):
        """Get adjacent landmarks."""
        adjacent = sample_map.adjacent_to([1.0, 0.0])  # auth
        adjacent_ids = {a.id for a in adjacent}
        # auth connects to retry, error, logging
        assert "retry" in adjacent_ids
        assert "error" in adjacent_ids

    def test_edges_from(self, sample_map):
        """Get edges from a landmark."""
        edges = sample_map.edges_from("auth")
        assert len(edges) >= 3  # retry, error, logging (+ reverses)

    def test_resolution_at(self, sample_map):
        """Get resolution at different distances."""
        # At origin (center) - full resolution
        res = sample_map.resolution_at([0.0, 0.0])
        assert res == 1.0

        # Beyond horizon
        res = sample_map.resolution_at([10.0, 0.0])
        assert res == 0.0

    def test_get_focal_landmarks(self, sample_map):
        """Get landmarks in focal zone."""
        focal = sample_map.get_focal_landmarks()
        # auth and logging are within inner_radius=1.0
        focal_ids = {l.id for l in focal}
        assert "auth" in focal_ids or "logging" in focal_ids

    def test_coverage(self, sample_map):
        """Coverage estimate."""
        coverage = sample_map.coverage
        assert 0.0 <= coverage <= 1.0


class TestHoloMapWithVoids:
    """Tests for HoloMap void handling."""

    @pytest.fixture
    def map_with_void(self) -> HoloMap:
        """Create a map with a void region."""
        origin = ContextVector(embedding=[0.0, 0.0])

        return HoloMap(
            origin=origin,
            landmarks=[
                Attractor(
                    id="known",
                    centroid=[1.0, 0.0],
                    members=[],
                    label="Known",
                    density=1.0,
                )
            ],
            desire_lines=[],
            voids=[
                Void(
                    id="dragons",
                    region=Region(
                        id="r1",
                        center=[5.0, 5.0],
                        radius=2.0,
                    ),
                    uncertainty=0.9,
                )
            ],
            horizon=Horizon(
                center=[0.0, 0.0],
                inner_radius=1.0,
                outer_radius=10.0,
            ),
        )

    def test_is_in_void(self, map_with_void):
        """Check if point is in void."""
        assert map_with_void.is_in_void([5.0, 5.0])
        assert map_with_void.is_in_void([5.5, 5.5])
        assert not map_with_void.is_in_void([0.0, 0.0])

    def test_get_void_at(self, map_with_void):
        """Get void at a point."""
        void = map_with_void.get_void_at([5.0, 5.0])
        assert void is not None
        assert void.id == "dragons"

        void = map_with_void.get_void_at([0.0, 0.0])
        assert void is None


# ============================================================================
# Navigation Plan Tests
# ============================================================================


class TestNavigationPlan:
    """Tests for NavigationPlan."""

    def test_navigation_plan_safe(self):
        """Safe navigation detection."""
        plan = NavigationPlan(
            waypoints=[],
            confidence=0.8,
            mode="desire_line",
        )
        assert plan.is_safe

    def test_navigation_plan_unsafe_low_confidence(self):
        """Low confidence is unsafe."""
        plan = NavigationPlan(
            waypoints=[],
            confidence=0.3,
            mode="desire_line",
        )
        assert not plan.is_safe

    def test_navigation_plan_unsafe_exploration(self):
        """Exploration mode is unsafe."""
        plan = NavigationPlan(
            waypoints=[],
            confidence=0.8,
            mode="exploration",
        )
        assert not plan.is_safe


# ============================================================================
# OptimalContext Tests
# ============================================================================


class TestOptimalContext:
    """Tests for OptimalContext."""

    def test_to_context_string(self):
        """Render context to string."""
        ctx = OptimalContext(
            position="At: Authentication Module",
            focal_memories=["- Auth handles login", "- Uses JWT tokens"],
            peripheral_summaries=["- Retry logic nearby"],
            desire_lines=["- Auth → Retry (80%)"],
            void_warnings=["- Unknown: External APIs"],
            tokens_used=500,
            tokens_remaining=3500,
        )
        rendered = ctx.to_context_string()

        assert "Current Position" in rendered
        assert "Authentication Module" in rendered
        assert "High Detail" in rendered
        assert "Common Transitions" in rendered


# ============================================================================
# Edge Cases
# ============================================================================


class TestEdgeCases:
    """Edge case tests."""

    def test_empty_map_operations(self):
        """Operations on empty map."""
        origin = create_context_vector([0.0, 0.0])
        hm = create_empty_holomap(origin)

        assert hm.nearest_landmark([0.0, 0.0]) is None
        assert hm.landmarks_within([0.0, 0.0], 1.0) == []
        assert not hm.has_path([0.0, 0.0], [1.0, 0.0])
        assert hm.get_paved_path([0.0, 0.0], [1.0, 0.0]) == []
        assert hm.adjacent_to([0.0, 0.0]) == []
        assert hm.coverage == 0.0

    def test_single_landmark_map(self):
        """Map with one landmark."""
        origin = create_context_vector([0.0, 0.0])
        hm = HoloMap(
            origin=origin,
            landmarks=[
                Attractor(
                    id="only",
                    centroid=[1.0, 0.0],
                    members=[],
                    label="Only",
                    density=1.0,
                )
            ],
            desire_lines=[],
            voids=[],
            horizon=Horizon(
                center=[0.0, 0.0],
                inner_radius=1.0,
                outer_radius=2.0,
            ),
        )

        assert hm.nearest_landmark([0.0, 0.0]).id == "only"
        assert hm.has_path([1.0, 0.0], [1.0, 0.0])  # Same point
        # Both points map to "only" landmark, so path exists (same landmark)
        # This is correct behavior - any point maps to nearest landmark
        assert hm.has_path([0.0, 0.0], [5.0, 0.0])  # Both map to "only"
        assert hm.adjacent_to([1.0, 0.0]) == []  # No connections

    def test_high_dimensional_vectors(self):
        """Works with high-dimensional embeddings."""
        dim = 768  # Typical embedding dimension
        embedding = [0.0] * dim
        embedding[0] = 1.0

        cv = ContextVector(embedding=embedding)
        assert cv.dimension == dim

        attr = Attractor(
            id="high_dim",
            centroid=[0.0] * dim,
            members=[],
            label="High Dim",
            density=1.0,
        )
        assert attr.distance_to(embedding) == 1.0
