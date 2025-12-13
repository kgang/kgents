---
path: devex/trace
status: complete
progress: 100
last_touched: 2025-12-13
touched_by: claude-opus-4.5
blocking: []
enables: [devex/telemetry, devex/dashboard]
session_notes: |
  ALL PHASES COMPLETE - 211 tests passing

  Phase 1 (StaticCallGraph) COMPLETE:
  - impl/claude/weave/static_trace.py (400+ LOC)
  - 56 tests passing
  - < 5s analysis of 2,545 files (3.79s)
  - Class/function/method definition tracking
  - Call graph with trace_callers/trace_callees
  - Ghost call detection for dynamic dispatch

  Phase 2 (Runtime TraceMonoid Integration) COMPLETE:
  - impl/claude/weave/runtime_trace.py (~500 LOC)
  - 51 tests passing
  - TraceCollector with sys.settrace/sys.setprofile hooks
  - Thread ID as event source (concurrency detection)
  - Call stack creates dependency chain in TraceMonoid
  - Context manager API: with collector.trace(): ...
  - TraceFilter for include/exclude patterns
  - OpenTelemetry integration (optional)
  - are_concurrent() correctly identifies parallel events
  - Can trace soul challenge-like execution patterns

  Phase 3 (ASCII Visualization) COMPLETE:
  - impl/claude/weave/trace_renderer.py (~500 LOC)
  - 37 tests passing
  - TraceRenderer class with 4 render modes:
    - render_call_graph: Tree/force layout for DependencyGraph
    - render_timeline: Concurrent events side-by-side by thread
    - render_flame: Horizontal bars by call depth
    - render_diff: Compare two traces (added/removed/unchanged)
  - Ghost nodes marked with distinct styling
  - Configurable via RenderConfig (width, truncation, etc.)
  - Convenience functions: render_graph, render_trace, render_diff
  - Uses patterns from GraphLayout/BranchTree widgets

  Phase 4 (CLI Handler) COMPLETE:
  - impl/claude/protocols/cli/handlers/trace.py (~500 LOC)
  - 23 tests passing
  - Full CLI: kgents trace <target> [--runtime] [--tree|--graph|--timeline|--flame]
  - Static analysis mode (default)
  - Runtime tracing mode with --runtime
  - Export to JSON/DOT format
  - Registered in hollow.py and appears in kgents --help

  Phase 5 (AGENTESE Integration) COMPLETE:
  - Extended protocols/agentese/contexts/time.py
  - 19 tests passing
  - time.trace.analyze - Static call graph
  - time.trace.collect - Runtime trace config
  - time.trace.render - ASCII visualization
  - time.trace.diff - Compare traces

  Hardening COMPLETE:
  - 25 additional tests for edge cases/resilience
  - Error handling: syntax errors, encoding issues, empty inputs
  - Performance: < 5s for full impl/ analysis verified
  - Edge cases: unicode names, deep recursion, disconnected graphs
  - Integration tests: cross-module, CLI end-to-end
---

# Unified Trace Architecture: `kgents trace`

> *"The trace is not the path taken, but the structure of all paths possible."*

**AGENTESE Context**: `time.trace.*`
**Status**: COMPLETE (211 tests passing)
**Principles**: Composable (5), Generative (7)
**Cross-refs**: devex/telemetry, devex/dashboard, weave/trace_monoid

---

## Core Insight

Transform `kgents trace` from AI-guided grep into a **hybrid static+runtime tracing system** that:

1. **Static Analysis** — AST-based call graph without execution (safe, fast)
2. **Runtime Tracing** — TraceMonoid-backed execution traces (accurate, deep)
3. **ASCII Visualization** — Reuse existing GraphLayout/BranchTree widgets

The mathematical foundation already exists: `TraceMonoid` implements Mazurkiewicz traces where independent events can commute. This is the perfect substrate for concurrent agent traces.

```
┌─────────────────────────────────────────────────────────────┐
│                    kgents trace Architecture                 │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│   ┌──────────────┐    ┌──────────────┐    ┌──────────────┐  │
│   │  Static AST  │───▶│ TraceMonoid  │───▶│  Visualizer  │  │
│   │   Analyzer   │    │   (Runtime)  │    │  (Terminal)  │  │
│   └──────────────┘    └──────────────┘    └──────────────┘  │
│          │                   │                   │          │
│          ▼                   ▼                   ▼          │
│   ┌──────────────┐    ┌──────────────┐    ┌──────────────┐  │
│   │  Call Graph  │    │  Dependency  │    │ GraphLayout  │  │
│   │   (PyCG)     │    │    Graph     │    │ + BranchTree │  │
│   └──────────────┘    └──────────────┘    └──────────────┘  │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## Research Summary

### Static Analysis (Call Graphs)

| Tool | Approach | Notes |
|------|----------|-------|
| [PyCG](https://arxiv.org/pdf/2103.00587) | Assignment Graph on IR | Best accuracy, academic |
| [Pyan3](https://github.com/Technologicat/pyan) | AST + symtable | Open source, Python 3.10+ |
| [Code2graph](https://dl.acm.org/doi/10.1145/3238147.3240484) | AST parsing | Includes similarity analysis |

**Key insight**: Static analysis outperforms LLMs for call graph generation. PyCG works by building an Assignment Graph that tracks identifier bindings across scopes.

### Runtime Instrumentation

| Method | Source | Notes |
|--------|--------|-------|
| `sys.settrace` | [PyMOTW](https://pymotw.com/2/sys/tracing.html) | Function call/return hooks |
| `sys.setprofile` | Python stdlib | Lower overhead than trace |
| DTrace/SystemTap | [Python Docs](https://docs.python.org/3/howto/instrumentation.html) | CPython markers |
| OpenTelemetry | [CNCF Guide](https://www.cncf.io/blog/2022/04/22/opentelemetry-and-python-a-complete-instrumentation-guide/) | Standard spans |

**Key insight**: `sys.settrace` feeds events into TraceMonoid's `append_mut()`. Thread ID becomes the event source, enabling concurrency analysis.

### Terminal Visualization

| Library | Purpose | Notes |
|---------|---------|-------|
| [Rich Tree](https://rich.readthedocs.io/en/stable/tree.html) | Tree rendering | Already using Rich |
| [asciigraf](https://pypi.org/project/asciigraf/) | ASCII → NetworkX | Parse ASCII diagrams |
| GraphLayout widget | 2D node-edge | Already have in I-gent |
| BranchTree widget | Git-style tree | Already have in I-gent |

**Key insight**: Reuse existing widgets. GraphLayout does force-directed/tree/semantic layouts. BranchTree shows "ghost branches" (rejected hypotheses) — perfect for showing dynamic dispatch possibilities.

---

## Implementation Phases

### Phase 1: Static Call Graph (~200 LOC)

**Goal**: AST-based call graph without executing code.

**Files**:
```
impl/claude/weave/
├── static_trace.py          # StaticCallGraph class
└── _tests/
    └── test_static_trace.py
```

**Key Types**:
```python
@dataclass
class CallSite:
    """A location where a call occurs."""
    file: Path
    line: int
    column: int
    caller: str      # Fully qualified name
    callee: str      # Fully qualified name
    is_dynamic: bool # True if inferred (ghost call)

class StaticCallGraph:
    """AST-based call graph for Python."""

    def analyze(self, pattern: str = "**/*.py") -> None: ...
    def trace_callers(self, target: str, depth: int = 5) -> DependencyGraph: ...
    def trace_callees(self, target: str, depth: int = 5) -> DependencyGraph: ...
    def get_ghost_calls(self, target: str) -> list[CallSite]: ...
```

**Exit Criteria**:
- `StaticCallGraph("impl/claude").analyze()` completes < 5s
- `trace_callers("FluxAgent.start")` returns correct DependencyGraph
- 30+ tests passing

---

### Phase 2: Runtime TraceMonoid Integration (~150 LOC)

**Goal**: Instrument execution and feed traces into existing TraceMonoid.

**Files**:
```
impl/claude/weave/
├── runtime_trace.py         # TraceCollector class
└── _tests/
    └── test_runtime_trace.py
```

**Key Types**:
```python
class TraceCollector:
    """Collects runtime traces into a TraceMonoid."""

    def __init__(self):
        self.monoid: TraceMonoid[dict[str, Any]] = TraceMonoid()

    def start(self) -> None:
        """Begin tracing (uses sys.settrace)."""

    def stop(self) -> TraceMonoid[dict[str, Any]]:
        """Stop and return the trace."""

    @contextmanager
    def trace(self) -> Iterator[TraceMonoid]:
        """Context manager for tracing a block."""
```

**Integration with TraceMonoid**:
- Each function call becomes an `Event`
- Thread ID → event source (enables concurrency detection)
- Call stack → dependency chain (child depends on parent)
- `monoid.are_concurrent(a, b)` → detect parallel execution

**Exit Criteria**:
- Can trace `kgents soul challenge` execution
- TraceMonoid correctly identifies concurrent events
- 25+ tests passing

---

### Phase 3: ASCII Visualization (~150 LOC)

**Goal**: Render traces using existing widgets + new TraceRenderer.

**Files**:
```
impl/claude/weave/
├── trace_renderer.py        # TraceRenderer class
└── _tests/
    └── test_trace_renderer.py
```

**Visualization Modes**:

| Mode | Widget | Use Case |
|------|--------|----------|
| `--graph` | GraphLayout | Call graph (force/tree layout) |
| `--tree` | BranchTree | Execution trace with ghosts |
| `--timeline` | Custom | Temporal view with concurrency |
| `--flame` | Custom | Flame graph (horizontal bars) |

**Key Types**:
```python
class TraceRenderer:
    """Renders traces as ASCII art."""

    def render_call_graph(
        self,
        graph: DependencyGraph,
        layout: str = "tree",  # tree | force | semantic
    ) -> str: ...

    def render_timeline(
        self,
        monoid: TraceMonoid,
        lens: str | None = None,  # Agent perspective filter
    ) -> str: ...

    def render_flame(
        self,
        monoid: TraceMonoid,
    ) -> str: ...

    def render_diff(
        self,
        before: TraceMonoid,
        after: TraceMonoid,
    ) -> str: ...
```

**Exit Criteria**:
- All 4 render modes produce valid ASCII
- Integrates with existing GraphLayout widget
- 20+ tests passing

---

### Phase 4: CLI Handler (~100 LOC)

**Goal**: Wire everything into `kgents trace` command.

**Files**:
```
impl/claude/protocols/cli/handlers/
├── trace.py                 # CLI handler
└── _tests/
    └── test_trace.py
```

**CLI Spec**:
```
kgents trace <target> [flags]

MODES:
  (default)         Static call graph analysis
  --runtime         Trace actual execution
  --hybrid          Static + runtime correlation

VISUALIZATION:
  --graph           Node-edge call graph
  --tree            Hierarchical tree (default)
  --timeline        Temporal execution view
  --flame           Flame graph
  --diff FILE       Compare with saved trace

OPTIONS:
  --depth N         Traversal depth (default: 5)
  --show-ghosts     Include dynamic/inferred calls
  --lens AGENT      View from agent's perspective
  --callees         Trace what target calls (vs who calls it)
  --deps            Module dependency graph
  --export FILE     Save trace (JSON or DOT)

EXAMPLES:
  kgents trace FluxAgent.start
  kgents trace --runtime "soul challenge 'test'"
  kgents trace agents/flux --deps --graph
  kgents trace --flame --runtime "a run prompt.txt"
```

**Exit Criteria**:
- `kgents trace FluxAgent.start` works
- `kgents trace --runtime` captures execution
- All visualization modes functional
- 20+ tests passing

---

### Phase 5: AGENTESE Integration (~50 LOC)

**Goal**: Add `time.trace.*` path for programmatic access.

**Files**:
```
impl/claude/protocols/agentese/contexts/
├── time_.py                 # time.trace.* handlers
└── _tests/
    └── test_time.py
```

**AGENTESE Paths**:
```python
time.trace.analyze   # Static call graph
time.trace.collect   # Runtime trace collection
time.trace.render    # ASCII visualization
time.trace.diff      # Compare traces
```

**Exit Criteria**:
- `logos.invoke("time.trace.analyze", umwelt, "FluxAgent.start")` works
- 10+ tests passing

---

## Key Types Summary

```python
# Static analysis
@dataclass
class CallSite:
    file: Path
    line: int
    caller: str
    callee: str
    is_dynamic: bool

class StaticCallGraph:
    def analyze(self, pattern: str) -> None: ...
    def trace_callers(self, target: str, depth: int) -> DependencyGraph: ...

# Runtime
class TraceCollector:
    monoid: TraceMonoid[dict[str, Any]]
    def start(self) -> None: ...
    def stop(self) -> TraceMonoid: ...

# Visualization
class TraceRenderer:
    def render_call_graph(self, graph: DependencyGraph) -> str: ...
    def render_timeline(self, monoid: TraceMonoid) -> str: ...
    def render_flame(self, monoid: TraceMonoid) -> str: ...
    def render_diff(self, before: TraceMonoid, after: TraceMonoid) -> str: ...
```

---

## Cross-References

### Enables (Downstream)

| Plan | How Trace Enables It |
|------|---------------------|
| `devex/telemetry` | TraceCollector → OpenTelemetry spans |
| `devex/dashboard` | RECENT TRACES panel uses TraceRenderer |

### Uses (Upstream)

| Component | Location | Purpose |
|-----------|----------|---------|
| TraceMonoid | `weave/trace_monoid.py` | Mazurkiewicz traces |
| DependencyGraph | `weave/dependency.py` | DAG operations |
| GraphLayout | `agents/i/widgets/graph_layout.py` | 2D ASCII graphs |
| BranchTree | `agents/i/widgets/branch_tree.py` | Git-style trees |

### Related DevEx Plans

| Plan | Relationship |
|------|-------------|
| `devex/telemetry` | Trace export to Jaeger/OTLP |
| `devex/dashboard` | Live trace panel |
| `devex/playground` | Trace demos for tutorials |

---

## Creative Enhancements (Stretch Goals)

### Ghost Calls
Show dynamic dispatch possibilities (like BranchTree's ghost branches):
```
FluxAgent.start
├─● RunLoop.cycle
│ └─○ [ghost] ErrorHandler.handle (if exception)
└─○ [ghost] __call__ via self.handler
```

### Temporal Lensing
View trace from specific agent's perspective using TraceMonoid.project():
```
kgents trace --runtime --lens K-gent "soul challenge"
```

### Semantic Diff
Compare behavioral changes between versions:
```
kgents trace --diff before.trace after.trace
```

---

## Success Criteria

| Criterion | Metric |
|-----------|--------|
| Static analysis speed | < 5s for full impl/ |
| Runtime overhead | < 10% latency |
| Visualization quality | Kent approval |
| Test coverage | 100+ tests |
| Integration | Works with dashboard TRACES panel |

---

## Testing Strategy

| Test Type | Coverage |
|-----------|----------|
| Unit | StaticCallGraph, TraceCollector, TraceRenderer |
| Integration | CLI handler, AGENTESE paths |
| Property | TraceMonoid concurrency invariants |
| Visual | Golden file tests for ASCII output |

---

## Dependencies

**Existing** (no new deps):
- `ast` (stdlib) — Python parsing
- `sys.settrace` (stdlib) — Runtime hooks
- TraceMonoid, DependencyGraph (weave/)
- GraphLayout, BranchTree (agents/i/widgets/)
- Rich (already installed) — Terminal formatting

**Optional** (for enhanced analysis):
- `pycg` — More accurate call graphs (academic quality)

---

## Sources

- [PyCG: Practical Call Graph Generation in Python](https://arxiv.org/pdf/2103.00587)
- [Pyan3 - Static Call Graph Generator](https://github.com/Technologicat/pyan)
- [Python Tracing with sys.settrace](https://pymotw.com/2/sys/tracing.html)
- [Rich Tree Visualization](https://rich.readthedocs.io/en/stable/tree.html)
- [OpenTelemetry Python Guide](https://www.cncf.io/blog/2022/04/22/opentelemetry-and-python-a-complete-instrumentation-guide/)
- [asciigraf - ASCII to NetworkX](https://pypi.org/project/asciigraf/)

---

*"Every path is a trace. Every trace reveals the topology."*
