# kgents SaaS Phase 1: IMPLEMENT

**Date**: 2025-12-14
**Cycle**: SaaS Foundation
**Phase**: IMPLEMENT (Phase 1: Core Tracks)
**Previous**: Phase 0 Foundation (Complete)

---

## Ledger

```yaml
phase_ledger:
  PLAN: touched          # plans/saas/strategy-implementation.md
  RESEARCH: touched      # Codebase analysis, synergy map
  DEVELOP: touched       # Schema design, Kong config, Python models
  STRATEGIZE: touched    # 4-track parallel strategy
  CROSS-SYNERGIZE: touched  # synergy-map.md - 40-50% effort reduction
  IMPLEMENT: in_progress # Phase 0 complete, Phase 1 starting
  QA: pending
  TEST: pending
  EDUCATE: pending
  MEASURE: pending
  REFLECT: pending

entropy:
  budget: 0.10
  spent: 0.03           # Phase 0 exploration
  remaining: 0.07
```

---

## Phase 0 Summary (Complete)

### Infrastructure Deployed
- **K8s Cluster**: `kgents-triad` running (Kind)
- **PostgreSQL**: Running with pgvector, CDC outbox, triggers
- **Redis**: Running for caching/rate limiting
- **Qdrant**: Running for vector search
- **Kong Gateway**: 2 replicas in `kgents-gateway` namespace

### Multi-Tenant Schema Created
| Table | Purpose | RLS |
|-------|---------|-----|
| `tenants` | Organizations with Stripe integration | Yes |
| `users` | Tenant members with RBAC | Yes |
| `api_keys` | Programmatic access (SHA-256 hashed) | Yes |
| `sessions` | K-Gent conversation sessions | Yes |
| `messages` | Chat message history | Yes |
| `usage_events` | Billing/metering events | Yes |

### Python Module Created
- `protocols/tenancy/` - Full tenant service
- **69 tests passing**
- Models: Tenant, TenantUser, ApiKey, Session, UsageEvent
- Context: Thread-safe tenant context with contextvars
- API Keys: Secure generation with SHA-256 hashing

### Files Created/Modified
```
impl/claude/infra/k8s/manifests/triad/05-multitenancy.yaml  # SQL migrations
impl/claude/infra/k8s/manifests/triad/06-kong.yaml          # Kong Gateway
impl/claude/protocols/tenancy/__init__.py
impl/claude/protocols/tenancy/models.py
impl/claude/protocols/tenancy/context.py
impl/claude/protocols/tenancy/api_keys.py
impl/claude/protocols/tenancy/service.py
impl/claude/protocols/tenancy/_tests/test_models.py
impl/claude/protocols/tenancy/_tests/test_context.py
impl/claude/protocols/tenancy/_tests/test_api_keys.py
impl/claude/protocols/tenancy/_tests/test_service.py
```

### Exit Criteria Verified
- [x] `kubectl cluster-info` succeeds
- [x] PostgreSQL running with tenant table (1 dev tenant)
- [x] Redis responds to PING
- [x] Kong is healthy (2 replicas)
- [x] RLS policies installed on all tenant-scoped tables
- [x] Python tenancy module tests pass (69/69)

---

## Phase 1 Mission: Core Tracks Launch

Per `plans/saas/strategy-implementation.md` Section 3 (Phase 1), implement the three parallel tracks:

### Track A: AGENTESE Core
| Step | Deliverable | Acceptance Test |
|------|-------------|-----------------|
| 1A.1 | Deploy NATS JetStream | Stream created, messages published |
| 1A.2 | Logos Invoker Service | POST `/v1/agentese/invoke` returns 200 |
| 1A.3 | world.* Handler | `world.test.manifest` resolves |
| 1A.4 | self.* Handler | `self.memory.recall` persists |
| 1A.5 | LLM Integration | Claude/OpenRouter invoked correctly |

### Track B: Metering Foundation
| Step | Deliverable | Acceptance Test |
|------|-------------|-----------------|
| 1B.1 | Deploy OpenMeter | Admin UI accessible |
| 1B.2 | Configure Meters | `agentese_tokens` meter created |
| 1B.3 | Event Pipeline | Service → NATS → OpenMeter flows |
| 1B.4 | Basic Usage API | `/v1/billing/usage` returns counts |

### Track C: GTM Foundation
| Step | Deliverable | Acceptance Test |
|------|-------------|-----------------|
| 1C.1 | API documentation | OpenAPI spec generated |
| 1C.2 | Quickstart guide | 5-minute path validated |

---

## Existing Infrastructure to Wire

From synergy-map.md, these exist and need REST wiring:

| Component | Location | Status |
|-----------|----------|--------|
| **Logos Resolver** | `protocols/agentese/logos.py` | Complete (559 tests) |
| **All 5 Contexts** | `protocols/agentese/contexts/` | Complete |
| **KgentSoul** | `agents/k/soul.py` | Complete |
| **KgentFlux** | `agents/k/flux.py` | Complete (streaming) |
| **StripeClient** | `protocols/billing/stripe_client.py` | Complete |
| **Metrics** | `protocols/agentese/metrics.py` | Complete (Prometheus) |

---

## Continuation Prompt

```
⟿[IMPLEMENT]

concept.forest.manifest[phase=IMPLEMENT][sprint=phase1_core]@span=saas_impl

/hydrate

handles:
  - strategy: plans/saas/strategy-implementation.md
  - synergies: plans/saas/synergy-map.md
  - tenancy: impl/claude/protocols/tenancy/
  - kong: impl/claude/infra/k8s/manifests/triad/06-kong.yaml
  - multitenancy: impl/claude/infra/k8s/manifests/triad/05-multitenancy.yaml

ledger: {PLAN:touched, RESEARCH:touched, DEVELOP:touched, STRATEGIZE:touched, CROSS-SYNERGIZE:touched, IMPLEMENT:in_progress}
entropy: 0.07 remaining

mission: Execute Phase 1 (Core Tracks Launch) from strategy-implementation.md Section 3.

priority_order:
  1. Create FastAPI app with tenant middleware (protocols/api/)
  2. Wire existing Logos resolver to REST endpoint /v1/agentese/invoke
  3. Wire existing KgentFlux to REST/SSE endpoint /v1/kgent/sessions
  4. Add CloudEvents adapter for usage metering
  5. Deploy NATS JetStream for event pipeline

actions:
  - Read protocols/api/app.py to understand existing API structure
  - Create /v1/agentese/invoke endpoint using existing logos.invoke()
  - Create /v1/kgent/sessions/* endpoints using existing KgentFlux
  - Add tenant context middleware to inject tenant from API key
  - Wire usage events to protocols/tenancy/service.py

exit_criteria:
  - POST /v1/agentese/invoke works with API key auth
  - POST /v1/kgent/sessions creates session with tenant_id
  - GET /v1/kgent/sessions/{id}/messages returns SSE stream
  - Usage events recorded in usage_events table
  - All new tests pass

continuation → QA (lint/type/security checks) then TEST
```

---

## Next Session Continuation Prompt

After completing Phase 1 IMPLEMENT, the next session should use:

```markdown
⟿[QA]

concept.forest.manifest[phase=QA][sprint=phase1_qa]@span=saas_impl

/hydrate

handles:
  - code: impl/claude/protocols/api/
  - tests: impl/claude/protocols/api/_tests/
  - tenancy: impl/claude/protocols/tenancy/

ledger: {PLAN:touched, RESEARCH:touched, DEVELOP:touched, STRATEGIZE:touched, CROSS-SYNERGIZE:touched, IMPLEMENT:touched, QA:in_progress}
entropy: ${remaining_entropy}

mission: Gate quality/security/lawfulness before broader testing.

actions:
  - uv run mypy impl/claude/protocols/api/
  - uv run ruff check impl/claude/protocols/api/
  - Security audit: API key handling, tenant isolation
  - Docstring coverage check

exit_criteria:
  - mypy passes with no errors
  - ruff passes with no errors
  - No security issues in API key handling
  - Tenant isolation verified in tests

continuation → TEST (run full test suite, add integration tests)
```

---

## Branch Candidates

| Branch | Classification | Notes |
|--------|----------------|-------|
| NATS JetStream deployment | Parallel | Can proceed independently |
| OpenMeter integration | Deferred | Depends on NATS, can mock for MVP |
| Dashboard UI | Deferred | Phase 2 work |
| Playground UI | Deferred | Phase 3 work |

---

## Blockers

- None identified. Foundation complete. Ready for core implementation.

---

**Document Status**: Continuation prompt ready
**Next Phase**: IMPLEMENT (Phase 1: Core Tracks)
**Exit Signifier**: ⟿[IMPLEMENT] upon human approval
