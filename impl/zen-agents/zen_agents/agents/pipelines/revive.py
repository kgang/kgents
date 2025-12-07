"""
ReviveSessionPipeline: Restore a session that was detached or paused.

Pipeline:
    ValidateSession    # Judge: session exists and is revivable
    >> SpawnTmux       # Id: restart tmux session
    >> DetectState     # Fix: poll until state stabilizes
"""

from dataclasses import dataclass
from typing import TYPE_CHECKING

import sys
sys.path.insert(0, str(__file__).rsplit("/impl/", 1)[0] + "/impl/claude-openrouter")

from bootstrap import Agent, Verdict, VerdictType

if TYPE_CHECKING:
    from ...models import Session, SessionState
    from ...services.tmux import TmuxService
    from ..config import ZenConfig


class ReviveError(Exception):
    """Raised when session cannot be revived."""
    def __init__(self, reason: str):
        self.reason = reason
        super().__init__(reason)


@dataclass
class ReviveContext:
    """Context for revive pipeline."""
    session: "Session"
    zen_config: "ZenConfig"
    tmux: "TmuxService"


class ValidateSession(Agent["Session", "Session"]):
    """
    Judge: Validate session is revivable.

    A session can be revived if:
    - It exists in our records
    - It's not already running
    - It was previously paused or killed (not failed with error)
    """

    @property
    def name(self) -> str:
        return "ValidateSession"

    async def invoke(self, session: "Session") -> "Session":
        """Validate session is revivable."""
        from ...models import SessionState

        if session.state == SessionState.RUNNING:
            raise ReviveError("Session is already running")

        if session.state == SessionState.FAILED and session.exit_code:
            # Only allow revive if it didn't fail with an error
            if session.exit_code != 0:
                raise ReviveError(
                    f"Session failed with exit code {session.exit_code}. "
                    "Create a new session instead."
                )

        return session


class RespawnTmux(Agent[ReviveContext, "Session"]):
    """
    Id: Respawn the tmux session.

    Recreates the tmux session with the same settings.
    """

    @property
    def name(self) -> str:
        return "RespawnTmux"

    async def invoke(self, ctx: ReviveContext) -> "Session":
        """Respawn tmux session."""
        from ...models import SessionState

        session = ctx.session

        # Get command
        command = session.command or ctx.zen_config.session_commands.get(
            session.session_type.value,
            ctx.zen_config.default_shell,
        )

        # Check if tmux session still exists
        if await ctx.tmux.session_exists(session.tmux_name):
            # Just attach/resurrect
            await ctx.tmux.resurrect_session(session.tmux_name)
        else:
            # Recreate the session
            await ctx.tmux.create_session(
                name=session.tmux_name,
                command=command,
                working_dir=session.working_dir,
                scrollback=ctx.zen_config.scrollback_lines,
            )

        return session.with_state(SessionState.RUNNING)


class DetectRevivedState(Agent["Session", "Session"]):
    """
    Fix: Poll until revived session stabilizes.
    """

    def __init__(self, tmux: "TmuxService"):
        self._tmux = tmux

    @property
    def name(self) -> str:
        return "DetectRevivedState"

    async def invoke(self, session: "Session") -> "Session":
        """Detect state after revival."""
        from ..detection import detect_state

        result = await detect_state(
            session=session,
            tmux=self._tmux,
            max_iterations=10,
        )

        if result.converged:
            return session.with_state(result.value.session_state)

        return session


# Composed pipeline (conceptual)
ReviveSessionPipeline = (
    ValidateSession
    # >> RespawnTmux
    # >> DetectRevivedState
)


async def revive_session_pipeline(
    session: "Session",
    zen_config: "ZenConfig",
    tmux: "TmuxService",
) -> "Session":
    """
    Execute the full revive session pipeline.

    Returns the session with updated state.
    """
    # Step 1: Validate (Judge)
    validate = ValidateSession()
    session = await validate.invoke(session)

    # Step 2: Respawn tmux (Id)
    ctx = ReviveContext(
        session=session,
        zen_config=zen_config,
        tmux=tmux,
    )
    respawn = RespawnTmux()
    session = await respawn.invoke(ctx)

    # Step 3: Detect state (Fix)
    detect = DetectRevivedState(tmux)
    session = await detect.invoke(session)

    return session
