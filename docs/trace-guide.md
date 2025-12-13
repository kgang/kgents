# Trace Guide: Understanding Code Flow in kgents

> *"The trace is not the path taken, but the structure of all paths possible."*

This guide covers the unified trace architecture in kgents — a hybrid static+runtime tracing system for understanding code flow, debugging, and performance analysis.

---

## Quick Start

```bash
# Trace who calls a function (static analysis)
kg trace FluxAgent.start

# Trace what a function calls
kg trace FluxAgent.start --callees

# Trace with runtime execution
kg trace --runtime "kg soul challenge 'test'"

# View as flame graph
kg trace StaticCallGraph.analyze --flame

# Export for external tools
kg trace agents/flux --deps --export graph.dot
```

---

## Overview

The trace system has three layers:

```
┌─────────────────────────────────────────────────────────────┐
│                    kgents trace Architecture                 │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│   ┌──────────────┐    ┌──────────────┐    ┌──────────────┐  │
│   │  Static AST  │───▶│ TraceMonoid  │───▶│  Visualizer  │  │
│   │   Analyzer   │    │   (Runtime)  │    │  (Terminal)  │  │
│   └──────────────┘    └──────────────┘    └──────────────┘  │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

| Layer | Purpose | Speed | Accuracy |
|-------|---------|-------|----------|
| **Static** | AST-based call graph | Fast (~4s for 2500 files) | Misses dynamic dispatch |
| **Runtime** | Actual execution trace | Slower | 100% accurate |
| **Hybrid** | Both combined | Medium | Best of both |

---

## CLI Usage

### Basic Syntax

```bash
kg trace <target> [options]
```

### Targets

| Target Type | Example | Description |
|-------------|---------|-------------|
| Function | `FluxAgent.start` | Trace specific function |
| Class | `StaticCallGraph` | Trace all methods |
| Module | `agents/flux` | Module dependencies |
| Pattern | `"*Agent.invoke"` | Glob pattern match |

### Modes

```bash
# Static analysis (default) - no execution
kg trace SoulState.challenge

# Runtime - actually execute and trace
kg trace --runtime "kg soul manifest"

# Hybrid - static + runtime correlation
kg trace --hybrid "kg soul challenge 'test'"
```

### Visualization Options

```bash
# Tree view (default) - hierarchical call tree
kg trace FluxAgent.start --tree

# Graph view - node-edge call graph
kg trace FluxAgent.start --graph

# Timeline - temporal view with concurrency
kg trace --runtime --timeline "kg soul challenge"

# Flame graph - horizontal depth bars
kg trace --runtime --flame "kg a run prompt.txt"

# Diff - compare two traces
kg trace --diff before.trace after.trace
```

### Direction

```bash
# Who calls this? (default)
kg trace FluxAgent.start

# What does this call?
kg trace FluxAgent.start --callees

# Both directions
kg trace FluxAgent.start --depth 3 --callees
```

### Export

```bash
# JSON format
kg trace FluxAgent.start --export trace.json

# DOT format (for Graphviz)
kg trace agents/flux --deps --export graph.dot

# Then visualize with Graphviz
dot -Tpng graph.dot -o graph.png
```

---

## Static Analysis

Static analysis parses Python source without executing it. Fast and safe.

### How It Works

1. **AST Parsing** — Walk all `.py` files
2. **Definition Tracking** — Record classes, functions, methods
3. **Call Site Detection** — Find all function calls
4. **Graph Building** — Build caller → callee relationships

### Example Output

```
kg trace StaticCallGraph.analyze
```

```
StaticCallGraph.analyze
├── CallVisitor.__init__
│   └── ast.NodeVisitor.__init__
├── CallVisitor.visit
│   ├── ast.walk
│   └── CallVisitor.visit_Call
│       ├── CallVisitor._resolve_callee
│       │   └── CallVisitor._get_qualified_name
│       └── CallSite.__init__
└── DependencyGraph.add
    └── DependencyGraph._ensure_node
```

### Ghost Calls

Dynamic dispatch can't be statically resolved. These appear as "ghost" calls:

```
FluxAgent.start
├── RunLoop.cycle
│   └── ○ [ghost] ErrorHandler.handle (if exception)
└── ○ [ghost] __call__ via self.handler
```

Show/hide ghosts:

```bash
kg trace FluxAgent.start --show-ghosts
kg trace FluxAgent.start --no-ghosts
```

---

## Runtime Tracing

Runtime tracing hooks into Python's execution to capture actual call flow.

### How It Works

1. **sys.settrace** — Python's trace hook
2. **Event Capture** — Function call/return events
3. **TraceMonoid** — Events stored in Mazurkiewicz trace structure
4. **Concurrency Detection** — Thread ID enables parallel event detection

### Example

```bash
kg trace --runtime "kg soul challenge 'singleton'"
```

```
[Thread-1] 10:32:45.123
├── cmd_soul (0.5ms)
│   ├── SoulState.challenge (0.3ms)
│   │   ├── Gatekeeper.should_reject (0.1ms)
│   │   │   └── PatternStore.match (0.05ms)
│   │   └── return: REJECT
│   └── print_result (0.1ms)
└── return: 0
```

### Filtering

Reduce noise by filtering what gets traced:

```bash
# Only trace specific modules
kg trace --runtime --include "agents/*" "kg soul"

# Exclude stdlib
kg trace --runtime --exclude "importlib" "kg soul"

# Max depth
kg trace --runtime --max-depth 5 "kg soul"
```

---

## Visualization Modes

### Tree (Default)

Best for: Understanding call hierarchy

```
FluxAgent.start
├── RunLoop.__init__
│   └── Queue.__init__
├── RunLoop.run
│   ├── Queue.get
│   └── Handler.handle
└── RunLoop.stop
```

### Graph

Best for: Seeing all connections at once

```
    ┌─────────────────┐
    │  FluxAgent.start │
    └────────┬────────┘
             │
    ┌────────┴────────┐
    ▼                 ▼
┌──────────┐    ┌──────────┐
│ RunLoop  │───▶│  Queue   │
└──────────┘    └──────────┘
    │
    ▼
┌──────────┐
│ Handler  │
└──────────┘
```

### Timeline

Best for: Concurrent execution, latency analysis

```
Thread-1          Thread-2          Thread-3
────────          ────────          ────────
│                 │                 │
├─ start          │                 │
│  │              │                 │
│  └─ init ───────┼─ spawn ─────────┼─ spawn
│                 │  │              │  │
│                 │  └─ work        │  └─ work
│                 │     │           │     │
├─ join ──────────┼─────┴───────────┼─────┘
│                 │                 │
└─ stop           │                 │
```

### Flame Graph

Best for: Performance profiling, finding hot paths

```
|████████████████████████████████████████████████████| start (100%)
|████████████████████████████████████| init (75%)
|████████████████████████| work (50%)
|████████| process (20%)
```

### Diff

Best for: Comparing behavior between versions

```
kg trace --diff v1.trace v2.trace
```

```
  FluxAgent.start
  ├── RunLoop.__init__
+ │   └── MetricsCollector.__init__  [ADDED]
  ├── RunLoop.run
- │   ├── OldHandler.handle          [REMOVED]
+ │   ├── NewHandler.handle          [ADDED]
  │   └── Queue.get
  └── RunLoop.stop
```

---

## AGENTESE Integration

Access trace functionality programmatically via AGENTESE paths.

### Available Paths

| Path | Purpose |
|------|---------|
| `time.trace.analyze` | Static call graph analysis |
| `time.trace.collect` | Runtime trace collection config |
| `time.trace.render` | ASCII visualization |
| `time.trace.diff` | Compare two traces |

### Examples

```python
from protocols.agentese.logos import create_logos

logos = create_logos()

# Static analysis
result = await logos.invoke(
    "time.trace.analyze",
    umwelt,
    target="FluxAgent.start",
    depth=3,
    direction="callers"
)

# Render as tree
output = await logos.invoke(
    "time.trace.render",
    umwelt,
    mode="tree",
    target="FluxAgent.start"
)
print(output)
```

---

## Programmatic API

### TraceDataProvider (Singleton)

For dashboard and integration use:

```python
from agents.i.data.trace_provider import get_trace_provider

provider = get_trace_provider()

# Analyze codebase (cached)
provider.analyze_static()

# Get callers of a function
callers = provider.get_callers("FluxAgent.start")

# Build call tree
tree = provider.build_call_tree(
    "FluxAgent.start",
    depth=3,
    direction="callers"
)
print(tree.render())

# Collect unified metrics
metrics = await provider.collect_metrics()
print(f"Files: {metrics.static.files_analyzed}")
print(f"Definitions: {metrics.static.definitions_found}")
```

### StaticCallGraph

For direct static analysis:

```python
from weave.static_trace import StaticCallGraph

graph = StaticCallGraph()
graph.analyze("impl/claude/**/*.py")

# Trace callers
callers = graph.trace_callers("FluxAgent.start", depth=5)

# Trace callees
callees = graph.trace_callees("FluxAgent.start", depth=5)

# Get ghost calls
ghosts = graph.get_ghost_calls("FluxAgent.start")
```

### TraceCollector

For runtime tracing:

```python
from weave.runtime_trace import TraceCollector

collector = TraceCollector()

# Context manager API
with collector.trace() as monoid:
    # Your code here
    result = some_function()

# Analyze the trace
print(f"Events: {len(monoid.events)}")
print(f"Max depth: {monoid.max_depth}")

# Check concurrency
if monoid.are_concurrent(event_a, event_b):
    print("These ran in parallel")
```

### TraceRenderer

For visualization:

```python
from weave.trace_renderer import TraceRenderer, RenderConfig

renderer = TraceRenderer(RenderConfig(
    max_width=80,
    show_ghosts=True,
    truncate_names=True
))

# Render static graph
output = renderer.render_call_graph(dependency_graph, layout="tree")

# Render runtime trace
output = renderer.render_timeline(trace_monoid)

# Render flame graph
output = renderer.render_flame(trace_monoid)

# Diff two traces
output = renderer.render_diff(before_monoid, after_monoid)
```

---

## Dashboard Integration

The dashboard shows trace analysis in the **CALL GRAPH** panel:

```bash
kg dashboard --demo
```

```
┌─────────────────────────────────────────────────────────────┐
│ CALL GRAPH                                                   │
├─────────────────────────────────────────────────────────────┤
│ ├─ 2,582 files │ 42,189 defs │ 133,421 calls               │
│ ├─ Hot Functions:                                            │
│ │  ├─ TraceRenderer.__init__ (1655)                         │
│ │  ├─ CallVisitor.__init__ (1655)                           │
│ │  └─ StaticCallGraph.__init__ (1655)                       │
│ └─ (no call trees)                                          │
└─────────────────────────────────────────────────────────────┘
```

The Ghost daemon also projects trace data to `.kgents/ghost/trace_summary.json`.

---

## Performance Tips

### Static Analysis

- First run analyzes ~2500 files in ~4 seconds
- Results are cached in `TraceDataProvider`
- Force re-analysis with `provider.analyze_static(force=True)`

### Runtime Tracing

- Use `--include` to limit scope
- Use `--max-depth` to reduce overhead
- Tracing adds ~10% latency

### Large Codebases

```bash
# Limit to specific directory
kg trace agents/k --deps

# Use shallow depth
kg trace FluxAgent.start --depth 2

# Export and analyze offline
kg trace --export full.json
```

---

## Troubleshooting

### "No calls found"

The target might not exist or might be dynamically dispatched:

```bash
# Check exact name
kg trace --list "Flux*"

# Try with ghosts
kg trace FluxAgent --show-ghosts
```

### "Too much output"

Reduce scope:

```bash
kg trace Target --depth 2 --no-ghosts
```

### "Slow analysis"

Check if cache is working:

```python
from agents.i.data.trace_provider import get_trace_provider
provider = get_trace_provider()
print(f"Cached: {provider._static_graph is not None}")
```

---

## See Also

- `plans/devex/trace.md` — Full implementation plan
- `weave/static_trace.py` — Static analysis source
- `weave/runtime_trace.py` — Runtime tracing source
- `weave/trace_renderer.py` — Visualization source
- `protocols/cli/handlers/trace.py` — CLI handler

---

*"Every path is a trace. Every trace reveals the topology."*
