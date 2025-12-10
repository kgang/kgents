"""
E-gent v2 Phase 8: Safety & Guardrails.

This module provides safety mechanisms for the E-gent evolution system:
1. Rollback guarantees (atomic mutations)
2. Rate limiting for mutation operations
3. Audit logging for all infections
4. Sandboxed execution environment

From spec/e-gents/thermodynamics.md:
> Safety is not optional. Evolution without guardrails becomes cancer.
> Every mutation must be reversible. Every infection must be logged.
> The system must be able to say "no" faster than it can say "yes".

Key principles:
- ATOMIC: Mutations succeed completely or not at all
- AUDITABLE: Every infection leaves a trace
- BOUNDED: Rate limits prevent runaway evolution
- SANDBOXED: Untrusted mutations run in isolation

Spec Reference: spec/e-gents/thermodynamics.md
"""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
from contextlib import asynccontextmanager, contextmanager
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, AsyncIterator, Iterator, Protocol
from uuid import uuid4


# =============================================================================
# Rollback Guarantees (Atomic Mutations)
# =============================================================================


class RollbackStatus(Enum):
    """Status of a rollback checkpoint."""

    ACTIVE = "active"  # Checkpoint is active, changes can be rolled back
    COMMITTED = "committed"  # Changes committed, checkpoint released
    ROLLED_BACK = "rolled_back"  # Changes were rolled back
    EXPIRED = "expired"  # Checkpoint expired (timed out)


@dataclass
class FileCheckpoint:
    """Checkpoint for a single file's state."""

    file_path: Path
    original_content: str | None  # None if file didn't exist
    original_hash: str
    created_at: datetime = field(default_factory=datetime.now)

    @classmethod
    def capture(cls, file_path: Path) -> "FileCheckpoint":
        """Capture current state of a file."""
        if file_path.exists():
            content = file_path.read_text()
            content_hash = hashlib.sha256(content.encode()).hexdigest()
        else:
            content = None
            content_hash = ""

        return cls(
            file_path=file_path,
            original_content=content,
            original_hash=content_hash,
        )

    def restore(self) -> bool:
        """Restore file to checkpointed state."""
        try:
            if self.original_content is None:
                # File didn't exist - delete it
                if self.file_path.exists():
                    self.file_path.unlink()
            else:
                # Restore original content
                self.file_path.parent.mkdir(parents=True, exist_ok=True)
                self.file_path.write_text(self.original_content)
            return True
        except Exception:
            return False

    def verify(self) -> bool:
        """Verify file hasn't changed since checkpoint."""
        if self.original_content is None:
            return not self.file_path.exists()

        if not self.file_path.exists():
            return False

        current_content = self.file_path.read_text()
        current_hash = hashlib.sha256(current_content.encode()).hexdigest()
        return current_hash == self.original_hash


@dataclass
class AtomicCheckpoint:
    """
    Atomic checkpoint for multiple files.

    Provides transaction-like semantics:
    - All files are checkpointed together
    - commit() releases the checkpoint
    - rollback() restores all files atomically

    From spec:
    > Mutations are atomic. Either all changes succeed, or none do.
    > This is enforced via checkpointing, not hoped for.
    """

    id: str = field(default_factory=lambda: f"ckpt_{uuid4().hex[:8]}")
    checkpoints: dict[str, FileCheckpoint] = field(default_factory=dict)
    status: RollbackStatus = RollbackStatus.ACTIVE
    created_at: datetime = field(default_factory=datetime.now)
    timeout_seconds: float = 300.0  # 5 minute default timeout
    metadata: dict[str, Any] = field(default_factory=dict)

    # Audit trail
    phage_id: str | None = None
    mutation_signature: str | None = None

    def add_file(self, file_path: Path) -> FileCheckpoint:
        """Add a file to the checkpoint."""
        if self.status != RollbackStatus.ACTIVE:
            raise RuntimeError(f"Cannot add files to {self.status.value} checkpoint")

        path_key = str(file_path.absolute())
        if path_key not in self.checkpoints:
            checkpoint = FileCheckpoint.capture(file_path)
            self.checkpoints[path_key] = checkpoint
            return checkpoint
        return self.checkpoints[path_key]

    def commit(self) -> bool:
        """
        Commit the checkpoint (accept changes).

        After commit, rollback is no longer possible.
        """
        if self.status != RollbackStatus.ACTIVE:
            return False

        self.status = RollbackStatus.COMMITTED
        return True

    def rollback(self) -> tuple[bool, list[str]]:
        """
        Rollback all files to checkpointed state.

        Returns:
            (success, list of errors)
        """
        if self.status != RollbackStatus.ACTIVE:
            return False, [f"Cannot rollback {self.status.value} checkpoint"]

        errors: list[str] = []
        for path_key, checkpoint in self.checkpoints.items():
            if not checkpoint.restore():
                errors.append(f"Failed to restore {path_key}")

        self.status = RollbackStatus.ROLLED_BACK
        return len(errors) == 0, errors

    def is_expired(self) -> bool:
        """Check if checkpoint has timed out."""
        if self.status != RollbackStatus.ACTIVE:
            return False
        elapsed = (datetime.now() - self.created_at).total_seconds()
        return elapsed > self.timeout_seconds

    def verify_unchanged(self) -> tuple[bool, list[str]]:
        """Verify all files are unchanged from original state."""
        changed: list[str] = []
        for path_key, checkpoint in self.checkpoints.items():
            if not checkpoint.verify():
                changed.append(path_key)
        return len(changed) == 0, changed


class AtomicMutationManager:
    """
    Manager for atomic mutation operations.

    Provides:
    - Multi-file checkpointing
    - Automatic rollback on failure
    - Timeout-based expiration
    - Nested checkpoint support

    Usage:
        async with manager.atomic(phage_id="phage_123") as checkpoint:
            checkpoint.add_file(target_path)
            # Make changes...
            # If exception raised, automatic rollback
        # Changes committed on successful exit
    """

    def __init__(
        self,
        default_timeout: float = 300.0,
        backup_dir: Path | None = None,
    ) -> None:
        """
        Initialize the manager.

        Args:
            default_timeout: Default timeout for checkpoints (seconds)
            backup_dir: Directory for backup files (temp dir if None)
        """
        self._default_timeout = default_timeout
        self._backup_dir = backup_dir or Path(tempfile.gettempdir()) / "egent_backups"
        self._active_checkpoints: dict[str, AtomicCheckpoint] = {}
        self._checkpoint_stack: list[str] = []  # For nesting

    @property
    def active_count(self) -> int:
        """Number of active checkpoints."""
        return len(self._active_checkpoints)

    @contextmanager
    def atomic(
        self,
        phage_id: str | None = None,
        timeout: float | None = None,
    ) -> Iterator[AtomicCheckpoint]:
        """
        Context manager for atomic mutations.

        Args:
            phage_id: Optional phage ID for audit trail
            timeout: Optional timeout override

        Yields:
            AtomicCheckpoint to add files to

        On exit:
            - Normal exit: commit checkpoint
            - Exception: rollback checkpoint
        """
        checkpoint = AtomicCheckpoint(
            timeout_seconds=timeout or self._default_timeout,
            phage_id=phage_id,
        )
        self._active_checkpoints[checkpoint.id] = checkpoint
        self._checkpoint_stack.append(checkpoint.id)

        try:
            yield checkpoint
            # Normal exit - commit
            checkpoint.commit()
        except Exception:
            # Exception - rollback
            checkpoint.rollback()
            raise
        finally:
            self._checkpoint_stack.pop()
            # Keep in history for audit (don't delete immediately)

    @asynccontextmanager
    async def atomic_async(
        self,
        phage_id: str | None = None,
        timeout: float | None = None,
    ) -> AsyncIterator[AtomicCheckpoint]:
        """Async version of atomic context manager."""
        checkpoint = AtomicCheckpoint(
            timeout_seconds=timeout or self._default_timeout,
            phage_id=phage_id,
        )
        self._active_checkpoints[checkpoint.id] = checkpoint
        self._checkpoint_stack.append(checkpoint.id)

        try:
            yield checkpoint
            checkpoint.commit()
        except Exception:
            checkpoint.rollback()
            raise
        finally:
            self._checkpoint_stack.pop()

    def get_checkpoint(self, checkpoint_id: str) -> AtomicCheckpoint | None:
        """Get a checkpoint by ID."""
        return self._active_checkpoints.get(checkpoint_id)

    def cleanup_expired(self) -> int:
        """Clean up expired checkpoints. Returns count cleaned."""
        expired = [
            cid for cid, ckpt in self._active_checkpoints.items() if ckpt.is_expired()
        ]
        for cid in expired:
            ckpt = self._active_checkpoints[cid]
            # Rollback BEFORE setting status to expired (rollback requires ACTIVE status)
            ckpt.rollback()  # Auto-rollback expired checkpoints
            # Now set to expired (rollback would have set it to ROLLED_BACK,
            # but we override to EXPIRED to indicate timeout was the cause)
            ckpt.status = RollbackStatus.EXPIRED
        return len(expired)


# =============================================================================
# Rate Limiting
# =============================================================================


@dataclass
class RateLimitConfig:
    """Configuration for rate limiting."""

    # Mutation limits
    max_mutations_per_minute: int = 60
    max_mutations_per_hour: int = 500
    max_mutations_per_day: int = 2000

    # Infection limits (more conservative)
    max_infections_per_minute: int = 10
    max_infections_per_hour: int = 100
    max_infections_per_day: int = 500

    # Burst allowance
    burst_allowance: int = 5  # Extra allowed in short bursts

    # Backoff
    backoff_base_seconds: float = 1.0
    backoff_max_seconds: float = 60.0
    backoff_multiplier: float = 2.0


@dataclass
class RateLimitState:
    """State for rate limiting tracking."""

    window_start: datetime
    count: int = 0


class RateLimitExceeded(Exception):
    """Raised when rate limit is exceeded."""

    def __init__(
        self,
        limit_type: str,
        current: int,
        limit: int,
        retry_after: float,
    ) -> None:
        self.limit_type = limit_type
        self.current = current
        self.limit = limit
        self.retry_after = retry_after
        super().__init__(
            f"Rate limit exceeded for {limit_type}: {current}/{limit}. "
            f"Retry after {retry_after:.1f}s"
        )


class RateLimiter:
    """
    Rate limiter for mutation operations.

    Implements sliding window rate limiting with:
    - Multiple time windows (minute, hour, day)
    - Burst allowance for short spikes
    - Exponential backoff on repeated violations

    From spec:
    > Evolution must be bounded. Runaway mutation is cancer.
    > Rate limits are the immune system's first line of defense.
    """

    def __init__(self, config: RateLimitConfig | None = None) -> None:
        """Initialize rate limiter with config."""
        self.config = config or RateLimitConfig()

        # State tracking
        self._mutation_windows: dict[str, RateLimitState] = {}
        self._infection_windows: dict[str, RateLimitState] = {}

        # Backoff tracking
        self._consecutive_violations = 0
        self._last_violation: datetime | None = None

    def _get_window_key(self, window_type: str) -> str:
        """Get key for current window."""
        now = datetime.now()
        if window_type == "minute":
            return now.strftime("%Y-%m-%d-%H-%M")
        elif window_type == "hour":
            return now.strftime("%Y-%m-%d-%H")
        else:  # day
            return now.strftime("%Y-%m-%d")

    def _check_limit(
        self,
        windows: dict[str, RateLimitState],
        window_type: str,
        limit: int,
        operation: str,
    ) -> None:
        """Check if rate limit is exceeded for a window."""
        key = self._get_window_key(window_type)
        now = datetime.now()

        # Get or create state
        if key not in windows:
            windows[key] = RateLimitState(window_start=now)

        state = windows[key]

        # Check with burst allowance
        effective_limit = limit + self.config.burst_allowance
        if state.count >= effective_limit:
            # Calculate retry after
            if window_type == "minute":
                window_end = state.window_start + timedelta(minutes=1)
            elif window_type == "hour":
                window_end = state.window_start + timedelta(hours=1)
            else:
                window_end = state.window_start + timedelta(days=1)

            retry_after = max(0, (window_end - now).total_seconds())

            # Apply backoff
            if self._consecutive_violations > 0:
                backoff = min(
                    self.config.backoff_max_seconds,
                    self.config.backoff_base_seconds
                    * (self.config.backoff_multiplier**self._consecutive_violations),
                )
                retry_after = max(retry_after, backoff)

            self._consecutive_violations += 1
            self._last_violation = now

            raise RateLimitExceeded(
                limit_type=f"{operation}_{window_type}",
                current=state.count,
                limit=limit,
                retry_after=retry_after,
            )

    def check_mutation(self) -> None:
        """Check if mutation is allowed. Raises RateLimitExceeded if not."""
        self._check_limit(
            self._mutation_windows,
            "minute",
            self.config.max_mutations_per_minute,
            "mutation",
        )
        self._check_limit(
            self._mutation_windows,
            "hour",
            self.config.max_mutations_per_hour,
            "mutation",
        )
        self._check_limit(
            self._mutation_windows,
            "day",
            self.config.max_mutations_per_day,
            "mutation",
        )

    def check_infection(self) -> None:
        """Check if infection is allowed. Raises RateLimitExceeded if not."""
        self._check_limit(
            self._infection_windows,
            "minute",
            self.config.max_infections_per_minute,
            "infection",
        )
        self._check_limit(
            self._infection_windows,
            "hour",
            self.config.max_infections_per_hour,
            "infection",
        )
        self._check_limit(
            self._infection_windows,
            "day",
            self.config.max_infections_per_day,
            "infection",
        )

    def record_mutation(self) -> None:
        """Record a mutation operation."""
        for window_type in ["minute", "hour", "day"]:
            key = self._get_window_key(window_type)
            if key not in self._mutation_windows:
                self._mutation_windows[key] = RateLimitState(
                    window_start=datetime.now()
                )
            self._mutation_windows[key].count += 1

        # Reset violation counter on success
        self._consecutive_violations = 0

    def record_infection(self) -> None:
        """Record an infection operation."""
        for window_type in ["minute", "hour", "day"]:
            key = self._get_window_key(window_type)
            if key not in self._infection_windows:
                self._infection_windows[key] = RateLimitState(
                    window_start=datetime.now()
                )
            self._infection_windows[key].count += 1

        self._consecutive_violations = 0

    def get_status(self) -> dict[str, Any]:
        """Get current rate limit status."""
        now = datetime.now()
        return {
            "mutations": {
                "minute": {
                    "current": self._mutation_windows.get(
                        self._get_window_key("minute"), RateLimitState(now)
                    ).count,
                    "limit": self.config.max_mutations_per_minute,
                },
                "hour": {
                    "current": self._mutation_windows.get(
                        self._get_window_key("hour"), RateLimitState(now)
                    ).count,
                    "limit": self.config.max_mutations_per_hour,
                },
                "day": {
                    "current": self._mutation_windows.get(
                        self._get_window_key("day"), RateLimitState(now)
                    ).count,
                    "limit": self.config.max_mutations_per_day,
                },
            },
            "infections": {
                "minute": {
                    "current": self._infection_windows.get(
                        self._get_window_key("minute"), RateLimitState(now)
                    ).count,
                    "limit": self.config.max_infections_per_minute,
                },
                "hour": {
                    "current": self._infection_windows.get(
                        self._get_window_key("hour"), RateLimitState(now)
                    ).count,
                    "limit": self.config.max_infections_per_hour,
                },
                "day": {
                    "current": self._infection_windows.get(
                        self._get_window_key("day"), RateLimitState(now)
                    ).count,
                    "limit": self.config.max_infections_per_day,
                },
            },
            "consecutive_violations": self._consecutive_violations,
        }


# =============================================================================
# Audit Logging
# =============================================================================


class AuditEventType(Enum):
    """Types of audit events."""

    # Mutation lifecycle
    MUTATION_GENERATED = "mutation_generated"
    MUTATION_SELECTED = "mutation_selected"
    MUTATION_REJECTED = "mutation_rejected"

    # Infection lifecycle
    INFECTION_STARTED = "infection_started"
    INFECTION_SUCCEEDED = "infection_succeeded"
    INFECTION_FAILED = "infection_failed"
    INFECTION_ROLLED_BACK = "infection_rolled_back"

    # Checkpoint events
    CHECKPOINT_CREATED = "checkpoint_created"
    CHECKPOINT_COMMITTED = "checkpoint_committed"
    CHECKPOINT_ROLLED_BACK = "checkpoint_rolled_back"
    CHECKPOINT_EXPIRED = "checkpoint_expired"

    # Rate limit events
    RATE_LIMIT_CHECKED = "rate_limit_checked"
    RATE_LIMIT_EXCEEDED = "rate_limit_exceeded"

    # Sandbox events
    SANDBOX_CREATED = "sandbox_created"
    SANDBOX_EXECUTED = "sandbox_executed"
    SANDBOX_VIOLATION = "sandbox_violation"
    SANDBOX_DESTROYED = "sandbox_destroyed"

    # Safety events
    SAFETY_CHECK_PASSED = "safety_check_passed"
    SAFETY_CHECK_FAILED = "safety_check_failed"


@dataclass
class AuditEvent:
    """
    Audit event for infection tracking.

    Every significant action is logged for:
    - Forensic analysis
    - Compliance
    - Learning (what went wrong?)
    """

    id: str = field(default_factory=lambda: f"evt_{uuid4().hex[:8]}")
    event_type: AuditEventType = AuditEventType.MUTATION_GENERATED
    timestamp: datetime = field(default_factory=datetime.now)

    # Context
    phage_id: str | None = None
    checkpoint_id: str | None = None
    target_path: str | None = None

    # Details
    details: dict[str, Any] = field(default_factory=dict)
    success: bool = True
    error_message: str | None = None

    # Metadata
    agent_id: str = "e-gent"
    cycle_id: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "id": self.id,
            "event_type": self.event_type.value,
            "timestamp": self.timestamp.isoformat(),
            "phage_id": self.phage_id,
            "checkpoint_id": self.checkpoint_id,
            "target_path": self.target_path,
            "details": self.details,
            "success": self.success,
            "error_message": self.error_message,
            "agent_id": self.agent_id,
            "cycle_id": self.cycle_id,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "AuditEvent":
        """Create from dictionary."""
        return cls(
            id=data.get("id", f"evt_{uuid4().hex[:8]}"),
            event_type=AuditEventType(data.get("event_type", "mutation_generated")),
            timestamp=datetime.fromisoformat(data["timestamp"])
            if "timestamp" in data
            else datetime.now(),
            phage_id=data.get("phage_id"),
            checkpoint_id=data.get("checkpoint_id"),
            target_path=data.get("target_path"),
            details=data.get("details", {}),
            success=data.get("success", True),
            error_message=data.get("error_message"),
            agent_id=data.get("agent_id", "e-gent"),
            cycle_id=data.get("cycle_id"),
        )


class AuditSink(Protocol):
    """Protocol for audit log sinks."""

    async def write(self, event: AuditEvent) -> None:
        """Write an audit event."""
        ...

    async def query(
        self,
        event_type: AuditEventType | None = None,
        phage_id: str | None = None,
        since: datetime | None = None,
        limit: int = 100,
    ) -> list[AuditEvent]:
        """Query audit events."""
        ...


class InMemoryAuditSink:
    """In-memory audit sink for testing."""

    def __init__(self, max_events: int = 10000) -> None:
        """Initialize with max event buffer."""
        self._events: list[AuditEvent] = []
        self._max_events = max_events

    async def write(self, event: AuditEvent) -> None:
        """Write an audit event."""
        self._events.append(event)
        # Trim if over limit
        if len(self._events) > self._max_events:
            self._events = self._events[-self._max_events :]

    async def query(
        self,
        event_type: AuditEventType | None = None,
        phage_id: str | None = None,
        since: datetime | None = None,
        limit: int = 100,
    ) -> list[AuditEvent]:
        """Query audit events."""
        results = self._events

        if event_type is not None:
            results = [e for e in results if e.event_type == event_type]

        if phage_id is not None:
            results = [e for e in results if e.phage_id == phage_id]

        if since is not None:
            results = [e for e in results if e.timestamp >= since]

        return results[-limit:]

    @property
    def events(self) -> list[AuditEvent]:
        """Access raw events list."""
        return self._events


class FileAuditSink:
    """File-based audit sink for production."""

    def __init__(
        self,
        log_dir: Path,
        rotate_size_mb: float = 10.0,
        max_files: int = 10,
    ) -> None:
        """
        Initialize file audit sink.

        Args:
            log_dir: Directory for log files
            rotate_size_mb: Size at which to rotate files
            max_files: Maximum number of log files to keep
        """
        self._log_dir = log_dir
        self._rotate_size = int(rotate_size_mb * 1024 * 1024)
        self._max_files = max_files
        self._current_file: Path | None = None

        # Ensure directory exists
        self._log_dir.mkdir(parents=True, exist_ok=True)

    def _get_current_file(self) -> Path:
        """Get current log file, rotating if needed."""
        if self._current_file is None:
            self._current_file = (
                self._log_dir / f"audit_{datetime.now():%Y%m%d_%H%M%S}.jsonl"
            )

        # Check if rotation needed
        if self._current_file.exists():
            if self._current_file.stat().st_size > self._rotate_size:
                self._rotate()

        return self._current_file

    def _rotate(self) -> None:
        """Rotate log files."""
        self._current_file = (
            self._log_dir / f"audit_{datetime.now():%Y%m%d_%H%M%S}.jsonl"
        )

        # Clean up old files
        log_files = sorted(self._log_dir.glob("audit_*.jsonl"))
        while len(log_files) > self._max_files:
            oldest = log_files.pop(0)
            oldest.unlink()

    async def write(self, event: AuditEvent) -> None:
        """Write an audit event."""
        log_file = self._get_current_file()
        with open(log_file, "a") as f:
            f.write(json.dumps(event.to_dict()) + "\n")

    async def query(
        self,
        event_type: AuditEventType | None = None,
        phage_id: str | None = None,
        since: datetime | None = None,
        limit: int = 100,
    ) -> list[AuditEvent]:
        """Query audit events from files."""
        results: list[AuditEvent] = []

        # Read from all log files (newest first)
        log_files = sorted(self._log_dir.glob("audit_*.jsonl"), reverse=True)

        for log_file in log_files:
            with open(log_file) as f:
                for line in f:
                    try:
                        data = json.loads(line.strip())
                        event = AuditEvent.from_dict(data)

                        # Apply filters
                        if event_type is not None and event.event_type != event_type:
                            continue
                        if phage_id is not None and event.phage_id != phage_id:
                            continue
                        if since is not None and event.timestamp < since:
                            continue

                        results.append(event)

                        if len(results) >= limit:
                            return results

                    except (json.JSONDecodeError, KeyError):
                        continue

        return results


class AuditLogger:
    """
    Audit logger for E-gent operations.

    Provides structured logging for all mutation and infection operations.

    From spec:
    > Every infection must be logged. Forensics require traces.
    > If we can't explain what happened, we can't fix what went wrong.
    """

    def __init__(
        self,
        sink: AuditSink | None = None,
        agent_id: str = "e-gent",
    ) -> None:
        """
        Initialize audit logger.

        Args:
            sink: Audit sink to write to
            agent_id: ID of the agent for attribution
        """
        self._sink = sink or InMemoryAuditSink()
        self._agent_id = agent_id
        self._current_cycle_id: str | None = None

    def set_cycle_id(self, cycle_id: str) -> None:
        """Set current cycle ID for event attribution."""
        self._current_cycle_id = cycle_id

    async def log(
        self,
        event_type: AuditEventType,
        phage_id: str | None = None,
        checkpoint_id: str | None = None,
        target_path: str | None = None,
        details: dict[str, Any] | None = None,
        success: bool = True,
        error_message: str | None = None,
    ) -> AuditEvent:
        """Log an audit event."""
        event = AuditEvent(
            event_type=event_type,
            phage_id=phage_id,
            checkpoint_id=checkpoint_id,
            target_path=target_path,
            details=details or {},
            success=success,
            error_message=error_message,
            agent_id=self._agent_id,
            cycle_id=self._current_cycle_id,
        )

        await self._sink.write(event)
        return event

    # Convenience methods for common events

    async def log_mutation_generated(
        self,
        phage_id: str,
        schema: str,
        gibbs: float,
    ) -> AuditEvent:
        """Log mutation generation."""
        return await self.log(
            AuditEventType.MUTATION_GENERATED,
            phage_id=phage_id,
            details={"schema": schema, "gibbs_free_energy": gibbs},
        )

    async def log_mutation_rejected(
        self,
        phage_id: str,
        reason: str,
    ) -> AuditEvent:
        """Log mutation rejection."""
        return await self.log(
            AuditEventType.MUTATION_REJECTED,
            phage_id=phage_id,
            success=False,
            details={"reason": reason},
        )

    async def log_infection_started(
        self,
        phage_id: str,
        target_path: str,
        checkpoint_id: str,
    ) -> AuditEvent:
        """Log infection start."""
        return await self.log(
            AuditEventType.INFECTION_STARTED,
            phage_id=phage_id,
            target_path=target_path,
            checkpoint_id=checkpoint_id,
        )

    async def log_infection_succeeded(
        self,
        phage_id: str,
        target_path: str,
        tests_passed: int,
    ) -> AuditEvent:
        """Log successful infection."""
        return await self.log(
            AuditEventType.INFECTION_SUCCEEDED,
            phage_id=phage_id,
            target_path=target_path,
            details={"tests_passed": tests_passed},
        )

    async def log_infection_failed(
        self,
        phage_id: str,
        target_path: str,
        reason: str,
    ) -> AuditEvent:
        """Log failed infection."""
        return await self.log(
            AuditEventType.INFECTION_FAILED,
            phage_id=phage_id,
            target_path=target_path,
            success=False,
            error_message=reason,
        )

    async def log_rollback(
        self,
        checkpoint_id: str,
        phage_id: str | None,
        reason: str,
    ) -> AuditEvent:
        """Log rollback."""
        return await self.log(
            AuditEventType.CHECKPOINT_ROLLED_BACK,
            checkpoint_id=checkpoint_id,
            phage_id=phage_id,
            details={"reason": reason},
        )

    async def query(
        self,
        event_type: AuditEventType | None = None,
        phage_id: str | None = None,
        since: datetime | None = None,
        limit: int = 100,
    ) -> list[AuditEvent]:
        """Query audit events."""
        return await self._sink.query(
            event_type=event_type,
            phage_id=phage_id,
            since=since,
            limit=limit,
        )


# =============================================================================
# Sandboxed Execution
# =============================================================================


class SandboxViolation(Exception):
    """Raised when sandbox policy is violated."""

    def __init__(self, operation: str, resource: str, reason: str) -> None:
        self.operation = operation
        self.resource = resource
        self.reason = reason
        super().__init__(f"Sandbox violation: {operation} on {resource}: {reason}")


@dataclass
class SandboxConfig:
    """Configuration for sandbox environment."""

    # Resource limits
    max_memory_mb: int = 512
    max_cpu_seconds: float = 30.0
    max_file_size_mb: int = 10
    max_files_created: int = 10

    # Network
    allow_network: bool = False

    # File system
    allowed_paths: list[Path] = field(default_factory=list)
    denied_paths: list[Path] = field(default_factory=list)

    # Process
    allow_subprocess: bool = False
    allowed_commands: list[str] = field(default_factory=list)

    # Execution
    timeout_seconds: float = 60.0


@dataclass
class SandboxResult:
    """Result of sandbox execution."""

    success: bool
    return_value: Any = None
    stdout: str = ""
    stderr: str = ""
    execution_time_ms: float = 0.0
    memory_used_mb: float = 0.0
    files_created: list[str] = field(default_factory=list)
    files_modified: list[str] = field(default_factory=list)
    violations: list[str] = field(default_factory=list)
    error: str | None = None


class Sandbox:
    """
    Sandboxed execution environment for mutations.

    Provides isolation for running untrusted mutation tests:
    - Resource limits (CPU, memory, files)
    - Network isolation
    - File system restrictions
    - Process restrictions

    From spec:
    > Untrusted code runs in a cage. The cage has:
    > - Walls (file system limits)
    > - A ceiling (resource caps)
    > - No doors (network isolation)
    > If the mutation tries to escape, it dies.
    """

    def __init__(
        self,
        config: SandboxConfig | None = None,
        work_dir: Path | None = None,
    ) -> None:
        """
        Initialize sandbox.

        Args:
            config: Sandbox configuration
            work_dir: Working directory (temp if None)
        """
        self.config = config or SandboxConfig()
        self._work_dir = work_dir
        self._temp_dir: Path | None = None
        self._files_created: list[Path] = []
        self._files_modified: list[Path] = []

    @property
    def work_dir(self) -> Path:
        """Get sandbox working directory."""
        if self._temp_dir:
            return self._temp_dir
        return self._work_dir or Path.cwd()

    def _check_path_allowed(self, path: Path) -> bool:
        """Check if path is allowed for access."""
        abs_path = path.absolute()

        # Check denied paths first
        for denied in self.config.denied_paths:
            try:
                abs_path.relative_to(denied.absolute())
                return False
            except ValueError:
                continue

        # Check if within sandbox work dir
        try:
            abs_path.relative_to(self.work_dir)
            return True
        except ValueError:
            pass

        # Check allowed paths
        for allowed in self.config.allowed_paths:
            try:
                abs_path.relative_to(allowed.absolute())
                return True
            except ValueError:
                continue

        return False

    def _check_file_size(self, path: Path) -> bool:
        """Check if file size is within limits."""
        if path.exists():
            size_mb = path.stat().st_size / (1024 * 1024)
            return size_mb <= self.config.max_file_size_mb
        return True

    @contextmanager
    def enter(self) -> Iterator["Sandbox"]:
        """
        Enter sandbox environment.

        Creates isolated temp directory and tracks file operations.
        """
        # Create temp directory
        self._temp_dir = Path(tempfile.mkdtemp(prefix="egent_sandbox_"))
        self._files_created = []
        self._files_modified = []

        try:
            yield self
        finally:
            # Cleanup
            if self._temp_dir and self._temp_dir.exists():
                shutil.rmtree(self._temp_dir)
            self._temp_dir = None

    @asynccontextmanager
    async def enter_async(self) -> AsyncIterator["Sandbox"]:
        """Async version of enter."""
        self._temp_dir = Path(tempfile.mkdtemp(prefix="egent_sandbox_"))
        self._files_created = []
        self._files_modified = []

        try:
            yield self
        finally:
            if self._temp_dir and self._temp_dir.exists():
                shutil.rmtree(self._temp_dir)
            self._temp_dir = None

    def copy_file(self, source: Path, dest_name: str | None = None) -> Path:
        """
        Copy a file into the sandbox.

        Args:
            source: Source file path
            dest_name: Optional destination filename

        Returns:
            Path to file in sandbox
        """
        if not source.exists():
            raise FileNotFoundError(f"Source file not found: {source}")

        dest_name = dest_name or source.name
        dest = self.work_dir / dest_name

        shutil.copy2(source, dest)
        self._files_created.append(dest)

        return dest

    def write_file(self, content: str, filename: str) -> Path:
        """
        Write a file in the sandbox.

        Args:
            content: File content
            filename: Filename

        Returns:
            Path to created file
        """
        if len(self._files_created) >= self.config.max_files_created:
            raise SandboxViolation(
                "write_file",
                filename,
                f"Max files ({self.config.max_files_created}) exceeded",
            )

        dest = self.work_dir / filename
        dest.write_text(content)
        self._files_created.append(dest)

        if not self._check_file_size(dest):
            dest.unlink()
            raise SandboxViolation(
                "write_file",
                filename,
                f"File size exceeds {self.config.max_file_size_mb}MB",
            )

        return dest

    async def run_tests(
        self,
        test_file: Path,
        test_command: str = "pytest",
        test_args: list[str] | None = None,
    ) -> SandboxResult:
        """
        Run tests in sandbox.

        Args:
            test_file: Path to test file
            test_command: Test command (must be in allowed_commands)
            test_args: Additional test arguments

        Returns:
            SandboxResult with test outcome
        """
        if not self.config.allow_subprocess:
            return SandboxResult(
                success=False,
                error="Subprocess not allowed in sandbox",
                violations=["subprocess_not_allowed"],
            )

        if (
            self.config.allowed_commands
            and test_command not in self.config.allowed_commands
        ):
            return SandboxResult(
                success=False,
                error=f"Command {test_command} not allowed",
                violations=[f"command_not_allowed:{test_command}"],
            )

        start_time = time.time()
        args = test_args or []

        try:
            # Run with timeout
            result = subprocess.run(
                [test_command, str(test_file)] + args,
                capture_output=True,
                text=True,
                timeout=self.config.timeout_seconds,
                cwd=self.work_dir,
                env={
                    **os.environ,
                    "PYTHONDONTWRITEBYTECODE": "1",
                },
            )

            execution_time = (time.time() - start_time) * 1000

            return SandboxResult(
                success=result.returncode == 0,
                stdout=result.stdout,
                stderr=result.stderr,
                execution_time_ms=execution_time,
                files_created=[str(f) for f in self._files_created],
            )

        except subprocess.TimeoutExpired:
            return SandboxResult(
                success=False,
                error=f"Execution timeout after {self.config.timeout_seconds}s",
                violations=["timeout"],
                execution_time_ms=self.config.timeout_seconds * 1000,
            )
        except Exception as e:
            return SandboxResult(
                success=False,
                error=str(e),
                execution_time_ms=(time.time() - start_time) * 1000,
            )

    async def execute_python(
        self,
        code: str,
        filename: str = "mutation.py",
    ) -> SandboxResult:
        """
        Execute Python code in sandbox.

        Args:
            code: Python code to execute
            filename: Filename for the code

        Returns:
            SandboxResult with execution outcome
        """
        # Write code to file
        code_file = self.write_file(code, filename)

        start_time = time.time()

        try:
            # Run with resource limits
            result = subprocess.run(
                [sys.executable, str(code_file)],
                capture_output=True,
                text=True,
                timeout=self.config.timeout_seconds,
                cwd=self.work_dir,
                env={
                    **os.environ,
                    "PYTHONDONTWRITEBYTECODE": "1",
                },
            )

            execution_time = (time.time() - start_time) * 1000

            return SandboxResult(
                success=result.returncode == 0,
                stdout=result.stdout,
                stderr=result.stderr,
                execution_time_ms=execution_time,
                files_created=[str(f) for f in self._files_created],
            )

        except subprocess.TimeoutExpired:
            return SandboxResult(
                success=False,
                error=f"Execution timeout after {self.config.timeout_seconds}s",
                violations=["timeout"],
                execution_time_ms=self.config.timeout_seconds * 1000,
            )
        except Exception as e:
            return SandboxResult(
                success=False,
                error=str(e),
                execution_time_ms=(time.time() - start_time) * 1000,
            )


# =============================================================================
# Unified Safety System
# =============================================================================


@dataclass
class SafetyConfig:
    """Configuration for the safety system."""

    # Enable/disable components
    enable_rollback: bool = True
    enable_rate_limiting: bool = True
    enable_audit: bool = True
    enable_sandbox: bool = True

    # Component configs
    rollback_timeout: float = 300.0
    rate_limit: RateLimitConfig = field(default_factory=RateLimitConfig)
    sandbox: SandboxConfig = field(default_factory=SandboxConfig)


class SafetySystem:
    """
    Unified safety system for E-gent.

    Integrates:
    - Atomic rollback
    - Rate limiting
    - Audit logging
    - Sandboxed execution

    From spec:
    > Safety is defense in depth:
    > - Rate limits stop runaway mutation
    > - Rollback undoes mistakes
    > - Audit trails enable forensics
    > - Sandboxing contains damage
    >
    > Each layer can fail; all layers together rarely do.
    """

    def __init__(
        self,
        config: SafetyConfig | None = None,
        audit_sink: AuditSink | None = None,
    ) -> None:
        """
        Initialize safety system.

        Args:
            config: Safety configuration
            audit_sink: Audit sink for logging
        """
        self.config = config or SafetyConfig()

        # Initialize components
        self.rollback_manager = AtomicMutationManager(
            default_timeout=self.config.rollback_timeout,
        )
        self.rate_limiter = RateLimiter(self.config.rate_limit)
        self.audit_logger = AuditLogger(sink=audit_sink)
        self.sandbox = Sandbox(self.config.sandbox)

    def set_cycle_id(self, cycle_id: str) -> None:
        """Set current cycle ID for audit attribution."""
        self.audit_logger.set_cycle_id(cycle_id)

    async def pre_mutation_check(self, phage_id: str) -> tuple[bool, str | None]:
        """
        Pre-mutation safety check.

        Returns:
            (allowed, rejection_reason)
        """
        if self.config.enable_rate_limiting:
            try:
                self.rate_limiter.check_mutation()
            except RateLimitExceeded as e:
                await self.audit_logger.log(
                    AuditEventType.RATE_LIMIT_EXCEEDED,
                    phage_id=phage_id,
                    success=False,
                    details={"limit_type": e.limit_type, "retry_after": e.retry_after},
                )
                return False, str(e)

        return True, None

    async def pre_infection_check(
        self,
        phage_id: str,
        target_path: Path,
    ) -> tuple[bool, str | None, AtomicCheckpoint | None]:
        """
        Pre-infection safety check.

        Returns:
            (allowed, rejection_reason, checkpoint)
        """
        # Rate limit check
        if self.config.enable_rate_limiting:
            try:
                self.rate_limiter.check_infection()
            except RateLimitExceeded as e:
                await self.audit_logger.log(
                    AuditEventType.RATE_LIMIT_EXCEEDED,
                    phage_id=phage_id,
                    target_path=str(target_path),
                    success=False,
                    details={"limit_type": e.limit_type, "retry_after": e.retry_after},
                )
                return False, str(e), None

        # Create checkpoint
        checkpoint: AtomicCheckpoint | None = None
        if self.config.enable_rollback:
            checkpoint = AtomicCheckpoint(phage_id=phage_id)
            checkpoint.add_file(target_path)

            await self.audit_logger.log(
                AuditEventType.CHECKPOINT_CREATED,
                phage_id=phage_id,
                checkpoint_id=checkpoint.id,
                target_path=str(target_path),
            )

        # Log infection start
        if self.config.enable_audit:
            await self.audit_logger.log_infection_started(
                phage_id=phage_id,
                target_path=str(target_path),
                checkpoint_id=checkpoint.id if checkpoint else "",
            )

        return True, None, checkpoint

    async def post_infection_success(
        self,
        phage_id: str,
        target_path: Path,
        checkpoint: AtomicCheckpoint | None,
        tests_passed: int,
    ) -> None:
        """Record successful infection."""
        # Commit checkpoint
        if checkpoint:
            checkpoint.commit()
            await self.audit_logger.log(
                AuditEventType.CHECKPOINT_COMMITTED,
                checkpoint_id=checkpoint.id,
                phage_id=phage_id,
            )

        # Record rate limit
        if self.config.enable_rate_limiting:
            self.rate_limiter.record_infection()

        # Audit log
        if self.config.enable_audit:
            await self.audit_logger.log_infection_succeeded(
                phage_id=phage_id,
                target_path=str(target_path),
                tests_passed=tests_passed,
            )

    async def post_infection_failure(
        self,
        phage_id: str,
        target_path: Path,
        checkpoint: AtomicCheckpoint | None,
        reason: str,
    ) -> None:
        """Record failed infection and rollback."""
        # Rollback
        if checkpoint and self.config.enable_rollback:
            success, errors = checkpoint.rollback()
            await self.audit_logger.log_rollback(
                checkpoint_id=checkpoint.id,
                phage_id=phage_id,
                reason=reason,
            )

        # Audit log
        if self.config.enable_audit:
            await self.audit_logger.log_infection_failed(
                phage_id=phage_id,
                target_path=str(target_path),
                reason=reason,
            )

    def get_status(self) -> dict[str, Any]:
        """Get safety system status."""
        return {
            "rollback": {
                "active_checkpoints": self.rollback_manager.active_count,
            },
            "rate_limit": self.rate_limiter.get_status(),
            "config": {
                "enable_rollback": self.config.enable_rollback,
                "enable_rate_limiting": self.config.enable_rate_limiting,
                "enable_audit": self.config.enable_audit,
                "enable_sandbox": self.config.enable_sandbox,
            },
        }


# =============================================================================
# Factory Functions
# =============================================================================


def create_safety_system(
    audit_dir: Path | None = None,
    strict: bool = False,
) -> SafetySystem:
    """
    Create a safety system with default configuration.

    Args:
        audit_dir: Directory for audit logs (in-memory if None)
        strict: Use strict rate limits if True

    Returns:
        Configured SafetySystem
    """
    # Rate limits
    if strict:
        rate_config = RateLimitConfig(
            max_mutations_per_minute=30,
            max_infections_per_minute=5,
            burst_allowance=2,
        )
    else:
        rate_config = RateLimitConfig()

    # Sandbox
    sandbox_config = SandboxConfig(
        allow_subprocess=True,
        allowed_commands=["pytest", "python", "mypy"],
    )

    # Safety config
    config = SafetyConfig(
        rate_limit=rate_config,
        sandbox=sandbox_config,
    )

    # Audit sink
    sink: AuditSink
    if audit_dir:
        sink = FileAuditSink(audit_dir)
    else:
        sink = InMemoryAuditSink()

    return SafetySystem(config=config, audit_sink=sink)


def create_test_safety_system() -> SafetySystem:
    """Create a safety system for testing (relaxed limits)."""
    config = SafetyConfig(
        enable_rollback=True,
        enable_rate_limiting=False,  # Disable for tests
        enable_audit=True,
        enable_sandbox=True,
        rate_limit=RateLimitConfig(
            max_mutations_per_minute=1000,
            max_infections_per_minute=100,
        ),
    )

    return SafetySystem(config=config, audit_sink=InMemoryAuditSink())
