# AGENTESE Universal Protocol: User Journeys

> *"There is no view from nowhere. Every observation is an interaction."*

This document describes how humans and agents interact through the AGENTESE Universal Protocol (AUP) at different scales: small (single user/agent), medium (teams/multi-agent), and large (distributed/federated systems).

---

## Table of Contents

1. [Core Concepts](#core-concepts)
2. [Human-Agent Journeys](#human-agent-journeys)
   - [Small: Solo Developer](#small-solo-developer)
   - [Medium: Team Workflow](#medium-team-workflow)
   - [Large: Enterprise Platform](#large-enterprise-platform)
3. [Agent-Agent Journeys](#agent-agent-journeys)
   - [Small: Two-Agent Composition](#small-two-agent-composition)
   - [Medium: Agent Town Simulation](#medium-agent-town-simulation)
   - [Large: Federated Agent Network](#large-federated-agent-network)
4. [Mixed Journeys](#mixed-journeys)
5. [Error Handling Patterns](#error-handling-patterns)
6. [Best Practices](#best-practices)

---

## Core Concepts

### The Observer Principle

Every AUP request requires an **observer context**. Different observers receive different perceptions of the same entity:

```
┌─────────────────────────────────────────────────────────┐
│                    world.house                          │
├─────────────────────────────────────────────────────────┤
│  Architect Observer  →  Blueprint, load calculations    │
│  Poet Observer       →  Metaphor, dwelling essence      │
│  Economist Observer  →  Appraisal, market value         │
│  Child Observer      →  "The place with the red door"   │
└─────────────────────────────────────────────────────────┘
```

Observer context is provided via HTTP headers:
```http
X-Observer-Archetype: architect
X-Observer-Id: user-123
X-Observer-Capabilities: define,spawn
```

### The Five Contexts

| Context | Domain | Example Paths |
|---------|--------|---------------|
| `world.*` | External reality | `world.codebase`, `world.document` |
| `self.*` | Internal state | `self.soul`, `self.memory` |
| `concept.*` | Abstract ideas | `concept.justice`, `concept.recursion` |
| `void.*` | Entropy/creativity | `void.slop`, `void.dream` |
| `time.*` | Temporal | `time.trace`, `time.forecast` |

### Affordances

What you can do depends on who you are:

| Affordance | Category | Who Can Use |
|------------|----------|-------------|
| `manifest` | Perception | Everyone |
| `witness` | Perception | Everyone |
| `affordances` | Perception | Everyone |
| `refine` | Generation | Philosophers, Architects |
| `define` | Generation | Architects, Developers |
| `spawn` | Generation | Architects, Admins |
| `sip` | Entropy | Artists, Explorers |
| `tithe` | Entropy | Anyone with capital |

---

## Human-Agent Journeys

### Small: Solo Developer

**Scenario**: A developer exploring their codebase through AGENTESE.

#### Journey 1: Understanding Code Structure

```
Developer                           AUP                              Logos
    │                                │                                  │
    │  GET /api/v1/world/codebase/manifest                             │
    │  X-Observer-Archetype: developer                                 │
    │ ─────────────────────────────► │                                  │
    │                                │  resolve("world.codebase")       │
    │                                │ ────────────────────────────────►│
    │                                │                                  │
    │                                │  ◄──── CodebaseNode              │
    │                                │                                  │
    │                                │  invoke("manifest", dev_umwelt)  │
    │                                │ ────────────────────────────────►│
    │                                │                                  │
    │  ◄─────────────────────────────│  ◄──── {modules, dependencies,   │
    │  200 OK                        │         entry_points, tests}     │
    │  {                             │                                  │
    │    "handle": "world.codebase.manifest",                          │
    │    "result": {                 │                                  │
    │      "modules": [...],         │                                  │
    │      "test_coverage": 0.87     │                                  │
    │    },                          │                                  │
    │    "meta": {                   │                                  │
    │      "observer": "developer",  │                                  │
    │      "span_id": "abc123"       │                                  │
    │    }                           │                                  │
    │  }                             │                                  │
```

#### Journey 2: Asking K-gent a Question (Streaming)

```
Developer                           AUP                              K-gent
    │                                │                                  │
    │  GET /api/v1/self/soul/challenge/stream?challenge=How+should+I+  │
    │      structure+this+module%3F                                    │
    │  Accept: text/event-stream                                       │
    │ ─────────────────────────────► │                                  │
    │                                │  stream_soul_challenge(...)      │
    │                                │ ────────────────────────────────►│
    │                                │                                  │
    │  event: chunk                  │  ◄──── "Consider the"            │
    │  data: {"type":"response",     │                                  │
    │         "content":"Consider",  │                                  │
    │         "partial":true}        │                                  │
    │ ◄──────────────────────────────│                                  │
    │                                │                                  │
    │  event: chunk                  │  ◄──── "single responsibility"   │
    │  data: {"type":"response",     │                                  │
    │         "content":"single",    │                                  │
    │         "partial":true}        │                                  │
    │ ◄──────────────────────────────│                                  │
    │                                │                                  │
    │  ...more chunks...             │                                  │
    │                                │                                  │
    │  event: done                   │                                  │
    │  data: {"span_id":"def456",    │                                  │
    │         "chunks_count":47}     │                                  │
    │ ◄──────────────────────────────│                                  │
```

#### Journey 3: Composing a Pipeline

```
Developer                           AUP                              Logos
    │                                │                                  │
    │  POST /api/v1/compose                                            │
    │  {                             │                                  │
    │    "paths": [                  │                                  │
    │      "world.document.manifest",│                                  │
    │      "concept.summary.refine", │                                  │
    │      "self.memory.engram"      │                                  │
    │    ]                           │                                  │
    │  }                             │                                  │
    │ ─────────────────────────────► │                                  │
    │                                │                                  │
    │                                │  Step 1: manifest document       │
    │                                │ ────────────────────────────────►│
    │                                │  ◄──── document_content          │
    │                                │                                  │
    │                                │  Step 2: refine into summary     │
    │                                │  (input: document_content)       │
    │                                │ ────────────────────────────────►│
    │                                │  ◄──── summary                   │
    │                                │                                  │
    │                                │  Step 3: store as engram         │
    │                                │  (input: summary)                │
    │                                │ ────────────────────────────────►│
    │                                │  ◄──── engram_id                 │
    │                                │                                  │
    │  ◄─────────────────────────────│                                  │
    │  200 OK                        │                                  │
    │  {                             │                                  │
    │    "result": "engram-789",     │                                  │
    │    "pipeline_trace": [         │                                  │
    │      {"path": "world.document.manifest", "duration_ms": 45},     │
    │      {"path": "concept.summary.refine", "duration_ms": 230},     │
    │      {"path": "self.memory.engram", "duration_ms": 12}           │
    │    ],                          │                                  │
    │    "laws_verified": ["identity", "associativity"]                │
    │  }                             │                                  │
```

---

### Medium: Team Workflow

**Scenario**: A team of 5 developers using shared agents for code review and documentation.

```
┌─────────────────────────────────────────────────────────────────────┐
│                        Team Workspace                                │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│   ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐  │
│   │  Alice  │  │   Bob   │  │  Carol  │  │  David  │  │   Eve   │  │
│   │ (Lead)  │  │ (Senior)│  │ (Junior)│  │  (QA)   │  │ (Docs)  │  │
│   └────┬────┘  └────┬────┘  └────┬────┘  └────┬────┘  └────┬────┘  │
│        │            │            │            │            │        │
│        └────────────┴────────────┴────────────┴────────────┘        │
│                              │                                       │
│                              ▼                                       │
│                    ┌─────────────────┐                              │
│                    │   AUP Gateway   │                              │
│                    │  (Load Balanced)│                              │
│                    └────────┬────────┘                              │
│                              │                                       │
│        ┌─────────────────────┼─────────────────────┐                │
│        │                     │                     │                │
│        ▼                     ▼                     ▼                │
│   ┌─────────┐          ┌─────────┐          ┌─────────┐            │
│   │ K-gent  │          │ Review  │          │  Docs   │            │
│   │ (Soul)  │          │  Agent  │          │  Agent  │            │
│   └─────────┘          └─────────┘          └─────────┘            │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

#### Journey 4: Code Review Flow

```
Carol (Junior)                      AUP                          Review Agent
    │                                │                                  │
    │  POST /api/v1/world/pr-123/manifest                              │
    │  X-Observer-Archetype: developer                                 │
    │  X-Observer-Capabilities: request-review                         │
    │ ─────────────────────────────► │                                  │
    │                                │                                  │
    │  ◄─────────────────────────────│                                  │
    │  {                             │                                  │
    │    "result": {                 │                                  │
    │      "diff": "...",            │                                  │
    │      "files_changed": 5,       │                                  │
    │      "suggested_reviewers": ["bob", "alice"]                     │
    │    }                           │                                  │
    │  }                             │                                  │
    │                                │                                  │
    │  POST /api/v1/concept/code-quality/refine                        │
    │  {"kwargs": {"pr_id": "pr-123", "depth": "thorough"}}            │
    │ ─────────────────────────────► │                                  │
    │                                │  invoke refine with PR context   │
    │                                │ ────────────────────────────────►│
    │                                │                                  │
    │                                │  ◄──── Review analysis           │
    │  ◄─────────────────────────────│                                  │
    │  {                             │                                  │
    │    "result": {                 │                                  │
    │      "issues": [               │                                  │
    │        {"severity": "warning", "line": 42, "message": "..."},   │
    │        {"severity": "info", "line": 78, "suggestion": "..."}    │
    │      ],                        │                                  │
    │      "overall_quality": 0.82,  │                                  │
    │      "ready_for_review": true  │                                  │
    │    }                           │                                  │
    │  }                             │                                  │
```

#### Journey 5: Documentation Generation with Different Observers

```
                              Same Entity, Different Views

Eve (Docs)                          AUP                              Docs Agent
    │                                │                                  │
    │  GET /api/v1/world/auth-module/manifest                          │
    │  X-Observer-Archetype: technical-writer                          │
    │ ─────────────────────────────► │                                  │
    │                                │                                  │
    │  ◄─────────────────────────────│                                  │
    │  {                             │                                  │
    │    "result": {                 │                                  │
    │      "summary": "User authentication and session management",    │
    │      "public_api": [...],      │     ◄── Writer gets docs view   │
    │      "examples": [...],        │                                  │
    │      "common_pitfalls": [...]  │                                  │
    │    }                           │                                  │
    │  }                             │                                  │


Alice (Lead)                        AUP                              Docs Agent
    │                                │                                  │
    │  GET /api/v1/world/auth-module/manifest                          │
    │  X-Observer-Archetype: architect                                 │
    │ ─────────────────────────────► │                                  │
    │                                │                                  │
    │  ◄─────────────────────────────│                                  │
    │  {                             │                                  │
    │    "result": {                 │                                  │
    │      "architecture": {...},    │     ◄── Architect gets          │
    │      "dependencies": [...],    │        technical deep-dive      │
    │      "security_model": {...},  │                                  │
    │      "scalability_notes": ".." │                                  │
    │    }                           │                                  │
    │  }                             │                                  │
```

---

### Large: Enterprise Platform

**Scenario**: A company with 500+ developers across multiple teams, using AUP as the standard agent interface.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         Enterprise AUP Platform                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │
│  │   Team A     │  │   Team B     │  │   Team C     │  │   Team D     │    │
│  │  (Frontend)  │  │  (Backend)   │  │   (ML/AI)    │  │  (Platform)  │    │
│  │   50 devs    │  │   80 devs    │  │   30 devs    │  │   40 devs    │    │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘    │
│         │                 │                 │                 │             │
│         └─────────────────┴─────────────────┴─────────────────┘             │
│                                    │                                         │
│                                    ▼                                         │
│                    ┌───────────────────────────────┐                        │
│                    │        API Gateway            │                        │
│                    │   (Rate Limiting, Auth, RBAC) │                        │
│                    └───────────────┬───────────────┘                        │
│                                    │                                         │
│         ┌──────────────────────────┼──────────────────────────┐             │
│         │                          │                          │             │
│         ▼                          ▼                          ▼             │
│  ┌─────────────┐           ┌─────────────┐           ┌─────────────┐       │
│  │  AUP Pod 1  │           │  AUP Pod 2  │           │  AUP Pod 3  │       │
│  │  (us-east)  │           │  (eu-west)  │           │ (ap-south)  │       │
│  └──────┬──────┘           └──────┬──────┘           └──────┬──────┘       │
│         │                          │                          │             │
│         └──────────────────────────┴──────────────────────────┘             │
│                                    │                                         │
│                    ┌───────────────┴───────────────┐                        │
│                    │       Shared Agent Pool       │                        │
│                    ├───────────────────────────────┤                        │
│                    │  K-gent  │ Review │ Security  │                        │
│                    │  Docs    │ Deploy │ Analytics │                        │
│                    └───────────────────────────────┘                        │
│                                                                              │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │                        Observability Layer                            │  │
│  │  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐    │  │
│  │  │ Traces  │  │ Metrics │  │  Logs   │  │ Alerts  │  │Dashboard│    │  │
│  │  │ (Tempo) │  │(Prom)   │  │ (Loki)  │  │(PagerD) │  │(Grafana)│    │  │
│  │  └─────────┘  └─────────┘  └─────────┘  └─────────┘  └─────────┘    │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

#### Journey 6: Cross-Team Knowledge Discovery

```
Developer (Team A)                  AUP                     Knowledge Graph
    │                                │                              │
    │  POST /api/v1/compose                                        │
    │  {                             │                              │
    │    "paths": [                  │                              │
    │      "concept.authentication.manifest",                      │
    │      "world.team-b-codebase.manifest",                       │
    │      "concept.integration-patterns.refine"                   │
    │    ],                          │                              │
    │    "observer": {               │                              │
    │      "archetype": "developer", │                              │
    │      "capabilities": ["cross-team-read"]                     │
    │    }                           │                              │
    │  }                             │                              │
    │ ─────────────────────────────► │                              │
    │                                │                              │
    │                                │  Check cross-team permission │
    │                                │ ─────────────────────────────►
    │                                │  ◄───── Approved (RBAC)      │
    │                                │                              │
    │                                │  Execute 3-step pipeline     │
    │                                │ ─────────────────────────────►
    │                                │                              │
    │  ◄─────────────────────────────│                              │
    │  {                             │                              │
    │    "result": {                 │                              │
    │      "recommended_approach": "Use Team B's OAuth service",   │
    │      "integration_guide": {...},                             │
    │      "contact": "bob@team-b"   │                              │
    │    },                          │                              │
    │    "pipeline_trace": [         │                              │
    │      {"path": "...", "duration_ms": 23, "cache_hit": true},  │
    │      {"path": "...", "duration_ms": 156},                    │
    │      {"path": "...", "duration_ms": 89}                      │
    │    ]                           │                              │
    │  }                             │                              │
```

#### Journey 7: Enterprise Audit Trail

```
Security Team                       AUP                         Audit System
    │                                │                                │
    │  GET /api/v1/time/audit/manifest                               │
    │  X-Observer-Archetype: security-auditor                        │
    │  {"kwargs": {"time_range": "7d", "actor": "carol@team-a"}}     │
    │ ─────────────────────────────► │                                │
    │                                │                                │
    │                                │  Query audit traces            │
    │                                │ ───────────────────────────────►
    │                                │                                │
    │  ◄─────────────────────────────│                                │
    │  {                             │                                │
    │    "result": {                 │                                │
    │      "total_invocations": 1247,│                                │
    │      "by_context": {           │                                │
    │        "world": 892,           │                                │
    │        "self": 201,            │                                │
    │        "concept": 154          │                                │
    │      },                        │                                │
    │      "sensitive_accesses": [   │                                │
    │        {"path": "world.secrets.manifest", "time": "...",       │
    │         "authorized": true}    │                                │
    │      ],                        │                                │
    │      "anomalies": []           │                                │
    │    }                           │                                │
    │  }                             │                                │
```

---

## Agent-Agent Journeys

### Small: Two-Agent Composition

**Scenario**: A summarization agent and a translation agent working together.

```
┌─────────────────────────────────────────────────────────────────────┐
│                    Agent Composition Pipeline                        │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│   Input: Long English document                                       │
│      │                                                               │
│      ▼                                                               │
│   ┌─────────────────┐                                               │
│   │ Summarizer Agent│  world.document.manifest                      │
│   │                 │  → concept.summary.refine                     │
│   └────────┬────────┘                                               │
│            │                                                         │
│            │  (Summary in English)                                   │
│            ▼                                                         │
│   ┌─────────────────┐                                               │
│   │ Translator Agent│  concept.summary.manifest                     │
│   │                 │  → concept.translation.refine                 │
│   └────────┬────────┘                                               │
│            │                                                         │
│            ▼                                                         │
│   Output: Concise summary in target language                         │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

#### Journey 8: Agent Invoking Another Agent

```
Summarizer Agent                    AUP                      Translator Agent
    │                                │                                │
    │  (Has document summary)        │                                │
    │                                │                                │
    │  POST /api/v1/concept/translation/refine                       │
    │  X-Observer-Archetype: agent   │                                │
    │  X-Observer-Id: summarizer-agent-001                           │
    │  X-Observer-Capabilities: agent-invoke                         │
    │  {                             │                                │
    │    "kwargs": {                 │                                │
    │      "input": "The document discusses...",                     │
    │      "source_lang": "en",      │                                │
    │      "target_lang": "ja"       │                                │
    │    }                           │                                │
    │  }                             │                                │
    │ ─────────────────────────────► │                                │
    │                                │  Resolve translator agent      │
    │                                │ ───────────────────────────────►
    │                                │                                │
    │                                │  invoke("refine", agent_umwelt)│
    │                                │ ───────────────────────────────►
    │                                │                                │
    │                                │  ◄──── Japanese translation    │
    │  ◄─────────────────────────────│                                │
    │  {                             │                                │
    │    "result": {                 │                                │
    │      "translation": "文書は...",│                                │
    │      "confidence": 0.94,       │                                │
    │      "alternatives": [...]     │                                │
    │    },                          │                                │
    │    "meta": {                   │                                │
    │      "observer": "agent",      │                                │
    │      "agent_chain": ["summarizer-001", "translator-002"]       │
    │    }                           │                                │
    │  }                             │                                │
```

---

### Medium: Agent Town Simulation

**Scenario**: Multiple agents interacting in a simulated environment, forming coalitions and evolving strategies.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           Agent Town: "Innovation Hub"                       │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   ┌─────────┐      Coalition A        ┌─────────┐                           │
│   │ Builder │◄─────────────────────────│ Thinker │                           │
│   │  Agent  │        (FORM)           │  Agent  │                           │
│   └────┬────┘                          └────┬────┘                           │
│        │                                    │                                │
│        │         ┌──────────────┐          │                                │
│        └────────►│   Shared     │◄─────────┘                                │
│                  │   Memory     │                                            │
│                  └──────┬───────┘                                            │
│                         │                                                    │
│                         │ (Pheromone Trails)                                │
│                         ▼                                                    │
│   ┌─────────┐      ┌──────────────┐      ┌─────────┐                        │
│   │ Critic  │      │   Garden     │      │ Explorer│                        │
│   │  Agent  │◄────►│   State      │◄────►│  Agent  │                        │
│   └─────────┘      └──────────────┘      └─────────┘                        │
│                                                                              │
│   Evolution: Generation 47 │ Fitness: 0.73 │ Active Coalitions: 3           │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

#### Journey 9: Coalition Formation

```
Thinker Agent                       AUP                       Town Orchestrator
    │                                │                                │
    │  POST /api/v1/self/town/coalition                              │
    │  X-Observer-Archetype: agent   │                                │
    │  X-Observer-Id: thinker-agent-042                              │
    │  {                             │                                │
    │    "kwargs": {                 │                                │
    │      "action": "propose",      │                                │
    │      "target_agent": "builder-agent-017",                      │
    │      "task": "design-new-protocol",                            │
    │      "commitment_tokens": 50   │                                │
    │    }                           │                                │
    │  }                             │                                │
    │ ─────────────────────────────► │                                │
    │                                │                                │
    │                                │  Route to town orchestrator    │
    │                                │ ───────────────────────────────►
    │                                │                                │
    │                                │  Validate & create proposal    │
    │                                │                                │
    │  ◄─────────────────────────────│                                │
    │  {                             │                                │
    │    "result": {                 │                                │
    │      "proposal_id": "coal-789",│                                │
    │      "status": "pending",      │                                │
    │      "expires_at": "...",      │                                │
    │      "acceptance_threshold": 0.6                               │
    │    }                           │                                │
    │  }                             │                                │


Builder Agent                       AUP                       Town Orchestrator
    │                                │                                │
    │  POST /api/v1/self/town/coalition                              │
    │  X-Observer-Id: builder-agent-017                              │
    │  {                             │                                │
    │    "kwargs": {                 │                                │
    │      "action": "accept",       │                                │
    │      "proposal_id": "coal-789",│                                │
    │      "commitment_tokens": 30   │                                │
    │    }                           │                                │
    │  }                             │                                │
    │ ─────────────────────────────► │                                │
    │                                │                                │
    │  ◄─────────────────────────────│                                │
    │  {                             │                                │
    │    "result": {                 │                                │
    │      "coalition_id": "active-coal-123",                        │
    │      "members": ["thinker-042", "builder-017"],                │
    │      "shared_capital": 80,     │                                │
    │      "task": "design-new-protocol"                             │
    │    }                           │                                │
    │  }                             │                                │
```

#### Journey 10: Real-Time Town Visualization (SSE)

```
Visualization Client                AUP                         Town State
    │                                │                                │
    │  GET /api/v1/self/town/events/stream                           │
    │  Accept: text/event-stream     │                                │
    │ ─────────────────────────────► │                                │
    │                                │                                │
    │  event: agent-move             │                                │
    │  data: {"agent": "explorer-003", "from": [0.2, 0.3],           │
    │         "to": [0.4, 0.5], "trail_strength": 0.7}               │
    │ ◄──────────────────────────────│                                │
    │                                │                                │
    │  event: coalition-formed       │                                │
    │  data: {"coalition": "active-coal-123",                        │
    │         "members": ["thinker-042", "builder-017"]}             │
    │ ◄──────────────────────────────│                                │
    │                                │                                │
    │  event: pheromone-update       │                                │
    │  data: {"location": [0.4, 0.5], "type": "success",             │
    │         "intensity": 0.8, "decay_rate": 0.1}                   │
    │ ◄──────────────────────────────│                                │
    │                                │                                │
    │  event: generation-complete    │                                │
    │  data: {"generation": 48, "avg_fitness": 0.76,                 │
    │         "top_performer": "builder-017"}                        │
    │ ◄──────────────────────────────│                                │
    │                                │                                │
    │  ... continuous stream ...     │                                │
```

---

### Large: Federated Agent Network

**Scenario**: Multiple organizations running their own AUP instances, with agents that can communicate across boundaries.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       Federated AGENTESE Network                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─────────────────────────┐         ┌─────────────────────────┐            │
│  │     Organization A      │         │     Organization B      │            │
│  │  ┌─────────────────┐   │         │  ┌─────────────────┐   │            │
│  │  │   AUP Instance  │   │         │  │   AUP Instance  │   │            │
│  │  └────────┬────────┘   │         │  └────────┬────────┘   │            │
│  │           │            │         │           │            │            │
│  │  ┌────────┴────────┐   │         │  ┌────────┴────────┐   │            │
│  │  │ Agent Pool A    │   │         │  │ Agent Pool B    │   │            │
│  │  │ ┌───┐ ┌───┐ ┌───┐│  │         │  │ ┌───┐ ┌───┐ ┌───┐│  │            │
│  │  │ │A1 │ │A2 │ │A3 ││  │         │  │ │B1 │ │B2 │ │B3 ││  │            │
│  │  │ └───┘ └───┘ └───┘│  │         │  │ └───┘ └───┘ └───┘│  │            │
│  │  └─────────────────-┘   │         │  └─────────────────-┘   │            │
│  └────────────┬────────────┘         └────────────┬────────────┘            │
│               │                                   │                          │
│               │      ┌───────────────────┐       │                          │
│               └─────►│  Federation Hub   │◄──────┘                          │
│                      │  (Trust Registry) │                                  │
│                      └─────────┬─────────┘                                  │
│                                │                                             │
│                      ┌─────────┴─────────┐                                  │
│                      │  Cross-Org Agents │                                  │
│                      │  (Federated Pool) │                                  │
│                      └───────────────────┘                                  │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

#### Journey 11: Cross-Organization Agent Collaboration

```
Agent A1 (Org A)                    Federation Hub              Agent B2 (Org B)
    │                                     │                           │
    │  POST /api/v1/federated/invoke      │                           │
    │  X-Observer-Id: agent-a1@org-a      │                           │
    │  X-Federation-Token: <jwt>          │                           │
    │  {                                  │                           │
    │    "target": "org-b:agent-b2",      │                           │
    │    "path": "concept.market-analysis.refine",                    │
    │    "kwargs": {                      │                           │
    │      "sector": "renewable-energy",  │                           │
    │      "time_horizon": "5y"           │                           │
    │    }                                │                           │
    │  }                                  │                           │
    │ ──────────────────────────────────► │                           │
    │                                     │                           │
    │                                     │  Validate federation trust│
    │                                     │  Check cross-org permissions
    │                                     │                           │
    │                                     │  Forward to Org B         │
    │                                     │ ──────────────────────────►
    │                                     │                           │
    │                                     │  Agent B2 processes       │
    │                                     │                           │
    │                                     │  ◄─────────────────────────
    │                                     │  Response with analysis   │
    │                                     │                           │
    │  ◄──────────────────────────────────│                           │
    │  {                                  │                           │
    │    "result": {                      │                           │
    │      "analysis": {...},             │                           │
    │      "confidence": 0.87,            │                           │
    │      "data_sources": ["org-b-internal", "public-markets"]      │
    │    },                               │                           │
    │    "meta": {                        │                           │
    │      "federation_hop": 1,           │                           │
    │      "source_org": "org-b",         │                           │
    │      "trust_level": "verified"      │                           │
    │    }                                │                           │
    │  }                                  │                           │
```

---

## Mixed Journeys

### Journey 12: Human-Orchestrated Multi-Agent Task

**Scenario**: A human product manager coordinating multiple agents to prepare a feature release.

```
Product Manager                     AUP                     Agent Orchestration
    │                                │                              │
    │  POST /api/v1/compose          │                              │
    │  {                             │                              │
    │    "paths": [                  │                              │
    │      "world.feature-x.manifest",          ◄── Get feature spec│
    │      "concept.test-plan.refine",          ◄── Generate tests  │
    │      "world.codebase.analyze",            ◄── Check impl      │
    │      "concept.documentation.refine",      ◄── Write docs      │
    │      "concept.release-notes.refine"       ◄── Prep release    │
    │    ],                          │                              │
    │    "observer": {               │                              │
    │      "archetype": "product-manager",                         │
    │      "capabilities": ["orchestrate", "release"]              │
    │    }                           │                              │
    │  }                             │                              │
    │ ─────────────────────────────► │                              │
    │                                │                              │
    │                                │  Execute 5-agent pipeline    │
    │                                │ ─────────────────────────────►
    │                                │                              │
    │                                │  [Feature Agent] → Spec      │
    │                                │  [Test Agent] → Test Plan    │
    │                                │  [Code Agent] → Analysis     │
    │                                │  [Docs Agent] → Documentation│
    │                                │  [Release Agent] → Notes     │
    │                                │                              │
    │  ◄─────────────────────────────│                              │
    │  {                             │                              │
    │    "result": {                 │                              │
    │      "release_package": {      │                              │
    │        "version": "2.3.0",     │                              │
    │        "test_coverage": 0.94,  │                              │
    │        "docs_complete": true,  │                              │
    │        "release_notes": "..."  │                              │
    │      }                         │                              │
    │    },                          │                              │
    │    "pipeline_trace": [         │                              │
    │      {"path": "...", "agent": "feature-agent", "ms": 45},    │
    │      {"path": "...", "agent": "test-agent", "ms": 1230},     │
    │      {"path": "...", "agent": "code-agent", "ms": 890},      │
    │      {"path": "...", "agent": "docs-agent", "ms": 2100},     │
    │      {"path": "...", "agent": "release-agent", "ms": 340}    │
    │    ]                           │                              │
    │  }                             │                              │
```

### Journey 13: Agent Requesting Human Input (Dialectic)

**Scenario**: An agent encounters an ethical dilemma and requests human judgment.

```
Ethics Agent                        AUP                         Human Reviewer
    │                                │                                │
    │  (Analyzing content moderation case)                           │
    │  (Encounters edge case requiring human judgment)               │
    │                                │                                │
    │  POST /api/v1/concept/moderation-decision/dialectic/stream     │
    │  X-Observer-Archetype: agent   │                                │
    │  {                             │                                │
    │    "kwargs": {                 │                                │
    │      "case_id": "mod-456",     │                                │
    │      "request_human": true,    │                                │
    │      "thesis": "Content should be removed (policy X)",         │
    │      "antithesis": "Content is protected speech (policy Y)"    │
    │    }                           │                                │
    │  }                             │                                │
    │ ─────────────────────────────► │                                │
    │                                │                                │
    │  event: thesis                 │                                │
    │  data: {"phase": "thesis", "content": "Based on policy X..."}  │
    │ ◄──────────────────────────────│                                │
    │                                │                                │
    │  event: antithesis             │                                │
    │  data: {"phase": "antithesis", "content": "However, policy Y.."│
    │ ◄──────────────────────────────│                                │
    │                                │                                │
    │  event: human-required         │                                │
    │  data: {"case_id": "mod-456", "options": [...],                │
    │         "deadline": "2h"}      │                                │
    │ ◄──────────────────────────────│                                │
    │                                │                                │
    │  ... waits for human input ... │                                │
    │                                │                                │
    │                                │  Human provides judgment       │
    │                                │ ◄─────────────────────────────
    │                                │                                │
    │  event: synthesis              │                                │
    │  data: {"phase": "synthesis",  │                                │
    │         "decision": "approve-with-warning",                    │
    │         "human_input": "Context matters here...",              │
    │         "confidence": 0.95}    │                                │
    │ ◄──────────────────────────────│                                │
    │                                │                                │
    │  event: done                   │                                │
    │ ◄──────────────────────────────│                                │
```

---

## Error Handling Patterns

### Sympathetic Errors

AUP errors always include:
- **What** went wrong
- **Why** it happened
- **What to do** about it
- **Alternatives** available

```json
{
  "detail": {
    "error": "Affordance 'spawn' not available to observer 'viewer'",
    "code": "AFFORDANCE_DENIED",
    "path": "world.agent.spawn",
    "why": "The 'spawn' affordance requires architect or admin privileges",
    "suggestion": "Request elevated permissions or use 'manifest' instead",
    "available": ["manifest", "witness", "affordances"],
    "span_id": "trace-abc123"
  }
}
```

### Common Error Scenarios

| Code | HTTP | When | Recovery |
|------|------|------|----------|
| `PATH_NOT_FOUND` | 404 | Entity doesn't exist | Check spelling, list available |
| `AFFORDANCE_DENIED` | 403 | Observer lacks permission | Request elevation, use alternative |
| `OBSERVER_REQUIRED` | 401 | No observer context | Add X-Observer-* headers |
| `SYNTAX_ERROR` | 400 | Malformed path | Fix path format |
| `LAW_VIOLATION` | 422 | Category law broken | Check composition order |
| `BUDGET_EXHAUSTED` | 429 | Rate/token limit hit | Wait or upgrade tier |

---

## Best Practices

### For Humans

1. **Always specify observer context** - Be explicit about who you are
2. **Use composition for multi-step tasks** - Let the system optimize
3. **Stream for long operations** - Better UX with progress updates
4. **Check affordances first** - Know what you can do before trying

### For Agents

1. **Maintain agent identity** - Use consistent X-Observer-Id
2. **Request minimal capabilities** - Don't over-privilege
3. **Handle partial failures** - Composition may fail mid-pipeline
4. **Respect rate limits** - Back off on 429 errors

### For Large Systems

1. **Use federation tokens** - Secure cross-org communication
2. **Implement circuit breakers** - Prevent cascade failures
3. **Monitor span_ids** - Trace requests through the system
4. **Cache aggressively** - Manifest results are often stable

---

## Quick Reference

### Essential Headers

```http
X-API-Key: kg_your_api_key
X-Observer-Archetype: developer|architect|viewer|admin|agent
X-Observer-Id: unique-identifier
X-Observer-Capabilities: define,spawn,dialectic
```

### Essential Endpoints

```
GET  /api/v1/{context}/{holon}/manifest      # See an entity
GET  /api/v1/{context}/{holon}/affordances   # What can I do?
POST /api/v1/{context}/{holon}/{aspect}      # Do something
POST /api/v1/compose                          # Chain operations
GET  /api/v1/{context}/{holon}/{aspect}/stream # Real-time response
```

### Context Quick Guide

```
world.*    → External things (code, docs, tools)
self.*     → Internal state (memory, soul, config)
concept.*  → Abstract ideas (patterns, principles)
void.*     → Creativity (exploration, dreams)
time.*     → History (traces, forecasts)
```

---

*Last updated: 2025-12-14*
