# kgents SaaS Implementation Strategy

**Date**: December 14, 2025
**Phase**: STRATEGIZE
**Status**: Strategy Complete

---

## Executive Summary

This document sequences the IMPLEMENT work for kgents SaaS based on dependency analysis of the 4 DEVELOP artifacts. The strategy prioritizes risk reduction and learning velocity while enabling maximum parallelization across 3 independent tracks.

**Key Insight**: Infrastructure and Auth are universal blockers. Once established, AGENTESE Core, Billing/Metering, and GTM Marketing can proceed in parallel.

---

## 1. Dependency Graph

### 1.1 Critical Path Analysis

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      DEPENDENCY GRAPH (Critical Path in Bold)                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ╔═══════════════════════════════════════════════════════════════════════╗  │
│  ║                    PHASE 0: FOUNDATION (Blocking)                      ║  │
│  ║  ┌───────────────┐    ┌───────────────┐    ┌───────────────┐          ║  │
│  ║  │ K8s Cluster   │───▶│ PostgreSQL    │───▶│ Tenant RLS    │          ║  │
│  ║  │ (EKS/Kind)    │    │ + PgBouncer   │    │ Policies      │          ║  │
│  ║  └───────────────┘    └───────────────┘    └───────────────┘          ║  │
│  ║         │                    │                    │                    ║  │
│  ║         ▼                    ▼                    ▼                    ║  │
│  ║  ┌───────────────┐    ┌───────────────┐    ┌───────────────┐          ║  │
│  ║  │ Kong Gateway  │───▶│ Auth Service  │───▶│ API Keys      │          ║  │
│  ║  │ + Rate Limit  │    │ (JWT)         │    │ Management    │          ║  │
│  ║  └───────────────┘    └───────────────┘    └───────────────┘          ║  │
│  ╚═══════════════════════════════════════════════════════════════════════╝  │
│                                   │                                          │
│                 ┌─────────────────┼─────────────────┐                       │
│                 ▼                 ▼                 ▼                        │
│  ┌──────────────────────┐ ┌──────────────────────┐ ┌──────────────────────┐ │
│  │   TRACK A: CORE      │ │   TRACK B: BILLING   │ │   TRACK C: GTM       │ │
│  │   (AGENTESE + K-Gent)│ │   (Metering + $)     │ │   (Marketing)        │ │
│  ├──────────────────────┤ ├──────────────────────┤ ├──────────────────────┤ │
│  │                      │ │                      │ │                      │ │
│  │ ┌────────────────┐   │ │ ┌────────────────┐   │ │ ┌────────────────┐   │ │
│  │ │ NATS JetStream │   │ │ │ OpenMeter      │   │ │ │ Documentation  │   │ │
│  │ └───────┬────────┘   │ │ └───────┬────────┘   │ │ │ Site           │   │ │
│  │         │            │ │         │            │ │ └────────────────┘   │ │
│  │         ▼            │ │         ▼            │ │         │            │ │
│  │ ┌────────────────┐   │ │ ┌────────────────┐   │ │         ▼            │ │
│  │ │ Logos Invoker  │   │ │ │ Event Emission │   │ │ ┌────────────────┐   │ │
│  │ │ API            │   │ │ │ Pipeline       │   │ │ │ Landing Page   │   │ │
│  │ └───────┬────────┘   │ │ └───────┬────────┘   │ │ └────────────────┘   │ │
│  │         │            │ │         │            │ │         │            │ │
│  │         ▼            │ │         ▼            │ │         ▼            │ │
│  │ ┌────────────────┐   │ │ ┌────────────────┐   │ │ ┌────────────────┐   │ │
│  │ │ world.*/self.* │   │ │ │ Lago Billing   │   │ │ │ Discord +      │   │ │
│  │ │ Handlers       │   │ │ │ Orchestration  │   │ │ │ GitHub Public  │   │ │
│  │ └───────┬────────┘   │ │ └───────┬────────┘   │ │ └────────────────┘   │ │
│  │         │            │ │         │            │ │         │            │ │
│  │         ▼            │ │         ▼            │ │         ▼            │ │
│  │ ┌────────────────┐   │ │ ┌────────────────┐   │ │ ┌────────────────┐   │ │
│  │ │ K-Gent Session │   │ │ │ Stripe         │   │ │ │ Content        │   │ │
│  │ │ + Dialogue     │   │ │ │ Integration    │   │ │ │ Marketing      │   │ │
│  │ └───────┬────────┘   │ │ └───────┬────────┘   │ │ └────────────────┘   │ │
│  │         │            │ │         │            │ │                      │ │
│  │         ▼            │ │         ▼            │ │                      │ │
│  │ ┌────────────────┐   │ │ ┌────────────────┐   │ │                      │ │
│  │ │ Trace          │   │ │ │ Quota          │   │ │                      │ │
│  │ │ Collection     │◀──┼─┼─│ Enforcement    │   │ │                      │ │
│  │ └───────┬────────┘   │ │ └────────────────┘   │ │                      │ │
│  │         │            │ │                      │ │                      │ │
│  └─────────┼────────────┘ └──────────────────────┘ └──────────────────────┘ │
│            │                                                                 │
│            ▼                                                                 │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                    PHASE FINAL: INTEGRATION                          │    │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐ │    │
│  │  │ Dashboard   │  │ Playground  │  │ Usage       │  │ Beta        │ │    │
│  │  │ UI          │  │ UI          │  │ Dashboard   │  │ Launch      │ │    │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘ │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 1.2 Dependency Matrix

| Component | Depends On | Blocks |
|-----------|------------|--------|
| **K8s Cluster** | — | Everything |
| **PostgreSQL + RLS** | K8s | Auth, AGENTESE, K-Gent, Billing |
| **Redis** | K8s | Kong rate limiting, quota cache |
| **Kong Gateway** | K8s, Redis | All API services |
| **Auth Service** | PostgreSQL, Kong | All authenticated endpoints |
| **NATS JetStream** | K8s | Event emission, metering pipeline |
| **Logos Invoker** | Auth, NATS | world.*, self.*, K-Gent |
| **world.* Handler** | Logos | AGENTESE API, K-Gent |
| **self.* Handler** | Logos, PostgreSQL | AGENTESE API, K-Gent |
| **K-Gent Session** | AGENTESE handlers, PostgreSQL | K-Gent API |
| **OpenMeter** | NATS, ClickHouse | Usage API, billing |
| **Lago** | OpenMeter | Subscriptions, invoices |
| **Stripe** | Lago | Payments |
| **Trace Collection** | AGENTESE invokes | Observability dashboard |
| **Dashboard UI** | All APIs | — |

---

## 2. Parallel Implementation Tracks

### 2.1 Track Overview

```
Timeline (relative phases, not weeks)
═══════════════════════════════════════════════════════════════════════════════

PHASE 0    │ PHASE 1           │ PHASE 2         │ PHASE 3      │ PHASE 4
Foundation │ Core Tracks       │ Integration     │ Polish       │ Launch
═══════════│═══════════════════│═════════════════│══════════════│══════════

TRACK A    │ [AGENTESE Core]   │ [K-Gent]        │ [Observ.]    │
(Product)  │ ████████████████  │ ████████████    │ ██████████   │ [QA]
           │                   │                 │              │

TRACK B    │ [Metering]        │ [Billing]       │ [Quotas]     │
(Billing)  │ ██████████        │ ████████████    │ ████████     │ [QA]
           │                   │                 │              │

TRACK C    │ [Docs + Landing]  │ [Community]     │ [Content]    │
(GTM)      │ ████████████████  │ ████████████    │ ██████████   │ [Launch]
           │                   │                 │              │

SHARED     │                   │ [Dashboard UI]  │ [Playground] │
(UI)       │                   │ ██████████████  │ ██████████   │ [QA]
```

### 2.2 Track Definitions

#### Track A: Core Product (AGENTESE + K-Gent)

**Owner**: Product Engineering
**Entry**: Phase 0 complete (infra + auth)
**Exit**: AGENTESE invoke API + K-Gent dialogue API functional

| Phase | Deliverable | Entry Criteria | Exit Criteria |
|-------|-------------|----------------|---------------|
| 1A | NATS + Logos API | Auth working | `/v1/agentese/invoke` accepts requests |
| 1B | world.*/self.* Handlers | Logos routing | Paths resolve to handlers |
| 2A | K-Gent Session Mgmt | Handlers working | Sessions persist across requests |
| 2B | K-Gent Dialogue API | Sessions working | `/v1/kgent/sessions/*/messages` works |
| 3A | Trace Collection | K-Gent working | Traces stored, queryable |
| 3B | Observability API | Traces stored | `/v1/traces` returns data |

**Risk Focus**: LLM orchestration latency, AGENTESE path resolution correctness

---

#### Track B: Billing & Metering

**Owner**: Platform Engineering
**Entry**: Phase 0 complete (infra + auth)
**Exit**: Usage metering + Stripe checkout functional

| Phase | Deliverable | Entry Criteria | Exit Criteria |
|-------|-------------|----------------|---------------|
| 1A | OpenMeter Deploy | NATS running | Meters accepting events |
| 1B | Event Emission | Services emitting | Events visible in OpenMeter |
| 2A | Lago Deploy | OpenMeter working | Plans configured |
| 2B | Stripe Integration | Lago working | Checkout creates subscription |
| 3A | Quota Enforcement | Metering accurate | 429 returned at limits |
| 3B | Usage API | Quotas working | `/v1/billing/usage` accurate |

**Risk Focus**: Metering accuracy (under-billing = revenue loss, over-billing = churn)

---

#### Track C: Go-to-Market

**Owner**: Developer Relations + Marketing
**Entry**: API specs defined (can start during Phase 1)
**Exit**: Beta launch ready (docs, landing, community)

| Phase | Deliverable | Entry Criteria | Exit Criteria |
|-------|-------------|----------------|---------------|
| 1A | Documentation Site | API specs exist | Quickstart published |
| 1B | Landing Page | Pricing defined | Live with signup |
| 2A | GitHub Public | Core working | spec/ and impl/ public |
| 2B | Discord Community | GitHub public | Server configured, seeded |
| 3A | Content Calendar | Community exists | First 8 posts planned |
| 3B | Beta Invites | All tracks converged | 100 beta users invited |

**Risk Focus**: Documentation accuracy vs API changes, community engagement

---

### 2.3 Cross-Track Dependencies

```
Track A (Core)                Track B (Billing)           Track C (GTM)
─────────────                 ─────────────               ─────────────
                                    │
Logos API ─────────────────────▶ Event Emission
    │                               │
    ▼                               ▼
Handlers ───────────────────────▶ Metering
    │                               │
    ▼                               ▼
K-Gent ─────────────────────────▶ Quota Check ◀────────── Pricing Copy
    │                               │
    ▼                               ▼
Trace Collection ───────────────▶ Usage API ◀──────────── Usage Dashboard Docs
    │                               │
    └───────────────────────────────┼───────────────────▶ Playground ◀─── Tutorials
```

**Synchronization Points**:
1. **Event Schema Agreement** (Phase 1): Tracks A+B must agree on usage event format
2. **API Stability** (Phase 2): Track C docs must freeze when APIs stabilize
3. **Dashboard Integration** (Phase 3): UI requires both trace and billing APIs

---

## 3. Implementation Phases

### Phase 0: Foundation (Blocking)

**Purpose**: Establish infrastructure that everything depends on
**Parallelism**: Sequential within phase (dependency chain)
**Risk Level**: HIGH (any failure blocks all tracks)

#### Entry Criteria
- [ ] Cloud provider account configured (AWS/GCP)
- [ ] Domain registered, DNS configured
- [ ] CI/CD pipeline skeleton ready

#### Deliverables

| Component | Description | Acceptance Test |
|-----------|-------------|-----------------|
| K8s Cluster | EKS/GKE or local Kind for dev | `kubectl cluster-info` succeeds |
| PostgreSQL | RDS or self-hosted with PgBouncer | Connection via pooler works |
| Tenant RLS | Row-level security policies | Cross-tenant query returns 0 rows |
| Redis | ElastiCache or self-hosted | Kong rate limiter connects |
| Kong | API Gateway with JWT plugin | `/health` returns 200 |
| Auth Service | JWT validation, API key CRUD | Key created, JWT validated |
| Tenant Service | Tenant provisioning | Tenant created, context set |

#### Exit Criteria
- [ ] Authenticated request reaches a backend service
- [ ] Tenant isolation verified (RLS test passes)
- [ ] Rate limiting functional (429 after burst)
- [ ] All components pass health checks

#### Risk Mitigations
| Risk | Mitigation |
|------|------------|
| K8s complexity | Start with Kind locally, EKS for staging |
| RLS misconfiguration | Comprehensive test suite, security audit |
| Auth0/Clerk integration delays | JWT validation can work with self-signed for dev |

---

### Phase 1: Core Tracks Launch

**Purpose**: Get all three tracks independently productive
**Parallelism**: Full (Tracks A, B, C run concurrently)
**Risk Level**: MEDIUM (isolated failures don't cascade)

#### Track A: AGENTESE Core

| Step | Description | Acceptance Test |
|------|-------------|-----------------|
| 1A.1 | Deploy NATS JetStream | Stream created, messages published |
| 1A.2 | Logos Invoker Service | POST `/v1/agentese/invoke` returns 200 |
| 1A.3 | world.* Handler | `world.test.manifest` resolves |
| 1A.4 | self.* Handler | `self.memory.recall` persists |
| 1A.5 | LLM Integration | Claude/OpenRouter invoked correctly |

#### Track B: Metering Foundation

| Step | Description | Acceptance Test |
|------|-------------|-----------------|
| 1B.1 | Deploy OpenMeter | Admin UI accessible |
| 1B.2 | Configure Meters | `agentese_tokens` meter created |
| 1B.3 | Event Pipeline | Service → NATS → OpenMeter flows |
| 1B.4 | Basic Usage API | `/v1/billing/usage` returns counts |

#### Track C: GTM Foundation

| Step | Description | Acceptance Test |
|------|-------------|-----------------|
| 1C.1 | Docs site (Docusaurus/Mintlify) | Deployed, HTTPS |
| 1C.2 | Quickstart guide | 5-minute path validated |
| 1C.3 | API reference (auto-gen) | All endpoints documented |
| 1C.4 | Landing page | Live with email capture |

#### Phase 1 Exit Criteria
- [ ] AGENTESE invoke works end-to-end with LLM
- [ ] Usage events flowing to OpenMeter
- [ ] Documentation site publicly accessible
- [ ] Quickstart tested by 3 external developers

---

### Phase 2: Integration

**Purpose**: Connect tracks, build K-Gent, complete billing
**Parallelism**: High (but with sync points)
**Risk Level**: MEDIUM-HIGH (integration bugs)

#### Track A: K-Gent Service

| Step | Description | Acceptance Test |
|------|-------------|-----------------|
| 2A.1 | Session Management | Create, get, delete sessions |
| 2A.2 | Dialogue API | Message → response flow |
| 2A.3 | Kent Persona Config | Persona traits in responses |
| 2A.4 | Streaming Responses | SSE stream works |
| 2A.5 | Session Persistence | Sessions survive pod restart |

#### Track B: Billing Orchestration

| Step | Description | Acceptance Test |
|------|-------------|-----------------|
| 2B.1 | Deploy Lago | Admin UI accessible |
| 2B.2 | Configure Plans | 5 tiers created |
| 2B.3 | Stripe Integration | Checkout session creates customer |
| 2B.4 | Subscription Lifecycle | Create, upgrade, cancel work |
| 2B.5 | Invoice Generation | Monthly invoice generated |

#### Track C: Community Launch

| Step | Description | Acceptance Test |
|------|-------------|-----------------|
| 2C.1 | GitHub repos public | Stars > 0 |
| 2C.2 | Discord server | Channels configured |
| 2C.3 | First blog posts | 3 posts published |
| 2C.4 | YouTube video | Quickstart video live |

#### UI Track (Shared): Dashboard Foundation

| Step | Description | Acceptance Test |
|------|-------------|-----------------|
| 2U.1 | Dashboard shell | Login, navigation works |
| 2U.2 | API key management | Create, revoke keys |
| 2U.3 | Usage overview | Token count displays |
| 2U.4 | Subscription view | Current plan shown |

#### Phase 2 Exit Criteria
- [ ] K-Gent dialogue works with persona
- [ ] Stripe checkout creates paying customer
- [ ] Dashboard shows accurate usage data
- [ ] GitHub has external contributors

---

### Phase 3: Polish & Observability

**Purpose**: Production readiness, full observability
**Parallelism**: Medium (UI depends on stable APIs)
**Risk Level**: MEDIUM (scope creep risk)

#### Track A: Observability

| Step | Description | Acceptance Test |
|------|-------------|-----------------|
| 3A.1 | Trace Collection | All invokes create traces |
| 3A.2 | Tempo Integration | Traces queryable |
| 3A.3 | Trace Viewer UI | Full trace tree renders |
| 3A.4 | Cost per Request | Token costs calculated |

#### Track B: Quota & Limits

| Step | Description | Acceptance Test |
|------|-------------|-----------------|
| 3B.1 | Real-time Quota Check | 429 at tier limit |
| 3B.2 | Usage Alerts | Email at 80% |
| 3B.3 | Overage Billing | Charges calculated correctly |
| 3B.4 | Credit System | Credits applied to invoice |

#### Track C: Launch Prep

| Step | Description | Acceptance Test |
|------|-------------|-----------------|
| 3C.1 | Beta invite flow | 100 invites sent |
| 3C.2 | Onboarding sequence | 5-email drip active |
| 3C.3 | Feedback collection | In-app survey works |
| 3C.4 | Case study template | Ready for first story |

#### UI Track: Playground

| Step | Description | Acceptance Test |
|------|-------------|-----------------|
| 3U.1 | AGENTESE Playground | Path invoke works in UI |
| 3U.2 | K-Gent Chat UI | Chat interface works |
| 3U.3 | Trace Viewer | Linked from invoke result |
| 3U.4 | Usage Dashboard | Charts render accurately |

#### Phase 3 Exit Criteria
- [ ] p99 latency < 500ms
- [ ] Error rate < 1%
- [ ] All P0 features complete
- [ ] Security audit passed
- [ ] 10 beta users give positive feedback

---

### Phase 4: Beta Launch

**Purpose**: Live traffic, iterate on feedback
**Parallelism**: All hands on feedback/fixes
**Risk Level**: LOW (contained blast radius)

| Step | Description | Acceptance Test |
|------|-------------|-----------------|
| 4.1 | Private beta open | 100 users active |
| 4.2 | HN/Reddit posts | Posts submitted |
| 4.3 | Feedback triage | Issues categorized |
| 4.4 | Rapid iteration | 3 patch releases |
| 4.5 | Public beta decision | Go/no-go based on metrics |

#### Phase 4 Exit Criteria
- [ ] 100 beta users with ≥1 API call
- [ ] NPS > 30
- [ ] No P0 bugs open
- [ ] MRR > $0 (first paid customer)

---

## 4. Risk-Ordered Backlog

### 4.1 Risk Categories

| Category | Description | Priority |
|----------|-------------|----------|
| **Foundational** | Failure blocks everything | Do First |
| **Learning** | Unknown unknowns, need validation | Do Early |
| **Revenue** | Directly impacts monetization | Do Before Launch |
| **Quality** | Affects user experience | Do Before Beta |
| **Scale** | Only matters with traffic | Do After Validation |

### 4.2 Risk-Prioritized Backlog

| Priority | Item | Risk Category | Why This Order |
|----------|------|---------------|----------------|
| 1 | K8s + PostgreSQL RLS | Foundational | Universal blocker |
| 2 | Auth Service (JWT) | Foundational | All APIs need auth |
| 3 | Logos Invoker + LLM | Learning | Core value prop, unknown latency |
| 4 | AGENTESE Handlers | Learning | Path resolution complexity |
| 5 | Event Emission Pipeline | Learning | Metering accuracy critical |
| 6 | OpenMeter Integration | Revenue | Usage tracking = billing |
| 7 | K-Gent Session | Learning | Stateful service complexity |
| 8 | K-Gent Dialogue | Learning | LLM response quality |
| 9 | Lago + Stripe | Revenue | Payment processing |
| 10 | Trace Collection | Quality | Key differentiator |
| 11 | Quota Enforcement | Revenue | Prevent abuse, enable limits |
| 12 | Dashboard UI | Quality | User self-service |
| 13 | Playground | Quality | Developer experience |
| 14 | Documentation | Quality | Adoption friction |
| 15 | Landing Page | Quality | Conversion funnel |
| 16 | Observability Dashboard | Quality | Debug experience |
| 17 | Credit System | Revenue | Enterprise flexibility |
| 18 | Streaming Responses | Scale | Nice-to-have for MVP |
| 19 | Multiple LLM Providers | Scale | Fallback, later optimization |
| 20 | GPU Node Pool | Scale | Only for fine-tuning |

### 4.3 High-Risk Items (Early Learning)

These items have the highest uncertainty and should be tackled early:

1. **LLM Orchestration Latency** (Items 3-4)
   - Unknown: How fast can we invoke AGENTESE paths?
   - Mitigation: Prototype in Phase 1, measure p99
   - Fallback: Simplify handler chains if too slow

2. **Metering Accuracy** (Items 5-6)
   - Unknown: Can we count tokens accurately in real-time?
   - Mitigation: End-to-end test with known token counts
   - Fallback: Async reconciliation if real-time fails

3. **K-Gent State Management** (Items 7-8)
   - Unknown: Session persistence across pod restarts
   - Mitigation: Redis-backed sessions, test failure scenarios
   - Fallback: Shorter session timeouts

4. **Multi-Tenant Isolation** (Item 1)
   - Unknown: Any RLS bypass vectors?
   - Mitigation: Security audit, penetration testing
   - Fallback: Schema-per-tenant for Enterprise

---

## 5. Branch Candidates

### 5.1 Classification Criteria

| Classification | Definition | Action |
|----------------|------------|--------|
| **Blocking** | Must complete before dependent work | Critical path |
| **Parallel** | Can run independently | Assign to separate track |
| **Deferred** | Not needed for MVP | Backlog for later |
| **Void** | Does not fit current scope | Document and archive |

### 5.2 Branch Analysis

#### Blocking Branches (Cannot Parallelize)

| Branch | Blocked By | Blocks | Reasoning |
|--------|-----------|--------|-----------|
| Auth Service | K8s, PostgreSQL | All APIs | Security foundation |
| Logos Invoker | Auth, NATS | All AGENTESE | Core routing |
| OpenMeter | NATS | Billing, Quotas | Usage data source |

#### Parallel Branches (Independent Tracks)

| Branch | Track | Can Start After | Reasoning |
|--------|-------|-----------------|-----------|
| K-Gent Service | A | AGENTESE handlers | Only needs handlers API |
| Lago Billing | B | OpenMeter | Only needs usage data |
| Documentation | C | API specs defined | Can use mocks |
| Landing Page | C | Pricing defined | Static content |
| Dashboard UI | Shared | API contracts | Can stub backends |

#### Deferred Branches (Post-MVP)

| Branch | Reason for Deferral | Trigger to Reactivate |
|--------|--------------------|-----------------------|
| void.*/time.*/concept.* contexts | Complexity, not core MVP | User demand, v1.1 planning |
| Custom Personas | K-gent variants | Enterprise requests |
| Multi-agent Orchestration | Architectural complexity | Clear use cases emerge |
| Fine-tuning Infrastructure | GPU costs, complexity | Enterprise contract |
| Enterprise SSO | Auth0/Clerk handles most | Enterprise deal requires |
| VS Code Extension | DX enhancement | Community request |

#### Void Branches (Out of Scope)

| Branch | Reason | Documentation |
|--------|--------|---------------|
| Mobile Apps | API-first approach | Not planned |
| On-premise Deployment | Self-hosted covers 90% | Enterprise-only if needed |
| Marketplace | Premature | Revisit Year 2 |

---

## 6. Shared Primitive Opportunities

### 6.1 Cross-Track Reuse

Components that serve multiple tracks:

| Primitive | Used By | Implementation |
|-----------|---------|----------------|
| **Tenant Context** | All services | Middleware extracting from JWT |
| **Usage Event Emitter** | AGENTESE, K-Gent, Storage | Shared NATS producer lib |
| **Error Response Format** | All APIs | Shared response schema |
| **Trace Context Propagation** | All services | OpenTelemetry middleware |
| **Rate Limit Headers** | All APIs | Kong plugin output |

### 6.2 AGENTESE Path Reuse

Paths that serve multiple features:

| Path | Features Using It |
|------|-------------------|
| `self.memory.*` | K-Gent sessions, Agent state |
| `world.*.witness` | Observability dashboard, N-gent traces |
| `self.capability.*` | Tool execution, K-Gent abilities |

### 6.3 Event Schema Standardization

All tracks emit events to the same schema:

```json
{
  "id": "uuid-v7",
  "source": "agentese|kgent|billing|...",
  "type": "agentese.tokens|kgent.session_start|...",
  "subject": "tenant_id",
  "time": "ISO8601",
  "data": { "...": "..." }
}
```

---

## 7. Implementation Principles

### 7.1 From Project Philosophy

1. **Tasteful Scope (P1)**: Start smaller, validate, expand
   - Each phase delivers usable value
   - Resist feature creep within phases

2. **Compositional (P5)**: Build primitives that compose
   - Usage Event Emitter used everywhere
   - Tenant Context middleware shared

3. **No Premature Abstraction**: Simplest thing that works
   - Single LLM provider in Phase 1
   - Add fallbacks only when needed

### 7.2 Phase Boundaries

- **Phase 0**: Foundation complete = authentication works
- **Phase 1**: Core works = can invoke AGENTESE, see usage
- **Phase 2**: Product works = K-Gent chats, billing flows
- **Phase 3**: Polish works = traces visible, quotas enforced
- **Phase 4**: Launch works = users active, feedback loop

### 7.3 Decision Criteria for Scope Changes

| Question | Yes → | No → |
|----------|-------|------|
| Does this block a critical path? | Add to current phase | Defer |
| Does this reduce high-priority risk? | Add to current phase | Defer |
| Do 3+ beta users request this? | Prioritize for next phase | Monitor |
| Can we ship without this? | Defer | Add to current phase |

---

## 8. Continuation Points

### 8.1 Ledger Update

```yaml
ledger:
  PLAN: touched
  RESEARCH: touched
  DEVELOP: touched
  STRATEGIZE: touched
  CROSS-SYNERGIZE: touched  # Completed 2025-12-14
  IMPLEMENT: pending
  QA: pending
  TEST: pending
  EDUCATE: pending
  MEASURE: pending
  REFLECT: pending

synergy_findings:
  existing_tests: 559
  effort_reduction: "40-50%"
  key_insight: "Extensive AGENTESE + K-gent infrastructure exists"
```

### 8.2 Next Phase: IMPLEMENT

**CROSS-SYNERGIZE Complete**: See [synergy-map.md](./synergy-map.md) for full analysis.

**Key Finding**: 40-50% less implementation work than originally estimated due to existing infrastructure:
- All 5 AGENTESE contexts fully implemented
- K-gent soul, persona, streaming (KgentFlux) complete
- N-gent traces (6 phases) complete
- Billing primitives (Stripe) exist
- Prometheus-compatible metrics exist

```
⟿[IMPLEMENT]

concept.forest.manifest[phase=IMPLEMENT][sprint=foundation]@span=saas_impl

handles:
  - strategy: plans/saas/strategy-implementation.md
  - synergies: plans/saas/synergy-map.md
  - platform: plans/saas/architecture-platform.md
  - scope: plans/saas/mvp-scope.md

ledger: {PLAN:touched, RESEARCH:touched, DEVELOP:touched, STRATEGIZE:touched, CROSS-SYNERGIZE:touched, IMPLEMENT:in_progress}
entropy: 0.05 remaining

mission: Execute Phase 0 (Foundation) from Section 3.

actions (Phase 0: Foundation):
  1. K8s Cluster — Set up local Kind or staging EKS
  2. PostgreSQL + RLS — Deploy with tenant isolation policies
  3. Redis — Deploy for rate limiting cache
  4. Kong Gateway — Configure with JWT plugin
  5. Auth Service — Implement JWT validation + API key CRUD
  6. Tenant Service — Implement tenant provisioning

exit_criteria:
  - kubectl cluster-info succeeds
  - Authenticated request reaches backend
  - RLS tenant isolation verified
  - Rate limiting returns 429 after burst
  - All health checks pass

continuation → IMPLEMENT (Phase 1: Core Tracks) or ⟂[BLOCKED] if foundation fails
```

---

## References

- [architecture-platform.md](./architecture-platform.md) - Platform architecture
- [architecture-billing.md](./architecture-billing.md) - Billing architecture
- [mvp-scope.md](./mvp-scope.md) - MVP feature scope
- [gtm-plan.md](./gtm-plan.md) - Go-to-market plan
- [synergy-map.md](./synergy-map.md) - **Synergy analysis (CROSS-SYNERGIZE output)**
- [spec/protocols/agentese.md](../../spec/protocols/agentese.md) - AGENTESE specification
- [impl/claude/protocols/agentese/](../../impl/claude/protocols/agentese/) - AGENTESE implementation

---

**Document Status**: Strategy + Synergies Complete
**Next Phase**: IMPLEMENT (Phase 0: Foundation)
**Owner**: Platform Architecture Team
