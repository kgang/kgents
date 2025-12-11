# U-gents: The Algebra of Utility

The letter **U** represents **Utility** agents—typed morphisms specialized for external interaction through composable tool interfaces.

> *"A tool is not an external function. It is an agent with a contract."*

---

## Philosophy

Traditional agent frameworks treat tools as **opaque function calls**:
```python
# Traditional approach (non-compositional)
result = agent.call_tool("search", {"query": "MCP protocol"})
```

**kgents approach**: Tools are **morphisms in the agent category**:
```python
# Categorical approach (compositional)
search_tool: Tool[SearchQuery, SearchResults]
pipeline = parse_query >> search_tool >> format_results
```

### Why This Matters

1. **Composition is Primary**: Tools compose via `>>` like all agents
2. **Type Safety**: Schema validation as morphism typing
3. **Unified Abstraction**: Tools are agents; agents use tools
4. **Category Laws Apply**: Associativity, identity verified

---

## The Six Types

U-gents are categorized into six types based on their role in tool composition:

| Type | Name | Purpose |
|------|------|---------|
| I | Core | `Tool[A,B]`, ToolMeta, PassthroughTool |
| II | Wrappers | TracedTool, CachedTool, RetryTool |
| III | Execution | ToolExecutor, CircuitBreaker, RetryExecutor |
| IV | MCP | MCPClient, MCPTool, Transports |
| V | Security | PermissionClassifier, AuditLogger |
| VI | Orchestration | ParallelOrchestrator, Supervisor, Handoff |

---

## Type I: Core

The foundational types for tool definition.

### Tool[A, B]

Every tool is a typed morphism with explicit domain and codomain:

```python
@dataclass
class Tool(Agent[Input, Output]):
    """
    A tool is an agent specialized for external interaction.

    Category Theory:
    - Object: Types (Input, Output)
    - Morphism: Tool execution (Input → Output)
    - Identity: PassthroughTool
    - Composition: Sequential tool chains
    """

    input_schema: type[Input]
    output_schema: type[Output]
    name: str
    description: str
```

**Type Safety Guarantee**:
```python
tool_a: Tool[A, B]
tool_b: Tool[B, C]
pipeline = tool_a >> tool_b  # Tool[A, C] ✓

tool_c: Tool[D, E]
pipeline = tool_a >> tool_c  # Type error: B ≠ D ✗
```

---

## Type II: Wrappers

Decorators that add cross-cutting concerns while preserving the tool signature.

| Wrapper | Purpose |
|---------|---------|
| **TracedTool** | W-gent integration for observability |
| **CachedTool** | D-gent integration for prompt caching (90% cost reduction) |
| **RetryTool** | Exponential backoff for transient errors |

```python
# Composition of wrappers
robust_search = TracedTool(
    CachedTool(
        RetryTool(web_search, max_retries=3),
        cache=d_gent_cache
    ),
    tracer=w_gent_tracer
)
```

---

## Type III: Execution

Runtime infrastructure for tool invocation with error handling.

### ToolExecutor

```python
class ToolExecutor:
    """Execute tools with Result monad error handling."""

    async def execute(
        self,
        tool: Tool[Input, Output],
        input: Input,
        context: ExecutionContext
    ) -> Result[Output, ToolError]:
        # Check cache, validate, execute, trace
        ...
```

### CircuitBreaker

Stop calling failing tools after N consecutive failures:

```python
class CircuitBreaker:
    """Circuit breaker pattern for tools."""

    states: ["CLOSED", "OPEN", "HALF_OPEN"]
    failure_threshold: int = 5
    recovery_timeout: float = 30.0
```

---

## Type IV: MCP

Integration with **Model Context Protocol**, the industry-standard tool interface.

| MCP Primitive | kgents Equivalent |
|---------------|-------------------|
| Tool | `Tool[Input, Output]` |
| Resource | `DataSource[Query, Data]` |
| Prompt | `PromptTemplate[Params, str]` |
| Server | ToolRegistry |
| Client | Agent invoking tools |

```python
# Connect to MCP server
client = MCPClient(server="localhost:8080")
tools = await client.list_tools()

# Invoke MCP tool
result = await client.invoke("search", {"query": "..."})
```

---

## Type V: Security

Permission model and audit logging.

### PermissionClassifier

Implements Attribute-Based Access Control (ABAC):

```python
class PermissionClassifier:
    """Classify tool as allowed/denied based on context."""

    def classify(self, tool: Tool, context: AgentContext) -> Permission:
        # Check security level, time, data sensitivity
        ...

    def grant_temporary(self, tool: Tool, duration: int = 900) -> Token:
        # Short-lived token (15-60 minutes)
        # Zero standing privileges
        ...
```

### AuditLogger

Complete execution trace for compliance:

```python
@dataclass
class AuditEntry:
    tool_name: str
    agent_id: str
    input: Any
    output: Result[Any, Error]
    timestamp: datetime
    permissions: list[str]
```

---

## Type VI: Orchestration

Multi-tool patterns as functors.

| Pattern | Category Theory | Description |
|---------|-----------------|-------------|
| Sequential | Functor composition | `f >> g >> h` |
| Parallel | Product functor | `f × g × h` |
| Fallback | Coproduct | `f + g + h` (try in order) |
| Supervisor | Comma category | Central coordinator |
| Handoff | Natural transformation | Transfer control |

```python
# Parallel: Run tools concurrently, merge results
gather_context = (search_web × search_docs × search_memory) >> merge

# Fallback: Try tools in order until success
robust_search = google + bing + duckduckgo
```

---

## Integration Points

### With P-gents (Parser)

Four parsing boundaries:
1. **Schema Parsing**: MCP → kgents Tool
2. **Input Parsing**: NL → Tool parameters
3. **Output Parsing**: Tool response → Structured data
4. **Error Parsing**: Errors → Recoverable/Fatal

### With D-gents (Data)

- **Prompt Caching**: 90% cost reduction for repeated contexts
- **Tool State**: Persistent configuration
- **Execution History**: Tool usage traces

### With L-gents (Library)

- **Tool Discovery**: Search by type signature
- **Composition Planning**: Find tool chains via graph search
- **Version Management**: Tool evolution

### With W-gents (Wire Observation)

- **Live Monitoring**: Real-time tool execution dashboard
- **Trace Emission**: OpenTelemetry integration
- **Performance Profiling**: Latency, cost, success rate

### With T-gents (Testing)

T-gents test U-gents via the same patterns:
- **MockAgent** simulates tools for testing
- **SpyAgent** observes tool execution
- **FlakyAgent** tests retry logic

---

## Specifications

| Document | Description |
|----------|-------------|
| [tool-use.md](tool-use.md) | Full specification (1380 lines) |
| [core.md](core.md) | Type I: Tool[A,B] base class |
| [mcp.md](mcp.md) | Type IV: MCP protocol integration |
| [execution.md](execution.md) | Type III: ToolExecutor, CircuitBreaker |

---

## Design Principles

### 1. Tools as Typed Morphisms

Every tool has explicit domain and codomain. Composition only succeeds if types align.

### 2. Parser-First Design

Every tool co-designed with P-gent parser. Graceful degradation on malformed outputs.

### 3. Monadic Error Handling

Result monad + Railway Oriented Programming. Type-safe error composition.

### 4. MCP Native

Industry-standard protocol as compositional substrate. Universal interoperability.

### 5. Observability via Traced Categories

Every execution is traced via W-gent. Full visibility into tool call trees.

---

## Principles Alignment

| Principle | How U-gent Aligns |
|-----------|-------------------|
| **Tasteful** | Single purpose: external interaction via tools |
| **Curated** | Six types, not sprawl |
| **Ethical** | Permission model, audit logging |
| **Composable** | Tools compose via `>>` |
| **Generative** | Regenerable from spec |

---

## Migration Note

> **Former "Understudy" content**: The U-gent letter previously specified knowledge distillation ("The Understudy"). That content has been migrated to [B-gent/distillation.md](../b-gents/distillation.md) as it is fundamentally an *economic optimization*, not a core agent capability. U now represents **Utility** agents—the Tool Use framework.

---

## See Also

- [tool-use.md](tool-use.md) - Full tool use specification
- [../t-gents/](../t-gents/) - T-gents: Testing (test U-gent tools)
- [../p-gents/](../p-gents/) - P-gents: Parser integration
- [../d-gents/](../d-gents/) - D-gents: Caching integration
- [../l-gents/](../l-gents/) - L-gents: Tool discovery
- [../w-gents/](../w-gents/) - W-gents: Observability
- [../b-gents/distillation.md](../b-gents/distillation.md) - Distillation (former Understudy)

---

*"A tool is not an external function. It is an agent with a contract."*
