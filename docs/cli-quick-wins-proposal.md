# CLI Quick Wins: Simple Ideas to Leverage kgents Today

**Status**: Proposal | **Author**: Claude Code | **Date**: 2025-12-10

This document proposes simple, high-impact CLI features that can be implemented quickly to help start leveraging the existing kgents system.

---

## Philosophy

These ideas follow a simple principle: **connect what exists**.

The kgents codebase already has:
- ~6,122 tests passing
- Bicameral Memory with Active Inference (Synapse, Hippocampus, Lucid Dreaming)
- CortexDashboard with health monitoring
- Semantic Field with cross-agent pheromone signaling
- M-gent Cartography (HoloMap, Pathfinder, ContextInjector)
- 10 intent verbs (`new`, `run`, `check`, `think`, `watch`, `find`, `fix`, `speak`, `judge`, `do`)
- Prism auto-CLI generation from agent methods

What's missing: **easy entry points** to experience these capabilities.

---

## Tier 1: Weekend Projects (1-2 hours each)

### 1. `kgents status` - System Health at a Glance

**What**: One command to show cortex health, memory stats, and recent activity.

**Why**: The CortexDashboard exists (`agents/w/cortex_dashboard.py`) but isn't wired to CLI.

**Implementation**:
```python
# protocols/cli/handlers/status.py
async def cmd_status(args):
    """Show system health: cortex, synapse, hippocampus."""
    dashboard = create_cortex_dashboard(observer=cortex_observer)
    print(dashboard.render_compact())
    # → [CORTEX] ✓ COHERENT | L:45ms R:12ms | H:45/100 | S:0.3 | Dreams:12
```

**Effort**: ~50 lines | Wire existing CortexDashboard to CLI
**Value**: Instant visibility into system health

---

### 2. `kgents dream` - Morning Briefing Interface

**What**: Surface the LucidDreamer's morning briefing—questions accumulated overnight.

**Why**: LucidDreamer (`instance_db/dreamer.py`) generates questions during maintenance but has no CLI exposure.

**Implementation**:
```bash
kgents dream              # Show morning briefing questions
kgents dream answer Q1    # Answer a question interactively
kgents dream cycle        # Trigger a REM cycle manually
```

**Effort**: ~80 lines | Expose existing dreamer.py APIs
**Value**: Human-in-the-loop for system evolution

---

### 3. `kgents map` - Context Cartography Visualization

**What**: ASCII render of M-gent's HoloMap showing memory landmarks and desire lines.

**Why**: MapRenderer exists (`agents/m/cartography_integrations.py`) but isn't CLI-accessible.

**Implementation**:
```bash
kgents map                   # Show current context map
kgents map --focus="agents"  # Center on topic
kgents map --voids           # Highlight unexplored regions
```

**Effort**: ~60 lines | Wire MapRenderer.render_ascii() to CLI
**Value**: Spatial awareness of codebase topology

---

### 4. `kgents signal` - Emit/Sense Semantic Field Pheromones

**What**: Interactive interface to the Semantic Field—emit signals, observe field state.

**Why**: SemanticField (`agents/i/semantic_field.py`) enables decoupled coordination but has no direct CLI access.

**Implementation**:
```bash
kgents signal sense                    # Show field summary
kgents signal emit WARNING "Budget low" --position="domain:economy"
kgents signal capabilities             # List advertised capabilities
```

**Effort**: ~100 lines | Expose SemanticField emitter/sensor APIs
**Value**: Direct interaction with agent coordination layer

---

### 5. `kgents metrics` - Prometheus/JSON Export

**What**: Export CortexObserver metrics in standard formats.

**Why**: MetricsExporter exists (`agents/o/metrics_export.py`) with Prometheus/OTEL/JSON support.

**Implementation**:
```bash
kgents metrics                 # JSON to stdout
kgents metrics --prometheus    # Prometheus format
kgents metrics --serve :9090   # Start metrics server
```

**Effort**: ~40 lines | Expose existing exporters
**Value**: Standard observability integration

---

## Tier 2: Week Projects (4-8 hours each)

### 6. `kgents evolve` - Interactive K-gent Prior Evolution

**What**: Teach K-gent your preferences through interactive dialogue.

**Why**: K-gent has PersonaSeed and evolution logic but no CLI for iterative training.

**Implementation**:
```bash
kgents evolve                           # Start evolution dialogue
kgents evolve --prior="naming_style"    # Focus on specific prior
kgents evolve --show                    # Display current priors
```

**Dialogue flow**:
```
K-gent: I suggested "CompostBin" for memory decay. Was this tasteful?
You: Yes, I prefer biological metaphors
K-gent: Updated naming_style prior (confidence: 0.85 → 0.92)
```

**Effort**: ~150 lines | Interactive TUI over K-gent evolution APIs
**Value**: Personalization functor becomes usable

---

### 7. `kgents replay` - Session Replay from N-gent Crystals

**What**: Replay past sessions from N-gent narrative crystals.

**Why**: N-gent stores session traces but there's no way to browse history.

**Implementation**:
```bash
kgents replay                        # List recent sessions
kgents replay 2025-01-15-devex       # Replay specific session
kgents replay --search="CompostBin"  # Find sessions mentioning topic
```

**Effort**: ~200 lines | N-gent crystal browser + timeline renderer
**Value**: Session continuity, institutional memory

---

### 8. `kgents contradict` - Find Spec/Impl Tensions

**What**: Surface contradictions between specs and implementations.

**Why**: Contradict morphism exists (`bootstrap/contradict.py`) but isn't CLI-exposed.

**Implementation**:
```bash
kgents contradict spec/agents/b.md impl/agents/b/
kgents contradict --auto-detect  # Scan for all contradictions
```

**Output**:
```
TENSION: B-gent spec mentions "fiscal sovereignty" but impl lacks FiscalConstitution
  → spec/agents/b.md:47
  → impl/agents/b/__init__.py (missing)
  Suggestion: Implement FiscalConstitution or update spec
```

**Effort**: ~180 lines | Wire contradict.py + diff heuristics
**Value**: Spec-first development becomes enforceable

---

### 9. `kgents compose` - Interactive Agent Composition

**What**: Compose agents interactively with type-guided suggestions.

**Why**: C-gent functor composition exists but requires code to use.

**Implementation**:
```bash
kgents compose
# Interactive:
# > Start with: P-gent (parser)
# > Compose with: [G-gent, T-gent, J-gent] (type-compatible)
# > Select: G-gent
# > Pipeline: P-gent >> G-gent
# > Test: "parse and reify calendar commands"
# > Save as: calendar-pipeline.flow.yaml
```

**Effort**: ~250 lines | TUI over C-gent composition APIs
**Value**: Category theory composition becomes accessible

---

### 10. `kgents void` - Detect Knowledge Gaps

**What**: Surface semantic voids—areas where documentation or tests are missing.

**Why**: Membrane CLI detects SemanticVoids but isn't integrated with actionable tooling.

**Implementation**:
```bash
kgents void              # Detect and list voids
kgents void --suggest    # Generate suggestions for each void
kgents void name "We never test error paths"  # Name a void (Membrane gesture)
```

**Effort**: ~120 lines | Membrane void detection + suggestions
**Value**: Proactive gap analysis

---

## Tier 3: Stretch Goals (Multi-day efforts)

### 11. `kgents pair` - DevEx Coordinator Mode

**What**: Full DevEx loop with K-gent, N-gent, O-gent, I-gent coordination.

**References**: `docs/devex-bootstrap-plan.md` Phase 5

**Implementation**: DevExCoordinator that orchestrates all four agents for development assistance.

---

### 12. `kgents autopilot` - Autonomous Improvement Suggestions

**What**: System watches development patterns and suggests improvements.

**References**: O-gent DevExObserver + semantic drift detection

**Implementation**: Background observer that accumulates evidence and proposes interventions.

---

### 13. `kgents forge` - LLM-Backed Agent Generation

**What**: Generate new agents from natural language descriptions.

**References**: F-gent `llm_generation.py` (prototype exists)

**Implementation**: Wire F-gent LLM generation to CLI with proper guardrails.

---

## Recommended Starting Points

Based on effort/value ratio, start with these three:

| Priority | Command | Why |
|----------|---------|-----|
| 1 | `kgents status` | Immediate visibility, minimal effort |
| 2 | `kgents dream` | Human-in-the-loop for neurogenesis |
| 3 | `kgents map` | Spatial awareness, already implemented |

These three commands would take ~4 hours total and provide:
- System health visibility
- Interactive maintenance participation
- Spatial codebase understanding

---

## Implementation Pattern

All commands follow the Hollow Shell pattern:

```python
# 1. Add to COMMAND_REGISTRY in hollow.py
"status": "protocols.cli.handlers.status:cmd_status",

# 2. Create handler in protocols/cli/handlers/
def cmd_status(args: list[str]) -> int:
    # Parse args
    # Bootstrap lifecycle if needed
    # Call existing agent APIs
    # Format output (rich or json)
    return 0
```

No new agent code required—just CLI glue over existing capabilities.

---

## What This Enables

With these CLI commands, the kgents development workflow becomes:

```bash
# Morning: Check system health
kgents status
kgents dream  # Review overnight questions

# Working: Navigate and understand
kgents map --focus="current task"
kgents find "related concepts"

# Reflecting: Teach the system
kgents evolve  # Update K-gent priors
kgents signal emit NARRATIVE "Completed Phase 1"

# Evening: Let the system consolidate
kgents dream cycle  # Trigger maintenance
```

The system becomes a **cognitive partner** rather than passive infrastructure.

---

## Next Steps

1. Review this proposal and prioritize
2. Pick 1-3 commands from Tier 1 to implement first
3. Wire them to CLI and test
4. Iterate based on usage patterns

---

*"The best interface is one where the system's capabilities are discoverable through use."*
