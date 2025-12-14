---
path: docs/skills/n-phase-cycle/process-metrics
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
- Span per phase with attributes: `{phase, tokens_in, tokens_out, duration_ms, entropy, success, law_checks, exploration_spend, ledger_state}`.  
- Link spans across cycles (re-metabolization loop) to see drift and recovery.  
- Emit events for strategy changes, puppet swaps, and cross-synergy selections.  
- Ingest `phase_ledger` + `entropy` from plan headers into spans to keep `_forest.md` reconciliation automatic.

---

## Dashboards (hotloadable)
- Cycle Health: durations, token slope, entropy vs throughput.  
- Lawfulness Board: identity/associativity failures over time.  
- Exploration Ledger: Accursed Share planned vs actual, ideas promoted/pruned.  
- Adoption/Effectiveness: MEASURE signals vs EDUCATE reach.  
- **Fixture schema**: keep hotloadable JSON/CSV in `metrics/fixtures/` with `{phase, tokens_in, tokens_out, duration_ms, entropy_spent, law_checks_passed, adoption_events, branch_count}` so demos work offline (AD-004).

## Hotloadable Fixtures (contract)
- **Format**: JSON Lines for easy `jq` slicing; each line follows schema  
  `{cycle_id, phase, phase_group(SENSE|ACT|REFLECT), tokens_in, tokens_out, duration_ms, entropy_spent, entropy_remaining, law_checks_run, law_checks_failed, adoption_events, branch_count, ledger, timestamp, notes}`.  
- **Fidelity decision**: Use **synthetic data shaped like OTEL spans** (field names parallel `otel.span.*` attributes) to stay offline yet align to future OTLP exporters. Raw OTEL ingestion is deferred until code wiring.  
- **Seed fixture**: `metrics/fixtures/process-metrics.jsonl` seeds one SENSE/ACT/REFLECT trio (cycle `cycle-2025-12-13-a`) with ledger + entropy budgets filled so dashboards demo without live collectors.  
- **Owners/branch**: `obs/metrics` owns schema; doc + fixtures may land on `main` (current driver: gpt-5-codex). Any future emitter wiring should branch `process-metrics-otel` to keep offline fixtures stable.  
- **Law checks**: Treat `law_checks_run - law_checks_failed` as associativity/identity pass count; fixture rows must keep `law_checks_failed <= law_checks_run` to satisfy invariants.

---

## Forest Handle Tracing (deferred wiring)
- Clause-first prompt starters for spans:
  - `concept.forest.manifest[phase=PLAN][minimal_output=true]@span=forest_plan` → attr `ledger_state` required.
  - `concept.forest.refine[phase=DEVELOP][rollback=true][law_check=true]@span=forest_dev` → attr `law_checks` incremented.
  - `time.forest.witness[phase=REFLECT][law_check=true]@span=forest_trace` → attr `items=1`, guard ordering.
  - `void.entropy.sip[phase=RESEARCH][entropy=0.07]@span=entropy_sip` → attr `entropy_spent=0.07`.
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
