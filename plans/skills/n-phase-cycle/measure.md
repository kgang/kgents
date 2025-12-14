---
path: plans/skills/n-phase-cycle/measure
status: active
progress: 0
last_touched: 2025-12-13
touched_by: gpt-5-codex
blocking: []
enables: []
session_notes: |
  Header added for forest compliance (STRATEGIZE).
phase_ledger:
  PLAN: touched
  RESEARCH: touched
  DEVELOP: skipped  # reason: doc-only
  STRATEGIZE: touched
  CROSS-SYNERGIZE: skipped  # reason: doc-only
  IMPLEMENT: skipped  # reason: doc-only
  QA: skipped  # reason: doc-only
  TEST: skipped  # reason: doc-only
  EDUCATE: skipped  # reason: doc-only
  MEASURE: deferred  # reason: metrics backlog
  REFLECT: touched
entropy:
  planned: 0.05
  spent: 0.0
  returned: 0.05
---

# Skill: MEASURE (N-Phase Cycle)

> Instrument and observe effects to validate value and guide adjustments.

**Difficulty**: Medium  
**Prerequisites**: `educate.md`, observability patterns, data access constraints  
**Files Touched**: metrics dashboards, telemetry configs, experiment logs

---

## Quick Wield
- **Snap prompt**:
```markdown
/hydrate → MEASURE | signals + baselines | ledger.MEASURE=touched | entropy.sip(0.05–0.10) | next=REFLECT
```
- **Minimal artifacts**: defined signals + owners, telemetry hooks/dashboards (hotloadable welcome), baselines + alert thresholds, ledger update, branch/bounty entries for gaps.
- **Signals**: report tokens/time/entropy + lawfulness + adoption to `process-metrics.md`; keep fixtures hotloadable.
- **Branch check**: if missing instrumentation blocks progress, emit a branch handle.

---

## Overview
MEASURE ensures work delivers real-world value. It aligns with Transparent Infrastructure and Generative principles—signals are composable and reusable.

---

## Step-by-Step

1. **Define signals**: Choose leading indicators (usage, latency, errors, adoption), aligned to goals from PLAN/STRATEGIZE and the `process-metrics.md` schema (token/time/entropy/lawfulness/exploration spend).  
2. **Instrument**: Add telemetry hooks (OTEL spans/metrics), feature flags, and dashboards; prefer hotloadable data for demos.  
3. **Run checks**: Validate data quality, baseline measurements, and alert thresholds; document how to read them.
4. **Lookback**: Run `lookback-revision.md` on measurement assumptions/results to catch double-loop shifts and trigger re-metabolization if needed.

---

## Recursive Hologram
- Apply PLAN→RESEARCH→DEVELOP to the measurement model: are we measuring the grammar or instances?
- Use `meta-skill-operad.md` so metrics/alerts compose (identity metric, associative aggregation) and survive skill mutations.

---

## Accursed Share (Entropy Budget)

MEASURE reserves 5-10% for exploration:

- **Metric invention**: What signal would you WANT but don't have? Sometimes it's measurable.
- **Counter-metrics**: What would indicate this feature is harmful? Measure that too.
- **Correlation hunting**: What other metrics might move when this one does?
- **Dashboard sketching**: Sketch the ideal dashboard before instrumenting. Work backward.

Draw: `void.entropy.sip(amount=0.07)`
Return unused: `void.entropy.pour`

---

## Verification
- Metrics live with readable dashboards and alerting where needed.  
- Baselines captured; data quality checked.  
- Insights piped back to REFLECT.

---

## Hand-off
Next: `reflect.md` to synthesize learnings and feed the next loop.

---

## Related Skills
- `meta-skill-operad.md`
- `meta-re-metabolize.md`
- `lookback-revision.md`
- `process-metrics.md`
- `../agent-observability.md`

---

## Continuation Generator

Emit this when exiting MEASURE:

### Exit Signifier

```markdown
# Normal exit (auto-continue):
⟿[REFLECT]
/hydrate
handles: metrics=${metrics_instrumented}; dashboards=${dashboards}; baselines=${baselines}; alerts=${alert_thresholds}; summary=${measurement_summary}; data=${data_quality_notes}; lookback=${lookback_findings}; ledger={MEASURE:touched}; branches=${branch_notes}
mission: synthesize outcomes; distill learnings; choose continuation (PLAN/meta-re-metabolize/DETACH).
actions: summarize shipped/changed/risks; distill one-line zettels (Molasses Test); epilogue + bounty updates; decide continuation.
exit: epilogue + next-plan entry or DETACH handle; ledger.REFLECT=touched; continuation emitted per choice.

# Halt conditions (rare for MEASURE):
⟂[BLOCKED:metrics_broken] Instrumentation failed; cannot measure
⟂[ENTROPY_DEPLETED] Budget exhausted without entropy sip
```

Template vars: `${metrics_instrumented}`, `${dashboards}`, `${baselines}`, `${alert_thresholds}`, `${measurement_summary}`, `${data_quality_notes}`, `${lookback_findings}`, `${branch_notes}`.

## Related Skills
- `auto-continuation.md` — The meta-skill defining this generator pattern
- `meta-skill-operad.md`
- `meta-re-metabolize.md`
- `lookback-revision.md`
- `process-metrics.md`
- `../agent-observability.md`

---

## Changelog
- 2025-12-13: Added Accursed Share section (re-metabolize).
- 2025-12-13: Added Continuation Generator section (auto-continuation).
- 2025-12-13: Initial version.
