"""
StateCrystal: Linearity-Aware Checkpoints with Comonadic Lineage.

A StateCrystal is a frozen snapshot of agent state that:
- Preserves PRESERVED fragments verbatim
- Summarizes DROPPABLE history
- Tracks comonadic lineage (parent_crystal)
- Supports TTL-based expiration with pinning

CrystallizationEngine handles:
- crystallize(): Snapshot ContextWindow to StateCrystal
- resume(): Restore ContextWindow from StateCrystal
- reap(): Clean up expired crystals (respects pinned)

AGENTESE: self.stream.crystal

Phase 2.4 Implementation.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any
from uuid import uuid4

from .context_window import ContextWindow, Turn, TurnRole
from .linearity import LinearityMap, ResourceClass


class TaskStatus(str, Enum):
    """Status of the task when crystallized."""

    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    YIELDED = "yielded"  # Semaphore yield
    FAILED = "failed"


@dataclass
class TaskState:
    """
    State of the current task.

    Captures what the agent was working on when crystallized.
    """

    task_id: str
    description: str
    status: TaskStatus = TaskStatus.ACTIVE
    progress: float = 0.0  # 0.0 - 1.0
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "task_id": self.task_id,
            "description": self.description,
            "status": self.status.value,
            "progress": self.progress,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "TaskState":
        """Create from dictionary."""
        return cls(
            task_id=data["task_id"],
            description=data["description"],
            status=TaskStatus(data.get("status", "active")),
            progress=data.get("progress", 0.0),
            metadata=data.get("metadata", {}),
        )


@dataclass(frozen=True)
class FocusFragment:
    """
    A verbatim-preserved piece of context.

    These fragments are marked PRESERVED in the linearity map and
    must survive crystallization without summarization.
    """

    fragment_id: str
    content: str
    role: TurnRole
    created_at: datetime
    rationale: str  # Why this was preserved

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "fragment_id": self.fragment_id,
            "content": self.content,
            "role": self.role.value,
            "created_at": self.created_at.isoformat(),
            "rationale": self.rationale,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "FocusFragment":
        """Create from dictionary."""
        return cls(
            fragment_id=data["fragment_id"],
            content=data["content"],
            role=TurnRole(data["role"]),
            created_at=datetime.fromisoformat(data["created_at"]),
            rationale=data["rationale"],
        )


@dataclass
class StateCrystal:
    """
    A frozen checkpoint of agent state.

    The crystal captures:
    - Task state: What was being worked on
    - Working memory: Key-value store of agent memory
    - History summary: Compressed DROPPABLE history
    - Focus fragments: Verbatim PRESERVED content
    - Comonadic lineage: Parent crystal reference

    Lifecycle:
    - TTL controls automatic expiration
    - cherish() pins from reaping
    - Pinned crystals survive until explicitly deleted

    Example:
        # Create checkpoint
        crystal = engine.crystallize(window, task_state)

        # Later: resume
        window = engine.resume(crystal.crystal_id)

        # Pin important crystals
        crystal.cherish()
    """

    crystal_id: str
    agent: str
    created_at: datetime

    # Core state
    task_state: TaskState
    working_memory: dict[str, Any]

    # Compressed history (DROPPABLE masked)
    history_summary: str

    # Focus fragments (PRESERVED: verbatim)
    focus_fragments: list[FocusFragment]

    # Comonadic lineage
    parent_crystal: str | None = None
    branch_depth: int = 0

    # Lifecycle
    ttl: timedelta = field(default_factory=lambda: timedelta(hours=24))
    pinned: bool = False

    # Internal tracking
    _reaped: bool = False

    def cherish(self) -> None:
        """
        Pin this crystal from reaping.

        Cherished crystals survive TTL expiration until explicitly deleted.
        Use for important checkpoints worth preserving.
        """
        object.__setattr__(self, "pinned", True)

    def uncherish(self) -> None:
        """Unpin this crystal, allowing TTL-based reaping."""
        object.__setattr__(self, "pinned", False)

    @property
    def expires_at(self) -> datetime:
        """When this crystal expires (if not pinned)."""
        return self.created_at + self.ttl

    @property
    def is_expired(self) -> bool:
        """True if crystal has expired (not counting pinned status)."""
        return datetime.now(UTC) > self.expires_at

    @property
    def should_reap(self) -> bool:
        """True if crystal should be reaped (expired and not pinned)."""
        return self.is_expired and not self.pinned

    @property
    def lineage_path(self) -> list[str]:
        """
        Get the lineage path from this crystal.

        Returns [this_id, parent_id, grandparent_id, ...].
        Note: Only includes IDs, not actual crystal objects.
        """
        path = [self.crystal_id]
        if self.parent_crystal:
            path.append(self.parent_crystal)
        return path

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "crystal_id": self.crystal_id,
            "agent": self.agent,
            "created_at": self.created_at.isoformat(),
            "task_state": self.task_state.to_dict(),
            "working_memory": self.working_memory,
            "history_summary": self.history_summary,
            "focus_fragments": [f.to_dict() for f in self.focus_fragments],
            "parent_crystal": self.parent_crystal,
            "branch_depth": self.branch_depth,
            "ttl_seconds": self.ttl.total_seconds(),
            "pinned": self.pinned,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "StateCrystal":
        """Deserialize from dictionary."""
        return cls(
            crystal_id=data["crystal_id"],
            agent=data["agent"],
            created_at=datetime.fromisoformat(data["created_at"]),
            task_state=TaskState.from_dict(data["task_state"]),
            working_memory=data.get("working_memory", {}),
            history_summary=data.get("history_summary", ""),
            focus_fragments=[
                FocusFragment.from_dict(f) for f in data.get("focus_fragments", [])
            ],
            parent_crystal=data.get("parent_crystal"),
            branch_depth=data.get("branch_depth", 0),
            ttl=timedelta(seconds=data.get("ttl_seconds", 86400)),
            pinned=data.get("pinned", False),
        )


@dataclass
class CrystallizationResult:
    """Result of a crystallization operation."""

    success: bool
    crystal: StateCrystal | None = None
    preserved_count: int = 0
    dropped_count: int = 0
    summary_length: int = 0
    error: str | None = None


@dataclass
class ResumeResult:
    """Result of a resume operation."""

    success: bool
    window: ContextWindow | None = None
    crystal: StateCrystal | None = None
    restored_fragments: int = 0
    error: str | None = None


@dataclass
class ReapResult:
    """Result of a reap operation."""

    reaped_count: int = 0
    skipped_pinned: int = 0
    skipped_unexpired: int = 0
    crystal_ids: list[str] = field(default_factory=list)


class CrystalReaper:
    """
    Manages crystal lifecycle and cleanup.

    The reaper:
    - Tracks crystal expiration
    - Respects pinned crystals
    - Provides bulk cleanup operations
    """

    def __init__(self, storage_path: Path | None = None) -> None:
        """Initialize reaper with optional persistent storage."""
        self._crystals: dict[str, StateCrystal] = {}
        self._storage_path = storage_path
        if storage_path:
            storage_path.mkdir(parents=True, exist_ok=True)
            self._load_crystals()

    def register(self, crystal: StateCrystal) -> None:
        """Register a crystal for lifecycle management."""
        self._crystals[crystal.crystal_id] = crystal
        if self._storage_path:
            self._save_crystal(crystal)

    def get(self, crystal_id: str) -> StateCrystal | None:
        """Get a crystal by ID."""
        return self._crystals.get(crystal_id)

    def reap(self) -> ReapResult:
        """
        Reap expired, non-pinned crystals.

        Returns statistics about the reaping operation.
        """
        result = ReapResult()

        to_reap = []
        for cid, crystal in self._crystals.items():
            if crystal.pinned:
                result.skipped_pinned += 1
            elif not crystal.is_expired:
                result.skipped_unexpired += 1
            else:
                to_reap.append(cid)

        for cid in to_reap:
            del self._crystals[cid]
            result.crystal_ids.append(cid)
            result.reaped_count += 1

            if self._storage_path:
                crystal_file = self._storage_path / f"{cid}.json"
                if crystal_file.exists():
                    crystal_file.unlink()

        return result

    def all_crystals(self) -> list[StateCrystal]:
        """Get all tracked crystals."""
        return list(self._crystals.values())

    def pinned_crystals(self) -> list[StateCrystal]:
        """Get all pinned crystals."""
        return [c for c in self._crystals.values() if c.pinned]

    def expired_crystals(self) -> list[StateCrystal]:
        """Get all expired crystals."""
        return [c for c in self._crystals.values() if c.is_expired]

    def clear(self) -> int:
        """Clear all crystals (ignores pinned status). Returns count."""
        count = len(self._crystals)
        self._crystals.clear()
        if self._storage_path:
            for f in self._storage_path.glob("*.json"):
                f.unlink()
        return count

    def _save_crystal(self, crystal: StateCrystal) -> None:
        """Save crystal to storage."""
        if self._storage_path:
            crystal_file = self._storage_path / f"{crystal.crystal_id}.json"
            crystal_file.write_text(json.dumps(crystal.to_dict(), indent=2))

    def _load_crystals(self) -> None:
        """Load crystals from storage."""
        if self._storage_path:
            for f in self._storage_path.glob("*.json"):
                try:
                    data = json.loads(f.read_text())
                    crystal = StateCrystal.from_dict(data)
                    self._crystals[crystal.crystal_id] = crystal
                except Exception:
                    pass  # Skip invalid files


class CrystallizationEngine:
    """
    Engine for creating and resuming StateCrystals.

    The engine handles:
    - Extracting PRESERVED fragments verbatim
    - Summarizing DROPPABLE history
    - Tracking comonadic lineage
    - Persistence and retrieval
    """

    def __init__(
        self,
        reaper: CrystalReaper | None = None,
        storage_path: Path | None = None,
    ) -> None:
        """Initialize engine with optional reaper and storage."""
        self._storage_path = storage_path
        self._reaper = reaper or CrystalReaper(storage_path)

    async def crystallize(
        self,
        window: ContextWindow,
        task_state: TaskState,
        agent: str,
        working_memory: dict[str, Any] | None = None,
        parent_crystal: StateCrystal | None = None,
        ttl: timedelta | None = None,
    ) -> CrystallizationResult:
        """
        Crystallize a ContextWindow into a StateCrystal.

        This extracts PRESERVED fragments verbatim and summarizes
        DROPPABLE history into a compressed summary.

        Args:
            window: The ContextWindow to crystallize
            task_state: Current task state
            agent: Agent identifier
            working_memory: Optional key-value memory
            parent_crystal: Optional parent for lineage tracking
            ttl: Optional TTL override

        Returns:
            CrystallizationResult with the new crystal
        """
        try:
            # Extract preserved fragments verbatim
            focus_fragments: list[FocusFragment] = []
            preserved_turns = window.preserved_turns()

            for turn in preserved_turns:
                fragment = FocusFragment(
                    fragment_id=f"frag_{uuid4().hex[:8]}",
                    content=turn.content,
                    role=turn.role,
                    created_at=turn.timestamp,
                    rationale="PRESERVED resource class",
                )
                focus_fragments.append(fragment)

            # Summarize droppable history
            droppable_turns = window.droppable_turns()
            history_summary = self._summarize_turns(droppable_turns)

            # Calculate lineage
            branch_depth = 0
            parent_id = None
            if parent_crystal:
                parent_id = parent_crystal.crystal_id
                branch_depth = parent_crystal.branch_depth + 1

            # Create crystal
            crystal = StateCrystal(
                crystal_id=f"crystal_{uuid4().hex[:12]}",
                agent=agent,
                created_at=datetime.now(UTC),
                task_state=task_state,
                working_memory=working_memory or {},
                history_summary=history_summary,
                focus_fragments=focus_fragments,
                parent_crystal=parent_id,
                branch_depth=branch_depth,
                ttl=ttl or timedelta(hours=24),
            )

            # Register with reaper
            self._reaper.register(crystal)

            return CrystallizationResult(
                success=True,
                crystal=crystal,
                preserved_count=len(focus_fragments),
                dropped_count=len(droppable_turns),
                summary_length=len(history_summary),
            )

        except Exception as e:
            return CrystallizationResult(
                success=False,
                error=str(e),
            )

    async def resume(
        self,
        crystal_id: str,
        max_tokens: int = 100_000,
    ) -> ResumeResult:
        """
        Resume a ContextWindow from a StateCrystal.

        Reconstructs the window with:
        1. History summary as SYSTEM turn
        2. Focus fragments restored verbatim

        Args:
            crystal_id: ID of the crystal to resume
            max_tokens: Max tokens for the new window

        Returns:
            ResumeResult with the restored window
        """
        crystal = self._reaper.get(crystal_id)
        if crystal is None:
            return ResumeResult(
                success=False,
                error=f"Crystal not found: {crystal_id}",
            )

        try:
            # Create new window
            window = ContextWindow(max_tokens=max_tokens)

            # Add history summary as system context
            if crystal.history_summary:
                window.append(
                    TurnRole.SYSTEM,
                    f"[Resumed from crystal {crystal.crystal_id}]\n\n"
                    f"Previous context summary:\n{crystal.history_summary}",
                )

            # Restore focus fragments verbatim
            for fragment in crystal.focus_fragments:
                turn = window.append(
                    fragment.role,
                    fragment.content,
                    metadata={"restored_from": crystal.crystal_id},
                )
                # Mark as PRESERVED
                window.promote_turn(
                    turn,
                    ResourceClass.PRESERVED,
                    f"restored from crystal: {fragment.rationale}",
                )

            return ResumeResult(
                success=True,
                window=window,
                crystal=crystal,
                restored_fragments=len(crystal.focus_fragments),
            )

        except Exception as e:
            return ResumeResult(
                success=False,
                error=str(e),
            )

    def get_crystal(self, crystal_id: str) -> StateCrystal | None:
        """Get a crystal by ID."""
        return self._reaper.get(crystal_id)

    def get_lineage(self, crystal_id: str) -> list[StateCrystal]:
        """
        Get the full lineage of a crystal.

        Returns [crystal, parent, grandparent, ...].
        """
        lineage = []
        current_id: str | None = crystal_id

        while current_id:
            crystal = self._reaper.get(current_id)
            if crystal is None:
                break
            lineage.append(crystal)
            current_id = crystal.parent_crystal

        return lineage

    def reap(self) -> ReapResult:
        """Reap expired crystals."""
        return self._reaper.reap()

    @property
    def reaper(self) -> CrystalReaper:
        """Access the reaper directly."""
        return self._reaper

    def _summarize_turns(self, turns: list[Turn]) -> str:
        """
        Summarize a list of turns into compressed history.

        This is a simple implementation - production would use LLM.
        """
        if not turns:
            return ""

        summaries = []
        for turn in turns[:20]:  # Limit to recent 20
            role = turn.role.value
            content_preview = (
                turn.content[:100] + "..." if len(turn.content) > 100 else turn.content
            )
            summaries.append(f"[{role}] {content_preview}")

        return "\n".join(summaries)


# === Factory Functions ===


def create_crystal_engine(
    storage_path: Path | None = None,
) -> CrystallizationEngine:
    """Create a CrystallizationEngine with optional persistence."""
    return CrystallizationEngine(storage_path=storage_path)


def create_task_state(
    task_id: str | None = None,
    description: str = "",
    status: TaskStatus = TaskStatus.ACTIVE,
    progress: float = 0.0,
) -> TaskState:
    """Create a TaskState for crystallization."""
    return TaskState(
        task_id=task_id or f"task_{uuid4().hex[:8]}",
        description=description,
        status=status,
        progress=progress,
    )
