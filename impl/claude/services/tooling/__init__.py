"""
U-gent Tool Infrastructure: Tools as First-Class Morphisms.

The key insight from Claude Code: tools are well-engineered but imperative.
The kgents opportunity: tools as first-class morphisms in the agent category.

CLAUDE CODE MODEL                    KGENTS MODEL
-----------------                    ------------
result = agent.call_tool(...)        pipeline = search >> summarize >> write
result = agent.call_tool(...)  vs    result = await pipeline.invoke(input)
result = agent.call_tool(...)

Imperative, sequential               Categorical, composable

This module provides:
- Tool[A, B]: Base protocol for all tools (categorical morphism)
- ToolMeta: Metadata for registered tools
- ToolRegistry: Central registry with trust-gated discovery
- ToolExecutor: Async execution with tracing and timeout

AGENTESE Paths:
- world.tools.file.* - Filesystem operations (read, write, edit, glob)
- world.tools.search.* - Search operations (grep, lsp)
- world.tools.system.* - System interaction (bash, kill)
- world.tools.web.* - Network operations (fetch, search)
- self.tools.task.* - Task management (todo)
- self.tools.mode.* - Modal transitions (plan, execute)

Trust Gating:
- L0: Read-only tools (read, glob, grep)
- L1: Bounded writes (.kgents/ only)
- L2: Write tools with confirmation (write, edit)
- L3: System tools (bash, web.fetch)

Philosophy:
    "A tool is not an external function. It is an agent with a contract."

See: spec/services/tooling.md
See: docs/skills/metaphysical-fullstack.md
See: docs/skills/crown-jewel-patterns.md
"""

from .base import (
    Tool,
    ToolCategory,
    ToolEffect,
    ToolError,
    ToolResult,
)
from .contracts import (
    # File tools
    EditRequest,
    EditResponse,
    FileContent,
    GlobQuery,
    GlobResponse,
    GrepQuery,
    GrepResponse,
    ReadRequest,
    # Manifest
    ToolManifestResponse,
    ToolMetaItem,
    WriteRequest,
    WriteResponse,
)
from .executor import (
    ExecutionContext,
    ToolExecutor,
)
from .orchestrator import (
    DAGNode,
    OrchestratorResult,
    ParallelRequest,
    ParallelResponse,
    ParallelTool,
    ToolOrchestrator,
)
from .registry import (
    DuplicateToolError,
    ToolMeta,
    ToolNotFoundError,
    ToolRegistry,
    get_registry,
    reset_registry,
)
from .trust_gate import (
    GateResult,
    ToolTrustGate,
    TrustViolation,
)

__all__ = [
    # Base
    "Tool",
    "ToolCategory",
    "ToolEffect",
    "ToolError",
    "ToolResult",
    # Registry
    "ToolMeta",
    "ToolRegistry",
    "DuplicateToolError",
    "ToolNotFoundError",
    "get_registry",
    "reset_registry",
    # Executor
    "ToolExecutor",
    "ExecutionContext",
    # Trust Gate
    "ToolTrustGate",
    "GateResult",
    "TrustViolation",
    # Contracts
    "ReadRequest",
    "FileContent",
    "WriteRequest",
    "WriteResponse",
    "EditRequest",
    "EditResponse",
    "GlobQuery",
    "GlobResponse",
    "GrepQuery",
    "GrepResponse",
    "ToolManifestResponse",
    "ToolMetaItem",
    # Orchestrator
    "ToolOrchestrator",
    "OrchestratorResult",
    "DAGNode",
    "ParallelTool",
    "ParallelRequest",
    "ParallelResponse",
]
