# Différance Crown Jewel Wiring

**Season:** SPROUTING
**Parent:** `plans/differance-cultivation.md` (Phase 5 complete)
**Target:** Wire trace recording into Brain, Gardener, and future Crown Jewels
**Status:** Planning → Ready for Implementation
**Updated:** 2025-12-18 (Critical analysis + internet research)

---

## The Vision

> *"The ghost heritage graph is the UI innovation: seeing what almost was alongside what is."*

Phase 5 built the **infrastructure**. Now we make it **live**. Every Brain capture, every Gardener gesture, every Town dialogue turn should leave a trace — not as logging, but as **self-knowledge**. The system remembers not just what it did, but what it almost did.

---

## Ground in Voice

> *"Daring, bold, creative, opinionated but not gaudy"*
> *"The Mirror Test: Does K-gent feel like me on my best day?"*

This isn't observability. It's **introspection made visible**. When you ask "why did this memory crystallize this way?", the answer should emerge from the heritage graph, not from grepping logs.

---

## Critical Analysis of Phase 5 Implementation

### What Worked Well (Keep)

1. **Clean Integration API**: `DifferanceIntegration` class is well-designed — jewel-scoped, async/sync dual-mode, buffer-first approach enables testing without persistence setup.

2. **Contract-First Types**: The 341-line `contracts.py` provides proper BE/FE sync via `@node(contracts={})` — this is the right pattern.

3. **TraceContext scoping**: Context variable approach (`_current_trace_id`) enables automatic parent linking for nested traces without explicit threading.

4. **GhostHeritageGraph component**: Living Earth palette, density-aware, proper responsive handling. The 2D Renaissance aesthetic is correct.

### Critical Gaps to Address

1. **🔴 No actual wiring exists**: The `DifferanceIntegration` is ready but `BrainPersistence` and `GardenerPersistence` don't import or use it. We have tooling, no tool usage.

2. **🟡 Buffer isolation**: Global `_trace_buffer` is module-level mutable state. This creates test pollution across pytest sessions. Need `contextvar` or fixture-based isolation.

3. **🟡 Alternative computation is expensive**: The sketched `_compute_capture_alternatives()` requires knowing context (recent crystals, similar content) that isn't available without extra queries.

4. **🟡 Missing correlation IDs**: Industry best practice for distributed tracing (per Datadog, OpenTelemetry) requires correlation IDs that propagate through request lifecycle. Current `parent_trace_id` is close but not the same.

5. **🔴 No AGENTESE node layer tracing**: The question "service layer vs node layer?" was left open. Answer: **Both, but differently**:
   - **Service layer**: Operation-level traces (what happened)
   - **Node layer**: Request-level traces (how it was invoked)

   This matches the industry pattern: "distributed tracing helps you identify root cause" via request tracing + "event sourcing stores all changes" via operation recording.

---

## Research-Informed Design Decisions

### Decision 1: Correlation ID Integration

Per [AI Observability best practices](https://www.vellum.ai/blog/understanding-your-agents-behavior-in-production):

> *"For reliable agents, you need to capture the full trace of a given execution run: its prompts, retrieved docs, tool invocations, latency, cost."*

**Solution**: Add `correlation_id` field to `WiringTrace` that links to AGENTESE request context. When `@node` handles a request, it sets `_current_correlation_id` via contextvar. All downstream traces inherit this.

```python
# New field in WiringTrace
correlation_id: str | None = None  # Links to AGENTESE request
```

### Decision 2: Traced Operations Taxonomy (Finalized)

Based on [event sourcing + distributed tracing integration research](https://www.sciencedirect.com/science/article/abs/pii/S0164121221001126):

> *"An event log does not have enough information for a complete audit. Adding end-to-end tracing mitigates traceability challenges."*

**Trace everything consequential, nothing trivial:**

| Jewel | Operation | Trace | Decision | Rationale |
|-------|-----------|-------|----------|-----------|
| **Brain** | `capture()` | ✅ | ALWAYS | Memory formation is the core act |
| **Brain** | `search()` | ❌ | NEVER | Read-only, high frequency, trace pollution |
| **Brain** | `surface()` | ✅ | ALWAYS | Serendipity is a decision with ghosts |
| **Brain** | `delete()` | ✅ | ALWAYS | Destruction is irreversible |
| **Gardener** | `record_gesture()` | ✅ | ALWAYS | Every tending shapes the garden |
| **Gardener** | `transition_season()` | ✅ | ALWAYS | State machine transition |
| **Gardener** | `create_plot()` | ✅ | ALWAYS | Structural decision |
| **Town** | `dialogue_turn()` | ✅ | ALWAYS | What almost was said |
| **Atelier** | `submit_bid()` | ✅ | ALWAYS | Economic decision |
| **All** | `get_*()` | ❌ | NEVER | Pure reads don't need traces |
| **All** | `list_*()` | ❌ | NEVER | Queries are not decisions |

**Rule**: If the operation mutates state or involves choice, trace it. If it only reads, don't.

### Decision 3: Alternative Generation Strategy (Hybrid)

The open question was: pre-defined vs computed vs LLM-suggested?

**Answer: Two-tier lazy alternatives**

1. **Tier 1: Static alternatives** (always available, zero cost)
   - Pre-defined per operation type
   - Example: `capture()` → `["auto_tag", "defer_embedding"]`

2. **Tier 2: Dynamic alternatives** (computed on demand)
   - Only populated when user clicks "Why?" in UI
   - Uses `@property` lazy loading
   - Example: "Could have linked to crystal X" (requires similarity query)

This matches the [counterfactual strategies for MDPs pattern](https://www.ijcai.org/proceedings/2025/47):

> *"Given an initial strategy that reaches an outcome, identify minimal changes to reduce probability below limit."*

We defer expensive counterfactual computation until requested.

### Decision 4: UI Placement (Progressive Disclosure)

Per [graph visualization UX research](https://cambridge-intelligence.com/graph-visualization-ux-how-to-avoid-wrecking-your-graph-visualization/):

> *"Effective graph visualization UX determines whether insight is revealed or lost."*

**Three-layer disclosure:**

```
Layer 1: Subtle indicator
┌─────────────────────────────────┐
│ Crystal: "Python is great..."   │
│ captured 2min ago • ⑂ 2 ghosts │  ← Ghost count badge
└─────────────────────────────────┘

Layer 2: Inline "Why?" panel (click badge)
┌─────────────────────────────────┐
│ Why This Memory?                │
│ ├── ✓ capture → crystal_abc    │
│ │   ├── ░ auto_tag [skipped]   │
│ │   └── ░ defer_embed [no]     │
│ └── "Explore full heritage →"  │
└─────────────────────────────────┘

Layer 3: Dedicated /differance page (deep dive)
Full interactive GhostHeritageGraph
```

This is Option C from original plan — **confirmed correct**.

### Decision 5: Performance Budget

Per [observability state of play 2025](https://sapphireventures.com/blog/observability-in-2024-understanding-the-state-of-play-and-future-trends/):

> *"Comprehensive tracing can reduce MTTR by up to 70%."*

But trace recording must not block operations.

**Budget**: < 1ms overhead per trace (not < 5ms as originally stated).

**Implementation**:
1. Trace recording is fire-and-forget (`create_task`)
2. Buffer append is O(1) list append
3. No synchronous I/O during trace recording
4. Async store append can fail silently (graceful degradation)

---

## The Challenge (Updated)

**We have:**
- ✅ `DifferanceIntegration` class ready
- ✅ `record_trace_sync()` for sync code paths
- ✅ `record_trace()` for async code paths
- ✅ Buffer-only mode for testing
- ✅ GhostHeritageGraph React component
- ✅ Contract types for AGENTESE discovery
- ✅ `useDifferanceQuery` hooks (heritage, why, ghosts, replay)

**We need:**
- [ ] Correlation ID propagation from AGENTESE nodes
- [ ] BrainPersistence wired with DifferanceIntegration
- [ ] GardenerPersistence wired with DifferanceIntegration
- [ ] Static alternatives defined per operation
- [ ] Ghost count badge in Crown Jewel UIs
- [ ] Inline "Why?" panel component
- [ ] Test isolation for trace buffer
- [ ] Storybook stories (3 minimum)

---

## Revised Phases

### Phase 6A: Test Infrastructure + Buffer Isolation

**Goal**: Bulletproof testing foundation before wiring.

**Tasks**:
1. Convert `_trace_buffer` to `ContextVar[list[WiringTrace]]`
2. Create `pytest` fixture: `differance_buffer` that resets per test
3. Add correlation ID field to `WiringTrace`
4. Wire `_current_correlation_id` contextvar
5. Test: parallel traces don't interfere

**Exit Criteria**:
- `pytest -n auto` passes without trace cross-pollution
- Correlation IDs propagate through nested traces

**Estimated effort**: 2-3 hours

### Phase 6B: Brain Wiring (Service Layer)

**Goal**: Brain operations record traces.

**Tasks**:
1. Add `self._differance = DifferanceIntegration("brain")` to `BrainPersistence.__init__`
2. Wire `capture()` — truncate content to 100 chars for trace
3. Wire `surface()` — include surfaced crystal ID and alternatives that almost surfaced
4. Wire `delete()` — record what was lost
5. Define static alternatives: `BRAIN_ALTERNATIVES = {"capture": [...], "surface": [...], "delete": [...]}`
6. Add tests: `test_brain_traces_capture`, `test_brain_traces_surface`

**Code location**: `services/brain/persistence.py`

**Exit Criteria**:
- `brain.capture("test")` → buffer contains 1 trace
- `time.differance.heritage(crystal_id)` returns DAG with Brain prefix

### Phase 6C: Gardener Wiring (Service Layer)

**Goal**: Gardener operations record traces.

**Tasks**:
1. Add `self._differance = DifferanceIntegration("gardener")` to `GardenerPersistence.__init__`
2. Wire `plant_idea()` — trace new idea with alternatives (could have used different lifecycle)
3. Wire `nurture_idea()` — trace nurturing with alternative verbs
4. Wire `transition_lifecycle()` — trace state change with alternative transitions
5. Define static alternatives per verb
6. Add tests: `test_gardener_traces_plant`, `test_gardener_traces_nurture`

**Code location**: `services/gardener/persistence.py`

**Exit Criteria**:
- Idea planting → trace with lifecycle alternatives
- `time.differance.why(idea_id)` returns lineage

### Phase 6D: UI Integration — Ghost Badge + Why Panel

**Goal**: Non-invasive heritage visibility in existing UIs.

**Tasks**:
1. Create `GhostBadge` component (shows ghost count, clickable)
2. Create `WhyPanel` component (inline accordion with heritage summary)
3. Add `GhostBadge` to `CrystalCard` in Brain UI
4. Add `GhostBadge` to `IdeaCard` in Gardener UI
5. Wire click → expand WhyPanel
6. Add Storybook stories: `WhyPanel/Empty`, `WhyPanel/WithGhosts`, `GhostBadge/Counts`

**Exit Criteria**:
- Crystal card shows ghost count
- Click → inline heritage panel expands
- Panel has "Explore full heritage →" link

### Phase 6E: Dedicated Differance Page (Optional Depth)

**Goal**: Full heritage exploration for power users.

**Tasks**:
1. Create `/differance` route
2. Search bar: find by output ID or operation
3. Full `GhostHeritageGraph` visualization
4. Filter controls: show/hide ghosts, date range
5. Export: download heritage as JSON

**Exit Criteria**:
- `/differance` page renders
- Can search for any traced output
- Export works

---

## Implementation Patterns (From Research)

### Pattern: Correlation ID Propagation

Per [Datadog best practices](https://www.datadoghq.com/blog/monitor-event-driven-architectures/):

> *"Embed a standardized specification into all events: source, type, date, correlation ID."*

```python
# protocols/agentese/gateway.py

_current_correlation_id: ContextVar[str | None] = ContextVar("correlation_id", default=None)

async def invoke(self, path: str, observer: Observer, **kwargs) -> Any:
    correlation_id = f"req_{uuid4().hex[:12]}"
    token = _current_correlation_id.set(correlation_id)
    try:
        # ... invoke node ...
    finally:
        _current_correlation_id.reset(token)
```

### Pattern: Static Alternative Registry

```python
# agents/differance/alternatives.py

BRAIN_ALTERNATIVES = {
    "capture": [
        Alternative("auto_tag", (), "Could auto-generate tags from content"),
        Alternative("defer_embedding", (), "Could skip embedding until search"),
    ],
    "surface": [
        Alternative("different_seed", (), "Different entropy seed → different memory"),
    ],
    "delete": [
        Alternative("archive_instead", (), "Could archive rather than delete"),
    ],
}

GARDENER_ALTERNATIVES = {
    "plant": [
        Alternative("different_lifecycle", ("seed",), "Could start as seed instead"),
    ],
    "nurture": [
        Alternative("prune", (), "Could prune instead of nurture"),
        Alternative("water", (), "Could water instead"),
    ],
    "transition": [
        Alternative("stay", (), "Could remain in current state"),
    ],
}

def get_alternatives(jewel: str, operation: str) -> list[Alternative]:
    """Get static alternatives for operation."""
    registry = {
        "brain": BRAIN_ALTERNATIVES,
        "gardener": GARDENER_ALTERNATIVES,
    }
    return registry.get(jewel, {}).get(operation, [])
```

### Pattern: Fire-and-Forget Recording

```python
# Integration call site (non-blocking)

async def capture(self, content: str, ...) -> CaptureResult:
    result = await self._do_capture(content, ...)

    # Fire-and-forget — don't await, don't block
    asyncio.create_task(
        self._differance.record(
            operation="capture",
            inputs=(content[:100],),
            output=result.crystal_id,
            context=f"[brain] Captured {result.source_type}",
            alternatives=get_alternatives("brain", "capture"),
        )
    )

    return result
```

---

## Open Questions (Resolved)

| Question | Resolution |
|----------|------------|
| Service layer vs node layer? | **Both**: Service = operations, Node = requests |
| Alternative generation strategy? | **Two-tier**: Static always, dynamic on-demand |
| UI placement? | **Progressive disclosure**: Badge → Panel → Page |
| Performance budget? | **< 1ms** (fire-and-forget, async) |
| Trace granularity? | **Operation-level** (not turn-level) |

## Open Questions (Remaining)

1. **Privacy/multi-tenant**: How do traces interact with AUP tenant isolation?
   - Proposed: Traces inherit tenant_id from correlation context

2. **Compression**: When does holographic compression kick in?
   - Proposed: > 1000 traces triggers summarization via M-gent

3. **Cross-jewel correlation**: How do we link Brain trace to Gardener trace from same request?
   - Proposed: Shared `correlation_id` enables join

---

## Success Metrics (Updated)

- [ ] Brain `capture()` records trace with < 1ms overhead
- [ ] Gardener `plant_idea()` records trace with alternatives
- [ ] `time.differance.heritage(id)` returns real data from Brain/Gardener
- [ ] Ghost badge appears on crystal cards (shows count)
- [ ] Click ghost badge → inline WhyPanel expands
- [ ] Storybook has 3+ stories (WhyPanel, GhostBadge, GhostHeritageGraph)
- [ ] `pytest -n auto` passes (no trace pollution)
- [ ] No mypy errors in modified files

---

## Anti-Patterns to Avoid (Expanded)

| Anti-Pattern | Why It's Bad | What To Do Instead |
|--------------|--------------|-------------------|
| **Trace pollution** | Tracing reads creates noise | Only trace mutations |
| **Alternative explosion** | > 3 alternatives overwhelms | Static registry, max 3 |
| **Blocking trace recording** | Slows user operations | Fire-and-forget async |
| **Coupling to persistence** | Can't test without store | Buffer-first, store optional |
| **UI clutter** | Heritage everywhere distracts | Progressive disclosure |
| **Correlation ID absence** | Can't join cross-jewel traces | Always propagate from request |

---

## Theoretical Foundation (Research Summary)

### Traced Monoidal Categories

From [Joyal, Street, Verity (1996)](https://www.cambridge.org/core/journals/mathematical-proceedings-of-the-cambridge-philosophical-society/article/abs/traced-monoidal-categories/2BE85628D269D9FABAB41B6364E117C8):

> *"A traced monoidal category has a trace operator that creates feedback loops while preserving composition laws."*

Our `TraceMonoid` implements this: traces compose associatively, empty trace is identity.

### Polynomial Functors + Wiring Diagrams

From [Spivak & Niu (2024)](https://arxiv.org/abs/2312.00990):

> *"Mode-dependent dynamical systems can be naturally recast within the category Poly of polynomial functors."*

Our traces record the **wiring decisions** between polynomial agents — which positions were active, which directions taken.

### Counterfactual Reasoning in MDPs

From [IJCAI 2025](https://www.ijcai.org/proceedings/2025/47):

> *"Given an initial strategy reaching an undesired outcome, identify minimal changes to the strategy."*

Our ghosts are counterfactuals: "what if we had chosen differently?" The heritage graph enables post-hoc counterfactual exploration.

### Event Sourcing + Distributed Tracing

From [ScienceDirect research](https://www.sciencedirect.com/science/article/abs/pii/S0164121221001126):

> *"Distributed tracing adds a new dimension to event sourcing by connecting it to execution metadata."*

Our correlation IDs connect AGENTESE request traces to Crown Jewel operation traces — request lineage + operation lineage unified.

---

## References

- [Traced monoidal categories - nLab](https://ncatlab.org/nlab/show/traced+monoidal+category)
- [Polynomial Functors - Spivak & Niu (2024)](https://arxiv.org/abs/2312.00990)
- [Neural wiring diagrams - Topos Institute (2024)](https://topos.institute/blog/2024-11-08-neural-wiring-diagrams/)
- [AI Observability Guide 2025](https://www.vellum.ai/blog/understanding-your-agents-behavior-in-production)
- [Graph visualization UX](https://cambridge-intelligence.com/graph-visualization-ux-how-to-avoid-wrecking-your-graph-visualization/)
- [Event sourcing + observability](https://www.sciencedirect.com/science/article/abs/pii/S0164121221001126)
- [Counterfactual strategies for MDPs - IJCAI 2025](https://www.ijcai.org/proceedings/2025/47)
- [Monitoring event-driven architectures - Datadog](https://www.datadoghq.com/blog/monitor-event-driven-architectures/)

---

*"The persona is a garden, not a museum."* — Traces are living history, not static logs.
