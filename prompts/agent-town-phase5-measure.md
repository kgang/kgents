# Agent Town Phase 5: MEASURE Phase

**Predecessor**: `plans/_epilogues/2025-12-14-agent-town-phase5-educate.md`
**Phase**: MEASURE (N-Phase 10 of 11)
**Ledger**: `{PLAN:touched, RESEARCH:touched, DEVELOP:touched, STRATEGIZE:touched, CROSS-SYNERGIZE:touched, IMPLEMENT:touched, QA:touched, TEST:touched, EDUCATE:touched, MEASURE:in_progress}`

---

## Context

Phase 5 EDUCATE complete:
- Skill document created: `docs/skills/agent-town-visualization.md`
- APIs documented: EigenvectorScatterWidget, TownSSEEndpoint, TownNATSBridge
- Examples provided: 15+ code samples
- Skills index updated

Current test count: 505 town tests, 87 visualization contract tests.

---

## MEASURE Objectives

### 1. Define Signals

| Signal | Description | Source | Baseline |
|--------|-------------|--------|----------|
| Visualization render time | ASCII/JSON projection latency | `project_scatter_to_ascii()` | <10ms |
| SSE event throughput | Events/second pushed | `TownSSEEndpoint` | 100 evt/s |
| NATS fallback rate | % using memory vs NATS | `TownNATSBridge` | <5% fallback |
| Widget state size | Bytes per ScatterState | serialization | <1KB/citizen |
| Functor law compliance | Identity/composition tests pass | pytest | 100% |

### 2. Instrumentation Points

| Component | Metric | Type |
|-----------|--------|------|
| `project_scatter_to_ascii` | execution_time_ms | Histogram |
| `EigenvectorScatterWidgetImpl.project` | target_type, duration | Counter+Timer |
| `TownSSEEndpoint._queue` | queue_depth, dropped_events | Gauge |
| `TownNATSBridge._publish` | fallback_used, publish_count | Counter |
| Widget.map() | transformation_count | Counter |

### 3. Dashboard Sketch

```
┌─────────────────────────────────────────────────────────┐
│ Agent Town Visualization Metrics                        │
├─────────────────────────────────────────────────────────┤
│ Render Latency (p50/p99)    │ SSE Throughput            │
│ ████████░░ 5ms / 12ms       │ ▂▄▆▇▅▃▂ 87 evt/s         │
├─────────────────────────────────────────────────────────┤
│ NATS Status                 │ Widget State Size         │
│ ● Connected (fallback: 2%)  │ avg: 0.8KB/citizen        │
├─────────────────────────────────────────────────────────┤
│ Law Compliance: ✓ 8/8       │ Test Coverage: 87 tests   │
└─────────────────────────────────────────────────────────┘
```

---

## Actions

1. **Add timing instrumentation** to visualization module
   - Wrap `project_scatter_to_ascii` with timing
   - Add metrics to widget projection methods
   - Track SSE queue depth

2. **Create metrics fixtures** for testing
   - Hotloadable baseline data
   - Performance regression tests

3. **Document baselines** in epilogue
   - Current performance numbers
   - Alert thresholds for degradation

4. **Lookback**: Validate measurement assumptions
   - Are we measuring the right things?
   - Counter-metrics: What would indicate harm?

---

## Entropy Budget

- Allocated: 0.07
- Draw: `void.entropy.sip(amount=0.07)`
- Purpose: Metric invention, correlation hunting, dashboard sketching

---

## Branch Candidates

- **Parallel**: Real NATS cluster metrics (defer to production)
- **Deferred**: Distributed tracing integration (OpenTelemetry)
- **Bounty**: Grafana dashboard template for visualization metrics

---

## Exit Criteria

- [ ] Key signals defined with baselines
- [ ] Instrumentation points identified (code or spec)
- [ ] Dashboard sketch documented
- [ ] Lookback on measurement assumptions
- [ ] Alert thresholds proposed

---

## Continuation

On success: `⟿[REFLECT]` - Synthesize learnings, decide next cycle
On failure: `⟂[BLOCKED:metrics_broken]` - Instrumentation issues

---

*Guard [phase=MEASURE][entropy=0.07][law_check=true][minimal_output=true]*

---

## Auto-Inducer

⟿[MEASURE]
/hydrate prompts/agent-town-phase5-measure.md
handles: scope=agent-town-phase5-visualization; educate_status=COMPLETE; skill_doc=docs/skills/agent-town-visualization.md; tests=505; ledger={PLAN:touched,RESEARCH:touched,DEVELOP:touched,STRATEGIZE:touched,CROSS-SYNERGIZE:touched,IMPLEMENT:touched,QA:touched,TEST:touched,EDUCATE:touched,MEASURE:in_progress}; entropy=0.07
mission: Define signals; identify instrumentation points; sketch dashboard; propose baselines; lookback on measurement assumptions.
actions: Define 5 key signals with baselines; identify instrumentation points in visualization.py; sketch ASCII dashboard; document alert thresholds; run lookback on what to measure.
exit: signals defined + baselines documented + dashboard sketched → ledger.MEASURE=touched; continuation → REFLECT | instrumentation blocked → ⟂[BLOCKED:metrics_broken].

---

**LAW**: This prompt auto-continues. The signifier `⟿[MEASURE]` triggers immediate execution without human intervention. Halt conditions: instrumentation failures, entropy depletion, or `⟂[HUMAN_INTERRUPT]`.
