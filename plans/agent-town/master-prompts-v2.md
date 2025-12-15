---
path: plans/agent-town/master-prompts-v2
status: active
progress: 0
priority: 10.0
importance: crown_jewel
last_touched: 2025-12-15
touched_by: claude-opus-4-5
blocking: []
enables:
  - agent-town-launch
session_notes: |
  MASTER PROMPTS for Agent Town N-Phase Cycle.
  5 parallel tracks, can be run concurrently or sequentially.
  Each prompt is self-contained with handles, mission, exit criteria.
phase_ledger:
  PLAN: touched
  RESEARCH: complete
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
  planned: 0.20
  spent: 0.05
  remaining: 0.15
---

# Agent Town Master Prompts v2: The Massive N-Phase Cycle

> *"Five rivers converge into one ocean. Each track is a river."*

---

## Track Overview

| Track | Priority | Dependencies | Effort Est. |
|-------|----------|--------------|-------------|
| **A: INHABIT Mode** | P0 | None | 2 sessions |
| **B: Instrumentation** | P0 | None | 1 session |
| **C: Monetization** | P0 | B (partial) | 2 sessions |
| **D: Web UI** | P1 | A, B, C | 3 sessions |
| **E: Premium Scenarios** | P2 | A, D | 1 session |

**Parallelization**: Tracks A, B, C can run concurrently. Track D starts when A+B+C reach IMPLEMENT. Track E starts when D reaches QA.

---

## Master Prompt: Track A — INHABIT Mode (Safety-First)

```markdown
⟿[PLAN] Agent Town Track A: INHABIT Mode

/hydrate plans/agent-town/unified-v2.md

handles:
  unified_plan: plans/agent-town/unified-v2.md
  dialogue_engine: impl/claude/agents/town/dialogue_engine.py
  citizen: impl/claude/agents/town/citizen.py
  flux: impl/claude/agents/town/flux.py
  spec_principles: spec/principles.md
  ledger: {PLAN: in_progress}
  entropy: 0.08

scope:
  - Implement INHABIT mode where user merges with citizen
  - Add consent debt meter per unified-v2.md §2
  - Implement force mechanic with ethical guardrails
  - Session caps: 15 min (Citizen), 30 min (Founder)
  - CLI command: `kg town inhabit <citizen>`
  - 60+ tests covering INHABIT mechanics + consent

non_goals:
  - Web UI (Track D)
  - Monetization integration (Track C)
  - Full LOD 5 artifact generation (separate concern)

exit_criteria:
  - [ ] InhabitSession with ConsentState working
  - [ ] Force mechanic respects guardrails (opt-in, logged, limited)
  - [ ] Consent debt accumulates and decays correctly
  - [ ] CLI `kg town inhabit alice` enters INHABIT mode
  - [ ] Citizen can resist and refuse at rupture
  - [ ] 60+ tests passing
  - [ ] Ethics principle satisfied per spec/principles.md §3

attention_budget:
  research: 15%
  develop: 25%
  implement: 40%
  test: 20%

mission:
  Build INHABIT mode that respects citizen autonomy. Users collaborate
  with citizens, not control them. Force is expensive, logged, and limited.
  The consent debt meter tracks relationship health. At rupture, the citizen
  refuses all interaction until harmony is restored.

continuation:
  ⟿[RESEARCH] if terrain unclear
  ⟿[IMPLEMENT] if design is solid
  ⟂[BLOCKED:ethics] if design violates spec/principles.md §3
```

---

## Master Prompt: Track B — Instrumentation Spine

```markdown
⟿[PLAN] Agent Town Track B: Instrumentation Spine

/hydrate plans/agent-town/unified-v2.md

handles:
  unified_plan: plans/agent-town/unified-v2.md
  metrics_target: impl/claude/protocols/api/metrics.py (new)
  town_api: impl/claude/protocols/api/town.py
  otel: OpenTelemetry Python SDK
  ledger: {PLAN: in_progress}
  entropy: 0.06

scope:
  - Create ActionMetric dataclass per unified-v2.md §4
  - Implement @instrument_action decorator
  - Add metrics emission to all billable actions (LOD, INHABIT, branch)
  - OTEL span export for distributed tracing
  - Dashboard data contract (what metrics, what format)
  - 30+ tests for metrics accuracy

non_goals:
  - Grafana/dashboard UI (future)
  - Billing integration (Track C)
  - Alert rules (post-launch)

exit_criteria:
  - [ ] ActionMetric captures: type, tokens, model, latency, credits
  - [ ] @instrument_action decorator works on async functions
  - [ ] Every LLM call in town/* emits metric
  - [ ] OTEL spans exported (local collector)
  - [ ] 30+ tests passing
  - [ ] Can query: "What was the average LOD3 latency today?"

attention_budget:
  research: 10%
  develop: 20%
  implement: 50%
  test: 20%

mission:
  Without metrics, we cannot validate business hypotheses.
  Instrument every billable action before launching monetization.
  This is the prerequisite for Track C and kill-switch enforcement.

continuation:
  ⟿[IMPLEMENT] (this is infrastructure, go straight to code)
  ⟂[BLOCKED:otel] if OTEL setup fails
```

---

## Master Prompt: Track C — Monetization Infrastructure

```markdown
⟿[PLAN] Agent Town Track C: Monetization Infrastructure

/hydrate plans/agent-town/unified-v2.md

handles:
  unified_plan: plans/agent-town/unified-v2.md
  budget_store: impl/claude/agents/town/budget_store.py
  paywall: impl/claude/agents/town/paywall.py (new)
  payments: impl/claude/protocols/api/payments.py (new)
  stripe_docs: https://stripe.com/docs/api
  instrumentation: Track B (dependency)
  ledger: {PLAN: in_progress}
  entropy: 0.08

scope:
  - Implement BudgetStore with revised credit costs per unified-v2.md §1
  - Implement paywall logic with upgrade options
  - Stripe integration: subscriptions + credit packs
  - Webhook handling for subscription events
  - Kill-switch conditions per unified-v2.md §5
  - 40+ tests for payment flows

non_goals:
  - Full Stripe production setup (Kent does this)
  - Marketing/landing page (Track D)
  - Refund handling (post-MVP)

exit_criteria:
  - [ ] BudgetStore tracks credits, subscription tier, monthly usage
  - [ ] check_paywall() returns correct response for all LOD levels
  - [ ] Stripe Checkout session creation works (test mode)
  - [ ] Webhook updates user subscription status
  - [ ] Kill-switch alerts defined (CAC > 30% LTV, churn > 25%)
  - [ ] 40+ tests passing
  - [ ] Can demo: Tourist → paywall → Resident upgrade → LOD3 access

attention_budget:
  research: 10%
  develop: 25%
  implement: 45%
  test: 20%

dependency_check:
  - Track B metrics must emit before billing validation
  - Can proceed in parallel, integrate at IMPLEMENT

mission:
  Build the payment infrastructure with margin-safe pricing.
  Every LOD unlock must be profitable. Use kill-switch conditions
  to halt if economics don't work. Stripe test mode first.

continuation:
  ⟿[IMPLEMENT] when Track B reaches IMPLEMENT
  ⟂[BLOCKED:economics] if margin math doesn't work
  ⟂[BLOCKED:stripe] if Stripe account not ready
```

---

## Master Prompt: Track D — Web UI MVP

```markdown
⟿[PLAN] Agent Town Track D: Web UI MVP

/hydrate plans/agent-town/unified-v2.md

handles:
  unified_plan: plans/agent-town/unified-v2.md
  phase9_original: plans/agent-town/phase9-web-ui.md
  town_api: impl/claude/protocols/api/town.py
  track_a: Track A (INHABIT dependency)
  track_b: Track B (Instrumentation dependency)
  track_c: Track C (Monetization dependency)
  ledger: {PLAN: in_progress}
  entropy: 0.10

scope:
  - React + TypeScript + Tailwind + Pixi.js
  - Landing page with demo town preview
  - Town Mesa (2D grid with citizens)
  - Citizen Panel with LOD gating
  - Event feed (SSE)
  - INHABIT mode in browser
  - Stripe Checkout integration
  - User dashboard (towns, credits, subscription)
  - Mobile responsive (basic)
  - 50+ frontend tests

non_goals:
  - Native mobile app
  - Advanced animations
  - Custom themes
  - VR/AR

exit_criteria:
  - [ ] Landing page converts visitors to demo watchers
  - [ ] Mesa renders 7 citizens with real-time movement
  - [ ] Citizen Panel shows LOD 0-2 free, gates 3-5
  - [ ] INHABIT works in browser with consent UI
  - [ ] Stripe Checkout completes subscription purchase
  - [ ] Dashboard shows user's towns and credit balance
  - [ ] Lighthouse score > 90
  - [ ] 50+ tests passing
  - [ ] Kent says "this is ready to show people"

attention_budget:
  research: 10%
  develop: 20%
  implement: 50%
  test: 15%
  educate: 5%

dependency_check:
  - Track A: INHABIT API must exist
  - Track B: Metrics must emit for LOD actions
  - Track C: Paywall and checkout must work
  - Start when all three reach IMPLEMENT phase

mission:
  Build the public face of Agent Town. This is where money comes from.
  Use existing reactive substrate patterns where possible.
  Prioritize time-to-demo over polish. Ship ugly, iterate.

continuation:
  ⟿[IMPLEMENT] when A+B+C reach IMPLEMENT
  ⟂[BLOCKED:api] if backend APIs not ready
  ⟂[BLOCKED:design] if UX decisions needed
```

---

## Master Prompt: Track E — Premium Scenarios (Flagship Only)

```markdown
⟿[PLAN] Agent Town Track E: Premium Scenarios

/hydrate plans/agent-town/unified-v2.md

handles:
  unified_plan: plans/agent-town/unified-v2.md
  citizen: impl/claude/agents/town/citizen.py
  flux: impl/claude/agents/town/flux.py
  track_d: Track D (Web UI dependency)
  ledger: {PLAN: in_progress}
  entropy: 0.07

scope:
  - TWO scenarios only (per unified-v2.md §10):
    1. "The Vanishing" - mystery: a citizen disappears
    2. "The Founding" - origin: seven citizens arrive, shape the town
  - Scenario data format (YAML or JSON)
  - Scenario loader in TownFlux
  - Purchase flow integration
  - 20+ tests

non_goals:
  - Custom scenario builder
  - More than 2 scenarios (until these prove revenue)
  - Procedural scenario generation

exit_criteria:
  - [ ] ScenarioConfig dataclass with citizen presets, initial state, hooks
  - [ ] "The Vanishing" playable: Eve disappears day 3, clues emerge
  - [ ] "The Founding" playable: 7 citizens meet, form first coalitions
  - [ ] Both purchasable via Stripe ($9.99 each)
  - [ ] 20+ tests passing
  - [ ] Kent plays through both and says "I want more"

attention_budget:
  research: 15%
  develop: 30%
  implement: 40%
  test: 15%

dependency_check:
  - Track D: Web UI must be able to load scenarios
  - Start when Track D reaches QA phase

mission:
  Create two flagship scenarios that demonstrate Agent Town's potential.
  "The Vanishing" is a mystery that hooks players.
  "The Founding" is an origin story that teaches the mechanics.
  If these sell, we build more. If not, we pivot.

continuation:
  ⟿[IMPLEMENT] when Track D reaches QA
  ⟂[BLOCKED:narrative] if story design needs work
  ⟂[DETACH:mvp_complete] when both scenarios are purchasable
```

---

## Orchestration Protocol

### Phase 1: Parallel Kickoff (Day 1-3)

```bash
# Session 1: Track A (INHABIT)
/hydrate plans/agent-town/master-prompts-v2.md
# Copy Track A prompt, execute

# Session 2: Track B (Instrumentation)
/hydrate plans/agent-town/master-prompts-v2.md
# Copy Track B prompt, execute

# Session 3: Track C (Monetization)
/hydrate plans/agent-town/master-prompts-v2.md
# Copy Track C prompt, execute
```

### Phase 2: Integration (Day 4-6)

```bash
# When A, B, C reach IMPLEMENT:
# Session 4: Track D (Web UI)
/hydrate plans/agent-town/master-prompts-v2.md
# Copy Track D prompt, execute

# Sync points:
# - Track D imports INHABIT from Track A
# - Track D imports metrics from Track B
# - Track D imports paywall from Track C
```

### Phase 3: Polish & Scenarios (Day 7-10)

```bash
# When Track D reaches QA:
# Session 5: Track E (Scenarios)
/hydrate plans/agent-town/master-prompts-v2.md
# Copy Track E prompt, execute

# Final sync:
# - Track E scenarios load in Track D UI
# - All payment flows tested end-to-end
```

### Phase 4: Launch Readiness

```bash
# All tracks reach REFLECT:
# - Metrics validated (Track B)
# - Economics validated (Track C kill-switch)
# - Ethics validated (Track A consent audit)
# - UX validated (Track D Lighthouse + Kent approval)
# - Content validated (Track E playthroughs)

⟂[DETACH:launch_ready]
```

---

## Emergency Protocols

### If Economics Fail

```markdown
⟂[BLOCKED:economics]

Trigger: Metrics show LOD4/5 margins < 20% after 100 actions

Actions:
1. Increase credit costs (LOD4 → 150, LOD5 → 500)
2. Add Haiku fallback for LOD4 (generate summary, not deep analysis)
3. If still failing, pivot to subscription-only (no consumables)

Resume: Re-run Track C IMPLEMENT with new prices
```

### If Churn Exceeds Threshold

```markdown
⟂[BLOCKED:retention]

Trigger: M1 churn > 25%

Actions:
1. Survey churned users (why did you leave?)
2. Analyze session depth (are they reaching value?)
3. Add engagement hooks (daily events, notifications)
4. Consider free tier expansion

Resume: Add retention track, deprioritize Track E
```

### If Ethics Concerns Arise

```markdown
⟂[BLOCKED:ethics]

Trigger: Force rate > 30% OR consent debt average > 0.5

Actions:
1. Audit force logs (what are users forcing?)
2. Increase force cost or decrease limit
3. Add "relationship repair" explicit action
4. Consider removing force entirely if pattern persists

Resume: Re-run Track A with stricter guardrails
```

---

## Success Celebration

When all tracks reach `⟂[DETACH:launch_ready]`:

```markdown
🎉 AGENT TOWN MVP COMPLETE 🎉

Metrics to celebrate:
- Tests passing: _____
- LOD margins: _____% (target: >30%)
- Consent violations: _____ (target: 0)
- Lighthouse score: _____ (target: >90)
- Kent approval: [ ] YES

Next: Soft launch to friends, gather feedback, iterate.

⟿[REFLECT] Agent Town Launch Retrospective
```

---

## Continuation

```markdown
To start the cycle:

1. Open 3 Claude sessions (or run sequentially)
2. In each session: `/hydrate plans/agent-town/unified-v2.md`
3. Copy the relevant Track prompt (A, B, or C)
4. Execute and follow the continuation signifiers

The prompts are designed to be:
- Self-contained (each has its own handles and exit criteria)
- Composable (tracks integrate at defined sync points)
- Accountable (skip debt declared, kill-switches enforced)
- Courage-driven ("the agent DOES work, not describes it")

Let the rivers flow. 🌊
```

---

*"Five rivers converge into one ocean. Each track is a river."*
