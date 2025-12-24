"""
Command Executor for Daemon-side Execution.

Executes CLI commands within the daemon context using a three-tier model:

- Tier 1: Pure async execution in daemon's event loop
- Tier 2: Interactive execution with PTY I/O bridge
- Tier 3: True subprocess execution (external commands only)

This module provides handlers with access to:
- Daemon's bootstrap state (already initialized)
- Trust levels for gated operations
- Audit logging for all CLI activity
- Consistent output capture (stdout/stderr/semantic)
- Worker pool for CPU-bound and I/O-bound tasks
- PTY bridge for interactive I/O (Tier 2)

See: plans/rustling-bouncing-seal.md
"""

from __future__ import annotations

import asyncio
import io
import inspect
import logging
import os
import sys
import time
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Any, Callable

from .socket_server import CLIRequest, CLIResponse, CLIStreamMessage

if TYPE_CHECKING:
    from .context import DaemonContext
    from .daemon import WitnessDaemon
    from .pty_bridge import PTYBridge
    from .worker_pool import WorkerPoolManager

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
        self._fd3_path: str | None = None

    def __enter__(self) -> OutputCapture:
        self._old_stdout = sys.stdout
        self._old_stderr = sys.stderr
        sys.stdout = self.stdout_buffer
        sys.stderr = self.stderr_buffer

        # Set up FD3 capture via temp file
        import tempfile

        fd, self._fd3_path = tempfile.mkstemp(prefix="kgentsd_fd3_", suffix=".json")
        os.close(fd)
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
# Command Resolution
# =============================================================================


def _resolve_command(name: str) -> Callable[..., int] | None:
    """Resolve a command name to its handler function."""
    from protocols.cli.hollow import resolve_command

    return resolve_command(name)


def _is_agentese_input(command: str, args: list[str]) -> bool:
    """Check if input should be routed through AGENTESE."""
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

    is_legacy = False
    if not (is_agentese_path or is_shortcut or is_query or is_composition):
        try:
            from protocols.cli.legacy import is_legacy_command

            is_legacy = is_legacy_command([command] + args)
        except ImportError:
            pass

    return is_agentese_path or is_shortcut or is_query or is_composition or is_legacy


# =============================================================================
# Handler Metadata
# =============================================================================


def _get_handler_meta(command: str) -> Any:
    """Get handler metadata for a command."""
    try:
        from protocols.cli.handler_meta import get_handler_meta, infer_handler_meta

        meta = get_handler_meta(command)
        if meta is not None:
            return meta

        # Infer metadata from handler
        handler = _resolve_command(command)
        return infer_handler_meta(command, handler)
    except ImportError:
        # handler_meta not available, return None
        return None


# =============================================================================
# Command Executor
# =============================================================================


class CommandExecutor:
    """
    Executes CLI commands within the daemon context.

    Uses a three-tier invocation model:

    - Tier 1: Pure async execution in daemon's event loop
      - Most commands (brain, witness, probe, etc.)
      - Output captured via OutputCapture
      - Returns CLIResponse with stdout/stderr

    - Tier 2: Interactive execution with PTY I/O bridge
      - Commands needing terminal I/O (soul, dawn, coffee)
      - I/O streamed via PTYBridge
      - Returns streaming messages

    - Tier 3: True subprocess execution
      - External commands only (git, npm, docker)
      - Full PTY fork-exec
      - Handler can opt-in via @handler(tier=3)

    Attributes:
        daemon: Reference to WitnessDaemon for state access
    """

    def __init__(self, daemon: WitnessDaemon | None = None) -> None:
        """Initialize the command executor.

        Args:
            daemon: Reference to the daemon for bootstrap state access
        """
        self.daemon = daemon

        # PTY bridge state (set when handling Tier 2)
        self._current_reader: asyncio.StreamReader | None = None
        self._current_writer: asyncio.StreamWriter | None = None

    # =========================================================================
    # Main Entry Point
    # =========================================================================

    async def execute(
        self,
        request: CLIRequest,
        worker_pool: WorkerPoolManager | None = None,
    ) -> CLIResponse:
        """
        Execute a CLI command and return the response.

        Routes command through appropriate tier based on handler metadata.

        Args:
            request: The CLI request to execute
            worker_pool: Optional worker pool for task routing

        Returns:
            CLIResponse with captured output
        """
        start_time = time.monotonic()
        command = request.command

        try:
            # Get handler metadata
            meta = _get_handler_meta(command)

            if meta is None:
                # No metadata - use legacy sync execution
                return await self._execute_legacy(request, worker_pool)

            # Route by tier
            if meta.tier == 1:
                response = await self._execute_tier1(request, meta, worker_pool)
            elif meta.tier == 2:
                # Tier 2 requires PTY mode - if not PTY, fallback to tier 1
                if request.pty and self._current_reader and self._current_writer:
                    response = await self._execute_tier2(request, meta)
                else:
                    # Fallback to tier 1 with output capture
                    response = await self._execute_tier1(request, meta, worker_pool)
            else:
                # Tier 3 - subprocess (handled by socket_server)
                response = await self._execute_legacy(request, worker_pool)

            response.duration_ms = int((time.monotonic() - start_time) * 1000)
            return response

        except Exception as e:
            logger.exception(f"Command execution failed: {request.command}")
            return CLIResponse.error(
                correlation_id=request.correlation_id,
                message=f"Internal error: {e}",
            )

    # =========================================================================
    # Tier 1: Pure Async Execution
    # =========================================================================

    async def _execute_tier1(
        self,
        request: CLIRequest,
        meta: Any,
        worker_pool: WorkerPoolManager | None = None,
    ) -> CLIResponse:
        """
        Execute a Tier 1 command (pure async, no PTY).

        The handler runs in the daemon's async context with access to
        daemon state via DaemonContext.
        """
        handler = _resolve_command(request.command)
        if handler is None:
            return CLIResponse.error(
                correlation_id=request.correlation_id,
                message=f"Unknown command: {request.command}",
            )

        # Create context
        ctx = self._create_context(request)

        # NOTE: We do NOT check _is_agentese_input here because we have a registered
        # handler. The handler (e.g., cmd_brain) will internally call project_command
        # to route to AGENTESE if needed. This allows handlers to have custom logic
        # (like extinct protocol) before/after AGENTESE invocation.

        # Execute with output capture
        with self._with_cwd_and_env(request):
            with OutputCapture() as capture:
                try:
                    if meta.is_async or asyncio.iscoroutinefunction(handler):
                        # Async handler - await directly on daemon's event loop
                        # Set KGENTS_DAEMON_WORKER so handlers know they're in daemon context
                        os.environ["KGENTS_DAEMON_WORKER"] = "1"
                        try:
                            exit_code = await handler(request.args, ctx=ctx)
                        finally:
                            if "KGENTS_DAEMON_WORKER" in os.environ:
                                del os.environ["KGENTS_DAEMON_WORKER"]
                    elif worker_pool and worker_pool.is_running:
                        # Sync handler - run in worker pool
                        exit_code = await worker_pool.io_bound(
                            self._run_sync_handler, handler, request.args, ctx
                        )
                    else:
                        # Sync handler - run in default thread pool
                        loop = asyncio.get_running_loop()
                        exit_code = await loop.run_in_executor(
                            None,
                            self._run_sync_handler,
                            handler,
                            request.args,
                            ctx,
                        )
                except KeyboardInterrupt:
                    exit_code = 130
                except Exception as e:
                    logger.exception(f"Handler error: {request.command}")
                    print(f"Error: {e}", file=sys.stderr)
                    exit_code = 1

        output = capture.get_output()
        return CLIResponse(
            correlation_id=request.correlation_id,
            exit_code=exit_code if isinstance(exit_code, int) else 1,
            stdout=output.stdout,
            stderr=output.stderr,
            semantic=output.semantic,
        )

    def _run_sync_handler(
        self,
        handler: Callable[..., int],
        args: list[str],
        ctx: DaemonContext | None,
    ) -> int:
        """Run a sync handler (in thread pool).

        Sets KGENTS_DAEMON_WORKER to signal that we're running in a daemon
        worker thread. This allows projection.py's _run_async to create
        proper fresh event loops for database operations.
        """
        # Set marker for daemon worker context
        os.environ["KGENTS_DAEMON_WORKER"] = "1"
        try:
            # Check if handler accepts ctx parameter
            sig = inspect.signature(handler)
            if "ctx" in sig.parameters:
                return int(handler(args, ctx=ctx))
            else:
                return int(handler(args))
        except Exception as e:
            logger.exception("Sync handler error")
            print(f"Error: {e}", file=sys.stderr)
            return 1
        finally:
            # Clean up marker
            if "KGENTS_DAEMON_WORKER" in os.environ:
                del os.environ["KGENTS_DAEMON_WORKER"]

    # =========================================================================
    # Tier 2: PTY-Bridged Execution
    # =========================================================================

    async def _execute_tier2(
        self,
        request: CLIRequest,
        meta: Any,
    ) -> CLIResponse:
        """
        Execute a Tier 2 command (PTY-bridged, interactive).

        The handler runs in the daemon with I/O bridged to client terminal.
        """
        from .pty_bridge import PTYBridge

        handler = _resolve_command(request.command)
        if handler is None:
            return CLIResponse.error(
                correlation_id=request.correlation_id,
                message=f"Unknown command: {request.command}",
            )

        # Create PTY bridge
        bridge = PTYBridge(
            reader=self._current_reader,
            writer=self._current_writer,
            correlation_id=request.correlation_id,
            term_size=request.term_size or (24, 80),
        )

        # Create context with PTY bridge
        ctx = self._create_context(request, pty_bridge=bridge)

        try:
            await bridge.start()

            # Redirect stdout/stderr to bridge
            old_stdout, old_stderr = sys.stdout, sys.stderr
            sys.stdout = bridge.stdout
            sys.stderr = bridge.stderr

            try:
                with self._with_cwd_and_env(request):
                    if meta.is_async or asyncio.iscoroutinefunction(handler):
                        exit_code = await handler(request.args, ctx=ctx)
                    else:
                        # Run sync handler in thread pool
                        loop = asyncio.get_running_loop()
                        exit_code = await loop.run_in_executor(
                            None,
                            self._run_sync_handler,
                            handler,
                            request.args,
                            ctx,
                        )
            except KeyboardInterrupt:
                exit_code = 130
            except Exception as e:
                logger.exception(f"Tier 2 handler error: {request.command}")
                print(f"Error: {e}", file=sys.stderr)
                exit_code = 1
            finally:
                sys.stdout, sys.stderr = old_stdout, old_stderr

            # Send exit message
            await bridge.send_exit(exit_code if isinstance(exit_code, int) else 1)

            return CLIResponse(
                correlation_id=request.correlation_id,
                exit_code=exit_code if isinstance(exit_code, int) else 1,
                stdout="",  # Output was streamed
                stderr="",
            )

        finally:
            await bridge.stop()

    # =========================================================================
    # Legacy Execution (Fallback)
    # =========================================================================

    async def _execute_legacy(
        self,
        request: CLIRequest,
        worker_pool: WorkerPoolManager | None = None,
    ) -> CLIResponse:
        """
        Execute a command using legacy sync execution.

        This is the fallback when no handler metadata is available.
        """
        if worker_pool and worker_pool.is_running:
            response = await worker_pool.io_bound(
                self._execute_sync,
                request,
            )
        else:
            loop = asyncio.get_running_loop()
            response = await loop.run_in_executor(
                None,
                self._execute_sync,
                request,
            )
        return response

    def _execute_sync(self, request: CLIRequest) -> CLIResponse:
        """Synchronous command execution (legacy mode)."""
        original_cwd = os.getcwd()
        original_env = dict(os.environ)

        try:
            if request.cwd and os.path.isdir(request.cwd):
                os.chdir(request.cwd)

            for key, value in request.env.items():
                os.environ[key] = value

            with OutputCapture() as capture:
                exit_code = self._run_command_sync(request)

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
            os.chdir(original_cwd)
            os.environ.clear()
            os.environ.update(original_env)

    def _run_command_sync(self, request: CLIRequest) -> int:
        """Run command handler synchronously (legacy mode)."""
        command = request.command
        args = request.args

        if _is_agentese_input(command, args):
            return self._run_agentese_sync([command] + args, request.flags)

        if request.flags.get("help") or "--help" in args or "-h" in args:
            return self._show_help(command, args)

        handler = _resolve_command(command)
        if handler is None:
            self._print_suggestions(command)
            return 1

        try:
            return int(handler(args))
        except KeyboardInterrupt:
            print("\n[...] Interrupted.")
            return 130
        except Exception as e:
            self._handle_exception(e)
            return 1

    # =========================================================================
    # Context & Environment
    # =========================================================================

    def _create_context(
        self,
        request: CLIRequest,
        pty_bridge: PTYBridge | None = None,
    ) -> DaemonContext:
        """Create a DaemonContext for the handler."""
        from .context import create_daemon_context

        return create_daemon_context(
            daemon=self.daemon,
            correlation_id=request.correlation_id,
            cwd=request.cwd,
            env=request.env,
            pty_bridge=pty_bridge,
        )

    @contextmanager
    def _with_cwd_and_env(self, request: CLIRequest):
        """Context manager for temporary cwd and env changes."""
        original_cwd = os.getcwd()
        original_env = dict(os.environ)

        try:
            if request.cwd and os.path.isdir(request.cwd):
                os.chdir(request.cwd)

            for key, value in request.env.items():
                os.environ[key] = value

            yield

        finally:
            os.chdir(original_cwd)
            os.environ.clear()
            os.environ.update(original_env)

    # =========================================================================
    # AGENTESE Routing
    # =========================================================================

    async def _run_agentese_async(
        self,
        request: CLIRequest,
        ctx: DaemonContext | None,
    ) -> CLIResponse:
        """Route through AGENTESE handler (async)."""
        try:
            from protocols.cli.hollow import _handle_agentese

            # Wrap in OutputCapture to capture stdout/stderr
            with OutputCapture() as capture:
                # Run in thread pool since _handle_agentese is sync
                loop = asyncio.get_running_loop()
                exit_code = await loop.run_in_executor(
                    None,
                    _handle_agentese,
                    [request.command] + request.args,
                    request.flags,
                )

            output = capture.get_output()
            return CLIResponse(
                correlation_id=request.correlation_id,
                exit_code=exit_code,
                stdout=output.stdout,
                stderr=output.stderr,
                semantic=output.semantic,
            )
        except Exception as e:
            return CLIResponse.error(
                correlation_id=request.correlation_id,
                message=f"AGENTESE error: {e}",
            )

    def _run_agentese_sync(self, args: list[str], flags: dict[str, Any]) -> int:
        """Route through AGENTESE handler (sync)."""
        try:
            from protocols.cli.hollow import _handle_agentese

            return _handle_agentese(args, flags)
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            return 1

    # =========================================================================
    # Helpers
    # =========================================================================

    def _show_help(self, command: str, args: list[str]) -> int:
        """Show help for a command."""
        try:
            from protocols.cli.hollow import _show_command_help

            result = _show_command_help(command)
            if result >= 0:
                return result

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

    # =========================================================================
    # PTY Session Support
    # =========================================================================

    def set_pty_streams(
        self,
        reader: asyncio.StreamReader,
        writer: asyncio.StreamWriter,
    ) -> None:
        """Set the PTY streams for Tier 2 execution."""
        self._current_reader = reader
        self._current_writer = writer

    def clear_pty_streams(self) -> None:
        """Clear the PTY streams after execution."""
        self._current_reader = None
        self._current_writer = None


# =============================================================================
# Factory
# =============================================================================


def create_executor(daemon: WitnessDaemon | None = None) -> CommandExecutor:
    """Create a command executor.

    Args:
        daemon: Reference to the daemon for bootstrap state access

    Returns:
        A configured CommandExecutor
    """
    return CommandExecutor(daemon=daemon)
