"""
System Tools: Shell Execution with Safety Protocols.

Phase 2 of U-gent Tooling: System interaction with strict safety patterns.

Key Principle: "With great power comes great sandboxing."

These tools provide controlled system access:
- BashTool: Shell command execution with NEVER/CONFIRMATION patterns
- KillShellTool: Background process termination

Safety Patterns:
- NEVER_PATTERNS: Commands that are always rejected
- REQUIRE_CONFIRMATION: Commands that need user approval
- Timeout enforcement: Max 10 minutes
- Output truncation: Max 30K chars

See: plans/ugent-tooling-phase2-handoff.md
"""

from __future__ import annotations

import asyncio
import re
import time
import uuid
from dataclasses import dataclass, field
from typing import Any, ClassVar

from ..base import SafetyViolation, Tool, ToolCategory, ToolEffect, ToolTimeoutError
from ..contracts import BashCommand, BashResult, KillShellRequest, KillShellResponse

# =============================================================================
# Safety Patterns
# =============================================================================

# Commands that are NEVER allowed - immediate rejection
NEVER_PATTERNS: list[str] = [
    r"git config.*--global",  # Never touch global git config
    r"git push.*--force",  # No force push
    r"git.*--no-verify",  # Don't skip hooks
    r"rm -rf /",  # Obvious
    r"rm -rf ~",  # Also obvious
    r"rm -rf \.",  # Delete current dir
    r"sudo\s",  # No privilege escalation
    r"> /etc/",  # No system file writes
    r"chmod 777",  # No world-writable
    r"curl.*\| ?sh",  # No pipe to shell
    r"wget.*\| ?sh",  # No pipe to shell
    r"eval\s",  # No eval
]

# Commands that require user confirmation before execution
REQUIRE_CONFIRMATION: list[str] = [
    r"git push",  # Confirm before push
    r"npm publish",  # Confirm before publish
    r"docker push",  # Confirm before push
    r"pip install",  # Confirm installs
    r"rm -r",  # Confirm recursive delete
]


# =============================================================================
# Internal Result Type
# =============================================================================


@dataclass
class _SubprocessResult:
    """Internal result from subprocess execution."""

    stdout: str
    stderr: str
    exit_code: int
    duration_ms: float
    task_id: str | None = None


# =============================================================================
# Background Process Registry
# =============================================================================


class BackgroundProcessRegistry:
    """
    Registry for tracking background shell processes.

    Thread-safe registry for managing background shells spawned by BashTool.
    """

    _instance: ClassVar[BackgroundProcessRegistry | None] = None
    _procs: dict[str, asyncio.subprocess.Process]

    def __new__(cls) -> BackgroundProcessRegistry:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._procs = {}
        return cls._instance

    def register(self, task_id: str, proc: asyncio.subprocess.Process) -> None:
        """Register a background process."""
        self._procs[task_id] = proc

    def get(self, task_id: str) -> asyncio.subprocess.Process | None:
        """Get a process by ID."""
        return self._procs.get(task_id)

    def remove(self, task_id: str) -> bool:
        """Remove a process from registry."""
        if task_id in self._procs:
            del self._procs[task_id]
            return True
        return False

    def list_ids(self) -> list[str]:
        """List all registered process IDs."""
        return list(self._procs.keys())

    @classmethod
    def reset(cls) -> None:
        """Reset the singleton (for testing)."""
        if cls._instance is not None:
            cls._instance._procs.clear()


def get_process_registry() -> BackgroundProcessRegistry:
    """Get the singleton process registry."""
    return BackgroundProcessRegistry()


# =============================================================================
# BashTool: Shell Execution
# =============================================================================


@dataclass
class BashTool(Tool[BashCommand, BashResult]):
    """
    BashTool: Shell execution with safety protocols.

    Trust Level: L3 (highest - requires explicit trust)
    Effects: CALLS(shell), WRITES(filesystem), SPAWNS(process)

    Safety:
    - NEVER patterns rejected immediately with SafetyViolation
    - CONFIRMATION patterns flagged (requires_confirmation in result)
    - Output truncated at 30K chars
    - Timeout enforced (default 2min, max 10min)

    Examples:
        BashCommand(command="echo hello")
        BashCommand(command="pytest -v", timeout_ms=300_000)
        BashCommand(command="npm run dev", run_in_background=True)
    """

    # Maximum output size before truncation
    MAX_OUTPUT_CHARS: ClassVar[int] = 30_000

    # Maximum timeout (10 minutes)
    MAX_TIMEOUT_MS: ClassVar[int] = 600_000

    @property
    def name(self) -> str:
        return "system.bash"

    @property
    def description(self) -> str:
        return "Execute shell commands with safety protocols"

    @property
    def category(self) -> ToolCategory:
        return ToolCategory.SYSTEM

    @property
    def effects(self) -> list[tuple[ToolEffect, str]]:
        return [
            ToolEffect.calls("shell"),
            ToolEffect.writes("filesystem"),
            ToolEffect.spawns("process"),
        ]

    @property
    def trust_required(self) -> int:
        return 3  # L3 - Highest trust required

    @property
    def timeout_default_ms(self) -> int:
        return 120_000  # 2 minutes default

    async def invoke(self, request: BashCommand) -> BashResult:
        """
        Execute the bash command with safety checks.

        Args:
            request: BashCommand with command, timeout, etc.

        Returns:
            BashResult with stdout, stderr, exit code

        Raises:
            SafetyViolation: If command matches NEVER_PATTERNS
            ToolTimeoutError: If command exceeds timeout
        """
        # 1. Safety check: reject NEVER patterns
        for pattern in NEVER_PATTERNS:
            if re.search(pattern, request.command, re.IGNORECASE):
                raise SafetyViolation(
                    f"Command matches forbidden pattern: {pattern}",
                    self.name,
                )

        # 2. Timeout enforcement (max 10 minutes)
        timeout_ms = min(request.timeout_ms, self.MAX_TIMEOUT_MS)

        # 3. Execute subprocess
        if request.run_in_background:
            result = await self._execute_background(
                command=request.command,
                cwd=request.working_directory,
            )
        else:
            result = await self._execute_foreground(
                command=request.command,
                timeout_seconds=timeout_ms / 1000,
                cwd=request.working_directory,
            )

        # 4. Truncate output if needed
        stdout = result.stdout
        truncated = False
        if len(stdout) > self.MAX_OUTPUT_CHARS:
            stdout = stdout[: self.MAX_OUTPUT_CHARS] + "\n... (output truncated)"
            truncated = True

        stderr = result.stderr
        if len(stderr) > self.MAX_OUTPUT_CHARS:
            stderr = stderr[: self.MAX_OUTPUT_CHARS] + "\n... (output truncated)"
            truncated = True

        return BashResult(
            command=request.command,
            stdout=stdout,
            stderr=stderr,
            exit_code=result.exit_code,
            duration_ms=result.duration_ms,
            truncated=truncated,
            background_task_id=result.task_id,
        )

    async def _execute_foreground(
        self,
        command: str,
        timeout_seconds: float,
        cwd: str | None,
    ) -> _SubprocessResult:
        """Execute command in foreground with timeout."""
        start = time.monotonic()

        try:
            proc = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=cwd,
            )

            stdout_bytes, stderr_bytes = await asyncio.wait_for(
                proc.communicate(),
                timeout=timeout_seconds,
            )

            duration_ms = (time.monotonic() - start) * 1000

            return _SubprocessResult(
                stdout=stdout_bytes.decode("utf-8", errors="replace"),
                stderr=stderr_bytes.decode("utf-8", errors="replace"),
                exit_code=proc.returncode or 0,
                duration_ms=duration_ms,
            )

        except asyncio.TimeoutError:
            # Kill the process on timeout
            if proc is not None:
                proc.kill()
                await proc.wait()  # Ensure process is cleaned up
            raise ToolTimeoutError(
                f"Command timed out after {timeout_seconds}s: {command[:50]}...",
                self.name,
                int(timeout_seconds * 1000),
            )

    async def _execute_background(
        self,
        command: str,
        cwd: str | None,
    ) -> _SubprocessResult:
        """Start command in background, return immediately."""
        start = time.monotonic()
        task_id = f"shell-{uuid.uuid4().hex[:8]}"

        proc = await asyncio.create_subprocess_shell(
            command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=cwd,
        )

        # Register for later termination
        get_process_registry().register(task_id, proc)

        duration_ms = (time.monotonic() - start) * 1000

        return _SubprocessResult(
            stdout=f"Background process started with ID: {task_id}",
            stderr="",
            exit_code=0,
            duration_ms=duration_ms,
            task_id=task_id,
        )

    def requires_confirmation(self, command: str) -> bool:
        """Check if command requires user confirmation."""
        for pattern in REQUIRE_CONFIRMATION:
            if re.search(pattern, command, re.IGNORECASE):
                return True
        return False


# =============================================================================
# KillShellTool: Background Process Termination
# =============================================================================


@dataclass
class KillShellTool(Tool[KillShellRequest, KillShellResponse]):
    """
    KillShellTool: Terminate background shell by ID.

    Trust Level: L2 (requires confirmation)
    Effects: CALLS(shell)

    Examples:
        KillShellRequest(shell_id="shell-a1b2c3d4")
    """

    @property
    def name(self) -> str:
        return "system.kill"

    @property
    def description(self) -> str:
        return "Terminate a background shell process"

    @property
    def category(self) -> ToolCategory:
        return ToolCategory.SYSTEM

    @property
    def effects(self) -> list[tuple[ToolEffect, str]]:
        return [ToolEffect.calls("shell")]

    @property
    def trust_required(self) -> int:
        return 2  # L2 - Confirmation required

    async def invoke(self, request: KillShellRequest) -> KillShellResponse:
        """
        Terminate a background shell process.

        Args:
            request: KillShellRequest with shell_id

        Returns:
            KillShellResponse with success status
        """
        registry = get_process_registry()
        proc = registry.get(request.shell_id)

        if proc is None:
            return KillShellResponse(
                shell_id=request.shell_id,
                success=False,
                message=f"Shell {request.shell_id} not found",
            )

        try:
            # Try graceful termination first
            proc.terminate()

            try:
                await asyncio.wait_for(proc.wait(), timeout=5.0)
            except asyncio.TimeoutError:
                # Force kill if graceful termination fails
                proc.kill()
                await proc.wait()

            registry.remove(request.shell_id)

            return KillShellResponse(
                shell_id=request.shell_id,
                success=True,
                message="Shell terminated successfully",
            )
        except Exception as e:
            return KillShellResponse(
                shell_id=request.shell_id,
                success=False,
                message=f"Failed to terminate shell: {e}",
            )


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    "BashTool",
    "KillShellTool",
    "NEVER_PATTERNS",
    "REQUIRE_CONFIRMATION",
    "BackgroundProcessRegistry",
    "get_process_registry",
]
