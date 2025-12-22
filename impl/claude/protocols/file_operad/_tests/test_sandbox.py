"""
Tests for Sandbox Mode (Session 5).

"Sandbox mode treats file execution like a hypothesis—
test it in isolation before committing to reality."
"""

from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path

import pytest

from ..sandbox import (
    DEFAULT_SANDBOX_TTL,
    MAX_SANDBOX_TTL,
    InvalidTransitionError,
    SandboxConfig,
    SandboxEvent,
    SandboxId,
    SandboxPhase,
    SandboxPolynomial,
    SandboxResult,
    SandboxRuntime,
    SandboxStore,
    generate_sandbox_id,
    get_sandbox_store,
    is_terminal,
    reset_sandbox_store,
    sandbox_directions,
    transition_sandbox,
)

# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture(autouse=True)
def reset_store():
    """Reset global store before each test."""
    reset_sandbox_store()
    yield
    reset_sandbox_store()


@pytest.fixture
def sample_content() -> str:
    """Sample .op file content."""
    return """# mark: Record a Witness Trace

> "The proof IS the decision."

**Arity**: 1
**Symbol**: `⊙`

## Type Signature

```
mark : (Action, Reasoning, Evidence) -> Witness[Mark]
```
"""


@pytest.fixture
def sample_sandbox(sample_content: str) -> SandboxPolynomial:
    """Create a sample sandbox."""
    return SandboxPolynomial.create(
        source_path="WITNESS_OPERAD/mark.op",
        content=sample_content,
    )


@pytest.fixture
def store() -> SandboxStore:
    """Create a fresh SandboxStore."""
    return SandboxStore()


# =============================================================================
# SandboxPhase and State Machine Tests
# =============================================================================


class TestSandboxPhase:
    """Tests for SandboxPhase enum and state machine."""

    def test_phases_exist(self):
        """All required phases exist."""
        assert SandboxPhase.ACTIVE
        assert SandboxPhase.PROMOTED
        assert SandboxPhase.DISCARDED
        assert SandboxPhase.EXPIRED

    def test_is_terminal(self):
        """Terminal states are correctly identified."""
        assert not is_terminal(SandboxPhase.ACTIVE)
        assert is_terminal(SandboxPhase.PROMOTED)
        assert is_terminal(SandboxPhase.DISCARDED)
        assert is_terminal(SandboxPhase.EXPIRED)

    def test_directions_active(self):
        """ACTIVE phase allows all non-terminal operations."""
        directions = sandbox_directions(SandboxPhase.ACTIVE)
        assert SandboxEvent.EXECUTE in directions
        assert SandboxEvent.PROMOTE in directions
        assert SandboxEvent.DISCARD in directions
        assert SandboxEvent.EXTEND in directions
        assert SandboxEvent.EXPIRE in directions

    def test_directions_promoted(self):
        """PROMOTED phase only allows observe."""
        directions = sandbox_directions(SandboxPhase.PROMOTED)
        assert SandboxEvent.OBSERVE in directions
        assert len(directions) == 1

    def test_directions_discarded(self):
        """DISCARDED phase has no valid directions."""
        directions = sandbox_directions(SandboxPhase.DISCARDED)
        assert len(directions) == 0

    def test_directions_expired(self):
        """EXPIRED phase has no valid directions."""
        directions = sandbox_directions(SandboxPhase.EXPIRED)
        assert len(directions) == 0


class TestSandboxTransitions:
    """Tests for state transitions."""

    def test_promote_from_active(self, sample_sandbox):
        """Can promote from ACTIVE."""
        promoted = transition_sandbox(sample_sandbox, SandboxEvent.PROMOTE)
        assert promoted.phase == SandboxPhase.PROMOTED
        assert promoted.promoted_to == sample_sandbox.source_path

    def test_promote_with_destination(self, sample_sandbox):
        """Promotion can specify destination."""
        promoted = transition_sandbox(
            sample_sandbox,
            SandboxEvent.PROMOTE,
            destination="WITNESS_OPERAD/mark_v2.op",
        )
        assert promoted.promoted_to == "WITNESS_OPERAD/mark_v2.op"

    def test_discard_from_active(self, sample_sandbox):
        """Can discard from ACTIVE."""
        discarded = transition_sandbox(sample_sandbox, SandboxEvent.DISCARD)
        assert discarded.phase == SandboxPhase.DISCARDED

    def test_expire_from_active(self, sample_sandbox):
        """Can expire from ACTIVE."""
        expired = transition_sandbox(sample_sandbox, SandboxEvent.EXPIRE)
        assert expired.phase == SandboxPhase.EXPIRED

    def test_extend_from_active(self, sample_sandbox):
        """Can extend TTL from ACTIVE."""
        original_expires = sample_sandbox.expires_at
        extended = transition_sandbox(sample_sandbox, SandboxEvent.EXTEND, minutes=30)
        assert extended.expires_at > original_expires
        # Should add 30 minutes
        expected = original_expires + timedelta(minutes=30)
        assert abs((extended.expires_at - expected).total_seconds()) < 1

    def test_cannot_promote_promoted(self, sample_sandbox):
        """Cannot promote an already promoted sandbox."""
        promoted = transition_sandbox(sample_sandbox, SandboxEvent.PROMOTE)
        with pytest.raises(InvalidTransitionError):
            transition_sandbox(promoted, SandboxEvent.PROMOTE)

    def test_cannot_discard_promoted(self, sample_sandbox):
        """Cannot discard a promoted sandbox."""
        promoted = transition_sandbox(sample_sandbox, SandboxEvent.PROMOTE)
        with pytest.raises(InvalidTransitionError):
            transition_sandbox(promoted, SandboxEvent.DISCARD)

    def test_cannot_extend_discarded(self, sample_sandbox):
        """Cannot extend a discarded sandbox."""
        discarded = transition_sandbox(sample_sandbox, SandboxEvent.DISCARD)
        with pytest.raises(InvalidTransitionError):
            transition_sandbox(discarded, SandboxEvent.EXTEND)

    def test_execute_records_result(self, sample_sandbox):
        """Execute records the result."""
        result = SandboxResult(success=True, output="test output")
        executed = transition_sandbox(sample_sandbox, SandboxEvent.EXECUTE, result=result)
        assert len(executed.execution_results) == 1
        assert executed.execution_results[0].success is True
        assert executed.execution_results[0].output == "test output"


# =============================================================================
# SandboxPolynomial Tests
# =============================================================================


class TestSandboxPolynomial:
    """Tests for SandboxPolynomial dataclass."""

    def test_create_sandbox(self, sample_content):
        """Create a new sandbox."""
        sandbox = SandboxPolynomial.create(
            source_path="WITNESS_OPERAD/mark.op",
            content=sample_content,
        )

        assert sandbox.id.startswith("sandbox-")
        assert sandbox.source_path == "WITNESS_OPERAD/mark.op"
        assert sandbox.content == sample_content
        assert sandbox.original_content == sample_content
        assert sandbox.phase == SandboxPhase.ACTIVE
        assert sandbox.is_active

    def test_sandbox_is_frozen(self, sample_sandbox):
        """Sandbox is immutable (frozen dataclass)."""
        with pytest.raises(AttributeError):
            sample_sandbox.content = "modified"  # type: ignore

    def test_is_expired_check(self, sample_content):
        """Expiration check works correctly."""
        # Create with very short TTL
        config = SandboxConfig(timeout_seconds=0.001)
        sandbox = SandboxPolynomial.create(
            source_path="test.op",
            content=sample_content,
            config=config,
        )
        # Should be expired almost immediately
        import time

        time.sleep(0.01)
        assert sandbox.is_expired

    def test_time_remaining(self, sample_sandbox):
        """Time remaining is calculated correctly."""
        remaining = sample_sandbox.time_remaining
        # Should be close to 15 minutes
        assert remaining.total_seconds() > 800  # At least ~13 minutes
        assert remaining.total_seconds() < 910  # Less than ~15.2 minutes

    def test_has_modifications_false_initially(self, sample_sandbox):
        """No modifications initially."""
        assert not sample_sandbox.has_modifications

    def test_has_modifications_after_change(self, sample_content):
        """Detects modifications."""
        sandbox = SandboxPolynomial.create("test.op", sample_content)
        # Use replace to simulate content change
        from dataclasses import replace

        modified = replace(sandbox, content="modified content")
        assert modified.has_modifications

    def test_get_diff(self, sample_content):
        """Diff is generated correctly."""
        sandbox = SandboxPolynomial.create("test.op", sample_content)
        from dataclasses import replace

        modified = replace(sandbox, content="new content\n")

        diff = modified.get_diff()
        assert "---" in diff
        assert "+++" in diff
        assert "-# mark:" in diff or "+new content" in diff

    def test_valid_events(self, sample_sandbox):
        """valid_events returns correct events for phase."""
        events = sample_sandbox.valid_events()
        assert SandboxEvent.PROMOTE in events
        assert SandboxEvent.DISCARD in events

    def test_can_transition(self, sample_sandbox):
        """can_transition checks correctly."""
        assert sample_sandbox.can_transition(SandboxEvent.PROMOTE)
        assert not sample_sandbox.can_transition(SandboxEvent.OBSERVE)


# =============================================================================
# SandboxStore Tests
# =============================================================================


class TestSandboxStore:
    """Tests for SandboxStore."""

    def test_create_and_get(self, store, sample_content):
        """Create and retrieve a sandbox."""
        sandbox = store.create("test.op", sample_content)
        retrieved = store.get(sandbox.id)

        assert retrieved is not None
        assert retrieved.id == sandbox.id
        assert retrieved.content == sample_content

    def test_create_increments_count(self, store, sample_content):
        """Creating sandboxes increments count."""
        assert len(store) == 0
        store.create("test1.op", sample_content)
        assert len(store) == 1
        store.create("test2.op", sample_content)
        assert len(store) == 2

    def test_get_nonexistent_returns_none(self, store):
        """Getting nonexistent sandbox returns None."""
        result = store.get(SandboxId("nonexistent"))
        assert result is None

    def test_list_active(self, store, sample_content):
        """List only active sandboxes."""
        sb1 = store.create("test1.op", sample_content)
        sb2 = store.create("test2.op", sample_content)

        # Discard one
        store.discard(sb2.id)

        active = store.list_active()
        assert len(active) == 1
        assert active[0].id == sb1.id

    def test_list_all(self, store, sample_content):
        """List all sandboxes including non-active."""
        sb1 = store.create("test1.op", sample_content)
        sb2 = store.create("test2.op", sample_content)
        store.discard(sb2.id)

        all_sandboxes = store.list_all()
        assert len(all_sandboxes) == 2

    def test_promote(self, store, sample_content):
        """Promote a sandbox."""
        sandbox = store.create("test.op", sample_content)
        promoted = store.promote(sandbox.id)

        assert promoted.phase == SandboxPhase.PROMOTED
        # Store should be updated
        retrieved = store.get(sandbox.id)
        assert retrieved.phase == SandboxPhase.PROMOTED

    def test_discard(self, store, sample_content):
        """Discard a sandbox."""
        sandbox = store.create("test.op", sample_content)
        discarded = store.discard(sandbox.id)

        assert discarded.phase == SandboxPhase.DISCARDED

    def test_extend(self, store, sample_content):
        """Extend a sandbox's TTL."""
        sandbox = store.create("test.op", sample_content)
        original_expires = sandbox.expires_at

        extended = store.extend(sandbox.id, minutes=30)

        assert extended.expires_at > original_expires

    def test_update_content(self, store, sample_content):
        """Update sandbox content."""
        sandbox = store.create("test.op", sample_content)
        updated = store.update_content(sandbox.id, "new content")

        assert updated.content == "new content"
        assert updated.has_modifications

    def test_cleanup_expired(self, store):
        """Cleanup removes expired sandboxes."""
        config = SandboxConfig(timeout_seconds=0.001)
        sb1 = store.create("test1.op", "content", config)
        sb2 = store.create("test2.op", "content", config)

        import time

        time.sleep(0.02)

        # Cleanup should remove expired
        count = store.cleanup_expired()
        assert count == 2
        assert len(store) == 0

    def test_auto_expire_on_get(self, store):
        """Sandbox auto-expires when retrieved after TTL."""
        config = SandboxConfig(timeout_seconds=0.001)
        sandbox = store.create("test.op", "content", config)

        import time

        time.sleep(0.02)

        # Get should transition to EXPIRED
        retrieved = store.get(sandbox.id)
        assert retrieved.phase == SandboxPhase.EXPIRED


# =============================================================================
# Global Store Tests
# =============================================================================


class TestGlobalStore:
    """Tests for global store functions."""

    def test_get_global_store_singleton(self):
        """Global store is a singleton."""
        store1 = get_sandbox_store()
        store2 = get_sandbox_store()
        assert store1 is store2

    def test_reset_clears_store(self):
        """Reset creates a new store."""
        store1 = get_sandbox_store()
        store1.create("test.op", "content")
        assert len(store1) == 1

        reset_sandbox_store()
        store2 = get_sandbox_store()
        assert len(store2) == 0
        assert store1 is not store2


# =============================================================================
# SandboxConfig Tests
# =============================================================================


class TestSandboxConfig:
    """Tests for SandboxConfig."""

    def test_default_config(self):
        """Default config has sensible values."""
        config = SandboxConfig()
        assert config.runtime == SandboxRuntime.NATIVE
        assert config.timeout_seconds == DEFAULT_SANDBOX_TTL.total_seconds()

    def test_custom_config(self):
        """Custom config is applied."""
        config = SandboxConfig(
            timeout_seconds=60,
            runtime=SandboxRuntime.JIT_GENT,
            allowed_imports=frozenset({"json"}),
        )
        assert config.timeout_seconds == 60
        assert config.runtime == SandboxRuntime.JIT_GENT
        assert "json" in config.allowed_imports

    def test_ttl_property(self):
        """TTL property returns timedelta."""
        config = SandboxConfig(timeout_seconds=120)
        assert config.ttl == timedelta(minutes=2)


# =============================================================================
# SandboxResult Tests
# =============================================================================


class TestSandboxResult:
    """Tests for SandboxResult."""

    def test_success_result(self):
        """Create a success result."""
        result = SandboxResult(success=True, output="test")
        assert result.success
        assert result.output == "test"
        assert result.error is None

    def test_error_result(self):
        """Create an error result."""
        result = SandboxResult(success=False, error="Something went wrong")
        assert not result.success
        assert result.error == "Something went wrong"

    def test_result_with_stdout(self):
        """Result captures stdout/stderr."""
        result = SandboxResult(
            success=True,
            output=42,
            stdout="printed output",
            stderr="warning message",
        )
        assert result.stdout == "printed output"
        assert result.stderr == "warning message"


# =============================================================================
# Persistence Tests
# =============================================================================


class TestSandboxPersistence:
    """Tests for SandboxStore persistence."""

    def test_save_and_load_roundtrip(self, store, sample_content, tmp_path):
        """Save and load preserves all sandbox data."""
        persistence_file = tmp_path / "sandboxes.json"
        store.set_persistence_path(persistence_file)

        # Create some sandboxes
        sb1 = store.create("test1.op", sample_content)
        sb2 = store.create("test2.op", "other content")

        # Promote one
        store.promote(sb2.id, "promoted.op")

        # Save
        store.save()
        assert persistence_file.exists()

        # Load into new store
        loaded = SandboxStore.load(persistence_file)

        assert len(loaded) == 2

        loaded1 = loaded.get(sb1.id)
        assert loaded1 is not None
        assert loaded1.source_path == "test1.op"
        assert loaded1.phase == SandboxPhase.ACTIVE

        loaded2 = loaded.get(sb2.id)
        assert loaded2 is not None
        assert loaded2.phase == SandboxPhase.PROMOTED
        assert loaded2.promoted_to == "promoted.op"

    def test_load_or_create_new(self, tmp_path):
        """load_or_create creates new store if file doesn't exist."""
        persistence_file = tmp_path / "nonexistent.json"
        store = SandboxStore.load_or_create(persistence_file)

        assert len(store) == 0
        assert store.persistence_path == persistence_file

    def test_load_or_create_existing(self, tmp_path, sample_content):
        """load_or_create loads from existing file."""
        persistence_file = tmp_path / "existing.json"

        # Create and save
        store1 = SandboxStore()
        store1.create("test.op", sample_content)
        store1.save(persistence_file)

        # Load via load_or_create
        store2 = SandboxStore.load_or_create(persistence_file)
        assert len(store2) == 1

    def test_sync(self, tmp_path, sample_content):
        """sync() saves to persistence path."""
        persistence_file = tmp_path / "sync_test.json"

        store = SandboxStore()
        store.set_persistence_path(persistence_file)
        store.create("test.op", sample_content)

        result = store.sync()
        assert result == persistence_file
        assert persistence_file.exists()

    def test_sync_without_path_returns_none(self):
        """sync() returns None if no persistence path."""
        store = SandboxStore()
        store.create("test.op", "content")

        assert store.sync() is None


# =============================================================================
# ID Generation Tests
# =============================================================================


class TestSandboxId:
    """Tests for sandbox ID generation."""

    def test_generate_sandbox_id(self):
        """Generated IDs have correct format."""
        id1 = generate_sandbox_id()
        assert id1.startswith("sandbox-")
        assert len(id1) == 20  # "sandbox-" + 12 hex chars

    def test_ids_are_unique(self):
        """Generated IDs are unique."""
        ids = {generate_sandbox_id() for _ in range(100)}
        assert len(ids) == 100


# =============================================================================
# Integration Tests
# =============================================================================


class TestSandboxIntegration:
    """Integration tests for sandbox workflow."""

    def test_full_workflow_promote(self, store, sample_content):
        """Full workflow: create → modify → promote."""
        # Create
        sandbox = store.create("test.op", sample_content)
        assert sandbox.is_active

        # Modify
        store.update_content(sandbox.id, "modified content")
        updated = store.get(sandbox.id)
        assert updated.has_modifications

        # Get diff
        diff = updated.get_diff()
        assert diff  # Should have diff

        # Promote
        promoted = store.promote(sandbox.id, "test_v2.op")
        assert promoted.phase == SandboxPhase.PROMOTED
        assert promoted.promoted_to == "test_v2.op"

    def test_full_workflow_discard(self, store, sample_content):
        """Full workflow: create → modify → discard."""
        # Create
        sandbox = store.create("test.op", sample_content)

        # Modify
        store.update_content(sandbox.id, "modified content")

        # Discard (modifications lost)
        discarded = store.discard(sandbox.id)
        assert discarded.phase == SandboxPhase.DISCARDED

    def test_multiple_executions(self, store, sample_content):
        """Multiple executions are recorded."""
        sandbox = store.create("test.op", sample_content)

        # Execute multiple times
        result1 = SandboxResult(success=True, output="run1")
        result2 = SandboxResult(success=True, output="run2")
        result3 = SandboxResult(success=False, error="failed")

        sandbox = transition_sandbox(sandbox, SandboxEvent.EXECUTE, result=result1)
        sandbox = transition_sandbox(sandbox, SandboxEvent.EXECUTE, result=result2)
        sandbox = transition_sandbox(sandbox, SandboxEvent.EXECUTE, result=result3)

        assert len(sandbox.execution_results) == 3
        assert sandbox.execution_results[0].output == "run1"
        assert sandbox.execution_results[2].success is False

    def test_extend_caps_at_max_ttl(self, store, sample_content):
        """Extension is capped at MAX_SANDBOX_TTL."""
        sandbox = store.create("test.op", sample_content)

        # Try to extend way past max
        extended = store.extend(sandbox.id, minutes=500)

        # Should be capped at max TTL from creation
        max_allowed = sandbox.created_at + MAX_SANDBOX_TTL
        assert extended.expires_at <= max_allowed
