"""
PTY I/O Bridge for Tier 2 Handler Execution.

This module provides the PTYBridge class that enables interactive handlers
to run in the daemon's process while bridging I/O to the client's terminal
via the Unix socket connection.

The key insight is that we don't need to fork a subprocess to get PTY
behavior - we can redirect the handler's stdout/stderr through a bridge
that sends data over the socket, and receive input from the client.

Architecture:
    ┌──────────────┐        ┌───────────────┐        ┌──────────────┐
    │ Client TTY   │◄──────►│  PTYBridge    │◄──────►│   Handler    │
    │ (real PTY)   │ socket │ (stream msgs) │ bridge │ (in daemon)  │
    └──────────────┘        └───────────────┘        └──────────────┘

See: plans/rustling-bouncing-seal.md
"""

from __future__ import annotations

import asyncio
import io
import json
import logging
import struct
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, TextIO

if TYPE_CHECKING:
    pass

logger = logging.getLogger("kgentsd.pty_bridge")


# =============================================================================
# Stream Message Encoding (shared with socket_server.py)
# =============================================================================


def encode_message(data: dict[str, Any]) -> bytes:
    """Encode a message with length prefix."""
    payload = json.dumps(data, default=str).encode("utf-8")
    return struct.pack(">I", len(payload)) + payload


async def decode_message_async(
    reader: asyncio.StreamReader,
) -> dict[str, Any] | None:
    """Decode a message from async reader."""
    try:
        length_bytes = await reader.readexactly(4)
        if not length_bytes:
            return None
        length = struct.unpack(">I", length_bytes)[0]
        payload = await reader.readexactly(length)
        return json.loads(payload.decode("utf-8"))
    except (asyncio.IncompleteReadError, json.JSONDecodeError):
        return None


# =============================================================================
# PTY Output Stream
# =============================================================================


class PTYOutputStream(io.TextIOBase):
    """
    File-like object that writes to the PTY bridge.

    This pretends to be a TTY and sends all writes to the client
    via the socket connection.

    Attributes:
        bridge: Reference to the PTYBridge
        name: Stream name ("stdout" or "stderr")
    """

    def __init__(self, bridge: PTYBridge, name: str = "stdout") -> None:
        super().__init__()
        self._bridge = bridge
        self._name = name
        self._closed = False

    def write(self, s: str) -> int:
        """Write string to the bridge (sends to client)."""
        if self._closed:
            raise ValueError("I/O operation on closed file")

        data = s.encode("utf-8")

        # Queue for async sending
        try:
            loop = asyncio.get_running_loop()
            asyncio.create_task(self._bridge.write_output(data))
        except RuntimeError:
            # No running event loop - try sync fallback
            # This can happen if called from sync code in thread pool
            try:
                if self._bridge._loop is not None:
                    asyncio.run_coroutine_threadsafe(
                        self._bridge.write_output(data),
                        self._bridge._loop,
                    )
            except Exception:
                pass

        return len(s)

    def writelines(self, lines: list[str]) -> None:
        """Write multiple lines."""
        for line in lines:
            self.write(line)

    def flush(self) -> None:
        """Flush is a no-op (messages are sent immediately)."""
        pass

    def close(self) -> None:
        """Close the stream."""
        self._closed = True

    def isatty(self) -> bool:
        """Pretend to be a TTY for ANSI support."""
        return True

    @property
    def closed(self) -> bool:
        return self._closed

    def fileno(self) -> int:
        """Fake fileno for compatibility."""
        raise io.UnsupportedOperation("fileno")

    def readable(self) -> bool:
        return False

    def writable(self) -> bool:
        return not self._closed

    def seekable(self) -> bool:
        return False

    @property
    def encoding(self) -> str:
        return "utf-8"

    @property
    def errors(self) -> str:
        return "replace"


# =============================================================================
# PTY Input Stream
# =============================================================================


class PTYInputStream(io.TextIOBase):
    """
    File-like object that reads from the PTY bridge.

    This receives input from the client via the socket connection.
    """

    def __init__(self, bridge: PTYBridge) -> None:
        super().__init__()
        self._bridge = bridge
        self._closed = False
        self._buffer = b""

    def read(self, n: int = -1) -> str:
        """Read from bridge (blocking)."""
        raise io.UnsupportedOperation("Use async read_input() instead")

    def readline(self, limit: int = -1) -> str:
        """Read a line (blocking)."""
        raise io.UnsupportedOperation("Use async read_line() instead")

    def isatty(self) -> bool:
        return True

    @property
    def closed(self) -> bool:
        return self._closed

    def readable(self) -> bool:
        return not self._closed

    def writable(self) -> bool:
        return False


# =============================================================================
# PTY Bridge
# =============================================================================


@dataclass
class StreamMessage:
    """A stream message to/from client."""

    type: str  # "output", "input", "resize", "exit", "event"
    correlation_id: str
    seq: int = 0
    data: bytes | None = None
    exit_code: int | None = None
    term_size: tuple[int, int] | None = None
    event: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to wire format."""
        d: dict[str, Any] = {
            "type": self.type,
            "correlation_id": self.correlation_id,
            "seq": self.seq,
        }
        if self.data is not None:
            import base64

            d["data"] = base64.b64encode(self.data).decode("ascii")
        if self.exit_code is not None:
            d["exit_code"] = self.exit_code
        if self.term_size is not None:
            d["term_size"] = list(self.term_size)
        if self.event is not None:
            d["event"] = self.event
        return d

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> StreamMessage:
        """Parse from wire format."""
        data = None
        if "data" in d and d["data"]:
            import base64

            data = base64.b64decode(d["data"])

        term_size = None
        if "term_size" in d and d["term_size"]:
            term_size = tuple(d["term_size"])

        return cls(
            type=d["type"],
            correlation_id=d.get("correlation_id", ""),
            seq=d.get("seq", 0),
            data=data,
            exit_code=d.get("exit_code"),
            term_size=term_size,
            event=d.get("event"),
        )

    @classmethod
    def output(cls, correlation_id: str, data: bytes, seq: int = 0) -> StreamMessage:
        """Create an output message."""
        return cls(type="output", correlation_id=correlation_id, data=data, seq=seq)

    @classmethod
    def exit(cls, correlation_id: str, exit_code: int, seq: int = 0) -> StreamMessage:
        """Create an exit message."""
        return cls(
            type="exit", correlation_id=correlation_id, exit_code=exit_code, seq=seq
        )

    @classmethod
    def event(
        cls, correlation_id: str, event: dict[str, Any], seq: int = 0
    ) -> StreamMessage:
        """Create an event message."""
        return cls(type="event", correlation_id=correlation_id, event=event, seq=seq)


class PTYBridge:
    """
    Bridges daemon handler I/O to client PTY via socket.

    This class enables Tier 2 handlers to run interactively without
    spawning a subprocess. It:

    1. Provides file-like stdout/stderr that send to client
    2. Queues input from client for handler to read
    3. Tracks terminal size for resize handling
    4. Supports structured event messages

    Lifecycle:
        bridge = PTYBridge(reader, writer, correlation_id, term_size)
        await bridge.start()
        try:
            # Handler runs with sys.stdout = bridge.stdout
            ...
        finally:
            await bridge.stop()
            await bridge.send_exit(exit_code)

    Attributes:
        reader: AsyncIO stream reader (from client)
        writer: AsyncIO stream writer (to client)
        correlation_id: Request tracking ID
        rows: Terminal rows
        cols: Terminal columns
    """

    def __init__(
        self,
        reader: asyncio.StreamReader,
        writer: asyncio.StreamWriter,
        correlation_id: str,
        term_size: tuple[int, int] = (24, 80),
    ) -> None:
        self.reader = reader
        self.writer = writer
        self.correlation_id = correlation_id
        self.rows, self.cols = term_size

        self._seq = 0
        self._loop: asyncio.AbstractEventLoop | None = None

        # Create file-like objects
        self._stdout = PTYOutputStream(self, "stdout")
        self._stderr = PTYOutputStream(self, "stderr")
        self._stdin = PTYInputStream(self)

        # Input queue from client
        self._input_queue: asyncio.Queue[bytes] = asyncio.Queue()

        # Background task for reading client messages
        self._reader_task: asyncio.Task[None] | None = None
        self._running = False

        # Lock for writer access
        self._write_lock = asyncio.Lock()

    @property
    def stdout(self) -> TextIO:
        """Get stdout file-like object."""
        return self._stdout  # type: ignore

    @property
    def stderr(self) -> TextIO:
        """Get stderr file-like object."""
        return self._stderr  # type: ignore

    @property
    def stdin(self) -> TextIO:
        """Get stdin file-like object (limited functionality)."""
        return self._stdin  # type: ignore

    async def start(self) -> None:
        """Start the bridge (begins reading client messages)."""
        if self._running:
            return

        self._running = True
        self._loop = asyncio.get_running_loop()

        # Start background reader
        self._reader_task = asyncio.create_task(self._read_client_messages())
        logger.debug(f"PTY bridge started: {self.correlation_id}")

    async def stop(self) -> None:
        """Stop the bridge (stops reading client messages)."""
        self._running = False

        # Cancel reader task
        if self._reader_task is not None:
            self._reader_task.cancel()
            try:
                await self._reader_task
            except asyncio.CancelledError:
                pass
            self._reader_task = None

        # Close streams
        self._stdout.close()
        self._stderr.close()

        logger.debug(f"PTY bridge stopped: {self.correlation_id}")

    async def write_output(self, data: bytes) -> None:
        """
        Send output data to client.

        Args:
            data: Bytes to send (will be displayed in client terminal)
        """
        msg = StreamMessage.output(self.correlation_id, data, self._seq)
        self._seq += 1
        await self._send_message(msg)

    async def write_event(self, event: dict[str, Any]) -> None:
        """
        Send structured event to client.

        Args:
            event: Event data (will be processed by client)
        """
        msg = StreamMessage.event(self.correlation_id, event, self._seq)
        self._seq += 1
        await self._send_message(msg)

    async def send_exit(self, exit_code: int) -> None:
        """
        Send exit message to client.

        Args:
            exit_code: Command exit code
        """
        msg = StreamMessage.exit(self.correlation_id, exit_code, self._seq)
        self._seq += 1
        await self._send_message(msg)

    async def read_input(self, n: int = -1) -> bytes:
        """
        Read input from client (blocking).

        Args:
            n: Number of bytes to read (-1 for any available)

        Returns:
            Bytes from client input
        """
        return await self._input_queue.get()

    async def _read_client_messages(self) -> None:
        """Background task: read messages from client."""
        while self._running:
            try:
                data = await decode_message_async(self.reader)
                if data is None:
                    logger.debug("Client disconnected")
                    break

                msg = StreamMessage.from_dict(data)

                if msg.type == "input" and msg.data is not None:
                    # Queue input for handler
                    await self._input_queue.put(msg.data)

                elif msg.type == "resize" and msg.term_size is not None:
                    # Update terminal size
                    self.rows, self.cols = msg.term_size
                    logger.debug(f"Terminal resized: {self.rows}x{self.cols}")

                # Ignore other message types (exit, etc.)

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.warning(f"Error reading client message: {e}")
                continue

    async def _send_message(self, msg: StreamMessage) -> None:
        """Send a message to the client."""
        async with self._write_lock:
            try:
                data = encode_message(msg.to_dict())
                self.writer.write(data)
                await self.writer.drain()
            except Exception as e:
                logger.warning(f"Error sending message: {e}")


# =============================================================================
# Context Manager
# =============================================================================


class PTYBridgeContext:
    """
    Context manager for PTY bridge with stdout/stderr redirection.

    Usage:
        async with PTYBridgeContext(reader, writer, correlation_id, term_size) as ctx:
            # sys.stdout and sys.stderr are redirected
            print("This goes to client terminal")
            # Access the bridge
            await ctx.bridge.write_event({"type": "progress", ...})

    Attributes:
        bridge: The PTYBridge instance
    """

    def __init__(
        self,
        reader: asyncio.StreamReader,
        writer: asyncio.StreamWriter,
        correlation_id: str,
        term_size: tuple[int, int] = (24, 80),
    ) -> None:
        self.bridge = PTYBridge(reader, writer, correlation_id, term_size)
        self._old_stdout: TextIO | None = None
        self._old_stderr: TextIO | None = None

    async def __aenter__(self) -> PTYBridgeContext:
        """Enter context: start bridge and redirect stdout/stderr."""
        import sys

        await self.bridge.start()

        # Save original streams
        self._old_stdout = sys.stdout
        self._old_stderr = sys.stderr

        # Redirect to bridge
        sys.stdout = self.bridge.stdout
        sys.stderr = self.bridge.stderr

        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Exit context: restore streams and stop bridge."""
        import sys

        # Restore original streams
        if self._old_stdout is not None:
            sys.stdout = self._old_stdout
        if self._old_stderr is not None:
            sys.stderr = self._old_stderr

        # Stop bridge
        await self.bridge.stop()


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    "PTYBridge",
    "PTYBridgeContext",
    "PTYOutputStream",
    "PTYInputStream",
    "StreamMessage",
    "encode_message",
    "decode_message_async",
]
