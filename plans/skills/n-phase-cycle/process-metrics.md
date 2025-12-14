# Meta Skill: Process Metrics & Traces for the N-Phase Cycle

> Instrument the lifecycle itself: tokens, time, entropy, and lawfulness as first-class signals.

**Difficulty**: Medium  
**Prerequisites**: `measure.md`, observability stack (OTEL/Tempo/Prometheus), `meta-skill-operad.md`  
**Files Touched**: observability configs, dashboards, logs/specs for metrics; documentation in skills

---

## Overview
This skill defines hard metrics for the lifecycle factory. It treats each phase as a node in a traced pipeline with composable metrics and encourages pre-computed, hotloadable dashboards.

---

## Core Metrics
- **Token metabolism**: tokens per phase, per artifact, and per accepted decision; slope over time.  
- **Throughput**: phase durations, WIP counts, parallel track utilization.  
- **Lawfulness**: identity/associativity checks executed vs failed (from operad/functor tests).  
- **Exploration budget**: Accursed Share percentage actually spent vs planned.  
- **Lookback intensity**: # lookbacks / cycle, double-loop vs single-loop fixes (from `lookback-revision.md`).  
- **Quality gates**: QA/Test pass rates, flaky counts, defect escape rate.  
- **Adoption**: EDUCATE artifact usage (docs hits, CLI command invocations), MEASURE-to-REFLECT loop closures.

---

## Tracing Model
- Span per phase with attributes: `{phase, tokens_in, tokens_out, duration_ms, entropy, success, law_checks, exploration_spend}`.  
- Link spans across cycles (re-metabolization loop) to see drift and recovery.  
- Emit events for strategy changes, puppet swaps, and cross-synergy selections.

---

## Dashboards (hotloadable)
- Cycle Health: durations, token slope, entropy vs throughput.  
- Lawfulness Board: identity/associativity failures over time.  
- Exploration Ledger: Accursed Share planned vs actual, ideas promoted/pruned.  
- Adoption/Effectiveness: MEASURE signals vs EDUCATE reach.

---

## Forest Handle Tracing (deferred wiring)
- Emit span per AGENTESE call once wired: name = `concept.forest.<affordance>`; attrs `{observer_role, law_checks, selection_entropy, plan_path, items=1}` (enforce Minimal Output).  
- `time.forest.witness` uses event stream with mtime watermark; measure lag between epilogue write and witness consumption.  
- Lookback trigger: after `forest_update` completes, increment counter of double-loop shifts (from `lookback-revision.md`) and stash in hotloadable dashboard spec (no runtime emission yet).  
- Accursed Share audit: track `void.forest.sip` entropy and dormant selection diversity; target entropy 0.05–0.10.

---

## Recursive Hologram
- PLAN→RESEARCH→DEVELOP the metric set quarterly via `meta-re-metabolize.md`; prune stale metrics (Molasses Test).  
- Use `meta-skill-operad.md` to compose metrics (identities = zero-values, associative aggregations).

---

## Verification
- Metrics defined and instrumented; traces emitted per phase.  
- Dashboards exist and are hotloadable.  
- Accursed Share and lawfulness signals visible in reports.

---

## Related
- `measure.md`  
- `meta-re-metabolize.md`  
- `lookback-revision.md`

---

## Changelog
- 2025-12-13: Initial version.
