"""
Tmux operations - Pure functions for tmux interaction.

All tmux commands are wrapped as async operations.
This is infrastructure, not agent logic.
"""

import asyncio
import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class TmuxConfig:
    """Configuration for tmux operations."""
    scrollback_lines: int = 50000
    default_shell: str = "/bin/bash"


class TmuxService:
    """
    Service for tmux operations.

    All operations are pure functions that interact with tmux.
    """

    def __init__(self, config: Optional[TmuxConfig] = None):
        self._config = config or TmuxConfig()

    async def _run_tmux(
        self,
        *args: str,
        check: bool = True,
    ) -> tuple[int, str, str]:
        """
        Run a tmux command.

        Returns (returncode, stdout, stderr).
        """
        cmd = ["tmux"] + list(args)

        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        stdout, stderr = await proc.communicate()

        if check and proc.returncode != 0:
            # Don't raise on common "expected" failures
            stderr_str = stderr.decode()
            if "no server running" in stderr_str.lower():
                return proc.returncode or 1, "", stderr_str
            if "session not found" in stderr_str.lower():
                return proc.returncode or 1, "", stderr_str

        return proc.returncode or 0, stdout.decode(), stderr.decode()

    async def create_session(
        self,
        name: str,
        command: Optional[str] = None,
        working_dir: Optional[str] = None,
        env: Optional[dict[str, str]] = None,
        scrollback: Optional[int] = None,
    ) -> bool:
        """
        Create a new tmux session.

        Returns True if created successfully.
        """
        args = [
            "new-session",
            "-d",  # Detached
            "-s", name,  # Session name
        ]

        # Set scrollback
        scroll = scrollback or self._config.scrollback_lines
        args.extend(["-x", "200", "-y", "50"])  # Size

        # Working directory
        if working_dir:
            args.extend(["-c", working_dir])

        # Command
        if command:
            args.append(command)
        else:
            args.append(self._config.default_shell)

        # Set environment variables before running
        if env:
            for key, value in env.items():
                await self._run_tmux(
                    "set-environment", "-g", key, value,
                    check=False,
                )

        code, _, _ = await self._run_tmux(*args)

        if code == 0:
            # Set scrollback after creation
            await self._run_tmux(
                "set-option", "-t", name,
                "history-limit", str(scroll),
                check=False,
            )

        return code == 0

    async def kill_session(self, name: str) -> bool:
        """
        Kill a tmux session.

        Returns True if killed successfully.
        """
        code, _, _ = await self._run_tmux(
            "kill-session", "-t", name,
            check=False,
        )
        return code == 0

    async def session_exists(self, name: str) -> bool:
        """Check if a tmux session exists."""
        code, _, _ = await self._run_tmux(
            "has-session", "-t", name,
            check=False,
        )
        return code == 0

    async def is_session_alive(self, name: str) -> bool:
        """
        Check if a tmux session is running and its command is alive.

        This checks both:
        1. The tmux session exists
        2. The pane command is still running
        """
        # First check if session exists
        if not await self.session_exists(name):
            return False

        # Check if any pane is running a command
        code, stdout, _ = await self._run_tmux(
            "list-panes", "-t", name,
            "-F", "#{pane_pid}",
            check=False,
        )

        if code != 0:
            return False

        pane_pids = stdout.strip().split("\n")
        if not pane_pids or not pane_pids[0]:
            return False

        # Check if the process is still running
        for pid in pane_pids:
            if pid:
                try:
                    os.kill(int(pid), 0)  # Signal 0 = check if process exists
                    return True
                except (ProcessLookupError, ValueError):
                    continue

        return False

    async def get_exit_code(self, name: str) -> Optional[int]:
        """
        Get the exit code of the last command in the session.

        Returns None if unable to determine.
        """
        # Try to get the exit status from the pane
        code, stdout, _ = await self._run_tmux(
            "display-message", "-t", name,
            "-p", "#{pane_dead_status}",
            check=False,
        )

        if code != 0:
            return None

        status = stdout.strip()
        if status and status.isdigit():
            return int(status)

        return None

    async def send_signal(self, name: str, signal: str) -> bool:
        """
        Send a signal to the process in the session.

        signal: "TERM", "KILL", "INT", etc.
        """
        # Get the pane PID
        code, stdout, _ = await self._run_tmux(
            "list-panes", "-t", name,
            "-F", "#{pane_pid}",
            check=False,
        )

        if code != 0:
            return False

        pane_pids = stdout.strip().split("\n")
        if not pane_pids or not pane_pids[0]:
            return False

        # Send signal to main process
        pid = pane_pids[0]
        if pid:
            try:
                import signal as sig
                sig_num = getattr(sig, f"SIG{signal}", sig.SIGTERM)
                os.kill(int(pid), sig_num)
                return True
            except (ProcessLookupError, ValueError, AttributeError):
                pass

        return False

    async def resurrect_session(self, name: str) -> bool:
        """
        Attempt to resurrect a dead session.

        This re-runs the last command in a dead pane.
        """
        # Respawn the pane
        code, _, _ = await self._run_tmux(
            "respawn-pane", "-t", name,
            check=False,
        )
        return code == 0

    async def send_keys(
        self,
        name: str,
        keys: str,
        enter: bool = True,
    ) -> bool:
        """
        Send keys to a tmux session.

        If enter=True, also sends Enter key.
        """
        args = ["send-keys", "-t", name, keys]
        if enter:
            args.append("Enter")

        code, _, _ = await self._run_tmux(*args, check=False)
        return code == 0

    async def capture_pane(
        self,
        name: str,
        lines: int = 100,
        start: int = -100,
    ) -> str:
        """
        Capture content from a tmux pane.

        Returns the captured text.
        """
        code, stdout, _ = await self._run_tmux(
            "capture-pane", "-t", name,
            "-p",  # Print to stdout
            "-S", str(start),  # Start line
            "-E", str(start + lines),  # End line
            check=False,
        )

        if code != 0:
            return ""

        return stdout

    async def list_sessions(self) -> list[str]:
        """
        List all tmux sessions.

        Returns list of session names.
        """
        code, stdout, _ = await self._run_tmux(
            "list-sessions",
            "-F", "#{session_name}",
            check=False,
        )

        if code != 0:
            return []

        return [s.strip() for s in stdout.strip().split("\n") if s.strip()]

    async def attach_session(self, name: str) -> bool:
        """
        Return the command to attach to a session.

        Note: This returns True but actual attachment should be done
        by the TUI, not by this service.
        """
        # Just verify session exists
        return await self.session_exists(name)
