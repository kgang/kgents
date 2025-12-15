"""
OrchestrationLog: Persistence for multi-agent orchestrations.

Enables:
- Save orchestration state to disk
- Resume after quit/crash
- Time-travel via checkpoints
- Deterministic replay

Architecture:
    TownFlux.step()
         │
         ▼
    EventBus ─────► OrchestrationLog
                         │
         ┌───────────────┼───────────────┐
         ▼               ▼               ▼
    events.jsonl   checkpoints/    metadata.json
    (append-only)   (per-phase)    (session info)

Pattern adapted from:
- agents/d/persistent.py: Atomic writes + JSONL history
- Signal snapshots: Point-in-time state capture

See: plans/purring-squishing-duckling.md Phase 2
"""

from __future__ import annotations

import json
import os
import tempfile
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any, AsyncIterator

if TYPE_CHECKING:
    from agents.i.reactive.signal import Snapshot
    from agents.town.flux import TownEvent, TownPhase


# =============================================================================
# Checkpoint: Full State Snapshot
# =============================================================================


@dataclass(frozen=True)
class Checkpoint:
    """
    Full state snapshot at a point in time.

    Captures everything needed to restore simulation state:
    - Environment (citizens, coalitions, regions)
    - Simulation state (phase, day, counters)
    - Widget snapshots (for UI restoration)

    Immutable for safe storage and comparison.
    """

    # Identity
    checkpoint_id: str
    tick: int
    timestamp: datetime

    # Simulation state
    phase: str  # TownPhase.name
    day: int
    total_events: int
    total_tokens: int

    # Environment state (serialized)
    environment_state: dict[str, Any]

    # Citizen states (id → serialized state)
    citizen_states: dict[str, Any]

    # Coalition state (id → serialized)
    coalition_state: dict[str, Any]

    # Widget signal snapshots (name → snapshot dict)
    widget_snapshots: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Serialize to JSON-compatible dict."""
        return {
            "checkpoint_id": self.checkpoint_id,
            "tick": self.tick,
            "timestamp": self.timestamp.isoformat(),
            "phase": self.phase,
            "day": self.day,
            "total_events": self.total_events,
            "total_tokens": self.total_tokens,
            "environment_state": self.environment_state,
            "citizen_states": self.citizen_states,
            "coalition_state": self.coalition_state,
            "widget_snapshots": self.widget_snapshots,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Checkpoint:
        """Deserialize from dict."""
        return cls(
            checkpoint_id=data["checkpoint_id"],
            tick=data["tick"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            phase=data["phase"],
            day=data["day"],
            total_events=data["total_events"],
            total_tokens=data["total_tokens"],
            environment_state=data["environment_state"],
            citizen_states=data["citizen_states"],
            coalition_state=data["coalition_state"],
            widget_snapshots=data.get("widget_snapshots", {}),
        )


# =============================================================================
# OrchestrationMetadata: Session Info
# =============================================================================


@dataclass
class OrchestrationMetadata:
    """Session metadata for orchestration."""

    orchestration_id: str
    name: str
    created_at: datetime
    last_modified: datetime
    phase_count: int  # Number of phases in simulation
    citizen_count: int
    checkpoint_ids: list[str] = field(default_factory=list)
    current_tick: int = 0
    status: str = "active"  # active, paused, completed

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dict."""
        return {
            "orchestration_id": self.orchestration_id,
            "name": self.name,
            "created_at": self.created_at.isoformat(),
            "last_modified": self.last_modified.isoformat(),
            "phase_count": self.phase_count,
            "citizen_count": self.citizen_count,
            "checkpoint_ids": self.checkpoint_ids,
            "current_tick": self.current_tick,
            "status": self.status,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> OrchestrationMetadata:
        """Deserialize from dict."""
        return cls(
            orchestration_id=data["orchestration_id"],
            name=data["name"],
            created_at=datetime.fromisoformat(data["created_at"]),
            last_modified=datetime.fromisoformat(data["last_modified"]),
            phase_count=data["phase_count"],
            citizen_count=data["citizen_count"],
            checkpoint_ids=data.get("checkpoint_ids", []),
            current_tick=data.get("current_tick", 0),
            status=data.get("status", "active"),
        )


# =============================================================================
# OrchestrationLog: Append-Only Event Log with Checkpoints
# =============================================================================


@dataclass
class OrchestrationLog:
    """
    Append-only event log with periodic checkpoints.

    Directory structure:
        orchestration_dir/
        ├── metadata.json      # Session info
        ├── events.jsonl       # Append-only event log
        └── checkpoints/
            ├── cp_0001.json   # Checkpoint after phase 1
            ├── cp_0002.json   # Checkpoint after phase 2
            └── ...

    Thread-safe via atomic writes (temp file + rename).
    """

    log_dir: Path
    checkpoint_on_phase: bool = True  # Create checkpoint after each phase
    max_checkpoints: int = 100  # Limit checkpoint storage

    # Runtime state (not persisted directly)
    _metadata: OrchestrationMetadata | None = field(default=None, repr=False)
    _events_file: Path = field(init=False, repr=False)
    _checkpoint_dir: Path = field(init=False, repr=False)
    _tick: int = field(default=0, repr=False)
    _last_phase: str | None = field(default=None, repr=False)

    def __post_init__(self) -> None:
        """Initialize paths."""
        self.log_dir = Path(self.log_dir)
        self._events_file = self.log_dir / "events.jsonl"
        self._checkpoint_dir = self.log_dir / "checkpoints"

    # --- Initialization ---

    def initialize(
        self,
        orchestration_id: str,
        name: str,
        phase_count: int,
        citizen_count: int,
    ) -> OrchestrationMetadata:
        """
        Initialize new orchestration log.

        Creates directory structure and metadata file.
        """
        # Create directories
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self._checkpoint_dir.mkdir(exist_ok=True)

        # Create metadata
        now = datetime.now()
        self._metadata = OrchestrationMetadata(
            orchestration_id=orchestration_id,
            name=name,
            created_at=now,
            last_modified=now,
            phase_count=phase_count,
            citizen_count=citizen_count,
        )

        # Write metadata atomically
        self._write_metadata()

        # Create empty events file
        self._events_file.touch()

        return self._metadata

    def load(self) -> OrchestrationMetadata:
        """
        Load existing orchestration log.

        Raises FileNotFoundError if not found.
        """
        metadata_path = self.log_dir / "metadata.json"
        if not metadata_path.exists():
            raise FileNotFoundError(f"No orchestration at {self.log_dir}")

        with open(metadata_path) as f:
            data = json.load(f)

        self._metadata = OrchestrationMetadata.from_dict(data)
        self._tick = self._metadata.current_tick

        return self._metadata

    # --- Event Logging ---

    async def append(self, event: "TownEvent") -> int:
        """
        Append event to log.

        Returns new tick number.
        """
        self._tick += 1

        # Serialize event
        event_data = {
            "tick": self._tick,
            "logged_at": datetime.now().isoformat(),
            "event": event.to_dict(),
        }

        # Append to JSONL atomically
        self._append_jsonl(event_data)

        # Update metadata
        if self._metadata:
            self._metadata.current_tick = self._tick
            self._metadata.last_modified = datetime.now()

        # Check for phase transition → checkpoint
        if self.checkpoint_on_phase and self._last_phase != event.phase.name:
            self._last_phase = event.phase.name

        return self._tick

    def _append_jsonl(self, data: dict[str, Any]) -> None:
        """Append line to JSONL file."""
        line = json.dumps(data) + "\n"
        with open(self._events_file, "a") as f:
            f.write(line)

    # --- Checkpointing ---

    async def checkpoint(
        self,
        phase: "TownPhase",
        day: int,
        total_events: int,
        total_tokens: int,
        environment_state: dict[str, Any],
        citizen_states: dict[str, Any],
        coalition_state: dict[str, Any],
        widget_snapshots: dict[str, Any] | None = None,
    ) -> Checkpoint:
        """
        Create full checkpoint.

        Called after each phase to enable time-travel.
        """
        checkpoint_id = f"cp_{self._tick:06d}"

        cp = Checkpoint(
            checkpoint_id=checkpoint_id,
            tick=self._tick,
            timestamp=datetime.now(),
            phase=phase.name,
            day=day,
            total_events=total_events,
            total_tokens=total_tokens,
            environment_state=environment_state,
            citizen_states=citizen_states,
            coalition_state=coalition_state,
            widget_snapshots=widget_snapshots or {},
        )

        # Write checkpoint atomically
        checkpoint_path = self._checkpoint_dir / f"{checkpoint_id}.json"
        self._write_atomic(checkpoint_path, cp.to_dict())

        # Update metadata
        if self._metadata:
            self._metadata.checkpoint_ids.append(checkpoint_id)
            self._write_metadata()

        # Prune old checkpoints if needed
        self._prune_checkpoints()

        return cp

    async def restore_checkpoint(self, checkpoint_id: str) -> Checkpoint:
        """
        Load checkpoint from disk.

        Raises FileNotFoundError if not found.
        """
        checkpoint_path = self._checkpoint_dir / f"{checkpoint_id}.json"
        if not checkpoint_path.exists():
            raise FileNotFoundError(f"Checkpoint not found: {checkpoint_id}")

        with open(checkpoint_path) as f:
            data = json.load(f)

        return Checkpoint.from_dict(data)

    def list_checkpoints(self) -> list[str]:
        """List all checkpoint IDs in order."""
        if self._metadata:
            return list(self._metadata.checkpoint_ids)
        return []

    def _prune_checkpoints(self) -> None:
        """Remove old checkpoints if exceeding max_checkpoints."""
        if not self._metadata:
            return

        while len(self._metadata.checkpoint_ids) > self.max_checkpoints:
            old_id = self._metadata.checkpoint_ids.pop(0)
            old_path = self._checkpoint_dir / f"{old_id}.json"
            if old_path.exists():
                old_path.unlink()

    # --- Replay ---

    async def replay_from(
        self, checkpoint_id: str | None = None
    ) -> AsyncIterator[dict[str, Any]]:
        """
        Replay events from checkpoint (or beginning).

        Yields event dicts in order.
        """
        start_tick = 0
        if checkpoint_id:
            cp = await self.restore_checkpoint(checkpoint_id)
            start_tick = cp.tick

        with open(self._events_file) as f:
            for line in f:
                if not line.strip():
                    continue
                data = json.loads(line)
                if data["tick"] > start_tick:
                    yield data["event"]

    async def event_count(self) -> int:
        """Count total events in log."""
        count = 0
        with open(self._events_file) as f:
            for line in f:
                if line.strip():
                    count += 1
        return count

    # --- Atomic Writes ---

    def _write_metadata(self) -> None:
        """Write metadata atomically."""
        if self._metadata:
            metadata_path = self.log_dir / "metadata.json"
            self._write_atomic(metadata_path, self._metadata.to_dict())

    def _write_atomic(self, path: Path, data: dict[str, Any]) -> None:
        """
        Write JSON file atomically.

        Uses temp file + rename for crash safety.
        """
        # Write to temp file
        fd, temp_path = tempfile.mkstemp(
            dir=path.parent, prefix=".tmp_", suffix=".json"
        )
        try:
            with os.fdopen(fd, "w") as f:
                json.dump(data, f, indent=2)
            # Atomic rename
            os.rename(temp_path, path)
        except Exception:
            # Clean up temp file on error
            if os.path.exists(temp_path):
                os.unlink(temp_path)
            raise

    # --- Status ---

    def set_status(self, status: str) -> None:
        """Update orchestration status."""
        if self._metadata:
            self._metadata.status = status
            self._metadata.last_modified = datetime.now()
            self._write_metadata()

    @property
    def metadata(self) -> OrchestrationMetadata | None:
        """Get current metadata."""
        return self._metadata

    @property
    def tick(self) -> int:
        """Current tick number."""
        return self._tick


# =============================================================================
# Factory Functions
# =============================================================================


def create_orchestration_log(
    base_dir: Path | str,
    orchestration_id: str,
    name: str = "Untitled Orchestration",
    phase_count: int = 4,
    citizen_count: int = 5,
) -> OrchestrationLog:
    """
    Create new orchestration log.

    Creates directory at base_dir/orchestration_id/.
    """
    log_dir = Path(base_dir) / orchestration_id
    log = OrchestrationLog(log_dir=log_dir)
    log.initialize(
        orchestration_id=orchestration_id,
        name=name,
        phase_count=phase_count,
        citizen_count=citizen_count,
    )
    return log


def load_orchestration_log(log_dir: Path | str) -> OrchestrationLog:
    """
    Load existing orchestration log.

    Raises FileNotFoundError if not found.
    """
    log = OrchestrationLog(log_dir=Path(log_dir))
    log.load()
    return log


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    "Checkpoint",
    "OrchestrationMetadata",
    "OrchestrationLog",
    "create_orchestration_log",
    "load_orchestration_log",
]
