"""
Checkpoint: Snapshot of prompt state at a point in time.

A checkpoint captures:
- Full before/after content
- Diff between states
- Reason for the change
- Timestamp
- Reasoning traces (per transparency taste decision)

Checkpoints are immutable and can be serialized for persistence.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from datetime import datetime
from typing import NewType

# Type alias for checkpoint IDs (content-addressable)
CheckpointId = NewType("CheckpointId", str)


@dataclass(frozen=True)
class CheckpointSummary:
    """
    Lightweight summary of a checkpoint for listing.

    Used for history browsing without loading full content.
    """

    id: CheckpointId
    timestamp: datetime
    reason: str
    before_token_count: int
    after_token_count: int
    sections_changed: tuple[str, ...]

    def __str__(self) -> str:
        delta = self.after_token_count - self.before_token_count
        sign = "+" if delta >= 0 else ""
        sections = ", ".join(self.sections_changed[:3])
        if len(self.sections_changed) > 3:
            sections += f" (+{len(self.sections_changed) - 3} more)"
        return (
            f"[{self.id[:8]}] {self.timestamp.isoformat(timespec='seconds')} "
            f"({sign}{delta} tokens) {self.reason[:50]}"
        )


@dataclass(frozen=True)
class Checkpoint:
    """
    Full checkpoint of prompt state.

    Captures everything needed to understand and restore a point in history.

    Attributes:
        id: Content-addressable ID (hash of before + after + reason)
        timestamp: When this checkpoint was created
        before_content: Full prompt content before the change
        after_content: Full prompt content after the change
        before_sections: Section names before
        after_sections: Section names after
        diff: Human-readable diff (unified format)
        reason: Why this change was made
        reasoning_traces: Accumulated reasoning from compilation
        parent_id: ID of the previous checkpoint (for history chain)
    """

    id: CheckpointId
    timestamp: datetime
    before_content: str
    after_content: str
    before_sections: tuple[str, ...]
    after_sections: tuple[str, ...]
    diff: str
    reason: str
    reasoning_traces: tuple[str, ...] = ()
    parent_id: CheckpointId | None = None

    @staticmethod
    def generate_id(
        before_content: str,
        after_content: str,
        reason: str,
        timestamp: datetime,
    ) -> CheckpointId:
        """
        Generate content-addressable checkpoint ID.

        Uses SHA-256 hash of content for deterministic IDs.
        """
        hasher = hashlib.sha256()
        hasher.update(before_content.encode("utf-8"))
        hasher.update(after_content.encode("utf-8"))
        hasher.update(reason.encode("utf-8"))
        hasher.update(timestamp.isoformat().encode("utf-8"))
        return CheckpointId(hasher.hexdigest()[:16])

    @staticmethod
    def compute_diff(before: str, after: str) -> str:
        """
        Compute unified diff between before and after content.

        Uses simple line-by-line diff for human readability.
        """
        import difflib

        before_lines = before.splitlines(keepends=True)
        after_lines = after.splitlines(keepends=True)

        diff = difflib.unified_diff(
            before_lines,
            after_lines,
            fromfile="before",
            tofile="after",
            lineterm="",
        )
        return "".join(diff)

    @classmethod
    def create(
        cls,
        before_content: str,
        after_content: str,
        before_sections: tuple[str, ...],
        after_sections: tuple[str, ...],
        reason: str,
        reasoning_traces: tuple[str, ...] = (),
        parent_id: CheckpointId | None = None,
    ) -> Checkpoint:
        """
        Create a new checkpoint with computed ID and diff.

        Factory method that handles ID generation and diff computation.
        """
        timestamp = datetime.now()
        checkpoint_id = cls.generate_id(before_content, after_content, reason, timestamp)
        diff = cls.compute_diff(before_content, after_content)

        return cls(
            id=checkpoint_id,
            timestamp=timestamp,
            before_content=before_content,
            after_content=after_content,
            before_sections=before_sections,
            after_sections=after_sections,
            diff=diff,
            reason=reason,
            reasoning_traces=reasoning_traces,
            parent_id=parent_id,
        )

    def summary(self) -> CheckpointSummary:
        """Create a lightweight summary for listing."""
        # Find changed sections
        before_set = set(self.before_sections)
        after_set = set(self.after_sections)
        changed = tuple(
            sorted(
                (before_set - after_set)
                | (after_set - before_set)
                | {s for s in before_set & after_set}  # Simplified: report all sections for now
            )
        )

        return CheckpointSummary(
            id=self.id,
            timestamp=self.timestamp,
            reason=self.reason,
            before_token_count=len(self.before_content) // 4,
            after_token_count=len(self.after_content) // 4,
            sections_changed=changed[:10],  # Limit for summary
        )

    def to_dict(self) -> dict:
        """Serialize checkpoint to dictionary for persistence."""
        return {
            "id": self.id,
            "timestamp": self.timestamp.isoformat(),
            "before_content": self.before_content,
            "after_content": self.after_content,
            "before_sections": list(self.before_sections),
            "after_sections": list(self.after_sections),
            "diff": self.diff,
            "reason": self.reason,
            "reasoning_traces": list(self.reasoning_traces),
            "parent_id": self.parent_id,
        }

    @classmethod
    def from_dict(cls, data: dict) -> Checkpoint:
        """Deserialize checkpoint from dictionary."""
        return cls(
            id=CheckpointId(data["id"]),
            timestamp=datetime.fromisoformat(data["timestamp"]),
            before_content=data["before_content"],
            after_content=data["after_content"],
            before_sections=tuple(data["before_sections"]),
            after_sections=tuple(data["after_sections"]),
            diff=data["diff"],
            reason=data["reason"],
            reasoning_traces=tuple(data.get("reasoning_traces", [])),
            parent_id=CheckpointId(data["parent_id"]) if data.get("parent_id") else None,
        )


__all__ = [
    "CheckpointId",
    "CheckpointSummary",
    "Checkpoint",
]
