# kgents SaaS MVP Feature Scope

**Date**: December 14, 2025
**Phase**: DEVELOP
**Status**: Scope Complete

---

## Executive Summary

This document defines the Minimum Viable Product (MVP) scope for kgents SaaS, based on competitive gaps identified in `research-competitive.md` and unmet community needs from `research-community.md`. The MVP focuses on three core differentiators: **AGENTESE protocol access**, **K-gent persona interactions**, and **transparent observability**.

### MVP Vision Statement

> "A tasteful, specification-first agent platform that developers can actually debug, with transparent costs and self-hosting options."

---

## 1. MVP Value Proposition

### 1.1 Unique Differentiators

Based on competitive analysis, kgents fills these critical market gaps:

| Gap | Competitor Pain | kgents Solution |
|-----|-----------------|-----------------|
| **Complexity creep** | LangChain "rabbit hole" | Verb-first AGENTESE simplicity |
| **Black box agents** | "Can't debug when it breaks" | N-gent witness/trace observability |
| **Framework fatigue** | Overengineered abstractions | Spec-first, composable primitives |
| **Cost explosions** | $2K surprise cloud bills | Transparent metering, self-host option |
| **Sterile UX** | "Agents feel robotic" | K-gent personality and joy |

### 1.2 Target Users (MVP)

| Persona | Description | Priority |
|---------|-------------|----------|
| **Framework Refugee** | Developers burned by LangChain/LangGraph complexity | P0 |
| **Privacy-First Builder** | Devs needing self-hosted, data-sovereign agents | P0 |
| **Cost-Conscious Indie** | Solo developers with cloud bill trauma | P1 |
| **Production Skeptic** | Teams who've seen 95% pilot failure rate | P1 |

---

## 2. MVP Feature Set

### 2.1 MoSCoW Prioritization

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           MVP FEATURE PRIORITY                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  MUST HAVE (MVP Launch)                                                      │
│  ├── AGENTESE Core Protocol                                                  │
│  │   ├── Logos invoker (path → handler)                                      │
│  │   ├── world.* context (external entities)                                 │
│  │   ├── self.* context (memory, capabilities)                               │
│  │   └── Basic tool execution                                                │
│  ├── K-Gent Persona                                                          │
│  │   ├── Session management                                                  │
│  │   ├── Dialogue API                                                        │
│  │   └── Default Kent persona                                                │
│  ├── Observability Dashboard                                                 │
│  │   ├── Request tracing (witness)                                           │
│  │   ├── Token consumption                                                   │
│  │   └── Cost tracking                                                       │
│  └── Core Platform                                                           │
│      ├── Auth (JWT, API keys)                                                │
│      ├── Tenant isolation                                                    │
│      └── Usage metering                                                      │
│                                                                              │
│  SHOULD HAVE (MVP+1)                                                         │
│  ├── void.* context (entropy, gratitude)                                     │
│  ├── time.* context (traces, forecasts)                                      │
│  ├── concept.* context (platonics)                                           │
│  ├── Multiple LLM providers                                                  │
│  ├── Self-hosted deployment guide                                            │
│  └── Credit system                                                           │
│                                                                              │
│  COULD HAVE (v1.1+)                                                          │
│  ├── Custom personas (K-gent variants)                                       │
│  ├── Agent templates marketplace                                             │
│  ├── Team collaboration features                                             │
│  ├── Webhook integrations                                                    │
│  └── VS Code extension                                                       │
│                                                                              │
│  WON'T HAVE (Future)                                                         │
│  ├── Multi-agent orchestration                                               │
│  ├── Fine-tuning infrastructure                                              │
│  ├── Enterprise SSO                                                          │
│  └── On-premise deployment                                                   │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Core Features (MUST HAVE)

### 3.1 AGENTESE Protocol Access

#### 3.1.1 Logos Invoker

**Description**: Core engine for invoking AGENTESE paths

**User Story**:
> As a developer, I want to invoke AGENTESE paths (e.g., `world.house.manifest`) so that I can interact with agents using the verb-first ontology.

**Acceptance Criteria**:
- [ ] Accept path strings in format `context.noun.aspect`
- [ ] Route to appropriate context handler
- [ ] Return structured responses with metadata
- [ ] Support async invocation
- [ ] Emit usage events for metering
- [ ] Handle errors with clear messages

**API Endpoint**:
```
POST /v1/agentese/invoke
{
  "path": "world.house.manifest",
  "umwelt": {
    "observer": "architect",
    "context": { ... }
  }
}

Response:
{
  "result": { ... },
  "metadata": {
    "tokens_used": 1250,
    "duration_ms": 342,
    "trace_id": "abc123"
  }
}
```

#### 3.1.2 world.* Context Handler

**Description**: External entity interactions

**User Story**:
> As a developer, I want to query external entities through `world.*` paths so that agents can perceive the environment.

**Acceptance Criteria**:
- [ ] Support `world.*.manifest` for observation
- [ ] Support `world.*.witness` for history
- [ ] Handle observer-dependent perceptions
- [ ] Integrate with external tools/APIs
- [ ] Cache frequent lookups

**Supported Aspects**:
| Aspect | Description | MVP Scope |
|--------|-------------|-----------|
| `manifest` | Collapse to observer view | Yes |
| `witness` | Show interaction history | Yes |
| `refine` | Dialectical challenge | No (v1.1) |

#### 3.1.3 self.* Context Handler

**Description**: Agent internal state and capabilities

**User Story**:
> As a developer, I want agents to access their own memory and capabilities via `self.*` so that they maintain state across interactions.

**Acceptance Criteria**:
- [ ] `self.memory.*` for persistent state
- [ ] `self.capability.*` for available tools
- [ ] `self.soul.*` for K-gent integration
- [ ] Tenant-isolated storage
- [ ] Configurable retention policies

---

### 3.2 K-Gent Persona Service

#### 3.2.1 Session Management

**Description**: Manage interactive K-gent sessions

**User Story**:
> As a developer, I want to create and manage K-gent sessions so that users can have persistent conversations with the Kent persona.

**Acceptance Criteria**:
- [ ] Create new sessions with unique IDs
- [ ] Maintain session state across requests
- [ ] Session timeout after 30 minutes of inactivity
- [ ] Explicit session termination
- [ ] Session history retrieval

**API Endpoints**:
```
POST /v1/kgent/sessions
{
  "persona": "kent_default"
}
→ { "session_id": "ses_abc123", "expires_at": "..." }

POST /v1/kgent/sessions/{session_id}/messages
{
  "content": "Hello, Kent!"
}
→ {
  "response": "Hey! Great to chat...",
  "metadata": { ... }
}

DELETE /v1/kgent/sessions/{session_id}
→ { "status": "terminated" }
```

#### 3.2.2 Dialogue API

**Description**: Send messages and receive responses from K-gent

**User Story**:
> As a developer, I want to send messages to K-gent and receive contextual responses so that users experience the Kent persona.

**Acceptance Criteria**:
- [ ] Accept text messages
- [ ] Return persona-appropriate responses
- [ ] Maintain conversation context
- [ ] Stream responses (optional)
- [ ] Handle rate limiting gracefully

#### 3.2.3 Default Kent Persona

**Description**: Pre-configured Kent simulacra persona

**User Story**:
> As a user, I want to interact with a default Kent persona so that I experience the kgents philosophy through conversation.

**Acceptance Criteria**:
- [ ] Tasteful, curated responses
- [ ] Joy-inducing personality
- [ ] Ethical guardrails
- [ ] Consistent voice/tone
- [ ] Graceful handling of edge cases

**Persona Configuration**:
```yaml
personas:
  kent_default:
    name: "Kent"
    description: "The default K-gent persona"
    traits:
      - tasteful
      - curious
      - philosophical
      - technical_depth
      - humor: subtle
    guardrails:
      - ethical_augmentation
      - no_replacement_of_judgment
      - bounded_autonomy
    system_prompt: |
      You are Kent, the K-gent persona. You embody the kgents
      philosophy: tasteful, curated, ethical, and joy-inducing.
      You help developers build better agents while maintaining
      a thoughtful, sometimes playful personality.
```

---

### 3.3 Observability Dashboard

#### 3.3.1 Request Tracing (Witness)

**Description**: Trace all AGENTESE invocations with full visibility

**User Story**:
> As a developer, I want to see detailed traces of every agent request so that I can debug issues without guessing what went wrong.

**Acceptance Criteria**:
- [ ] Trace ID for every request
- [ ] Full path execution breakdown
- [ ] Input/output at each step
- [ ] Duration per step
- [ ] Error highlighting
- [ ] Search by trace ID
- [ ] Filter by path, time, status

**Trace View**:
```
Trace: abc123 | world.house.manifest | 342ms | SUCCESS

├─ [0ms] Request received
│  └─ path: world.house.manifest
│  └─ observer: architect
│
├─ [5ms] Logos router
│  └─ handler: world_handler
│  └─ noun: house
│
├─ [12ms] Context lookup
│  └─ source: external_api
│  └─ cache: MISS
│
├─ [280ms] LLM inference
│  └─ model: claude-3-5-sonnet
│  └─ tokens_in: 850
│  └─ tokens_out: 400
│
└─ [340ms] Response formatted
   └─ status: success
```

#### 3.3.2 Token Consumption

**Description**: Real-time token usage visibility

**User Story**:
> As a developer, I want to see exactly how many tokens each request uses so that I can optimize costs and avoid surprises.

**Acceptance Criteria**:
- [ ] Per-request token breakdown (input/output)
- [ ] Aggregated daily/weekly/monthly views
- [ ] By agent, path, or model
- [ ] Comparison to tier limits
- [ ] Export to CSV

**Dashboard Components**:
```
┌─────────────────────────────────────────┐
│ Token Usage - Last 30 Days              │
├─────────────────────────────────────────┤
│ ████████████░░░░░░░░ 58,000 / 100,000   │
│                                         │
│ Today:     2,450 tokens                 │
│ This week: 15,230 tokens                │
│ This month: 58,000 tokens               │
│                                         │
│ By Model:                               │
│  claude-3-5-sonnet: 45,000 (78%)        │
│  gpt-4o: 13,000 (22%)                   │
│                                         │
│ Top Paths:                              │
│  world.*.manifest: 32,000               │
│  self.memory.recall: 18,000             │
│  kgent.dialogue: 8,000                  │
└─────────────────────────────────────────┘
```

#### 3.3.3 Cost Tracking

**Description**: Real-time cost visibility with projections

**User Story**:
> As a developer, I want to see my current costs and projected monthly spend so that I never get surprised by bills.

**Acceptance Criteria**:
- [ ] Real-time cost accumulator
- [ ] Daily/weekly/monthly breakdown
- [ ] Projection based on usage trends
- [ ] Alerts at 50%, 80%, 100% of tier
- [ ] Cost per agent/path breakdown

---

### 3.4 Core Platform

#### 3.4.1 Authentication

**Description**: Secure access to kgents APIs

**User Story**:
> As a developer, I want to authenticate with API keys so that I can securely access kgents services.

**Acceptance Criteria**:
- [ ] API key generation in dashboard
- [ ] Multiple keys per tenant
- [ ] Key rotation support
- [ ] Key scoping (read/write/admin)
- [ ] JWT for dashboard sessions
- [ ] Rate limiting per key

#### 3.4.2 Tenant Isolation

**Description**: Secure multi-tenant data isolation

**User Story**:
> As a developer, I want my data completely isolated from other tenants so that I can trust kgents with sensitive information.

**Acceptance Criteria**:
- [ ] Row-Level Security on all tables
- [ ] Tenant ID in all queries
- [ ] Isolated storage paths
- [ ] No cross-tenant data leakage
- [ ] Audit logging per tenant

#### 3.4.3 Usage Metering

**Description**: Accurate usage tracking for billing

**User Story**:
> As a developer, I want accurate usage tracking so that I only pay for what I use.

**Acceptance Criteria**:
- [ ] Event emission for all billable actions
- [ ] Real-time usage aggregation
- [ ] Quota enforcement at tier limits
- [ ] Clear overage notifications
- [ ] Usage API for programmatic access

---

## 4. API Specification

### 4.1 AGENTESE API

```yaml
openapi: 3.0.3
info:
  title: kgents AGENTESE API
  version: 1.0.0

paths:
  /v1/agentese/invoke:
    post:
      summary: Invoke an AGENTESE path
      requestBody:
        content:
          application/json:
            schema:
              type: object
              required: [path]
              properties:
                path:
                  type: string
                  example: "world.house.manifest"
                umwelt:
                  type: object
                  properties:
                    observer:
                      type: string
                    context:
                      type: object
                options:
                  type: object
                  properties:
                    model:
                      type: string
                      enum: [claude-3-5-sonnet, gpt-4o]
                    stream:
                      type: boolean
      responses:
        200:
          description: Successful invocation
          content:
            application/json:
              schema:
                type: object
                properties:
                  result:
                    type: object
                  metadata:
                    type: object
                    properties:
                      tokens_used:
                        type: integer
                      duration_ms:
                        type: integer
                      trace_id:
                        type: string
        429:
          description: Rate limited or quota exceeded

  /v1/agentese/paths:
    get:
      summary: List available AGENTESE paths
      responses:
        200:
          description: List of paths
          content:
            application/json:
              schema:
                type: object
                properties:
                  paths:
                    type: array
                    items:
                      type: object
                      properties:
                        path:
                          type: string
                        description:
                          type: string
                        aspects:
                          type: array
                          items:
                            type: string
```

### 4.2 K-Gent API

```yaml
paths:
  /v1/kgent/sessions:
    post:
      summary: Create a new K-gent session
      requestBody:
        content:
          application/json:
            schema:
              type: object
              properties:
                persona:
                  type: string
                  default: kent_default
      responses:
        201:
          description: Session created
          content:
            application/json:
              schema:
                type: object
                properties:
                  session_id:
                    type: string
                  persona:
                    type: string
                  expires_at:
                    type: string
                    format: date-time

  /v1/kgent/sessions/{session_id}/messages:
    post:
      summary: Send message to K-gent
      parameters:
        - name: session_id
          in: path
          required: true
          schema:
            type: string
      requestBody:
        content:
          application/json:
            schema:
              type: object
              required: [content]
              properties:
                content:
                  type: string
                stream:
                  type: boolean
                  default: false
      responses:
        200:
          description: Response from K-gent
          content:
            application/json:
              schema:
                type: object
                properties:
                  response:
                    type: string
                  metadata:
                    type: object

    get:
      summary: Get session message history
      parameters:
        - name: session_id
          in: path
          required: true
          schema:
            type: string
        - name: limit
          in: query
          schema:
            type: integer
            default: 50
      responses:
        200:
          description: Message history
```

### 4.3 Observability API

```yaml
paths:
  /v1/traces:
    get:
      summary: List traces
      parameters:
        - name: start
          in: query
          schema:
            type: string
            format: date-time
        - name: end
          in: query
          schema:
            type: string
            format: date-time
        - name: path
          in: query
          schema:
            type: string
        - name: status
          in: query
          schema:
            type: string
            enum: [success, error]
        - name: limit
          in: query
          schema:
            type: integer
            default: 100
      responses:
        200:
          description: List of traces

  /v1/traces/{trace_id}:
    get:
      summary: Get trace details
      responses:
        200:
          description: Full trace with spans

  /v1/usage:
    get:
      summary: Get usage metrics
      parameters:
        - name: period
          in: query
          schema:
            type: string
            enum: [day, week, month]
        - name: metric
          in: query
          schema:
            type: string
            enum: [tokens, sessions, api_calls]
      responses:
        200:
          description: Usage metrics
```

---

## 5. UI/UX Requirements

### 5.1 Dashboard Pages

| Page | Purpose | Priority |
|------|---------|----------|
| **Overview** | Usage summary, quick stats, alerts | P0 |
| **Playground** | Interactive AGENTESE/K-gent testing | P0 |
| **Traces** | Request tracing and debugging | P0 |
| **Usage** | Detailed usage metrics | P0 |
| **API Keys** | Key management | P0 |
| **Settings** | Account, billing, preferences | P0 |
| **Docs** | Embedded documentation | P1 |

### 5.2 Playground Experience

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ AGENTESE Playground                                              [K-Gent] ▼ │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  Path: [world.house.manifest                              ] [Invoke]        │
│                                                                              │
│  ┌─ Umwelt ──────────────────────┐  ┌─ Options ──────────────────────────┐ │
│  │ Observer: [architect      ] ▼ │  │ Model: [claude-3-5-sonnet] ▼      │ │
│  │ Context:                      │  │ Stream: [x]                        │ │
│  │ {                             │  │                                    │ │
│  │   "project": "villa"          │  │                                    │ │
│  │ }                             │  │                                    │ │
│  └───────────────────────────────┘  └────────────────────────────────────┘ │
│                                                                              │
│  ┌─ Result ─────────────────────────────────────────────────────────────┐  │
│  │ {                                                                     │  │
│  │   "blueprint": {                                                      │  │
│  │     "type": "residential",                                            │  │
│  │     "style": "mediterranean",                                         │  │
│  │     ...                                                               │  │
│  │   }                                                                   │  │
│  │ }                                                                     │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
│                                                                              │
│  Tokens: 1,250 (input: 850, output: 400) | Duration: 342ms | [View Trace]   │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 5.3 Design Principles

1. **Transparency First**: Always show what's happening (tokens, costs, traces)
2. **Developer-Focused**: Code snippets, API examples everywhere
3. **Minimal Chrome**: Clean, focused interfaces
4. **Joy-Inducing**: Subtle personality in copy, interactions
5. **Dark Mode Default**: Because developers

---

## 6. Technical Dependencies

### 6.1 Infrastructure (from architecture-platform.md)

| Component | Purpose | Status |
|-----------|---------|--------|
| PostgreSQL 15+ | Primary database with RLS | Required |
| Redis | Caching, rate limiting | Required |
| NATS | Event streaming | Required |
| Kong | API Gateway | Required |
| Kubernetes | Container orchestration | Required |

### 6.2 External Services

| Service | Purpose | Fallback |
|---------|---------|----------|
| Claude API | Primary LLM | OpenAI GPT-4o |
| OpenRouter | LLM routing | Direct provider |
| Auth0 | Authentication | Clerk |
| Stripe | Payments | None |

### 6.3 Internal Dependencies

| Dependency | Owner | Status |
|------------|-------|--------|
| AGENTESE impl | `impl/claude/protocols/agentese/` | 559 tests passing |
| K-gent impl | `impl/claude/agents/k/` | In development |
| Logos service | `impl/claude/protocols/agentese/logos.py` | Exists |

---

## 7. Prioritized Backlog

### Sprint 1 (Weeks 1-2): Foundation
| ID | Story | Points | Priority |
|----|-------|--------|----------|
| MVP-001 | Deploy PostgreSQL with RLS | 5 | P0 |
| MVP-002 | API Gateway (Kong) setup | 3 | P0 |
| MVP-003 | Auth service (API keys) | 5 | P0 |
| MVP-004 | Basic tenant isolation | 5 | P0 |
| MVP-005 | Usage event emission | 3 | P0 |

### Sprint 2 (Weeks 3-4): AGENTESE Core
| ID | Story | Points | Priority |
|----|-------|--------|----------|
| MVP-006 | Logos invoker API | 8 | P0 |
| MVP-007 | world.* context handler | 8 | P0 |
| MVP-008 | self.* context handler | 8 | P0 |
| MVP-009 | Basic tool execution | 5 | P0 |
| MVP-010 | AGENTESE API tests | 3 | P0 |

### Sprint 3 (Weeks 5-6): K-Gent
| ID | Story | Points | Priority |
|----|-------|--------|----------|
| MVP-011 | Session management | 5 | P0 |
| MVP-012 | Dialogue API | 5 | P0 |
| MVP-013 | Kent persona config | 3 | P0 |
| MVP-014 | Session persistence | 5 | P0 |
| MVP-015 | Streaming responses | 5 | P0 |

### Sprint 4 (Weeks 7-8): Observability
| ID | Story | Points | Priority |
|----|-------|--------|----------|
| MVP-016 | Trace collection | 5 | P0 |
| MVP-017 | Trace viewer UI | 8 | P0 |
| MVP-018 | Token usage dashboard | 5 | P0 |
| MVP-019 | Cost tracking | 5 | P0 |
| MVP-020 | Usage alerts | 3 | P0 |

### Sprint 5 (Weeks 9-10): Polish & Launch
| ID | Story | Points | Priority |
|----|-------|--------|----------|
| MVP-021 | Playground UI | 8 | P0 |
| MVP-022 | API key management UI | 5 | P0 |
| MVP-023 | Documentation | 8 | P0 |
| MVP-024 | Landing page | 5 | P0 |
| MVP-025 | Beta signup flow | 3 | P0 |

---

## 8. Success Metrics

### 8.1 Launch Criteria

- [ ] All P0 user stories complete
- [ ] 95% test coverage on core paths
- [ ] < 500ms p99 latency on AGENTESE invoke
- [ ] < 1% error rate
- [ ] Documentation complete
- [ ] Security audit passed

### 8.2 MVP Success Metrics (30 days post-launch)

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Developer signups** | 500 | Auth0 registrations |
| **Active users (WAU)** | 100 | Users with ≥1 API call |
| **API calls** | 50,000 | OpenMeter aggregation |
| **NPS** | > 40 | In-app survey |
| **Paid conversions** | 10 | Stripe subscriptions |

### 8.3 Qualitative Goals

- Developers can go from signup to first API call in < 5 minutes
- "I can actually see what my agent is doing"
- "Finally, a framework that doesn't fight me"
- Community engagement (GitHub stars, Discord members)

---

## 9. Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| LLM API rate limits | Medium | High | Multi-provider fallback |
| Scope creep | High | Medium | Strict MoSCoW adherence |
| Performance issues | Medium | High | Load testing in Sprint 4 |
| Security vulnerability | Low | Critical | Security audit, pen testing |
| Low adoption | Medium | High | Early user feedback, iterate |

---

## 10. Out of Scope (Explicit)

The following are **explicitly not in MVP**:

1. **Multi-agent orchestration** - Future roadmap
2. **Custom model fine-tuning** - Enterprise feature
3. **Enterprise SSO** - Post-MVP
4. **On-premise deployment** - Enterprise feature
5. **Mobile apps** - API-first approach
6. **Marketplace** - v1.1+
7. **Team collaboration** - Post-MVP
8. **Advanced void./time./concept. contexts** - MVP+1

---

## References

- [research-competitive.md](./research-competitive.md) - Competitive gaps
- [research-community.md](./research-community.md) - Developer needs
- [architecture-platform.md](./architecture-platform.md) - Platform architecture
- [architecture-billing.md](./architecture-billing.md) - Billing architecture
- [spec/protocols/agentese.md](../../spec/protocols/agentese.md) - AGENTESE spec

---

**Document Status**: Scope Complete
**Next Phase**: BUILD
**Owner**: Product Team
