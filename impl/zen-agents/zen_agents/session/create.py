"""
SessionCreate Agent

Create: SessionConfig → Session
Create(config) = Session(state=CREATING, config=config, ...)

Takes a validated session configuration and produces a session object.
Does NOT start the session - that's for tmux agents.

This is a pure transform: config in, session out.
"""

import sys
import uuid
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "claude-openrouter"))

from bootstrap import Agent
from ..types import (
    Session,
    SessionConfig,
    SessionState,
)


class SessionCreate(Agent[SessionConfig, Session]):
    """
    Creates a session object from configuration.

    Type signature: SessionCreate: SessionConfig → Session

    This is the first step in the session lifecycle.
    The resulting session is in CREATING state - not yet running.

    Pure transform:
        - Generates unique ID
        - Sets initial state
        - Records creation time
        - Does NOT interact with tmux
    """

    @property
    def name(self) -> str:
        return "SessionCreate"

    @property
    def genus(self) -> str:
        return "zen/session"

    @property
    def purpose(self) -> str:
        return "Transform session config into session object"

    async def invoke(self, config: SessionConfig) -> Session:
        """
        Create a session from config.

        The session starts in CREATING state.
        Use Compose with tmux agents to actually start it.
        """
        session_id = self._generate_id(config.name)

        return Session(
            id=session_id,
            config=config,
            state=SessionState.CREATING,
            tmux=None,  # Not yet spawned
            output_lines=[],
            error=None,
            started_at=None,  # Not yet started
            completed_at=None,
        )

    def _generate_id(self, name: str) -> str:
        """Generate a unique session ID based on name"""
        short_uuid = uuid.uuid4().hex[:8]
        return f"{name}-{short_uuid}"


# Singleton instance
create_session = SessionCreate()
