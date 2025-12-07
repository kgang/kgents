"""
CleanSessionPipeline: Clean up (kill) a session.

Pipeline:
    ValidateKill      # Judge: session exists and can be killed
    >> SendSignal     # Graceful shutdown attempt
    >> KillTmux       # Force kill tmux session
    >> CleanupSession # Remove from tracking
"""

from dataclasses import dataclass
from typing import TYPE_CHECKING
import asyncio

import sys
sys.path.insert(0, str(__file__).rsplit("/impl/", 1)[0] + "/impl/claude-openrouter")

from bootstrap import Agent, fix, FixResult

if TYPE_CHECKING:
    from ...models import Session, SessionState
    from ...services.tmux import TmuxService
    from ..config import ZenConfig


class CleanError(Exception):
    """Raised when session cannot be cleaned."""
    def __init__(self, reason: str):
        self.reason = reason
        super().__init__(reason)


@dataclass
class CleanContext:
    """Context for clean pipeline."""
    session: "Session"
    zen_config: "ZenConfig"
    tmux: "TmuxService"
    force: bool = False  # Skip graceful shutdown


class ValidateKill(Agent["Session", "Session"]):
    """
    Judge: Validate session can be killed.
    """

    @property
    def name(self) -> str:
        return "ValidateKill"

    async def invoke(self, session: "Session") -> "Session":
        """Validate session can be killed."""
        from ...models import SessionState

        if session.state == SessionState.KILLED:
            raise CleanError("Session is already killed")

        if session.state == SessionState.COMPLETED:
            # Already completed - just cleanup
            pass

        return session


class SendGracefulSignal(Agent[CleanContext, CleanContext]):
    """
    Attempt graceful shutdown first.

    Send SIGTERM and wait for grace period.
    """

    @property
    def name(self) -> str:
        return "SendGracefulSignal"

    async def invoke(self, ctx: CleanContext) -> CleanContext:
        """Send graceful shutdown signal."""
        if ctx.force:
            return ctx

        # Send SIGTERM
        await ctx.tmux.send_signal(ctx.session.tmux_name, "TERM")

        # Wait for grace period
        grace = ctx.zen_config.grace_period

        @dataclass
        class ShutdownState:
            is_alive: bool
            waited: float

        async def poll_shutdown(state: ShutdownState) -> ShutdownState:
            """Poll for graceful shutdown."""
            await asyncio.sleep(0.5)
            is_alive = await ctx.tmux.is_session_alive(ctx.session.tmux_name)
            return ShutdownState(is_alive, state.waited + 0.5)

        result = await fix(
            transform=poll_shutdown,
            initial=ShutdownState(True, 0.0),
            equality_check=lambda a, b: not b.is_alive or b.waited >= grace,
            max_iterations=int(grace * 2),  # Poll every 0.5s
        )

        # Mark if graceful shutdown succeeded
        ctx._graceful_shutdown = not result.value.is_alive  # type: ignore

        return ctx


class KillTmux(Agent[CleanContext, CleanContext]):
    """
    Force kill tmux session.

    Called if graceful shutdown failed or force=True.
    """

    @property
    def name(self) -> str:
        return "KillTmux"

    async def invoke(self, ctx: CleanContext) -> CleanContext:
        """Kill tmux session."""
        graceful = getattr(ctx, "_graceful_shutdown", False)

        if graceful:
            # Already shut down gracefully
            return ctx

        # Force kill
        await ctx.tmux.kill_session(ctx.session.tmux_name)

        return ctx


class CleanupSession(Agent[CleanContext, "Session"]):
    """
    Clean up session state.

    Mark session as killed and prepare for removal from tracking.
    """

    @property
    def name(self) -> str:
        return "CleanupSession"

    async def invoke(self, ctx: CleanContext) -> "Session":
        """Mark session as killed."""
        from ...models import SessionState

        graceful = getattr(ctx, "_graceful_shutdown", False)

        # Get exit code if available
        exit_code = await ctx.tmux.get_exit_code(ctx.session.tmux_name)

        session = ctx.session.with_state(SessionState.KILLED)
        session.exit_code = exit_code

        return session


# Composed pipeline (conceptual)
CleanSessionPipeline = (
    ValidateKill
    # >> SendGracefulSignal
    # >> KillTmux
    # >> CleanupSession
)


async def clean_session_pipeline(
    session: "Session",
    zen_config: "ZenConfig",
    tmux: "TmuxService",
    force: bool = False,
) -> "Session":
    """
    Execute the full clean session pipeline.

    Returns the session with KILLED state.
    """
    # Step 1: Validate (Judge)
    validate = ValidateKill()
    session = await validate.invoke(session)

    ctx = CleanContext(
        session=session,
        zen_config=zen_config,
        tmux=tmux,
        force=force,
    )

    # Step 2: Graceful shutdown attempt
    graceful = SendGracefulSignal()
    ctx = await graceful.invoke(ctx)

    # Step 3: Force kill if needed
    kill = KillTmux()
    ctx = await kill.invoke(ctx)

    # Step 4: Cleanup
    cleanup = CleanupSession()
    session = await cleanup.invoke(ctx)

    return session


async def clean_all_sessions(
    sessions: list["Session"],
    zen_config: "ZenConfig",
    tmux: "TmuxService",
    force: bool = False,
) -> list["Session"]:
    """
    Clean all sessions in parallel.

    Returns list of cleaned sessions.
    """
    tasks = [
        clean_session_pipeline(s, zen_config, tmux, force)
        for s in sessions
    ]
    return await asyncio.gather(*tasks, return_exceptions=False)
