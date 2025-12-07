"""
TmuxCapture Agent

Capture: TmuxSession → OutputLines
Capture(session) = tmux capture-pane -p -t PANE

Captures output from a tmux pane.
Maps to zenportal's TmuxService.capture_pane()
"""

import asyncio
from dataclasses import dataclass
from pathlib import Path

from bootstrap import Agent
from ..types import TmuxSession


@dataclass
class CaptureInput:
    """Input for capturing output"""
    session: TmuxSession
    lines: int = 100  # Number of lines to capture


@dataclass
class CapturedOutput:
    """Result of capture"""
    lines: list[str]
    pane_id: str
    is_dead: bool  # True if pane process has exited
    exit_code: int | None  # Exit code if dead


class TmuxCapture(Agent[CaptureInput, CapturedOutput]):
    """
    Capture output from a tmux pane.

    Type signature: TmuxCapture: CaptureInput → CapturedOutput

    Also checks if the pane is dead (process exited).
    """

    def __init__(self, socket_path: str | None = None):
        self._socket_path = socket_path

    @property
    def name(self) -> str:
        return "TmuxCapture"

    @property
    def genus(self) -> str:
        return "zen/tmux"

    @property
    def purpose(self) -> str:
        return "Capture output from tmux pane"

    async def invoke(self, input: CaptureInput) -> CapturedOutput:
        """
        Capture pane output.

        Returns lines, dead status, and exit code.
        """
        pane_id = input.session.pane_id

        # Capture output
        lines = await self._capture_pane(pane_id, input.lines)

        # Check if dead
        is_dead, exit_code = await self._check_pane_dead(pane_id)

        return CapturedOutput(
            lines=lines,
            pane_id=pane_id,
            is_dead=is_dead,
            exit_code=exit_code,
        )

    async def _capture_pane(self, pane_id: str, lines: int) -> list[str]:
        """Capture pane output"""
        cmd = [
            "tmux", "capture-pane",
            "-t", pane_id,
            "-p",                    # Print to stdout
            "-S", f"-{lines}",       # Start N lines back
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
            output = stdout.decode()
            return output.splitlines()
        except Exception:
            return []

    async def _check_pane_dead(self, pane_id: str) -> tuple[bool, int | None]:
        """Check if pane is dead and get exit code"""
        # Check pane_dead
        cmd = ["tmux", "display-message", "-t", pane_id, "-p", "#{pane_dead}"]
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
            is_dead = stdout.decode().strip() == "1"

            if not is_dead:
                return False, None

            # Get exit code
            cmd2 = ["tmux", "display-message", "-t", pane_id, "-p", "#{pane_dead_status}"]
            if self._socket_path:
                cmd2.insert(1, "-L")
                cmd2.insert(2, self._socket_path)

            process2 = await asyncio.create_subprocess_exec(
                *cmd2,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.DEVNULL,
            )
            stdout2, _ = await process2.communicate()
            exit_code_str = stdout2.decode().strip()
            exit_code = int(exit_code_str) if exit_code_str.isdigit() else None

            return True, exit_code

        except Exception:
            return False, None


# Singleton instance
capture_output = TmuxCapture()
