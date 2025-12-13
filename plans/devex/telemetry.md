---
path: devex/telemetry
status: planned
progress: 0
last_touched: 2025-12-13
touched_by: claude-opus-4.5
blocking: []
enables: []
uses: [devex/trace]  # TraceCollector → OpenTelemetry spans
session_notes: |
  Plan created from strategic recommendations.
  Priority 6 of 6 DevEx improvements.
  Lowest priority - enterprise feature.
---

# OpenTelemetry Integration: Enterprise Observability

> *"Every invocation leaves a trace."*

**Goal**: Export AGENTESE invocations to standard observability tools (Jaeger, Prometheus).
**Priority**: 6 (medium impact, high effort)

---

## The Problem

Traces exist but don't integrate with standard observability tools. Enterprise users expect OpenTelemetry, Jaeger, Prometheus—not custom logging.

---

## The Solution

```python
# Already have:
await logos.invoke("self.soul.challenge", umwelt, "idea")

# Add automatic spans:
# span: agentese.invoke
#   path: self.soul.challenge
#   duration: 23ms
#   tokens.in: 1234
#   tokens.out: 567
#   result: REJECT
```

Export to:
- **Jaeger** — Distributed tracing visualization
- **Prometheus** — Metrics scraping
- **OTLP** — Generic OpenTelemetry Protocol endpoint
- **Local JSON** — Development mode

---

## Research & References

### OpenTelemetry Python
- Official instrumentation packages
- Async support via `contextvars`
- Auto-instrumentation for common libraries
- Source: [OpenTelemetry Python Docs](https://opentelemetry.io/docs/languages/python/instrumentation/)

### Asyncio Instrumentation
- `opentelemetry-instrumentation-asyncio` package
- Traces coroutines, futures, tasks
- Environment variables for configuration
- Source: [Asyncio Instrumentation PyPI](https://pypi.org/project/opentelemetry-instrumentation-asyncio/)
- Source: [Asyncio Instrumentation Docs](https://opentelemetry-python-contrib.readthedocs.io/en/latest/instrumentation/asyncio/asyncio.html)

### Context Propagation
- `ContextVarsRuntimeContext` is the default
- Safe with async/await
- Source: [Stack Overflow Discussion](https://stackoverflow.com/questions/77410600/is-opentelemetry-in-python-safe-to-use-with-async)

### Key Methods
- `start_span()` — Create span without making it current
- `trace_coroutine()` — Wrap coroutine for tracing
- Source: [Uptrace Python Tracing Guide](https://uptrace.dev/get/opentelemetry-python/tracing)

---

## Implementation Outline

### Phase 1: Core Instrumentation (~150 LOC)
```python
# protocols/agentese/telemetry.py
from opentelemetry import trace
from opentelemetry.trace import Span, Status, StatusCode

tracer = trace.get_tracer("kgents.agentese")

class TelemetryMiddleware:
    """Middleware that adds OpenTelemetry spans to AGENTESE invocations."""

    async def __call__(
        self,
        path: str,
        umwelt: Umwelt,
        args: tuple,
        next_handler: Callable,
    ) -> Any:
        with tracer.start_as_current_span(
            f"agentese.invoke",
            attributes={
                "agentese.path": path,
                "agentese.context": path.split(".")[0],
                "agentese.observer": umwelt.observer_id,
            },
        ) as span:
            try:
                result = await next_handler(path, umwelt, args)
                span.set_status(Status(StatusCode.OK))
                return result
            except Exception as e:
                span.set_status(Status(StatusCode.ERROR, str(e)))
                span.record_exception(e)
                raise
```

### Phase 2: Metrics Export (~100 LOC)
```python
# protocols/agentese/metrics.py
from opentelemetry import metrics

meter = metrics.get_meter("kgents.agentese")

invoke_counter = meter.create_counter(
    "agentese.invocations",
    description="Number of AGENTESE invocations",
)

invoke_duration = meter.create_histogram(
    "agentese.invoke.duration",
    description="Duration of AGENTESE invocations",
    unit="ms",
)

token_counter = meter.create_counter(
    "agentese.tokens",
    description="Tokens consumed by AGENTESE invocations",
)
```

### Phase 3: Exporter Configuration (~100 LOC)
```python
# protocols/agentese/exporters.py
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.exporter.jaeger.thrift import JaegerExporter

def configure_telemetry(config: TelemetryConfig) -> None:
    """Configure OpenTelemetry exporters based on config."""
    provider = TracerProvider()

    if config.otlp_endpoint:
        provider.add_span_processor(
            BatchSpanProcessor(OTLPSpanExporter(endpoint=config.otlp_endpoint))
        )

    if config.jaeger_endpoint:
        provider.add_span_processor(
            BatchSpanProcessor(JaegerExporter(agent_host_name=config.jaeger_host))
        )

    if config.local_json:
        provider.add_span_processor(
            BatchSpanProcessor(JsonFileExporter(config.local_json_path))
        )

    trace.set_tracer_provider(provider)
```

### Phase 4: Configuration (~50 LOC)
```yaml
# ~/.kgents/telemetry.yaml
enabled: true

traces:
  exporter: otlp  # otlp | jaeger | json | none
  otlp_endpoint: "localhost:4317"
  jaeger_host: "localhost"
  jaeger_port: 6831
  json_path: "~/.kgents/traces/"

metrics:
  exporter: prometheus  # prometheus | otlp | none
  prometheus_port: 9090

sampling:
  rate: 1.0  # Sample all traces (development)
  # rate: 0.1  # Sample 10% (production)
```

---

## Span Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `agentese.path` | string | Full path (e.g., `self.soul.challenge`) |
| `agentese.context` | string | Context (self, world, concept, void, time) |
| `agentese.observer` | string | Observer ID |
| `agentese.tokens.in` | int | Input tokens (if LLM) |
| `agentese.tokens.out` | int | Output tokens (if LLM) |
| `agentese.result` | string | Result type |

---

## File Structure

```
protocols/agentese/
├── telemetry.py      # Span middleware
├── metrics.py        # Metrics definitions
├── exporters.py      # Exporter configuration
└── _tests/
    └── test_telemetry.py
```

---

## Success Criteria

| Criterion | Metric |
|-----------|--------|
| Trace overhead | < 5% latency |
| Metrics collection | All invocations captured |
| Jaeger visualization | Traces visible |
| Prometheus scrape | Metrics exposed |
| Kent's approval | "This is enterprise-grade" |

---

## Testing Strategy

| Test Type | Coverage |
|-----------|----------|
| Unit | Middleware, metrics |
| Integration | Export to local JSON |
| E2E | Export to Jaeger (manual) |
| Performance | Overhead benchmark |

---

## Dependencies (New)

```toml
# pyproject.toml
opentelemetry-api = "^1.24.0"
opentelemetry-sdk = "^1.24.0"
opentelemetry-instrumentation-asyncio = "^0.45b0"
opentelemetry-exporter-otlp = "^1.24.0"
opentelemetry-exporter-jaeger = "^1.24.0"
opentelemetry-exporter-prometheus = "^0.45b0"
```

---

## Cross-References

- **Strategic Recommendations**: `plans/ideas/strategic-recommendations-2025-12-13.md`
- **AGENTESE**: `spec/protocols/agentese.md`
- **Logos Implementation**: `protocols/agentese/logos.py`
- **OpenTelemetry Python**: https://opentelemetry.io/docs/languages/python/

---

*"What is observed becomes understandable."*
