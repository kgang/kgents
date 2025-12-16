# Gestalt Sprint 3: History & Polish (90% → 100%)

## Context
- **Sprint 1 Complete**: SSE streaming backend + `useGestaltStream` hook
- **Sprint 2 Complete**: Observer umwelts + Drift synergy (43 new tests)
- **Sprint 3.1 Complete**: 🌿 Forest Theme transformation
- **Tests**: 189 passing
- **Goal**: Health trends + Semantic zoom + Animations → 100%

## What We Have

### Infrastructure (Sprints 1-2)
```
protocols/gestalt/
├── analysis.py      # Static analysis engine
├── governance.py    # Drift rules, suppression
├── reactive.py      # GestaltStore (Signals + Computed)
├── handler.py       # CLI handler
├── umwelt.py        # ✨ NEW: Observer roles (6 umwelts)
└── _tests/
    ├── test_analysis.py      # 30 tests
    ├── test_governance.py    # 24 tests
    ├── test_handler.py       # 43 tests
    ├── test_reactive.py      # 49 tests
    └── test_umwelt.py        # ✨ NEW: 28 tests

protocols/api/gestalt.py     # REST + SSE (role param added)
protocols/synergy/handlers/
└── gestalt_brain.py         # ✨ NEW: Drift capture to Brain

web/src/pages/Gestalt.tsx    # 3D vis, elastic layout, observer wiring
```

### Sprint 3.1: Forest Theme (Complete)

> *"The codebase is a forest, not a machine. Each module is a plant.
>  Dependencies are roots reaching for water. Health is growth. Violations are thorns."*

**New Components:**
```
web/src/components/gestalt/
├── OrganicNode.tsx    # 🌿 Plant-like module visualization
├── VineEdge.tsx       # 🌿 Organic curved connections with flow
└── index.ts           # Updated exports

web/src/constants/
└── forest.ts          # 🌿 Forest theme color palette & config
```

**What Changed:**
- ✅ **OrganicNode**: Spheres → living plant bulbs with:
  - Central glowing core (health-colored)
  - Growth rings (tree ring aesthetic, size = LOC)
  - Subtle breathing animation (alive, not static)
  - Health-based forest color palette

- ✅ **VineEdge**: Straight lines → organic vines with:
  - Bezier curves (not straight lines!)
  - **Visible** thickness (1.5px normal, 2.5px active)
  - Glowing highlights when selected
  - Flow particles for active connections
  - Thorns on violations

- ✅ **FilterPanel**: Added "🌿 Forest Mode" toggle
- ✅ **Forest Palette**: Rich greens, browns, and organic colors

**Design Philosophy Applied:**
- From `docs/creative/emergence-principles.md`:
  - "We do not design the flower—we design the soil and the season"
  - Cymatics-inspired flow patterns
  - Growth as emergence visualization
- From Kent's wishes in `_focus.md`:
  - Pixar-like storytelling
  - Daring, bold, creative, opinionated but not gaudy

### Current Capabilities
- ✅ Static analysis (Python + TS)
- ✅ Health grades (A+ to F)
- ✅ Drift detection & suppression
- ✅ SSE streaming (poll-based)
- ✅ Observer-dependent views (6 roles)
- ✅ Drift → Brain synergy
- ✅ 3D visualization (elastic, responsive)
- ✅ 🌿 Forest Theme (organic nodes + vine edges)

---

## Sprint 3 Tasks

### 1. Health History Persistence
**Why**: Single point-in-time is useful; trends are actionable.

```python
# protocols/gestalt/history.py
@dataclass
class HealthSnapshot:
    """Point-in-time health capture."""
    timestamp: datetime
    module_count: int
    overall_grade: str
    average_health: float
    drift_count: int
    grade_distribution: dict[str, int]

class HealthHistory:
    """Persisted health snapshots for trend analysis."""

    def __init__(self, storage_path: Path):
        self._storage = storage_path / ".gestalt-history.json"

    def record(self, graph: ArchitectureGraph) -> HealthSnapshot:
        """Record current health state."""
        ...

    def get_trend(self, days: int = 30) -> list[HealthSnapshot]:
        """Get health trend over time."""
        ...

    def get_delta(self, since: datetime) -> HealthDelta:
        """Compare current to historical state."""
        ...
```

**Deliverables**:
- [ ] `HealthSnapshot` dataclass
- [ ] `HealthHistory` persistence class
- [ ] Auto-record on scan
- [ ] JSON file storage (`.gestalt-history.json`)
- [ ] 8 tests

### 2. History API Endpoint
**Why**: Web dashboard needs trend data.

```python
# protocols/api/gestalt.py

class HistoryResponse(BaseModel):
    """Health history response."""
    snapshots: list[HealthSnapshotResponse]
    trend: str  # "improving", "stable", "degrading"
    delta: HealthDeltaResponse | None

@router.get("/history", response_model=HistoryResponse)
async def get_history(
    days: int = Query(30, ge=1, le=365),
) -> HistoryResponse:
    """Get health history for trend analysis."""
    ...
```

**Deliverables**:
- [ ] `GET /v1/world/codebase/history?days=30`
- [ ] Trend calculation ("improving", "stable", "degrading")
- [ ] Delta from first snapshot
- [ ] 5 tests

### 3. Sparkline Component
**Why**: Visual trends at a glance.

```tsx
// web/src/components/gestalt/Sparkline.tsx

interface SparklineProps {
  data: number[];           // Health scores over time
  trend: 'up' | 'down' | 'stable';
  width?: number;
  height?: number;
  color?: string;
}

export function Sparkline({ data, trend, width = 120, height = 32 }: SparklineProps) {
  // SVG path from data points
  // Trend indicator (▲/▼/─)
  // Tooltip on hover with date/value
}

// Usage in Gestalt.tsx header:
<div className="flex items-center gap-2">
  <span>Health Trend</span>
  <Sparkline data={history.map(h => h.average_health)} trend={trend} />
  <TrendBadge trend={trend} />
</div>
```

**Deliverables**:
- [ ] `Sparkline` component (SVG-based)
- [ ] `TrendBadge` component (▲ improving, ▼ degrading, ─ stable)
- [ ] Integration in Gestalt.tsx header
- [ ] `useHealthHistory` hook
- [ ] 4 tests (component + hook)

### 4. Semantic Zoom (C4 Levels)
**Why**: Navigate from 10,000ft to code level.

```
ZOOM LEVELS:

Level 1: SYSTEM
┌─────────────────────────────────────────┐
│  ┌─────────┐    ┌─────────┐            │
│  │ Agents  │───▶│Protocols│            │
│  └─────────┘    └─────────┘            │
│       │              │                  │
│       ▼              ▼                  │
│  ┌─────────┐    ┌─────────┐            │
│  │   Web   │◀───│   API   │            │
│  └─────────┘    └─────────┘            │
└─────────────────────────────────────────┘

Level 2: CONTAINER (click Agents)
┌─────────────────────────────────────────┐
│ AGENTS                                   │
│  ┌────┐ ┌────┐ ┌────┐ ┌────┐ ┌────┐    │
│  │ M  │ │ D  │ │ K  │ │ T  │ │Town│    │
│  └────┘ └────┘ └────┘ └────┘ └────┘    │
│     Memory  Data  Soul  Test  Sim       │
└─────────────────────────────────────────┘

Level 3: COMPONENT (click M)
┌─────────────────────────────────────────┐
│ agents.m                                 │
│  ● memory.py (A+)                       │
│  ● associative.py (A)                   │
│  ● consolidation_engine.py (B+)         │
│  ● substrate.py (B)                     │
│  ─────────────────────                  │
│  Dependencies: 4 | Dependents: 12       │
└─────────────────────────────────────────┘

Level 4: CODE (click memory.py)
┌─────────────────────────────────────────┐
│ agents.m.memory                          │
│ ─────────────────────                   │
│ class Memory:                            │
│     """Core memory interface."""         │
│     async def store(self, ...):          │
│     async def recall(self, ...):         │
│     async def forget(self, ...):         │
└─────────────────────────────────────────┘
```

**Implementation**:

```tsx
// web/src/components/gestalt/SemanticZoom.tsx

type ZoomLevel = 'system' | 'container' | 'component' | 'code';

interface SemanticZoomProps {
  topology: CodebaseTopologyResponse;
  level: ZoomLevel;
  focusPath?: string;  // e.g., "agents.m"
  onLevelChange: (level: ZoomLevel) => void;
  onFocusChange: (path: string) => void;
}

// Aggregation logic
function aggregateToSystem(topology: CodebaseTopologyResponse): SystemView {
  // Group modules by top-level: agents, protocols, web, infra
  // Sum health, count modules, aggregate edges
}

function aggregateToContainer(topology: CodebaseTopologyResponse, focus: string): ContainerView {
  // Filter to focus path children
  // e.g., focus="agents" → show agents.m, agents.d, agents.k, etc.
}
```

**Deliverables**:
- [ ] `ZoomLevel` type and state
- [ ] `aggregateToSystem()` function
- [ ] `aggregateToContainer()` function
- [ ] Zoom level selector UI (breadcrumb style)
- [ ] Click-to-zoom-in on nodes
- [ ] Breadcrumb navigation (← back)
- [ ] Smooth zoom transitions (Framer Motion)
- [ ] 8 tests

### 5. Graph Update Animations
**Why**: Smooth transitions feel alive.

```tsx
// Framer Motion integration

// Node enter/exit
<motion.group
  initial={{ scale: 0, opacity: 0 }}
  animate={{ scale: 1, opacity: 1 }}
  exit={{ scale: 0, opacity: 0 }}
  transition={{ type: "spring", stiffness: 300, damping: 25 }}
>
  <ModuleNode ... />
</motion.group>

// Health change glow
const healthChanged = prevHealth !== node.health_score;
<mesh>
  <meshStandardMaterial
    emissive={healthChanged ? pulseColor : undefined}
    emissiveIntensity={healthChanged ? pulse : 0}
  />
</mesh>

// Edge flow animation (already exists, enhance)
const activeEdges = useActiveEdges(selectedNodeId);
// Pulse animation on active edges
```

**Deliverables**:
- [ ] Node enter/exit animations
- [ ] Health change pulse effect
- [ ] Zoom transition animations
- [ ] 3 tests (animation states)

### 6. Performance Benchmarks
**Why**: Prove it's fast.

```python
# protocols/gestalt/_tests/test_performance.py

@pytest.mark.benchmark
class TestGestaltPerformance:
    """Performance benchmarks for Gestalt operations."""

    def test_cold_scan_under_5s(self, large_codebase):
        """Initial scan completes in <5s for 500 modules."""
        start = time.monotonic()
        graph = build_architecture_graph(large_codebase)
        elapsed = time.monotonic() - start
        assert elapsed < 5.0

    def test_incremental_update_under_500ms(self, gestalt_store):
        """Single file change updates in <500ms."""
        ...

    def test_topology_response_under_200ms(self, api_client):
        """API response time for topology endpoint."""
        ...
```

**Deliverables**:
- [ ] `test_performance.py` with 3 benchmarks
- [ ] CI integration (pytest-benchmark)
- [ ] Document baseline metrics

---

## Files to Create/Modify

| File | Action | Purpose |
|------|--------|---------|
| `protocols/gestalt/history.py` | Create | Health snapshot persistence |
| `protocols/gestalt/_tests/test_history.py` | Create | History tests |
| `protocols/gestalt/_tests/test_performance.py` | Create | Benchmark tests |
| `protocols/api/gestalt.py` | Modify | Add /history endpoint |
| `web/src/components/gestalt/Sparkline.tsx` | Create | Trend visualization |
| `web/src/components/gestalt/TrendBadge.tsx` | Create | Trend indicator |
| `web/src/components/gestalt/SemanticZoom.tsx` | Create | Zoom level logic |
| `web/src/components/gestalt/ZoomBreadcrumb.tsx` | Create | Navigation |
| `web/src/hooks/useHealthHistory.ts` | Create | History data hook |
| `web/src/pages/Gestalt.tsx` | Modify | Integrate all new features |

---

## Success Criteria

### Functional
- [ ] Health history persists across sessions
- [ ] Sparkline shows 30-day trend in header
- [ ] 4 zoom levels work (System → Container → Component → Code)
- [ ] Click-to-zoom navigation feels natural
- [ ] Graph updates animate smoothly

### Performance
- [ ] Cold scan: <5s for 500 modules
- [ ] Incremental update: <500ms
- [ ] API response: <200ms

### Test Coverage
- [ ] 25+ new tests (target: 214 total)
- [ ] All benchmarks pass

### Documentation
- [ ] `docs/skills/gestalt-analysis.md` updated
- [ ] Performance baselines documented

---

## Definition of Done (100%)

When Sprint 3 is complete, Gestalt will have:

1. **History**: Health trends over time, persisted and visualized
2. **Semantic Zoom**: Navigate from system overview to code detail
3. **Animations**: Smooth, living graph updates
4. **Performance**: Proven fast with benchmarks
5. **Tests**: 214+ passing (currently 189)

The Hero Path (Brain + Gestalt + Gardener) will be **100% complete**.

---

## Quick Start

```bash
# Terminal 1: Run tests
cd impl/claude
uv run pytest protocols/gestalt/ -v

# Terminal 2: Run API
uv run uvicorn protocols.api.app:create_app --factory --reload --port 8000

# Terminal 3: Run Web
cd impl/claude/web
npm run dev

# Check current test count
uv run pytest protocols/gestalt/ protocols/synergy/_tests/test_drift_handler.py -q --collect-only | tail -5
```

---

## Task Execution Order

1. **History persistence** (backend foundation)
2. **History API endpoint** (expose to frontend)
3. **Sparkline + TrendBadge** (quick visual win)
4. **Semantic Zoom** (biggest feature)
5. **Animations** (polish)
6. **Performance benchmarks** (prove it works)

---

*Sprint 2 completed: 2025-12-16*
*Sprint 3 target: Hero Path 100%*
