"""
Tests for ModalScope (Phase 2.2).

Verifies:
- Branch creation and isolation
- Merge strategies (SUMMARIZE, SQUASH, REBASE)
- Discard behavior
- Budget enforcement
- Comonadic properties (duplicate-style branching)
"""

from __future__ import annotations

from datetime import UTC, datetime

import pytest

from ..context_window import TurnRole
from ..modal_scope import (
    DiscardResult,
    MergeResult,
    MergeStrategy,
    ModalScope,
)


class TestModalScopeCreation:
    """Tests for ModalScope creation."""

    def test_create_root_scope(self) -> None:
        """Can create a root scope."""
        root = ModalScope.create_root(max_tokens=8000)

        assert root.is_root
        assert root.is_active
        assert root.parent_scope is None
        assert root.branch_name == "main"
        assert root.entropy_budget == 1.0
        assert root.depth == 0

    def test_create_root_with_system_message(self) -> None:
        """Root scope can have initial system message."""
        root = ModalScope.create_root(
            max_tokens=8000,
            initial_system="You are a helpful assistant.",
        )

        assert len(root.window) == 1
        turns = root.window.all_turns()
        assert turns[0].role == TurnRole.SYSTEM
        assert "helpful assistant" in turns[0].content

    def test_scope_id_format(self) -> None:
        """Scope IDs have correct format."""
        root = ModalScope.create_root()
        assert root.scope_id.startswith("root-")
        assert len(root.scope_id) == len("root-") + 8  # 8 hex chars

    def test_created_at_is_set(self) -> None:
        """created_at timestamp is set on creation."""
        before = datetime.now(UTC)
        root = ModalScope.create_root()
        after = datetime.now(UTC)

        assert before <= root.created_at <= after


class TestBranching:
    """Tests for branch() operation."""

    @pytest.fixture
    def root_with_context(self) -> ModalScope:
        """Create a root scope with some context."""
        root = ModalScope.create_root(max_tokens=8000)
        root.window.append(TurnRole.USER, "What are the options?")
        root.window.append(TurnRole.ASSISTANT, "Let me explore...")
        return root

    def test_branch_creates_child(self, root_with_context: ModalScope) -> None:
        """branch() creates a child scope."""
        child = root_with_context.branch("option-a")

        assert not child.is_root
        assert child.parent_scope == root_with_context.scope_id
        assert child.branch_name == "option-a"
        assert child.is_active

    def test_branch_scope_id_is_nested(self, root_with_context: ModalScope) -> None:
        """Child scope ID contains parent ID."""
        child = root_with_context.branch("option-a")

        assert child.scope_id == f"{root_with_context.scope_id}:option-a"
        assert child.depth == 1

    def test_branch_inherits_context(self, root_with_context: ModalScope) -> None:
        """Child inherits parent's context."""
        child = root_with_context.branch("option-a")

        # Child should have same turns as parent at branch time
        assert len(child.window) == len(root_with_context.window)
        child_turns = child.window.all_turns()
        parent_turns = root_with_context.window.all_turns()
        assert child_turns[0].content == parent_turns[0].content

    def test_branch_is_isolated(self, root_with_context: ModalScope) -> None:
        """Changes in branch don't affect parent."""
        child = root_with_context.branch("option-a")
        original_parent_len = len(root_with_context.window)

        # Add turns to child
        child.window.append(TurnRole.ASSISTANT, "Option A analysis...")
        child.window.append(TurnRole.ASSISTANT, "More analysis...")

        # Parent should be unchanged
        assert len(root_with_context.window) == original_parent_len
        assert len(child.window) == original_parent_len + 2

    def test_multiple_branches(self, root_with_context: ModalScope) -> None:
        """Can create multiple branches from same parent."""
        branch_a = root_with_context.branch("option-a")
        branch_b = root_with_context.branch("option-b")
        branch_c = root_with_context.branch("option-c")

        assert len(root_with_context.children) == 3
        assert branch_a.branch_name == "option-a"
        assert branch_b.branch_name == "option-b"
        assert branch_c.branch_name == "option-c"

    def test_duplicate_branch_name_fails(self, root_with_context: ModalScope) -> None:
        """Cannot create two branches with same name."""
        root_with_context.branch("option-a")

        with pytest.raises(ValueError, match="already exists"):
            root_with_context.branch("option-a")

    def test_branch_with_custom_budget(self, root_with_context: ModalScope) -> None:
        """branch() accepts custom entropy budget."""
        child = root_with_context.branch("expensive", budget=0.2)
        assert child.entropy_budget == 0.2

    def test_branch_invalid_budget_fails(self, root_with_context: ModalScope) -> None:
        """branch() rejects invalid budget values."""
        with pytest.raises(ValueError, match="Budget"):
            root_with_context.branch("bad", budget=0)

        with pytest.raises(ValueError, match="Budget"):
            root_with_context.branch("bad", budget=1.5)

    def test_branch_with_commit_message(self, root_with_context: ModalScope) -> None:
        """branch() accepts optional commit message."""
        child = root_with_context.branch(
            "option-a",
            commit_message="Exploring recursive approach",
        )
        assert child.commit_message == "Exploring recursive approach"

    def test_nested_branching(self, root_with_context: ModalScope) -> None:
        """Can branch from a branch."""
        level1 = root_with_context.branch("level1")
        level2 = level1.branch("level2")
        level3 = level2.branch("level3")

        assert level1.depth == 1
        assert level2.depth == 2
        assert level3.depth == 3
        assert level3.parent_scope == level2.scope_id


class TestMerge:
    """Tests for merge() operation."""

    @pytest.fixture
    def root_and_branch(self) -> tuple[ModalScope, ModalScope]:
        """Create root and branch with divergent content."""
        root = ModalScope.create_root(max_tokens=8000)
        root.window.append(TurnRole.USER, "What are the options?")

        branch = root.branch("explore")
        branch.window.append(TurnRole.ASSISTANT, "Let me explore option A...")
        branch.window.append(TurnRole.USER, "Tell me more")
        branch.window.append(TurnRole.ASSISTANT, "Here are the details...")

        return root, branch

    def test_merge_summarize(
        self, root_and_branch: tuple[ModalScope, ModalScope]
    ) -> None:
        """SUMMARIZE merge creates summary turn."""
        root, branch = root_and_branch
        original_len = len(root.window)

        result = root.merge(branch, strategy=MergeStrategy.SUMMARIZE)

        assert result.success
        assert result.strategy == MergeStrategy.SUMMARIZE
        assert result.merged_turns == 3  # 3 new turns in branch
        assert result.summary is not None
        assert "explore" in result.summary.lower()

        # Root should have one new turn (the summary)
        assert len(root.window) == original_len + 1

    def test_merge_squash(self, root_and_branch: tuple[ModalScope, ModalScope]) -> None:
        """SQUASH merge creates single turn with decisions."""
        root, branch = root_and_branch
        original_len = len(root.window)

        result = root.merge(branch, strategy=MergeStrategy.SQUASH)

        assert result.success
        assert result.strategy == MergeStrategy.SQUASH
        assert len(root.window) == original_len + 1

        # Squashed turn should contain assistant content
        new_turn = root.window.all_turns()[-1]
        assert "Squashed" in new_turn.content

    def test_merge_rebase(self, root_and_branch: tuple[ModalScope, ModalScope]) -> None:
        """REBASE merge replays all turns."""
        root, branch = root_and_branch
        original_len = len(root.window)

        result = root.merge(branch, strategy=MergeStrategy.REBASE)

        assert result.success
        assert result.strategy == MergeStrategy.REBASE
        # Should have all 3 new turns
        assert len(root.window) == original_len + 3

    def test_merge_marks_branch_as_merged(
        self, root_and_branch: tuple[ModalScope, ModalScope]
    ) -> None:
        """Merged branch is marked as such."""
        root, branch = root_and_branch
        assert branch.is_active

        root.merge(branch)

        assert not branch.is_active
        assert branch._is_merged

    def test_merge_removes_from_children(
        self, root_and_branch: tuple[ModalScope, ModalScope]
    ) -> None:
        """Merged branch is removed from parent's children."""
        root, branch = root_and_branch
        assert "explore" in [c.branch_name for c in root.children]

        root.merge(branch)

        assert "explore" not in [c.branch_name for c in root.children]

    def test_cannot_merge_non_child(self) -> None:
        """Cannot merge scope that isn't a child."""
        root1 = ModalScope.create_root()
        root2 = ModalScope.create_root()
        orphan = root2.branch("orphan")

        result = root1.merge(orphan)

        assert not result.success
        assert result.error is not None
        assert "not a child" in result.error

    def test_cannot_merge_twice(
        self, root_and_branch: tuple[ModalScope, ModalScope]
    ) -> None:
        """Cannot merge the same branch twice."""
        root, branch = root_and_branch
        root.merge(branch)

        result = root.merge(branch)

        assert not result.success
        assert result.error is not None
        assert "already merged" in result.error

    def test_merge_empty_branch(self) -> None:
        """Merging branch with no new turns succeeds gracefully."""
        root = ModalScope.create_root()
        root.window.append(TurnRole.USER, "Hello")
        branch = root.branch("empty")
        # Don't add anything to branch

        result = root.merge(branch)

        assert result.success
        assert result.merged_turns == 0

    def test_merge_uses_branch_default_strategy(self) -> None:
        """Merge uses branch's default strategy if not specified."""
        root = ModalScope.create_root()
        branch = root.branch("squashy", strategy=MergeStrategy.SQUASH)
        branch.window.append(TurnRole.ASSISTANT, "Some content")

        result = root.merge(branch)  # No strategy specified

        assert result.strategy == MergeStrategy.SQUASH


class TestDiscard:
    """Tests for discard() operation."""

    @pytest.fixture
    def root_and_branch(self) -> tuple[ModalScope, ModalScope]:
        """Create root and branch with content."""
        root = ModalScope.create_root(max_tokens=8000)
        root.window.append(TurnRole.USER, "Let's explore")

        branch = root.branch("explore", budget=0.1)
        branch.window.append(TurnRole.ASSISTANT, "Exploring...")
        branch.window.append(TurnRole.ASSISTANT, "More exploration...")

        return root, branch

    def test_discard_marks_branch(
        self, root_and_branch: tuple[ModalScope, ModalScope]
    ) -> None:
        """Discard marks branch as discarded."""
        root, branch = root_and_branch
        assert branch.is_active

        root.discard(branch)

        assert not branch.is_active
        assert branch._is_discarded

    def test_discard_removes_from_children(
        self, root_and_branch: tuple[ModalScope, ModalScope]
    ) -> None:
        """Discarded branch is removed from parent's children."""
        root, branch = root_and_branch
        assert "explore" in [c.branch_name for c in root.children]

        root.discard(branch)

        assert "explore" not in [c.branch_name for c in root.children]

    def test_discard_returns_entropy(
        self, root_and_branch: tuple[ModalScope, ModalScope]
    ) -> None:
        """Discard returns entropy budget info."""
        root, branch = root_and_branch

        result = root.discard(branch)

        assert result.success
        assert result.discarded_turns >= 0
        assert result.entropy_returned >= 0

    def test_discard_counts_new_turns(
        self, root_and_branch: tuple[ModalScope, ModalScope]
    ) -> None:
        """Discard reports correct turn count."""
        root, branch = root_and_branch

        result = root.discard(branch)

        assert result.discarded_turns == 2  # The 2 turns added to branch

    def test_cannot_discard_non_child(self) -> None:
        """Cannot discard scope that isn't a child."""
        root1 = ModalScope.create_root()
        root2 = ModalScope.create_root()
        orphan = root2.branch("orphan")

        result = root1.discard(orphan)

        assert not result.success
        assert result.error is not None
        assert "not a child" in result.error

    def test_cannot_discard_merged_branch(
        self, root_and_branch: tuple[ModalScope, ModalScope]
    ) -> None:
        """Cannot discard a branch that was already merged."""
        root, branch = root_and_branch
        root.merge(branch)

        result = root.discard(branch)

        assert not result.success
        assert result.error is not None
        assert "already merged" in result.error

    def test_cannot_discard_twice(
        self, root_and_branch: tuple[ModalScope, ModalScope]
    ) -> None:
        """Cannot discard the same branch twice."""
        root, branch = root_and_branch
        root.discard(branch)

        result = root.discard(branch)

        assert not result.success
        assert result.error is not None
        assert "already discarded" in result.error

    def test_parent_unchanged_after_discard(
        self, root_and_branch: tuple[ModalScope, ModalScope]
    ) -> None:
        """Parent context is unchanged after discard."""
        root, branch = root_and_branch
        original_len = len(root.window)

        root.discard(branch)

        assert len(root.window) == original_len


class TestBudgetEnforcement:
    """Tests for entropy budget tracking."""

    def test_budget_remaining_full(self) -> None:
        """Fresh branch has full budget remaining."""
        root = ModalScope.create_root()
        root.window.append(TurnRole.USER, "Hello")
        branch = root.branch("test", budget=0.1)

        assert branch.budget_remaining == pytest.approx(1.0, rel=0.1)

    def test_budget_decreases_with_tokens(self) -> None:
        """Budget remaining decreases as tokens are added."""
        root = ModalScope.create_root()
        # Add substantial content to parent
        root.window.append(TurnRole.USER, "x" * 400)  # ~100 tokens
        branch = root.branch("test", budget=0.1)  # 10% = ~10 tokens allowed

        # Add tokens to branch
        branch.window.append(TurnRole.ASSISTANT, "y" * 40)  # ~10 tokens

        # Should have used most of budget
        assert branch.budget_remaining < 0.5

    def test_is_over_budget(self) -> None:
        """is_over_budget returns True when budget exhausted."""
        root = ModalScope.create_root()
        root.window.append(TurnRole.USER, "x" * 400)  # ~100 tokens
        branch = root.branch("test", budget=0.05)  # 5% = ~5 tokens

        # Add more than budget allows
        branch.window.append(TurnRole.ASSISTANT, "y" * 100)  # ~25 tokens

        assert branch.is_over_budget

    def test_tokens_remaining(self) -> None:
        """tokens_remaining reports correct value."""
        root = ModalScope.create_root()
        root.window.append(TurnRole.USER, "x" * 400)  # ~100 tokens
        branch = root.branch("test", budget=0.1)  # 10% = ~10 tokens

        initial_remaining = branch.tokens_remaining
        branch.window.append(TurnRole.ASSISTANT, "y" * 20)  # ~5 tokens

        assert branch.tokens_remaining < initial_remaining


class TestSerialization:
    """Tests for to_dict/from_dict."""

    def test_roundtrip_root(self) -> None:
        """Root scope survives serialization roundtrip."""
        root = ModalScope.create_root(max_tokens=8000)
        root.window.append(TurnRole.USER, "Hello")
        root.window.append(TurnRole.ASSISTANT, "Hi there!")

        data = root.to_dict()
        restored = ModalScope.from_dict(data)

        assert restored.scope_id == root.scope_id
        assert restored.branch_name == root.branch_name
        assert len(restored.window) == len(root.window)

    def test_roundtrip_with_children(self) -> None:
        """Scope with children survives serialization roundtrip."""
        root = ModalScope.create_root()
        root.window.append(TurnRole.USER, "Hello")
        branch = root.branch("child")
        branch.window.append(TurnRole.ASSISTANT, "Child content")

        data = root.to_dict()
        restored = ModalScope.from_dict(data)

        assert len(restored.children) == 1
        restored_child = restored.get_child("child")
        assert restored_child is not None
        assert len(restored_child.window) == 2

    def test_roundtrip_preserves_state(self) -> None:
        """Merge/discard state survives serialization."""
        root = ModalScope.create_root()
        branch1 = root.branch("merged")
        branch2 = root.branch("discarded")
        root.merge(branch1)
        root.discard(branch2)

        # Children are removed after merge/discard at runtime
        assert len(root.children) == 0

        # Since children are removed, serialize and restore
        data = root.to_dict()
        restored = ModalScope.from_dict(data)

        # Restored should also have no children
        assert len(restored.children) == 0
        assert restored.is_active


class TestComonadProperties:
    """Tests verifying comonadic properties of branching."""

    def test_branch_is_duplicate_style(self) -> None:
        """branch() creates independent snapshots like duplicate()."""
        root = ModalScope.create_root()
        root.window.append(TurnRole.USER, "Initial")

        # Create branches at same point
        branch_a = root.branch("a")
        branch_b = root.branch("b")

        # Diverge the branches
        branch_a.window.append(TurnRole.ASSISTANT, "Path A")
        branch_b.window.append(TurnRole.ASSISTANT, "Path B")

        # Each branch should be independent
        turns_a = branch_a.window.all_turns()
        turns_b = branch_b.window.all_turns()
        root_turns = root.window.all_turns()

        assert turns_a[-1].content == "Path A"
        assert turns_b[-1].content == "Path B"
        assert len(root_turns) == 1  # Unchanged

    def test_branching_preserves_history(self) -> None:
        """Branching preserves full history at branch point."""
        root = ModalScope.create_root()
        for i in range(5):
            root.window.append(TurnRole.USER, f"Message {i}")

        branch = root.branch("test")

        assert len(branch.window) == len(root.window)
        for i, turn in enumerate(branch.window.all_turns()):
            assert turn.content == f"Message {i}"


class TestStateTransitions:
    """Tests for branch state transitions."""

    def test_cannot_branch_from_merged(self) -> None:
        """Cannot branch from a merged scope."""
        root = ModalScope.create_root()
        branch = root.branch("child")
        root.merge(branch)

        with pytest.raises(ValueError, match="merged"):
            branch.branch("grandchild")

    def test_cannot_branch_from_discarded(self) -> None:
        """Cannot branch from a discarded scope."""
        root = ModalScope.create_root()
        branch = root.branch("child")
        root.discard(branch)

        with pytest.raises(ValueError, match="discarded"):
            branch.branch("grandchild")

    def test_get_child_returns_none_for_unknown(self) -> None:
        """get_child returns None for unknown branch name."""
        root = ModalScope.create_root()
        assert root.get_child("nonexistent") is None

    def test_get_child_returns_branch(self) -> None:
        """get_child returns the correct branch."""
        root = ModalScope.create_root()
        branch = root.branch("test")

        retrieved = root.get_child("test")

        assert retrieved is branch
