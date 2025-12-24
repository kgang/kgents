"""
PTY Executor for Interactive Terminal Sessions.

Provides PTY (pseudo-terminal) allocation and bidirectional I/O for
interactive CLI commands running through the daemon.

Key components:
- PTYSession: Low-level PTY allocation and management
- PTYStreamExecutor: Async integration for streaming I/O

Usage:
    session = PTYSession()
    session.spawn("/bin/bash", ["-l"])
    session.set_size(24, 80)

    # In event loop
    executor = PTYStreamExecutor(session, callback)
    await executor.run()
"""

from __future__ import annotations

import asyncio
import fcntl
import logging
import os
import pty
import select
import struct
import sys
import termios
import tty
from dataclasses import dataclass
from typing import TYPE_CHECKING, Callable

if TYPE_CHECKING:
    from .socket_server import CLIStreamMessage

logger = logging.getLogger("kgentsd.pty")


@dataclass
class PTYConfig:
    """Configuration for PTY session."""

    rows: int = 24
    cols: int = 80
    read_size: int = 4096
    select_timeout: float = 0.1


class PTYSession:
    """Low-level PTY session management.

    Handles PTY allocation, subprocess spawning, and terminal control.
    This class is synchronous - async wrapper is PTYStreamExecutor.
    """

    def __init__(self, config: PTYConfig | None = None):
        self.config = config or PTYConfig()
        self._master_fd: int | None = None
        self._pid: int | None = None
        self._exit_code: int | None = None
        self._closed = False

    @property
    def master_fd(self) -> int | None:
        """Get the master file descriptor."""
        return self._master_fd

    @property
    def pid(self) -> int | None:
        """Get the child process ID."""
        return self._pid

    @property
    def is_alive(self) -> bool:
        """Check if the child process is still running."""
        if self._pid is None:
            return False
        if self._exit_code is not None:
            return False

        # Check without blocking
        try:
            pid, status = os.waitpid(self._pid, os.WNOHANG)
            if pid == 0:
                return True
            # Process exited
            self._exit_code = os.WEXITSTATUS(status) if os.WIFEXITED(status) else -1
            return False
        except ChildProcessError:
            return False

    def spawn(self, command: str, args: list[str] | None = None) -> int:
        """Spawn a subprocess with PTY.

        Args:
            command: Command to execute (will be looked up in PATH)
            args: Arguments to pass (command is automatically prepended)

        Returns:
            The child process ID
        """
        if self._master_fd is not None:
            raise RuntimeError("PTY session already spawned")

        args = args or []

        # Fork with PTY
        self._pid, self._master_fd = pty.fork()

        if self._pid == 0:
            # Child process
            try:
                # Set initial terminal size
                self._set_size_on_fd(sys.stdout.fileno())

                # Execute command
                os.execlp(command, command, *args)
            except Exception as e:
                # If exec fails, exit child
                print(f"Failed to execute {command}: {e}", file=sys.stderr)
                os._exit(1)
        else:
            # Parent process
            # Set initial terminal size on master
            self.set_size(self.config.rows, self.config.cols)

            # Make master non-blocking for async reads
            self._set_nonblocking(self._master_fd)

            logger.debug(f"Spawned PTY session: pid={self._pid}, fd={self._master_fd}")
            return self._pid

        # Should not reach here
        return -1

    def _set_size_on_fd(self, fd: int) -> None:
        """Set terminal size on a file descriptor."""
        size = struct.pack("HHHH", self.config.rows, self.config.cols, 0, 0)
        try:
            fcntl.ioctl(fd, termios.TIOCSWINSZ, size)
        except OSError:
            pass

    def _set_nonblocking(self, fd: int) -> None:
        """Set file descriptor to non-blocking mode."""
        flags = fcntl.fcntl(fd, fcntl.F_GETFL)
        fcntl.fcntl(fd, fcntl.F_SETFL, flags | os.O_NONBLOCK)

    def set_size(self, rows: int, cols: int) -> None:
        """Set the terminal size.

        Args:
            rows: Number of rows
            cols: Number of columns
        """
        if self._master_fd is None:
            self.config.rows = rows
            self.config.cols = cols
            return

        self.config.rows = rows
        self.config.cols = cols

        size = struct.pack("HHHH", rows, cols, 0, 0)
        try:
            fcntl.ioctl(self._master_fd, termios.TIOCSWINSZ, size)
            logger.debug(f"Set PTY size to {rows}x{cols}")
        except OSError as e:
            logger.warning(f"Failed to set PTY size: {e}")

    def write(self, data: bytes) -> int:
        """Write data to the PTY (send to subprocess stdin).

        Args:
            data: Bytes to write

        Returns:
            Number of bytes written
        """
        if self._master_fd is None:
            raise RuntimeError("PTY session not spawned")

        try:
            return os.write(self._master_fd, data)
        except OSError as e:
            logger.warning(f"PTY write failed: {e}")
            return 0

    def read(self, size: int | None = None) -> bytes:
        """Read data from the PTY (subprocess stdout/stderr).

        Non-blocking - returns empty bytes if no data available.

        Args:
            size: Maximum bytes to read (default: config.read_size)

        Returns:
            Bytes read, or empty bytes if none available
        """
        if self._master_fd is None:
            raise RuntimeError("PTY session not spawned")

        size = size or self.config.read_size

        try:
            return os.read(self._master_fd, size)
        except BlockingIOError:
            return b""
        except OSError as e:
            logger.debug(f"PTY read ended: {e}")
            return b""

    def has_data(self, timeout: float = 0) -> bool:
        """Check if data is available to read.

        Args:
            timeout: Seconds to wait (0 = no wait)

        Returns:
            True if data is available
        """
        if self._master_fd is None:
            return False

        try:
            r, _, _ = select.select([self._master_fd], [], [], timeout)
            return bool(r)
        except (ValueError, OSError):
            return False

    def wait(self, timeout: float | None = None) -> int:
        """Wait for the subprocess to exit.

        Args:
            timeout: Maximum seconds to wait (None = forever)

        Returns:
            Exit code of the subprocess
        """
        if self._pid is None:
            return -1

        if self._exit_code is not None:
            return self._exit_code

        try:
            if timeout is not None:
                # Polling wait with timeout
                elapsed = 0.0
                interval = 0.1
                while elapsed < timeout:
                    pid, status = os.waitpid(self._pid, os.WNOHANG)
                    if pid != 0:
                        self._exit_code = (
                            os.WEXITSTATUS(status) if os.WIFEXITED(status) else -1
                        )
                        return self._exit_code
                    import time

                    time.sleep(interval)
                    elapsed += interval
                return -1  # Timeout
            else:
                # Blocking wait
                _, status = os.waitpid(self._pid, 0)
                self._exit_code = (
                    os.WEXITSTATUS(status) if os.WIFEXITED(status) else -1
                )
                return self._exit_code
        except ChildProcessError:
            self._exit_code = -1
            return -1

    def close(self) -> None:
        """Close the PTY session and cleanup."""
        if self._closed:
            return

        self._closed = True

        # Close master FD
        if self._master_fd is not None:
            try:
                os.close(self._master_fd)
            except OSError:
                pass
            self._master_fd = None

        # Wait for child to exit (don't leave zombies)
        if self._pid is not None and self._exit_code is None:
            try:
                os.waitpid(self._pid, os.WNOHANG)
            except ChildProcessError:
                pass

        logger.debug("PTY session closed")

    def __enter__(self) -> PTYSession:
        return self

    def __exit__(self, *args: object) -> None:
        self.close()


class PTYStreamExecutor:
    """Async executor for PTY streaming I/O.

    Integrates PTYSession with asyncio event loop for
    non-blocking bidirectional communication.
    """

    def __init__(
        self,
        session: PTYSession,
        on_output: Callable[[bytes], None],
        on_exit: Callable[[int], None],
    ):
        """Initialize the stream executor.

        Args:
            session: The PTY session to manage
            on_output: Callback when PTY produces output
            on_exit: Callback when subprocess exits
        """
        self.session = session
        self.on_output = on_output
        self.on_exit = on_exit
        self._running = False
        self._input_queue: asyncio.Queue[bytes] = asyncio.Queue()
        self._reader_task: asyncio.Task[None] | None = None
        self._writer_task: asyncio.Task[None] | None = None

    async def start(self) -> None:
        """Start the I/O tasks."""
        if self._running:
            return

        self._running = True

        # Start reader and writer tasks
        self._reader_task = asyncio.create_task(self._read_loop())
        self._writer_task = asyncio.create_task(self._write_loop())

        logger.debug("PTY stream executor started")

    async def stop(self) -> None:
        """Stop the I/O tasks."""
        self._running = False

        # Cancel tasks
        if self._reader_task:
            self._reader_task.cancel()
            try:
                await self._reader_task
            except asyncio.CancelledError:
                pass

        if self._writer_task:
            self._writer_task.cancel()
            try:
                await self._writer_task
            except asyncio.CancelledError:
                pass

        logger.debug("PTY stream executor stopped")

    async def send_input(self, data: bytes) -> None:
        """Send input to the PTY subprocess.

        Args:
            data: Bytes to send to stdin
        """
        await self._input_queue.put(data)

    async def _read_loop(self) -> None:
        """Read from PTY and emit output."""
        loop = asyncio.get_event_loop()

        while self._running and self.session.is_alive:
            # Check for data using select in thread pool
            # (select on PTY fd doesn't work well with asyncio)
            try:
                has_data = await loop.run_in_executor(
                    None, lambda: self.session.has_data(0.05)
                )

                if has_data:
                    data = await loop.run_in_executor(None, self.session.read)
                    if data:
                        self.on_output(data)
                else:
                    # Small delay to avoid busy loop
                    await asyncio.sleep(0.01)

            except Exception as e:
                logger.debug(f"Read loop error: {e}")
                break

        # Process exited - get exit code
        if not self.session.is_alive:
            exit_code = self.session.wait(timeout=0.1)
            self.on_exit(exit_code)

    async def _write_loop(self) -> None:
        """Write input to PTY."""
        loop = asyncio.get_event_loop()

        while self._running:
            try:
                # Wait for input with timeout
                try:
                    data = await asyncio.wait_for(self._input_queue.get(), timeout=0.1)
                    await loop.run_in_executor(None, self.session.write, data)
                except asyncio.TimeoutError:
                    continue

            except Exception as e:
                logger.debug(f"Write loop error: {e}")
                break


# =============================================================================
# Terminal Utilities
# =============================================================================


def get_terminal_size() -> tuple[int, int]:
    """Get the current terminal size.

    Returns:
        (rows, cols) tuple
    """
    try:
        size = struct.pack("HHHH", 0, 0, 0, 0)
        result = fcntl.ioctl(sys.stdout.fileno(), termios.TIOCGWINSZ, size)
        rows, cols = struct.unpack("HHHH", result)[:2]
        return rows, cols
    except (OSError, IOError):
        return 24, 80  # Fallback


class RawTerminal:
    """Context manager for raw terminal mode.

    Sets the terminal to raw mode for direct character input,
    and restores original settings on exit.
    """

    def __init__(self, fd: int | None = None):
        """Initialize with file descriptor.

        Args:
            fd: File descriptor (default: stdin)
        """
        self.fd = fd if fd is not None else sys.stdin.fileno()
        self._original_settings: list[int | list[bytes | int]] | None = None

    def __enter__(self) -> RawTerminal:
        try:
            self._original_settings = termios.tcgetattr(self.fd)
            tty.setraw(self.fd)
        except termios.error:
            pass
        return self

    def __exit__(self, *args: object) -> None:
        if self._original_settings:
            try:
                termios.tcsetattr(self.fd, termios.TCSAFLUSH, self._original_settings)
            except termios.error:
                pass
