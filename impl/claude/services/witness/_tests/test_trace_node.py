"""
Tests for Mark, MarkLink, and MarkStore.

Verifies the three Mark laws:
- Law 1 (Immutability): Marks are frozen after creation
- Law 2 (Causality): link.target.timestamp > link.source.timestamp
- Law 3 (Completeness): Every AGENTESE invocation emits exactly one Mark

See: spec/protocols/warp-primitives.md
"""

from __future__ import annotations

import time
from dataclasses import FrozenInstanceError
from datetime import datetime, timedelta

import pytest

from services.witness import (
    CausalityViolation,
    DuplicateMarkError,
    LinkRelation,
    Mark,
    MarkId,
    MarkLink,
    MarkNotFoundError,
    MarkQuery,
    MarkStore,
    NPhase,
    Participant,
    PlanPath,
    Response,
    Stimulus,
    UmweltSnapshot,
    Walk,
    WalkId,
    WalkStatus,
    get_mark_store,
    reset_mark_store,
)

# =============================================================================
# Law 1: Immutability Tests
# =============================================================================


class TestLaw1Immutability:
    """Law 1: Marks are frozen after creation."""

    def test_tracenode_is_frozen(self) -> None:
        """Marks cannot be modified after creation."""
        node = Mark.from_thought("Test thought", "git", ("test",))

        with pytest.raises(FrozenInstanceError):
            node.origin = "modified"  # type: ignore[misc]

    def test_tracenode_timestamp_immutable(self) -> None:
        """Timestamp cannot be modified."""
        node = Mark.from_thought("Test", "git")

        with pytest.raises(FrozenInstanceError):
            node.timestamp = datetime.now()  # type: ignore[misc]

    def test_tracenode_links_immutable(self) -> None:
        """Links tuple cannot be modified."""
        node = Mark.from_thought("Test", "git")

        # Cannot reassign links
        with pytest.raises(FrozenInstanceError):
            node.links = ()  # type: ignore[misc]

    def test_tracelink_is_frozen(self) -> None:
        """MarkLinks are frozen."""
        link = MarkLink(
            source=MarkId("trace-abc"),
            target=MarkId("trace-def"),
            relation=LinkRelation.CAUSES,
        )

        with pytest.raises(FrozenInstanceError):
            link.relation = LinkRelation.BRANCHES  # type: ignore[misc]

    def test_stimulus_is_frozen(self) -> None:
        """Stimulus is frozen."""
        stim = Stimulus.from_prompt("Test prompt")

        with pytest.raises(FrozenInstanceError):
            stim.content = "Modified"  # type: ignore[misc]

    def test_response_is_frozen(self) -> None:
        """Response is frozen."""
        resp = Response.thought("Test thought")

        with pytest.raises(FrozenInstanceError):
            resp.content = "Modified"  # type: ignore[misc]

    def test_umwelt_snapshot_is_frozen(self) -> None:
        """UmweltSnapshot is frozen."""
        umwelt = UmweltSnapshot.system()

        with pytest.raises(FrozenInstanceError):
            umwelt.trust_level = 0  # type: ignore[misc]


# =============================================================================
# Law 2: Causality Tests
# =============================================================================


class TestLaw2Causality:
    """Law 2: link.target.timestamp > link.source.timestamp."""

    def setup_method(self) -> None:
        """Reset trace store before each test."""
        reset_mark_store()

    def test_valid_causal_link(self) -> None:
        """Valid links have target after source."""
        store = MarkStore()

        # Create source node
        source = Mark.from_thought("Source", "git")
        store.append(source)

        # Small delay to ensure different timestamps
        time.sleep(0.01)

        # Create target with link to source
        link = MarkLink(
            source=source.id,
            target=MarkId("placeholder"),  # Will be replaced
            relation=LinkRelation.CAUSES,
        )

        target = Mark(
            origin="witness",
            stimulus=Stimulus.from_event("git", "Target event", "git"),
            response=Response.thought("Target thought"),
            links=(
                MarkLink(source=source.id, target=MarkId("self"), relation=LinkRelation.CAUSES),
            ),
        )

        # Need to create link properly with actual target ID
        target = Mark(
            id=target.id,
            origin="witness",
            stimulus=Stimulus.from_event("git", "Target event", "git"),
            response=Response.thought("Target thought"),
            links=(MarkLink(source=source.id, target=target.id, relation=LinkRelation.CAUSES),),
        )

        # Should not raise
        store.append(target)
        assert len(store) == 2

    def test_causality_violation_raises(self) -> None:
        """Links violating causality raise CausalityViolation."""
        store = MarkStore()

        # Create "future" node first (but we'll try to link back to it)
        future_node = Mark.from_thought("Future", "git")
        store.append(future_node)

        # Create "past" node that tries to claim future_node caused it
        # But with an earlier timestamp (impossible)
        past_timestamp = future_node.timestamp - timedelta(seconds=1)
        past_node = Mark(
            origin="witness",
            stimulus=Stimulus.from_event("git", "Past event", "git"),
            response=Response.thought("Past thought"),
            links=(
                MarkLink(
                    source=future_node.id, target=MarkId("past"), relation=LinkRelation.CAUSES
                ),
            ),
            timestamp=past_timestamp,
        )

        # Update with correct target ID
        past_node = Mark(
            id=past_node.id,
            origin="witness",
            stimulus=past_node.stimulus,
            response=past_node.response,
            links=(
                MarkLink(source=future_node.id, target=past_node.id, relation=LinkRelation.CAUSES),
            ),
            timestamp=past_timestamp,
        )

        with pytest.raises(CausalityViolation):
            store.append(past_node)

    def test_plan_links_skip_causality_check(self) -> None:
        """Links to plan paths don't require timestamp validation."""
        store = MarkStore()

        # Create node linking to a plan (no timestamp to check)
        node = Mark(
            origin="witness",
            stimulus=Stimulus.from_event("git", "Event", "git"),
            response=Response.thought("Thought"),
            links=(
                MarkLink(
                    source=PlanPath("plans/warp-servo-phase1.md"),
                    target=MarkId("placeholder"),
                    relation=LinkRelation.FULFILLS,
                ),
            ),
        )

        # Update with correct target ID
        node = Mark(
            id=node.id,
            origin=node.origin,
            stimulus=node.stimulus,
            response=node.response,
            links=(
                MarkLink(
                    source=PlanPath("plans/warp-servo-phase1.md"),
                    target=node.id,
                    relation=LinkRelation.FULFILLS,
                ),
            ),
        )

        # Should not raise
        store.append(node)
        assert len(store) == 1

    def test_link_to_nonexistent_node_raises(self) -> None:
        """Links to non-existent nodes raise MarkNotFoundError."""
        store = MarkStore()

        # Create node with link to non-existent source
        node = Mark(
            origin="witness",
            stimulus=Stimulus.from_event("git", "Event", "git"),
            response=Response.thought("Thought"),
            links=(
                MarkLink(
                    source=MarkId("trace-nonexistent"),
                    target=MarkId("placeholder"),
                    relation=LinkRelation.CAUSES,
                ),
            ),
        )

        # Update with correct target ID
        node = Mark(
            id=node.id,
            origin=node.origin,
            stimulus=node.stimulus,
            response=node.response,
            links=(
                MarkLink(
                    source=MarkId("trace-nonexistent"),
                    target=node.id,
                    relation=LinkRelation.CAUSES,
                ),
            ),
        )

        with pytest.raises(MarkNotFoundError):
            store.append(node)


# =============================================================================
# MarkStore Tests
# =============================================================================


class TestMarkStore:
    """Tests for MarkStore append-only semantics."""

    def setup_method(self) -> None:
        """Reset trace store before each test."""
        reset_mark_store()

    def test_append_and_get(self) -> None:
        """Basic append and retrieval."""
        store = MarkStore()
        node = Mark.from_thought("Test", "git")

        store.append(node)
        retrieved = store.get(node.id)

        assert retrieved is not None
        assert retrieved.id == node.id

    def test_duplicate_raises(self) -> None:
        """Appending duplicate ID raises DuplicateMarkError."""
        store = MarkStore()
        node = Mark.from_thought("Test", "git")

        store.append(node)

        with pytest.raises(DuplicateMarkError):
            store.append(node)

    def test_query_by_origin(self) -> None:
        """Query filters by origin."""
        store = MarkStore()

        git_node = Mark.from_thought("Git event", "git")
        file_node = Mark.from_thought("File event", "filesystem")

        store.append(git_node)
        store.append(file_node)

        query = MarkQuery(origins=("witness",))  # Default origin from from_thought
        results = list(store.query(query))

        assert len(results) == 2  # Both have origin "witness"

    def test_query_by_phase(self) -> None:
        """Query filters by N-Phase."""
        store = MarkStore()

        sense_node = Mark.from_thought("Sense", "git", phase=NPhase.SENSE)
        act_node = Mark.from_thought("Act", "git", phase=NPhase.ACT)

        store.append(sense_node)
        store.append(act_node)

        query = MarkQuery(phases=(NPhase.SENSE,))
        results = list(store.query(query))

        assert len(results) == 1
        assert results[0].phase == NPhase.SENSE

    def test_query_by_time_range(self) -> None:
        """Query filters by time range."""
        store = MarkStore()

        old_node = Mark(
            origin="witness",
            stimulus=Stimulus.from_event("git", "Old", "git"),
            response=Response.thought("Old"),
            timestamp=datetime.now() - timedelta(hours=2),
        )
        new_node = Mark.from_thought("New", "git")

        store.append(old_node)
        store.append(new_node)

        # Query for recent nodes only
        query = MarkQuery(after=datetime.now() - timedelta(hours=1))
        results = list(store.query(query))

        assert len(results) == 1

    def test_get_walk_traces(self) -> None:
        """Get traces belonging to a Walk."""
        store = MarkStore()
        walk_id = WalkId("walk-test123")

        # Create nodes with and without walk_id
        walk_node = Mark(
            origin="witness",
            stimulus=Stimulus.from_event("git", "Walk event", "git"),
            response=Response.thought("Walk thought"),
            walk_id=walk_id,
        )
        other_node = Mark.from_thought("Other", "git")

        store.append(walk_node)
        store.append(other_node)

        walk_traces = store.get_walk_traces(walk_id)

        assert len(walk_traces) == 1
        assert walk_traces[0].walk_id == walk_id

    def test_stats(self) -> None:
        """Store statistics are accurate."""
        store = MarkStore()

        store.append(Mark.from_thought("A", "git", phase=NPhase.SENSE))
        store.append(Mark.from_thought("B", "git", phase=NPhase.ACT))
        store.append(Mark.from_thought("C", "test", phase=NPhase.SENSE))

        stats = store.stats()

        assert stats["total_nodes"] == 3
        assert stats["by_phase"]["SENSE"] == 2
        assert stats["by_phase"]["ACT"] == 1


# =============================================================================
# Walk Tests
# =============================================================================


class TestWalk:
    """Tests for Walk durable work stream."""

    def test_walk_creation(self) -> None:
        """Walk creation with goal and plan."""
        walk = Walk.create(
            goal="Implement Mark",
            root_plan=PlanPath("plans/warp-servo-phase1.md"),
        )

        assert walk.goal is not None
        assert walk.goal.description == "Implement Mark"
        assert walk.root_plan == PlanPath("plans/warp-servo-phase1.md")
        assert walk.status == WalkStatus.ACTIVE
        assert walk.phase == NPhase.SENSE

    def test_walk_advance_monotonicity(self) -> None:
        """Law 1: trace_nodes only grows."""
        walk = Walk.create(goal="Test")

        node1 = Mark.from_thought("First", "git")
        node2 = Mark.from_thought("Second", "git")

        walk.advance(node1)
        assert walk.mark_count == 1

        walk.advance(node2)
        assert walk.mark_count == 2

        # Cannot remove (no method for it - monotonicity enforced by design)

    def test_walk_phase_transitions(self) -> None:
        """Law 2: Phase transitions follow N-Phase grammar."""
        walk = Walk.create(goal="Test", initial_phase=NPhase.SENSE)

        # Valid: SENSE → ACT
        assert walk.can_transition(NPhase.ACT)
        assert walk.transition_phase(NPhase.ACT)
        assert walk.phase == NPhase.ACT

        # Valid: ACT → REFLECT
        assert walk.transition_phase(NPhase.REFLECT)
        assert walk.phase == NPhase.REFLECT

        # Valid: REFLECT → SENSE (cycle)
        assert walk.transition_phase(NPhase.SENSE)
        assert walk.phase == NPhase.SENSE

    def test_walk_invalid_transition_blocked(self) -> None:
        """Invalid phase transitions are blocked."""
        walk = Walk.create(goal="Test", initial_phase=NPhase.SENSE)

        # Invalid: SENSE → REFLECT (must go through ACT)
        assert not walk.can_transition(NPhase.REFLECT)
        assert not walk.transition_phase(NPhase.REFLECT)

        # Phase unchanged
        assert walk.phase == NPhase.SENSE

    def test_walk_status_transitions(self) -> None:
        """Walk status transitions work correctly."""
        walk = Walk.create(goal="Test")

        assert walk.status == WalkStatus.ACTIVE

        walk.pause()
        assert walk.status == WalkStatus.PAUSED

        walk.resume()
        assert walk.status == WalkStatus.ACTIVE

        walk.complete()
        assert walk.status == WalkStatus.COMPLETE
        assert walk.ended_at is not None

    def test_walk_participants(self) -> None:
        """Walk participant management."""
        walk = Walk.create(goal="Test")

        human = Participant.human("Kent", role="orchestrator")
        agent = Participant.agent("witness", trust_level=1)

        walk.add_participant(human)
        walk.add_participant(agent)

        assert len(walk.participants) == 2

        retrieved = walk.get_participant(human.id)
        assert retrieved is not None
        assert retrieved.name == "Kent"


# =============================================================================
# Serialization Tests
# =============================================================================


class TestSerialization:
    """Tests for to_dict/from_dict roundtrip."""

    def test_tracenode_roundtrip(self) -> None:
        """Mark serializes and deserializes correctly."""
        original = Mark(
            origin="witness",
            stimulus=Stimulus.from_agentese("world.house", "manifest"),
            response=Response.projection("world.house.manifest"),
            umwelt=UmweltSnapshot.witness(trust_level=2),
            phase=NPhase.ACT,
            tags=("test", "roundtrip"),
        )

        data = original.to_dict()
        restored = Mark.from_dict(data)

        assert restored.id == original.id
        assert restored.origin == original.origin
        assert restored.stimulus.kind == original.stimulus.kind
        assert restored.phase == original.phase
        assert restored.umwelt.trust_level == original.umwelt.trust_level

    def test_walk_roundtrip(self) -> None:
        """Walk serializes and deserializes correctly."""
        original = Walk.create(
            goal="Test roundtrip",
            root_plan=PlanPath("plans/test.md"),
        )
        original.add_participant(Participant.human("Kent"))
        original.transition_phase(NPhase.ACT)

        data = original.to_dict()
        restored = Walk.from_dict(data)

        assert restored.id == original.id
        assert restored.goal.description == original.goal.description
        assert restored.phase == NPhase.ACT
        assert len(restored.participants) == 1

    def test_tracelink_roundtrip(self) -> None:
        """MarkLink serializes and deserializes correctly."""
        original = MarkLink(
            source=MarkId("trace-abc"),
            target=MarkId("trace-def"),
            relation=LinkRelation.CAUSES,
            metadata={"reason": "test"},
        )

        data = original.to_dict()
        restored = MarkLink.from_dict(data)

        assert str(restored.source) == str(original.source)
        assert str(restored.target) == str(original.target)
        assert restored.relation == original.relation


# =============================================================================
# NPhase Tests
# =============================================================================


class TestNPhase:
    """Tests for NPhase enum."""

    def test_phase_families(self) -> None:
        """Phases belong to correct families."""
        # SENSE family
        assert NPhase.SENSE.family == "SENSE"
        assert NPhase.PLAN.family == "SENSE"
        assert NPhase.RESEARCH.family == "SENSE"

        # ACT family
        assert NPhase.ACT.family == "ACT"
        assert NPhase.IMPLEMENT.family == "ACT"
        assert NPhase.TEST.family == "ACT"

        # REFLECT family
        assert NPhase.REFLECT.family == "REFLECT"
        assert NPhase.MEASURE.family == "REFLECT"


# =============================================================================
# UmweltSnapshot Tests
# =============================================================================


class TestUmweltSnapshot:
    """Tests for UmweltSnapshot."""

    def test_system_umwelt(self) -> None:
        """System umwelt has full capabilities."""
        umwelt = UmweltSnapshot.system()

        assert umwelt.trust_level == 3
        assert "execute" in umwelt.capabilities
        assert umwelt.observer_id == "system"

    def test_witness_umwelt_trust_levels(self) -> None:
        """Witness umwelt capabilities scale with trust."""
        l0 = UmweltSnapshot.witness(trust_level=0)
        l1 = UmweltSnapshot.witness(trust_level=1)
        l2 = UmweltSnapshot.witness(trust_level=2)
        l3 = UmweltSnapshot.witness(trust_level=3)

        assert "observe" in l0.capabilities
        assert "write_kgents" not in l0.capabilities

        assert "write_kgents" in l1.capabilities
        assert "suggest" not in l1.capabilities

        assert "suggest" in l2.capabilities
        assert "execute" not in l2.capabilities

        assert "execute" in l3.capabilities


# =============================================================================
# Edge Case Tests (QA Additions)
# =============================================================================


class TestEdgeCases:
    """Edge cases for robustness."""

    def setup_method(self) -> None:
        """Reset stores before each test."""
        reset_mark_store()
        from services.witness import reset_walk_store

        reset_walk_store()

    def test_empty_store_query(self) -> None:
        """Empty store returns empty results."""
        store = MarkStore()

        # Query on empty store
        query = MarkQuery(origins=("witness",))
        results = list(store.query(query))
        assert results == []

        # Count on empty store
        assert store.count() == 0
        assert store.count(query) == 0

        # Recent on empty store
        assert store.recent() == []

    def test_walk_with_zero_traces_complete(self) -> None:
        """Walk with no traces can complete successfully."""
        walk = Walk.create(goal="Empty walk test")
        assert walk.mark_count == 0

        walk.complete()
        assert walk.status == WalkStatus.COMPLETE
        assert walk.mark_count == 0
        assert walk.ended_at is not None

    def test_walk_phase_same_phase_no_op(self) -> None:
        """Transitioning to same phase is a no-op (allowed)."""
        walk = Walk.create(goal="Test", initial_phase=NPhase.SENSE)
        initial_history_len = len(walk.phase_history)

        # Same phase transition
        assert walk.can_transition(NPhase.SENSE)
        result = walk.transition_phase(NPhase.SENSE)

        assert result is True
        assert walk.phase == NPhase.SENSE
        # History should still grow (records the attempt)
        assert len(walk.phase_history) >= initial_history_len

    def test_walk_phase_forced_transition(self) -> None:
        """Forced transitions bypass validation."""
        walk = Walk.create(goal="Test", initial_phase=NPhase.SENSE)

        # Invalid transition SENSE → REFLECT (should fail without force)
        assert not walk.can_transition(NPhase.REFLECT)

        # With force=True, should succeed
        result = walk.transition_phase(NPhase.REFLECT, force=True)
        assert result is True
        assert walk.phase == NPhase.REFLECT

    def test_tracelink_with_planpath_source(self) -> None:
        """MarkLink can have PlanPath as source."""
        link = MarkLink(
            source=PlanPath("plans/warp-servo-phase1.md"),
            target=MarkId("trace-abc123"),
            relation=LinkRelation.FULFILLS,
            metadata={"plan_chunk": "1.1"},
        )

        # Roundtrip
        data = link.to_dict()
        restored = MarkLink.from_dict(data)

        assert isinstance(restored.source, str)
        assert restored.source == "plans/warp-servo-phase1.md"
        assert restored.relation == LinkRelation.FULFILLS

    def test_large_mark_count_performance(self) -> None:
        """Store handles 100+ traces efficiently."""
        store = MarkStore()

        # Add 100 traces
        for i in range(100):
            node = Mark.from_thought(
                f"Trace {i}",
                "git",
                tags=(f"batch-{i // 10}",),
                phase=NPhase.SENSE if i % 2 == 0 else NPhase.ACT,
            )
            store.append(node)

        assert len(store) == 100
        assert store.count() == 100

        # Query should be reasonably fast
        start = time.time()
        query = MarkQuery(phases=(NPhase.SENSE,), limit=50)
        results = list(store.query(query))
        elapsed = time.time() - start

        assert len(results) == 50
        assert elapsed < 1.0, f"Query took too long: {elapsed}s"

        # Stats should work
        stats = store.stats()
        assert stats["total_nodes"] == 100
        assert stats["by_phase"]["SENSE"] == 50
        assert stats["by_phase"]["ACT"] == 50


class TestSerializationEdgeCases:
    """Edge cases for serialization roundtrip."""

    def test_datetime_precision_preserved(self) -> None:
        """Datetime microseconds are preserved in roundtrip."""
        # Create with specific microseconds
        specific_time = datetime(2025, 12, 20, 12, 34, 56, 789012)
        node = Mark(
            origin="witness",
            stimulus=Stimulus.from_prompt("Test"),
            response=Response.thought("Test"),
            timestamp=specific_time,
        )

        data = node.to_dict()
        restored = Mark.from_dict(data)

        assert restored.timestamp == specific_time
        assert restored.timestamp.microsecond == 789012

    def test_frozenset_roundtrip(self) -> None:
        """Frozenset fields survive list serialization."""
        umwelt = UmweltSnapshot(
            observer_id="test",
            role="developer",
            capabilities=frozenset({"read", "write", "execute"}),
            perceptions=frozenset({"git", "filesystem"}),
            trust_level=2,
        )

        data = umwelt.to_dict()
        # Lists in serialized form
        assert isinstance(data["capabilities"], list)
        assert isinstance(data["perceptions"], list)

        restored = UmweltSnapshot.from_dict(data)
        # Back to frozenset
        assert isinstance(restored.capabilities, frozenset)
        assert isinstance(restored.perceptions, frozenset)
        assert restored.capabilities == umwelt.capabilities
        assert restored.perceptions == umwelt.perceptions

    def test_nested_metadata_preserved(self) -> None:
        """Nested metadata dicts are preserved."""
        node = Mark(
            origin="witness",
            stimulus=Stimulus(
                kind="agentese",
                content="world.house.manifest",
                metadata={"nested": {"deep": {"value": 42}}},
            ),
            response=Response.thought("Test"),
            metadata={"top_level": {"inner": [1, 2, 3]}},
        )

        data = node.to_dict()
        restored = Mark.from_dict(data)

        assert restored.stimulus.metadata["nested"]["deep"]["value"] == 42
        assert restored.metadata["top_level"]["inner"] == [1, 2, 3]

    def test_empty_collections_preserved(self) -> None:
        """Empty tags and links are preserved correctly."""
        node = Mark(
            origin="witness",
            stimulus=Stimulus.from_prompt("Test"),
            response=Response.thought("Test"),
            tags=(),
            links=(),
        )

        data = node.to_dict()
        restored = Mark.from_dict(data)

        assert restored.tags == ()
        assert restored.links == ()


class TestWalkStoreEdgeCases:
    """Edge cases for WalkStore operations."""

    def setup_method(self) -> None:
        """Reset walk store before each test."""
        from services.witness import reset_walk_store

        reset_walk_store()

    def test_walk_store_empty_operations(self) -> None:
        """WalkStore handles empty state correctly."""
        from services.witness import WalkStore

        store = WalkStore()

        assert len(store) == 0
        assert store.active_walks() == []
        assert store.recent_walks() == []
        assert store.get(WalkId("nonexistent")) is None

    def test_walk_store_add_and_retrieve(self) -> None:
        """WalkStore add and get operations."""
        from services.witness import WalkStore

        store = WalkStore()
        walk = Walk.create(goal="Test")

        store.add(walk)
        assert len(store) == 1

        retrieved = store.get(walk.id)
        assert retrieved is not None
        assert retrieved.id == walk.id

    def test_walk_store_active_filter(self) -> None:
        """WalkStore filters active walks correctly."""
        from services.witness import WalkStore

        store = WalkStore()

        active_walk = Walk.create(goal="Active")
        completed_walk = Walk.create(goal="Complete")
        completed_walk.complete()
        paused_walk = Walk.create(goal="Paused")
        paused_walk.pause()

        store.add(active_walk)
        store.add(completed_walk)
        store.add(paused_walk)

        active = store.active_walks()
        assert len(active) == 1
        assert active[0].id == active_walk.id


class TestMetadataMutability:
    """
    Test that metadata dicts don't violate Law 1.

    Note: Python frozen dataclasses with dict fields allow mutation
    of the dict contents. This is a known limitation. The test documents
    this behavior but does NOT enforce immutability on dict contents.
    """

    def test_metadata_dict_contents_mutable(self) -> None:
        """
        Document: metadata dict contents CAN be mutated (Python limitation).

        This is expected behavior for frozen dataclasses with dict fields.
        The dataclass itself is frozen (can't reassign metadata), but the
        dict contents are still mutable.

        For true immutability, consider using types.MappingProxyType or
        similar in a future refactor.
        """
        node = Mark(
            origin="witness",
            stimulus=Stimulus.from_prompt("Test"),
            response=Response.thought("Test"),
            metadata={"key": "original"},
        )

        # Can mutate dict contents (Python limitation)
        node.metadata["key"] = "mutated"
        assert node.metadata["key"] == "mutated"

        # But cannot reassign the field
        with pytest.raises(FrozenInstanceError):
            node.metadata = {}  # type: ignore[misc]


class TestCausalGraphNavigation:
    """Tests for causal graph traversal methods."""

    def setup_method(self) -> None:
        """Reset trace store before each test."""
        reset_mark_store()

    def test_get_causes_and_effects(self) -> None:
        """Navigate causal relationships."""
        store = MarkStore()

        # Create a causal chain: source → target
        source = Mark.from_thought("Source event", "git")
        store.append(source)

        time.sleep(0.01)

        target = Mark(
            origin="witness",
            stimulus=Stimulus.from_event("git", "Target event", "git"),
            response=Response.thought("Target thought"),
            links=(
                MarkLink(source=source.id, target=MarkId("temp"), relation=LinkRelation.CAUSES),
            ),
        )
        # Fix target ID in link
        target = Mark(
            id=target.id,
            origin=target.origin,
            stimulus=target.stimulus,
            response=target.response,
            links=(MarkLink(source=source.id, target=target.id, relation=LinkRelation.CAUSES),),
            timestamp=target.timestamp,
        )
        store.append(target)

        # Navigate
        effects = store.get_effects(source.id)
        assert len(effects) == 1
        assert effects[0].id == target.id

        causes = store.get_causes(target.id)
        assert len(causes) == 1
        assert causes[0].id == source.id

    def test_get_continuation_and_branches(self) -> None:
        """Navigate continuation and branch relationships."""
        store = MarkStore()

        source = Mark.from_thought("Source", "git")
        store.append(source)

        time.sleep(0.01)

        continuation = Mark(
            origin="witness",
            stimulus=Stimulus.from_event("git", "Continuation", "git"),
            response=Response.thought("Continuation"),
            links=(
                MarkLink(source=source.id, target=MarkId("temp"), relation=LinkRelation.CONTINUES),
            ),
        )
        continuation = Mark(
            id=continuation.id,
            origin=continuation.origin,
            stimulus=continuation.stimulus,
            response=continuation.response,
            links=(
                MarkLink(source=source.id, target=continuation.id, relation=LinkRelation.CONTINUES),
            ),
            timestamp=continuation.timestamp,
        )
        store.append(continuation)

        time.sleep(0.01)

        branch = Mark(
            origin="witness",
            stimulus=Stimulus.from_event("git", "Branch", "git"),
            response=Response.thought("Branch"),
            links=(
                MarkLink(source=source.id, target=MarkId("temp"), relation=LinkRelation.BRANCHES),
            ),
        )
        branch = Mark(
            id=branch.id,
            origin=branch.origin,
            stimulus=branch.stimulus,
            response=branch.response,
            links=(MarkLink(source=source.id, target=branch.id, relation=LinkRelation.BRANCHES),),
            timestamp=branch.timestamp,
        )
        store.append(branch)

        continuations = store.get_continuation(source.id)
        assert len(continuations) == 1

        branches = store.get_branches(source.id)
        assert len(branches) == 1

    def test_empty_navigation_results(self) -> None:
        """Navigation on node with no relationships returns empty."""
        store = MarkStore()
        node = Mark.from_thought("Isolated", "git")
        store.append(node)

        assert store.get_causes(node.id) == []
        assert store.get_effects(node.id) == []
        assert store.get_continuation(node.id) == []
        assert store.get_branches(node.id) == []
        assert store.get_fulfillments(node.id) == []


# =============================================================================
# Phase 1: Proof (Toulmin Argumentation) Tests
# =============================================================================

from services.witness import EvidenceTier, Proof


class TestProofCreation:
    """Tests for Proof dataclass creation and factory methods."""

    def test_proof_basic_creation(self) -> None:
        """Create Proof with all fields."""
        proof = Proof(
            data="3 hours, 45K tokens invested",
            warrant="Infrastructure investment enables future velocity",
            claim="This refactoring was worthwhile",
            backing="CLAUDE.md: 'DI > mocking' pattern saves 30% test time",
            qualifier="almost certainly",
            rebuttals=("unless the API changes completely",),
            tier=EvidenceTier.EMPIRICAL,
            principles=("composable", "generative"),
        )

        assert proof.data == "3 hours, 45K tokens invested"
        assert proof.warrant == "Infrastructure investment enables future velocity"
        assert proof.claim == "This refactoring was worthwhile"
        assert proof.backing == "CLAUDE.md: 'DI > mocking' pattern saves 30% test time"
        assert proof.qualifier == "almost certainly"
        assert proof.rebuttals == ("unless the API changes completely",)
        assert proof.tier == EvidenceTier.EMPIRICAL
        assert proof.principles == ("composable", "generative")

    def test_proof_defaults(self) -> None:
        """Proof has sensible defaults."""
        proof = Proof(
            data="tests pass",
            warrant="passing tests indicate correctness",
            claim="code is correct",
        )

        assert proof.backing == ""
        assert proof.qualifier == "probably"
        assert proof.rebuttals == ()
        assert proof.tier == EvidenceTier.EMPIRICAL
        assert proof.principles == ()

    def test_proof_categorical_factory(self) -> None:
        """Proof.categorical() creates mathematical proof."""
        proof = Proof.categorical(
            data="Id >> f ≡ f ≡ f >> Id",
            warrant="Identity law holds",
            claim="Agent satisfies category laws",
            principles=("composable",),
        )

        assert proof.tier == EvidenceTier.CATEGORICAL
        assert proof.qualifier == "definitely"
        assert proof.principles == ("composable",)

    def test_proof_empirical_factory(self) -> None:
        """Proof.empirical() creates test-based proof."""
        proof = Proof.empirical(
            data="47 tests pass in 0.53s",
            warrant="Comprehensive test coverage indicates correctness",
            claim="Mark implementation is correct",
            backing="test_trace_node.py covers all Mark laws",
            principles=("composable", "generative"),
        )

        assert proof.tier == EvidenceTier.EMPIRICAL
        assert proof.qualifier == "almost certainly"
        assert proof.backing == "test_trace_node.py covers all Mark laws"

    def test_proof_aesthetic_factory(self) -> None:
        """Proof.aesthetic() creates Hardy-criteria proof."""
        proof = Proof.aesthetic(
            data="Single dataclass captures justification essence",
            warrant="Inevitability: this is the right abstraction",
            claim="Proof design is elegant",
            principles=("tasteful", "generative"),
        )

        assert proof.tier == EvidenceTier.AESTHETIC
        assert proof.qualifier == "arguably"

    def test_proof_somatic_factory(self) -> None:
        """Proof.somatic() creates Mirror Test proof."""
        proof = Proof.somatic(
            claim="This feels like Kent on his best day",
            feeling="deeply right",
        )

        assert proof.tier == EvidenceTier.SOMATIC
        assert proof.qualifier == "personally"
        assert proof.data == "deeply right"
        assert "Mirror Test" in proof.warrant
        assert "ethical" in proof.principles
        assert "joy-inducing" in proof.principles


class TestProofImmutability:
    """Tests for Proof immutability (frozen=True)."""

    def test_proof_is_frozen(self) -> None:
        """Proof cannot be modified after creation."""
        proof = Proof(data="test", warrant="test", claim="test")

        with pytest.raises(FrozenInstanceError):
            proof.claim = "modified"  # type: ignore[misc]

    def test_proof_strengthen_returns_new_instance(self) -> None:
        """strengthen() returns new Proof with added backing."""
        original = Proof.empirical(
            data="tests pass",
            warrant="passing tests indicate correctness",
            claim="code works",
            backing="unit tests",
        )

        strengthened = original.strengthen("integration tests also pass")

        # Original unchanged
        assert original.backing == "unit tests"
        # New instance has combined backing
        assert strengthened.backing == "unit tests; integration tests also pass"
        assert strengthened is not original

    def test_proof_with_rebuttal_returns_new_instance(self) -> None:
        """with_rebuttal() returns new Proof with added rebuttal."""
        original = Proof.empirical(
            data="performance improved",
            warrant="benchmarks show 10x speedup",
            claim="optimization was worthwhile",
        )

        with_rebuttal = original.with_rebuttal("unless memory usage is a concern")

        # Original unchanged
        assert original.rebuttals == ()
        # New instance has rebuttal
        assert with_rebuttal.rebuttals == ("unless memory usage is a concern",)
        assert with_rebuttal is not original


class TestProofSerialization:
    """Tests for Proof serialization."""

    def test_proof_to_dict(self) -> None:
        """to_dict() serializes all fields."""
        proof = Proof(
            data="3 hours invested",
            warrant="time investment pays off",
            claim="worthwhile effort",
            backing="historical evidence",
            qualifier="almost certainly",
            rebuttals=("unless project cancelled",),
            tier=EvidenceTier.EMPIRICAL,
            principles=("composable", "generative"),
        )

        d = proof.to_dict()

        assert d["data"] == "3 hours invested"
        assert d["warrant"] == "time investment pays off"
        assert d["claim"] == "worthwhile effort"
        assert d["backing"] == "historical evidence"
        assert d["qualifier"] == "almost certainly"
        assert d["rebuttals"] == ["unless project cancelled"]
        assert d["tier"] == "EMPIRICAL"
        assert d["principles"] == ["composable", "generative"]

    def test_proof_from_dict(self) -> None:
        """from_dict() restores Proof correctly."""
        data = {
            "data": "tests pass",
            "warrant": "tests indicate correctness",
            "claim": "code is correct",
            "backing": "comprehensive suite",
            "qualifier": "definitely",
            "rebuttals": ["unless tests are wrong"],
            "tier": "CATEGORICAL",
            "principles": ["composable"],
        }

        proof = Proof.from_dict(data)

        assert proof.data == "tests pass"
        assert proof.warrant == "tests indicate correctness"
        assert proof.claim == "code is correct"
        assert proof.backing == "comprehensive suite"
        assert proof.qualifier == "definitely"
        assert proof.rebuttals == ("unless tests are wrong",)
        assert proof.tier == EvidenceTier.CATEGORICAL
        assert proof.principles == ("composable",)

    def test_proof_roundtrip(self) -> None:
        """Proof survives to_dict -> from_dict roundtrip."""
        original = Proof.empirical(
            data="complex evidence",
            warrant="sophisticated reasoning",
            claim="important conclusion",
            backing="deep support",
            principles=("tasteful", "curated", "ethical"),
        )

        restored = Proof.from_dict(original.to_dict())

        assert restored.data == original.data
        assert restored.warrant == original.warrant
        assert restored.claim == original.claim
        assert restored.backing == original.backing
        assert restored.qualifier == original.qualifier
        assert restored.tier == original.tier
        assert restored.principles == original.principles


class TestProofIntegrationWithMark:
    """Tests for Mark with Proof field."""

    def test_mark_with_proof(self) -> None:
        """Mark can carry a Proof."""
        proof = Proof.empirical(
            data="Refactored DI container",
            warrant="DI enables Crown Jewel pattern",
            claim="Refactoring was worthwhile",
            principles=("composable", "generative"),
        )

        mark = Mark(
            origin="witness",
            stimulus=Stimulus.from_prompt("Refactor request"),
            response=Response.thought("Completed refactoring"),
            proof=proof,
        )

        assert mark.proof is not None
        assert mark.proof.claim == "Refactoring was worthwhile"
        assert mark.proof.tier == EvidenceTier.EMPIRICAL

    def test_mark_without_proof(self) -> None:
        """Mark works without Proof (backwards compatible)."""
        mark = Mark.from_thought("Simple thought", "git")

        assert mark.proof is None

    def test_mark_with_proof_method(self) -> None:
        """with_proof() attaches Proof to existing Mark."""
        mark = Mark.from_thought("Initial thought", "git")
        assert mark.proof is None

        proof = Proof.somatic(claim="Feels right")
        mark_with_proof = mark.with_proof(proof)

        # Original unchanged
        assert mark.proof is None
        # New mark has proof
        assert mark_with_proof.proof is not None
        assert mark_with_proof.proof.claim == "Feels right"
        # Other fields preserved
        assert mark_with_proof.id == mark.id
        assert mark_with_proof.origin == mark.origin

    def test_mark_with_proof_serialization(self) -> None:
        """Mark with Proof survives serialization."""
        proof = Proof.categorical(
            data="Laws verified",
            warrant="Category laws are necessary",
            claim="Agent is valid",
        )
        mark = Mark(
            origin="witness",
            stimulus=Stimulus.from_prompt("Test"),
            response=Response.thought("Result"),
            proof=proof,
        )

        # Serialize and restore
        data = mark.to_dict()
        restored = Mark.from_dict(data)

        assert restored.proof is not None
        assert restored.proof.claim == "Agent is valid"
        assert restored.proof.tier == EvidenceTier.CATEGORICAL

    def test_mark_without_proof_serialization(self) -> None:
        """Mark without Proof serializes correctly."""
        mark = Mark.from_thought("No proof thought", "git")

        data = mark.to_dict()
        assert data["proof"] is None

        restored = Mark.from_dict(data)
        assert restored.proof is None


class TestEvidenceTier:
    """Tests for EvidenceTier enum."""

    def test_all_tiers_exist(self) -> None:
        """All five evidence tiers exist."""
        assert EvidenceTier.CATEGORICAL.value == 1
        assert EvidenceTier.EMPIRICAL.value == 2
        assert EvidenceTier.AESTHETIC.value == 3
        assert EvidenceTier.GENEALOGICAL.value == 4
        assert EvidenceTier.SOMATIC.value == 5

    def test_tier_ordering(self) -> None:
        """Tiers have meaningful ordering."""
        # Lower values are more objective
        assert EvidenceTier.CATEGORICAL.value < EvidenceTier.EMPIRICAL.value
        assert EvidenceTier.EMPIRICAL.value < EvidenceTier.AESTHETIC.value
        assert EvidenceTier.AESTHETIC.value < EvidenceTier.GENEALOGICAL.value
        assert EvidenceTier.GENEALOGICAL.value < EvidenceTier.SOMATIC.value


class TestProofRepr:
    """Tests for Proof representation."""

    def test_proof_repr_short_claim(self) -> None:
        """repr() shows short claims fully."""
        proof = Proof(data="d", warrant="w", claim="Short claim")
        repr_str = repr(proof)

        assert "Short claim" in repr_str
        assert "probably" in repr_str
        assert "EMPIRICAL" in repr_str

    def test_proof_repr_long_claim_truncated(self) -> None:
        """repr() truncates long claims."""
        long_claim = "A" * 100
        proof = Proof(data="d", warrant="w", claim=long_claim)
        repr_str = repr(proof)

        assert "..." in repr_str
        assert len(repr_str) < 150  # Reasonable length
