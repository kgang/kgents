"""
Daemon Context for Handler Execution.

This module provides the DaemonContext class that is passed to handlers
when executing within the daemon. It provides access to:

- Daemon state (trust level, storage, lifecycle)
- Output channels (stdout, stderr, semantic)
- PTY bridge for interactive I/O (Tier 2)
- Request metadata (correlation ID, cwd, env)

The context enables handlers to access daemon resources without
spawning a subprocess, solving the "context loss" problem.

See: plans/rustling-bouncing-seal.md
"""

from __future__ import annotations

import os
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Any, Callable, TextIO

if TYPE_CHECKING:
    from services.witness.polynomial import TrustLevel

    from .daemon import WitnessDaemon
    from .pty_bridge import PTYBridge


# =============================================================================
# Daemon Context
# =============================================================================


@dataclass
class DaemonContext:
    """
    Context passed to handlers executing in the daemon.

    This is the unified context object that replaces the fragmented
    context passing in the old architecture. Handlers receive this
    as their `ctx` argument and can access all daemon state.

    Attributes:
        daemon: Reference to the WitnessDaemon (full state access)
        storage: StorageProvider for persistence operations
        trust_level: Current trust escalation level
        stdout: File-like for stdout (may be PTY bridge)
        stderr: File-like for stderr (may be PTY bridge)
        semantic_writer: Callback for structured output (FD3 equivalent)
        pty_bridge: PTY I/O bridge for Tier 2 handlers
        correlation_id: Request tracking ID
        cwd: Working directory for the command
        env: Environment variables (filtered)
        is_pty_mode: Whether running in PTY mode

    Example:
        @handler("brain", is_async=True, tier=1)
        async def cmd_brain(args: list[str], ctx: DaemonContext | None = None) -> int:
            if ctx:
                # Use daemon's storage provider
                storage = ctx.storage
                # Check trust level
                if ctx.trust_level.value < 2:
                    ctx.stderr.write("Insufficient trust level\\n")
                    return 1
                # Write semantic output
                if ctx.semantic_writer:
                    ctx.semantic_writer({"status": "complete", "count": 42})
            ...
    """

    # Core state
    daemon: WitnessDaemon | None = None
    storage: Any | None = None  # StorageProvider
    trust_level: TrustLevel | None = None

    # Output channels
    stdout: TextIO = field(default_factory=lambda: sys.stdout)
    stderr: TextIO = field(default_factory=lambda: sys.stderr)
    semantic_writer: Callable[[dict[str, Any]], None] | None = None

    # PTY bridge (Tier 2 only)
    pty_bridge: PTYBridge | None = None

    # Request info
    correlation_id: str = ""
    cwd: Path = field(default_factory=Path.cwd)
    env: dict[str, str] = field(default_factory=dict)

    # Flags
    is_pty_mode: bool = False

    def __post_init__(self) -> None:
        """Derive additional state."""
        # If we have a PTY bridge, use its stdout/stderr
        if self.pty_bridge is not None:
            self.stdout = self.pty_bridge.stdout
            self.stderr = self.pty_bridge.stderr
            self.is_pty_mode = True

        # Extract trust level from daemon if not provided
        if self.trust_level is None and self.daemon is not None:
            self.trust_level = self.daemon.trust_level

        # Extract storage from daemon if not provided
        if self.storage is None and self.daemon is not None:
            self.storage = self.daemon.storage_provider

    # =========================================================================
    # Convenience Properties
    # =========================================================================

    @property
    def lifecycle_state(self) -> Any | None:
        """Get the daemon's lifecycle state."""
        if self.daemon is not None:
            return self.daemon._lifecycle_state
        return None

    @property
    def worker_pool(self) -> Any | None:
        """Get the daemon's worker pool for task submission."""
        if self.daemon is not None:
            return self.daemon._worker_pool
        return None

    @property
    def witness_bus(self) -> Any | None:
        """Get the daemon's witness event bus."""
        if self.daemon is not None:
            return getattr(self.daemon, "_witness_bus", None)
        return None

    @property
    def trust_status(self) -> dict[str, Any]:
        """Get detailed trust status."""
        if self.daemon is not None:
            return self.daemon.trust_status
        return {
            "trust_level": "UNKNOWN",
            "trust_level_value": 0,
            "observation_count": 0,
        }

    # =========================================================================
    # Output Helpers
    # =========================================================================

    def print(self, *args: Any, **kwargs: Any) -> None:
        """Print to context stdout (respects PTY mode)."""
        kwargs.setdefault("file", self.stdout)
        print(*args, **kwargs)

    def error(self, *args: Any, **kwargs: Any) -> None:
        """Print to context stderr (respects PTY mode)."""
        kwargs.setdefault("file", self.stderr)
        print(*args, **kwargs)

    def emit_semantic(self, data: dict[str, Any]) -> None:
        """
        Emit structured semantic data.

        In non-PTY mode, this writes to FD3.
        In PTY mode, this sends an 'event' message.
        """
        if self.semantic_writer is not None:
            self.semantic_writer(data)
        elif self.pty_bridge is not None:
            # Queue event for sending
            import asyncio

            try:
                loop = asyncio.get_running_loop()
                asyncio.create_task(self.pty_bridge.write_event(data))
            except RuntimeError:
                # No running event loop, skip
                pass

    def emit_progress(
        self,
        step: str,
        percent: float,
        message: str = "",
    ) -> None:
        """
        Emit a progress event.

        Convenience method for common progress reporting pattern.
        """
        self.emit_semantic(
            {
                "type": "progress",
                "step": step,
                "percent": percent,
                "message": message,
            }
        )

    def emit_status(self, status: str, message: str = "") -> None:
        """
        Emit a status event.

        Convenience method for status updates.
        """
        self.emit_semantic(
            {
                "type": "status",
                "status": status,
                "message": message,
            }
        )

    # =========================================================================
    # PTY Helpers (Tier 2)
    # =========================================================================

    @property
    def terminal_size(self) -> tuple[int, int]:
        """Get current terminal size (rows, cols)."""
        if self.pty_bridge is not None:
            return self.pty_bridge.rows, self.pty_bridge.cols
        # Fallback to environment or defaults
        try:
            import shutil

            size = shutil.get_terminal_size()
            return size.lines, size.columns
        except Exception:
            return 24, 80

    async def read_input(self, n: int = -1) -> bytes:
        """
        Read raw input from terminal (PTY mode only).

        Args:
            n: Number of bytes to read (-1 for any available)

        Returns:
            Bytes read from terminal

        Raises:
            RuntimeError: If not in PTY mode
        """
        if self.pty_bridge is None:
            raise RuntimeError("read_input() requires PTY mode")
        return await self.pty_bridge.read_input(n)

    async def read_line(self, prompt: str = "") -> str:
        """
        Read a line of input (PTY mode only).

        Args:
            prompt: Optional prompt to display

        Returns:
            Line of text (without newline)

        Raises:
            RuntimeError: If not in PTY mode
        """
        if self.pty_bridge is None:
            raise RuntimeError("read_line() requires PTY mode")

        if prompt:
            self.print(prompt, end="", flush=True)

        # Read until newline
        buffer = b""
        while True:
            chunk = await self.pty_bridge.read_input(1)
            if not chunk:
                break
            if chunk == b"\n" or chunk == b"\r":
                self.print()  # Echo newline
                break
            buffer += chunk
            # Echo character
            self.stdout.write(chunk.decode("utf-8", errors="replace"))
            self.stdout.flush()

        return buffer.decode("utf-8", errors="replace")

    # =========================================================================
    # Context Manager
    # =========================================================================

    def with_cwd(self) -> "_CwdContext":
        """
        Context manager to temporarily change to request's cwd.

        Usage:
            with ctx.with_cwd():
                # Now in ctx.cwd
                ...
            # Restored to original cwd
        """
        return _CwdContext(self.cwd)


class _CwdContext:
    """Context manager for temporary cwd change."""

    def __init__(self, target: Path) -> None:
        self.target = target
        self.original: Path | None = None

    def __enter__(self) -> Path:
        self.original = Path.cwd()
        os.chdir(self.target)
        return self.target

    def __exit__(self, *args: Any) -> None:
        if self.original is not None:
            os.chdir(self.original)


# =============================================================================
# Context Factory
# =============================================================================


def create_daemon_context(
    daemon: WitnessDaemon | None = None,
    correlation_id: str = "",
    cwd: str | Path | None = None,
    env: dict[str, str] | None = None,
    pty_bridge: PTYBridge | None = None,
    semantic_writer: Callable[[dict[str, Any]], None] | None = None,
) -> DaemonContext:
    """
    Factory function to create a DaemonContext.

    Args:
        daemon: WitnessDaemon reference
        correlation_id: Request tracking ID
        cwd: Working directory (defaults to daemon's cwd)
        env: Environment variables
        pty_bridge: PTY bridge for interactive I/O
        semantic_writer: Callback for FD3-style output

    Returns:
        Configured DaemonContext
    """
    return DaemonContext(
        daemon=daemon,
        correlation_id=correlation_id,
        cwd=Path(cwd) if cwd else Path.cwd(),
        env=env or {},
        pty_bridge=pty_bridge,
        semantic_writer=semantic_writer,
    )


# =============================================================================
# Null Context (for testing/standalone)
# =============================================================================


class NullContext(DaemonContext):
    """
    A null context for testing or standalone execution.

    All operations are no-ops or return safe defaults.
    """

    def __init__(self) -> None:
        super().__init__(
            daemon=None,
            storage=None,
            trust_level=None,
            correlation_id="null",
            cwd=Path.cwd(),
            env={},
        )

    def emit_semantic(self, data: dict[str, Any]) -> None:
        """No-op for null context."""
        pass

    async def read_input(self, n: int = -1) -> bytes:
        """Return empty bytes for null context."""
        return b""


# Singleton null context
NULL_CONTEXT = NullContext()


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    "DaemonContext",
    "create_daemon_context",
    "NullContext",
    "NULL_CONTEXT",
]
