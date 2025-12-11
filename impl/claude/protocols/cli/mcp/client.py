"""
MCP Client - Connect to external MCP servers.

Allows kgents to invoke tools from external MCP servers,
enabling integration with the broader MCP ecosystem.

Commands:
    kgents mcp connect <server>
    kgents mcp list
    kgents mcp tools
    kgents mcp invoke <tool> [args...]

From docs/cli-integration-plan.md Part 8.
"""

from __future__ import annotations

import json
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from .server import MCPRequest, MCPResponse, MCPTool, MCPToolResult

# =============================================================================
# Connection Types
# =============================================================================


@dataclass
class MCPConnection:
    """Connection to an external MCP server."""

    name: str
    command: str  # Command to start server (e.g., "npx @modelcontextprotocol/server-filesystem")
    args: list[str] = field(default_factory=list)
    env: dict[str, str] = field(default_factory=dict)

    # Runtime state
    process: subprocess.Popen | None = None
    tools: list[MCPTool] = field(default_factory=list)
    _initialized: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "command": self.command,
            "args": self.args,
            "env": self.env,
            "connected": self.process is not None,
            "tools": len(self.tools),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> MCPConnection:
        return cls(
            name=data["name"],
            command=data["command"],
            args=data.get("args", []),
            env=data.get("env", {}),
        )


# =============================================================================
# MCP Client
# =============================================================================


class MCPClient:
    """
    Client for connecting to external MCP servers.

    Manages connections and tool invocations.
    """

    def __init__(self, config_path: Path | None = None):
        """
        Initialize client.

        Args:
            config_path: Path to .kgents/mcp.json config (default: .kgents/mcp.json)
        """
        self.config_path = config_path or Path(".kgents/mcp.json")
        self.connections: dict[str, MCPConnection] = {}
        self._request_id = 0

    def _next_id(self) -> int:
        """Get next request ID."""
        self._request_id += 1
        return self._request_id

    def load_config(self) -> None:
        """Load connections from config file."""
        if self.config_path.exists():
            data = json.loads(self.config_path.read_text())
            for conn_data in data.get("connections", []):
                conn = MCPConnection.from_dict(conn_data)
                self.connections[conn.name] = conn

    def save_config(self) -> None:
        """Save connections to config file."""
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        data = {
            "connections": [
                {
                    "name": c.name,
                    "command": c.command,
                    "args": c.args,
                    "env": c.env,
                }
                for c in self.connections.values()
            ]
        }
        self.config_path.write_text(json.dumps(data, indent=2))

    async def connect(self, connection: MCPConnection) -> bool:
        """
        Connect to an MCP server.

        Starts the server process and initializes the connection.
        """
        try:
            # Start process
            cmd = [connection.command] + connection.args
            env = {**connection.env}

            connection.process = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                env=env if env else None,
            )

            # Send initialize request
            init_request = MCPRequest(
                jsonrpc="2.0",
                id=self._next_id(),
                method="initialize",
                params={
                    "protocolVersion": "2024-11-05",
                    "capabilities": {},
                    "clientInfo": {
                        "name": "kgents",
                        "version": "0.2.0",
                    },
                },
            )

            await self._send_request(connection, init_request)

            # Send initialized notification
            await self._send_notification(connection, "notifications/initialized", {})

            # Get tools list
            tools_request = MCPRequest(
                jsonrpc="2.0",
                id=self._next_id(),
                method="tools/list",
            )
            response = await self._send_request(connection, tools_request)

            if response.result:
                tools_data = response.result.get("tools", [])
                connection.tools = [
                    MCPTool(
                        name=t.get("name", ""),
                        description=t.get("description", ""),
                    )
                    for t in tools_data
                ]

            connection._initialized = True
            self.connections[connection.name] = connection
            return True

        except Exception as e:
            print(f"Failed to connect to {connection.name}: {e}", file=sys.stderr)
            if connection.process:
                connection.process.terminate()
                connection.process = None
            return False

    async def disconnect(self, name: str) -> bool:
        """Disconnect from an MCP server."""
        if name not in self.connections:
            return False

        conn = self.connections[name]
        if conn.process:
            conn.process.terminate()
            conn.process.wait()
            conn.process = None

        conn._initialized = False
        return True

    async def _send_request(
        self, connection: MCPConnection, request: MCPRequest
    ) -> MCPResponse:
        """Send request and wait for response."""
        if (
            not connection.process
            or not connection.process.stdin
            or not connection.process.stdout
        ):
            raise RuntimeError("Not connected")

        # Send request
        request_line = json.dumps(
            {
                "jsonrpc": request.jsonrpc,
                "id": request.id,
                "method": request.method,
                "params": request.params,
            }
        )
        connection.process.stdin.write(request_line + "\n")
        connection.process.stdin.flush()

        # Read response
        response_line = connection.process.stdout.readline()
        if not response_line:
            raise RuntimeError("No response from server")

        data = json.loads(response_line)
        return MCPResponse(
            jsonrpc=data.get("jsonrpc", "2.0"),
            id=data.get("id", 0),
            result=data.get("result"),
            error=data.get("error"),
        )

    async def _send_notification(
        self, connection: MCPConnection, method: str, params: dict[str, Any]
    ) -> None:
        """Send notification (no response expected)."""
        if not connection.process or not connection.process.stdin:
            raise RuntimeError("Not connected")

        notification = json.dumps(
            {
                "jsonrpc": "2.0",
                "method": method,
                "params": params,
            }
        )
        connection.process.stdin.write(notification + "\n")
        connection.process.stdin.flush()

    async def invoke(
        self, connection_name: str, tool_name: str, arguments: dict[str, Any]
    ) -> MCPToolResult:
        """
        Invoke a tool on a connected server.

        Args:
            connection_name: Name of the connection
            tool_name: Name of the tool to invoke
            arguments: Tool arguments

        Returns:
            MCPToolResult with the invocation result
        """
        if connection_name not in self.connections:
            return MCPToolResult(
                success=False,
                content=f"Unknown connection: {connection_name}",
            )

        conn = self.connections[connection_name]
        if not conn._initialized or not conn.process:
            return MCPToolResult(
                success=False,
                content=f"Not connected to: {connection_name}",
            )

        try:
            request = MCPRequest(
                jsonrpc="2.0",
                id=self._next_id(),
                method="tools/call",
                params={
                    "name": tool_name,
                    "arguments": arguments,
                },
            )

            response = await self._send_request(conn, request)

            if response.error:
                return MCPToolResult(
                    success=False,
                    content=response.error.get("message", "Unknown error"),
                )

            # Extract content from response
            result = response.result or {}
            content_list = result.get("content", [])
            is_error = result.get("isError", False)

            if content_list:
                text_parts = [
                    c.get("text", "") for c in content_list if c.get("type") == "text"
                ]
                content = "\n".join(text_parts)
            else:
                content = json.dumps(result)

            return MCPToolResult(
                success=not is_error,
                content=content,
            )

        except Exception as e:
            return MCPToolResult(
                success=False,
                content=f"Invocation failed: {e}",
            )

    def list_connections(self) -> list[dict[str, Any]]:
        """List all connections and their status."""
        return [conn.to_dict() for conn in self.connections.values()]

    def list_tools(self, connection_name: str | None = None) -> list[MCPTool]:
        """List tools from connection(s)."""
        if connection_name:
            conn = self.connections.get(connection_name)
            return conn.tools if conn else []

        # All tools from all connections
        all_tools = []
        for conn in self.connections.values():
            for tool in conn.tools:
                all_tools.append(tool)
        return all_tools


# =============================================================================
# Convenience Functions
# =============================================================================


async def invoke_tool(
    connection_name: str,
    tool_name: str,
    arguments: dict[str, Any],
    config_path: Path | None = None,
) -> MCPToolResult:
    """
    Convenience function to invoke a tool on a connected server.

    Args:
        connection_name: Name of the connection
        tool_name: Name of the tool
        arguments: Tool arguments
        config_path: Path to config file

    Returns:
        MCPToolResult
    """
    client = MCPClient(config_path=config_path)
    client.load_config()

    if connection_name not in client.connections:
        return MCPToolResult(
            success=False,
            content=f"Unknown connection: {connection_name}. Use 'kgents mcp connect' first.",
        )

    # Reconnect if needed
    conn = client.connections[connection_name]
    if not conn._initialized:
        connected = await client.connect(conn)
        if not connected:
            return MCPToolResult(
                success=False,
                content=f"Failed to connect to: {connection_name}",
            )

    return await client.invoke(connection_name, tool_name, arguments)
