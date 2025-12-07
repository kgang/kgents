"""
Session Lifecycle Agents (Pause, Kill)

Simple state transitions for session lifecycle.
These are straightforward morphisms - not as interesting as detect,
but essential for completeness.
"""

import sys
from dataclasses import replace
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "claude-openrouter"))

from bootstrap import Agent
from ..types import (
    Session,
    SessionState,
)


class SessionPause(Agent[Session, Session]):
    """
    Pause a running session.

    Type signature: SessionPause: Session → Session

    Transition: RUNNING → PAUSED

    In tmux terms: detach the session but keep it alive.
    """

    @property
    def name(self) -> str:
        return "SessionPause"

    @property
    def genus(self) -> str:
        return "zen/session"

    @property
    def purpose(self) -> str:
        return "Transition session from running to paused"

    async def invoke(self, session: Session) -> Session:
        """
        Pause a session.

        Only valid for RUNNING sessions.
        Returns unchanged session if not in valid state.
        """
        if session.state != SessionState.RUNNING:
            # Invalid transition - return unchanged
            return session

        # Create new session with PAUSED state
        return replace(session, state=SessionState.PAUSED)


class SessionKill(Agent[Session, Session]):
    """
    Kill a session.

    Type signature: SessionKill: Session → Session

    Transition: (RUNNING | PAUSED | CREATING) → COMPLETED

    Forcibly terminates the session.
    """

    @property
    def name(self) -> str:
        return "SessionKill"

    @property
    def genus(self) -> str:
        return "zen/session"

    @property
    def purpose(self) -> str:
        return "Forcibly terminate a session"

    async def invoke(self, session: Session) -> Session:
        """
        Kill a session.

        Valid for any alive session.
        Returns unchanged if already dead.
        """
        if not session.is_alive():
            return session

        # In real impl: tmux kill-session -t {session.tmux.id}

        return replace(
            session,
            state=SessionState.COMPLETED,
            completed_at=datetime.now(),
        )


class SessionResume(Agent[Session, Session]):
    """
    Resume a paused session.

    Type signature: SessionResume: Session → Session

    Transition: PAUSED → RUNNING
    """

    @property
    def name(self) -> str:
        return "SessionResume"

    @property
    def genus(self) -> str:
        return "zen/session"

    @property
    def purpose(self) -> str:
        return "Resume a paused session"

    async def invoke(self, session: Session) -> Session:
        """Resume a paused session."""
        if session.state != SessionState.PAUSED:
            return session

        return replace(session, state=SessionState.RUNNING)


# Singleton instances
pause_session = SessionPause()
kill_session = SessionKill()
resume_session = SessionResume()
