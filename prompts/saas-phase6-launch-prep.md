```markdown
concept.forest.manifest[phase=PLAN][sprint=saas_phase6_launch_prep]@span=saas_launch_plan

/hydrate

handles:
  - checklist: docs/saas/production-checklist.md
  - phase5: docs/skills/n-phase-cycle/saas-phase5-operate.md
  - nats: impl/claude/infra/k8s/manifests/nats/
  - network: impl/claude/infra/k8s/manifests/network-policies/  # to create
  - runbook: docs/saas/runbook.md
  - billing: impl/claude/protocols/billing/

ledger: {PLAN:in_progress, RESEARCH:not_started, DEVELOP:not_started, STRATEGIZE:not_started, CROSS-SYNERGIZE:not_started, IMPLEMENT:not_started, QA:not_started, TEST:not_started, EDUCATE:not_started, MEASURE:not_started, REFLECT:not_started}
entropy: 0.10 budget (fresh cycle)

## Context

Phase 5 Operate complete. All infrastructure running:
- NATS 3-pod cluster in `kgents-agents` (v2.10.29, JetStream enabled)
- 8 Prometheus alerting rules deployed
- Redis idempotency store with graceful fallback
- Production checklist documented with 4 blocking items

## Blocking Items (from docs/saas/production-checklist.md)

| Item | Category | Priority | Risk if Unresolved |
|------|----------|----------|-------------------|
| Network policies for NATS | Security | **High** | Unrestricted cluster access |
| PodDisruptionBudget | Reliability | Medium | Pods evicted during upgrades |
| Load testing baseline | Performance | Medium | Unknown capacity limits |
| Log aggregation | Observability | Low | Debugging difficulty |

## Your Mission

Resolve HIGH priority blocking items to unblock production launch.

### Track A: Network Policies (40%)
1. Create `NetworkPolicy` for NATS: only `kgents-gateway` namespace can access port 4222
2. Create `NetworkPolicy` for Redis: only `kgents-agents` and `kgents-gateway` can access
3. Audit existing manifests for default-allow patterns
4. Apply and verify with `kubectl describe networkpolicy`

### Track B: PodDisruptionBudget (20%)
1. Create PDB for NATS: `minAvailable: 2`
2. Apply and test with simulated drain

### Track C: Load Test Framework (30%)
1. Create k6 load test script for `/health/saas` endpoint
2. Document baseline throughput (target: 100 req/s sustained)
3. Add to CI/CD pipeline (optional)

### Track D: Launch Readiness Review (10%)
1. Re-audit production checklist
2. Update blocking items to resolved
3. Draft launch announcement

## Exit Criteria

- [ ] Network policies applied and tested
- [ ] PDB for NATS deployed
- [ ] Load test script created with baseline documented
- [ ] Zero HIGH-priority blocking items remain

## Non-Goals

- Full log aggregation setup (defer to Phase 7)
- Multi-region NATS (future phase)
- HPA configuration (after baseline established)

## Attention Budget

```
Primary (60%): Track A - Network Policies
Secondary (30%): Tracks B + C
Maintenance (10%): Track D review
```

---

This is the *PLAN* for SaaS Phase 6: Launch Prep.

⟿[RESEARCH]
```
