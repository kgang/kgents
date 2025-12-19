"""
T-gents Phase 2: Tool Use - Core Tool Types

This module implements Tool[A, B] as morphisms in the agent category,
extending the existing T-gents testing framework with tool use capabilities.

Philosophy:
- Tools are agents specialized for external interaction
- Tools compose via >> like all agents (categorical composition)
- Tools are typed morphisms with explicit input/output schemas
- P-gents parse all tool boundaries (schema, input, output, error)

Integration:
- Extends Agent[A, B] from bootstrap.types
- Uses Result monad for error handling (Railway Oriented Programming)
- P-gent parsing for graceful degradation
- W-gent tracing for observability
- L-gent registry for discovery
- D-gent caching for performance

References:
- spec/u-gents/tool-use.md - Complete specification
- bootstrap.types - Base Agent[A, B] and Result monad
- agents/p - Parser integration
"""

from __future__ import annotations

from abc import abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Generic, Optional, Type, TypeVar

from agents.poly.types import Agent, Result, err, ok

# Type variables
A = TypeVar("A")  # Input type
B = TypeVar("B")  # Output type
C = TypeVar("C")  # Third type for composition


# --- Tool Metadata ---


@dataclass
class ToolIdentity:
    """
    Identity metadata for a tool.

    Analogous to AgentIdentity but specialized for tools.
    Includes MCP-specific metadata.
    """

    name: str  # Tool name (unique within server)
    description: str  # Human-readable description
    version: str = "0.1.0"  # Semantic version
    server: Optional[str] = None  # MCP server address (if remote)
    tags: list[str] = field(default_factory=list)  # Searchable tags


@dataclass
class ToolInterface:
    """
    Interface declaration for a tool.

    Describes the typed morphism signature A → B with schemas.
    """

    input_schema: Type[Any]  # Input type/schema
    input_description: str  # What the input represents
    output_schema: Type[Any]  # Output type/schema
    output_description: str  # What the output represents
    error_codes: list[tuple[str, str]] = field(default_factory=list)  # (code, description)


@dataclass
class ToolRuntime:
    """
    Runtime characteristics of a tool.

    Performance expectations and resource requirements.
    """

    timeout_ms: int = 30000  # Default 30s timeout
    retry_count: int = 3  # Max retry attempts
    cache_ttl_seconds: Optional[int] = None  # Cache TTL (None = no cache)
    rate_limit: Optional[tuple[int, int]] = None  # (calls, per_seconds)


@dataclass
class ToolMeta:
    """
    Complete metadata for a tool.

    Similar to AgentMeta but specialized for tool use cases.
    Includes MCP protocol metadata.
    """

    identity: ToolIdentity
    interface: ToolInterface
    runtime: ToolRuntime = field(default_factory=ToolRuntime)

    @classmethod
    def minimal(
        cls,
        name: str,
        description: str,
        input_schema: Type[Any],
        output_schema: Type[Any],
    ) -> ToolMeta:
        """Create minimal tool metadata."""
        return cls(
            identity=ToolIdentity(name=name, description=description),
            interface=ToolInterface(
                input_schema=input_schema,
                input_description=f"Input for {name}",
                output_schema=output_schema,
                output_description=f"Output from {name}",
            ),
        )


# --- Tool Errors ---


class ToolErrorType(Enum):
    """
    Classification of tool errors for recovery strategies.

    Based on T-gents FailureType but extended for tool use.
    """

    # Recoverable errors (retry)
    NETWORK = "network"  # Network timeout/connection error
    RATE_LIMIT = "rate_limit"  # Rate limit exceeded
    TIMEOUT = "timeout"  # Tool execution timeout
    TRANSIENT = "transient"  # Temporary failure

    # Non-recoverable errors (fail fast)
    VALIDATION = "validation"  # Input validation failed
    PERMISSION = "permission"  # Permission denied
    NOT_FOUND = "not_found"  # Tool/resource not found
    FATAL = "fatal"  # Unrecoverable error


@dataclass
class ToolError(Exception):
    """
    Tool execution error with recovery metadata.

    Integrates with Result monad for Railway Oriented Programming.
    """

    error_type: ToolErrorType
    message: str
    tool_name: str
    input: Any = None
    recoverable: bool = True
    retry_after_ms: Optional[int] = None  # Retry delay for rate limits

    def __str__(self) -> str:
        return f"ToolError({self.error_type.value}): {self.message} [tool={self.tool_name}]"


# --- Tool Trace (W-gent Integration) ---


@dataclass
class ToolTrace:
    """
    Execution trace for tool invocation.

    Integrates with W-gents for live observability.
    Tracks performance, cost, and categorical metadata.
    """

    tool_name: str
    input: Any
    output: Optional[Result[Any, ToolError]] = None

    # Timing
    start_time: datetime = field(default_factory=datetime.now)
    end_time: Optional[datetime] = None
    latency_ms: Optional[float] = None

    # Categorical metadata
    composition_depth: int = 0  # Depth in pipeline (f >> g >> h)
    parent_trace: Optional[ToolTrace] = None  # For nested composition

    # Cost tracking
    tokens_used: Optional[int] = None
    cost_usd: Optional[float] = None

    # Cache metadata
    cache_hit: bool = False

    def finish_success(self, output: Any) -> None:
        """Mark trace as successful."""
        self.end_time = datetime.now()
        self.latency_ms = (self.end_time - self.start_time).total_seconds() * 1000
        self.output = ok(output)

    def finish_error(self, error: ToolError) -> None:
        """Mark trace as failed."""
        self.end_time = datetime.now()
        self.latency_ms = (self.end_time - self.start_time).total_seconds() * 1000
        self.output = err(error, error.message, error.recoverable)

    def finish_cached(self, output: Any) -> None:
        """Mark trace as cache hit."""
        self.end_time = datetime.now()
        self.latency_ms = (self.end_time - self.start_time).total_seconds() * 1000
        self.output = ok(output)
        self.cache_hit = True


# --- Tool Base Class ---


class Tool(Agent[A, B], Generic[A, B]):
    """
    Tool[A, B]: Typed morphism for external interaction.

    A tool is an agent specialized for calling external systems:
    - MCP servers (Model Context Protocol)
    - APIs (REST, GraphQL, gRPC)
    - Shell commands
    - File system operations
    - Database queries

    Category Theory:
    - Objects: Types (A, B)
    - Morphisms: Tool execution (A → B)
    - Identity: PassthroughTool (returns input unchanged)
    - Composition: Sequential tool chains (f >> g)

    Laws (inherited from Agent):
    - Associativity: (f >> g) >> h ≡ f >> (g >> h)
    - Identity: Id >> f ≡ f ≡ f >> Id

    Integration:
    - P-gents: Parse schemas, inputs, outputs, errors
    - Result monad: Railway Oriented Programming for errors
    - W-gents: Trace emission for observability
    - D-gents: Caching for performance
    - L-gents: Discovery via registry

    Usage:
        # Define tool with schemas
        class WebSearchTool(Tool[SearchQuery, SearchResults]):
            meta = ToolMeta.minimal(
                name="web_search",
                description="Search the web",
                input_schema=SearchQuery,
                output_schema=SearchResults,
            )

            async def invoke(self, input: SearchQuery) -> SearchResults:
                # Implementation with P-gent parsing
                ...

        # Compose tools
        pipeline = parse_query >> web_search >> summarize

        # Execute with error handling
        result: Result[Summary, ToolError] = await pipeline.invoke(user_input)
    """

    # Metadata (must be set by subclasses)
    meta: ToolMeta

    # Mark as test tool (for T-gent compatibility)
    __is_test__: bool = False  # Tools are NOT test agents by default

    @property
    def name(self) -> str:
        """Tool name from metadata."""
        return self.meta.identity.name

    @abstractmethod
    async def invoke(self, input: A) -> B:
        """
        Execute tool with typed input.

        Subclasses must implement this method.
        Should handle errors gracefully and return Result when appropriate.
        """
        pass

    def with_trace(self, parent_trace: Optional[ToolTrace] = None) -> TracedTool[A, B]:
        """
        Wrap tool with tracing (W-gent integration).

        Returns a new tool that emits traces on every invocation.
        """
        return TracedTool(self, parent_trace)

    def with_cache(self, ttl_seconds: int = 300) -> CachedTool[A, B]:
        """
        Wrap tool with caching (D-gent integration).

        Returns a new tool that caches results for TTL duration.
        """
        return CachedTool(self, ttl_seconds)

    def with_retry(self, max_attempts: int = 3) -> RetryTool[A, B]:
        """
        Wrap tool with retry logic (T-gent pattern).

        Returns a new tool that retries on recoverable errors.
        """
        return RetryTool(self, max_attempts)


# --- Tool Decorators/Wrappers ---


class TracedTool(Tool[A, B], Generic[A, B]):
    """
    Tool wrapper that emits traces (W-gent integration).

    Wraps any tool to track execution timing, success/failure,
    and categorical metadata for observability.
    """

    def __init__(self, inner: Tool[A, B], parent_trace: Optional[ToolTrace] = None):
        self.inner = inner
        self.parent_trace = parent_trace
        self.meta = inner.meta

    async def invoke(self, input: A) -> B:
        """Execute with tracing."""
        trace = ToolTrace(
            tool_name=self.inner.name,
            input=input,
            parent_trace=self.parent_trace,
        )

        try:
            output = await self.inner.invoke(input)
            trace.finish_success(output)
            return output
        except ToolError as e:
            trace.finish_error(e)
            raise
        finally:
            # TODO: Emit trace to W-gent observer
            # await self.tracer.emit(trace)
            pass


class CachedTool(Tool[A, B], Generic[A, B]):
    """
    Tool wrapper with caching (D-gent integration).

    Caches tool results for specified TTL to reduce API calls
    and improve performance.

    Handles both hashable and non-hashable inputs by converting
    non-hashable inputs to string representation for caching.
    """

    def __init__(self, inner: Tool[A, B], ttl_seconds: int):
        self.inner = inner
        self.ttl_seconds = ttl_seconds
        self.meta = inner.meta
        self._cache: dict[Any, tuple[B, datetime]] = {}

    def _make_cache_key(self, input: A) -> Any:
        """Convert input to hashable cache key."""
        try:
            # Try to use input directly (if hashable)
            hash(input)
            return input
        except TypeError:
            # Fall back to string representation for non-hashable inputs
            # Future: Use json.dumps or pickle for better serialization
            return str(input)

    async def invoke(self, input: A) -> B:
        """Execute with caching."""
        cache_key = self._make_cache_key(input)

        # Check cache
        if cache_key in self._cache:
            cached_output, cached_at = self._cache[cache_key]
            age_seconds = (datetime.now() - cached_at).total_seconds()

            if age_seconds < self.ttl_seconds:
                # Cache hit
                return cached_output

        # Cache miss - execute tool
        output = await self.inner.invoke(input)

        # Store in cache
        self._cache[cache_key] = (output, datetime.now())

        return output


class RetryTool(Tool[A, B], Generic[A, B]):
    """
    Tool wrapper with retry logic (T-gent pattern).

    Retries tool execution on recoverable errors with exponential backoff.
    Integrates with FailingAgent patterns from T-gents Phase 1.
    """

    def __init__(self, inner: Tool[A, B], max_attempts: int):
        self.inner = inner
        self.max_attempts = max_attempts
        self.meta = inner.meta

    async def invoke(self, input: A) -> B:
        """Execute with retry."""
        import asyncio

        last_error: Optional[ToolError] = None

        for attempt in range(self.max_attempts):
            try:
                return await self.inner.invoke(input)
            except ToolError as e:
                last_error = e

                # Don't retry non-recoverable errors
                if not e.recoverable:
                    raise

                # Don't retry on last attempt
                if attempt == self.max_attempts - 1:
                    raise

                # Exponential backoff: 100ms, 200ms, 400ms, ...
                delay_ms = e.retry_after_ms or (100 * (2**attempt))
                await asyncio.sleep(delay_ms / 1000)

        # Should never reach here, but type checker needs it
        if last_error:
            raise last_error
        else:
            raise RuntimeError("Retry logic error")


# --- Passthrough Tool (Identity) ---


class PassthroughTool(Tool[A, A], Generic[A]):
    """
    Identity tool: returns input unchanged.

    Category theory identity morphism for tools.
    Useful for testing and as a base case for composition.
    """

    def __init__(self, name: str = "passthrough"):
        self.meta = ToolMeta.minimal(
            name=name,
            description="Identity tool (returns input unchanged)",
            input_schema=Any,
            output_schema=Any,
        )

    async def invoke(self, input: A) -> A:
        """Return input unchanged."""
        return input


# --- Exports ---

__all__ = [
    # Metadata
    "ToolIdentity",
    "ToolInterface",
    "ToolRuntime",
    "ToolMeta",
    # Errors
    "ToolErrorType",
    "ToolError",
    # Tracing
    "ToolTrace",
    # Core
    "Tool",
    "PassthroughTool",
    # Wrappers
    "TracedTool",
    "CachedTool",
    "RetryTool",
]
