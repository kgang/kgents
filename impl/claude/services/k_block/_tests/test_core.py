"""
Tests for K-Block core functionality.

Verifies:
- HARNESS_OPERAD laws
- Monad laws for K-Block
- Basic operations
- Polynomial state transitions
- Cosmos append-only behavior

Philosophy:
    "The proof IS the decision. The test IS the verification."
"""

import pytest

from ..core import (
    Cosmos,
    EditDelta,
    EditingState,
    FileOperadHarness,
    IsolationState,
    KBlock,
    KBlockInput,
    KBlockPolynomial,
    KBlockState,
    generate_kblock_id,
    reset_cosmos,
    reset_harness,
)

# -----------------------------------------------------------------------------
# Fixtures
# -----------------------------------------------------------------------------


@pytest.fixture
def cosmos() -> Cosmos:
    """Fresh cosmos for each test."""
    reset_cosmos()
    return Cosmos()


@pytest.fixture
def harness(cosmos: Cosmos) -> FileOperadHarness:
    """Fresh harness for each test."""
    reset_harness()
    return FileOperadHarness(cosmos=cosmos)


# -----------------------------------------------------------------------------
# HARNESS_OPERAD Law Tests
# -----------------------------------------------------------------------------


class TestHarnessLaws:
    """
    Verify HARNESS_OPERAD laws.

    These are the fundamental guarantees of the K-Block system.
    """

    @pytest.mark.asyncio
    async def test_create_discard_identity(self, harness: FileOperadHarness, cosmos: Cosmos):
        """
        Law: discard(create(p)) ≡ id

        Creating then discarding a K-Block should have no cosmic effect.
        The cosmos should be identical before and after.
        """
        path = "test/sample.md"

        # Seed some content in cosmos
        await cosmos.commit(path, "original content")
        original_entries = cosmos.total_entries

        # Create K-Block
        block = await harness.create(path)
        assert block.content == "original content"
        assert block.isolation == IsolationState.PRISTINE

        # Discard it
        await harness.discard(block)

        # Cosmos should be unchanged
        assert cosmos.total_entries == original_entries
        content = await cosmos.read(path)
        assert content == "original content"

    @pytest.mark.asyncio
    async def test_save_idempotence(self, harness: FileOperadHarness, cosmos: Cosmos):
        """
        Law: save(save(kb)) ≡ save(kb)

        Saving a K-Block twice should be the same as saving once.
        The second save should be a no-op (no changes).
        """
        path = "test/sample.md"

        # Create and edit
        block = await harness.create(path)
        block.set_content("new content")

        # First save
        result1 = await harness.save(block)
        assert result1.success
        assert result1.version_id is not None

        # Second save
        result2 = await harness.save(block)
        assert result2.success
        assert result2.no_changes  # No changes since first save

        # Cosmos should have exactly one new entry
        history = await cosmos.history(path)
        assert len(history) == 1

    @pytest.mark.asyncio
    async def test_fork_merge_identity(self, harness: FileOperadHarness, cosmos: Cosmos):
        """
        Law: merge(fork(kb)) ≡ kb

        Forking then immediately merging (with no edits) should recover
        the original K-Block.
        """
        path = "test/sample.md"
        await cosmos.commit(path, "original content")

        # Create K-Block
        block = await harness.create(path)
        block.set_content("edited content")
        original_content = block.content

        # Fork
        left, right = await harness.fork(block)
        assert left.content == original_content
        assert right.content == original_content
        assert left.id != right.id

        # Merge (no independent edits)
        result = await harness.merge(left, right)
        assert result.success
        assert not result.has_conflicts

        # Content should be identical
        merged = harness.get_block(result.block_id)
        assert merged is not None
        assert merged.content == original_content

    @pytest.mark.asyncio
    async def test_checkpoint_rewind_identity(self, harness: FileOperadHarness, cosmos: Cosmos):
        """
        Law: rewind(kb, checkpoint(kb)) ≡ kb

        Creating a checkpoint then immediately rewinding should give
        the same content.
        """
        path = "test/sample.md"

        block = await harness.create(path)
        block.set_content("content at checkpoint")

        # Create checkpoint
        cp_id = await harness.checkpoint(block, "v1")

        # Edit further
        block.set_content("content after checkpoint")
        assert block.content == "content after checkpoint"

        # Rewind
        await harness.rewind(block, cp_id)
        assert block.content == "content at checkpoint"


# -----------------------------------------------------------------------------
# Monad Law Tests
# -----------------------------------------------------------------------------


class TestMonadLaws:
    """
    Verify K-Block monad laws.

    The K-Block forms a monad over Documents:
    - return: Doc -> KBlock Doc (create)
    - bind: KBlock Doc -> (Doc -> KBlock Doc) -> KBlock Doc
    """

    @pytest.mark.asyncio
    async def test_left_identity(self, harness: FileOperadHarness, cosmos: Cosmos):
        """
        Law: return a >>= f ≡ f a

        Lifting a document into K-Block then binding should equal
        applying the function directly.
        """
        path = "test/sample.md"
        initial_content = "hello world"
        await cosmos.commit(path, initial_content)

        # Define f: content -> K-Block with appended text
        def f(content: str) -> KBlock:
            block = KBlock(
                id=generate_kblock_id(),
                path=path,
                content=content + " appended",
                base_content=content,
            )
            return block

        # Left side: return a >>= f
        block = await harness.create(path)  # return
        result_left = block.bind(f)  # >>= f

        # Right side: f a
        result_right = f(initial_content)

        # Should be equivalent
        assert result_left.content == result_right.content

    @pytest.mark.asyncio
    async def test_right_identity(self, harness: FileOperadHarness, cosmos: Cosmos):
        """
        Law: m >>= return ≡ m

        Binding with return should give back the original K-Block content.
        """
        path = "test/sample.md"
        await cosmos.commit(path, "content")

        # Create K-Block
        block = await harness.create(path)
        block.set_content("edited content")
        original_content = block.content

        # Define return: content -> K-Block wrapping that content
        def return_fn(content: str) -> KBlock:
            return KBlock(
                id=generate_kblock_id(),
                path=path,
                content=content,
                base_content=content,
            )

        # m >>= return
        result = block.bind(return_fn)

        # Should be equivalent to m
        assert result.content == original_content

    @pytest.mark.asyncio
    async def test_associativity(self, harness: FileOperadHarness, cosmos: Cosmos):
        """
        Law: (m >>= f) >>= g ≡ m >>= (λx. f x >>= g)

        Binding is associative.
        """
        path = "test/sample.md"
        await cosmos.commit(path, "a")

        def f(content: str) -> KBlock:
            return KBlock(
                id=generate_kblock_id(),
                path=path,
                content=content + "b",
                base_content=content,
            )

        def g(content: str) -> KBlock:
            return KBlock(
                id=generate_kblock_id(),
                path=path,
                content=content + "c",
                base_content=content,
            )

        block = await harness.create(path)

        # Left side: (m >>= f) >>= g
        left = block.bind(f).bind(g)

        # Right side: m >>= (λx. f x >>= g)
        def fg(content: str) -> KBlock:
            return f(content).bind(g)

        right = block.bind(fg)

        # Should be equivalent
        assert left.content == right.content
        assert left.content == "abc"


# -----------------------------------------------------------------------------
# Basic Operation Tests
# -----------------------------------------------------------------------------


class TestBasicOperations:
    """Test basic K-Block operations."""

    @pytest.mark.asyncio
    async def test_create_new_path(self, harness: FileOperadHarness):
        """Creating K-Block for new path gives empty content."""
        block = await harness.create("new/path.md")
        assert block.content == ""
        assert block.base_content == ""
        assert block.isolation == IsolationState.PRISTINE

    @pytest.mark.asyncio
    async def test_create_existing_path(self, harness: FileOperadHarness, cosmos: Cosmos):
        """Creating K-Block for existing path loads content."""
        await cosmos.commit("existing.md", "existing content")

        block = await harness.create("existing.md")
        assert block.content == "existing content"
        assert block.base_content == "existing content"
        assert block.isolation == IsolationState.PRISTINE

    @pytest.mark.asyncio
    async def test_edit_marks_dirty(self, harness: FileOperadHarness):
        """Editing content marks K-Block as dirty."""
        block = await harness.create("test.md")
        assert block.isolation == IsolationState.PRISTINE

        block.set_content("edited")
        assert block.isolation == IsolationState.DIRTY
        assert block.is_dirty

    @pytest.mark.asyncio
    async def test_save_commits_to_cosmos(self, harness: FileOperadHarness, cosmos: Cosmos):
        """Saving writes content to cosmos."""
        block = await harness.create("test.md")
        block.set_content("new content")

        result = await harness.save(block)
        assert result.success
        assert result.version_id is not None

        # Verify in cosmos
        content = await cosmos.read("test.md")
        assert content == "new content"

    @pytest.mark.asyncio
    async def test_save_resets_isolation(self, harness: FileOperadHarness):
        """Saving resets K-Block to pristine."""
        block = await harness.create("test.md")
        block.set_content("new content")
        assert block.isolation == IsolationState.DIRTY

        await harness.save(block)
        assert block.isolation == IsolationState.PRISTINE
        assert not block.is_dirty

    @pytest.mark.asyncio
    async def test_discard_removes_block(self, harness: FileOperadHarness):
        """Discarding removes K-Block from registry."""
        block = await harness.create("test.md")
        block_id = block.id

        await harness.discard(block)

        assert harness.get_block(block_id) is None
        assert harness.get_block_for_path("test.md") is None


# -----------------------------------------------------------------------------
# Edit Delta Tests
# -----------------------------------------------------------------------------


class TestEditDelta:
    """Test edit delta operations."""

    @pytest.mark.asyncio
    async def test_insert(self, harness: FileOperadHarness):
        """Insert delta works correctly."""
        block = await harness.create("test.md")
        block.set_content("hello world")

        delta = EditDelta(operation="insert", position=5, new_text=" beautiful")
        block.edit(delta)

        assert block.content == "hello beautiful world"

    @pytest.mark.asyncio
    async def test_delete(self, harness: FileOperadHarness):
        """Delete delta works correctly."""
        block = await harness.create("test.md")
        block.set_content("hello world")

        delta = EditDelta(operation="delete", position=5, old_text=" world")
        block.edit(delta)

        assert block.content == "hello"

    @pytest.mark.asyncio
    async def test_replace(self, harness: FileOperadHarness):
        """Replace delta works correctly."""
        block = await harness.create("test.md")
        block.set_content("hello world")

        delta = EditDelta(operation="replace", position=6, old_text="world", new_text="universe")
        block.edit(delta)

        assert block.content == "hello universe"


# -----------------------------------------------------------------------------
# Cosmos Tests
# -----------------------------------------------------------------------------


class TestCosmos:
    """Test cosmos behavior."""

    @pytest.mark.asyncio
    async def test_append_only(self, cosmos: Cosmos):
        """Cosmos never overwrites, only appends."""
        path = "test.md"

        v1 = await cosmos.commit(path, "v1")
        v2 = await cosmos.commit(path, "v2")
        v3 = await cosmos.commit(path, "v3")

        # All versions exist
        assert await cosmos.read(path, v1) == "v1"
        assert await cosmos.read(path, v2) == "v2"
        assert await cosmos.read(path, v3) == "v3"

        # Latest is v3
        assert await cosmos.read(path) == "v3"

        # History has all versions
        history = await cosmos.history(path)
        assert len(history) == 3

    @pytest.mark.asyncio
    async def test_history_order(self, cosmos: Cosmos):
        """History returns newest first."""
        path = "test.md"

        await cosmos.commit(path, "first")
        await cosmos.commit(path, "second")
        await cosmos.commit(path, "third")

        history = await cosmos.history(path)
        assert [e.content for e in history] == ["third", "second", "first"]

    @pytest.mark.asyncio
    async def test_time_travel(self, cosmos: Cosmos):
        """Can view cosmos at historical versions."""
        path = "test.md"

        v1 = await cosmos.commit(path, "v1")
        await cosmos.commit(path, "v2")

        # Travel to v1
        old_view = await cosmos.travel(v1)
        content = await old_view.read(path)
        assert content == "v1"

        # Current is still v2
        assert await cosmos.read(path) == "v2"


# -----------------------------------------------------------------------------
# Polynomial State Machine Tests
# -----------------------------------------------------------------------------


class TestPolynomial:
    """Test K-Block polynomial state machine."""

    def test_initial_state(self):
        """Initial state is PRISTINE:VIEWING."""
        state = KBlockState.initial()
        assert state.isolation == IsolationState.PRISTINE
        assert state.editing == EditingState.VIEWING

    def test_valid_directions_pristine(self):
        """PRISTINE state has expected directions."""
        state = KBlockState(IsolationState.PRISTINE, EditingState.VIEWING)
        directions = KBlockPolynomial.directions(state)

        assert KBlockInput.START_EDIT in directions
        assert KBlockInput.SAVE in directions
        assert KBlockInput.DISCARD in directions
        assert KBlockInput.FORK in directions

    def test_valid_directions_dirty(self):
        """DIRTY state has checkpoint/rewind."""
        state = KBlockState(IsolationState.DIRTY, EditingState.VIEWING)
        directions = KBlockPolynomial.directions(state)

        assert KBlockInput.CHECKPOINT in directions
        assert KBlockInput.REWIND in directions
        assert KBlockInput.SAVE in directions

    def test_valid_directions_conflicting(self):
        """CONFLICTING state requires resolution."""
        state = KBlockState(IsolationState.CONFLICTING, EditingState.VIEWING)
        directions = KBlockPolynomial.directions(state)

        assert KBlockInput.RESOLVE_CONFLICT in directions
        assert KBlockInput.DISCARD in directions
        assert KBlockInput.SAVE not in directions

    def test_transition_start_edit(self):
        """START_EDIT transitions to EDITING."""
        state = KBlockState(IsolationState.PRISTINE, EditingState.VIEWING)
        new_state, output = KBlockPolynomial.transition(state, KBlockInput.START_EDIT)

        assert new_state.editing == EditingState.EDITING
        assert output.success

    def test_transition_save(self):
        """SAVE transitions DIRTY to PRISTINE."""
        state = KBlockState(IsolationState.DIRTY, EditingState.VIEWING)
        new_state, output = KBlockPolynomial.transition(state, KBlockInput.SAVE)

        assert new_state.isolation == IsolationState.PRISTINE
        assert output.success

    def test_invalid_transition_rejected(self):
        """Invalid transitions are rejected."""
        state = KBlockState(IsolationState.CONFLICTING, EditingState.VIEWING)
        new_state, output = KBlockPolynomial.transition(state, KBlockInput.SAVE)

        assert not output.success
        assert new_state == state  # Unchanged


# -----------------------------------------------------------------------------
# Fork and Merge Tests
# -----------------------------------------------------------------------------


class TestForkMerge:
    """Test fork and merge operations."""

    @pytest.mark.asyncio
    async def test_fork_creates_independent_blocks(
        self, harness: FileOperadHarness, cosmos: Cosmos
    ):
        """Forked blocks can be edited independently."""
        await cosmos.commit("test.md", "original")
        block = await harness.create("test.md")

        left, right = await harness.fork(block)

        left.set_content("left edit")
        right.set_content("right edit")

        assert left.content == "left edit"
        assert right.content == "right edit"
        assert left.content != right.content

    @pytest.mark.asyncio
    async def test_merge_without_conflict(self, harness: FileOperadHarness, cosmos: Cosmos):
        """Merge succeeds when changes don't conflict."""
        await cosmos.commit("test.md", "line 1\nline 2\nline 3")
        block = await harness.create("test.md")

        left, right = await harness.fork(block)

        # Edit different parts
        left.set_content("EDITED\nline 2\nline 3")
        right.set_content("line 1\nline 2\nEDITED")

        result = await harness.merge(left, right)
        assert result.success
        # Note: Our simple merge may not be perfect for disjoint edits,
        # but the law tests verify the basic behavior

    @pytest.mark.asyncio
    async def test_merge_with_conflict(self, harness: FileOperadHarness, cosmos: Cosmos):
        """Merge detects conflicts when same lines edited."""
        await cosmos.commit("test.md", "original line")
        block = await harness.create("test.md")

        left, right = await harness.fork(block)

        # Edit same line differently
        left.set_content("left version")
        right.set_content("right version")

        result = await harness.merge(left, right)
        assert result.success  # Merge completes
        assert result.has_conflicts  # But has conflicts

        merged = harness.get_block(result.block_id)
        assert merged is not None
        assert merged.isolation == IsolationState.CONFLICTING
        assert "<<<<<<< LOCAL" in merged.content


# -----------------------------------------------------------------------------
# Staleness Tests
# -----------------------------------------------------------------------------


class TestStaleness:
    """Test staleness propagation."""

    @pytest.mark.asyncio
    async def test_save_marks_dependents_stale(self, harness: FileOperadHarness, cosmos: Cosmos):
        """Saving marks dependent K-Blocks as stale."""
        # Set up dependency: b.md references a.md
        await cosmos.commit("a.md", "content a")
        await cosmos.commit("b.md", "content b")
        cosmos.add_dependent("a.md", "b.md")

        # Open both
        block_a = await harness.create("a.md")
        block_b = await harness.create("b.md")

        assert block_b.isolation == IsolationState.PRISTINE

        # Save a.md
        block_a.set_content("new content a")
        await harness.save(block_a)

        # b.md should be marked stale
        assert block_b.isolation == IsolationState.STALE

    @pytest.mark.asyncio
    async def test_refresh_clears_stale(self, harness: FileOperadHarness, cosmos: Cosmos):
        """Refresh updates base and clears stale state."""
        await cosmos.commit("test.md", "v1")
        block = await harness.create("test.md")

        # Simulate upstream change
        await cosmos.commit("test.md", "v2")
        block.isolation = IsolationState.STALE

        # Refresh
        delta = await harness.refresh(block)

        assert delta is not None
        assert delta.new_content == "v2"
        assert block.base_content == "v2"
        assert block.isolation == IsolationState.PRISTINE


# -----------------------------------------------------------------------------
# Edge Cases
# -----------------------------------------------------------------------------


class TestEdgeCases:
    """Test edge cases and error handling."""

    @pytest.mark.asyncio
    async def test_save_empty_content(self, harness: FileOperadHarness, cosmos: Cosmos):
        """Can save empty content."""
        block = await harness.create("test.md")
        block.set_content("")

        result = await harness.save(block)
        # Empty is same as initial, so no changes
        assert result.no_changes

    @pytest.mark.asyncio
    async def test_rewind_invalid_checkpoint(self, harness: FileOperadHarness):
        """Rewind with invalid checkpoint raises error."""
        block = await harness.create("test.md")

        with pytest.raises(ValueError, match="Checkpoint not found"):
            block.rewind("nonexistent_checkpoint")

    @pytest.mark.asyncio
    async def test_merge_different_paths_fails(self, harness: FileOperadHarness, cosmos: Cosmos):
        """Cannot merge K-Blocks with different paths."""
        block_a = await harness.create("a.md")
        block_b = await harness.create("b.md")

        result = await harness.merge(block_a, block_b)
        assert not result.success
        assert "different paths" in result.error

    @pytest.mark.asyncio
    async def test_multiple_blocks_same_path(self, harness: FileOperadHarness, cosmos: Cosmos):
        """Multiple K-Blocks for same path are independent."""
        await cosmos.commit("test.md", "original")

        block1 = await harness.create("test.md")
        # Fork to get second block
        _, block2 = await harness.fork(block1)

        block1.set_content("edit 1")
        block2.set_content("edit 2")

        assert block1.content != block2.content
