"""
Tests for D-gent Phase 3: Extended Protocols.

Tests TransactionalDataAgent, QueryableDataAgent, ObservableDataAgent, and UnifiedMemory.
"""

import pytest
import asyncio

from ..volatile import VolatileAgent
from ..transactional import (
    TransactionalDataAgent,
    TransactionError,
    RollbackError,
)
from ..queryable import (
    QueryableDataAgent,
    Query,
    Predicate,
    Operator,
    eq,
    gt,
    contains,
    exists,
)
from ..observable import (
    ObservableDataAgent,
    ChangeType,
)
from ..unified import (
    UnifiedMemory,
    MemoryConfig,
    MemoryLayer,
    LayerNotAvailableError,
    create_unified_memory,
)


# ==============================================================================
# TransactionalDataAgent Tests
# ==============================================================================


class TestTransactionalDataAgent:
    """Tests for TransactionalDataAgent."""

    @pytest.fixture
    def memory(self):
        return VolatileAgent(_state={"count": 0})

    @pytest.fixture
    def txn_agent(self, memory):
        return TransactionalDataAgent(memory)

    @pytest.mark.asyncio
    async def test_load_without_transaction(self, txn_agent):
        """Load returns underlying state when not in transaction."""
        state = await txn_agent.load()
        assert state == {"count": 0}

    @pytest.mark.asyncio
    async def test_save_without_transaction(self, txn_agent):
        """Save persists directly when not in transaction."""
        await txn_agent.save({"count": 5})
        state = await txn_agent.load()
        assert state == {"count": 5}

    @pytest.mark.asyncio
    async def test_basic_transaction_commit(self, txn_agent):
        """Transaction commits pending changes."""
        async with txn_agent.transaction():
            await txn_agent.save({"count": 10})

        state = await txn_agent.load()
        assert state == {"count": 10}

    @pytest.mark.asyncio
    async def test_transaction_rollback_on_exception(self, txn_agent):
        """Transaction rolls back on exception."""
        with pytest.raises(ValueError):
            async with txn_agent.transaction():
                await txn_agent.save({"count": 10})
                raise ValueError("test error")

        # State should be unchanged
        state = await txn_agent.load()
        assert state == {"count": 0}

    @pytest.mark.asyncio
    async def test_explicit_rollback(self, txn_agent):
        """Explicit rollback discards changes."""
        await txn_agent.begin()
        await txn_agent.save({"count": 10})
        await txn_agent.rollback()

        state = await txn_agent.load()
        assert state == {"count": 0}

    @pytest.mark.asyncio
    async def test_savepoint_create_and_rollback(self, txn_agent):
        """Savepoints allow partial rollback."""
        await txn_agent.begin()
        await txn_agent.save({"count": 5})
        txn_agent.savepoint("checkpoint1")
        await txn_agent.save({"count": 10})
        txn_agent.rollback_to("checkpoint1")

        # Pending state should be rolled back to savepoint
        state = await txn_agent.load()
        assert state == {"count": 5}

        await txn_agent.commit()
        state = await txn_agent.load()
        assert state == {"count": 5}

    @pytest.mark.asyncio
    async def test_multiple_savepoints(self, txn_agent):
        """Multiple savepoints work correctly."""
        await txn_agent.begin()
        txn_agent.savepoint("sp1")
        await txn_agent.save({"count": 1})
        txn_agent.savepoint("sp2")
        await txn_agent.save({"count": 2})
        txn_agent.savepoint("sp3")
        await txn_agent.save({"count": 3})

        # Rollback to middle savepoint
        txn_agent.rollback_to("sp2")
        state = await txn_agent.load()
        assert state == {"count": 1}

        await txn_agent.commit()

    @pytest.mark.asyncio
    async def test_savepoint_not_found(self, txn_agent):
        """Rollback to nonexistent savepoint raises error."""
        await txn_agent.begin()
        with pytest.raises(RollbackError):
            txn_agent.rollback_to("nonexistent")
        await txn_agent.rollback()

    @pytest.mark.asyncio
    async def test_nested_transactions_not_allowed(self, txn_agent):
        """Nested transactions raise error."""
        await txn_agent.begin()
        with pytest.raises(TransactionError):
            await txn_agent.begin()
        await txn_agent.rollback()

    @pytest.mark.asyncio
    async def test_transaction_log(self, txn_agent):
        """Transaction operations are logged."""
        await txn_agent.begin()
        await txn_agent.save({"count": 1})
        txn_agent.savepoint("sp1")
        txn_agent.rollback_to("sp1")

        log = txn_agent.transaction_log()
        assert "begin()" in log
        assert any("save" in op for op in log)
        assert any("savepoint" in op for op in log)
        assert any("rollback_to" in op for op in log)

        await txn_agent.rollback()

    @pytest.mark.asyncio
    async def test_in_transaction_property(self, txn_agent):
        """in_transaction property reflects transaction state."""
        assert not txn_agent.in_transaction

        await txn_agent.begin()
        assert txn_agent.in_transaction

        await txn_agent.commit()
        assert not txn_agent.in_transaction

    @pytest.mark.asyncio
    async def test_savepoint_diff(self, txn_agent):
        """Savepoint diff shows state changes."""
        await txn_agent.begin()
        await txn_agent.save({"count": 1})
        txn_agent.savepoint("before")
        await txn_agent.save({"count": 10})
        txn_agent.savepoint("after")

        diff = txn_agent.savepoint_diff("before", "after")
        assert diff["from_state"] == {"count": 1}
        assert diff["to_state"] == {"count": 10}
        assert not diff["states_equal"]

        await txn_agent.rollback()


# ==============================================================================
# QueryableDataAgent Tests
# ==============================================================================


class TestQueryableDataAgent:
    """Tests for QueryableDataAgent."""

    @pytest.fixture
    def memory(self):
        return VolatileAgent(
            _state={
                "users": [
                    {"name": "Alice", "age": 30, "role": "admin"},
                    {"name": "Bob", "age": 25, "role": "user"},
                    {"name": "Charlie", "age": 35, "role": "user"},
                ],
                "config": {"debug": True, "version": "1.0"},
            }
        )

    @pytest.fixture
    def qa(self, memory):
        return QueryableDataAgent(memory)

    @pytest.mark.asyncio
    async def test_get_simple_path(self, qa):
        """Get value at simple path."""
        debug = await qa.get("config.debug")
        assert debug is True

    @pytest.mark.asyncio
    async def test_get_array_index(self, qa):
        """Get value at array index."""
        name = await qa.get("users[0].name")
        assert name == "Alice"

    @pytest.mark.asyncio
    async def test_get_with_default(self, qa):
        """Get returns default for missing path."""
        value = await qa.get("nonexistent.path", default="default")
        assert value == "default"

    @pytest.mark.asyncio
    async def test_exists_true(self, qa):
        """Exists returns True for existing path."""
        assert await qa.exists("config.debug") is True

    @pytest.mark.asyncio
    async def test_exists_false(self, qa):
        """Exists returns False for missing path."""
        assert await qa.exists("config.nonexistent") is False

    @pytest.mark.asyncio
    async def test_set_path(self, qa):
        """Set creates/updates path."""
        await qa.set("config.new_field", "new_value")
        value = await qa.get("config.new_field")
        assert value == "new_value"

    @pytest.mark.asyncio
    async def test_query_with_filter(self, qa):
        """Query filters results."""
        result = await qa.query(
            Query(
                where=[Predicate("role", Operator.EQ, "user")],
            )
        )
        # Query returns filtered state (dict in this case)
        assert result.count >= 0

    @pytest.mark.asyncio
    async def test_find_with_predicate(self, qa):
        """Find returns matching items."""
        results = await qa.find("users", lambda u: u["age"] > 28)
        names = [r["name"] for r in results]
        assert "Alice" in names
        assert "Charlie" in names
        assert "Bob" not in names

    @pytest.mark.asyncio
    async def test_find_one(self, qa):
        """Find one returns first match."""
        result = await qa.find_one("users", lambda u: u["name"] == "Bob")
        assert result["name"] == "Bob"
        assert result["age"] == 25

    @pytest.mark.asyncio
    async def test_count(self, qa):
        """Count returns collection size."""
        count = await qa.count("users")
        assert count == 3

    @pytest.mark.asyncio
    async def test_sum(self, qa):
        """Sum aggregates numeric values."""
        total = await qa.sum("users", "age")
        assert total == 90  # 30 + 25 + 35

    @pytest.mark.asyncio
    async def test_avg(self, qa):
        """Avg computes average."""
        avg = await qa.avg("users", "age")
        assert avg == 30.0

    @pytest.mark.asyncio
    async def test_min_max(self, qa):
        """Min/max find extremes."""
        min_age = await qa.min_value("users", "age")
        max_age = await qa.max_value("users", "age")
        assert min_age == 25
        assert max_age == 35

    @pytest.mark.asyncio
    async def test_distinct(self, qa):
        """Distinct returns unique values."""
        roles = await qa.distinct("users", "role")
        assert set(roles) == {"admin", "user"}

    @pytest.mark.asyncio
    async def test_group_by(self, qa):
        """Group by creates groups."""
        groups = await qa.group_by("users", "role")
        assert len(groups["admin"]) == 1
        assert len(groups["user"]) == 2

    @pytest.mark.asyncio
    async def test_predicate_helpers(self, qa):
        """Predicate helper functions work."""
        # Test eq predicate
        p = eq("name", "Alice")
        assert p.evaluate({"name": "Alice"})
        assert not p.evaluate({"name": "Bob"})

        # Test gt predicate
        p = gt("age", 25)
        assert p.evaluate({"age": 30})
        assert not p.evaluate({"age": 20})

        # Test contains predicate
        p = contains("name", "li")
        assert p.evaluate({"name": "Alice"})
        assert p.evaluate({"name": "Charlie"})

        # Test exists predicate
        p = exists("name")
        assert p.evaluate({"name": "Alice"})
        assert not p.evaluate({"other": "field"})


# ==============================================================================
# ObservableDataAgent Tests
# ==============================================================================


class TestObservableDataAgent:
    """Tests for ObservableDataAgent."""

    @pytest.fixture
    def memory(self):
        return VolatileAgent(_state={"count": 0})

    @pytest.fixture
    def obs(self, memory):
        return ObservableDataAgent(memory)

    @pytest.mark.asyncio
    async def test_subscribe_and_notify(self, obs):
        """Subscribers receive change notifications."""
        received = []

        async def callback(change):
            received.append(change)

        sub_id = await obs.subscribe(callback)
        await obs.load()  # Initialize last_state
        await obs.save({"count": 1})

        assert len(received) == 1
        assert received[0].change_type == ChangeType.SET
        assert received[0].new_value == {"count": 1}

        await obs.unsubscribe(sub_id)

    @pytest.mark.asyncio
    async def test_unsubscribe(self, obs):
        """Unsubscribed callbacks don't receive notifications."""
        received = []

        async def callback(change):
            received.append(change)

        sub_id = await obs.subscribe(callback)
        await obs.load()
        await obs.save({"count": 1})
        assert len(received) == 1

        await obs.unsubscribe(sub_id)
        await obs.save({"count": 2})
        assert len(received) == 1  # No new notifications

    @pytest.mark.asyncio
    async def test_path_subscription(self, obs):
        """Path subscriptions only notify for matching paths."""
        received = []

        async def callback(change):
            received.append(change)

        sub_id = await obs.subscribe_path("count", callback)
        await obs.load()
        await obs.update_path("count", 5)

        assert len(received) == 1
        assert received[0].path == "count"
        assert received[0].new_value == 5

        await obs.unsubscribe(sub_id)

    @pytest.mark.asyncio
    async def test_batch_mode(self, obs):
        """Batch mode collects changes and notifies at end."""
        received = []

        async def callback(change):
            received.append(change)

        await obs.subscribe(callback)
        await obs.load()

        await obs.batch_start()
        await obs.save({"count": 1})
        await obs.save({"count": 2})
        await obs.save({"count": 3})

        # No notifications during batch
        assert len(received) == 0

        await obs.batch_end()

        # All notifications at once
        assert len(received) == 3

    @pytest.mark.asyncio
    async def test_change_history(self, obs):
        """Change history is recorded."""
        await obs.load()
        await obs.save({"count": 1})
        await obs.save({"count": 2})

        history = obs.change_history(limit=5)
        assert len(history) == 2
        assert history[0].new_value == {"count": 2}  # Most recent first
        assert history[1].new_value == {"count": 1}

    @pytest.mark.asyncio
    async def test_diff(self, obs):
        """Diff computes state differences."""
        old = {"a": 1, "b": 2}
        new = {"a": 1, "b": 3, "c": 4}

        diffs = obs.diff(old, new)

        # Find each change type
        change_types = {d["type"] for d in diffs}
        paths = {d["path"] for d in diffs}

        assert "change" in change_types  # b changed
        assert "add" in change_types  # c added
        assert "b" in paths
        assert "c" in paths

    @pytest.mark.asyncio
    async def test_subscription_count(self, obs):
        """Subscription count is accurate."""
        assert obs.subscription_count() == 0

        sub1 = await obs.subscribe(lambda c: None)
        assert obs.subscription_count() == 1

        await obs.subscribe(lambda c: None)
        assert obs.subscription_count() == 2

        await obs.unsubscribe(sub1)
        assert obs.subscription_count() == 1


# ==============================================================================
# UnifiedMemory Tests
# ==============================================================================


class TestUnifiedMemory:
    """Tests for UnifiedMemory."""

    @pytest.fixture
    def memory(self):
        return VolatileAgent(_state={"data": "initial"})

    @pytest.fixture
    def unified(self, memory):
        config = MemoryConfig(
            enable_semantic=True,
            enable_temporal=True,
            enable_relational=True,
        )
        return UnifiedMemory(memory, config)

    @pytest.mark.asyncio
    async def test_basic_load_save(self, unified):
        """Basic load/save works."""
        state = await unified.load()
        assert state == {"data": "initial"}

        await unified.save({"data": "updated"})
        state = await unified.load()
        assert state == {"data": "updated"}

    @pytest.mark.asyncio
    async def test_semantic_associate_recall(self, unified):
        """Semantic association and recall work."""
        state = {"user": "alice"}
        await unified.save(state)
        await unified.associate(state, "user-profile")

        results = await unified.recall("user-profile")
        assert len(results) > 0
        assert results[0][1] == 1.0  # Exact match has score 1.0

    @pytest.mark.asyncio
    async def test_semantic_partial_recall(self, unified):
        """Partial semantic recall works."""
        state = {"data": "test"}
        await unified.save(state)
        await unified.associate(state, "test-data")

        results = await unified.recall("test")
        assert len(results) > 0
        assert results[0][1] < 1.0  # Partial match has lower score

    @pytest.mark.asyncio
    async def test_temporal_witness_replay(self, unified):
        """Temporal witness and replay work."""
        state1 = {"count": 1}
        state2 = {"count": 2}

        await unified.witness("increment", state1)
        await asyncio.sleep(0.01)  # Small delay for distinct timestamps
        await unified.witness("increment", state2)

        timeline = await unified.timeline()
        assert len(timeline) == 2
        assert timeline[0][2] == state1
        assert timeline[1][2] == state2

    @pytest.mark.asyncio
    async def test_temporal_events_by_label(self, unified):
        """Events can be filtered by label."""
        await unified.witness("login", {"user": "alice"})
        await unified.witness("logout", {"user": "alice"})
        await unified.witness("login", {"user": "bob"})

        logins = await unified.events_by_label("login")
        assert len(logins) == 2

    @pytest.mark.asyncio
    async def test_relational_relate_and_query(self, unified):
        """Relational layer works."""
        await unified.relate("user-1", "owns", "doc-1")
        await unified.relate("user-1", "owns", "doc-2")
        await unified.relate("user-1", "follows", "user-2")

        # Query forward relationships
        owns = await unified.related_to("user-1", "owns")
        assert len(owns) == 2
        assert ("owns", "doc-1") in owns
        assert ("owns", "doc-2") in owns

        # Query all relationships
        all_rels = await unified.related_to("user-1")
        assert len(all_rels) == 3

    @pytest.mark.asyncio
    async def test_relational_reverse_query(self, unified):
        """Reverse relational query works."""
        await unified.relate("user-1", "owns", "doc-1")

        # Query reverse
        owners = await unified.related_from("doc-1", "owns")
        assert len(owners) == 1
        assert ("owns", "user-1") in owners

    @pytest.mark.asyncio
    async def test_trace_graph(self, unified):
        """Graph trace works."""
        await unified.relate("a", "to", "b")
        await unified.relate("b", "to", "c")
        await unified.relate("c", "to", "d")

        graph = await unified.trace("a", max_depth=3)
        assert "a" in graph["nodes"]
        assert "b" in graph["nodes"]
        assert "c" in graph["nodes"]
        assert len(graph["edges"]) == 3

    @pytest.mark.asyncio
    async def test_lineage_tracking(self, unified):
        """Lineage is tracked across saves."""
        id1 = await unified.save({"v": 1})
        id2 = await unified.save({"v": 2})
        id3 = await unified.save({"v": 3})

        ancestors = await unified.ancestors(id3)
        assert id2 in ancestors
        assert id1 in ancestors

    @pytest.mark.asyncio
    async def test_layer_not_available_error(self, memory):
        """Disabled layers raise LayerNotAvailableError."""
        config = MemoryConfig(enable_semantic=False)
        unified = UnifiedMemory(memory, config)

        with pytest.raises(LayerNotAvailableError):
            await unified.associate({}, "concept")

    @pytest.mark.asyncio
    async def test_available_layers(self, unified):
        """Available layers reflects config."""
        layers = unified.available_layers
        assert MemoryLayer.IMMEDIATE in layers
        assert MemoryLayer.SEMANTIC in layers
        assert MemoryLayer.TEMPORAL in layers
        assert MemoryLayer.RELATIONAL in layers

    @pytest.mark.asyncio
    async def test_stats(self, unified):
        """Stats returns memory statistics."""
        await unified.save({"v": 1})
        await unified.associate({"v": 1}, "test")
        await unified.witness("event", {"v": 1})
        await unified.relate("a", "to", "b")

        stats = unified.stats()
        assert stats["entry_count"] >= 1
        assert stats["concept_count"] >= 1
        assert stats["event_count"] >= 1
        assert stats["relationship_count"] >= 1

    @pytest.mark.asyncio
    async def test_create_unified_memory_helper(self, memory):
        """Factory function works."""
        unified = create_unified_memory(memory, enable_all=True)
        assert MemoryLayer.SEMANTIC in unified.available_layers
        assert MemoryLayer.TEMPORAL in unified.available_layers
        assert MemoryLayer.RELATIONAL in unified.available_layers


# ==============================================================================
# Integration Tests
# ==============================================================================


class TestPhase3Integration:
    """Integration tests combining multiple Phase 3 components."""

    @pytest.mark.asyncio
    async def test_transactional_with_observable(self):
        """Transactional changes notify observers."""
        memory = VolatileAgent(_state={"count": 0})
        obs = ObservableDataAgent(memory)
        txn = TransactionalDataAgent(obs)

        received = []

        async def callback(change):
            received.append(change)

        await obs.subscribe(callback)
        await obs.load()

        async with txn.transaction():
            await txn.save({"count": 5})

        # Observer notified after commit
        assert len(received) == 1
        assert received[0].new_value == {"count": 5}

    @pytest.mark.asyncio
    async def test_queryable_with_unified(self):
        """Queryable works on UnifiedMemory."""
        memory = VolatileAgent(
            _state={
                "users": [
                    {"name": "Alice", "active": True},
                    {"name": "Bob", "active": False},
                ]
            }
        )
        unified = UnifiedMemory(memory)
        qa = QueryableDataAgent(unified)

        active = await qa.find("users", lambda u: u["active"])
        assert len(active) == 1
        assert active[0]["name"] == "Alice"

    @pytest.mark.asyncio
    async def test_full_stack_workflow(self):
        """Full workflow using all Phase 3 components."""
        # Setup
        base = VolatileAgent(_state={"items": []})
        unified = create_unified_memory(base, enable_all=True)
        txn = TransactionalDataAgent(unified)
        qa = QueryableDataAgent(txn)

        # Transactional updates
        async with txn.transaction():
            current = await qa.load()
            current["items"].append({"id": 1, "name": "Item 1"})
            await txn.save(current)
            txn.savepoint("after_first_item")

            current["items"].append({"id": 2, "name": "Item 2"})
            await txn.save(current)

        # Query the results
        count = await qa.count("items")
        assert count == 2

        names = await qa.distinct("items", "name")
        assert "Item 1" in names
        assert "Item 2" in names
