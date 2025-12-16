"""
SessionStore: SQLite Persistence for GardenerSession.

Stores session state, history, and links to forest plan files.
Enables resume across Claude Code sessions via `kg /continue`.

AGENTESE: concept.gardener.session.* persistence

Key Design:
- Sessions persist as JSON in SQLite with indexed metadata
- Plan file links stored as foreign keys to forest path
- Last active session tracked for quick resume
- History preserved for time.sessions.witness
"""

from __future__ import annotations

import json
import sqlite3
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any, Iterator

from opentelemetry import trace

if TYPE_CHECKING:
    pass


# =============================================================================
# OTEL Telemetry
# =============================================================================

_tracer: trace.Tracer | None = None


def _get_store_tracer() -> trace.Tracer:
    """Get the SessionStore tracer, creating if needed."""
    global _tracer
    if _tracer is None:
        _tracer = trace.get_tracer("kgents.gardener.persistence", "0.1.0")
    return _tracer


# =============================================================================
# Schema
# =============================================================================

SESSION_SCHEMA = """
-- GardenerSession storage
CREATE TABLE IF NOT EXISTS gardener_sessions (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    plan_path TEXT,
    phase TEXT NOT NULL DEFAULT 'SENSE',
    state_json TEXT NOT NULL DEFAULT '{}',
    intent_json TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    resumed_at TEXT,
    completed_at TEXT,
    is_active INTEGER NOT NULL DEFAULT 1
);

CREATE INDEX IF NOT EXISTS idx_sessions_active ON gardener_sessions(is_active);
CREATE INDEX IF NOT EXISTS idx_sessions_plan ON gardener_sessions(plan_path);
CREATE INDEX IF NOT EXISTS idx_sessions_updated ON gardener_sessions(updated_at DESC);

-- Session history (phase transitions, actions)
CREATE TABLE IF NOT EXISTS gardener_session_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL REFERENCES gardener_sessions(id),
    event_type TEXT NOT NULL,
    phase_from TEXT,
    phase_to TEXT,
    artifact_json TEXT,
    timestamp TEXT NOT NULL,
    FOREIGN KEY (session_id) REFERENCES gardener_sessions(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_history_session ON gardener_session_history(session_id);
CREATE INDEX IF NOT EXISTS idx_history_timestamp ON gardener_session_history(timestamp DESC);

-- Singleton for last active session
CREATE TABLE IF NOT EXISTS gardener_active_session (
    id INTEGER PRIMARY KEY CHECK (id = 1),
    session_id TEXT REFERENCES gardener_sessions(id),
    updated_at TEXT NOT NULL
);

INSERT OR IGNORE INTO gardener_active_session (id, session_id, updated_at)
VALUES (1, NULL, datetime('now'));
"""


# =============================================================================
# Data Types
# =============================================================================


@dataclass
class StoredSession:
    """
    A persisted GardenerSession.

    Maps to gardener_sessions table.
    """

    id: str
    name: str
    plan_path: str | None
    phase: str
    state: dict[str, Any]
    intent: dict[str, Any] | None
    created_at: datetime
    updated_at: datetime
    resumed_at: datetime | None = None
    completed_at: datetime | None = None
    is_active: bool = True

    def to_row(self) -> dict[str, Any]:
        """Convert to database row."""
        return {
            "id": self.id,
            "name": self.name,
            "plan_path": self.plan_path,
            "phase": self.phase,
            "state_json": json.dumps(self.state),
            "intent_json": json.dumps(self.intent) if self.intent else None,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "resumed_at": self.resumed_at.isoformat() if self.resumed_at else None,
            "completed_at": self.completed_at.isoformat()
            if self.completed_at
            else None,
            "is_active": 1 if self.is_active else 0,
        }

    @classmethod
    def from_row(cls, row: sqlite3.Row | dict[str, Any]) -> "StoredSession":
        """Create from database row."""
        # Handle both sqlite3.Row and dict
        if isinstance(row, sqlite3.Row):
            row = dict(row)

        def parse_dt(val: str | None) -> datetime | None:
            if val is None:
                return None
            return datetime.fromisoformat(val)

        return cls(
            id=row["id"],
            name=row["name"],
            plan_path=row["plan_path"],
            phase=row["phase"],
            state=json.loads(row["state_json"]) if row["state_json"] else {},
            intent=json.loads(row["intent_json"]) if row.get("intent_json") else None,
            created_at=parse_dt(row["created_at"]) or datetime.now(),
            updated_at=parse_dt(row["updated_at"]) or datetime.now(),
            resumed_at=parse_dt(row.get("resumed_at")),
            completed_at=parse_dt(row.get("completed_at")),
            is_active=bool(row.get("is_active", 1)),
        )


@dataclass
class SessionHistoryEvent:
    """A historical event in a session."""

    id: int | None
    session_id: str
    event_type: str  # "created", "advanced", "resumed", "completed"
    phase_from: str | None
    phase_to: str | None
    artifact: dict[str, Any] | None
    timestamp: datetime

    def to_row(self) -> dict[str, Any]:
        """Convert to database row."""
        return {
            "session_id": self.session_id,
            "event_type": self.event_type,
            "phase_from": self.phase_from,
            "phase_to": self.phase_to,
            "artifact_json": json.dumps(self.artifact) if self.artifact else None,
            "timestamp": self.timestamp.isoformat(),
        }

    @classmethod
    def from_row(cls, row: sqlite3.Row | dict[str, Any]) -> "SessionHistoryEvent":
        """Create from database row."""
        if isinstance(row, sqlite3.Row):
            row = dict(row)

        return cls(
            id=row.get("id"),
            session_id=row["session_id"],
            event_type=row["event_type"],
            phase_from=row.get("phase_from"),
            phase_to=row.get("phase_to"),
            artifact=json.loads(row["artifact_json"])
            if row.get("artifact_json")
            else None,
            timestamp=datetime.fromisoformat(row["timestamp"]),
        )


# =============================================================================
# SessionStore
# =============================================================================


@dataclass
class SessionStore:
    """
    SQLite persistence for GardenerSession.

    Thread-safe via connection-per-operation pattern.
    Uses WAL mode for concurrent reads.

    Usage:
        store = SessionStore(db_path)
        await store.init()

        # Create session
        session_id = await store.create(name="My Session", plan_path="plans/foo.md")

        # Resume
        session = await store.get_active()
        if session:
            print(f"Resuming: {session.name}")

        # List recent
        sessions = await store.list_recent(limit=10)
    """

    db_path: Path
    _initialized: bool = field(default=False, init=False)

    def __post_init__(self) -> None:
        """Ensure db_path is a Path."""
        if isinstance(self.db_path, str):
            self.db_path = Path(self.db_path)

    @contextmanager
    def _connection(self) -> Iterator[sqlite3.Connection]:
        """Get a database connection with row factory."""
        conn = sqlite3.connect(str(self.db_path), timeout=30.0)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA foreign_keys=ON")
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    async def init(self) -> None:
        """Initialize the database schema."""
        tracer = _get_store_tracer()
        with tracer.start_as_current_span("session_store.init") as span:
            # Ensure directory exists
            self.db_path.parent.mkdir(parents=True, exist_ok=True)

            with self._connection() as conn:
                conn.executescript(SESSION_SCHEMA)

            self._initialized = True
            span.set_attribute("db.path", str(self.db_path))

    async def create(
        self,
        session_id: str,
        name: str,
        plan_path: str | None = None,
        initial_state: dict[str, Any] | None = None,
        intent: dict[str, Any] | None = None,
    ) -> StoredSession:
        """
        Create a new session.

        Returns the created StoredSession.
        """
        tracer = _get_store_tracer()
        with tracer.start_as_current_span("session_store.create") as span:
            span.set_attribute("session.id", session_id)
            span.set_attribute("session.name", name)

            now = datetime.now()
            session = StoredSession(
                id=session_id,
                name=name,
                plan_path=plan_path,
                phase="SENSE",
                state=initial_state or {},
                intent=intent,
                created_at=now,
                updated_at=now,
                is_active=True,
            )

            row = session.to_row()
            with self._connection() as conn:
                conn.execute(
                    """
                    INSERT INTO gardener_sessions
                    (id, name, plan_path, phase, state_json, intent_json, created_at, updated_at, is_active)
                    VALUES (:id, :name, :plan_path, :phase, :state_json, :intent_json, :created_at, :updated_at, :is_active)
                    """,
                    row,
                )

                # Record creation event
                conn.execute(
                    """
                    INSERT INTO gardener_session_history
                    (session_id, event_type, phase_to, timestamp)
                    VALUES (?, 'created', 'SENSE', ?)
                    """,
                    (session_id, now.isoformat()),
                )

                # Set as active session
                conn.execute(
                    """
                    UPDATE gardener_active_session
                    SET session_id = ?, updated_at = ?
                    WHERE id = 1
                    """,
                    (session_id, now.isoformat()),
                )

            return session

    async def get(self, session_id: str) -> StoredSession | None:
        """Get a session by ID."""
        tracer = _get_store_tracer()
        with tracer.start_as_current_span("session_store.get") as span:
            span.set_attribute("session.id", session_id)

            with self._connection() as conn:
                cursor = conn.execute(
                    "SELECT * FROM gardener_sessions WHERE id = ?",
                    (session_id,),
                )
                row = cursor.fetchone()

            if row:
                return StoredSession.from_row(row)
            return None

    async def get_active(self) -> StoredSession | None:
        """Get the currently active session for quick resume."""
        tracer = _get_store_tracer()
        with tracer.start_as_current_span("session_store.get_active"):
            with self._connection() as conn:
                cursor = conn.execute(
                    """
                    SELECT s.* FROM gardener_sessions s
                    JOIN gardener_active_session a ON s.id = a.session_id
                    WHERE s.is_active = 1
                    """,
                )
                row = cursor.fetchone()

            if row:
                return StoredSession.from_row(row)
            return None

    async def get_by_plan(self, plan_path: str) -> StoredSession | None:
        """Get the most recent active session for a plan."""
        tracer = _get_store_tracer()
        with tracer.start_as_current_span("session_store.get_by_plan") as span:
            span.set_attribute("plan.path", plan_path)

            with self._connection() as conn:
                cursor = conn.execute(
                    """
                    SELECT * FROM gardener_sessions
                    WHERE plan_path = ? AND is_active = 1
                    ORDER BY updated_at DESC
                    LIMIT 1
                    """,
                    (plan_path,),
                )
                row = cursor.fetchone()

            if row:
                return StoredSession.from_row(row)
            return None

    async def list_recent(
        self,
        limit: int = 10,
        active_only: bool = True,
    ) -> list[StoredSession]:
        """List recent sessions."""
        tracer = _get_store_tracer()
        with tracer.start_as_current_span("session_store.list_recent") as span:
            span.set_attribute("limit", limit)
            span.set_attribute("active_only", active_only)

            with self._connection() as conn:
                if active_only:
                    cursor = conn.execute(
                        """
                        SELECT * FROM gardener_sessions
                        WHERE is_active = 1
                        ORDER BY updated_at DESC
                        LIMIT ?
                        """,
                        (limit,),
                    )
                else:
                    cursor = conn.execute(
                        """
                        SELECT * FROM gardener_sessions
                        ORDER BY updated_at DESC
                        LIMIT ?
                        """,
                        (limit,),
                    )
                rows = cursor.fetchall()

            return [StoredSession.from_row(row) for row in rows]

    async def update(
        self,
        session_id: str,
        phase: str | None = None,
        state: dict[str, Any] | None = None,
        intent: dict[str, Any] | None = None,
    ) -> bool:
        """
        Update session state.

        Returns True if session was updated.
        """
        tracer = _get_store_tracer()
        with tracer.start_as_current_span("session_store.update") as span:
            span.set_attribute("session.id", session_id)

            now = datetime.now()
            updates = ["updated_at = ?"]
            params: list[Any] = [now.isoformat()]

            if phase is not None:
                updates.append("phase = ?")
                params.append(phase)
                span.set_attribute("session.phase", phase)

            if state is not None:
                updates.append("state_json = ?")
                params.append(json.dumps(state))

            if intent is not None:
                updates.append("intent_json = ?")
                params.append(json.dumps(intent))

            params.append(session_id)

            with self._connection() as conn:
                cursor = conn.execute(
                    f"""
                    UPDATE gardener_sessions
                    SET {", ".join(updates)}
                    WHERE id = ?
                    """,
                    params,
                )
                return cursor.rowcount > 0

    async def advance_phase(
        self,
        session_id: str,
        from_phase: str,
        to_phase: str,
        artifact: dict[str, Any] | None = None,
    ) -> bool:
        """
        Record a phase transition.

        Returns True if transition was recorded.
        """
        tracer = _get_store_tracer()
        with tracer.start_as_current_span("session_store.advance_phase") as span:
            span.set_attribute("session.id", session_id)
            span.set_attribute("phase.from", from_phase)
            span.set_attribute("phase.to", to_phase)

            now = datetime.now()

            with self._connection() as conn:
                # Update session phase
                cursor = conn.execute(
                    """
                    UPDATE gardener_sessions
                    SET phase = ?, updated_at = ?
                    WHERE id = ? AND phase = ?
                    """,
                    (to_phase, now.isoformat(), session_id, from_phase),
                )

                if cursor.rowcount == 0:
                    return False

                # Record history event
                conn.execute(
                    """
                    INSERT INTO gardener_session_history
                    (session_id, event_type, phase_from, phase_to, artifact_json, timestamp)
                    VALUES (?, 'advanced', ?, ?, ?, ?)
                    """,
                    (
                        session_id,
                        from_phase,
                        to_phase,
                        json.dumps(artifact) if artifact else None,
                        now.isoformat(),
                    ),
                )

                return True

    async def mark_resumed(self, session_id: str) -> bool:
        """Mark a session as resumed."""
        tracer = _get_store_tracer()
        with tracer.start_as_current_span("session_store.mark_resumed") as span:
            span.set_attribute("session.id", session_id)

            now = datetime.now()

            with self._connection() as conn:
                cursor = conn.execute(
                    """
                    UPDATE gardener_sessions
                    SET resumed_at = ?, updated_at = ?
                    WHERE id = ?
                    """,
                    (now.isoformat(), now.isoformat(), session_id),
                )

                if cursor.rowcount == 0:
                    return False

                # Set as active session
                conn.execute(
                    """
                    UPDATE gardener_active_session
                    SET session_id = ?, updated_at = ?
                    WHERE id = 1
                    """,
                    (session_id, now.isoformat()),
                )

                # Record history event
                conn.execute(
                    """
                    INSERT INTO gardener_session_history
                    (session_id, event_type, timestamp)
                    VALUES (?, 'resumed', ?)
                    """,
                    (session_id, now.isoformat()),
                )

                return True

    async def complete(
        self,
        session_id: str,
        final_artifact: dict[str, Any] | None = None,
    ) -> bool:
        """Mark a session as completed."""
        tracer = _get_store_tracer()
        with tracer.start_as_current_span("session_store.complete") as span:
            span.set_attribute("session.id", session_id)

            now = datetime.now()

            with self._connection() as conn:
                cursor = conn.execute(
                    """
                    UPDATE gardener_sessions
                    SET completed_at = ?, is_active = 0, updated_at = ?
                    WHERE id = ?
                    """,
                    (now.isoformat(), now.isoformat(), session_id),
                )

                if cursor.rowcount == 0:
                    return False

                # Clear active if this was the active session
                conn.execute(
                    """
                    UPDATE gardener_active_session
                    SET session_id = NULL, updated_at = ?
                    WHERE session_id = ?
                    """,
                    (now.isoformat(), session_id),
                )

                # Record history event
                conn.execute(
                    """
                    INSERT INTO gardener_session_history
                    (session_id, event_type, artifact_json, timestamp)
                    VALUES (?, 'completed', ?, ?)
                    """,
                    (
                        session_id,
                        json.dumps(final_artifact) if final_artifact else None,
                        now.isoformat(),
                    ),
                )

                return True

    async def get_history(
        self,
        session_id: str,
        limit: int = 100,
    ) -> list[SessionHistoryEvent]:
        """Get session history events."""
        tracer = _get_store_tracer()
        with tracer.start_as_current_span("session_store.get_history") as span:
            span.set_attribute("session.id", session_id)

            with self._connection() as conn:
                cursor = conn.execute(
                    """
                    SELECT * FROM gardener_session_history
                    WHERE session_id = ?
                    ORDER BY timestamp DESC
                    LIMIT ?
                    """,
                    (session_id, limit),
                )
                rows = cursor.fetchall()

            return [SessionHistoryEvent.from_row(row) for row in rows]

    async def delete(self, session_id: str) -> bool:
        """Delete a session and its history."""
        tracer = _get_store_tracer()
        with tracer.start_as_current_span("session_store.delete") as span:
            span.set_attribute("session.id", session_id)

            with self._connection() as conn:
                # Clear active if this was the active session
                conn.execute(
                    """
                    UPDATE gardener_active_session
                    SET session_id = NULL, updated_at = ?
                    WHERE session_id = ?
                    """,
                    (datetime.now().isoformat(), session_id),
                )

                # Delete history first (foreign key)
                conn.execute(
                    "DELETE FROM gardener_session_history WHERE session_id = ?",
                    (session_id,),
                )

                # Delete session
                cursor = conn.execute(
                    "DELETE FROM gardener_sessions WHERE id = ?",
                    (session_id,),
                )

                return cursor.rowcount > 0

    async def count_active(self) -> int:
        """Count active sessions."""
        with self._connection() as conn:
            cursor = conn.execute(
                "SELECT COUNT(*) FROM gardener_sessions WHERE is_active = 1"
            )
            row = cursor.fetchone()
            return row[0] if row else 0


# =============================================================================
# Factory
# =============================================================================


def create_session_store(db_path: Path | str | None = None) -> SessionStore:
    """
    Create a SessionStore with sensible defaults.

    Args:
        db_path: Path to SQLite database. Defaults to XDG data directory.

    Returns:
        SessionStore ready for use (call await store.init() to initialize schema)
    """
    if db_path is None:
        # Use XDG data directory
        import os

        xdg_data = os.environ.get(
            "XDG_DATA_HOME", str(Path.home() / ".local" / "share")
        )
        db_path = Path(xdg_data) / "kgents" / "gardener_sessions.db"

    return SessionStore(db_path=Path(db_path))


__all__ = [
    "StoredSession",
    "SessionHistoryEvent",
    "SessionStore",
    "create_session_store",
]
