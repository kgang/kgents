"""
N-Phase Session State Management.

Provides stateful sessions that track phase progress across requests.
Phase state lives in the Session Router, not in LLM context,
enabling persistence across context boundaries.

Key Design Decisions:
- D1: Phase state lives in Session Router (persists across context exhaustion)
- D4: Checkpoint at phase boundaries + on-demand
- D5: Handle accumulation per phase

See: plans/nphase-native-integration.md, docs/skills/n-phase-cycle/
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from protocols.nphase.operad import (
    NPhase,
    NPhaseState,
    is_valid_transition,
    next_phase,
)


@dataclass
class Handle:
    """
    A handle accumulated during a phase.

    Handles are AGENTESE paths that have been resolved during
    session execution. They represent acquired knowledge/artifacts.

    Example:
        Handle(
            path="world.codebase.file.manifest",
            phase=NPhase.UNDERSTAND,
            content={"file": "session.py", "lines": 100},
        )
    """

    path: str  # AGENTESE path
    phase: NPhase  # Phase when acquired
    content: Any  # Resolved content
    created_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "path": self.path,
            "phase": self.phase.name,
            "content": self.content,
            "created_at": self.created_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Handle:
        """Deserialize from dictionary."""
        return cls(
            path=data["path"],
            phase=NPhase[data["phase"]],
            content=data.get("content"),
            created_at=datetime.fromisoformat(data["created_at"])
            if "created_at" in data
            else datetime.now(),
        )


@dataclass
class PhaseLedgerEntry:
    """
    Record of a phase transition.

    The ledger provides an audit trail of all phase transitions,
    enabling analysis and debugging of session flow.
    """

    from_phase: NPhase
    to_phase: NPhase
    timestamp: datetime
    payload: Any  # What triggered the transition
    cycle_count: int

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "from_phase": self.from_phase.name,
            "to_phase": self.to_phase.name,
            "timestamp": self.timestamp.isoformat(),
            "payload": self.payload,
            "cycle_count": self.cycle_count,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> PhaseLedgerEntry:
        """Deserialize from dictionary."""
        return cls(
            from_phase=NPhase[data["from_phase"]],
            to_phase=NPhase[data["to_phase"]],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            payload=data.get("payload"),
            cycle_count=data.get("cycle_count", 0),
        )


@dataclass
class SessionCheckpoint:
    """
    Snapshot of session state at a phase boundary.

    Checkpoints enable rollback and session handoff.
    Created automatically at phase transitions and on-demand.

    Decision D4: Checkpoint at phase boundaries + on-demand.
    """

    id: str
    session_id: str
    phase: NPhase
    cycle_count: int
    handles: list[Handle]
    entropy_spent: dict[str, float]
    created_at: datetime
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "id": self.id,
            "session_id": self.session_id,
            "phase": self.phase.name,
            "cycle_count": self.cycle_count,
            "handles": [h.to_dict() for h in self.handles],
            "entropy_spent": dict(self.entropy_spent),
            "created_at": self.created_at.isoformat(),
            "metadata": dict(self.metadata),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> SessionCheckpoint:
        """Deserialize from dictionary."""
        return cls(
            id=data["id"],
            session_id=data["session_id"],
            phase=NPhase[data["phase"]],
            cycle_count=data.get("cycle_count", 0),
            handles=[Handle.from_dict(h) for h in data.get("handles", [])],
            entropy_spent=dict(data.get("entropy_spent", {})),
            created_at=datetime.fromisoformat(data["created_at"])
            if "created_at" in data
            else datetime.now(),
            metadata=dict(data.get("metadata", {})),
        )


@dataclass
class NPhaseSession:
    """
    Session with embedded N-Phase state.

    The session router maintains phase state across requests,
    independent of LLM context. This enables:
    - Persistence across context exhaustion
    - Checkpoint/restore for recovery
    - Handle accumulation per phase
    - Audit trail via ledger

    Decision D1: Phase state lives here, not in LLM context.

    Example:
        session = create_session("Implement feature X")
        session.advance_phase(NPhase.ACT)
        session.add_handle("world.file.content", {"file": "foo.py"})
        checkpoint = session.checkpoint({"reason": "before test run"})
    """

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    title: str = ""
    phase_state: NPhaseState = field(default_factory=NPhaseState)
    checkpoints: list[SessionCheckpoint] = field(default_factory=list)
    handles: list[Handle] = field(default_factory=list)
    ledger: list[PhaseLedgerEntry] = field(default_factory=list)
    entropy_spent: dict[str, float] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    last_touched: datetime = field(default_factory=datetime.now)
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def current_phase(self) -> NPhase:
        """Get current phase."""
        return self.phase_state.current_phase

    @property
    def cycle_count(self) -> int:
        """Get current cycle count."""
        return self.phase_state.cycle_count

    def can_advance_to(self, target: NPhase) -> bool:
        """Check if transition to target is valid."""
        return is_valid_transition(self.current_phase, target)

    def advance_phase(
        self,
        target: NPhase | None = None,
        payload: Any = None,
        auto_checkpoint: bool = True,
    ) -> PhaseLedgerEntry:
        """
        Advance to target phase (or next phase if target is None).

        Args:
            target: Target phase. If None, advances to next in cycle.
            payload: What triggered the transition (for audit).
            auto_checkpoint: If True, create checkpoint before advancing.

        Returns:
            Ledger entry recording the transition.

        Raises:
            ValueError: If transition is invalid.
        """
        if target is None:
            target = next_phase(self.current_phase)

        if not self.can_advance_to(target):
            raise ValueError(
                f"Invalid transition: {self.current_phase.name} → {target.name}"
            )

        # Auto-checkpoint at phase boundary
        if auto_checkpoint:
            self.checkpoint({"trigger": "auto", "reason": "phase_boundary"})

        from_phase = self.current_phase

        # Check for cycle completion (REFLECT → UNDERSTAND)
        if from_phase == NPhase.REFLECT and target == NPhase.UNDERSTAND:
            self.phase_state.cycle_count += 1

        self.phase_state.current_phase = target
        self.last_touched = datetime.now()

        entry = PhaseLedgerEntry(
            from_phase=from_phase,
            to_phase=target,
            timestamp=self.last_touched,
            payload=payload,
            cycle_count=self.cycle_count,
        )
        self.ledger.append(entry)

        return entry

    def checkpoint(self, metadata: dict[str, Any] | None = None) -> SessionCheckpoint:
        """
        Create checkpoint at current state.

        Args:
            metadata: Optional metadata about the checkpoint.

        Returns:
            The created checkpoint.
        """
        cp = SessionCheckpoint(
            id=str(uuid.uuid4()),
            session_id=self.id,
            phase=self.current_phase,
            cycle_count=self.cycle_count,
            handles=list(self.handles),  # Copy
            entropy_spent=dict(self.entropy_spent),  # Copy
            created_at=datetime.now(),
            metadata=metadata or {},
        )
        self.checkpoints.append(cp)
        return cp

    def restore(self, checkpoint_id: str) -> None:
        """
        Restore session state from checkpoint.

        Args:
            checkpoint_id: ID of checkpoint to restore.

        Raises:
            ValueError: If checkpoint not found.
        """
        cp = next((c for c in self.checkpoints if c.id == checkpoint_id), None)
        if cp is None:
            raise ValueError(f"Checkpoint not found: {checkpoint_id}")

        self.phase_state.current_phase = cp.phase
        self.phase_state.cycle_count = cp.cycle_count
        self.handles = list(cp.handles)
        self.entropy_spent = dict(cp.entropy_spent)
        self.last_touched = datetime.now()

        # Add ledger entry for restore
        self.ledger.append(
            PhaseLedgerEntry(
                from_phase=self.current_phase,
                to_phase=cp.phase,
                timestamp=self.last_touched,
                payload={"restored_from": checkpoint_id},
                cycle_count=cp.cycle_count,
            )
        )

    def add_handle(self, path: str, content: Any) -> Handle:
        """
        Add a handle acquired in current phase.

        Args:
            path: AGENTESE path of the handle.
            content: Resolved content.

        Returns:
            The created handle.
        """
        handle = Handle(
            path=path,
            phase=self.current_phase,
            content=content,
        )
        self.handles.append(handle)
        return handle

    def get_handles_for_phase(self, phase: NPhase) -> list[Handle]:
        """Get all handles acquired in a specific phase."""
        return [h for h in self.handles if h.phase == phase]

    def spend_entropy(self, category: str, amount: float) -> None:
        """
        Record entropy expenditure.

        Args:
            category: Entropy category (e.g., "llm", "search").
            amount: Amount spent.
        """
        if category not in self.entropy_spent:
            self.entropy_spent[category] = 0.0
        self.entropy_spent[category] += amount
        self.last_touched = datetime.now()

    def get_latest_checkpoint(self) -> SessionCheckpoint | None:
        """Get the most recent checkpoint."""
        return self.checkpoints[-1] if self.checkpoints else None

    def get_checkpoint_for_phase(self, phase: NPhase) -> SessionCheckpoint | None:
        """Get the latest checkpoint for a specific phase."""
        for cp in reversed(self.checkpoints):
            if cp.phase == phase:
                return cp
        return None

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "id": self.id,
            "title": self.title,
            "current_phase": self.current_phase.name,
            "cycle_count": self.cycle_count,
            "checkpoints": [cp.to_dict() for cp in self.checkpoints],
            "handles": [h.to_dict() for h in self.handles],
            "ledger": [e.to_dict() for e in self.ledger],
            "entropy_spent": dict(self.entropy_spent),
            "created_at": self.created_at.isoformat(),
            "last_touched": self.last_touched.isoformat(),
            "metadata": dict(self.metadata),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> NPhaseSession:
        """Deserialize from dictionary."""
        session = cls(
            id=data["id"],
            title=data.get("title", ""),
            metadata=dict(data.get("metadata", {})),
        )

        # Restore phase state
        session.phase_state.current_phase = NPhase[data.get("current_phase", "UNDERSTAND")]
        session.phase_state.cycle_count = data.get("cycle_count", 0)

        # Restore checkpoints
        session.checkpoints = [
            SessionCheckpoint.from_dict(cp) for cp in data.get("checkpoints", [])
        ]

        # Restore handles
        session.handles = [Handle.from_dict(h) for h in data.get("handles", [])]

        # Restore ledger
        session.ledger = [
            PhaseLedgerEntry.from_dict(e) for e in data.get("ledger", [])
        ]

        # Restore entropy
        session.entropy_spent = dict(data.get("entropy_spent", {}))

        # Restore timestamps
        if "created_at" in data:
            session.created_at = datetime.fromisoformat(data["created_at"])
        if "last_touched" in data:
            session.last_touched = datetime.fromisoformat(data["last_touched"])

        return session

    def summary(self) -> dict[str, Any]:
        """Get a summary of session state (for API responses)."""
        return {
            "id": self.id,
            "title": self.title,
            "current_phase": self.current_phase.name,
            "cycle_count": self.cycle_count,
            "checkpoint_count": len(self.checkpoints),
            "handle_count": len(self.handles),
            "ledger_count": len(self.ledger),
            "entropy_spent": self.entropy_spent,
            "created_at": self.created_at.isoformat(),
            "last_touched": self.last_touched.isoformat(),
        }


# =============================================================================
# Session Store (In-Memory MVP)
# =============================================================================


class SessionStore:
    """
    In-memory session store.

    For MVP, sessions are stored in memory.
    Production would persist to database via D-gent.

    Thread-safety: Not thread-safe. For production, use async locks
    or database transactions.
    """

    def __init__(self) -> None:
        self._sessions: dict[str, NPhaseSession] = {}

    def create(self, title: str = "", metadata: dict[str, Any] | None = None) -> NPhaseSession:
        """Create a new N-Phase session."""
        session = NPhaseSession(title=title, metadata=metadata or {})
        self._sessions[session.id] = session
        return session

    def get(self, session_id: str) -> NPhaseSession | None:
        """Get session by ID."""
        return self._sessions.get(session_id)

    def list(self) -> list[NPhaseSession]:
        """List all sessions."""
        return list(self._sessions.values())

    def delete(self, session_id: str) -> bool:
        """Delete session by ID. Returns True if deleted."""
        if session_id in self._sessions:
            del self._sessions[session_id]
            return True
        return False

    def clear(self) -> None:
        """Clear all sessions (for testing)."""
        self._sessions.clear()

    def count(self) -> int:
        """Get total session count."""
        return len(self._sessions)


# Global session store instance
_session_store = SessionStore()


def get_session_store() -> SessionStore:
    """Get the global session store."""
    return _session_store


def reset_session_store() -> None:
    """Reset the global session store (for testing)."""
    _session_store.clear()


# =============================================================================
# Convenience Functions
# =============================================================================


def create_session(title: str = "", metadata: dict[str, Any] | None = None) -> NPhaseSession:
    """Create a new N-Phase session."""
    return _session_store.create(title=title, metadata=metadata)


def get_session(session_id: str) -> NPhaseSession | None:
    """Get session by ID."""
    return _session_store.get(session_id)


def list_sessions() -> list[NPhaseSession]:
    """List all sessions."""
    return _session_store.list()


def delete_session(session_id: str) -> bool:
    """Delete session by ID."""
    return _session_store.delete(session_id)


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    # Data classes
    "Handle",
    "PhaseLedgerEntry",
    "SessionCheckpoint",
    "NPhaseSession",
    # Store
    "SessionStore",
    "get_session_store",
    "reset_session_store",
    # Convenience functions
    "create_session",
    "get_session",
    "list_sessions",
    "delete_session",
]
