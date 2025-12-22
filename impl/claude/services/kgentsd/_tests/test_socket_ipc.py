"""
Tests for Unix Socket IPC.

Covers:
- Wire format (length-prefixed JSON) encoding/decoding
- CLIRequest/CLIResponse serialization
- Socket server lifecycle
- Command execution through socket
- Error handling and edge cases
"""

from __future__ import annotations

import asyncio
import json
import struct
import tempfile
import uuid
from pathlib import Path
from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest

from services.kgentsd.socket_client import (
    SAFE_ENV_VARS,
    DaemonConnectionError,
    DaemonNotRunningError,
    DaemonProtocolError,
    DaemonTimeoutError,
    _filter_env,
    is_daemon_available,
)
from services.kgentsd.socket_server import (
    CLIRequest,
    CLIResponse,
    CLISocketServer,
    decode_message,
    encode_message,
    encode_message_sync,
)

# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def short_socket_path(tmp_path: Path) -> Path:
    """Create a short socket path for Unix socket tests.

    Unix sockets have a path length limit (~108 bytes on macOS).
    pytest's tmp_path can be too long, so we use /tmp directly.
    """
    import os
    import random
    import string

    # Generate a short random name
    suffix = "".join(random.choices(string.ascii_lowercase, k=8))
    socket_path = Path(f"/tmp/kg_test_{suffix}.sock")

    yield socket_path

    # Cleanup
    if socket_path.exists():
        try:
            socket_path.unlink()
        except OSError:
            pass


# =============================================================================
# Wire Protocol Tests
# =============================================================================


class TestWireProtocol:
    """Tests for length-prefixed JSON wire format."""

    def test_encode_simple_message(self) -> None:
        """Encode a simple message."""
        data = {"command": "brain", "args": ["capture", "hello"]}
        encoded = encode_message(data)

        # Should start with 4-byte length prefix
        assert len(encoded) >= 4

        # Extract length
        length = struct.unpack(">I", encoded[:4])[0]
        payload = encoded[4:]

        assert len(payload) == length
        assert json.loads(payload.decode("utf-8")) == data

    def test_encode_empty_message(self) -> None:
        """Encode an empty dict."""
        data: dict[str, Any] = {}
        encoded = encode_message(data)

        length = struct.unpack(">I", encoded[:4])[0]
        payload = encoded[4:]

        assert json.loads(payload.decode("utf-8")) == {}

    def test_encode_unicode_message(self) -> None:
        """Encode message with unicode characters."""
        data = {"content": "Hello, world! Greeting in other languages."}
        encoded = encode_message(data)

        length = struct.unpack(">I", encoded[:4])[0]
        payload = encoded[4:]

        decoded = json.loads(payload.decode("utf-8"))
        assert decoded["content"] == data["content"]

    def test_encode_large_message(self) -> None:
        """Encode a large message."""
        data = {"content": "x" * 100000}  # 100KB of data
        encoded = encode_message(data)

        length = struct.unpack(">I", encoded[:4])[0]
        payload = encoded[4:]

        assert len(payload) == length
        assert json.loads(payload.decode("utf-8")) == data

    @pytest.mark.asyncio
    async def test_decode_simple_message(self) -> None:
        """Decode a simple message."""
        data = {"command": "brain", "args": ["capture"]}
        encoded = encode_message(data)

        reader = asyncio.StreamReader()
        reader.feed_data(encoded)
        reader.feed_eof()

        decoded = await decode_message(reader)
        assert decoded == data

    @pytest.mark.asyncio
    async def test_decode_roundtrip(self) -> None:
        """Encode and decode should be inverses."""
        original = {
            "command": "soul",
            "args": ["reflect"],
            "cwd": "/home/user",
            "env": {"HOME": "/home/user"},
            "flags": {"format": "json", "budget": "high"},
            "correlation_id": str(uuid.uuid4()),
        }

        encoded = encode_message(original)

        reader = asyncio.StreamReader()
        reader.feed_data(encoded)
        reader.feed_eof()

        decoded = await decode_message(reader)
        assert decoded == original


# =============================================================================
# CLIRequest/CLIResponse Tests
# =============================================================================


class TestCLIRequest:
    """Tests for CLIRequest dataclass."""

    def test_create_request(self) -> None:
        """Create a simple request."""
        request = CLIRequest(
            command="brain",
            args=["capture", "hello"],
            cwd="/home/user/project",
            env={"HOME": "/home/user"},
            flags={"format": "json"},
        )

        assert request.command == "brain"
        assert request.args == ["capture", "hello"]
        assert request.cwd == "/home/user/project"
        assert request.correlation_id  # Auto-generated

    def test_request_from_dict(self) -> None:
        """Deserialize request from dict."""
        data = {
            "command": "soul",
            "args": ["reflect"],
            "cwd": "/tmp",
            "env": {},
            "flags": {},
            "correlation_id": "test-123",
        }

        request = CLIRequest.from_dict(data)

        assert request.command == "soul"
        assert request.args == ["reflect"]
        assert request.correlation_id == "test-123"

    def test_request_to_dict(self) -> None:
        """Serialize request to dict."""
        request = CLIRequest(
            command="brain",
            args=["list"],
            cwd="/home",
            env={},
            flags={},
            correlation_id="abc-123",
        )

        data = request.to_dict()

        assert data["command"] == "brain"
        assert data["args"] == ["list"]
        assert data["correlation_id"] == "abc-123"

    def test_request_roundtrip(self) -> None:
        """Request -> dict -> Request should preserve data."""
        original = CLIRequest(
            command="town",
            args=["inhabit", "alice"],
            cwd="/project",
            env={"USER": "test"},
            flags={"verbose": True},
            correlation_id="xyz-789",
        )

        data = original.to_dict()
        restored = CLIRequest.from_dict(data)

        assert restored.command == original.command
        assert restored.args == original.args
        assert restored.cwd == original.cwd
        assert restored.env == original.env
        assert restored.flags == original.flags
        assert restored.correlation_id == original.correlation_id


class TestCLIResponse:
    """Tests for CLIResponse dataclass."""

    def test_create_response(self) -> None:
        """Create a simple response."""
        response = CLIResponse(
            correlation_id="test-123",
            exit_code=0,
            stdout="Hello, world!\n",
            stderr="",
        )

        assert response.exit_code == 0
        assert response.stdout == "Hello, world!\n"
        assert response.semantic is None

    def test_error_response(self) -> None:
        """Create an error response."""
        response = CLIResponse.error(
            correlation_id="test-456",
            message="Command not found",
            exit_code=127,
        )

        assert response.exit_code == 127
        assert response.stderr == "Command not found"
        assert response.stdout == ""

    def test_response_roundtrip(self) -> None:
        """Response -> dict -> Response should preserve data."""
        original = CLIResponse(
            correlation_id="abc",
            exit_code=0,
            stdout="output",
            stderr="warnings",
            semantic={"key": "value"},
            duration_ms=150,
        )

        data = original.to_dict()
        restored = CLIResponse.from_dict(data)

        assert restored.correlation_id == original.correlation_id
        assert restored.exit_code == original.exit_code
        assert restored.stdout == original.stdout
        assert restored.stderr == original.stderr
        assert restored.semantic == original.semantic
        assert restored.duration_ms == original.duration_ms


# =============================================================================
# Environment Filtering Tests
# =============================================================================


class TestEnvironmentFiltering:
    """Tests for environment variable filtering."""

    def test_filter_safe_vars(self) -> None:
        """Filter keeps safe variables."""
        env = {
            "HOME": "/home/user",
            "PATH": "/usr/bin",
            "KGENTS_DEBUG": "1",
            "SECRET_KEY": "don't leak this",
            "AWS_SECRET_ACCESS_KEY": "also secret",
        }

        filtered = _filter_env(env)

        assert "HOME" in filtered
        assert "PATH" in filtered
        assert "KGENTS_DEBUG" in filtered
        assert "SECRET_KEY" not in filtered
        assert "AWS_SECRET_ACCESS_KEY" not in filtered

    def test_filter_empty_env(self) -> None:
        """Filter handles empty env."""
        assert _filter_env({}) == {}

    def test_safe_vars_constant(self) -> None:
        """SAFE_ENV_VARS contains expected variables."""
        assert "HOME" in SAFE_ENV_VARS
        assert "PATH" in SAFE_ENV_VARS
        assert "KGENTS_FD3" in SAFE_ENV_VARS
        assert "KGENTS_DATABASE_URL" in SAFE_ENV_VARS


# =============================================================================
# Socket Client Tests
# =============================================================================


class TestSocketClient:
    """Tests for socket client functions."""

    def test_daemon_not_available_no_socket(self, tmp_path: Path) -> None:
        """is_daemon_available returns False if socket doesn't exist."""
        nonexistent = tmp_path / "nonexistent.sock"
        assert is_daemon_available(nonexistent) is False

    def test_daemon_not_available_wrong_file(self, tmp_path: Path) -> None:
        """is_daemon_available returns False if path is a regular file."""
        regular_file = tmp_path / "not_a_socket"
        regular_file.write_text("not a socket")
        assert is_daemon_available(regular_file) is False


# =============================================================================
# Socket Server Tests
# =============================================================================


class TestSocketServer:
    """Tests for CLISocketServer."""

    @pytest.mark.asyncio
    async def test_server_lifecycle(self, short_socket_path: Path) -> None:
        """Server can start and stop cleanly."""
        socket_path = short_socket_path

        # Create mock executor
        mock_executor = MagicMock()
        mock_executor.execute = AsyncMock(
            return_value=CLIResponse(
                correlation_id="test",
                exit_code=0,
                stdout="OK",
                stderr="",
            )
        )

        server = CLISocketServer(
            socket_path=socket_path,
            command_executor=mock_executor,
        )

        # Start server
        await server.start()
        assert server.is_running
        assert socket_path.exists()

        # Stop server
        await server.stop()
        assert not server.is_running
        assert not socket_path.exists()

    @pytest.mark.asyncio
    async def test_server_handles_request(self, short_socket_path: Path) -> None:
        """Server handles a request and returns response."""
        socket_path = short_socket_path

        # Create mock executor
        mock_executor = MagicMock()
        mock_executor.execute = AsyncMock(
            return_value=CLIResponse(
                correlation_id="test-123",
                exit_code=0,
                stdout="Hello from server",
                stderr="",
            )
        )

        server = CLISocketServer(
            socket_path=socket_path,
            command_executor=mock_executor,
        )

        await server.start()

        try:
            # Connect as client
            reader, writer = await asyncio.open_unix_connection(str(socket_path))

            # Send request
            request = CLIRequest(
                command="brain",
                args=["capture", "test"],
                cwd="/tmp",
                env={},
                flags={},
                correlation_id="test-123",
            )
            writer.write(encode_message(request.to_dict()))
            await writer.drain()

            # Read response
            response_data = await decode_message(reader)
            response = CLIResponse.from_dict(response_data)

            assert response.exit_code == 0
            assert response.stdout == "Hello from server"
            assert response.correlation_id == "test-123"

            writer.close()
            await writer.wait_closed()

        finally:
            await server.stop()

    @pytest.mark.asyncio
    async def test_server_handles_multiple_connections(self, short_socket_path: Path) -> None:
        """Server handles multiple concurrent connections."""
        socket_path = short_socket_path

        # Counter for tracking calls
        call_count = 0

        async def mock_execute(request: CLIRequest) -> CLIResponse:
            nonlocal call_count
            call_count += 1
            await asyncio.sleep(0.01)  # Simulate some work
            return CLIResponse(
                correlation_id=request.correlation_id,
                exit_code=0,
                stdout=f"Response {call_count}",
                stderr="",
            )

        mock_executor = MagicMock()
        mock_executor.execute = mock_execute

        server = CLISocketServer(
            socket_path=socket_path,
            command_executor=mock_executor,
        )

        await server.start()

        try:
            # Create 3 concurrent connections
            async def make_request(n: int) -> CLIResponse:
                reader, writer = await asyncio.open_unix_connection(str(socket_path))

                request = CLIRequest(
                    command="brain",
                    args=[str(n)],
                    cwd="/tmp",
                    env={},
                    flags={},
                    correlation_id=f"req-{n}",
                )
                writer.write(encode_message(request.to_dict()))
                await writer.drain()

                response_data = await decode_message(reader)
                response = CLIResponse.from_dict(response_data)

                writer.close()
                await writer.wait_closed()

                return response

            # Run all requests concurrently
            responses = await asyncio.gather(
                make_request(1),
                make_request(2),
                make_request(3),
            )

            # All should succeed
            assert all(r.exit_code == 0 for r in responses)
            assert call_count == 3

        finally:
            await server.stop()

    @pytest.mark.asyncio
    async def test_server_handles_invalid_request(self, short_socket_path: Path) -> None:
        """Server returns error for invalid request format."""
        socket_path = short_socket_path

        mock_executor = MagicMock()
        mock_executor.execute = AsyncMock()

        server = CLISocketServer(
            socket_path=socket_path,
            command_executor=mock_executor,
        )

        await server.start()

        try:
            reader, writer = await asyncio.open_unix_connection(str(socket_path))

            # Send invalid request (missing required fields)
            invalid_data = {"not_a_command": "oops"}
            writer.write(encode_message(invalid_data))
            await writer.drain()

            # Should get error response
            response_data = await decode_message(reader)
            response = CLIResponse.from_dict(response_data)

            assert response.exit_code == 1
            assert "Invalid request format" in response.stderr

            writer.close()
            await writer.wait_closed()

        finally:
            await server.stop()


# =============================================================================
# Integration Tests
# =============================================================================


class TestEndToEndRouting:
    """End-to-end tests for CLI -> socket -> daemon -> response."""

    @pytest.mark.asyncio
    async def test_full_roundtrip(self, short_socket_path: Path) -> None:
        """Full roundtrip through socket server."""
        socket_path = short_socket_path

        # Create executor that echoes the command
        async def echo_execute(request: CLIRequest) -> CLIResponse:
            return CLIResponse(
                correlation_id=request.correlation_id,
                exit_code=0,
                stdout=f"Executed: {request.command} {' '.join(request.args)}",
                stderr="",
            )

        mock_executor = MagicMock()
        mock_executor.execute = echo_execute

        server = CLISocketServer(
            socket_path=socket_path,
            command_executor=mock_executor,
        )

        await server.start()

        try:
            # Connect and send request
            reader, writer = await asyncio.open_unix_connection(str(socket_path))

            request = CLIRequest(
                command="brain",
                args=["capture", "Hello, World!"],
                cwd="/home/user",
                env={"HOME": "/home/user"},
                flags={"format": "json"},
            )

            writer.write(encode_message(request.to_dict()))
            await writer.drain()

            response_data = await decode_message(reader)
            response = CLIResponse.from_dict(response_data)

            assert response.exit_code == 0
            assert "brain" in response.stdout
            assert "Hello, World!" in response.stdout

            writer.close()
            await writer.wait_closed()

        finally:
            await server.stop()
