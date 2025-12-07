"""
tmux Query Agents

Query agents for discovering tmux state:
    - TmuxList: Void → [TmuxSession]
    - TmuxExists: SessionName → bool
"""

import asyncio
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from bootstrap import Agent
from ..types import TmuxSession


class TmuxList(Agent[None, list[TmuxSession]]):
    """
    List all tmux sessions.

    Type signature: TmuxList: Void → [TmuxSession]

    Discovers running tmux sessions (the "world state").
    """

    def __init__(self, socket_path: str | None = None, prefix: str | None = None):
        self._socket_path = socket_path
        self._prefix = prefix  # Filter to sessions with this prefix

    @property
    def name(self) -> str:
        return "TmuxList"

    @property
    def genus(self) -> str:
        return "zen/tmux"

    @property
    def purpose(self) -> str:
        return "List running tmux sessions"

    async def invoke(self, input: None = None) -> list[TmuxSession]:
        """List all tmux sessions."""
        cmd = [
            "tmux", "list-sessions",
            "-F", "#{session_name}:#{session_created}:#{session_attached}",
        ]
        if self._socket_path:
            cmd.insert(1, "-L")
            cmd.insert(2, self._socket_path)

        try:
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.DEVNULL,
            )
            stdout, _ = await asyncio.wait_for(
                process.communicate(),
                timeout=5.0,
            )

            sessions: list[TmuxSession] = []
            for line in stdout.decode().splitlines():
                parts = line.strip().split(":")
                if len(parts) >= 3:
                    session_name = parts[0]

                    # Filter by prefix if specified
                    if self._prefix and not session_name.startswith(self._prefix):
                        continue

                    # Parse created timestamp
                    try:
                        created_ts = int(parts[1])
                        created_at = datetime.fromtimestamp(created_ts)
                    except (ValueError, IndexError):
                        created_at = datetime.now()

                    is_attached = parts[2] == "1"

                    sessions.append(TmuxSession(
                        id=session_name,
                        name=session_name,
                        pane_id=f"{session_name}:0.0",
                        created_at=created_at,
                        is_attached=is_attached,
                    ))

            return sessions

        except Exception:
            return []


class TmuxExists(Agent[str, bool]):
    """
    Check if a tmux session exists.

    Type signature: TmuxExists: SessionName → bool
    """

    def __init__(self, socket_path: str | None = None):
        self._socket_path = socket_path

    @property
    def name(self) -> str:
        return "TmuxExists"

    @property
    def genus(self) -> str:
        return "zen/tmux"

    @property
    def purpose(self) -> str:
        return "Check if tmux session exists"

    async def invoke(self, session_name: str) -> bool:
        """Check if session exists."""
        cmd = ["tmux", "has-session", "-t", session_name]
        if self._socket_path:
            cmd.insert(1, "-L")
            cmd.insert(2, self._socket_path)

        try:
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.DEVNULL,
                stderr=asyncio.subprocess.DEVNULL,
            )
            await asyncio.wait_for(process.wait(), timeout=5.0)
            return process.returncode == 0
        except Exception:
            return False


# Singleton instances
list_sessions = TmuxList()
session_exists = TmuxExists()
