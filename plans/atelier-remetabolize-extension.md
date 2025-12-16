---
path: atelier/remetabolize-extension
status: active
progress: 0
last_touched: 2025-12-15
touched_by: gpt-5-codex
blocking: []
enables: []
session_notes: |
  Spawned from critical read of plans/_epilogues/2025-12-15-atelier-remetabolize.md.
  Goal: push Tiny Atelier from “complete demo” to production-ready, joyful utility for Kent (developer) with coherent UX and ops.
phase_ledger:
  PLAN: touched
  RESEARCH: pending
  DEVELOP: pending
  STRATEGIZE: pending
  CROSS-SYNERGIZE: pending
  IMPLEMENT: pending
  QA: pending
  TEST: pending
  EDUCATE: pending
  MEASURE: pending
  REFLECT: pending
entropy:
  planned: 0.12
  spent: 0.0
  remaining: 0.12
---

# Atelier Re-Metabolize: Usability, Coherence, Production Readiness

> *"The artisans await patrons; give them rails, metrics, and ritual so Kent can trust them in daylight."*

**Context**: `plans/_epilogues/2025-12-15-atelier-remetabolize.md`, Tiny Atelier stack (`agents/atelier/*`, `protocols/api/atelier.py`, `protocols/cli/handlers/atelier.py`, `web/src/pages/Atelier.tsx`, `agents/atelier/ui/widgets.py`).
**Principles**: Tasteful, Ethical, Joy-Inducing, Composable; Lawful spans/opacity.

---

## Critical Gaps (from epilogue)
- **Usability**: No documented golden path or defaults for first run; streaming SSE failure modes unspecified; Gallery/Lineage UX lacks empty/error states and pagination; no sample commissions pre-seeded.
- **Coherence**: CLI, web, and marimo widgets not described as a single journey; collaboration operad not surfaced as templates; Orisinal theme noted but not enforced across UI.
- **Developer Value**: No runbook/SLOs, perf/load expectations, or local dev quickstart; missing contract tests for REST/SSE; artisan contracts and operad laws unasserted in CI.
- **Production Readiness**: Auth/tenancy, quotas, and budget enforcement absent; no kill-switch/oncall hooks; deployment manifests missing; no monitoring of SSE drop/offline artisans; persistence durability unstated.

---

## Goals
1) Make Tiny Atelier easy and delightful to use (golden path, resilient streaming, cohesive UI).  
2) Increase Kent’s leverage: strong contracts/tests, runbooks, observability, and fast local loop.  
3) Ship toward production: auth/quotas, SLOs/alerts, deploy scripts/manifests, failure drills.  
4) Preserve joy: ritualized celebrations/gratitude without harming margins.

---

## Phases & Exit Criteria

### Phase 1 — Usability & Coherence
- **Deliver**: Golden-path “Hello Commission” across CLI → SSE → Gallery → Lineage; empty/error/loading states for web widgets; sample commissions/lineage seeds; collaboration presets (solo/duet/ensemble/refinement/chain) exposed in UI + CLI helpers.  
- **Files**: `protocols/cli/handlers/atelier.py`, `protocols/api/atelier.py`, `agents/atelier/ui/widgets.py`, `web/src/pages/Atelier.tsx`, `agents/atelier/gallery/store.py`.  
- **Exit**: New user can run one command to see streaming piece + gallery entry + lineage tree; SSE failure degrades to polling with clear affordance; presets documented in UI tooltips.

### Phase 2 — Developer Value (Kent)
- **Deliver**: Runbook (start/stop, logs, failure triage), quickstart script (seed + smoke), REST/SSE contract tests, artisan/operad property tests (IDLE→READY, associativity/identity for operad ops), type hints tightened.  
- **Files**: `agents/atelier/artisan.py`, `agents/atelier/workshop/operad.py`, `agents/atelier/_tests/`, `protocols/api/_tests/`, `scripts/` (smoke), `docs/` (runbook).  
- **Exit**: CI enforces contracts; `uv run pytest impl/claude/agents/atelier/_tests` green; smoke script returns 0 and emits spans; developer can reproduce issues with one command.

### Phase 3 — Production Readiness
- **Deliver**: Auth/tenant-aware commissions, quotas/credits (reuse budget store/paywall pattern from Agent Town), SLOs (latency, stream dropout, artisan error rate), OpenTelemetry spans/metrics, kill-switch for artisans, durability guarantees (fs vs object store), K8s/compose manifests, health/readiness probes.  
- **Files**: `agents/atelier/workshop/orchestrator.py`, `agents/atelier/event_bus.py`, `protocols/api/atelier.py`, `agents/town/budget_store.py` (pattern reuse), `impl/claude/infra/k8s/manifests` (new), `docs/` (SLOs/oncall).  
- **Exit**: Authenticated commission path with per-tenant quotas; metrics exported; K8s manifest deploys service with readiness/liveness; kill-switch tested; data persisted and restorable.

### Phase 4 — Joy & Monetization Hooks
- **Deliver**: Light celebration/gratitude scenes for completed pieces (Haiku-first to protect margins), optional paid premium artisans or “festival” commissions using existing paywall mechanics, analytics for user delight (opt-in).  
- **Files**: `agents/atelier/artisans/*.py`, `agents/atelier/workshop/collaboration.py`, `agents/atelier/paywall.py` (new), `web/src/pages/Atelier.tsx`, `protocols/api/atelier.py`.  
- **Exit**: Celebration surfaced in UI without blocking; premium paths gated and metered; opt-in metrics collected; joy elements toggleable via config.

---

## Risks & Mitigations
- **SSE brittleness**: Add fallback polling and heartbeats; surface degraded mode.  
- **Margin bleed from celebration**: Use Haiku-tier models and cap tokens; reuse model_router.  
- **Complexity creep**: Keep operad ops law-checked with property tests; constrain scope per phase.  
- **Ops toil**: Automate smoke + health checks; centralize alerts with existing action_metrics pipeline.

---

## Cross-References
- Epilogue: `plans/_epilogues/2025-12-15-atelier-remetabolize.md`  
- Skills: `docs/skills/n-phase-cycle/*`, `docs/skills/plan-file.md`, `docs/skills/harden-module.md`, `docs/skills/qa.md`, `docs/skills/test-patterns.md`  
- Patterns to reuse: Agent Town paywall/budget (`agents/town/paywall.py`, `agents/town/budget_store.py`), kill-switch (`agents/town/kill_switch.py`), spans (`protocols/api/action_metrics.py`).
