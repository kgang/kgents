---
path: devex/trace-integration
status: planned
progress: 0
last_touched: 2025-12-13
touched_by: claude-opus-4.5
blocking: []
enables: [devex/debugger, devex/profiler]
depends_on: [devex/trace]
session_notes: |
  Initial brainstorm for trace integration into dashboard and CLI.
  devex/trace is now 100% complete with 211 tests.

  Key insight: Trace data has THREE uses:
  1. Diagnostic: Understanding execution flow (CLI trace command)
  2. Observability: Live monitoring (Dashboard TRACES panel)
  3. Analysis: Pattern recognition (Ghost, Flinch integration)
---

# Trace Integration Plan: Dashboard & CLI

> *"Make execution visible at every level of detail."*

**Status**: Planned (depends on devex/trace which is COMPLETE)
**Principles**: Glass Terminal (visibility), Heterarchical (multiple views)
**Cross-refs**: devex/trace, devex/dashboard, devex/ghost

---

## Integration Opportunities

### 1. Dashboard Enhancement: LIVE TRACE Panel

**Current state**: Dashboard has a "RECENT TRACES" panel showing AGENTESE path invocations.

**Opportunity**: Enhance with call-graph visualization from our new trace stack.

```
┌─────────────────────────────────────────────────────────────────┐
│ RECENT TRACES (enhanced)                                         │
├─────────────────────────────────────────────────────────────────┤
│  ├─ self.soul.challenge ("singleton")                 [23ms]    │
│  │   └─ K-gent.challenge_singleton                              │
│  │       └─ GateKeeper.evaluate                                 │
│  ├─ world.cortex.invoke (gpt-4) → success            [1.2s]     │
│  │   └─ LLM.call                                                │
│  │       └─ [ghost] error_handler (if exception)                │
│  └─ void.entropy.tithe (0.1) → discharged             [1ms]     │
├─────────────────────────────────────────────────────────────────┤
│  [t] Toggle call-tree  [f] Show flame  [d] Focus trace          │
└─────────────────────────────────────────────────────────────────┘
```

**Implementation**:
- Add `TraceCollector` integration to dashboard metric collectors
- Show nested call trees for each AGENTESE invocation
- Keybinding `t` to toggle between flat list and call tree
- Keybinding `f` to show flame graph for selected trace

**Files**:
- `agents/i/data/dashboard_collectors.py` - Add trace collection
- `agents/i/screens/dashboard.py` - Enhanced TracesPanel
- `agents/i/widgets/trace_tree.py` - New widget for inline traces

**Tests**: 15 new tests
**LOC**: ~200

---

### 2. Dashboard New Panel: CALL GRAPH Panel

**Opportunity**: Add a dedicated panel for live call graph analysis.

```
┌─────────────────────────────────────────────────────────────────┐
│ CALL GRAPH (focus: FluxAgent.start)                      [5]    │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  FluxAgent.start                                                 │
│  ├─● RunLoop.cycle (3 calls in last 5s)                         │
│  │   ├─● EventProcessor.process                                 │
│  │   │   └─● SourceAdapter.poll                                 │
│  │   └─○ [ghost] ErrorHandler.handle                            │
│  └─● MetricEmitter.emit                                         │
│                                                                  │
│  Legend: ● active  ○ ghost  ━ hot path                          │
├─────────────────────────────────────────────────────────────────┤
│  [/] Set focus  [depth +-]  [g] Toggle ghosts                   │
└─────────────────────────────────────────────────────────────────┘
```

**Implementation**:
- New panel type: `CallGraphPanel`
- Tracks focus target and renders call graph in real-time
- Shows "hot paths" with higher activity
- Ghost calls toggleable

**Files**:
- `agents/i/screens/dashboard.py` - Add CallGraphPanel
- `agents/i/widgets/call_graph.py` - Inline call graph widget

**Tests**: 10 new tests
**LOC**: ~150

---

### 3. Ghost Integration: trace_summary.json

**Current state**: Ghost projects system state to `.kgents/ghost/`

**Opportunity**: Add trace analysis to ghost projection.

```
.kgents/ghost/
├── thought_stream.md
├── tension_map.json
├── health.status
├── context.json
├── flinch_summary.json
└── trace_summary.json   # NEW
```

**trace_summary.json contents**:
```json
{
  "last_updated": "2025-12-13T10:23:45Z",
  "static_analysis": {
    "files_analyzed": 512,
    "definitions": 2847,
    "hottest_functions": [
      {"name": "FluxAgent.process", "callers": 47},
      {"name": "TraceMonoid.append_mut", "callers": 32}
    ]
  },
  "recent_runtime": {
    "total_events": 1234,
    "avg_depth": 4.2,
    "hottest_paths": [
      "FluxAgent.start -> RunLoop.cycle -> process",
      "logos.invoke -> SoulNode._challenge"
    ]
  },
  "anomalies": [
    "Recursive call detected: _resolve -> _resolve (5 levels)"
  ]
}
```

**Implementation**:
- Add trace collector to ghost daemon
- Generate summary every projection cycle (3 min)
- Track anomalies (deep recursion, circular calls)

**Files**:
- `protocols/cli/handlers/ghost.py` - Add trace projection
- `infra/ghost/trace_collector.py` - NEW: Ghost-specific collector

**Tests**: 10 new tests
**LOC**: ~100

---

### 4. Flinch Integration: Failure Call Traces

**Current state**: Flinch captures test failures but not call context.

**Opportunity**: Correlate failures with call traces for root cause analysis.

```
$ kgents flinch --traces
[FLINCH] Test Failure Analysis with Call Traces

test_flux_agent.py::test_process_event (5 failures)
├─ Last failure: 2h ago
├─ Call trace at failure:
│   FluxAgent.process
│   └─ EventProcessor.validate
│       └─ SchemaValidator.check  <-- EXCEPTION HERE
│           └─ raise ValidationError
├─ Probable root cause: SchemaValidator.check
└─ Related failures: test_schema_validation (same path)
```

**Implementation**:
- Capture call stack at test failure time
- Store simplified trace in flinch record
- Correlate traces across failures to find patterns

**Files**:
- `protocols/cli/handlers/flinch.py` - Add --traces mode
- `infra/ghost/flinch_store.py` - Store call traces

**Tests**: 8 new tests
**LOC**: ~80

---

### 5. Status Integration: Trace Health

**Current state**: `kgents status` shows cortex health.

**Opportunity**: Include trace health metrics.

```
$ kgents status
[CORTEX] OK HEALTHY | instance:a8f3b2 | agents:5 | branch:main dirty:3
[TRACE] analyzed:512 files | depth:4.2 avg | ghosts:12 | 0 anomalies
```

```
$ kgents status --full
...
TRACE HEALTH
├─ Static: 512 files, 2847 definitions analyzed
├─ Runtime: 1234 events captured (last 5 min)
├─ Avg depth: 4.2 calls
├─ Ghost calls: 12 detected
└─ Anomalies: 0
```

**Implementation**:
- Add trace health metrics to status output
- Cache analysis results for fast status check
- Highlight anomalies

**Files**:
- `protocols/cli/handlers/status.py` - Add trace section

**Tests**: 5 new tests
**LOC**: ~50

---

### 6. Cockpit Integration: Agent Trace View

**Current state**: Cockpit shows per-agent operational view.

**Opportunity**: Add trace lens for specific agent's execution.

```
┌─────────────────────────────────────────────────────────────────┐
│ COCKPIT: FluxAgent                                               │
├─────────────────────────────────────────────────────────────────┤
│ METRICS                    │ TRACE (last 30s)                   │
│ ├─ Temperature: 0.72       │ start ──┬── cycle ──── process     │
│ ├─ Events/sec: 2.5         │         ├── cycle ──┬─ process     │
│ └─ Queue: 7 pending        │         │           └─ emit        │
│                            │         └── cycle ──── process     │
│ SEMAPHORES                 │                                     │
│ └─ (none active)           │ [Flame: ████████░░ 83%]            │
└─────────────────────────────────────────────────────────────────┘
```

**Implementation**:
- Add trace panel to cockpit screen
- Filter traces by agent using `--lens` parameter
- Show mini flame graph for agent activity

**Files**:
- `agents/i/screens/cockpit.py` - Add trace panel

**Tests**: 8 new tests
**LOC**: ~100

---

### 7. MRI Screen: Deep Trace Analysis

**Current state**: MRI shows deep agent internals.

**Opportunity**: Add full trace visualization as MRI mode.

```
$ kgents dashboard --mri --trace FluxAgent

┌─────────────────────────────────────────────────────────────────┐
│ MRI: FluxAgent (TRACE MODE)                                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  STATIC CALL GRAPH (callers, depth=3)                           │
│  ═══════════════════════════════════                            │
│  FluxAgent.start                                                 │
│  ├─● cmd_a (CLI entry)                                          │
│  │   └─● _run_agent                                             │
│  ├─● TestFluxAgent.test_start                                   │
│  └─● DaemonLoop.spawn                                           │
│                                                                  │
│  RUNTIME FLAME GRAPH (last 60s)                                 │
│  ═════════════════════════════                                  │
│  ████████████████████████████████ start (100%)                  │
│  ██████████████████████ cycle (67%)                             │
│  ████████████ process (37%)                                     │
│  ████ emit (12%)                                                │
│                                                                  │
│  GHOST CALLS                                                    │
│  ═══════════                                                    │
│  ○ ErrorHandler.handle (if exception in process)                │
│  ○ CircuitBreaker.trip (if 3+ failures)                         │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

**Implementation**:
- Add TRACE mode to MRI screen
- Combine static + runtime visualization
- Show ghost calls as hypothetical paths

**Files**:
- `agents/i/screens/mri.py` - Add trace mode

**Tests**: 12 new tests
**LOC**: ~200

---

### 8. Play Integration: Trace Tutorials

**Current state**: `kgents play` is an interactive playground with tutorials.

**Opportunity**: Add trace tutorials and interactive trace exploration.

```
$ kgents play trace

╔═══════════════════════════════════════════════════════════════╗
║  TRACE PLAYGROUND                                             ║
╠═══════════════════════════════════════════════════════════════╣
║                                                               ║
║  Welcome to trace exploration!                                ║
║                                                               ║
║  TUTORIALS:                                                   ║
║  [1] Static Analysis 101 - Finding who calls what             ║
║  [2] Runtime Tracing - Watching execution live                ║
║  [3] Ghost Calls - Understanding dynamic dispatch             ║
║  [4] Performance Hunting - Finding hot paths                  ║
║                                                               ║
║  SANDBOX:                                                     ║
║  [s] Start trace sandbox (trace your own code)                ║
║                                                               ║
║  Or try: trace self.soul.challenge                            ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
```

**Implementation**:
- Add trace module to play command
- Interactive trace visualization
- Self-guided tutorials

**Files**:
- `protocols/cli/handlers/play.py` - Add trace mode

**Tests**: 6 new tests
**LOC**: ~150

---

## Priority Matrix

| Integration | Impact | Effort | Priority |
|-------------|--------|--------|----------|
| Dashboard TRACES enhancement | High | Medium | P1 |
| Ghost trace_summary.json | High | Low | P1 |
| Status trace health | Medium | Low | P1 |
| Flinch failure traces | High | Medium | P2 |
| Dashboard CALL GRAPH panel | Medium | Medium | P2 |
| Cockpit agent trace | Medium | Medium | P3 |
| MRI trace mode | Medium | High | P3 |
| Play trace tutorials | Low | Medium | P4 |

---

## Implementation Order

### Phase 1: Foundation (P1 items)

1. **Ghost trace_summary.json** (~100 LOC, 10 tests)
   - Easiest integration
   - Provides data for other integrations
   - Enables peripheral awareness

2. **Status trace health** (~50 LOC, 5 tests)
   - Quick win
   - Uses ghost data
   - Validates integration pattern

3. **Dashboard TRACES enhancement** (~200 LOC, 15 tests)
   - High visibility
   - Core dashboard improvement
   - Most user impact

### Phase 2: Analysis (P2 items)

4. **Flinch failure traces** (~80 LOC, 8 tests)
   - Critical for debugging
   - Correlates trace + test data
   - Trust loop enhancement

5. **Dashboard CALL GRAPH panel** (~150 LOC, 10 tests)
   - New capability
   - Live call graph
   - Power user feature

### Phase 3: Deep Integration (P3-P4 items)

6. **Cockpit agent trace** (~100 LOC, 8 tests)
7. **MRI trace mode** (~200 LOC, 12 tests)
8. **Play trace tutorials** (~150 LOC, 6 tests)

---

## Data Flow Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        TRACE DATA FLOW                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐       │
│  │ StaticCall   │    │ TraceCollec  │    │ TraceRender  │       │
│  │    Graph     │───▶│    tor       │───▶│    er        │       │
│  └──────────────┘    └──────────────┘    └──────────────┘       │
│         │                   │                   │                │
│         │                   │                   │                │
│         ▼                   ▼                   ▼                │
│  ┌──────────────────────────────────────────────────────┐       │
│  │              TraceDataProvider (NEW)                  │       │
│  │  - Caches static analysis                            │       │
│  │  - Collects runtime traces                           │       │
│  │  - Provides unified API for consumers                │       │
│  └──────────────────────────────────────────────────────┘       │
│         │                   │                   │                │
│         ▼                   ▼                   ▼                │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐   │
│  │Dashboard │    │  Ghost   │    │  Status  │    │  Flinch  │   │
│  │  Panel   │    │Collector │    │ Handler  │    │Analyzer  │   │
│  └──────────┘    └──────────┘    └──────────┘    └──────────┘   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

**TraceDataProvider** (new shared component):
- Singleton that manages trace data across CLI
- Caches static analysis (expensive to compute)
- Provides lightweight runtime trace summaries
- Used by dashboard, ghost, status, flinch

**Files**: `agents/i/data/trace_provider.py` (~100 LOC)

---

## Success Metrics

| Metric | Target |
|--------|--------|
| Dashboard TRACES shows call depth | Nested 3+ levels |
| Ghost projects trace summary | Every 3 min cycle |
| Status shows trace health | In `--full` mode |
| Flinch correlates failures | >50% have trace |
| New tests | 74+ total |
| Total new LOC | ~1000 |

---

## Dependencies

**From devex/trace** (all available):
- `StaticCallGraph` - Call graph analysis
- `TraceCollector` - Runtime tracing
- `TraceRenderer` - ASCII visualization
- `time.trace.*` - AGENTESE paths

**From existing infrastructure**:
- `DashboardMetrics` - Metric collection framework
- `GhostWriter` - Filesystem projection
- `FlinchStore` - Test failure storage
- `GlassClient` - Three-layer fallback

---

## Risk Assessment

| Risk | Mitigation |
|------|------------|
| Performance: Static analysis is slow | Cache in TraceDataProvider, run async |
| Complexity: Too many trace panels | Progressive disclosure, default off |
| Data volume: Runtime traces grow | Circular buffer, summary only |
| UX: Information overload | Clear visual hierarchy, collapsible |

---

## Open Questions

1. **Dashboard panel arrangement**: Add new CALL GRAPH panel or replace existing TRACES?
2. **Ghost update frequency**: Match 3-min cycle or more frequent for traces?
3. **Flinch trace storage**: Full trace or summary only (storage concern)?
4. **MRI vs dedicated trace screen**: New screen or mode of existing?

---

*"Every line of code has a story. Trace integration tells that story at the right level of detail for each context."*
