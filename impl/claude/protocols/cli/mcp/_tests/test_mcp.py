"""
Tests for MCP Server and Client.

Tests cover:
- Tool definitions and manifests
- Request/response handling
- Tool invocation
- Client connections
"""

import json
from pathlib import Path

import pytest

from ..client import (
    MCPClient,
    MCPConnection,
)
from ..server import (
    KGENTS_TOOLS,
    TOOL_REGISTRY,
    MCPRequest,
    MCPResponse,
    MCPServer,
    MCPTool,
    MCPToolParameter,
    MCPToolResult,
    create_tool_manifest,
    handle_check,
    handle_fix,
    handle_judge,
    handle_laws,
    handle_principles,
    handle_think,
)

# =============================================================================
# Tool Definition Tests
# =============================================================================


class TestMCPToolParameter:
    """Test tool parameter definitions."""

    def test_create_required(self) -> None:
        param = MCPToolParameter(
            name="target",
            type="string",
            description="Target to check",
        )
        assert param.name == "target"
        assert param.type == "string"
        assert param.required is True

    def test_create_optional_with_default(self) -> None:
        param = MCPToolParameter(
            name="budget",
            type="string",
            description="Budget level",
            required=False,
            default="medium",
        )
        assert param.required is False
        assert param.default == "medium"

    def test_create_with_enum(self) -> None:
        param = MCPToolParameter(
            name="level",
            type="string",
            description="Complexity level",
            enum=("low", "medium", "high"),
        )
        assert param.enum == ("low", "medium", "high")

    def test_to_dict(self) -> None:
        param = MCPToolParameter(
            name="query",
            type="string",
            description="Search query",
            required=True,
        )
        d = param.to_dict()
        assert d["name"] == "query"
        assert d["type"] == "string"
        assert "required" not in d  # Only added if False


class TestMCPTool:
    """Test tool definitions."""

    def test_create_minimal(self) -> None:
        tool = MCPTool(
            name="test_tool",
            description="A test tool",
        )
        assert tool.name == "test_tool"
        assert tool.parameters == ()
        assert tool.handler is None

    def test_create_with_parameters(self) -> None:
        tool = MCPTool(
            name="kgents_check",
            description="Check code",
            parameters=(MCPToolParameter("target", "string", "Target file"),),
        )
        assert len(tool.parameters) == 1

    def test_to_dict(self) -> None:
        tool = MCPTool(
            name="kgents_check",
            description="Verify code against principles",
            parameters=(
                MCPToolParameter("target", "string", "File to check"),
                MCPToolParameter(
                    "strictness", "string", "Level", required=False, default="high"
                ),
            ),
        )
        d = tool.to_dict()

        assert d["name"] == "kgents_check"
        assert d["description"] == "Verify code against principles"
        assert "inputSchema" in d
        assert d["inputSchema"]["type"] == "object"
        assert "target" in d["inputSchema"]["properties"]
        assert d["inputSchema"]["required"] == ["target"]


class TestMCPToolResult:
    """Test tool results."""

    def test_success_result(self) -> None:
        result = MCPToolResult(
            success=True,
            content="Operation completed",
        )
        assert result.success is True
        assert result.content_type == "text/plain"

    def test_to_dict(self) -> None:
        result = MCPToolResult(
            success=True,
            content="Hello, world!",
        )
        d = result.to_dict()
        assert d["type"] == "text"
        assert d["text"] == "Hello, world!"


# =============================================================================
# Tool Registry Tests
# =============================================================================


class TestToolRegistry:
    """Test the tool registry."""

    def test_all_tools_registered(self) -> None:
        """All KGENTS_TOOLS should be in the registry."""
        for tool in KGENTS_TOOLS:
            assert tool.name in TOOL_REGISTRY

    def test_expected_tools_exist(self) -> None:
        """Check expected tools are present."""
        expected = [
            "kgents_check",
            "kgents_judge",
            "kgents_think",
            "kgents_fix",
            "kgents_speak",
            "kgents_find",
            "kgents_flow_run",
            "kgents_laws",
            "kgents_principles",
        ]
        for name in expected:
            assert name in TOOL_REGISTRY, f"Missing tool: {name}"

    def test_all_tools_have_handlers(self) -> None:
        """All tools should have handlers."""
        for tool in KGENTS_TOOLS:
            assert tool.handler is not None, f"Tool {tool.name} missing handler"


class TestToolManifest:
    """Test manifest generation."""

    def test_create_manifest(self) -> None:
        manifest = create_tool_manifest()

        assert manifest["name"] == "kgents"
        assert manifest["version"] == "0.2.0"
        assert "tools" in manifest
        assert len(manifest["tools"]) == len(KGENTS_TOOLS)

    def test_manifest_is_valid_json(self) -> None:
        manifest = create_tool_manifest()
        json_str = json.dumps(manifest)
        parsed = json.loads(json_str)
        assert parsed["name"] == "kgents"


# =============================================================================
# Request/Response Tests
# =============================================================================


class TestMCPRequest:
    """Test MCP request handling."""

    def test_from_dict(self) -> None:
        data = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/list",
        }
        request = MCPRequest.from_dict(data)
        assert request.id == 1
        assert request.method == "tools/list"

    def test_from_dict_with_params(self) -> None:
        data = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {
                "name": "kgents_check",
                "arguments": {"target": "main.py"},
            },
        }
        request = MCPRequest.from_dict(data)
        assert request.params["name"] == "kgents_check"


class TestMCPResponse:
    """Test MCP response handling."""

    def test_success_response(self) -> None:
        response = MCPResponse(
            id=1,
            result={"tools": []},
        )
        d = response.to_dict()
        assert d["id"] == 1
        assert d["result"] == {"tools": []}
        assert "error" not in d

    def test_error_response(self) -> None:
        response = MCPResponse(
            id=1,
            error={"code": -32601, "message": "Method not found"},
        )
        d = response.to_dict()
        assert "error" in d
        assert d["error"]["code"] == -32601


# =============================================================================
# Tool Handler Tests
# =============================================================================


class TestToolHandlers:
    """Test individual tool handlers."""

    @pytest.mark.asyncio
    async def test_handle_laws(self) -> None:
        result = await handle_laws()
        assert result.success is True
        assert "IDENTITY" in result.content  # Laws are displayed in UPPERCASE

    @pytest.mark.asyncio
    async def test_handle_principles(self) -> None:
        result = await handle_principles()
        assert result.success is True
        assert "TASTEFUL" in result.content
        assert "COMPOSABLE" in result.content

    @pytest.mark.asyncio
    async def test_handle_check_placeholder(self) -> None:
        """Check handler returns reasonable result.

        With insufficient input, the evaluation returns 'unclear' verdict
        which maps to success=False. This is correct behavior.
        """
        result = await handle_check("test.py", "spec/principles.md")
        # With minimal input, evaluation is unclear (not enough info)
        assert result.content_type == "application/json"
        assert "verdict" in result.content

    @pytest.mark.asyncio
    async def test_handle_judge_placeholder(self) -> None:
        """Judge handler returns reasonable result.

        With insufficient input, the evaluation returns 'unclear' verdict
        which maps to success=False. This is correct behavior.
        """
        result = await handle_judge("Some code to judge", "high")
        # With minimal input, evaluation is unclear (not enough info)
        assert "Verdict:" in result.content
        assert "Evaluations:" in result.content

    @pytest.mark.asyncio
    async def test_handle_think_placeholder(self) -> None:
        """Think handler returns reasonable result."""
        result = await handle_think("optimization strategies", "medium")
        assert result.success is True

    @pytest.mark.asyncio
    async def test_handle_fix_with_string(self) -> None:
        """Fix handler with string input."""
        result = await handle_fix("  malformed input  ", "anchor")
        assert result.success is True
        assert result.content == "malformed input"  # Stripped


# =============================================================================
# Server Tests
# =============================================================================


class TestMCPServer:
    """Test MCP server."""

    def test_create_server(self) -> None:
        server = MCPServer()
        assert server.name == "kgents"
        assert len(server.tools) > 0

    def test_custom_name(self) -> None:
        server = MCPServer(name="custom", version="1.0.0")
        assert server.name == "custom"
        assert server.version == "1.0.0"

    @pytest.mark.asyncio
    async def test_handle_initialize(self) -> None:
        server = MCPServer()
        request = MCPRequest(
            jsonrpc="2.0",
            id=1,
            method="initialize",
        )
        response = await server.handle_request(request)
        assert response.error is None
        assert "capabilities" in response.result

    @pytest.mark.asyncio
    async def test_handle_tools_list(self) -> None:
        server = MCPServer()
        request = MCPRequest(
            jsonrpc="2.0",
            id=2,
            method="tools/list",
        )
        response = await server.handle_request(request)
        assert response.error is None
        assert "tools" in response.result
        assert len(response.result["tools"]) > 0

    @pytest.mark.asyncio
    async def test_handle_tools_call(self) -> None:
        server = MCPServer()
        request = MCPRequest(
            jsonrpc="2.0",
            id=3,
            method="tools/call",
            params={
                "name": "kgents_principles",
                "arguments": {},
            },
        )
        response = await server.handle_request(request)
        assert response.error is None
        assert "content" in response.result
        assert response.result["isError"] is False

    @pytest.mark.asyncio
    async def test_handle_unknown_method(self) -> None:
        server = MCPServer()
        request = MCPRequest(
            jsonrpc="2.0",
            id=4,
            method="unknown/method",
        )
        response = await server.handle_request(request)
        assert response.error is not None
        assert response.error["code"] == -32601

    @pytest.mark.asyncio
    async def test_handle_unknown_tool(self) -> None:
        server = MCPServer()
        request = MCPRequest(
            jsonrpc="2.0",
            id=5,
            method="tools/call",
            params={
                "name": "nonexistent_tool",
                "arguments": {},
            },
        )
        response = await server.handle_request(request)
        assert response.result["isError"] is True

    def test_register_custom_tool(self) -> None:
        server = MCPServer()
        custom = MCPTool(
            name="custom_tool",
            description="A custom tool",
            handler=lambda: MCPToolResult(success=True, content="custom"),
        )
        server.register_tool(custom)
        assert "custom_tool" in server.tools


# =============================================================================
# Client Tests
# =============================================================================


class TestMCPConnection:
    """Test MCP connection objects."""

    def test_create_connection(self) -> None:
        conn = MCPConnection(
            name="test",
            command="echo",
            args=["hello"],
        )
        assert conn.name == "test"
        assert conn.process is None
        assert conn._initialized is False

    def test_to_dict(self) -> None:
        conn = MCPConnection(
            name="filesystem",
            command="npx",
            args=["@modelcontextprotocol/server-filesystem", "/tmp"],
        )
        d = conn.to_dict()
        assert d["name"] == "filesystem"
        assert d["connected"] is False
        assert d["tools"] == 0

    def test_from_dict(self) -> None:
        data = {
            "name": "test",
            "command": "python",
            "args": ["-m", "server"],
        }
        conn = MCPConnection.from_dict(data)
        assert conn.name == "test"
        assert conn.command == "python"


class TestMCPClient:
    """Test MCP client."""

    def test_create_client(self) -> None:
        client = MCPClient()
        assert len(client.connections) == 0

    def test_save_and_load_config(self, tmp_path: Path) -> None:
        config_path = tmp_path / ".kgents" / "mcp.json"
        client = MCPClient(config_path=config_path)

        # Add connection
        conn = MCPConnection(name="test", command="echo")
        client.connections["test"] = conn

        # Save
        client.save_config()
        assert config_path.exists()

        # Load in new client
        client2 = MCPClient(config_path=config_path)
        client2.load_config()
        assert "test" in client2.connections

    def test_list_connections_empty(self) -> None:
        client = MCPClient()
        assert client.list_connections() == []

    def test_list_connections(self) -> None:
        client = MCPClient()
        client.connections["test"] = MCPConnection(name="test", command="echo")
        conns = client.list_connections()
        assert len(conns) == 1
        assert conns[0]["name"] == "test"

    def test_list_tools_no_connections(self) -> None:
        client = MCPClient()
        assert client.list_tools() == []


# =============================================================================
# Integration Tests
# =============================================================================


class TestIntegration:
    """Integration tests for MCP."""

    @pytest.mark.asyncio
    async def test_full_server_flow(self) -> None:
        """Test a full request/response cycle."""
        server = MCPServer()

        # Initialize
        init_req = MCPRequest(jsonrpc="2.0", id=1, method="initialize")
        init_resp = await server.handle_request(init_req)
        assert init_resp.error is None

        # List tools
        list_req = MCPRequest(jsonrpc="2.0", id=2, method="tools/list")
        list_resp = await server.handle_request(list_req)
        assert len(list_resp.result["tools"]) > 0

        # Call a tool
        call_req = MCPRequest(
            jsonrpc="2.0",
            id=3,
            method="tools/call",
            params={"name": "kgents_laws", "arguments": {}},
        )
        call_resp = await server.handle_request(call_req)
        assert call_resp.result["isError"] is False

    def test_manifest_matches_tools(self) -> None:
        """Manifest should have all registered tools."""
        manifest = create_tool_manifest()
        manifest_names = {t["name"] for t in manifest["tools"]}
        registry_names = set(TOOL_REGISTRY.keys())
        assert manifest_names == registry_names
