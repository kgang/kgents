---
path: docs/skills/n-phase-cycle/saas-phase2-infrastructure
status: active
progress: 25
last_touched: 2025-12-14
touched_by: opus-4-5
blocking: []
enables:
  - monetization/grand-initiative-monetization
  - deployment/permanent-kgent-chatbot
session_notes: |
  PLAN complete. Four tracks researched and documented.
phase_ledger:
  PLAN: touched
  RESEARCH: in_progress
  DEVELOP: pending
  STRATEGIZE: pending
  CROSS-SYNERGIZE: pending
  IMPLEMENT: pending
  QA: pending
  TEST: pending
  EDUCATE: pending
  MEASURE: pending
  REFLECT: pending
entropy:
  budget: 0.10
  spent: 0.03
  remaining: 0.07
---

# SaaS Phase 2: Infrastructure Track

> Wire real event streaming and billing-grade metering to the Phase 1 API foundation.

**Difficulty**: Medium-High
**Prerequisites**: Phase 1 Complete (API + Sessions + Auth)
**Files Touched**: `impl/claude/protocols/api/`, `impl/claude/protocols/tenancy/`, `infra/k8s/`

---

## Executive Summary

Phase 2 wires real infrastructure (NATS JetStream, OpenMeter) to the Phase 1 API skeleton:
- **Track A (40%)**: NATS JetStream for real event streaming
- **Track B (30%)**: OpenMeter for billing-grade usage metering
- **Track C (20%)**: SSE wiring from KgentFlux to sessions endpoint
- **Track D (10%)**: datetime.utcnow() → datetime.now(UTC) migration

---

## Track A: NATS JetStream (40%)

### Research Findings

**Key Resources**:
- [nats.py](https://github.com/nats-io/nats.py) - Official Python client
- [FastStream](https://github.com/ag2ai/faststream) - High-level framework with FastAPI integration
- [JetStream Docs](https://docs.nats.io/nats-concepts/jetstream) - Persistence and replay

### Architecture Decision

**Recommendation**: Use **nats.py directly** (not FastStream) for these reasons:
1. KgentFlux already has robust streaming abstractions (FluxStream, FluxEvent)
2. Direct control over JetStream consumer modes is needed for SSE backpressure
3. Simpler dependency tree

### Topology Strategy

```yaml
# Single-server development, cluster for production
jetstream:
  streams:
    kgent-events:
      subjects: ["kgent.>"]
      retention: limits
      max_msgs_per_subject: 10000
      max_age: 168h  # 7 days
      storage: file
      replicas: 1  # 3 for production

  consumers:
    # Push consumer for SSE (per-session)
    sse-session-{id}:
      durable_name: sse-{session_id}
      deliver_policy: new
      ack_policy: explicit
      max_deliver: 3
      filter_subject: kgent.session.{session_id}.>

    # Pull consumer for batch processing (metering)
    metering-processor:
      durable_name: metering
      deliver_policy: all
      ack_policy: explicit
      batch_size: 100
```

### Integration Points

| File | Integration | Priority |
|------|-------------|----------|
| `impl/claude/protocols/api/sessions.py:554` | Replace simulated chunks | P0 |
| `impl/claude/agents/k/flux.py:1444` | Mirror to NATS stream | P1 |
| `impl/claude/protocols/terrarium/gateway.py` | WebSocket → NATS bridge | P2 |

### Implementation Approach

```python
# New file: impl/claude/protocols/streaming/nats_bridge.py
from nats.aio.client import Client as NATSClient
from nats.js.api import StreamConfig, ConsumerConfig

class NATSBridge:
    """Bridge KgentFlux events to NATS JetStream."""

    def __init__(self, servers: list[str] = ["nats://localhost:4222"]):
        self._nc: Optional[NATSClient] = None
        self._js: Optional[JetStreamContext] = None
        self._servers = servers

    async def connect(self) -> None:
        self._nc = await nats.connect(servers=self._servers)
        self._js = self._nc.jetstream()

    async def publish_soul_event(
        self,
        session_id: str,
        event: SoulEvent,
    ) -> None:
        """Publish SoulEvent to JetStream."""
        subject = f"kgent.session.{session_id}.{event.event_type.value}"
        await self._js.publish(subject, event.to_json().encode())

    async def subscribe_session(
        self,
        session_id: str,
    ) -> AsyncIterator[SoulEvent]:
        """Subscribe to session events for SSE streaming."""
        subject = f"kgent.session.{session_id}.>"
        psub = await self._js.pull_subscribe(
            subject,
            durable=f"sse-{session_id}",
        )

        while True:
            try:
                msgs = await psub.fetch(batch=10, timeout=0.1)
                for msg in msgs:
                    yield SoulEvent.from_json(msg.data.decode())
                    await msg.ack()
            except TimeoutError:
                continue
```

### Exit Criteria

- [ ] NATSBridge class implemented with connect/publish/subscribe
- [ ] JetStream stream configuration documented
- [ ] SSE endpoint uses NATSBridge instead of simulated chunks
- [ ] Integration test with local NATS server

---

## Track B: OpenMeter (30%)

### Research Findings

**Key Resources**:
- [OpenMeter GitHub](https://github.com/openmeterio/openmeter) - Core project
- [OpenMeter Docs](https://openmeter.io/docs/billing/entitlements/quickstart) - Getting started
- [OpenAI Metering Guide](https://openmeter.io/blog/how-to-meter-openai-and-chatgpt-api-usage) - Token tracking pattern

### SDK Integration

OpenMeter has a Python SDK. Installation:
```bash
pip install openmeter
```

### Event Schema Design

```python
# OpenMeter event format for kgents
@dataclass
class KgentsUsageEvent:
    """Usage event for OpenMeter billing."""

    # Required fields
    id: str          # Unique event ID (UUID)
    source: str      # "kgents-api"
    type: str        # Event type (below)
    subject: str     # Tenant ID
    time: datetime   # UTC timestamp

    # Event-specific data
    data: dict[str, Any]

# Event Types
USAGE_EVENT_TYPES = {
    "api.request": {
        "endpoint": str,
        "method": str,
        "status_code": int,
    },
    "llm.tokens": {
        "tokens_in": int,
        "tokens_out": int,
        "model": str,
        "session_id": str,
    },
    "session.create": {
        "agent_type": str,
    },
    "session.message": {
        "session_id": str,
        "message_length": int,
    },
}
```

### OpenMeter Meters Configuration

```yaml
# openmeter-config.yaml
meters:
  - slug: api_requests
    description: API request count
    eventType: api.request
    aggregation: COUNT
    windowSize: HOUR

  - slug: llm_tokens_in
    description: LLM input tokens
    eventType: llm.tokens
    aggregation: SUM
    valueProperty: $.tokens_in
    windowSize: HOUR

  - slug: llm_tokens_out
    description: LLM output tokens
    eventType: llm.tokens
    aggregation: SUM
    valueProperty: $.tokens_out
    windowSize: HOUR

  - slug: session_count
    description: Sessions created
    eventType: session.create
    aggregation: COUNT
    windowSize: DAY
```

### Implementation Approach

```python
# New file: impl/claude/protocols/billing/openmeter_client.py
from openmeter import OpenMeter
from dataclasses import dataclass
from datetime import datetime, UTC
from typing import Any
import uuid

@dataclass
class OpenMeterConfig:
    """OpenMeter configuration."""
    api_key: str
    base_url: str = "https://openmeter.cloud"
    batch_size: int = 100
    flush_interval: float = 1.0  # seconds

class OpenMeterClient:
    """OpenMeter integration for kgents billing."""

    def __init__(self, config: OpenMeterConfig):
        self._config = config
        self._client = OpenMeter(
            api_key=config.api_key,
            base_url=config.base_url,
        )
        self._buffer: list[dict] = []

    async def record_tokens(
        self,
        tenant_id: str,
        session_id: str,
        tokens_in: int,
        tokens_out: int,
        model: str = "kgent",
    ) -> None:
        """Record token usage for billing."""
        event = {
            "id": str(uuid.uuid4()),
            "source": "kgents-api",
            "type": "llm.tokens",
            "subject": str(tenant_id),
            "time": datetime.now(UTC).isoformat(),
            "data": {
                "tokens_in": tokens_in,
                "tokens_out": tokens_out,
                "model": model,
                "session_id": str(session_id),
            },
        }
        await self._buffer_event(event)

    async def record_request(
        self,
        tenant_id: str,
        endpoint: str,
        method: str,
        status_code: int,
    ) -> None:
        """Record API request for billing."""
        event = {
            "id": str(uuid.uuid4()),
            "source": "kgents-api",
            "type": "api.request",
            "subject": str(tenant_id),
            "time": datetime.now(UTC).isoformat(),
            "data": {
                "endpoint": endpoint,
                "method": method,
                "status_code": status_code,
            },
        }
        await self._buffer_event(event)

    async def _buffer_event(self, event: dict) -> None:
        """Buffer event and flush if needed."""
        self._buffer.append(event)
        if len(self._buffer) >= self._config.batch_size:
            await self.flush()

    async def flush(self) -> None:
        """Flush buffered events to OpenMeter."""
        if not self._buffer:
            return

        events = self._buffer
        self._buffer = []

        # Send to OpenMeter
        await self._client.ingest_events(events)
```

### Migration from In-Memory Metering

| Current Location | Change |
|------------------|--------|
| `protocols/api/metering.py` | Keep for rate limiting, remove usage stats |
| `protocols/tenancy/service.py:469` | Replace with OpenMeterClient |
| `protocols/api/sessions.py:596` | Replace record_usage with OpenMeterClient |

### Exit Criteria

- [ ] OpenMeterClient implemented with buffered batching
- [ ] Event schema documented and validated
- [ ] Meters configured in OpenMeter
- [ ] Integration with TenantService.record_usage

---

## Track C: SSE Wiring (20%)

### Current State Analysis

**File**: `impl/claude/protocols/api/sessions.py:554-624`

The current `_stream_response` function:
1. Invokes KgentFlux.invoke() synchronously
2. **Simulates** streaming by chunking the response (lines 585-590)
3. Adds artificial 10ms delays

**Problem**: This is not real streaming - it waits for full response, then chunks it.

### KgentFlux Streaming Architecture

**File**: `impl/claude/agents/k/flux.py`

KgentFlux already supports real streaming:
- `LLMStreamSource` (line 603): Wraps LLM client with backpressure queue
- `FluxEvent[T]` (line 90): Data vs metadata events
- `FluxStream` (line 176): Composable operators (map, filter, take, tap)
- `on_chunk` callback in dialogue() (line 1225): Per-chunk emission

### Integration Approach

```python
# Updated _stream_response in sessions.py
async def _stream_response(
    flux: KgentFlux,
    session_id: str,
    message: str,
    mode: Optional[DialogueMode],
    tenant_id: UUID,
    tenant_service: TenantService,
    nats_bridge: Optional[NATSBridge] = None,
) -> AsyncIterator[str]:
    """Generate real SSE stream from KgentFlux."""

    chunks: list[str] = []
    tokens_used = 0
    chunk_queue: asyncio.Queue[str | None] = asyncio.Queue()

    def on_chunk(chunk_text: str) -> None:
        """Callback for each streaming chunk."""
        chunk_queue.put_nowait(chunk_text)

        # Optionally publish to NATS for other consumers
        if nats_bridge:
            asyncio.create_task(
                nats_bridge.publish_chunk(session_id, chunk_text, len(chunks))
            )

    # Start dialogue in background
    async def run_dialogue():
        nonlocal tokens_used
        result = await flux.soul.dialogue(
            message=message,
            mode=mode,
            budget=BudgetTier.DIALOGUE,
            on_chunk=on_chunk,
        )
        tokens_used = result.tokens_used
        chunk_queue.put_nowait(None)  # Signal completion

    dialogue_task = asyncio.create_task(run_dialogue())

    try:
        while True:
            chunk = await chunk_queue.get()
            if chunk is None:
                break

            chunks.append(chunk)
            yield f"event: chunk\ndata: {json.dumps({'text': chunk, 'index': len(chunks) - 1})}\n\n"

        # Wait for dialogue to complete
        await dialogue_task

        # Final bookkeeping
        full_response = "".join(chunks)
        _add_message(session_id, "assistant", full_response, tokens_used)

        # Record to OpenMeter (replaces tenant_service.record_usage)
        # ... metering code ...

        yield f"event: complete\ndata: {json.dumps({'text': full_response, 'tokens_used': tokens_used, 'chunks': len(chunks)})}\n\n"

    except Exception as e:
        dialogue_task.cancel()
        yield f"event: error\ndata: {json.dumps({'error': str(e)})}\n\n"
```

### Backpressure Handling

The current approach has no backpressure - it drops chunks if the queue is full.

**Solution**: Use `FluxStream` operators for backpressure:

```python
# Apply backpressure via FluxStream
source = LLMStreamSource(
    client=llm_client,
    system=system_prompt,
    user=message,
    buffer_size=64,  # Configurable backpressure
)

stream = FluxStream(source).tap(
    lambda e: chunk_queue.put_nowait(e.value) if e.is_data else None
)

async for event in stream:
    pass  # Side effects handled by tap
```

### Exit Criteria

- [ ] _stream_response uses KgentFlux.dialogue(on_chunk=...)
- [ ] Chunks emitted in real-time (no artificial delay)
- [ ] Backpressure handled via queue/buffer size
- [ ] Optional NATS publishing for multi-consumer scenarios

---

## Track D: datetime.utcnow() Cleanup (10%)

### Audit Results

```
Total occurrences: 16

By file:
  impl/claude/protocols/tenancy/service.py      - 10 occurrences
  impl/claude/protocols/tenancy/api_keys.py     - 1 occurrence
  impl/claude/protocols/tenancy/models.py       - 1 occurrence
  impl/claude/protocols/tenancy/_tests/test_models.py    - 2 occurrences
  impl/claude/protocols/tenancy/_tests/test_api_keys.py  - 1 occurrence
  impl/claude/protocols/api/sessions.py         - 1 occurrence
```

### Migration Pattern

```python
# Before (deprecated)
from datetime import datetime
created_at = datetime.utcnow()

# After (timezone-aware)
from datetime import datetime, UTC
created_at = datetime.now(UTC)
```

### Migration Script

```bash
# Find and replace (manual review required)
grep -rn "datetime.utcnow()" impl/claude/protocols/ | while read line; do
    file=$(echo $line | cut -d: -f1)
    # Manual review each file
done
```

### Files to Update

| File | Line | Context |
|------|------|---------|
| `tenancy/service.py` | 123, 137, 172, 229, 266, 304, 352, 398, 430, 469 | Object timestamps |
| `tenancy/api_keys.py` | 211 | API key creation |
| `tenancy/models.py` | 203 | Token expiry check |
| `api/sessions.py` | 156 | Message timestamp |
| Test files | Various | Fixture timestamps |

### Test Fixtures Update

The test files use `datetime.utcnow()` for creating test data. These need updating to ensure consistency:

```python
# In test fixtures
from datetime import datetime, timedelta, UTC

expires_at = datetime.now(UTC) + timedelta(days=30)
```

### Exit Criteria

- [ ] All 16 occurrences migrated to datetime.now(UTC)
- [ ] Import statements updated (add UTC to imports)
- [ ] Tests pass with timezone-aware datetimes
- [ ] No deprecation warnings related to utcnow()

---

## Dependency Graph

```
Track A (NATS) ──┬──▶ Track C (SSE Wiring)
                 │
Track B (OpenMeter) ──▶ [standalone, can proceed in parallel]
                 │
Track D (datetime) ──▶ [standalone, can proceed in parallel]
```

**Recommended Order**:
1. Track D first (quick win, removes warnings)
2. Tracks A and B in parallel (independent infrastructure)
3. Track C last (depends on NATS for full integration)

---

## Continuation Prompt

```markdown
⟿[DEVELOP]

concept.forest.manifest[phase=DEVELOP][sprint=phase2_infra]@span=saas_impl

/hydrate

handles:
  - plan: docs/skills/n-phase-cycle/saas-phase2-infrastructure.md
  - api: impl/claude/protocols/api/
  - tenancy: impl/claude/protocols/tenancy/
  - flux: impl/claude/agents/k/flux.py

ledger: {PLAN:touched, RESEARCH:touched, DEVELOP:in_progress}
entropy: 0.07 remaining

## Your Mission

Implement the four tracks from Phase 2 plan.

### Actions

1. **Track D (datetime)**: Quick win first
   - Migrate all 16 occurrences
   - Run tests to verify

2. **Track B (OpenMeter)**: Parallel
   - Create `impl/claude/protocols/billing/openmeter_client.py`
   - Implement event schema
   - Wire to TenantService

3. **Track A (NATS)**: Parallel
   - Create `impl/claude/protocols/streaming/nats_bridge.py`
   - Implement JetStream publish/subscribe
   - Wire to KgentFlux mirror

4. **Track C (SSE)**: Last
   - Update `_stream_response` in sessions.py
   - Use real streaming with on_chunk callback
   - Integrate NATSBridge for multi-consumer

### Exit Criteria

- [ ] datetime.utcnow() warnings eliminated
- [ ] OpenMeterClient functional with batching
- [ ] NATSBridge connects and publishes
- [ ] SSE streams real chunks

---

continuation → STRATEGIZE
```

---

## Related Skills

- `plan.md` - PLAN phase protocol
- `research.md` - RESEARCH phase protocol
- `develop.md` - DEVELOP phase protocol
- `../streaming-patterns.md` - Flux streaming patterns

---

## Sources

- [nats.py GitHub](https://github.com/nats-io/nats.py)
- [FastStream Framework](https://github.com/ag2ai/faststream)
- [JetStream Docs](https://docs.nats.io/nats-concepts/jetstream)
- [OpenMeter GitHub](https://github.com/openmeterio/openmeter)
- [OpenMeter Docs](https://openmeter.io/docs/billing/entitlements/quickstart)
- [OpenMeter OpenAI Metering](https://openmeter.io/blog/how-to-meter-openai-and-chatgpt-api-usage)

---

## Changelog

- 2025-12-14: Initial version with all four tracks researched and documented.
