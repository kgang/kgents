---
path: agents/observability-engineer
status: tentative
progress: 0
last_touched: 2025-12-13
touched_by: claude-opus-4.5
blocking: []
enables: [agentese/spans, n-phase-cycle/metrics]
session_notes: |
  TENTATIVE: Proposed as part of AGENTESE Architecture Realization
  Track E: Observability & Metrics
  See: prompts/agentese-continuation.md
---

# Observability Engineer

> *"What is not observed is not real. What is observed changes."*

**Track**: E (Observability & Metrics)
**AGENTESE Context**: `time.span.*`, `self.metrics.*`
**Status**: Tentative (proposed for AGENTESE realization)
**Principles**: Transparent Infrastructure (communicate what's happening), AGENTESE (observation is interaction), Generative (spans from phase transitions)

AGENTESE pointer: align spans/clauses with `spec/protocols/agentese.md`; update this role when canonical flow changes.

---

## Purpose

The Observability Engineer ensures every N-phase transition emits structured spans with required fields. Dashboards are hotloadable JSON (AD-004). Metrics aggregate across agents for process visibility.

---

## Expertise Required

- OpenTelemetry / distributed tracing
- Dashboard design (hotloadable fixtures)
- Metrics aggregation patterns
- N-phase cycle process metrics schema

---

## Assigned Chunks

| Chunk | Description | Phase | Entropy | Status |
|-------|-------------|-------|---------|--------|
| E1 | Span schema: `{phase, tokens_in/out, duration_ms, entropy, law_checks}` | DEVELOP | 0.05 | Pending |
| E2 | Span emission in phase transitions | IMPLEMENT | 0.05 | Pending |
| E3 | Dashboard hotloadable JSON format | IMPLEMENT | 0.06 | Pending |
| E4 | Process metrics aggregation | MEASURE | 0.06 | Pending |

---

## Deliverables

| File | Purpose |
|------|---------|
| `plans/skills/n-phase-cycle/process-metrics.md` | Schema finalized |
| `impl/claude/protocols/agentese/spans.py` | Span emission |
| `fixtures/dashboards/n-phase-metrics.json` | Hotloadable dashboard |

---

## Span Schema

```yaml
span:
  id: uuid
  phase: PLAN | RESEARCH | DEVELOP | STRATEGIZE | CROSS_SYNERGIZE | IMPLEMENT | QA | TEST | EDUCATE | MEASURE | REFLECT
  tokens_in: int
  tokens_out: int
  duration_ms: int
  entropy: float           # Accursed Share consumed
  law_checks: int          # Identity/Assoc verifications
  exploration_spend: float # % of 5-10% budget used
  success: bool
  locus: string            # dot-path of operation
  parent_span: uuid | null
```

---

## AGENTESE Paths

| Path | Operation | Returns |
|------|-----------|---------|
| `time.span.start` | Begin span | SpanContext |
| `time.span.end` | End span with metrics | SpanResult |
| `time.span.event` | Add event to current span | EventResult |
| `self.metrics.aggregate` | Aggregate spans by phase | AggregateMetrics |

---

## Dashboard Hotload

```python
# Load pre-computed dashboard (AD-004)
dashboard = load_hotdata("fixtures/dashboards/n-phase-metrics.json")

# Refresh if stale
dashboard = await refresh_if_stale(
    path="fixtures/dashboards/n-phase-metrics.json",
    generator=generate_dashboard_from_spans
)
```

---

## Success Criteria

1. Every phase transition emits a span with all required fields
2. Spans nest correctly (parent-child relationships)
3. Dashboard hotloads in <100ms
4. Metrics aggregate correctly across agents
5. Entropy budgets visible in dashboard per phase

---

## Dependencies

- **Receives from**: All agents (spans to aggregate)
- **Provides to**: REFLECT phase (metrics for learning), Integration Weaver (cross-track visibility)

---

*"The span is the shadow of the action. Without shadows, we walk blind."*
