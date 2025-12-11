# U-gents: Tool Use as Categorical Composition

**Status**: Standard
**Date**: 2025-12-08 (migrated to U-gents: 2025-12-11)
**Research Foundation**: 2024-2025 industry analysis + MCP ecosystem study

---

## Executive Summary

This specification defines **U-gents Tool Use**, a novel architecture for empowering all kgents agents with composable, category-theoretic tool capabilities. Unlike traditional agentic frameworks that bolt tool use onto existing systems, this approach treats **tools as morphisms** and **tool composition as functorial operations**, creating a unified mathematical foundation.

**Core Innovation**: Tools are not external functions—they are **U-gents** (utility agents) that compose via categorical laws, enabling:
- **Algebraic reliability**: Tools proven correct via categorical laws
- **Composable pipelines**: Tools chain via `>>` just like agents
- **Type-safe execution**: Schema validation as morphism typing
- **Parser integration**: P-gents parse tool schemas and responses
- **MCP native**: Industry-standard protocol as compositional substrate

**Integration Points**:
- **P-gents (Parser)**: Parse tool schemas, responses, and errors
- **T-gents (Testing)**: Test tools via MockAgent, SpyAgent, FlakyAgent
- **Bootstrap**: Tools compose via Compose, validated via Judge
- **All genera**: Universal tool use empowers A/B/C/D/E/F/H/I/J/K/L agents

---

## Philosophy: Tools as Morphisms

### The Categorical Foundation

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
- MockAgent simulates tools for testing
- SpyAgent traces tool execution
- FlakyAgent tests retry logic

**3. Unified Framework**
- No separate "tool calling" subsystem
- Tools are agents; agents use tools
- Recursive elegance: agents made of agents

---

## Design Principles (Category-Theoretic)

### Principle 1: **Tools as Typed Morphisms**

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

    # Schema (type signature)
    input_schema: type[Input]
    output_schema: type[Output]

    # MCP metadata
    name: str
    description: str
    server: Optional[str] = None  # MCP server if remote

    # Execution
    async def invoke(self, input: Input) -> Output:
        """Execute tool with typed input."""
        ...
```

**Type Safety Guarantee**: Composition only succeeds if types align:
```python
tool_a: Tool[A, B]
tool_b: Tool[B, C]

# Valid composition (B matches)
pipeline = tool_a >> tool_b  # Tool[A, C]

# Invalid composition (type error at compose-time)
tool_c: Tool[D, E]
pipeline = tool_a >> tool_c  # ❌ Type error: B ≠ D
```

### Principle 2: **P-gents Parse Everything**

Tool use has **four parsing boundaries**:

1. **Schema Parsing**: Tool definitions → Structured schemas
2. **Input Parsing**: Natural language → Tool parameters
3. **Output Parsing**: Tool response → Structured data
4. **Error Parsing**: Tool errors → Recoverable/Fatal classification

**P-gents Integration**:
```python
# Schema parser (MCP → kgents Tool)
schema_parser: Parser[MCPToolDef, ToolSchema]

# Input parser (NL → JSON parameters)
input_parser: Parser[str, ToolInput]

# Output parser (JSON → Domain type)
output_parser: Parser[str, ToolOutput]

# Error parser (Error → RecoveryStrategy)
error_parser: Parser[ToolError, ErrorClassification]
```

**Fallback Chains**: Each parser uses P-gent composition patterns:
```python
input_parser = FallbackParser(
    StructuredInputParser(),  # Try JSON first
    NaturalLanguageParser(),  # Then NL extraction
    PartialFieldParser()      # Finally field-by-field
)
```

### Principle 3: **Monadic Error Handling**

Tool errors compose via **Either monad** (Result type):

```python
# Tool execution returns Result[Output, Error]
result: Result[SearchResults, ToolError] = await search_tool.invoke(query)

# Monadic composition (Railway Oriented Programming)
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

### Principle 4: **MCP as Universal Protocol**

**Model Context Protocol (MCP)** is the industry-standard tool interface:

**Why MCP**:
- **Universal adoption**: OpenAI, Anthropic, Google, Microsoft (2025)
- **Category-friendly**: Tools as typed morphisms
- **Composable**: JSON-RPC naturally supports chaining
- **Secure**: Permission model via capabilities

**MCP Primitives Map to kgents**:

| MCP Primitive | kgents Equivalent | Category |
|---------------|-------------------|----------|
| **Tool** | `Tool[Input, Output]` | Morphism |
| **Resource** | `DataSource[Query, Data]` | Morphism to data |
| **Prompt** | `PromptTemplate[Params, str]` | Template morphism |
| **Server** | Tool registry/catalog | Category |
| **Client** | Agent invoking tools | Functor |

### Principle 5: **Observability via Traced Categories**

Every tool execution is **traced** for debugging and optimization:

```python
@dataclass
class ToolTrace:
    """Trace of tool execution (categorical trace)."""

    tool_name: str
    input: Any
    output: Result[Any, Error]

    # Timing
    start_time: float
    end_time: float
    latency_ms: float

    # Categorical metadata
    composition_depth: int  # Depth in pipeline
    parent_trace: Optional[ToolTrace]  # For nested composition

    # Cost tracking
    tokens_used: Optional[int]
    cost_usd: Optional[float]
```

**Integration with W-gents (Wire Observation)**:
- W-gents observe tool execution in real-time
- Live dashboards show tool call trees
- Performance profiling (latency, cost, success rate)

### Principle 6: **Dynamic Tool Selection as Functor**

Agent **context** determines which tools are available:

```python
class ToolFunctor:
    """
    Functor from agent contexts to tool categories.

    Maps:
    - AgentContext → Available tools
    - Preserves composition (context transforms preserve tool chains)
    """

    def map_context(self, context: AgentContext) -> ToolCategory:
        """Select tools based on context."""

        if context.security_level == "high":
            # High security → Limited tools
            return SandboxedTools()

        if context.domain == "scientific":
            # Science domain → Hypothesis tools
            return ScientificTools()

        # Default tools
        return StandardTools()
```

**Permission Model**:
- **Zero standing privileges**: Tools granted per-task
- **Short-lived tokens**: 15-60 minute OAuth tokens (never static keys)
- **Attribute-based**: Context-aware permissions (time, location, sensitivity)

---

## Architecture: The Five-Layer Stack

### Layer 1: **Tool Definition** (Schema Layer)

Tools are defined via **typed schemas** (Pydantic/Zod/JSON Schema):

```python
from pydantic import BaseModel, Field

class SearchQuery(BaseModel):
    """Input schema for search tool."""
    query: str = Field(description="Natural language search query")
    max_results: int = Field(default=10, ge=1, le=100)
    domain: Optional[str] = Field(default=None, description="Filter by domain")

class SearchResult(BaseModel):
    """Single search result."""
    title: str
    url: str
    snippet: str
    relevance: float = Field(ge=0.0, le=1.0)

class SearchResults(BaseModel):
    """Output schema for search tool."""
    results: list[SearchResult]
    total_found: int
    query_time_ms: float

# Tool definition
@tool(
    name="web_search",
    description="Search the web for information",
    input_schema=SearchQuery,
    output_schema=SearchResults
)
class WebSearchTool(Tool[SearchQuery, SearchResults]):
    async def invoke(self, input: SearchQuery) -> SearchResults:
        # Implementation uses P-gent to parse API response
        ...
```

**Schema as Type System**:
- **Algebraic Data Types**: Sum types (A | B), Product types (A × B)
- **Validation = Proof**: Schema validation proves input conformance
- **Composition = Function types**: `Tool[A, B] >> Tool[B, C] = Tool[A, C]`

### Layer 2: **Tool Registry** (Catalog Layer)

Tools are **catalogued** via L-gent (Library) integration:

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

    async def register(self, tool: Tool) -> ToolEntry:
        """Register tool in catalog."""
        entry = ToolEntry(
            id=generate_id(),
            name=tool.name,
            version=tool.version,
            input_schema=tool.input_schema,
            output_schema=tool.output_schema,
            description=tool.description,
            server=tool.server,  # MCP server address
            tags=extract_tags(tool.description),
            created_at=now(),
        )

        # Store via D-gent persistence
        await self.catalog.store(entry)

        return entry

    async def find_by_signature(
        self,
        input_type: type,
        output_type: type
    ) -> list[Tool]:
        """Find tools matching type signature."""

        # Query L-gent lattice for compatible tools
        candidates = await self.catalog.find_by_type(
            input_type=input_type,
            output_type=output_type
        )

        return [self.load_tool(c.id) for c in candidates]

    async def find_composition_path(
        self,
        source_type: type,
        target_type: type
    ) -> Optional[list[Tool]]:
        """
        Find sequence of tools composing source → target.

        Uses L-gent lattice to solve composition planning.
        """

        # Graph search in type lattice
        path = await self.catalog.find_path(source_type, target_type)

        if path:
            return [self.load_tool(tool_id) for tool_id in path]

        return None
```

**Integration with L-gents**:
- **Type Lattice**: Tool signatures form partial order
- **Composition Planning**: Find tool chains via graph search
- **Semantic Search**: Keyword/embedding search for tool discovery

### Layer 3: **Tool Execution** (Runtime Layer)

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
    ) -> Result[Output, ToolError]:
        """Execute tool with full observability."""

        # Start trace
        trace = ToolTrace.start(tool.name, input)

        try:
            # Check cache (D-gent integration)
            if cached := await self.cache.get(tool, input):
                trace.finish_cached(cached)
                return ok(cached)

            # Execute tool
            output = await tool.invoke(input)

            # Validate output schema
            validated = self.validate_output(output, tool.output_schema)

            # Cache result
            await self.cache.set(tool, input, validated)

            # Finish trace
            trace.finish_success(validated)

            return ok(validated)

        except ToolError as e:
            # Parse error (P-gent integration)
            classification = await self.error_parser.parse(e)

            # Decide recovery strategy
            if classification.recoverable:
                # Retry with exponential backoff
                return await self.retry_with_backoff(tool, input, context)
            else:
                # Fatal error
                trace.finish_error(e)
                return err(e, recoverable=False)

        finally:
            # Emit trace (W-gent integration)
            await self.tracer.emit(trace)
```

**Retry Logic** (from research):
- **Exponential backoff**: 100ms, 200ms, 400ms, ...
- **Max attempts**: Configurable (default 3)
- **Circuit breaker**: Stop after N consecutive failures
- **Jitter**: Random delay to avoid thundering herd

### Layer 4: **Tool Composition** (Pipeline Layer)

Tools compose via **categorical composition** (`>>`):

```python
# Simple composition
search_and_summarize = web_search >> summarize_text

# Complex pipeline with error handling
pipeline = (
    parse_query           # str → Result[Query, ParseError]
    >> web_search         # Query → Result[Results, SearchError]
    >> filter_results     # Results → Result[Filtered, FilterError]
    >> summarize_top_3    # Filtered → Result[Summary, SummaryError]
    >> format_markdown    # Summary → Result[Markdown, FormatError]
)

# Execute pipeline
result: Result[Markdown, Error] = await pipeline.invoke(user_question)

# Handle result
match result:
    case Ok(markdown):
        print(markdown)
    case Err(error):
        print(f"Pipeline failed: {error}")
```

**Composition Patterns** (from C-gents):

1. **Sequential** (`;` or `>>`): Chain tools in order
2. **Parallel** (`×`): Run tools concurrently, merge results
3. **Choice** (`+`): Try tools in fallback order
4. **Feedback** (`trace`): Iterative tool application

```python
# Parallel composition (product functor)
gather_context = (
    search_web × search_docs × search_memory
) >> merge_results

# Choice composition (coproduct)
robust_search = (
    google_search
    + bing_search
    + duckduckgo_search
)  # Try in order until success

# Feedback (traced category)
refine_query = trace(
    lambda q: generate_query(q) >> evaluate_results >> refine(q),
    max_iterations=5
)
```

### Layer 5: **Agent Integration** (Agentic Layer)

Agents **use tools** via natural composition:

```python
class ResearchAgent(Agent[str, Report]):
    """
    Research agent using tools compositionally.

    Tools available:
    - web_search: Search the web
    - read_paper: Extract paper content
    - generate_summary: LLM summarization
    - fact_check: Verify claims
    """

    def __init__(self, registry: ToolRegistry):
        self.registry = registry

        # Load tools from registry
        self.web_search = registry.get("web_search")
        self.read_paper = registry.get("read_paper")
        self.summarize = registry.get("generate_summary")
        self.fact_check = registry.get("fact_check")

    async def invoke(self, topic: str) -> Report:
        """Research topic and generate report."""

        # Step 1: Search for papers
        search_results = await self.web_search.invoke(
            SearchQuery(query=f"{topic} research papers", max_results=10)
        )

        # Step 2: Read top papers (parallel composition)
        papers = await asyncio.gather(*[
            self.read_paper.invoke(result.url)
            for result in search_results.results[:3]
        ])

        # Step 3: Summarize each paper
        summaries = await asyncio.gather(*[
            self.summarize.invoke(paper.content)
            for paper in papers
        ])

        # Step 4: Fact-check summaries
        verified = await asyncio.gather(*[
            self.fact_check.invoke(summary)
            for summary in summaries
        ])

        # Step 5: Synthesize report
        return Report(
            topic=topic,
            papers=papers,
            summaries=verified,
            generated_at=now()
        )
```

**Beyond ReAct**: This is **compositional tool use**, not prompt-driven:
- No "thought/action/observation" loops
- Direct functional composition
- Type-safe at compile time
- Traces show exact execution graph

---

## Novel Patterns: Beyond Industry State-of-Art

### Pattern 1: **Tool Specialization via T-gents**

Tools **extend T-gent patterns** for domain-specific testing:

```python
# Mock tool for testing
mock_search = MockAgent[SearchQuery, SearchResults](
    output=SearchResults(results=[...], total_found=5)
)

# Failing tool for resilience testing
failing_api = FailingAgent[APIRequest, APIResponse](
    FailingConfig(
        error_type=FailureType.NETWORK,
        fail_count=2,  # Fail twice, then succeed
        recovery_token=APIResponse(data={...})
    )
)

# Spy tool for observability
traced_llm = SpyAgent[Prompt, Completion](label="LLM Calls")

# Flaky tool for chaos testing
flaky_search = FlakyAgent(
    wrapped=real_search,
    probability=0.1,  # 10% failure rate
    seed=42
)

# Test resilience via composition
test_pipeline = (
    parse_query
    >> failing_api       # Will fail 2x, test retry logic
    >> traced_llm        # Trace all LLM calls
    >> flaky_search      # Random failures
)
```

**This is unique to kgents**: Testing and tool use are **unified**. No other framework treats test doubles as composable morphisms.

### Pattern 2: **Parser-Tool Codesign**

Every tool **co-designed with parser**:

```python
@tool(
    name="hypothesis_generator",
    description="Generate scientific hypotheses",
    input_schema=HypothesisRequest,
    output_schema=HypothesisOutput,
    parser=HypothesisParser()  # ← P-gent handles parsing
)
class HypothesisGeneratorTool(Tool[HypothesisRequest, HypothesisOutput]):
    """
    Tool that generates hypotheses.

    Parser handles:
    - Structured response (HYPOTHESES:, REASONING:, TESTS:)
    - Fallback extraction if LLM output malformed
    - Confidence scoring based on completeness
    """

    async def invoke(self, input: HypothesisRequest) -> HypothesisOutput:
        # Generate hypotheses via LLM
        response = await self.llm.generate(
            prompt=build_hypothesis_prompt(input)
        )

        # Parse response via P-gent
        parsed = await self.parser.parse(response)

        # Handle parse failures gracefully
        if not parsed.success:
            # Try repair strategies
            repaired = await self.parser.repair(response)
            return repaired.value

        return parsed.value
```

**This is unique to kgents**: **Parser-first tool design**. Tools don't fail on malformed output—they degrade gracefully via P-gent fallback chains.

### Pattern 3: **Categorical Prompt Caching**

Prompt caching formalized as **memoization functor**:

```python
class CachedTool(Tool[Input, Output]):
    """
    Tool with prompt caching (memoization functor).

    Category Theory:
    - Original functor: F: Context → Response
    - Memoized functor: Memo(F): Context → Cached[Response]
    - Natural transformation: η: Memo(F) → F (cache lookup)
    """

    def __init__(self, base_tool: Tool[Input, Output], cache: D-gent):
        self.base_tool = base_tool
        self.cache = cache  # D-gent PersistentAgent

    async def invoke(self, input: Input) -> Output:
        # Check cache (90% cost reduction!)
        cache_key = self.compute_cache_key(input)

        if cached := await self.cache.get(cache_key):
            return cached.value

        # Cache miss - execute base tool
        output = await self.base_tool.invoke(input)

        # Write to cache
        await self.cache.set(cache_key, output, ttl=3600)

        return output

    def compute_cache_key(self, input: Input) -> str:
        """
        Compute cache key from input.

        Anthropic requirement: Exact prefix match.
        Any change (even whitespace) → cache miss.
        """
        # Normalize input for stable caching
        normalized = self.normalize(input)
        return sha256(normalized).hexdigest()
```

**Cost Savings** (from research):
- **Writing to cache**: 25% price increase (one-time)
- **Reading from cache**: Only 10% of base price (ongoing)
- **Net savings**: Up to 90% for repeated contexts

### Pattern 4: **Functorial Multi-Tool Orchestration**

Multi-tool patterns as **functors between categories**:

```python
# Sequential orchestration → Functor composition
class SequentialOrchestrator(Functor):
    """Chain tools in order (compose functors)."""

    def map(self, tools: list[Tool]) -> ComposedTool:
        return reduce(lambda f, g: f >> g, tools)

# Parallel orchestration → Product functor
class ParallelOrchestrator(Functor):
    """Run tools concurrently (monoidal product)."""

    def map(self, tools: list[Tool[Input, Output]]) -> Tool[Input, list[Output]]:
        async def parallel_invoke(input: Input) -> list[Output]:
            results = await asyncio.gather(*[
                tool.invoke(input) for tool in tools
            ])
            return results

        return Tool(name="parallel", invoke=parallel_invoke)

# Supervisor pattern → Comma category
class SupervisorOrchestrator(Functor):
    """Central coordinator (comma category construction)."""

    def map(self, workers: list[Tool]) -> Tool[Task, Result]:
        # Supervisor decomposes task, delegates to workers, synthesizes
        ...

# Handoff pattern → Natural transformation
class HandoffOrchestrator:
    """Transfer control between tools (natural transformation)."""

    def transform(
        self,
        source: Tool[A, B],
        target: Tool[B, C]
    ) -> Tool[A, C]:
        # Natural transformation preserves structure
        return source >> target
```

**This is unique to kgents**: Multi-agent orchestration **derived from category theory**, not ad-hoc patterns.

### Pattern 5: **Security as Subobject Classifier**

Tool permissions modeled via **subobject classifiers**:

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

    def classify(
        self,
        tool: Tool,
        context: AgentContext
    ) -> Permission:
        """
        Classify tool as allowed/denied based on context.

        Implements Attribute-Based Access Control (ABAC).
        """

        # Check security level
        if context.security_level == "high" and tool.requires_network:
            return Permission.DENIED

        # Check time-based restrictions
        if tool.requires_approval and not context.user_present:
            return Permission.DENIED

        # Check data sensitivity
        if tool.accesses_pii and not context.pii_authorized:
            return Permission.DENIED

        # Default: allowed with audit
        return Permission.ALLOWED_AUDITED

    def grant_temporary(
        self,
        tool: Tool,
        context: AgentContext,
        duration_seconds: int = 900  # 15 minutes
    ) -> TemporaryToken:
        """
        Grant short-lived token (zero standing privileges).

        Following research best practices:
        - Short-lived: 15-60 minutes
        - Task-specific: Only for current operation
        - Revocable: Can be cancelled mid-execution
        """

        token = TemporaryToken(
            tool_id=tool.id,
            context_id=context.id,
            expires_at=now() + timedelta(seconds=duration_seconds),
            permissions=self.compute_permissions(tool, context)
        )

        # Store token (D-gent)
        await self.token_store.set(token.id, token, ttl=duration_seconds)

        return token
```

**This is unique to kgents**: Security **derived from categorical foundations**, not bolted on.

---

## Integration with Existing Genera

### With **P-gents (Parser)**

**Four Integration Points**:

1. **Schema Parsing**: MCP tool definitions → kgents Tool
```python
mcp_parser: Parser[MCPToolDef, ToolSchema]

# Parse MCP server tool list
tools = [mcp_parser.parse(defn) for defn in server.list_tools()]
```

2. **Input Parsing**: Natural language → Tool parameters
```python
input_parser: Parser[str, ToolInput]

# User says: "Search for recent papers on category theory"
params = input_parser.parse("Search for recent papers on category theory")
# → SearchQuery(query="category theory papers", max_results=10, ...)
```

3. **Output Parsing**: Tool response → Structured data
```python
output_parser: Parser[str, ToolOutput]

# Tool returns JSON (possibly malformed)
result = output_parser.parse(tool_response)
# → Uses fallback chain if malformed
```

4. **Error Parsing**: Tool errors → Recovery strategy
```python
error_parser: Parser[ToolError, ErrorClassification]

# Classify errors as recoverable/fatal
classification = error_parser.parse(error)
if classification.recoverable:
    retry()
else:
    fail_gracefully()
```

### With **D-gents (Data)**

**Three Integration Points**:

1. **Tool State**: Persistent tool configuration
```python
# Store tool config via PersistentAgent
tool_store = PersistentAgent[str, ToolConfig](
    schema=ToolConfig,
    storage_path=".kgents/tools/"
)

await tool_store.set_state("web_search", search_config)
```

2. **Prompt Caching**: Cache tool contexts
```python
# Cache expensive contexts (90% cost reduction)
cache = CachedAgent[ToolInput, ToolOutput](
    backend=PersistentAgent(...),
    ttl_seconds=3600
)
```

3. **Execution History**: Track tool usage
```python
# Store tool traces via VolatileAgent
trace_buffer = VolatileAgent[str, ToolTrace](
    max_history=1000
)

await trace_buffer.mutate(lambda traces: traces + [new_trace])
```

### With **L-gents (Library)**

**Tool Discovery Integration**:

```python
# Register tools in catalog
registry = ToolRegistry(catalog=L-gent_catalog)

await registry.register(web_search_tool)
await registry.register(summarize_tool)

# Find tools by type signature
candidates = await registry.find_by_signature(
    input_type=str,
    output_type=Summary
)

# Find composition path
path = await registry.find_composition_path(
    source_type=Query,
    target_type=Report
)
# → [web_search, extract_facts, synthesize_report]
```

### With **W-gents (Wire Observation)**

**Live Tool Monitoring**:

```python
# Observe tool execution in real-time
wire_observer = W-gent_server(agent=research_agent)

# Live dashboard shows:
# - Tool call tree (nested composition)
# - Latency breakdown per tool
# - Cache hit rates
# - Error rates and retry counts
# - Cost tracking (tokens × price)

await wire_observer.start()
# → http://localhost:8080/observe/research_agent
```

### With **E-gents (Evolution)**

**Tool-Augmented Evolution**:

```python
# Evolve agent WITH tool feedback
evolved = await evolve(
    target_agent=hypothesis_generator,
    tools=[
        literature_search,
        fact_checker,
        citation_validator
    ],
    improvement_goal="Generate more falsifiable hypotheses"
)

# Evolution loop uses tools to validate improvements:
# 1. Generate hypothesis
# 2. Use literature_search to find related work
# 3. Use fact_checker to validate claims
# 4. Use citation_validator to check references
# 5. Judge: Did quality improve?
```

### With **F-gents (Forge)**

**Tool-Guided Forge**:

```python
# Search for similar tools before forging new one
search_result = await registry.search(
    intent="I need a tool that converts markdown to PDF"
)

if search_result.matches:
    # Reuse existing tool
    return search_result.matches[0]
else:
    # Forge new tool
    new_tool = await forge_tool(
        intent="Convert markdown to PDF",
        input_schema=Markdown,
        output_schema=PDF
    )

    # Register in catalog
    await registry.register(new_tool)

    return new_tool
```

### With **Bootstrap Agents**

**Foundational Integration**:

1. **Compose**: Tools compose via `>>`
```python
pipeline = tool_a >> tool_b >> tool_c
```

2. **Judge**: Tools evaluated via 7 principles
```python
verdict = await judge(web_search_tool, principles)
# → Check: composable? tasteful? ethical?
```

3. **Ground**: Tools grounded in persona preferences
```python
# Kent prefers direct, minimal tools (no bloat)
tools = select_tools(persona=ground())
```

4. **Fix**: Iterative tool refinement
```python
# Refine tool until stable
refined_tool = await fix(
    initial_tool,
    improve_fn=lambda t: evolve_tool(t, feedback),
    stable_fn=lambda t1, t2: performance_similar(t1, t2)
)
```

---

## Implementation Roadmap

### Phase 1: **Foundation** (Week 1-2)

**Goal**: Core types and composition

**Tasks**:
- [ ] Define `Tool[Input, Output]` base class
- [ ] Implement `ToolRegistry` (L-gent integration)
- [ ] Add `Result[T, E]` monad to bootstrap.types
- [ ] Implement basic composition (`>>`, `×`, `+`)
- [ ] Create `ToolTrace` type for observability

**Tests**:
- [ ] Tool composition laws (associativity, identity)
- [ ] Type safety (composition only if types align)
- [ ] Registry CRUD operations
- [ ] Trace emission

### Phase 2: **Parsing** (Week 3)

**Goal**: P-gent integration

**Tasks**:
- [ ] `SchemaParser`: MCP → kgents Tool
- [ ] `InputParser`: NL → Tool parameters
- [ ] `OutputParser`: Tool response → Data
- [ ] `ErrorParser`: Errors → Classification
- [ ] Fallback chains for each parser

**Tests**:
- [ ] Parse valid schemas
- [ ] Handle malformed schemas
- [ ] Extract parameters from NL
- [ ] Repair malformed JSON outputs
- [ ] Classify recoverable vs fatal errors

### Phase 3: **Execution** (Week 4)

**Goal**: Runtime with retry/cache/trace

**Tasks**:
- [ ] `ToolExecutor` with Result monad
- [ ] Retry logic (exponential backoff)
- [ ] Prompt caching (D-gent integration)
- [ ] Circuit breaker for failing tools
- [ ] W-gent trace emission

**Tests**:
- [ ] Successful execution
- [ ] Retry on transient failure
- [ ] Cache hit/miss
- [ ] Circuit breaker triggers
- [ ] Trace completeness

### Phase 4: **MCP Integration** (Week 5-6)

**Goal**: Connect to MCP servers

**Tasks**:
- [ ] MCP client implementation
- [ ] Server discovery and connection
- [ ] Tool schema fetching
- [ ] Remote tool invocation
- [ ] Streaming responses

**Tests**:
- [ ] Connect to MCP server
- [ ] List available tools
- [ ] Invoke remote tool
- [ ] Handle connection failures
- [ ] Stream large responses

### Phase 5: **Security** (Week 7)

**Goal**: Permission model and sandboxing

**Tasks**:
- [ ] `PermissionClassifier` (ABAC)
- [ ] Short-lived token generation
- [ ] Tool permission checks
- [ ] Audit logging
- [ ] Sandbox mode for untrusted tools

**Tests**:
- [ ] Permission denial
- [ ] Token expiration
- [ ] Audit trail completeness
- [ ] Sandbox escape prevention

### Phase 6: **Multi-Tool Patterns** (Week 8-9)

**Goal**: Orchestration functors

**Tasks**:
- [ ] Sequential orchestrator
- [ ] Parallel orchestrator (product functor)
- [ ] Supervisor pattern (comma category)
- [ ] Handoff pattern (natural transformation)
- [ ] Dynamic tool selection

**Tests**:
- [ ] Sequential execution
- [ ] Parallel execution and merging
- [ ] Supervisor task delegation
- [ ] Agent handoffs
- [ ] Context-based tool selection

### Phase 7: **Cross-Genus Integration** (Week 10-11)

**Goal**: Connect with all genera

**Tasks**:
- [ ] E-gent: Tool-augmented evolution
- [ ] F-gent: Tool search before forge
- [ ] B-gent: Hypothesis validation tools
- [ ] J-gent: Template-based tool generation
- [ ] I-gent: Tool execution visualization
- [ ] W-gent: Live tool monitoring

**Tests**:
- [ ] E-gent evolves with tool feedback
- [ ] F-gent reuses existing tools
- [ ] B-gent validates hypotheses
- [ ] J-gent instantiates tool templates
- [ ] I-gent renders tool call trees
- [ ] W-gent streams tool traces

### Phase 8: **Production Hardening** (Week 12)

**Goal**: Reliability and observability

**Tasks**:
- [ ] Comprehensive error handling
- [ ] Performance benchmarks
- [ ] Cost tracking and budgets
- [ ] Rate limiting
- [ ] OpenTelemetry integration

**Tests**:
- [ ] Load testing (1000 concurrent tools)
- [ ] Failure recovery scenarios
- [ ] Cost budget enforcement
- [ ] Rate limit compliance
- [ ] Telemetry export

---

## Success Criteria

A successful T-gents Phase 2 implementation satisfies:

### Functional Requirements

- [ ] **F1**: Tools are typed morphisms (`Tool[A, B]`)
- [ ] **F2**: Tools compose via `>>` with type safety
- [ ] **F3**: P-gent parses schemas, inputs, outputs, errors
- [ ] **F4**: Result monad handles errors gracefully
- [ ] **F5**: MCP protocol natively supported
- [ ] **F6**: L-gent registry enables tool discovery
- [ ] **F7**: D-gent provides caching (90% cost reduction)
- [ ] **F8**: W-gent observes tool execution live
- [ ] **F9**: Permission model enforces security
- [ ] **F10**: All genera can use tools

### Non-Functional Requirements

- [ ] **NF1**: Zero regressions in existing tests
- [ ] **NF2**: <50ms overhead per tool call
- [ ] **NF3**: Handles 1000 concurrent tool calls
- [ ] **NF4**: 99.9% retry success for transient errors
- [ ] **NF5**: Cache hit rate >80% for repeated contexts
- [ ] **NF6**: Tool discovery <100ms (L-gent query)
- [ ] **NF7**: Permission check <10ms
- [ ] **NF8**: Full execution trace captured
- [ ] **NF9**: OpenTelemetry compliant
- [ ] **NF10**: Comprehensive documentation

### Philosophical Requirements

- [ ] **P1**: Maintains category-theoretic purity
- [ ] **P2**: Tools feel like agents (unified abstraction)
- [ ] **P3**: Composability is primary operation
- [ ] **P4**: Security derived from mathematical foundations
- [ ] **P5**: Parsers handle all malformed inputs
- [ ] **P6**: Joyful to use (minimal boilerplate)
- [ ] **P7**: Tasteful (no bloat, every feature justified)
- [ ] **P8**: Generative (regenerable from spec)

---

## Novel Contributions to AI Agent Field

This specification makes **8 novel contributions** to the state-of-the-art:

### 1. **Tools as Categorical Morphisms**
**Unique to kgents**: Tools are typed morphisms, not opaque functions. Enables algebraic reasoning about tool pipelines.

### 2. **Unified Testing and Tool Use**
**Unique to kgents**: T-gents extend to tool mocking, spying, and chaos testing. No other framework unifies these.

### 3. **Parser-First Tool Design**
**Unique to kgents**: Every tool co-designed with P-gent parser. Graceful degradation on malformed outputs.

### 4. **Functorial Multi-Tool Orchestration**
**Unique to kgents**: Orchestration patterns derived from category theory (product functor, comma category, natural transformation).

### 5. **Security as Subobject Classifier**
**Unique to kgents**: Permissions modeled categorically, not ad-hoc. ABAC derived from mathematical foundations.

### 6. **Monadic Error Recovery**
**Unique to kgents**: Result monad + Railway Oriented Programming for tool errors. Type-safe error composition.

### 7. **Prompt Caching as Memoization Functor**
**Unique to kgents**: Caching formalized as functor, not implementation detail. Natural transformation for cache lookup.

### 8. **MCP Native Integration**
**Among first**: Full MCP support with categorical interpretation. Industry-standard protocol as compositional substrate.

---

## Comparison with Existing Frameworks

| Feature | kgents T-gents | LangChain | AutoGen | OpenAI SDK | CrewAI |
|---------|----------------|-----------|---------|------------|--------|
| **Tools as Morphisms** | ✅ Yes | ❌ No | ❌ No | ❌ No | ❌ No |
| **Categorical Composition** | ✅ Yes | ⚠️ Partial | ❌ No | ❌ No | ❌ No |
| **Type Safety** | ✅ Yes | ⚠️ Partial | ⚠️ Partial | ✅ Yes | ❌ No |
| **Parser Integration** | ✅ P-gents | ⚠️ Manual | ⚠️ Manual | ⚠️ Manual | ⚠️ Manual |
| **Error Monad** | ✅ Result | ❌ Exceptions | ❌ Exceptions | ❌ Exceptions | ❌ Exceptions |
| **MCP Support** | ✅ Native | ✅ Yes | ⚠️ Partial | ✅ Yes | ⚠️ Partial |
| **Prompt Caching** | ✅ Functor | ✅ Yes | ⚠️ Partial | ✅ Yes | ❌ No |
| **Observability** | ✅ W-gents | ✅ Langfuse | ⚠️ Partial | ✅ Yes | ⚠️ Partial |
| **Security Model** | ✅ ABAC | ⚠️ Manual | ⚠️ Manual | ⚠️ Manual | ⚠️ Manual |
| **Tool Discovery** | ✅ L-gents | ⚠️ Registry | ❌ No | ❌ No | ❌ No |
| **Testing Integration** | ✅ T-gents | ⚠️ Separate | ⚠️ Separate | ⚠️ Separate | ⚠️ Separate |
| **Multi-Tool Patterns** | ✅ Functorial | ✅ Graph | ✅ Agents | ⚠️ Manual | ✅ Crews |

**Legend**:
- ✅ **Yes**: Fully supported, first-class feature
- ⚠️ **Partial**: Some support, not primary design
- ❌ **No**: Not supported or requires external library

---

## Open Questions and Future Work

### Research Questions

**Q1**: Can we **prove tool pipeline correctness** via categorical laws?
- Hypothesis: Pipelines satisfying associativity + identity are provably correct
- Validation: Generate QuickCheck-style property tests
- Impact: Formal verification of tool compositions

**Q2**: How do we handle **streaming tool responses** categorically?
- Hypothesis: Streams are functors from naturals to outputs
- Validation: Implement StreamingTool[N → Output]
- Impact: Real-time tool output processing

**Q3**: Can **tool discovery be automated** via type inference?
- Hypothesis: L-gent lattice solves constraint satisfaction
- Validation: Given input type + goal, find tool sequence
- Impact: "I want X" → automatic tool pipeline

**Q4**: How do we **version tools** while preserving composition?
- Hypothesis: Tool versions form a directed acyclic graph
- Validation: Semantic versioning + compatibility matrix
- Impact: Safe tool evolution without breaking compositions

**Q5**: Can we **learn tool selection** from execution traces?
- Hypothesis: W-gent traces reveal usage patterns
- Validation: ML model predicts best tool for context
- Impact: Adaptive tool selection

### Future Enhancements

**E1**: **Tool Templates** (J-gent integration)
- Parameterized tool definitions
- Runtime instantiation with specific values
- Template registry for reusable patterns

**E2**: **Tool Synthesis** (F-gent integration)
- Generate new tools from natural language specs
- Validate via E-gent evolution
- Register in L-gent catalog automatically

**E3**: **Multi-Agent Tool Sharing**
- Agents share tool instances
- Resource pooling (rate limits, quotas)
- Collaborative tool usage patterns

**E4**: **Tool Performance Optimization**
- Automatic batching of similar requests
- Intelligent caching strategies
- Load balancing across tool instances

**E5**: **Tool Debugging UI** (I-gent integration)
- Visual tool call trees
- Interactive trace exploration
- Time-travel debugging

---

## Conclusion

T-gents Phase 2: Tool Use represents a **paradigm shift** in agent architectures:

**From**: Tools as opaque function calls, ad-hoc orchestration, exception-based errors
**To**: Tools as typed morphisms, categorical composition, monadic error handling

**Core Innovations**:
1. **Mathematical foundations**: Category theory, not engineering heuristics
2. **Unified abstraction**: Tools are agents, agents use tools
3. **Parser integration**: P-gents ensure graceful degradation
4. **Industry alignment**: MCP as standard protocol
5. **Cross-genus synergy**: D/E/F/I/L/W-gents all benefit

**Expected Impact**:
- **Reliability**: Provably correct tool pipelines
- **Composability**: Type-safe tool chaining
- **Observability**: Full execution traces via W-gents
- **Security**: Categorical permission model
- **Cost**: 90% reduction via prompt caching
- **Discovery**: Semantic tool search via L-gents

**Next Steps**:
1. Review this specification
2. Validate architectural decisions
3. Begin Phase 1 implementation
4. Integrate with P-gents spec
5. Update HYDRATE.md

This specification demonstrates that **category theory is not just elegant—it's practical**. By treating tools as morphisms, we achieve reliability, composability, and type safety that ad-hoc approaches cannot match.

The future of AI agents is **compositional, typed, and categorical**.

---

**End of T-gents Phase 2 Specification**

**Document Metadata**:
- **Version**: 1.0 (Proposal)
- **Date**: 2025-12-08
- **Session**: J-gents Phase 2 Deep Research
- **Research Sources**: 50+ papers, blogs, frameworks (2024-2025)
- **Integration**: P-gents, existing T-gents, bootstrap, all genera
- **Status**: Awaiting review and implementation planning
