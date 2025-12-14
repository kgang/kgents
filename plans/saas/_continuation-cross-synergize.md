# kgents SaaS - CROSS-SYNERGIZE Continuation Prompt

**Generated**: 2025-12-14
**From Phase**: STRATEGIZE
**To Phase**: CROSS-SYNERGIZE

---

## Phase Transition Record

```yaml
phase_ledger:
  PLAN: touched
  RESEARCH: touched
  DEVELOP: touched
  STRATEGIZE: touched
  CROSS-SYNERGIZE: pending → in_progress
  IMPLEMENT: pending
  QA: pending
  TEST: pending
  EDUCATE: pending
  MEASURE: pending
  REFLECT: pending

entropy:
  budget: 0.10
  spent: 0.04
  remaining: 0.06

branch_candidates:
  blocking: []
  parallel:
    - "billing-integration" # Can proceed independently once metering ready
    - "gtm-marketing" # No code dependencies
  deferred:
    - "void-time-concept-contexts" # MVP+1
    - "custom-personas" # Enterprise feature
    - "multi-agent-orchestration" # Complexity deferral
  void:
    - "mobile-apps"
    - "marketplace"
```

---

## Continuation Prompt

```
⟿[CROSS-SYNERGIZE]

concept.forest.manifest[phase=CROSS-SYNERGIZE][minimal_output=true]@span=saas_synergy

ATTACH

/hydrate

handles:
  - strategy: plans/saas/strategy-implementation.md
  - platform: plans/saas/architecture-platform.md
  - billing: plans/saas/architecture-billing.md
  - scope: plans/saas/mvp-scope.md
  - gtm: plans/saas/gtm-plan.md
  - agentese_impl: impl/claude/protocols/agentese/ (559 tests)
  - agentese_spec: spec/protocols/agentese.md

ledger: {PLAN:touched, RESEARCH:touched, DEVELOP:touched, STRATEGIZE:touched, CROSS-SYNERGIZE:in_progress}
entropy: 0.06 remaining

---

## Mission

Identify synergies across the 3 implementation tracks (Core, Billing, GTM) and leverage existing kgents primitives.

## Actions

1. **AGENTESE Path Reuse** — Map which existing paths serve multiple features:
   - `self.memory.*` → K-Gent sessions + Agent state
   - `world.*.witness` → Observability dashboard + N-gent traces
   - `self.soul.*` → K-Gent persona + SOUL_POLYNOMIAL

2. **Impl/Spec Gap Analysis** — Check impl/claude/protocols/agentese/ for:
   - Which handlers already exist vs need building
   - Test coverage gaps for SaaS use cases
   - Any spec/ → impl/ drift

3. **Event Schema Unification** — Ensure billing/metering events align with:
   - OpenMeter CloudEvents format
   - Existing AGENTESE trace emission
   - N-gent witness patterns

4. **K-Gent/Observability Overlap** — Identify shared infrastructure:
   - Trace collection serves both debugging + billing
   - Session state overlaps with D-gent memory
   - Witness service serves N-gent + audit

5. **Dormant Plan Connections** — Check for related plans in plans/:
   - Any existing SaaS groundwork?
   - Related agent work (K-gent, D-gent, N-gent)?
   - Skills that apply?

## Exit Criteria

- [ ] Synergy map documented (shared primitives identified)
- [ ] Composition opportunities listed (agent reuse, path reuse)
- [ ] Impl/spec gaps surfaced (what needs building vs exists)
- [ ] Event schema alignment confirmed
- [ ] ledger.CROSS-SYNERGIZE = touched

## Output

Append synergy findings to: plans/saas/strategy-implementation.md (Section 6)
Or create: plans/saas/synergy-map.md if substantial

---

continuation → IMPLEMENT (Phase 1: Foundation)
```

---

## Next Phase Continuations

### After CROSS-SYNERGIZE → IMPLEMENT

```
⟿[IMPLEMENT]

time.forest.manifest[phase=IMPLEMENT][sprint=foundation]@span=saas_impl

ATTACH

/hydrate

handles:
  - strategy: plans/saas/strategy-implementation.md
  - synergies: plans/saas/synergy-map.md (or strategy Section 6)
  - platform: plans/saas/architecture-platform.md
  - scope: plans/saas/mvp-scope.md

ledger: {PLAN:touched, RESEARCH:touched, DEVELOP:touched, STRATEGIZE:touched, CROSS-SYNERGIZE:touched, IMPLEMENT:in_progress}
entropy: 0.05 remaining

---

## Mission

Execute Phase 0 (Foundation) from strategy-implementation.md.

## Actions (Phase 0: Foundation)

1. **K8s Cluster** — Set up local Kind or staging EKS
2. **PostgreSQL + RLS** — Deploy with tenant isolation policies
3. **Redis** — Deploy for rate limiting cache
4. **Kong Gateway** — Configure with JWT plugin
5. **Auth Service** — Implement JWT validation + API key CRUD
6. **Tenant Service** — Implement tenant provisioning

## Entry Criteria

- [ ] Cloud provider configured (or local Kind)
- [ ] CI/CD pipeline skeleton ready

## Exit Criteria

- [ ] `kubectl cluster-info` succeeds
- [ ] Authenticated request reaches backend
- [ ] RLS tenant isolation verified
- [ ] Rate limiting returns 429 after burst
- [ ] All health checks pass
- [ ] ledger.IMPLEMENT = in_progress (Foundation complete)

---

continuation → IMPLEMENT (Phase 1: Core Tracks) or ⟂[BLOCKED] if foundation fails
```

---

### After IMPLEMENT (all phases) → QA

```
⟿[QA]

self.capability.manifest[phase=QA][checklist=full]@span=saas_qa

ATTACH

/hydrate

handles:
  - impl: impl/claude/protocols/saas/ (or wherever SaaS code lands)
  - tests: impl/claude/protocols/saas/_tests/
  - strategy: plans/saas/strategy-implementation.md

ledger: {PLAN:touched, RESEARCH:touched, DEVELOP:touched, STRATEGIZE:touched, CROSS-SYNERGIZE:touched, IMPLEMENT:touched, QA:in_progress}
entropy: 0.04 remaining

---

## Mission

Run QA checklist on all implemented code.

## Actions

1. **Lint** — `uv run ruff check impl/`
2. **Type Check** — `uv run mypy impl/`
3. **Security Scan** — Check for OWASP top 10, RLS bypass vectors
4. **API Contract** — Verify endpoints match mvp-scope.md specs
5. **Tenant Isolation** — Penetration test RLS policies

## Exit Criteria

- [ ] Zero lint errors
- [ ] Zero type errors
- [ ] No critical security findings
- [ ] API contracts validated
- [ ] ledger.QA = touched

---

continuation → TEST or ⟂[QA:blocked] if errors require resolution
```

---

### After QA → TEST

```
⟿[TEST]

self.capability.manifest[phase=TEST][coverage=p0]@span=saas_test

ATTACH

/hydrate

handles:
  - impl: impl/claude/protocols/saas/
  - existing_tests: impl/claude/protocols/agentese/_tests/ (559 tests)
  - scope: plans/saas/mvp-scope.md

ledger: {..., QA:touched, TEST:in_progress}
entropy: 0.03 remaining

---

## Mission

Add/update tests for SaaS functionality.

## Actions

1. **Unit Tests** — Core service functions
2. **Integration Tests** — API endpoints end-to-end
3. **RLS Tests** — Tenant isolation verification
4. **Billing Tests** — Metering accuracy, quota enforcement
5. **Run Suite** — `uv run pytest impl/claude/protocols/saas/`

## Exit Criteria

- [ ] ≥90% coverage on core paths
- [ ] All P0 user stories have test coverage
- [ ] Tests pass in CI
- [ ] ledger.TEST = touched

---

continuation → EDUCATE or ⟂[TEST:blocked] if tests fail
```

---

### After TEST → EDUCATE

```
⟿[EDUCATE]

world.docs.manifest[phase=EDUCATE][audience=developers]@span=saas_docs

ATTACH

/hydrate

handles:
  - api_spec: plans/saas/mvp-scope.md (Section 4: API Specification)
  - gtm: plans/saas/gtm-plan.md (documentation strategy)
  - agentese_spec: spec/protocols/agentese.md

ledger: {..., TEST:touched, EDUCATE:in_progress}
entropy: 0.02 remaining

---

## Mission

Create developer-facing documentation and usage guides.

## Actions

1. **Quickstart** — 5-minute first API call guide
2. **API Reference** — Auto-generate from OpenAPI specs
3. **AGENTESE Guide** — How to invoke paths
4. **K-Gent Tutorial** — Chat integration example
5. **Troubleshooting** — Common errors and fixes

## Exit Criteria

- [ ] Quickstart tested by 3 external developers
- [ ] All endpoints documented
- [ ] Code examples copy-paste ready
- [ ] ledger.EDUCATE = touched

---

continuation → MEASURE
```

---

### After EDUCATE → MEASURE

```
⟿[MEASURE]

time.metrics.manifest[phase=MEASURE][baseline=true]@span=saas_measure

ATTACH

/hydrate

handles:
  - gtm: plans/saas/gtm-plan.md (success metrics)
  - scope: plans/saas/mvp-scope.md (launch criteria)

ledger: {..., EDUCATE:touched, MEASURE:in_progress}
entropy: 0.01 remaining

---

## Mission

Establish measurement infrastructure and baseline metrics.

## Actions

1. **Instrumentation** — Prometheus metrics in all services
2. **Dashboards** — Grafana dashboards for KPIs
3. **Alerts** — PagerDuty/Slack for SLA breaches
4. **Baseline Capture** — p99 latency, error rate, token costs
5. **GTM Metrics** — Analytics for signups, activation, conversion

## Exit Criteria

- [ ] p99 latency < 500ms baseline established
- [ ] Error rate < 1% baseline established
- [ ] Usage dashboard live
- [ ] GTM funnel instrumented
- [ ] ledger.MEASURE = touched

---

continuation → REFLECT
```

---

### After MEASURE → REFLECT (Cycle Complete)

```
⟿[REFLECT]

void.gratitude.tithe[phase=REFLECT][cycle=saas_mvp]@span=saas_reflect

ATTACH

/hydrate

handles:
  - all_plans: plans/saas/*.md
  - impl: impl/claude/protocols/saas/
  - metrics: (from MEASURE)

ledger: {..., MEASURE:touched, REFLECT:in_progress}
entropy: 0.00 (cycle complete, tithe remainder)

---

## Mission

Capture learnings, update mycelium, seed next cycle.

## Actions

1. **Learnings** — What worked? What didn't? What surprised us?
2. **Process Refinements** — N-Phase cycle improvements
3. **Technical Debt** — What did we defer? What's the risk?
4. **Double-Loop** — Did our assumptions hold? Frame changes needed?
5. **Next-Loop Seeds** — What should Cycle 2 focus on?

## Exit Criteria

- [ ] Learnings documented in epilogue
- [ ] Deferred items backlogged with owners
- [ ] Process improvements captured
- [ ] Next cycle seeds identified
- [ ] ledger.REFLECT = touched

## Output

Create: plans/_epilogues/2025-12-XX-saas-mvp-cycle1.md

---

⟂[DETACH:cycle_complete]

Next cycle seeds:
- Sprint 1 execution (if not complete)
- MVP+1 features (void.*/time.*/concept.* contexts)
- Enterprise features (SSO, custom personas)
- Scale optimizations (multi-LLM, GPU pools)
```

---

## Cycle 2 Continuation (Post-REFLECT)

```
⟿[PLAN]

concept.forest.manifest[phase=PLAN][cycle=2]@span=saas_cycle2

# kgents SaaS - Cycle 2: MVP+1 Features

ATTACH

/hydrate

handles:
  - cycle1_reflect: plans/_epilogues/2025-12-XX-saas-mvp-cycle1.md
  - strategy: plans/saas/strategy-implementation.md
  - deferred: (from strategy Section 5.2: Deferred Branches)

ledger: {cycle1:complete, cycle2.PLAN:in_progress}
entropy: 0.10 (fresh cycle)

---

## Context from Cycle 1 REFLECT

- Learnings: ${key_learnings}
- Refinements: ${process_refinements}
- Deferred items: void.*/time.*/concept.* contexts, custom personas

## Cycle 2 Scope Candidates

1. **void.* Context** — Entropy/gratitude handlers
2. **time.* Context** — Temporal traces, forecasts
3. **concept.* Context** — Platonic definitions
4. **Custom Personas** — K-gent variants beyond Kent
5. **Self-Hosted Guide** — Docker/Helm deployment docs

## Exit Criteria

- [ ] Scope selected (MoSCoW)
- [ ] Dependencies mapped
- [ ] Attention budget set
- [ ] Entropy sip: 0.07
- [ ] ledger.PLAN = touched

---

continuation → RESEARCH for Cycle 2 terrain mapping
```

---

## Law Compliance

- **Every cycle MUST reach ⟂ eventually**: Cycle ends at REFLECT with `⟂[DETACH:cycle_complete]`
- **Skipped phases leave debt**: None skipped; all 11 phases will be touched
- **Branch candidates classified**: Documented in phase_ledger above
- **Entropy budgeted**: 0.10 total, 0.04 spent through STRATEGIZE, 0.06 remaining

---

*Generated by N-Phase Cycle auto-continuation. See `plans/skills/n-phase-cycle/README.md`.*
