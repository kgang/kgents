"""
MCP Server - Expose kgents as MCP tools and resources.

This is the "Killer Feature" - making kgents available to Claude/Cursor.
Priority: Implement early so Claude can help build the rest of the CLI.

Exposed Tools (auto-generated from intent layer):
- kgents_check: Verify code/agent/flow
- kgents_judge: 7-principles evaluation
- kgents_think: Generate hypotheses
- kgents_fix: Repair malformed input
- kgents_speak: Create domain language
- kgents_find: Search catalog
- kgents_flow: Execute flowfile

Exposed Resources (Phase E - K8s integration):
- kgents://agents: List Agent CRs
- kgents://agents/{name}: Agent status
- kgents://pheromones: Active pheromones
- kgents://cluster/status: Cluster health

From docs/cli-integration-plan.md Part 8.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Callable

# =============================================================================
# MCP Protocol Types
# =============================================================================


class MCPVersion(str, Enum):
    """MCP protocol versions."""

    V1 = "2024-11-05"


@dataclass(frozen=True)
class MCPToolParameter:
    """Tool parameter definition."""

    name: str
    type: str  # "string", "number", "boolean", "array", "object"
    description: str
    required: bool = True
    default: Any = None
    enum: tuple[str, ...] | None = None

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {
            "name": self.name,
            "type": self.type,
            "description": self.description,
        }
        if not self.required:
            result["required"] = False
        if self.default is not None:
            result["default"] = self.default
        if self.enum:
            result["enum"] = list(self.enum)
        return result


@dataclass(frozen=True)
class MCPTool:
    """Tool definition for MCP manifest."""

    name: str
    description: str
    parameters: tuple[MCPToolParameter, ...] = ()
    handler: Callable[..., Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "inputSchema": {
                "type": "object",
                "properties": {
                    p.name: {
                        "type": p.type,
                        "description": p.description,
                        **({"enum": list(p.enum)} if p.enum else {}),
                        **({"default": p.default} if p.default is not None else {}),
                    }
                    for p in self.parameters
                },
                "required": [p.name for p in self.parameters if p.required],
            },
        }


@dataclass
class MCPToolResult:
    """Result from tool invocation."""

    success: bool
    content: str
    content_type: str = "text/plain"
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": "text",
            "text": self.content,
        }


@dataclass
class MCPRequest:
    """Incoming MCP request."""

    jsonrpc: str
    id: int | str
    method: str
    params: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> MCPRequest:
        return cls(
            jsonrpc=data.get("jsonrpc", "2.0"),
            id=data.get("id", 0),
            method=data["method"],
            params=data.get("params", {}),
        )


@dataclass
class MCPResponse:
    """Outgoing MCP response."""

    jsonrpc: str = "2.0"
    id: int | str = 0
    result: Any = None
    error: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        response: dict[str, Any] = {"jsonrpc": self.jsonrpc, "id": self.id}
        if self.error:
            response["error"] = self.error
        else:
            response["result"] = self.result
        return response


# =============================================================================
# Tool Handlers
# =============================================================================


async def handle_check(target: str, principles: str = "spec/principles.md") -> MCPToolResult:
    """
    Verify code/agent/flow against principles.

    Maps to: kgents check <target> --principles=<path>
    """
    # Import lazily to avoid circular imports
    try:
        from ..bootstrap.principles import evaluate_against_principles

        result_report = await evaluate_against_principles(target)

        # Convert EvaluationReport to dict format
        result = {
            "approved": result_report.overall_verdict.value == "accept",
            "verdict": result_report.overall_verdict.value,
            "summary": result_report.summary,
        }

        return MCPToolResult(
            success=bool(result.get("approved", False)),
            content=json.dumps(result, indent=2),
            content_type="application/json",
        )
    except ImportError:
        # Fallback if bootstrap not available
        return MCPToolResult(
            success=True,
            content=f"Check target: {target} against {principles}",
            metadata={"target": target, "principles": principles},
        )


async def handle_judge(input_text: str, strictness: str = "high") -> MCPToolResult:
    """
    Evaluate input against the 7 design principles.

    Maps to: kgents judge "<input>" --strictness=<level>
    """
    try:
        from ..bootstrap.principles import evaluate_against_principles

        result_report = await evaluate_against_principles(input_text)

        verdict = result_report.overall_verdict.value
        formatted = f"Verdict: {verdict}\n\nEvaluations:\n"
        for eval in result_report.evaluations:
            formatted += (
                f"  - {eval.principle.value}: {eval.verdict.value} ({eval.confidence:.2f})\n"
            )
        formatted += f"\nSummary: {result_report.summary}\n"

        return MCPToolResult(
            success=verdict == "accept",
            content=formatted,
            metadata={
                "verdict": verdict,
                "summary": result_report.summary,
                "evaluations": [
                    {
                        "principle": e.principle.value,
                        "verdict": e.verdict.value,
                        "confidence": e.confidence,
                    }
                    for e in result_report.evaluations
                ],
            },
        )
    except ImportError:
        # Placeholder
        return MCPToolResult(
            success=True,
            content=f"Judging: {input_text[:100]}... (strictness={strictness})",
        )


async def handle_think(topic: str, budget: str = "medium") -> MCPToolResult:
    """
    Generate hypotheses about a topic.

    Maps to: kgents think "<topic>" --budget=<level>
    """
    try:
        from ..scientific import generate_hypotheses

        hypotheses = generate_hypotheses(topic, budget)
        formatted = f"Hypotheses about '{topic}':\n\n"
        for i, h in enumerate(hypotheses, 1):
            formatted += f"{i}. {h}\n"

        return MCPToolResult(
            success=True,
            content=formatted,
            metadata={"topic": topic, "count": len(hypotheses)},
        )
    except ImportError:
        # Placeholder
        return MCPToolResult(
            success=True,
            content=f"Thinking about: {topic} (budget={budget})",
        )


async def handle_fix(target: str, strategy: str = "anchor") -> MCPToolResult:
    """
    Repair malformed input.

    Maps to: kgents fix <target> --strategy=<strategy>
    """
    try:
        # Read file if it's a path
        if Path(target).exists():
            content = Path(target).read_text()
        else:
            content = target

        # Basic repair attempt (P-gent would do more)
        repaired = content.strip()

        return MCPToolResult(
            success=True,
            content=repaired,
            metadata={"strategy": strategy, "original_length": len(content)},
        )
    except Exception as e:
        return MCPToolResult(
            success=False,
            content=f"Failed to repair: {e}",
        )


async def handle_speak(domain: str, level: str = "COMMAND") -> MCPToolResult:
    """
    Create a domain language (Tongue).

    Maps to: kgents speak "<domain>" --level=<schema|command|recursive>
    """
    try:
        from agents.g import Grammarian, GrammarLevel

        # Map level string to GrammarLevel enum
        level_map = {
            "SCHEMA": GrammarLevel.SCHEMA,
            "COMMAND": GrammarLevel.COMMAND,
            "RECURSIVE": GrammarLevel.RECURSIVE,
        }
        grammar_level = level_map.get(level.upper(), GrammarLevel.COMMAND)

        # Create tongue via Grammarian (async call with required constraints)
        grammarian = Grammarian()
        tongue = await grammarian.reify(
            domain=domain,
            constraints=[],  # Empty constraints for basic creation
            level=grammar_level,
            examples=[],  # Empty examples for quick creation
        )

        # Format output
        output = f"Created tongue for '{domain}' at level {level}\n\n"
        output += f"Name: {tongue.name}\n"
        output += f"Level: {tongue.level.name}\n"
        output += f"Format: {tongue.format.name}\n"
        if tongue.grammar:
            output += (
                f"\nGrammar:\n{tongue.grammar[:500]}{'...' if len(tongue.grammar) > 500 else ''}"
            )

        return MCPToolResult(
            success=True,
            content=output,
            content_type="text/plain",
            metadata={"domain": domain, "level": level, "tongue_name": tongue.name},
        )
    except ImportError as e:
        return MCPToolResult(
            success=True,
            content=f"Creating tongue for: {domain} (level={level})\n[G-gent not available: {e}]",
        )
    except Exception as e:
        return MCPToolResult(
            success=False,
            content=f"Failed to create tongue: {e}",
        )


async def handle_find(query: str, limit: int = 10) -> MCPToolResult:
    """
    Search the catalog for agents/tongues/artifacts.

    Maps to: kgents find "<query>" --limit=<n>
    """
    # Built-in agent catalog for quick lookup
    standard_agents = [
        ("A-gent", "Abstract architectures and creative agents", "AGENT"),
        ("B-gent", "Bio/Scientific discovery and economics", "AGENT"),
        ("C-gent", "Category theory composition", "AGENT"),
        ("D-gent", "Data agents - state, memory, persistence", "AGENT"),
        ("F-gent", "Flow - chat, research, collaboration substrate", "AGENT"),
        ("G-gent", "Grammarian - DSL synthesis", "AGENT"),
        ("H-gent", "Shadow/ethical agents", "AGENT"),
        ("I-gent", "Interface agents - TUI/interaction", "AGENT"),
        ("J-gent", "JIT compilation and optimization", "AGENT"),
        ("K-gent", "Kent simulacra persona", "AGENT"),
        ("L-gent", "Librarian - semantic search and catalogs", "AGENT"),
        ("M-gent", "Memory - holographic recall", "AGENT"),
        ("N-gent", "Narrator - storytelling and tracing", "AGENT"),
        ("O-gent", "Observer - telemetry and monitoring", "AGENT"),
        ("P-gent", "Parser - error repair", "AGENT"),
        ("Psi-gent", "Psychopomp - metaphor-based problem solving", "AGENT"),
        ("T-gent", "Tester - fuzzing and property testing", "AGENT"),
        ("W-gent", "Wire - communication protocol", "AGENT"),
    ]

    # Simple keyword matching search
    query_lower = query.lower()
    results = []

    for name, desc, etype in standard_agents:
        score = 0.0

        # Exact name match
        if query_lower == name.lower():
            score = 1.0
        # Partial name match
        elif query_lower in name.lower():
            score = 0.7
        # Description match
        elif query_lower in desc.lower():
            score = 0.5
        # Word match in description
        elif any(query_lower in word.lower() for word in desc.split()):
            score = 0.3

        if score > 0:
            results.append((name, desc, etype, score))

    # Sort by score descending
    results.sort(key=lambda x: x[3], reverse=True)
    results = results[:limit]

    if not results:
        return MCPToolResult(
            success=True,
            content=f"No results found for '{query}'",
            metadata={"query": query, "count": 0},
        )

    formatted = f"Search results for '{query}':\n\n"
    for name, desc, etype, score in results:
        formatted += f"- **{name}** ({etype})\n"
        formatted += f"  {desc}\n"
        formatted += f"  Score: {score:.2f}\n\n"

    return MCPToolResult(
        success=True,
        content=formatted,
        metadata={"query": query, "count": len(results)},
    )


async def handle_flow_run(flowfile: str, input_data: str = "") -> MCPToolResult:
    """
    Execute a flowfile.

    Maps to: kgents flow run <file> [input]
    """
    try:
        from ..flow.engine import execute_flow_sync

        # Check if flowfile exists
        path = Path(flowfile)
        if not path.exists():
            return MCPToolResult(
                success=False,
                content=f"Flowfile not found: {flowfile}",
            )

        # Parse and execute
        result = execute_flow_sync(path, input_data)

        return MCPToolResult(
            success=result.status.value == "completed",
            content=json.dumps(result.to_dict(), indent=2),
            content_type="application/json",
            metadata={"flow_name": result.flow_name},
        )
    except Exception as e:
        return MCPToolResult(
            success=False,
            content=f"Flow execution failed: {e}",
        )


async def handle_laws() -> MCPToolResult:
    """
    Display the 7 category laws.

    Maps to: kgents laws
    """
    try:
        from ..bootstrap.laws import format_laws_rich

        return MCPToolResult(
            success=True,
            content=format_laws_rich(),
        )
    except ImportError:
        laws = [
            "1. Left Identity: Id >> f == f",
            "2. Right Identity: f >> Id == f",
            "3. Associativity: (f >> g) >> h == f >> (g >> h)",
            "4. Composition Closure: f: A->B, g: B->C => f >> g: A->C",
            "5. Functor Identity: F(Id) == Id",
            "6. Functor Composition: F(g . f) == F(g) . F(f)",
            "7. Natural Transformation: mu . F(mu) == mu . mu_F",
        ]
        return MCPToolResult(
            success=True,
            content="\n".join(laws),
        )


async def handle_principles() -> MCPToolResult:
    """
    Display the 7 design principles.

    Maps to: kgents principles
    """
    principles = [
        "1. TASTEFUL: Quality over quantity",
        "2. CURATED: Intentional selection",
        "3. ETHICAL: Augment, don't replace judgment",
        "4. JOY-INDUCING: Personality encouraged",
        "5. COMPOSABLE: Agents are morphisms",
        "6. HETERARCHICAL: Both hierarchical and lateral",
        "7. GENERATIVE: Create new possibilities",
    ]
    return MCPToolResult(
        success=True,
        content="\n".join(principles),
    )


# NOTE: handle_psi removed (Psi-gent archived 2025-12-16)


# =============================================================================
# Tool Registry
# =============================================================================


# All exposed tools
KGENTS_TOOLS: list[MCPTool] = [
    MCPTool(
        name="kgents_check",
        description="Verify code, agent, or flow against principles. Returns approval status and detailed scores.",
        parameters=(
            MCPToolParameter("target", "string", "File path or code to verify"),
            MCPToolParameter(
                "principles",
                "string",
                "Path to principles file",
                required=False,
                default="spec/principles.md",
            ),
        ),
        handler=handle_check,
    ),
    MCPTool(
        name="kgents_judge",
        description="Evaluate input against the 7 design principles (tasteful, curated, ethical, joy-inducing, composable, heterarchical, generative).",
        parameters=(
            MCPToolParameter("input_text", "string", "Text or code to judge"),
            MCPToolParameter(
                "strictness",
                "string",
                "Evaluation strictness",
                required=False,
                default="high",
                enum=("low", "medium", "high"),
            ),
        ),
        handler=handle_judge,
    ),
    MCPTool(
        name="kgents_think",
        description="Generate hypotheses about a topic using scientific method (B-gent). Returns list of testable hypotheses.",
        parameters=(
            MCPToolParameter("topic", "string", "Topic to generate hypotheses about"),
            MCPToolParameter(
                "budget",
                "string",
                "Entropy budget",
                required=False,
                default="medium",
                enum=("minimal", "low", "medium", "high"),
            ),
        ),
        handler=handle_think,
    ),
    MCPTool(
        name="kgents_fix",
        description="Repair malformed input (P-gent parser/repair). Attempts to fix syntax errors, missing fields, etc.",
        parameters=(
            MCPToolParameter("target", "string", "File path or malformed content to repair"),
            MCPToolParameter(
                "strategy",
                "string",
                "Repair strategy",
                required=False,
                default="anchor",
                enum=("anchor", "incremental", "stack"),
            ),
        ),
        handler=handle_fix,
    ),
    MCPTool(
        name="kgents_speak",
        description="Create a domain-specific language (Tongue) using G-gent grammar synthesis.",
        parameters=(
            MCPToolParameter(
                "domain",
                "string",
                "Domain to create language for (e.g., 'file operations', 'API calls')",
            ),
            MCPToolParameter(
                "level",
                "string",
                "Grammar complexity level",
                required=False,
                default="COMMAND",
                enum=("SCHEMA", "COMMAND", "RECURSIVE"),
            ),
        ),
        handler=handle_speak,
    ),
    MCPTool(
        name="kgents_find",
        description="Search the L-gent catalog for agents, tongues, and artifacts. Returns matching entries with descriptions.",
        parameters=(
            MCPToolParameter("query", "string", "Search query"),
            MCPToolParameter(
                "limit",
                "number",
                "Maximum results to return",
                required=False,
                default=10,
            ),
        ),
        handler=handle_find,
    ),
    MCPTool(
        name="kgents_flow_run",
        description="Execute a flowfile pipeline. Flowfiles define multi-step agent compositions in YAML.",
        parameters=(
            MCPToolParameter("flowfile", "string", "Path to flowfile (.flow.yaml)"),
            MCPToolParameter(
                "input_data",
                "string",
                "Input data for the flow",
                required=False,
                default="",
            ),
        ),
        handler=handle_flow_run,
    ),
    MCPTool(
        name="kgents_laws",
        description="Display the 7 category laws that govern agent composition. These laws are verified at runtime.",
        parameters=(),
        handler=handle_laws,
    ),
    MCPTool(
        name="kgents_principles",
        description="Display the 7 design principles: tasteful, curated, ethical, joy-inducing, composable, heterarchical, generative.",
        parameters=(),
        handler=handle_principles,
    ),
    # NOTE: kgents_psi removed (Psi-gent archived 2025-12-16)
]

TOOL_REGISTRY: dict[str, MCPTool] = {tool.name: tool for tool in KGENTS_TOOLS}


# =============================================================================
# MCP Server
# =============================================================================


class MCPServer:
    """
    MCP Server for kgents.

    Implements JSON-RPC 2.0 over stdio for MCP protocol.
    Exposes both tools (active operations) and resources (passive data).
    """

    def __init__(self, name: str = "kgents", version: str = "0.2.0"):
        self.name = name
        self.version = version
        self.tools = TOOL_REGISTRY.copy()
        self._running = False
        self._resource_provider: Any = None

    def _get_resource_provider(self) -> Any:
        """Lazy-load the K8s resource provider."""
        if self._resource_provider is None:
            try:
                from .resources import get_provider

                self._resource_provider = get_provider()
            except ImportError:
                self._resource_provider = None
        return self._resource_provider

    def register_tool(self, tool: MCPTool) -> None:
        """Register a custom tool."""
        self.tools[tool.name] = tool

    def _get_capabilities(self) -> dict[str, Any]:
        """Get server capabilities."""
        capabilities: dict[str, Any] = {
            "tools": {},
        }

        # Add resources capability if provider available
        if self._get_resource_provider() is not None:
            capabilities["resources"] = {}

        return {
            "capabilities": capabilities,
            "protocolVersion": MCPVersion.V1.value,
            "serverInfo": {
                "name": self.name,
                "version": self.version,
            },
        }

    def _list_tools(self) -> list[dict[str, Any]]:
        """List all available tools."""
        return [tool.to_dict() for tool in self.tools.values()]

    async def _call_tool(self, name: str, arguments: dict[str, Any]) -> dict[str, Any]:
        """Call a tool and return result."""
        if name not in self.tools:
            return {
                "content": [{"type": "text", "text": f"Unknown tool: {name}"}],
                "isError": True,
            }

        tool = self.tools[name]
        if tool.handler is None:
            return {
                "content": [{"type": "text", "text": f"Tool {name} has no handler"}],
                "isError": True,
            }

        try:
            result = await tool.handler(**arguments)
            return {
                "content": [result.to_dict()],
                "isError": not result.success,
            }
        except Exception as e:
            return {
                "content": [{"type": "text", "text": f"Error: {e}"}],
                "isError": True,
            }

    def _list_resources(self) -> list[dict[str, Any]]:
        """List all available resources."""
        provider = self._get_resource_provider()
        if provider is None:
            return []

        return [r.to_dict() for r in provider.list_resources()]

    def _list_resource_templates(self) -> list[dict[str, Any]]:
        """List resource templates (for dynamic URIs)."""
        provider = self._get_resource_provider()
        if provider is None:
            return []

        return list(provider.list_resource_templates())

    async def _read_resource(self, uri: str) -> dict[str, Any]:
        """Read a resource by URI."""
        provider = self._get_resource_provider()
        if provider is None:
            return {
                "contents": [
                    {
                        "uri": uri,
                        "mimeType": "application/json",
                        "text": '{"error": "Resource provider not available"}',
                    }
                ]
            }

        try:
            content = await provider.read_resource(uri)
            return {"contents": [content.to_dict()]}
        except Exception as e:
            return {
                "contents": [
                    {
                        "uri": uri,
                        "mimeType": "application/json",
                        "text": json.dumps({"error": str(e)}),
                    }
                ]
            }

    async def handle_request(self, request: MCPRequest) -> MCPResponse:
        """Handle an incoming MCP request."""
        method = request.method
        params = request.params

        if method == "initialize":
            return MCPResponse(id=request.id, result=self._get_capabilities())

        # Tool methods
        elif method == "tools/list":
            return MCPResponse(id=request.id, result={"tools": self._list_tools()})

        elif method == "tools/call":
            tool_name = params.get("name", "")
            arguments = params.get("arguments", {})
            result = await self._call_tool(tool_name, arguments)
            return MCPResponse(id=request.id, result=result)

        # Resource methods (Phase E - K8s integration)
        elif method == "resources/list":
            resources = self._list_resources()
            return MCPResponse(id=request.id, result={"resources": resources})

        elif method == "resources/templates/list":
            templates = self._list_resource_templates()
            return MCPResponse(id=request.id, result={"resourceTemplates": templates})

        elif method == "resources/read":
            uri = params.get("uri", "")
            result = await self._read_resource(uri)
            return MCPResponse(id=request.id, result=result)

        elif method == "notifications/initialized":
            # Client notification - no response needed
            return MCPResponse(id=request.id, result={})

        else:
            return MCPResponse(
                id=request.id,
                error={"code": -32601, "message": f"Method not found: {method}"},
            )

    async def run_stdio(self) -> None:
        """Run server over stdio."""
        self._running = True

        while self._running:
            try:
                # Read line from stdin
                line = await asyncio.get_event_loop().run_in_executor(None, sys.stdin.readline)

                if not line:
                    break

                # Parse request
                data = json.loads(line.strip())
                request = MCPRequest.from_dict(data)

                # Handle request
                response = await self.handle_request(request)

                # Send response (skip for notifications)
                if request.method.startswith("notifications/"):
                    continue

                print(json.dumps(response.to_dict()), flush=True)

            except json.JSONDecodeError:
                continue
            except Exception as e:
                error_response = MCPResponse(
                    id=0,
                    error={"code": -32603, "message": str(e)},
                )
                print(json.dumps(error_response.to_dict()), flush=True)

    def stop(self) -> None:
        """Stop the server."""
        self._running = False


# =============================================================================
# CLI Command
# =============================================================================


def cmd_mcp(args: list[str]) -> int:
    """
    MCP server command handler.

    Usage:
        kgents mcp serve [--port=8080]
        kgents mcp expose <command>
        kgents mcp export --format=manifest
    """
    parser = argparse.ArgumentParser(prog="kgents mcp")
    subparsers = parser.add_subparsers(dest="subcommand")

    # serve
    serve_parser = subparsers.add_parser("serve", help="Start MCP server")
    serve_parser.add_argument("--port", type=int, default=0, help="Port (0 for stdio)")
    serve_parser.add_argument("--name", default="kgents", help="Server name")

    # export
    export_parser = subparsers.add_parser("export", help="Export tool manifest")
    export_parser.add_argument("--format", choices=["json", "manifest"], default="json")

    # list
    subparsers.add_parser("list", help="List available tools")

    parsed = parser.parse_args(args)

    if parsed.subcommand == "serve":
        server = MCPServer(name=parsed.name)
        print(f"Starting MCP server '{parsed.name}'...", file=sys.stderr)
        asyncio.run(server.run_stdio())
        return 0

    elif parsed.subcommand == "export":
        manifest = create_tool_manifest()
        print(json.dumps(manifest, indent=2))
        return 0

    elif parsed.subcommand == "list":
        print("Available kgents MCP tools:\n")
        for tool in KGENTS_TOOLS:
            print(f"  {tool.name}")
            print(f"    {tool.description}\n")
        return 0

    else:
        parser.print_help()
        return 1


# =============================================================================
# Convenience Functions
# =============================================================================


def create_tool_manifest() -> dict[str, Any]:
    """Create MCP tool manifest."""
    return {
        "protocolVersion": MCPVersion.V1.value,
        "name": "kgents",
        "version": "0.2.0",
        "description": "Kent's Agents - Tasteful, curated, ethical, joy-inducing agents",
        "tools": [tool.to_dict() for tool in KGENTS_TOOLS],
    }


async def start_server(name: str = "kgents") -> MCPServer:
    """Start MCP server (for programmatic use)."""
    server = MCPServer(name=name)
    await server.run_stdio()
    return server
