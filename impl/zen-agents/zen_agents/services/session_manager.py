"""
Session Manager - Orchestrates pipelines for session lifecycle.

The central coordinator that:
- Maintains session registry
- Dispatches to appropriate pipelines
- Emits events for UI updates
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Callable, Optional, Awaitable
from uuid import UUID
import asyncio

from ..models import Session, SessionState, SessionType, NewSessionConfig
from ..agents.config import ConfigGround, ZenConfig, ResolveConfig
from ..agents.pipelines.create import create_session_pipeline, ValidationError, ConflictError
from ..agents.pipelines.revive import revive_session_pipeline, ReviveError
from ..agents.pipelines.clean import clean_session_pipeline, clean_all_sessions, CleanError
from .tmux import TmuxService


# Event types for UI updates
@dataclass
class SessionEvent:
    """Base event for session changes."""
    session_id: UUID
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass(kw_only=True)
class SessionCreated(SessionEvent):
    """Emitted when a session is created."""
    session: Session


@dataclass(kw_only=True)
class SessionStateChanged(SessionEvent):
    """Emitted when session state changes."""
    old_state: SessionState
    new_state: SessionState


@dataclass(kw_only=True)
class SessionKilled(SessionEvent):
    """Emitted when a session is killed."""
    exit_code: Optional[int] = None


@dataclass(kw_only=True)
class SessionError(SessionEvent):
    """Emitted when an error occurs."""
    error: str
    error_type: str


EventHandler = Callable[[SessionEvent], Awaitable[None]]


class SessionManager:
    """
    Orchestrates session lifecycle operations.

    This is the main interface for the TUI to interact with sessions.
    """

    def __init__(
        self,
        tmux: Optional[TmuxService] = None,
        session_config: Optional[dict] = None,
    ):
        self._tmux = tmux or TmuxService()
        self._sessions: dict[UUID, Session] = {}
        self._event_handlers: list[EventHandler] = []
        self._zen_config: Optional[ZenConfig] = None
        self._session_config = session_config or {}
        self._lock = asyncio.Lock()

    @property
    def sessions(self) -> list[Session]:
        """Get all sessions."""
        return list(self._sessions.values())

    @property
    def tmux(self) -> TmuxService:
        """Get the tmux service."""
        return self._tmux

    def get_session(self, session_id: UUID) -> Optional[Session]:
        """Get a session by ID."""
        return self._sessions.get(session_id)

    def get_session_by_name(self, name: str) -> Optional[Session]:
        """Get a session by name."""
        for session in self._sessions.values():
            if session.name == name:
                return session
        return None

    def add_event_handler(self, handler: EventHandler) -> None:
        """Add an event handler for session events."""
        self._event_handlers.append(handler)

    def remove_event_handler(self, handler: EventHandler) -> None:
        """Remove an event handler."""
        if handler in self._event_handlers:
            self._event_handlers.remove(handler)

    async def _emit_event(self, event: SessionEvent) -> None:
        """Emit an event to all handlers."""
        for handler in self._event_handlers:
            try:
                await handler(event)
            except Exception:
                pass  # Don't let handler errors break the manager

    async def _ensure_config(self) -> ZenConfig:
        """Ensure we have loaded config."""
        if self._zen_config is None:
            ground = ConfigGround(session_config=self._session_config)
            facts = await ground.invoke(None)
            resolve = ResolveConfig()
            self._zen_config = await resolve.invoke(facts)
        return self._zen_config

    async def create_session(
        self,
        name: str,
        session_type: SessionType,
        working_dir: Optional[str] = None,
        command: Optional[str] = None,
        env: Optional[dict[str, str]] = None,
        model: Optional[str] = None,
    ) -> Session:
        """
        Create a new session.

        Executes the create pipeline and returns the new session.
        Raises ValidationError or ConflictError on failure.
        """
        async with self._lock:
            config = NewSessionConfig(
                name=name,
                session_type=session_type,
                working_dir=working_dir,
                command=command,
                env=env or {},
                model=model,
            )

            zen_config = await self._ensure_config()

            session = await create_session_pipeline(
                config=config,
                zen_config=zen_config,
                existing_sessions=self.sessions,
                tmux=self._tmux,
            )

            # Register session
            self._sessions[session.id] = session

            # Emit event
            await self._emit_event(SessionCreated(
                session_id=session.id,
                session=session,
            ))

            return session

    async def revive_session(self, session_id: UUID) -> Session:
        """
        Revive a paused or killed session.

        Raises ReviveError on failure.
        """
        async with self._lock:
            session = self._sessions.get(session_id)
            if not session:
                raise ReviveError(f"Session {session_id} not found")

            old_state = session.state
            zen_config = await self._ensure_config()

            session = await revive_session_pipeline(
                session=session,
                zen_config=zen_config,
                tmux=self._tmux,
            )

            # Update registry
            self._sessions[session.id] = session

            # Emit event
            await self._emit_event(SessionStateChanged(
                session_id=session.id,
                old_state=old_state,
                new_state=session.state,
            ))

            return session

    async def kill_session(
        self,
        session_id: UUID,
        force: bool = False,
    ) -> Session:
        """
        Kill a session.

        If force=True, skip graceful shutdown.
        Raises CleanError on failure.
        """
        async with self._lock:
            session = self._sessions.get(session_id)
            if not session:
                raise CleanError(f"Session {session_id} not found")

            zen_config = await self._ensure_config()

            session = await clean_session_pipeline(
                session=session,
                zen_config=zen_config,
                tmux=self._tmux,
                force=force,
            )

            # Update registry
            self._sessions[session.id] = session

            # Emit event
            await self._emit_event(SessionKilled(
                session_id=session.id,
                exit_code=session.exit_code,
            ))

            return session

    async def kill_all_sessions(self, force: bool = False) -> list[Session]:
        """Kill all sessions."""
        async with self._lock:
            zen_config = await self._ensure_config()

            sessions = await clean_all_sessions(
                sessions=self.sessions,
                zen_config=zen_config,
                tmux=self._tmux,
                force=force,
            )

            # Update registry
            for session in sessions:
                self._sessions[session.id] = session
                await self._emit_event(SessionKilled(
                    session_id=session.id,
                    exit_code=session.exit_code,
                ))

            return sessions

    async def remove_session(self, session_id: UUID) -> bool:
        """
        Remove a session from tracking.

        Only removes from registry, does not kill tmux.
        Use kill_session first if session is still running.
        """
        async with self._lock:
            if session_id in self._sessions:
                del self._sessions[session_id]
                return True
            return False

    async def update_session_state(
        self,
        session_id: UUID,
        new_state: SessionState,
        exit_code: Optional[int] = None,
    ) -> Optional[Session]:
        """
        Update a session's state.

        Called by StateRefresher when state changes are detected.
        """
        async with self._lock:
            session = self._sessions.get(session_id)
            if not session:
                return None

            if session.state == new_state:
                return session

            old_state = session.state
            session = session.with_state(new_state)
            if exit_code is not None:
                session.exit_code = exit_code

            self._sessions[session.id] = session

            await self._emit_event(SessionStateChanged(
                session_id=session.id,
                old_state=old_state,
                new_state=new_state,
            ))

            return session

    async def refresh_sessions_from_tmux(self) -> None:
        """
        Sync session states with actual tmux state.

        Useful on startup to recover state.
        """
        async with self._lock:
            # Get actual tmux sessions
            tmux_sessions = await self._tmux.list_sessions()
            zen_prefix = (await self._ensure_config()).tmux_prefix

            # Filter to our sessions
            our_tmux = [s for s in tmux_sessions if s.startswith(zen_prefix)]

            # Update states
            for session in list(self._sessions.values()):
                if session.tmux_name in our_tmux:
                    is_alive = await self._tmux.is_session_alive(session.tmux_name)
                    if is_alive and session.state != SessionState.RUNNING:
                        await self.update_session_state(
                            session.id,
                            SessionState.RUNNING,
                        )
                    elif not is_alive and session.state == SessionState.RUNNING:
                        exit_code = await self._tmux.get_exit_code(session.tmux_name)
                        new_state = (
                            SessionState.COMPLETED
                            if exit_code == 0
                            else SessionState.FAILED
                        )
                        await self.update_session_state(
                            session.id,
                            new_state,
                            exit_code,
                        )
                else:
                    # Tmux session is gone
                    if session.state == SessionState.RUNNING:
                        await self.update_session_state(
                            session.id,
                            SessionState.KILLED,
                        )
