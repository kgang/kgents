"""
Tests for Crystal Trail Adapter: Phase 5A.

Tests the bridge between crystals and Trail visualization.

See: services/witness/crystal_trail.py
See: plans/witness-crystallization.md (Phase 5)
"""

from __future__ import annotations

from datetime import UTC, datetime

import pytest

from services.witness.crystal import Crystal, CrystalId, CrystalLevel, MoodVector
from services.witness.crystal_store import CrystalStore, reset_crystal_store, set_crystal_store
from services.witness.crystal_trail import (
    CrystalGraph,
    CrystalGraphEdge,
    CrystalGraphNode,
    CrystalTrailAdapter,
    crystals_to_graph,
    format_graph_response,
    get_hierarchy_graph,
)
from services.witness.mark import MarkId

# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def session_crystal() -> Crystal:
    """Create a level-0 (SESSION) crystal."""
    return Crystal(
        id=CrystalId("crystal-session-001"),
        level=CrystalLevel.SESSION,
        insight="Completed Phase 4 integration and streaming",
        significance="Real-time crystal updates now available",
        principles=("composable", "generative"),
        topics=frozenset({"witness", "streaming", "phase4"}),
        source_marks=(MarkId("mark-001"), MarkId("mark-002"), MarkId("mark-003")),
        source_crystals=(),
        mood=MoodVector(brightness=0.8, warmth=0.7),
        confidence=0.9,
        crystallized_at=datetime.now(UTC),
    )


@pytest.fixture
def day_crystal(session_crystal: Crystal) -> Crystal:
    """Create a level-1 (DAY) crystal that compresses session crystals."""
    return Crystal(
        id=CrystalId("crystal-day-001"),
        level=CrystalLevel.DAY,
        insight="Day of witness improvements: streaming + integration",
        significance="Foundation for visual projection complete",
        principles=("composable",),
        topics=frozenset({"witness", "crystallization"}),
        source_marks=(),
        source_crystals=(session_crystal.id,),
        mood=MoodVector(brightness=0.75),
        confidence=0.85,
        crystallized_at=datetime.now(UTC),
    )


@pytest.fixture
def week_crystal(day_crystal: Crystal) -> Crystal:
    """Create a level-2 (WEEK) crystal."""
    return Crystal(
        id=CrystalId("crystal-week-001"),
        level=CrystalLevel.WEEK,
        insight="Week 52: Crystallization infrastructure complete",
        significance="Memory system operational",
        principles=("composable", "generative", "tasteful"),
        topics=frozenset({"witness", "infrastructure"}),
        source_marks=(),
        source_crystals=(day_crystal.id,),
        mood=MoodVector(brightness=0.9, saturation=0.8),
        confidence=0.88,
        crystallized_at=datetime.now(UTC),
    )


@pytest.fixture
def mock_store(
    session_crystal: Crystal,
    day_crystal: Crystal,
    week_crystal: Crystal,
) -> CrystalStore:
    """Create a store with crystals at multiple levels."""
    store = CrystalStore()

    # Add crystals
    for crystal in [session_crystal, day_crystal, week_crystal]:
        store._crystals[crystal.id] = crystal
        store._by_level[crystal.level].append(crystal.id)
        store._timeline.append(crystal.id)

    set_crystal_store(store)
    yield store
    reset_crystal_store()


# =============================================================================
# CrystalGraphNode Tests
# =============================================================================


class TestCrystalGraphNode:
    """Tests for CrystalGraphNode dataclass."""

    def test_to_dict(self) -> None:
        """Test node serialization."""
        node = CrystalGraphNode(
            id="crystal-abc",
            type="crystal",
            position={"x": 100, "y": 200},
            data={
                "insight": "Test insight",
                "level": "SESSION",
            },
        )

        result = node.to_dict()

        assert result["id"] == "crystal-abc"
        assert result["type"] == "crystal"
        assert result["position"]["x"] == 100
        assert result["position"]["y"] == 200
        assert result["data"]["insight"] == "Test insight"

    def test_default_values(self) -> None:
        """Test default values."""
        node = CrystalGraphNode(id="test")

        assert node.type == "crystal"
        assert node.position == {"x": 0, "y": 0}
        assert node.data == {}


# =============================================================================
# CrystalGraphEdge Tests
# =============================================================================


class TestCrystalGraphEdge:
    """Tests for CrystalGraphEdge dataclass."""

    def test_to_dict(self) -> None:
        """Test edge serialization."""
        edge = CrystalGraphEdge(
            id="edge-0",
            source="node-a",
            target="node-b",
            label="compresses",
            type="compression",
            animated=True,
            style={"strokeDasharray": "5 5"},
        )

        result = edge.to_dict()

        assert result["id"] == "edge-0"
        assert result["source"] == "node-a"
        assert result["target"] == "node-b"
        assert result["label"] == "compresses"
        assert result["animated"] is True

    def test_default_values(self) -> None:
        """Test default values."""
        edge = CrystalGraphEdge(
            id="edge-0",
            source="a",
            target="b",
        )

        assert edge.label == "compresses"
        assert edge.type == "compression"
        assert edge.animated is False


# =============================================================================
# CrystalGraph Tests
# =============================================================================


class TestCrystalGraph:
    """Tests for CrystalGraph dataclass."""

    def test_to_dict_empty(self) -> None:
        """Test empty graph serialization."""
        graph = CrystalGraph(nodes=[], edges=[])

        result = graph.to_dict()

        assert result["nodes"] == []
        assert result["edges"] == []
        assert result["total_crystals"] == 0
        assert result["time_range"] is None

    def test_to_dict_with_time_range(self) -> None:
        """Test graph with time range."""
        now = datetime.now(UTC)
        graph = CrystalGraph(
            nodes=[],
            edges=[],
            time_range=(now, now),
        )

        result = graph.to_dict()

        assert result["time_range"] is not None
        assert len(result["time_range"]) == 2


# =============================================================================
# CrystalTrailAdapter Tests
# =============================================================================


class TestCrystalTrailAdapter:
    """Tests for CrystalTrailAdapter."""

    def test_to_graph_empty_store(self) -> None:
        """Test conversion with empty store."""
        store = CrystalStore()
        adapter = CrystalTrailAdapter(store)

        graph = adapter.to_graph()

        assert len(graph.nodes) == 0
        assert len(graph.edges) == 0
        assert graph.total_crystals == 0

    def test_to_graph_with_crystals(
        self,
        mock_store: CrystalStore,
        session_crystal: Crystal,
        day_crystal: Crystal,
        week_crystal: Crystal,
    ) -> None:
        """Test conversion with crystals at multiple levels."""
        adapter = CrystalTrailAdapter(mock_store)

        graph = adapter.to_graph()

        # Should have 3 nodes (one per crystal)
        assert len(graph.nodes) == 3
        assert graph.total_crystals == 3

        # Should have 2 edges (day→session, week→day)
        assert len(graph.edges) == 2

        # Check level counts
        assert graph.level_counts["SESSION"] == 1
        assert graph.level_counts["DAY"] == 1
        assert graph.level_counts["WEEK"] == 1
        assert graph.level_counts["EPOCH"] == 0

    def test_to_graph_level_filter(
        self,
        mock_store: CrystalStore,
    ) -> None:
        """Test filtering by level."""
        adapter = CrystalTrailAdapter(mock_store)

        # Only SESSION level
        graph = adapter.to_graph(level_filter=CrystalLevel.SESSION)

        assert len(graph.nodes) == 1
        assert graph.nodes[0].data["level"] == "SESSION"

    def test_node_positions_by_level(
        self,
        mock_store: CrystalStore,
    ) -> None:
        """Test that nodes are positioned by level (y-axis)."""
        adapter = CrystalTrailAdapter(mock_store)
        graph = adapter.to_graph()

        # Find nodes by level
        session_node = next(n for n in graph.nodes if n.data["level"] == "SESSION")
        day_node = next(n for n in graph.nodes if n.data["level"] == "DAY")
        week_node = next(n for n in graph.nodes if n.data["level"] == "WEEK")

        # SESSION should be lowest (highest y)
        assert session_node.position["y"] > day_node.position["y"]
        # DAY should be in middle
        assert day_node.position["y"] > week_node.position["y"]
        # WEEK should be highest (lowest y)
        assert week_node.position["y"] == 150  # From LEVEL_Y_POSITIONS

    def test_node_data_trail_compatible(
        self,
        mock_store: CrystalStore,
    ) -> None:
        """Test that node data is compatible with TrailGraph.tsx."""
        adapter = CrystalTrailAdapter(mock_store)
        graph = adapter.to_graph()

        node = graph.nodes[0]
        data = node.data

        # Required TrailGraph fields
        assert "path" in data
        assert "holon" in data
        assert "step_index" in data
        assert "reasoning" in data

        # Crystal-specific fields
        assert "crystal_id" in data
        assert "insight" in data
        assert "confidence" in data

    def test_edges_connect_compression_chain(
        self,
        mock_store: CrystalStore,
        session_crystal: Crystal,
        day_crystal: Crystal,
    ) -> None:
        """Test that edges represent compression relationships."""
        adapter = CrystalTrailAdapter(mock_store)
        graph = adapter.to_graph()

        # Find edge from session to day
        session_node_id = f"crystal-{str(session_crystal.id)[:12]}"
        day_node_id = f"crystal-{str(day_crystal.id)[:12]}"

        # Edge should go from source (session) to target (day)
        edge = next(
            (e for e in graph.edges if e.target == day_node_id),
            None,
        )

        assert edge is not None
        assert edge.source == session_node_id
        assert edge.label == "compresses"
        assert edge.animated is True

    def test_get_crystal_detail(
        self,
        mock_store: CrystalStore,
        session_crystal: Crystal,
    ) -> None:
        """Test getting detailed crystal info."""
        adapter = CrystalTrailAdapter(mock_store)

        detail = adapter.get_crystal_detail(session_crystal.id)

        assert detail is not None
        assert detail["id"] == str(session_crystal.id)
        assert detail["level"] == "SESSION"
        assert detail["insight"] == session_crystal.insight
        assert "source_marks" in detail
        assert len(detail["source_marks"]) == 3

    def test_get_crystal_detail_not_found(
        self,
        mock_store: CrystalStore,
    ) -> None:
        """Test getting detail for nonexistent crystal."""
        adapter = CrystalTrailAdapter(mock_store)

        detail = adapter.get_crystal_detail(CrystalId("nonexistent"))

        assert detail is None


# =============================================================================
# Standalone Function Tests
# =============================================================================


class TestStandaloneFunctions:
    """Tests for standalone convenience functions."""

    def test_crystals_to_graph(
        self,
        session_crystal: Crystal,
        day_crystal: Crystal,
    ) -> None:
        """Test crystals_to_graph with explicit list."""
        graph = crystals_to_graph(crystals=[session_crystal, day_crystal])

        assert len(graph.nodes) == 2
        assert len(graph.edges) == 1

    def test_get_hierarchy_graph(
        self,
        mock_store: CrystalStore,
    ) -> None:
        """Test get_hierarchy_graph with store."""
        graph = get_hierarchy_graph(mock_store)

        assert graph.total_crystals == 3

    def test_format_graph_response(
        self,
        mock_store: CrystalStore,
    ) -> None:
        """Test API response formatting."""
        adapter = CrystalTrailAdapter(mock_store)
        graph = adapter.to_graph()

        response = format_graph_response(graph)

        # AGENTESE response structure
        assert "summary" in response
        assert "content" in response
        assert "metadata" in response

        # Metadata contains graph data
        assert "nodes" in response["metadata"]
        assert "edges" in response["metadata"]
        assert response["metadata"]["mode"] == "crystal"


# =============================================================================
# Edge Case Tests
# =============================================================================


class TestEdgeCases:
    """Tests for edge cases and error handling."""

    def test_crystal_without_sources_in_store(self) -> None:
        """Test handling of crystals with source_crystals not in store."""
        store = CrystalStore()

        # Day crystal referencing nonexistent session crystal
        orphan_day = Crystal(
            id=CrystalId("crystal-orphan-day"),
            level=CrystalLevel.DAY,
            insight="Day crystal with missing source",
            significance="Source was deleted",
            principles=(),
            topics=frozenset(),
            source_marks=(),
            source_crystals=(CrystalId("crystal-missing"),),
            confidence=0.7,
            crystallized_at=datetime.now(UTC),
        )

        store._crystals[orphan_day.id] = orphan_day
        store._by_level[orphan_day.level].append(orphan_day.id)
        store._timeline.append(orphan_day.id)

        adapter = CrystalTrailAdapter(store)
        graph = adapter.to_graph()

        # Should still create node, just no edge
        assert len(graph.nodes) == 1
        assert len(graph.edges) == 0

    def test_limit_per_level(self) -> None:
        """Test limit parameter restricts crystals per level."""
        store = CrystalStore()

        # Create 5 session crystals
        for i in range(5):
            crystal = Crystal(
                id=CrystalId(f"crystal-session-{i}"),
                level=CrystalLevel.SESSION,
                insight=f"Session {i}",
                significance="",
                principles=(),
                topics=frozenset(),
                source_marks=(MarkId("mark-x"),),
                confidence=0.8,
                crystallized_at=datetime.now(UTC),
            )
            store._crystals[crystal.id] = crystal
            store._by_level[crystal.level].append(crystal.id)
            store._timeline.append(crystal.id)

        adapter = CrystalTrailAdapter(store)
        graph = adapter.to_graph(limit=3)

        # Should only have 3 nodes (limited)
        assert len(graph.nodes) == 3

    def test_time_range_computation(
        self,
        mock_store: CrystalStore,
    ) -> None:
        """Test that time range is computed from crystals."""
        adapter = CrystalTrailAdapter(mock_store)
        graph = adapter.to_graph()

        assert graph.time_range is not None
        assert graph.time_range[0] <= graph.time_range[1]
