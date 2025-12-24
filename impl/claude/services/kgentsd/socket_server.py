"""
Unix Socket Server for CLI Routing.

Handles CLI requests routed through kgentsd, enabling:
- Centralized command execution with daemon context
- Trust-gated operations via ActionGate
- Audit trail for all CLI activity
- Consistent bootstrap state across all commands
- Multi-processing for CPU-bound tasks (LLM, crystallization)
- Multi-threading for I/O-bound tasks (database, file ops)

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
from typing import TYPE_CHECKING, Any, Literal

if TYPE_CHECKING:
    from .command_executor import CommandExecutor
    from .worker_pool import WorkerPoolManager

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
    # PTY mode fields
    pty: bool = False  # Request PTY allocation for interactive commands
    term_size: tuple[int, int] | None = None  # Terminal size (rows, cols)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> CLIRequest:
        """Deserialize from dict."""
        term_size = data.get("term_size")
        if term_size and isinstance(term_size, list):
            term_size = tuple(term_size)
        return cls(
            command=data["command"],
            args=data.get("args", []),
            cwd=data.get("cwd", "."),
            env=data.get("env", {}),
            flags=data.get("flags", {}),
            correlation_id=data.get("correlation_id", str(uuid.uuid4())),
            pty=data.get("pty", False),
            term_size=term_size,
        )

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dict."""
        result = asdict(self)
        # Convert tuple to list for JSON serialization
        if result.get("term_size"):
            result["term_size"] = list(result["term_size"])
        return result


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


# PTY stream message types
PTYStreamType = Literal["output", "input", "resize", "exit", "event"]


@dataclass
class CLIStreamMessage:
    """Streaming message for PTY mode bidirectional I/O.

    Used for real-time communication between client and daemon during
    interactive PTY sessions. Messages flow in both directions:

    - output: daemon → client (PTY output chunk)
    - input:  client → daemon (user input to forward to PTY)
    - resize: client → daemon (terminal size change)
    - exit:   daemon → client (process exited)
    - event:  daemon → client (structured event: progress, status, etc.)
    """

    type: PTYStreamType
    correlation_id: str
    seq: int = 0  # Sequence number for ordering
    data: bytes | None = None  # Raw bytes for input/output
    exit_code: int | None = None  # Only for type="exit"
    term_size: tuple[int, int] | None = None  # Only for type="resize" (rows, cols)
    event: dict[str, Any] | None = None  # Only for type="event" (structured data)

    @classmethod
    def output(cls, correlation_id: str, data: bytes, seq: int = 0) -> CLIStreamMessage:
        """Create an output message (daemon → client)."""
        return cls(type="output", correlation_id=correlation_id, data=data, seq=seq)

    @classmethod
    def input(cls, correlation_id: str, data: bytes, seq: int = 0) -> CLIStreamMessage:
        """Create an input message (client → daemon)."""
        return cls(type="input", correlation_id=correlation_id, data=data, seq=seq)

    @classmethod
    def resize(
        cls, correlation_id: str, rows: int, cols: int, seq: int = 0
    ) -> CLIStreamMessage:
        """Create a resize message (client → daemon)."""
        return cls(
            type="resize",
            correlation_id=correlation_id,
            term_size=(rows, cols),
            seq=seq,
        )

    @classmethod
    def exit(cls, correlation_id: str, exit_code: int, seq: int = 0) -> CLIStreamMessage:
        """Create an exit message (daemon → client)."""
        return cls(
            type="exit", correlation_id=correlation_id, exit_code=exit_code, seq=seq
        )

    @classmethod
    def event(
        cls, correlation_id: str, event: dict[str, Any], seq: int = 0
    ) -> CLIStreamMessage:
        """Create an event message (daemon → client).

        Use for structured data like progress updates, status changes, etc.

        Args:
            correlation_id: Request tracking ID
            event: Event payload (e.g., {"type": "progress", "percent": 50})
            seq: Sequence number
        """
        return cls(
            type="event", correlation_id=correlation_id, event=event, seq=seq
        )

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> CLIStreamMessage:
        """Deserialize from dict."""
        term_size = data.get("term_size")
        if term_size and isinstance(term_size, list):
            term_size = tuple(term_size)

        # Handle base64-encoded bytes
        raw_data = data.get("data")
        if raw_data and isinstance(raw_data, str):
            import base64

            raw_data = base64.b64decode(raw_data)

        return cls(
            type=data["type"],
            correlation_id=data["correlation_id"],
            seq=data.get("seq", 0),
            data=raw_data,
            exit_code=data.get("exit_code"),
            term_size=term_size,
            event=data.get("event"),
        )

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dict."""
        result: dict[str, Any] = {
            "type": self.type,
            "correlation_id": self.correlation_id,
            "seq": self.seq,
        }

        # Encode bytes as base64 for JSON
        if self.data is not None:
            import base64

            result["data"] = base64.b64encode(self.data).decode("ascii")

        if self.exit_code is not None:
            result["exit_code"] = self.exit_code

        if self.term_size is not None:
            result["term_size"] = list(self.term_size)

        if self.event is not None:
            result["event"] = self.event

        return result


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

    Enhanced with worker pool integration for:
    - CPU-bound tasks: Process pool (LLM, crystallization)
    - I/O-bound tasks: Thread pool (database, file ops)
    - Async tasks: Event loop (socket I/O, SSE streaming)

    Stats tracking for monitoring and debugging.
    """

    def __init__(
        self,
        socket_path: Path,
        command_executor: CommandExecutor,
        max_connections: int = 10,
        worker_pool: WorkerPoolManager | None = None,
    ):
        self.socket_path = socket_path
        self.executor = command_executor
        self.max_connections = max_connections
        self.worker_pool = worker_pool

        self._server: asyncio.Server | None = None
        self._semaphore = asyncio.Semaphore(max_connections)
        self._active_connections = 0

        # Stats tracking
        self._stats = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "pty_sessions": 0,
            "peak_connections": 0,
            "total_duration_ms": 0,
        }

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
            # Track peak connections
            if self._active_connections > self._stats["peak_connections"]:
                self._stats["peak_connections"] = self._active_connections

            peer = writer.get_extra_info("peername") or "unknown"
            logger.debug(f"New connection from {peer} (active: {self._active_connections})")

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

            # Route based on PTY mode
            if request.pty:
                # PTY mode: bidirectional streaming session
                self._stats["pty_sessions"] += 1
                await self._handle_pty_session(reader, writer, request)
                # PTY session takes over the connection - exit loop after
                break
            else:
                # Standard mode: request-response
                self._stats["total_requests"] += 1
                start_time = time.monotonic()
                try:
                    response = await self.executor.execute(request, self.worker_pool)
                    self._stats["successful_requests"] += 1
                except Exception as e:
                    logger.exception(f"Error executing command: {request.command}")
                    response = CLIResponse.error(
                        correlation_id=request.correlation_id,
                        message=f"Command execution failed: {e}",
                    )
                    self._stats["failed_requests"] += 1

                # Add timing
                duration_ms = int((time.monotonic() - start_time) * 1000)
                response.duration_ms = duration_ms
                self._stats["total_duration_ms"] += duration_ms

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

    async def _send_stream_message(
        self,
        writer: asyncio.StreamWriter,
        message: CLIStreamMessage,
    ) -> None:
        """Send a stream message to the client."""
        data = encode_message(message.to_dict())
        writer.write(data)
        await writer.drain()

    async def _handle_pty_session(
        self,
        reader: asyncio.StreamReader,
        writer: asyncio.StreamWriter,
        request: CLIRequest,
    ) -> None:
        """Handle a PTY streaming session.

        Routes based on handler tier:
        - Tier 2: Execute in daemon with PTY I/O bridge (no subprocess)
        - Tier 3: True subprocess with PTY (fork-exec, for external commands)
        - Default: Fall back to Tier 2 if handler exists, else Tier 3
        """
        from protocols.cli.handler_meta import get_handler_meta, infer_handler_meta
        from protocols.cli.hollow import resolve_command

        correlation_id = request.correlation_id

        # Get handler metadata to determine tier
        meta = get_handler_meta(request.command)
        if meta is None:
            # Infer from handler
            handler = resolve_command(request.command)
            if handler is not None:
                meta = infer_handler_meta(request.command, handler)

        # Determine execution mode
        if meta is not None and meta.tier == 3:
            # Tier 3: True subprocess (external commands)
            await self._handle_pty_session_subprocess(reader, writer, request)
        elif meta is not None and (meta.tier == 2 or meta.tier == 1):
            # Tier 1 or 2: Execute in daemon with I/O bridge
            await self._handle_pty_session_bridged(reader, writer, request, meta)
        else:
            # Unknown command - try subprocess fallback
            await self._handle_pty_session_subprocess(reader, writer, request)

    async def _handle_pty_session_bridged(
        self,
        reader: asyncio.StreamReader,
        writer: asyncio.StreamWriter,
        request: CLIRequest,
        meta: Any,
    ) -> None:
        """Handle PTY session via I/O bridge (Tier 1 & 2).

        Executes the handler directly in the daemon's process,
        bridging I/O to the client via the socket.
        """
        logger.info(f"Starting bridged PTY session: {request.command} (tier={meta.tier})")

        try:
            # Set up PTY streams on executor
            self.executor.set_pty_streams(reader, writer)

            # Execute through command executor (handles Tier 1/2 routing)
            response = await self.executor.execute(request, self.worker_pool)

            # If Tier 1, we need to send output as stream messages
            if meta.tier == 1:
                seq = 0
                if response.stdout:
                    msg = CLIStreamMessage.output(
                        request.correlation_id,
                        response.stdout.encode("utf-8"),
                        seq,
                    )
                    await self._send_stream_message(writer, msg)
                    seq += 1
                if response.stderr:
                    msg = CLIStreamMessage.output(
                        request.correlation_id,
                        response.stderr.encode("utf-8"),
                        seq,
                    )
                    await self._send_stream_message(writer, msg)
                    seq += 1

                # ALWAYS send exit for Tier 1 (client is waiting for it)
                exit_msg = CLIStreamMessage.exit(
                    request.correlation_id,
                    response.exit_code,
                    seq,
                )
                await self._send_stream_message(writer, exit_msg)

            # Tier 2 sends its own exit message via the bridge

            logger.info(f"Bridged PTY session ended: exit_code={response.exit_code}")

        except Exception as e:
            logger.exception(f"Bridged PTY session error: {e}")
            exit_msg = CLIStreamMessage.exit(request.correlation_id, 1, 0)
            await self._send_stream_message(writer, exit_msg)

        finally:
            self.executor.clear_pty_streams()

    async def _handle_pty_session_subprocess(
        self,
        reader: asyncio.StreamReader,
        writer: asyncio.StreamWriter,
        request: CLIRequest,
    ) -> None:
        """Handle PTY session via true subprocess (Tier 3).

        Spawns a subprocess with PTY for bidirectional I/O.
        Used for external commands that need full PTY support.
        """
        from .pty_executor import PTYConfig, PTYSession, PTYStreamExecutor

        correlation_id = request.correlation_id
        seq = 0

        # Configure PTY
        config = PTYConfig()
        if request.term_size:
            config.rows, config.cols = request.term_size

        session = PTYSession(config)

        try:
            # Build command
            command, args = self._build_pty_command(request)

            logger.info(f"Starting subprocess PTY session: {command} {args}")

            # Spawn subprocess with PTY
            session.spawn(command, args)

            # Output callback - send to client
            async def on_output(data: bytes) -> None:
                nonlocal seq
                msg = CLIStreamMessage.output(correlation_id, data, seq)
                seq += 1
                await self._send_stream_message(writer, msg)

            # Exit callback - notify client
            exit_event = asyncio.Event()
            exit_code_holder: list[int] = [0]

            def on_exit(code: int) -> None:
                exit_code_holder[0] = code
                exit_event.set()

            # Create sync wrapper for async callback
            loop = asyncio.get_event_loop()

            def sync_on_output(data: bytes) -> None:
                asyncio.run_coroutine_threadsafe(on_output(data), loop)

            # Start stream executor
            executor = PTYStreamExecutor(session, sync_on_output, on_exit)
            await executor.start()

            # Bidirectional loop: read from client, forward to PTY
            try:
                while not exit_event.is_set():
                    try:
                        data = await asyncio.wait_for(decode_message(reader), timeout=0.1)
                        if data is None:
                            break

                        msg = CLIStreamMessage.from_dict(data)

                        if msg.type == "input" and msg.data:
                            await executor.send_input(msg.data)
                        elif msg.type == "resize" and msg.term_size:
                            session.set_size(msg.term_size[0], msg.term_size[1])

                    except asyncio.TimeoutError:
                        continue
                    except asyncio.IncompleteReadError:
                        break

            finally:
                await executor.stop()

            # Send exit message
            exit_msg = CLIStreamMessage.exit(correlation_id, exit_code_holder[0], seq)
            await self._send_stream_message(writer, exit_msg)

            logger.info(f"Subprocess PTY session ended: exit_code={exit_code_holder[0]}")

        except Exception as e:
            logger.exception(f"Subprocess PTY session error: {e}")
            exit_msg = CLIStreamMessage.exit(correlation_id, 1, seq)
            await self._send_stream_message(writer, exit_msg)

        finally:
            session.close()

    def _build_pty_command(self, request: CLIRequest) -> tuple[str, list[str]]:
        """Build the command to run in PTY.

        For now, we run Python with the CLI entry point.
        This ensures the command runs in the same environment as the daemon.

        IMPORTANT: We set KGENTS_INSIDE_DAEMON=1 to prevent the spawned
        process from trying to route through the daemon again (infinite loop).
        """
        import sys

        # Set environment to prevent recursive daemon routing
        os.environ["KGENTS_INSIDE_DAEMON"] = "1"

        # Run the CLI handler in a subprocess
        # This preserves the daemon's Python environment
        python = sys.executable
        args = [
            "-m",
            "protocols.cli.hollow",
            request.command,
            *request.args,
        ]
        return python, args

    @property
    def is_running(self) -> bool:
        """Check if the server is running."""
        return self._server is not None and self._server.is_serving()

    @property
    def active_connections(self) -> int:
        """Get the number of active connections."""
        return self._active_connections

    @property
    def stats(self) -> dict[str, int]:
        """Get server statistics.

        Returns:
            Dict with keys:
            - total_requests: Total non-PTY requests received
            - successful_requests: Requests that completed successfully
            - failed_requests: Requests that failed
            - pty_sessions: Total PTY sessions created
            - peak_connections: Maximum concurrent connections seen
            - total_duration_ms: Sum of all request durations
        """
        return dict(self._stats)

    @property
    def avg_request_duration_ms(self) -> float:
        """Get average request duration in milliseconds."""
        total = self._stats["total_requests"]
        if total == 0:
            return 0.0
        return self._stats["total_duration_ms"] / total
