```markdown
concept.forest.manifest[phase=PLAN][sprint=saas_phase7_production_launch]@span=saas_launch

/hydrate

handles:
  - checklist: docs/saas/production-checklist.md
  - phase6: impl/claude/plans/_epilogues/2025-12-14-saas-phase6-launch-prep.md
  - network-policies: impl/claude/infra/k8s/manifests/network-policies/
  - pdb: impl/claude/infra/k8s/manifests/nats/pdb.yaml
  - load-tests: impl/claude/tests/load/
  - runbook: docs/saas/runbook.md

ledger: {PLAN:in_progress, RESEARCH:not_started, DEVELOP:not_started, STRATEGIZE:not_started, CROSS-SYNERGIZE:not_started, IMPLEMENT:not_started, QA:not_started, TEST:not_started, EDUCATE:not_started, MEASURE:not_started, REFLECT:not_started}
entropy: 0.10 budget (fresh cycle)

## Context

Phase 6 Launch Prep COMPLETE. All HIGH priority blocking items resolved:
- NetworkPolicies for NATS and Redis deployed (default-deny + explicit-allow)
- PodDisruptionBudget for NATS (minAvailable: 2)
- k6 load test framework created (target: 100 req/s, p95 < 500ms)
- Production checklist updated with resolved items

## Remaining Items (from docs/saas/production-checklist.md)

| Item | Category | Priority | Status |
|------|----------|----------|--------|
| Log aggregation | Observability | Low | Deferred from Phase 6 |
| Security review sign-off | Governance | N/A | Pending |
| API ingress rules | Security | Medium | Pending (Kong gateway exists) |
| HPA for API | Reliability | Low | Post-baseline |

## Your Mission

Complete production launch readiness and execute first deployment.

### Track A: Apply & Verify Manifests (30%)
1. Apply network policies: `kubectl apply -k manifests/network-policies/`
2. Apply PDB: `kubectl apply -f manifests/nats/pdb.yaml`
3. Verify with `kubectl describe networkpolicy -n kgents-agents`
4. Test that NATS is only accessible from labeled namespaces
5. Simulate pod disruption to verify PDB: `kubectl drain --dry-run`

### Track B: Execute Load Tests (25%)
1. Start API locally or in cluster
2. Run baseline: `k6 run impl/claude/tests/load/saas-health.js`
3. Document baseline metrics (req/s, p95, p99, error rate)
4. If thresholds fail, investigate and re-run
5. Commit results to `docs/saas/load-test-baseline.md`

### Track C: Log Aggregation Setup (25%)
1. Evaluate options: Loki (recommended), Elasticsearch, or stdout-only
2. If Loki: deploy via Helm or manifest
3. Configure log collection for `kgents-agents` and `kgents-gateway`
4. Create Grafana log panel in existing dashboard
5. Document in runbook

### Track D: Launch Execution (20%)
1. Re-audit production checklist (all categories)
2. Create `docs/saas/launch-announcement.md`
3. Update HYDRATE.md with SaaS status
4. Tag release: `git tag saas-v1.0.0`
5. Write session epilogue

## Exit Criteria

- [ ] Network policies applied and verified
- [ ] PDB active and tested
- [ ] Load test baseline documented (100 req/s target)
- [ ] Log aggregation operational OR explicitly deferred with risk acceptance
- [ ] Production checklist fully audited
- [ ] Launch announcement drafted

## Non-Goals

- Multi-region deployment (Phase 8+)
- Full 24h soak test (post-launch monitoring)
- Automated rollback procedures (manual first)

## Attention Budget

```
Primary (55%): Tracks A + B (verification & load tests)
Secondary (25%): Track C (observability)
Maintenance (20%): Track D (documentation & launch)
```

## Branch Candidates

- **HPA configuration**: After baseline load test, separate phase for autoscaling
- **Multi-region NATS**: Enterprise feature, defer to monetization phase
- **Security audit**: May spawn dedicated security review cycle

---

This is the *PLAN* for SaaS Phase 7: Production Launch.

⟿[RESEARCH]
```
