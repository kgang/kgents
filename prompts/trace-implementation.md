# Continuation Prompt: `kgents trace` Implementation

## Quick Start

```
Implement Phase 1 of plans/devex/trace.md — StaticCallGraph.

Begin with weave/static_trace.py. Use parallel agents for:
1. Research: Latest PyCG techniques, Python 3.13 AST changes
2. Explore: Existing DependencyGraph patterns in weave/dependency.py
3. Implement: StaticCallGraph class with analyze() and trace_callers()

Discretion: If research reveals better approaches (e.g., tree-sitter,
Python's symtable module), adapt the implementation. The plan is a
guide, not a contract.

Exit criteria: 30+ tests, < 5s for full impl/ analysis.
```

## With Parallel Agents

```
Implement plans/devex/trace.md with parallel exploration:

Agent 1 (Research):
  - Search: "Python AST call graph 2025 best practices"
  - Search: "sys.settrace async Python performance"
  - Search: "Mazurkiewicz trace implementation patterns"

Agent 2 (Explore):
  - Read weave/trace_monoid.py, weave/dependency.py
  - Read agents/i/widgets/graph_layout.py, branch_tree.py
  - Understand existing patterns before writing new code

Agent 3 (Implement):
  - After research/explore complete, implement StaticCallGraph
  - Wire into CLI handler at protocols/cli/handlers/trace.py
  - Ensure integration with TraceMonoid for runtime traces

Synthesize findings. Adapt plan based on discoveries.
The TraceMonoid foundation is solid — build on it.
```

## Full Implementation (All 5 Phases)

```
Implement all phases of plans/devex/trace.md:

Phase 1: StaticCallGraph (weave/static_trace.py)
Phase 2: TraceCollector (weave/runtime_trace.py)
Phase 3: TraceRenderer (weave/trace_renderer.py)
Phase 4: CLI Handler (protocols/cli/handlers/trace.py)
Phase 5: AGENTESE time.trace.* (protocols/agentese/contexts/time_.py)

Use discretion:
- Research may reveal better AST parsing (tree-sitter?)
- Runtime tracing may benefit from cProfile over settrace
- Visualization may need new widget patterns

Cross-reference:
- devex/telemetry uses TraceCollector for OpenTelemetry
- devex/dashboard uses TraceRenderer for TRACES panel
- Ensure compatibility with both downstream consumers

Target: 100+ tests, full CLI working, all visualization modes.
```
