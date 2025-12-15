# MCP Integration Guide

> *"Protocols are infrastructure, not cognition."*

This document describes how to integrate external tools and data sources via the **Model Context Protocol (MCP)** into kgents. MCP is a protocol layer, not an agent genus—external capabilities are wrapped as agents using existing L-gent (catalog) and D-gent (data) patterns.

## Why Not X-gent?

An earlier proposal suggested "X-gent" (Xenolinguist) as a separate genus for MCP integration. Analysis revealed:

1. **Protocols are infrastructure** - MCP/OpenAPI are transport protocols, not reasoning patterns
2. **Already covered** - L-gent (catalog), P-gent (parsing), D-gent (backends)
3. **No bootstrap derivation** - Protocol adapters don't derive from the seven bootstrap agents

**Decision**: MCP integration is infrastructure, documented here rather than as an agent genus.

## MCP Overview

The Model Context Protocol connects AI systems to external data sources and tools:

```
┌─────────────────────────────────────────────────────────────────┐
│                    MODEL CONTEXT PROTOCOL                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────┐      JSON-RPC       ┌─────────────┐           │
│  │   KGENTS    │ ◄────────────────► │  MCP SERVER │           │
│  │  (client)   │                     │  (external) │           │
│  └─────────────┘                     └─────────────┘           │
│                                                                  │
│  Capabilities exposed:                                           │
│  • Resources (read data)                                        │
│  • Tools (execute actions)                                      │
│  • Prompts (templated interactions)                             │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## Architecture

External MCP capabilities integrate through existing kgents patterns:

```
External MCP Server
       │
       │ JSON-RPC
       ▼
┌──────────────────┐
│   MCP Client     │  ← Infrastructure layer (this doc)
│   (protocol)     │
└────────┬─────────┘
         │
    ┌────┴────┐
    ▼         ▼
┌────────┐ ┌────────┐
│ L-gent │ │ D-gent │  ← Agent layer (existing)
│(catalog)│ │ (data) │
└────────┘ └────────┘
```

## MCP Client Implementation

```python
@dataclass
class MCPClient:
    """
    Core MCP client implementation.

    INFRASTRUCTURE LAYER - not an agent.
    """

    servers: dict[str, MCPServer] = field(default_factory=dict)
    resources: dict[str, MCPResource] = field(default_factory=dict)
    tools: dict[str, MCPTool] = field(default_factory=dict)
    transport: MCPTransport = field(default_factory=StdioTransport)

    async def connect(self, config: MCPServerConfig) -> MCPConnection:
        """Connect to an MCP server."""
        connection = await self.transport.connect(config)

        # Initialize protocol
        init_result = await connection.initialize(
            protocol_version="2024-11-05",
            capabilities=self._get_client_capabilities(),
            client_info={"name": "kgents", "version": "1.0.0"}
        )

        # Store server
        server = MCPServer(
            name=config.name,
            connection=connection,
            capabilities=init_result.capabilities
        )
        self.servers[config.name] = server

        # Discover resources and tools
        await self._discover_resources(server)
        await self._discover_tools(server)

        return connection

    async def call_tool(self, tool_name: str, arguments: dict) -> MCPToolResult:
        """Call an MCP tool."""
        tool = self.tools.get(tool_name)
        if not tool:
            raise ToolNotFoundError(tool_name)

        server = self.servers[tool.server]
        return await server.connection.call_tool(tool.name, arguments)

    async def read_resource(self, resource_uri: str) -> MCPResourceContent:
        """Read an MCP resource."""
        resource = self.resources.get(resource_uri)
        if not resource:
            raise ResourceNotFoundError(resource_uri)

        server = self.servers[resource.server]
        return await server.connection.read_resource(resource.uri)
```

## L-gent Integration (Catalog)

MCP tools and resources register with L-gent as agents:

```python
class MCPAgentFactory:
    """
    Creates kgents Agents from MCP capabilities.

    Uses L-gent for registration.
    """

    def __init__(self, mcp_client: MCPClient, l_gent: "L"):
        self.mcp = mcp_client
        self.l_gent = l_gent

    async def register_all(self, server_name: str) -> list[str]:
        """Register all MCP tools/resources as agents with L-gent."""
        registered = []

        # Register tools as agents
        for tool_name, tool in self.mcp.tools.items():
            if tool.server == server_name:
                agent = self._create_tool_agent(tool_name)
                await self.l_gent.register(
                    name=f"mcp.{tool_name}",
                    artifact=agent,
                    tags=["external", "mcp", server_name],
                    metadata={"source": "mcp", "type": "tool"}
                )
                registered.append(tool_name)

        # Register resources as agents
        for uri, resource in self.mcp.resources.items():
            if resource.server == server_name:
                agent = self._create_resource_agent(uri)
                await self.l_gent.register(
                    name=f"mcp.{resource.name}",
                    artifact=agent,
                    tags=["external", "mcp", server_name],
                    metadata={"source": "mcp", "type": "resource"}
                )
                registered.append(uri)

        return registered

    def _create_tool_agent(self, tool_name: str) -> Agent:
        """Wrap MCP tool as Agent."""
        tool = self.mcp.tools[tool_name]

        async def invoke(arguments: dict) -> Any:
            result = await self.mcp.call_tool(tool_name, arguments)
            return result.content

        return FunctionAgent(
            invoke,
            meta=AgentMeta(
                name=f"MCP_{tool_name}",
                genus="external",
                description=tool.description
            )
        )

    def _create_resource_agent(self, resource_uri: str) -> Agent:
        """Wrap MCP resource as Agent."""
        resource = self.mcp.resources[resource_uri]

        async def invoke(_: None) -> Any:
            content = await self.mcp.read_resource(resource_uri)
            return content.text

        return FunctionAgent(
            invoke,
            meta=AgentMeta(
                name=f"MCP_{resource.name}",
                genus="external",
                description=resource.description
            )
        )
```

## D-gent Integration (Data)

MCP databases integrate as D-gent backends:

```python
class MCPDatabaseBackend(DataBackend):
    """
    D-gent backend for MCP database servers.
    """

    def __init__(self, mcp_client: MCPClient, server_name: str):
        self.mcp = mcp_client
        self.server = server_name
        self.query_tool = f"{server_name}.query"

    async def load(self, key: str) -> Any:
        """Load data via MCP query."""
        result = await self.mcp.call_tool(
            self.query_tool,
            {"query": f"SELECT * FROM {key}"}
        )
        return result.content

    async def save(self, key: str, value: Any) -> None:
        """Save data via MCP (implementation depends on server)."""
        raise NotImplementedError("Depends on MCP server capabilities")

    async def query(self, sql: str) -> list[dict]:
        """Execute SQL query via MCP."""
        result = await self.mcp.call_tool(self.query_tool, {"query": sql})
        return result.content
```

## OpenAPI Integration

For REST APIs without MCP servers, use OpenAPI specs:

```python
@dataclass
class OpenAPIAdapter:
    """
    Creates agents from OpenAPI specifications.

    Complements MCP for REST APIs.
    """

    http_client: httpx.AsyncClient = field(default_factory=httpx.AsyncClient)

    async def load_spec(self, spec_url: str) -> OpenAPISpec:
        """Load and parse an OpenAPI specification."""
        response = await self.http_client.get(spec_url)
        spec_dict = response.json()
        return OpenAPISpec.from_dict(spec_dict)

    def create_endpoint_agent(
        self,
        spec: OpenAPISpec,
        path: str,
        method: str
    ) -> Agent:
        """Create an Agent from an OpenAPI endpoint."""
        endpoint = spec.paths.get(path, {}).get(method.lower())
        base_url = spec.servers[0].get("url", "") if spec.servers else ""

        async def invoke(params: dict) -> Any:
            url = f"{base_url}{path}"

            # Handle path parameters
            for param in endpoint.get("parameters", []):
                if param.get("in") == "path":
                    url = url.replace(
                        f"{{{param['name']}}}",
                        str(params.get(param["name"], ""))
                    )

            response = await self.http_client.request(
                method=method.upper(),
                url=url,
                params={k: v for k, v in params.items() if k not in url},
                json=params.get("body")
            )
            return response.json()

        return FunctionAgent(invoke)
```

## Security Considerations

External data must be sanitized:

```python
async def secure_mcp_call(
    mcp_client: MCPClient,
    tool_name: str,
    arguments: dict,
    p_gent: "P"  # Parser for sanitization
) -> Any:
    """Call MCP tool with input/output sanitization."""

    # Sanitize outgoing data
    for key, value in arguments.items():
        if isinstance(value, str):
            # Use P-gent to validate/sanitize
            sanitized = await p_gent.sanitize(value)
            arguments[key] = sanitized

    # Call external tool
    result = await mcp_client.call_tool(tool_name, arguments)

    # Sanitize incoming data
    if isinstance(result.content, str):
        result.content = await p_gent.sanitize(result.content)

    return result
```

## Configuration

MCP servers are configured via `kgents.toml`:

```toml
[mcp.servers.github]
command = "npx"
args = ["-y", "@modelcontextprotocol/server-github"]

[mcp.servers.postgres]
command = "npx"
args = ["-y", "@modelcontextprotocol/server-postgres"]
env = { DATABASE_URL = "postgresql://..." }

[mcp.servers.filesystem]
command = "npx"
args = ["-y", "@modelcontextprotocol/server-filesystem", "/allowed/path"]
```

## Supported MCP Servers

| Server | Capabilities | Notes |
|--------|--------------|-------|
| GitHub | Issues, PRs, Repos | Read/write |
| Slack | Messages, Channels | Read/write |
| PostgreSQL | Query, Schema | Read/write |
| Filesystem | Read, Write | Sandboxed paths |
| Puppeteer | Browser automation | Heavy resource use |

## Anti-Patterns

1. ❌ Creating "X-gent" as protocol adapter genus (protocols are infrastructure)
2. ❌ Exposing raw MCP interfaces to agents (wrap as proper agents)
3. ❌ Skipping sanitization for "trusted" external sources (all external is untrusted)
4. ❌ Hardcoding external API URLs (use config)
5. ❌ Caching external data indefinitely (respect TTLs)

## See Also

- [../spec/l-gents/](../spec/l-gents/) - Agent catalog for registration
- [../spec/d-gents/](../spec/d-gents/) - Data persistence patterns
- [../spec/p-gents/](../spec/p-gents/) - Parsing and sanitization
- [MCP Documentation](https://modelcontextprotocol.io/) - Official MCP docs
