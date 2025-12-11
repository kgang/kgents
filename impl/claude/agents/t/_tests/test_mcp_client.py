"""
Tests for T-gents Phase 4: MCP Client Implementation

Test Coverage:
1. JSON-RPC 2.0 message serialization/deserialization
2. Stdio transport (process spawn, communication, cleanup)
3. MCP client lifecycle (connect, initialize, disconnect)
4. Tool discovery (list_tools)
5. Tool invocation (call_tool)
6. Resource management (list_resources)
7. Error handling (timeouts, connection errors, tool errors)
8. MCPTool integration with Tool[A, B]
9. Result monad error handling
10. Mock server testing patterns
"""

import asyncio
import json
from unittest.mock import AsyncMock

import pytest
from agents.t.mcp_client import (
    HttpSseTransport,
    JsonRpcError,
    JsonRpcRequest,
    JsonRpcResponse,
    MCPClient,
    MCPServerInfo,
    MCPTool,
    MCPToolSchema,
    StdioTransport,
)
from agents.t.tool import ToolError, ToolErrorType

# --- JSON-RPC Tests ---


def test_jsonrpc_request_serialization() -> None:
    """Test JSON-RPC request serialization to JSON."""
    request = JsonRpcRequest(id=1, method="tools/list", params={})

    json_str = request.to_json()
    data = json.loads(json_str)

    assert data["jsonrpc"] == "2.0"
    assert data["id"] == 1
    assert data["method"] == "tools/list"
    assert data["params"] == {}


def test_jsonrpc_request_notification() -> None:
    """Test JSON-RPC notification (no id) serialization."""
    request = JsonRpcRequest(method="notifications/initialized", params={})

    json_str = request.to_json()
    data = json.loads(json_str)

    assert data["jsonrpc"] == "2.0"
    assert "id" not in data  # Notifications have no id
    assert data["method"] == "notifications/initialized"


def test_jsonrpc_response_deserialization_success() -> None:
    """Test JSON-RPC success response deserialization."""
    json_str = json.dumps({"jsonrpc": "2.0", "id": 1, "result": {"tools": []}})

    response = JsonRpcResponse.from_json(json_str)

    assert response.jsonrpc == "2.0"
    assert response.id == 1
    assert response.result == {"tools": []}
    assert response.error is None
    assert not response.is_error()


def test_jsonrpc_response_deserialization_error() -> None:
    """Test JSON-RPC error response deserialization."""
    json_str = json.dumps(
        {
            "jsonrpc": "2.0",
            "id": 1,
            "error": {"code": -32601, "message": "Method not found"},
        }
    )

    response = JsonRpcResponse.from_json(json_str)

    assert response.jsonrpc == "2.0"
    assert response.id == 1
    assert response.result is None
    assert response.error == {"code": -32601, "message": "Method not found"}
    assert response.is_error()


def test_jsonrpc_error_codes() -> None:
    """Test JSON-RPC standard error codes."""
    assert JsonRpcError.PARSE_ERROR == -32700
    assert JsonRpcError.INVALID_REQUEST == -32600
    assert JsonRpcError.METHOD_NOT_FOUND == -32601
    assert JsonRpcError.INVALID_PARAMS == -32602
    assert JsonRpcError.INTERNAL_ERROR == -32603


# --- Stdio Transport Tests ---


@pytest.mark.asyncio
async def test_stdio_transport_initialization() -> None:
    """Test stdio transport initialization."""
    transport = StdioTransport(command=["echo", "test"])

    assert transport.command == ["echo", "test"]
    assert transport.process is None
    assert transport._reader_task is None


@pytest.mark.asyncio
async def test_stdio_transport_connect() -> None:
    """Test stdio transport process spawn."""
    # Use echo command that terminates immediately
    transport = StdioTransport(command=["echo", "test"])

    await transport.connect()

    assert transport.process is not None
    assert transport.process.stdin is not None
    assert transport.process.stdout is not None
    assert transport._reader_task is not None

    await transport.close()


@pytest.mark.asyncio
@pytest.mark.skip(reason="Test hangs with cat - needs mock server implementation")
async def test_stdio_transport_send_receive() -> None:
    """Test stdio transport send/receive with mock process."""
    transport = StdioTransport(command=["cat"])

    # Mock process
    mock_process = AsyncMock()
    mock_process.stdin = AsyncMock()
    mock_process.stdout = AsyncMock()

    # Mock stdout to return a response
    mock_response = (
        json.dumps({"jsonrpc": "2.0", "id": 1, "result": {"status": "ok"}}) + "\n"
    )
    mock_process.stdout.readline = AsyncMock(return_value=mock_response.encode())

    transport.process = mock_process

    # Start reader task
    transport._reader_task = asyncio.create_task(transport._read_responses())

    # Send request
    request = JsonRpcRequest(id=1, method="test", params={})
    await transport.send(request)

    # Verify stdin write
    mock_process.stdin.write.assert_called_once()
    written_data = mock_process.stdin.write.call_args[0][0].decode()
    assert "test" in written_data

    # Receive response
    response = await asyncio.wait_for(transport.receive(), timeout=1.0)

    assert response.id == 1
    assert response.result == {"status": "ok"}

    transport._reader_task.cancel()


@pytest.mark.asyncio
@pytest.mark.skip(reason="Test hangs with cat - needs mock server implementation")
async def test_stdio_transport_close() -> None:
    """Test stdio transport cleanup."""
    transport = StdioTransport(command=["cat"])
    await transport.connect()

    assert transport.process is not None
    assert transport._reader_task is not None

    await transport.close()

    # Process should be terminated
    # Reader task should be cancelled


# --- HTTP/SSE Transport Tests ---


def test_http_sse_transport_initialization() -> None:
    """Test HTTP/SSE transport initialization."""
    transport = HttpSseTransport(
        base_url="https://api.example.com/mcp", auth_token="token123"
    )

    assert transport.base_url == "https://api.example.com/mcp"
    assert transport.auth_token == "token123"


@pytest.mark.asyncio
async def test_http_sse_transport_not_implemented() -> None:
    """Test HTTP/SSE transport raises NotImplementedError."""
    transport = HttpSseTransport(base_url="https://api.example.com/mcp")

    with pytest.raises(NotImplementedError):
        await transport.send(JsonRpcRequest(method="test"))

    with pytest.raises(NotImplementedError):
        await transport.receive()


# --- MCP Client Tests ---


@pytest.mark.asyncio
async def test_mcp_client_initialization() -> None:
    """Test MCP client initialization."""
    transport = StdioTransport(command=["echo"])
    client = MCPClient(transport)

    assert client.transport == transport
    assert client.server_info is None
    assert client._request_id_counter == 0


@pytest.mark.asyncio
async def test_mcp_client_request_id_generation() -> None:
    """Test unique request ID generation."""
    transport = StdioTransport(command=["echo"])
    client = MCPClient(transport)

    id1 = client._next_request_id()
    id2 = client._next_request_id()
    id3 = client._next_request_id()

    assert id1 == 1
    assert id2 == 2
    assert id3 == 3


@pytest.mark.asyncio
async def test_mcp_client_connect_success() -> None:
    """Test MCP client connect with successful initialize."""
    transport = AsyncMock(spec=StdioTransport)

    # Mock initialize response
    init_response = JsonRpcResponse(
        id=1,
        result={
            "serverInfo": {"name": "test-server", "version": "1.0.0"},
            "protocolVersion": "2025-06-18",
            "capabilities": {"tools": {}},
        },
    )

    transport.receive = AsyncMock(return_value=init_response)
    transport.send = AsyncMock()

    client = MCPClient(transport)

    result = await client.connect()

    assert result.is_ok()
    server_info = result.unwrap()
    assert isinstance(server_info, MCPServerInfo)
    assert server_info.name == "test-server"
    assert server_info.version == "1.0.0"
    assert client.server_info == server_info

    # Verify initialize and initialized were sent
    assert transport.send.call_count == 2


@pytest.mark.asyncio
async def test_mcp_client_connect_error() -> None:
    """Test MCP client connect with initialize error."""
    transport = AsyncMock(spec=StdioTransport)

    # Mock initialize error response
    init_response = JsonRpcResponse(
        id=1, error={"code": -32603, "message": "Server initialization failed"}
    )

    transport.receive = AsyncMock(return_value=init_response)
    transport.send = AsyncMock()

    client = MCPClient(transport)

    result = await client.connect()

    assert result.is_err()
    error = result.error
    assert isinstance(error, ToolError)
    assert error.error_type == ToolErrorType.FATAL
    assert "initialization failed" in error.message.lower()


@pytest.mark.asyncio
@pytest.mark.slow
async def test_mcp_client_connect_timeout() -> None:
    """Test MCP client connect timeout using mocked timeout."""
    transport = AsyncMock(spec=StdioTransport)

    # Mock timeout by raising TimeoutError immediately
    transport.receive = AsyncMock(side_effect=asyncio.TimeoutError())
    transport.send = AsyncMock()

    client = MCPClient(transport)

    result = await client.connect()

    assert result.is_err()
    error = result.error
    assert error.error_type == ToolErrorType.TIMEOUT


@pytest.mark.asyncio
async def test_mcp_client_list_tools_success() -> None:
    """Test MCP client list tools."""
    transport = AsyncMock(spec=StdioTransport)
    client = MCPClient(transport)

    # Mock server as connected
    client.server_info = MCPServerInfo(name="test", version="1.0", capabilities={})

    # Mock list tools response
    tools_response = JsonRpcResponse(
        id=1,
        result={
            "tools": [
                {
                    "name": "web_search",
                    "description": "Search the web",
                    "inputSchema": {"type": "object", "properties": {}},
                },
                {
                    "name": "calculator",
                    "description": "Perform calculations",
                    "inputSchema": {"type": "object", "properties": {}},
                },
            ]
        },
    )

    transport.receive = AsyncMock(return_value=tools_response)
    transport.send = AsyncMock()

    result = await client.list_tools()

    assert result.is_ok()
    tools = result.unwrap()
    assert len(tools) == 2
    assert tools[0].name == "web_search"
    assert tools[1].name == "calculator"


@pytest.mark.asyncio
async def test_mcp_client_list_tools_not_connected() -> None:
    """Test MCP client list tools when not connected."""
    transport = AsyncMock(spec=StdioTransport)
    client = MCPClient(transport)

    # Server not connected
    client.server_info = None

    result = await client.list_tools()

    assert result.is_err()
    error = result.error
    assert error.error_type == ToolErrorType.FATAL
    assert "not connected" in error.message.lower()


@pytest.mark.asyncio
async def test_mcp_client_call_tool_success() -> None:
    """Test MCP client call tool."""
    transport = AsyncMock(spec=StdioTransport)
    client = MCPClient(transport)

    # Mock server as connected
    client.server_info = MCPServerInfo(name="test", version="1.0", capabilities={})

    # Mock tool call response
    tool_response = JsonRpcResponse(
        id=1,
        result={"content": [{"type": "text", "text": "Search results: ..."}]},
    )

    transport.receive = AsyncMock(return_value=tool_response)
    transport.send = AsyncMock()

    result = await client.call_tool("web_search", {"query": "MCP protocol"})

    assert result.is_ok()
    output = result.unwrap()
    assert output == "Search results: ..."


@pytest.mark.asyncio
async def test_mcp_client_call_tool_method_not_found() -> None:
    """Test MCP client call tool with method not found error."""
    transport = AsyncMock(spec=StdioTransport)
    client = MCPClient(transport)

    # Mock server as connected
    client.server_info = MCPServerInfo(name="test", version="1.0", capabilities={})

    # Mock method not found error
    tool_response = JsonRpcResponse(
        id=1, error={"code": JsonRpcError.METHOD_NOT_FOUND, "message": "Tool not found"}
    )

    transport.receive = AsyncMock(return_value=tool_response)
    transport.send = AsyncMock()

    result = await client.call_tool("nonexistent_tool", {})

    assert result.is_err()
    error = result.error
    assert error.error_type == ToolErrorType.NOT_FOUND


@pytest.mark.asyncio
async def test_mcp_client_call_tool_invalid_params() -> None:
    """Test MCP client call tool with invalid params error."""
    transport = AsyncMock(spec=StdioTransport)
    client = MCPClient(transport)

    # Mock server as connected
    client.server_info = MCPServerInfo(name="test", version="1.0", capabilities={})

    # Mock invalid params error
    tool_response = JsonRpcResponse(
        id=1, error={"code": JsonRpcError.INVALID_PARAMS, "message": "Invalid params"}
    )

    transport.receive = AsyncMock(return_value=tool_response)
    transport.send = AsyncMock()

    result = await client.call_tool("web_search", {"invalid": "params"})

    assert result.is_err()
    error = result.error
    assert error.error_type == ToolErrorType.VALIDATION


@pytest.mark.asyncio
@pytest.mark.slow
async def test_mcp_client_call_tool_timeout() -> None:
    """Test MCP client call tool timeout using mocked timeout."""
    transport = AsyncMock(spec=StdioTransport)
    client = MCPClient(transport)

    # Mock server as connected
    client.server_info = MCPServerInfo(name="test", version="1.0", capabilities={})

    # Mock timeout by raising TimeoutError immediately
    transport.receive = AsyncMock(side_effect=asyncio.TimeoutError())
    transport.send = AsyncMock()

    result = await client.call_tool("slow_tool", {})

    assert result.is_err()
    error = result.error
    assert error.error_type == ToolErrorType.TIMEOUT


@pytest.mark.asyncio
async def test_mcp_client_list_resources_success() -> None:
    """Test MCP client list resources."""
    transport = AsyncMock(spec=StdioTransport)
    client = MCPClient(transport)

    # Mock server as connected
    client.server_info = MCPServerInfo(name="test", version="1.0", capabilities={})

    # Mock list resources response
    resources_response = JsonRpcResponse(
        id=1,
        result={
            "resources": [
                {
                    "uri": "file:///path/to/file.txt",
                    "name": "file.txt",
                    "description": "A text file",
                    "mimeType": "text/plain",
                },
                {
                    "uri": "https://example.com/data",
                    "name": "remote-data",
                    "description": "Remote dataset",
                },
            ]
        },
    )

    transport.receive = AsyncMock(return_value=resources_response)
    transport.send = AsyncMock()

    result = await client.list_resources()

    assert result.is_ok()
    resources = result.unwrap()
    assert len(resources) == 2
    assert resources[0].uri == "file:///path/to/file.txt"
    assert resources[0].mime_type == "text/plain"
    assert resources[1].uri == "https://example.com/data"


@pytest.mark.asyncio
async def test_mcp_client_disconnect() -> None:
    """Test MCP client disconnect."""
    transport = AsyncMock(spec=StdioTransport)
    client = MCPClient(transport)

    # Mock server as connected
    client.server_info = MCPServerInfo(name="test", version="1.0", capabilities={})

    await client.disconnect()

    # Verify transport closed
    transport.close.assert_called_once()
    assert client.server_info is None


# --- MCPTool Tests ---


@pytest.mark.asyncio
async def test_mcp_tool_initialization() -> None:
    """Test MCPTool initialization from schema."""
    schema = MCPToolSchema(
        name="web_search",
        description="Search the web",
        input_schema={"type": "object", "properties": {}},
    )

    transport = AsyncMock(spec=StdioTransport)
    client = MCPClient(transport)
    client.server_info = MCPServerInfo(
        name="test-server", version="1.0", capabilities={}
    )

    tool = MCPTool.from_schema(schema, client)

    assert tool.schema == schema
    assert tool.client == client
    assert tool.meta.identity.name == "web_search"
    assert tool.meta.identity.description == "Search the web"
    assert tool.meta.identity.server == "test-server"


@pytest.mark.asyncio
async def test_mcp_tool_invoke_success() -> None:
    """Test MCPTool invoke with successful result."""
    schema = MCPToolSchema(
        name="web_search",
        description="Search the web",
        input_schema={"type": "object"},
    )

    transport = AsyncMock(spec=StdioTransport)
    client = MCPClient(transport)
    client.server_info = MCPServerInfo(name="test", version="1.0", capabilities={})

    # Mock call_tool to return success
    from bootstrap.types import ok

    client.call_tool = AsyncMock(return_value=ok("Search results"))

    tool = MCPTool.from_schema(schema, client)

    result = await tool.invoke({"query": "MCP protocol"})

    assert result == "Search results"
    client.call_tool.assert_called_once_with("web_search", {"query": "MCP protocol"})


@pytest.mark.asyncio
async def test_mcp_tool_invoke_error() -> None:
    """Test MCPTool invoke with error result."""
    schema = MCPToolSchema(
        name="web_search",
        description="Search the web",
        input_schema={"type": "object"},
    )

    transport = AsyncMock(spec=StdioTransport)
    client = MCPClient(transport)
    client.server_info = MCPServerInfo(name="test", version="1.0", capabilities={})

    # Mock call_tool to return error
    from bootstrap.types import err

    tool_error = ToolError(
        error_type=ToolErrorType.NETWORK,
        message="Connection failed",
        tool_name="web_search",
    )
    client.call_tool = AsyncMock(
        return_value=err(tool_error, message="Connection failed", recoverable=True)
    )

    tool = MCPTool.from_schema(schema, client)

    # Should raise ToolError
    with pytest.raises(ToolError) as exc_info:
        await tool.invoke({"query": "MCP protocol"})

    assert exc_info.value.error_type == ToolErrorType.NETWORK
    assert "Connection failed" in str(exc_info.value)


# --- Integration Tests ---


@pytest.mark.asyncio
async def test_mcp_full_lifecycle() -> None:
    """Test full MCP client lifecycle: connect → list → call → disconnect."""
    transport = AsyncMock(spec=StdioTransport)
    client = MCPClient(transport)

    # 1. Connect
    init_response = JsonRpcResponse(
        id=1,
        result={
            "serverInfo": {"name": "test-server", "version": "1.0.0"},
            "protocolVersion": "2025-06-18",
            "capabilities": {"tools": {}},
        },
    )
    transport.receive = AsyncMock(return_value=init_response)
    transport.send = AsyncMock()

    connect_result = await client.connect()
    assert connect_result.is_ok()

    # 2. List tools
    tools_response = JsonRpcResponse(
        id=2,
        result={
            "tools": [
                {
                    "name": "calculator",
                    "description": "Calculate",
                    "inputSchema": {"type": "object"},
                }
            ]
        },
    )
    transport.receive = AsyncMock(return_value=tools_response)

    list_result = await client.list_tools()
    assert list_result.is_ok()
    tools = list_result.unwrap()
    assert len(tools) == 1

    # 3. Call tool
    call_response = JsonRpcResponse(
        id=3, result={"content": [{"type": "text", "text": "42"}]}
    )
    transport.receive = AsyncMock(return_value=call_response)

    call_result = await client.call_tool("calculator", {"expression": "6 * 7"})
    assert call_result.is_ok()
    assert call_result.unwrap() == "42"

    # 4. Disconnect
    await client.disconnect()
    transport.close.assert_called_once()


@pytest.mark.asyncio
async def test_mcp_tool_composition() -> None:
    """Test MCPTool composition with other agents."""
    # Create mock schema and client
    schema = MCPToolSchema(
        name="uppercase", description="Convert to uppercase", input_schema={}
    )

    transport = AsyncMock(spec=StdioTransport)
    client = MCPClient(transport)
    client.server_info = MCPServerInfo(name="test", version="1.0", capabilities={})

    # Mock call_tool
    from bootstrap.types import ok

    client.call_tool = AsyncMock(return_value=ok("HELLO WORLD"))

    tool = MCPTool.from_schema(schema, client)

    # Test Tool[A, B] interface
    result = await tool.invoke({"text": "hello world"})
    assert result == "HELLO WORLD"

    # MCPTool should be composable with >> operator (inherited from Agent)
    assert hasattr(tool, "__rshift__")  # Has >> operator


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
