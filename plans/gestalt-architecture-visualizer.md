---
path: plans/gestalt-architecture-visualizer
status: research
progress: 0.05
last_touched: 2025-12-15
touched_by: gpt-5-codex
blocking: []
enables: [reactive-substrate-unification, monetization/grand-initiative-monetization]
session_notes: |
  Promoted from brainstorming/developer-tools-on-kgents.md
  Key insight: Architecture visualization IS reactive substrate application
  Leverages M-gent HoloMaps + Projection Protocol for multi-target rendering
  Revenue potential: $29/mo Pro tier, $99/seat Enterprise
  Fresh research sweep (Dec 2025): CodeSee Maps (living code maps), CodeScene (temporal coupling & socio-technical metrics), Structurizr (C4-as-code), ArchGuard (architecture governance) all validate demand for drift-free living diagrams; none provide reactive multi-target projections or holographic storage.
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

**AGENTESE Context**: `world.codebase.manifest`, `self.memory.cartography`
**Status**: research (0 tests)
**Principles**: Composable, Generative, Joy-Inducing, Transparent Infrastructure, Explainable-by-default
**Cross-refs**: `plans/reactive-substrate-unification.md`, `agents/m/cartography.py`

---

## Current Readiness (audit)
- Engine: nonexistent; reuse Cartographer scaffolding + reactive substrate primitives available.
- Interfaces: CLI/Web/AGENTESE affordances defined; no implementations.
- Data: No corpus of example repos; need goldens for correctness + regressions.
- Tests: 0; target 80+ before CLI/Web shipping.

---

## Core Insight

Traditional architecture visualization is **static**: draw once, watch it rot. Gestalt inverts this by treating architecture as **live reactive state**:

```
Traditional: Human draws → Diagram → (time passes) → Stale diagram

Gestalt:     Signal[Architecture] → Auto-updates → Projections
             (watches code)        (reactive)      (CLI/Web/VR)
```

The architecture IS a `Signal[ArchitectureState]`. File changes update the signal. Projectors render to any target. **Zero manual maintenance.**

---

## Fresh Market Scan (Dec 2025)

| Product | What they do | Gaps we exploit |
|---------|--------------|-----------------|
| **CodeSee Maps** | Live dependency maps for onboarding | Lacks governance + drift policy, no multi-target projections (CLI/Web/VR), no holographic memory |
| **CodeScene** | Temporal coupling + socio-technical metrics | No reactive substrate or projections; limited explorable graph; mostly reports |
| **Structurizr** | C4-as-code diagrams | Static; refresh requires re-render; no drift detection or live health signals |
| **ArchGuard** | Architecture governance (China OSS) | Limited integrations; not reactive; no holographic storage; thin visualization |
| **IDE diagrams (JetBrains/VSCode)** | On-demand local diagrams | IDE-bound, not collaborative; no historical drift trail |

Takeaway: Demand validated for living diagrams, but nobody offers reactive, multi-surface projections powered by holographic storage and governance hooks.

---

## The Gestalt Vision

```
                     GESTALT ARCHITECTURE
                            │
     ┌──────────────────────┼──────────────────────┐
     │                      │                      │
     ▼                      ▼                      ▼
 FILE WATCHER         HOLOMAP ENGINE         PROJECTION LAYER

 Watches for          Builds reactive        Renders to any
 code changes         architecture graph     target surface
     │                      │                      │
     ▼                      ▼                      ▼
 inotify/fswatch      M-gent Cartographer    Reactive Substrate
     │                      │                      │
     └──────────────────────┼──────────────────────┘
                            │
                            ▼
              ┌─────────────┴─────────────┐
              │                           │
         CHANGE EVENT              ARCHITECTURE SIGNAL
              │                           │
              ▼                           ▼
     Signal.set(new_arch)          Subscribers notified
              │                           │
              └─────────────┬─────────────┘
                            │
           ┌────────────────┼────────────────┐
           │                │                │
           ▼                ▼                ▼
       CLI Mode         Web Mode         VR Mode
                                        (future)
   ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
   │ auth ████░░  │  │  [Interactive │  │  [Walk       │
   │ api  ██████  │  │   node graph] │  │   through    │
   │ db   ███░░░  │  │              │  │   your code] │
   │              │  │  Dependency  │  │              │
   │ drift: 12%   │  │  health      │  │  3D city     │
   │ coupling: 7  │  │  sparklines  │  │  metaphor    │
   └──────────────┘  └──────────────┘  └──────────────┘
```

---

## Why Kgents Uniquely Enables This

| Kgents System | Gestalt Application | Synergy |
|---------------|---------------------|---------|
| **Reactive Substrate** | `Signal[ArchitectureState]` auto-notifies all views | Core mechanism |
| **Projection Protocol** | Same data → CLI/TUI/Web/marimo/VR rendering | Multi-target |
| **M-gent CartographerAgent** | Builds HoloMaps from code structure | Analysis engine |
| **M-gent HolographicMemory** | Architecture IS holographic - any fragment reconstructs whole | Efficient storage |
| **Terrarium metrics** | Real-time health scores, dependency heat | Observability |
| **AGENTESE paths** | `world.codebase.module[name=auth].manifest` for navigation | Unified API |
| **Agent Town coalitions** | Modules as "citizens" that form coalitions (layers, features) | Social metaphor |

### The Holographic Principle Applied

M-gent's holographic memory means:

```python
# Any module view contains enough to reconstruct relationships
auth_module = await logos.invoke("world.codebase.module[name=auth].manifest", umwelt)

# Returns not just auth, but auth's place in the whole:
# - Inbound dependencies (who calls auth)
# - Outbound dependencies (what auth uses)
# - Coupling score (how entangled)
# - Cohesion score (how self-contained)
# - Drift from declared architecture
```

---

## Quality Bar & Guardrails
- **Explainability**: Every health score exposes factors + source lines; drift alerts link to exact imports/commit.
- **Policy-aware**: Layer/ring rules expressed as code (C4/ADR anchors) with allow/deny lists; suppressions are auditable.
- **Multi-language path**: Start Python + TypeScript; design interfaces to add JVM/.NET later without refactors.
- **Performance**: <5s cold scan on 1000-file repo; <2s incremental; incremental graph diffing preferred over full rebuild.
- **Privacy**: No code leaves host by default; anonymized metrics only with explicit opt-in; align with `protocols/licensing` data contracts.
- **Test depth**: Golden repos + snapshot tests for projections; property tests for dependency graph invariants; contract tests for AGENTESE resolvers.

---

## Architecture Health Metrics

Gestalt tracks these real-time metrics per module:

| Metric | Calculation | Signal |
|--------|-------------|--------|
| **Coupling** | Inbound + Outbound dependencies | `coupling_score: Signal[float]` |
| **Cohesion** | Internal vs external calls ratio | `cohesion_score: Signal[float]` |
| **Drift** | Actual vs declared dependencies | `drift_score: Signal[float]` |
| **Complexity** | Cyclomatic + cognitive | `complexity_score: Signal[float]` |
| **Churn** | Recent change frequency | `churn_score: Signal[float]` |
| **Test Coverage** | Lines covered / total | `coverage_score: Signal[float]` |

### Aggregate Health

```python
@dataclass(frozen=True)
class ModuleHealth:
    """Holographic health snapshot of a module."""
    name: str
    coupling: float      # 0-1, lower is better
    cohesion: float      # 0-1, higher is better
    drift: float         # 0-1, lower is better
    complexity: float    # 0-1, lower is better
    churn: float         # 0-1, lower is better (high = unstable)
    coverage: float      # 0-1, higher is better
    instability: float | None = None  # Martin metric; opt-in when git history available

    @property
    def overall_health(self) -> float:
        """Weighted aggregate health score."""
        return (
            (1 - self.coupling) * 0.20 +
            self.cohesion * 0.15 +
            (1 - self.drift) * 0.25 +
            (1 - self.complexity) * 0.15 +
            (1 - self.churn) * 0.10 +
            self.coverage * 0.15
        )

    @property
    def health_grade(self) -> str:
        """A-F grade for quick assessment."""
        score = self.overall_health
        if score >= 0.9: return "A"
        if score >= 0.8: return "B"
        if score >= 0.7: return "C"
        if score >= 0.6: return "D"
        return "F"
```

**Data sources**: static imports, git history (churn + instability), test coverage artifacts, declared architecture rules (ADR/C4/CUE).
**Time decay**: drift penalties age out after N green builds; churn smoothed with EWMA to avoid alert storms.

---

## User Journeys

### Journey 1: First-Time Setup (Day 1)

```
Developer                    Gestalt                        Output
    │                           │                              │
    ├─ gestalt init ───────────▶│                              │
    │                           │                              │
    │                           ├─ Scan codebase               │
    │                           │  (CartographerAgent)         │
    │                           │                              │
    │                           ├─ Build HoloMap               │
    │                           │  (dependency graph)          │
    │                           │                              │
    │                           ├─ Detect layers               │
    │                           │  (k-clique coalitions)       │
    │                           │                              │
    │◀──────────────────────────┤                              │
    │                           │                              │
    │  "Found 47 modules in     │                              │
    │   6 detected layers:      │                              │
    │   - api (8 modules)       │                              │
    │   - domain (12 modules)   │                              │
    │   - infra (15 modules)    │                              │
    │   - shared (7 modules)    │                              │
    │   - tests (excluded)      │                              │
    │                           │                              │
    │   Health: B (0.82)        │                              │
    │   Drift detected: 3       │                              │
    │   modules have undeclared │                              │
    │   dependencies"           │                              │
```

### Journey 2: Daily Workflow (Week 1)

```
Developer                    Gestalt (watching)              Signals
    │                           │                              │
    ├─ Edit auth/tokens.py ────▶│                              │
    │                           │                              │
    │                           ├─ fswatch detects change      │
    │                           │                              │
    │                           ├─ Re-analyze auth module      │
    │                           │                              │
    │                           ├─ Update Signal[Architecture] │
    │                           │                              │
    │                           ├─ Notify all subscribers      │
    │                           │  (CLI sparkline, web dash)   │
    │                           │                              │
    │                           │                              │
    │  (CLI auto-updates)       │                              │
    │  auth: ████████░░ B       │                              │
    │        ↑ +0.02 (tokens)   │                              │
    │                           │                              │
    ├─ Add new import ─────────▶│                              │
    │  (from db import ...)     │                              │
    │                           │                              │
    │                           ├─ Detect new dependency       │
    │                           │  auth → db (NEW)             │
    │                           │                              │
    │                           ├─ Check declared deps         │
    │                           │  auth.toml: db NOT declared  │
    │                           │                              │
    │◀──────────────────────────┤                              │
    │                           │                              │
    │  ⚠️  Drift detected:       │                              │
    │  auth → db is undeclared  │                              │
    │                           │                              │
    │  Options:                 │                              │
    │  1. Add to auth deps      │                              │
    │  2. Investigate coupling  │                              │
    │  3. Suppress (risky)      │                              │
```

### Journey 3: Architecture Review (Month 1)

```
Team Lead                    Gestalt Web Dashboard           Actions
    │                           │                              │
    ├─ Open gestalt.dev/org ───▶│                              │
    │                           │                              │
    │                           │   ┌─────────────────────┐    │
    │                           │   │ ARCHITECTURE HEALTH │    │
    │                           │   │                     │    │
    │                           │   │  Overall: B (0.79)  │    │
    │                           │   │                     │    │
    │                           │   │  [Node Graph]       │    │
    │                           │   │   api ──→ domain    │    │
    │                           │   │     ╲     ↓         │    │
    │                           │   │      → infra ←      │    │
    │                           │   │        ↑            │    │
    │                           │   │      shared         │    │
    │                           │   │                     │    │
    │                           │   │  DRIFT ALERTS (3)   │    │
    │                           │   │  ⚠️ payments → auth  │    │
    │                           │   │  ⚠️ api → db direct  │    │
    │                           │   │  ⚠️ shared → domain  │    │
    │                           │   │                     │    │
    │                           │   │  [Weekly Sparklines]│    │
    │                           │   │  coupling: ▁▂▃▃▃▂▁  │    │
    │                           │   │  coverage: ▅▅▆▆▆▆▇  │    │
    │                           │   │  drift:    ▂▂▃▅▆▆▇  │    │
    │                           │   └─────────────────────┘    │
    │                           │                              │
    ├─ Click "payments" node ──▶│                              │
    │                           │                              │
    │                           │   ┌─────────────────────┐    │
    │                           │   │ payments MODULE     │    │
    │                           │   │                     │    │
    │                           │   │ Health: C (0.68)    │    │
    │                           │   │                     │    │
    │                           │   │ Declared deps: 4    │    │
    │                           │   │ Actual deps: 6      │    │
    │                           │   │ Drift: 2 undeclared │    │
    │                           │   │                     │    │
    │                           │   │ Suggested actions:  │    │
    │                           │   │ - Declare auth dep  │    │
    │                           │   │ - Extract webhook   │    │
    │                           │   │   handler to shared │    │
    │                           │   │                     │    │
    │                           │   │ [Export to ADR]     │    │
    │                           │   └─────────────────────┘    │
```

### Journey 4: Onboarding New Developer (Month 3)

```
New Developer                Gestalt Interactive             Learning
    │                           │                              │
    ├─ gestalt tour ───────────▶│                              │
    │                           │                              │
    │                           │  "Welcome! Let's explore     │
    │                           │   your codebase together."   │
    │                           │                              │
    │                           │  Starting at: api/           │
    │                           │                              │
    │                           │  api/ (8 modules)            │
    │                           │  ├── routes/                 │
    │                           │  │   └── health: A           │
    │                           │  │   └── auth: B             │
    │                           │  │   └── payments: C         │
    │                           │  └── middleware/             │
    │                           │      └── logging: A          │
    │                           │                              │
    │                           │  "This layer handles HTTP.   │
    │                           │   Notice payments (C grade)  │
    │                           │   has some technical debt."  │
    │                           │                              │
    ├─ "show me payments" ─────▶│                              │
    │                           │                              │
    │                           │  payments dependency tree:   │
    │                           │                              │
    │                           │  payments                    │
    │                           │  ├── stripe (external)       │
    │                           │  ├── domain/billing ✓        │
    │                           │  ├── domain/customers ✓      │
    │                           │  ├── infra/db ✓              │
    │                           │  ├── auth ⚠️ (undeclared)     │
    │                           │  └── shared/webhook ⚠️        │
    │                           │                              │
    │                           │  "The auth dependency should │
    │                           │   probably go through the    │
    │                           │   domain layer instead."     │
```

### Journey 5: VR Exploration (Future State)

```
Developer with VR           Gestalt VR                       Experience
    │                           │                              │
    ├─ gestalt vr ─────────────▶│                              │
    │                           │                              │
    │                           │  [Enters 3D codebase city]   │
    │                           │                              │
    │                           │       ╔═══════════╗          │
    │                           │       ║   API     ║          │
    │                           │       ║  (tall)   ║          │
    │                           │       ╚═══════════╝          │
    │                           │            │                 │
    │                           │     ╔══════╧══════╗          │
    │                           │     ║   DOMAIN    ║          │
    │                           │     ║  (medium)   ║          │
    │                           │     ╚═════════════╝          │
    │                           │            │                 │
    │                           │     ╔══════╧══════╗          │
    │                           │     ║    INFRA    ║          │
    │                           │     ║   (wide)    ║          │
    │                           │     ╚═════════════╝          │
    │                           │                              │
    │                           │  Buildings = modules         │
    │                           │  Height = complexity         │
    │                           │  Color = health grade        │
    │                           │    (green=A, red=F)          │
    │                           │  Bridges = dependencies      │
    │                           │  Bridge thickness = coupling │
    │                           │                              │
    ├─ Walk to payments ───────▶│                              │
    │                           │                              │
    │                           │  [Building pulses orange]    │
    │                           │  [Two red bridges visible]   │
    │                           │  [Voice: "This module has    │
    │                           │   undeclared dependencies"]  │
```

---

## Implementation Phases

### Phase 1: Core Analysis Engine (Chunk 1)

**Goal**: Build the static analysis foundation using M-gent CartographerAgent.

**Scope additions**:
- Parse Python + TypeScript imports (tsserver AST or tree-sitter) to de-risk polyglot path.
- Pluggable rules engine for layer policies (C4-like levels, explicit allow/deny).
- Minimal corpus of golden repos (clean arch, layered, hexagonal, monorepo) for regression.

**Files**:
```
impl/claude/agents/gestalt/
├── __init__.py
├── analyzer.py           # Code structure analyzer
├── dependency_graph.py   # Dependency extraction
├── metrics.py            # Health metric calculations
└── _tests/
    ├── test_analyzer.py
    ├── test_dependency_graph.py
    └── test_metrics.py
```

**Key Types**:
```python
@dataclass(frozen=True)
class ModuleNode:
    """A node in the architecture graph."""
    name: str
    path: Path
    dependencies: frozenset[str]
    dependents: frozenset[str]
    metrics: ModuleHealth
    layer: str | None = None  # Detected or declared layer

@dataclass(frozen=True)
class ArchitectureGraph:
    """The full architecture as an immutable graph."""
    modules: Mapping[str, ModuleNode]
    layers: Mapping[str, frozenset[str]]  # layer_name -> module_names
    edges: frozenset[tuple[str, str]]     # (from, to) dependencies
    timestamp: datetime

    def health_score(self) -> float:
        """Aggregate health of entire architecture."""
        ...

    def drift_violations(self) -> list[DriftViolation]:
        """Find undeclared or forbidden dependencies."""
        ...
```

**Exit Criteria**:
- Parse Python imports to build dependency graph
- Parse TypeScript imports for parity
- Calculate coupling, cohesion, complexity metrics
- Detect layers via k-clique analysis (reuse from Agent Town)
- Drift detection vs declared rules; suppression file supported
- Golden repo fixtures + 50+ tests (property + snapshot)

### Phase 2: Reactive Substrate Integration (Chunk 2)

**Goal**: Wrap architecture in Signal/Computed for reactive updates.

**Files**:
```
impl/claude/agents/gestalt/
├── reactive.py           # Signal[ArchitectureGraph]
├── watcher.py            # File system watcher
└── _tests/
    ├── test_reactive.py
    └── test_watcher.py
```

**Key Types**:
```python
class GestaltState:
    """Reactive architecture state."""

    def __init__(self, root_path: Path):
        self.root = root_path
        self._architecture: Signal[ArchitectureGraph] = Signal(self._initial_scan())

        # Derived signals
        self.overall_health = Computed(
            lambda: self._architecture.value.health_score()
        )
        self.drift_count = Computed(
            lambda: len(self._architecture.value.drift_violations())
        )
        self.module_count = Computed(
            lambda: len(self._architecture.value.modules)
        )

        # Module-level signals (lazy)
        self._module_signals: dict[str, Signal[ModuleNode]] = {}

    def module_signal(self, name: str) -> Signal[ModuleNode]:
        """Get reactive signal for specific module."""
        if name not in self._module_signals:
            self._module_signals[name] = Computed(
                lambda: self._architecture.value.modules.get(name)
            )
        return self._module_signals[name]

    async def start_watching(self) -> None:
        """Start file system watcher for live updates."""
        async for event in self._watcher.events():
            affected_modules = self._identify_affected(event)
            new_graph = self._reanalyze(affected_modules)
            self._architecture.set(new_graph)
```

**Exit Criteria**:
- File changes trigger signal updates
- Derived computations invalidate correctly
- Incremental graph diffing (no full rescans on single-file change)
- 30+ tests (fswatch mocks + performance budget checks)

### Phase 3: CLI Projection (Chunk 3)

**Goal**: CLI output with sparklines and health grades.

**Files**:
```
impl/claude/protocols/cli/handlers/gestalt.py
impl/claude/agents/gestalt/projections/
├── __init__.py
├── cli.py                # ASCII rendering
└── _tests/
    └── test_cli.py
```

**CLI Commands**:
```bash
# Initialize gestalt for a project
gestalt init [--path PATH]

# Show current health overview
gestalt status

# Watch for changes (live CLI updates)
gestalt watch

# Show specific module details
gestalt show <module>

# Interactive tour mode
gestalt tour

# Export architecture to formats
gestalt export --format [mermaid|dot|json|adr]
```

**Example Output**:
```
$ gestalt status

GESTALT ARCHITECTURE HEALTH
═══════════════════════════════════════════════════════════

Overall Health: B (0.79)    Modules: 47    Layers: 6

LAYER HEALTH
─────────────────────────────────────────────────────────────
  api       ████████░░ B   8 modules   coupling: 0.23
  domain    ██████████ A  12 modules   coupling: 0.12
  infra     ███████░░░ B  15 modules   coupling: 0.31
  shared    █████░░░░░ C   7 modules   coupling: 0.45
─────────────────────────────────────────────────────────────

DRIFT ALERTS (3)
─────────────────────────────────────────────────────────────
  ⚠️  payments → auth      (undeclared, suggest: declare or refactor)
  ⚠️  api → db             (layer violation, suggest: go through domain)
  ⚠️  shared → domain      (reverse dependency, suggest: extract)
─────────────────────────────────────────────────────────────

RECENT CHANGES (24h)
─────────────────────────────────────────────────────────────
  coupling:  ▁▂▃▃▃▂▁  stable
  coverage:  ▅▅▆▆▆▆▇  improving (+2%)
  drift:     ▂▂▃▅▆▆▇  degrading (+2 violations)
─────────────────────────────────────────────────────────────
```

**Exit Criteria**:
- `gestalt init` scans and displays summary
- `gestalt status` shows health and drift
- `gestalt watch` updates live as files change
- `gestalt export` outputs C4-ish JSON + mermaid graph for docs
- 40+ tests (golden snapshots + contract tests for exit codes)

### Phase 4: Web Dashboard (Chunk 4)

**Goal**: React-based interactive visualization.

**Files**:
```
impl/claude/web/src/pages/Gestalt.tsx
impl/claude/web/src/components/gestalt/
├── ArchitectureGraph.tsx     # D3/vis.js node graph
├── ModuleDetail.tsx          # Module drill-down
├── HealthSparkline.tsx       # Time-series health
├── DriftAlerts.tsx           # Alert list
└── LayerView.tsx             # Layer-based view
impl/claude/protocols/api/gestalt.py   # REST endpoints
```

**API Endpoints**:
```
GET  /v1/gestalt/status                    # Overall health
GET  /v1/gestalt/modules                   # All modules
GET  /v1/gestalt/modules/{name}            # Module detail
GET  /v1/gestalt/drift                     # Drift violations
GET  /v1/gestalt/history                   # Health over time
SSE  /v1/gestalt/stream                    # Live updates
```

**Exit Criteria**:
- Interactive node graph with click-to-drill
- Health sparklines for week/month
- Drift alert management
- SSE live updates; offline-first cache for recent health
- SLA: initial load <2s on 50-module repo; zoom/pan @ 60fps on mid laptops
- 50+ tests (frontend + API)

### Phase 5: AGENTESE Integration (Chunk 5)

**Goal**: Expose Gestalt through AGENTESE paths.

**AGENTESE Paths**:
```
world.codebase.manifest                    # Full architecture
world.codebase.module[name=X].manifest     # Specific module
world.codebase.drift.witness               # Drift history
world.codebase.layer[name=X].manifest      # Layer view
self.memory.cartography                    # HoloMap integration
```

**Files**:
```
impl/claude/protocols/agentese/resolvers/gestalt.py
impl/claude/protocols/agentese/handlers/codebase.py
```

**Example Usage**:
```python
# Get architecture view based on observer
arch = await logos.invoke("world.codebase.manifest", architect_umwelt)
# Returns: full graph with layer suggestions

arch = await logos.invoke("world.codebase.manifest", security_umwelt)
# Returns: graph highlighting auth flows and data paths

# Get specific module
module = await logos.invoke("world.codebase.module[name=payments].manifest", umwelt)

# Witness drift over time
history = await logos.invoke("world.codebase.drift.witness", umwelt)
```

**Exit Criteria**:
- All paths resolve correctly
- Observer-dependent affordances work
- Integration with existing Logos
- 30+ tests
- Governance path tested against suppression/policy cases

### Phase 6: VR Projection (Chunk 6 - Future)

**Goal**: 3D codebase exploration (deferred until core is stable).

**Concept**:
```
Module → Building
  - Height = cyclomatic complexity
  - Width = lines of code
  - Color = health grade (green→red)

Dependency → Bridge/Road
  - Thickness = coupling strength
  - Color = declared (green) vs undeclared (red)

Layer → District/Zone
  - Grouping of buildings
  - Elevation = layer level (api high, infra low)
```

**Tech Stack Options**:
- Three.js for web VR
- Unity for native VR
- A-Frame for quick prototype

**Exit Criteria**: TBD when Phase 5 complete

---

## Cross-Synergies

### With Reactive Substrate

Gestalt IS a reactive substrate application:

```python
# Gestalt uses exact same primitives as other widgets
class GestaltWidget(KgentsWidget[ArchitectureGraph]):
    """Architecture visualization as a kgents widget."""

    state: Signal[ArchitectureGraph]

    def project(self, target: RenderTarget) -> Any:
        match target:
            case RenderTarget.CLI:
                return self._render_ascii()
            case RenderTarget.WEB:
                return self._render_json()  # React consumes
            case RenderTarget.MARIMO:
                return self._render_anywidget()
            case RenderTarget.VR:
                return self._render_threejs()
```

### With M-gent Memory

Gestalt leverages holographic memory:

```python
# Architecture IS a HoloMap
from agents.m import CartographerAgent, HoloMap

cartographer = CartographerAgent()
holomap = await cartographer.map_territory(codebase_path)

# HoloMap provides:
# - Semantic routing (find modules by concept)
# - Compression (store efficiently)
# - Reconstruction (any piece can rebuild relations)
```

### With Agent Town

Modules AS citizens:

```python
# Each module can be treated as a Town citizen
# - Has personality (eigenvector from metrics)
# - Forms coalitions (layers, feature groups)
# - Interacts with neighbors (dependencies)

module_citizen = Citizen(
    name="payments",
    eigenvector=ModuleEigenvector(
        coupling=0.45,
        cohesion=0.78,
        complexity=0.32,
        ...
    ),
    phase=CitizenPhase.ACTIVE,
)

# Layers are coalitions detected via k-clique
layer_coalition = detect_k_clique_communities(dependency_graph, k=3)
```

### With Other Developer Tools (from brainstorm)

| Tool | Synergy with Gestalt |
|------|----------------------|
| **Prism** (Code Review) | Gestalt highlights which modules touched in PR, shows coupling impact |
| **Pheromone** (Docs) | Documentation trails inform which modules need more explanation |
| **Morphism** (Tests) | Gestalt metrics identify undertested modules, Morphism generates tests |
| **Hive** (Debug) | Gestalt dependency graph guides debug agent investigation paths |
| **Licensing/Billing** | Tier gates history depth + targets (CLI-only vs Web/VR), monetization enforcement |
| **Tenancy** | Multi-repo + org isolation with RLS context; usage metering via OpenMeter hooks |

---

## Revenue Model

### Pricing Tiers

| Tier | Price | Limits | Features |
|------|-------|--------|----------|
| **Free** | $0 | 1 repo, CLI only | Basic health, no history |
| **Pro** | $29/mo | 5 repos | Web dashboard, 30-day history, drift alerts |
| **Team** | $79/mo | 20 repos | Multi-user, Slack integration, ADR export |
| **Enterprise** | $199/seat | Unlimited | Self-hosted, SSO, VR mode, audit logs |

### Market Opportunity

From research:
- Observability market: $1.8B+ in 2025, growing double digits
- Code intelligence tools: ~23% YoY (analyst consensus)
- Architecture drift / governance: validated by CodeScene, ArchGuard, CodeSee adoption; few reactive offerings

### Competitive Differentiation

| Competitor | Gap Gestalt Fills |
|------------|-------------------|
| **Graphviz/PlantUML** | Static, manual, rot immediately |
| **CodeScene** | Analysis-focused, not real-time visualization |
| **Sourcegraph** | Search-focused, not architecture-aware |
| **Mermaid in docs** | Manual maintenance, no live connection |
| **IDE diagrams** | IDE-bound, not shareable |
| **Structurizr** | Architecture-as-code but not reactive; no drift governance or multi-target projections |
| **CodeSee Maps** | Great maps, lacks governance, holographic storage, VR/CLI parity |

---

## Success Metrics

| Metric | Phase 1-2 | Phase 3-4 | Phase 5+ |
|--------|-----------|-----------|----------|
| Test count | 80+ | 170+ | 250+ |
| Module analysis | Python only | Multi-language | All major |
| Update latency | <5s | <2s | <500ms |
| CLI commands | 3 | 6 | 10 |
| Web features | None | Dashboard | Full |
| User adoption | Internal | Beta | GA |
| Drift false positives | <10% | <5% | <2% |
| NRR | n/a | 105% | 120% |
| Usage coverage | n/a | 3+ internal repos | 10+ design partners |

---

## Risks and Mitigations

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Multi-language complexity | High | High | Start Python-only, add languages incrementally |
| Large codebase performance | Medium | High | Incremental analysis, caching, lazy loading |
| False positive drift | Medium | Medium | Allow suppressions, learn from user feedback |
| VR adoption low | High | Low | VR is stretch goal, core value is CLI+Web |
| Competition from IDE vendors | Medium | Medium | Focus on collaboration and sharing, not IDE-bound |
| Visualization noise | Medium | Medium | Provide filtering, focus+fog rendering, layer-level rollups |
| Security/PII in code uploads | Medium | High | Default local-only; if cloud, redact + hash paths; honor tenancy + licensing constraints |

---

## Related Plans

- `plans/reactive-substrate-unification.md` - Gestalt IS a substrate application
- `agents/m/cartography.py` - Holographic mapping foundation
- `agents/town/coalitions.py` - k-clique detection for layer discovery
- `protocols/api/` - REST endpoints pattern
- `brainstorming/developer-tools-on-kgents.md` - Original concept

---

*"The architecture is not a diagram. The architecture is a living graph that breathes with every commit."*
