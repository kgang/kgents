# kgents SaaS Synergy Map

**Date**: December 14, 2025
**Phase**: CROSS-SYNERGIZE
**Status**: Complete

---

## Executive Summary

This document maps synergies across the 3 SaaS implementation tracks (Core, Billing, GTM) and identifies leverage points from existing kgents primitives. **Key finding**: Substantially more infrastructure exists than anticipated. The existing AGENTESE implementation (559 tests) provides a robust foundation that significantly reduces implementation scope.

---

## 1. AGENTESE Path Reuse Map

### 1.1 Paths Directly Serving SaaS Features

| AGENTESE Path | SaaS Feature | Status | Leverage |
|---------------|--------------|--------|----------|
| `self.memory.*` | K-Gent session state | **Implemented** | 24+ affordances, Four Pillars integration |
| `self.soul.*` | K-Gent personality | **Implemented** | Full SOUL_POLYNOMIAL support |
| `time.trace.*` | Observability dashboard | **Implemented** | witness, query, replay, analyze, collect, render, diff |
| `void.entropy.*` | Serendipity features | **Implemented** | sip, pour, tithe with history |
| `void.capital.*` | Usage tracking | **Implemented** | EventSourcedLedger |
| `world.agent.*` | Agent discovery | **Implemented** | AGENT_REGISTRY |
| `concept.forest.*` | Plan management | **Implemented** | ForestNode with N-Phase |

### 1.2 Paths Ready for SaaS (Exist, Need Wiring)

| Path | SaaS Use Case | Required Wiring |
|------|---------------|-----------------|
| `self.judgment.*` | Rate limiting decisions | Connect to quota service |
| `self.vitals.*` | Health dashboard | Expose via API |
| `self.semaphore.*` | Request queuing | Connect to Purgatory |
| `time.schedule.*` | Scheduled operations | Connect to Kairos |
| `concept.blend.*` | Agent combinations | Expose via API |

### 1.3 Paths Deferred (MVP+1)

| Path | Reason for Deferral |
|------|---------------------|
| `void.*` context (full) | Complexity, not core value |
| `time.*` context (full) | Temporal operations are MVP+1 |
| `concept.*` context (full) | Abstract operations not needed for MVP |

---

## 2. Impl/Spec Gap Analysis

### 2.1 What EXISTS (No Building Needed)

| Component | Location | Test Coverage | Notes |
|-----------|----------|---------------|-------|
| **Logos Resolver** | `impl/claude/protocols/agentese/logos.py` | Covered | Full path resolution |
| **All 5 Contexts** | `impl/claude/protocols/agentese/contexts/` | Covered | world, self, concept, void, time |
| **Telemetry Middleware** | `impl/claude/protocols/agentese/telemetry.py` | Covered | OpenTelemetry spans |
| **Metrics** | `impl/claude/protocols/agentese/metrics.py` | Covered | Prometheus-compatible |
| **Parser** | `impl/claude/protocols/agentese/parser.py` | Covered | Path + clause parsing |
| **Affordances** | `impl/claude/protocols/agentese/affordances.py` | Covered | Permission system |
| **Category Laws** | `impl/claude/protocols/agentese/laws.py` | Covered | Identity/associativity |
| **Exceptions** | `impl/claude/protocols/agentese/exceptions.py` | Covered | Sympathetic errors |

**Total existing tests: 559**

### 2.2 What EXISTS for K-Gent

| Component | Location | Notes |
|-----------|----------|-------|
| **KgentSoul** | `impl/claude/agents/k/soul.py` | Core soul with dialogue, intercept |
| **KgentFlux** | `impl/claude/agents/k/flux.py` | Streaming via Flux |
| **SoulSession** | `impl/claude/agents/k/session.py` | Cross-session identity |
| **SoulEvent** | `impl/claude/agents/k/events.py` | 25+ event types |
| **Persona** | `impl/claude/agents/k/persona.py` | PersonaSeed, PersonaState |
| **Eigenvectors** | `impl/claude/agents/k/eigenvectors.py` | Kent personality vectors |
| **Hypnagogia** | `impl/claude/agents/k/hypnagogia.py` | Memory consolidation |
| **PatternStore** | `impl/claude/agents/k/pattern_store.py` | Pattern persistence |
| **GardenSQL** | `impl/claude/agents/k/garden_sql.py` | SQL-backed storage |

### 2.3 What EXISTS for Billing

| Component | Location | Notes |
|-----------|----------|-------|
| **StripeClient** | `impl/claude/protocols/billing/stripe_client.py` | Stripe SDK wrapper |
| **CustomerManager** | `impl/claude/protocols/billing/customers.py` | Customer CRUD |
| **SubscriptionManager** | `impl/claude/protocols/billing/subscriptions.py` | Subscription lifecycle |
| **WebhookHandler** | `impl/claude/protocols/billing/webhooks.py` | Stripe webhooks |

### 2.4 What EXISTS for Observability (N-gent)

| Component | Location | Notes |
|-----------|----------|-------|
| **SemanticTrace** | `impl/claude/agents/n/types.py` | Crystal format |
| **Historian** | `impl/claude/agents/n/historian.py` | Trace collection |
| **Chronicle** | `impl/claude/agents/n/chronicle.py` | Multi-agent traces |
| **Bard** | `impl/claude/agents/n/bard.py` | Trace → Narrative |
| **EchoChamber** | `impl/claude/agents/n/echo_chamber.py` | Replay engine |

### 2.5 What NEEDS Building

| Component | Priority | Complexity | Notes |
|-----------|----------|------------|-------|
| **OpenMeter Integration** | P0 | Medium | Event emission to NATS → OpenMeter |
| **Lago Integration** | P0 | Medium | Usage aggregation → billing |
| **Tenant Context Middleware** | P0 | Low | Extract tenant from JWT |
| **RLS Policies** | P0 | Medium | PostgreSQL row-level security |
| **API Gateway Config** | P0 | Low | Kong + JWT plugin |
| **K-Gent REST API** | P1 | Medium | Expose KgentFlux via REST/SSE |
| **Dashboard UI** | P1 | High | React/Svelte frontend |

---

## 3. Event Schema Unification

### 3.1 Existing Event Formats

**AGENTESE Metrics (metrics.py)**:
```python
record_invocation(
    path="self.soul.challenge",
    context="self",
    duration_s=0.125,
    success=True,
    tokens_in=100,
    tokens_out=50,
)
```

**K-gent SoulEvent (events.py)**:
```python
SoulEvent(
    event_type=SoulEventType.DIALOGUE_TURN,
    timestamp=datetime.utcnow(),
    payload={"message": "...", "tokens_used": 150},
    correlation_id="uuid",
)
```

**N-gent SemanticTrace (types.py)**:
```python
SemanticTrace(
    id="uuid",
    timestamp=datetime.utcnow(),
    agent_id="k-gent",
    action=Action.INVOKE,
    inputs={"message": "..."},
    outputs={"response": "..."},
    determinism=Determinism.STOCHASTIC,
)
```

### 3.2 Unified CloudEvents Format

The existing events can be mapped to CloudEvents for OpenMeter:

```json
{
  "id": "${trace.id}",
  "source": "kgents/${service}",
  "type": "kgents.agentese.invoke",
  "subject": "${tenant_id}",
  "time": "${ISO8601}",
  "data": {
    "path": "${agentese_path}",
    "context": "${context}",
    "tokens_in": 100,
    "tokens_out": 50,
    "duration_ms": 125,
    "session_id": "${optional}"
  }
}
```

### 3.3 Mapping Strategy

| Source | CloudEvents Type | Metered |
|--------|------------------|---------|
| `record_invocation()` | `kgents.agentese.invoke` | tokens_in + tokens_out |
| `SoulEvent.DIALOGUE_TURN` | `kgents.kgent.dialogue` | tokens_used |
| `SoulEvent.PULSE` | `kgents.kgent.session` | session_active |
| `SemanticTrace` | `kgents.trace.record` | storage_bytes |

**Action**: Create thin adapter that emits CloudEvents from existing event sources.

---

## 4. K-Gent/Observability Shared Infrastructure

### 4.1 Overlap Analysis

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    SHARED INFRASTRUCTURE MAP                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌───────────────────┐                                                      │
│  │   K-Gent Events   │ ──────────┐                                          │
│  │  (SoulEvent)      │           │                                          │
│  └───────────────────┘           │                                          │
│                                  │                                          │
│  ┌───────────────────┐           ▼                                          │
│  │ AGENTESE Metrics  │ ───▶ ┌─────────────────┐ ───▶ ┌─────────────┐       │
│  │  (telemetry.py)   │      │  Event Adapter  │      │  OpenMeter  │       │
│  └───────────────────┘      │  (CloudEvents)  │      │  (Metering) │       │
│                                  └─────────────────┘      └──────┬──────┘       │
│  ┌───────────────────┐           │                               │              │
│  │  N-gent Traces    │ ──────────┘                               │              │
│  │  (SemanticTrace)  │                                           │              │
│  └───────────────────┘                                           │              │
│                                                                  ▼              │
│  ┌───────────────────────────────────────────────────────────────────────┐   │
│  │                          SHARED CONSUMERS                              │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  │   │
│  │  │ Observ. UI  │  │ Billing UI  │  │ Quota Check │  │  N-gent Tap │  │   │
│  │  │ (Debugging) │  │ (Usage)     │  │ (Rate Limit)│  │ (Historian) │  │   │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘  │   │
│  └───────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 4.2 Shared Components

| Component | Used By | Implementation |
|-----------|---------|----------------|
| **Trace Collection** | Debugging + Billing | N-gent Historian + AGENTESE telemetry |
| **Session State** | K-Gent + Audit | self.memory.* via D-gent Lens |
| **Event Emission** | All services | NATS JetStream (planned) |
| **Token Counting** | Usage + Quotas | metrics.py `total_tokens_in/out` |

### 4.3 Single Collection, Multiple Views

The key insight: **Collect once, project many ways**.

```python
# Single trace collection point
@TelemetryMiddleware
async def invoke(path: str, umwelt: Umwelt, **kwargs):
    # 1. Executes AGENTESE path
    # 2. Records to OpenTelemetry span
    # 3. Records to metrics.py
    # 4. (NEW) Emits CloudEvent to NATS
    pass

# Multiple projections
# Projection 1: Debugging
await logos.invoke("time.trace.witness", umwelt)  # N-gent narrative

# Projection 2: Billing
GET /v1/billing/usage  # Aggregated from OpenMeter

# Projection 3: Quota
POST /v1/agentese/invoke  # Checks usage before execution
```

---

## 5. Dormant Plan Connections

### 5.1 Relevant Existing Plans

| Plan | Location | Relevance |
|------|----------|-----------|
| `cross-synergy.md` | `plans/ideas/impl/` | Agent combination patterns |
| `crown-jewels.md` | `plans/ideas/impl/` | High-value features |
| `kgent-chatbot-strategy.md` | `plans/deployment/_strategy/` | K-Gent deployment patterns |
| `kgent-chatbot-api.md` | `plans/deployment/_specs/` | K-Gent API design |
| `grand-initiative-monetization.md` | `plans/monetization/` | Monetization strategy |
| `k-terrarium-llm-agents.md` | `plans/` | LLM agent infrastructure |

### 5.2 Skills That Apply

| Skill | Location | Application |
|-------|----------|-------------|
| `agentese-path.md` | `plans/skills/` | Adding new AGENTESE paths |
| `flux-agent.md` | `plans/skills/` | K-Gent streaming |
| `cli-command.md` | `plans/skills/` | Adding CLI commands |
| `handler-patterns.md` | `plans/skills/` | CLI handler patterns |
| `n-phase-cycle/` | `plans/skills/` | This cycle methodology |

### 5.3 Work Already Done

| Work | Status | Implication |
|------|--------|-------------|
| K-Gent streaming (KgentFlux) | Complete | REST/SSE wrapper only |
| AGENTESE contexts | Complete | API exposure only |
| Billing primitives | Partial | Need metering layer |
| Trace infrastructure (N-gent) | Complete | Need OpenMeter bridge |
| OpenTelemetry | Complete | Export to Tempo |

---

## 6. Composition Opportunities

### 6.1 Agent Reuse for SaaS

| SaaS Feature | Existing Agents | Composition |
|--------------|-----------------|-------------|
| **K-Gent Chat API** | KgentSoul + KgentFlux | Expose via REST + SSE |
| **Usage Dashboard** | B-gent + I-gent | BudgetedBard + VisualizableBard |
| **Trace Viewer** | N-gent + I-gent | Bard + NarrativeVisualization |
| **Quota Enforcement** | B-gent | Token budgeting |
| **Session Replay** | N-gent | EchoChamber |

### 6.2 Path Composition Patterns

```python
# Quota check before invoke
quota_check = logos.lift("self.judgment.taste")
invoke = logos.lift("world.agent.manifest")
pipeline = quota_check >> invoke  # Fails fast if over quota

# Trace + Store
trace = logos.lift("time.trace.collect")
store = logos.lift("self.memory.engram")
audit_pipeline = trace >> store

# Usage + Billing
meter = logos.lift("void.capital.tithe")
bill = external_billing_service
billing_pipeline = meter >> bill
```

### 6.3 Zero-New-Code Features

These features require **only API exposure**, no new implementation:

| Feature | Existing Path | API Endpoint |
|---------|---------------|--------------|
| Memory retrieval | `self.memory.recall` | `GET /v1/memory/{key}` |
| Session state | `self.memory.manifest` | `GET /v1/sessions/{id}/state` |
| Trace query | `time.trace.query` | `GET /v1/traces?filter=...` |
| Entropy sip | `void.entropy.sip` | `POST /v1/entropy/sip` |
| Concept definition | `concept.{name}.define` | `POST /v1/concepts` |

---

## 7. Gap Summary

### 7.1 True Gaps (Must Build)

| Gap | Complexity | Track |
|-----|------------|-------|
| OpenMeter deployment + integration | Medium | Billing |
| Lago deployment + configuration | Medium | Billing |
| Tenant RLS policies | Medium | Platform |
| API Gateway (Kong) configuration | Low | Platform |
| CloudEvents adapter | Low | Platform |
| K-Gent REST API wrapper | Medium | Core |
| Dashboard UI | High | Shared |

### 7.2 False Gaps (Already Solved)

| "Gap" | Reality |
|-------|---------|
| AGENTESE implementation | 559 tests, all contexts |
| K-Gent soul/persona | Complete with streaming |
| Trace collection | N-gent Historian + AGENTESE telemetry |
| Token counting | metrics.py with Prometheus format |
| Event types | SoulEvent + SemanticTrace |
| Stripe integration | billing/stripe_client.py |

---

## 8. Recommendations

### 8.1 Implementation Order (Revised)

Given the extensive existing infrastructure:

1. **Deploy Infrastructure** (Phase 0)
   - K8s, PostgreSQL, Redis, Kong
   - This is the true blocker

2. **Wire Existing to API** (Phase 1)
   - Expose KgentFlux via REST/SSE
   - Expose AGENTESE paths via REST
   - Add tenant context middleware

3. **Add Metering Layer** (Phase 1B)
   - Deploy OpenMeter
   - Create CloudEvents adapter
   - Connect to existing event sources

4. **Complete Billing Chain** (Phase 2)
   - Deploy Lago
   - Connect to Stripe
   - Implement quota checks

### 8.2 Effort Reduction

| Original Estimate | Revised Estimate | Reason |
|-------------------|------------------|--------|
| Build AGENTESE API | Wire existing | 559 tests exist |
| Build K-Gent service | Wrap KgentFlux | Complete with streaming |
| Build trace collection | Deploy N-gent | 6 phases implemented |
| Build event system | Add CloudEvents adapter | SoulEvent + SemanticTrace exist |

**Estimated effort reduction: 40-50%**

---

## 9. Ledger Update

```yaml
ledger:
  PLAN: touched
  RESEARCH: touched
  DEVELOP: touched
  STRATEGIZE: touched
  CROSS-SYNERGIZE: touched  # <- This document
  IMPLEMENT: pending
  QA: pending
  TEST: pending
  EDUCATE: pending
  MEASURE: pending
  REFLECT: pending

entropy:
  budget: 0.10
  spent: 0.05
  remaining: 0.05
```

---

## 10. Continuation

```
⟿[IMPLEMENT]

concept.forest.manifest[phase=IMPLEMENT][sprint=foundation]@span=saas_impl

handles:
  - synergies: plans/saas/synergy-map.md
  - strategy: plans/saas/strategy-implementation.md

mission: Execute Phase 0 (Foundation) with knowledge of existing primitives.

key_insight: 40-50% less work than originally estimated.

continuation → Phase 0 infrastructure deployment
```

---

**Document Status**: Complete
**Key Finding**: Extensive existing infrastructure reduces SaaS implementation scope by 40-50%
**Next Phase**: IMPLEMENT (Phase 0: Foundation)
