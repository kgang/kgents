"""
ZenGround Agent

Ground: Void → ZenGroundState
Ground() = {config cascade, known sessions, tmux facts, preferences}

The empirical seed for zen-agents. Extends kgents Ground with
session-management specific state.

What it grounds:
    - The 3-tier config cascade (global > portal > session)
    - Known sessions and their states
    - Raw tmux facts (the "world")
    - User preferences for zen behavior
"""

from datetime import datetime
from pathlib import Path
from typing import Any

from bootstrap import Agent, ground_agent, KENT_PERSONA
from .types import (
    ZenGroundState,
    ConfigLayer,
    Session,
    SessionConfig,
    SessionType,
    SessionState,
    TmuxSession,
)
from .persistence import state_load, state_save


class ZenGround(Agent[None, ZenGroundState]):
    """
    The empirical seed for zen-agents.

    Type signature: ZenGround: Void → ZenGroundState

    Produces the irreducible facts about:
        - Configuration hierarchy
        - Session state
        - tmux reality
        - User preferences

    This is the "world model" from which all zen-agents operate.
    """

    def __init__(
        self,
        config_path: Path | None = None,
        discover_tmux: bool = True,
        auto_persist: bool = True,
    ):
        self._config_path = config_path
        self._discover_tmux = discover_tmux
        self._auto_persist = auto_persist
        self._cached_state: ZenGroundState | None = None
        self._loaded = False

    @property
    def name(self) -> str:
        return "ZenGround"

    @property
    def genus(self) -> str:
        return "zen"

    @property
    def purpose(self) -> str:
        return "Empirical seed for zen-agents; session-specific ground state"

    async def invoke(self, input: None = None) -> ZenGroundState:
        """
        Build and return the ground state.

        This gathers facts from:
            1. Persisted state (if exists and not yet loaded)
            2. Config files (if present)
            3. tmux (if available)
            4. Cached session state
        """
        # Load persisted state on first invoke
        if not self._loaded:
            await self._load_persisted_state()
            self._loaded = True

        # Build config cascade
        config_cascade = await self._build_config_cascade()

        # Discover tmux sessions (if enabled)
        tmux_sessions = []
        if self._discover_tmux:
            tmux_sessions = await self._discover_tmux_sessions()

        # Get known sessions (from cache or empty)
        sessions = self._cached_state.sessions if self._cached_state else {}

        # Build state
        state = ZenGroundState(
            config_cascade=config_cascade,
            sessions=sessions,
            tmux_sessions=tmux_sessions,
            default_session_type=SessionType.CLAUDE,
            auto_discovery=True,
            max_sessions=10,
            last_discovery=datetime.now() if self._discover_tmux else None,
            last_updated=datetime.now(),
        )

        self._cached_state = state
        return state

    async def _load_persisted_state(self) -> None:
        """Load state from disk if available."""
        loaded = await state_load.invoke(None)
        if loaded:
            self._cached_state = loaded

    async def save(self) -> bool:
        """Persist current state to disk."""
        if self._cached_state:
            try:
                await state_save.invoke(self._cached_state)
                return True
            except OSError:
                return False
        return False

    async def _build_config_cascade(self) -> list[ConfigLayer]:
        """
        Build the 3-tier config cascade.

        In zenportal: config.toml > portal.toml > session overrides
        Here: simplified to layers that can be merged.
        """
        layers = []

        # Global defaults (hardcoded for now)
        layers.append(ConfigLayer(
            name="global",
            values={
                "default_shell": "/bin/zsh",
                "default_session_type": "claude",
                "tmux_prefix": "zen",
                "auto_attach": True,
            }
        ))

        # Portal config (would read from file)
        if self._config_path and self._config_path.exists():
            # TODO: Actually read config file
            layers.append(ConfigLayer(
                name="portal",
                values={}
            ))

        return layers

    async def _discover_tmux_sessions(self) -> list[TmuxSession]:
        """
        Discover running tmux sessions.

        This is the empirical "world state" - what actually exists.
        In full implementation, would shell out to `tmux list-sessions`.
        """
        # Placeholder - in real impl, would run:
        # tmux list-sessions -F "#{session_id}:#{session_name}:#{session_created}"
        return []

    def update_session(self, session: Session) -> None:
        """Update a session in the ground state (mutation!)"""
        if self._cached_state:
            self._cached_state.sessions[session.id] = session
            self._cached_state.last_updated = datetime.now()

    def query(self, aspect: str) -> Any:
        """
        Query a specific aspect of the ground state.

        Examples:
            zen_ground.query("config.default_shell")
            zen_ground.query("sessions.my-session.state")
        """
        if not self._cached_state:
            return None

        parts = aspect.split(".")
        current: Any = self._cached_state

        for part in parts:
            if hasattr(current, part):
                current = getattr(current, part)
            elif isinstance(current, dict) and part in current:
                current = current[part]
            else:
                return None

        return current


# Singleton instance
zen_ground = ZenGround()
