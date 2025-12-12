"""
U-gents: Utility Agents for External Tool Use

U-gents are boundary morphisms: U: Cat_Agent -> Cat_Tool
They bridge the agent category to external systems.

Categorical Distinction:
- T-gents: Endofunctors (stay within agent category)
- U-gents: Boundary morphisms (cross to external tools)

Types:
- Type I (Core): Tool[A,B], ToolMeta, ToolError
- Type II (Wrappers): TracedTool, CachedTool, RetryTool
- Type III (Execution): ToolExecutor, CircuitBreaker
- Type IV (MCP): MCPClient, MCPTool, transports
- Type V (Security): PermissionClassifier, AuditLogger
- Type VI (Orchestration): Parallel, Supervisor, Handoff

Usage:
    from agents.u import Tool, ToolMeta, MCPClient

    # Define a tool
    class SearchTool(Tool[Query, Results]):
        meta = ToolMeta.minimal("search", "Search the web", Query, Results)

        async def invoke(self, query: Query) -> Results:
            ...

    # Compose tools
    pipeline = parse >> search >> summarize

    # Execute
    result = await pipeline.invoke(user_input)
"""

# Type I - Core
from .core import (
    CachedTool,
    PassthroughTool,
    RetryTool,
    Tool,
    ToolError,
    ToolErrorType,
    ToolIdentity,
    ToolInterface,
    ToolMeta,
    ToolRuntime,
    ToolTrace,
    TracedTool,
)

# Type III - Execution
from .executor import (
    CircuitBreakerConfig,
    CircuitBreakerError,
    CircuitBreakerState,
    CircuitBreakerTool,
    CircuitState,
    RetryConfig,
    RetryExecutor,
    RobustToolExecutor,
    SecureToolExecutor,
    ToolExecutor,
)

# Type IV - MCP
from .mcp import (
    HttpSseTransport,
    JsonRpcError,
    JsonRpcRequest,
    JsonRpcResponse,
    MCPClient,
    MCPResource,
    MCPServerInfo,
    MCPTool,
    MCPToolSchema,
    MCPTransport,
    MCPTransportType,
    StdioTransport,
)

# Type VI - Orchestration
from .orchestration import (
    CostBasedSelection,
    DynamicToolSelector,
    EnvironmentBasedSelection,
    HandoffCondition,
    HandoffPattern,
    HandoffRule,
    LatencyBasedSelection,
    ParallelOrchestrator,
    ParallelResult,
    SelectionContext,
    SelectionStrategy,
    SequentialOrchestrator,
    SupervisorPattern,
    Task,
    WorkerAssignment,
)

# Type V - Security
from .permissions import (
    AgentContext,
    AuditLog,
    AuditLogger,
    PermissionClassifier,
    PermissionLevel,
    SecurityLevel,
    SensitivityLevel,
    TemporaryToken,
    ToolCapabilities,
)

# Registry
from .registry import (
    ToolEntry,
    ToolRegistry,
    get_registry,
    set_registry,
)

__all__ = [
    # Type I - Core
    "Tool",
    "ToolMeta",
    "ToolIdentity",
    "ToolInterface",
    "ToolRuntime",
    "ToolError",
    "ToolErrorType",
    "ToolTrace",
    "PassthroughTool",
    # Type II - Wrappers
    "TracedTool",
    "CachedTool",
    "RetryTool",
    # Type III - Execution
    "CircuitState",
    "CircuitBreakerConfig",
    "CircuitBreakerState",
    "CircuitBreakerError",
    "CircuitBreakerTool",
    "ToolExecutor",
    "RetryExecutor",
    "RobustToolExecutor",
    "SecureToolExecutor",
    "RetryConfig",
    # Type IV - MCP
    "MCPTransportType",
    "MCPServerInfo",
    "MCPToolSchema",
    "MCPResource",
    "JsonRpcRequest",
    "JsonRpcResponse",
    "JsonRpcError",
    "MCPTransport",
    "StdioTransport",
    "HttpSseTransport",
    "MCPClient",
    "MCPTool",
    # Type V - Security
    "PermissionLevel",
    "SecurityLevel",
    "SensitivityLevel",
    "AgentContext",
    "ToolCapabilities",
    "TemporaryToken",
    "PermissionClassifier",
    "AuditLogger",
    "AuditLog",
    # Type VI - Orchestration
    "SequentialOrchestrator",
    "ParallelOrchestrator",
    "ParallelResult",
    "SupervisorPattern",
    "Task",
    "WorkerAssignment",
    "HandoffPattern",
    "HandoffCondition",
    "HandoffRule",
    "DynamicToolSelector",
    "SelectionContext",
    "SelectionStrategy",
    "CostBasedSelection",
    "LatencyBasedSelection",
    "EnvironmentBasedSelection",
    # Registry
    "ToolRegistry",
    "ToolEntry",
    "get_registry",
    "set_registry",
]
