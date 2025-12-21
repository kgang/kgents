"""
Tests for TerrariumView: Observer-Dependent Lens Over Mark Streams.

These tests verify:
1. TerrariumView laws (fault isolation, observer dependence, selection monotonicity)
2. Selection queries (predicates, filtering, pagination)
3. Lens configurations (timeline, graph, summary, detail)
4. Projection to SceneGraph
5. View store management

Philosophy:
    "Same traces + different lens = different scene" — Law 2
"""

from __future__ import annotations

from datetime import datetime, timedelta

import pytest

from protocols.agentese.projection.scene import (
    LayoutDirective,
    SceneGraph,
    SceneNodeKind,
)
from protocols.agentese.projection.terrarium_view import (
    LensConfig,
    LensMode,
    SelectionOperator,
    SelectionPredicate,
    SelectionQuery,
    TerrariumView,
    TerrariumViewStore,
    ViewStatus,
    generate_view_id,
)

# =============================================================================
# Test Fixtures
# =============================================================================


@pytest.fixture
def sample_traces() -> list[dict]:
    """Create sample trace dicts for testing."""
    base_time = datetime.now()
    return [
        {
            "id": "trace-001",
            "origin": "witness",
            "stimulus": {"kind": "git", "content": "Commit abc"},
            "response": {"kind": "thought", "content": "Noticed commit"},
            "timestamp": (base_time - timedelta(minutes=5)).isoformat(),
            "phase": "SENSE",
            "walk_id": "walk-001",
            "tags": ["git", "commit"],
            "links": [],
            "umwelt": {"observer_id": "system", "trust_level": 1},
        },
        {
            "id": "trace-002",
            "origin": "witness",
            "stimulus": {"kind": "file", "content": "File changed"},
            "response": {"kind": "thought", "content": "Detected file change"},
            "timestamp": (base_time - timedelta(minutes=3)).isoformat(),
            "phase": "SENSE",
            "walk_id": "walk-001",
            "tags": ["file", "watch"],
            "links": [{"source": "trace-001", "target": "trace-002", "relation": "CAUSES"}],
            "umwelt": {"observer_id": "system", "trust_level": 1},
        },
        {
            "id": "trace-003",
            "origin": "brain",
            "stimulus": {"kind": "agentese", "content": "self.brain.capture"},
            "response": {"kind": "projection", "content": "Captured thought"},
            "timestamp": (base_time - timedelta(minutes=1)).isoformat(),
            "phase": "ACT",
            "walk_id": "walk-002",
            "tags": ["brain", "capture"],
            "links": [],
            "umwelt": {"observer_id": "developer", "trust_level": 2},
        },
    ]


# =============================================================================
# ID Generation Tests
# =============================================================================


class TestIdGeneration:
    """Tests for view ID generation."""

    def test_view_id_format(self) -> None:
        """View IDs have correct format."""
        view_id = generate_view_id()
        assert view_id.startswith("tv-")
        assert len(view_id) == 15

    def test_ids_unique(self) -> None:
        """Generated IDs are unique."""
        ids = {generate_view_id() for _ in range(100)}
        assert len(ids) == 100


# =============================================================================
# SelectionPredicate Tests
# =============================================================================


class TestSelectionPredicate:
    """Tests for SelectionPredicate filtering."""

    def test_equals_predicate(self) -> None:
        """EQ operator matches equal values."""
        pred = SelectionPredicate(field="origin", op=SelectionOperator.EQ, value="witness")

        assert pred.matches({"origin": "witness"}) is True
        assert pred.matches({"origin": "brain"}) is False

    def test_not_equals_predicate(self) -> None:
        """NE operator matches non-equal values."""
        pred = SelectionPredicate(field="origin", op=SelectionOperator.NE, value="witness")

        assert pred.matches({"origin": "brain"}) is True
        assert pred.matches({"origin": "witness"}) is False

    def test_in_predicate(self) -> None:
        """IN operator matches values in list."""
        pred = SelectionPredicate(
            field="origin",
            op=SelectionOperator.IN,
            value=["witness", "brain"],
        )

        assert pred.matches({"origin": "witness"}) is True
        assert pred.matches({"origin": "brain"}) is True
        assert pred.matches({"origin": "gardener"}) is False

    def test_contains_predicate(self) -> None:
        """CONTAINS operator matches substrings."""
        pred = SelectionPredicate(
            field="content",
            op=SelectionOperator.CONTAINS,
            value="git",
        )

        assert pred.matches({"content": "git commit abc"}) is True
        assert pred.matches({"content": "file changed"}) is False

    def test_starts_with_predicate(self) -> None:
        """STARTS_WITH operator matches prefixes."""
        pred = SelectionPredicate(
            field="id",
            op=SelectionOperator.STARTS_WITH,
            value="trace-",
        )

        assert pred.matches({"id": "trace-001"}) is True
        assert pred.matches({"id": "walk-001"}) is False

    def test_missing_field_returns_false(self) -> None:
        """Missing field returns False (except for NE)."""
        eq_pred = SelectionPredicate(field="missing", op=SelectionOperator.EQ, value="x")
        ne_pred = SelectionPredicate(field="missing", op=SelectionOperator.NE, value="x")

        assert eq_pred.matches({"other": "y"}) is False
        assert ne_pred.matches({"other": "y"}) is True  # NE on missing = True


# =============================================================================
# SelectionQuery Tests
# =============================================================================


class TestSelectionQuery:
    """Tests for SelectionQuery filtering and pagination."""

    def test_all_query(self, sample_traces: list[dict]) -> None:
        """All query returns all traces."""
        query = SelectionQuery.all()
        result = query.apply(sample_traces)
        assert len(result) == 3

    def test_by_origin_query(self, sample_traces: list[dict]) -> None:
        """by_origin filters correctly."""
        query = SelectionQuery.by_origin("witness")
        result = query.apply(sample_traces)

        assert len(result) == 2
        assert all(t["origin"] == "witness" for t in result)

    def test_by_walk_query(self, sample_traces: list[dict]) -> None:
        """by_walk filters correctly."""
        query = SelectionQuery.by_walk("walk-001")
        result = query.apply(sample_traces)

        assert len(result) == 2
        assert all(t["walk_id"] == "walk-001" for t in result)

    def test_by_phase_query(self, sample_traces: list[dict]) -> None:
        """by_phase filters correctly."""
        query = SelectionQuery.by_phase("SENSE")
        result = query.apply(sample_traces)

        assert len(result) == 2

    def test_recent_query(self, sample_traces: list[dict]) -> None:
        """recent returns limited traces in descending order."""
        query = SelectionQuery.recent(limit=2)
        result = query.apply(sample_traces)

        assert len(result) == 2
        # Should be most recent first
        assert result[0]["id"] == "trace-003"

    def test_with_predicate_chains(self, sample_traces: list[dict]) -> None:
        """Predicates can be chained."""
        query = SelectionQuery.by_origin("witness").with_predicate(
            SelectionPredicate(field="phase", op=SelectionOperator.EQ, value="SENSE")
        )
        result = query.apply(sample_traces)

        assert len(result) == 2

    def test_with_limit(self, sample_traces: list[dict]) -> None:
        """Limit restricts result count."""
        query = SelectionQuery.all().with_limit(1)
        result = query.apply(sample_traces)

        assert len(result) == 1

    def test_ordering(self, sample_traces: list[dict]) -> None:
        """Results are ordered by specified field."""
        asc_query = SelectionQuery(descending=False, order_by="id")
        result = asc_query.apply(sample_traces)

        assert result[0]["id"] == "trace-001"
        assert result[-1]["id"] == "trace-003"

    def test_serialization(self) -> None:
        """Query can be serialized."""
        query = SelectionQuery.by_origin("witness").with_limit(50)
        data = query.to_dict()

        assert len(data["predicates"]) == 1
        assert data["predicates"][0]["field"] == "origin"
        assert data["limit"] == 50


# =============================================================================
# LensConfig Tests
# =============================================================================


class TestLensConfig:
    """Tests for LensConfig transformation modes."""

    def test_timeline_lens(self) -> None:
        """Timeline lens has correct defaults."""
        lens = LensConfig.timeline()
        assert lens.mode == LensMode.TIMELINE
        assert lens.show_links is False

    def test_timeline_with_links(self) -> None:
        """Timeline lens can show links."""
        lens = LensConfig.timeline(show_links=True)
        assert lens.show_links is True

    def test_graph_lens(self) -> None:
        """Graph lens has correct settings."""
        lens = LensConfig.graph()
        assert lens.mode == LensMode.GRAPH
        assert lens.show_links is True
        assert lens.layout.direction == "free"

    def test_summary_lens(self) -> None:
        """Summary lens has grouping."""
        lens = LensConfig.summary(group_by="phase")
        assert lens.mode == LensMode.SUMMARY
        assert lens.group_by == "phase"

    def test_detail_lens(self) -> None:
        """Detail lens shows full info."""
        lens = LensConfig.detail()
        assert lens.mode == LensMode.DETAIL
        assert lens.show_umwelt is True
        assert lens.show_metadata is True

    def test_serialization(self) -> None:
        """Lens can be serialized."""
        lens = LensConfig.graph()
        data = lens.to_dict()

        assert data["mode"] == "GRAPH"
        assert data["show_links"] is True


# =============================================================================
# TerrariumView Tests
# =============================================================================


class TestTerrariumView:
    """Tests for TerrariumView projection."""

    def test_create_timeline_view(self) -> None:
        """Can create timeline view."""
        view = TerrariumView.timeline("Witness Activity", origin="witness")

        assert view.name == "Witness Activity"
        assert view.lens.mode == LensMode.TIMELINE

    def test_create_graph_view(self) -> None:
        """Can create graph view."""
        view = TerrariumView.graph("Walk Graph", walk_id="walk-001")

        assert view.lens.mode == LensMode.GRAPH
        assert len(view.selection.predicates) == 1

    def test_create_summary_view(self) -> None:
        """Can create summary view."""
        view = TerrariumView.summary("Activity Summary", group_by="origin")

        assert view.lens.mode == LensMode.SUMMARY

    def test_project_timeline(self, sample_traces: list[dict]) -> None:
        """Timeline projection produces SceneGraph."""
        view = TerrariumView.timeline("Test", origin="witness")
        scene = view.project(sample_traces)

        assert isinstance(scene, SceneGraph)
        assert scene.node_count() == 2  # 2 witness traces
        assert all(n.kind == SceneNodeKind.TRACE for n in scene.nodes)

    def test_project_graph(self, sample_traces: list[dict]) -> None:
        """Graph projection includes edges."""
        # Add link to sample traces
        view = TerrariumView.graph("Test", walk_id="walk-001")
        scene = view.project(sample_traces)

        assert scene.node_count() == 2
        # Graph uses free layout
        assert scene.layout.direction == "free"

    def test_project_summary(self, sample_traces: list[dict]) -> None:
        """Summary projection groups traces."""
        view = TerrariumView.summary("Test", group_by="origin")
        scene = view.project(sample_traces)

        # Should have 2 groups: witness and brain
        assert scene.node_count() == 2
        assert all(n.kind == SceneNodeKind.GROUP for n in scene.nodes)

    def test_project_detail(self, sample_traces: list[dict]) -> None:
        """Detail projection shows full trace."""
        view = TerrariumView(
            name="Detail",
            selection=SelectionQuery.all().with_limit(1),
            lens=LensConfig.detail(),
        )
        scene = view.project(sample_traces)

        # Detail includes umwelt panel
        assert scene.node_count() >= 1

    def test_project_empty_traces(self) -> None:
        """Projection of empty traces returns empty graph."""
        view = TerrariumView.timeline("Test")
        scene = view.project([])

        assert scene.is_empty()

    def test_view_is_frozen(self) -> None:
        """TerrariumView is immutable."""
        view = TerrariumView.timeline("Test")
        with pytest.raises(Exception):
            view.name = "Modified"  # type: ignore

    def test_with_selection_immutable(self) -> None:
        """with_selection returns new view."""
        original = TerrariumView.timeline("Test")
        modified = original.with_selection(SelectionQuery.by_origin("brain"))

        assert original.selection != modified.selection

    def test_with_lens_immutable(self) -> None:
        """with_lens returns new view."""
        original = TerrariumView.timeline("Test")
        modified = original.with_lens(LensConfig.graph())

        assert original.lens.mode == LensMode.TIMELINE
        assert modified.lens.mode == LensMode.GRAPH

    def test_serialization(self) -> None:
        """View can be serialized."""
        view = TerrariumView(
            name="Test View",
            selection=SelectionQuery.by_origin("witness"),
            lens=LensConfig.timeline(),
            observer_id="developer",
            trust_level=2,
        )

        data = view.to_dict()

        assert data["name"] == "Test View"
        assert data["observer_id"] == "developer"
        assert data["trust_level"] == 2


# =============================================================================
# TerrariumView Laws Tests
# =============================================================================


class TestTerrariumViewLaws:
    """
    Tests for TerrariumView laws.

    Law 1 (Fault Isolation): Crashed view doesn't affect other views
    Law 2 (Observer Dependence): Same traces + different lens = different scene
    Law 3 (Selection Monotonicity): Narrower query ⊂ wider query results
    """

    def test_law1_fault_isolation(self, sample_traces: list[dict]) -> None:
        """Law 1: Crashed view doesn't affect other views."""
        store = TerrariumViewStore()

        view1 = store.add(TerrariumView.timeline("View 1"))
        view2 = store.add(TerrariumView.timeline("View 2"))

        # Simulate crash of view1
        store.mark_crashed(view1.id, "Test error")

        # View2 should still work
        view2_fresh = store.get(view2.id)
        assert view2_fresh is not None
        assert view2_fresh.status == ViewStatus.IDLE

        # View1 should be crashed
        view1_crashed = store.get(view1.id)
        assert view1_crashed is not None
        assert view1_crashed.status == ViewStatus.CRASHED
        assert view1_crashed.metadata.get("crash_error") == "Test error"

    def test_law2_observer_dependence(self, sample_traces: list[dict]) -> None:
        """Law 2: Same traces + different lens = different scene."""
        timeline_view = TerrariumView(
            name="Timeline",
            selection=SelectionQuery.all(),
            lens=LensConfig.timeline(),
        )
        summary_view = TerrariumView(
            name="Summary",
            selection=SelectionQuery.all(),
            lens=LensConfig.summary(group_by="origin"),
        )

        timeline_scene = timeline_view.project(sample_traces)
        summary_scene = summary_view.project(sample_traces)

        # Same traces, different structure
        assert timeline_scene.node_count() == 3  # All traces as nodes
        assert summary_scene.node_count() == 2  # Grouped by origin

        # Different node kinds
        assert all(n.kind == SceneNodeKind.TRACE for n in timeline_scene.nodes)
        assert all(n.kind == SceneNodeKind.GROUP for n in summary_scene.nodes)

    def test_law3_selection_monotonicity(self, sample_traces: list[dict]) -> None:
        """Law 3: Narrower query ⊂ wider query results."""
        wide_query = SelectionQuery.all()
        narrow_query = SelectionQuery.by_origin("witness")

        wide_results = wide_query.apply(sample_traces)
        narrow_results = narrow_query.apply(sample_traces)

        # Narrow results should be subset of wide results
        narrow_ids = {t["id"] for t in narrow_results}
        wide_ids = {t["id"] for t in wide_results}

        assert narrow_ids <= wide_ids  # Subset relation
        assert len(narrow_results) <= len(wide_results)


# =============================================================================
# TerrariumViewStore Tests
# =============================================================================


class TestTerrariumViewStore:
    """Tests for TerrariumViewStore management."""

    def test_add_and_get(self) -> None:
        """Can add and retrieve views."""
        store = TerrariumViewStore()
        view = TerrariumView.timeline("Test")

        store.add(view)
        retrieved = store.get(view.id)

        assert retrieved is not None
        assert retrieved.name == "Test"

    def test_remove(self) -> None:
        """Can remove views."""
        store = TerrariumViewStore()
        view = store.add(TerrariumView.timeline("Test"))

        assert store.remove(view.id) is True
        assert store.get(view.id) is None
        assert store.remove(view.id) is False  # Already removed

    def test_all_views(self) -> None:
        """Can get all views."""
        store = TerrariumViewStore()
        store.add(TerrariumView.timeline("V1"))
        store.add(TerrariumView.timeline("V2"))

        all_views = store.all()
        assert len(all_views) == 2

    def test_active_views(self) -> None:
        """Can filter to active views only."""
        store = TerrariumViewStore()

        # Create views with different statuses
        view1 = TerrariumView(name="Active", status=ViewStatus.ACTIVE)
        view2 = TerrariumView(name="Idle", status=ViewStatus.IDLE)

        store.add(view1)
        store.add(view2)

        active = store.active()
        assert len(active) == 1
        assert active[0].status == ViewStatus.ACTIVE

    def test_by_observer(self) -> None:
        """Can filter by observer."""
        store = TerrariumViewStore()

        store.add(TerrariumView(name="V1", observer_id="alice"))
        store.add(TerrariumView(name="V2", observer_id="alice"))
        store.add(TerrariumView(name="V3", observer_id="bob"))

        alice_views = store.by_observer("alice")
        assert len(alice_views) == 2

    def test_mark_crashed(self) -> None:
        """Can mark view as crashed."""
        store = TerrariumViewStore()
        view = store.add(TerrariumView.timeline("Test"))

        crashed = store.mark_crashed(view.id, "Simulated failure")

        assert crashed is not None
        assert crashed.status == ViewStatus.CRASHED
        assert crashed.metadata["crash_error"] == "Simulated failure"

    def test_count_and_clear(self) -> None:
        """Count and clear work correctly."""
        store = TerrariumViewStore()
        store.add(TerrariumView.timeline("V1"))
        store.add(TerrariumView.timeline("V2"))

        assert store.count() == 2

        store.clear()
        assert store.count() == 0


# =============================================================================
# Integration Tests
# =============================================================================


class TestIntegration:
    """Integration tests for TerrariumView with SceneGraph."""

    def test_multi_view_composition(self, sample_traces: list[dict]) -> None:
        """Multiple views can project same traces differently."""
        views = [
            TerrariumView.timeline("Timeline", limit=50),
            TerrariumView.summary("Summary", group_by="origin"),
            TerrariumView.graph("Graph", walk_id="walk-001"),
        ]

        scenes = [view.project(sample_traces) for view in views]

        # All produce valid SceneGraphs
        assert all(isinstance(s, SceneGraph) for s in scenes)

        # Different structures
        node_counts = [s.node_count() for s in scenes]
        assert len(set(node_counts)) > 1  # At least 2 different counts

    def test_view_with_trust_filtering(self, sample_traces: list[dict]) -> None:
        """Views can be filtered by trust level."""
        # View that only shows high-trust traces
        high_trust_query = SelectionQuery.all().with_predicate(
            SelectionPredicate(
                field="trust_level",
                op=SelectionOperator.GTE,
                value=2,
            )
        )

        # Add trust_level to sample traces (simulate nested access)
        for trace in sample_traces:
            trace["trust_level"] = trace.get("umwelt", {}).get("trust_level", 0)

        view = TerrariumView(
            name="High Trust Only",
            selection=high_trust_query,
            lens=LensConfig.timeline(),
            trust_level=2,
        )

        scene = view.project(sample_traces)

        # Only trace-003 has trust_level >= 2
        assert scene.node_count() == 1

    def test_scene_metadata_includes_view_info(self, sample_traces: list[dict]) -> None:
        """Projected scenes include view metadata."""
        view = TerrariumView(
            name="Annotated View",
            selection=SelectionQuery.recent(10),
            lens=LensConfig.timeline(),
        )

        scene = view.project(sample_traces)

        assert "view_id" in scene.metadata
        assert scene.metadata["mode"] == "timeline"
        assert scene.title == "Annotated View"
