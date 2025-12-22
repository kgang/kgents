"""
Unix Socket Server for CLI Routing.

Handles CLI requests routed through kgentsd, enabling:
- Centralized command execution with daemon context
- Trust-gated operations via ActionGate
- Audit trail for all CLI activity
- Consistent bootstrap state across all commands

Wire Protocol:
    [4 bytes: uint32 BE length] + [N bytes: JSON payload]

See: plans/rustling-wishing-summit.md for architecture.
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
import struct
import time
import uuid
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .command_executor import CommandExecutor

logger = logging.getLogger("kgentsd.socket")


# =============================================================================
# Wire Protocol Messages
# =============================================================================


@dataclass
class CLIRequest:
    """Request from CLI to daemon."""

    command: str  # e.g., "brain"
    args: list[str]  # e.g., ["capture", "hello"]
    cwd: str  # Current working directory
    env: dict[str, str]  # Filtered environment variables
    flags: dict[str, Any]  # Global flags (--format, --budget, etc.)
    correlation_id: str = field(default_factory=lambda: str(uuid.uuid4()))

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> CLIRequest:
        """Deserialize from dict."""
        return cls(
            command=data["command"],
            args=data.get("args", []),
            cwd=data.get("cwd", "."),
            env=data.get("env", {}),
            flags=data.get("flags", {}),
            correlation_id=data.get("correlation_id", str(uuid.uuid4())),
        )

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dict."""
        return asdict(self)


@dataclass
class CLIResponse:
    """Response from daemon to CLI."""

    correlation_id: str
    exit_code: int
    stdout: str
    stderr: str
    semantic: dict[str, Any] | None = None  # FD3 structured output
    duration_ms: int = 0

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> CLIResponse:
        """Deserialize from dict."""
        return cls(
            correlation_id=data["correlation_id"],
            exit_code=data.get("exit_code", 0),
            stdout=data.get("stdout", ""),
            stderr=data.get("stderr", ""),
            semantic=data.get("semantic"),
            duration_ms=data.get("duration_ms", 0),
        )

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dict."""
        return asdict(self)

    @classmethod
    def error(cls, correlation_id: str, message: str, exit_code: int = 1) -> CLIResponse:
        """Create an error response."""
        return cls(
            correlation_id=correlation_id,
            exit_code=exit_code,
            stdout="",
            stderr=message,
        )


# =============================================================================
# Wire Protocol Encoding/Decoding
# =============================================================================


def encode_message(data: dict[str, Any]) -> bytes:
    """Encode a message with length prefix.

    Format: [4 bytes: uint32 BE length] + [N bytes: JSON payload]
    """
    payload = json.dumps(data).encode("utf-8")
    length = struct.pack(">I", len(payload))
    return length + payload


async def decode_message(reader: asyncio.StreamReader) -> dict[str, Any] | None:
    """Decode a length-prefixed message.

    Returns None if connection closed.
    """
    # Read length prefix
    length_bytes = await reader.readexactly(4)
    if not length_bytes:
        return None

    length = struct.unpack(">I", length_bytes)[0]

    # Sanity check: max 100MB message
    if length > 100 * 1024 * 1024:
        raise ValueError(f"Message too large: {length} bytes")

    # Read payload
    payload = await reader.readexactly(length)
    result: dict[str, Any] = json.loads(payload.decode("utf-8"))
    return result


def encode_message_sync(data: dict[str, Any]) -> bytes:
    """Synchronous version of encode_message for client use."""
    return encode_message(data)


def decode_message_sync(sock: Any) -> dict[str, Any]:
    """Synchronous version of decode_message for client use.

    Args:
        sock: A socket.socket object
    """
    # Read length prefix
    length_bytes = b""
    while len(length_bytes) < 4:
        chunk = sock.recv(4 - len(length_bytes))
        if not chunk:
            raise ConnectionError("Connection closed while reading length")
        length_bytes += chunk

    length = struct.unpack(">I", length_bytes)[0]

    # Sanity check
    if length > 100 * 1024 * 1024:
        raise ValueError(f"Message too large: {length} bytes")

    # Read payload in chunks
    chunks = []
    remaining = length
    while remaining > 0:
        chunk = sock.recv(min(remaining, 65536))
        if not chunk:
            raise ConnectionError("Connection closed while reading payload")
        chunks.append(chunk)
        remaining -= len(chunk)

    payload = b"".join(chunks)
    result: dict[str, Any] = json.loads(payload.decode("utf-8"))
    return result


# =============================================================================
# Socket Server
# =============================================================================


class CLISocketServer:
    """Unix socket server for CLI requests.

    Handles multiple concurrent connections, routing each request
    through the CommandExecutor with proper output capture.
    """

    def __init__(
        self,
        socket_path: Path,
        command_executor: CommandExecutor,
        max_connections: int = 10,
    ):
        self.socket_path = socket_path
        self.executor = command_executor
        self.max_connections = max_connections

        self._server: asyncio.Server | None = None
        self._semaphore = asyncio.Semaphore(max_connections)
        self._active_connections = 0

    async def start(self) -> None:
        """Start the socket server."""
        # Remove stale socket
        if self.socket_path.exists():
            try:
                self.socket_path.unlink()
            except OSError as e:
                logger.warning(f"Could not remove stale socket: {e}")

        # Ensure parent directory exists
        self.socket_path.parent.mkdir(parents=True, exist_ok=True)

        # Start server
        self._server = await asyncio.start_unix_server(
            self._handle_connection,
            path=str(self.socket_path),
        )

        # Set permissions (owner-only)
        os.chmod(self.socket_path, 0o600)

        logger.info(f"CLI socket server listening on {self.socket_path}")

    async def stop(self) -> None:
        """Stop the socket server gracefully."""
        if self._server:
            self._server.close()
            await self._server.wait_closed()
            self._server = None

        # Remove socket file
        if self.socket_path.exists():
            try:
                self.socket_path.unlink()
            except OSError as e:
                logger.warning(f"Could not remove socket: {e}")

        logger.info("CLI socket server stopped")

    async def _handle_connection(
        self,
        reader: asyncio.StreamReader,
        writer: asyncio.StreamWriter,
    ) -> None:
        """Handle a single client connection."""
        async with self._semaphore:
            self._active_connections += 1
            peer = writer.get_extra_info("peername") or "unknown"
            logger.debug(f"New connection from {peer}")

            try:
                await self._process_requests(reader, writer)
            except asyncio.IncompleteReadError:
                logger.debug(f"Client {peer} disconnected")
            except Exception as e:
                logger.error(f"Error handling connection from {peer}: {e}")
            finally:
                self._active_connections -= 1
                writer.close()
                await writer.wait_closed()
                logger.debug(f"Connection closed: {peer}")

    async def _process_requests(
        self,
        reader: asyncio.StreamReader,
        writer: asyncio.StreamWriter,
    ) -> None:
        """Process requests on a connection until closed."""
        while True:
            # Read request
            try:
                data = await decode_message(reader)
            except asyncio.IncompleteReadError:
                # Connection closed
                break

            if data is None:
                break

            # Parse request
            try:
                request = CLIRequest.from_dict(data)
            except (KeyError, TypeError) as e:
                response = CLIResponse.error(
                    correlation_id=data.get("correlation_id", "unknown"),
                    message=f"Invalid request format: {e}",
                )
                await self._send_response(writer, response)
                continue

            # Execute command
            start_time = time.monotonic()
            try:
                response = await self.executor.execute(request)
            except Exception as e:
                logger.exception(f"Error executing command: {request.command}")
                response = CLIResponse.error(
                    correlation_id=request.correlation_id,
                    message=f"Command execution failed: {e}",
                )

            # Add timing
            response.duration_ms = int((time.monotonic() - start_time) * 1000)

            # Send response
            await self._send_response(writer, response)

    async def _send_response(
        self,
        writer: asyncio.StreamWriter,
        response: CLIResponse,
    ) -> None:
        """Send a response to the client."""
        data = encode_message(response.to_dict())
        writer.write(data)
        await writer.drain()

    @property
    def is_running(self) -> bool:
        """Check if the server is running."""
        return self._server is not None and self._server.is_serving()

    @property
    def active_connections(self) -> int:
        """Get the number of active connections."""
        return self._active_connections
