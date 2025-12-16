"""
Rollback Registry: High-level API for checkpoint management.

Per taste decision: auto-change with rollback.
The system can change freely but maintains full history.
Always reversible.

Key features:
- checkpoint(): Save state before auto-change
- rollback(): Restore to any checkpoint
- history(): Browse evolution history
- diff(): Compare any two checkpoints

Category Law (must hold):
    rollback(checkpoint(p)) == p  # Invertibility
"""

from __future__ import annotations

import logging
import threading
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING

from .checkpoint import Checkpoint, CheckpointId, CheckpointSummary
from .storage import CheckpointStorage, InMemoryCheckpointStorage, JSONCheckpointStorage

if TYPE_CHECKING:
    from ..compiler import CompiledPrompt

logger = logging.getLogger(__name__)


@dataclass
class RollbackResult:
    """Result of a rollback operation."""

    success: bool
    restored_content: str | None
    checkpoint_id: CheckpointId | None
    message: str
    reasoning_trace: tuple[str, ...]


class RollbackRegistry:
    """
    Full history with instant rollback capability.

    Per taste decision: auto-change with rollback.
    Every change is recorded. You can always go back.

    Usage:
        registry = RollbackRegistry(storage_path)

        # Save before auto-change
        checkpoint_id = registry.checkpoint(
            before=current_prompt,
            after=improved_prompt,
            reason="TextGRAD improvement from user feedback",
        )

        # View history
        for summary in registry.history(limit=10):
            print(summary)

        # Rollback if needed
        result = registry.rollback(checkpoint_id)
    """

    def __init__(
        self,
        storage: CheckpointStorage | None = None,
        storage_path: Path | None = None,
    ) -> None:
        """
        Initialize the rollback registry.

        Args:
            storage: Custom storage backend (for testing)
            storage_path: Path for JSON storage (default: ~/.kgents/prompt-history)
        """
        if storage is not None:
            self._storage = storage
        elif storage_path is not None:
            self._storage = JSONCheckpointStorage(storage_path)
        else:
            # Default storage location
            default_path = Path.home() / ".kgents" / "prompt-history"
            self._storage = JSONCheckpointStorage(default_path)

        self._current_content: str | None = None
        self._current_sections: tuple[str, ...] = ()

    def checkpoint(
        self,
        before_content: str,
        after_content: str,
        before_sections: tuple[str, ...],
        after_sections: tuple[str, ...],
        reason: str,
        reasoning_traces: tuple[str, ...] = (),
    ) -> CheckpointId:
        """
        Save state before auto-change.

        Records:
        - Full before/after content
        - Diff
        - Reason for change
        - Timestamp
        - Reasoning traces from compilation

        Args:
            before_content: Full prompt content before the change
            after_content: Full prompt content after the change
            before_sections: Section names before
            after_sections: Section names after
            reason: Why this change was made
            reasoning_traces: Accumulated reasoning from the change

        Returns:
            Checkpoint ID for later rollback
        """
        traces = list(reasoning_traces)
        traces.append(f"Creating checkpoint: {reason}")

        # Get parent ID for history chain
        parent_id = self._storage.get_latest_id()

        checkpoint = Checkpoint.create(
            before_content=before_content,
            after_content=after_content,
            before_sections=before_sections,
            after_sections=after_sections,
            reason=reason,
            reasoning_traces=tuple(traces),
            parent_id=parent_id,
        )

        self._storage.save(checkpoint)

        # Update current state
        self._current_content = after_content
        self._current_sections = after_sections

        logger.info(f"Checkpoint created: {checkpoint.id} ({reason})")
        return checkpoint.id

    def checkpoint_from_prompts(
        self,
        before: "CompiledPrompt",
        after: "CompiledPrompt",
        reason: str,
    ) -> CheckpointId:
        """
        Convenience method to checkpoint from CompiledPrompt objects.

        Extracts content and sections from the prompt objects.
        """
        # Extract reasoning traces if available
        reasoning_traces: tuple[str, ...] = ()
        if hasattr(after, "reasoning_traces"):
            reasoning_traces = after.reasoning_traces

        return self.checkpoint(
            before_content=before.content,
            after_content=after.content,
            before_sections=tuple(s.name for s in before.sections),
            after_sections=tuple(s.name for s in after.sections),
            reason=reason,
            reasoning_traces=reasoning_traces,
        )

    def rollback(self, checkpoint_id: CheckpointId) -> RollbackResult:
        """
        Restore to checkpoint.

        Does NOT delete forward history - you can roll forward again.
        Rolling back creates a new checkpoint recording the rollback.

        Args:
            checkpoint_id: ID of checkpoint to restore

        Returns:
            RollbackResult with restored content and status
        """
        traces = [f"Rolling back to checkpoint {checkpoint_id}"]

        checkpoint = self._storage.load(checkpoint_id)
        if checkpoint is None:
            traces.append(f"Checkpoint not found: {checkpoint_id}")
            return RollbackResult(
                success=False,
                restored_content=None,
                checkpoint_id=None,
                message=f"Checkpoint not found: {checkpoint_id}",
                reasoning_trace=tuple(traces),
            )

        traces.append(f"Found checkpoint from {checkpoint.timestamp.isoformat()}")
        traces.append(f"Reason for original change: {checkpoint.reason}")

        # Get current state before rollback
        current_content = self._current_content or ""
        current_sections = self._current_sections

        # Create a new checkpoint recording the rollback
        # This preserves forward history
        rollback_checkpoint_id = self.checkpoint(
            before_content=current_content,
            after_content=checkpoint.before_content,
            before_sections=current_sections,
            after_sections=checkpoint.before_sections,
            reason=f"Rollback to {checkpoint_id}",
            reasoning_traces=tuple(traces),
        )

        traces.append(f"Rollback complete, new checkpoint: {rollback_checkpoint_id}")

        return RollbackResult(
            success=True,
            restored_content=checkpoint.before_content,
            checkpoint_id=rollback_checkpoint_id,
            message=f"Rolled back to {checkpoint_id}",
            reasoning_trace=tuple(traces),
        )

    def history(self, limit: int = 20) -> list[CheckpointSummary]:
        """
        Show evolution history with summaries.

        Args:
            limit: Maximum number of entries to return

        Returns:
            List of checkpoint summaries, most recent first
        """
        return self._storage.list_summaries(limit)

    def get_checkpoint(self, checkpoint_id: CheckpointId) -> Checkpoint | None:
        """
        Get full checkpoint details.

        Args:
            checkpoint_id: ID of checkpoint to retrieve

        Returns:
            Full checkpoint, or None if not found
        """
        return self._storage.load(checkpoint_id)

    def diff(
        self,
        id1: CheckpointId,
        id2: CheckpointId,
    ) -> str | None:
        """
        Show diff between any two checkpoints.

        Computes diff of the 'after' content of each checkpoint.

        Args:
            id1: First checkpoint ID
            id2: Second checkpoint ID

        Returns:
            Unified diff string, or None if checkpoints not found
        """
        cp1 = self._storage.load(id1)
        cp2 = self._storage.load(id2)

        if cp1 is None or cp2 is None:
            return None

        return Checkpoint.compute_diff(cp1.after_content, cp2.after_content)

    def get_content_at(self, checkpoint_id: CheckpointId) -> str | None:
        """
        Get the 'after' content at a specific checkpoint.

        Args:
            checkpoint_id: Checkpoint to query

        Returns:
            The prompt content after that checkpoint, or None
        """
        checkpoint = self._storage.load(checkpoint_id)
        return checkpoint.after_content if checkpoint else None

    def set_current(self, content: str, sections: tuple[str, ...]) -> None:
        """
        Set current prompt state (for rollback reference).

        Call this after loading or compiling a prompt to establish
        the baseline for future rollbacks.
        """
        self._current_content = content
        self._current_sections = sections

    @property
    def latest_checkpoint_id(self) -> CheckpointId | None:
        """Get the most recent checkpoint ID."""
        return self._storage.get_latest_id()

    def __len__(self) -> int:
        """Number of checkpoints in history."""
        return self._storage.count()


# Singleton registry for convenience (thread-safe)
_default_registry: RollbackRegistry | None = None
_registry_lock = threading.Lock()


def get_default_registry() -> RollbackRegistry:
    """
    Get the default rollback registry (lazily initialized).

    Thread-safe: uses double-checked locking pattern.
    """
    global _default_registry
    if _default_registry is None:
        with _registry_lock:
            # Double-check after acquiring lock
            if _default_registry is None:
                _default_registry = RollbackRegistry()
    return _default_registry


__all__ = [
    "RollbackRegistry",
    "RollbackResult",
    "get_default_registry",
]
