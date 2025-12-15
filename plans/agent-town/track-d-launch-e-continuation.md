---
path: plans/agent-town/track-d-launch-e-continuation
status: active
progress: 0
priority: 10.0
importance: crown_jewel
last_touched: 2025-12-15
touched_by: claude-opus-4-5
blocking: []
enables:
  - agent-town-launch
  - revenue/first-dollar
supersedes: []
session_notes: |
  Continuation from MEASURE/REFLECT on unified-v2.md economics implementation.
  Track A/B/C complete. Track D 80% complete. Track E pending.
  This prompt covers: D polish → Launch → Validate → Track E.
phase_ledger:
  PLAN: in_progress
  RESEARCH: pending
  DEVELOP: pending
  STRATEGIZE: pending
  CROSS-SYNERGIZE: pending
  IMPLEMENT: pending
  QA: pending
  TEST: pending
  MEASURE: pending
  REFLECT: pending
  EDUCATE: pending
entropy:
  planned: 0.25
  spent: 0.00
  remaining: 0.25
---

# Agent Town: Track D Polish → Launch → Validate → Track E

> *"Ship the arrow, then sharpen the next."*

---

## Context from MEASURE/REFLECT

**Completed (Tracks A/B/C)**:
- ConsentState unified in `budget_store.py` with force_log, status_message
- Webhook → BudgetStore wired for subscriptions and credit packs
- LOD paywall (402) with upgrade_options
- Session caps enforced (check_session_expired, time_remaining)
- Model router with LOD→model mapping and degradation chain
- 17,601 tests passing (100%)

**Track D Status (80% complete)**:
- `impl/claude/web/` — 4,534 lines of React/TypeScript
- Components: Landing, Mesa, CitizenPanel, LODGate, UpgradeModal, Inhabit
- API client with full type definitions
- State stores (town, user, UI)
- `useInhabitSession` hook with consent debt integration

**Gaps Identified**:
- No frontend tests (Jest/RTL)
- No E2E payment flow test (Playwright)
- Instrumentation verification needed
- Track E (Premium Scenarios) not started

---

## Phase 1: Track D Polish

### ⟿[IMPLEMENT] Track D Polish — Frontend Testing & E2E

```
/hydrate plans/agent-town/track-d-launch-e-continuation.md

handles:
  scope=track-d-polish
  web_dir=impl/claude/web
  api_dir=impl/claude/protocols/api
  ledger={PLAN:touched, IMPLEMENT:in_progress}
  entropy=0.06
  parent_plan=plans/agent-town/unified-v2.md

Your Mission

Polish Track D with comprehensive testing:

1. Jest + React Testing Library Setup
   - Configure Jest in impl/claude/web/
   - Add @testing-library/react, @testing-library/user-event
   - Create test utilities (renderWithProviders, mockApi)

2. Critical Component Tests (Priority Order)
   a. useInhabitSession hook
      - Test session start/end
      - Test consent debt tracking
      - Test force action guards (canForce, isRuptured)
      - Test session expiry handling
   b. LODGate component
      - Test paywall render for each tier
      - Test upgrade_options display
      - Test unlock flow
   c. CitizenPanel
      - Test LOD level display
      - Test manifest rendering per LOD
   d. Mesa
      - Test town visualization
      - Test citizen position updates

3. Playwright E2E Setup
   - Install Playwright in impl/claude/web/
   - Create test fixtures for API mocking
   - Write critical path E2E tests:
     a. Tourist → View demo town (LOD 0-1 only)
     b. Tourist → Hit paywall at LOD 3
     c. Tourist → Checkout → Become Resident
     d. Resident → Start INHABIT session
     e. Resident → Force action → See consent debt rise
     f. Citizen → Upgrade → Access LOD 4

4. Instrumentation Verification
   - Check if OTEL spans exist in dialogue_engine.py
   - If missing, add @trace_span decorator to:
     - generate()
     - generate_stream()
     - negotiate_resistance()
   - Verify metrics emit for ActionMetric

Exit Criteria

- [ ] Jest configured with 80%+ coverage on critical hooks
- [ ] 10+ component tests passing
- [ ] Playwright configured with 6 E2E scenarios
- [ ] E2E Tourist → Resident upgrade flow passing
- [ ] Instrumentation verified or added
- [ ] All existing 17,601 tests still passing

Files to Create/Modify

impl/claude/web/
├── jest.config.js
├── jest.setup.ts
├── playwright.config.ts
├── src/
│   ├── test-utils/
│   │   ├── index.tsx           # renderWithProviders
│   │   └── mocks.ts            # API mocks
│   ├── hooks/__tests__/
│   │   └── useInhabitSession.test.ts
│   └── components/__tests__/
│       ├── LODGate.test.tsx
│       ├── CitizenPanel.test.tsx
│       └── Mesa.test.tsx
├── e2e/
│   ├── fixtures/
│   │   └── api.ts              # Playwright API mocks
│   ├── tourist-flow.spec.ts
│   ├── upgrade-flow.spec.ts
│   └── inhabit-flow.spec.ts

Continuation

Upon completing Track D Polish, emit:

⟿[QA]
/hydrate
handles: scope=track-d-qa; ledger={..., IMPLEMENT:touched, QA:in_progress}
mission: Manual QA checklist, smoke tests, staging prep.
```

---

## Phase 2: Launch Preparation

### ⟿[QA] Launch Preparation — Staging Deploy & Smoke Tests

```
/hydrate plans/agent-town/track-d-launch-e-continuation.md

handles:
  scope=launch-preparation
  web_dir=impl/claude/web
  k8s_dir=impl/claude/infra/k8s
  ledger={..., QA:in_progress}
  entropy=0.05

Your Mission

Prepare Agent Town for staging deployment and smoke testing.

1. Staging Environment Setup
   - Review impl/claude/infra/k8s/manifests/ for Agent Town
   - Ensure API deployment includes:
     - STRIPE_SECRET_KEY (staging)
     - STRIPE_WEBHOOK_SECRET
     - DATABASE_URL (staging PG)
     - REDIS_URL
   - Create staging-values.yaml if needed
   - Web UI build → CDN or static serve

2. Smoke Test Checklist (Manual)

   □ API Health
     - GET /health returns 200
     - GET /town/demo returns demo town
     - Auth endpoints functional

   □ Tourist Flow
     - Can view demo town
     - Can see citizens at LOD 0-1
     - Paywall triggers at LOD 3
     - Upgrade options render

   □ Payment Flow (Stripe Test Mode)
     - Checkout session creates
     - Webhook receives events
     - BudgetStore updates tier
     - Credits appear after pack purchase

   □ INHABIT Flow
     - Session starts for Resident+
     - Consent debt visible
     - Force action costs credits
     - Session expires correctly
     - Rupture blocks actions

   □ Metrics
     - OTEL spans visible in traces
     - ActionMetric counters increment
     - Latency p50/p95 reasonable

3. Kill-Switch Verification
   - Verify kill_switch.py thresholds per unified-v2.md §5
   - Test alert firing (mock exceeding threshold)

4. Pre-Launch Checklist

   □ Legal
     - Terms of Service URL set
     - Privacy Policy URL set
     - Refund policy documented

   □ Operational
     - Error alerting configured
     - On-call rotation (even if just Kent)
     - Rollback procedure documented

   □ Metrics Dashboard
     - DAU/MAU tracking
     - Conversion funnel
     - Revenue per day

Exit Criteria

- [ ] Staging deployed and accessible
- [ ] All smoke tests pass
- [ ] Kill-switch alerts verified
- [ ] Legal checkboxes complete
- [ ] Ops runbook exists

Continuation

Upon completing QA, emit:

⟿[LAUNCH]
/hydrate
handles: scope=launch; ledger={..., QA:touched}; entropy=0.03
mission: Go live. Monitor. Iterate.
```

---

## Phase 3: Launch & Validation

### ⟿[LAUNCH] Go Live — Production Deploy & Monitoring

```
/hydrate plans/agent-town/track-d-launch-e-continuation.md

handles:
  scope=launch
  ledger={..., QA:touched}
  entropy=0.03

Your Mission

Deploy Agent Town to production and establish monitoring loop.

1. Production Deploy Sequence

   Step 1: Database migrations
   - Run Alembic migrations against prod DB
   - Verify budget_store tables exist

   Step 2: API deploy
   - Deploy impl/claude/protocols/api to prod k8s
   - Verify /health endpoint
   - Verify Stripe webhook endpoint reachable

   Step 3: Web UI deploy
   - Build React app with prod env vars
   - Deploy to CDN/static hosting
   - Verify CORS headers

   Step 4: DNS/Routing
   - Point agenttown.kgents.com (or similar) to web UI
   - Point api.agenttown.kgents.com to API

   Step 5: Smoke test prod
   - Run manual smoke checklist again
   - Test Stripe live mode (small credit pack)
   - Verify webhook fires

2. Monitoring Setup

   Critical Alerts:
   - API 5xx rate > 1%
   - Latency p95 > 2s
   - Stripe webhook failures
   - Kill-switch thresholds

   Dashboard Panels:
   - Active sessions (INHABIT)
   - Revenue (daily/weekly/monthly)
   - Conversion funnel (Tourist → Resident → Citizen)
   - LOD unlock rate
   - Force action rate (ethics monitoring)

3. First 24 Hours Protocol

   Hour 0-1: Intense monitoring
   - Watch error logs
   - Watch Stripe dashboard
   - Watch first user flows

   Hour 1-6: Light monitoring
   - Check dashboards hourly
   - Respond to any alerts

   Hour 6-24: Normal monitoring
   - Check dashboards 3x
   - Document any issues

4. Validation Metrics (Week 1)

   Target (Conservative):
   - 100+ unique visitors
   - 10+ Tourist → Resident conversions (10%)
   - 3+ Resident → Citizen upgrades
   - $50+ revenue
   - <5% churn (first week)
   - Force rate <30% of INHABIT sessions

   Kill-Switch Triggers:
   - Conversion <3%: Pause, analyze funnel
   - Churn >25%: Emergency retention review
   - Force rate >30%: Ethics review
   - Negative margin: Halt until repriced

Exit Criteria

- [ ] Production live and stable
- [ ] First real payment processed
- [ ] Monitoring dashboards functional
- [ ] Week 1 metrics captured
- [ ] No kill-switch triggers

Continuation

Upon completing Launch & initial validation, emit:

⟿[MEASURE]
/hydrate
handles: scope=launch-validation; ledger={..., LAUNCH:touched, MEASURE:in_progress}
mission: Capture Week 1 metrics, decide Track E timing.
```

---

## Phase 4: Track E — Premium Scenarios

### ⟿[PLAN] Track E — Premium Scenarios: The Vanishing & The Founding

```
/hydrate plans/agent-town/track-d-launch-e-continuation.md

handles:
  scope=track-e-premium-scenarios
  town_dir=impl/claude/agents/town
  fixtures_dir=impl/claude/agents/town/fixtures
  spec_dir=spec/town
  ledger={..., MEASURE:touched, PLAN:in_progress}
  entropy=0.08
  prerequisite=launch-validated

GATE CHECK

Before proceeding with Track E, verify:
- [ ] Week 1 revenue > $50
- [ ] Conversion rate > 3%
- [ ] No kill-switch triggers
- [ ] User feedback indicates interest in scenarios

If gate check fails, PAUSE Track E and focus on:
- Funnel optimization
- Retention mechanics
- User research

Your Mission

Design and implement two flagship premium scenarios that demonstrate
Agent Town's unique value proposition: emergent narrative through
citizen simulation.

Scenario 1: "The Vanishing"

  Premise: A citizen has disappeared. The town is unsettled.

  Setup:
  - 8 citizens (standard demo town)
  - One citizen (e.g., "Marcus") marked as VANISHED
  - Other citizens have hidden knowledge fragments
  - Coalition dynamics shifted by absence

  Mechanics:
  - LOD 3+ reveals citizens' memories of Marcus
  - LOD 4 reveals psychological impact
  - LOD 5 reveals hidden connections to the vanishing
  - INHABIT enables investigation through citizen eyes
  - Multiple possible "truths" — no single canonical answer

  Purchasable Elements:
  - Scenario unlock: 500 credits ($5-10)
  - "Detective Mode": Enhanced LOD 3 for all citizens (200 credits)
  - "Marcus's Journal": LOD 5 artifact (400 credits)

  Implementation:
  - Create fixtures/vanishing_citizens.yaml
  - Add VanishingScenario class with:
    - initial_state: PreVanishing, PostVanishing, Investigation, Resolution
    - hidden_truths: List of possible explanations (player discovers one)
    - clue_distribution: Which citizen knows what
  - Add scenario loader to TownEnvironment

Scenario 2: "The Founding"

  Premise: Flashback to the town's creation. Secrets laid bare.

  Setup:
  - 5 citizens (founders only)
  - Historical timeline: Year 0 of the town
  - Original coalitions and their compromises
  - "The Pact" — a founding agreement with hidden clauses

  Mechanics:
  - LOD 3+ reveals founding memories (rose-tinted vs. realistic)
  - LOD 4 reveals original intentions vs. outcomes
  - LOD 5 reveals "The Pact" details
  - INHABIT enables living through founding moments
  - Connects to present-day town dynamics

  Purchasable Elements:
  - Scenario unlock: 500 credits ($5-10)
  - "The Pact (Full Text)": LOD 5 artifact (400 credits)
  - "Founder's Perspective": INHABIT bonus scenes (300 credits)

  Implementation:
  - Create fixtures/founding_citizens.yaml
  - Add FoundingScenario class with:
    - timeline: List of founding events
    - pact_clauses: Hidden agreements (revealed at LOD 5)
    - present_day_echoes: How founding affects current town
  - Add timeline navigation to INHABIT mode

Shared Infrastructure:
  - ScenarioLoader: Load scenarios from fixtures
  - ScenarioPurchase: Stripe product for scenarios
  - ScenarioProgress: Track user progress through scenario
  - ScenarioArtifacts: Purchasable LOD 5 items

Exit Criteria (PLAN Phase)

- [ ] Both scenarios fully designed with citizen configs
- [ ] Purchasable elements defined with credit costs
- [ ] Implementation approach documented
- [ ] No scope creep (exactly 2 scenarios)
- [ ] Estimated: 1 session IMPLEMENT, 1 session TEST

Continuation

Upon completing PLAN, emit:

⟿[IMPLEMENT]
/hydrate
handles: scope=track-e-implement; ledger={..., PLAN:touched, IMPLEMENT:in_progress}
mission: Build "The Vanishing" first (MVP scenario), then "The Founding".
```

---

### ⟿[IMPLEMENT] Track E — Build Premium Scenarios

```
/hydrate plans/agent-town/track-d-launch-e-continuation.md

handles:
  scope=track-e-implement
  ledger={..., PLAN:touched, IMPLEMENT:in_progress}
  entropy=0.08

Your Mission

Implement both premium scenarios with purchasable artifacts.

1. Scenario Infrastructure (shared)

   impl/claude/agents/town/scenarios/
   ├── __init__.py
   ├── base.py            # ScenarioBase, ScenarioState
   ├── loader.py          # ScenarioLoader (YAML → Scenario)
   ├── progress.py        # ScenarioProgress (user state)
   ├── artifacts.py       # Purchasable LOD 5 items
   ├── vanishing/
   │   ├── __init__.py
   │   ├── scenario.py    # VanishingScenario
   │   └── fixtures.yaml  # Citizen configs
   └── founding/
       ├── __init__.py
       ├── scenario.py    # FoundingScenario
       └── fixtures.yaml  # Citizen configs

2. Scenario API Endpoints

   POST /town/{town_id}/scenario/{scenario_id}/unlock
   - Requires credits
   - Returns scenario initial state

   GET /town/{town_id}/scenario/{scenario_id}/progress
   - Returns user's scenario progress

   POST /town/{town_id}/scenario/{scenario_id}/artifact/{artifact_id}/purchase
   - Requires credits
   - Returns artifact content

3. "The Vanishing" Implementation

   Step 1: Create vanishing/fixtures.yaml
   - 8 citizens with hidden_knowledge fields
   - Marcus (VANISHED) with last_known_state
   - clue_distribution across citizens

   Step 2: VanishingScenario class
   ```python
   class VanishingScenario(ScenarioBase):
       state: Literal["PRE", "POST", "INVESTIGATION", "RESOLUTION"]
       hidden_truths: list[str]  # Multiple possible explanations
       discovered_clues: set[str]

       def get_citizen_knowledge(self, citizen: str, lod: int) -> str:
           """Return what this citizen knows at this LOD."""

       def check_resolution(self) -> bool:
           """Has user discovered enough to form a theory?"""
   ```

   Step 3: Integrate with TownEnvironment
   - Add scenario_id field
   - Modify citizen manifests based on scenario state
   - Add scenario-specific INHABIT prompts

4. "The Founding" Implementation

   Step 1: Create founding/fixtures.yaml
   - 5 founder citizens with founding_memory fields
   - timeline of events
   - pact_clauses (hidden until LOD 5)

   Step 2: FoundingScenario class
   ```python
   class FoundingScenario(ScenarioBase):
       timeline: list[FoundingEvent]
       current_year: int  # 0 = founding, can navigate
       pact_revealed: bool

       def navigate_timeline(self, year: int) -> None:
           """Move to different point in history."""

       def get_pact_clause(self, clause_id: str) -> str | None:
           """Return clause if purchased/unlocked."""
   ```

   Step 3: Timeline navigation in INHABIT
   - Add "remember <year>" command in INHABIT
   - Citizen manifests change based on timeline position

5. Stripe Products Setup

   Products to create:
   - scenario_vanishing_unlock (500 credits = $5-10)
   - scenario_vanishing_detective (200 credits)
   - scenario_vanishing_journal (400 credits)
   - scenario_founding_unlock (500 credits)
   - scenario_founding_pact (400 credits)
   - scenario_founding_perspective (300 credits)

   Add to webhooks.py:
   - Handle scenario purchases
   - Update ScenarioProgress

6. Web UI Integration

   impl/claude/web/src/pages/Scenarios.tsx
   - List available scenarios
   - Show locked/unlocked state
   - Purchase flow

   impl/claude/web/src/components/scenario/
   ├── ScenarioCard.tsx
   ├── VanishingView.tsx
   ├── FoundingView.tsx
   └── ArtifactPurchase.tsx

Exit Criteria

- [ ] ScenarioBase and infrastructure working
- [ ] VanishingScenario complete with 8 citizens
- [ ] FoundingScenario complete with 5 founders
- [ ] Both scenarios purchasable via API
- [ ] Artifacts purchasable and content delivered
- [ ] Web UI shows scenarios
- [ ] 40+ tests for scenario logic
- [ ] Integration with existing INHABIT mode

Continuation

Upon completing IMPLEMENT, emit:

⟿[TEST]
/hydrate
handles: scope=track-e-test; ledger={..., IMPLEMENT:touched, TEST:in_progress}
mission: Comprehensive scenario testing, edge cases, purchase flows.
```

---

### ⟿[TEST] Track E — Scenario Testing

```
/hydrate plans/agent-town/track-d-launch-e-continuation.md

handles:
  scope=track-e-test
  ledger={..., IMPLEMENT:touched, TEST:in_progress}
  entropy=0.04

Your Mission

Comprehensive testing of premium scenarios.

1. Unit Tests

   Scenario Infrastructure:
   - test_scenario_loader.py (YAML → Scenario)
   - test_scenario_progress.py (state tracking)
   - test_artifacts.py (purchase, delivery)

   Vanishing Scenario:
   - test_vanishing_clues.py (clue distribution)
   - test_vanishing_lod.py (knowledge at each LOD)
   - test_vanishing_resolution.py (theory formation)
   - test_vanishing_citizens.py (citizen configs valid)

   Founding Scenario:
   - test_founding_timeline.py (navigation)
   - test_founding_pact.py (clause revelation)
   - test_founding_citizens.py (founder configs valid)

2. Integration Tests

   - test_scenario_purchase_flow.py
     - Tourist cannot purchase (tier gate)
     - Resident can purchase with credits
     - Webhook updates progress
     - Artifact delivered after purchase

   - test_scenario_inhabit_integration.py
     - INHABIT in scenario context
     - Scenario-specific prompts work
     - Progress updates during INHABIT

   - test_scenario_manifest_integration.py
     - Citizen manifests reflect scenario state
     - LOD levels respect scenario unlocks

3. E2E Tests (Playwright)

   e2e/scenarios/vanishing.spec.ts:
   - View scenario listing (locked)
   - Purchase scenario
   - Enter scenario town
   - View clues at LOD 3
   - Purchase artifact
   - View artifact content

   e2e/scenarios/founding.spec.ts:
   - Purchase and enter
   - Navigate timeline
   - View pact at LOD 5

4. Edge Cases

   - Scenario purchase fails mid-flight (rollback)
   - Artifact purchase with insufficient credits
   - INHABIT in scenario with rupture
   - Timeline navigation during active INHABIT
   - Multiple users in same scenario (isolation)

5. Performance Tests

   - Scenario load time < 500ms
   - 100 concurrent scenario sessions
   - Artifact delivery < 200ms

Exit Criteria

- [ ] 40+ scenario-specific tests passing
- [ ] E2E purchase flow verified
- [ ] Edge cases covered
- [ ] Performance acceptable
- [ ] All 17,601+ tests still passing

Continuation

Upon completing TEST, emit:

⟿[MEASURE]
/hydrate
handles: scope=track-e-measure; ledger={..., TEST:touched, MEASURE:in_progress}
mission: Capture scenario metrics, prepare for launch.
```

---

## Phase 5: Final Measurement & Reflection

### ⟿[MEASURE] Track E Complete — Metrics & Launch Prep

```
/hydrate plans/agent-town/track-d-launch-e-continuation.md

handles:
  scope=track-e-measure
  ledger={..., TEST:touched, MEASURE:in_progress}
  entropy=0.02

Your Mission

Capture final metrics and prepare Track E for launch.

1. Test Metrics

   - Total test count (target: 17,700+)
   - Scenario-specific tests (target: 40+)
   - E2E scenario tests (target: 4+)
   - Pass rate (target: 100%)

2. Code Metrics

   - Files created (scenarios/, web components)
   - Lines added
   - Complexity assessment

3. Success Criteria Evaluation

   From unified-v2.md §9:
   - [ ] 2 scenarios available ("The Vanishing" + "The Founding")
   - [ ] Scenarios purchasable via credits
   - [ ] Artifacts deliver value at LOD 5
   - [ ] Integration with INHABIT mode
   - [ ] No scope creep (exactly 2 scenarios)

4. Launch Readiness

   - [ ] Stripe products created (staging + prod)
   - [ ] Web UI shows scenarios
   - [ ] Pricing finalized
   - [ ] Marketing copy ready

5. Learnings

   - What worked well in scenario design?
   - What could improve?
   - What's next after these 2 scenarios?

Exit Criteria

- [ ] All metrics captured
- [ ] Success criteria evaluated
- [ ] Launch readiness confirmed
- [ ] Epilogue written

Continuation

Upon completing MEASURE, emit:

⟿[REFLECT]
/hydrate
handles: scope=full-cycle-complete; ledger={all:touched}; entropy=0.01
mission: Final reflection, unified-v2.md closure, next cycle seeds.
```

---

## Summary: The Full Continuation Path

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    TRACK D → LAUNCH → VALIDATE → TRACK E                    │
│                                                                             │
│   Phase 1: Track D Polish                                                   │
│   ├─ Jest + RTL setup                                                       │
│   ├─ Component tests (useInhabitSession, LODGate, CitizenPanel, Mesa)       │
│   ├─ Playwright E2E (6 critical paths)                                      │
│   └─ Instrumentation verification                                           │
│                                                                             │
│   Phase 2: Launch Preparation                                               │
│   ├─ Staging deploy                                                         │
│   ├─ Smoke test checklist                                                   │
│   ├─ Kill-switch verification                                               │
│   └─ Pre-launch legal/ops checklist                                         │
│                                                                             │
│   Phase 3: Launch & Validation                                              │
│   ├─ Production deploy sequence                                             │
│   ├─ Monitoring setup                                                       │
│   ├─ First 24 hours protocol                                                │
│   └─ Week 1 validation metrics                                              │
│                                                                             │
│   GATE CHECK: Week 1 revenue > $50, conversion > 3%, no kill-switch         │
│                                                                             │
│   Phase 4: Track E — Premium Scenarios                                      │
│   ├─ PLAN: Design "The Vanishing" + "The Founding"                          │
│   ├─ IMPLEMENT: Scenario infrastructure, both scenarios, Stripe products    │
│   └─ TEST: Unit, integration, E2E, edge cases                               │
│                                                                             │
│   Phase 5: Final Measurement                                                │
│   ├─ Metrics capture                                                        │
│   ├─ Success criteria evaluation                                            │
│   └─ Cycle closure + next seeds                                             │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Quick Start

To begin, copy and paste this into a new session:

```
⟿[IMPLEMENT] Track D Polish — Frontend Testing & E2E

/hydrate plans/agent-town/track-d-launch-e-continuation.md

handles:
  scope=track-d-polish
  web_dir=impl/claude/web
  api_dir=impl/claude/protocols/api
  ledger={PLAN:touched, IMPLEMENT:in_progress}
  entropy=0.06
  parent_plan=plans/agent-town/unified-v2.md

Your Mission

Polish Track D with comprehensive testing:

1. Jest + React Testing Library Setup
   - Configure Jest in impl/claude/web/
   - Add @testing-library/react, @testing-library/user-event
   - Create test utilities (renderWithProviders, mockApi)

2. Critical Component Tests (Priority Order)
   a. useInhabitSession hook — session lifecycle, consent debt, force guards
   b. LODGate — paywall render, upgrade flow
   c. CitizenPanel — LOD display, manifest rendering
   d. Mesa — town visualization

3. Playwright E2E (6 critical paths)
   a. Tourist → View demo (LOD 0-1)
   b. Tourist → Paywall at LOD 3
   c. Tourist → Checkout → Resident
   d. Resident → INHABIT session
   e. Resident → Force → Consent debt rise
   f. Citizen → Upgrade → LOD 4 access

4. Instrumentation verification (OTEL spans in dialogue_engine)

Exit Criteria

- [ ] Jest configured, 80%+ coverage on critical hooks
- [ ] 10+ component tests passing
- [ ] Playwright with 6 E2E scenarios
- [ ] E2E upgrade flow passing
- [ ] Instrumentation verified
- [ ] All 17,601 tests still passing
```

---

*"Ship the arrow, then sharpen the next."*
