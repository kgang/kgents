# Skill: MEASURE (N-Phase Cycle)

> Instrument and observe effects to validate value and guide adjustments.

**Difficulty**: Medium  
**Prerequisites**: `educate.md`, observability patterns, data access constraints  
**Files Touched**: metrics dashboards, telemetry configs, experiment logs

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

## Changelog
- 2025-12-13: Initial version.
