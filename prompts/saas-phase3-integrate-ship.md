# SaaS Phase 3: Integrate & Ship

> Wire Phase 2 infrastructure into production paths. Robustify. Ship.

## Context

**Phase 2 Complete** (ba03b04):
- Track A: NATSBridge for JetStream streaming (fallback-capable)
- Track B: OpenMeterClient for usage-based billing (batched, CloudEvents)
- Track C: SSE wired to real KgentFlux streaming (on_chunk callback)
- Track D: datetime.utcnow() → datetime.now(UTC) migration

**Artifacts**:
- `protocols/streaming/nats_bridge.py` - NATSBridge with graceful degradation
- `protocols/billing/openmeter_client.py` - OpenMeterClient with buffering
- `protocols/api/sessions.py` - Real SSE streaming via chunk queue
- `docs/skills/n-phase-cycle/saas-phase2-infrastructure.md` - Plan document

**Test Coverage**: 244 tests passing

---

## Phase 3 Objectives

### 1. Deep Integration (40%)

Wire the new infrastructure into existing code paths:

```
┌─────────────────────────────────────────────────────────────┐
│                      API Layer                               │
│  sessions.py ─┬─▶ NATSBridge.publish_chunk()                │
│               └─▶ OpenMeterClient.record_tokens()           │
│                                                              │
│  agentese.py ───▶ OpenMeterClient.record_agentese_invoke() │
│                                                              │
│  soul.py ───────▶ OpenMeterClient.record_request()         │
└─────────────────────────────────────────────────────────────┘
```

**Tasks**:
- [ ] Wire OpenMeterClient into MeteringMiddleware (replace in-memory stats)
- [ ] Wire NATSBridge into SSE endpoint for multi-consumer scenarios
- [ ] Add OpenMeter recording to AGENTESE invoke endpoint
- [ ] Add OpenMeter recording to Soul API endpoints
- [ ] Create shared client instances (singleton pattern or dependency injection)

### 2. Configuration & Environment (20%)

Production-ready configuration:

```python
# Expected environment variables
NATS_SERVERS=nats://nats:4222
NATS_ENABLED=true
OPENMETER_API_KEY=om_...
OPENMETER_BASE_URL=https://openmeter.cloud
OPENMETER_ENABLED=true
```

**Tasks**:
- [ ] Create `protocols/config/saas.py` with Pydantic settings
- [ ] Wire config into FastAPI app startup/shutdown
- [ ] Add health check endpoints for NATS and OpenMeter
- [ ] Document environment variables in README or docs

### 3. Robustification (25%)

Harden for production:

**Error Handling**:
- [ ] Circuit breaker for NATS connection failures
- [ ] Retry logic for OpenMeter API failures (already has basic retry)
- [ ] Graceful degradation logging (structured, not just warnings)

**Observability**:
- [ ] Add OpenTelemetry spans for NATS publish/subscribe
- [ ] Add OpenTelemetry spans for OpenMeter flush
- [ ] Metrics: events_published, events_failed, flush_latency

**Testing**:
- [ ] Integration tests with testcontainers (NATS)
- [ ] Mock OpenMeter API tests
- [ ] Chaos tests (NATS disconnect mid-stream)

### 4. Deployment (15%)

Ship it:

**Kubernetes**:
- [ ] Add NATS to `infra/k8s/` manifests (or use managed NATS)
- [ ] Configure OpenMeter webhook for usage alerts
- [ ] Update deployment with new env vars

**Documentation**:
- [ ] Update CLAUDE.md with SaaS configuration section
- [ ] Add troubleshooting guide for streaming issues
- [ ] Document billing event schema for finance team

---

## Entry Points

### Option A: Start with Integration
```
/hydrate cat prompts/saas-phase3-integrate-ship.md

Focus: Wire OpenMeterClient into MeteringMiddleware

Files:
  - impl/claude/protocols/api/metering.py (existing middleware)
  - impl/claude/protocols/billing/openmeter_client.py (new client)
  - impl/claude/protocols/api/app.py (FastAPI app setup)
```

### Option B: Start with Configuration
```
/hydrate cat prompts/saas-phase3-integrate-ship.md

Focus: Create centralized SaaS configuration

Files:
  - impl/claude/protocols/config/ (new directory)
  - impl/claude/protocols/api/app.py (wire config)
```

### Option C: Start with Robustification
```
/hydrate cat prompts/saas-phase3-integrate-ship.md

Focus: Add circuit breaker and observability

Files:
  - impl/claude/protocols/streaming/nats_bridge.py
  - impl/claude/protocols/billing/openmeter_client.py
```

---

## Integration Architecture

```
                                    ┌──────────────┐
                                    │   OpenMeter  │
                                    │    Cloud     │
                                    └──────▲───────┘
                                           │
┌─────────────────────────────────────────┼─────────────────────────────┐
│ kgents API                              │                              │
│                                         │                              │
│  ┌─────────┐    ┌─────────────┐    ┌───┴────────┐                     │
│  │ Request │───▶│  Metering   │───▶│ OpenMeter  │                     │
│  │         │    │ Middleware  │    │  Client    │                     │
│  └────┬────┘    └─────────────┘    └────────────┘                     │
│       │                                                                │
│       ▼                                                                │
│  ┌─────────┐    ┌─────────────┐    ┌────────────┐    ┌────────────┐  │
│  │Sessions │───▶│  KgentFlux  │───▶│   NATS     │───▶│    SSE     │  │
│  │  API    │    │  .dialogue  │    │  Bridge    │    │  Clients   │  │
│  └─────────┘    └─────────────┘    └────────────┘    └────────────┘  │
│                                           │                           │
│                                           ▼                           │
│                                    ┌────────────┐                     │
│                                    │  Metering  │                     │
│                                    │ Processor  │                     │
│                                    └────────────┘                     │
└───────────────────────────────────────────────────────────────────────┘
```

---

## Success Criteria

- [ ] OpenMeter receives real usage events from API
- [ ] NATS streams session events (or gracefully falls back)
- [ ] Health endpoints report infrastructure status
- [ ] No regression in existing 244 tests
- [ ] New integration tests cover failure scenarios
- [ ] Deployment manifests updated and tested

---

## Entropy Budget

- Budget: 0.10
- Phase 2 spent: 0.08
- Remaining: 0.02 (tight - focus on integration, minimize exploration)

If entropy needed for research:
- NATS cluster topology for production
- OpenMeter webhook configuration
- Cost estimation for usage-based pricing tiers

---

## Related Files

```
impl/claude/protocols/
├── api/
│   ├── app.py              # FastAPI app setup
│   ├── metering.py         # Existing metering middleware
│   ├── sessions.py         # SSE streaming (updated Phase 2)
│   ├── agentese.py         # AGENTESE REST API
│   └── soul.py             # Soul API
├── billing/
│   ├── openmeter_client.py # NEW: Usage metering
│   └── stripe_client.py    # Existing: Payments
├── streaming/
│   └── nats_bridge.py      # NEW: Event streaming
└── tenancy/
    └── service.py          # Tenant management (datetime fixed)
```

---

## Continuation

After Phase 3:
- Phase 4: Pricing tiers and quota enforcement
- Phase 5: Admin dashboard and usage analytics
- Phase 6: Self-service onboarding flow
