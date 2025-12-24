"""
Unix Socket Client for CLI Routing.

Synchronous client used by hollow.py to route commands
through the kgentsd daemon. This is intentionally synchronous
because the CLI entry point (hollow.py) is sync.

Usage:
    from services.kgentsd.socket_client import is_daemon_available, route_command

    if is_daemon_available():
        response = route_command("brain", ["capture", "hello"], flags)
        print(response.stdout)
        sys.exit(response.exit_code)
"""

from __future__ import annotations

import fcntl
import os
import select
import signal
import socket
import struct
import sys
import termios
import tty
import uuid
from pathlib import Path
from typing import Any

from .socket_server import (
    CLIRequest,
    CLIResponse,
    CLIStreamMessage,
    decode_message_sync,
    encode_message_sync,
)

# =============================================================================
# Constants
# =============================================================================

SOCKET_PATH = Path.home() / ".kgents" / "kgentsd.sock"
DEFAULT_TIMEOUT = 30.0  # seconds

# Safe environment variables to pass through
SAFE_ENV_VARS = frozenset(
    {
        # kgents-specific
        "KGENTS_FD3",
        "KGENTS_DATABASE_URL",
        "KGENTS_DEBUG",
        "KGENTS_GATEWAY_URL",
        # System
        "HOME",
        "USER",
        "PATH",
        "TERM",
        "LANG",
        "LC_ALL",
        "TZ",
        # Git
        "GIT_AUTHOR_NAME",
        "GIT_AUTHOR_EMAIL",
        "GIT_COMMITTER_NAME",
        "GIT_COMMITTER_EMAIL",
    }
)


# =============================================================================
# Errors
# =============================================================================


class DaemonNotRunningError(Exception):
    """Raised when the daemon is not running."""

    pass


class DaemonConnectionError(Exception):
    """Raised when unable to connect to the daemon."""

    pass


class DaemonTimeoutError(Exception):
    """Raised when the daemon doesn't respond in time."""

    pass


class DaemonProtocolError(Exception):
    """Raised when the daemon returns an invalid response."""

    pass


# =============================================================================
# Public API
# =============================================================================


def is_daemon_available(socket_path: Path | None = None) -> bool:
    """Check if the daemon socket exists and is connectable.

    This performs a quick connection test to verify the daemon
    is actually accepting connections, not just that the socket
    file exists.
    """
    path = socket_path or SOCKET_PATH

    # Quick check: does socket file exist?
    if not path.exists():
        return False

    # Try to connect (with very short timeout)
    try:
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        sock.settimeout(0.5)  # 500ms for quick check
        sock.connect(str(path))
        sock.close()
        return True
    except (socket.error, OSError):
        return False


def route_command(
    command: str,
    args: list[str],
    flags: dict[str, Any],
    *,
    socket_path: Path | None = None,
    timeout: float = DEFAULT_TIMEOUT,
) -> CLIResponse:
    """Route a command through the daemon via Unix socket.

    Automatically selects PTY mode if stdin/stdout are TTYs.

    Args:
        command: The command name (e.g., "brain")
        args: Command arguments (e.g., ["capture", "hello"])
        flags: Global flags from hollow.py (--format, --budget, etc.)
        socket_path: Override socket path (for testing)
        timeout: Socket timeout in seconds

    Returns:
        CLIResponse with exit_code, stdout, stderr, semantic

    Raises:
        DaemonNotRunningError: Socket doesn't exist
        DaemonConnectionError: Can't connect to socket
        DaemonTimeoutError: No response within timeout
        DaemonProtocolError: Invalid response format
    """
    # Auto-select PTY mode if both stdin and stdout are TTYs
    if sys.stdin.isatty() and sys.stdout.isatty():
        return route_command_pty(
            command, args, flags, socket_path=socket_path, timeout=timeout
        )

    return route_command_simple(
        command, args, flags, socket_path=socket_path, timeout=timeout
    )


def route_command_simple(
    command: str,
    args: list[str],
    flags: dict[str, Any],
    *,
    socket_path: Path | None = None,
    timeout: float = DEFAULT_TIMEOUT,
) -> CLIResponse:
    """Route a command through the daemon (non-PTY mode).

    Used when stdin/stdout are not TTYs (pipes, redirects, etc.)
    """
    path = socket_path or SOCKET_PATH

    # Build request
    request = CLIRequest(
        command=command,
        args=args,
        cwd=str(Path.cwd()),
        env=_filter_env(dict(os.environ)),
        flags=flags,
        correlation_id=str(uuid.uuid4()),
        pty=False,
    )

    # Connect
    sock = _connect(path, timeout)

    try:
        # Send request
        _send_request(sock, request)

        # Receive response
        response = _receive_response(sock, request.correlation_id)

        return response

    finally:
        sock.close()


def route_command_pty(
    command: str,
    args: list[str],
    flags: dict[str, Any],
    *,
    socket_path: Path | None = None,
    timeout: float = DEFAULT_TIMEOUT,
) -> CLIResponse:
    """Route a command through the daemon with PTY support.

    This function:
    1. Sets local terminal to raw mode
    2. Installs SIGWINCH handler for terminal resize
    3. Opens bidirectional streaming connection to daemon
    4. Forwards stdin to daemon, daemon output to stdout
    5. Restores terminal on exit

    Returns:
        CLIResponse with exit_code (stdout/stderr are streamed directly)
    """
    path = socket_path or SOCKET_PATH

    # Get current terminal size
    term_size = _get_terminal_size()

    # Build PTY request
    correlation_id = str(uuid.uuid4())
    request = CLIRequest(
        command=command,
        args=args,
        cwd=str(Path.cwd()),
        env=_filter_env(dict(os.environ)),
        flags=flags,
        correlation_id=correlation_id,
        pty=True,
        term_size=term_size,
    )

    # Connect
    sock = _connect(path, timeout)
    sock.setblocking(False)

    # Save terminal state for restoration
    original_settings = None
    original_sigwinch = None
    seq = 0

    try:
        # Set terminal to raw mode
        try:
            original_settings = termios.tcgetattr(sys.stdin.fileno())
            tty.setraw(sys.stdin.fileno())
        except termios.error:
            pass

        # Install SIGWINCH handler
        def on_resize(signum: int, frame: Any) -> None:
            nonlocal seq
            new_size = _get_terminal_size()
            msg = CLIStreamMessage.resize(correlation_id, new_size[0], new_size[1], seq)
            seq += 1
            try:
                sock.sendall(encode_message_sync(msg.to_dict()))
            except (socket.error, OSError):
                pass

        try:
            original_sigwinch = signal.signal(signal.SIGWINCH, on_resize)
        except (ValueError, OSError):
            pass  # SIGWINCH not available

        # Send initial request
        sock.setblocking(True)
        sock.sendall(encode_message_sync(request.to_dict()))
        sock.setblocking(False)

        # Bidirectional I/O loop
        exit_code = _pty_io_loop(sock, correlation_id, seq)

        return CLIResponse(
            correlation_id=correlation_id,
            exit_code=exit_code,
            stdout="",  # Output was streamed directly
            stderr="",
        )

    finally:
        # Restore terminal settings
        if original_settings is not None:
            try:
                termios.tcsetattr(
                    sys.stdin.fileno(), termios.TCSAFLUSH, original_settings
                )
            except termios.error:
                pass

        # Restore SIGWINCH handler
        if original_sigwinch is not None:
            try:
                signal.signal(signal.SIGWINCH, original_sigwinch)
            except (ValueError, OSError):
                pass

        sock.close()


# =============================================================================
# Internal Helpers
# =============================================================================


def _filter_env(env: dict[str, str]) -> dict[str, str]:
    """Filter environment to only safe variables."""
    return {k: v for k, v in env.items() if k in SAFE_ENV_VARS}


def _connect(path: Path, timeout: float) -> socket.socket:
    """Connect to the daemon socket."""
    if not path.exists():
        raise DaemonNotRunningError(f"Daemon socket not found: {path}")

    try:
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        sock.connect(str(path))
        return sock
    except socket.timeout:
        raise DaemonTimeoutError(f"Connection to daemon timed out after {timeout}s")
    except socket.error as e:
        raise DaemonConnectionError(f"Cannot connect to daemon: {e}")


def _send_request(sock: socket.socket, request: CLIRequest) -> None:
    """Send a request to the daemon."""
    try:
        data = encode_message_sync(request.to_dict())
        sock.sendall(data)
    except socket.timeout:
        raise DaemonTimeoutError("Timeout while sending request to daemon")
    except socket.error as e:
        raise DaemonConnectionError(f"Error sending request: {e}")


def _receive_response(sock: socket.socket, correlation_id: str) -> CLIResponse:
    """Receive a response from the daemon."""
    try:
        data = decode_message_sync(sock)
    except socket.timeout:
        raise DaemonTimeoutError("Timeout waiting for daemon response")
    except (ConnectionError, socket.error) as e:
        raise DaemonConnectionError(f"Error receiving response: {e}")
    except (ValueError, UnicodeDecodeError) as e:
        raise DaemonProtocolError(f"Invalid response encoding: {e}")

    try:
        response = CLIResponse.from_dict(data)
    except (KeyError, TypeError) as e:
        raise DaemonProtocolError(f"Invalid response format: {e}")

    # Verify correlation ID matches
    if response.correlation_id != correlation_id:
        raise DaemonProtocolError(
            f"Response correlation_id mismatch: "
            f"expected {correlation_id}, got {response.correlation_id}"
        )

    return response


def _get_terminal_size() -> tuple[int, int]:
    """Get the current terminal size (rows, cols)."""
    try:
        size = struct.pack("HHHH", 0, 0, 0, 0)
        result = fcntl.ioctl(sys.stdout.fileno(), termios.TIOCGWINSZ, size)
        rows, cols = struct.unpack("HHHH", result)[:2]
        return rows, cols
    except (OSError, IOError):
        return 24, 80  # Fallback


# =============================================================================
# Event Handling
# =============================================================================


def _handle_event(event: dict[str, Any]) -> None:
    """
    Handle structured event from daemon.

    Events are structured messages for things like:
    - Progress updates (type="progress")
    - Status changes (type="status")
    - Warnings (type="warning")
    - Custom events from handlers

    Args:
        event: Event dictionary with at least a "type" key
    """
    event_type = event.get("type", "unknown")

    if event_type == "progress":
        _handle_progress_event(event)
    elif event_type == "status":
        _handle_status_event(event)
    elif event_type == "warning":
        _handle_warning_event(event)
    else:
        # Unknown event type - log if debug mode
        pass


def _handle_progress_event(event: dict[str, Any]) -> None:
    """Handle a progress event.

    Displays a progress indicator if Rich is available.
    """
    step = event.get("step", "")
    percent = event.get("percent", 0)
    message = event.get("message", "")

    try:
        from rich.console import Console

        console = Console(stderr=True)
        # Clear line and show progress
        progress_bar = "█" * int(percent / 5) + "░" * (20 - int(percent / 5))
        console.print(
            f"\r[dim]{step}[/dim] [{progress_bar}] {percent:.0f}% {message}",
            end="",
        )
        if percent >= 100:
            console.print()  # Newline at completion
    except ImportError:
        # Fallback without Rich
        if percent >= 100:
            print(f"\r{step}: {message or 'Complete'}")
        else:
            print(f"\r{step}: {percent:.0f}%", end="", flush=True)


def _handle_status_event(event: dict[str, Any]) -> None:
    """Handle a status event.

    Displays a status message.
    """
    status = event.get("status", "")
    message = event.get("message", "")

    try:
        from rich.console import Console

        console = Console(stderr=True)
        emoji = {
            "starting": "🚀",
            "running": "⚡",
            "complete": "✅",
            "error": "❌",
            "warning": "⚠️",
        }.get(status, "ℹ️")
        console.print(f"[dim]{emoji} {status}:[/dim] {message}")
    except ImportError:
        print(f"[{status}] {message}", file=sys.stderr)


def _handle_warning_event(event: dict[str, Any]) -> None:
    """Handle a warning event."""
    message = event.get("message", "")

    try:
        from rich.console import Console

        console = Console(stderr=True)
        console.print(f"[yellow]⚠️  {message}[/yellow]")
    except ImportError:
        print(f"Warning: {message}", file=sys.stderr)


def _pty_io_loop(sock: socket.socket, correlation_id: str, seq: int) -> int:
    """Run bidirectional I/O loop for PTY mode.

    Forwards stdin to daemon, daemon output to stdout.
    Returns the exit code when the subprocess exits.
    """
    stdin_fd = sys.stdin.fileno()
    exit_code = 0

    # Buffer for partial message reads
    recv_buffer = b""

    while True:
        # Use select to wait for input from either stdin or socket
        try:
            readable, _, _ = select.select([stdin_fd, sock], [], [], 0.1)
        except (ValueError, OSError):
            break

        # Handle stdin input
        if stdin_fd in readable:
            try:
                data = os.read(stdin_fd, 4096)
                if data:
                    # Send input to daemon
                    msg = CLIStreamMessage.input(correlation_id, data, seq)
                    seq += 1
                    sock.setblocking(True)
                    sock.sendall(encode_message_sync(msg.to_dict()))
                    sock.setblocking(False)
            except (OSError, IOError):
                pass

        # Handle socket input (messages from daemon)
        if sock in readable:
            try:
                # Read available data
                chunk = sock.recv(65536)
                if not chunk:
                    # Connection closed
                    break

                recv_buffer += chunk

                # Process complete messages from buffer
                while True:
                    if len(recv_buffer) < 4:
                        break

                    # Parse length prefix
                    msg_len = struct.unpack(">I", recv_buffer[:4])[0]

                    if len(recv_buffer) < 4 + msg_len:
                        break  # Incomplete message

                    # Extract message
                    payload = recv_buffer[4 : 4 + msg_len]
                    recv_buffer = recv_buffer[4 + msg_len :]

                    # Parse message
                    import json

                    data = json.loads(payload.decode("utf-8"))

                    # Check if it's a stream message
                    if "type" in data:
                        msg = CLIStreamMessage.from_dict(data)

                        if msg.type == "output" and msg.data:
                            # Write output to stdout
                            sys.stdout.buffer.write(msg.data)
                            sys.stdout.buffer.flush()
                        elif msg.type == "event" and msg.event:
                            # Handle structured event from daemon
                            _handle_event(msg.event)
                        elif msg.type == "exit":
                            exit_code = msg.exit_code or 0
                            return exit_code
                    else:
                        # Might be a CLIResponse (error case)
                        if "exit_code" in data:
                            return data.get("exit_code", 1)

            except BlockingIOError:
                pass
            except (OSError, IOError, json.JSONDecodeError):
                break

    return exit_code
