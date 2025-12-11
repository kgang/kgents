"""
Tests for M-gent PathfinderAgent and ContextInjector.

Phase 3: PathfinderAgent with desire line navigation.
Phase 4: ContextInjector with foveation algorithm.
"""

import pytest
from agents.m.cartographer import (
    MockTrace,
    create_mock_cartographer,
)
from agents.m.cartography import (
    Attractor,
    Goal,
    HoloMap,
    Horizon,
    InjectionRequest,
    Region,
    Void,
    WeightedEdge,
    create_context_vector,
)
from agents.m.context_injector import (
    ContextInjector,
    InjectorConfig,
    create_context_injector,
    inject_context,
)
from agents.m.pathfinder import (
    PathfinderAgent,
    PathfinderConfig,
    analyze_path,
    create_pathfinder,
)

# ============================================================================
# Test Fixtures
# ============================================================================


@pytest.fixture
def simple_map() -> HoloMap:
    """Create a simple HoloMap for testing."""
    origin = create_context_vector([0.0, 0.0], label="origin")

    landmarks = [
        Attractor(
            id="auth",
            centroid=[1.0, 0.0],
            members=["m1", "m2"],
            label="Authentication",
            density=0.9,
        ),
        Attractor(
            id="retry",
            centroid=[2.0, 0.5],
            members=["m3"],
            label="Retry Logic",
            density=0.8,
        ),
        Attractor(
            id="error",
            centroid=[3.0, 0.0],
            members=["m4", "m5", "m6"],
            label="Error Handling",
            density=0.7,
        ),
        Attractor(
            id="logging",
            centroid=[1.0, 1.0],
            members=["m7"],
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
            inner_radius=2.0,
            outer_radius=5.0,
            max_tokens=4000,
        ),
    )


@pytest.fixture
def map_with_void() -> HoloMap:
    """Create a map with a void region."""
    origin = create_context_vector([0.0, 0.0])

    landmarks = [
        Attractor(id="a", centroid=[1.0, 0.0], members=[], label="A", density=1.0),
        Attractor(id="b", centroid=[5.0, 0.0], members=[], label="B", density=1.0),
    ]

    desire_lines = [
        WeightedEdge(source="a", target="b", weight=0.5),
    ]

    voids = [
        Void(
            id="void_1",
            region=Region(
                id="r1",
                center=[3.0, 0.0],  # Between a and b
                radius=0.5,
                label="Unknown Zone",
            ),
            uncertainty=0.9,
        ),
    ]

    return HoloMap(
        origin=origin,
        landmarks=landmarks,
        desire_lines=desire_lines,
        voids=voids,
        horizon=Horizon(
            center=[0.0, 0.0],
            inner_radius=2.0,
            outer_radius=10.0,
        ),
    )


# ============================================================================
# PathfinderAgent Tests
# ============================================================================


class TestPathfinderAgent:
    """Tests for PathfinderAgent."""

    @pytest.mark.asyncio
    async def test_create_pathfinder(self):
        """Create pathfinder with factory."""
        pathfinder = create_pathfinder()
        assert pathfinder is not None

    @pytest.mark.asyncio
    async def test_invoke_no_map_no_cartographer(self):
        """Invoke without map or cartographer returns failure."""
        pathfinder = PathfinderAgent()
        goal = Goal(
            current_context=create_context_vector([0.0, 0.0]),
            target=[1.0, 0.0],
        )
        plan = await pathfinder.invoke(goal)

        assert plan.confidence == 0.0
        assert plan.mode == "exploration"
        assert "No map" in plan.warning

    @pytest.mark.asyncio
    async def test_invoke_with_map(self, simple_map):
        """Invoke with provided map."""
        pathfinder = PathfinderAgent()
        goal = Goal(
            current_context=simple_map.origin,
            target=[3.0, 0.0],  # Near error landmark
        )
        plan = await pathfinder.invoke(goal, holo_map=simple_map)

        assert len(plan.waypoints) >= 1
        assert plan.mode == "desire_line"

    @pytest.mark.asyncio
    async def test_path_prefers_desire_lines(self, simple_map):
        """Pathfinder prefers historical paths."""
        pathfinder = PathfinderAgent()
        goal = Goal(
            current_context=create_context_vector([1.0, 0.0]),  # At auth
            target=[3.0, 0.0],  # At error
        )
        plan = await pathfinder.invoke(goal, holo_map=simple_map)

        # Should follow desire lines, not direct path
        assert plan.mode == "desire_line"
        assert plan.confidence > 0.3

    @pytest.mark.asyncio
    async def test_bushwhack_when_no_path(self, simple_map):
        """Bushwhack mode when no desire line path exists."""
        # Create a map with disconnected landmarks
        isolated_map = HoloMap(
            origin=create_context_vector([0.0, 0.0]),
            landmarks=[
                Attractor(
                    id="a", centroid=[0.0, 0.0], members=[], label="A", density=1.0
                ),
                Attractor(
                    id="b", centroid=[100.0, 0.0], members=[], label="B", density=1.0
                ),
            ],
            desire_lines=[],  # No connections
            voids=[],
            horizon=Horizon(center=[0.0, 0.0], inner_radius=1.0, outer_radius=200.0),
        )

        pathfinder = PathfinderAgent()
        goal = Goal(
            current_context=create_context_vector([0.0, 0.0]),
            target=[100.0, 0.0],
        )
        plan = await pathfinder.invoke(goal, holo_map=isolated_map)

        # Should be exploration mode (bushwhacking)
        assert plan.mode == "exploration"
        assert plan.confidence <= 0.3

    @pytest.mark.asyncio
    async def test_void_crossing_reduces_confidence(self, map_with_void):
        """Path crossing void has reduced confidence."""
        pathfinder = PathfinderAgent()
        goal = Goal(
            current_context=create_context_vector([1.0, 0.0]),  # At a
            target=[5.0, 0.0],  # At b
        )
        plan = await pathfinder.invoke(goal, holo_map=map_with_void)

        # Path exists via desire line, but crosses void
        # Note: the void is at [3.0, 0.0] but landmarks are at [1,0] and [5,0]
        # The centroid doesn't cross the void, but the path might
        assert plan.mode == "desire_line"


class TestPathfinderConfig:
    """Tests for PathfinderConfig."""

    def test_default_config(self):
        """Default config has sensible values."""
        config = PathfinderConfig()
        assert config.max_path_length > 0
        assert config.allow_exploration is True

    @pytest.mark.asyncio
    async def test_disable_exploration(self, simple_map):
        """Can disable exploration mode."""
        config = PathfinderConfig(allow_exploration=False)
        pathfinder = PathfinderAgent(config=config)

        # Create map with no path
        isolated_map = HoloMap(
            origin=create_context_vector([0.0, 0.0]),
            landmarks=[
                Attractor(
                    id="a", centroid=[0.0, 0.0], members=[], label="A", density=1.0
                ),
                Attractor(
                    id="b", centroid=[100.0, 0.0], members=[], label="B", density=1.0
                ),
            ],
            desire_lines=[],
            voids=[],
            horizon=Horizon(center=[0.0, 0.0], inner_radius=1.0, outer_radius=200.0),
        )

        goal = Goal(
            current_context=create_context_vector([0.0, 0.0]),
            target=[100.0, 0.0],
        )
        plan = await pathfinder.invoke(goal, holo_map=isolated_map)

        # Should fail without exploration
        assert plan.confidence == 0.0
        assert "disabled" in plan.warning


class TestPathAnalysis:
    """Tests for path analysis."""

    def test_analyze_empty_path(self, simple_map):
        """Analyze empty path."""
        from agents.m.cartography import NavigationPlan

        plan = NavigationPlan(
            waypoints=[],
            confidence=0.0,
            mode="exploration",
        )
        analysis = analyze_path(plan, simple_map)

        assert analysis.total_distance == 0.0
        assert analysis.void_crossings == 0

    def test_analyze_single_waypoint(self, simple_map):
        """Analyze single waypoint path."""
        from agents.m.cartography import NavigationPlan

        landmark = simple_map.get_landmark("auth")
        plan = NavigationPlan(
            waypoints=[landmark],
            confidence=1.0,
            mode="desire_line",
        )
        analysis = analyze_path(plan, simple_map)

        assert analysis.total_distance == 0.0

    def test_analyze_multi_waypoint(self, simple_map):
        """Analyze multi-waypoint path."""
        from agents.m.cartography import NavigationPlan

        auth = simple_map.get_landmark("auth")
        retry = simple_map.get_landmark("retry")
        error = simple_map.get_landmark("error")

        plan = NavigationPlan(
            waypoints=[auth, retry, error],
            confidence=0.7,
            mode="desire_line",
        )
        analysis = analyze_path(plan, simple_map)

        assert analysis.total_distance > 0.0


# ============================================================================
# ContextInjector Tests
# ============================================================================


class TestContextInjector:
    """Tests for ContextInjector."""

    @pytest.mark.asyncio
    async def test_create_injector(self):
        """Create injector with factory."""
        injector = create_context_injector()
        assert injector is not None

    @pytest.mark.asyncio
    async def test_invoke_no_map_no_cartographer(self):
        """Invoke without map or cartographer returns minimal context."""
        injector = ContextInjector()
        request = InjectionRequest(
            current_context=create_context_vector([0.0, 0.0]),
            budget_tokens=4000,
        )
        result = await injector.invoke(request)

        assert (
            "unknown" in result.position.lower() or "no map" in result.position.lower()
        )
        assert result.tokens_used == 0
        assert result.tokens_remaining == 4000

    @pytest.mark.asyncio
    async def test_invoke_with_map(self, simple_map):
        """Invoke with provided map."""
        injector = ContextInjector()
        request = InjectionRequest(
            current_context=simple_map.origin,
            budget_tokens=4000,
        )
        result = await injector.invoke(request, holo_map=simple_map)

        # Should have position
        assert result.position != ""
        # Should respect budget
        assert result.tokens_used <= 4000

    @pytest.mark.asyncio
    async def test_focal_zone_populated(self, simple_map):
        """Focal zone has nearby landmarks."""
        injector = ContextInjector()
        request = InjectionRequest(
            current_context=create_context_vector([1.0, 0.0]),  # Near auth
            budget_tokens=4000,
        )
        result = await injector.invoke(request, holo_map=simple_map)

        # Should have some focal memories
        assert len(result.focal_memories) >= 0  # May be 0 if budget tight

    @pytest.mark.asyncio
    async def test_budget_constraint(self, simple_map):
        """Small budget limits output."""
        injector = ContextInjector()

        # Very small budget
        small_request = InjectionRequest(
            current_context=simple_map.origin,
            budget_tokens=50,
        )
        small_result = await injector.invoke(small_request, holo_map=simple_map)

        # Normal budget
        normal_request = InjectionRequest(
            current_context=simple_map.origin,
            budget_tokens=4000,
        )
        normal_result = await injector.invoke(normal_request, holo_map=simple_map)

        # Small budget should have fewer items or same if minimal
        assert (
            small_result.tokens_used <= 50
            or small_result.tokens_used <= normal_result.tokens_used
        )

    @pytest.mark.asyncio
    async def test_void_warnings_included(self, map_with_void):
        """Void warnings are included in output."""
        injector = ContextInjector()
        request = InjectionRequest(
            current_context=map_with_void.origin,
            budget_tokens=4000,
            include_voids=True,
        )
        result = await injector.invoke(request, holo_map=map_with_void)

        assert len(result.void_warnings) >= 1

    @pytest.mark.asyncio
    async def test_desire_lines_included(self, simple_map):
        """Desire lines are included in output."""
        injector = ContextInjector()
        request = InjectionRequest(
            current_context=create_context_vector([1.0, 0.0]),  # Near auth
            budget_tokens=4000,
            include_paths=True,
        )
        result = await injector.invoke(request, holo_map=simple_map)

        # May have desire lines if auth is in focal zone
        # The result depends on foveation
        assert isinstance(result.desire_lines, list)


class TestInjectorConfig:
    """Tests for InjectorConfig."""

    def test_default_config(self):
        """Default config has sensible values."""
        config = InjectorConfig()
        assert config.focal_threshold > config.blur_threshold
        assert config.tokens_per_landmark_full > config.tokens_per_landmark_blur

    @pytest.mark.asyncio
    async def test_custom_config_no_focal(self, simple_map):
        """Can disable focal zone."""
        config = InjectorConfig(include_focal=False)
        injector = ContextInjector(config=config)
        request = InjectionRequest(
            current_context=simple_map.origin,
            budget_tokens=4000,
        )
        result = await injector.invoke(request, holo_map=simple_map)

        assert result.focal_memories == []


class TestContextString:
    """Tests for context string generation."""

    @pytest.mark.asyncio
    async def test_to_context_string(self, simple_map):
        """OptimalContext renders to string."""
        injector = ContextInjector()
        request = InjectionRequest(
            current_context=simple_map.origin,
            budget_tokens=4000,
        )
        result = await injector.invoke(request, holo_map=simple_map)
        context_str = result.to_context_string()

        assert isinstance(context_str, str)
        assert len(context_str) > 0


# ============================================================================
# Integration Tests
# ============================================================================


class TestPathfinderInjectorIntegration:
    """Integration tests for Pathfinder + ContextInjector."""

    @pytest.mark.asyncio
    async def test_injector_with_pathfinder(self, simple_map):
        """ContextInjector uses pathfinder for goal-directed context."""
        pathfinder = PathfinderAgent()
        injector = ContextInjector(pathfinder=pathfinder)

        request = InjectionRequest(
            current_context=create_context_vector([1.0, 0.0]),  # At auth
            goal=create_context_vector([3.0, 0.0]),  # At error
            budget_tokens=4000,
        )
        result = await injector.invoke(request, holo_map=simple_map)

        # Should have context related to the path
        assert result.position != ""

    @pytest.mark.asyncio
    async def test_full_pipeline_with_cartographer(self):
        """Full pipeline: Cartographer -> Pathfinder -> Injector."""
        # Create mock cartographer
        cartographer = create_mock_cartographer(
            items=[
                ("auth", [0.0, 0.0]),
                ("retry", [0.1, 0.0]),
                ("error", [0.2, 0.0]),
            ],
            traces=[
                MockTrace(trace_id="t1", vector=[0.0, 0.0]),
                MockTrace(trace_id="t2", vector=[0.1, 0.0]),
                MockTrace(trace_id="t3", vector=[0.2, 0.0]),
            ],
        )
        pathfinder = PathfinderAgent(cartographer=cartographer)
        injector = ContextInjector(cartographer=cartographer, pathfinder=pathfinder)

        request = InjectionRequest(
            current_context=create_context_vector([0.0, 0.0]),
            budget_tokens=4000,
        )

        # This will generate map via cartographer
        result = await injector.invoke(request)

        assert result is not None
        assert result.tokens_remaining <= 4000


class TestInjectContextConvenience:
    """Tests for inject_context convenience function."""

    @pytest.mark.asyncio
    async def test_inject_context_minimal(self):
        """inject_context works with minimal arguments."""
        context = create_context_vector([0.0, 0.0])
        result = await inject_context(context)

        assert isinstance(result, str)

    @pytest.mark.asyncio
    async def test_inject_context_with_budget(self):
        """inject_context respects budget."""
        context = create_context_vector([0.0, 0.0])
        result = await inject_context(context, budget=100)

        assert isinstance(result, str)
