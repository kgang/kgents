# Gestalt Continuation: 80% → 100%

> *"Architecture diagrams rot the moment they're drawn. Gestalt never rots because it never stops watching."*

## Context

**Plan**: `plans/core-apps/gestalt-architecture-visualizer.md`
**Current Progress**: 90% (Sprint 2 complete)
**Test Count**: 189 (analysis 30 + governance 24 + handler 43 + reactive 49 + umwelt 28 + drift 15)
**Hero Path**: Gestalt is Tier 1 (Brain 100% + Gestalt 90% + Gardener 100%)

**Sprint 3 Continuation**: See `plans/_continuations/gestalt-sprint3.md`

---

## What's Done (70%)

| Phase | Status | Key Deliverables |
|-------|--------|------------------|
| **1. Core Analysis** | ✅ | Python + TS parsing, ModuleHealth, ArchitectureGraph, drift detection |
| **2. Reactive Substrate** | ✅ | GestaltStore with Signals, file watcher, incremental updates |
| **3. CLI Projection** | ✅ | manifest/health/drift/module/scan/watch, OTEL spans, 43 tests |
| **4. Web Dashboard** | ✅ | 3D graph, elastic layout, health coloring, detail panel |
| **5. AGENTESE v3** | 🔶 | 10 paths registered, handlers wired, but NO subscriptions |
| **6. VR Projection** | ❌ | Future (post-100%) |

### Built Infrastructure
- `protocols/gestalt/analysis.py` - Static analysis engine
- `protocols/gestalt/governance.py` - Drift rules, suppression
- `protocols/gestalt/reactive.py` - GestaltStore (Signals + Computed)
- `protocols/gestalt/analyzer.py` - Language-agnostic Analyzer[T] protocol
- `protocols/api/gestalt.py` - REST endpoints (6 routes)
- `web/src/pages/Gestalt.tsx` - 3D visualization (elastic, responsive)
- `protocols/cli/handlers/gestalt.py` - CLI handler with OTEL

---

## Gap Analysis (30% Remaining)

### Priority 1: Live Architecture (SSE Streaming)
**Why**: The "watch" mode works in CLI but web is poll-based. Live updates are the differentiator.

```python
# NOT YET IMPLEMENTED:
# GET /v1/world/codebase/stream -> SSE endpoint
# - Emits ArchitectureUpdate events on file changes
# - Web subscribes via EventSource
# - Graph updates smoothly (no full refresh)
```

**Tasks**:
1. Add SSE endpoint to `protocols/api/gestalt.py`
2. Wire file watcher events through FastAPI background task
3. Add `useEventSource` hook to web client
4. Animate graph updates (nodes fade in/out, edges morph)

### Priority 2: Observer-Dependent Perception
**Why**: This is THE AGENTESE principle. Different roles should see different views.

```python
# SPEC'd BUT NOT IMPLEMENTED:
await logos("world.codebase.manifest", security_umwelt)
# → SecurityView(vulnerable_deps, access_paths, attack_surface)

await logos("world.codebase.manifest", performance_umwelt)
# → PerformanceView(hot_modules, coupling_bottlenecks, complexity_spikes)
```

**Tasks**:
1. Define `Umwelt` types for Security/Performance/Product/TechLead roles
2. Add `?role=` query param to `/v1/world/codebase/manifest`
3. Transform response based on role (filter, reweight metrics)
4. Add role selector dropdown to web UI
5. Tests verifying different outputs for different roles

### Priority 3: Health History & Trends
**Why**: Single point-in-time is useful; trends are actionable.

**Tasks**:
1. Add `HealthSnapshot` with timestamp to GestaltStore
2. Persist snapshots (JSON file or SQLite) on scan
3. Add `/v1/world/codebase/history` endpoint
4. Add sparkline component to web dashboard
5. CLI: `kg world codebase history --days 30`

### Priority 4: Semantic Zoom (C4 Levels)
**Why**: Spec describes 4 zoom levels but web only shows one.

| Zoom Level | What's Visible |
|------------|----------------|
| System | Agents as boxes, no internals |
| Container | Agent internals, contexts |
| Component | Nodes, affordances listed |
| Code | Handler code snippets |

**Tasks**:
1. Add `zoomLevel: 'system' | 'container' | 'component' | 'code'` state
2. Filter graph data based on zoom level
3. Add zoom level selector to UI
4. Animate transitions between levels

### Priority 5: Brain Synergy (Cross-Jewel)
**Why**: Gestalt insights should auto-capture to Brain.

```python
# Pattern from Crown Jewels:
@on_event("gestalt.drift_detected")
async def capture_drift_to_brain(event: DriftEvent):
    await logos("self.memory.capture", {
        "content": f"Drift: {event.violation}",
        "metadata": {"jewel": "gestalt", "type": "drift"}
    })
```

**Tasks**:
1. Create `GestaltToBrainHandler` in synergy handlers
2. Emit synergy events on drift detection, health degradation
3. Add Brain context enrichment for architecture queries
4. Tests verifying synergy capture

---

## Sprint Plan

### Sprint 1: Live Foundation (→ 80%) ✅ COMPLETE
**Focus**: SSE streaming + subscription patterns

- [x] Add SSE endpoint `/v1/world/codebase/stream`
- [x] Background task for file watcher → SSE events (poll-based, 5s default)
- [x] `useGestaltStream` hook in web client
- [ ] Graph update animations (GSAP or Framer Motion) - FUTURE
- [x] Tests: 146 total (54+ new from data-architecture cleanup)
- [x] Fixed broken imports from data-architecture-rewrite

**Success Criteria**: ✅ Backend SSE endpoint + Frontend hook ready

**Session 2025-12-16 Notes**:
- Added `GET /v1/world/codebase/stream` SSE endpoint with poll_interval param
- Created `useGestaltStream` hook with auto-reconnection
- Fixed all broken imports from data-architecture-rewrite:
  - `agents/t/spy.py` - simplified to use plain Python list
  - `agents/town/citizen.py` - inline `CitizenMemory` class
  - Removed legacy D-gent imports (volatile, persistent, symbiont, legacy)

### Sprint 2: Perception & Synergy (→ 90%) ✅ COMPLETE
**Focus**: Observer-dependent views + Brain integration

- [x] Define 6 role Umwelts (tech_lead, developer, reviewer, product, security, performance)
- [x] `?role=` query param support on `/topology`
- [x] Role selector wired in web UI (observer → API)
- [x] GestaltToBrainHandler synergy (ANALYSIS_COMPLETE + DRIFT_DETECTED)
- [x] Auto-capture drift events to Brain
- [x] 43 new tests (28 umwelt + 15 drift handler)

**Session 2025-12-16 Notes**:
- Created `protocols/gestalt/umwelt.py` with 6 observer roles
- Added `UmweltConfig` with metric weights and visibility filters
- Updated `/topology` endpoint to accept `?role=` param
- Added `create_drift_detected_event()` factory function
- Extended `GestaltToBrainHandler` to handle DRIFT_DETECTED events
- Wired observer state in Gestalt.tsx to pass role to API
- All 43 new tests passing

**Success Criteria**: ✅ Same codebase, 6 different useful views

### Sprint 3: History & Polish (→ 100%)
**Focus**: Trends + semantic zoom

**See detailed plan**: `plans/_continuations/gestalt-sprint3.md`

- [ ] HealthSnapshot persistence + HealthHistory class
- [ ] `/v1/world/codebase/history` endpoint
- [ ] Sparkline + TrendBadge components
- [ ] Semantic zoom (4 levels: system/container/component/code)
- [ ] Graph update animations (Framer Motion)
- [ ] Performance benchmarks (pytest-benchmark)
- [ ] 25 new tests minimum (target: 214 total)

**Success Criteria**: "Wow moment" - explore architecture at multiple levels, see trends, feel alive

---

## Technical Notes

### SSE Implementation Pattern
```python
# protocols/api/gestalt.py
from sse_starlette.sse import EventSourceResponse

@router.get("/v1/world/codebase/stream")
async def stream_updates():
    async def event_generator():
        store = get_gestalt_store()
        async for event in store.subscribe():
            yield {"event": "update", "data": event.to_json()}
    return EventSourceResponse(event_generator())
```

### Umwelt Pattern
```python
# protocols/gestalt/umwelt.py
class GestaltUmwelt(Enum):
    TECH_LEAD = "tech_lead"      # Health, drift, governance
    SECURITY = "security"        # Vulnerabilities, access paths
    PERFORMANCE = "performance"  # Bottlenecks, complexity
    PRODUCT = "product"          # Features, integration points

def filter_for_umwelt(graph: ArchitectureGraph, umwelt: GestaltUmwelt) -> FilteredView:
    ...
```

### Synergy Pattern
```python
# protocols/synergy/gestalt_brain.py
class GestaltToBrainHandler(SynergyHandler):
    async def on_drift_detected(self, violation: DriftViolation):
        await self.logos("self.memory.capture", {
            "content": violation.suggested_fix,
            "metadata": {"source": "gestalt", "severity": violation.severity}
        })
```

---

## Files to Modify/Create

| File | Action | Purpose |
|------|--------|---------|
| `protocols/api/gestalt.py` | Modify | Add SSE endpoint, role param |
| `protocols/gestalt/umwelt.py` | Create | Observer role definitions |
| `protocols/gestalt/history.py` | Create | Health snapshot persistence |
| `protocols/synergy/gestalt_brain.py` | Create | Brain synergy handler |
| `web/src/hooks/useGestaltStream.ts` | Create | SSE subscription hook |
| `web/src/components/gestalt/Sparkline.tsx` | Create | Trend visualization |
| `web/src/pages/Gestalt.tsx` | Modify | SSE, role selector, zoom levels |
| `docs/skills/codebase-analysis.md` | Modify | Add new features |

---

## Definition of Done (100%)

- [x] SSE streaming works end-to-end (poll-based, 5s default)
- [x] 6 observer roles with meaningfully different views
- [ ] Health history with 30-day trend visualization
- [ ] Semantic zoom (4 levels: System/Container/Component/Code)
- [x] Brain synergy captures drift events
- [x] 189+ tests (Sprint 2 complete)
- [ ] 214+ tests (Sprint 3 target)
- [ ] Performance: <500ms update latency, <5s cold scan
- [ ] `EDUCATE` phase complete (skill doc updated)
- [ ] `MEASURE` phase complete (benchmarks documented)

---

## Session Start Checklist

When resuming work on Gestalt:

1. Read this continuation prompt
2. Check current test count: `uv run pytest protocols/gestalt/ -q --collect-only`
3. Check web builds: `cd impl/claude/web && npm run build`
4. Pick the next unchecked task from Sprint 1/2/3
5. Update `plans/core-apps/gestalt-architecture-visualizer.md` session_notes

---

*Created: 2025-12-16 | Sprint 2 completed: 2025-12-16 | Target: 100% by end of Q1 2025*
