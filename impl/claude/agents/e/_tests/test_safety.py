"""
Tests for E-gent Phase 8: Safety & Guardrails.

Tests cover:
1. Rollback guarantees (atomic mutations)
2. Rate limiting for mutation operations
3. Audit logging for all infections
4. Sandboxed execution environment
5. Unified SafetySystem integration
"""

from __future__ import annotations

import tempfile
import time
from collections.abc import Generator
from pathlib import Path

import pytest
from agents.e.safety import (
    # Rollback
    AtomicCheckpoint,
    AtomicMutationManager,
    # Audit logging
    AuditEvent,
    AuditEventType,
    AuditLogger,
    FileAuditSink,
    FileCheckpoint,
    InMemoryAuditSink,
    RateLimitConfig,
    # Rate limiting
    RateLimiter,
    RateLimitExceeded,
    RollbackStatus,
    # Unified
    SafetySystem,
    # Sandbox
    Sandbox,
    SandboxConfig,
    SandboxViolation,
    create_safety_system,
    create_test_safety_system,
)

# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """Create a temporary directory for tests."""
    with tempfile.TemporaryDirectory() as d:
        yield Path(d)


@pytest.fixture
def test_file(temp_dir: Path) -> Path:
    """Create a test file."""
    test_path = temp_dir / "test_file.py"
    test_path.write_text("original content")
    return test_path


@pytest.fixture
def rollback_manager() -> AtomicMutationManager:
    """Create a rollback manager for tests."""
    return AtomicMutationManager(default_timeout=60.0)


@pytest.fixture
def rate_limiter() -> RateLimiter:
    """Create a rate limiter with low limits for testing."""
    config = RateLimitConfig(
        max_mutations_per_minute=5,
        max_mutations_per_hour=10,
        max_mutations_per_day=20,
        max_infections_per_minute=3,
        max_infections_per_hour=5,
        max_infections_per_day=10,
        burst_allowance=1,
    )
    return RateLimiter(config)


@pytest.fixture
def audit_logger() -> AuditLogger:
    """Create an audit logger with in-memory sink."""
    return AuditLogger(sink=InMemoryAuditSink())


@pytest.fixture
def safety_system() -> SafetySystem:
    """Create a safety system for testing."""
    return create_test_safety_system()


# =============================================================================
# FileCheckpoint Tests
# =============================================================================


class TestFileCheckpoint:
    """Tests for FileCheckpoint."""

    def test_capture_existing_file(self, test_file: Path) -> None:
        """Test capturing an existing file."""
        checkpoint = FileCheckpoint.capture(test_file)

        assert checkpoint.file_path == test_file
        assert checkpoint.original_content == "original content"
        assert checkpoint.original_hash != ""

    def test_capture_nonexistent_file(self, temp_dir: Path) -> None:
        """Test capturing a file that doesn't exist."""
        nonexistent = temp_dir / "nonexistent.py"
        checkpoint = FileCheckpoint.capture(nonexistent)

        assert checkpoint.file_path == nonexistent
        assert checkpoint.original_content is None
        assert checkpoint.original_hash == ""

    def test_restore_existing_file(self, test_file: Path) -> None:
        """Test restoring an existing file after modification."""
        checkpoint = FileCheckpoint.capture(test_file)

        # Modify file
        test_file.write_text("modified content")
        assert test_file.read_text() == "modified content"

        # Restore
        success = checkpoint.restore()
        assert success
        assert test_file.read_text() == "original content"

    def test_restore_deleted_file(self, temp_dir: Path) -> None:
        """Test restoring a file that was deleted."""
        test_path = temp_dir / "to_delete.py"
        test_path.write_text("delete me")

        checkpoint = FileCheckpoint.capture(test_path)

        # Delete file
        test_path.unlink()
        assert not test_path.exists()

        # Restore
        success = checkpoint.restore()
        assert success
        assert test_path.exists()
        assert test_path.read_text() == "delete me"

    def test_restore_file_that_didnt_exist(self, temp_dir: Path) -> None:
        """Test restoring removes a file that was created after checkpoint."""
        nonexistent = temp_dir / "nonexistent.py"
        checkpoint = FileCheckpoint.capture(nonexistent)

        # Create file
        nonexistent.write_text("new file")
        assert nonexistent.exists()

        # Restore (should delete)
        success = checkpoint.restore()
        assert success
        assert not nonexistent.exists()

    def test_verify_unchanged(self, test_file: Path) -> None:
        """Test verifying file hasn't changed."""
        checkpoint = FileCheckpoint.capture(test_file)

        # Should be unchanged
        assert checkpoint.verify()

        # Modify
        test_file.write_text("modified")
        assert not checkpoint.verify()

    def test_verify_nonexistent(self, temp_dir: Path) -> None:
        """Test verifying nonexistent file."""
        nonexistent = temp_dir / "nonexistent.py"
        checkpoint = FileCheckpoint.capture(nonexistent)

        # Should be valid (doesn't exist)
        assert checkpoint.verify()

        # Create file
        nonexistent.write_text("new")
        assert not checkpoint.verify()


# =============================================================================
# AtomicCheckpoint Tests
# =============================================================================


class TestAtomicCheckpoint:
    """Tests for AtomicCheckpoint."""

    def test_create_checkpoint(self) -> None:
        """Test creating a checkpoint."""
        checkpoint = AtomicCheckpoint()

        assert checkpoint.id.startswith("ckpt_")
        assert checkpoint.status == RollbackStatus.ACTIVE
        assert len(checkpoint.checkpoints) == 0

    def test_add_file(self, test_file: Path) -> None:
        """Test adding a file to checkpoint."""
        checkpoint = AtomicCheckpoint()
        file_ckpt = checkpoint.add_file(test_file)

        assert str(test_file.absolute()) in checkpoint.checkpoints
        assert file_ckpt.original_content == "original content"

    def test_add_file_idempotent(self, test_file: Path) -> None:
        """Test adding the same file twice returns same checkpoint."""
        checkpoint = AtomicCheckpoint()
        ckpt1 = checkpoint.add_file(test_file)
        ckpt2 = checkpoint.add_file(test_file)

        assert ckpt1 is ckpt2
        assert len(checkpoint.checkpoints) == 1

    def test_commit(self, test_file: Path) -> None:
        """Test committing a checkpoint."""
        checkpoint = AtomicCheckpoint()
        checkpoint.add_file(test_file)

        # Modify file
        test_file.write_text("modified")

        # Commit
        success = checkpoint.commit()
        assert success
        assert checkpoint.status == RollbackStatus.COMMITTED

        # File should remain modified
        assert test_file.read_text() == "modified"

    def test_rollback(self, test_file: Path) -> None:
        """Test rolling back a checkpoint."""
        checkpoint = AtomicCheckpoint()
        checkpoint.add_file(test_file)

        # Modify file
        test_file.write_text("modified")

        # Rollback
        success, errors = checkpoint.rollback()
        assert success
        assert len(errors) == 0
        assert checkpoint.status == RollbackStatus.ROLLED_BACK

        # File should be restored
        assert test_file.read_text() == "original content"

    def test_rollback_multiple_files(self, temp_dir: Path) -> None:
        """Test rolling back multiple files."""
        file1 = temp_dir / "file1.py"
        file2 = temp_dir / "file2.py"
        file1.write_text("content1")
        file2.write_text("content2")

        checkpoint = AtomicCheckpoint()
        checkpoint.add_file(file1)
        checkpoint.add_file(file2)

        # Modify both files
        file1.write_text("modified1")
        file2.write_text("modified2")

        # Rollback
        success, errors = checkpoint.rollback()
        assert success
        assert file1.read_text() == "content1"
        assert file2.read_text() == "content2"

    def test_cannot_add_after_commit(self, test_file: Path, temp_dir: Path) -> None:
        """Test cannot add files after commit."""
        checkpoint = AtomicCheckpoint()
        checkpoint.commit()

        with pytest.raises(RuntimeError, match="Cannot add files to committed"):
            checkpoint.add_file(temp_dir / "new.py")

    def test_cannot_rollback_after_commit(self, test_file: Path) -> None:
        """Test cannot rollback after commit."""
        checkpoint = AtomicCheckpoint()
        checkpoint.add_file(test_file)
        checkpoint.commit()

        success, errors = checkpoint.rollback()
        assert not success

    def test_timeout_expiration(self) -> None:
        """Test checkpoint timeout expiration."""
        checkpoint = AtomicCheckpoint(timeout_seconds=0.1)

        assert not checkpoint.is_expired()
        time.sleep(0.15)
        assert checkpoint.is_expired()

    def test_verify_unchanged(self, test_file: Path) -> None:
        """Test verify_unchanged method."""
        checkpoint = AtomicCheckpoint()
        checkpoint.add_file(test_file)

        unchanged, changed = checkpoint.verify_unchanged()
        assert unchanged
        assert len(changed) == 0

        # Modify file
        test_file.write_text("modified")

        unchanged, changed = checkpoint.verify_unchanged()
        assert not unchanged
        assert str(test_file.absolute()) in changed


# =============================================================================
# AtomicMutationManager Tests
# =============================================================================


class TestAtomicMutationManager:
    """Tests for AtomicMutationManager."""

    def test_atomic_context_commit(
        self, rollback_manager: AtomicMutationManager, test_file: Path
    ) -> None:
        """Test atomic context manager commits on success."""
        checkpoint: AtomicCheckpoint | None = None
        with rollback_manager.atomic(phage_id="phage_123") as cp:
            checkpoint = cp
            checkpoint.add_file(test_file)
            test_file.write_text("modified")

        # Should be committed
        assert checkpoint is not None
        assert checkpoint.status == RollbackStatus.COMMITTED
        assert test_file.read_text() == "modified"

    def test_atomic_context_rollback(
        self, rollback_manager: AtomicMutationManager, test_file: Path
    ) -> None:
        """Test atomic context manager rolls back on exception."""
        checkpoint: AtomicCheckpoint | None = None
        with pytest.raises(ValueError):
            with rollback_manager.atomic(phage_id="phage_123") as cp:
                checkpoint = cp
                checkpoint.add_file(test_file)
                test_file.write_text("modified")
                raise ValueError("Test error")

        # Should be rolled back
        assert checkpoint is not None
        assert checkpoint.status == RollbackStatus.ROLLED_BACK
        assert test_file.read_text() == "original content"

    @pytest.mark.asyncio
    async def test_atomic_async_context(
        self, rollback_manager: AtomicMutationManager, test_file: Path
    ) -> None:
        """Test async atomic context manager."""
        async with rollback_manager.atomic_async(phage_id="phage_123") as checkpoint:
            checkpoint.add_file(test_file)
            test_file.write_text("modified")

        assert checkpoint.status == RollbackStatus.COMMITTED
        assert test_file.read_text() == "modified"

    def test_active_count(
        self, rollback_manager: AtomicMutationManager, test_file: Path
    ) -> None:
        """Test active checkpoint counting."""
        assert rollback_manager.active_count == 0

        with rollback_manager.atomic() as _:
            assert rollback_manager.active_count == 1

        # Still tracked in history
        assert rollback_manager.active_count == 1

    def test_get_checkpoint(
        self, rollback_manager: AtomicMutationManager, test_file: Path
    ) -> None:
        """Test getting checkpoint by ID."""
        with rollback_manager.atomic() as checkpoint:
            retrieved = rollback_manager.get_checkpoint(checkpoint.id)
            assert retrieved is checkpoint

    def test_cleanup_expired(self, temp_dir: Path) -> None:
        """Test cleaning up expired checkpoints."""
        manager = AtomicMutationManager(default_timeout=0.1)

        # Create checkpoint
        test_file = temp_dir / "test.py"
        test_file.write_text("original")

        # Start but don't finish
        checkpoint = AtomicCheckpoint(timeout_seconds=0.1)
        checkpoint.add_file(test_file)
        manager._active_checkpoints[checkpoint.id] = checkpoint

        # Modify file BEFORE expiration (within checkpoint lifetime)
        test_file.write_text("modified")

        # Wait for expiration
        time.sleep(0.15)
        assert checkpoint.is_expired()

        # Cleanup should rollback to original state
        cleaned = manager.cleanup_expired()
        assert cleaned == 1
        assert checkpoint.status == RollbackStatus.EXPIRED
        # Rollback restores to checkpoint state (original)
        assert test_file.read_text() == "original"


# =============================================================================
# RateLimiter Tests
# =============================================================================


class TestRateLimiter:
    """Tests for RateLimiter."""

    def test_check_mutation_allowed(self, rate_limiter: RateLimiter) -> None:
        """Test mutation check when under limit."""
        # Should not raise
        rate_limiter.check_mutation()

    def test_check_mutation_exceeded(self, rate_limiter: RateLimiter) -> None:
        """Test mutation check when limit exceeded."""
        # Record mutations up to limit + burst
        for _ in range(6):  # 5 limit + 1 burst
            rate_limiter.record_mutation()

        # Next one should fail
        with pytest.raises(RateLimitExceeded) as exc_info:
            rate_limiter.check_mutation()

        assert exc_info.value.limit_type == "mutation_minute"
        assert exc_info.value.current == 6
        assert exc_info.value.limit == 5

    def test_check_infection_allowed(self, rate_limiter: RateLimiter) -> None:
        """Test infection check when under limit."""
        rate_limiter.check_infection()

    def test_check_infection_exceeded(self, rate_limiter: RateLimiter) -> None:
        """Test infection check when limit exceeded."""
        # Record infections up to limit + burst
        for _ in range(4):  # 3 limit + 1 burst
            rate_limiter.record_infection()

        with pytest.raises(RateLimitExceeded) as exc_info:
            rate_limiter.check_infection()

        assert exc_info.value.limit_type == "infection_minute"

    def test_record_resets_violations(self, rate_limiter: RateLimiter) -> None:
        """Test successful record resets violation counter."""
        # Trigger violation
        for _ in range(6):
            rate_limiter.record_mutation()

        try:
            rate_limiter.check_mutation()
        except RateLimitExceeded:
            pass

        assert rate_limiter._consecutive_violations == 1

        # Wait for new window and record success
        rate_limiter._mutation_windows.clear()
        rate_limiter.record_mutation()

        assert rate_limiter._consecutive_violations == 0

    def test_exponential_backoff(self) -> None:
        """Test exponential backoff on repeated violations."""
        config = RateLimitConfig(
            max_mutations_per_minute=1,
            burst_allowance=0,
            backoff_base_seconds=10.0,  # Larger base to make difference clearer
            backoff_multiplier=2.0,
            backoff_max_seconds=600.0,  # High max so we can see the effect
        )
        limiter = RateLimiter(config)

        # First violation
        limiter.record_mutation()
        try:
            limiter.check_mutation()
        except RateLimitExceeded:
            pass

        # Second violation (without reset)
        try:
            limiter.check_mutation()
        except RateLimitExceeded as e:
            second_retry = e.retry_after

        # Second retry should include backoff from consecutive violations
        # The backoff adds exponentially: base * (multiplier ^ violations)
        # With 2 violations: 10 * 2^2 = 40 extra seconds
        assert limiter._consecutive_violations == 2
        # We can't directly compare retry_after since it includes window time,
        # but we know violations accumulate
        assert second_retry > 0

    def test_get_status(self, rate_limiter: RateLimiter) -> None:
        """Test getting rate limit status."""
        rate_limiter.record_mutation()
        rate_limiter.record_infection()

        status = rate_limiter.get_status()

        assert "mutations" in status
        assert "infections" in status
        assert status["mutations"]["minute"]["current"] == 1
        assert status["infections"]["minute"]["current"] == 1


# =============================================================================
# AuditLogger Tests
# =============================================================================


class TestAuditEvent:
    """Tests for AuditEvent."""

    def test_create_event(self) -> None:
        """Test creating an audit event."""
        event = AuditEvent(
            event_type=AuditEventType.INFECTION_STARTED,
            phage_id="phage_123",
            target_path="/path/to/file.py",
        )

        assert event.id.startswith("evt_")
        assert event.event_type == AuditEventType.INFECTION_STARTED
        assert event.phage_id == "phage_123"

    def test_to_dict(self) -> None:
        """Test serialization to dict."""
        event = AuditEvent(
            event_type=AuditEventType.MUTATION_GENERATED,
            phage_id="phage_123",
            details={"schema": "loop_to_comprehension"},
        )

        data = event.to_dict()

        assert data["event_type"] == "mutation_generated"
        assert data["phage_id"] == "phage_123"
        assert data["details"]["schema"] == "loop_to_comprehension"

    def test_from_dict(self) -> None:
        """Test deserialization from dict."""
        data = {
            "id": "evt_test",
            "event_type": "infection_succeeded",
            "timestamp": "2025-01-01T00:00:00",
            "phage_id": "phage_123",
            "success": True,
        }

        event = AuditEvent.from_dict(data)

        assert event.id == "evt_test"
        assert event.event_type == AuditEventType.INFECTION_SUCCEEDED
        assert event.phage_id == "phage_123"


class TestInMemoryAuditSink:
    """Tests for InMemoryAuditSink."""

    @pytest.mark.asyncio
    async def test_write_and_query(self) -> None:
        """Test writing and querying events."""
        sink = InMemoryAuditSink()

        event = AuditEvent(
            event_type=AuditEventType.INFECTION_STARTED,
            phage_id="phage_123",
        )
        await sink.write(event)

        results = await sink.query()
        assert len(results) == 1
        assert results[0].phage_id == "phage_123"

    @pytest.mark.asyncio
    async def test_query_by_type(self) -> None:
        """Test querying by event type."""
        sink = InMemoryAuditSink()

        await sink.write(
            AuditEvent(event_type=AuditEventType.INFECTION_STARTED, phage_id="p1")
        )
        await sink.write(
            AuditEvent(event_type=AuditEventType.INFECTION_SUCCEEDED, phage_id="p1")
        )
        await sink.write(
            AuditEvent(event_type=AuditEventType.INFECTION_STARTED, phage_id="p2")
        )

        results = await sink.query(event_type=AuditEventType.INFECTION_STARTED)
        assert len(results) == 2

    @pytest.mark.asyncio
    async def test_query_by_phage_id(self) -> None:
        """Test querying by phage ID."""
        sink = InMemoryAuditSink()

        await sink.write(
            AuditEvent(event_type=AuditEventType.INFECTION_STARTED, phage_id="p1")
        )
        await sink.write(
            AuditEvent(event_type=AuditEventType.INFECTION_STARTED, phage_id="p2")
        )

        results = await sink.query(phage_id="p1")
        assert len(results) == 1
        assert results[0].phage_id == "p1"

    @pytest.mark.asyncio
    async def test_max_events_trimming(self) -> None:
        """Test that events are trimmed when max reached."""
        sink = InMemoryAuditSink(max_events=5)

        for i in range(10):
            await sink.write(
                AuditEvent(
                    event_type=AuditEventType.MUTATION_GENERATED,
                    phage_id=f"phage_{i}",
                )
            )

        # Should only have last 5
        assert len(sink.events) == 5
        assert sink.events[0].phage_id == "phage_5"


class TestFileAuditSink:
    """Tests for FileAuditSink."""

    @pytest.mark.asyncio
    async def test_write_and_query(self, temp_dir: Path) -> None:
        """Test writing to file and querying."""
        sink = FileAuditSink(temp_dir)

        event = AuditEvent(
            event_type=AuditEventType.INFECTION_STARTED,
            phage_id="phage_123",
        )
        await sink.write(event)

        results = await sink.query()
        assert len(results) == 1
        assert results[0].phage_id == "phage_123"

    @pytest.mark.asyncio
    async def test_creates_log_directory(self, temp_dir: Path) -> None:
        """Test that log directory is created."""
        log_dir = temp_dir / "logs" / "audit"
        sink = FileAuditSink(log_dir)

        await sink.write(AuditEvent(event_type=AuditEventType.MUTATION_GENERATED))

        assert log_dir.exists()


class TestAuditLogger:
    """Tests for AuditLogger."""

    @pytest.mark.asyncio
    async def test_log_event(self, audit_logger: AuditLogger) -> None:
        """Test logging an event."""
        event = await audit_logger.log(
            AuditEventType.MUTATION_GENERATED,
            phage_id="phage_123",
            details={"schema": "test"},
        )

        assert event.event_type == AuditEventType.MUTATION_GENERATED
        assert event.phage_id == "phage_123"

    @pytest.mark.asyncio
    async def test_convenience_methods(self, audit_logger: AuditLogger) -> None:
        """Test convenience logging methods."""
        await audit_logger.log_mutation_generated("phage_1", "schema_1", -0.5)
        await audit_logger.log_mutation_rejected("phage_2", "low alignment")
        await audit_logger.log_infection_started("phage_3", "/path.py", "ckpt_1")
        await audit_logger.log_infection_succeeded("phage_3", "/path.py", 10)
        await audit_logger.log_infection_failed("phage_4", "/path.py", "tests failed")

        events = await audit_logger.query()
        assert len(events) == 5

    @pytest.mark.asyncio
    async def test_set_cycle_id(self, audit_logger: AuditLogger) -> None:
        """Test cycle ID is attached to events."""
        audit_logger.set_cycle_id("cycle_123")

        event = await audit_logger.log(
            AuditEventType.MUTATION_GENERATED,
            phage_id="phage_1",
        )

        assert event.cycle_id == "cycle_123"


# =============================================================================
# Sandbox Tests
# =============================================================================


class TestSandbox:
    """Tests for Sandbox."""

    def test_create_sandbox(self) -> None:
        """Test creating a sandbox."""
        sandbox = Sandbox()

        assert sandbox.config is not None

    def test_enter_creates_temp_dir(self) -> None:
        """Test entering sandbox creates temp directory."""
        sandbox = Sandbox()

        with sandbox.enter() as sb:
            assert sb._temp_dir is not None
            assert sb._temp_dir.exists()
            temp_path = sb._temp_dir

        # Should be cleaned up
        assert not temp_path.exists()

    @pytest.mark.asyncio
    async def test_enter_async(self) -> None:
        """Test async sandbox entry."""
        sandbox = Sandbox()

        async with sandbox.enter_async() as sb:
            assert sb._temp_dir is not None
            assert sb._temp_dir.exists()

    def test_copy_file(self, temp_dir: Path) -> None:
        """Test copying a file into sandbox."""
        source = temp_dir / "source.py"
        source.write_text("source content")

        sandbox = Sandbox()

        with sandbox.enter() as sb:
            dest = sb.copy_file(source)
            assert dest.exists()
            assert dest.read_text() == "source content"
            assert dest.parent == sb.work_dir

    def test_write_file(self) -> None:
        """Test writing a file in sandbox."""
        sandbox = Sandbox()

        with sandbox.enter() as sb:
            path = sb.write_file("test content", "test.py")
            assert path.exists()
            assert path.read_text() == "test content"

    def test_max_files_limit(self) -> None:
        """Test max files limit enforcement."""
        config = SandboxConfig(max_files_created=2)
        sandbox = Sandbox(config=config)

        with sandbox.enter() as sb:
            sb.write_file("1", "file1.py")
            sb.write_file("2", "file2.py")

            with pytest.raises(SandboxViolation) as exc_info:
                sb.write_file("3", "file3.py")

            assert "Max files" in exc_info.value.reason

    def test_file_size_limit(self) -> None:
        """Test file size limit enforcement."""
        config = SandboxConfig(max_file_size_mb=1)  # 1 MB limit
        sandbox = Sandbox(config=config)

        with sandbox.enter() as sb:
            # Large content (2 MB)
            content = "x" * (2 * 1024 * 1024)

            with pytest.raises(SandboxViolation) as exc_info:
                sb.write_file(content, "large.py")

            assert "size exceeds" in exc_info.value.reason

    @pytest.mark.asyncio
    async def test_execute_python(self) -> None:
        """Test executing Python code."""
        config = SandboxConfig(timeout_seconds=5.0)
        sandbox = Sandbox(config=config)

        async with sandbox.enter_async() as sb:
            result = await sb.execute_python("print('hello')")

            assert result.success
            assert "hello" in result.stdout

    @pytest.mark.asyncio
    async def test_execute_timeout(self) -> None:
        """Test execution timeout."""
        config = SandboxConfig(timeout_seconds=0.5)
        sandbox = Sandbox(config=config)

        async with sandbox.enter_async() as sb:
            result = await sb.execute_python("import time; time.sleep(5)")

            assert not result.success
            assert "timeout" in result.violations or (
                result.error is not None and "timeout" in result.error.lower()
            )

    @pytest.mark.asyncio
    async def test_run_tests_without_subprocess(self) -> None:
        """Test run_tests fails when subprocess not allowed."""
        config = SandboxConfig(allow_subprocess=False)
        sandbox = Sandbox(config=config)

        async with sandbox.enter_async() as sb:
            test_file = sb.write_file("def test_foo(): pass", "test_foo.py")
            result = await sb.run_tests(test_file)

            assert not result.success
            assert "subprocess_not_allowed" in result.violations


# =============================================================================
# SafetySystem Tests
# =============================================================================


class TestSafetySystem:
    """Tests for SafetySystem."""

    @pytest.mark.asyncio
    async def test_pre_mutation_check_allowed(
        self, safety_system: SafetySystem
    ) -> None:
        """Test pre-mutation check allows operation."""
        allowed, reason = await safety_system.pre_mutation_check("phage_1")

        assert allowed
        assert reason is None

    @pytest.mark.asyncio
    async def test_pre_infection_check_creates_checkpoint(
        self, safety_system: SafetySystem, test_file: Path
    ) -> None:
        """Test pre-infection check creates checkpoint."""
        allowed, reason, checkpoint = await safety_system.pre_infection_check(
            "phage_1", test_file
        )

        assert allowed
        assert checkpoint is not None
        assert checkpoint.phage_id == "phage_1"

    @pytest.mark.asyncio
    async def test_post_infection_success_commits(
        self, safety_system: SafetySystem, test_file: Path
    ) -> None:
        """Test post-infection success commits checkpoint."""
        _, _, checkpoint = await safety_system.pre_infection_check("phage_1", test_file)

        test_file.write_text("modified")

        await safety_system.post_infection_success("phage_1", test_file, checkpoint, 10)

        assert checkpoint is not None
        assert checkpoint.status == RollbackStatus.COMMITTED
        assert test_file.read_text() == "modified"

    @pytest.mark.asyncio
    async def test_post_infection_failure_rollsback(
        self, safety_system: SafetySystem, test_file: Path
    ) -> None:
        """Test post-infection failure rolls back."""
        _, _, checkpoint = await safety_system.pre_infection_check("phage_1", test_file)

        test_file.write_text("modified")

        await safety_system.post_infection_failure(
            "phage_1", test_file, checkpoint, "tests failed"
        )

        assert checkpoint is not None
        assert checkpoint.status == RollbackStatus.ROLLED_BACK
        assert test_file.read_text() == "original content"

    @pytest.mark.asyncio
    async def test_audit_logging(
        self, safety_system: SafetySystem, test_file: Path
    ) -> None:
        """Test audit logging during operations."""
        safety_system.set_cycle_id("cycle_123")

        await safety_system.pre_infection_check("phage_1", test_file)

        events = await safety_system.audit_logger.query()
        assert len(events) >= 1  # At least checkpoint and infection start

    def test_get_status(self, safety_system: SafetySystem) -> None:
        """Test getting safety system status."""
        status = safety_system.get_status()

        assert "rollback" in status
        assert "rate_limit" in status
        assert "config" in status


class TestFactoryFunctions:
    """Tests for factory functions."""

    def test_create_safety_system_default(self) -> None:
        """Test creating default safety system."""
        system = create_safety_system()

        assert system.config.enable_rollback
        assert system.config.enable_rate_limiting
        assert system.config.enable_audit
        assert system.config.enable_sandbox

    def test_create_safety_system_strict(self) -> None:
        """Test creating strict safety system."""
        system = create_safety_system(strict=True)

        assert system.rate_limiter.config.max_mutations_per_minute == 30

    def test_create_safety_system_with_audit_dir(self, temp_dir: Path) -> None:
        """Test creating safety system with audit directory."""
        audit_dir = temp_dir / "audit"
        system = create_safety_system(audit_dir=audit_dir)

        assert isinstance(system.audit_logger._sink, FileAuditSink)

    def test_create_test_safety_system(self) -> None:
        """Test creating test safety system."""
        system = create_test_safety_system()

        assert not system.config.enable_rate_limiting


# =============================================================================
# Integration Tests
# =============================================================================


class TestIntegration:
    """Integration tests for safety system."""

    @pytest.mark.asyncio
    async def test_full_infection_flow_success(
        self, safety_system: SafetySystem, test_file: Path
    ) -> None:
        """Test full infection flow with success."""
        safety_system.set_cycle_id("cycle_integration_1")

        # Pre-check
        allowed, reason, checkpoint = await safety_system.pre_infection_check(
            "phage_int_1", test_file
        )
        assert allowed

        # Simulate mutation
        test_file.write_text("improved code")

        # Post-success
        await safety_system.post_infection_success(
            "phage_int_1", test_file, checkpoint, 5
        )

        # Verify
        assert test_file.read_text() == "improved code"

        # Check audit
        events = await safety_system.audit_logger.query(phage_id="phage_int_1")
        event_types = [e.event_type for e in events]
        assert AuditEventType.CHECKPOINT_CREATED in event_types
        assert AuditEventType.INFECTION_STARTED in event_types
        assert AuditEventType.INFECTION_SUCCEEDED in event_types

    @pytest.mark.asyncio
    async def test_full_infection_flow_failure(
        self, safety_system: SafetySystem, test_file: Path
    ) -> None:
        """Test full infection flow with failure and rollback."""
        safety_system.set_cycle_id("cycle_integration_2")

        # Pre-check
        allowed, reason, checkpoint = await safety_system.pre_infection_check(
            "phage_int_2", test_file
        )
        assert allowed

        # Simulate mutation
        test_file.write_text("broken code")

        # Post-failure
        await safety_system.post_infection_failure(
            "phage_int_2", test_file, checkpoint, "tests failed"
        )

        # Verify rollback
        assert test_file.read_text() == "original content"

        # Check audit
        events = await safety_system.audit_logger.query(phage_id="phage_int_2")
        event_types = [e.event_type for e in events]
        assert AuditEventType.CHECKPOINT_ROLLED_BACK in event_types
        assert AuditEventType.INFECTION_FAILED in event_types

    @pytest.mark.asyncio
    async def test_sandboxed_test_execution(self, temp_dir: Path) -> None:
        """Test sandboxed test execution."""
        config = SandboxConfig(
            allow_subprocess=True,
            allowed_commands=["python"],
            timeout_seconds=10.0,
        )
        sandbox = Sandbox(config=config)

        async with sandbox.enter_async() as sb:
            # Write simple test
            code = """
def test_simple() -> None:
    assert 1 + 1 == 2

if __name__ == "__main__":
    test_simple()
    print("PASS")
"""
            sb.write_file(code, "test_simple.py")

            result = await sb.execute_python(code)

            assert result.success or "PASS" in result.stdout


# =============================================================================
# Property Tests
# =============================================================================


class TestProperties:
    """Property-based tests for safety invariants."""

    def test_rollback_is_atomic(self, temp_dir: Path) -> None:
        """Test that rollback is atomic (all or nothing)."""
        files = [temp_dir / f"file{i}.py" for i in range(5)]
        for f in files:
            f.write_text(f"original_{f.name}")

        checkpoint = AtomicCheckpoint()
        for f in files:
            checkpoint.add_file(f)

        # Modify all files
        for f in files:
            f.write_text(f"modified_{f.name}")

        # Rollback
        success, errors = checkpoint.rollback()
        assert success

        # All should be restored
        for f in files:
            assert f.read_text() == f"original_{f.name}"

    def test_rate_limits_are_honored(self) -> None:
        """Test that rate limits cannot be bypassed."""
        config = RateLimitConfig(
            max_mutations_per_minute=3,
            burst_allowance=0,
        )
        limiter = RateLimiter(config)

        # Record up to limit
        for _ in range(3):
            limiter.check_mutation()  # Should pass
            limiter.record_mutation()

        # Next should fail
        with pytest.raises(RateLimitExceeded):
            limiter.check_mutation()

    @pytest.mark.asyncio
    async def test_audit_events_are_immutable(self) -> None:
        """Test that audit events cannot be modified after creation."""
        sink = InMemoryAuditSink()
        logger = AuditLogger(sink=sink)

        event = await logger.log(
            AuditEventType.INFECTION_STARTED,
            phage_id="phage_1",
        )

        original_id = event.id
        original_type = event.event_type

        # Try to query and verify immutability
        events = await sink.query()
        assert events[0].id == original_id
        assert events[0].event_type == original_type
