"""
CLI Session Service: Unified session tracking for kgents CLI.

This module provides session tracking that uses the unified membrane.db
instead of the deprecated per-project history.db.

MIGRATION NOTE (2025-12-20):
- Old: Per-project ~/.kgents/history.db (deprecated)
- New: Global ~/.local/share/kgents/membrane.db (cli_sessions table)

The CLI session service tracks:
- Interactive sessions (kg repl)
- Flow executions (kg flow)
- Agent spawns and completions
- Artifacts produced

Usage:
    from protocols.cli.instance_db import CLISessionService

    async with CLISessionService() as service:
        session = await service.start_session("interactive", "My Session")
        await service.log_event(session.id, "command", "Executed check")
        await service.end_session(session.id)
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from .interfaces import IRelationalStore


@dataclass
class CLISession:
    """A CLI session record."""

    id: str
    name: str
    session_type: str  # "interactive", "flow", "script"
    state: str  # "active", "completed", "failed", "interrupted"
    started_at: datetime
    ended_at: datetime | None = None
    project_path: str | None = None
    project_hash: str | None = None
    flow_name: str | None = None
    flow_path: str | None = None
    budget_level: str = "medium"
    tokens_used: int = 0
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "session_type": self.session_type,
            "state": self.state,
            "started_at": self.started_at.isoformat(),
            "ended_at": self.ended_at.isoformat() if self.ended_at else None,
            "project_path": self.project_path,
            "project_hash": self.project_hash,
            "flow_name": self.flow_name,
            "flow_path": self.flow_path,
            "budget_level": self.budget_level,
            "tokens_used": self.tokens_used,
            "metadata": self.metadata,
        }


@dataclass
class CLISessionEvent:
    """An event within a CLI session."""

    id: str
    session_id: str
    timestamp: datetime
    event_type: str  # "command", "agent_spawn", "artifact", "error", "info"
    source: str  # e.g., "repl", "flow", "agent:check"
    message: str
    data: dict[str, Any] = field(default_factory=dict)


@dataclass
class CLISessionAgent:
    """An agent spawned within a CLI session."""

    id: str
    session_id: str
    name: str
    genus: str  # e.g., "c-gent", "b-gent", "i-gent"
    status: str  # "pending", "running", "completed", "failed"
    started_at: datetime | None = None
    completed_at: datetime | None = None
    error: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class CLISessionArtifact:
    """An artifact produced by a CLI session."""

    id: str
    session_id: str
    name: str
    path: str | None
    artifact_type: str  # "code", "doc", "plan", "report", "test"
    created_at: datetime
    updated_at: datetime
    size_bytes: int = 0
    content_preview: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


class CLISessionService:
    """
    Service for CLI session tracking.

    Uses the unified membrane.db via IRelationalStore interface.
    Can be used with StorageProvider for production or InMemoryRelationalStore for testing.
    """

    def __init__(self, store: IRelationalStore):
        """
        Initialize with a relational store.

        Args:
            store: IRelationalStore implementation (from StorageProvider or in-memory)
        """
        self._store = store

    async def start_session(
        self,
        session_type: str,
        name: str,
        *,
        project_path: str | None = None,
        project_hash: str | None = None,
        flow_name: str | None = None,
        flow_path: str | None = None,
        budget_level: str = "medium",
        metadata: dict[str, Any] | None = None,
    ) -> CLISession:
        """
        Start a new CLI session.

        Args:
            session_type: Type of session ("interactive", "flow", "script")
            name: Human-readable session name
            project_path: Optional project path
            project_hash: Optional project hash for cross-project correlation
            flow_name: Flow name (if session_type is "flow")
            flow_path: Flow file path
            budget_level: Budget level for the session
            metadata: Additional metadata

        Returns:
            The created CLISession
        """
        import json

        session_id = f"cli_{uuid.uuid4().hex[:12]}"
        now = datetime.now()

        session = CLISession(
            id=session_id,
            name=name,
            session_type=session_type,
            state="active",
            started_at=now,
            project_path=project_path,
            project_hash=project_hash,
            flow_name=flow_name,
            flow_path=flow_path,
            budget_level=budget_level,
            metadata=metadata or {},
        )

        await self._store.execute(
            """
            INSERT INTO cli_sessions
            (id, name, session_type, state, started_at, project_path, project_hash,
             flow_name, flow_path, budget_level, tokens_used, metadata)
            VALUES (:id, :name, :session_type, :state, :started_at, :project_path,
                    :project_hash, :flow_name, :flow_path, :budget_level, :tokens_used, :metadata)
            """,
            {
                "id": session_id,
                "name": name,
                "session_type": session_type,
                "state": "active",
                "started_at": now.isoformat(),
                "project_path": project_path,
                "project_hash": project_hash,
                "flow_name": flow_name,
                "flow_path": flow_path,
                "budget_level": budget_level,
                "tokens_used": 0,
                "metadata": json.dumps(metadata or {}),
            },
        )

        # Log session start event
        await self.log_event(
            session_id,
            event_type="session_start",
            source="cli",
            message=f"Started {session_type} session: {name}",
        )

        return session

    async def end_session(
        self,
        session_id: str,
        *,
        state: str = "completed",
        tokens_used: int | None = None,
    ) -> bool:
        """
        End a CLI session.

        Args:
            session_id: Session ID
            state: Final state ("completed", "failed", "interrupted")
            tokens_used: Total tokens used (optional)

        Returns:
            True if session was ended, False if not found
        """
        now = datetime.now()

        # Build update query
        updates = ["state = :state", "ended_at = :ended_at"]
        params: dict[str, Any] = {
            "state": state,
            "ended_at": now.isoformat(),
            "id": session_id,
        }

        if tokens_used is not None:
            updates.append("tokens_used = :tokens_used")
            params["tokens_used"] = tokens_used

        result = await self._store.execute(
            f"""
            UPDATE cli_sessions
            SET {", ".join(updates)}
            WHERE id = :id
            """,
            params,
        )

        if result > 0:
            await self.log_event(
                session_id,
                event_type="session_end",
                source="cli",
                message=f"Session ended with state: {state}",
            )

        return result > 0

    async def get_session(self, session_id: str) -> CLISession | None:
        """Get a session by ID."""
        import json

        row = await self._store.fetch_one(
            "SELECT * FROM cli_sessions WHERE id = :id",
            {"id": session_id},
        )

        if row is None:
            return None

        return CLISession(
            id=row["id"],
            name=row["name"],
            session_type=row["session_type"],
            state=row["state"],
            started_at=datetime.fromisoformat(row["started_at"]),
            ended_at=datetime.fromisoformat(row["ended_at"]) if row["ended_at"] else None,
            project_path=row["project_path"],
            project_hash=row["project_hash"],
            flow_name=row["flow_name"],
            flow_path=row["flow_path"],
            budget_level=row["budget_level"],
            tokens_used=row["tokens_used"],
            metadata=json.loads(row["metadata"]) if row["metadata"] else {},
        )

    async def list_sessions(
        self,
        *,
        limit: int = 20,
        state: str | None = None,
        project_hash: str | None = None,
    ) -> list[CLISession]:
        """
        List recent sessions.

        Args:
            limit: Maximum number of sessions to return
            state: Filter by state (optional)
            project_hash: Filter by project (optional)

        Returns:
            List of sessions, newest first
        """
        import json

        conditions = []
        params: dict[str, Any] = {"limit": limit}

        if state:
            conditions.append("state = :state")
            params["state"] = state

        if project_hash:
            conditions.append("project_hash = :project_hash")
            params["project_hash"] = project_hash

        where_clause = " AND ".join(conditions) if conditions else "1=1"

        rows = await self._store.fetch_all(
            f"""
            SELECT * FROM cli_sessions
            WHERE {where_clause}
            ORDER BY started_at DESC
            LIMIT :limit
            """,
            params,
        )

        return [
            CLISession(
                id=row["id"],
                name=row["name"],
                session_type=row["session_type"],
                state=row["state"],
                started_at=datetime.fromisoformat(row["started_at"]),
                ended_at=datetime.fromisoformat(row["ended_at"]) if row["ended_at"] else None,
                project_path=row["project_path"],
                project_hash=row["project_hash"],
                flow_name=row["flow_name"],
                flow_path=row["flow_path"],
                budget_level=row["budget_level"],
                tokens_used=row["tokens_used"],
                metadata=json.loads(row["metadata"]) if row["metadata"] else {},
            )
            for row in rows
        ]

    async def log_event(
        self,
        session_id: str,
        event_type: str,
        source: str,
        message: str,
        data: dict[str, Any] | None = None,
    ) -> CLISessionEvent:
        """
        Log an event within a session.

        Args:
            session_id: Session ID
            event_type: Type of event
            source: Source of the event
            message: Human-readable message
            data: Additional event data

        Returns:
            The created event
        """
        import json

        event_id = f"evt_{uuid.uuid4().hex[:12]}"
        now = datetime.now()

        event = CLISessionEvent(
            id=event_id,
            session_id=session_id,
            timestamp=now,
            event_type=event_type,
            source=source,
            message=message,
            data=data or {},
        )

        await self._store.execute(
            """
            INSERT INTO cli_session_events
            (id, session_id, timestamp, event_type, source, message, data)
            VALUES (:id, :session_id, :timestamp, :event_type, :source, :message, :data)
            """,
            {
                "id": event_id,
                "session_id": session_id,
                "timestamp": now.isoformat(),
                "event_type": event_type,
                "source": source,
                "message": message,
                "data": json.dumps(data or {}),
            },
        )

        return event

    async def get_session_events(
        self,
        session_id: str,
        *,
        limit: int = 100,
        event_type: str | None = None,
    ) -> list[CLISessionEvent]:
        """Get events for a session."""
        import json

        conditions = ["session_id = :session_id"]
        params: dict[str, Any] = {"session_id": session_id, "limit": limit}

        if event_type:
            conditions.append("event_type = :event_type")
            params["event_type"] = event_type

        where_clause = " AND ".join(conditions)

        rows = await self._store.fetch_all(
            f"""
            SELECT * FROM cli_session_events
            WHERE {where_clause}
            ORDER BY timestamp DESC
            LIMIT :limit
            """,
            params,
        )

        return [
            CLISessionEvent(
                id=row["id"],
                session_id=row["session_id"],
                timestamp=datetime.fromisoformat(row["timestamp"]),
                event_type=row["event_type"],
                source=row["source"],
                message=row["message"],
                data=json.loads(row["data"]) if row["data"] else {},
            )
            for row in rows
        ]

    async def spawn_agent(
        self,
        session_id: str,
        name: str,
        genus: str,
        metadata: dict[str, Any] | None = None,
    ) -> CLISessionAgent:
        """
        Record an agent spawn within a session.

        Args:
            session_id: Session ID
            name: Agent name
            genus: Agent genus (e.g., "c-gent", "b-gent")
            metadata: Additional metadata

        Returns:
            The created agent record
        """
        import json

        agent_id = f"agt_{uuid.uuid4().hex[:12]}"
        now = datetime.now()

        agent = CLISessionAgent(
            id=agent_id,
            session_id=session_id,
            name=name,
            genus=genus,
            status="running",
            started_at=now,
            metadata=metadata or {},
        )

        await self._store.execute(
            """
            INSERT INTO cli_session_agents
            (id, session_id, name, genus, status, started_at, metadata)
            VALUES (:id, :session_id, :name, :genus, :status, :started_at, :metadata)
            """,
            {
                "id": agent_id,
                "session_id": session_id,
                "name": name,
                "genus": genus,
                "status": "running",
                "started_at": now.isoformat(),
                "metadata": json.dumps(metadata or {}),
            },
        )

        return agent

    async def complete_agent(
        self,
        agent_id: str,
        *,
        status: str = "completed",
        error: str | None = None,
    ) -> bool:
        """
        Mark an agent as completed.

        Args:
            agent_id: Agent ID
            status: Final status ("completed", "failed")
            error: Error message if failed

        Returns:
            True if agent was updated, False if not found
        """
        now = datetime.now()

        result = await self._store.execute(
            """
            UPDATE cli_session_agents
            SET status = :status, completed_at = :completed_at, error = :error
            WHERE id = :id
            """,
            {
                "status": status,
                "completed_at": now.isoformat(),
                "error": error,
                "id": agent_id,
            },
        )

        return result > 0

    async def record_artifact(
        self,
        session_id: str,
        name: str,
        artifact_type: str,
        *,
        path: str | None = None,
        size_bytes: int = 0,
        content_preview: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> CLISessionArtifact:
        """
        Record an artifact produced by a session.

        Args:
            session_id: Session ID
            name: Artifact name
            artifact_type: Type of artifact
            path: File path if applicable
            size_bytes: Size in bytes
            content_preview: Preview of content
            metadata: Additional metadata

        Returns:
            The created artifact record
        """
        import json

        artifact_id = f"art_{uuid.uuid4().hex[:12]}"
        now = datetime.now()

        artifact = CLISessionArtifact(
            id=artifact_id,
            session_id=session_id,
            name=name,
            path=path,
            artifact_type=artifact_type,
            created_at=now,
            updated_at=now,
            size_bytes=size_bytes,
            content_preview=content_preview,
            metadata=metadata or {},
        )

        await self._store.execute(
            """
            INSERT INTO cli_session_artifacts
            (id, session_id, name, path, artifact_type, created_at, updated_at,
             size_bytes, content_preview, metadata)
            VALUES (:id, :session_id, :name, :path, :artifact_type, :created_at,
                    :updated_at, :size_bytes, :content_preview, :metadata)
            """,
            {
                "id": artifact_id,
                "session_id": session_id,
                "name": name,
                "path": path,
                "artifact_type": artifact_type,
                "created_at": now.isoformat(),
                "updated_at": now.isoformat(),
                "size_bytes": size_bytes,
                "content_preview": content_preview,
                "metadata": json.dumps(metadata or {}),
            },
        )

        return artifact


# Factory function
async def create_cli_session_service() -> CLISessionService:
    """
    Create a CLISessionService with the default StorageProvider.

    Returns:
        CLISessionService connected to membrane.db
    """
    from .storage import StorageProvider

    storage = await StorageProvider.from_config()
    await storage.run_migrations()  # Ensure schema is up-to-date
    return CLISessionService(storage.relational)


__all__ = [
    "CLISession",
    "CLISessionEvent",
    "CLISessionAgent",
    "CLISessionArtifact",
    "CLISessionService",
    "create_cli_session_service",
]
