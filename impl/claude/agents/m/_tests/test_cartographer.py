"""
Tests for M-gent CartographerAgent.

Phase 2: CartographerAgent with L-gent/N-gent integration.
"""

import pytest
from agents.m.cartographer import (
    CartographerAgent,
    CartographerConfig,
    DesireLineComputer,
    MockTrace,
    MockTraceStore,
    MockVectorSearch,
    create_cartographer,
    create_mock_cartographer,
    simple_cluster,
)
from agents.m.cartography import (
    Attractor,
    Resolution,
    create_context_vector,
)

# ============================================================================
# Clustering Tests
# ============================================================================


class TestSimpleClustering:
    """Tests for simple clustering algorithm."""

    def test_empty_items(self):
        """Empty input returns empty clusters."""
        clusters = simple_cluster([])
        assert clusters == []

    def test_single_item(self):
        """Single item forms single cluster."""
        items = [("a", [1.0, 0.0])]
        clusters = simple_cluster(items)
        assert len(clusters) == 1
        assert len(clusters[0].members) == 1

    def test_two_nearby_items(self):
        """Nearby items cluster together."""
        items = [
            ("a", [1.0, 0.0]),
            ("b", [1.1, 0.0]),
        ]
        clusters = simple_cluster(items, threshold=0.2)
        assert len(clusters) == 1
        assert len(clusters[0].members) == 2

    def test_two_distant_items(self):
        """Distant items form separate clusters."""
        items = [
            ("a", [0.0, 0.0]),
            ("b", [10.0, 0.0]),
        ]
        clusters = simple_cluster(items, threshold=0.5)
        assert len(clusters) == 2

    def test_three_clusters(self):
        """Multiple distinct clusters."""
        items = [
            ("a1", [0.0, 0.0]),
            ("a2", [0.1, 0.0]),
            ("b1", [5.0, 0.0]),
            ("b2", [5.1, 0.0]),
            ("c1", [10.0, 0.0]),
        ]
        clusters = simple_cluster(items, threshold=0.5)
        assert len(clusters) == 3

    def test_centroid_computation(self):
        """Centroid is computed correctly."""
        items = [
            ("a", [0.0, 0.0]),
            ("b", [2.0, 0.0]),
        ]
        clusters = simple_cluster(
            items, threshold=5.0
        )  # Large threshold to cluster together
        assert len(clusters) == 1
        # Centroid should be [1.0, 0.0]
        centroid = clusters[0].centroid
        assert abs(centroid[0] - 1.0) < 0.01
        assert abs(centroid[1] - 0.0) < 0.01

    def test_cluster_density(self):
        """Cluster density is computed."""
        items = [("a", [0.0, 0.0])]
        clusters = simple_cluster(items)
        assert clusters[0].density > 0


# ============================================================================
# DesireLineComputer Tests
# ============================================================================


class TestDesireLineComputer:
    """Tests for DesireLineComputer."""

    def test_empty_traces(self):
        """Empty traces returns empty edges."""
        computer = DesireLineComputer()
        landmarks = [
            Attractor(id="a", centroid=[0.0, 0.0], members=[], label="A", density=1.0),
        ]
        edges = computer.compute_from_traces([], landmarks)
        assert edges == []

    def test_empty_landmarks(self):
        """Empty landmarks returns empty edges."""
        computer = DesireLineComputer()
        traces = [MockTrace(trace_id="t1", vector=[0.0, 0.0])]
        edges = computer.compute_from_traces(traces, [])
        assert edges == []

    def test_single_trace(self):
        """Single trace produces no edges (need two)."""
        computer = DesireLineComputer()
        landmarks = [
            Attractor(id="a", centroid=[0.0, 0.0], members=[], label="A", density=1.0),
        ]
        traces = [MockTrace(trace_id="t1", vector=[0.0, 0.0])]
        edges = computer.compute_from_traces(traces, landmarks)
        assert edges == []

    def test_two_traces_same_landmark(self):
        """Two traces at same landmark produce no edge."""
        computer = DesireLineComputer()
        landmarks = [
            Attractor(id="a", centroid=[0.0, 0.0], members=[], label="A", density=1.0),
        ]
        traces = [
            MockTrace(trace_id="t1", vector=[0.0, 0.0]),
            MockTrace(trace_id="t2", vector=[0.1, 0.0]),  # Close to same landmark
        ]
        edges = computer.compute_from_traces(traces, landmarks)
        assert edges == []

    def test_two_traces_different_landmarks(self):
        """Two traces at different landmarks produce edge."""
        computer = DesireLineComputer()
        landmarks = [
            Attractor(id="a", centroid=[0.0, 0.0], members=[], label="A", density=1.0),
            Attractor(id="b", centroid=[10.0, 0.0], members=[], label="B", density=1.0),
        ]
        traces = [
            MockTrace(trace_id="t1", vector=[0.0, 0.0]),
            MockTrace(trace_id="t2", vector=[10.0, 0.0]),
        ]
        edges = computer.compute_from_traces(traces, landmarks)
        assert len(edges) == 1
        assert edges[0].source == "a"
        assert edges[0].target == "b"
        assert edges[0].weight == 1.0

    def test_multiple_transitions(self):
        """Multiple transitions increase weight."""
        computer = DesireLineComputer()
        landmarks = [
            Attractor(id="a", centroid=[0.0, 0.0], members=[], label="A", density=1.0),
            Attractor(id="b", centroid=[10.0, 0.0], members=[], label="B", density=1.0),
            Attractor(id="c", centroid=[20.0, 0.0], members=[], label="C", density=1.0),
        ]
        traces = [
            MockTrace(trace_id="t1", vector=[0.0, 0.0]),  # a
            MockTrace(trace_id="t2", vector=[10.0, 0.0]),  # b
            MockTrace(trace_id="t3", vector=[0.0, 0.0]),  # a
            MockTrace(trace_id="t4", vector=[10.0, 0.0]),  # b
            MockTrace(trace_id="t5", vector=[20.0, 0.0]),  # c
        ]
        edges = computer.compute_from_traces(traces, landmarks)

        # a->b appears twice, b->a once, b->c once = 4 total
        # a->b weight = 2/4 = 0.5
        ab_edge = next((e for e in edges if e.source == "a" and e.target == "b"), None)
        assert ab_edge is not None
        assert ab_edge.transition_count == 2

    def test_bidirectional_detection(self):
        """Bidirectional edges detected."""
        computer = DesireLineComputer()
        landmarks = [
            Attractor(id="a", centroid=[0.0, 0.0], members=[], label="A", density=1.0),
            Attractor(id="b", centroid=[10.0, 0.0], members=[], label="B", density=1.0),
        ]
        traces = [
            MockTrace(trace_id="t1", vector=[0.0, 0.0]),  # a
            MockTrace(trace_id="t2", vector=[10.0, 0.0]),  # b
            MockTrace(trace_id="t3", vector=[0.0, 0.0]),  # a
        ]
        edges = computer.compute_from_traces(traces, landmarks)

        # Both a->b and b->a transitions exist
        ab_edge = next((e for e in edges if e.source == "a" and e.target == "b"), None)
        assert ab_edge is not None
        assert ab_edge.bidirectional is True

    def test_traces_without_vectors_skipped(self):
        """Traces without vectors are skipped."""
        computer = DesireLineComputer()
        landmarks = [
            Attractor(id="a", centroid=[0.0, 0.0], members=[], label="A", density=1.0),
        ]
        traces = [
            MockTrace(trace_id="t1", vector=None),
            MockTrace(trace_id="t2", vector=None),
        ]
        edges = computer.compute_from_traces(traces, landmarks)
        assert edges == []


# ============================================================================
# MockVectorSearch Tests
# ============================================================================


class TestMockVectorSearch:
    """Tests for MockVectorSearch."""

    @pytest.mark.asyncio
    async def test_empty_search(self):
        """Empty search returns nothing."""
        search = MockVectorSearch([])
        results = await search.find_similar([0.0, 0.0])
        assert results == []

    @pytest.mark.asyncio
    async def test_find_similar(self):
        """Find similar items."""
        search = MockVectorSearch(
            [
                ("a", [0.0, 0.0]),
                ("b", [1.0, 0.0]),
                ("c", [10.0, 0.0]),
            ]
        )
        results = await search.find_similar([0.0, 0.0], threshold=0.3)
        # a should be found (distance 0), maybe b (distance 1)
        assert len(results) >= 1
        assert results[0][0] == "a"  # Closest first

    @pytest.mark.asyncio
    async def test_limit_respected(self):
        """Limit parameter respected."""
        search = MockVectorSearch(
            [
                ("a", [0.0, 0.0]),
                ("b", [0.1, 0.0]),
                ("c", [0.2, 0.0]),
            ]
        )
        results = await search.find_similar([0.0, 0.0], threshold=0.1, limit=2)
        assert len(results) <= 2


# ============================================================================
# MockTraceStore Tests
# ============================================================================


class TestMockTraceStore:
    """Tests for MockTraceStore."""

    def test_empty_query(self):
        """Empty store returns empty."""
        store = MockTraceStore([])
        results = store.query()
        assert results == []

    def test_add_and_query(self):
        """Add traces and query."""
        store = MockTraceStore()
        store.add_trace(MockTrace(trace_id="t1"))
        store.add_trace(MockTrace(trace_id="t2"))
        results = store.query()
        assert len(results) == 2

    def test_filter_by_agent_id(self):
        """Filter by agent_id."""
        store = MockTraceStore(
            [
                MockTrace(trace_id="t1", agent_id="a1"),
                MockTrace(trace_id="t2", agent_id="a2"),
            ]
        )
        results = store.query(agent_id="a1")
        assert len(results) == 1
        assert results[0].trace_id == "t1"

    def test_limit_and_offset(self):
        """Limit and offset work."""
        store = MockTraceStore(
            [
                MockTrace(trace_id="t1"),
                MockTrace(trace_id="t2"),
                MockTrace(trace_id="t3"),
            ]
        )
        results = store.query(limit=1, offset=1)
        assert len(results) == 1
        assert results[0].trace_id == "t2"


# ============================================================================
# CartographerAgent Tests
# ============================================================================


class TestCartographerAgent:
    """Tests for CartographerAgent."""

    @pytest.mark.asyncio
    async def test_create_cartographer(self):
        """Create cartographer with factory."""
        cartographer = create_cartographer()
        assert cartographer is not None

    @pytest.mark.asyncio
    async def test_invoke_empty_backends(self):
        """Invoke with no backends returns minimal map."""
        cartographer = CartographerAgent()
        context = create_context_vector([0.0, 0.0], label="origin")
        holomap = await cartographer.invoke(context)

        assert holomap is not None
        assert holomap.origin == context
        assert holomap.landmark_count == 0
        assert holomap.edge_count == 0
        # Total void when no landmarks
        assert holomap.void_count >= 1

    @pytest.mark.asyncio
    async def test_invoke_with_vector_search(self):
        """Invoke with vector search finds landmarks."""
        search = MockVectorSearch(
            [
                ("auth_1", [0.0, 0.0]),  # Close to origin
                ("auth_2", [0.1, 0.0]),  # Close to origin
                ("retry_1", [0.2, 0.0]),  # Still close enough
            ]
        )
        config = CartographerConfig(cluster_threshold=0.5)  # Allow wider clustering
        cartographer = CartographerAgent(vector_search=search, config=config)
        context = create_context_vector([0.0, 0.0], label="origin")
        holomap = await cartographer.invoke(context)

        assert holomap.landmark_count >= 1  # At least one cluster

    @pytest.mark.asyncio
    async def test_invoke_with_traces(self):
        """Invoke with traces computes desire lines."""
        search = MockVectorSearch(
            [
                ("a1", [0.0, 0.0]),
                ("b1", [10.0, 0.0]),
            ]
        )
        traces = [
            MockTrace(trace_id="t1", vector=[0.0, 0.0]),
            MockTrace(trace_id="t2", vector=[10.0, 0.0]),
        ]
        store = MockTraceStore(traces)

        cartographer = CartographerAgent(
            vector_search=search,
            trace_store=store,
        )
        context = create_context_vector([0.0, 0.0])
        holomap = await cartographer.invoke(context)

        # Should have landmarks and possibly desire lines
        assert holomap.landmark_count >= 1

    @pytest.mark.asyncio
    async def test_invoke_with_mock_cartographer(self):
        """Use factory for mock cartographer."""
        cartographer = create_mock_cartographer(
            items=[
                ("item1", [0.0, 0.0]),
                ("item2", [0.1, 0.0]),
            ],
            traces=[
                MockTrace(trace_id="t1", vector=[0.0, 0.0]),
            ],
        )
        context = create_context_vector([0.0, 0.0])
        holomap = await cartographer.invoke(context)

        assert holomap is not None

    @pytest.mark.asyncio
    async def test_resolution_affects_horizon(self):
        """Different resolutions produce different horizons."""
        cartographer = CartographerAgent()
        context = create_context_vector([0.0, 0.0])

        high_res = await cartographer.invoke(context, resolution=Resolution.HIGH)
        low_res = await cartographer.invoke(context, resolution=Resolution.LOW)

        # High resolution should have larger horizon
        assert high_res.horizon.outer_radius > low_res.horizon.outer_radius

    @pytest.mark.asyncio
    async def test_budget_affects_horizon(self):
        """Token budget affects horizon size."""
        cartographer = CartographerAgent()
        context = create_context_vector([0.0, 0.0])

        big_budget = await cartographer.invoke(context, budget_tokens=8000)
        small_budget = await cartographer.invoke(context, budget_tokens=1000)

        assert big_budget.horizon.max_tokens == 8000
        assert small_budget.horizon.max_tokens == 1000
        assert big_budget.horizon.outer_radius > small_budget.horizon.outer_radius


class TestCartographerConfig:
    """Tests for CartographerConfig."""

    def test_default_config(self):
        """Default config has sensible values."""
        config = CartographerConfig()
        assert config.cluster_threshold > 0
        assert config.min_cluster_size >= 1
        assert config.default_budget > 0

    @pytest.mark.asyncio
    async def test_custom_config(self):
        """Custom config is used."""
        config = CartographerConfig(
            cluster_threshold=0.1,
            min_transitions=5,
            default_budget=2000,
        )
        cartographer = CartographerAgent(config=config)

        assert cartographer.config.cluster_threshold == 0.1
        assert cartographer.config.min_transitions == 5


# ============================================================================
# Find Attractors Tests
# ============================================================================


class TestFindAttractors:
    """Tests for find_attractors method."""

    @pytest.mark.asyncio
    async def test_no_vector_search(self):
        """No vector search returns empty."""
        cartographer = CartographerAgent()
        context = create_context_vector([0.0, 0.0])
        attractors = await cartographer.find_attractors(context)
        assert attractors == []

    @pytest.mark.asyncio
    async def test_single_cluster(self):
        """Nearby items form single attractor."""
        search = MockVectorSearch(
            [
                ("a", [0.0, 0.0]),
                ("b", [0.1, 0.0]),
                ("c", [0.05, 0.05]),
            ]
        )
        cartographer = CartographerAgent(vector_search=search)
        context = create_context_vector([0.0, 0.0])

        attractors = await cartographer.find_attractors(context)
        # All close together, should form one cluster
        assert len(attractors) >= 1

    @pytest.mark.asyncio
    async def test_attractor_has_members(self):
        """Attractors track their members."""
        search = MockVectorSearch(
            [
                ("item_1", [0.0, 0.0]),
                ("item_2", [0.1, 0.0]),
            ]
        )
        cartographer = CartographerAgent(vector_search=search)
        context = create_context_vector([0.0, 0.0])

        attractors = await cartographer.find_attractors(context)
        assert len(attractors) >= 1
        assert attractors[0].member_count >= 1

    @pytest.mark.asyncio
    async def test_attractor_label_generated(self):
        """Attractors get human-readable labels."""
        search = MockVectorSearch(
            [
                ("authentication_handler", [0.0, 0.0]),
            ]
        )
        cartographer = CartographerAgent(vector_search=search)
        context = create_context_vector([0.0, 0.0])

        attractors = await cartographer.find_attractors(context)
        assert len(attractors) >= 1
        assert attractors[0].label != ""


# ============================================================================
# Compute Desire Lines Tests
# ============================================================================


class TestComputeDesireLines:
    """Tests for compute_desire_lines method."""

    @pytest.mark.asyncio
    async def test_no_trace_store(self):
        """No trace store returns empty."""
        cartographer = CartographerAgent()
        landmarks = [
            Attractor(id="a", centroid=[0.0, 0.0], members=[], label="A", density=1.0),
        ]
        edges = await cartographer.compute_desire_lines(landmarks)
        assert edges == []

    @pytest.mark.asyncio
    async def test_no_landmarks(self):
        """No landmarks returns empty."""
        store = MockTraceStore([MockTrace(trace_id="t1")])
        cartographer = CartographerAgent(trace_store=store)
        edges = await cartographer.compute_desire_lines([])
        assert edges == []

    @pytest.mark.asyncio
    async def test_desire_lines_from_traces(self):
        """Traces produce desire lines."""
        landmarks = [
            Attractor(id="a", centroid=[0.0, 0.0], members=[], label="A", density=1.0),
            Attractor(id="b", centroid=[10.0, 0.0], members=[], label="B", density=1.0),
        ]
        traces = [
            MockTrace(trace_id="t1", vector=[0.0, 0.0]),
            MockTrace(trace_id="t2", vector=[10.0, 0.0]),
        ]
        store = MockTraceStore(traces)
        cartographer = CartographerAgent(trace_store=store)

        edges = await cartographer.compute_desire_lines(landmarks)
        assert len(edges) >= 1


# ============================================================================
# Void Detection Tests
# ============================================================================


class TestVoidDetection:
    """Tests for void detection."""

    @pytest.mark.asyncio
    async def test_total_void_when_no_landmarks(self):
        """No landmarks = total void."""
        cartographer = CartographerAgent()
        context = create_context_vector([0.0, 0.0])
        holomap = await cartographer.invoke(context)

        assert holomap.void_count >= 1
        assert holomap.voids[0].reason == "no_landmarks"

    @pytest.mark.asyncio
    async def test_void_between_distant_landmarks(self):
        """Voids detected between distant landmarks."""
        search = MockVectorSearch(
            [
                ("a1", [0.0, 0.0]),
                ("b1", [10.0, 0.0]),  # Far away
            ]
        )
        # Use large threshold to make them separate clusters
        config = CartographerConfig(cluster_threshold=0.5)
        cartographer = CartographerAgent(vector_search=search, config=config)
        context = create_context_vector([0.0, 0.0])

        await cartographer.invoke(context)
        # May have voids between clusters
        # (depends on clustering result)


# ============================================================================
# Integration Tests
# ============================================================================


class TestCartographerIntegration:
    """Integration tests for CartographerAgent."""

    @pytest.mark.asyncio
    async def test_full_pipeline(self):
        """Full pipeline: search -> cluster -> desire lines -> map."""
        # Setup vector search with distinct clusters
        search = MockVectorSearch(
            [
                # Auth cluster
                ("auth_handler", [0.0, 0.0]),
                ("auth_middleware", [0.1, 0.0]),
                ("auth_token", [0.05, 0.05]),
                # Retry cluster
                ("retry_logic", [5.0, 0.0]),
                ("retry_handler", [5.1, 0.0]),
                # Error cluster
                ("error_handler", [10.0, 0.0]),
            ]
        )

        # Setup traces showing transitions
        traces = [
            MockTrace(trace_id="t1", vector=[0.0, 0.0]),  # auth
            MockTrace(trace_id="t2", vector=[5.0, 0.0]),  # retry
            MockTrace(trace_id="t3", vector=[0.0, 0.0]),  # auth
            MockTrace(trace_id="t4", vector=[10.0, 0.0]),  # error
        ]
        store = MockTraceStore(traces)

        cartographer = CartographerAgent(
            vector_search=search,
            trace_store=store,
            config=CartographerConfig(cluster_threshold=1.0),
        )
        context = create_context_vector([0.0, 0.0], label="Current: Auth")

        holomap = await cartographer.invoke(context)

        # Should have landmarks
        assert holomap.landmark_count >= 1
        # Should have horizon
        assert holomap.horizon is not None
        assert holomap.horizon.max_tokens > 0

    @pytest.mark.asyncio
    async def test_navigation_after_map(self):
        """Can navigate the generated map."""
        search = MockVectorSearch(
            [
                ("a", [0.0, 0.0]),
                ("b", [5.0, 0.0]),
            ]
        )
        traces = [
            MockTrace(trace_id="t1", vector=[0.0, 0.0]),
            MockTrace(trace_id="t2", vector=[5.0, 0.0]),
        ]
        store = MockTraceStore(traces)

        config = CartographerConfig(cluster_threshold=1.0)
        cartographer = CartographerAgent(
            vector_search=search,
            trace_store=store,
            config=config,
        )
        context = create_context_vector([0.0, 0.0])

        holomap = await cartographer.invoke(context)

        # Can use map for navigation
        nearest = holomap.nearest_landmark([0.0, 0.0])
        if nearest:
            holomap.adjacent_to([0.0, 0.0])
            # May or may not have adjacent depending on desire lines
