"""
Event Store - SQLite-based session persistence for the DVR.

All dashboard events are persisted to enable:
- Session replay (scrubbing through historical sessions)
- Session export (to flowfiles)
- Cross-session analysis
- Crash recovery

Uses SQLite for simplicity and portability. The database
is stored in .kgents/history.db by default.
"""

from __future__ import annotations

import json
import sqlite3
import uuid
from contextlib import contextmanager
from datetime import datetime, timedelta
from pathlib import Path
from typing import Iterator

from .types import (
    DashboardEvent,
    EventType,
    Session,
    SessionState,
    AgentEntry,
    AgentStatus,
    ArtifactEntry,
)


# =============================================================================
# Database Schema
# =============================================================================

SCHEMA = """
-- Sessions table
CREATE TABLE IF NOT EXISTS sessions (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    state TEXT NOT NULL,
    started_at TEXT NOT NULL,
    ended_at TEXT,
    flow_name TEXT,
    flow_path TEXT,
    budget_level TEXT DEFAULT 'medium',
    tokens_used INTEGER DEFAULT 0,
    metadata TEXT DEFAULT '{}'
);

-- Events table
CREATE TABLE IF NOT EXISTS events (
    id TEXT PRIMARY KEY,
    session_id TEXT NOT NULL,
    timestamp TEXT NOT NULL,
    event_type TEXT NOT NULL,
    source TEXT NOT NULL,
    message TEXT NOT NULL,
    data TEXT DEFAULT '{}',
    FOREIGN KEY (session_id) REFERENCES sessions(id)
);

-- Agents table (for quick lookup)
CREATE TABLE IF NOT EXISTS agents (
    id TEXT PRIMARY KEY,
    session_id TEXT NOT NULL,
    name TEXT NOT NULL,
    genus TEXT NOT NULL,
    status TEXT NOT NULL,
    started_at TEXT,
    completed_at TEXT,
    error TEXT,
    FOREIGN KEY (session_id) REFERENCES sessions(id)
);

-- Artifacts table
CREATE TABLE IF NOT EXISTS artifacts (
    id TEXT PRIMARY KEY,
    session_id TEXT NOT NULL,
    name TEXT NOT NULL,
    path TEXT,
    artifact_type TEXT NOT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    size_bytes INTEGER DEFAULT 0,
    content_preview TEXT,
    FOREIGN KEY (session_id) REFERENCES sessions(id)
);

-- Indices for fast queries
CREATE INDEX IF NOT EXISTS idx_events_session ON events(session_id);
CREATE INDEX IF NOT EXISTS idx_events_timestamp ON events(timestamp);
CREATE INDEX IF NOT EXISTS idx_events_type ON events(event_type);
CREATE INDEX IF NOT EXISTS idx_agents_session ON agents(session_id);
CREATE INDEX IF NOT EXISTS idx_artifacts_session ON artifacts(session_id);
CREATE INDEX IF NOT EXISTS idx_sessions_state ON sessions(state);
"""


# =============================================================================
# Event Store
# =============================================================================


class EventStore:
    """
    SQLite-based event store for dashboard sessions.

    Provides:
    - Session CRUD operations
    - Event streaming and persistence
    - Historical session queries
    - Session export
    """

    def __init__(self, db_path: Path | str | None = None):
        """
        Initialize event store.

        Args:
            db_path: Path to SQLite database. Defaults to .kgents/history.db
        """
        if db_path is None:
            db_path = Path.cwd() / ".kgents" / "history.db"
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _init_db(self) -> None:
        """Initialize database schema."""
        with self._connection() as conn:
            conn.executescript(SCHEMA)
            conn.commit()

    @contextmanager
    def _connection(self) -> Iterator[sqlite3.Connection]:
        """Context manager for database connections."""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()

    @staticmethod
    def generate_id(prefix: str = "evt") -> str:
        """Generate a unique ID with prefix."""
        return f"{prefix}_{uuid.uuid4().hex[:12]}"

    # =========================================================================
    # Session Operations
    # =========================================================================

    def create_session(
        self,
        name: str,
        flow_name: str | None = None,
        flow_path: Path | None = None,
        budget_level: str = "medium",
    ) -> Session:
        """
        Create a new session.

        Args:
            name: Session name
            flow_name: Optional flow being executed
            flow_path: Optional path to flowfile
            budget_level: Budget level (minimal/low/medium/high/unlimited)

        Returns:
            New Session object
        """
        session = Session(
            id=self.generate_id("sess"),
            name=name,
            state=SessionState.LIVE,
            started_at=datetime.now(),
            flow_name=flow_name,
            flow_path=flow_path,
            budget_level=budget_level,
        )

        with self._connection() as conn:
            conn.execute(
                """
                INSERT INTO sessions (id, name, state, started_at, flow_name, flow_path, budget_level)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    session.id,
                    session.name,
                    session.state.value,
                    session.started_at.isoformat(),
                    session.flow_name,
                    str(session.flow_path) if session.flow_path else None,
                    session.budget_level,
                ),
            )
            conn.commit()

        # Add session start event
        self.add_event(
            session.id,
            EventType.SESSION_START,
            "system",
            f"Session '{name}' started",
            {"flow_name": flow_name},
        )

        return session

    def end_session(self, session_id: str) -> None:
        """End a session."""
        ended_at = datetime.now()

        with self._connection() as conn:
            conn.execute(
                """
                UPDATE sessions SET state = ?, ended_at = ?
                WHERE id = ?
                """,
                (SessionState.ENDED.value, ended_at.isoformat(), session_id),
            )
            conn.commit()

        self.add_event(
            session_id,
            EventType.SESSION_END,
            "system",
            "Session ended",
        )

    def get_session(self, session_id: str) -> Session | None:
        """Get a session by ID, including all events."""
        with self._connection() as conn:
            row = conn.execute(
                "SELECT * FROM sessions WHERE id = ?",
                (session_id,),
            ).fetchone()

            if row is None:
                return None

            session = Session(
                id=row["id"],
                name=row["name"],
                state=SessionState(row["state"]),
                started_at=datetime.fromisoformat(row["started_at"]),
                ended_at=datetime.fromisoformat(row["ended_at"])
                if row["ended_at"]
                else None,
                flow_name=row["flow_name"],
                flow_path=Path(row["flow_path"]) if row["flow_path"] else None,
                budget_level=row["budget_level"],
                tokens_used=row["tokens_used"],
            )

            # Load events
            events = conn.execute(
                "SELECT * FROM events WHERE session_id = ? ORDER BY timestamp",
                (session_id,),
            ).fetchall()

            for event_row in events:
                session.events.append(
                    DashboardEvent(
                        id=event_row["id"],
                        timestamp=datetime.fromisoformat(event_row["timestamp"]),
                        event_type=EventType(event_row["event_type"]),
                        source=event_row["source"],
                        message=event_row["message"],
                        data=json.loads(event_row["data"]),
                        session_id=session_id,
                    )
                )

            # Load agents
            agents = conn.execute(
                "SELECT * FROM agents WHERE session_id = ?",
                (session_id,),
            ).fetchall()

            for agent_row in agents:
                session.agents[agent_row["id"]] = AgentEntry(
                    id=agent_row["id"],
                    name=agent_row["name"],
                    genus=agent_row["genus"],
                    status=AgentStatus(agent_row["status"]),
                    started_at=datetime.fromisoformat(agent_row["started_at"])
                    if agent_row["started_at"]
                    else None,
                    completed_at=datetime.fromisoformat(agent_row["completed_at"])
                    if agent_row["completed_at"]
                    else None,
                    error=agent_row["error"],
                )

            # Load artifacts
            artifacts = conn.execute(
                "SELECT * FROM artifacts WHERE session_id = ?",
                (session_id,),
            ).fetchall()

            for artifact_row in artifacts:
                session.artifacts[artifact_row["id"]] = ArtifactEntry(
                    id=artifact_row["id"],
                    name=artifact_row["name"],
                    path=Path(artifact_row["path"]) if artifact_row["path"] else None,
                    artifact_type=artifact_row["artifact_type"],
                    created_at=datetime.fromisoformat(artifact_row["created_at"]),
                    updated_at=datetime.fromisoformat(artifact_row["updated_at"]),
                    size_bytes=artifact_row["size_bytes"],
                    content_preview=artifact_row["content_preview"] or "",
                )

            return session

    def list_sessions(
        self,
        state: SessionState | None = None,
        since: datetime | None = None,
        limit: int = 20,
    ) -> list[Session]:
        """
        List sessions with optional filters.

        Args:
            state: Filter by session state
            since: Only sessions started after this time
            limit: Maximum number of sessions to return

        Returns:
            List of sessions (without full event data)
        """
        with self._connection() as conn:
            query = "SELECT * FROM sessions WHERE 1=1"
            params: list = []

            if state:
                query += " AND state = ?"
                params.append(state.value)

            if since:
                query += " AND started_at >= ?"
                params.append(since.isoformat())

            query += " ORDER BY started_at DESC LIMIT ?"
            params.append(limit)

            rows = conn.execute(query, params).fetchall()

            sessions = []
            for row in rows:
                session = Session(
                    id=row["id"],
                    name=row["name"],
                    state=SessionState(row["state"]),
                    started_at=datetime.fromisoformat(row["started_at"]),
                    ended_at=datetime.fromisoformat(row["ended_at"])
                    if row["ended_at"]
                    else None,
                    flow_name=row["flow_name"],
                    flow_path=Path(row["flow_path"]) if row["flow_path"] else None,
                    budget_level=row["budget_level"],
                    tokens_used=row["tokens_used"],
                )
                sessions.append(session)

            return sessions

    def delete_session(self, session_id: str) -> bool:
        """Delete a session and all its data."""
        with self._connection() as conn:
            # Delete in order (foreign keys)
            conn.execute("DELETE FROM artifacts WHERE session_id = ?", (session_id,))
            conn.execute("DELETE FROM agents WHERE session_id = ?", (session_id,))
            conn.execute("DELETE FROM events WHERE session_id = ?", (session_id,))
            result = conn.execute("DELETE FROM sessions WHERE id = ?", (session_id,))
            conn.commit()
            return result.rowcount > 0

    # =========================================================================
    # Event Operations
    # =========================================================================

    def add_event(
        self,
        session_id: str,
        event_type: EventType,
        source: str,
        message: str,
        data: dict | None = None,
    ) -> DashboardEvent:
        """
        Add an event to a session.

        Args:
            session_id: Session to add event to
            event_type: Type of event
            source: Source agent/step
            message: Human-readable message
            data: Optional structured data

        Returns:
            Created event
        """
        event = DashboardEvent(
            id=self.generate_id("evt"),
            timestamp=datetime.now(),
            event_type=event_type,
            source=source,
            message=message,
            data=data or {},
            session_id=session_id,
        )

        with self._connection() as conn:
            conn.execute(
                """
                INSERT INTO events (id, session_id, timestamp, event_type, source, message, data)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    event.id,
                    session_id,
                    event.timestamp.isoformat(),
                    event.event_type.value,
                    event.source,
                    event.message,
                    json.dumps(event.data),
                ),
            )
            conn.commit()

        return event

    def get_events(
        self,
        session_id: str,
        event_type: EventType | None = None,
        since: datetime | None = None,
        limit: int | None = None,
    ) -> list[DashboardEvent]:
        """Get events for a session with optional filters."""
        with self._connection() as conn:
            query = "SELECT * FROM events WHERE session_id = ?"
            params: list = [session_id]

            if event_type:
                query += " AND event_type = ?"
                params.append(event_type.value)

            if since:
                query += " AND timestamp >= ?"
                params.append(since.isoformat())

            query += " ORDER BY timestamp"

            if limit:
                query += " LIMIT ?"
                params.append(limit)

            rows = conn.execute(query, params).fetchall()

            return [
                DashboardEvent(
                    id=row["id"],
                    timestamp=datetime.fromisoformat(row["timestamp"]),
                    event_type=EventType(row["event_type"]),
                    source=row["source"],
                    message=row["message"],
                    data=json.loads(row["data"]),
                    session_id=session_id,
                )
                for row in rows
            ]

    # =========================================================================
    # Agent Operations
    # =========================================================================

    def register_agent(
        self,
        session_id: str,
        agent_id: str,
        name: str,
        genus: str,
    ) -> AgentEntry:
        """Register an agent for tracking."""
        agent = AgentEntry(
            id=agent_id,
            name=name,
            genus=genus,
            status=AgentStatus.PENDING,
        )

        with self._connection() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO agents (id, session_id, name, genus, status)
                VALUES (?, ?, ?, ?, ?)
                """,
                (agent_id, session_id, name, genus, agent.status.value),
            )
            conn.commit()

        return agent

    def update_agent_status(
        self,
        session_id: str,
        agent_id: str,
        status: AgentStatus,
        error: str | None = None,
    ) -> None:
        """Update agent status."""
        now = datetime.now().isoformat()

        with self._connection() as conn:
            if status == AgentStatus.RUNNING:
                conn.execute(
                    "UPDATE agents SET status = ?, started_at = ? WHERE id = ? AND session_id = ?",
                    (status.value, now, agent_id, session_id),
                )
            elif status in (
                AgentStatus.COMPLETE,
                AgentStatus.FAILED,
                AgentStatus.SKIPPED,
            ):
                conn.execute(
                    "UPDATE agents SET status = ?, completed_at = ?, error = ? WHERE id = ? AND session_id = ?",
                    (status.value, now, error, agent_id, session_id),
                )
            else:
                conn.execute(
                    "UPDATE agents SET status = ? WHERE id = ? AND session_id = ?",
                    (status.value, agent_id, session_id),
                )
            conn.commit()

    # =========================================================================
    # Artifact Operations
    # =========================================================================

    def register_artifact(
        self,
        session_id: str,
        name: str,
        artifact_type: str,
        path: Path | None = None,
        size_bytes: int = 0,
        content_preview: str = "",
    ) -> ArtifactEntry:
        """Register an artifact."""
        now = datetime.now()
        artifact = ArtifactEntry(
            id=self.generate_id("art"),
            name=name,
            path=path,
            artifact_type=artifact_type,
            created_at=now,
            updated_at=now,
            size_bytes=size_bytes,
            content_preview=content_preview[:100] if content_preview else "",
        )

        with self._connection() as conn:
            conn.execute(
                """
                INSERT INTO artifacts (id, session_id, name, path, artifact_type, created_at, updated_at, size_bytes, content_preview)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    artifact.id,
                    session_id,
                    artifact.name,
                    str(artifact.path) if artifact.path else None,
                    artifact.artifact_type,
                    artifact.created_at.isoformat(),
                    artifact.updated_at.isoformat(),
                    artifact.size_bytes,
                    artifact.content_preview,
                ),
            )
            conn.commit()

        return artifact

    # =========================================================================
    # Cleanup
    # =========================================================================

    def cleanup_old_sessions(self, retention: timedelta = timedelta(days=30)) -> int:
        """
        Clean up sessions older than retention period.

        Returns number of sessions deleted.
        """
        cutoff = (datetime.now() - retention).isoformat()

        with self._connection() as conn:
            # Get session IDs to delete
            rows = conn.execute(
                "SELECT id FROM sessions WHERE ended_at < ? AND state = ?",
                (cutoff, SessionState.ENDED.value),
            ).fetchall()

            session_ids = [row["id"] for row in rows]

            for session_id in session_ids:
                conn.execute(
                    "DELETE FROM artifacts WHERE session_id = ?", (session_id,)
                )
                conn.execute("DELETE FROM agents WHERE session_id = ?", (session_id,))
                conn.execute("DELETE FROM events WHERE session_id = ?", (session_id,))
                conn.execute("DELETE FROM sessions WHERE id = ?", (session_id,))

            conn.commit()
            return len(session_ids)

    def get_statistics(self) -> dict:
        """Get store statistics."""
        with self._connection() as conn:
            sessions = conn.execute("SELECT COUNT(*) as count FROM sessions").fetchone()
            events = conn.execute("SELECT COUNT(*) as count FROM events").fetchone()
            agents = conn.execute("SELECT COUNT(*) as count FROM agents").fetchone()
            artifacts = conn.execute(
                "SELECT COUNT(*) as count FROM artifacts"
            ).fetchone()

            live = conn.execute(
                "SELECT COUNT(*) as count FROM sessions WHERE state = ?",
                (SessionState.LIVE.value,),
            ).fetchone()

            return {
                "total_sessions": sessions["count"],
                "live_sessions": live["count"],
                "total_events": events["count"],
                "total_agents": agents["count"],
                "total_artifacts": artifacts["count"],
                "db_path": str(self.db_path),
                "db_size_bytes": self.db_path.stat().st_size
                if self.db_path.exists()
                else 0,
            }
