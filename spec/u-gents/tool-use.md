# U-gents: Tool Use as Categorical Composition

**Status**: Standard
**Date**: 2025-12-08 (distilled: 2025-12-17)
**Implementation**: `impl/claude/agents/u/`

---

## Purpose

U-gents provide composable, category-theoretic tool capabilities for all kgents agents. Unlike traditional frameworks that bolt tool use onto existing systems, **tools are morphisms** that compose via categorical laws, enabling algebraic reliability, type-safe execution, and parser integration.

**Core Innovation**: Tools compose via `>>` just like agents, creating a unified mathematical foundation where tools ARE agents and agents USE tools recursively.

---

## Philosophy: Tools as Morphisms

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

**1. Composition is Primary**
- Tools compose via `>>` like all agents
- Categorical laws (associativity, identity) apply
- Type safety via morphism signatures

**2. Testing Integration**
- T-gents test U-gent tools via existing patterns
- MockAgent, SpyAgent, FlakyAgent work for tools
- No separate testing framework needed

**3. Unified Framework**
- No separate "tool calling" subsystem
- Tools are agents; agents use tools
- Recursive elegance: agents made of agents

---

## Design Principles

### Principle 1: Tools as Typed Morphisms

Every tool is a morphism with explicit domain and codomain:

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
    server: Optional[str] = None  # MCP server if remote

    async def invoke(self, input: Input) -> Output: ...
```

**Type Safety**: Composition only succeeds if types align:
```python
tool_a: Tool[A, B]
tool_b: Tool[B, C]
pipeline = tool_a >> tool_b  # Tool[A, C] ✅

tool_c: Tool[D, E]
pipeline = tool_a >> tool_c  # Type error: B ≠ D ❌
```

### Principle 2: P-gents Parse Everything

Tool use has **four parsing boundaries**:

1. **Schema Parsing**: Tool definitions → Structured schemas
2. **Input Parsing**: Natural language → Tool parameters
3. **Output Parsing**: Tool response → Structured data
4. **Error Parsing**: Tool errors → Recoverable/Fatal classification

Each parser uses P-gent fallback chains for graceful degradation.

### Principle 3: Monadic Error Handling

Tool errors compose via **Result monad**:

```python
# Tool execution returns Result[Output, Error]
result: Result[SearchResults, ToolError] = await search_tool.invoke(query)

# Railway Oriented Programming
pipeline = (
    parse_query           # Result[Query, ParseError]
    >> search_tool        # Result[Results, ToolError]
    >> format_results     # Result[Formatted, FormatError]
)

# Error short-circuits automatically
final: Result[Formatted, Error] = await pipeline.invoke(user_input)
```

**Error Recovery Patterns**:
- **Retry**: Exponential backoff for transient errors
- **Fallback**: Alternative tools when primary fails
- **Repair**: P-gent repairs malformed responses
- **Circuit Breaker**: Stop calling failing tools

### Principle 4: MCP as Universal Protocol

**Model Context Protocol (MCP)** is the industry-standard tool interface:

| MCP Primitive | kgents Equivalent | Category |
|---------------|-------------------|----------|
| **Tool** | `Tool[Input, Output]` | Morphism |
| **Resource** | `DataSource[Query, Data]` | Morphism to data |
| **Prompt** | `PromptTemplate[Params, str]` | Template morphism |
| **Server** | Tool registry/catalog | Category |
| **Client** | Agent invoking tools | Functor |

### Principle 5: Observability via Traced Categories

Every tool execution is **traced**:

```python
@dataclass
class ToolTrace:
    """Trace of tool execution (categorical trace)."""
    tool_name: str
    input: Any
    output: Result[Any, Error]
    start_time: float
    end_time: float
    latency_ms: float
    composition_depth: int  # Depth in pipeline
    parent_trace: Optional[ToolTrace]  # For nested composition
    tokens_used: Optional[int]
    cost_usd: Optional[float]
```

### Principle 6: Dynamic Tool Selection as Functor

Agent **context** determines available tools:

```python
class ToolFunctor:
    """
    Functor from agent contexts to tool categories.

    Maps:
    - AgentContext → Available tools
    - Preserves composition (context transforms preserve tool chains)
    """
    def map_context(self, context: AgentContext) -> ToolCategory: ...
```

**Permission Model**:
- **Zero standing privileges**: Tools granted per-task
- **Short-lived tokens**: 15-60 minute OAuth tokens (never static keys)
- **Attribute-based**: Context-aware permissions (time, location, sensitivity)

---

## Architecture: The Five-Layer Stack

### Layer 1: Tool Definition (Schema Layer)

Tools defined via **typed schemas** (Pydantic):

```python
class SearchQuery(BaseModel):
    query: str = Field(description="Natural language search query")
    max_results: int = Field(default=10, ge=1, le=100)

class SearchResults(BaseModel):
    results: list[SearchResult]
    total_found: int

@tool(
    name="web_search",
    description="Search the web",
    input_schema=SearchQuery,
    output_schema=SearchResults
)
class WebSearchTool(Tool[SearchQuery, SearchResults]):
    async def invoke(self, input: SearchQuery) -> SearchResults: ...
```

**Schema as Type System**:
- Algebraic Data Types: Sum types (A | B), Product types (A × B)
- Validation = Proof: Schema validation proves input conformance
- Composition = Function types: `Tool[A, B] >> Tool[B, C] = Tool[A, C]`

### Layer 2: Tool Registry (Catalog Layer)

Tools catalogued via **L-gent integration**:

```python
class ToolRegistry:
    """
    Central registry for tools (L-gent integration).

    Provides:
    - Tool discovery (search by type signature)
    - Version management (tool evolution)
    - Dependency resolution (tool A requires tool B)
    - Permission management (who can use what)
    """
    async def register(self, tool: Tool) -> ToolEntry: ...
    async def find_by_signature(self, input_type: type, output_type: type) -> list[Tool]: ...
    async def find_composition_path(self, source_type: type, target_type: type) -> Optional[list[Tool]]: ...
```

### Layer 3: Tool Execution (Runtime Layer)

Tool execution uses **Result monad** for error handling:

```python
class ToolExecutor:
    """
    Execute tools with tracing, caching, and error recovery.

    Integrates:
    - W-gents: Observability and tracing
    - D-gents: Prompt caching for repeated calls
    - T-gents: Retry and fallback logic
    """
    async def execute(
        self,
        tool: Tool[Input, Output],
        input: Input,
        context: ExecutionContext
    ) -> Result[Output, ToolError]: ...
```

**Retry Logic**:
- Exponential backoff: 100ms, 200ms, 400ms, ...
- Max attempts: Configurable (default 3)
- Circuit breaker: Stop after N consecutive failures
- Jitter: Random delay to avoid thundering herd

### Layer 4: Tool Composition (Pipeline Layer)

Tools compose via **categorical composition**:

```python
# Sequential composition
search_and_summarize = web_search >> summarize_text

# Parallel composition (product functor)
gather_context = (
    search_web × search_docs × search_memory
) >> merge_results

# Choice composition (coproduct)
robust_search = (
    google_search + bing_search + duckduckgo_search
)  # Try in order until success

# Feedback (traced category)
refine_query = trace(
    lambda q: generate_query(q) >> evaluate_results >> refine(q),
    max_iterations=5
)
```

### Layer 5: Agent Integration (Agentic Layer)

Agents **use tools** via natural composition:

```python
class ResearchAgent(Agent[str, Report]):
    """Research agent using tools compositionally."""

    async def invoke(self, topic: str) -> Report:
        # Search → Read → Summarize → Verify → Synthesize
        search_results = await self.web_search.invoke(SearchQuery(query=topic))
        papers = await asyncio.gather(*[self.read_paper.invoke(r.url) for r in search_results.results])
        summaries = await asyncio.gather(*[self.summarize.invoke(p.content) for p in papers])
        verified = await asyncio.gather(*[self.fact_check.invoke(s) for s in summaries])
        return Report(topic=topic, papers=papers, summaries=verified)
```

**Beyond ReAct**: Compositional tool use, not prompt-driven.

---

## Novel Patterns

### Pattern 1: Tool Specialization via T-gents

Tools extend **T-gent patterns** for domain-specific testing:

```python
# Mock, Spy, Failing, Flaky agents work for tools
mock_search = MockAgent[SearchQuery, SearchResults](output=...)
failing_api = FailingAgent[APIRequest, APIResponse](...)
traced_llm = SpyAgent[Prompt, Completion](label="LLM Calls")
flaky_search = FlakyAgent(wrapped=real_search, probability=0.1)

# Test resilience via composition
test_pipeline = parse_query >> failing_api >> traced_llm >> flaky_search
```

**Unique to kgents**: Testing and tool use unified as composable morphisms.

### Pattern 2: Parser-Tool Codesign

Every tool **co-designed with parser**:

```python
@tool(
    name="hypothesis_generator",
    parser=HypothesisParser()  # ← P-gent handles parsing
)
class HypothesisGeneratorTool(Tool[HypothesisRequest, HypothesisOutput]):
    async def invoke(self, input: HypothesisRequest) -> HypothesisOutput:
        response = await self.llm.generate(prompt=build_prompt(input))
        parsed = await self.parser.parse(response)

        # Graceful degradation if malformed
        if not parsed.success:
            repaired = await self.parser.repair(response)
            return repaired.value

        return parsed.value
```

**Unique to kgents**: Tools don't fail on malformed output—they degrade gracefully.

### Pattern 3: Categorical Prompt Caching

Prompt caching as **memoization functor**:

```python
class CachedTool(Tool[Input, Output]):
    """
    Tool with prompt caching (memoization functor).

    Category Theory:
    - Original functor: F: Context → Response
    - Memoized functor: Memo(F): Context → Cached[Response]
    - Natural transformation: η: Memo(F) → F (cache lookup)
    """
    async def invoke(self, input: Input) -> Output: ...
```

**Cost Savings**: Up to 90% for repeated contexts (10% cache read vs 100% base price).

### Pattern 4: Functorial Multi-Tool Orchestration

Multi-tool patterns as **functors between categories**:

- **Sequential**: Functor composition
- **Parallel**: Product functor (monoidal product)
- **Supervisor**: Comma category construction
- **Handoff**: Natural transformation

**Unique to kgents**: Orchestration derived from category theory, not ad-hoc.

### Pattern 5: Security as Subobject Classifier

Tool permissions via **subobject classifiers**:

```python
class PermissionClassifier:
    """
    Subobject classifier for tool permissions.

    Category Theory:
    - Objects: Tool capabilities
    - Subobjects: Permitted tool subsets
    - Classifier: Ω (permission oracle)
    - Characteristic morphism: χ: Tool → {allowed, denied}
    """
    def classify(self, tool: Tool, context: AgentContext) -> Permission: ...
    def grant_temporary(self, tool: Tool, context: AgentContext, duration_seconds: int = 900) -> TemporaryToken: ...
```

**Unique to kgents**: Security derived from categorical foundations.

---

## Integration with Existing Genera

### With P-gents (Parser)
- **Schema Parsing**: MCP tool definitions → kgents Tool
- **Input Parsing**: Natural language → Tool parameters
- **Output Parsing**: Tool response → Structured data
- **Error Parsing**: Tool errors → Recovery strategy

### With D-gents (Data)
- **Tool State**: Persistent tool configuration
- **Prompt Caching**: Cache tool contexts (90% cost reduction)
- **Execution History**: Track tool usage

### With L-gents (Library)
- **Tool Discovery**: Register/find tools by type signature
- **Composition Planning**: Find tool chains via graph search
- **Semantic Search**: Keyword/embedding search

### With T-gents (Testing)
- **Mock Tools**: MockAgent for testing
- **Spy Tools**: SpyAgent for observability
- **Flaky Tools**: FlakyAgent for chaos testing
- **Failing Tools**: FailingAgent for resilience testing

### With Bootstrap Agents
- **Compose**: Tools compose via `>>`
- **Judge**: Tools evaluated via 7 principles
- **Ground**: Tools grounded in persona preferences
- **Fix**: Iterative tool refinement

See `impl/claude/agents/u/` for full integration examples.

---

## Categorical Laws

### Identity Law
```python
identity_tool >> tool == tool
tool >> identity_tool == tool
```

### Associativity Law
```python
(tool_a >> tool_b) >> tool_c == tool_a >> (tool_b >> tool_c)
```

### Functor Laws (for ToolRegistry)
```python
# Identity: registry.map(id) == id
registry.find_composition_path(A, A) == [identity_tool]

# Composition: registry.map(f >> g) == registry.map(f) >> registry.map(g)
registry.find_composition_path(A, C) ==
    registry.find_composition_path(A, B) + registry.find_composition_path(B, C)
```

---

## Anti-Patterns

### Don't: Opaque Tool Calls
```python
# ❌ Loses composability
result = agent.call_tool("search", {"query": "..."})
```

### Don't: Exception-Based Error Handling
```python
# ❌ Breaks composition, no type safety
try:
    result = tool.invoke(input)
except ToolError:
    fallback()
```

### Don't: Static Tool Lists
```python
# ❌ Ignores context, no dynamic selection
tools = [search, summarize, verify]  # Same for all agents
```

### Don't: Manual Retry Logic
```python
# ❌ Boilerplate, error-prone
for i in range(3):
    try:
        return tool.invoke(input)
    except TransientError:
        time.sleep(2 ** i)
```

### Don't: Skip Parsers
```python
# ❌ Fragile, no graceful degradation
output = json.loads(tool_response)  # Fails on malformed JSON
```

---

## Implementation Reference

See `impl/claude/agents/u/` for production implementation:

- `core.py`: Tool base types and composition
- `executor.py`: Execution with retry/cache/trace
- `mcp.py`: MCP protocol integration
- `orchestration.py`: Multi-tool patterns (sequential, parallel, supervisor)
- `permissions.py`: Permission classifier and ABAC
- `registry.py`: Tool catalog and discovery
- `state.py`: Tool state management
- `_tests/`: Comprehensive test suite

---

**End of U-gents Specification**

**Version**: 2.0 (Distilled)
**Lines**: ~350
**Principle**: "Spec is compression. If you can't compress it, you don't understand it."
