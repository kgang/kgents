"""Tests for CrystalStore implementations."""

from datetime import datetime, timedelta

import pytest

from ..store import MemoryCrystalStore, compute_stats
from ..types import Action, Determinism, SemanticTrace


def make_trace(
    trace_id: str = "test-123",
    parent_id: str | None = None,
    agent_id: str = "agent-1",
    agent_genus: str = "B",
    action: str = Action.INVOKE,
    determinism: Determinism = Determinism.PROBABILISTIC,
    timestamp: datetime | None = None,
    gas: int = 100,
) -> SemanticTrace:
    """Helper to create test traces."""
    return SemanticTrace(
        trace_id=trace_id,
        parent_id=parent_id,
        timestamp=timestamp or datetime.utcnow(),
        agent_id=agent_id,
        agent_genus=agent_genus,
        action=action,
        inputs={"test": True},
        outputs={"result": "ok"},
        input_hash="hash123",
        input_snapshot=b"test data",
        output_hash="hash456",
        gas_consumed=gas,
        duration_ms=50,
        determinism=determinism,
        metadata={},
    )


class TestMemoryCrystalStore:
    """Tests for MemoryCrystalStore."""

    @pytest.fixture
    def store(self) -> MemoryCrystalStore:
        return MemoryCrystalStore()

    def test_store_and_get(self, store):
        """Can store and retrieve a crystal."""
        crystal = make_trace()
        store.store(crystal)

        retrieved = store.get("test-123")
        assert retrieved is not None
        assert retrieved.trace_id == crystal.trace_id
        assert retrieved.agent_id == crystal.agent_id

    def test_get_nonexistent(self, store):
        """Get returns None for nonexistent trace."""
        assert store.get("nonexistent") is None

    def test_count(self, store):
        """Count tracks stored crystals."""
        assert store.count() == 0

        store.store(make_trace("t1"))
        assert store.count() == 1

        store.store(make_trace("t2"))
        assert store.count() == 2

    def test_clear(self, store):
        """Clear removes all crystals."""
        store.store(make_trace("t1"))
        store.store(make_trace("t2"))
        assert store.count() == 2

        store.clear()
        assert store.count() == 0

    def test_query_all(self, store):
        """Query with no filters returns all."""
        store.store(make_trace("t1"))
        store.store(make_trace("t2"))
        store.store(make_trace("t3"))

        results = store.query()
        assert len(results) == 3

    def test_query_by_agent_id(self, store):
        """Query filters by agent_id."""
        store.store(make_trace("t1", agent_id="agent-a"))
        store.store(make_trace("t2", agent_id="agent-b"))
        store.store(make_trace("t3", agent_id="agent-a"))

        results = store.query(agent_id="agent-a")
        assert len(results) == 2
        assert all(r.agent_id == "agent-a" for r in results)

    def test_query_by_agent_genus(self, store):
        """Query filters by agent_genus."""
        store.store(make_trace("t1", agent_genus="B"))
        store.store(make_trace("t2", agent_genus="G"))
        store.store(make_trace("t3", agent_genus="B"))

        results = store.query(agent_genus="B")
        assert len(results) == 2
        assert all(r.agent_genus == "B" for r in results)

    def test_query_by_action(self, store):
        """Query filters by action."""
        store.store(make_trace("t1", action=Action.INVOKE))
        store.store(make_trace("t2", action=Action.GENERATE))
        store.store(make_trace("t3", action=Action.INVOKE))

        results = store.query(action=Action.INVOKE)
        assert len(results) == 2

    def test_query_by_determinism(self, store):
        """Query filters by determinism."""
        store.store(make_trace("t1", determinism=Determinism.DETERMINISTIC))
        store.store(make_trace("t2", determinism=Determinism.PROBABILISTIC))
        store.store(make_trace("t3", determinism=Determinism.CHAOTIC))

        results = store.query(determinism=Determinism.PROBABILISTIC)
        assert len(results) == 1
        assert results[0].trace_id == "t2"

    def test_query_by_time_range(self, store):
        """Query filters by time range."""
        now = datetime.utcnow()
        old = now - timedelta(hours=2)
        recent = now - timedelta(hours=1)

        store.store(make_trace("t1", timestamp=old))
        store.store(make_trace("t2", timestamp=recent))
        store.store(make_trace("t3", timestamp=now))

        # Query for last 90 minutes
        results = store.query(start_time=now - timedelta(minutes=90))
        assert len(results) == 2

        # Query for specific range
        results = store.query(
            start_time=old,
            end_time=recent + timedelta(seconds=1),
        )
        assert len(results) == 2

    def test_query_combined_filters(self, store):
        """Query with multiple filters ANDs them."""
        store.store(make_trace("t1", agent_id="a1", action=Action.INVOKE))
        store.store(make_trace("t2", agent_id="a1", action=Action.GENERATE))
        store.store(make_trace("t3", agent_id="a2", action=Action.INVOKE))

        results = store.query(agent_id="a1", action=Action.INVOKE)
        assert len(results) == 1
        assert results[0].trace_id == "t1"

    def test_query_limit(self, store):
        """Query respects limit."""
        for i in range(10):
            store.store(make_trace(f"t{i}"))

        results = store.query(limit=5)
        assert len(results) == 5

    def test_query_offset(self, store):
        """Query respects offset."""
        for i in range(10):
            store.store(
                make_trace(f"t{i}", timestamp=datetime.utcnow() + timedelta(seconds=i))
            )

        results = store.query(offset=3, limit=3)
        assert len(results) == 3
        # Results are sorted by timestamp
        assert results[0].trace_id == "t3"

    def test_query_sorted_by_timestamp(self, store):
        """Query results sorted by timestamp."""
        now = datetime.utcnow()
        store.store(make_trace("t3", timestamp=now + timedelta(seconds=2)))
        store.store(make_trace("t1", timestamp=now))
        store.store(make_trace("t2", timestamp=now + timedelta(seconds=1)))

        results = store.query()
        assert [r.trace_id for r in results] == ["t1", "t2", "t3"]

    def test_get_children(self, store):
        """Get children returns traces with matching parent_id."""
        parent = make_trace("parent")
        child1 = make_trace("child1", parent_id="parent")
        child2 = make_trace("child2", parent_id="parent")
        other = make_trace("other", parent_id="other-parent")

        store.store(parent)
        store.store(child1)
        store.store(child2)
        store.store(other)

        children = store.get_children("parent")
        assert len(children) == 2
        assert set(c.trace_id for c in children) == {"child1", "child2"}

    def test_get_children_empty(self, store):
        """Get children returns empty for no children."""
        store.store(make_trace("lonely"))
        children = store.get_children("lonely")
        assert children == []

    def test_get_ancestors(self, store):
        """Get ancestors traverses parent chain."""
        store.store(make_trace("root"))
        store.store(make_trace("child", parent_id="root"))
        store.store(make_trace("grandchild", parent_id="child"))

        ancestors = store.get_ancestors("grandchild")
        assert len(ancestors) == 2
        assert ancestors[0].trace_id == "child"
        assert ancestors[1].trace_id == "root"

    def test_get_tree(self, store):
        """Get tree returns nested structure."""
        store.store(make_trace("root"))
        store.store(make_trace("child1", parent_id="root"))
        store.store(make_trace("child2", parent_id="root"))
        store.store(make_trace("grandchild", parent_id="child1"))

        tree = store.get_tree("root")
        assert tree["trace"].trace_id == "root"
        assert len(tree["children"]) == 2

        # Find child1 in children
        child1_tree = next(
            c for c in tree["children"] if c["trace"].trace_id == "child1"
        )
        assert len(child1_tree["children"]) == 1
        assert child1_tree["children"][0]["trace"].trace_id == "grandchild"

    def test_iter_all(self, store):
        """Iter all yields all crystals."""
        for i in range(5):
            store.store(make_trace(f"t{i}"))

        all_crystals = list(store.iter_all())
        assert len(all_crystals) == 5


class TestCrystalStats:
    """Tests for compute_stats function."""

    @pytest.fixture
    def store(self) -> MemoryCrystalStore:
        return MemoryCrystalStore()

    def test_stats_empty_store(self, store):
        """Stats for empty store."""
        stats = compute_stats(store)

        assert stats.total_crystals == 0
        assert stats.unique_agents == 0
        assert stats.unique_actions == 0
        assert stats.oldest_timestamp is None
        assert stats.newest_timestamp is None
        assert stats.total_gas == 0
        assert stats.error_count == 0

    def test_stats_with_crystals(self, store):
        """Stats computed from crystals."""
        now = datetime.utcnow()

        store.store(make_trace("t1", agent_id="a1", gas=100, timestamp=now))
        store.store(
            make_trace(
                "t2", agent_id="a2", gas=200, timestamp=now + timedelta(seconds=1)
            )
        )
        store.store(
            make_trace(
                "t3", agent_id="a1", gas=50, timestamp=now + timedelta(seconds=2)
            )
        )

        stats = compute_stats(store)

        assert stats.total_crystals == 3
        assert stats.unique_agents == 2
        assert stats.total_gas == 350
        assert stats.oldest_timestamp == now
        assert stats.newest_timestamp == now + timedelta(seconds=2)

    def test_stats_counts_errors(self, store):
        """Stats counts error traces."""
        store.store(make_trace("t1", action=Action.INVOKE))
        store.store(make_trace("t2", action=Action.ERROR))
        store.store(make_trace("t3", action=Action.ERROR))

        stats = compute_stats(store)
        assert stats.error_count == 2

    def test_stats_by_determinism(self, store):
        """Stats groups by determinism."""
        store.store(make_trace("t1", determinism=Determinism.DETERMINISTIC))
        store.store(make_trace("t2", determinism=Determinism.PROBABILISTIC))
        store.store(make_trace("t3", determinism=Determinism.PROBABILISTIC))

        stats = compute_stats(store)
        assert stats.by_determinism["deterministic"] == 1
        assert stats.by_determinism["probabilistic"] == 2

    def test_stats_by_genus(self, store):
        """Stats groups by agent genus."""
        store.store(make_trace("t1", agent_genus="B"))
        store.store(make_trace("t2", agent_genus="B"))
        store.store(make_trace("t3", agent_genus="G"))

        stats = compute_stats(store)
        assert stats.by_genus["B"] == 2
        assert stats.by_genus["G"] == 1
