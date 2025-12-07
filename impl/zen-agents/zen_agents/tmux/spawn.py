"""
TmuxSpawn Agent

Spawn: SpawnInput → TmuxSession | SpawnError
Spawn(input) = tmux new-session -d -s NAME -c DIR COMMAND

Creates a new detached tmux session.
Maps to zenportal's TmuxService.create_session()
"""

import sys
import asyncio
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "claude-openrouter"))

from bootstrap import Agent
from ..types import TmuxSession


@dataclass
class SpawnInput:
    """Input for spawning a tmux session"""
    name: str
    command: str
    working_dir: Path | None = None
    env: dict[str, str] | None = None


@dataclass
class SpawnError:
    """Returned when spawn fails"""
    error: str
    name: str


class TmuxSpawn(Agent[SpawnInput, TmuxSession | SpawnError]):
    """
    Spawn a new tmux session.

    Type signature: TmuxSpawn: SpawnInput → TmuxSession | SpawnError

    Maps to zenportal's TmuxService.create_session()

    tmux options applied:
        - remain-on-exit on (pane stays after process exits)
        - history-limit 50000 (scrollback)
        - detached mode (-d)
    """

    def __init__(self, prefix: str = "zen", socket_path: str | None = None):
        self._prefix = prefix
        self._socket_path = socket_path

    @property
    def name(self) -> str:
        return "TmuxSpawn"

    @property
    def genus(self) -> str:
        return "zen/tmux"

    @property
    def purpose(self) -> str:
        return "Spawn a new detached tmux session"

    async def invoke(self, input: SpawnInput) -> TmuxSession | SpawnError:
        """
        Create a tmux session.

        Returns TmuxSession on success, SpawnError on failure.
        """
        session_name = f"{self._prefix}-{input.name}"
        working_dir = input.working_dir or Path.cwd()

        # Build tmux command
        cmd_parts = ["tmux"]

        if self._socket_path:
            cmd_parts.extend(["-L", self._socket_path])

        cmd_parts.extend([
            "new-session",
            "-d",                              # Detached
            "-s", session_name,                # Session name
            "-c", str(working_dir),            # Working directory
        ])

        # Add the command to run
        cmd_parts.append(input.command)

        try:
            # Run tmux command
            env = {**dict(input.env or {})}
            process = await asyncio.create_subprocess_exec(
                *cmd_parts,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                env=env if env else None,
            )

            stdout, stderr = await asyncio.wait_for(
                process.communicate(),
                timeout=5.0,
            )

            if process.returncode != 0:
                return SpawnError(
                    error=stderr.decode().strip() or f"Exit code {process.returncode}",
                    name=session_name,
                )

            # Set tmux options
            await self._configure_session(session_name)

            # Get pane ID
            pane_id = await self._get_pane_id(session_name)

            return TmuxSession(
                id=session_name,
                name=input.name,
                pane_id=pane_id or f"{session_name}:0.0",
                created_at=datetime.now(),
                is_attached=False,
            )

        except asyncio.TimeoutError:
            return SpawnError(error="Timeout creating session", name=session_name)
        except Exception as e:
            return SpawnError(error=str(e), name=session_name)

    async def _configure_session(self, session_name: str) -> None:
        """Configure tmux session options"""
        options = [
            ("remain-on-exit", "on"),
            ("history-limit", "50000"),
        ]

        for option, value in options:
            cmd = ["tmux", "set-option", "-t", session_name, option, value]
            if self._socket_path:
                cmd.insert(1, "-L")
                cmd.insert(2, self._socket_path)

            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.DEVNULL,
                stderr=asyncio.subprocess.DEVNULL,
            )
            await process.wait()

    async def _get_pane_id(self, session_name: str) -> str | None:
        """Get the pane ID for a session"""
        cmd = ["tmux", "display-message", "-t", session_name, "-p", "#{pane_id}"]
        if self._socket_path:
            cmd.insert(1, "-L")
            cmd.insert(2, self._socket_path)

        try:
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.DEVNULL,
            )
            stdout, _ = await process.communicate()
            return stdout.decode().strip() or None
        except Exception:
            return None


# Singleton instance
spawn_tmux = TmuxSpawn()
