"""
AGENTESE REPL Session Persistence.

Wave 3 Intelligence: Save and restore REPL state across restarts.

Session data includes:
    - Current path (context navigation)
    - Observer archetype
    - Timestamp

Design Principles:
    - Non-intrusive: Session restore is optional and silent
    - Secure: Only saves path/observer, not command history (that's readline)
    - Human-readable: JSON format for easy inspection
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# Default session file location
DEFAULT_SESSION_FILE = Path.home() / ".kgents_repl_session.json"


@dataclass
class SessionData:
    """
    Serializable REPL session state.

    Only contains state needed for session continuity.
    Command history is handled separately by readline.
    """

    path: list[str] = field(default_factory=list)
    observer: str = "explorer"
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


def save_session(
    path: list[str],
    observer: str,
    session_file: Path = DEFAULT_SESSION_FILE,
) -> bool:
    """
    Save current session state to disk.

    Args:
        path: Current AGENTESE path (e.g., ["self", "soul"])
        observer: Current observer archetype
        session_file: Where to save (default: ~/.kgents_repl_session.json)

    Returns:
        True if saved successfully, False otherwise
    """
    try:
        data = SessionData(
            path=path,
            observer=observer,
            timestamp=datetime.now(timezone.utc).isoformat(),
        )

        session_file.write_text(
            json.dumps(
                {
                    "path": data.path,
                    "observer": data.observer,
                    "timestamp": data.timestamp,
                },
                indent=2,
            )
        )
        return True
    except (OSError, PermissionError, TypeError):
        return False


def load_session(
    session_file: Path = DEFAULT_SESSION_FILE,
) -> SessionData | None:
    """
    Load session state from disk.

    Args:
        session_file: Where to load from (default: ~/.kgents_repl_session.json)

    Returns:
        SessionData if loaded successfully, None otherwise
    """
    try:
        if not session_file.exists():
            return None

        data = json.loads(session_file.read_text())

        return SessionData(
            path=data.get("path", []),
            observer=data.get("observer", "explorer"),
            timestamp=data.get("timestamp", ""),
        )
    except (OSError, PermissionError, json.JSONDecodeError, TypeError, KeyError):
        return None


def restore_session_to_state(state: Any, session_file: Path = DEFAULT_SESSION_FILE) -> bool:
    """
    Restore session state to a ReplState object.

    Args:
        state: ReplState object to restore into
        session_file: Where to load from

    Returns:
        True if restored successfully, False otherwise
    """
    session = load_session(session_file)
    if session is None:
        return False

    state.path = session.path
    state.observer = session.observer
    return True


def clear_session(session_file: Path = DEFAULT_SESSION_FILE) -> bool:
    """
    Clear the saved session.

    Args:
        session_file: Session file to remove

    Returns:
        True if cleared successfully, False if file didn't exist
    """
    try:
        if session_file.exists():
            session_file.unlink()
            return True
        return False
    except (OSError, PermissionError):
        return False


def format_session_info(session: SessionData) -> str:
    """
    Format session data for display.

    Args:
        session: SessionData to format

    Returns:
        Human-readable session info
    """
    path_str = ".".join(session.path) if session.path else "(root)"
    return f"Path: {path_str}, Observer: {session.observer}, Saved: {session.timestamp}"
