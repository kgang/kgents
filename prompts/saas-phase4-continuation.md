# SaaS Phase 4 Continuation Prompt

> Use this prompt to continue the SaaS deployment work in a new session.

---

## Current State

```
⟿[REFLECT]

time.forest.witness[phase=REFLECT][law_check=true]@span=saas_phase4_reflect

/hydrate

handles:
  - plan: docs/skills/n-phase-cycle/saas-phase4-deploy.md
  - epilogue: impl/claude/plans/_epilogues/2025-12-14-saas-phase4-deploy.md
  - nats: impl/claude/infra/k8s/manifests/nats/
  - webhooks: impl/claude/protocols/api/webhooks.py
  - metrics: impl/claude/protocols/api/metrics.py
  - docs: docs/saas/

ledger: {PLAN:complete, RESEARCH:complete, DEVELOP:complete, STRATEGIZE:complete, IMPLEMENT:complete, QA:complete, TEST:complete, EDUCATE:complete, MEASURE:pending, REFLECT:in_progress}
entropy: 0.02 remaining

## Your Mission

Close Phase 4 with REFLECT. Synthesize outcomes, extract learnings, decide continuation.

### Outcomes to Summarize

1. **Track A (NATS K8s)**: StatefulSet with 3 replicas, JetStream config, Prometheus sidecar
2. **Track B (Stripe Bridge)**: 6 event types translated, idempotency store, 14 tests
3. **Track C (Observability)**: Prometheus metrics endpoint, Grafana dashboard JSON
4. **Track D (Documentation)**: 4 docs (README, env vars, health endpoints, runbook)

### Learnings to Distill

- Pattern: Non-blocking webhook processing via asyncio.create_task()
- Pattern: Idempotency with in-memory store (MVP) → Redis (production)
- Pattern: Graceful degradation with HAS_* flags
- Decision: StatefulSet for NATS (stable network identity + persistence)

### Exit Criteria

- [ ] Learnings distilled to one-liners
- [ ] Bounty board updated if applicable
- [ ] Continuation type decided (PLAN/META-RE-METABOLIZE/DETACH)
- [ ] Next cycle entry point proposed

---

continuation → PLAN (Phase 5) or ⟂[DETACH:cycle_complete]
```

---

## Next N-Phase Cycle Continuation Prompt

After REFLECT completes, use this prompt to start Phase 5 or a new initiative:

```markdown
⟿[PLAN]

concept.forest.manifest[phase=PLAN][sprint=saas_phase5_operate]@span=saas_operate

/hydrate

handles:
  - prior: docs/skills/n-phase-cycle/saas-phase4-deploy.md
  - infra: impl/claude/infra/k8s/manifests/
  - api: impl/claude/protocols/api/
  - docs: docs/saas/

ledger: {PLAN:in_progress}
entropy: 0.10 budget

## Your Mission (Phase 5: Operate & Scale)

Build on Phase 4 deployment to operationalize SaaS infrastructure.

### Candidate Tracks

1. **Track A (30%): Staging Deployment**
   - Deploy NATS cluster to staging K8s
   - Configure API with SaaS environment variables
   - Verify end-to-end flow (API → NATS → OpenMeter)

2. **Track B (30%): Alerting Rules**
   - Prometheus alertmanager rules for SaaS metrics
   - PagerDuty/Slack integration
   - Runbook links in alert annotations

3. **Track C (20%): Redis Idempotency Store**
   - Replace in-memory IdempotencyStore with Redis
   - TTL-based expiration
   - Horizontal scaling support

4. **Track D (20%): Production Checklist**
   - Security review (secrets rotation, network policies)
   - Load testing (NATS throughput, OpenMeter rate limits)
   - Disaster recovery (NATS data backup, circuit breaker tuning)

### Research Questions

- Staging cluster available? (kind vs cloud)
- Alertmanager already deployed?
- Redis available or need to deploy?

### Exit Criteria

- [ ] Scope defined with dependencies
- [ ] Tracks sequenced with rationale
- [ ] Entropy budget allocated
- [ ] Exit criteria for each track

---

continuation → RESEARCH
```

---

## Alternative: Crown Jewel Pivot

If the priority shifts to Agent Town or AGENTESE REPL, use this entry point:

```markdown
⟿[PLAN]

concept.forest.manifest[phase=PLAN][sprint=agent_town_saas]@span=agent_town_monetization

/hydrate

handles:
  - focus: plans/_focus.md
  - town: impl/claude/agents/town/
  - saas: docs/saas/
  - monetization: plans/monetization/grand-initiative-monetization.md

ledger: {PLAN:in_progress}
entropy: 0.10 budget

## Your Mission

Connect Agent Town to SaaS infrastructure for monetization.

### Candidate Tracks

1. **Usage Metering for Agent Town**
   - OpenMeter events for citizen interactions
   - Token usage tracking per agent
   - Session billing

2. **Subscription Tiers**
   - Free tier: Limited citizens, basic modes
   - Pro tier: Unlimited citizens, all modes
   - Teams tier: Multi-tenant, shared memory

3. **Stripe Integration**
   - Checkout flow for Agent Town subscriptions
   - Customer portal for management
   - Webhook handlers for lifecycle

### Exit Criteria

- [ ] Scope aligned with _focus.md priorities
- [ ] Integration points with existing SaaS infrastructure identified
- [ ] Monetization model defined

---

continuation → RESEARCH
```

---

## Session Boundary (DETACH)

If ending the session without starting a new cycle:

```markdown
⟂[DETACH:cycle_complete]

## Handle Created

Session ending. Handle created for future ATTACH.

**Epilogue**: impl/claude/plans/_epilogues/2025-12-14-saas-phase4-deploy.md
**Continuation**: prompts/saas-phase4-continuation.md

## Artifacts Summary

| Track | Files | Tests |
|-------|-------|-------|
| NATS K8s | 5 manifests + deploy script | - |
| Stripe Bridge | 2 modules | 14 |
| Observability | 2 modules + dashboard | - |
| Documentation | 4 docs | - |

## For Future Observer

To continue:
1. /hydrate
2. Read this continuation prompt
3. Choose: Phase 5 (operate) OR Crown Jewel pivot (Agent Town)
4. Act from principles with courage

*void.gratitude.tithe. The infrastructure awaits its inhabitants.*
```

---

## Quick Reference

| Phase | Status | Next Action |
|-------|--------|-------------|
| Phase 3 (Integrate) | Complete | - |
| Phase 4 (Deploy) | IMPLEMENT complete, REFLECT pending | Run REFLECT prompt |
| Phase 5 (Operate) | Not started | After REFLECT |

| Dependency | Status | Notes |
|------------|--------|-------|
| monetization/grand-initiative | Unblocked | SaaS infrastructure ready |
| deployment/permanent-kgent-chatbot | Unblocked | Can deploy with billing |
| Agent Town | Can integrate | Usage metering available |
