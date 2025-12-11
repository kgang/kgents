"""
MCP (Model Context Protocol) Integration.

kgents can be both MCP client AND server - bidirectional integration.

As Server (Priority!):
- Exposes kgents commands as MCP tools
- Allows Claude/Cursor to invoke kgents operations
- Bootstrapping: Claude helps build the rest of the CLI

As Client:
- Connects to external MCP servers
- Invokes external tools from flows

From docs/cli-integration-plan.md Part 8.
"""

from .client import (
    MCPClient,
    MCPConnection,
    invoke_tool,
)
from .server import (
    MCPRequest,
    MCPResponse,
    MCPServer,
    MCPTool,
    MCPToolResult,
    create_tool_manifest,
    start_server,
)

__all__ = [
    # Server
    "MCPServer",
    "MCPTool",
    "MCPToolResult",
    "MCPRequest",
    "MCPResponse",
    "start_server",
    "create_tool_manifest",
    # Client
    "MCPClient",
    "MCPConnection",
    "invoke_tool",
]
