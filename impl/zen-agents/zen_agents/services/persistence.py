"""Session persistence layer.

Persists sessions to JSON for recovery across TUI restarts.
Sessions are reconciled with actual tmux state on load.

Usage:
    persistence = SessionPersistence()
    persistence.save(sessions)
    recovered = persistence.load()
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Optional
from uuid import UUID

from ..models.session import Session, SessionState, SessionType


CONFIG_DIR = Path.home() / ".config" / "zen-agents"
SESSIONS_FILE = CONFIG_DIR / "sessions.json"


class DateTimeEncoder(json.JSONEncoder):
    """JSON encoder that handles datetime, UUID, and enums."""

    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        if isinstance(obj, UUID):
            return str(obj)
        if isinstance(obj, (SessionState, SessionType)):
            return obj.value
        return super().default(obj)


class SessionPersistence:
    """
    Persist sessions across TUI restarts.

    Sessions are stored as JSON in ~/.config/zen-agents/sessions.json.
    On load, sessions are reconciled with actual tmux state - any session
    whose tmux session no longer exists is marked as KILLED.
    """

    def __init__(self, sessions_file: Optional[Path] = None):
        """
        Initialize persistence.

        Args:
            sessions_file: Optional custom path. Defaults to ~/.config/zen-agents/sessions.json
        """
        self.sessions_file = sessions_file or SESSIONS_FILE
        self.sessions_file.parent.mkdir(parents=True, exist_ok=True)

    def save(self, sessions: list[Session]) -> None:
        """
        Save sessions to file.

        Args:
            sessions: List of sessions to persist
        """
        data = []
        for session in sessions:
            session_dict = {
                "id": str(session.id),
                "name": session.name,
                "session_type": session.session_type.value,
                "state": session.state.value,
                "tmux_name": session.tmux_name,
                "created_at": session.created_at.isoformat(),
                "updated_at": session.updated_at.isoformat(),
                "metadata": session.metadata,
            }
            # Optional fields
            if session.exit_code is not None:
                session_dict["exit_code"] = session.exit_code
            if session.error_message is not None:
                session_dict["error_message"] = session.error_message
            if session.working_dir is not None:
                session_dict["working_dir"] = session.working_dir
            if session.command is not None:
                session_dict["command"] = session.command

            data.append(session_dict)

        self.sessions_file.write_text(
            json.dumps(data, indent=2, cls=DateTimeEncoder)
        )

    def load(self) -> list[Session]:
        """
        Load sessions from file.

        Returns:
            List of recovered sessions. Sessions whose tmux no longer
            exists will need to be reconciled by the caller.
        """
        if not self.sessions_file.exists():
            return []

        try:
            data = json.loads(self.sessions_file.read_text())
            sessions = []
            for d in data:
                session = Session(
                    id=UUID(d["id"]),
                    name=d["name"],
                    session_type=SessionType(d["session_type"]),
                    state=SessionState(d["state"]),
                    tmux_name=d["tmux_name"],
                    created_at=datetime.fromisoformat(d["created_at"]),
                    updated_at=datetime.fromisoformat(d.get("updated_at", d["created_at"])),
                    exit_code=d.get("exit_code"),
                    error_message=d.get("error_message"),
                    working_dir=d.get("working_dir"),
                    command=d.get("command"),
                    metadata=d.get("metadata", {}),
                )
                sessions.append(session)
            return sessions
        except (json.JSONDecodeError, KeyError, ValueError):
            # Corrupted file - start fresh
            return []

    def delete(self) -> None:
        """Delete persistence file."""
        if self.sessions_file.exists():
            self.sessions_file.unlink()

    def exists(self) -> bool:
        """Check if persistence file exists."""
        return self.sessions_file.exists()
