# Différance Engine Cultivation

**Season:** SPROUTING
**Spec:** `spec/protocols/differance.md`
**Target:** `impl/claude/agents/differance/`

---

## Prompt for Planning Agent

You are cultivating the **Différance Engine** — a traced wiring diagram system with ghost heritage graphs. The spec exists at `spec/protocols/differance.md`. Your task: plan a multi-phase implementation that reduces uncertainty at each step.

### Ground in Voice

> *"Daring, bold, creative, opinionated but not gaudy"*
> *"Tasteful > feature-complete"*

This is not a logging system. It's a **self-knowing system** — outputs that know their own lineage, including roads not taken.

### The Core Types to Implement

```
TraceMonoid        — Associative composition of wiring decisions
WiringTrace        — Single decision record (ADR-style)
Alternative        — A ghost (road not taken)
GhostHeritageDAG   — Full lineage graph
TRACED_OPERAD      — Extension of AGENT_OPERAD
DIFFERANCE_POLYNOMIAL — Core state machine
```

### Phase Strategy (Garden Protocol)

**Phase 1: SPROUTING** — Reduce type uncertainty
- [ ] Implement core dataclasses: `WiringTrace`, `Alternative`, `TraceMonoid`
- [ ] Property tests for monoid laws (identity, associativity)
- [ ] Identify: What's unclear in the spec?
- **Exit criteria:** Monoid laws pass; uncertainties documented

**Phase 2: SPROUTING** — Reduce integration uncertainty
- [ ] Implement `TRACED_OPERAD` extending `AGENT_OPERAD`
- [ ] `traced_seq`, `traced_par` operations
- [ ] Verify: `traced_seq(a, b).agent ≅ seq(a, b)` (semantic preservation)
- **Exit criteria:** Traced operations compose correctly

**Phase 3: BLOOMING** — Build heritage graph
- [ ] Implement `GhostHeritageDAG` builder
- [ ] D-gent storage adapter for traces
- [ ] Query: heritage by output_id, depth-limited traversal
- **Exit criteria:** Can build DAG from trace log

**Phase 4: BLOOMING** — AGENTESE integration
- [ ] `time.trace.*` paths (manifest, witness, heritage, ghosts)
- [ ] `time.branch.*` paths (create, explore, compare)
- [ ] `self.differance.*` paths (why, navigate)
- **Exit criteria:** CLI `kg time.trace.why <id>` works

**Phase 5: FRUITING** — Crown Jewel integration
- [ ] Wire into Brain, Gardener (100% complete jewels first)
- [ ] Ghost Heritage Graph React component
- [ ] Three projection modes: CLI, JSON, Web
- **Exit criteria:** Can see ghost heritage in Crown Jewel UI

### Spec Improvements to Consider

As you implement, capture uncertainties and propose spec amendments:

1. **Trace granularity**: Is `WiringTrace` per-operation right, or should we trace at turn level?
2. **Ghost retention**: 7/30 day defaults — are these appropriate?
3. **Compression**: When does holographic compression kick in?
4. **Performance**: What's the cost model for trace recording?
5. **Privacy boundaries**: How do traces interact with multi-tenant?

### Output Format

After each phase, produce:

```markdown
## Phase N Complete

### What Worked
- ...

### What's Uncertain
- ...

### Spec Amendments Proposed
- ...

### Next Phase Entry Criteria
- ...
```

### Laws That Must Hold

```python
# Monoid
assert TraceMonoid.empty().compose(t) == t == t.compose(TraceMonoid.empty())
assert (a.compose(b)).compose(c) == a.compose(b.compose(c))

# Semantic preservation
assert traced_seq(x, y).agent.invoke(input) == seq(x, y).invoke(input)

# Ghost preservation
assert set(traced_seq(a, b).ghosts()) >= set(a.ghosts()) | set(b.ghosts())

# DAG integrity
for trace in monoid.traces:
    assert trace.parent_trace_id is None or trace.parent_trace_id in monoid.trace_ids()
```

### Anti-Patterns to Avoid

- **Over-engineering storage**: Start with in-memory, move to D-gent later
- **Premature UI**: Get the algebra right before visualization
- **Ghost worship**: Not every alternative needs to be recorded
- **Trace pollution**: Don't trace trivial operations

---

*"The ghost heritage graph is the UI innovation: seeing what almost was alongside what is."*
