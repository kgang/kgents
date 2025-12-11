"""
T-gents Phase 4: MCP (Model Context Protocol) Client Implementation

This module implements an MCP client for connecting to MCP servers and
invoking remote tools via the Model Context Protocol.

MCP Spec: https://modelcontextprotocol.io/specification/2025-06-18

Architecture:
- JSON-RPC 2.0 message protocol
- Stdio and HTTP/SSE transport
- Tool discovery and invocation
- Resource management
- OAuth 2.1 authentication support

Integration:
- Tool[A, B]: MCP tools mapped to typed morphisms
- Result monad: Error handling for connection/invocation failures
- P-gents: Parse tool schemas and responses
- W-gents: Trace MCP calls for observability

References:
- spec/t-gents/tool-use.md (Phase 4: MCP Integration)
- MCP Specification 2025-06-18
- JSON-RPC 2.0: https://www.jsonrpc.org/specification
"""

from __future__ import annotations

import asyncio
import json
import subprocess
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, TypeVar, Union

from bootstrap.types import Err, Result, err, ok

from .tool import Tool, ToolError, ToolErrorType, ToolMeta

# Type variables
A = TypeVar("A")
B = TypeVar("B")


# --- JSON-RPC 2.0 Types ---


@dataclass
class JsonRpcRequest:
    """
    JSON-RPC 2.0 request message.

    Spec: https://www.jsonrpc.org/specification#request_object
    """

    jsonrpc: str = "2.0"
    id: Optional[Union[str, int]] = None
    method: str = ""
    params: Dict[str, Any] = field(default_factory=dict)

    def to_json(self) -> str:
        """Serialize to JSON string."""
        data: Dict[str, Any] = {"jsonrpc": self.jsonrpc, "method": self.method}

        if self.id is not None:
            data["id"] = self.id

        # Always include params (even if empty) for requests with IDs
        if self.id is not None or self.params:
            data["params"] = self.params

        return json.dumps(data)


@dataclass
class JsonRpcResponse:
    """
    JSON-RPC 2.0 response message.

    Spec: https://www.jsonrpc.org/specification#response_object
    """

    jsonrpc: str = "2.0"
    id: Optional[Union[str, int]] = None
    result: Optional[Any] = None
    error: Optional[Dict[str, Any]] = None

    @classmethod
    def from_json(cls, data: str) -> JsonRpcResponse:
        """Deserialize from JSON string."""
        parsed = json.loads(data)
        return cls(
            jsonrpc=parsed.get("jsonrpc", "2.0"),
            id=parsed.get("id"),
            result=parsed.get("result"),
            error=parsed.get("error"),
        )

    def is_error(self) -> bool:
        """Check if response is an error."""
        return self.error is not None


@dataclass
class JsonRpcError:
    """
    JSON-RPC 2.0 error object.

    Spec: https://www.jsonrpc.org/specification#error_object
    """

    code: int
    message: str
    data: Optional[Any] = None

    # Standard error codes
    PARSE_ERROR = -32700
    INVALID_REQUEST = -32600
    METHOD_NOT_FOUND = -32601
    INVALID_PARAMS = -32602
    INTERNAL_ERROR = -32603


# --- MCP Protocol Types ---


class MCPTransportType(Enum):
    """
    MCP transport types.

    MCP supports two transport mechanisms:
    - STDIO: Local process communication via stdin/stdout
    - HTTP_SSE: Remote communication via HTTP POST + Server-Sent Events
    """

    STDIO = "stdio"
    HTTP_SSE = "http_sse"


@dataclass
class MCPServerInfo:
    """
    Information about an MCP server.

    Returned from initialize handshake.
    """

    name: str
    version: str
    protocol_version: str = "2025-06-18"
    capabilities: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MCPToolSchema:
    """
    Tool schema from MCP server.

    Maps to Tool[A, B] metadata for kgents integration.
    """

    name: str
    description: str
    input_schema: Dict[str, Any]  # JSON Schema


@dataclass
class MCPResource:
    """
    Resource exposed by MCP server.

    Resources represent data sources (files, URLs, etc.) that tools can access.
    """

    uri: str
    name: str
    description: Optional[str] = None
    mime_type: Optional[str] = None


# --- Transport Layer ---


class MCPTransport(ABC):
    """
    Abstract base for MCP transport implementations.

    MCP supports two transports:
    1. Stdio: Local process communication
    2. HTTP/SSE: Remote communication
    """

    @abstractmethod
    async def send(self, request: JsonRpcRequest) -> None:
        """Send JSON-RPC request to server."""
        pass

    @abstractmethod
    async def receive(self) -> JsonRpcResponse:
        """Receive JSON-RPC response from server."""
        pass

    @abstractmethod
    async def close(self) -> None:
        """Close transport connection."""
        pass


class StdioTransport(MCPTransport):
    """
    Stdio transport for local MCP servers.

    Spawns server process and communicates via stdin/stdout.
    Most common transport for MCP.

    Usage:
        transport = StdioTransport(command=["python", "server.py"])
        await transport.connect()
        await transport.send(request)
        response = await transport.receive()
        await transport.close()
    """

    def __init__(self, command: List[str]):
        """
        Initialize stdio transport.

        Args:
            command: Command to spawn server process (e.g., ["python", "server.py"])
        """
        self.command = command
        self.process: Optional[asyncio.subprocess.Process] = None
        self._response_queue: asyncio.Queue[JsonRpcResponse] = asyncio.Queue()
        self._reader_task: Optional[asyncio.Task[None]] = None

    async def connect(self) -> None:
        """Spawn server process and start reading responses."""
        self.process = await asyncio.create_subprocess_exec(
            *self.command,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        # Start background task to read responses
        self._reader_task = asyncio.create_task(self._read_responses())

    async def _read_responses(self) -> None:
        """Background task to read line-delimited JSON-RPC responses."""
        if not self.process or not self.process.stdout:
            return

        while True:
            try:
                line = await self.process.stdout.readline()
                if not line:
                    break  # EOF

                response = JsonRpcResponse.from_json(line.decode("utf-8"))
                await self._response_queue.put(response)
            except json.JSONDecodeError as e:
                # Invalid JSON - log and continue
                print(f"Invalid JSON from server: {e}")
                continue
            except Exception as e:
                print(f"Error reading response: {e}")
                break

    async def send(self, request: JsonRpcRequest) -> None:
        """Send JSON-RPC request via stdin."""
        if not self.process or not self.process.stdin:
            raise RuntimeError("Transport not connected")

        # Send line-delimited JSON
        message = request.to_json() + "\n"
        self.process.stdin.write(message.encode("utf-8"))
        await self.process.stdin.drain()

    async def receive(self) -> JsonRpcResponse:
        """Receive JSON-RPC response from stdout."""
        response: JsonRpcResponse = await self._response_queue.get()
        return response

    async def close(self) -> None:
        """Close connection and terminate process."""
        if self.process:
            # Send shutdown notification
            shutdown = JsonRpcRequest(method="notifications/shutdown", params={})
            try:
                await self.send(shutdown)
            except Exception:
                pass  # Best effort

            # Terminate process
            self.process.terminate()
            await self.process.wait()

        if self._reader_task:
            self._reader_task.cancel()
            try:
                await self._reader_task
            except asyncio.CancelledError:
                pass


class HttpSseTransport(MCPTransport):
    """
    HTTP/SSE transport for remote MCP servers.

    Uses HTTP POST for requests and Server-Sent Events for server→client messages.
    Enables stateful connections over HTTP.

    NOTE: This is a placeholder implementation. Full HTTP/SSE support requires:
    - aiohttp or httpx for async HTTP
    - SSE stream parsing
    - Connection management
    """

    def __init__(self, base_url: str, auth_token: Optional[str] = None):
        """
        Initialize HTTP/SSE transport.

        Args:
            base_url: MCP server base URL (e.g., "https://api.example.com/mcp")
            auth_token: Optional OAuth bearer token
        """
        self.base_url = base_url
        self.auth_token = auth_token
        # TODO: Initialize HTTP client (aiohttp/httpx)

    async def send(self, request: JsonRpcRequest) -> None:
        """Send JSON-RPC request via HTTP POST."""
        # TODO: Implement HTTP POST
        raise NotImplementedError("HTTP/SSE transport not yet implemented")

    async def receive(self) -> JsonRpcResponse:
        """Receive JSON-RPC response via SSE stream."""
        # TODO: Implement SSE stream reading
        raise NotImplementedError("HTTP/SSE transport not yet implemented")

    async def close(self) -> None:
        """Close HTTP connection."""
        # TODO: Close HTTP client
        pass


# --- MCP Client ---


class MCPClient:
    """
    Model Context Protocol (MCP) client.

    Implements MCP protocol for connecting to servers, discovering tools,
    and invoking remote tools.

    Protocol Flow:
    1. Connect: Establish transport (stdio or HTTP/SSE)
    2. Initialize: Exchange capabilities via initialize/initialized handshake
    3. Discover: List tools, resources, prompts
    4. Invoke: Call tools with JSON-RPC
    5. Shutdown: Clean disconnect

    Usage:
        # Connect to local server
        client = MCPClient(StdioTransport(["python", "server.py"]))
        await client.connect()

        # Discover tools
        tools = await client.list_tools()

        # Invoke tool
        result = await client.call_tool("web_search", {"query": "MCP protocol"})

        # Cleanup
        await client.disconnect()

    Integration with kgents:
        # Convert MCP tools to Tool[A, B]
        mcp_tools = await client.list_tools()
        kgents_tools = [MCPTool.from_schema(schema, client) for schema in mcp_tools]

        # Register in ToolRegistry
        registry = ToolRegistry()
        for tool in kgents_tools:
            await registry.register(tool)
    """

    def __init__(self, transport: MCPTransport):
        """
        Initialize MCP client.

        Args:
            transport: Transport implementation (stdio or HTTP/SSE)
        """
        self.transport = transport
        self.server_info: Optional[MCPServerInfo] = None
        self._request_id_counter = 0
        self._pending_requests: Dict[Union[str, int], asyncio.Future[Any]] = {}

    def _next_request_id(self) -> int:
        """Generate unique request ID."""
        self._request_id_counter += 1
        return self._request_id_counter

    async def connect(self) -> Result[MCPServerInfo, ToolError]:
        """
        Connect to MCP server and complete initialize handshake.

        Returns:
            Result[MCPServerInfo, ToolError]: Server info or connection error
        """
        try:
            # 1. Establish transport
            if isinstance(self.transport, StdioTransport):
                await self.transport.connect()

            # 2. Send initialize request
            init_request = JsonRpcRequest(
                id=self._next_request_id(),
                method="initialize",
                params={
                    "protocolVersion": "2025-06-18",
                    "capabilities": {
                        "roots": {},  # Client can provide filesystem roots
                        "sampling": {},  # Client can invoke LLM
                    },
                    "clientInfo": {"name": "kgents", "version": "0.1.0"},
                },
            )

            await self.transport.send(init_request)

            # 3. Receive initialize response
            init_response = await asyncio.wait_for(
                self.transport.receive(), timeout=10.0
            )

            if init_response.is_error():
                error = init_response.error or {}
                return err(
                    ToolError(
                        error_type=ToolErrorType.FATAL,
                        message=f"Initialize failed: {error.get('message', 'Unknown error')}",
                        tool_name="MCPClient",
                        recoverable=False,
                    ),
                    message=error.get("message", "Initialize failed"),
                    recoverable=False,
                )

            # Parse server info
            result_data = init_response.result or {}
            self.server_info = MCPServerInfo(
                name=result_data.get("serverInfo", {}).get("name", "unknown"),
                version=result_data.get("serverInfo", {}).get("version", "0.0.0"),
                protocol_version=result_data.get("protocolVersion", "2025-06-18"),
                capabilities=result_data.get("capabilities", {}),
            )

            # 4. Send initialized notification
            initialized_notification = JsonRpcRequest(
                method="notifications/initialized", params={}
            )
            await self.transport.send(initialized_notification)

            return ok(self.server_info)

        except asyncio.TimeoutError:
            return err(
                ToolError(
                    error_type=ToolErrorType.TIMEOUT,
                    message="Connection timeout during initialize",
                    tool_name="MCPClient",
                    recoverable=True,
                ),
                message="Connection timeout",
                recoverable=True,
            )
        except Exception as e:
            return err(
                ToolError(
                    error_type=ToolErrorType.NETWORK,
                    message=f"Connection error: {str(e)}",
                    tool_name="MCPClient",
                    recoverable=True,
                ),
                message=str(e),
                recoverable=True,
            )

    async def list_tools(self) -> Result[List[MCPToolSchema], ToolError]:
        """
        List all tools available on the MCP server.

        Returns:
            Result[List[MCPToolSchema], ToolError]: Tool schemas or error
        """
        if not self.server_info:
            return err(
                ToolError(
                    error_type=ToolErrorType.FATAL,
                    message="Client not connected",
                    tool_name="MCPClient",
                    recoverable=False,
                ),
                message="Not connected",
                recoverable=False,
            )

        try:
            request = JsonRpcRequest(
                id=self._next_request_id(), method="tools/list", params={}
            )

            await self.transport.send(request)
            response = await asyncio.wait_for(self.transport.receive(), timeout=10.0)

            if response.is_error():
                error = response.error or {}
                return err(
                    ToolError(
                        error_type=ToolErrorType.FATAL,
                        message=f"List tools failed: {error.get('message')}",
                        tool_name="MCPClient",
                        recoverable=False,
                    ),
                    message=error.get("message", "List tools failed"),
                    recoverable=False,
                )

            # Parse tool schemas
            result_data = response.result or {}
            tools_data = result_data.get("tools", [])

            tools = [
                MCPToolSchema(
                    name=tool.get("name", ""),
                    description=tool.get("description", ""),
                    input_schema=tool.get("inputSchema", {}),
                )
                for tool in tools_data
            ]

            return ok(tools)

        except asyncio.TimeoutError:
            return err(
                ToolError(
                    error_type=ToolErrorType.TIMEOUT,
                    message="Timeout listing tools",
                    tool_name="MCPClient",
                    recoverable=True,
                ),
                message="Timeout",
                recoverable=True,
            )
        except Exception as e:
            return err(
                ToolError(
                    error_type=ToolErrorType.NETWORK,
                    message=f"Error listing tools: {str(e)}",
                    tool_name="MCPClient",
                    recoverable=True,
                ),
                message=str(e),
                recoverable=True,
            )

    async def call_tool(
        self, tool_name: str, arguments: Dict[str, Any]
    ) -> Result[Any, ToolError]:
        """
        Call a tool on the MCP server.

        Args:
            tool_name: Name of tool to invoke
            arguments: Tool input arguments (JSON-serializable dict)

        Returns:
            Result[Any, ToolError]: Tool output or error
        """
        if not self.server_info:
            return err(
                ToolError(
                    error_type=ToolErrorType.FATAL,
                    message="Client not connected",
                    tool_name=tool_name,
                    recoverable=False,
                ),
                message="Not connected",
                recoverable=False,
            )

        try:
            request = JsonRpcRequest(
                id=self._next_request_id(),
                method="tools/call",
                params={"name": tool_name, "arguments": arguments},
            )

            await self.transport.send(request)
            response = await asyncio.wait_for(self.transport.receive(), timeout=30.0)

            if response.is_error():
                error = response.error or {}
                error_code = error.get("code", -1)

                # Map JSON-RPC error codes to ToolErrorType
                if error_code == JsonRpcError.METHOD_NOT_FOUND:
                    error_type = ToolErrorType.NOT_FOUND
                elif error_code == JsonRpcError.INVALID_PARAMS:
                    error_type = ToolErrorType.VALIDATION
                else:
                    error_type = ToolErrorType.FATAL

                return err(
                    ToolError(
                        error_type=error_type,
                        message=error.get("message", "Tool call failed"),
                        tool_name=tool_name,
                        input=arguments,
                        recoverable=False,
                    ),
                    message=error.get("message", "Tool call failed"),
                    recoverable=False,
                )

            # Extract content from result
            result_data = response.result or {}
            content = result_data.get("content", [])

            # MCP tools return content as list of content blocks
            # For now, extract first text block
            if content and isinstance(content, list) and len(content) > 0:
                first_block = content[0]
                if first_block.get("type") == "text":
                    return ok(first_block.get("text"))

            # Return full result if no text content
            return ok(result_data)

        except asyncio.TimeoutError:
            return err(
                ToolError(
                    error_type=ToolErrorType.TIMEOUT,
                    message="Tool call timeout",
                    tool_name=tool_name,
                    input=arguments,
                    recoverable=True,
                    retry_after_ms=1000,
                ),
                message="Timeout",
                recoverable=True,
            )
        except Exception as e:
            return err(
                ToolError(
                    error_type=ToolErrorType.NETWORK,
                    message=f"Tool call error: {str(e)}",
                    tool_name=tool_name,
                    input=arguments,
                    recoverable=True,
                ),
                message=str(e),
                recoverable=True,
            )

    async def list_resources(self) -> Result[List[MCPResource], ToolError]:
        """
        List all resources available on the MCP server.

        Resources represent data sources (files, URLs, etc.) that tools can access.

        Returns:
            Result[List[MCPResource], ToolError]: Resource list or error
        """
        if not self.server_info:
            return err(
                ToolError(
                    error_type=ToolErrorType.FATAL,
                    message="Client not connected",
                    tool_name="MCPClient",
                    recoverable=False,
                ),
                message="Not connected",
                recoverable=False,
            )

        try:
            request = JsonRpcRequest(
                id=self._next_request_id(), method="resources/list", params={}
            )

            await self.transport.send(request)
            response = await asyncio.wait_for(self.transport.receive(), timeout=10.0)

            if response.is_error():
                error = response.error or {}
                return err(
                    ToolError(
                        error_type=ToolErrorType.FATAL,
                        message=f"List resources failed: {error.get('message')}",
                        tool_name="MCPClient",
                        recoverable=False,
                    ),
                    message=error.get("message", "List resources failed"),
                    recoverable=False,
                )

            # Parse resources
            result_data = response.result or {}
            resources_data = result_data.get("resources", [])

            resources = [
                MCPResource(
                    uri=res.get("uri", ""),
                    name=res.get("name", ""),
                    description=res.get("description"),
                    mime_type=res.get("mimeType"),
                )
                for res in resources_data
            ]

            return ok(resources)

        except asyncio.TimeoutError:
            return err(
                ToolError(
                    error_type=ToolErrorType.TIMEOUT,
                    message="Timeout listing resources",
                    tool_name="MCPClient",
                    recoverable=True,
                ),
                message="Timeout",
                recoverable=True,
            )
        except Exception as e:
            return err(
                ToolError(
                    error_type=ToolErrorType.NETWORK,
                    message=f"Error listing resources: {str(e)}",
                    tool_name="MCPClient",
                    recoverable=True,
                ),
                message=str(e),
                recoverable=True,
            )

    async def disconnect(self) -> None:
        """Disconnect from MCP server."""
        await self.transport.close()
        self.server_info = None


# --- MCPTool: Bridge between MCP and Tool[A, B] ---


class MCPTool(Tool[Dict[str, Any], Any]):
    """
    Tool[A, B] implementation for MCP remote tools.

    Bridges MCP protocol tools to kgents Tool[A, B] abstraction.
    Enables categorical composition with MCP tools:

        mcp_tool = MCPTool.from_schema(schema, client)
        pipeline = parse_input >> mcp_tool >> format_output

    NOTE: Currently uses Dict[str, Any] for input/output since we don't have
    the actual Python types. P-gents will parse these at runtime.
    """

    def __init__(self, schema: MCPToolSchema, client: MCPClient):
        """
        Initialize MCP tool.

        Args:
            schema: Tool schema from MCP server
            client: Connected MCP client
        """
        self.client = client
        self.schema = schema

        # Create metadata
        self.meta = ToolMeta.minimal(
            name=schema.name,
            description=schema.description,
            input_schema=Dict[str, Any],  # Generic dict for now
            output_schema=Any,  # Generic output for now
        )

        # Add MCP server info
        if client.server_info:
            self.meta.identity.server = client.server_info.name
            self.meta.identity.version = client.server_info.version

    @classmethod
    def from_schema(cls, schema: MCPToolSchema, client: MCPClient) -> MCPTool:
        """Create MCPTool from schema."""
        return cls(schema, client)

    async def invoke(self, input: Dict[str, Any]) -> Any:
        """
        Invoke MCP tool with input arguments.

        Uses Result monad for error handling.
        P-gents will parse the result downstream.
        """
        result = await self.client.call_tool(self.schema.name, input)

        # Unwrap Result - raise ToolError if failed
        # (Agent[A, B] expects exceptions, not Result directly)
        if result.is_err():
            # Type narrowing - result must be Err[ToolError]
            assert isinstance(result, Err)
            raise result.error

        return result.unwrap()
