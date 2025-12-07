"""
Session Lifecycle Agents (Pause, Kill, Revive)

Complete session lifecycle morphisms with tmux integration.
Maps zenportal's session_manager pause/kill/revive to kgents agents.

Key agents:
    - SessionPause: Session → Session (RUNNING → PAUSED, kills tmux)
    - SessionKill: Session → Session (Any → COMPLETED, kills tmux + cleanup)
    - SessionRevive: Session → Session (PAUSED/COMPLETED/FAILED → RUNNING, respawns tmux)
    - SessionResume: Session → Session (PAUSED → RUNNING, simple state change)
"""

from dataclasses import replace
from datetime import datetime
from pathlib import Path

from bootstrap import Agent
from ..types import (
    Session,
    SessionState,
)
from ..tmux import TmuxKill, TmuxClear, TmuxSpawn
from ..tmux.spawn import SpawnInput


class SessionPause(Agent[Session, Session]):
    """
    Pause a running session.

    Type signature: SessionPause: Session → Session

    Transition: RUNNING → PAUSED

    Maps to zenportal's pause_session():
        1. Clear tmux history
        2. Kill tmux session
        3. Set state to PAUSED
        4. Record ended_at time
    """

    def __init__(self, socket_path: str | None = None):
        self._tmux_clear = TmuxClear(socket_path=socket_path)
        self._tmux_kill = TmuxKill(socket_path=socket_path)

    @property
    def name(self) -> str:
        return "SessionPause"

    @property
    def genus(self) -> str:
        return "zen/session"

    @property
    def purpose(self) -> str:
        return "Pause a running session (kill tmux but preserve state)"

    async def invoke(self, session: Session) -> Session:
        """
        Pause a session.

        Only valid for RUNNING sessions.
        Kills the tmux session but preserves session state for revival.
        Returns unchanged session if not in valid state.
        """
        if session.state != SessionState.RUNNING:
            # Invalid transition - return unchanged
            return session

        # If tmux session exists, clean it up
        if session.tmux:
            # Clear history first (following zenportal pattern)
            await self._tmux_clear.invoke(session.tmux)
            # Kill the tmux session
            await self._tmux_kill.invoke(session.tmux)

        # Create new session with PAUSED state
        return replace(
            session,
            state=SessionState.PAUSED,
            completed_at=datetime.now(),  # Record when paused
        )


class SessionKill(Agent[Session, Session]):
    """
    Kill a session permanently.

    Type signature: SessionKill: Session → Session

    Transition: (RUNNING | PAUSED | CREATING) → COMPLETED

    Maps to zenportal's kill_session():
        1. Clear tmux history
        2. Kill tmux session
        3. Set state to COMPLETED (note: zenportal uses KILLED state)
        4. Record ended_at time

    Note: We use COMPLETED instead of KILLED to match the existing SessionState enum.
    In zenportal, KILLED is a separate state but the current zen-agents types don't have it.
    """

    def __init__(self, socket_path: str | None = None):
        self._tmux_clear = TmuxClear(socket_path=socket_path)
        self._tmux_kill = TmuxKill(socket_path=socket_path)

    @property
    def name(self) -> str:
        return "SessionKill"

    @property
    def genus(self) -> str:
        return "zen/session"

    @property
    def purpose(self) -> str:
        return "Forcibly terminate a session permanently"

    async def invoke(self, session: Session) -> Session:
        """
        Kill a session.

        Valid for any alive session.
        Returns unchanged if already dead.
        Cleans up tmux session and marks as completed.
        """
        if not session.is_alive():
            return session

        # If tmux session exists, clean it up
        if session.tmux:
            # Clear history first (following zenportal pattern)
            await self._tmux_clear.invoke(session.tmux)
            # Kill the tmux session
            await self._tmux_kill.invoke(session.tmux)

        return replace(
            session,
            state=SessionState.COMPLETED,
            completed_at=datetime.now(),
        )


class SessionRevive(Agent[Session, Session]):
    """
    Revive a paused/completed/failed session.

    Type signature: SessionRevive: Session → Session

    Transition: (PAUSED | COMPLETED | FAILED) → RUNNING

    Maps to zenportal's revive_session():
        1. Clear old tmux session if exists
        2. Kill old tmux session
        3. Spawn new tmux session with same command
        4. Set state to RUNNING
        5. Clear ended_at, set started_at

    This is different from SessionResume - it actually respawns the tmux session.
    """

    def __init__(self, socket_path: str | None = None):
        self._tmux_clear = TmuxClear(socket_path=socket_path)
        self._tmux_kill = TmuxKill(socket_path=socket_path)
        self._tmux_spawn = TmuxSpawn(socket_path=socket_path)

    @property
    def name(self) -> str:
        return "SessionRevive"

    @property
    def genus(self) -> str:
        return "zen/session"

    @property
    def purpose(self) -> str:
        return "Revive a paused/completed/failed session (respawn tmux)"

    async def invoke(self, session: Session) -> Session:
        """
        Revive a session.

        Valid for PAUSED, COMPLETED, or FAILED sessions.
        Returns unchanged if already RUNNING or CREATING.
        Respawns the tmux session with the same configuration.
        """
        # Only revive non-running sessions
        if session.state in {SessionState.RUNNING, SessionState.CREATING}:
            return session

        # Clean up old tmux session if it exists
        if session.tmux:
            await self._tmux_clear.invoke(session.tmux)
            await self._tmux_kill.invoke(session.tmux)

        # Determine command to run
        command = session.config.command
        if not command:
            # If no command specified, return with error
            return replace(
                session,
                state=SessionState.FAILED,
                error="Cannot revive: no command specified in config",
            )

        # Determine working directory
        working_dir = None
        if session.config.working_dir:
            working_dir = Path(session.config.working_dir)

        # Spawn new tmux session
        spawn_input = SpawnInput(
            name=session.id,
            command=command,
            working_dir=working_dir,
            env=session.config.env,
        )

        spawn_result = await self._tmux_spawn.invoke(spawn_input)

        # Check if spawn failed
        from ..tmux.spawn import SpawnError
        if isinstance(spawn_result, SpawnError):
            return replace(
                session,
                state=SessionState.FAILED,
                error=f"Failed to revive: {spawn_result.error}",
                completed_at=datetime.now(),
            )

        # Success - update session with new tmux session
        return replace(
            session,
            state=SessionState.RUNNING,
            tmux=spawn_result,
            error=None,
            started_at=datetime.now(),
            completed_at=None,  # Clear completed_at since we're running again
        )


class SessionResume(Agent[Session, Session]):
    """
    Resume a paused session (simple state change).

    Type signature: SessionResume: Session → Session

    Transition: PAUSED → RUNNING

    This is a simple state transition without tmux interaction.
    Use SessionRevive if you need to respawn the tmux session.
    """

    @property
    def name(self) -> str:
        return "SessionResume"

    @property
    def genus(self) -> str:
        return "zen/session"

    @property
    def purpose(self) -> str:
        return "Resume a paused session (state change only)"

    async def invoke(self, session: Session) -> Session:
        """Resume a paused session."""
        if session.state != SessionState.PAUSED:
            return session

        return replace(session, state=SessionState.RUNNING)


# Singleton instances
pause_session = SessionPause()
kill_session = SessionKill()
revive_session = SessionRevive()
resume_session = SessionResume()
