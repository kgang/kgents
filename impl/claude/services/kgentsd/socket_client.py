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

import os
import socket
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .socket_server import (
    CLIRequest,
    CLIResponse,
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
    path = socket_path or SOCKET_PATH

    # Build request
    request = CLIRequest(
        command=command,
        args=args,
        cwd=str(Path.cwd()),
        env=_filter_env(dict(os.environ)),
        flags=flags,
        correlation_id=str(uuid.uuid4()),
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
