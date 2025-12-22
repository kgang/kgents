"""
Command Executor for Daemon-side Execution.

Executes CLI commands within the daemon context, with access to:
- Daemon's bootstrap state (already initialized)
- Trust levels for gated operations
- Audit logging for all CLI activity
- Consistent output capture (stdout/stderr/semantic)

This mirrors the execution logic in hollow.py but runs within
the daemon's event loop and uses the daemon's bootstrap state.
"""

from __future__ import annotations

import asyncio
import io
import logging
import os
import sys
import time
from contextlib import redirect_stderr, redirect_stdout
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Any, Callable

from .socket_server import CLIRequest, CLIResponse

if TYPE_CHECKING:
    from .daemon import WitnessDaemon

logger = logging.getLogger("kgentsd.executor")


# =============================================================================
# Output Capture
# =============================================================================


@dataclass
class CapturedOutput:
    """Captured stdout, stderr, and semantic output."""

    stdout: str
    stderr: str
    semantic: dict[str, Any] | None


class OutputCapture:
    """Context manager for capturing command output."""

    def __init__(self) -> None:
        self.stdout_buffer = io.StringIO()
        self.stderr_buffer = io.StringIO()
        self.semantic: dict[str, Any] | None = None
        self._old_stdout: Any = None
        self._old_stderr: Any = None
        self._fd3_file: io.TextIOWrapper | None = None
        self._fd3_path: str | None = None

    def __enter__(self) -> OutputCapture:
        self._old_stdout = sys.stdout
        self._old_stderr = sys.stderr
        sys.stdout = self.stdout_buffer
        sys.stderr = self.stderr_buffer

        # Set up FD3 capture if needed
        # We'll capture semantic data via a temp file
        import tempfile

        fd, self._fd3_path = tempfile.mkstemp(prefix="kgentsd_fd3_", suffix=".json")
        os.close(fd)  # Close the file descriptor, we just need the path
        os.environ["KGENTS_FD3"] = self._fd3_path

        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        sys.stdout = self._old_stdout
        sys.stderr = self._old_stderr

        # Read FD3 semantic output if available
        if self._fd3_path:
            try:
                if os.path.exists(self._fd3_path) and os.path.getsize(self._fd3_path) > 0:
                    import json

                    with open(self._fd3_path) as f:
                        self.semantic = json.load(f)
            except (OSError, json.JSONDecodeError):
                pass
            finally:
                try:
                    os.unlink(self._fd3_path)
                except OSError:
                    pass
                if "KGENTS_FD3" in os.environ:
                    del os.environ["KGENTS_FD3"]

    def get_output(self) -> CapturedOutput:
        """Get the captured output."""
        return CapturedOutput(
            stdout=self.stdout_buffer.getvalue(),
            stderr=self.stderr_buffer.getvalue(),
            semantic=self.semantic,
        )


# =============================================================================
# Command Resolution (from hollow.py)
# =============================================================================


def _get_command_registry() -> dict[str, str]:
    """Get the command registry from hollow.py."""
    from protocols.cli.hollow import COMMAND_REGISTRY

    return COMMAND_REGISTRY


def _resolve_command(name: str) -> Callable[..., int] | None:
    """Resolve a command name to its handler function."""
    from protocols.cli.hollow import resolve_command

    return resolve_command(name)


def _is_agentese_input(command: str, args: list[str]) -> bool:
    """Check if input should be routed through AGENTESE."""
    # Direct paths like self.brain.capture
    is_agentese_path = "." in command and command.split(".")[0] in {
        "world",
        "self",
        "concept",
        "void",
        "time",
    }
    is_shortcut = command.startswith("/")
    is_query = command.startswith("?")
    is_composition = ">>" in " ".join([command] + args)

    # Check for legacy commands
    is_legacy = False
    if not (is_agentese_path or is_shortcut or is_query or is_composition):
        try:
            from protocols.cli.legacy import is_legacy_command

            is_legacy = is_legacy_command([command] + args)
        except ImportError:
            pass

    return is_agentese_path or is_shortcut or is_query or is_composition or is_legacy


# =============================================================================
# Command Executor
# =============================================================================


class CommandExecutor:
    """Executes CLI commands within the daemon context.

    This class handles:
    1. Command resolution (same as hollow.py)
    2. Output capture (stdout, stderr, semantic)
    3. Working directory management
    4. Environment variable filtering
    5. Error handling
    """

    def __init__(
        self,
        daemon: WitnessDaemon | None = None,
    ) -> None:
        """Initialize the command executor.

        Args:
            daemon: Reference to the daemon for access to bootstrap state.
                    Can be None for testing.
        """
        self.daemon = daemon

    async def execute(self, request: CLIRequest) -> CLIResponse:
        """Execute a CLI command and return the response.

        This runs the command in a thread pool to avoid blocking
        the daemon's event loop.
        """
        start_time = time.monotonic()

        # Run command execution in thread pool (handlers are sync)
        loop = asyncio.get_running_loop()
        try:
            response = await loop.run_in_executor(
                None,
                self._execute_sync,
                request,
            )
            response.duration_ms = int((time.monotonic() - start_time) * 1000)
            return response
        except Exception as e:
            logger.exception(f"Command execution failed: {request.command}")
            return CLIResponse.error(
                correlation_id=request.correlation_id,
                message=f"Internal error: {e}",
            )

    def _execute_sync(self, request: CLIRequest) -> CLIResponse:
        """Synchronous command execution (runs in thread pool)."""
        # Save original state
        original_cwd = os.getcwd()
        original_env = dict(os.environ)

        try:
            # Change to request's working directory
            if request.cwd and os.path.isdir(request.cwd):
                os.chdir(request.cwd)

            # Apply filtered environment
            for key, value in request.env.items():
                os.environ[key] = value

            # Execute with output capture
            with OutputCapture() as capture:
                exit_code = self._run_command(request)

            output = capture.get_output()
            return CLIResponse(
                correlation_id=request.correlation_id,
                exit_code=exit_code,
                stdout=output.stdout,
                stderr=output.stderr,
                semantic=output.semantic,
            )

        except Exception as e:
            logger.exception(f"Error executing {request.command}")
            return CLIResponse.error(
                correlation_id=request.correlation_id,
                message=f"Command failed: {e}",
            )

        finally:
            # Restore original state
            os.chdir(original_cwd)
            os.environ.clear()
            os.environ.update(original_env)

    def _run_command(self, request: CLIRequest) -> int:
        """Run the actual command handler."""
        command = request.command
        args = request.args

        # Check for AGENTESE routing
        if _is_agentese_input(command, args):
            return self._run_agentese([command] + args, request.flags)

        # Check for command-level help
        if request.flags.get("help") or "--help" in args or "-h" in args:
            return self._show_help(command, args)

        # Resolve command handler
        handler = _resolve_command(command)

        if handler is None:
            self._print_suggestions(command)
            return 1

        # Execute handler
        try:
            return int(handler(args))
        except KeyboardInterrupt:
            print("\n[...] Interrupted.")
            return 130
        except Exception as e:
            self._handle_exception(e)
            return 1

    def _run_agentese(self, args: list[str], flags: dict[str, Any]) -> int:
        """Route through AGENTESE handler."""
        try:
            from protocols.cli.hollow import _handle_agentese

            return _handle_agentese(args, flags)
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            return 1

    def _show_help(self, command: str, args: list[str]) -> int:
        """Show help for a command."""
        try:
            from protocols.cli.hollow import _show_command_help

            result = _show_command_help(command)
            if result >= 0:
                return result

            # Fallback to handler's built-in help
            handler = _resolve_command(command)
            if handler:
                filtered_args = [a for a in args if a not in ("--help", "-h")]
                return int(handler(["--help"] + filtered_args))
        except Exception:
            pass

        self._print_suggestions(command)
        return 1

    def _print_suggestions(self, command: str) -> None:
        """Print suggestions for unknown command."""
        try:
            from protocols.cli.hollow import print_suggestions

            print_suggestions(command)
        except ImportError:
            print(f"Unknown command: {command}")
            print("Run 'kg --help' for available commands.")

    def _handle_exception(self, e: Exception) -> None:
        """Handle exceptions with sympathetic errors."""
        try:
            from protocols.cli.errors import handle_exception

            print(handle_exception(e, verbose=False))
        except ImportError:
            print(f"Error: {e}", file=sys.stderr)


# =============================================================================
# Factory
# =============================================================================


def create_executor(daemon: WitnessDaemon | None = None) -> CommandExecutor:
    """Create a command executor.

    Args:
        daemon: Reference to the daemon (optional, for access to bootstrap state)

    Returns:
        A configured CommandExecutor
    """
    return CommandExecutor(daemon=daemon)
