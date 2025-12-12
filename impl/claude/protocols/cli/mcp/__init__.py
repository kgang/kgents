"""
MCP (Model Context Protocol) Integration.

kgents can be both MCP client AND server - bidirectional integration.

As Server (Priority!):
- Exposes kgents commands as MCP tools
- Exposes K8s cluster state as MCP resources (Phase E)
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
from .resources import (
    K8sConfig,
    K8sResourceProvider,
    MCPResource,
    MCPResourceContent,
    get_provider,
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
    # Resources (Phase E)
    "MCPResource",
    "MCPResourceContent",
    "K8sResourceProvider",
    "K8sConfig",
    "get_provider",
    # Client
    "MCPClient",
    "MCPConnection",
    "invoke_tool",
]
