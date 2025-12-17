# Wave 4: Observability Integration

**Status**: Active
**Priority**: Medium
**Progress**: 0%
**Parent**: `plans/cli-isomorphic-migration.md`
**Depends On**: Waves 0-3
**Last Updated**: 2025-12-17

---

## Objective

Implement comprehensive observability for the CLI layer as specified in `spec/protocols/cli.md` §10. Every CLI invocation should produce traces that enable debugging, performance monitoring, and user experience optimization.

---

## The Core Insight

> *"If you can't see it, you can't improve it. Every CLI invocation is an opportunity to learn."*

Observability is not an afterthought—it's a fundamental property of a well-designed system. The CLI should produce traces that:

1. **Enable debugging**: What went wrong and where?
2. **Support performance optimization**: What's slow?
3. **Inform UX decisions**: How do users actually use the CLI?
4. **Maintain accountability**: Who did what and when?

---

## Current State

### Existing OTEL Infrastructure

| Component | Status | Location |
|-----------|--------|----------|
| OpenTelemetry SDK | ✅ Installed | `pyproject.toml` |
| Telemetry middleware | ✅ Partial | `logos.py` |
| Trace invocation helper | ✅ Exists | `telemetry.py` |
| Exporters config | ✅ Basic | `exporters.py` |
| Router tracing | ✅ Partial | `agentese_router.py` |

### Gaps

| Gap | Impact | Fix |
|-----|--------|-----|
| Handler-level tracing | Medium | Add spans in projection |
| Effect tracking | High | Record effects in spans |
| User journey spans | High | Cross-invocation correlation |
| Budget tracking | Medium | Record LLM costs in spans |
| Error categorization | Medium | Structured error spans |
| Local collector | Low | Optional local Jaeger |

---

## Phase 1: Unified Trace Architecture (Day 1)

### Step 1.1: Trace Span Hierarchy

Define the span hierarchy for CLI operations:

```
┌─────────────────────────────────────────────────────────────────────┐
│  cli.invocation                                                      │
│  ├── trace_id: abc123                                               │
│  ├── command: "kg brain capture 'test'"                             │
│  ├── input_type: "legacy"                                           │
│  ├── agentese_path: "self.memory.capture"                           │
│  │                                                                   │
│  │  ┌────────────────────────────────────────────────────────────┐  │
│  │  │  cli.dimension_derivation                                   │  │
│  │  │  ├── path: "self.memory.capture"                            │  │
│  │  │  ├── execution: "async"                                     │  │
│  │  │  ├── backend: "llm"                                         │  │
│  │  │  ├── seriousness: "neutral"                                 │  │
│  │  └────────────────────────────────────────────────────────────┘  │
│  │                                                                   │
│  │  ┌────────────────────────────────────────────────────────────┐  │
│  │  │  agentese.invoke                                            │  │
│  │  │  ├── path: "self.memory.capture"                            │  │
│  │  │  ├── observer: "cli/guest"                                  │  │
│  │  │  │                                                          │  │
│  │  │  │  ┌─────────────────────────────────────────────────────┐│  │
│  │  │  │  │  agent.execute                                       ││  │
│  │  │  │  │  ├── agent: "BrainCrystal"                           ││  │
│  │  │  │  │  ├── method: "capture"                               ││  │
│  │  │  │  │  │                                                   ││  │
│  │  │  │  │  │  ┌──────────────────────────────────────────────┐││  │
│  │  │  │  │  │  │  effect.writes                                │││  │
│  │  │  │  │  │  │  ├── resource: "memory_crystals"              │││  │
│  │  │  │  │  │  │  ├── success: true                            │││  │
│  │  │  │  │  │  └──────────────────────────────────────────────┘││  │
│  │  │  │  │  │                                                   ││  │
│  │  │  │  │  │  ┌──────────────────────────────────────────────┐││  │
│  │  │  │  │  │  │  effect.calls                                 │││  │
│  │  │  │  │  │  │  ├── resource: "llm"                          │││  │
│  │  │  │  │  │  │  ├── model: "claude-3-haiku"                  │││  │
│  │  │  │  │  │  │  ├── tokens_in: 150                           │││  │
│  │  │  │  │  │  │  ├── tokens_out: 512                          │││  │
│  │  │  │  │  │  │  ├── cost_usd: 0.0012                         │││  │
│  │  │  │  │  │  └──────────────────────────────────────────────┘││  │
│  │  │  │  └─────────────────────────────────────────────────────┘│  │
│  │  └────────────────────────────────────────────────────────────┘  │
│  │                                                                   │
│  │  ┌────────────────────────────────────────────────────────────┐  │
│  │  │  cli.render                                                 │  │
│  │  │  ├── format: "human"                                        │  │
│  │  │  ├── lines: 5                                               │  │
│  │  │  ├── duration_ms: 12                                        │  │
│  │  └────────────────────────────────────────────────────────────┘  │
│  │                                                                   │
│  ├── exit_code: 0                                                   │
│  ├── duration_ms: 847                                               │
└─────────────────────────────────────────────────────────────────────┘
```

### Step 1.2: Span Context Module

**File**: `impl/claude/protocols/cli/observability/spans.py`

```python
"""
CLI Span Context

Defines the span hierarchy and attributes for CLI observability.
"""

from contextlib import asynccontextmanager
from dataclasses import dataclass
from typing import Any

from opentelemetry import trace
from opentelemetry.trace import Status, StatusCode

# Semantic conventions for CLI spans
class SpanNames:
    INVOCATION = "cli.invocation"
    DIMENSION = "cli.dimension_derivation"
    INVOKE = "agentese.invoke"
    EXECUTE = "agent.execute"
    EFFECT_WRITES = "effect.writes"
    EFFECT_CALLS = "effect.calls"
    EFFECT_READS = "effect.reads"
    RENDER = "cli.render"
    ERROR = "cli.error"

@dataclass
class InvocationAttributes:
    """Standard attributes for cli.invocation spans."""
    command: str
    input_type: str
    agentese_path: str
    observer_archetype: str = "guest"

@dataclass
class EffectAttributes:
    """Attributes for effect spans."""
    effect_type: str
    resource: str
    success: bool
    metadata: dict[str, Any] | None = None

@asynccontextmanager
async def trace_invocation(
    command: str,
    input_type: str,
    path: str,
):
    """
    Context manager for tracing a complete CLI invocation.

    Usage:
        async with trace_invocation("kg brain capture", "legacy", "self.memory.capture") as span:
            result = await projection.project(path, observer, dims, kwargs)
            span.set_attribute("exit_code", 0)
    """
    tracer = trace.get_tracer("kgents.cli")

    with tracer.start_as_current_span(SpanNames.INVOCATION) as span:
        span.set_attribute("cli.command", command)
        span.set_attribute("cli.input_type", input_type)
        span.set_attribute("agentese.path", path)

        try:
            yield span
        except Exception as e:
            span.set_status(Status(StatusCode.ERROR))
            span.record_exception(e)
            raise

@asynccontextmanager
async def trace_effect(
    effect_type: str,
    resource: str,
):
    """
    Context manager for tracing effect execution.

    Usage:
        async with trace_effect("writes", "memory_crystals") as span:
            await crystal.store(content)
            span.set_attribute("effect.success", True)
    """
    tracer = trace.get_tracer("kgents.cli")
    span_name = f"effect.{effect_type}"

    with tracer.start_as_current_span(span_name) as span:
        span.set_attribute("effect.type", effect_type)
        span.set_attribute("effect.resource", resource)

        try:
            yield span
            span.set_attribute("effect.success", True)
        except Exception as e:
            span.set_attribute("effect.success", False)
            span.record_exception(e)
            raise
```

---

## Phase 2: Projection Tracing (Day 1)

### Step 2.1: Update CLIProjection

**File**: `impl/claude/protocols/cli/projection.py` (update)

```python
class CLIProjection:
    """The CLI projection functor with full observability."""

    async def project(
        self,
        path: str,
        observer: Observer,
        dimensions: CommandDimensions,
        kwargs: dict[str, Any],
    ) -> TerminalOutput:
        """Project with tracing."""
        from .observability.spans import trace_invocation

        command = self._format_command(path, kwargs)

        async with trace_invocation(command, "projection", path) as span:
            # Trace dimension derivation
            span.set_attribute("cli.execution", dimensions.execution.name)
            span.set_attribute("cli.backend", dimensions.backend.name)
            span.set_attribute("cli.seriousness", dimensions.seriousness.name)

            # Pre-UX
            await self._pre_ux(dimensions, path)

            # Invoke with effect tracing
            result = await self._invoke_with_tracing(path, observer, kwargs, span)

            # Post-UX and render
            output = self._post_ux(result, dimensions)

            # Record render metrics
            span.set_attribute("cli.render.format", "human")
            span.set_attribute("cli.render.lines", output.line_count)

            return output

    async def _invoke_with_tracing(
        self,
        path: str,
        observer: Observer,
        kwargs: dict[str, Any],
        parent_span: trace.Span,
    ) -> Any:
        """Invoke with effect tracing."""
        tracer = trace.get_tracer("kgents.cli")

        with tracer.start_as_current_span("agentese.invoke") as span:
            span.set_attribute("agentese.path", path)
            span.set_attribute("observer.archetype", observer.archetype)

            # Get aspect metadata for effect tracking
            meta = self.logos.get_aspect_meta(path)

            # Pre-log declared effects
            for effect in (meta.effects or []):
                if hasattr(effect, "effect") and hasattr(effect, "resource"):
                    span.add_event(
                        f"effect.{effect.effect.name.lower()}.start",
                        {"resource": effect.resource}
                    )

            result = await self.logos.invoke(path, observer, **kwargs)

            # Post-log effect completion
            for effect in (meta.effects or []):
                if hasattr(effect, "effect") and hasattr(effect, "resource"):
                    span.add_event(
                        f"effect.{effect.effect.name.lower()}.end",
                        {"resource": effect.resource, "success": True}
                    )

            return result
```

---

## Phase 3: LLM Cost Tracking (Day 2)

### Step 3.1: Budget Instrumentation

**File**: `impl/claude/protocols/cli/observability/budget.py`

```python
"""
LLM Budget Tracking

Records API costs in trace spans for analysis.
"""

from dataclasses import dataclass
from opentelemetry import trace

@dataclass
class LLMUsage:
    """LLM usage metrics."""
    model: str
    tokens_in: int
    tokens_out: int
    cost_usd: float
    duration_ms: int

# Cost per 1K tokens (approximate)
COST_PER_1K = {
    "claude-3-opus": {"input": 0.015, "output": 0.075},
    "claude-3-sonnet": {"input": 0.003, "output": 0.015},
    "claude-3-haiku": {"input": 0.00025, "output": 0.00125},
    "claude-3-5-sonnet": {"input": 0.003, "output": 0.015},
    "claude-3-5-haiku": {"input": 0.0008, "output": 0.004},
}

def estimate_cost(model: str, tokens_in: int, tokens_out: int) -> float:
    """Estimate cost for LLM usage."""
    rates = COST_PER_1K.get(model, {"input": 0.01, "output": 0.03})
    input_cost = (tokens_in / 1000) * rates["input"]
    output_cost = (tokens_out / 1000) * rates["output"]
    return input_cost + output_cost

def record_llm_usage(usage: LLMUsage) -> None:
    """Record LLM usage in current span."""
    span = trace.get_current_span()
    if span:
        span.set_attribute("llm.model", usage.model)
        span.set_attribute("llm.tokens_in", usage.tokens_in)
        span.set_attribute("llm.tokens_out", usage.tokens_out)
        span.set_attribute("llm.cost_usd", usage.cost_usd)
        span.set_attribute("llm.duration_ms", usage.duration_ms)

        # Also emit as event for timeline visibility
        span.add_event("llm.call", {
            "model": usage.model,
            "tokens": usage.tokens_in + usage.tokens_out,
            "cost_usd": usage.cost_usd,
        })
```

### Step 3.2: Integration with LLM Backends

Update K-gent and other LLM-backed agents to report usage:

```python
# In agents/k/kgent_soul.py

async def _call_llm(self, prompt: str) -> str:
    from protocols.cli.observability.budget import record_llm_usage, LLMUsage, estimate_cost
    import time

    start = time.time()
    response = await self.client.messages.create(...)
    duration_ms = int((time.time() - start) * 1000)

    usage = LLMUsage(
        model=response.model,
        tokens_in=response.usage.input_tokens,
        tokens_out=response.usage.output_tokens,
        cost_usd=estimate_cost(
            response.model,
            response.usage.input_tokens,
            response.usage.output_tokens
        ),
        duration_ms=duration_ms,
    )
    record_llm_usage(usage)

    return response.content[0].text
```

---

## Phase 4: Error Categorization (Day 2)

### Step 4.1: Structured Error Types

**File**: `impl/claude/protocols/cli/observability/errors.py`

```python
"""
Structured Error Recording

Categorizes errors for analysis and sympathy.
"""

from enum import Enum, auto
from dataclasses import dataclass
from opentelemetry import trace
from opentelemetry.trace import Status, StatusCode

class ErrorCategory(Enum):
    """Categories of CLI errors for analysis."""
    PATH_NOT_FOUND = auto()
    AFFORDANCE_DENIED = auto()
    VALIDATION_FAILED = auto()
    BACKEND_ERROR = auto()
    LLM_ERROR = auto()
    TIMEOUT = auto()
    USER_CANCELLED = auto()
    CONFIGURATION = auto()
    INTERNAL = auto()

@dataclass
class StructuredError:
    """Structured error for observability."""
    category: ErrorCategory
    message: str
    path: str | None = None
    suggestion: str | None = None
    retriable: bool = False

def categorize_error(exception: Exception, path: str | None = None) -> StructuredError:
    """Categorize an exception for observability."""
    from protocols.agentese.exceptions import (
        PathNotFoundError,
        AffordanceError,
        TastefulnessError,
    )

    if isinstance(exception, PathNotFoundError):
        return StructuredError(
            category=ErrorCategory.PATH_NOT_FOUND,
            message=str(exception),
            path=path,
            suggestion=getattr(exception, "suggestion", None),
            retriable=False,
        )

    if isinstance(exception, AffordanceError):
        return StructuredError(
            category=ErrorCategory.AFFORDANCE_DENIED,
            message=str(exception),
            path=path,
            retriable=False,
        )

    if isinstance(exception, TastefulnessError):
        return StructuredError(
            category=ErrorCategory.VALIDATION_FAILED,
            message=str(exception),
            path=path,
            retriable=False,
        )

    if isinstance(exception, TimeoutError):
        return StructuredError(
            category=ErrorCategory.TIMEOUT,
            message=str(exception),
            path=path,
            retriable=True,
        )

    if isinstance(exception, KeyboardInterrupt):
        return StructuredError(
            category=ErrorCategory.USER_CANCELLED,
            message="Cancelled by user",
            path=path,
            retriable=False,
        )

    # Default: internal error
    return StructuredError(
        category=ErrorCategory.INTERNAL,
        message=str(exception),
        path=path,
        retriable=False,
    )

def record_error(error: StructuredError) -> None:
    """Record structured error in current span."""
    span = trace.get_current_span()
    if span:
        span.set_status(Status(StatusCode.ERROR))
        span.set_attribute("error.category", error.category.name)
        span.set_attribute("error.message", error.message)
        span.set_attribute("error.retriable", error.retriable)

        if error.path:
            span.set_attribute("error.path", error.path)
        if error.suggestion:
            span.set_attribute("error.suggestion", error.suggestion)
```

---

## Phase 5: Local Collector Setup (Day 2)

### Step 5.1: Optional Local Jaeger

**File**: `impl/claude/docker-compose.observability.yml`

```yaml
version: "3.8"

services:
  jaeger:
    image: jaegertracing/all-in-one:latest
    environment:
      - COLLECTOR_OTLP_ENABLED=true
    ports:
      - "16686:16686"  # UI
      - "4317:4317"    # OTLP gRPC
      - "4318:4318"    # OTLP HTTP
    profiles:
      - observability
```

### Step 5.2: CLI Flag for Tracing

**File**: `impl/claude/protocols/cli/hollow.py` (update)

```python
def main(args: list[str]) -> int:
    # Enable tracing with --trace flag or KGENTS_TRACE env var
    trace_enabled = "--trace" in args or os.getenv("KGENTS_TRACE", "").lower() == "true"

    if trace_enabled:
        from protocols.agentese.exporters import configure_telemetry, TelemetryConfig

        config = TelemetryConfig(
            otlp_endpoint=os.getenv("KGENTS_OTLP_ENDPOINT", "localhost:4317"),
            service_name="kgents-cli",
        )
        configure_telemetry(config)

    # ... rest of main
```

### Step 5.3: Trace ID Display

```python
# In projection.py

async def project(...):
    async with trace_invocation(...) as span:
        ...

        # If trace mode, display trace ID
        if self.config.trace_output:
            trace_id = span.get_span_context().trace_id
            print(f"\nTrace: {trace_id:032x}")
            print(f"View: http://localhost:16686/trace/{trace_id:032x}")
```

---

## Phase 6: Metrics (Optional Enhancement)

### Step 6.1: CLI Metrics

**File**: `impl/claude/protocols/cli/observability/metrics.py`

```python
"""
CLI Metrics

Counter and histogram metrics for CLI usage patterns.
"""

from opentelemetry import metrics

meter = metrics.get_meter("kgents.cli")

# Counters
invocation_counter = meter.create_counter(
    "cli.invocations",
    description="Number of CLI invocations",
    unit="1",
)

error_counter = meter.create_counter(
    "cli.errors",
    description="Number of CLI errors by category",
    unit="1",
)

# Histograms
duration_histogram = meter.create_histogram(
    "cli.duration",
    description="CLI invocation duration",
    unit="ms",
)

llm_cost_histogram = meter.create_histogram(
    "cli.llm_cost",
    description="LLM costs per invocation",
    unit="usd",
)

def record_invocation(path: str, duration_ms: int, success: bool):
    """Record CLI invocation metrics."""
    invocation_counter.add(
        1,
        {"path": path, "success": str(success)}
    )
    duration_histogram.record(
        duration_ms,
        {"path": path}
    )

def record_error(category: str, path: str):
    """Record CLI error metrics."""
    error_counter.add(
        1,
        {"category": category, "path": path}
    )
```

---

## Acceptance Criteria

1. [ ] Span hierarchy implemented (cli.invocation → agentese.invoke → effect.*)
2. [ ] All CLI invocations produce traces
3. [ ] Effect execution tracked in spans
4. [ ] LLM costs recorded in spans
5. [ ] Errors categorized and recorded
6. [ ] `--trace` flag shows trace ID
7. [ ] Optional local Jaeger setup documented
8. [ ] Metrics counters/histograms implemented
9. [ ] Tests verify span attributes

---

## Files Created/Modified

| File | Action | Lines Est. |
|------|--------|------------|
| `protocols/cli/observability/__init__.py` | Create | ~10 |
| `protocols/cli/observability/spans.py` | Create | ~150 |
| `protocols/cli/observability/budget.py` | Create | ~80 |
| `protocols/cli/observability/errors.py` | Create | ~100 |
| `protocols/cli/observability/metrics.py` | Create | ~60 |
| `protocols/cli/projection.py` | Modify | +80 |
| `protocols/cli/hollow.py` | Modify | +30 |
| `docker-compose.observability.yml` | Create | ~20 |
| `protocols/cli/_tests/test_observability.py` | Create | ~200 |

---

## Example Output

```
$ kg brain capture "Category theory is beautiful" --trace

✓ Captured: Category theory is beautiful...
  ID: abc123
  Embedding: ✓ semantic
  Storage: SQLite + Vector

Trace: 4bf92f3577b34da6a3ce929d0e0e4736
View: http://localhost:16686/trace/4bf92f3577b34da6a3ce929d0e0e4736
```

In Jaeger UI:
```
cli.invocation (847ms)
├── cli.dimension_derivation (2ms)
├── agentese.invoke (840ms)
│   └── agent.execute (835ms)
│       ├── effect.writes memory_crystals (50ms)
│       └── effect.calls llm (780ms)
│           └── llm.call model=claude-3-haiku tokens=662 cost=$0.0012
└── cli.render (5ms)
```

---

*Next: Wave 5 - Cleanup and Validation (if needed)*
