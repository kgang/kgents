---
path: plans/core-apps/gestalt-architecture-visualizer
status: active
progress: 0.70
last_touched: 2025-12-16
touched_by: claude-opus-4-5
blocking: []
enables:
  - plans/reactive-substrate-unification
  - monetization/grand-initiative-monetization
session_notes: |
  Session 6 (2025-12-16): DevEx Hardening Sprint.
  - Created docs/skills/codebase-analysis.md skill document covering:
    - Adding new language analyzers (Go, Rust, etc.)
    - Creating custom governance rules (Layer, Ring, Custom)
    - Extending health metrics
    - Wiring new AGENTESE paths
  - Added suggested_fix field and generation to DriftViolation:
    - LAYER violations: move module, extract shared, or suppress
    - RING violations: move to inner ring, use interfaces, or DI
    - DENY violations: remove import, use adapter, or exception
  - Extracted Analyzer[T] protocol for language-agnostic analysis:
    - Analyzer protocol with can_analyze, analyze_source, analyze_file, discover
    - AnalyzerRegistry for managing multiple analyzers
    - PythonAnalyzer and TypeScriptAnalyzer concrete implementations
    - create_default_registry() and get_default_registry() helpers
  - Added GestaltStoreFactory with builder pattern:
    - with_config(), with_language(), with_graph(), with_violations()
    - with_debounce() for configuring file watcher
    - Enables easy testing without filesystem scanning
  - Fixed rich markup escaping bug in path_display.py (property-based test edge case)
  - All 146 gestalt tests passing

  Session 5 (2025-12-16): Spike 6A Elastic Edition - Responsive UI Refactor.
  - Completely refactored Gestalt.tsx to use elastic primitives:
    - ElasticSplit for canvas/panel responsive layout
    - ElasticContainer for control panel with density-aware styling
    - useWindowLayout for responsive breakpoint detection
  - Three layout modes based on screen size:
    - Desktop (>1024px): Canvas | Controls | Details with draggable divider
    - Tablet (768-1024px): Canvas | Controls/Details with dynamic split ratio
    - Mobile (<768px): Full canvas + FloatingActions + BottomDrawer panels
  - Density-aware rendering (compact/comfortable/spacious):
    - NODE_BASE_SIZE scales 0.2/0.25/0.3
    - LABEL_FONT_SIZE scales 0.14/0.18/0.22
    - MAX_VISIBLE_LABELS scales 15/30/50
    - Control panel adapts: inline checkboxes on compact, legend only on spacious
    - Detail panel: 4-col stats grid on compact, 2-col on comfortable+
  - New mobile-specific components:
    - FloatingActions: Scan/Controls/Details toggle buttons
    - BottomDrawer: Slide-up panels with drag handle
    - Auto-open details drawer on node click
  - Smart defaults: labels off on mobile, fewer max nodes
  - Dynamic split ratio: expands canvas when no module selected

  Session 4 (2025-12-16): Spike 6A Hardened - Robustified CLI Handler.
  - Added OTEL span instrumentation (gestalt.* spans with duration metrics)
  - Added dual-channel output support (InvocationContext, _emit_output, _emit_error)
  - Added --help/-h flag with comprehensive usage documentation
  - Added proper error handling with exit codes (0=success, 1=error)
  - Added property-based tests with Hypothesis (arbitrary args, module names)
  - Added performance baseline tests (manifest/health/drift <100ms, scan <2s)
  - Added OTEL span verification tests
  - Verified CrownJewelRegistry integration (10 Gestalt paths registered)
  - Total: 146 tests passing (analysis 34 + governance 24 + reactive 45 + handler 43)
  - Cross-synergy: Brain handler patterns (thread-safe singleton, factory injection, OTEL)

  Session 3 (2025-12-16): Spike 6B Complete - Web Topology Component.
  - Created protocols/api/gestalt.py with REST endpoints:
    - GET /v1/world/codebase/manifest -> Full architecture graph
    - GET /v1/world/codebase/health -> Health metrics summary
    - GET /v1/world/codebase/drift -> Drift violations
    - GET /v1/world/codebase/module/{name} -> Module details
    - POST /v1/world/codebase/scan -> Force rescan
    - GET /v1/world/codebase/topology -> Graph data for visualization
  - Added gestaltApi to web/src/api/client.ts
  - Created Gestalt.tsx page with:
    - 3D force-directed graph using react-three-fiber
    - Module nodes with health-based coloring (A+:green to F:red)
    - Node sizing by LOC and health score
    - Dependency edges (gray) with violation highlighting (red)
    - Layer ring overlays
    - Zoom/pan/rotate controls (OrbitControls)
    - Module detail sidebar on click (health stats, dependencies, violations)
    - Health distribution chart
    - Layer filter dropdown
    - Max nodes slider (50-500)
  - Added TypeScript types for all codebase responses
  - Route added: /gestalt
  - All 135 gestalt tests passing

  Session 2 (2025-12-16): Spike 6A Complete - GestaltStore CLI Wiring.
  - Updated handler.py to use GestaltStore reactive substrate
  - All CLI commands now read from GestaltStore Signals/Computed:
    - manifest: store.module_count, store.edge_count, store.overall_grade
    - health: store.grade_distribution, store.module_healths
    - drift: store.violations Signal, store.drift_count, store.active_drift_count
    - module: store.graph, store.violations
  - Added --watch flag for live file watching mode
  - Created test injection hooks (_set_store_factory, _reset_store)
  - 32 new handler tests verifying CLI output matches store state
  - Total: 135 tests passing (analysis + governance + reactive + handler)

  Session 1 (2025-12-16): Phase 1 Complete - Core Analysis Engine.
  - Created protocols/gestalt/ with analysis.py and governance.py
  - Implemented ModuleHealth dataclass with weighted health scoring
  - Python and TypeScript import parsing (AST + regex)
  - ArchitectureGraph with instability metric (Martin's I = Ce/(Ca+Ce))
  - LayerRule and RingRule for drift detection
  - GovernanceConfig with pattern-based layer/ring assignment
  - Wired to AGENTESE: world.codebase.* paths
  - CLI commands: kg world codebase [manifest|health|drift|module|scan]
  - Scanned kgents: 1814 modules, 14226 edges, B+ (86%) overall health

  Previous: Relocated to core-apps; format aligned with pillar plans.
phase_ledger:
  PLAN: complete
  RESEARCH: complete
  DEVELOP: complete
  STRATEGIZE: touched  # OTEL span design
  CROSS-SYNERGIZE: touched  # Brain handler patterns, Crown Jewel registry
  IMPLEMENT: touched
  QA: touched  # Property-based tests, performance baselines
  TEST: complete
  EDUCATE: pending
  MEASURE: pending
  REFLECT: pending
entropy:
  planned: 0.10
  spent: 0.05
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
| **Status** | Phase 1 complete (analysis engine + CLI); Phase 2-5 pending |
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

### Phase 5 — AGENTESE v3 Integration (Chunk 5)
**Goal**: Full Logos paths for architecture + v3 features.

#### Path Registry

| AGENTESE Path | Aspect | Handler | Effects |
|---------------|--------|---------|---------|
| `world.codebase.manifest` | manifest | Full architecture graph | — |
| `world.codebase.module[name].manifest` | manifest | Module details | — |
| `world.codebase.layer[name].manifest` | manifest | Layer with members | — |
| `world.codebase.drift.witness` | witness | Drift violations | — |
| `world.codebase.drift.refine` | refine | Challenge drift rule | — |
| `world.codebase.health.manifest` | manifest | Health metrics | — |
| `world.codebase.subscribe` | witness | Live architecture updates | — |
| `?world.codebase.module.*` | query | Search modules by pattern | — |
| `?world.codebase.drift.*` | query | Search drift violations | — |
| `self.memory.cartography` | manifest | Holographic architecture view | — |
| `concept.governance.manifest` | manifest | Architecture rules | — |
| `concept.governance.refine` | refine | Propose rule change | `QUEUE_REVIEW` |

#### Observer-Dependent Perception

```python
# Security engineer sees: vulnerabilities, access patterns
await logos("world.codebase.manifest", security_umwelt)
# → SecurityView(vulnerable_deps, access_paths, attack_surface)

# Performance engineer sees: hot paths, bottlenecks
await logos("world.codebase.manifest", performance_umwelt)
# → PerformanceView(hot_modules, coupling_bottlenecks, complexity_spikes)

# Product manager sees: feature modules, dependencies
await logos("world.codebase.manifest", product_umwelt)
# → ProductView(feature_modules, integration_points, change_impact)

# Tech lead sees: health metrics, governance
await logos("world.codebase.manifest", tech_lead_umwelt)
# → GovernanceView(health_grades, drift_alerts, layer_violations)
```

#### Subscription Patterns

```python
# Live architecture updates (file watcher → Signal → subscription)
arch_sub = await logos.subscribe(
    "world.codebase.update",
    delivery=DeliveryMode.AT_MOST_ONCE,  # Debounce OK
    buffer_size=50
)

# Drift alerts (important, don't miss)
drift_sub = await logos.subscribe(
    "world.codebase.drift.alert",
    delivery=DeliveryMode.AT_LEAST_ONCE
)

# Health degradation warnings
health_sub = await logos.subscribe(
    "world.codebase.health.warning",
    delivery=DeliveryMode.AT_LEAST_ONCE
)
```

#### CLI Shortcuts

```yaml
# .kgents/shortcuts.yaml additions
arch: world.codebase.manifest
modules: "?world.codebase.module.*"
drift: world.codebase.drift.witness
health: world.codebase.health.manifest
layers: "?world.codebase.layer.*"
governance: concept.governance.manifest
tour: world.codebase.tour
```

#### Pipeline Composition

```python
# Scan → analyze → report
analysis_pipeline = (
    path("world.codebase.manifest")
    >> path("world.codebase.health.manifest")
    >> path("world.codebase.drift.witness")
)

# Governance challenge workflow
challenge_pipeline = (
    path("world.codebase.drift[id].manifest")
    >> path("world.codebase.drift[id].refine")  # Propose exception
    >> path("concept.governance.refine")         # Queue for review
)
```

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
