---
path: plans/core-apps/gestalt-architecture-visualizer
status: research
progress: 0.05
last_touched: 2025-12-15
touched_by: gpt-5-codex
blocking: []
enables:
  - plans/reactive-substrate-unification
  - monetization/grand-initiative-monetization
session_notes: |
  Relocated to core-apps; format aligned with pillar plans.
  Fresh scan (Dec 2025): CodeSee Maps, CodeScene, Structurizr, ArchGuard validate demand for live diagrams; none deliver reactive, multi-target, policy-aware visualizations with holographic storage.
phase_ledger:
  PLAN: touched
  RESEARCH: touched
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
  planned: 0.10
  spent: 0.0
  returned: 0.0
---

# Gestalt: Living Architecture Visualizer

> *"Architecture diagrams rot the moment they're drawn. Gestalt never rots because it never stops watching."*

**Master Plan**: `plans/core-apps-synthesis.md` (addendum)  
**Existing Infrastructure**: `agents/m/` (HoloMaps), `agents/i/reactive/` (Signal/Computed), `protocols/agentese/` (Logos paths), `protocols/terrarium/` (metrics), `agents/town/` (k-clique coalitions)

---

## Overview

| Aspect | Detail |
|--------|--------|
| **Frame** | Living architecture operations & governance |
| **Core Mechanic** | File watcher → Cartographer → `Signal[ArchitectureGraph]` → projectors (CLI/Web/VR) |
| **Revenue** | Free (1 repo, CLI) / Pro $29 (5 repos) / Team $79 (20 repos) / Enterprise $199 seat (unlimited, SSO, VR) |
| **Status** | Engine unbuilt; substrate + cartography primitives ready |
| **AGENTESE Context** | `world.codebase.manifest`, `self.memory.cartography` |

---

## What This Plan Covers

### Absorbs These Ideas

| Idea | Source | Integration |
|------|--------|-------------|
| Living architecture visualizer | `brainstorming/developer-tools-on-kgents.md` | Core concept |
| Reactive substrate unification | `plans/reactive-substrate-unification.md` | Projection layer |
| HoloMap cartography | `agents/m/cartography.py` | Graph + holographic storage |
| Agent Town coalitions | `agents/town/coalitions.py` | Layer detection (k-clique) |
| Projection protocol | `protocols/terrarium/`, `agents/i/reactive/` | Multi-target rendering |

---

## Differentiators vs Market (Dec 2025)

| Competitor | They Do | Gestalt Advantage |
|------------|---------|-------------------|
| CodeSee Maps | Live maps for onboarding | Add governance + drift policies, multi-target (CLI/Web/VR), holographic storage |
| CodeScene | Temporal coupling, socio-technical metrics | Reactive projections, live drift enforcement, explainable scores |
| Structurizr | C4-as-code diagrams | Not reactive; Gestalt keeps diagrams live, policy-aware |
| ArchGuard | Architecture governance | Limited projections; no holographic memory or multi-surface |
| IDE diagrams | Local on-demand views | Collaboration + history; not IDE-bound |

---

## Quality Guardrails

- Explainable-by-default: every score links to factors + source lines.
- Policy-aware: allow/deny rules (layers/rings/C4) as code; suppressions auditable.
- Performance: cold scan <5s (1k files), incremental <2s; diff graph instead of full rebuild.
- Privacy: local-first; cloud requires explicit opt-in + path redaction + tenancy/RLS.
- Tests: golden repos + property tests for graph invariants; snapshot tests for projections; contract tests for AGENTESE paths.

---

## Architecture Signals (core types)

```python
@dataclass(frozen=True)
class ModuleHealth:
    name: str
    coupling: float       # 0-1, lower better
    cohesion: float       # 0-1, higher better
    drift: float          # 0-1, lower better
    complexity: float     # 0-1, lower better
    churn: float          # 0-1, lower better
    coverage: float       # 0-1, higher better
    instability: float | None = None  # Martin metric when git data available

    @property
    def overall_health(self) -> float:
        return (
            (1 - self.coupling) * 0.20 +
            self.cohesion * 0.15 +
            (1 - self.drift) * 0.25 +
            (1 - self.complexity) * 0.15 +
            (1 - self.churn) * 0.10 +
            self.coverage * 0.15
        )
```

**Data sources**: static imports (Python+TS), git history (churn/instability), coverage artifacts, declared architecture rules (ADR/C4/CUE).  
**Time decay**: drift penalties age out after green builds; churn smoothed via EWMA to reduce alert storms.

---

## Implementation Phases

### Phase 1 — Core Analysis Engine (Chunk 1)
**Goal**: Build static analysis + governance foundation (Python + TypeScript).
- Parse imports → dependency graph; k-clique layer detection (reuse Agent Town).
- Drift rules: allow/deny, layers/rings; suppression file with audit trail.
- Golden repos (clean-arch, layered monolith, monorepo) for regression.
- Exit: Python+TS parity; drift detection; 50+ tests (property + snapshots).

### Phase 2 — Reactive Substrate Integration (Chunk 2)
**Goal**: Architecture as `Signal[ArchitectureGraph]`.
- File watcher → incremental diff → Signal.set().
- Derived Computeds: overall health, drift count, module count, per-module signal.
- Exit: incremental updates <2s; 30+ tests (fswatch mocks, perf budget).

### Phase 3 — CLI Projection (Chunk 3)
**Goal**: Governance-grade CLI.
- Commands: `gestalt init|status|watch|show|tour|export`.
- Exports: C4-ish JSON, mermaid, dot; health sparklines.
- Exit: drift alerts with remediation suggestions; 40+ tests (snapshot + contracts).

### Phase 4 — Web Dashboard (Chunk 4)
**Goal**: Interactive graph + history.
- Node graph with drill-down; sparklines; alert triage; offline cache.
- SSE stream; initial load <2s on 50-module repo; smooth zoom/pan.
- Exit: 50+ tests (API + frontend); accessibility + perf budgets met.

### Phase 5 — AGENTESE Integration (Chunk 5)
**Goal**: Logos paths for architecture.
- Paths: `world.codebase.manifest`, `.module[name=x].manifest`, `.drift.witness`, `.layer[name=x].manifest`, `self.memory.cartography`.
- Observer-dependent affordances (security, performance, product lenses).
- Exit: 30+ tests; governance rules respected in resolver outputs.

### Phase 6 — VR Projection (Future)
**Goal**: 3D exploration (Three.js/Unity prototype).  
Exit TBD post Phase 5.

---

## User Journeys (condensed)

- **Day 1 Setup**: `gestalt init` → scan → detected layers, health grade, drift count → export mermaid for docs.
- **Daily Flow**: Save file → watcher diff → Signal update → CLI sparkline + web alert with actionable options (declare dep, refactor, suppress).
- **Architecture Review**: Web dashboard shows B-tree health, drift alerts, weekly sparklines; click node to export ADR suggestion.
- **Onboarding**: `gestalt tour` narrates layers/modules, highlights risky modules, links to docs/tests.
- **Future VR**: Districts by layer; buildings by module (height=complexity, color=health); bridges as dependencies.

---

## Dependencies

| System | Usage |
|--------|-------|
| `agents/m/` | Cartographer + HoloMap storage |
| `agents/i/reactive/` | Signal/Computed + projection adapters |
| `protocols/agentese/` | Path-based invocation |
| `protocols/terrarium/` | Metrics + projection protocol |
| `agents/town/` | k-clique coalition detection |
| `protocols/licensing` / `protocols/tenancy` | Feature gating, RLS, metering |

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Multi-language complexity | High | Start Python+TS; plug-in analyzers; shared graph IR |
| Drift false positives | Medium | Suppressions with expiry; explainability; EWMA smoothing |
| Large repo performance | High | Incremental diffing; cached graphs; sampling for churn |
| Visualization noise | Medium | Filters, focus/fog, layer rollups |
| Security/PII | High | Local-only default; redaction in exports; tenancy-aware API |

---

## Success Metrics

| Metric | Phase 1-2 | Phase 3-4 | Phase 5+ |
|--------|-----------|-----------|----------|
| Test count | 80+ | 170+ | 250+ |
| Languages | Python+TS | +JVM if demand | +.NET/Go |
| Update latency | <5s cold, <2s incr | <1s incr | <500ms incr |
| Drift false positives | <10% | <5% | <2% |
| Adoption | 3+ internal repos | 10+ design partners | GA |
| NRR | n/a | 105% | 120% |

---

## UX Research: Reference Flows

### Proven Patterns from Architecture Visualization Tools

#### 1. Structurizr's Architecture-as-Code
**Source**: [Software Architecture as Code with Structurizr](https://mydeveloperplanet.com/2024/03/20/software-architecture-as-code-with-structurizr/)

Structurizr's model-centric approach provides foundational patterns:

| Structurizr Pattern | Gestalt Application |
|--------------------|---------------------|
| **C4 model levels** (Context/Container/Component/Code) | `GestaltLevels` — Agent/Protocol/Node/Affordance |
| **Architecture as code** (version-controlled) | `AgenteseDSL` — declarative agent definitions |
| **Cross-view synchronization** | `LiveSync` — all views update from single source |
| **Interactive graph explorer** | `GestaltExplorer` — pan/zoom/filter |

**Key Insight**: "Structurizr is the only tool that is aware of the connection between elements on different views, which keeps all software architecture diagrams in sync." Gestalt must maintain **single source of truth** across all projections.

#### 2. C4 Model Abstraction Levels
**Source**: [C4 Diagram: The New Way to Visualize Software Architecture](https://www.codesee.io/learning-center/c4-diagram)

The C4 model's hierarchical approach directly maps to Gestalt:

| C4 Level | Gestalt Equivalent |
|----------|-------------------|
| **System Context** (birds-eye view) | `TownView` — all agents and their external interfaces |
| **Container** (applications, services) | `AgentView` — individual agent architecture |
| **Component** (building blocks) | `ProtocolView` — AGENTESE contexts and nodes |
| **Code** (implementation detail) | `NodeView` — specific affordances and handlers |

**Key Insight**: "The primary purpose of C4 tools is to visualize the architecture of a software system...at four levels of abstraction." Gestalt must support **semantic zoom** — more detail as you zoom in.

#### 3. Live Diagramming with Code Sync
**Source**: [Architecture Diagram Tools 2024](https://snappify.com/blog/architecture-diagram-tools)

Modern tools synchronize diagrams with running code:

| Live Pattern | Gestalt Application |
|--------------|---------------------|
| **Auto-diagram generation** | `LiveTrace` — generate from running agents |
| **Automated updates** (save time) | `AgentReflection` — diagrams update when code changes |
| **Single source of truth** | `AgentRegistry` — canonical agent definitions |
| **Pre-built themes** (cloud providers) | `ProtocolThemes` — visual styles for contexts |

---

## Precise User Flows

### Flow 1: First Exploration ("The Discovery")

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ ENTRY: Developer opens Gestalt for first time                                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  1. LANDING VIEW (0-5 seconds)                                               │
│     ├── System Context level loads automatically                             │
│     │                                                                        │
│     │   ┌─────────────────────────────────────────────────────────────┐     │
│     │   │  GESTALT: KGENTS ARCHITECTURE              [Search] [📷]    │     │
│     │   ├─────────────────────────────────────────────────────────────┤     │
│     │   │                                                             │     │
│     │   │          ┌─────────┐                                        │     │
│     │   │          │  USER   │                                        │     │
│     │   │          └────┬────┘                                        │     │
│     │   │               │                                             │     │
│     │   │               ▼                                             │     │
│     │   │    ┌──────────────────────────────────────────────┐        │     │
│     │   │    │                  KGENTS                       │        │     │
│     │   │    │                                               │        │     │
│     │   │    │   ┌────────┐  ┌────────┐  ┌────────┐         │        │     │
│     │   │    │   │ K-gent │──│ Town   │──│Atelier │         │        │     │
│     │   │    │   └────────┘  └────────┘  └────────┘         │        │     │
│     │   │    │                    │                          │        │     │
│     │   │    │              ┌─────┴─────┐                   │        │     │
│     │   │    │              │ AGENTESE  │                   │        │     │
│     │   │    │              └───────────┘                   │        │     │
│     │   │    └──────────────────────────────────────────────┘        │     │
│     │   │                                                             │     │
│     │   │  ZOOM LEVEL: [System ◉]  Container ○  Component ○  Code ○  │     │
│     │   └─────────────────────────────────────────────────────────────┘     │
│     │                                                                        │
│     └── Color coding: 🔵 Core | 🟢 Active | 🟡 Dormant                       │
│                                                                              │
│  2. INTERACTIVE EXPLORATION (click/zoom)                                     │
│     ├── User clicks on "AGENTESE" box                                        │
│     ├── Zoom level auto-advances: System → Container                         │
│     │                                                                        │
│     │   ┌─────────────────────────────────────────────────────────────┐     │
│     │   │  AGENTESE ARCHITECTURE                                      │     │
│     │   ├─────────────────────────────────────────────────────────────┤     │
│     │   │                                                             │     │
│     │   │    ┌──────────────────────────────────────────────────┐    │     │
│     │   │    │                   AGENTESE                        │    │     │
│     │   │    │                                                   │    │     │
│     │   │    │  ┌────────┐  ┌────────┐  ┌────────┐  ┌────────┐ │    │     │
│     │   │    │  │ world  │  │ self   │  │concept │  │ void   │ │    │     │
│     │   │    │  └────────┘  └────────┘  └────────┘  └────────┘ │    │     │
│     │   │    │       │           │           │           │      │    │     │
│     │   │    │       └───────────┼───────────┼───────────┘      │    │     │
│     │   │    │                   │                               │    │     │
│     │   │    │              ┌────┴────┐                         │    │     │
│     │   │    │              │ Logos   │                         │    │     │
│     │   │    │              │ Engine  │                         │    │     │
│     │   │    │              └─────────┘                         │    │     │
│     │   │    │                                                   │    │     │
│     │   │    └──────────────────────────────────────────────────┘    │     │
│     │   │                                                             │     │
│     │   │  ZOOM: System ○ [Container ◉] Component ○  Code ○          │     │
│     │   └─────────────────────────────────────────────────────────────┘     │
│     │                                                                        │
│     └── Breadcrumb: KGENTS > AGENTESE                                        │
│                                                                              │
│  3. DRILL INTO CONTEXT (double-click "world")                                │
│     ├── Zoom advances: Container → Component                                 │
│     │                                                                        │
│     │   ┌─────────────────────────────────────────────────────────────┐     │
│     │   │  world.* CONTEXT                                            │     │
│     │   ├─────────────────────────────────────────────────────────────┤     │
│     │   │                                                             │     │
│     │   │    NODES:                                                   │     │
│     │   │    ┌────────────┐  ┌────────────┐  ┌────────────┐          │     │
│     │   │    │ world.time │  │world.space │  │world.entity│          │     │
│     │   │    │            │  │            │  │            │          │     │
│     │   │    │ Affordances│  │ Affordances│  │ Affordances│          │     │
│     │   │    │ • manifest │  │ • manifest │  │ • manifest │          │     │
│     │   │    │ • witness  │  │ • navigate │  │ • inspect  │          │     │
│     │   │    │ • schedule │  │ • contains │  │ • interact │          │     │
│     │   │    └────────────┘  └────────────┘  └────────────┘          │     │
│     │   │                                                             │     │
│     │   │  ZOOM: System ○ Container ○ [Component ◉] Code ○           │     │
│     │   └─────────────────────────────────────────────────────────────┘     │
│     │                                                                        │
│     └── Click any affordance → see implementation (Code level)              │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Flow 2: Live Tracing ("The Running System")

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ CONTEXT: Developer connects Gestalt to running agent system                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  1. CONNECT TO LIVE SYSTEM                                                   │
│     ├── [Connect to Runtime] button                                          │
│     ├── Select endpoint: "localhost:8000" or "production-api.kgents.io"     │
│     └── Connection established: "🟢 Live — 3 agents active"                 │
│                                                                              │
│  2. REAL-TIME VIEW                                                           │
│     │                                                                        │
│     │   ┌─────────────────────────────────────────────────────────────┐     │
│     │   │  LIVE TRACE                           🟢 Connected          │     │
│     │   ├─────────────────────────────────────────────────────────────┤     │
│     │   │                                                             │     │
│     │   │        ┌─────────┐         ┌─────────┐                     │     │
│     │   │        │ K-gent  │ ──⚡──► │ Scout   │                     │     │
│     │   │        │ ∿∿∿∿    │ 23ms   │ ░░░░    │                     │     │
│     │   │        └─────────┘         └────┬────┘                     │     │
│     │   │                                 │                          │     │
│     │   │                            ⚡ 45ms                          │     │
│     │   │                                 ▼                          │     │
│     │   │                          ┌─────────┐                       │     │
│     │   │                          │ Sage    │                       │     │
│     │   │                          │ ████    │ ← currently executing │     │
│     │   │                          └─────────┘                       │     │
│     │   │                                                             │     │
│     │   │  Legend: ∿∿∿ Thinking  ░░░ Idle  ████ Active  ⚡ Message   │     │
│     │   │                                                             │     │
│     │   │  MESSAGE LOG:                                               │     │
│     │   │  14:23:45 K-gent → Scout: "Research X"                     │     │
│     │   │  14:23:47 Scout → Sage: "Found 5 results"                  │     │
│     │   │  14:23:48 Sage: Processing...                              │     │
│     │   │                                                             │     │
│     │   │  [⏸ Pause] [🔍 Filter] [📥 Export Trace]                   │     │
│     │   └─────────────────────────────────────────────────────────────┘     │
│     │                                                                        │
│     └── Click any agent → see internal state (eigenvectors, memory)         │
│                                                                              │
│  3. TRACE REPLAY                                                             │
│     ├── After session ends, full trace available                             │
│     ├── Timeline scrubber: drag to any point                                 │
│     ├── Step-through mode: advance message by message                        │
│     └── Export as: SVG, PNG, JSON, Mermaid                                   │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Flow 3: Protocol Authoring ("The Designer")

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ CONTEXT: Developer designing new AGENTESE protocol                           │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  1. SPLIT VIEW: Visual + DSL                                                 │
│     │                                                                        │
│     │   ┌─────────────────────────────┬─────────────────────────────────┐   │
│     │   │  VISUAL EDITOR              │  DSL EDITOR                      │   │
│     │   ├─────────────────────────────┼─────────────────────────────────┤   │
│     │   │                             │                                  │   │
│     │   │   ┌──────┐    ┌──────┐     │  context payment {              │   │
│     │   │   │ init │ →  │verify│     │    node transaction {           │   │
│     │   │   └──────┘    └───┬──┘     │      affordance initiate(       │   │
│     │   │                   │        │        amount: Currency,         │   │
│     │   │         ┌─────────┴────┐   │        recipient: Entity         │   │
│     │   │         │              │   │      ) -> TransactionId;         │   │
│     │   │    ┌────┴───┐    ┌────┴──┐│      affordance verify(          │   │
│     │   │    │process │    │reject │ │        txId: TransactionId       │   │
│     │   │    └────────┘    └───────┘ │      ) -> VerificationResult;    │   │
│     │   │                             │    }                             │   │
│     │   │   Drag to add: [+ Node]    │  }                               │   │
│     │   │                             │                                  │   │
│     │   └─────────────────────────────┴─────────────────────────────────┘   │
│     │                                                                        │
│     └── Changes in either pane sync immediately                              │
│                                                                              │
│  2. VALIDATION                                                               │
│     ├── Real-time law checking:                                              │
│     │   ├── ✓ All nodes have at least one affordance                        │
│     │   ├── ✓ Types are well-formed                                          │
│     │   ├── ⚠ "reject" node has no outgoing edges — terminal ok?            │
│     │   └── ✗ Missing: "process" needs error affordance                     │
│     └── Errors highlighted in both visual and DSL views                      │
│                                                                              │
│  3. EXPORT / INTEGRATE                                                       │
│     ├── [Generate Python] → creates handler stubs                            │
│     ├── [Generate Tests] → creates property-based tests                      │
│     └── [Add to Registry] → publishes to agent ecosystem                     │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Flow 4: Health Dashboard ("The Governance View")

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ CONTEXT: Tech lead reviewing architecture health                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  HEALTH DASHBOARD                                                            │
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │  ARCHITECTURE HEALTH                                                     ││
│  ├─────────────────────────────────────────────────────────────────────────┤│
│  │                                                                          ││
│  │  OVERALL: B+ (83%)                                                       ││
│  │                                                                          ││
│  │  METRICS:                                                                ││
│  │  Coupling:    ██████████░░░░░░░░░░ 50%  ⚠️ Above target                 ││
│  │  Cohesion:    ████████████████░░░░ 80%  ✅ On track                     ││
│  │  Drift:       ██░░░░░░░░░░░░░░░░░░ 10%  ✅ Low                          ││
│  │  Coverage:    ██████████████████░░ 90%  ✅ Excellent                    ││
│  │                                                                          ││
│  │  DRIFT ALERTS (3):                                                       ││
│  │  ┌─────────────────────────────────────────────────────────────────┐    ││
│  │  │ ⚠️ agents/town → protocols/api (undeclared dependency)         │    ││
│  │  │    [Declare] [Suppress] [View Code]                             │    ││
│  │  ├─────────────────────────────────────────────────────────────────┤    ││
│  │  │ ⚠️ agents/atelier importing from agents/town (layer violation)  │    ││
│  │  │    [Refactor] [Suppress] [View Code]                            │    ││
│  │  └─────────────────────────────────────────────────────────────────┘    ││
│  │                                                                          ││
│  │  MODULE HEALTH RANKING:                                                  ││
│  │  1. protocols/agentese  A+ (97%)                                        ││
│  │  2. agents/k/           A  (92%)                                        ││
│  │  3. agents/town/        B+ (85%)                                        ││
│  │  ...                                                                     ││
│  │  12. agents/atelier/    C  (72%) ← needs attention                      ││
│  │                                                                          ││
│  │  [Export Report] [Schedule Review] [Set Policies]                       ││
│  │                                                                          ││
│  └─────────────────────────────────────────────────────────────────────────┘│
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Interaction Micropatterns

### Semantic Zoom Behavior

```
Zoom level determines what's visible:

SYSTEM LEVEL (zoomed out):
┌─────────────────────────────────────────────────────────────┐
│ All agents as labeled boxes, connections as lines           │
│ No internal detail, just topology                           │
└─────────────────────────────────────────────────────────────┘
           │
           │ zoom in
           ▼
CONTAINER LEVEL:
┌─────────────────────────────────────────────────────────────┐
│ Agent internals visible: contexts, major components         │
│ Connections show protocol names                             │
└─────────────────────────────────────────────────────────────┘
           │
           │ zoom in
           ▼
COMPONENT LEVEL:
┌─────────────────────────────────────────────────────────────┐
│ Individual nodes visible, affordances listed                │
│ Data types shown on connections                             │
└─────────────────────────────────────────────────────────────┘
           │
           │ zoom in
           ▼
CODE LEVEL:
┌─────────────────────────────────────────────────────────────┐
│ Actual handler code snippets visible                        │
│ Line-level connections to source files                      │
│ [Click to open in editor]                                   │
└─────────────────────────────────────────────────────────────┘
```

### Context-Sensitive Actions

```
Right-click on any element:

┌─────────────────────────────────────────┐
│ 🔍 SCOUT AGENT                          │
├─────────────────────────────────────────┤
│ 📖 View Documentation                   │
│ 📊 See Live Metrics                     │
│ 🔗 Show All Connections                 │
│ 📝 Add Annotation                       │
│ 📷 Export as Image                      │
│ ────────────────────────────────────    │
│ 🔧 Open in Editor (VS Code)             │
│ 🧪 Run Tests for This Agent             │
│ 📜 View Git History                     │
└─────────────────────────────────────────┘
```

---

## References

- `plans/reactive-substrate-unification.md`
- `agents/m/cartography.py`
- `agents/town/coalitions.py`
- `protocols/agentese/`
- `protocols/terrarium/`

### UX Research Sources

- [Software Architecture as Code with Structurizr](https://mydeveloperplanet.com/2024/03/20/software-architecture-as-code-with-structurizr/) — Architecture-as-code patterns
- [C4 Diagram Guide](https://www.codesee.io/learning-center/c4-diagram) — Hierarchical abstraction levels
- [C4 Model Tools](https://www.codesee.io/learning-center/c4-model-tools) — Tool comparison
- [Architecture Diagram Tools 2024](https://snappify.com/blog/architecture-diagram-tools) — Modern tooling landscape
- [C4 Model Official](https://c4model.com/) — C4 model specification

---

*Last updated: 2025-12-15*
