"""
TmuxSendKeys Agent

SendKeys: (TmuxSession, Keys) → Sent
SendKeys(session, keys) = tmux send-keys -t PANE KEYS

Sends keystrokes to a tmux pane.
Maps to zenportal's TmuxService.send_keys()
"""

import sys
import asyncio
from dataclasses import dataclass
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "claude-openrouter"))

from bootstrap import Agent
from ..types import TmuxSession


@dataclass
class SendInput:
    """Input for sending keys"""
    session: TmuxSession
    keys: str
    literal: bool = True  # Use -l flag (literal mode)
    enter: bool = False   # Append Enter key


@dataclass
class SendResult:
    """Result of send"""
    success: bool
    error: str | None = None


class TmuxSendKeys(Agent[SendInput, SendResult]):
    """
    Send keys to a tmux pane.

    Type signature: TmuxSendKeys: SendInput → SendResult

    Options:
        - literal: Send keys literally (escape special chars)
        - enter: Append Enter keypress
    """

    def __init__(self, socket_path: str | None = None):
        self._socket_path = socket_path

    @property
    def name(self) -> str:
        return "TmuxSendKeys"

    @property
    def genus(self) -> str:
        return "zen/tmux"

    @property
    def purpose(self) -> str:
        return "Send keystrokes to tmux pane"

    async def invoke(self, input: SendInput) -> SendResult:
        """Send keys to pane."""
        pane_id = input.session.pane_id

        cmd = ["tmux", "send-keys", "-t", pane_id]
        if self._socket_path:
            cmd.insert(1, "-L")
            cmd.insert(2, self._socket_path)

        if input.literal:
            cmd.append("-l")

        cmd.append(input.keys)

        if input.enter:
            # Send Enter separately
            cmd.extend(["Enter"])

        try:
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.DEVNULL,
                stderr=asyncio.subprocess.PIPE,
            )
            _, stderr = await asyncio.wait_for(
                process.communicate(),
                timeout=5.0,
            )

            if process.returncode != 0:
                return SendResult(
                    success=False,
                    error=stderr.decode().strip(),
                )

            return SendResult(success=True)

        except asyncio.TimeoutError:
            return SendResult(success=False, error="Timeout")
        except Exception as e:
            return SendResult(success=False, error=str(e))


# Singleton instance
send_keys = TmuxSendKeys()
