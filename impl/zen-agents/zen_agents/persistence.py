"""
zen-agents Persistence

Agents for saving and loading session state to disk.

Implements:
    - StateSave: ZenGroundState → Path (save to file)
    - StateLoad: Path → ZenGroundState | None (load from file)
    - SessionPersist: Session → bool (persist single session update)

Persistence format:
    ~/.zen-agents/state.json - Current state (JSON)

Inspired by zenportal's StateService but simplified for zen-agents.
"""

import json
from dataclasses import asdict
from datetime import datetime
from pathlib import Path
from typing import Any

from bootstrap import Agent
from .types import ZenGroundState, Session, SessionConfig, SessionType, SessionState, ConfigLayer, TmuxSession


# =============================================================================
# SERIALIZATION HELPERS
# =============================================================================

def _serialize_datetime(dt: datetime | None) -> str | None:
    """Convert datetime to ISO format string."""
    return dt.isoformat() if dt else None


def _deserialize_datetime(iso: str | None) -> datetime | None:
    """Convert ISO format string to datetime."""
    if not iso:
        return None
    try:
        return datetime.fromisoformat(iso)
    except (ValueError, TypeError):
        return None


def _serialize_session_config(config: SessionConfig) -> dict[str, Any]:
    """Convert SessionConfig to serializable dict."""
    return {
        'name': config.name,
        'session_type': config.session_type.value,
        'working_dir': config.working_dir,
        'command': config.command,
        'env': config.env,
        'model': config.model,
        'system_prompt': config.system_prompt,
        'max_tokens': config.max_tokens,
        'tags': config.tags,
        'priority': config.priority,
    }


def _serialize_session(session: Session) -> dict[str, Any]:
    """Convert Session to serializable dict."""
    return {
        'id': session.id,
        'config': _serialize_session_config(session.config),
        'state': session.state.value,
        'tmux': _serialize_tmux_session(session.tmux) if session.tmux else None,
        'output_lines': session.output_lines,
        'error': session.error,
        'started_at': _serialize_datetime(session.started_at),
        'completed_at': _serialize_datetime(session.completed_at),
    }


def _deserialize_session(data: dict[str, Any]) -> Session:
    """Convert dict back to Session."""
    # Parse config
    config_data = data.get('config', {})
    config = SessionConfig(
        name=config_data.get('name', 'unknown'),
        session_type=SessionType(config_data.get('session_type', 'shell')),
        working_dir=config_data.get('working_dir'),
        command=config_data.get('command'),
        env=config_data.get('env', {}),
        model=config_data.get('model'),
        system_prompt=config_data.get('system_prompt'),
        max_tokens=config_data.get('max_tokens'),
        tags=config_data.get('tags', []),
        priority=config_data.get('priority', 0),
    )

    # Parse state
    try:
        state = SessionState(data.get('state', 'unknown'))
    except ValueError:
        state = SessionState.UNKNOWN

    # Parse tmux if present
    tmux = None
    tmux_data = data.get('tmux')
    if tmux_data:
        tmux = TmuxSession(
            id=tmux_data.get('id', ''),
            name=tmux_data.get('name', ''),
            pane_id=tmux_data.get('pane_id', ''),
            created_at=_deserialize_datetime(tmux_data.get('created_at')) or datetime.now(),
            is_attached=tmux_data.get('is_attached', False),
        )

    return Session(
        id=data.get('id', ''),
        config=config,
        state=state,
        tmux=tmux,
        output_lines=data.get('output_lines', []),
        error=data.get('error'),
        started_at=_deserialize_datetime(data.get('started_at')),
        completed_at=_deserialize_datetime(data.get('completed_at')),
    )


def _serialize_tmux_session(tmux: TmuxSession) -> dict[str, Any]:
    """Convert TmuxSession to serializable dict."""
    return {
        'id': tmux.id,
        'name': tmux.name,
        'pane_id': tmux.pane_id,
        'created_at': _serialize_datetime(tmux.created_at),
        'is_attached': tmux.is_attached,
    }


def _serialize_ground_state(state: ZenGroundState) -> dict[str, Any]:
    """Convert ZenGroundState to serializable dict."""
    return {
        'version': 1,
        'last_updated': _serialize_datetime(state.last_updated),
        'config_cascade': [asdict(layer) for layer in state.config_cascade],
        'sessions': {sid: _serialize_session(session) for sid, session in state.sessions.items()},
        'tmux_sessions': [_serialize_tmux_session(tmux) for tmux in state.tmux_sessions],
        'default_session_type': state.default_session_type.value,
        'auto_discovery': state.auto_discovery,
        'max_sessions': state.max_sessions,
        'last_discovery': _serialize_datetime(state.last_discovery),
    }


def _deserialize_ground_state(data: dict[str, Any]) -> ZenGroundState:
    """Convert dict back to ZenGroundState."""
    # Parse config cascade
    config_cascade = []
    for layer_data in data.get('config_cascade', []):
        config_cascade.append(ConfigLayer(
            name=layer_data.get('name', 'unknown'),
            values=layer_data.get('values', {}),
        ))

    # Parse sessions
    sessions = {}
    for sid, session_data in data.get('sessions', {}).items():
        sessions[sid] = _deserialize_session(session_data)

    # Parse tmux sessions
    tmux_sessions = []
    for tmux_data in data.get('tmux_sessions', []):
        tmux_sessions.append(TmuxSession(
            id=tmux_data.get('id', ''),
            name=tmux_data.get('name', ''),
            pane_id=tmux_data.get('pane_id', ''),
            created_at=_deserialize_datetime(tmux_data.get('created_at')) or datetime.now(),
            is_attached=tmux_data.get('is_attached', False),
        ))

    # Parse session type
    try:
        default_session_type = SessionType(data.get('default_session_type', 'claude'))
    except ValueError:
        default_session_type = SessionType.CLAUDE

    return ZenGroundState(
        config_cascade=config_cascade,
        sessions=sessions,
        tmux_sessions=tmux_sessions,
        default_session_type=default_session_type,
        auto_discovery=data.get('auto_discovery', True),
        max_sessions=data.get('max_sessions', 10),
        last_discovery=_deserialize_datetime(data.get('last_discovery')),
        last_updated=_deserialize_datetime(data.get('last_updated')) or datetime.now(),
    )


# =============================================================================
# STATE SAVE AGENT
# =============================================================================

class StateSave(Agent[ZenGroundState, Path]):
    """
    Save ZenGroundState to a JSON file.

    Type: ZenGroundState → Path

    Saves:
        - Config cascade
        - All sessions
        - tmux facts
        - Preferences
        - Timestamps

    Uses atomic writes (temp file + rename) to prevent corruption.
    """

    def __init__(self, path: Path | None = None):
        """
        Initialize StateSave.

        Args:
            path: Custom save path (default: ~/.zen-agents/state.json)
        """
        if path:
            self._path = path
        else:
            self._path = Path.home() / ".zen-agents" / "state.json"

    @property
    def name(self) -> str:
        return "StateSave"

    @property
    def genus(self) -> str:
        return "zen"

    @property
    def purpose(self) -> str:
        return "Persist ZenGroundState to disk as JSON"

    async def invoke(self, state: ZenGroundState) -> Path:
        """
        Save state to disk atomically.

        Args:
            state: The ground state to save

        Returns:
            Path where state was saved

        Raises:
            OSError: If save fails
        """
        # Ensure directory exists
        self._path.parent.mkdir(parents=True, exist_ok=True)

        # Serialize state
        data = _serialize_ground_state(state)

        # Write to temp file first (atomic write)
        temp_path = self._path.with_suffix('.tmp')
        try:
            with open(temp_path, 'w') as f:
                json.dump(data, f, indent=2)

            # Atomic rename
            temp_path.rename(self._path)
            return self._path

        except OSError as e:
            # Clean up temp file if it exists
            if temp_path.exists():
                temp_path.unlink()
            raise OSError(f"Failed to save state: {e}") from e


# =============================================================================
# STATE LOAD AGENT
# =============================================================================

class StateLoad(Agent[Path, ZenGroundState | None]):
    """
    Load ZenGroundState from a JSON file.

    Type: Path → ZenGroundState | None

    Returns None if:
        - File doesn't exist
        - File is corrupted/invalid JSON
        - Data is missing required fields

    Graceful degradation - never crashes, just returns None.
    """

    def __init__(self, default_path: Path | None = None):
        """
        Initialize StateLoad.

        Args:
            default_path: Default path to load from (default: ~/.zen-agents/state.json)
        """
        if default_path:
            self._default_path = default_path
        else:
            self._default_path = Path.home() / ".zen-agents" / "state.json"

    @property
    def name(self) -> str:
        return "StateLoad"

    @property
    def genus(self) -> str:
        return "zen"

    @property
    def purpose(self) -> str:
        return "Load ZenGroundState from disk, gracefully handling errors"

    async def invoke(self, path: Path | None = None) -> ZenGroundState | None:
        """
        Load state from disk.

        Args:
            path: Path to load from (uses default if None)

        Returns:
            Loaded state, or None if file doesn't exist or is corrupted
        """
        load_path = path if path else self._default_path

        # Check if file exists
        if not load_path.exists():
            return None

        try:
            # Read and parse JSON
            with open(load_path) as f:
                data = json.load(f)

            # Deserialize to ZenGroundState
            return _deserialize_ground_state(data)

        except (json.JSONDecodeError, KeyError, TypeError, ValueError):
            # Corrupted file - return None
            return None
        except OSError:
            # Read error - return None
            return None


# =============================================================================
# SESSION PERSIST AGENT
# =============================================================================

class SessionPersist(Agent[Session, bool]):
    """
    Persist a single session update.

    Type: Session → bool

    Loads current state, updates the specified session, saves back.
    Returns True on success, False on failure.

    This is a convenience agent for incremental updates without
    having to load/modify/save the entire ground state manually.
    """

    def __init__(self, state_path: Path | None = None):
        """
        Initialize SessionPersist.

        Args:
            state_path: Path to state file (default: ~/.zen-agents/state.json)
        """
        self._state_path = state_path or (Path.home() / ".zen-agents" / "state.json")
        self._loader = StateLoad(self._state_path)
        self._saver = StateSave(self._state_path)

    @property
    def name(self) -> str:
        return "SessionPersist"

    @property
    def genus(self) -> str:
        return "zen"

    @property
    def purpose(self) -> str:
        return "Update a single session in persisted state"

    async def invoke(self, session: Session) -> bool:
        """
        Persist session to state file.

        Args:
            session: The session to persist

        Returns:
            True if successful, False otherwise
        """
        try:
            # Load current state (or create new if doesn't exist)
            state = await self._loader.invoke(self._state_path)

            if not state:
                # Create minimal state with just this session
                state = ZenGroundState(
                    config_cascade=[],
                    sessions={session.id: session},
                    tmux_sessions=[],
                    default_session_type=SessionType.CLAUDE,
                    auto_discovery=True,
                    max_sessions=10,
                    last_discovery=None,
                    last_updated=datetime.now(),
                )
            else:
                # Update session in existing state
                state.sessions[session.id] = session
                state.last_updated = datetime.now()

            # Save updated state
            await self._saver.invoke(state)
            return True

        except (OSError, Exception):
            # Any error - return False
            return False


# =============================================================================
# SINGLETON INSTANCES
# =============================================================================

# Default instances using standard paths
state_save = StateSave()
state_load = StateLoad()
session_persist = SessionPersist()


__all__ = [
    'StateSave',
    'StateLoad',
    'SessionPersist',
    'state_save',
    'state_load',
    'session_persist',
]
