# SaaS Phase 5: Operate & Scale — Continuation Prompt

> Use this prompt to continue SaaS work from Phase 4 completion.

---

## Entry Point

```markdown
⟿[PLAN]

concept.forest.manifest[phase=PLAN][sprint=saas_phase5_operate]@span=saas_operate

/hydrate

handles:
  - prior: docs/skills/n-phase-cycle/saas-phase4-deploy.md
  - epilogue: impl/claude/plans/_epilogues/2025-12-14-saas-phase4-deploy.md
  - infra: impl/claude/infra/k8s/manifests/
  - api: impl/claude/protocols/api/
  - billing: impl/claude/protocols/billing/
  - docs: docs/saas/
  - focus: plans/_focus.md

ledger: {PLAN:in_progress}
entropy: 0.10 budget

## Context from Phase 4

Phase 4 (Deploy & Operationalize) is COMPLETE:
- Track A: NATS K8s manifests (StatefulSet, ConfigMap, Service, deploy script)
- Track B: Stripe → OpenMeter bridge (6 event types, 14 tests)
- Track C: Grafana dashboard JSON + Prometheus metrics endpoint
- Track D: Full documentation (4 docs)

Learnings distilled:
1. Non-blocking webhooks via `asyncio.create_task()`
2. Idempotency pattern: In-memory (MVP) → Redis (production)
3. Graceful degradation with `HAS_*` flags
4. StatefulSet required for NATS JetStream consensus
5. Stripe signature verification must happen before processing

Dependencies unblocked:
- `monetization/grand-initiative-monetization`
- `deployment/permanent-kgent-chatbot`

## Your Mission

Operationalize Phase 4 artifacts into a production-ready SaaS stack. This phase moves from "infrastructure exists" to "infrastructure runs reliably."

### Candidate Tracks

| Track | Weight | Deliverable | Dependencies |
|-------|--------|-------------|--------------|
| A | 30% | Staging Deployment | NATS manifests, API config |
| B | 30% | Alerting Rules | Prometheus metrics, runbook |
| C | 20% | Redis Idempotency Store | Stripe webhook handler |
| D | 20% | Production Checklist | All tracks |

### Track A: Staging Deployment (30%)

**Goal**: Deploy NATS cluster and API to staging K8s, verify end-to-end flow.

**Artifacts**:
- `impl/claude/infra/k8s/overlays/staging/` — Kustomize overlay
- `impl/claude/infra/k8s/scripts/deploy-staging.sh` — Deployment script
- Integration test: API → NATS → OpenMeter pipeline

**Exit Criteria**:
- [ ] NATS StatefulSet running in staging
- [ ] API pods connected to NATS with circuit breaker closed
- [ ] End-to-end event flow verified (publish → consume → meter)

### Track B: Alerting Rules (30%)

**Goal**: Prometheus alertmanager rules for SaaS infrastructure.

**Artifacts**:
- `impl/claude/infra/k8s/manifests/prometheus/alerting-rules.yaml`
- Slack/PagerDuty integration config (template)
- Runbook links in alert annotations

**Alerts**:
| Alert | Condition | Severity | Runbook |
|-------|-----------|----------|---------|
| NATSCircuitOpen | `kgents_nats_circuit_state == 1` for 5m | critical | `docs/saas/runbook.md#nats-circuit-open` |
| OpenMeterFlushErrors | `rate(kgents_openmeter_flush_errors[5m]) > 0.1` | warning | `docs/saas/runbook.md#openmeter-errors` |
| HighWebhookLatency | `kgents_stripe_webhook_latency_p99 > 5s` | warning | `docs/saas/runbook.md#webhook-latency` |

**Exit Criteria**:
- [ ] Alert rules YAML valid and deployable
- [ ] At least 3 critical alerts defined
- [ ] Runbook sections referenced in annotations

### Track C: Redis Idempotency Store (20%)

**Goal**: Replace in-memory `IdempotencyStore` with Redis for horizontal scaling.

**Artifacts**:
- `impl/claude/protocols/billing/idempotency.py` — Redis-backed store
- `impl/claude/protocols/billing/_tests/test_idempotency.py` — Tests
- Environment variable: `REDIS_URL` for idempotency backend

**Design**:
```python
class RedisIdempotencyStore:
    """Redis-backed idempotency store with TTL expiration."""

    async def check_and_set(self, event_id: str, ttl: int = 86400) -> bool:
        """Returns True if event is new, False if duplicate."""
        return await self.redis.set(f"idempotency:{event_id}", "1", nx=True, ex=ttl)
```

**Exit Criteria**:
- [ ] Redis store passes all existing idempotency tests
- [ ] Graceful fallback to in-memory when Redis unavailable
- [ ] TTL-based expiration working

### Track D: Production Checklist (20%)

**Goal**: Security review and operational readiness checklist.

**Artifacts**:
- `docs/saas/production-checklist.md` — Pre-launch checklist

**Checklist Categories**:
1. **Secrets Management**: Rotation policy, K8s secrets vs external vault
2. **Network Policies**: NATS cluster isolation, API ingress rules
3. **Load Testing**: NATS throughput baseline, OpenMeter rate limits
4. **Disaster Recovery**: NATS data backup, circuit breaker recovery

**Exit Criteria**:
- [ ] All checklist items documented
- [ ] Blocking items flagged with owners
- [ ] Non-blocking items scheduled

## Research Questions

Before IMPLEMENT:
1. Staging cluster available? (kind vs cloud provider)
2. Alertmanager already deployed? (standalone vs kube-prometheus-stack)
3. Redis available or need to deploy?
4. What's the timeline pressure? (affects Track D depth)

## Sequencing

```
Track A (Staging) ──────────┬──▶ Track D (Checklist)
                            │
Track B (Alerting) ─────────┤
                            │
Track C (Redis) ────────────┘
```

Tracks A, B, C can run in parallel. Track D synthesizes learnings from all.

## Non-Goals

- Multi-region NATS clustering (future phase)
- Full PagerDuty runbook automation (manual first)
- Redis cluster mode (single instance sufficient for MVP)
- Load testing execution (checklist defines it, Phase 6 executes)

## Entropy Budget

| Phase | Allocation | Notes |
|-------|------------|-------|
| PLAN | 0.01 | Scope definition |
| RESEARCH | 0.02 | Staging env, Redis options |
| IMPLEMENT | 0.05 | Main work |
| Reserve | 0.02 | Unexpected issues |

## Exit Criteria (PLAN Phase)

- [ ] Scope defined with track weights
- [ ] Research questions identified
- [ ] Sequencing rationale documented
- [ ] Entropy budget allocated
- [ ] Non-goals explicit

---

continuation → RESEARCH

This is the *PLAN* for SaaS Phase 5: Operate & Scale — operationalizing Phase 4 infrastructure into production readiness with staging deployment, alerting, Redis idempotency, and a production checklist.
```

---

## Quick Reference

| Phase | Status | Next Action |
|-------|--------|-------------|
| Phase 4 (Deploy) | Complete | ✅ |
| Phase 5 (Operate) | PLAN | Execute this prompt |
| Phase 6 (Scale) | Not started | After Phase 5 |

| Dependency | Status | Notes |
|------------|--------|-------|
| NATS K8s manifests | Ready | Phase 4 Track A |
| Stripe bridge | Ready | Phase 4 Track B (14 tests) |
| Prometheus metrics | Ready | Phase 4 Track C |
| Documentation | Ready | Phase 4 Track D |

---

## Alternative Pivots

If priorities shift per `_focus.md`:

### Crown Jewel: Agent Town + SaaS

```markdown
⟿[PLAN]

concept.forest.manifest[phase=PLAN][sprint=agent_town_saas]@span=agent_town_monetization

/hydrate

handles:
  - focus: plans/_focus.md
  - town: impl/claude/agents/town/
  - saas: docs/saas/
  - billing: impl/claude/protocols/billing/

ledger: {PLAN:in_progress}
entropy: 0.10 budget

## Your Mission

Connect Agent Town to SaaS infrastructure for monetization.

Tracks:
1. Usage metering for citizen interactions (OpenMeter events)
2. Token tracking per agent
3. Subscription tiers (Free/Pro/Teams)
4. Stripe integration for Agent Town subscriptions

---

This is the *PLAN* for Agent Town SaaS Monetization — connecting the crown jewel to billing infrastructure.
```

### Crown Jewel: AGENTESE REPL (Wave 3)

```markdown
⟿[IMPLEMENT]

concept.forest.manifest[phase=IMPLEMENT][sprint=agentese_repl_wave3]@span=repl_wave3

/hydrate

handles:
  - plan: plans/devex/agentese-repl-crown-jewel.md
  - repl: impl/claude/protocols/agentese/repl/
  - tests: impl/claude/protocols/agentese/_tests/test_repl*.py

ledger: {PLAN:complete, RESEARCH:complete, DEVELOP:complete, IMPLEMENT:in_progress}
entropy: 0.08 remaining

## Your Mission

Continue Wave 3: Semantic completions and fuzzy path matching.

---

This is the *IMPLEMENT* for AGENTESE REPL Wave 3 — bringing semantic intelligence to path discovery.
```

---

*void.gratitude.tithe. The infrastructure awaits operation.*
