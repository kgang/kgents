"""
TmuxKill and TmuxClear Agents

Kill: TmuxSession → KillResult
Kill(session) = tmux kill-session -t SESSION

Clear: TmuxSession → ClearResult
Clear(session) = tmux clear-history -t SESSION

Maps to zenportal's TmuxService.kill_session() and clear_history()
"""

import asyncio
from dataclasses import dataclass

from bootstrap import Agent
from ..types import TmuxSession


@dataclass
class KillResult:
    """Result of killing a tmux session"""
    success: bool
    session_id: str
    error: str | None = None


@dataclass
class ClearResult:
    """Result of clearing tmux history"""
    success: bool
    session_id: str
    error: str | None = None


class TmuxKill(Agent[TmuxSession, KillResult]):
    """
    Kill a tmux session.

    Type signature: TmuxKill: TmuxSession → KillResult

    Maps to zenportal's TmuxService.kill_session()

    Executes: tmux kill-session -t SESSION_NAME
    """

    def __init__(self, socket_path: str | None = None):
        self._socket_path = socket_path

    @property
    def name(self) -> str:
        return "TmuxKill"

    @property
    def genus(self) -> str:
        return "zen/tmux"

    @property
    def purpose(self) -> str:
        return "Kill a tmux session"

    async def invoke(self, session: TmuxSession) -> KillResult:
        """
        Kill the tmux session.

        Returns KillResult indicating success/failure.
        """
        cmd_parts = ["tmux"]

        if self._socket_path:
            cmd_parts.extend(["-L", self._socket_path])

        cmd_parts.extend(["kill-session", "-t", session.id])

        try:
            process = await asyncio.create_subprocess_exec(
                *cmd_parts,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

            stdout, stderr = await asyncio.wait_for(
                process.communicate(),
                timeout=5.0,
            )

            if process.returncode != 0:
                return KillResult(
                    success=False,
                    session_id=session.id,
                    error=stderr.decode().strip() or f"Exit code {process.returncode}",
                )

            return KillResult(success=True, session_id=session.id)

        except asyncio.TimeoutError:
            return KillResult(
                success=False,
                session_id=session.id,
                error="Timeout killing session",
            )
        except Exception as e:
            return KillResult(
                success=False,
                session_id=session.id,
                error=str(e),
            )


class TmuxClear(Agent[TmuxSession, ClearResult]):
    """
    Clear tmux session history.

    Type signature: TmuxClear: TmuxSession → ClearResult

    Maps to zenportal's TmuxService.clear_history()

    Executes: tmux clear-history -t SESSION_NAME
    """

    def __init__(self, socket_path: str | None = None):
        self._socket_path = socket_path

    @property
    def name(self) -> str:
        return "TmuxClear"

    @property
    def genus(self) -> str:
        return "zen/tmux"

    @property
    def purpose(self) -> str:
        return "Clear tmux session scrollback history"

    async def invoke(self, session: TmuxSession) -> ClearResult:
        """
        Clear the session's scrollback history.

        Returns ClearResult indicating success/failure.
        """
        cmd_parts = ["tmux"]

        if self._socket_path:
            cmd_parts.extend(["-L", self._socket_path])

        cmd_parts.extend(["clear-history", "-t", session.id])

        try:
            process = await asyncio.create_subprocess_exec(
                *cmd_parts,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

            stdout, stderr = await asyncio.wait_for(
                process.communicate(),
                timeout=5.0,
            )

            if process.returncode != 0:
                return ClearResult(
                    success=False,
                    session_id=session.id,
                    error=stderr.decode().strip() or f"Exit code {process.returncode}",
                )

            return ClearResult(success=True, session_id=session.id)

        except asyncio.TimeoutError:
            return ClearResult(
                success=False,
                session_id=session.id,
                error="Timeout clearing history",
            )
        except Exception as e:
            return ClearResult(
                success=False,
                session_id=session.id,
                error=str(e),
            )


# Singleton instances
kill_tmux = TmuxKill()
clear_tmux = TmuxClear()
