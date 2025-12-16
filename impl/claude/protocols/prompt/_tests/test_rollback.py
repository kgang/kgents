"""
Tests for the Rollback Registry.

Verifies the category law:
    rollback(checkpoint(p)) == p  # Invertibility

Also tests:
- Checkpoint creation and storage
- History browsing
- Diff computation
- Forward history preservation
"""

from datetime import datetime, timedelta

import pytest
from protocols.prompt.rollback import (
    Checkpoint,
    CheckpointId,
    CheckpointSummary,
    RollbackRegistry,
)
from protocols.prompt.rollback.storage import InMemoryCheckpointStorage

# =============================================================================
# Checkpoint Tests
# =============================================================================


class TestCheckpoint:
    """Tests for the Checkpoint dataclass."""

    def test_create_checkpoint(self):
        """Creating a checkpoint computes ID and diff."""
        checkpoint = Checkpoint.create(
            before_content="Hello world",
            after_content="Hello universe",
            before_sections=("intro",),
            after_sections=("intro",),
            reason="Expanded scope",
        )

        assert checkpoint.id is not None
        assert len(checkpoint.id) == 16  # SHA-256 truncated to 16 chars
        assert checkpoint.before_content == "Hello world"
        assert checkpoint.after_content == "Hello universe"
        assert checkpoint.reason == "Expanded scope"
        assert "world" in checkpoint.diff
        assert "universe" in checkpoint.diff

    def test_checkpoint_id_deterministic(self):
        """Same inputs produce same ID (at same timestamp)."""
        # Note: timestamps differ, so IDs will differ
        # This tests that the ID is based on content
        cp1 = Checkpoint.create(
            before_content="A",
            after_content="B",
            before_sections=(),
            after_sections=(),
            reason="test",
        )
        cp2 = Checkpoint.create(
            before_content="A",
            after_content="B",
            before_sections=(),
            after_sections=(),
            reason="test",
        )

        # IDs differ due to different timestamps
        # But generate_id with same timestamp is deterministic
        ts = datetime.now()
        id1 = Checkpoint.generate_id("A", "B", "test", ts)
        id2 = Checkpoint.generate_id("A", "B", "test", ts)
        assert id1 == id2

    def test_checkpoint_diff(self):
        """Diff computation produces unified diff."""
        diff = Checkpoint.compute_diff(
            "line1\nline2\nline3",
            "line1\nmodified\nline3",
        )

        assert "-line2" in diff
        assert "+modified" in diff

    def test_checkpoint_serialization(self):
        """Checkpoint can be serialized and deserialized."""
        original = Checkpoint.create(
            before_content="Before",
            after_content="After",
            before_sections=("a", "b"),
            after_sections=("a", "b", "c"),
            reason="Added section c",
            reasoning_traces=("Step 1", "Step 2"),
        )

        # Serialize
        data = original.to_dict()
        assert data["id"] == original.id
        assert data["reason"] == "Added section c"
        assert data["reasoning_traces"] == ["Step 1", "Step 2"]

        # Deserialize
        restored = Checkpoint.from_dict(data)
        assert restored.id == original.id
        assert restored.before_content == original.before_content
        assert restored.after_content == original.after_content
        assert restored.reasoning_traces == original.reasoning_traces

    def test_checkpoint_summary(self):
        """Summary provides lightweight view."""
        checkpoint = Checkpoint.create(
            before_content="Short",
            after_content="Much longer content here",
            before_sections=("a",),
            after_sections=("a", "b"),
            reason="Expanded content",
        )

        summary = checkpoint.summary()
        assert summary.id == checkpoint.id
        assert summary.reason == "Expanded content"
        assert summary.before_token_count < summary.after_token_count

    def test_summary_str(self):
        """Summary string is readable."""
        checkpoint = Checkpoint.create(
            before_content="A" * 100,
            after_content="B" * 200,
            before_sections=("x",),
            after_sections=("x", "y"),
            reason="Test change",
        )

        summary_str = str(checkpoint.summary())
        assert checkpoint.id[:8] in summary_str
        assert "Test change" in summary_str


# =============================================================================
# Storage Tests
# =============================================================================


class TestInMemoryStorage:
    """Tests for in-memory checkpoint storage."""

    def test_save_and_load(self):
        """Can save and load checkpoints."""
        storage = InMemoryCheckpointStorage()

        checkpoint = Checkpoint.create(
            before_content="A",
            after_content="B",
            before_sections=(),
            after_sections=(),
            reason="test",
        )

        storage.save(checkpoint)
        loaded = storage.load(checkpoint.id)

        assert loaded is not None
        assert loaded.id == checkpoint.id
        assert loaded.before_content == "A"
        assert loaded.after_content == "B"

    def test_list_summaries(self):
        """Summaries are listed most recent first."""
        storage = InMemoryCheckpointStorage()

        # Save multiple checkpoints
        for i in range(5):
            checkpoint = Checkpoint.create(
                before_content=f"Before {i}",
                after_content=f"After {i}",
                before_sections=(),
                after_sections=(),
                reason=f"Change {i}",
            )
            storage.save(checkpoint)

        summaries = storage.list_summaries(limit=3)
        assert len(summaries) == 3
        # Most recent should be "Change 4"
        assert "Change 4" in summaries[0].reason

    def test_exists(self):
        """Exists check works."""
        storage = InMemoryCheckpointStorage()

        checkpoint = Checkpoint.create(
            before_content="A",
            after_content="B",
            before_sections=(),
            after_sections=(),
            reason="test",
        )

        assert not storage.exists(checkpoint.id)
        storage.save(checkpoint)
        assert storage.exists(checkpoint.id)

    def test_get_latest_id(self):
        """Can get most recent checkpoint ID."""
        storage = InMemoryCheckpointStorage()

        assert storage.get_latest_id() is None

        checkpoint = Checkpoint.create(
            before_content="A",
            after_content="B",
            before_sections=(),
            after_sections=(),
            reason="test",
        )
        storage.save(checkpoint)

        assert storage.get_latest_id() == checkpoint.id


# =============================================================================
# Registry Tests
# =============================================================================


class TestRollbackRegistry:
    """Tests for the RollbackRegistry."""

    @pytest.fixture
    def registry(self):
        """Create a registry with in-memory storage."""
        storage = InMemoryCheckpointStorage()
        return RollbackRegistry(storage=storage)

    def test_checkpoint_creates_entry(self, registry):
        """Checkpointing creates a new entry."""
        checkpoint_id = registry.checkpoint(
            before_content="Original",
            after_content="Modified",
            before_sections=("a",),
            after_sections=("a",),
            reason="First change",
        )

        assert checkpoint_id is not None
        assert len(registry) == 1

    def test_history_shows_entries(self, registry):
        """History shows checkpoint summaries."""
        registry.checkpoint(
            before_content="V1",
            after_content="V2",
            before_sections=(),
            after_sections=(),
            reason="Change 1",
        )
        registry.checkpoint(
            before_content="V2",
            after_content="V3",
            before_sections=(),
            after_sections=(),
            reason="Change 2",
        )

        history = registry.history(limit=10)
        assert len(history) == 2
        # Most recent first
        assert "Change 2" in history[0].reason

    def test_get_checkpoint(self, registry):
        """Can retrieve full checkpoint by ID."""
        checkpoint_id = registry.checkpoint(
            before_content="Before",
            after_content="After",
            before_sections=("x",),
            after_sections=("x", "y"),
            reason="Test",
            reasoning_traces=("Trace 1", "Trace 2"),
        )

        checkpoint = registry.get_checkpoint(checkpoint_id)
        assert checkpoint is not None
        assert checkpoint.before_content == "Before"
        assert checkpoint.after_content == "After"
        assert "Trace 1" in checkpoint.reasoning_traces

    def test_diff_between_checkpoints(self, registry):
        """Can compute diff between checkpoints."""
        id1 = registry.checkpoint(
            before_content="A",
            after_content="Version 1",
            before_sections=(),
            after_sections=(),
            reason="First",
        )
        id2 = registry.checkpoint(
            before_content="Version 1",
            after_content="Version 2",
            before_sections=(),
            after_sections=(),
            reason="Second",
        )

        diff = registry.diff(id1, id2)
        assert diff is not None
        assert "Version 1" in diff
        assert "Version 2" in diff


# =============================================================================
# Category Law Tests: Invertibility
# =============================================================================


class TestInvertibilityLaw:
    """
    Tests for the invertibility law:
        rollback(checkpoint(p)) == p

    This is the core category law for the rollback system.
    """

    @pytest.fixture
    def registry(self):
        """Create a registry with in-memory storage."""
        storage = InMemoryCheckpointStorage()
        return RollbackRegistry(storage=storage)

    def test_rollback_restores_content(self, registry):
        """rollback(checkpoint(p)) restores original content."""
        original_content = "This is the original prompt content."
        modified_content = "This is the modified content."

        # Set current state
        registry.set_current(original_content, ("section1",))

        # Create checkpoint (original -> modified)
        checkpoint_id = registry.checkpoint(
            before_content=original_content,
            after_content=modified_content,
            before_sections=("section1",),
            after_sections=("section1",),
            reason="Test modification",
        )

        # Rollback should restore original
        result = registry.rollback(checkpoint_id)

        assert result.success
        assert result.restored_content == original_content
        assert "Rolled back" in result.message

    def test_rollback_preserves_forward_history(self, registry):
        """Rolling back does NOT delete forward history."""
        # Create chain: V1 -> V2 -> V3
        registry.set_current("V1", ())
        id1 = registry.checkpoint(
            before_content="V1",
            after_content="V2",
            before_sections=(),
            after_sections=(),
            reason="V1 to V2",
        )
        id2 = registry.checkpoint(
            before_content="V2",
            after_content="V3",
            before_sections=(),
            after_sections=(),
            reason="V2 to V3",
        )

        # Roll back to id1
        result = registry.rollback(id1)
        assert result.success

        # History should now have 3 entries:
        # Original 2 + 1 for the rollback
        history = registry.history(limit=10)
        assert len(history) == 3

        # The rollback should be recorded
        assert any("Rollback" in h.reason for h in history)

    def test_multiple_rollbacks_work(self, registry):
        """Can rollback multiple times."""
        registry.set_current("Start", ())

        # Create chain
        id1 = registry.checkpoint(
            before_content="Start",
            after_content="V1",
            before_sections=(),
            after_sections=(),
            reason="To V1",
        )
        id2 = registry.checkpoint(
            before_content="V1",
            after_content="V2",
            before_sections=(),
            after_sections=(),
            reason="To V2",
        )

        # Rollback to V1
        result1 = registry.rollback(id2)
        assert result1.success
        assert result1.restored_content == "V1"

        # Rollback to Start
        result2 = registry.rollback(id1)
        assert result2.success
        assert result2.restored_content == "Start"

    def test_rollback_nonexistent_checkpoint(self, registry):
        """Rollback to nonexistent checkpoint fails gracefully."""
        result = registry.rollback(CheckpointId("nonexistent123"))

        assert not result.success
        assert "not found" in result.message.lower()

    def test_rollback_with_reasoning_traces(self, registry):
        """Rollback includes reasoning traces."""
        registry.set_current("Original", ())

        checkpoint_id = registry.checkpoint(
            before_content="Original",
            after_content="Modified",
            before_sections=(),
            after_sections=(),
            reason="Test change",
            reasoning_traces=("Step 1", "Step 2"),
        )

        result = registry.rollback(checkpoint_id)

        assert result.success
        assert len(result.reasoning_trace) > 0
        assert any("Rolling back" in t for t in result.reasoning_trace)


# =============================================================================
# Property-Based Tests (if hypothesis is available)
# =============================================================================


class TestJSONCheckpointStorage:
    """Tests for JSON file storage."""

    def test_save_and_load_to_disk(self, tmp_path):
        """Can save and load checkpoints from disk."""
        from protocols.prompt.rollback.storage import JSONCheckpointStorage

        storage = JSONCheckpointStorage(tmp_path / "checkpoints")

        checkpoint = Checkpoint.create(
            before_content="Disk test before",
            after_content="Disk test after",
            before_sections=("a",),
            after_sections=("a", "b"),
            reason="Test disk storage",
        )

        storage.save(checkpoint)

        # Verify file was created
        checkpoint_path = (
            tmp_path / "checkpoints" / "checkpoints" / f"{checkpoint.id}.json"
        )
        assert checkpoint_path.exists()

        # Load and verify
        loaded = storage.load(checkpoint.id)
        assert loaded is not None
        assert loaded.before_content == "Disk test before"
        assert loaded.after_content == "Disk test after"

    def test_prune_removes_old_checkpoints(self, tmp_path):
        """Prune removes old checkpoints while keeping recent ones."""
        from protocols.prompt.rollback.storage import JSONCheckpointStorage

        storage = JSONCheckpointStorage(tmp_path / "checkpoints")

        # Create 5 checkpoints
        checkpoint_ids = []
        for i in range(5):
            checkpoint = Checkpoint.create(
                before_content=f"V{i}",
                after_content=f"V{i + 1}",
                before_sections=(),
                after_sections=(),
                reason=f"Change {i}",
            )
            storage.save(checkpoint)
            checkpoint_ids.append(checkpoint.id)

        assert storage.count() == 5

        # Prune to keep only 3
        removed = storage.prune(keep_count=3)
        assert removed == 2
        assert storage.count() == 3

        # Oldest should be gone
        assert storage.load(checkpoint_ids[0]) is None
        assert storage.load(checkpoint_ids[1]) is None

        # Recent should still exist
        assert storage.load(checkpoint_ids[2]) is not None
        assert storage.load(checkpoint_ids[3]) is not None
        assert storage.load(checkpoint_ids[4]) is not None

    def test_prune_noop_when_below_limit(self, tmp_path):
        """Prune does nothing when count is below limit."""
        from protocols.prompt.rollback.storage import JSONCheckpointStorage

        storage = JSONCheckpointStorage(tmp_path / "checkpoints")

        # Create 2 checkpoints
        for i in range(2):
            checkpoint = Checkpoint.create(
                before_content=f"V{i}",
                after_content=f"V{i + 1}",
                before_sections=(),
                after_sections=(),
                reason=f"Change {i}",
            )
            storage.save(checkpoint)

        # Prune with limit higher than count
        removed = storage.prune(keep_count=10)
        assert removed == 0
        assert storage.count() == 2


try:
    from hypothesis import given
    from hypothesis import strategies as st

    class TestRollbackProperties:
        """Property-based tests for rollback system."""

        @given(
            before=st.text(min_size=1, max_size=1000),
            after=st.text(min_size=1, max_size=1000),
            reason=st.text(min_size=1, max_size=100),
        )
        def test_checkpoint_roundtrip(self, before, after, reason):
            """Any content can be checkpointed and retrieved."""
            # Create fresh registry for each property test
            storage = InMemoryCheckpointStorage()
            registry = RollbackRegistry(storage=storage)
            registry.set_current(before, ())

            checkpoint_id = registry.checkpoint(
                before_content=before,
                after_content=after,
                before_sections=(),
                after_sections=(),
                reason=reason,
            )

            checkpoint = registry.get_checkpoint(checkpoint_id)
            assert checkpoint is not None
            assert checkpoint.before_content == before
            assert checkpoint.after_content == after

except ImportError:
    # hypothesis not installed, skip property tests
    pass


__all__ = [
    "TestCheckpoint",
    "TestInMemoryStorage",
    "TestRollbackRegistry",
    "TestInvertibilityLaw",
]
