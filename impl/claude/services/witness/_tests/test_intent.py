"""
Tests for IntentTree.

Verifies laws:
- Law 1 (Typed): Every Intent has exactly one IntentType
- Law 2 (Tree Structure): Parent-child relationships form a tree
- Law 3 (Dependencies): Dependencies form a DAG (no cycles)
- Law 4 (Status Propagation): Parent status reflects children

See: spec/protocols/warp-primitives.md
"""

from __future__ import annotations

from dataclasses import FrozenInstanceError

import pytest

from services.witness.intent import (
    CyclicDependencyError,
    Intent,
    IntentId,
    IntentStatus,
    IntentTree,
    IntentType,
    get_intent_tree,
    reset_intent_tree,
)

# =============================================================================
# Law 1: Typed Tests
# =============================================================================


class TestLaw1Typed:
    """Law 1: Every Intent has exactly one IntentType."""

    def test_intent_has_type(self) -> None:
        """Every Intent has a type."""
        intent = Intent.create(
            description="Test task",
            intent_type=IntentType.IMPLEMENT,
        )

        assert intent.intent_type == IntentType.IMPLEMENT

    def test_all_intent_types(self) -> None:
        """All IntentTypes are valid."""
        for intent_type in IntentType:
            intent = Intent.create(
                description=f"Test {intent_type.value}",
                intent_type=intent_type,
            )
            assert intent.intent_type == intent_type

    def test_default_type_is_implement(self) -> None:
        """Default IntentType is IMPLEMENT."""
        intent = Intent.create(description="Test")
        assert intent.intent_type == IntentType.IMPLEMENT


# =============================================================================
# Law 2: Tree Structure Tests
# =============================================================================


class TestLaw2TreeStructure:
    """Law 2: Parent-child relationships form a tree."""

    def test_root_has_no_parent(self) -> None:
        """Root Intent has no parent."""
        intent = Intent.create(description="Root task")
        assert intent.parent_id is None

    def test_child_has_parent(self) -> None:
        """Child Intent references parent."""
        tree = IntentTree()

        root = Intent.create(description="Root")
        tree.add(root)

        child = Intent.create(
            description="Child",
            parent_id=root.id,
        )
        tree.add(child)

        assert child.parent_id == root.id
        # Parent should have child in children_ids
        updated_root = tree.get(root.id)
        assert child.id in updated_root.children_ids

    def test_deep_tree(self) -> None:
        """Tree can have multiple levels."""
        tree = IntentTree()

        root = Intent.create(description="Root")
        tree.add(root)

        child = Intent.create(description="Child", parent_id=root.id)
        tree.add(child)

        grandchild = Intent.create(description="Grandchild", parent_id=child.id)
        tree.add(grandchild)

        # Verify structure
        assert grandchild.parent_id == child.id
        updated_child = tree.get(child.id)
        assert grandchild.id in updated_child.children_ids

    def test_parent_must_exist(self) -> None:
        """Cannot add child if parent doesn't exist."""
        tree = IntentTree()

        child = Intent.create(
            description="Orphan",
            parent_id=IntentId("nonexistent"),
        )

        with pytest.raises(ValueError) as exc_info:
            tree.add(child)

        assert "not found" in str(exc_info.value)


# =============================================================================
# Law 3: Dependencies (DAG) Tests
# =============================================================================


class TestLaw3Dependencies:
    """Law 3: Dependencies form a DAG (no cycles)."""

    def test_intent_can_have_dependencies(self) -> None:
        """Intent can depend on other Intents."""
        tree = IntentTree()

        first = Intent.create(description="First")
        tree.add(first)

        second = Intent.create(
            description="Second",
            depends_on=(first.id,),
        )
        tree.add(second)

        assert first.id in second.depends_on

    def test_dependencies_must_exist(self) -> None:
        """Cannot depend on non-existent Intent."""
        tree = IntentTree()

        intent = Intent.create(
            description="Test",
            depends_on=(IntentId("nonexistent"),),
        )

        with pytest.raises(ValueError) as exc_info:
            tree.add(intent)

        assert "not found" in str(exc_info.value)

    def test_no_self_dependency(self) -> None:
        """Cannot depend on self (cycle of 1)."""
        tree = IntentTree()

        # Create intent and add it
        intent = Intent.create(description="Test")
        tree.add(intent)

        # Try to add dependency on self
        updated = Intent(
            id=intent.id,
            description=intent.description,
            intent_type=intent.intent_type,
            depends_on=(intent.id,),
        )

        with pytest.raises(CyclicDependencyError):
            tree._check_no_cycles(updated)

    def test_no_circular_dependencies(self) -> None:
        """Detects circular dependencies."""
        tree = IntentTree()

        a = Intent.create(description="A")
        tree.add(a)

        b = Intent.create(description="B", depends_on=(a.id,))
        tree.add(b)

        # Try to make A depend on B (creates cycle)
        c = Intent.create(description="C", depends_on=(b.id,))
        tree.add(c)

        # Now try to make A depend on C (A -> B -> C -> A would be cycle)
        a_with_dep = Intent(
            id=a.id,
            description=a.description,
            intent_type=a.intent_type,
            depends_on=(c.id,),
        )

        with pytest.raises(CyclicDependencyError):
            tree._check_no_cycles(a_with_dep)

    def test_multiple_dependencies_allowed(self) -> None:
        """Intent can have multiple dependencies."""
        tree = IntentTree()

        a = Intent.create(description="A")
        b = Intent.create(description="B")
        tree.add(a)
        tree.add(b)

        c = Intent.create(
            description="C",
            depends_on=(a.id, b.id),
        )
        tree.add(c)

        assert len(c.depends_on) == 2


# =============================================================================
# Law 4: Status Propagation Tests
# =============================================================================


class TestLaw4StatusPropagation:
    """Law 4: Parent status reflects children."""

    def test_all_children_complete_completes_parent(self) -> None:
        """All children COMPLETE → Parent COMPLETE."""
        tree = IntentTree()

        parent = Intent.create(description="Parent")
        tree.add(parent)

        child1 = Intent.create(description="Child 1", parent_id=parent.id)
        child2 = Intent.create(description="Child 2", parent_id=parent.id)
        tree.add(child1)
        tree.add(child2)

        # Complete both children
        tree.update(child1.complete())
        tree.update(child2.complete())

        # Propagate status
        tree.propagate_status(child1.id)

        updated_parent = tree.get(parent.id)
        assert updated_parent.status == IntentStatus.COMPLETE

    def test_blocked_child_blocks_parent(self) -> None:
        """Any child BLOCKED → Parent BLOCKED."""
        tree = IntentTree()

        parent = Intent.create(description="Parent")
        tree.add(parent)

        child1 = Intent.create(description="Child 1", parent_id=parent.id)
        child2 = Intent.create(description="Child 2", parent_id=parent.id)
        tree.add(child1)
        tree.add(child2)

        # Block one child
        tree.update(child1.block("Test block"))

        tree.propagate_status(child1.id)

        updated_parent = tree.get(parent.id)
        assert updated_parent.status == IntentStatus.BLOCKED

    def test_active_child_activates_parent(self) -> None:
        """Any child ACTIVE → Parent ACTIVE."""
        tree = IntentTree()

        parent = Intent.create(description="Parent")
        tree.add(parent)

        child = Intent.create(description="Child", parent_id=parent.id)
        tree.add(child)

        # Start child
        tree.update(child.start())
        tree.propagate_status(child.id)

        updated_parent = tree.get(parent.id)
        assert updated_parent.status == IntentStatus.ACTIVE


# =============================================================================
# Intent Status Transition Tests
# =============================================================================


class TestIntentStatusTransitions:
    """Tests for Intent status transitions."""

    def test_pending_to_active(self) -> None:
        """PENDING → ACTIVE via start()."""
        intent = Intent.create(description="Test")
        assert intent.status == IntentStatus.PENDING

        started = intent.start()
        assert started.status == IntentStatus.ACTIVE
        assert started.started_at is not None

    def test_active_to_complete(self) -> None:
        """ACTIVE → COMPLETE via complete()."""
        intent = Intent.create(description="Test").start()
        completed = intent.complete()

        assert completed.status == IntentStatus.COMPLETE
        assert completed.completed_at is not None

    def test_block_sets_reason(self) -> None:
        """block() stores reason in metadata."""
        intent = Intent.create(description="Test")
        blocked = intent.block("Waiting for review")

        assert blocked.status == IntentStatus.BLOCKED
        assert blocked.metadata["block_reason"] == "Waiting for review"

    def test_cancel_intent(self) -> None:
        """Intent can be cancelled."""
        intent = Intent.create(description="Test").start()
        cancelled = intent.cancel()

        assert cancelled.status == IntentStatus.CANCELLED
        assert cancelled.is_terminal


# =============================================================================
# IntentTree Query Tests
# =============================================================================


class TestIntentTreeQueries:
    """Tests for IntentTree query methods."""

    def setup_method(self) -> None:
        """Reset global tree."""
        reset_intent_tree()

    def test_by_type(self) -> None:
        """Query by IntentType."""
        tree = IntentTree()

        explore = Intent.create(description="Explore", intent_type=IntentType.EXPLORE)
        implement = Intent.create(description="Implement", intent_type=IntentType.IMPLEMENT)
        verify = Intent.create(description="Verify", intent_type=IntentType.VERIFY)

        tree.add(explore)
        tree.add(implement)
        tree.add(verify)

        explore_intents = tree.by_type(IntentType.EXPLORE)
        assert len(explore_intents) == 1
        assert explore_intents[0].id == explore.id

    def test_by_status(self) -> None:
        """Query by status."""
        tree = IntentTree()

        pending = Intent.create(description="Pending")
        active = Intent.create(description="Active").start()
        complete = Intent.create(description="Complete").start().complete()

        tree.add(pending)
        tree.add(active)
        tree.add(complete)

        pending_intents = tree.by_status(IntentStatus.PENDING)
        assert len(pending_intents) == 1

    def test_ready_to_start(self) -> None:
        """Find Intents ready to start (deps met)."""
        tree = IntentTree()

        first = Intent.create(description="First")
        tree.add(first)

        second = Intent.create(description="Second", depends_on=(first.id,))
        tree.add(second)

        # First is ready (no deps)
        ready = tree.ready_to_start()
        assert len(ready) == 1
        assert ready[0].id == first.id

        # Complete first
        tree.update(first.start().complete())

        # Now second is ready
        ready = tree.ready_to_start()
        assert len(ready) == 1
        assert ready[0].id == second.id

    def test_leaves(self) -> None:
        """Get leaf Intents (no children)."""
        tree = IntentTree()

        root = Intent.create(description="Root")
        tree.add(root)

        leaf1 = Intent.create(description="Leaf 1", parent_id=root.id)
        leaf2 = Intent.create(description="Leaf 2", parent_id=root.id)
        tree.add(leaf1)
        tree.add(leaf2)

        leaves = tree.leaves()
        assert len(leaves) == 2
        assert all(not leaf.children_ids for leaf in leaves)


# =============================================================================
# Immutability Tests
# =============================================================================


class TestImmutability:
    """Tests for Intent immutability."""

    def test_intent_is_frozen(self) -> None:
        """Intent is frozen dataclass."""
        intent = Intent.create(description="Test")

        with pytest.raises(FrozenInstanceError):
            intent.description = "Modified"  # type: ignore[misc]

    def test_status_transitions_return_new_intent(self) -> None:
        """Status transitions return new Intent (original unchanged)."""
        original = Intent.create(description="Test")
        started = original.start()

        assert original.status == IntentStatus.PENDING
        assert started.status == IntentStatus.ACTIVE
        assert original.id == started.id  # Same ID


# =============================================================================
# Serialization Tests
# =============================================================================


class TestSerialization:
    """Tests for to_dict/from_dict roundtrip."""

    def test_intent_roundtrip(self) -> None:
        """Intent serializes correctly."""
        original = Intent.create(
            description="Test intent",
            intent_type=IntentType.DESIGN,
            priority=5,
            tags=("important", "urgent"),
        ).start()

        data = original.to_dict()
        restored = Intent.from_dict(data)

        assert restored.id == original.id
        assert restored.description == original.description
        assert restored.intent_type == original.intent_type
        assert restored.status == IntentStatus.ACTIVE
        assert restored.priority == 5
        assert restored.tags == ("important", "urgent")

    def test_intent_tree_roundtrip(self) -> None:
        """IntentTree serializes correctly."""
        tree = IntentTree()

        root = Intent.create(description="Root")
        tree.add(root)

        child = Intent.create(description="Child", parent_id=root.id)
        tree.add(child)

        data = tree.to_dict()
        restored = IntentTree.from_dict(data)

        assert len(restored) == 2
        assert restored.root_id == root.id


# =============================================================================
# Edge Cases
# =============================================================================


class TestEdgeCases:
    """Edge cases for robustness."""

    def test_empty_tree(self) -> None:
        """Empty tree works correctly."""
        tree = IntentTree()

        assert len(tree) == 0
        assert tree.root is None
        assert tree.leaves() == []
        assert tree.roots() == []
        assert tree.ready_to_start() == []

    def test_single_intent_is_root_and_leaf(self) -> None:
        """Single Intent is both root and leaf."""
        tree = IntentTree()

        intent = Intent.create(description="Solo")
        tree.add(intent)

        assert tree.root.id == intent.id
        leaves = tree.leaves()
        assert len(leaves) == 1
        assert leaves[0].id == intent.id

    def test_dependencies_and_parent_are_independent(self) -> None:
        """Dependencies and parent relationships are separate."""
        tree = IntentTree()

        root = Intent.create(description="Root")
        tree.add(root)

        prereq = Intent.create(description="Prerequisite", parent_id=root.id)
        tree.add(prereq)

        # This Intent is a child of root AND depends on prereq
        dependent = Intent.create(
            description="Dependent",
            parent_id=root.id,
            depends_on=(prereq.id,),
        )
        tree.add(dependent)

        # Both relationships exist
        assert dependent.parent_id == root.id
        assert prereq.id in dependent.depends_on

    def test_priority_ordering_in_ready(self) -> None:
        """ready_to_start returns highest priority first."""
        tree = IntentTree()

        low = Intent.create(description="Low", priority=1)
        high = Intent.create(description="High", priority=10)
        medium = Intent.create(description="Medium", priority=5)

        tree.add(low)
        tree.add(high)
        tree.add(medium)

        ready = tree.ready_to_start()
        assert ready[0].priority == 10
        assert ready[1].priority == 5
        assert ready[2].priority == 1
